"""
Letgo Marketplace API Integration
İkinci el alışveriş platformu entegrasyonu
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
import requests

from core.Services.base_service import BaseService
from core.Services.cache_service import CacheService


class LetgoMarketplaceAPI(BaseService):
    """Letgo API Entegrasyonu"""
    
    def __init__(self):
        super().__init__()
        self.api_key = self.get_config('letgo.api_key')
        self.api_secret = self.get_config('letgo.api_secret')
        self.user_id = self.get_config('letgo.user_id')
        self.base_url = "https://api.letgo.com/api/v2"
        self.cache = CacheService()
        self.logger = logging.getLogger(__name__)
        
    def _get_auth_headers(self) -> Dict[str, str]:
        """API kimlik doğrulama başlıkları"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-User-Id': self.user_id
        }
        
    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Letgo'da ürün oluştur"""
        try:
            # Kategori eşleştirmesi
            category_id = self._map_category(product_data.get('category'))
            
            # Konum bilgisi
            location = self._get_location(product_data)
            
            # İlan verilerini hazırla
            listing_data = {
                'title': product_data['name'],
                'description': product_data['description'],
                'price': float(product_data['price']),
                'currency': 'TRY',
                'category_id': category_id,
                'condition': product_data.get('condition', 'used'),
                'images': product_data.get('images', []),
                'location': location,
                'contact_preference': product_data.get('contact_preference', 'chat'),
                'negotiable': product_data.get('negotiable', True)
            }
            
            # API çağrısı simülasyonu
            self.logger.info(f"Creating listing on Letgo: {listing_data['title']}")
            
            # Başarılı yanıt
            return {
                'success': True,
                'listing_id': f"LETGO_{datetime.now().timestamp()}",
                'listing_url': f"https://www.letgo.com/item/{listing_data['title'].lower().replace(' ', '-')}",
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Letgo create product error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def update_product(self, listing_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """İlan güncelle"""
        try:
            allowed_updates = ['price', 'description', 'images', 'negotiable', 'condition']
            filtered_data = {k: v for k, v in update_data.items() if k in allowed_updates}
            
            self.logger.info(f"Updating Letgo listing {listing_id}")
            
            return {
                'success': True,
                'listing_id': listing_id,
                'updated_fields': list(filtered_data.keys()),
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Letgo update error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def delete_product(self, listing_id: str) -> Dict[str, Any]:
        """İlan sil"""
        try:
            self.logger.info(f"Deleting Letgo listing {listing_id}")
            
            return {
                'success': True,
                'listing_id': listing_id,
                'deleted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Letgo delete error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def get_product(self, listing_id: str) -> Dict[str, Any]:
        """İlan detaylarını getir"""
        cache_key = f"letgo_listing_{listing_id}"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
            
        try:
            # API çağrısı simülasyonu
            listing_data = {
                'listing_id': listing_id,
                'title': 'Örnek Letgo İlanı',
                'price': 2500.0,
                'currency': 'TRY',
                'description': 'Temiz kullanılmış ürün',
                'condition': 'used',
                'negotiable': True,
                'images': [],
                'views': 856,
                'likes': 23,
                'chat_count': 12,
                'status': 'active',
                'location': {
                    'city': 'İstanbul',
                    'district': 'Beşiktaş',
                    'neighborhood': 'Levent'
                },
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            self.cache.set(cache_key, listing_data, 300)
            return listing_data
            
        except Exception as e:
            self.logger.error(f"Letgo get product error: {str(e)}")
            return None
            
    async def search_products(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """İlan ara"""
        try:
            search_params = {
                'q': query,
                'offset': filters.get('offset', 0) if filters else 0,
                'limit': filters.get('limit', 20) if filters else 20
            }
            
            if filters:
                if 'category' in filters:
                    search_params['category_id'] = self._map_category(filters['category'])
                if 'min_price' in filters:
                    search_params['price_min'] = filters['min_price']
                if 'max_price' in filters:
                    search_params['price_max'] = filters['max_price']
                if 'condition' in filters:
                    search_params['condition'] = filters['condition']
                if 'location' in filters:
                    search_params['location'] = filters['location']
                    
            # Simülasyon sonuçları
            results = []
            for i in range(5):
                results.append({
                    'listing_id': f"LETGO_{i}",
                    'title': f"{query} - Letgo İlan {i+1}",
                    'price': 500 + (i * 300),
                    'currency': 'TRY',
                    'condition': 'used' if i % 2 == 0 else 'like_new',
                    'location': 'İstanbul',
                    'image': f"https://example.com/letgo_image_{i}.jpg",
                    'created_at': datetime.now().isoformat()
                })
                
            return {
                'success': True,
                'total': len(results),
                'listings': results
            }
            
        except Exception as e:
            self.logger.error(f"Letgo search error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'listings': []
            }
            
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Kategori listesini getir"""
        cache_key = "letgo_categories"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
            
        try:
            # Letgo kategorileri
            categories = [
                {'id': 1, 'name': 'Elektronik', 'icon': 'electronics'},
                {'id': 2, 'name': 'Ev & Bahçe', 'icon': 'home'},
                {'id': 3, 'name': 'Moda & Aksesuar', 'icon': 'fashion'},
                {'id': 4, 'name': 'Bebek & Çocuk', 'icon': 'baby'},
                {'id': 5, 'name': 'Hobi & Eğlence', 'icon': 'hobbies'},
                {'id': 6, 'name': 'Spor & Outdoor', 'icon': 'sports'},
                {'id': 7, 'name': 'Araç', 'icon': 'vehicles'},
                {'id': 8, 'name': 'Diğer', 'icon': 'other'},
                
                # Alt kategoriler
                {'id': 101, 'name': 'Cep Telefonu', 'parent_id': 1},
                {'id': 102, 'name': 'Bilgisayar', 'parent_id': 1},
                {'id': 103, 'name': 'Tablet', 'parent_id': 1},
                {'id': 104, 'name': 'TV & Ses Sistemleri', 'parent_id': 1},
                {'id': 105, 'name': 'Oyun Konsolları', 'parent_id': 1},
                
                {'id': 201, 'name': 'Mobilya', 'parent_id': 2},
                {'id': 202, 'name': 'Dekorasyon', 'parent_id': 2},
                {'id': 203, 'name': 'Beyaz Eşya', 'parent_id': 2},
                {'id': 204, 'name': 'Küçük Ev Aletleri', 'parent_id': 2},
                
                {'id': 301, 'name': 'Kadın Giyim', 'parent_id': 3},
                {'id': 302, 'name': 'Erkek Giyim', 'parent_id': 3},
                {'id': 303, 'name': 'Ayakkabı', 'parent_id': 3},
                {'id': 304, 'name': 'Çanta', 'parent_id': 3},
                {'id': 305, 'name': 'Aksesuar', 'parent_id': 3}
            ]
            
            self.cache.set(cache_key, categories, 86400)  # 24 saat cache
            return categories
            
        except Exception as e:
            self.logger.error(f"Letgo get categories error: {str(e)}")
            return []
            
    async def get_my_listings(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Kullanıcının ilanlarını getir"""
        try:
            # Simülasyon ilanları
            listings = [
                {
                    'listing_id': 'LETGO_001',
                    'title': 'iPhone 12 Pro',
                    'price': 15000,
                    'status': 'active',
                    'views': 234,
                    'likes': 12,
                    'created_at': datetime.now().isoformat()
                },
                {
                    'listing_id': 'LETGO_002',
                    'title': 'Gaming Laptop',
                    'price': 8500,
                    'status': 'active',
                    'views': 156,
                    'likes': 8,
                    'created_at': (datetime.now() - timedelta(days=3)).isoformat()
                },
                {
                    'listing_id': 'LETGO_003',
                    'title': 'Bisiklet',
                    'price': 2000,
                    'status': 'sold',
                    'views': 89,
                    'likes': 5,
                    'created_at': (datetime.now() - timedelta(days=7)).isoformat()
                }
            ]
            
            if status:
                listings = [l for l in listings if l['status'] == status]
                
            return {
                'success': True,
                'total': len(listings),
                'listings': listings
            }
            
        except Exception as e:
            self.logger.error(f"Letgo get my listings error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'listings': []
            }
            
    async def get_chat_messages(self, listing_id: str) -> List[Dict[str, Any]]:
        """İlan için gelen mesajları getir"""
        try:
            # Simülasyon mesajları
            messages = [
                {
                    'message_id': 'MSG_L001',
                    'listing_id': listing_id,
                    'sender': {
                        'user_id': 'USER_123',
                        'name': 'Mehmet K.',
                        'avatar': 'https://example.com/avatar1.jpg'
                    },
                    'message': 'Merhaba, ürün hala satılık mı?',
                    'timestamp': datetime.now().isoformat(),
                    'is_read': True
                },
                {
                    'message_id': 'MSG_L002',
                    'listing_id': listing_id,
                    'sender': {
                        'user_id': 'USER_124',
                        'name': 'Zeynep A.',
                        'avatar': 'https://example.com/avatar2.jpg'
                    },
                    'message': 'Fiyatta pazarlık payı var mı?',
                    'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                    'is_read': False
                }
            ]
            
            return {
                'success': True,
                'total': len(messages),
                'messages': messages
            }
            
        except Exception as e:
            self.logger.error(f"Letgo get chat messages error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'messages': []
            }
            
    async def mark_as_sold(self, listing_id: str, buyer_id: Optional[str] = None) -> Dict[str, Any]:
        """İlanı satıldı olarak işaretle"""
        try:
            self.logger.info(f"Marking Letgo listing {listing_id} as sold")
            
            return {
                'success': True,
                'listing_id': listing_id,
                'status': 'sold',
                'buyer_id': buyer_id,
                'sold_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Letgo mark as sold error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def boost_listing(self, listing_id: str, boost_type: str = 'standard') -> Dict[str, Any]:
        """İlanı öne çıkar"""
        try:
            boost_prices = {
                'standard': 50,
                'premium': 100,
                'featured': 200
            }
            
            price = boost_prices.get(boost_type, 50)
            
            self.logger.info(f"Boosting Letgo listing {listing_id} with {boost_type}")
            
            return {
                'success': True,
                'listing_id': listing_id,
                'boost_type': boost_type,
                'price': price,
                'boosted_until': (datetime.now() + timedelta(days=7)).isoformat(),
                'transaction_id': f"BOOST_{datetime.now().timestamp()}"
            }
            
        except Exception as e:
            self.logger.error(f"Letgo boost listing error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def _map_category(self, category_name: str) -> int:
        """Kategori eşleştirmesi"""
        category_map = {
            'electronics': 1,
            'computer': 102,
            'phone': 101,
            'fashion': 3,
            'home': 2,
            'sports': 6,
            'baby': 4,
            'hobbies': 5,
            'vehicles': 7,
            'other': 8
        }
        
        return category_map.get(category_name.lower(), 8)  # Default: Diğer
        
    def _get_location(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Konum bilgisini hazırla"""
        return {
            'latitude': product_data.get('latitude', 41.0082),
            'longitude': product_data.get('longitude', 28.9784),
            'city': product_data.get('city', 'İstanbul'),
            'district': product_data.get('district', 'Kadıköy'),
            'neighborhood': product_data.get('neighborhood'),
            'address': product_data.get('address')
        }
        
    async def report_listing(self, listing_id: str, reason: str, details: Optional[str] = None) -> Dict[str, Any]:
        """İlanı şikayet et"""
        try:
            valid_reasons = ['spam', 'fake', 'inappropriate', 'scam', 'other']
            
            if reason not in valid_reasons:
                return {
                    'success': False,
                    'error': f"Invalid reason. Must be one of: {', '.join(valid_reasons)}"
                }
                
            self.logger.info(f"Reporting Letgo listing {listing_id} for {reason}")
            
            return {
                'success': True,
                'report_id': f"REPORT_{datetime.now().timestamp()}",
                'listing_id': listing_id,
                'reason': reason,
                'details': details,
                'reported_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Letgo report listing error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }