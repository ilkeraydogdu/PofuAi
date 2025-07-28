#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Controller
======================

Entegrasyon yönetimi controller'ı
- Entegrasyon ekleme/kaldırma
- Entegrasyon aktivasyonu
- Ürün/sipariş senkronizasyonu
- Stok/fiyat güncellemeleri
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import request, jsonify, session

from app.Controllers.BaseController import BaseController
from core.Services.logger import LoggerService
from core.Services.validators import Validator
from core.Integrations.integration_manager import integration_manager


class IntegrationController(BaseController):
    """
    Entegrasyon yönetimi controller'ı
    """
    
    def __init__(self):
        super().__init__()
        self.logger = LoggerService.get_logger()
        self.validator = Validator()
        self.integration_manager = integration_manager
        
        self.logger.info("Integration Controller başlatıldı")
    
    async def list_integrations(self):
        """
        Kullanıcının entegrasyonlarını listele
        
        GET /api/integrations
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Tüm entegrasyon durumlarını al
            status_result = await self.integration_manager.get_integration_status()
            
            if status_result['success']:
                # Kullanıcıya ait olanları filtrele
                user_integrations = []
                for integration in status_result.get('integrations', []):
                    # Veritabanından kullanıcı kontrolü yap
                    query = """
                    SELECT user_id FROM integrations 
                    WHERE id = %s AND deleted_at IS NULL
                    """
                    result = await self.db.fetch_one(query, (integration['id'],))
                    
                    if result and result[0] == user['id']:
                        user_integrations.append(integration)
                
                return self.success_response(
                    'Entegrasyonlar başarıyla listelendi',
                    {
                        'integrations': user_integrations,
                        'total': len(user_integrations)
                    }
                )
            else:
                return self.error_response('Entegrasyonlar alınamadı', 500)
            
        except Exception as e:
            self.logger.error(f"Entegrasyon listeleme hatası: {e}")
            return self.error_response('Entegrasyonlar listelenirken hata oluştu', 500)
    
    async def add_integration(self):
        """
        Yeni entegrasyon ekle
        
        POST /api/integrations
        
        Body:
        {
            "integration_type": "marketplace",
            "integration_name": "trendyol",
            "config": {
                "api_key": "xxx",
                "api_secret": "yyy",
                "seller_id": "12345"
            }
        }
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Request verilerini al
            data = request.get_json()
            if not data:
                return self.error_response('Geçersiz JSON verisi', 400)
            
            # Validasyon
            validation_rules = {
                'integration_type': 'required|in:marketplace,ecommerce,accounting,shipping,payment,social,erp,crm',
                'integration_name': 'required|string|min:2|max:100',
                'config': 'required|dict'
            }
            
            validation_result = self.validator.validate(data, validation_rules)
            if not validation_result['is_valid']:
                return self.error_response('Validasyon hatası', 400, validation_result['errors'])
            
            # Entegrasyonu ekle
            result = await self.integration_manager.add_integration(
                integration_type=data['integration_type'],
                integration_name=data['integration_name'],
                config=data['config'],
                user_id=user['id']
            )
            
            if result['success']:
                self.logger.info(f"Yeni entegrasyon eklendi: {data['integration_name']} (User: {user['id']})")
                return self.success_response(
                    'Entegrasyon başarıyla eklendi',
                    {
                        'integration_id': result['integration_id']
                    }
                )
            else:
                return self.error_response(
                    result.get('error', 'Entegrasyon eklenemedi'),
                    400,
                    {'code': result.get('code')}
                )
            
        except Exception as e:
            self.logger.error(f"Entegrasyon ekleme hatası: {e}")
            return self.error_response('Entegrasyon eklenirken hata oluştu', 500)
    
    async def activate_integration(self, integration_id: int):
        """
        Entegrasyonu aktifleştir
        
        POST /api/integrations/{integration_id}/activate
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Entegrasyonun kullanıcıya ait olduğunu kontrol et
            if not await self._check_integration_ownership(integration_id, user['id']):
                return self.error_response('Bu entegrasyona erişim yetkiniz yok', 403)
            
            # Entegrasyonu aktifleştir
            result = await self.integration_manager.activate_integration(integration_id)
            
            if result['success']:
                self.logger.info(f"Entegrasyon aktifleştirildi: {integration_id} (User: {user['id']})")
                return self.success_response(result['message'])
            else:
                return self.error_response(
                    result.get('error', 'Entegrasyon aktifleştirilemedi'),
                    400,
                    {'code': result.get('code')}
                )
            
        except Exception as e:
            self.logger.error(f"Entegrasyon aktivasyon hatası: {e}")
            return self.error_response('Entegrasyon aktifleştirilirken hata oluştu', 500)
    
    async def deactivate_integration(self, integration_id: int):
        """
        Entegrasyonu deaktif et
        
        POST /api/integrations/{integration_id}/deactivate
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Entegrasyonun kullanıcıya ait olduğunu kontrol et
            if not await self._check_integration_ownership(integration_id, user['id']):
                return self.error_response('Bu entegrasyona erişim yetkiniz yok', 403)
            
            # Entegrasyonu deaktif et
            result = await self.integration_manager.deactivate_integration(integration_id)
            
            if result['success']:
                self.logger.info(f"Entegrasyon deaktif edildi: {integration_id} (User: {user['id']})")
                return self.success_response(result['message'])
            else:
                return self.error_response(
                    result.get('error', 'Entegrasyon deaktif edilemedi'),
                    400,
                    {'code': result.get('code')}
                )
            
        except Exception as e:
            self.logger.error(f"Entegrasyon deaktivasyon hatası: {e}")
            return self.error_response('Entegrasyon deaktif edilirken hata oluştu', 500)
    
    async def sync_products(self):
        """
        Ürünleri tüm aktif entegrasyonlara senkronize et
        
        POST /api/integrations/sync/products
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Senkronizasyonu başlat
            self.logger.info(f"Ürün senkronizasyonu başlatılıyor (User: {user['id']})")
            
            result = await self.integration_manager.sync_all_products(user['id'])
            
            if result['success']:
                return self.success_response(
                    'Ürün senkronizasyonu tamamlandı',
                    {
                        'total_integrations': result['total_integrations'],
                        'successful_syncs': result['successful_syncs'],
                        'failed_syncs': result['failed_syncs'],
                        'details': result.get('results', {})
                    }
                )
            else:
                return self.error_response(
                    result.get('error', 'Senkronizasyon başarısız'),
                    400,
                    {'code': result.get('code')}
                )
            
        except Exception as e:
            self.logger.error(f"Ürün senkronizasyon hatası: {e}")
            return self.error_response('Ürün senkronizasyonu sırasında hata oluştu', 500)
    
    async def sync_orders(self):
        """
        Tüm aktif entegrasyonlardan siparişleri çek
        
        POST /api/integrations/sync/orders
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Senkronizasyonu başlat
            self.logger.info(f"Sipariş senkronizasyonu başlatılıyor (User: {user['id']})")
            
            result = await self.integration_manager.sync_all_orders(user['id'])
            
            if result['success']:
                return self.success_response(
                    'Sipariş senkronizasyonu tamamlandı',
                    {
                        'total_orders': result['total_orders'],
                        'saved_orders': result['saved_orders'],
                        'sync_results': result.get('sync_results', {})
                    }
                )
            else:
                return self.error_response(
                    result.get('error', 'Senkronizasyon başarısız'),
                    400,
                    {'code': result.get('code')}
                )
            
        except Exception as e:
            self.logger.error(f"Sipariş senkronizasyon hatası: {e}")
            return self.error_response('Sipariş senkronizasyonu sırasında hata oluştu', 500)
    
    async def update_stock(self):
        """
        Tüm entegrasyonlarda stok güncelle
        
        POST /api/integrations/update/stock
        
        Body:
        {
            "product_id": 123,
            "new_stock": 50
        }
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Request verilerini al
            data = request.get_json()
            if not data:
                return self.error_response('Geçersiz JSON verisi', 400)
            
            # Validasyon
            validation_rules = {
                'product_id': 'required|integer|min:1',
                'new_stock': 'required|integer|min:0'
            }
            
            validation_result = self.validator.validate(data, validation_rules)
            if not validation_result['is_valid']:
                return self.error_response('Validasyon hatası', 400, validation_result['errors'])
            
            # Ürünün kullanıcıya ait olduğunu kontrol et
            product_query = """
            SELECT user_id FROM products WHERE id = %s
            """
            product_result = await self.db.fetch_one(product_query, (data['product_id'],))
            
            if not product_result or product_result[0] != user['id']:
                return self.error_response('Bu ürüne erişim yetkiniz yok', 403)
            
            # Stok güncellemeyi başlat
            result = await self.integration_manager.update_stock_all(
                data['product_id'],
                data['new_stock']
            )
            
            if result['success']:
                # Kendi veritabanımızda da güncelle
                update_query = """
                UPDATE products SET stock = %s, updated_at = NOW()
                WHERE id = %s
                """
                await self.db.execute(update_query, (data['new_stock'], data['product_id']))
                
                return self.success_response(
                    'Stok güncellemesi tamamlandı',
                    {
                        'total_integrations': result['total_integrations'],
                        'successful_updates': result['successful_updates'],
                        'failed_updates': result['failed_updates'],
                        'results': result.get('results', {})
                    }
                )
            else:
                return self.error_response(
                    result.get('error', 'Stok güncellemesi başarısız'),
                    400,
                    {'code': result.get('code')}
                )
            
        except Exception as e:
            self.logger.error(f"Stok güncelleme hatası: {e}")
            return self.error_response('Stok güncellenirken hata oluştu', 500)
    
    async def get_integration_details(self, integration_id: int):
        """
        Entegrasyon detaylarını getir
        
        GET /api/integrations/{integration_id}
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Entegrasyonun kullanıcıya ait olduğunu kontrol et
            if not await self._check_integration_ownership(integration_id, user['id']):
                return self.error_response('Bu entegrasyona erişim yetkiniz yok', 403)
            
            # Entegrasyon detaylarını al
            status_result = await self.integration_manager.get_integration_status(integration_id)
            
            if status_result['success']:
                # Son senkronizasyon bilgilerini ekle
                sync_query = """
                SELECT sync_type, total_items, successful_items, failed_items, 
                       created_at, duration_seconds
                FROM sync_logs
                WHERE integration_id = %s
                ORDER BY created_at DESC
                LIMIT 5
                """
                
                sync_logs = await self.db.fetch_all(sync_query, (integration_id,))
                
                recent_syncs = []
                for log in sync_logs:
                    recent_syncs.append({
                        'sync_type': log[0],
                        'total_items': log[1],
                        'successful_items': log[2],
                        'failed_items': log[3],
                        'created_at': log[4].isoformat() if log[4] else None,
                        'duration_seconds': log[5]
                    })
                
                return self.success_response(
                    'Entegrasyon detayları başarıyla alındı',
                    {
                        'integration': status_result['status'],
                        'recent_syncs': recent_syncs
                    }
                )
            else:
                return self.error_response(
                    status_result.get('error', 'Detaylar alınamadı'),
                    404,
                    {'code': status_result.get('code')}
                )
            
        except Exception as e:
            self.logger.error(f"Entegrasyon detay hatası: {e}")
            return self.error_response('Entegrasyon detayları alınırken hata oluştu', 500)
    
    async def delete_integration(self, integration_id: int):
        """
        Entegrasyonu sil (soft delete)
        
        DELETE /api/integrations/{integration_id}
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Entegrasyonun kullanıcıya ait olduğunu kontrol et
            if not await self._check_integration_ownership(integration_id, user['id']):
                return self.error_response('Bu entegrasyona erişim yetkiniz yok', 403)
            
            # Önce deaktif et
            await self.integration_manager.deactivate_integration(integration_id)
            
            # Soft delete yap
            delete_query = """
            UPDATE integrations 
            SET deleted_at = NOW(), is_active = FALSE
            WHERE id = %s
            """
            
            await self.db.execute(delete_query, (integration_id,))
            
            self.logger.info(f"Entegrasyon silindi: {integration_id} (User: {user['id']})")
            
            return self.success_response('Entegrasyon başarıyla silindi')
            
        except Exception as e:
            self.logger.error(f"Entegrasyon silme hatası: {e}")
            return self.error_response('Entegrasyon silinirken hata oluştu', 500)
    
    async def get_sync_logs(self):
        """
        Senkronizasyon loglarını getir
        
        GET /api/integrations/sync-logs
        
        Query params:
        - integration_id: Spesifik entegrasyon (opsiyonel)
        - sync_type: products, orders, stock, price (opsiyonel)
        - page: Sayfa numarası
        - limit: Sayfa başına kayıt sayısı
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Query parametreleri
            integration_id = request.args.get('integration_id', type=int)
            sync_type = request.args.get('sync_type')
            page = max(1, request.args.get('page', 1, type=int))
            limit = min(100, max(10, request.args.get('limit', 20, type=int)))
            offset = (page - 1) * limit
            
            # Temel query
            query = """
            SELECT sl.id, sl.integration_id, i.integration_name, sl.sync_type,
                   sl.sync_direction, sl.total_items, sl.successful_items, 
                   sl.failed_items, sl.started_at, sl.completed_at, 
                   sl.duration_seconds, sl.created_at
            FROM sync_logs sl
            LEFT JOIN integrations i ON sl.integration_id = i.id
            WHERE sl.user_id = %s
            """
            
            params = [user['id']]
            
            # Filtreler
            if integration_id:
                # Entegrasyonun kullanıcıya ait olduğunu kontrol et
                if not await self._check_integration_ownership(integration_id, user['id']):
                    return self.error_response('Bu entegrasyona erişim yetkiniz yok', 403)
                
                query += " AND sl.integration_id = %s"
                params.append(integration_id)
            
            if sync_type:
                query += " AND sl.sync_type = %s"
                params.append(sync_type)
            
            # Sıralama ve limit
            query += " ORDER BY sl.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            # Logları al
            logs = await self.db.fetch_all(query, params)
            
            # Toplam sayı
            count_query = """
            SELECT COUNT(*) FROM sync_logs sl
            WHERE sl.user_id = %s
            """
            count_params = [user['id']]
            
            if integration_id:
                count_query += " AND sl.integration_id = %s"
                count_params.append(integration_id)
            
            if sync_type:
                count_query += " AND sl.sync_type = %s"
                count_params.append(sync_type)
            
            total_result = await self.db.fetch_one(count_query, count_params)
            total = total_result[0] if total_result else 0
            
            # Sonuçları formatla
            formatted_logs = []
            for log in logs:
                formatted_logs.append({
                    'id': log[0],
                    'integration_id': log[1],
                    'integration_name': log[2],
                    'sync_type': log[3],
                    'sync_direction': log[4],
                    'total_items': log[5],
                    'successful_items': log[6],
                    'failed_items': log[7],
                    'started_at': log[8].isoformat() if log[8] else None,
                    'completed_at': log[9].isoformat() if log[9] else None,
                    'duration_seconds': log[10],
                    'created_at': log[11].isoformat() if log[11] else None
                })
            
            return self.success_response(
                'Senkronizasyon logları başarıyla alındı',
                {
                    'logs': formatted_logs,
                    'pagination': {
                        'total': total,
                        'page': page,
                        'limit': limit,
                        'pages': (total + limit - 1) // limit
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Senkronizasyon logları alma hatası: {e}")
            return self.error_response('Loglar alınırken hata oluştu', 500)
    
    async def get_available_integrations(self):
        """
        Kullanılabilir entegrasyon listesini getir
        
        GET /api/integrations/available
        """
        try:
            # Giriş kontrolü gerekmiyor, herkes görebilir
            
            # Kategorileri ve entegrasyonları al
            categories = self.integration_manager.categories
            
            # Her kategori için detaylı bilgi hazırla
            available_integrations = {}
            
            for category, integrations in categories.items():
                available_integrations[category] = []
                
                for integration in integrations:
                    # Entegrasyon bilgilerini ekle
                    info = {
                        'name': integration,
                        'display_name': self._get_integration_display_name(integration),
                        'description': self._get_integration_description(integration),
                        'required_fields': self._get_integration_required_fields(integration),
                        'logo_url': f"/static/images/integrations/{integration}.png"
                    }
                    available_integrations[category].append(info)
            
            return self.success_response(
                'Kullanılabilir entegrasyonlar başarıyla listelendi',
                {
                    'categories': available_integrations,
                    'total_categories': len(categories),
                    'total_integrations': sum(len(v) for v in categories.values())
                }
            )
            
        except Exception as e:
            self.logger.error(f"Kullanılabilir entegrasyonlar listesi hatası: {e}")
            return self.error_response('Liste alınırken hata oluştu', 500)
    
    async def _check_integration_ownership(self, integration_id: int, user_id: int) -> bool:
        """Entegrasyonun kullanıcıya ait olup olmadığını kontrol et"""
        try:
            query = """
            SELECT user_id FROM integrations 
            WHERE id = %s AND deleted_at IS NULL
            """
            result = await self.db.fetch_one(query, (integration_id,))
            
            return result and result[0] == user_id
            
        except Exception as e:
            self.logger.error(f"Sahiplik kontrolü hatası: {e}")
            return False
    
    def _get_integration_display_name(self, integration: str) -> str:
        """Entegrasyon görünen adını getir"""
        display_names = {
            'trendyol': 'Trendyol',
            'hepsiburada': 'Hepsiburada',
            'n11': 'N11',
            'gittigidiyor': 'GittiGidiyor',
            'amazon': 'Amazon',
            'amazon_tr': 'Amazon Türkiye',
            'ebay': 'eBay',
            'etsy': 'Etsy',
            'aliexpress': 'AliExpress',
            'walmart': 'Walmart',
            'shopify': 'Shopify',
            'woocommerce': 'WooCommerce',
            'magento': 'Magento',
            'prestashop': 'PrestaShop',
            'opencart': 'OpenCart',
            'bigcommerce': 'BigCommerce',
            'wix': 'Wix',
            'squarespace': 'Squarespace',
            'logo': 'Logo',
            'mikro': 'Mikro',
            'netsis': 'Netsis',
            'parasut': 'Paraşüt',
            'quickbooks': 'QuickBooks',
            'sage': 'Sage',
            'yurtici': 'Yurtiçi Kargo',
            'aras': 'Aras Kargo',
            'mng': 'MNG Kargo',
            'ptt': 'PTT Kargo',
            'ups': 'UPS',
            'dhl': 'DHL',
            'fedex': 'FedEx',
            'iyzico': 'iyzico',
            'paytr': 'PayTR',
            'payu': 'PayU',
            'stripe': 'Stripe',
            'paypal': 'PayPal',
            'square': 'Square',
            'facebook': 'Facebook',
            'instagram': 'Instagram',
            'twitter': 'Twitter',
            'tiktok': 'TikTok',
            'pinterest': 'Pinterest',
            'sap': 'SAP',
            'oracle': 'Oracle',
            'microsoft_dynamics': 'Microsoft Dynamics',
            'netsuite': 'NetSuite',
            'salesforce': 'Salesforce',
            'hubspot': 'HubSpot',
            'zoho': 'Zoho CRM',
            'pipedrive': 'Pipedrive'
        }
        
        return display_names.get(integration, integration.title())
    
    def _get_integration_description(self, integration: str) -> str:
        """Entegrasyon açıklamasını getir"""
        descriptions = {
            'trendyol': 'Türkiye\'nin lider e-ticaret platformu',
            'hepsiburada': 'Her şey ayağına gelsin',
            'n11': 'Hayat sana gelir',
            'shopify': 'Profesyonel e-ticaret altyapısı',
            'woocommerce': 'WordPress tabanlı e-ticaret çözümü',
            'parasut': 'Bulut tabanlı ön muhasebe programı',
            'yurtici': 'Türkiye\'nin yaygın kargo şirketi',
            'stripe': 'Global ödeme altyapısı',
            'facebook': 'Facebook Shop ve Marketplace entegrasyonu',
            'salesforce': 'Dünyanın lider CRM platformu'
        }
        
        return descriptions.get(integration, f'{self._get_integration_display_name(integration)} entegrasyonu')
    
    def _get_integration_required_fields(self, integration: str) -> List[Dict[str, str]]:
        """Entegrasyon için gerekli alanları getir"""
        fields = {
            'trendyol': [
                {'name': 'api_key', 'label': 'API Anahtarı', 'type': 'text'},
                {'name': 'api_secret', 'label': 'API Secret', 'type': 'password'},
                {'name': 'seller_id', 'label': 'Satıcı ID', 'type': 'text'}
            ],
            'hepsiburada': [
                {'name': 'username', 'label': 'Kullanıcı Adı', 'type': 'text'},
                {'name': 'password', 'label': 'Şifre', 'type': 'password'},
                {'name': 'merchant_id', 'label': 'Merchant ID', 'type': 'text'}
            ],
            'shopify': [
                {'name': 'shop_domain', 'label': 'Mağaza Domain', 'type': 'text'},
                {'name': 'api_key', 'label': 'API Key', 'type': 'text'},
                {'name': 'password', 'label': 'API Password', 'type': 'password'}
            ],
            'parasut': [
                {'name': 'company_id', 'label': 'Firma ID', 'type': 'text'},
                {'name': 'client_id', 'label': 'Client ID', 'type': 'text'},
                {'name': 'client_secret', 'label': 'Client Secret', 'type': 'password'}
            ]
        }
        
        # Varsayılan alanlar
        default_fields = [
            {'name': 'api_key', 'label': 'API Key', 'type': 'text'},
            {'name': 'api_secret', 'label': 'API Secret', 'type': 'password'}
        ]
        
        return fields.get(integration, default_fields)