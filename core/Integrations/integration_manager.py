#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Manager
===================

Tüm entegrasyonları yöneten ana sınıf
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from abc import ABC, abstractmethod

from core.Services.logger import LoggerService
from core.Database.connection import DatabaseConnection
from core.Services.cache_service import CacheService


class IntegrationBase(ABC):
    """Tüm entegrasyonlar için temel sınıf"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = LoggerService.get_logger()
        self.db = DatabaseConnection()
        self.cache = CacheService()
        self.is_active = False
        self.last_sync = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Entegrasyona bağlan"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Entegrasyon bağlantısını kes"""
        pass
    
    @abstractmethod
    async def sync_products(self, products: List[Dict]) -> Dict[str, Any]:
        """Ürünleri senkronize et"""
        pass
    
    @abstractmethod
    async def sync_orders(self) -> List[Dict]:
        """Siparişleri senkronize et"""
        pass
    
    @abstractmethod
    async def update_stock(self, product_id: str, stock: int) -> bool:
        """Stok güncelle"""
        pass
    
    @abstractmethod
    async def update_price(self, product_id: str, price: float) -> bool:
        """Fiyat güncelle"""
        pass
    
    async def validate_credentials(self) -> bool:
        """Kimlik bilgilerini doğrula"""
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """Entegrasyon durumunu getir"""
        return {
            'is_active': self.is_active,
            'last_sync': self.last_sync,
            'config': {k: v for k, v in self.config.items() if k not in ['api_key', 'secret']}
        }


