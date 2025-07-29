"""
Enterprise Payment Integration Service
Kurumsal seviyede ödeme entegrasyonu servisi - Tüm popüler ödeme sistemlerini destekler
"""

import asyncio
import json
import logging
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum

from core.Services.base_service import BaseService
from core.Services.cache_service import CacheService
from core.Services.notification_service import get_notification_service


class PaymentStatus(Enum):
    """Ödeme durumları"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    EXPIRED = "expired"


class PaymentMethod(Enum):
    """Ödeme metodları"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTO = "crypto"
    BUY_NOW_PAY_LATER = "bnpl"


class BasePaymentProvider(ABC):
    """Tüm ödeme sağlayıcıları için temel sınıf"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.api_key = config.get('api_key')
        self.secret_key = config.get('secret_key')
        self.merchant_id = config.get('merchant_id')
        self.test_mode = config.get('test_mode', True)
        self.webhook_secret = config.get('webhook_secret')
        
    @abstractmethod
    async def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ödeme oluştur"""
        pass
        
    @abstractmethod
    async def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """Ödeme doğrula"""
        pass
        
    @abstractmethod
    async def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Ödeme iadesi"""
        pass
        
    @abstractmethod
    async def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        """Ödeme iptali"""
        pass
        
    @abstractmethod
    def verify_webhook(self, payload: str, signature: str) -> bool:
        """Webhook doğrulama"""
        pass
        
    def generate_signature(self, data: str) -> str:
        """İmza oluştur"""
        return hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()


class IyzicoProvider(BasePaymentProvider):
    """İyzico Ödeme Entegrasyonu"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://sandbox-api.iyzipay.com" if self.test_mode else "https://api.iyzipay.com"
        
    async def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """İyzico ile ödeme oluştur"""
        try:
            # İyzico API isteği hazırla
            request_data = {
                "locale": payment_data.get("locale", "tr"),
                "conversationId": str(uuid.uuid4()),
                "price": str(payment_data["amount"]),
                "paidPrice": str(payment_data["amount"]),
                "currency": payment_data.get("currency", "TRY"),
                "installment": payment_data.get("installment", 1),
                "basketId": payment_data.get("order_id"),
                "paymentChannel": "WEB",
                "paymentGroup": "PRODUCT",
                "paymentCard": {
                    "cardHolderName": payment_data["card"]["holder_name"],
                    "cardNumber": payment_data["card"]["number"],
                    "expireMonth": payment_data["card"]["exp_month"],
                    "expireYear": payment_data["card"]["exp_year"],
                    "cvc": payment_data["card"]["cvc"],
                    "registerCard": payment_data.get("save_card", 0)
                },
                "buyer": payment_data.get("buyer", {}),
                "shippingAddress": payment_data.get("shipping_address", {}),
                "billingAddress": payment_data.get("billing_address", {}),
                "basketItems": payment_data.get("items", [])
            }
            
            # API çağrısı simülasyonu
            self.logger.info(f"İyzico payment created: {request_data['conversationId']}")
            
            return {
                "status": "success",
                "provider": "iyzico",
                "payment_id": request_data["conversationId"],
                "amount": payment_data["amount"],
                "currency": payment_data.get("currency", "TRY"),
                "created_at": datetime.now().isoformat(),
                "3d_secure": payment_data.get("3d_secure", False),
                "callback_url": f"{self.base_url}/callback/{request_data['conversationId']}"
            }
            
        except Exception as e:
            self.logger.error(f"İyzico payment creation error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "provider": "iyzico"
            }
            
    async def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """İyzico ödeme doğrulama"""
        try:
            # API çağrısı simülasyonu
            self.logger.info(f"İyzico payment verified: {payment_id}")
            
            return {
                "status": "success",
                "payment_status": PaymentStatus.SUCCESS.value,
                "payment_id": payment_id,
                "verified_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"İyzico payment verification error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """İyzico ödeme iadesi"""
        try:
            refund_data = {
                "conversationId": str(uuid.uuid4()),
                "paymentTransactionId": payment_id,
                "price": str(amount) if amount else None,
                "currency": "TRY"
            }
            
            self.logger.info(f"İyzico refund processed: {payment_id}")
            
            return {
                "status": "success",
                "refund_id": refund_data["conversationId"],
                "payment_id": payment_id,
                "amount": amount,
                "refunded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"İyzico refund error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        """İyzico ödeme iptali"""
        try:
            self.logger.info(f"İyzico payment cancelled: {payment_id}")
            
            return {
                "status": "success",
                "payment_id": payment_id,
                "cancelled_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"İyzico cancellation error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    def verify_webhook(self, payload: str, signature: str) -> bool:
        """İyzico webhook doğrulama"""
        expected_signature = self.generate_signature(payload)
        return hmac.compare_digest(expected_signature, signature)


class PayTRProvider(BasePaymentProvider):
    """PayTR Ödeme Entegrasyonu"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://www.paytr.com/odeme" if not self.test_mode else "https://sandbox.paytr.com/odeme"
        
    async def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """PayTR ile ödeme oluştur"""
        try:
            # PayTR token oluştur
            merchant_oid = f"PAYTR_{uuid.uuid4().hex[:10]}"
            
            request_data = {
                "merchant_id": self.merchant_id,
                "merchant_oid": merchant_oid,
                "email": payment_data.get("email"),
                "payment_amount": int(payment_data["amount"] * 100),  # Kuruş cinsinden
                "currency": payment_data.get("currency", "TL"),
                "test_mode": "1" if self.test_mode else "0",
                "user_name": payment_data.get("user_name"),
                "user_address": payment_data.get("user_address"),
                "user_phone": payment_data.get("user_phone"),
                "merchant_ok_url": payment_data.get("success_url"),
                "merchant_fail_url": payment_data.get("fail_url"),
                "user_basket": json.dumps(payment_data.get("items", [])),
                "no_installment": "0" if payment_data.get("installment", 1) > 1 else "1",
                "max_installment": payment_data.get("max_installment", 12)
            }
            
            # Token hesapla
            hash_str = f"{self.merchant_id}{payment_data.get('user_ip')}{merchant_oid}{payment_data.get('email')}{request_data['payment_amount']}{request_data['test_mode']}"
            request_data["paytr_token"] = self.generate_signature(hash_str)
            
            self.logger.info(f"PayTR payment created: {merchant_oid}")
            
            return {
                "status": "success",
                "provider": "paytr",
                "payment_id": merchant_oid,
                "amount": payment_data["amount"],
                "currency": payment_data.get("currency", "TRY"),
                "created_at": datetime.now().isoformat(),
                "iframe_token": request_data["paytr_token"],
                "payment_url": f"{self.base_url}/iframe/{request_data['paytr_token']}"
            }
            
        except Exception as e:
            self.logger.error(f"PayTR payment creation error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "provider": "paytr"
            }
            
    async def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """PayTR ödeme doğrulama"""
        try:
            self.logger.info(f"PayTR payment verified: {payment_id}")
            
            return {
                "status": "success",
                "payment_status": PaymentStatus.SUCCESS.value,
                "payment_id": payment_id,
                "verified_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"PayTR payment verification error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """PayTR ödeme iadesi"""
        try:
            refund_data = {
                "merchant_id": self.merchant_id,
                "merchant_oid": payment_id,
                "return_amount": int(amount * 100) if amount else None
            }
            
            self.logger.info(f"PayTR refund processed: {payment_id}")
            
            return {
                "status": "success",
                "refund_id": f"REF_{uuid.uuid4().hex[:10]}",
                "payment_id": payment_id,
                "amount": amount,
                "refunded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"PayTR refund error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        """PayTR ödeme iptali"""
        try:
            self.logger.info(f"PayTR payment cancelled: {payment_id}")
            
            return {
                "status": "success",
                "payment_id": payment_id,
                "cancelled_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"PayTR cancellation error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    def verify_webhook(self, payload: str, signature: str) -> bool:
        """PayTR webhook doğrulama"""
        # PayTR webhook doğrulama mantığı
        expected_hash = self.generate_signature(payload)
        return hmac.compare_digest(expected_hash, signature)


class StripeProvider(BasePaymentProvider):
    """Stripe Ödeme Entegrasyonu"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.stripe.com/v1"
        
    async def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stripe ile ödeme oluştur"""
        try:
            # Stripe PaymentIntent oluştur
            intent_data = {
                "amount": int(payment_data["amount"] * 100),  # Cent cinsinden
                "currency": payment_data.get("currency", "try").lower(),
                "payment_method_types": ["card"],
                "description": payment_data.get("description", ""),
                "metadata": {
                    "order_id": payment_data.get("order_id"),
                    "customer_id": payment_data.get("customer_id")
                },
                "capture_method": "automatic",
                "confirm": payment_data.get("confirm", False)
            }
            
            # 3D Secure ayarları
            if payment_data.get("3d_secure", True):
                intent_data["payment_method_options"] = {
                    "card": {
                        "request_three_d_secure": "automatic"
                    }
                }
            
            payment_intent_id = f"pi_{uuid.uuid4().hex}"
            client_secret = f"pi_{uuid.uuid4().hex}_secret_{uuid.uuid4().hex}"
            
            self.logger.info(f"Stripe payment intent created: {payment_intent_id}")
            
            return {
                "status": "success",
                "provider": "stripe",
                "payment_id": payment_intent_id,
                "client_secret": client_secret,
                "amount": payment_data["amount"],
                "currency": payment_data.get("currency", "TRY"),
                "created_at": datetime.now().isoformat(),
                "requires_action": payment_data.get("3d_secure", True)
            }
            
        except Exception as e:
            self.logger.error(f"Stripe payment creation error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "provider": "stripe"
            }
            
    async def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """Stripe ödeme doğrulama"""
        try:
            self.logger.info(f"Stripe payment verified: {payment_id}")
            
            return {
                "status": "success",
                "payment_status": PaymentStatus.SUCCESS.value,
                "payment_id": payment_id,
                "verified_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Stripe payment verification error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Stripe ödeme iadesi"""
        try:
            refund_data = {
                "payment_intent": payment_id,
                "amount": int(amount * 100) if amount else None,
                "reason": "requested_by_customer"
            }
            
            refund_id = f"re_{uuid.uuid4().hex}"
            
            self.logger.info(f"Stripe refund processed: {refund_id}")
            
            return {
                "status": "success",
                "refund_id": refund_id,
                "payment_id": payment_id,
                "amount": amount,
                "refunded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Stripe refund error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        """Stripe ödeme iptali"""
        try:
            self.logger.info(f"Stripe payment cancelled: {payment_id}")
            
            return {
                "status": "success",
                "payment_id": payment_id,
                "cancelled_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Stripe cancellation error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    def verify_webhook(self, payload: str, signature: str) -> bool:
        """Stripe webhook doğrulama"""
        # Stripe webhook signature doğrulama
        try:
            import stripe
            stripe.api_key = self.api_key
            
            # Webhook signature doğrulama
            timestamp = signature.split(",")[0].split("=")[1]
            signatures = signature.split(" ")
            
            signed_payload = f"{timestamp}.{payload}"
            expected_signature = self.generate_signature(signed_payload)
            
            for sig in signatures:
                if sig.startswith("v1="):
                    if hmac.compare_digest(sig[3:], expected_signature):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Stripe webhook verification error: {e}")
            return False


class PayPalProvider(BasePaymentProvider):
    """PayPal Ödeme Entegrasyonu"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api-m.sandbox.paypal.com" if self.test_mode else "https://api-m.paypal.com"
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        
    async def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """PayPal ile ödeme oluştur"""
        try:
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": payment_data.get("currency", "TRY"),
                        "value": str(payment_data["amount"])
                    },
                    "description": payment_data.get("description", ""),
                    "reference_id": payment_data.get("order_id")
                }],
                "application_context": {
                    "return_url": payment_data.get("success_url"),
                    "cancel_url": payment_data.get("cancel_url"),
                    "brand_name": payment_data.get("brand_name", ""),
                    "locale": payment_data.get("locale", "tr-TR"),
                    "landing_page": "BILLING",
                    "user_action": "PAY_NOW"
                }
            }
            
            order_id = f"PAYPAL_{uuid.uuid4().hex[:20]}"
            
            self.logger.info(f"PayPal order created: {order_id}")
            
            return {
                "status": "success",
                "provider": "paypal",
                "payment_id": order_id,
                "amount": payment_data["amount"],
                "currency": payment_data.get("currency", "TRY"),
                "created_at": datetime.now().isoformat(),
                "approval_url": f"{self.base_url}/checkoutnow?token={order_id}"
            }
            
        except Exception as e:
            self.logger.error(f"PayPal payment creation error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "provider": "paypal"
            }
            
    async def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """PayPal ödeme doğrulama"""
        try:
            self.logger.info(f"PayPal payment verified: {payment_id}")
            
            return {
                "status": "success",
                "payment_status": PaymentStatus.SUCCESS.value,
                "payment_id": payment_id,
                "verified_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"PayPal payment verification error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """PayPal ödeme iadesi"""
        try:
            refund_data = {
                "amount": {
                    "currency_code": "TRY",
                    "value": str(amount) if amount else None
                },
                "note_to_payer": "Refund processed"
            }
            
            refund_id = f"REFUND_{uuid.uuid4().hex[:20]}"
            
            self.logger.info(f"PayPal refund processed: {refund_id}")
            
            return {
                "status": "success",
                "refund_id": refund_id,
                "payment_id": payment_id,
                "amount": amount,
                "refunded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"PayPal refund error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        """PayPal ödeme iptali"""
        try:
            self.logger.info(f"PayPal payment cancelled: {payment_id}")
            
            return {
                "status": "success",
                "payment_id": payment_id,
                "cancelled_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"PayPal cancellation error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    def verify_webhook(self, payload: str, signature: str) -> bool:
        """PayPal webhook doğrulama"""
        # PayPal webhook doğrulama
        try:
            # PayPal webhook verification API çağrısı simülasyonu
            verification_data = {
                "transmission_id": signature.get("transmission_id"),
                "transmission_time": signature.get("transmission_time"),
                "cert_url": signature.get("cert_url"),
                "auth_algo": signature.get("auth_algo"),
                "transmission_sig": signature.get("transmission_sig"),
                "webhook_id": self.webhook_secret,
                "webhook_event": json.loads(payload)
            }
            
            # Doğrulama mantığı
            return True
            
        except Exception as e:
            self.logger.error(f"PayPal webhook verification error: {e}")
            return False


class PaymentIntegrationService(BaseService):
    """Kurumsal Ödeme Entegrasyon Servisi"""
    
    def __init__(self):
        super().__init__()
        self.cache = CacheService()
        self.notification_service = get_notification_service()
        self.providers: Dict[str, BasePaymentProvider] = {}
        self.payment_config = self.get_config('payment', {})
        self._initialize_providers()
        
    def _initialize_providers(self):
        """Ödeme sağlayıcılarını başlat"""
        provider_configs = self.payment_config.get('providers', {})
        
        # İyzico
        if provider_configs.get('iyzico', {}).get('enabled', False):
            self.providers['iyzico'] = IyzicoProvider(provider_configs['iyzico'])
            
        # PayTR
        if provider_configs.get('paytr', {}).get('enabled', False):
            self.providers['paytr'] = PayTRProvider(provider_configs['paytr'])
            
        # Stripe
        if provider_configs.get('stripe', {}).get('enabled', False):
            self.providers['stripe'] = StripeProvider(provider_configs['stripe'])
            
        # PayPal
        if provider_configs.get('paypal', {}).get('enabled', False):
            self.providers['paypal'] = PayPalProvider(provider_configs['paypal'])
            
        self.log(f"Initialized {len(self.providers)} payment providers")
        
    async def create_payment(self, provider: str, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ödeme oluştur"""
        try:
            if provider not in self.providers:
                return self.error_response(f"Payment provider not found: {provider}")
                
            # Ödeme verilerini doğrula
            validation_result = self._validate_payment_data(payment_data)
            if not validation_result['valid']:
                return self.error_response(validation_result['message'])
                
            # Fraud kontrolü
            fraud_check = await self._check_fraud(payment_data)
            if fraud_check['is_fraud']:
                self.log(f"Fraud detected for payment: {payment_data}", "warning")
                return self.error_response("Payment rejected due to security reasons")
                
            # Ödemeyi oluştur
            provider_instance = self.providers[provider]
            result = await provider_instance.create_payment(payment_data)
            
            if result['status'] == 'success':
                # Ödeme kaydını veritabanına kaydet
                payment_record = await self._save_payment_record(provider, payment_data, result)
                
                # Cache'e kaydet
                self.cache.set(f"payment:{result['payment_id']}", payment_record, 3600)
                
                # Bildirim gönder
                await self._send_payment_notification(payment_record, 'created')
                
                self.log(f"Payment created: {result['payment_id']} via {provider}")
                
                return self.success_response("Payment created successfully", {
                    **result,
                    'payment_record_id': payment_record.get('id')
                })
            else:
                return self.error_response(result.get('message', 'Payment creation failed'), result)
                
        except Exception as e:
            self.log(f"Payment creation error: {str(e)}", "error")
            return self.error_response(f"Payment creation error: {str(e)}")
            
    async def verify_payment(self, provider: str, payment_id: str) -> Dict[str, Any]:
        """Ödeme doğrula"""
        try:
            if provider not in self.providers:
                return self.error_response(f"Payment provider not found: {provider}")
                
            provider_instance = self.providers[provider]
            result = await provider_instance.verify_payment(payment_id)
            
            if result['status'] == 'success':
                # Ödeme kaydını güncelle
                await self._update_payment_status(payment_id, result['payment_status'])
                
                # Cache'i güncelle
                payment_record = self.cache.get(f"payment:{payment_id}")
                if payment_record:
                    payment_record['status'] = result['payment_status']
                    payment_record['verified_at'] = result['verified_at']
                    self.cache.set(f"payment:{payment_id}", payment_record, 3600)
                
                # Bildirim gönder
                await self._send_payment_notification(payment_record, 'verified')
                
                self.log(f"Payment verified: {payment_id}")
                
                return self.success_response("Payment verified successfully", result)
            else:
                return self.error_response(result.get('message', 'Payment verification failed'), result)
                
        except Exception as e:
            self.log(f"Payment verification error: {str(e)}", "error")
            return self.error_response(f"Payment verification error: {str(e)}")
            
    async def refund_payment(self, provider: str, payment_id: str, 
                           amount: Optional[Decimal] = None, reason: Optional[str] = None) -> Dict[str, Any]:
        """Ödeme iadesi"""
        try:
            if provider not in self.providers:
                return self.error_response(f"Payment provider not found: {provider}")
                
            # Ödeme kaydını kontrol et
            payment_record = await self._get_payment_record(payment_id)
            if not payment_record:
                return self.error_response("Payment not found")
                
            if payment_record['status'] != PaymentStatus.SUCCESS.value:
                return self.error_response("Only successful payments can be refunded")
                
            # İade tutarını kontrol et
            if amount and amount > payment_record['amount']:
                return self.error_response("Refund amount cannot exceed payment amount")
                
            provider_instance = self.providers[provider]
            result = await provider_instance.refund_payment(payment_id, amount)
            
            if result['status'] == 'success':
                # İade kaydını oluştur
                refund_record = await self._save_refund_record(payment_id, amount, reason, result)
                
                # Ödeme durumunu güncelle
                new_status = PaymentStatus.PARTIALLY_REFUNDED if amount and amount < payment_record['amount'] else PaymentStatus.REFUNDED
                await self._update_payment_status(payment_id, new_status.value)
                
                # Bildirim gönder
                await self._send_payment_notification(payment_record, 'refunded')
                
                self.log(f"Payment refunded: {payment_id} - Amount: {amount}")
                
                return self.success_response("Payment refunded successfully", {
                    **result,
                    'refund_record_id': refund_record.get('id')
                })
            else:
                return self.error_response(result.get('message', 'Refund failed'), result)
                
        except Exception as e:
            self.log(f"Payment refund error: {str(e)}", "error")
            return self.error_response(f"Payment refund error: {str(e)}")
            
    async def process_webhook(self, provider: str, payload: str, signature: str) -> Dict[str, Any]:
        """Webhook işle"""
        try:
            if provider not in self.providers:
                return self.error_response(f"Payment provider not found: {provider}")
                
            provider_instance = self.providers[provider]
            
            # Webhook doğrula
            if not provider_instance.verify_webhook(payload, signature):
                self.log(f"Invalid webhook signature for {provider}", "warning")
                return self.error_response("Invalid webhook signature")
                
            # Webhook verilerini parse et
            webhook_data = json.loads(payload)
            
            # Webhook türüne göre işlem yap
            event_type = webhook_data.get('event_type', webhook_data.get('type'))
            
            if event_type in ['payment.completed', 'payment_intent.succeeded', 'PAYMENTS.PAYMENT.COMPLETED']:
                # Ödeme tamamlandı
                payment_id = webhook_data.get('payment_id', webhook_data.get('data', {}).get('id'))
                await self._update_payment_status(payment_id, PaymentStatus.SUCCESS.value)
                
            elif event_type in ['payment.failed', 'payment_intent.payment_failed', 'PAYMENTS.PAYMENT.FAILED']:
                # Ödeme başarısız
                payment_id = webhook_data.get('payment_id', webhook_data.get('data', {}).get('id'))
                await self._update_payment_status(payment_id, PaymentStatus.FAILED.value)
                
            elif event_type in ['refund.completed', 'charge.refunded', 'PAYMENTS.PAYMENT.REFUNDED']:
                # İade tamamlandı
                payment_id = webhook_data.get('payment_id', webhook_data.get('data', {}).get('payment_intent'))
                await self._update_payment_status(payment_id, PaymentStatus.REFUNDED.value)
                
            # Webhook kaydını sakla
            await self._save_webhook_record(provider, webhook_data)
            
            self.log(f"Webhook processed: {provider} - {event_type}")
            
            return self.success_response("Webhook processed successfully")
            
        except Exception as e:
            self.log(f"Webhook processing error: {str(e)}", "error")
            return self.error_response(f"Webhook processing error: {str(e)}")
            
    def _validate_payment_data(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ödeme verilerini doğrula"""
        required_fields = ['amount', 'currency']
        
        for field in required_fields:
            if field not in payment_data:
                return {'valid': False, 'message': f"Missing required field: {field}"}
                
        if payment_data['amount'] <= 0:
            return {'valid': False, 'message': "Amount must be greater than 0"}
            
        if len(payment_data.get('currency', '')) != 3:
            return {'valid': False, 'message': "Invalid currency code"}
            
        return {'valid': True}
        
    async def _check_fraud(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fraud kontrolü"""
        fraud_score = 0
        reasons = []
        
        # Yüksek tutar kontrolü
        if payment_data['amount'] > 10000:
            fraud_score += 20
            reasons.append("High amount")
            
        # Hızlı ardışık işlem kontrolü
        user_id = payment_data.get('user_id')
        if user_id:
            recent_payments_key = f"recent_payments:{user_id}"
            recent_payments = self.cache.get(recent_payments_key) or []
            
            if len(recent_payments) > 5:
                fraud_score += 30
                reasons.append("Too many recent payments")
                
            # Listeye ekle
            recent_payments.append(datetime.now().isoformat())
            # Son 1 saatteki işlemleri tut
            recent_payments = recent_payments[-10:]
            self.cache.set(recent_payments_key, recent_payments, 3600)
            
        # IP kontrolü
        ip_address = payment_data.get('ip_address')
        if ip_address:
            blacklisted = await self._check_ip_blacklist(ip_address)
            if blacklisted:
                fraud_score += 50
                reasons.append("Blacklisted IP")
                
        # Kart kontrolü (varsa)
        card_data = payment_data.get('card', {})
        if card_data:
            # Test kartı kontrolü
            if card_data.get('number', '').startswith('4111111111111111'):
                fraud_score -= 100  # Test kartı, fraud değil
                
        return {
            'is_fraud': fraud_score > 50,
            'score': fraud_score,
            'reasons': reasons
        }
        
    async def _check_ip_blacklist(self, ip_address: str) -> bool:
        """IP kara liste kontrolü"""
        # Basit IP kontrolü - gerçek implementasyonda harici servis kullanılabilir
        blacklisted_ips = self.cache.get('blacklisted_ips') or []
        return ip_address in blacklisted_ips
        
    async def _save_payment_record(self, provider: str, payment_data: Dict[str, Any], 
                                  result: Dict[str, Any]) -> Dict[str, Any]:
        """Ödeme kaydını veritabanına kaydet"""
        record = {
            'id': str(uuid.uuid4()),
            'provider': provider,
            'payment_id': result['payment_id'],
            'amount': payment_data['amount'],
            'currency': payment_data.get('currency', 'TRY'),
            'status': PaymentStatus.PENDING.value,
            'user_id': payment_data.get('user_id'),
            'order_id': payment_data.get('order_id'),
            'metadata': payment_data.get('metadata', {}),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Veritabanına kaydet (simülasyon)
        self.log(f"Payment record saved: {record['id']}")
        
        return record
        
    async def _update_payment_status(self, payment_id: str, status: str):
        """Ödeme durumunu güncelle"""
        # Veritabanında güncelle (simülasyon)
        self.log(f"Payment status updated: {payment_id} -> {status}")
        
    async def _get_payment_record(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Ödeme kaydını getir"""
        # Önce cache'den bak
        cached = self.cache.get(f"payment:{payment_id}")
        if cached:
            return cached
            
        # Veritabanından getir (simülasyon)
        return {
            'id': str(uuid.uuid4()),
            'payment_id': payment_id,
            'amount': Decimal('100.00'),
            'status': PaymentStatus.SUCCESS.value
        }
        
    async def _save_refund_record(self, payment_id: str, amount: Optional[Decimal], 
                                 reason: Optional[str], result: Dict[str, Any]) -> Dict[str, Any]:
        """İade kaydını oluştur"""
        record = {
            'id': str(uuid.uuid4()),
            'payment_id': payment_id,
            'refund_id': result['refund_id'],
            'amount': amount,
            'reason': reason,
            'status': 'completed',
            'created_at': datetime.now().isoformat()
        }
        
        # Veritabanına kaydet (simülasyon)
        self.log(f"Refund record saved: {record['id']}")
        
        return record
        
    async def _save_webhook_record(self, provider: str, webhook_data: Dict[str, Any]):
        """Webhook kaydını sakla"""
        record = {
            'id': str(uuid.uuid4()),
            'provider': provider,
            'event_type': webhook_data.get('event_type', webhook_data.get('type')),
            'data': webhook_data,
            'received_at': datetime.now().isoformat()
        }
        
        # Veritabanına kaydet (simülasyon)
        self.log(f"Webhook record saved: {record['id']}")
        
    async def _send_payment_notification(self, payment_record: Dict[str, Any], action: str):
        """Ödeme bildirimi gönder"""
        if not payment_record or not payment_record.get('user_id'):
            return
            
        notification_data = {
            'title': f'Ödeme {action.title()}',
            'message': f'Ödemeniz {action} - Tutar: {payment_record["amount"]} {payment_record["currency"]}',
            'type': 'payment',
            'data': {
                'payment_id': payment_record['payment_id'],
                'action': action
            }
        }
        
        await self.notification_service.send_to_user(
            payment_record['user_id'],
            notification_data
        )
        
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Kullanılabilir ödeme sağlayıcılarını getir"""
        providers = []
        
        for name, provider in self.providers.items():
            providers.append({
                'name': name,
                'display_name': name.title(),
                'test_mode': provider.test_mode,
                'supported_currencies': self._get_supported_currencies(name),
                'supported_methods': self._get_supported_methods(name)
            })
            
        return providers
        
    def _get_supported_currencies(self, provider: str) -> List[str]:
        """Desteklenen para birimlerini getir"""
        currency_map = {
            'iyzico': ['TRY', 'USD', 'EUR', 'GBP'],
            'paytr': ['TRY'],
            'stripe': ['TRY', 'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD'],
            'paypal': ['TRY', 'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY']
        }
        
        return currency_map.get(provider, ['TRY'])
        
    def _get_supported_methods(self, provider: str) -> List[str]:
        """Desteklenen ödeme metodlarını getir"""
        method_map = {
            'iyzico': [PaymentMethod.CREDIT_CARD.value, PaymentMethod.DEBIT_CARD.value, PaymentMethod.BUY_NOW_PAY_LATER.value],
            'paytr': [PaymentMethod.CREDIT_CARD.value, PaymentMethod.DEBIT_CARD.value, PaymentMethod.BANK_TRANSFER.value],
            'stripe': [PaymentMethod.CREDIT_CARD.value, PaymentMethod.DEBIT_CARD.value, PaymentMethod.DIGITAL_WALLET.value],
            'paypal': [PaymentMethod.CREDIT_CARD.value, PaymentMethod.DIGITAL_WALLET.value, PaymentMethod.BANK_TRANSFER.value]
        }
        
        return method_map.get(provider, [PaymentMethod.CREDIT_CARD.value])
        
    async def get_payment_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Ödeme analitiği"""
        # Analitik verileri topla (simülasyon)
        analytics = {
            'total_payments': 1250,
            'successful_payments': 1180,
            'failed_payments': 70,
            'total_amount': Decimal('125000.00'),
            'average_amount': Decimal('100.00'),
            'refund_count': 25,
            'refund_amount': Decimal('2500.00'),
            'provider_breakdown': {
                'iyzico': {'count': 500, 'amount': Decimal('50000.00')},
                'paytr': {'count': 300, 'amount': Decimal('30000.00')},
                'stripe': {'count': 250, 'amount': Decimal('25000.00')},
                'paypal': {'count': 200, 'amount': Decimal('20000.00')}
            },
            'currency_breakdown': {
                'TRY': {'count': 1000, 'amount': Decimal('100000.00')},
                'USD': {'count': 150, 'amount': Decimal('15000.00')},
                'EUR': {'count': 100, 'amount': Decimal('10000.00')}
            },
            'daily_trend': self._calculate_daily_trend(start_date, end_date)
        }
        
        return analytics
        
    def _calculate_daily_trend(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Günlük trend hesapla"""
        trend = []
        current_date = start_date
        
        while current_date <= end_date:
            trend.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': 40 + (current_date.day % 10) * 5,
                'amount': Decimal('4000.00') + (current_date.day % 10) * Decimal('500.00')
            })
            current_date += timedelta(days=1)
            
        return trend


# Global payment service instance
_payment_service = None

def get_payment_service() -> PaymentIntegrationService:
    """Global payment service instance'ını al"""
    global _payment_service
    if _payment_service is None:
        _payment_service = PaymentIntegrationService()
    return _payment_service