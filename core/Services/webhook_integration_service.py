"""
Enterprise Webhook Integration Service
Kurumsal seviyede webhook entegrasyonu servisi - Tüm webhook işlemlerini yönetir
"""

import asyncio
import json
import logging
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from functools import wraps

from core.Services.base_service import BaseService
from core.Services.cache_service import CacheService
from core.Services.notification_service import get_notification_service
from core.Services.queue_service import QueueService


class WebhookStatus(Enum):
    """Webhook durumları"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"


class WebhookProvider(Enum):
    """Webhook sağlayıcıları"""
    GITHUB = "github"
    GITLAB = "gitlab"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"
    SLACK = "slack"
    DISCORD = "discord"
    TWILIO = "twilio"
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    CUSTOM = "custom"


class WebhookHandler:
    """Webhook handler temel sınıfı"""
    
    def __init__(self, name: str, handler_func: Callable, config: Dict[str, Any] = None):
        self.name = name
        self.handler_func = handler_func
        self.config = config or {}
        self.logger = logging.getLogger(f"WebhookHandler.{name}")
        
    async def handle(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Webhook'u işle"""
        try:
            result = await self.handler_func(payload, headers)
            self.logger.info(f"Webhook handled successfully: {self.name}")
            return {
                'status': 'success',
                'result': result
            }
        except Exception as e:
            self.logger.error(f"Webhook handler error: {self.name} - {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def validate_signature(self, payload: str, signature: str, secret: str) -> bool:
        """İmza doğrulama"""
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)


