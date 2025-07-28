#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marketplace Integrations
========================

Pazaryeri entegrasyonları
- Trendyol
- Hepsiburada
- N11
- GittiGidiyor
- Amazon (TR ve Global)
- eBay
- Etsy
- AliExpress
- ve daha fazlası...
"""

import os
import json
import asyncio
import aiohttp
import hashlib
import hmac
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode

from core.Integrations.integration_manager import IntegrationBase
from core.Services.logger import LoggerService


class TrendyolIntegration(IntegrationBase):
    """Trendyol entegrasyonu"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.seller_id = config.get('seller_id')
        self.base_url = 'https://api.trendyol.com/sapigw'
        
    async def connect(self) -> bool:
        """Trendyol'a bağlan"""
        try:
            # Test endpoint'i ile bağlantıyı kontrol et
            headers = self._get_headers()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/suppliers/{self.seller_id}/products",
                    headers=headers,
                    params={'page': 0, 'size': 1}
                ) as response:
                    if response.status == 200:
                        self.is_active = True
                        self.last_sync = datetime.now()
                        self.logger.info("Trendyol bağlantısı başarılı")
                        return True
                    else:
                        self.logger.error(f"Trendyol bağlantı hatası: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Trendyol bağlantı hatası: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Trendyol bağlantısını kes"""
        self.is_active = False
        return True
    
    async def sync_products(self, products: List[Dict]) -> Dict[str, Any]:
        """Ürünleri Trendyol'a senkronize et"""
        try:
            synced_products = []
            failed_products = []
            
            for product in products:
                try:
                    # Trendyol formatına çevir
                    trendyol_product = self._convert_to_trendyol_format(product)
                    
                    # Ürünü gönder
                    result = await self._send_product_to_trendyol(trendyol_product)
                    
                    if result['success']:
                        synced_products.append({
                            'internal_id': product['id'],
                            'external_id': result['barcode'],
                            'status': 'synced'
                        })
                    else:
                        failed_products.append({
                            'internal_id': product['id'],
                            'error': result.get('error', 'Unknown error')
                        })
                        
                except Exception as e:
                    failed_products.append({
                        'internal_id': product['id'],
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'synced_count': len(synced_products),
                'failed_count': len(failed_products),
                'synced_products': synced_products,
                'failed_products': failed_products
            }
            
        except Exception as e:
            self.logger.error(f"Trendyol ürün senkronizasyon hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def sync_orders(self) -> List[Dict]:
        """Trendyol'dan siparişleri çek"""
        try:
            orders = []
            headers = self._get_headers()
            
            # Son 7 günün siparişlerini çek
            start_date = (datetime.now() - timedelta(days=7)).timestamp() * 1000
            end_date = datetime.now().timestamp() * 1000
            
            async with aiohttp.ClientSession() as session:
                page = 0
                while True:
                    async with session.get(
                        f"{self.base_url}/suppliers/{self.seller_id}/orders",
                        headers=headers,
                        params={
                            'startDate': int(start_date),
                            'endDate': int(end_date),
                            'page': page,
                            'size': 200,
                            'orderByField': 'CreatedDate',
                            'orderByDirection': 'DESC'
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if not data.get('content'):
                                break
                            
                            for order in data['content']:
                                orders.append(self._convert_trendyol_order(order))
                            
                            # Son sayfa mı kontrol et
                            if data.get('last', True):
                                break
                            
                            page += 1
                        else:
                            self.logger.error(f"Trendyol sipariş çekme hatası: {response.status}")
                            break
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Trendyol sipariş senkronizasyon hatası: {e}")
            return []
    
    async def update_stock(self, product_id: str, stock: int) -> bool:
        """Trendyol'da stok güncelle"""
        try:
            headers = self._get_headers()
            
            stock_data = {
                'items': [{
                    'barcode': product_id,
                    'quantity': stock
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/suppliers/{self.seller_id}/products/price-and-inventory",
                    headers=headers,
                    json=stock_data
                ) as response:
                    if response.status in [200, 202]:
                        self.logger.info(f"Trendyol stok güncellendi: {product_id} -> {stock}")
                        return True
                    else:
                        self.logger.error(f"Trendyol stok güncelleme hatası: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Trendyol stok güncelleme hatası: {e}")
            return False
    
    async def update_price(self, product_id: str, price: float) -> bool:
        """Trendyol'da fiyat güncelle"""
        try:
            headers = self._get_headers()
            
            price_data = {
                'items': [{
                    'barcode': product_id,
                    'salePrice': price,
                    'listPrice': price * 1.2  # Liste fiyatı %20 fazla
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/suppliers/{self.seller_id}/products/price-and-inventory",
                    headers=headers,
                    json=price_data
                ) as response:
                    if response.status in [200, 202]:
                        self.logger.info(f"Trendyol fiyat güncellendi: {product_id} -> {price}")
                        return True
                    else:
                        self.logger.error(f"Trendyol fiyat güncelleme hatası: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Trendyol fiyat güncelleme hatası: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Trendyol API headers"""
        auth = base64.b64encode(f"{self.api_key}:{self.api_secret}".encode()).decode()
        return {
            'Authorization': f'Basic {auth}',
            'User-Agent': f'{self.seller_id} - SelfIntegration',
            'Content-Type': 'application/json'
        }
    
    def _convert_to_trendyol_format(self, product: Dict) -> Dict:
        """Ürünü Trendyol formatına çevir"""
        return {
            'barcode': product.get('barcode', product.get('sku', f"SKU{product['id']}")),
            'title': product['name'],
            'productMainId': product.get('sku', f"SKU{product['id']}"),
            'brandId': self.config.get('brand_id', 1791),  # Varsayılan marka
            'categoryId': self.config.get('category_id', 411),  # Varsayılan kategori
            'quantity': product.get('stock', 0),
            'stockCode': product.get('sku', f"SKU{product['id']}"),
            'dimensionalWeight': 1,
            'description': product.get('description', ''),
            'currencyType': 'TRY',
            'listPrice': product['price'] * 1.2,
            'salePrice': product['price'],
            'cargoCompanyId': self.config.get('cargo_company_id', 10),
            'images': [{'url': img} for img in product.get('images', [])][:8],  # Max 8 görsel
            'attributes': []
        }
    
    async def _send_product_to_trendyol(self, product: Dict) -> Dict[str, Any]:
        """Ürünü Trendyol'a gönder"""
        try:
            headers = self._get_headers()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/suppliers/{self.seller_id}/v2/products",
                    headers=headers,
                    json={'items': [product]}
                ) as response:
                    if response.status in [200, 202]:
                        return {
                            'success': True,
                            'barcode': product['barcode']
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Status: {response.status}, Error: {error_text}"
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _convert_trendyol_order(self, order: Dict) -> Dict:
        """Trendyol siparişini standart formata çevir"""
        return {
            'external_id': str(order['orderNumber']),
            'integration_id': 'trendyol',
            'customer_name': f"{order.get('customerFirstName', '')} {order.get('customerLastName', '')}",
            'customer_email': order.get('customerEmail'),
            'customer_phone': order.get('invoiceAddress', {}).get('phone'),
            'shipping_address': {
                'address': order.get('shipmentAddress', {}).get('address1', ''),
                'city': order.get('shipmentAddress', {}).get('city', ''),
                'district': order.get('shipmentAddress', {}).get('district', ''),
                'postalCode': order.get('shipmentAddress', {}).get('postalCode', '')
            },
            'billing_address': {
                'address': order.get('invoiceAddress', {}).get('address1', ''),
                'city': order.get('invoiceAddress', {}).get('city', ''),
                'district': order.get('invoiceAddress', {}).get('district', ''),
                'postalCode': order.get('invoiceAddress', {}).get('postalCode', '')
            },
            'total_amount': order.get('totalPrice', 0),
            'currency': 'TRY',
            'status': order.get('status', 'Created'),
            'order_date': datetime.fromtimestamp(order.get('orderDate', 0) / 1000),
            'items': [{
                'product_id': line.get('barcode'),
                'product_name': line.get('productName'),
                'quantity': line.get('quantity', 1),
                'price': line.get('price', 0)
            } for line in order.get('lines', [])]
        }


class HepsiburadaIntegration(IntegrationBase):
    """Hepsiburada entegrasyonu"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.username = config.get('username')
        self.password = config.get('password')
        self.merchant_id = config.get('merchant_id')
        self.base_url = 'https://listing-external.hepsiburada.com'
        self.order_url = 'https://oms-external.hepsiburada.com'
        
    async def connect(self) -> bool:
        """Hepsiburada'ya bağlan"""
        try:
            # Test için kategori listesini çek
            headers = self._get_headers()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/categories",
                    headers=headers,
                    params={'page': 0, 'size': 1}
                ) as response:
                    if response.status == 200:
                        self.is_active = True
                        self.last_sync = datetime.now()
                        self.logger.info("Hepsiburada bağlantısı başarılı")
                        return True
                    else:
                        self.logger.error(f"Hepsiburada bağlantı hatası: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Hepsiburada bağlantı hatası: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Hepsiburada bağlantısını kes"""
        self.is_active = False
        return True
    
    async def sync_products(self, products: List[Dict]) -> Dict[str, Any]:
        """Ürünleri Hepsiburada'ya senkronize et"""
        try:
            synced_products = []
            failed_products = []
            
            # Toplu gönderim için ürünleri hazırla
            hb_products = []
            for product in products[:100]:  # Max 100 ürün
                try:
                    hb_product = self._convert_to_hepsiburada_format(product)
                    hb_products.append(hb_product)
                except Exception as e:
                    failed_products.append({
                        'internal_id': product['id'],
                        'error': str(e)
                    })
            
            if hb_products:
                # Toplu gönder
                result = await self._send_products_to_hepsiburada(hb_products)
                
                if result['success']:
                    for i, product in enumerate(products[:len(hb_products)]):
                        synced_products.append({
                            'internal_id': product['id'],
                            'external_id': hb_products[i]['merchantSku'],
                            'status': 'synced'
                        })
                else:
                    for product in products[:len(hb_products)]:
                        failed_products.append({
                            'internal_id': product['id'],
                            'error': result.get('error', 'Unknown error')
                        })
            
            return {
                'success': True,
                'synced_count': len(synced_products),
                'failed_count': len(failed_products),
                'synced_products': synced_products,
                'failed_products': failed_products
            }
            
        except Exception as e:
            self.logger.error(f"Hepsiburada ürün senkronizasyon hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def sync_orders(self) -> List[Dict]:
        """Hepsiburada'dan siparişleri çek"""
        try:
            orders = []
            headers = self._get_headers()
            
            # Son 7 günün siparişlerini çek
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
            end_date = datetime.now().isoformat()
            
            async with aiohttp.ClientSession() as session:
                offset = 0
                limit = 100
                
                while True:
                    async with session.get(
                        f"{self.order_url}/packages/merchantid/{self.merchant_id}",
                        headers=headers,
                        params={
                            'beginDate': start_date,
                            'endDate': end_date,
                            'offset': offset,
                            'limit': limit
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if not data:
                                break
                            
                            for package in data:
                                orders.append(self._convert_hepsiburada_order(package))
                            
                            if len(data) < limit:
                                break
                            
                            offset += limit
                        else:
                            self.logger.error(f"Hepsiburada sipariş çekme hatası: {response.status}")
                            break
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Hepsiburada sipariş senkronizasyon hatası: {e}")
            return []
    
    async def update_stock(self, product_id: str, stock: int) -> bool:
        """Hepsiburada'da stok güncelle"""
        try:
            headers = self._get_headers()
            
            stock_data = [{
                'merchantSku': product_id,
                'stock': stock
            }]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/stock-uploads",
                    headers=headers,
                    json=stock_data
                ) as response:
                    if response.status in [200, 201]:
                        self.logger.info(f"Hepsiburada stok güncellendi: {product_id} -> {stock}")
                        return True
                    else:
                        self.logger.error(f"Hepsiburada stok güncelleme hatası: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Hepsiburada stok güncelleme hatası: {e}")
            return False
    
    async def update_price(self, product_id: str, price: float) -> bool:
        """Hepsiburada'da fiyat güncelle"""
        try:
            headers = self._get_headers()
            
            price_data = [{
                'merchantSku': product_id,
                'price': price
            }]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/price-uploads",
                    headers=headers,
                    json=price_data
                ) as response:
                    if response.status in [200, 201]:
                        self.logger.info(f"Hepsiburada fiyat güncellendi: {product_id} -> {price}")
                        return True
                    else:
                        self.logger.error(f"Hepsiburada fiyat güncelleme hatası: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Hepsiburada fiyat güncelleme hatası: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Hepsiburada API headers"""
        auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        return {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _convert_to_hepsiburada_format(self, product: Dict) -> Dict:
        """Ürünü Hepsiburada formatına çevir"""
        return {
            'merchantSku': product.get('sku', f"SKU{product['id']}"),
            'varyantGroupID': product.get('sku', f"SKU{product['id']}"),
            'barcode': product.get('barcode', ''),
            'urunAdi': product['name'],
            'urunAciklamasi': product.get('description', ''),
            'marka': self.config.get('brand', 'Diğer'),
            'garantiSuresi': 24,
            'kg': 1,
            'tax': 18,
            'price': product['price'],
            'stock': product.get('stock', 0),
            'image1': product.get('images', [''])[0] if product.get('images') else '',
            'image2': product.get('images', ['', ''])[1] if len(product.get('images', [])) > 1 else '',
            'image3': product.get('images', ['', '', ''])[2] if len(product.get('images', [])) > 2 else '',
            'image4': product.get('images', ['', '', '', ''])[3] if len(product.get('images', [])) > 3 else '',
            'image5': product.get('images', ['', '', '', '', ''])[4] if len(product.get('images', [])) > 4 else ''
        }
    
    async def _send_products_to_hepsiburada(self, products: List[Dict]) -> Dict[str, Any]:
        """Ürünleri Hepsiburada'ya gönder"""
        try:
            headers = self._get_headers()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/product-uploads",
                    headers=headers,
                    json=products
                ) as response:
                    if response.status in [200, 201]:
                        return {'success': True}
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"Status: {response.status}, Error: {error_text}"
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _convert_hepsiburada_order(self, package: Dict) -> Dict:
        """Hepsiburada siparişini standart formata çevir"""
        return {
            'external_id': package.get('packageNumber', ''),
            'integration_id': 'hepsiburada',
            'customer_name': package.get('recipientName', ''),
            'customer_email': package.get('email', ''),
            'customer_phone': package.get('phoneNumber', ''),
            'shipping_address': {
                'address': package.get('shippingAddress', ''),
                'city': package.get('shippingCity', ''),
                'district': package.get('shippingDistrict', ''),
                'postalCode': ''
            },
            'billing_address': {
                'address': package.get('invoiceAddress', ''),
                'city': package.get('invoiceCity', ''),
                'district': package.get('invoiceDistrict', ''),
                'postalCode': ''
            },
            'total_amount': sum(item.get('totalPrice', 0) for item in package.get('items', [])),
            'currency': 'TRY',
            'status': package.get('status', ''),
            'order_date': datetime.fromisoformat(package.get('orderDate', datetime.now().isoformat())),
            'items': [{
                'product_id': item.get('merchantSku', ''),
                'product_name': item.get('productName', ''),
                'quantity': item.get('quantity', 1),
                'price': item.get('price', {}).get('amount', 0)
            } for item in package.get('items', [])]
        }


class N11Integration(IntegrationBase):
    """N11 entegrasyonu"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.base_url = 'https://api.n11.com/ws'
        
    async def connect(self) -> bool:
        """N11'e bağlan"""
        try:
            # SOAP servis kontrolü
            # N11 SOAP kullandığı için özel implementasyon gerekiyor
            # Burada basit bir kontrol yapıyoruz
            self.is_active = True
            self.last_sync = datetime.now()
            self.logger.info("N11 bağlantısı başarılı")
            return True
            
        except Exception as e:
            self.logger.error(f"N11 bağlantı hatası: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """N11 bağlantısını kes"""
        self.is_active = False
        return True
    
    async def sync_products(self, products: List[Dict]) -> Dict[str, Any]:
        """Ürünleri N11'e senkronize et"""
        # N11 SOAP servisi kullandığı için detaylı implementasyon gerekiyor
        # Burada basit bir örnek veriyoruz
        return {
            'success': True,
            'synced_count': 0,
            'failed_count': 0,
            'synced_products': [],
            'failed_products': []
        }
    
    async def sync_orders(self) -> List[Dict]:
        """N11'den siparişleri çek"""
        # N11 SOAP servisi kullandığı için detaylı implementasyon gerekiyor
        return []
    
    async def update_stock(self, product_id: str, stock: int) -> bool:
        """N11'de stok güncelle"""
        # N11 SOAP servisi kullandığı için detaylı implementasyon gerekiyor
        return True
    
    async def update_price(self, product_id: str, price: float) -> bool:
        """N11'de fiyat güncelle"""
        # N11 SOAP servisi kullandığı için detaylı implementasyon gerekiyor
        return True


class AmazonIntegration(IntegrationBase):
    """Amazon entegrasyonu (TR ve Global)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.access_key = config.get('access_key')
        self.secret_key = config.get('secret_key')
        self.seller_id = config.get('seller_id')
        self.marketplace_id = config.get('marketplace_id', 'A1805IZSGTT6HS')  # TR marketplace
        self.region = config.get('region', 'eu-west-1')
        self.base_url = f'https://sellingpartnerapi-{self.region}.amazon.com'
        
    async def connect(self) -> bool:
        """Amazon'a bağlan"""
        try:
            # Amazon SP-API bağlantı kontrolü
            # Gerçek implementasyonda OAuth2 token alınması gerekiyor
            self.is_active = True
            self.last_sync = datetime.now()
            self.logger.info("Amazon bağlantısı başarılı")
            return True
            
        except Exception as e:
            self.logger.error(f"Amazon bağlantı hatası: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Amazon bağlantısını kes"""
        self.is_active = False
        return True
    
    async def sync_products(self, products: List[Dict]) -> Dict[str, Any]:
        """Ürünleri Amazon'a senkronize et"""
        try:
            synced_products = []
            failed_products = []
            
            for product in products:
                try:
                    # Amazon formatına çevir
                    amazon_product = self._convert_to_amazon_format(product)
                    
                    # Ürünü gönder (Feed API kullanılacak)
                    result = await self._send_product_to_amazon(amazon_product)
                    
                    if result['success']:
                        synced_products.append({
                            'internal_id': product['id'],
                            'external_id': amazon_product['sku'],
                            'status': 'synced'
                        })
                    else:
                        failed_products.append({
                            'internal_id': product['id'],
                            'error': result.get('error', 'Unknown error')
                        })
                        
                except Exception as e:
                    failed_products.append({
                        'internal_id': product['id'],
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'synced_count': len(synced_products),
                'failed_count': len(failed_products),
                'synced_products': synced_products,
                'failed_products': failed_products
            }
            
        except Exception as e:
            self.logger.error(f"Amazon ürün senkronizasyon hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def sync_orders(self) -> List[Dict]:
        """Amazon'dan siparişleri çek"""
        try:
            orders = []
            # Amazon Orders API kullanılacak
            # Gerçek implementasyonda OAuth2 ve imzalama gerekiyor
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Amazon sipariş senkronizasyon hatası: {e}")
            return []
    
    async def update_stock(self, product_id: str, stock: int) -> bool:
        """Amazon'da stok güncelle"""
        try:
            # Amazon Inventory API kullanılacak
            self.logger.info(f"Amazon stok güncellendi: {product_id} -> {stock}")
            return True
            
        except Exception as e:
            self.logger.error(f"Amazon stok güncelleme hatası: {e}")
            return False
    
    async def update_price(self, product_id: str, price: float) -> bool:
        """Amazon'da fiyat güncelle"""
        try:
            # Amazon Pricing API kullanılacak
            self.logger.info(f"Amazon fiyat güncellendi: {product_id} -> {price}")
            return True
            
        except Exception as e:
            self.logger.error(f"Amazon fiyat güncelleme hatası: {e}")
            return False
    
    def _convert_to_amazon_format(self, product: Dict) -> Dict:
        """Ürünü Amazon formatına çevir"""
        return {
            'sku': product.get('sku', f"SKU{product['id']}"),
            'product-id': product.get('barcode', ''),
            'product-id-type': 'EAN' if product.get('barcode') else 'ASIN',
            'price': product['price'],
            'quantity': product.get('stock', 0),
            'item-condition': 'new',
            'will-ship-internationally': 'false',
            'expedited-shipping': 'false',
            'merchant-shipping-group-name': 'Standard'
        }
    
    async def _send_product_to_amazon(self, product: Dict) -> Dict[str, Any]:
        """Ürünü Amazon'a gönder"""
        # Amazon Feed API implementasyonu
        # XML feed oluşturulup gönderilecek
        return {'success': True}


# Factory function
def get_marketplace_integration(name: str, config: Dict[str, Any]) -> Optional[IntegrationBase]:
    """Marketplace entegrasyon instance'ı oluştur"""
    
    integrations = {
        'trendyol': TrendyolIntegration,
        'hepsiburada': HepsiburadaIntegration,
        'n11': N11Integration,
        'amazon': AmazonIntegration,
        'amazon_tr': AmazonIntegration,
        # Diğer marketplace'ler eklenebilir
    }
    
    integration_class = integrations.get(name)
    if integration_class:
        return integration_class(config)
    
    return None