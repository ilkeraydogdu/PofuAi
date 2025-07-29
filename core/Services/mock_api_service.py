#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock API Service
================

Development ve test ortamları için 3. parti servislerin mock implementasyonları
- E-ticaret platformları (Trendyol, Hepsiburada, N11, vb.)
- Ödeme sistemleri (İyzico, PayTR, Stripe, vb.)
- Kargo sistemleri (Yurtiçi, Aras, MNG, vb.)
- Sosyal medya API'leri (Facebook, Instagram, Twitter, vb.)
- AI servisleri (OpenAI, Google Cloud, vb.)
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from core.Services.logger import LoggerService


class MockAPIService:
    """
    Mock API servisi - 3. parti servislerin test implementasyonları
    """
    
    def __init__(self):
        self.logger = LoggerService.get_logger()
        self.request_count = 0
        self.mock_data = self._init_mock_data()
        
        self.logger.info("Mock API Service başlatıldı")
    
    def _init_mock_data(self) -> Dict[str, Any]:
        """Mock verilerini başlat"""
        return {
            'products': [
                {
                    'id': 'MOCK_PROD_001',
                    'title': 'Mock Ürün 1',
                    'price': 99.99,
                    'stock': 50,
                    'category': 'Elektronik',
                    'brand': 'MockBrand',
                    'status': 'active'
                },
                {
                    'id': 'MOCK_PROD_002', 
                    'title': 'Mock Ürün 2',
                    'price': 149.99,
                    'stock': 25,
                    'category': 'Giyim',
                    'brand': 'MockFashion',
                    'status': 'active'
                }
            ],
            'orders': [
                {
                    'id': 'MOCK_ORDER_001',
                    'customer_name': 'Test Müşteri',
                    'total': 99.99,
                    'status': 'processing',
                    'created_at': datetime.now().isoformat(),
                    'items': [
                        {'product_id': 'MOCK_PROD_001', 'quantity': 1, 'price': 99.99}
                    ]
                }
            ],
            'shipments': [
                {
                    'id': 'MOCK_SHIP_001',
                    'tracking_number': 'MOCK123456789',
                    'status': 'in_transit',
                    'estimated_delivery': (datetime.now() + timedelta(days=2)).isoformat()
                }
            ]
        }
    
    # E-ticaret Platformları Mock API'leri
    
    def trendyol_api(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """Trendyol API Mock"""
        self._log_request('Trendyol', endpoint, method)
        
        if endpoint == '/suppliers/products':
            if method == 'GET':
                return {
                    'content': self.mock_data['products'],
                    'totalElements': len(self.mock_data['products']),
                    'success': True
                }
            elif method == 'POST':
                new_product = data.copy()
                new_product['id'] = f"MOCK_TRENDYOL_{random.randint(1000, 9999)}"
                new_product['status'] = 'pending_approval'
                return {'id': new_product['id'], 'success': True}
        
        elif endpoint.startswith('/suppliers/orders'):
            return {
                'content': self.mock_data['orders'],
                'totalElements': len(self.mock_data['orders']),
                'success': True
            }
        
        return {'success': False, 'error': 'Mock endpoint not implemented'}
    
    def hepsiburada_api(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """Hepsiburada API Mock"""
        self._log_request('Hepsiburada', endpoint, method)
        
        if endpoint == '/product/api/products':
            if method == 'GET':
                return {
                    'data': self.mock_data['products'],
                    'totalCount': len(self.mock_data['products']),
                    'success': True
                }
            elif method == 'POST':
                new_product = data.copy()
                new_product['id'] = f"MOCK_HB_{random.randint(1000, 9999)}"
                return {'productId': new_product['id'], 'success': True}
        
        elif endpoint == '/order/api/orders':
            return {
                'data': self.mock_data['orders'],
                'totalCount': len(self.mock_data['orders']),
                'success': True
            }
        
        return {'success': False, 'error': 'Mock endpoint not implemented'}
    
    def n11_api(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """N11 API Mock"""
        self._log_request('N11', endpoint, method)
        
        if endpoint == 'ProductService':
            return {
                'result': {
                    'status': 'success',
                    'products': self.mock_data['products']
                }
            }
        
        elif endpoint == 'OrderService':
            return {
                'result': {
                    'status': 'success',
                    'orders': self.mock_data['orders']
                }
            }
        
        return {'result': {'status': 'error', 'errorMessage': 'Mock endpoint not implemented'}}
    
    # Ödeme Sistemleri Mock API'leri
    
    def iyzico_api(self, endpoint: str, method: str = 'POST', data: Dict = None) -> Dict[str, Any]:
        """İyzico API Mock"""
        self._log_request('İyzico', endpoint, method)
        
        if endpoint == '/payment/auth':
            return {
                'status': 'success',
                'paymentId': f"MOCK_PAY_{random.randint(10000, 99999)}",
                'paymentStatus': 'SUCCESS',
                'paidPrice': data.get('price', 100.00),
                'currency': 'TRY',
                'installment': 1
            }
        
        elif endpoint == '/payment/refund':
            return {
                'status': 'success',
                'paymentId': data.get('paymentTransactionId'),
                'refundTransactionId': f"MOCK_REF_{random.randint(10000, 99999)}",
                'price': data.get('price')
            }
        
        return {'status': 'failure', 'errorMessage': 'Mock endpoint not implemented'}
    
    def paytr_api(self, endpoint: str, method: str = 'POST', data: Dict = None) -> Dict[str, Any]:
        """PayTR API Mock"""
        self._log_request('PayTR', endpoint, method)
        
        if endpoint == '/odeme/api/get-token':
            return {
                'status': 'success',
                'token': f"mock_paytr_token_{random.randint(100000, 999999)}"
            }
        
        elif endpoint == '/odeme/api/callback':
            return {
                'status': 'success',
                'merchant_oid': data.get('merchant_oid'),
                'payment_amount': data.get('payment_amount'),
                'payment_status': 'success'
            }
        
        return {'status': 'failed', 'reason': 'Mock endpoint not implemented'}
    
    # Kargo Sistemleri Mock API'leri
    
    def yurtici_kargo_api(self, endpoint: str, method: str = 'POST', data: Dict = None) -> Dict[str, Any]:
        """Yurtiçi Kargo API Mock"""
        self._log_request('Yurtiçi Kargo', endpoint, method)
        
        if endpoint == '/createShipment':
            return {
                'success': True,
                'cargoKey': f"YK{random.randint(1000000000, 9999999999)}",
                'trackingNumber': f"YK{random.randint(100000, 999999)}",
                'estimatedDeliveryDate': (datetime.now() + timedelta(days=random.randint(1, 5))).isoformat()
            }
        
        elif endpoint == '/trackShipment':
            return {
                'success': True,
                'trackingNumber': data.get('trackingNumber'),
                'status': random.choice(['shipped', 'in_transit', 'out_for_delivery', 'delivered']),
                'lastUpdate': datetime.now().isoformat()
            }
        
        return {'success': False, 'error': 'Mock endpoint not implemented'}
    
    def aras_kargo_api(self, endpoint: str, method: str = 'POST', data: Dict = None) -> Dict[str, Any]:
        """Aras Kargo API Mock"""
        self._log_request('Aras Kargo', endpoint, method)
        
        if endpoint == '/shipment/create':
            return {
                'result': True,
                'shipmentId': f"AR{random.randint(1000000, 9999999)}",
                'trackingCode': f"AR{random.randint(100000, 999999)}",
                'message': 'Shipment created successfully'
            }
        
        elif endpoint == '/shipment/track':
            return {
                'result': True,
                'trackingCode': data.get('trackingCode'),
                'currentStatus': random.choice(['Kargo Alındı', 'Yolda', 'Dağıtımda', 'Teslim Edildi']),
                'lastUpdateTime': datetime.now().isoformat()
            }
        
        return {'result': False, 'message': 'Mock endpoint not implemented'}
    
    # Sosyal Medya API'leri
    
    def facebook_api(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """Facebook API Mock"""
        self._log_request('Facebook', endpoint, method)
        
        if endpoint.startswith('/me/accounts'):
            return {
                'data': [
                    {
                        'id': 'mock_page_id_123',
                        'name': 'Mock Business Page',
                        'access_token': 'mock_page_access_token'
                    }
                ]
            }
        
        elif 'feed' in endpoint and method == 'POST':
            return {
                'id': f"mock_post_{random.randint(10000, 99999)}",
                'created_time': datetime.now().isoformat()
            }
        
        return {'error': {'message': 'Mock endpoint not implemented'}}
    
    def instagram_api(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """Instagram API Mock"""
        self._log_request('Instagram', endpoint, method)
        
        if 'media' in endpoint and method == 'POST':
            return {
                'id': f"mock_media_{random.randint(10000, 99999)}",
                'created_time': datetime.now().isoformat()
            }
        
        elif 'insights' in endpoint:
            return {
                'data': [
                    {'name': 'impressions', 'values': [{'value': random.randint(100, 1000)}]},
                    {'name': 'reach', 'values': [{'value': random.randint(50, 500)}]},
                    {'name': 'engagement', 'values': [{'value': random.randint(10, 100)}]}
                ]
            }
        
        return {'error': {'message': 'Mock endpoint not implemented'}}
    
    # AI Servisleri Mock API'leri
    
    def openai_api(self, endpoint: str, method: str = 'POST', data: Dict = None) -> Dict[str, Any]:
        """OpenAI API Mock"""
        self._log_request('OpenAI', endpoint, method)
        
        if endpoint == '/chat/completions':
            return {
                'id': f"chatcmpl-mock{random.randint(10000, 99999)}",
                'object': 'chat.completion',
                'created': int(time.time()),
                'model': data.get('model', 'gpt-3.5-turbo'),
                'choices': [{
                    'index': 0,
                    'message': {
                        'role': 'assistant',
                        'content': 'Bu bir mock AI yanıtıdır. Gerçek OpenAI API entegrasyonu için geçerli API anahtarı gereklidir.'
                    },
                    'finish_reason': 'stop'
                }],
                'usage': {
                    'prompt_tokens': 50,
                    'completion_tokens': 25,
                    'total_tokens': 75
                }
            }
        
        elif endpoint == '/images/generations':
            return {
                'created': int(time.time()),
                'data': [{
                    'url': 'https://mock-image-url.com/generated-image.png'
                }]
            }
        
        return {'error': {'message': 'Mock endpoint not implemented'}}
    
    # Yardımcı Metodlar
    
    def _log_request(self, service: str, endpoint: str, method: str):
        """API isteğini logla"""
        self.request_count += 1
        self.logger.info(f"Mock API çağrısı #{self.request_count}: {service} - {method} {endpoint}")
    
    def get_mock_statistics(self) -> Dict[str, Any]:
        """Mock API istatistiklerini döndür"""
        return {
            'total_requests': self.request_count,
            'available_services': [
                'Trendyol', 'Hepsiburada', 'N11',
                'İyzico', 'PayTR',
                'Yurtiçi Kargo', 'Aras Kargo',
                'Facebook', 'Instagram',
                'OpenAI'
            ],
            'mock_data_counts': {
                'products': len(self.mock_data['products']),
                'orders': len(self.mock_data['orders']),
                'shipments': len(self.mock_data['shipments'])
            }
        }
    
    def reset_mock_data(self):
        """Mock verilerini sıfırla"""
        self.mock_data = self._init_mock_data()
        self.request_count = 0
        self.logger.info("Mock API verileri sıfırlandı")


# Singleton instance
mock_api_service = MockAPIService()