class WebhookIntegrationService(BaseService):
    """Kurumsal Webhook Entegrasyon Servisi"""
    
    def __init__(self):
        super().__init__()
        self.cache = CacheService()
        self.queue = QueueService()
        self.notification_service = get_notification_service()
        self.webhook_config = self.get_config('webhook', {})
        self.handlers: Dict[str, WebhookHandler] = {}
        self.provider_configs: Dict[str, Dict[str, Any]] = {}
        self._initialize_providers()
        
    def _initialize_providers(self):
        """Webhook sağlayıcılarını başlat"""
        # GitHub webhook config
        self.provider_configs[WebhookProvider.GITHUB.value] = {
            'secret': self.webhook_config.get('github', {}).get('secret'),
            'events': ['push', 'pull_request', 'issues', 'release'],
            'signature_header': 'X-Hub-Signature-256',
            'event_header': 'X-GitHub-Event'
        }
        
        # Stripe webhook config
        self.provider_configs[WebhookProvider.STRIPE.value] = {
            'secret': self.webhook_config.get('stripe', {}).get('webhook_secret'),
            'events': ['payment_intent.succeeded', 'payment_intent.failed', 'charge.refunded'],
            'signature_header': 'Stripe-Signature'
        }
        
        # PayPal webhook config
        self.provider_configs[WebhookProvider.PAYPAL.value] = {
            'webhook_id': self.webhook_config.get('paypal', {}).get('webhook_id'),
            'events': ['PAYMENT.SALE.COMPLETED', 'PAYMENT.SALE.REFUNDED'],
            'signature_header': 'PAYPAL-TRANSMISSION-SIG'
        }
        
        # Slack webhook config
        self.provider_configs[WebhookProvider.SLACK.value] = {
            'verification_token': self.webhook_config.get('slack', {}).get('verification_token'),
            'signing_secret': self.webhook_config.get('slack', {}).get('signing_secret'),
            'signature_header': 'X-Slack-Signature',
            'timestamp_header': 'X-Slack-Request-Timestamp'
        }
        
        self.log(f"Initialized {len(self.provider_configs)} webhook providers")
        
    def register_handler(self, event_type: str, handler: Union[Callable, WebhookHandler],
                        provider: Optional[str] = None) -> bool:
        """Webhook handler kaydet"""
        try:
            # Handler'ı WebhookHandler instance'ına dönüştür
            if not isinstance(handler, WebhookHandler):
                handler = WebhookHandler(event_type, handler)
                
            # Provider varsa event_type'a ekle
            if provider:
                key = f"{provider}:{event_type}"
            else:
                key = event_type
                
            self.handlers[key] = handler
            self.log(f"Webhook handler registered: {key}")
            return True
            
        except Exception as e:
            self.log(f"Handler registration error: {str(e)}", "error")
            return False
            
    async def process_webhook(self, provider: str, payload: Union[str, Dict], 
                            headers: Dict[str, str]) -> Dict[str, Any]:
        """Webhook işle"""
        webhook_id = str(uuid.uuid4())
        
        try:
            # Webhook kaydını oluştur
            webhook_record = {
                'id': webhook_id,
                'provider': provider,
                'status': WebhookStatus.PROCESSING.value,
                'received_at': datetime.now().isoformat(),
                'headers': headers,
                'retry_count': 0
            }
            
            # İmza doğrulama
            if not await self._verify_webhook_signature(provider, payload, headers):
                webhook_record['status'] = WebhookStatus.FAILED.value
                webhook_record['error'] = 'Invalid signature'
                await self._save_webhook_record(webhook_record)
                return self.error_response("Invalid webhook signature")
                
            # Payload'ı parse et
            if isinstance(payload, str):
                try:
                    payload_data = json.loads(payload)
                except json.JSONDecodeError:
                    payload_data = {'raw': payload}
            else:
                payload_data = payload
                
            webhook_record['payload'] = payload_data
            
            # Event type'ı belirle
            event_type = self._extract_event_type(provider, payload_data, headers)
            webhook_record['event_type'] = event_type
            
            # Handler'ı bul ve çalıştır
            handler_key = f"{provider}:{event_type}"
            handler = self.handlers.get(handler_key) or self.handlers.get(event_type)
            
            if not handler:
                # Genel provider handler'ı dene
                handler = self.handlers.get(provider)
                
            if handler:
                # Webhook'u işle
                result = await handler.handle(payload_data, headers)
                
                if result['status'] == 'success':
                    webhook_record['status'] = WebhookStatus.SUCCESS.value
                    webhook_record['result'] = result.get('result')
                    
                    # Başarılı webhook bildirimi
                    await self._send_webhook_notification(webhook_record, 'processed')
                    
                else:
                    webhook_record['status'] = WebhookStatus.FAILED.value
                    webhook_record['error'] = result.get('message')
                    
                    # Retry kuyruğuna ekle
                    if webhook_record['retry_count'] < 3:
                        await self._queue_for_retry(webhook_record)
                        
            else:
                self.log(f"No handler found for webhook: {handler_key}", "warning")
                webhook_record['status'] = WebhookStatus.FAILED.value
                webhook_record['error'] = 'No handler found'
                
            # Webhook kaydını sakla
            await self._save_webhook_record(webhook_record)
            
            # Cache'e ekle
            self.cache.set(f"webhook:{webhook_id}", webhook_record, 86400)  # 24 saat
            
            return self.success_response("Webhook processed", {
                'webhook_id': webhook_id,
                'status': webhook_record['status'],
                'event_type': event_type
            })
            
        except Exception as e:
            self.log(f"Webhook processing error: {str(e)}", "error")
            
            # Hata durumunda webhook kaydını güncelle
            if 'webhook_record' in locals():
                webhook_record['status'] = WebhookStatus.FAILED.value
                webhook_record['error'] = str(e)
                await self._save_webhook_record(webhook_record)
                
            return self.error_response(f"Webhook processing error: {str(e)}")
            
    async def _verify_webhook_signature(self, provider: str, payload: Union[str, Dict], 
                                      headers: Dict[str, str]) -> bool:
        """Webhook imzasını doğrula"""
        try:
            provider_config = self.provider_configs.get(provider, {})
            
            if provider == WebhookProvider.GITHUB.value:
                return await self._verify_github_signature(payload, headers, provider_config)
                
            elif provider == WebhookProvider.STRIPE.value:
                return await self._verify_stripe_signature(payload, headers, provider_config)
                
            elif provider == WebhookProvider.PAYPAL.value:
                return await self._verify_paypal_signature(payload, headers, provider_config)
                
            elif provider == WebhookProvider.SLACK.value:
                return await self._verify_slack_signature(payload, headers, provider_config)
                
            else:
                # Custom provider - basit HMAC doğrulama
                signature_header = provider_config.get('signature_header', 'X-Webhook-Signature')
                signature = headers.get(signature_header)
                secret = provider_config.get('secret')
                
                if not signature or not secret:
                    return True  # İmza yoksa doğrulama yapma
                    
                payload_str = json.dumps(payload) if isinstance(payload, dict) else payload
                expected_signature = hmac.new(
                    secret.encode(),
                    payload_str.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                return hmac.compare_digest(expected_signature, signature)
                
        except Exception as e:
            self.log(f"Signature verification error: {str(e)}", "error")
            return False
            
    async def _verify_github_signature(self, payload: Union[str, Dict], headers: Dict[str, str], 
                                     config: Dict[str, Any]) -> bool:
        """GitHub webhook imzası doğrula"""
        signature = headers.get(config.get('signature_header', 'X-Hub-Signature-256'))
        secret = config.get('secret')
        
        if not signature or not secret:
            return False
            
        payload_str = json.dumps(payload) if isinstance(payload, dict) else payload
        expected_signature = 'sha256=' + hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
        
    async def _verify_stripe_signature(self, payload: Union[str, Dict], headers: Dict[str, str], 
                                     config: Dict[str, Any]) -> bool:
        """Stripe webhook imzası doğrula"""
        signature = headers.get(config.get('signature_header', 'Stripe-Signature'))
        secret = config.get('secret')
        
        if not signature or not secret:
            return False
            
        # Stripe signature format: t=timestamp,v1=signature
        elements = {}
        for element in signature.split(','):
            key, value = element.split('=')
            elements[key] = value
            
        timestamp = elements.get('t')
        signatures = [v for k, v in elements.items() if k.startswith('v')]
        
        payload_str = json.dumps(payload) if isinstance(payload, dict) else payload
        signed_payload = f"{timestamp}.{payload_str}"
        
        expected_signature = hmac.new(
            secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return any(hmac.compare_digest(expected_signature, sig) for sig in signatures)
        
    async def _verify_paypal_signature(self, payload: Union[str, Dict], headers: Dict[str, str], 
                                     config: Dict[str, Any]) -> bool:
        """PayPal webhook imzası doğrula"""
        # PayPal webhook verification API kullanılmalı
        # Bu basit bir simülasyon
        return True
        
    async def _verify_slack_signature(self, payload: Union[str, Dict], headers: Dict[str, str], 
                                    config: Dict[str, Any]) -> bool:
        """Slack webhook imzası doğrula"""
        signature = headers.get(config.get('signature_header', 'X-Slack-Signature'))
        timestamp = headers.get(config.get('timestamp_header', 'X-Slack-Request-Timestamp'))
        secret = config.get('signing_secret')
        
        if not signature or not timestamp or not secret:
            return False
            
        # Timestamp kontrolü (5 dakikadan eski olmamalı)
        if abs(datetime.now().timestamp() - float(timestamp)) > 300:
            return False
            
        payload_str = json.dumps(payload) if isinstance(payload, dict) else payload
        sig_basestring = f"v0:{timestamp}:{payload_str}"
        
        expected_signature = 'v0=' + hmac.new(
            secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
        
    def _extract_event_type(self, provider: str, payload: Dict[str, Any], 
                          headers: Dict[str, str]) -> str:
        """Event type'ı çıkar"""
        if provider == WebhookProvider.GITHUB.value:
            return headers.get('X-GitHub-Event', 'unknown')
            
        elif provider == WebhookProvider.STRIPE.value:
            return payload.get('type', 'unknown')
            
        elif provider == WebhookProvider.PAYPAL.value:
            return payload.get('event_type', 'unknown')
            
        elif provider == WebhookProvider.SLACK.value:
            return payload.get('type', payload.get('event', {}).get('type', 'unknown'))
            
        else:
            # Payload'dan event type bulmaya çalış
            return (payload.get('event_type') or 
                   payload.get('event') or 
                   payload.get('type') or 
                   'unknown')
                   
    async def _queue_for_retry(self, webhook_record: Dict[str, Any]):
        """Webhook'u retry kuyruğuna ekle"""
        webhook_record['retry_count'] += 1
        webhook_record['status'] = WebhookStatus.RETRYING.value
        
        # Exponential backoff
        delay = min(300, 30 * (2 ** webhook_record['retry_count']))  # Max 5 dakika
        
        await self.queue.push('webhook_retry', {
            'webhook_record': webhook_record,
            'retry_at': (datetime.now() + timedelta(seconds=delay)).isoformat()
        })
        
        self.log(f"Webhook queued for retry: {webhook_record['id']} - Attempt {webhook_record['retry_count']}")
        
    async def retry_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Webhook'u yeniden dene"""
        try:
            # Cache'den webhook kaydını al
            webhook_record = self.cache.get(f"webhook:{webhook_id}")
            if not webhook_record:
                return self.error_response("Webhook not found")
                
            # Handler'ı bul
            provider = webhook_record['provider']
            event_type = webhook_record['event_type']
            handler_key = f"{provider}:{event_type}"
            handler = self.handlers.get(handler_key) or self.handlers.get(event_type)
            
            if handler:
                result = await handler.handle(webhook_record['payload'], webhook_record['headers'])
                
                if result['status'] == 'success':
                    webhook_record['status'] = WebhookStatus.SUCCESS.value
                    webhook_record['result'] = result.get('result')
                    webhook_record['retried_at'] = datetime.now().isoformat()
                else:
                    webhook_record['status'] = WebhookStatus.FAILED.value
                    webhook_record['error'] = result.get('message')
                    
                    # Daha fazla retry dene
                    if webhook_record['retry_count'] < 3:
                        await self._queue_for_retry(webhook_record)
                        
                # Kaydı güncelle
                await self._save_webhook_record(webhook_record)
                self.cache.set(f"webhook:{webhook_id}", webhook_record, 86400)
                
                return self.success_response("Webhook retry completed", {
                    'webhook_id': webhook_id,
                    'status': webhook_record['status'],
                    'retry_count': webhook_record['retry_count']
                })
            else:
                return self.error_response("Handler not found for webhook")
                
        except Exception as e:
            self.log(f"Webhook retry error: {str(e)}", "error")
            return self.error_response(f"Webhook retry error: {str(e)}")
            
    async def _save_webhook_record(self, webhook_record: Dict[str, Any]):
        """Webhook kaydını sakla"""
        # Veritabanına kaydet (simülasyon)
        self.log(f"Webhook record saved: {webhook_record['id']} - Status: {webhook_record['status']}")
        
    async def _send_webhook_notification(self, webhook_record: Dict[str, Any], action: str):
        """Webhook bildirimi gönder"""
        notification_data = {
            'title': f'Webhook {action.title()}',
            'message': f'{webhook_record["provider"]} webhook {action} - Event: {webhook_record.get("event_type", "unknown")}',
            'type': 'webhook',
            'data': {
                'webhook_id': webhook_record['id'],
                'provider': webhook_record['provider'],
                'event_type': webhook_record.get('event_type'),
                'action': action
            }
        }
        
        # Admin'e bildirim gönder
        await self.notification_service.send_to_user(
            'admin',  # Admin user ID
            notification_data
        )
        
    def create_webhook_endpoint(self, provider: str, config: Dict[str, Any] = None) -> str:
        """Webhook endpoint oluştur"""
        webhook_id = str(uuid.uuid4())
        endpoint_config = config or {}
        
        # Endpoint bilgilerini sakla
        endpoint_data = {
            'id': webhook_id,
            'provider': provider,
            'config': endpoint_config,
            'created_at': datetime.now().isoformat(),
            'active': True
        }
        
        self.cache.set(f"webhook_endpoint:{webhook_id}", endpoint_data, 0)  # Süresiz
        
        # Endpoint URL'i oluştur
        base_url = self.webhook_config.get('base_url', 'https://api.example.com')
        endpoint_url = f"{base_url}/webhooks/{provider}/{webhook_id}"
        
        self.log(f"Webhook endpoint created: {endpoint_url}")
        
        return endpoint_url
        
    async def list_webhooks(self, provider: Optional[str] = None, 
                          status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Webhook listesi"""
        # Veritabanından webhook kayıtlarını getir (simülasyon)
        webhooks = []
        
        # Cache'den son webhook'ları al
        for i in range(10):
            webhook_id = f"webhook:{uuid.uuid4()}"
            webhook = self.cache.get(webhook_id)
            if webhook:
                if provider and webhook.get('provider') != provider:
                    continue
                if status and webhook.get('status') != status:
                    continue
                webhooks.append(webhook)
                
        return webhooks
        
    async def get_webhook_analytics(self, start_date: datetime, end_date: datetime, 
                                  provider: Optional[str] = None) -> Dict[str, Any]:
        """Webhook analitiği"""
        # Analitik verileri topla (simülasyon)
        analytics = {
            'total_webhooks': 5420,
            'successful_webhooks': 5180,
            'failed_webhooks': 240,
            'retry_count': 120,
            'average_processing_time': 0.245,  # seconds
            'provider_breakdown': {
                'github': {'count': 2100, 'success_rate': 0.98},
                'stripe': {'count': 1500, 'success_rate': 0.96},
                'paypal': {'count': 800, 'success_rate': 0.94},
                'slack': {'count': 600, 'success_rate': 0.99},
                'other': {'count': 420, 'success_rate': 0.92}
            },
            'event_type_breakdown': {
                'payment.completed': 1200,
                'payment.failed': 300,
                'push': 800,
                'pull_request': 600,
                'message': 400,
                'other': 2120
            },
            'hourly_distribution': self._calculate_hourly_distribution(start_date, end_date),
            'error_types': {
                'invalid_signature': 80,
                'handler_not_found': 60,
                'processing_error': 50,
                'timeout': 30,
                'other': 20
            }
        }
        
        if provider:
            # Provider'a göre filtrele
            provider_data = analytics['provider_breakdown'].get(provider, {})
            analytics = {
                'provider': provider,
                'total_webhooks': provider_data.get('count', 0),
                'success_rate': provider_data.get('success_rate', 0),
                **analytics
            }
            
        return analytics
        
    def _calculate_hourly_distribution(self, start_date: datetime, 
                                     end_date: datetime) -> List[Dict[str, Any]]:
        """Saatlik dağılım hesapla"""
        distribution = []
        
        for hour in range(24):
            count = 200 + (hour * 10) + (50 if 9 <= hour <= 17 else 0)  # İş saatlerinde daha fazla
            distribution.append({
                'hour': hour,
                'count': count,
                'success_rate': 0.95 + (0.02 if 9 <= hour <= 17 else 0)
            })
            
        return distribution
        
    def register_batch_handler(self, event_types: List[str], handler: Callable, 
                             provider: Optional[str] = None):
        """Toplu webhook handler kaydet"""
        for event_type in event_types:
            self.register_handler(event_type, handler, provider)
            
    async def bulk_process_webhooks(self, webhooks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Toplu webhook işleme"""
        results = {
            'total': len(webhooks),
            'success': 0,
            'failed': 0,
            'results': []
        }
        
        # Paralel işleme için task'lar oluştur
        tasks = []
        for webhook in webhooks:
            task = self.process_webhook(
                webhook.get('provider', 'custom'),
                webhook.get('payload', {}),
                webhook.get('headers', {})
            )
            tasks.append(task)
            
        # Tüm task'ları çalıştır
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Sonuçları topla
        for i, result in enumerate(task_results):
            if isinstance(result, Exception):
                results['failed'] += 1
                results['results'].append({
                    'index': i,
                    'status': 'error',
                    'message': str(result)
                })
            else:
                if result.get('status') == 'success':
                    results['success'] += 1
                else:
                    results['failed'] += 1
                results['results'].append({
                    'index': i,
                    **result
                })
                
        return results


# Webhook handler dekoratörü
def webhook_handler(event_type: str, provider: Optional[str] = None):
    """Webhook handler dekoratörü"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
            
        # Handler'ı otomatik kaydet
        service = get_webhook_service()
        service.register_handler(event_type, wrapper, provider)
        
        return wrapper
    return decorator


# Global webhook service instance
_webhook_service = None

def get_webhook_service() -> WebhookIntegrationService:
    """Global webhook service instance'ını al"""
    global _webhook_service
    if _webhook_service is None:
        _webhook_service = WebhookIntegrationService()
    return _webhook_service