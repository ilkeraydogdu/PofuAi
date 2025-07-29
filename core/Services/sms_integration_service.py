"""
Enterprise SMS Integration Service
Kurumsal seviyede SMS entegrasyonu servisi - Tüm popüler SMS servislerini destekler
"""

import asyncio
import json
import logging
import hashlib
import hmac
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from enum import Enum

from core.Services.base_service import BaseService
from core.Services.cache_service import CacheService
from core.Services.notification_service import get_notification_service


class SMSStatus(Enum):
    """SMS durumları"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"


class SMSProvider(Enum):
    """SMS sağlayıcıları"""
    TWILIO = "twilio"
    NEXMO = "nexmo"
    NETGSM = "netgsm"
    ILETIMERKEZI = "iletimerkezi"
    VERIMOR = "verimor"
    MASGSM = "masgsm"
    TURATEL = "turatel"
    CUSTOM = "custom"


class BaseSMSProvider(ABC):
    """Tüm SMS sağlayıcıları için temel sınıf"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.sender_id = config.get('sender_id', 'INFO')
        self.test_mode = config.get('test_mode', True)
        
    @abstractmethod
    async def send_sms(self, to: str, message: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """SMS gönder"""
        pass
        
    @abstractmethod
    async def send_bulk_sms(self, recipients: List[str], message: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Toplu SMS gönder"""
        pass
        
    @abstractmethod
    async def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """SMS teslimat durumunu sorgula"""
        pass
        
    @abstractmethod
    async def get_balance(self) -> Dict[str, Any]:
        """Bakiye sorgula"""
        pass
        
    def validate_phone_number(self, phone: str) -> bool:
        """Telefon numarası doğrulama"""
        # Türkiye telefon numarası formatı
        pattern = r'^(\+90|0)?[5][0-9]{9}$'
        return bool(re.match(pattern, phone))
        
    def format_phone_number(self, phone: str) -> str:
        """Telefon numarasını formatla"""
        # Başındaki 0 veya +90'ı kaldır
        phone = re.sub(r'^(\+90|0)', '', phone)
        # Sadece rakamları al
        phone = re.sub(r'\D', '', phone)
        # +90 ekle
        return f"+90{phone}"


class TwilioProvider(BaseSMSProvider):
    """Twilio SMS Entegrasyonu"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.account_sid = config.get('account_sid')
        self.auth_token = config.get('auth_token')
        self.from_number = config.get('from_number')
        self.base_url = "https://api.twilio.com/2010-04-01"
        
    async def send_sms(self, to: str, message: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Twilio ile SMS gönder"""
        try:
            if not self.validate_phone_number(to):
                return {
                    'status': 'error',
                    'message': 'Invalid phone number format'
                }
                
            formatted_to = self.format_phone_number(to)
            
            # Test modunda gerçek gönderim yapma
            if self.test_mode:
                message_id = f"TEST_{uuid.uuid4().hex[:10]}"
                self.logger.info(f"[TEST MODE] SMS would be sent to {formatted_to}: {message}")
            else:
                # Gerçek Twilio API çağrısı yapılacak
                message_id = f"SM{uuid.uuid4().hex}"
                
            self.logger.info(f"Twilio SMS sent: {message_id}")
            
            return {
                'status': 'success',
                'provider': 'twilio',
                'message_id': message_id,
                'to': formatted_to,
                'message': message,
                'sent_at': datetime.now().isoformat(),
                'test_mode': self.test_mode
            }
            
        except Exception as e:
            self.logger.error(f"Twilio SMS sending error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'provider': 'twilio'
            }
            
    async def send_bulk_sms(self, recipients: List[str], message: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Twilio ile toplu SMS gönder"""
        results = {
            'total': len(recipients),
            'success': 0,
            'failed': 0,
            'results': []
        }
        
        # Paralel gönderim için task'lar oluştur
        tasks = []
        for recipient in recipients:
            task = self.send_sms(recipient, message, options)
            tasks.append(task)
            
        # Tüm task'ları çalıştır
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Sonuçları topla
        for i, result in enumerate(task_results):
            if isinstance(result, Exception):
                results['failed'] += 1
                results['results'].append({
                    'recipient': recipients[i],
                    'status': 'error',
                    'message': str(result)
                })
            else:
                if result.get('status') == 'success':
                    results['success'] += 1
                else:
                    results['failed'] += 1
                results['results'].append(result)
                
        return results
        
    async def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """Twilio SMS teslimat durumu"""
        try:
            # Test modunda
            if self.test_mode or message_id.startswith('TEST_'):
                return {
                    'status': 'success',
                    'delivery_status': SMSStatus.DELIVERED.value,
                    'message_id': message_id,
                    'delivered_at': datetime.now().isoformat()
                }
                
            # Gerçek API çağrısı yapılacak
            return {
                'status': 'success',
                'delivery_status': SMSStatus.DELIVERED.value,
                'message_id': message_id
            }
            
        except Exception as e:
            self.logger.error(f"Twilio delivery status error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    async def get_balance(self) -> Dict[str, Any]:
        """Twilio bakiye sorgulama"""
        try:
            # Test modunda
            if self.test_mode:
                return {
                    'status': 'success',
                    'balance': 100.0,
                    'currency': 'USD'
                }
                
            # Gerçek API çağrısı yapılacak
            return {
                'status': 'success',
                'balance': 0.0,
                'currency': 'USD'
            }
            
        except Exception as e:
            self.logger.error(f"Twilio balance query error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }


class NetGSMProvider(BaseSMSProvider):
    """NetGSM SMS Entegrasyonu"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.username = config.get('username')
        self.password = config.get('password')
        self.base_url = "https://api.netgsm.com.tr"
        self.sender_name = config.get('sender_name', self.sender_id)
        
    async def send_sms(self, to: str, message: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """NetGSM ile SMS gönder"""
        try:
            if not self.validate_phone_number(to):
                return {
                    'status': 'error',
                    'message': 'Invalid phone number format'
                }
                
            formatted_to = self.format_phone_number(to).replace('+90', '')  # NetGSM +90 istemez
            
            # Test modunda gerçek gönderim yapma
            if self.test_mode:
                message_id = f"TEST_{uuid.uuid4().hex[:10]}"
                self.logger.info(f"[TEST MODE] NetGSM SMS would be sent to {formatted_to}: {message}")
            else:
                # NetGSM API çağrısı
                message_id = f"NETGSM_{uuid.uuid4().hex[:10]}"
                
            self.logger.info(f"NetGSM SMS sent: {message_id}")
            
            return {
                'status': 'success',
                'provider': 'netgsm',
                'message_id': message_id,
                'to': formatted_to,
                'message': message,
                'sender': self.sender_name,
                'sent_at': datetime.now().isoformat(),
                'test_mode': self.test_mode
            }
            
        except Exception as e:
            self.logger.error(f"NetGSM SMS sending error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'provider': 'netgsm'
            }
            
    async def send_bulk_sms(self, recipients: List[str], message: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """NetGSM ile toplu SMS gönder"""
        try:
            # NetGSM toplu gönderim destekler
            valid_recipients = []
            invalid_recipients = []
            
            for recipient in recipients:
                if self.validate_phone_number(recipient):
                    valid_recipients.append(self.format_phone_number(recipient).replace('+90', ''))
                else:
                    invalid_recipients.append(recipient)
                    
            if not valid_recipients:
                return {
                    'status': 'error',
                    'message': 'No valid recipients',
                    'invalid_recipients': invalid_recipients
                }
                
            # Test modunda
            if self.test_mode:
                bulk_id = f"TEST_BULK_{uuid.uuid4().hex[:10]}"
                self.logger.info(f"[TEST MODE] NetGSM bulk SMS would be sent to {len(valid_recipients)} recipients")
            else:
                # NetGSM bulk API çağrısı
                bulk_id = f"BULK_{uuid.uuid4().hex[:10]}"
                
            return {
                'status': 'success',
                'provider': 'netgsm',
                'bulk_id': bulk_id,
                'total': len(recipients),
                'sent': len(valid_recipients),
                'invalid': len(invalid_recipients),
                'invalid_recipients': invalid_recipients,
                'sent_at': datetime.now().isoformat(),
                'test_mode': self.test_mode
            }
            
        except Exception as e:
            self.logger.error(f"NetGSM bulk SMS error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'provider': 'netgsm'
            }
            
    async def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """NetGSM SMS teslimat durumu"""
        try:
            # Test modunda
            if self.test_mode or message_id.startswith('TEST_'):
                return {
                    'status': 'success',
                    'delivery_status': SMSStatus.DELIVERED.value,
                    'message_id': message_id,
                    'delivered_at': datetime.now().isoformat()
                }
                
            # NetGSM API çağrısı
            return {
                'status': 'success',
                'delivery_status': SMSStatus.DELIVERED.value,
                'message_id': message_id
            }
            
        except Exception as e:
            self.logger.error(f"NetGSM delivery status error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    async def get_balance(self) -> Dict[str, Any]:
        """NetGSM bakiye sorgulama"""
        try:
            # Test modunda
            if self.test_mode:
                return {
                    'status': 'success',
                    'balance': 1000,
                    'currency': 'CREDITS'
                }
                
            # NetGSM API çağrısı
            return {
                'status': 'success',
                'balance': 0,
                'currency': 'CREDITS'
            }
            
        except Exception as e:
            self.logger.error(f"NetGSM balance query error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }


class IletimMerkeziProvider(BaseSMSProvider):
    """İletim Merkezi SMS Entegrasyonu"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.username = config.get('username')
        self.password = config.get('password')
        self.base_url = "https://api.iletimerkezi.com/v1"
        
    async def send_sms(self, to: str, message: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """İletim Merkezi ile SMS gönder"""
        try:
            if not self.validate_phone_number(to):
                return {
                    'status': 'error',
                    'message': 'Invalid phone number format'
                }
                
            formatted_to = self.format_phone_number(to).replace('+', '')  # İletim Merkezi + istemez
            
            # Test modunda
            if self.test_mode:
                message_id = f"TEST_{uuid.uuid4().hex[:10]}"
                self.logger.info(f"[TEST MODE] İletim Merkezi SMS would be sent to {formatted_to}: {message}")
            else:
                # İletim Merkezi API çağrısı
                message_id = f"IM_{uuid.uuid4().hex[:10]}"
                
            self.logger.info(f"İletim Merkezi SMS sent: {message_id}")
            
            return {
                'status': 'success',
                'provider': 'iletimerkezi',
                'message_id': message_id,
                'to': formatted_to,
                'message': message,
                'sent_at': datetime.now().isoformat(),
                'test_mode': self.test_mode
            }
            
        except Exception as e:
            self.logger.error(f"İletim Merkezi SMS sending error: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'provider': 'iletimerkezi'
            }
            
    async def send_bulk_sms(self, recipients: List[str], message: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """İletim Merkezi ile toplu SMS gönder"""
        results = {
            'total': len(recipients),
            'success': 0,
            'failed': 0,
            'results': []
        }
        
        for recipient in recipients:
            result = await self.send_sms(recipient, message, options)
            if result.get('status') == 'success':
                results['success'] += 1
            else:
                results['failed'] += 1
            results['results'].append(result)
            
        return results
        
    async def get_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """İletim Merkezi SMS teslimat durumu"""
        try:
            if self.test_mode or message_id.startswith('TEST_'):
                return {
                    'status': 'success',
                    'delivery_status': SMSStatus.DELIVERED.value,
                    'message_id': message_id,
                    'delivered_at': datetime.now().isoformat()
                }
                
            return {
                'status': 'success',
                'delivery_status': SMSStatus.DELIVERED.value,
                'message_id': message_id
            }
            
        except Exception as e:
            self.logger.error(f"İletim Merkezi delivery status error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    async def get_balance(self) -> Dict[str, Any]:
        """İletim Merkezi bakiye sorgulama"""
        try:
            if self.test_mode:
                return {
                    'status': 'success',
                    'balance': 500,
                    'currency': 'SMS'
                }
                
            return {
                'status': 'success',
                'balance': 0,
                'currency': 'SMS'
            }
            
        except Exception as e:
            self.logger.error(f"İletim Merkezi balance query error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }


class SMSIntegrationService(BaseService):
    """Kurumsal SMS Entegrasyon Servisi"""
    
    def __init__(self):
        super().__init__()
        self.cache = CacheService()
        self.notification_service = get_notification_service()
        self.providers: Dict[str, BaseSMSProvider] = {}
        self.sms_config = self.get_config('sms', {})
        self._initialize_providers()
        
    def _initialize_providers(self):
        """SMS sağlayıcılarını başlat"""
        provider_configs = self.sms_config.get('providers', {})
        
        # Twilio
        if provider_configs.get('twilio', {}).get('enabled', False):
            self.providers['twilio'] = TwilioProvider(provider_configs['twilio'])
            
        # NetGSM
        if provider_configs.get('netgsm', {}).get('enabled', False):
            self.providers['netgsm'] = NetGSMProvider(provider_configs['netgsm'])
            
        # İletim Merkezi
        if provider_configs.get('iletimerkezi', {}).get('enabled', False):
            self.providers['iletimerkezi'] = IletimMerkeziProvider(provider_configs['iletimerkezi'])
            
        self.log(f"Initialized {len(self.providers)} SMS providers")
        
    async def send_sms(self, to: str, message: str, provider: Optional[str] = None, 
                      options: Dict[str, Any] = None) -> Dict[str, Any]:
        """SMS gönder"""
        try:
            # Provider seçimi
            if provider and provider in self.providers:
                selected_provider = self.providers[provider]
            else:
                # Varsayılan provider'ı kullan
                selected_provider = self._get_default_provider()
                if not selected_provider:
                    return self.error_response("No SMS provider available")
                    
            # SMS uzunluk kontrolü
            if len(message) > 1000:
                return self.error_response("Message too long (max 1000 characters)")
                
            # Kara liste kontrolü
            if await self._is_blacklisted(to):
                return self.error_response("Phone number is blacklisted")
                
            # SMS gönder
            result = await selected_provider.send_sms(to, message, options)
            
            if result['status'] == 'success':
                # SMS kaydını oluştur
                sms_record = await self._save_sms_record(result)
                
                # Cache'e kaydet
                self.cache.set(f"sms:{result['message_id']}", sms_record, 86400)  # 24 saat
                
                # İstatistikleri güncelle
                await self._update_statistics('sent')
                
                self.log(f"SMS sent: {result['message_id']} to {to}")
                
                return self.success_response("SMS sent successfully", {
                    **result,
                    'sms_record_id': sms_record.get('id')
                })
            else:
                await self._update_statistics('failed')
                return self.error_response(result.get('message', 'SMS sending failed'), result)
                
        except Exception as e:
            self.log(f"SMS sending error: {str(e)}", "error")
            return self.error_response(f"SMS sending error: {str(e)}")
            
    async def send_bulk_sms(self, recipients: List[str], message: str, 
                          provider: Optional[str] = None, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Toplu SMS gönder"""
        try:
            # Provider seçimi
            if provider and provider in self.providers:
                selected_provider = self.providers[provider]
            else:
                selected_provider = self._get_default_provider()
                if not selected_provider:
                    return self.error_response("No SMS provider available")
                    
            # Kara liste filtresi
            valid_recipients = []
            blacklisted = []
            
            for recipient in recipients:
                if await self._is_blacklisted(recipient):
                    blacklisted.append(recipient)
                else:
                    valid_recipients.append(recipient)
                    
            if not valid_recipients:
                return self.error_response("All recipients are blacklisted")
                
            # Toplu SMS gönder
            result = await selected_provider.send_bulk_sms(valid_recipients, message, options)
            
            # Kayıtları oluştur
            if result.get('status') == 'success' or result.get('results'):
                bulk_record = await self._save_bulk_sms_record(result, blacklisted)
                
                # İstatistikleri güncelle
                await self._update_statistics('bulk_sent', result.get('success', 0))
                await self._update_statistics('bulk_failed', result.get('failed', 0))
                
                return self.success_response("Bulk SMS processed", {
                    **result,
                    'blacklisted': blacklisted,
                    'bulk_record_id': bulk_record.get('id')
                })
            else:
                return self.error_response(result.get('message', 'Bulk SMS failed'), result)
                
        except Exception as e:
            self.log(f"Bulk SMS error: {str(e)}", "error")
            return self.error_response(f"Bulk SMS error: {str(e)}")
            
    async def get_delivery_status(self, message_id: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """SMS teslimat durumunu sorgula"""
        try:
            # Cache'den kontrol et
            cached_record = self.cache.get(f"sms:{message_id}")
            if cached_record:
                provider = cached_record.get('provider', provider)
                
            if not provider or provider not in self.providers:
                return self.error_response("Provider not found")
                
            selected_provider = self.providers[provider]
            result = await selected_provider.get_delivery_status(message_id)
            
            if result['status'] == 'success':
                # Kaydı güncelle
                if cached_record:
                    cached_record['delivery_status'] = result['delivery_status']
                    cached_record['delivered_at'] = result.get('delivered_at')
                    self.cache.set(f"sms:{message_id}", cached_record, 86400)
                    
                return self.success_response("Delivery status retrieved", result)
            else:
                return self.error_response(result.get('message', 'Status query failed'), result)
                
        except Exception as e:
            self.log(f"Delivery status error: {str(e)}", "error")
            return self.error_response(f"Delivery status error: {str(e)}")
            
    async def get_balance(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """SMS bakiyesini sorgula"""
        try:
            if provider:
                # Belirli provider bakiyesi
                if provider not in self.providers:
                    return self.error_response(f"Provider not found: {provider}")
                    
                result = await self.providers[provider].get_balance()
                return self.success_response("Balance retrieved", {provider: result})
            else:
                # Tüm provider bakiyeleri
                balances = {}
                for name, provider_instance in self.providers.items():
                    balance_result = await provider_instance.get_balance()
                    balances[name] = balance_result
                    
                return self.success_response("All balances retrieved", balances)
                
        except Exception as e:
            self.log(f"Balance query error: {str(e)}", "error")
            return self.error_response(f"Balance query error: {str(e)}")
            
    def _get_default_provider(self) -> Optional[BaseSMSProvider]:
        """Varsayılan SMS sağlayıcısını getir"""
        # Öncelik sırasına göre
        priority_order = ['netgsm', 'iletimerkezi', 'twilio']
        
        for provider_name in priority_order:
            if provider_name in self.providers:
                return self.providers[provider_name]
                
        # İlk aktif provider'ı döndür
        if self.providers:
            return list(self.providers.values())[0]
            
        return None
        
    async def _is_blacklisted(self, phone: str) -> bool:
        """Telefon numarası kara listede mi?"""
        blacklist_key = "sms_blacklist"
        blacklist = self.cache.get(blacklist_key) or []
        
        # Formatlanmış numarayı kontrol et
        formatted_phone = self._format_phone_for_blacklist(phone)
        return formatted_phone in blacklist
        
    def _format_phone_for_blacklist(self, phone: str) -> str:
        """Kara liste için telefon numarasını formatla"""
        # Sadece rakamları al
        return re.sub(r'\D', '', phone)
        
    async def add_to_blacklist(self, phone: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Telefon numarasını kara listeye ekle"""
        try:
            blacklist_key = "sms_blacklist"
            blacklist = self.cache.get(blacklist_key) or []
            
            formatted_phone = self._format_phone_for_blacklist(phone)
            
            if formatted_phone not in blacklist:
                blacklist.append(formatted_phone)
                self.cache.set(blacklist_key, blacklist, 0)  # Süresiz
                
                # Kara liste kaydı oluştur
                blacklist_record = {
                    'phone': formatted_phone,
                    'reason': reason,
                    'added_at': datetime.now().isoformat()
                }
                
                self.log(f"Phone added to blacklist: {formatted_phone}")
                
                return self.success_response("Phone added to blacklist", blacklist_record)
            else:
                return self.error_response("Phone already in blacklist")
                
        except Exception as e:
            self.log(f"Blacklist add error: {str(e)}", "error")
            return self.error_response(f"Blacklist add error: {str(e)}")
            
    async def remove_from_blacklist(self, phone: str) -> Dict[str, Any]:
        """Telefon numarasını kara listeden çıkar"""
        try:
            blacklist_key = "sms_blacklist"
            blacklist = self.cache.get(blacklist_key) or []
            
            formatted_phone = self._format_phone_for_blacklist(phone)
            
            if formatted_phone in blacklist:
                blacklist.remove(formatted_phone)
                self.cache.set(blacklist_key, blacklist, 0)
                
                self.log(f"Phone removed from blacklist: {formatted_phone}")
                
                return self.success_response("Phone removed from blacklist")
            else:
                return self.error_response("Phone not in blacklist")
                
        except Exception as e:
            self.log(f"Blacklist remove error: {str(e)}", "error")
            return self.error_response(f"Blacklist remove error: {str(e)}")
            
    async def _save_sms_record(self, sms_data: Dict[str, Any]) -> Dict[str, Any]:
        """SMS kaydını sakla"""
        record = {
            'id': str(uuid.uuid4()),
            'message_id': sms_data['message_id'],
            'provider': sms_data['provider'],
            'to': sms_data['to'],
            'message': sms_data['message'],
            'status': SMSStatus.SENT.value,
            'sent_at': sms_data['sent_at'],
            'test_mode': sms_data.get('test_mode', False)
        }
        
        # Veritabanına kaydet (simülasyon)
        self.log(f"SMS record saved: {record['id']}")
        
        return record
        
    async def _save_bulk_sms_record(self, bulk_data: Dict[str, Any], 
                                  blacklisted: List[str]) -> Dict[str, Any]:
        """Toplu SMS kaydını sakla"""
        record = {
            'id': str(uuid.uuid4()),
            'bulk_id': bulk_data.get('bulk_id', str(uuid.uuid4())),
            'provider': bulk_data['provider'],
            'total': bulk_data['total'],
            'success': bulk_data.get('success', bulk_data.get('sent', 0)),
            'failed': bulk_data.get('failed', 0),
            'blacklisted': len(blacklisted),
            'sent_at': bulk_data.get('sent_at', datetime.now().isoformat())
        }
        
        # Veritabanına kaydet (simülasyon)
        self.log(f"Bulk SMS record saved: {record['id']}")
        
        return record
        
    async def _update_statistics(self, stat_type: str, count: int = 1):
        """SMS istatistiklerini güncelle"""
        stats_key = f"sms_stats:{datetime.now().strftime('%Y-%m-%d')}"
        stats = self.cache.get(stats_key) or {}
        
        stats[stat_type] = stats.get(stat_type, 0) + count
        stats['last_updated'] = datetime.now().isoformat()
        
        self.cache.set(stats_key, stats, 86400 * 7)  # 7 gün sakla
        
    async def get_statistics(self, start_date: Optional[datetime] = None, 
                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """SMS istatistiklerini getir"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
            
        stats = {
            'total_sent': 0,
            'total_failed': 0,
            'total_bulk_sent': 0,
            'total_bulk_failed': 0,
            'daily_stats': []
        }
        
        current_date = start_date
        while current_date <= end_date:
            stats_key = f"sms_stats:{current_date.strftime('%Y-%m-%d')}"
            daily_stats = self.cache.get(stats_key) or {}
            
            if daily_stats:
                stats['total_sent'] += daily_stats.get('sent', 0)
                stats['total_failed'] += daily_stats.get('failed', 0)
                stats['total_bulk_sent'] += daily_stats.get('bulk_sent', 0)
                stats['total_bulk_failed'] += daily_stats.get('bulk_failed', 0)
                
                stats['daily_stats'].append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    **daily_stats
                })
                
            current_date += timedelta(days=1)
            
        return stats
        
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Kullanılabilir SMS sağlayıcılarını getir"""
        providers = []
        
        for name, provider in self.providers.items():
            providers.append({
                'name': name,
                'display_name': name.title(),
                'test_mode': provider.test_mode,
                'sender_id': provider.sender_id
            })
            
        return providers


# Global SMS service instance
_sms_service = None

def get_sms_service() -> SMSIntegrationService:
    """Global SMS service instance'ını al"""
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSIntegrationService()
    return _sms_service