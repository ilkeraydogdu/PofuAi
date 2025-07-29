"""
Gerçek Entegrasyon Yöneticisi - Marketplace ve Ödeme API'leri
Bu modül gerçek marketplace ve ödeme API'lerini kullanır.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os

# Gerçek API modüllerini import et
from .trendyol_marketplace_api import TrendyolMarketplaceAPI
from .n11_marketplace_api import N11MarketplaceAPI
from .hepsiburada_marketplace_api import HepsiburadaMarketplaceAPI
from .iyzico_payment_api import IyzicoPaymentAPI

# Configuration management
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.marketplace_config import get_marketplace_config, get_marketplace_credentials, validate_marketplace_config

class RealIntegrationManager:
    """Gerçek API'leri kullanan entegrasyon yöneticisi"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # API client'ları
        self.trendyol = None
        self.n11 = None
        self.hepsiburada = None
        self.iyzico = None
        
        # Entegrasyon durumları
        self.integration_status = {
            'trendyol': {'connected': False, 'last_check': None, 'error': None},
            'n11': {'connected': False, 'last_check': None, 'error': None},
            'hepsiburada': {'connected': False, 'last_check': None, 'error': None},
            'iyzico': {'connected': False, 'last_check': None, 'error': None}
        }
        
        self._initialize_apis()

    def _initialize_apis(self):
        """API client'larını başlatır - güvenli config management ile"""
        try:
            # Trendyol API
            try:
                trendyol_config = get_marketplace_config('trendyol')
                if trendyol_config.get('enabled', False):
                    credentials = get_marketplace_credentials('trendyol')
                    self.trendyol = TrendyolMarketplaceAPI(
                        api_key=credentials.api_key,
                        api_secret=credentials.api_secret,
                        supplier_id=credentials.additional_params.get('supplier_id'),
                        sandbox=trendyol_config.get('sandbox', True)
                    )
                    self.logger.info("Trendyol API initialized successfully")
            except Exception as e:
                self.logger.error(f"Trendyol API initialization failed: {e}")
                
            # N11 API
            try:
                n11_config = get_marketplace_config('n11')
                if n11_config.get('enabled', False):
                    credentials = get_marketplace_credentials('n11')
                    self.n11 = N11MarketplaceAPI(
                        api_key=credentials.api_key,
                        api_secret=credentials.api_secret,
                        sandbox=n11_config.get('sandbox', True)
                    )
                    self.logger.info("N11 API initialized successfully")
            except Exception as e:
                self.logger.error(f"N11 API initialization failed: {e}")
                
            # Hepsiburada API
            try:
                hb_config = get_marketplace_config('hepsiburada')
                if hb_config.get('enabled', False):
                    credentials = get_marketplace_credentials('hepsiburada')
                    self.hepsiburada = HepsiburadaMarketplaceAPI(
                        username=credentials.api_key,
                        password=credentials.api_secret,
                        merchant_id=credentials.additional_params.get('merchant_id'),
                        sandbox=hb_config.get('sandbox', True)
                    )
                    self.logger.info("Hepsiburada API initialized successfully")
            except Exception as e:
                self.logger.error(f"Hepsiburada API initialization failed: {e}")
                
            # İyzico API
            try:
                iyzico_config = get_marketplace_config('iyzico')
                if iyzico_config.get('enabled', False):
                    credentials = get_marketplace_credentials('iyzico')
                    self.iyzico = IyzicoPaymentAPI(
                        api_key=credentials.api_key,
                        secret_key=credentials.api_secret,
                        sandbox=iyzico_config.get('sandbox', True)
                    )
                    self.logger.info("İyzico API initialized successfully")
            except Exception as e:
                self.logger.error(f"İyzico API initialization failed: {e}")
                
        except Exception as e:
            self.logger.error(f"General API initialization failed: {e}")

    def test_all_connections(self) -> Dict:
        """Tüm API bağlantılarını test eder"""
        results = {}
        
        # Trendyol test
        if self.trendyol:
            try:
                result = self.trendyol.test_connection()
                self.integration_status['trendyol'] = {
                    'connected': result['success'],
                    'last_check': datetime.now().isoformat(),
                    'error': None if result['success'] else result.get('message')
                }
                results['trendyol'] = result
            except Exception as e:
                self.integration_status['trendyol']['error'] = str(e)
                results['trendyol'] = {'success': False, 'error': str(e)}
        
        # N11 test
        if self.n11:
            try:
                result = self.n11.test_connection()
                self.integration_status['n11'] = {
                    'connected': result['success'],
                    'last_check': datetime.now().isoformat(),
                    'error': None if result['success'] else result.get('message')
                }
                results['n11'] = result
            except Exception as e:
                self.integration_status['n11']['error'] = str(e)
                results['n11'] = {'success': False, 'error': str(e)}
        
        # Hepsiburada test
        if self.hepsiburada:
            try:
                result = self.hepsiburada.test_connection()
                self.integration_status['hepsiburada'] = {
                    'connected': result['success'],
                    'last_check': datetime.now().isoformat(),
                    'error': None if result['success'] else result.get('message')
                }
                results['hepsiburada'] = result
            except Exception as e:
                self.integration_status['hepsiburada']['error'] = str(e)
                results['hepsiburada'] = {'success': False, 'error': str(e)}
        
        # İyzico test
        if self.iyzico:
            try:
                result = self.iyzico.test_connection()
                self.integration_status['iyzico'] = {
                    'connected': result['success'],
                    'last_check': datetime.now().isoformat(),
                    'error': None if result['success'] else result.get('message')
                }
                results['iyzico'] = result
            except Exception as e:
                self.integration_status['iyzico']['error'] = str(e)
                results['iyzico'] = {'success': False, 'error': str(e)}
        
        return results

    # ÜRÜN YÖNETİMİ
    def sync_product_to_all_platforms(self, product_data: Dict) -> Dict:
        """Ürünü tüm platformlara senkronize eder"""
        results = {}
        
        # Trendyol'a ürün ekle
        if self.trendyol and self.integration_status['trendyol']['connected']:
            try:
                results['trendyol'] = self.trendyol.create_product(product_data)
            except Exception as e:
                results['trendyol'] = {'success': False, 'error': str(e)}
        
        # N11'e ürün ekle
        if self.n11 and self.integration_status['n11']['connected']:
            try:
                results['n11'] = self.n11.save_product(product_data)
            except Exception as e:
                results['n11'] = {'success': False, 'error': str(e)}
        
        # Hepsiburada'ya ürün ekle
        if self.hepsiburada and self.integration_status['hepsiburada']['connected']:
            try:
                results['hepsiburada'] = self.hepsiburada.create_product(product_data)
            except Exception as e:
                results['hepsiburada'] = {'success': False, 'error': str(e)}
        
        return results

    def sync_stock_to_all_platforms(self, stock_updates: List[Dict]) -> Dict:
        """Stok bilgilerini tüm platformlara senkronize eder"""
        results = {}
        
        # Trendyol stok güncelle
        if self.trendyol and self.integration_status['trendyol']['connected']:
            try:
                results['trendyol'] = self.trendyol.update_stock_price(stock_updates)
            except Exception as e:
                results['trendyol'] = {'success': False, 'error': str(e)}
        
        # N11 stok güncelle
        if self.n11 and self.integration_status['n11']['connected']:
            try:
                for update in stock_updates:
                    result = self.n11.update_stock_by_stock_code(
                        update.get('stockCode', update.get('sku')),
                        update.get('quantity', 0)
                    )
                    results['n11'] = result
            except Exception as e:
                results['n11'] = {'success': False, 'error': str(e)}
        
        # Hepsiburada stok güncelle
        if self.hepsiburada and self.integration_status['hepsiburada']['connected']:
            try:
                results['hepsiburada'] = self.hepsiburada.update_stock_price(stock_updates)
            except Exception as e:
                results['hepsiburada'] = {'success': False, 'error': str(e)}
        
        return results

    # SİPARİŞ YÖNETİMİ
    def get_all_orders(self, start_date: str = None, end_date: str = None) -> Dict:
        """Tüm platformlardan siparişleri getirir"""
        all_orders = {}
        
        # Trendyol siparişleri
        if self.trendyol and self.integration_status['trendyol']['connected']:
            try:
                orders = self.trendyol.get_orders(
                    start_date=start_date,
                    end_date=end_date,
                    page=0,
                    size=100
                )
                all_orders['trendyol'] = orders
            except Exception as e:
                all_orders['trendyol'] = {'success': False, 'error': str(e)}
        
        # N11 siparişleri
        if self.n11 and self.integration_status['n11']['connected']:
            try:
                orders = self.n11.get_order_list(
                    start_date=start_date,
                    end_date=end_date,
                    page_index=0,
                    page_size=100
                )
                all_orders['n11'] = orders
            except Exception as e:
                all_orders['n11'] = {'success': False, 'error': str(e)}
        
        # Hepsiburada siparişleri
        if self.hepsiburada and self.integration_status['hepsiburada']['connected']:
            try:
                orders = self.hepsiburada.get_orders(
                    start_date=start_date,
                    end_date=end_date,
                    page=0,
                    size=100
                )
                all_orders['hepsiburada'] = orders
            except Exception as e:
                all_orders['hepsiburada'] = {'success': False, 'error': str(e)}
        
        return all_orders

    def ship_order_on_platform(self, platform: str, order_id: str, 
                               tracking_number: str, cargo_company: str) -> Dict:
        """Belirtilen platformda siparişi kargoya verir"""
        if platform == 'trendyol' and self.trendyol:
            return self.trendyol.ship_order(order_id, tracking_number, 10)  # 10 = Yurtiçi Kargo ID
        elif platform == 'n11' and self.n11:
            return self.n11.ship_order(order_id, tracking_number, 1)  # 1 = Yurtiçi Kargo ID
        elif platform == 'hepsiburada' and self.hepsiburada:
            return self.hepsiburada.ship_order(order_id, tracking_number, cargo_company)
        else:
            return {'success': False, 'error': f'Platform {platform} not supported or not connected'}

    # ÖDEME İŞLEMLERİ
    def process_payment(self, payment_data: Dict) -> Dict:
        """İyzico ile ödeme işlemi yapar"""
        if not self.iyzico or not self.integration_status['iyzico']['connected']:
            return {'success': False, 'error': 'İyzico not connected'}
        
        try:
            if payment_data.get('use_3ds', False):
                return self.iyzico.create_3ds_payment(payment_data)
            else:
                return self.iyzico.create_payment(payment_data)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def refund_payment(self, payment_transaction_id: str, amount: str, 
                       ip: str, reason: str = None) -> Dict:
        """İyzico ile ödeme iadesi yapar"""
        if not self.iyzico or not self.integration_status['iyzico']['connected']:
            return {'success': False, 'error': 'İyzico not connected'}
        
        try:
            return self.iyzico.refund_payment(payment_transaction_id, amount, ip, 'TRY', reason)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # RAPORLAMA
    def get_integration_report(self) -> Dict:
        """Entegrasyon durumu raporu"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'integrations': self.integration_status,
            'summary': {
                'total_integrations': len(self.integration_status),
                'connected_count': sum(1 for status in self.integration_status.values() if status['connected']),
                'failed_count': sum(1 for status in self.integration_status.values() if not status['connected'])
            }
        }
        
        return report

    def get_sales_summary(self, start_date: str, end_date: str) -> Dict:
        """Tüm platformlardan satış özeti"""
        sales_data = {}
        
        # Her platformdan sipariş verilerini al
        orders = self.get_all_orders(start_date, end_date)
        
        for platform, order_data in orders.items():
            if order_data.get('success', True):
                # Platform bazında satış özetini hesapla
                sales_data[platform] = {
                    'total_orders': len(order_data.get('content', order_data.get('data', []))),
                    'platform': platform,
                    'status': 'success'
                }
            else:
                sales_data[platform] = {
                    'total_orders': 0,
                    'platform': platform,
                    'status': 'error',
                    'error': order_data.get('error')
                }
        
        return sales_data

    # YARDIMCI FONKSİYONLAR
    def get_platform_categories(self, platform: str) -> Dict:
        """Belirtilen platformun kategorilerini getirir"""
        if platform == 'trendyol' and self.trendyol:
            return self.trendyol.get_categories()
        elif platform == 'n11' and self.n11:
            return self.n11.get_top_level_categories()
        elif platform == 'hepsiburada' and self.hepsiburada:
            return self.hepsiburada.get_categories()
        else:
            return {'success': False, 'error': f'Platform {platform} not supported'}

    def get_platform_brands(self, platform: str) -> Dict:
        """Belirtilen platformun markalarını getirir"""
        if platform == 'trendyol' and self.trendyol:
            return self.trendyol.get_brands()
        elif platform == 'n11' and self.n11:
            return {'success': False, 'error': 'N11 brand listing not available via API'}
        elif platform == 'hepsiburada' and self.hepsiburada:
            return self.hepsiburada.get_brands()
        else:
            return {'success': False, 'error': f'Platform {platform} not supported'}

    def health_check(self) -> Dict:
        """Sistem sağlık kontrolü"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'services': {}
        }
        
        # Her servisin durumunu kontrol et
        connection_results = self.test_all_connections()
        
        for service, result in connection_results.items():
            health_status['services'][service] = {
                'status': 'up' if result.get('success') else 'down',
                'message': result.get('message', 'OK'),
                'last_check': datetime.now().isoformat()
            }
        
        # Genel durum
        failed_services = [s for s, status in health_status['services'].items() 
                          if status['status'] == 'down']
        
        if failed_services:
            health_status['status'] = 'degraded' if len(failed_services) < len(health_status['services']) else 'unhealthy'
            health_status['failed_services'] = failed_services
        
        return health_status


