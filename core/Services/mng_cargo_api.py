"""
MNG Kargo API Implementation
Türkiye'nin lider kargo firmalarından MNG Kargo entegrasyonu

Bu modül MNG Kargo'nun kargo gönderimi, takip, fiyat sorgulama
ve diğer lojistik hizmetlerini destekler.
"""

import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import hashlib
import hmac
from base64 import b64encode

from .base_service import BaseService


class MNGCargoAPI(BaseService):
    """MNG Kargo API Implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.username = config.get('username')
        self.password = config.get('password')
        self.customer_code = config.get('customer_code')
        self.base_url = config.get('base_url', 'https://api.mngkargo.com.tr')
        self.test_mode = config.get('test_mode', True)
        
        # API Endpoints
        self.endpoints = {
            'create_shipment': '/shipment/create',
            'track_shipment': '/shipment/track',
            'get_price': '/shipment/price',
            'cancel_shipment': '/shipment/cancel',
            'get_cities': '/reference/cities',
            'get_districts': '/reference/districts',
            'get_branches': '/reference/branches',
            'get_services': '/reference/services',
            'create_pickup': '/pickup/create',
            'get_barcode': '/shipment/barcode',
            'get_waybill': '/shipment/waybill'
        }
        
        # Servis tipleri
        self.service_types = {
            'standard': 1,
            'express': 2,
            'same_day': 3,
            'next_day': 4,
            'economic': 5
        }
        
        # Ödeme tipleri
        self.payment_types = {
            'sender': 1,      # Gönderen öder
            'receiver': 2,    # Alıcı öder
            'third_party': 3  # Üçüncü şahıs öder
        }
        
        # Kargo türleri
        self.cargo_types = {
            'package': 1,     # Koli
            'document': 2,    # Evrak
            'pallet': 3,      # Palet
            'bulk': 4         # Dökme
        }
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Kimlik doğrulama başlıklarını oluştur"""
        auth_string = f"{self.username}:{self.password}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = b64encode(auth_bytes).decode('ascii')
        
        return {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Customer-Code': self.customer_code
        }
    
    def create_shipment(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kargo gönderimi oluşturma
        
        Args:
            shipment_data: Gönderi bilgileri
            
        Returns:
            API yanıtı
        """
        try:
            # Zorunlu alanlar
            required_fields = [
                'sender_name', 'sender_phone', 'sender_address', 'sender_city',
                'receiver_name', 'receiver_phone', 'receiver_address', 'receiver_city',
                'piece_count', 'total_weight'
            ]
            
            for field in required_fields:
                if field not in shipment_data:
                    raise ValueError(f"Zorunlu alan eksik: {field}")
            
            # İstek verilerini hazırla
            request_data = {
                'sender': {
                    'name': shipment_data['sender_name'],
                    'phone': shipment_data['sender_phone'],
                    'address': shipment_data['sender_address'],
                    'city': shipment_data['sender_city'],
                    'district': shipment_data.get('sender_district', ''),
                    'postal_code': shipment_data.get('sender_postal_code', ''),
                    'tax_number': shipment_data.get('sender_tax_number', ''),
                    'tax_office': shipment_data.get('sender_tax_office', '')
                },
                'receiver': {
                    'name': shipment_data['receiver_name'],
                    'phone': shipment_data['receiver_phone'],
                    'address': shipment_data['receiver_address'],
                    'city': shipment_data['receiver_city'],
                    'district': shipment_data.get('receiver_district', ''),
                    'postal_code': shipment_data.get('receiver_postal_code', ''),
                    'tax_number': shipment_data.get('receiver_tax_number', ''),
                    'tax_office': shipment_data.get('receiver_tax_office', '')
                },
                'shipment': {
                    'service_type': self.service_types.get(
                        shipment_data.get('service_type', 'standard'), 1
                    ),
                    'payment_type': self.payment_types.get(
                        shipment_data.get('payment_type', 'sender'), 1
                    ),
                    'cargo_type': self.cargo_types.get(
                        shipment_data.get('cargo_type', 'package'), 1
                    ),
                    'piece_count': shipment_data['piece_count'],
                    'total_weight': shipment_data['total_weight'],
                    'total_volume': shipment_data.get('total_volume', 0),
                    'declared_value': shipment_data.get('declared_value', 0),
                    'description': shipment_data.get('description', ''),
                    'special_instructions': shipment_data.get('special_instructions', ''),
                    'delivery_type': shipment_data.get('delivery_type', 'standard'),
                    'collect_on_delivery': shipment_data.get('collect_on_delivery', 0),
                    'insurance': shipment_data.get('insurance', False),
                    'sms_notification': shipment_data.get('sms_notification', True),
                    'email_notification': shipment_data.get('email_notification', True)
                },
                'reference_number': shipment_data.get('reference_number', ''),
                'pickup_date': shipment_data.get('pickup_date', ''),
                'delivery_date': shipment_data.get('delivery_date', '')
            }
            
            # Parça detayları
            if 'pieces' in shipment_data:
                request_data['pieces'] = []
                for piece in shipment_data['pieces']:
                    request_data['pieces'].append({
                        'weight': piece.get('weight', 0),
                        'length': piece.get('length', 0),
                        'width': piece.get('width', 0),
                        'height': piece.get('height', 0),
                        'description': piece.get('description', '')
                    })
            
            # API isteği gönder
            response = requests.post(
                f"{self.base_url}{self.endpoints['create_shipment']}",
                headers=self._get_auth_headers(),
                json=request_data,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                return {
                    'success': True,
                    'tracking_number': result.get('tracking_number'),
                    'barcode': result.get('barcode'),
                    'reference_number': result.get('reference_number'),
                    'estimated_delivery': result.get('estimated_delivery'),
                    'cost': result.get('cost', 0),
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Bilinmeyen hata'),
                    'error_code': result.get('error_code'),
                    'data': result
                }
                
        except Exception as e:
            self.logger.error(f"MNG Kargo gönderi oluşturma hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def track_shipment(self, tracking_number: str) -> Dict[str, Any]:
        """
        Kargo takibi
        
        Args:
            tracking_number: Takip numarası
            
        Returns:
            Takip bilgileri
        """
        try:
            # API isteği gönder
            response = requests.get(
                f"{self.base_url}{self.endpoints['track_shipment']}",
                headers=self._get_auth_headers(),
                params={'tracking_number': tracking_number},
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                tracking_info = result.get('tracking_info', {})
                
                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'status': tracking_info.get('status'),
                    'status_description': tracking_info.get('status_description'),
                    'current_location': tracking_info.get('current_location'),
                    'estimated_delivery': tracking_info.get('estimated_delivery'),
                    'delivery_date': tracking_info.get('delivery_date'),
                    'receiver_name': tracking_info.get('receiver_name'),
                    'tracking_events': tracking_info.get('events', []),
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Takip bilgisi bulunamadı'),
                    'error_code': result.get('error_code'),
                    'data': result
                }
                
        except Exception as e:
            self.logger.error(f"MNG Kargo takip hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_shipping_price(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kargo fiyat sorgulama
        
        Args:
            price_data: Fiyat sorgu bilgileri
            
        Returns:
            Fiyat bilgileri
        """
        try:
            # Zorunlu alanlar
            required_fields = ['origin_city', 'destination_city', 'weight', 'piece_count']
            for field in required_fields:
                if field not in price_data:
                    raise ValueError(f"Zorunlu alan eksik: {field}")
            
            # İstek parametreleri
            params = {
                'origin_city': price_data['origin_city'],
                'destination_city': price_data['destination_city'],
                'weight': price_data['weight'],
                'piece_count': price_data['piece_count'],
                'volume': price_data.get('volume', 0),
                'declared_value': price_data.get('declared_value', 0),
                'service_type': self.service_types.get(
                    price_data.get('service_type', 'standard'), 1
                ),
                'cargo_type': self.cargo_types.get(
                    price_data.get('cargo_type', 'package'), 1
                ),
                'insurance': price_data.get('insurance', False),
                'collect_on_delivery': price_data.get('collect_on_delivery', 0)
            }
            
            # API isteği gönder
            response = requests.get(
                f"{self.base_url}{self.endpoints['get_price']}",
                headers=self._get_auth_headers(),
                params=params,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                price_info = result.get('price_info', {})
                
                return {
                    'success': True,
                    'base_price': price_info.get('base_price', 0),
                    'fuel_surcharge': price_info.get('fuel_surcharge', 0),
                    'insurance_fee': price_info.get('insurance_fee', 0),
                    'cod_fee': price_info.get('cod_fee', 0),
                    'total_price': price_info.get('total_price', 0),
                    'currency': price_info.get('currency', 'TRY'),
                    'estimated_delivery_days': price_info.get('estimated_delivery_days', 1),
                    'service_options': price_info.get('service_options', []),
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Fiyat bilgisi alınamadı'),
                    'error_code': result.get('error_code'),
                    'data': result
                }
                
        except Exception as e:
            self.logger.error(f"MNG Kargo fiyat sorgulama hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_shipment(self, tracking_number: str, reason: str = '') -> Dict[str, Any]:
        """
        Kargo iptal etme
        
        Args:
            tracking_number: Takip numarası
            reason: İptal nedeni
            
        Returns:
            İptal sonucu
        """
        try:
            request_data = {
                'tracking_number': tracking_number,
                'reason': reason
            }
            
            # API isteği gönder
            response = requests.post(
                f"{self.base_url}{self.endpoints['cancel_shipment']}",
                headers=self._get_auth_headers(),
                json=request_data,
                timeout=30
            )
            
            result = response.json()
            
            return {
                'success': response.status_code == 200 and result.get('success'),
                'message': result.get('message', ''),
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"MNG Kargo iptal hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_cities(self) -> Dict[str, Any]:
        """
        Şehir listesi
        
        Returns:
            Şehir listesi
        """
        try:
            response = requests.get(
                f"{self.base_url}{self.endpoints['get_cities']}",
                headers=self._get_auth_headers(),
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                return {
                    'success': True,
                    'cities': result.get('cities', []),
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Şehir listesi alınamadı'),
                    'data': result
                }
                
        except Exception as e:
            self.logger.error(f"MNG Kargo şehir listesi hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_districts(self, city_code: str) -> Dict[str, Any]:
        """
        İlçe listesi
        
        Args:
            city_code: Şehir kodu
            
        Returns:
            İlçe listesi
        """
        try:
            response = requests.get(
                f"{self.base_url}{self.endpoints['get_districts']}",
                headers=self._get_auth_headers(),
                params={'city_code': city_code},
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                return {
                    'success': True,
                    'districts': result.get('districts', []),
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'İlçe listesi alınamadı'),
                    'data': result
                }
                
        except Exception as e:
            self.logger.error(f"MNG Kargo ilçe listesi hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_pickup_request(self, pickup_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Toplama talebi oluşturma
        
        Args:
            pickup_data: Toplama bilgileri
            
        Returns:
            Toplama talebi sonucu
        """
        try:
            # Zorunlu alanlar
            required_fields = [
                'contact_name', 'contact_phone', 'address', 'city',
                'pickup_date', 'piece_count', 'total_weight'
            ]
            
            for field in required_fields:
                if field not in pickup_data:
                    raise ValueError(f"Zorunlu alan eksik: {field}")
            
            request_data = {
                'contact_name': pickup_data['contact_name'],
                'contact_phone': pickup_data['contact_phone'],
                'address': pickup_data['address'],
                'city': pickup_data['city'],
                'district': pickup_data.get('district', ''),
                'pickup_date': pickup_data['pickup_date'],
                'pickup_time_start': pickup_data.get('pickup_time_start', '09:00'),
                'pickup_time_end': pickup_data.get('pickup_time_end', '18:00'),
                'piece_count': pickup_data['piece_count'],
                'total_weight': pickup_data['total_weight'],
                'description': pickup_data.get('description', ''),
                'special_instructions': pickup_data.get('special_instructions', '')
            }
            
            # API isteği gönder
            response = requests.post(
                f"{self.base_url}{self.endpoints['create_pickup']}",
                headers=self._get_auth_headers(),
                json=request_data,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                return {
                    'success': True,
                    'pickup_id': result.get('pickup_id'),
                    'pickup_number': result.get('pickup_number'),
                    'estimated_pickup_time': result.get('estimated_pickup_time'),
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Toplama talebi oluşturulamadı'),
                    'error_code': result.get('error_code'),
                    'data': result
                }
                
        except Exception as e:
            self.logger.error(f"MNG Kargo toplama talebi hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_barcode_image(self, tracking_number: str, format: str = 'PNG') -> Dict[str, Any]:
        """
        Barkod görüntüsü alma
        
        Args:
            tracking_number: Takip numarası
            format: Görüntü formatı (PNG, PDF, JPG)
            
        Returns:
            Barkod bilgileri
        """
        try:
            params = {
                'tracking_number': tracking_number,
                'format': format.upper()
            }
            
            response = requests.get(
                f"{self.base_url}{self.endpoints['get_barcode']}",
                headers=self._get_auth_headers(),
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                if format.upper() in ['PNG', 'JPG']:
                    return {
                        'success': True,
                        'barcode_image': response.content,
                        'content_type': response.headers.get('content-type'),
                        'format': format.upper()
                    }
                else:
                    result = response.json()
                    return {
                        'success': True,
                        'barcode_url': result.get('barcode_url'),
                        'barcode_base64': result.get('barcode_base64'),
                        'data': result
                    }
            else:
                return {
                    'success': False,
                    'error': 'Barkod alınamadı'
                }
                
        except Exception as e:
            self.logger.error(f"MNG Kargo barkod hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_waybill(self, tracking_number: str, format: str = 'PDF') -> Dict[str, Any]:
        """
        İrsaliye alma
        
        Args:
            tracking_number: Takip numarası
            format: Dosya formatı (PDF, HTML)
            
        Returns:
            İrsaliye bilgileri
        """
        try:
            params = {
                'tracking_number': tracking_number,
                'format': format.upper()
            }
            
            response = requests.get(
                f"{self.base_url}{self.endpoints['get_waybill']}",
                headers=self._get_auth_headers(),
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                if format.upper() == 'PDF':
                    return {
                        'success': True,
                        'waybill_pdf': response.content,
                        'content_type': 'application/pdf',
                        'format': 'PDF'
                    }
                else:
                    result = response.json()
                    return {
                        'success': True,
                        'waybill_url': result.get('waybill_url'),
                        'waybill_html': result.get('waybill_html'),
                        'data': result
                    }
            else:
                return {
                    'success': False,
                    'error': 'İrsaliye alınamadı'
                }
                
        except Exception as e:
            self.logger.error(f"MNG Kargo irsaliye hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_service_types(self) -> Dict[str, Any]:
        """Servis tiplerini döndür"""
        return {
            'success': True,
            'service_types': {
                name: {
                    'id': service_id,
                    'name': name.replace('_', ' ').title(),
                    'description': self._get_service_description(name)
                }
                for name, service_id in self.service_types.items()
            }
        }
    
    def _get_service_description(self, service_type: str) -> str:
        """Servis tipi açıklaması"""
        descriptions = {
            'standard': 'Standart kargo hizmeti',
            'express': 'Hızlı kargo hizmeti',
            'same_day': 'Aynı gün teslimat',
            'next_day': 'Ertesi gün teslimat',
            'economic': 'Ekonomik kargo hizmeti'
        }
        return descriptions.get(service_type, '')
    
    def format_tracking_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takip olaylarını formatla
        
        Args:
            events: Ham takip olayları
            
        Returns:
            Formatlanmış takip olayları
        """
        formatted_events = []
        for event in events:
            formatted_events.append({
                'date': event.get('date'),
                'time': event.get('time'),
                'location': event.get('location'),
                'status': event.get('status'),
                'description': event.get('description'),
                'branch': event.get('branch'),
                'employee': event.get('employee')
            })
        return formatted_events