class IntegrationManager:
    """
    Ana entegrasyon yöneticisi
    Tüm entegrasyonları merkezi olarak yönetir
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(IntegrationManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Integration Manager başlatıcı"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.logger = LoggerService.get_logger()
        self.db = DatabaseConnection()
        self.cache = CacheService()
        
        # Entegrasyon havuzu
        self.integrations = {}
        self.active_integrations = {}
        
        # Thread pool
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Entegrasyon kategorileri
        self.categories = {
            'marketplace': [
                'trendyol', 'hepsiburada', 'n11', 'gittigidiyor', 'amazon_tr',
                'amazon', 'ebay', 'etsy', 'aliexpress', 'walmart'
            ],
            'ecommerce': [
                'shopify', 'woocommerce', 'magento', 'prestashop', 'opencart',
                'bigcommerce', 'wix', 'squarespace'
            ],
            'accounting': [
                'logo', 'mikro', 'netsis', 'parasut', 'quickbooks', 'sage'
            ],
            'shipping': [
                'yurtici', 'aras', 'mng', 'ptt', 'ups', 'dhl', 'fedex'
            ],
            'payment': [
                'iyzico', 'paytr', 'payu', 'stripe', 'paypal', 'square'
            ],
            'social': [
                'facebook', 'instagram', 'twitter', 'tiktok', 'pinterest'
            ],
            'erp': [
                'sap', 'oracle', 'microsoft_dynamics', 'netsuite'
            ],
            'crm': [
                'salesforce', 'hubspot', 'zoho', 'pipedrive'
            ]
        }
        
        # Entegrasyon durumları
        self.statuses = {
            'total': 0,
            'active': 0,
            'inactive': 0,
            'error': 0,
            'syncing': 0
        }
        
        # Başlatma
        self._load_integrations()
        
        self.logger.info("Integration Manager başlatıldı")
    
    def _load_integrations(self):
        """Kayıtlı entegrasyonları yükle"""
        try:
            # Veritabanından entegrasyon ayarlarını yükle
            query = """
            SELECT id, integration_type, integration_name, config, is_active, created_at
            FROM integrations
            WHERE deleted_at IS NULL
            """
            
            integrations = self.db.fetch_all_sync(query)
            
            for integration in integrations:
                integration_id = integration[0]
                integration_type = integration[1]
                integration_name = integration[2]
                config = json.loads(integration[3]) if integration[3] else {}
                is_active = integration[4]
                
                self.integrations[integration_id] = {
                    'id': integration_id,
                    'type': integration_type,
                    'name': integration_name,
                    'config': config,
                    'is_active': is_active,
                    'instance': None
                }
                
                self.statuses['total'] += 1
                if is_active:
                    self.statuses['active'] += 1
                else:
                    self.statuses['inactive'] += 1
            
            self.logger.info(f"{len(self.integrations)} entegrasyon yüklendi")
            
        except Exception as e:
            self.logger.error(f"Entegrasyonlar yüklenirken hata: {e}")
    
    async def add_integration(
        self,
        integration_type: str,
        integration_name: str,
        config: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Yeni entegrasyon ekle
        
        Args:
            integration_type: Entegrasyon tipi (marketplace, ecommerce, vb.)
            integration_name: Entegrasyon adı (trendyol, shopify, vb.)
            config: Entegrasyon konfigürasyonu
            user_id: Ekleyen kullanıcı ID'si
            
        Returns:
            Ekleme sonucu
        """
        try:
            # Entegrasyon tipini kontrol et
            valid_type = False
            for cat_type, names in self.categories.items():
                if integration_type == cat_type and integration_name in names:
                    valid_type = True
                    break
            
            if not valid_type:
                return {
                    'success': False,
                    'error': 'Geçersiz entegrasyon tipi veya adı',
                    'code': 'INVALID_INTEGRATION'
                }
            
            # Aynı entegrasyon var mı kontrol et
            check_query = """
            SELECT id FROM integrations
            WHERE integration_type = %s AND integration_name = %s 
            AND user_id = %s AND deleted_at IS NULL
            """
            
            existing = await self.db.fetch_one(check_query, (integration_type, integration_name, user_id))
            if existing:
                return {
                    'success': False,
                    'error': 'Bu entegrasyon zaten mevcut',
                    'code': 'INTEGRATION_EXISTS'
                }
            
            # Entegrasyonu ekle
            insert_query = """
            INSERT INTO integrations (
                integration_type, integration_name, config, user_id, 
                is_active, created_at
            ) VALUES (%s, %s, %s, %s, %s, NOW())
            """
            
            integration_id = await self.db.execute_insert(
                insert_query,
                (integration_type, integration_name, json.dumps(config), user_id, False)
            )
            
            # Belleğe ekle
            self.integrations[integration_id] = {
                'id': integration_id,
                'type': integration_type,
                'name': integration_name,
                'config': config,
                'is_active': False,
                'instance': None
            }
            
            self.statuses['total'] += 1
            self.statuses['inactive'] += 1
            
            self.logger.info(f"Yeni entegrasyon eklendi: {integration_name} (ID: {integration_id})")
            
            return {
                'success': True,
                'integration_id': integration_id,
                'message': 'Entegrasyon başarıyla eklendi'
            }
            
        except Exception as e:
            self.logger.error(f"Entegrasyon ekleme hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'ADD_ERROR'
            }
    
    async def activate_integration(self, integration_id: int) -> Dict[str, Any]:
        """
        Entegrasyonu aktifleştir
        
        Args:
            integration_id: Entegrasyon ID'si
            
        Returns:
            Aktivasyon sonucu
        """
        try:
            if integration_id not in self.integrations:
                return {
                    'success': False,
                    'error': 'Entegrasyon bulunamadı',
                    'code': 'NOT_FOUND'
                }
            
            integration = self.integrations[integration_id]
            
            # Entegrasyon instance'ı oluştur
            instance = await self._create_integration_instance(
                integration['type'],
                integration['name'],
                integration['config']
            )
            
            if not instance:
                return {
                    'success': False,
                    'error': 'Entegrasyon instance oluşturulamadı',
                    'code': 'INSTANCE_ERROR'
                }
            
            # Bağlantıyı test et
            connected = await instance.connect()
            if not connected:
                return {
                    'success': False,
                    'error': 'Entegrasyona bağlanılamadı',
                    'code': 'CONNECTION_ERROR'
                }
            
            # Aktif olarak işaretle
            update_query = """
            UPDATE integrations 
            SET is_active = TRUE, last_connected_at = NOW()
            WHERE id = %s
            """
            
            await self.db.execute(update_query, (integration_id,))
            
            # Belleği güncelle
            integration['is_active'] = True
            integration['instance'] = instance
            self.active_integrations[integration_id] = instance
            
            self.statuses['active'] += 1
            self.statuses['inactive'] -= 1
            
            self.logger.info(f"Entegrasyon aktifleştirildi: {integration['name']} (ID: {integration_id})")
            
            return {
                'success': True,
                'message': 'Entegrasyon başarıyla aktifleştirildi'
            }
            
        except Exception as e:
            self.logger.error(f"Entegrasyon aktivasyon hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'ACTIVATION_ERROR'
            }
    
    async def deactivate_integration(self, integration_id: int) -> Dict[str, Any]:
        """
        Entegrasyonu deaktif et
        
        Args:
            integration_id: Entegrasyon ID'si
            
        Returns:
            Deaktivasyon sonucu
        """
        try:
            if integration_id not in self.integrations:
                return {
                    'success': False,
                    'error': 'Entegrasyon bulunamadı',
                    'code': 'NOT_FOUND'
                }
            
            integration = self.integrations[integration_id]
            
            # Instance varsa bağlantıyı kes
            if integration_id in self.active_integrations:
                instance = self.active_integrations[integration_id]
                await instance.disconnect()
                del self.active_integrations[integration_id]
            
            # Deaktif olarak işaretle
            update_query = """
            UPDATE integrations 
            SET is_active = FALSE
            WHERE id = %s
            """
            
            await self.db.execute(update_query, (integration_id,))
            
            # Belleği güncelle
            integration['is_active'] = False
            integration['instance'] = None
            
            self.statuses['active'] -= 1
            self.statuses['inactive'] += 1
            
            self.logger.info(f"Entegrasyon deaktif edildi: {integration['name']} (ID: {integration_id})")
            
            return {
                'success': True,
                'message': 'Entegrasyon başarıyla deaktif edildi'
            }
            
        except Exception as e:
            self.logger.error(f"Entegrasyon deaktivasyon hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'DEACTIVATION_ERROR'
            }
    
    async def sync_all_products(self, user_id: int) -> Dict[str, Any]:
        """
        Tüm aktif entegrasyonlar için ürün senkronizasyonu
        
        Args:
            user_id: Kullanıcı ID'si
            
        Returns:
            Senkronizasyon sonuçları
        """
        try:
            # Kullanıcının ürünlerini al
            products_query = """
            SELECT id, name, description, price, stock, sku, barcode, images
            FROM products
            WHERE user_id = %s AND is_active = TRUE
            """
            
            products = await self.db.fetch_all(products_query, (user_id,))
            
            if not products:
                return {
                    'success': False,
                    'error': 'Senkronize edilecek ürün bulunamadı',
                    'code': 'NO_PRODUCTS'
                }
            
            # Ürünleri dict formatına çevir
            product_list = []
            for product in products:
                product_list.append({
                    'id': product[0],
                    'name': product[1],
                    'description': product[2],
                    'price': float(product[3]),
                    'stock': product[4],
                    'sku': product[5],
                    'barcode': product[6],
                    'images': json.loads(product[7]) if product[7] else []
                })
            
            # Aktif entegrasyonlarda senkronize et
            sync_results = {}
            sync_tasks = []
            
            for integration_id, instance in self.active_integrations.items():
                if self.integrations[integration_id]['type'] in ['marketplace', 'ecommerce']:
                    task = self._sync_products_to_integration(
                        integration_id,
                        instance,
                        product_list
                    )
                    sync_tasks.append(task)
            
            if sync_tasks:
                results = await asyncio.gather(*sync_tasks, return_exceptions=True)
                
                for i, (integration_id, _) in enumerate(self.active_integrations.items()):
                    if i < len(results):
                        sync_results[integration_id] = results[i]
            
            # Sonuçları kaydet
            successful_syncs = sum(1 for r in sync_results.values() if r.get('success', False))
            failed_syncs = len(sync_results) - successful_syncs
            
            await self._save_sync_log(user_id, 'products', sync_results)
            
            return {
                'success': True,
                'total_integrations': len(sync_results),
                'successful_syncs': successful_syncs,
                'failed_syncs': failed_syncs,
                'results': sync_results
            }
            
        except Exception as e:
            self.logger.error(f"Ürün senkronizasyon hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'SYNC_ERROR'
            }
    
    async def sync_all_orders(self, user_id: int) -> Dict[str, Any]:
        """
        Tüm aktif entegrasyonlardan sipariş çek
        
        Args:
            user_id: Kullanıcı ID'si
            
        Returns:
            Sipariş senkronizasyon sonuçları
        """
        try:
            all_orders = []
            sync_results = {}
            sync_tasks = []
            
            # Aktif entegrasyonlardan sipariş çek
            for integration_id, instance in self.active_integrations.items():
                if self.integrations[integration_id]['type'] in ['marketplace', 'ecommerce']:
                    task = self._sync_orders_from_integration(integration_id, instance)
                    sync_tasks.append(task)
            
            if sync_tasks:
                results = await asyncio.gather(*sync_tasks, return_exceptions=True)
                
                for i, (integration_id, _) in enumerate(self.active_integrations.items()):
                    if i < len(results) and not isinstance(results[i], Exception):
                        sync_results[integration_id] = results[i]
                        if results[i].get('success') and results[i].get('orders'):
                            all_orders.extend(results[i]['orders'])
            
            # Siparişleri veritabanına kaydet
            saved_orders = 0
            for order in all_orders:
                saved = await self._save_order(order, user_id)
                if saved:
                    saved_orders += 1
            
            # Sonuçları kaydet
            await self._save_sync_log(user_id, 'orders', sync_results)
            
            return {
                'success': True,
                'total_orders': len(all_orders),
                'saved_orders': saved_orders,
                'sync_results': sync_results
            }
            
        except Exception as e:
            self.logger.error(f"Sipariş senkronizasyon hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'ORDER_SYNC_ERROR'
            }
    
    async def update_stock_all(self, product_id: int, new_stock: int) -> Dict[str, Any]:
        """
        Tüm aktif entegrasyonlarda stok güncelle
        
        Args:
            product_id: Ürün ID'si
            new_stock: Yeni stok miktarı
            
        Returns:
            Güncelleme sonuçları
        """
        try:
            update_results = {}
            update_tasks = []
            
            # Her aktif entegrasyonda güncelle
            for integration_id, instance in self.active_integrations.items():
                if self.integrations[integration_id]['type'] in ['marketplace', 'ecommerce']:
                    # Entegrasyondaki ürün ID'sini bul
                    mapping = await self._get_product_mapping(product_id, integration_id)
                    if mapping:
                        task = instance.update_stock(mapping['external_id'], new_stock)
                        update_tasks.append((integration_id, task))
            
            if update_tasks:
                for integration_id, task in update_tasks:
                    try:
                        result = await task
                        update_results[integration_id] = {
                            'success': result,
                            'integration': self.integrations[integration_id]['name']
                        }
                    except Exception as e:
                        update_results[integration_id] = {
                            'success': False,
                            'error': str(e),
                            'integration': self.integrations[integration_id]['name']
                        }
            
            # Sonuçları logla
            successful_updates = sum(1 for r in update_results.values() if r.get('success', False))
            
            return {
                'success': True,
                'total_integrations': len(update_results),
                'successful_updates': successful_updates,
                'failed_updates': len(update_results) - successful_updates,
                'results': update_results
            }
            
        except Exception as e:
            self.logger.error(f"Stok güncelleme hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'STOCK_UPDATE_ERROR'
            }
    
    async def get_integration_status(self, integration_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Entegrasyon durumunu getir
        
        Args:
            integration_id: Spesifik entegrasyon ID'si (opsiyonel)
            
        Returns:
            Durum bilgileri
        """
        try:
            if integration_id:
                if integration_id not in self.integrations:
                    return {
                        'success': False,
                        'error': 'Entegrasyon bulunamadı',
                        'code': 'NOT_FOUND'
                    }
                
                integration = self.integrations[integration_id]
                status = {
                    'id': integration_id,
                    'type': integration['type'],
                    'name': integration['name'],
                    'is_active': integration['is_active'],
                    'has_instance': integration['instance'] is not None
                }
                
                # Aktif ise detaylı durum al
                if integration_id in self.active_integrations:
                    instance = self.active_integrations[integration_id]
                    detailed_status = await instance.get_status()
                    status.update(detailed_status)
                
                return {
                    'success': True,
                    'status': status
                }
            
            else:
                # Tüm entegrasyonların durumu
                all_statuses = []
                
                for int_id, integration in self.integrations.items():
                    status = {
                        'id': int_id,
                        'type': integration['type'],
                        'name': integration['name'],
                        'is_active': integration['is_active']
                    }
                    all_statuses.append(status)
                
                return {
                    'success': True,
                    'total': self.statuses['total'],
                    'active': self.statuses['active'],
                    'inactive': self.statuses['inactive'],
                    'integrations': all_statuses
                }
                
        except Exception as e:
            self.logger.error(f"Durum alma hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'STATUS_ERROR'
            }
    
    async def _create_integration_instance(
        self,
        integration_type: str,
        integration_name: str,
        config: Dict[str, Any]
    ) -> Optional[IntegrationBase]:
        """Entegrasyon instance'ı oluştur"""
        try:
            # Dinamik import
            if integration_type == 'marketplace':
                from core.Integrations.marketplace_integrations import get_marketplace_integration
                return get_marketplace_integration(integration_name, config)
            
            elif integration_type == 'ecommerce':
                from core.Integrations.ecommerce_integrations import get_ecommerce_integration
                return get_ecommerce_integration(integration_name, config)
            
            elif integration_type == 'accounting':
                from core.Integrations.accounting_integrations import get_accounting_integration
                return get_accounting_integration(integration_name, config)
            
            elif integration_type == 'shipping':
                from core.Integrations.shipping_integrations import get_shipping_integration
                return get_shipping_integration(integration_name, config)
            
            elif integration_type == 'social':
                from core.Integrations.social_media_integrations import get_social_integration
                return get_social_integration(integration_name, config)
            
            else:
                self.logger.warning(f"Bilinmeyen entegrasyon tipi: {integration_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Entegrasyon instance oluşturma hatası: {e}")
            return None
    
    async def _sync_products_to_integration(
        self,
        integration_id: int,
        instance: IntegrationBase,
        products: List[Dict]
    ) -> Dict[str, Any]:
        """Ürünleri entegrasyona senkronize et"""
        try:
            result = await instance.sync_products(products)
            
            # Başarılı senkronizasyonları kaydet
            if result.get('success') and result.get('synced_products'):
                for sync_info in result['synced_products']:
                    await self._save_product_mapping(
                        sync_info['internal_id'],
                        sync_info['external_id'],
                        integration_id
                    )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ürün senkronizasyon hatası (Integration: {integration_id}): {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _sync_orders_from_integration(
        self,
        integration_id: int,
        instance: IntegrationBase
    ) -> Dict[str, Any]:
        """Entegrasyondan sipariş çek"""
        try:
            orders = await instance.sync_orders()
            
            return {
                'success': True,
                'orders': orders,
                'count': len(orders)
            }
            
        except Exception as e:
            self.logger.error(f"Sipariş çekme hatası (Integration: {integration_id}): {e}")
            return {
                'success': False,
                'error': str(e),
                'orders': []
            }
    
    async def _save_product_mapping(
        self,
        internal_id: int,
        external_id: str,
        integration_id: int
    ):
        """Ürün eşleştirmesini kaydet"""
        try:
            query = """
            INSERT INTO product_mappings (
                product_id, external_id, integration_id, created_at
            ) VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                external_id = VALUES(external_id),
                updated_at = NOW()
            """
            
            await self.db.execute(query, (internal_id, external_id, integration_id))
            
        except Exception as e:
            self.logger.error(f"Ürün eşleştirme kayıt hatası: {e}")
    
    async def _get_product_mapping(
        self,
        product_id: int,
        integration_id: int
    ) -> Optional[Dict[str, Any]]:
        """Ürün eşleştirmesini getir"""
        try:
            query = """
            SELECT external_id, created_at, updated_at
            FROM product_mappings
            WHERE product_id = %s AND integration_id = %s
            """
            
            result = await self.db.fetch_one(query, (product_id, integration_id))
            
            if result:
                return {
                    'external_id': result[0],
                    'created_at': result[1],
                    'updated_at': result[2]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ürün eşleştirme getirme hatası: {e}")
            return None
    
    async def _save_order(self, order: Dict[str, Any], user_id: int) -> bool:
        """Siparişi kaydet"""
        try:
            # Sipariş zaten var mı kontrol et
            check_query = """
            SELECT id FROM orders
            WHERE external_order_id = %s AND integration_id = %s
            """
            
            existing = await self.db.fetch_one(
                check_query,
                (order['external_id'], order['integration_id'])
            )
            
            if existing:
                # Güncelle
                update_query = """
                UPDATE orders SET
                    status = %s,
                    total_amount = %s,
                    updated_at = NOW()
                WHERE id = %s
                """
                
                await self.db.execute(
                    update_query,
                    (order['status'], order['total_amount'], existing[0])
                )
            else:
                # Yeni ekle
                insert_query = """
                INSERT INTO orders (
                    user_id, external_order_id, integration_id,
                    customer_name, customer_email, customer_phone,
                    shipping_address, billing_address,
                    total_amount, currency, status,
                    order_date, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """
                
                await self.db.execute_insert(
                    insert_query,
                    (
                        user_id, order['external_id'], order['integration_id'],
                        order.get('customer_name'), order.get('customer_email'),
                        order.get('customer_phone'), json.dumps(order.get('shipping_address', {})),
                        json.dumps(order.get('billing_address', {})),
                        order['total_amount'], order.get('currency', 'TRY'),
                        order['status'], order.get('order_date', datetime.now())
                    )
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Sipariş kaydetme hatası: {e}")
            return False
    
    async def _save_sync_log(
        self,
        user_id: int,
        sync_type: str,
        results: Dict[str, Any]
    ):
        """Senkronizasyon logunu kaydet"""
        try:
            query = """
            INSERT INTO sync_logs (
                user_id, sync_type, sync_results, created_at
            ) VALUES (%s, %s, %s, NOW())
            """
            
            await self.db.execute(
                query,
                (user_id, sync_type, json.dumps(results))
            )
            
        except Exception as e:
            self.logger.error(f"Senkronizasyon logu kaydetme hatası: {e}")


# Singleton instance
integration_manager = IntegrationManager()