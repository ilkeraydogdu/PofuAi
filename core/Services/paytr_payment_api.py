"""
PayTR Payment API Implementation
Türkiye'nin önde gelen ödeme sistemi PayTR entegrasyonu

Bu modül PayTR'nin iFrame API, Direct API, Link API ve diğer
ödeme çözümlerini destekler.
"""

import hashlib
import hmac
import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from base64 import b64encode
from urllib.parse import urlencode

from .base_service import BaseService


class PayTRPaymentAPI(BaseService):
    """PayTR Payment API Implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.merchant_id = config.get('merchant_id')
        self.merchant_key = config.get('merchant_key')
        self.merchant_salt = config.get('merchant_salt')
        self.base_url = config.get('base_url', 'https://www.paytr.com')
        self.test_mode = config.get('test_mode', True)
        
        # API Endpoints
        self.endpoints = {
            'iframe_token': '/odeme/api/get-token',
            'direct_payment': '/odeme/api/direct-payment',
            'link_create': '/link/api/create',
            'link_delete': '/link/api/delete',
            'refund': '/odeme/api/refund',
            'status_inquiry': '/odeme/api/status',
            'installment_rates': '/odeme/api/taksit-oranlari',
            'bin_lookup': '/odeme/api/bin-sorgulama',
            'card_storage': '/odeme/api/kart-saklama',
            'transfer': '/odeme/api/platform-transfer',
            'transaction_detail': '/odeme/api/islem-detay'
        }
        
        # Test kartları
        self.test_cards = {
            'visa': {
                'number': '4355084355084358',
                'holder': 'PAYTR TEST',
                'expiry_month': '12',
                'expiry_year': '24',
                'cvv': '000'
            },
            'mastercard': {
                'number': '5406675406675403',
                'holder': 'PAYTR TEST',
                'expiry_month': '12',
                'expiry_year': '24',
                'cvv': '000'
            },
            'troy': {
                'number': '9792030394440796',
                'holder': 'PAYTR TEST',
                'expiry_month': '12',
                'expiry_year': '24',
                'cvv': '000'
            }
        }
    
    def _generate_hash(self, data: str) -> str:
        """PayTR hash oluşturma"""
        return b64encode(hmac.new(
            self.merchant_key.encode(),
            data.encode(),
            hashlib.sha256
        ).digest()).decode()
    
    def _generate_paytr_token(self, data: Dict[str, Any]) -> str:
        """PayTR token oluşturma"""
        hash_str = f"{self.merchant_id}|{data.get('user_ip')}|{data.get('merchant_oid')}|{data.get('email')}|{data.get('payment_amount')}|{data.get('payment_type', 'card')}|{data.get('installment_count', 0)}|{data.get('currency', 'TL')}|{data.get('test_mode', 1)}|{data.get('non_3d', 0)}"
        return self._generate_hash(hash_str + self.merchant_salt)
    
    def create_iframe_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        iFrame ödeme token'ı oluşturma
        
        Args:
            payment_data: Ödeme bilgileri
            
        Returns:
            API yanıtı
        """
        try:
            # Zorunlu alanlar
            required_fields = ['merchant_oid', 'email', 'payment_amount', 'user_basket', 'user_name', 'user_address', 'user_phone']
            for field in required_fields:
                if field not in payment_data:
                    raise ValueError(f"Zorunlu alan eksik: {field}")
            
            # İstek verilerini hazırla
            request_data = {
                'merchant_id': self.merchant_id,
                'user_ip': payment_data.get('user_ip', '127.0.0.1'),
                'merchant_oid': payment_data['merchant_oid'],
                'email': payment_data['email'],
                'payment_amount': int(payment_data['payment_amount'] * 100),  # Kuruş cinsine çevir
                'payment_type': payment_data.get('payment_type', 'card'),
                'installment_count': payment_data.get('installment_count', 0),
                'currency': payment_data.get('currency', 'TL'),
                'test_mode': 1 if self.test_mode else 0,
                'non_3d': payment_data.get('non_3d', 0),
                'merchant_ok_url': payment_data.get('success_url', ''),
                'merchant_fail_url': payment_data.get('fail_url', ''),
                'user_name': payment_data['user_name'],
                'user_address': payment_data['user_address'],
                'user_phone': payment_data['user_phone'],
                'user_basket': b64encode(json.dumps(payment_data['user_basket']).encode()).decode(),
                'debug_on': 1 if self.test_mode else 0,
                'client_lang': payment_data.get('lang', 'tr'),
                'no_installment': payment_data.get('no_installment', 0),
                'max_installment': payment_data.get('max_installment', 0),
                'timeout_limit': payment_data.get('timeout_limit', 30),
                'card_type_1': payment_data.get('card_type_1', 1),
                'card_type_2': payment_data.get('card_type_2', 1)
            }
            
            # Token oluştur
            request_data['paytr_token'] = self._generate_paytr_token(request_data)
            
            # API isteği gönder
            response = requests.post(
                f"{self.base_url}{self.endpoints['iframe_token']}",
                data=request_data,
                timeout=30
            )
            
            result = response.json()
            
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'token': result.get('token'),
                    'iframe_url': f"{self.base_url}/odeme/guvenli/{result.get('token')}",
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('reason', 'Bilinmeyen hata'),
                    'data': result
                }
                
        except Exception as e:
            self.logger.error(f"PayTR iFrame ödeme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_direct_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct API ile ödeme
        
        Args:
            payment_data: Ödeme ve kart bilgileri
            
        Returns:
            API yanıtı
        """
        try:
            # Zorunlu alanlar
            required_fields = ['merchant_oid', 'email', 'payment_amount', 'cc_owner', 'card_number', 'expiry_month', 'expiry_year', 'cvv']
            for field in required_fields:
                if field not in payment_data:
                    raise ValueError(f"Zorunlu alan eksik: {field}")
            
            # İstek verilerini hazırla
            request_data = {
                'merchant_id': self.merchant_id,
                'user_ip': payment_data.get('user_ip', '127.0.0.1'),
                'merchant_oid': payment_data['merchant_oid'],
                'email': payment_data['email'],
                'payment_amount': int(payment_data['payment_amount'] * 100),
                'payment_type': 'card',
                'installment_count': payment_data.get('installment_count', 0),
                'currency': payment_data.get('currency', 'TL'),
                'test_mode': 1 if self.test_mode else 0,
                'non_3d': payment_data.get('non_3d', 0),
                'cc_owner': payment_data['cc_owner'],
                'card_number': payment_data['card_number'],
                'expiry_month': payment_data['expiry_month'],
                'expiry_year': payment_data['expiry_year'],
                'cvv': payment_data['cvv'],
                'user_name': payment_data.get('user_name', ''),
                'user_address': payment_data.get('user_address', ''),
                'user_phone': payment_data.get('user_phone', ''),
                'user_basket': b64encode(json.dumps(payment_data.get('user_basket', [])).encode()).decode()
            }
            
            # Token oluştur
            request_data['paytr_token'] = self._generate_paytr_token(request_data)
            
            # API isteği gönder
            response = requests.post(
                f"{self.base_url}{self.endpoints['direct_payment']}",
                data=request_data,
                timeout=30
            )
            
            result = response.json()
            
            return {
                'success': result.get('status') == 'success',
                'data': result,
                'transaction_id': result.get('payment_id'),
                'status': result.get('status'),
                'message': result.get('reason', '')
            }
            
        except Exception as e:
            self.logger.error(f"PayTR direct ödeme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_payment_link(self, link_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Linkle ödeme oluşturma
        
        Args:
            link_data: Link bilgileri
            
        Returns:
            API yanıtı
        """
        try:
            # Zorunlu alanlar
            required_fields = ['amount', 'order_id']
            for field in required_fields:
                if field not in link_data:
                    raise ValueError(f"Zorunlu alan eksik: {field}")
            
            # Hash oluştur
            hash_str = f"{self.merchant_id}|{link_data['amount']}|{link_data['order_id']}|{link_data.get('currency', 'TL')}"
            
            request_data = {
                'merchant_id': self.merchant_id,
                'amount': link_data['amount'],
                'order_id': link_data['order_id'],
                'currency': link_data.get('currency', 'TL'),
                'test_mode': 1 if self.test_mode else 0,
                'client_lang': link_data.get('lang', 'tr'),
                'paytr_token': self._generate_hash(hash_str + self.merchant_salt),
                'link_text': link_data.get('link_text', ''),
                'callback_url': link_data.get('callback_url', ''),
                'expiry_date': link_data.get('expiry_date', ''),
                'installment': link_data.get('installment', 0)
            }
            
            # API isteği gönder
            response = requests.post(
                f"{self.base_url}{self.endpoints['link_create']}",
                data=request_data,
                timeout=30
            )
            
            result = response.json()
            
            return {
                'success': result.get('status') == 'success',
                'link_id': result.get('link_id'),
                'payment_url': result.get('link'),
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"PayTR link oluşturma hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund_payment(self, refund_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        İade işlemi
        
        Args:
            refund_data: İade bilgileri
            
        Returns:
            API yanıtı
        """
        try:
            # Zorunlu alanlar
            required_fields = ['merchant_oid', 'return_amount']
            for field in required_fields:
                if field not in refund_data:
                    raise ValueError(f"Zorunlu alan eksik: {field}")
            
            # Hash oluştur
            hash_str = f"{self.merchant_id}|{refund_data['merchant_oid']}|{refund_data['return_amount']}"
            
            request_data = {
                'merchant_id': self.merchant_id,
                'merchant_oid': refund_data['merchant_oid'],
                'return_amount': refund_data['return_amount'],
                'paytr_token': self._generate_hash(hash_str + self.merchant_salt)
            }
            
            # API isteği gönder
            response = requests.post(
                f"{self.base_url}{self.endpoints['refund']}",
                data=request_data,
                timeout=30
            )
            
            result = response.json()
            
            return {
                'success': result.get('status') == 'success',
                'data': result,
                'message': result.get('err_msg', result.get('reason', ''))
            }
            
        except Exception as e:
            self.logger.error(f"PayTR iade hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_installment_rates(self, bin_number: str = None) -> Dict[str, Any]:
        """
        Taksit oranları sorgulama
        
        Args:
            bin_number: Kart BIN numarası (opsiyonel)
            
        Returns:
            Taksit oranları
        """
        try:
            hash_str = f"{self.merchant_id}"
            if bin_number:
                hash_str += f"|{bin_number}"
            
            request_data = {
                'merchant_id': self.merchant_id,
                'paytr_token': self._generate_hash(hash_str + self.merchant_salt)
            }
            
            if bin_number:
                request_data['bin_number'] = bin_number
            
            # API isteği gönder
            response = requests.post(
                f"{self.base_url}{self.endpoints['installment_rates']}",
                data=request_data,
                timeout=30
            )
            
            result = response.json()
            
            return {
                'success': result.get('status') == 'success',
                'installments': result.get('installment_rates', []),
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"PayTR taksit oranları hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def bin_lookup(self, bin_number: str) -> Dict[str, Any]:
        """
        BIN sorgulama
        
        Args:
            bin_number: 6 haneli BIN numarası
            
        Returns:
            Kart bilgileri
        """
        try:
            hash_str = f"{self.merchant_id}|{bin_number}"
            
            request_data = {
                'merchant_id': self.merchant_id,
                'bin_number': bin_number,
                'paytr_token': self._generate_hash(hash_str + self.merchant_salt)
            }
            
            # API isteği gönder
            response = requests.post(
                f"{self.base_url}{self.endpoints['bin_lookup']}",
                data=request_data,
                timeout=30
            )
            
            result = response.json()
            
            return {
                'success': result.get('status') == 'success',
                'card_info': {
                    'bank_name': result.get('bank_name'),
                    'card_type': result.get('card_type'),
                    'card_association': result.get('card_association'),
                    'card_family': result.get('card_family'),
                    'supports_installment': result.get('installment_support'),
                    'supports_3d': result.get('supports_3d')
                },
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"PayTR BIN sorgulama hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_callback(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Callback doğrulama
        
        Args:
            post_data: POST ile gelen veriler
            
        Returns:
            Doğrulama sonucu
        """
        try:
            # Hash doğrulama
            merchant_oid = post_data.get('merchant_oid')
            status = post_data.get('status')
            total_amount = post_data.get('total_amount')
            hash_value = post_data.get('hash')
            
            # Beklenen hash'i hesapla
            hash_str = f"{merchant_oid}|{self.merchant_salt}|{status}|{total_amount}"
            expected_hash = b64encode(hmac.new(
                self.merchant_key.encode(),
                hash_str.encode(),
                hashlib.sha256
            ).digest()).decode()
            
            is_valid = hash_value == expected_hash
            
            return {
                'success': True,
                'is_valid': is_valid,
                'status': status,
                'merchant_oid': merchant_oid,
                'total_amount': total_amount,
                'payment_type': post_data.get('payment_type'),
                'installment_count': post_data.get('installment_count'),
                'data': post_data
            }
            
        except Exception as e:
            self.logger.error(f"PayTR callback doğrulama hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_test_cards(self) -> Dict[str, Any]:
        """Test kartları bilgilerini döndür"""
        return {
            'success': True,
            'cards': self.test_cards
        }
    
    def format_user_basket(self, items: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Kullanıcı sepetini PayTR formatına çevir
        
        Args:
            items: Sepet öğeleri
            
        Returns:
            PayTR formatında sepet
        """
        basket = []
        for item in items:
            basket.append([
                item.get('name', 'Ürün'),
                str(item.get('price', 0)),
                str(item.get('quantity', 1))
            ])
        return basket
    
    def calculate_total_amount(self, items: List[Dict[str, Any]]) -> float:
        """Sepet toplam tutarını hesapla"""
        total = 0
        for item in items:
            price = float(item.get('price', 0))
            quantity = int(item.get('quantity', 1))
            total += price * quantity
        return total