# Test ve örnek kullanım fonksiyonları
def test_real_integrations():
    """Gerçek entegrasyonları test eder"""
    
    # Örnek config (gerçek projede environment variable'lardan alınmalı)
    config = {
        'trendyol': {
            'enabled': True,
            'api_key': 'YOUR_TRENDYOL_API_KEY',
            'api_secret': 'YOUR_TRENDYOL_API_SECRET',
            'supplier_id': 'YOUR_SUPPLIER_ID',
            'sandbox': True
        },
        'n11': {
            'enabled': True,
            'api_key': 'YOUR_N11_API_KEY',
            'api_secret': 'YOUR_N11_API_SECRET',
            'sandbox': True
        },
        'hepsiburada': {
            'enabled': True,
            'username': 'YOUR_HB_USERNAME',
            'password': 'YOUR_HB_PASSWORD',
            'merchant_id': 'YOUR_MERCHANT_ID',
            'sandbox': True
        },
        'iyzico': {
            'enabled': True,
            'api_key': 'YOUR_IYZICO_API_KEY',
            'secret_key': 'YOUR_IYZICO_SECRET_KEY',
            'sandbox': True
        }
    }
    
    # Integration manager oluştur
    manager = RealIntegrationManager(config)
    
    print("🔄 Gerçek Entegrasyon Testleri Başlıyor...")
    print("=" * 50)
    
    # Bağlantı testleri
    print("\n1️⃣ API Bağlantı Testleri:")
    connection_results = manager.test_all_connections()
    
    for platform, result in connection_results.items():
        status = "✅ Başarılı" if result.get('success') else "❌ Başarısız"
        print(f"   {platform}: {status}")
        if not result.get('success'):
            print(f"      Hata: {result.get('message', 'Unknown error')}")
    
    # Sağlık kontrolü
    print("\n2️⃣ Sistem Sağlık Kontrolü:")
    health = manager.health_check()
    print(f"   Genel Durum: {health['status'].upper()}")
    
    for service, status in health['services'].items():
        print(f"   {service}: {status['status'].upper()}")
    
    # Entegrasyon raporu
    print("\n3️⃣ Entegrasyon Durumu Raporu:")
    report = manager.get_integration_report()
    print(f"   Toplam Entegrasyon: {report['summary']['total_integrations']}")
    print(f"   Bağlı: {report['summary']['connected_count']}")
    print(f"   Başarısız: {report['summary']['failed_count']}")
    
    # Platform kategorileri test
    print("\n4️⃣ Platform Kategori Testleri:")
    for platform in ['trendyol', 'n11', 'hepsiburada']:
        if connection_results.get(platform, {}).get('success'):
            try:
                categories = manager.get_platform_categories(platform)
                status = "✅" if categories.get('success', True) else "❌"
                print(f"   {platform} kategorileri: {status}")
            except Exception as e:
                print(f"   {platform} kategorileri: ❌ ({str(e)})")
    
    print("\n✅ Gerçek entegrasyon testleri tamamlandı!")
    print("🎯 Marketplace ve ödeme API'leri hazır!")


if __name__ == "__main__":
    # Logging ayarla
    logging.basicConfig(level=logging.INFO)
    
    # Testleri çalıştır
    test_real_integrations()