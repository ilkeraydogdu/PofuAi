"""
Hepsiburada Marketplace API - Gerçek Implementasyon
Bu modül Hepsiburada'nın resmi Marketplace API'sini kullanır.
API Dokümantasyonu: https://developers.hepsiburada.com/
"""

import requests
import json
import hashlib
import hmac
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

class HepsiburadaMarketplaceAPI:
    """Hepsiburada Marketplace API Client"""
    
    def __init__(self, username: str, password: str, merchant_id: str, sandbox: bool = True):
        self.username = username
        self.password = password
        self.merchant_id = merchant_id
        self.sandbox = sandbox
        
        # API Base URLs
        if sandbox:
            self.base_url = "https://oms-external-sandbox.hepsiburada.com"
        else:
            self.base_url = "https://oms-external.hepsiburada.com"
            
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HepsiburadaMarketplace-Python-Client/1.0'
        })
        
        self.access_token = None
        self.token_expires_at = None
        
        self.logger = logging.getLogger(__name__)

    def _authenticate(self) -> bool:
        """API kimlik doğrulaması yapar"""
        try:
            auth_url = f"{self.base_url}/user/login"
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            response = self.session.post(auth_url, json=auth_data)
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                self.access_token = result.get("data", {}).get("access_token")
                # Token'ı header'a ekle
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                return True
            else:
                self.logger.error(f"Authentication failed: {result.get('message')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """API isteği yapar"""
        # Token yoksa veya süresi dolmuşsa yeniden authenticate et
        if not self.access_token:
            if not self._authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=data)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Hepsiburada API request failed: {e}")
            # 401 hatası alırsa yeniden authenticate et
            if hasattr(e, 'response') and e.response.status_code == 401:
                self.access_token = None
                return self._make_request(method, endpoint, data)
            return {"success": False, "error": str(e)}

    # ÜRÜN YÖNETİMİ
    def create_product(self, product_data: Dict) -> Dict:
        """Yeni ürün oluşturur"""
        endpoint = f"/products/api/products/{self.merchant_id}"
        
        # Hepsiburada ürün formatına çevir
        hb_product = {
            "merchantId": self.merchant_id,
            "sku": product_data.get("sku"),
            "VaryantGroupID": product_data.get("variant_group_id"),
            "Barcode": product_data.get("barcode"),
            "Title": product_data.get("title"),
            "ProductDescription": product_data.get("description"),
            "BrandName": product_data.get("brand_name"),
            "CategoryName": product_data.get("category_name"),
            "Price": product_data.get("price"),
            "AvailableStock": product_data.get("stock", 0),
            "DispatchTime": product_data.get("dispatch_time", 1),
            "CargoCompany1": product_data.get("cargo_company", "Yurtiçi Kargo"),
            "ShippingAddressLabel": product_data.get("shipping_address_label", "varsayılan"),
            "ClaimAddressLabel": product_data.get("claim_address_label", "varsayılan"),
            "Images": product_data.get("images", []),
            "Attributes": product_data.get("attributes", [])
        }
        
        return self._make_request('POST', endpoint, hb_product)

    def update_product(self, sku: str, product_data: Dict) -> Dict:
        """Ürün bilgilerini günceller"""
        endpoint = f"/products/api/products/{self.merchant_id}/{sku}"
        return self._make_request('PUT', endpoint, product_data)

    def get_products(self, page: int = 0, size: int = 50, sku: str = None) -> Dict:
        """Ürün listesini getirir"""
        endpoint = f"/products/api/products/{self.merchant_id}"
        
        params = {
            "offset": page * size,
            "limit": size
        }
        
        if sku:
            params["sku"] = sku
            
        return self._make_request('GET', endpoint, params)

    def get_product(self, sku: str) -> Dict:
        """Tek ürün bilgisini getirir"""
        endpoint = f"/products/api/products/{self.merchant_id}/{sku}"
        return self._make_request('GET', endpoint)

    def update_stock_price(self, updates: List[Dict]) -> Dict:
        """Stok ve fiyat günceller"""
        endpoint = f"/products/api/inventory/{self.merchant_id}"
        
        inventory_updates = []
        for update in updates:
            inventory_updates.append({
                "sku": update.get("sku"),
                "price": update.get("price"),
                "availableStock": update.get("stock")
            })
        
        data = {"items": inventory_updates}
        return self._make_request('PUT', endpoint, data)

    def delete_product(self, sku: str) -> Dict:
        """Ürün siler"""
        endpoint = f"/products/api/products/{self.merchant_id}/{sku}"
        return self._make_request('DELETE', endpoint)

    # SİPARİŞ YÖNETİMİ
    def get_orders(self, start_date: str = None, end_date: str = None, 
                   status: str = None, page: int = 0, size: int = 50) -> Dict:
        """Sipariş listesini getirir"""
        endpoint = f"/orders/api/orders/{self.merchant_id}"
        
        params = {
            "offset": page * size,
            "limit": size
        }
        
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if status:
            params["status"] = status
            
        return self._make_request('GET', endpoint, params)

    def get_order(self, order_number: str) -> Dict:
        """Tek sipariş bilgisini getirir"""
        endpoint = f"/orders/api/orders/{self.merchant_id}/{order_number}"
        return self._make_request('GET', endpoint)

    def accept_order(self, order_number: str) -> Dict:
        """Siparişi onayla"""
        endpoint = f"/orders/api/orders/{self.merchant_id}/{order_number}/accept"
        return self._make_request('POST', endpoint)

    def reject_order(self, order_number: str, reject_reason: str) -> Dict:
        """Siparişi reddet"""
        endpoint = f"/orders/api/orders/{self.merchant_id}/{order_number}/reject"
        data = {"rejectReason": reject_reason}
        return self._make_request('POST', endpoint, data)

    def ship_order(self, order_number: str, tracking_number: str, 
                   cargo_company: str) -> Dict:
        """Siparişi kargoya ver"""
        endpoint = f"/orders/api/orders/{self.merchant_id}/{order_number}/ship"
        
        data = {
            "trackingNumber": tracking_number,
            "cargoCompany": cargo_company
        }
        
        return self._make_request('POST', endpoint, data)

    def deliver_order(self, order_number: str) -> Dict:
        """Siparişi teslim edildi olarak işaretle"""
        endpoint = f"/orders/api/orders/{self.merchant_id}/{order_number}/deliver"
        return self._make_request('POST', endpoint)

    # KARGO YÖNETİMİ
    def get_cargo_companies(self) -> Dict:
        """Kargo firmalarını listeler"""
        endpoint = "/orders/api/cargo-companies"
        return self._make_request('GET', endpoint)

    def get_shipping_addresses(self) -> Dict:
        """Kargo adreslerini listeler"""
        endpoint = f"/products/api/addresses/{self.merchant_id}/shipping"
        return self._make_request('GET', endpoint)

    def get_claim_addresses(self) -> Dict:
        """İade adreslerini listeler"""
        endpoint = f"/products/api/addresses/{self.merchant_id}/claim"
        return self._make_request('GET', endpoint)

    # KATEGORİ VE MARKA
    def get_categories(self) -> Dict:
        """Kategori listesini getirir"""
        endpoint = "/products/api/categories"
        return self._make_request('GET', endpoint)

    def get_category_attributes(self, category_id: str) -> Dict:
        """Kategori özelliklerini getirir"""
        endpoint = f"/products/api/categories/{category_id}/attributes"
        return self._make_request('GET', endpoint)

    def get_brands(self) -> Dict:
        """Marka listesini getirir"""
        endpoint = "/products/api/brands"
        return self._make_request('GET', endpoint)

    def search_brand(self, brand_name: str) -> Dict:
        """Marka arar"""
        endpoint = "/products/api/brands/search"
        params = {"name": brand_name}
        return self._make_request('GET', endpoint, params)

    # RAPORLAMA
    def get_sales_report(self, start_date: str, end_date: str) -> Dict:
        """Satış raporu getirir"""
        endpoint = f"/reports/api/sales/{self.merchant_id}"
        params = {
            "startDate": start_date,
            "endDate": end_date
        }
        return self._make_request('GET', endpoint, params)

    def get_inventory_report(self) -> Dict:
        """Stok raporu getirir"""
        endpoint = f"/reports/api/inventory/{self.merchant_id}"
        return self._make_request('GET', endpoint)

    def get_return_report(self, start_date: str, end_date: str) -> Dict:
        """İade raporu getirir"""
        endpoint = f"/reports/api/returns/{self.merchant_id}"
        params = {
            "startDate": start_date,
            "endDate": end_date
        }
        return self._make_request('GET', endpoint, params)

    # İADE YÖNETİMİ
    def get_returns(self, start_date: str = None, end_date: str = None,
                    page: int = 0, size: int = 50) -> Dict:
        """İade listesini getirir"""
        endpoint = f"/returns/api/returns/{self.merchant_id}"
        
        params = {
            "offset": page * size,
            "limit": size
        }
        
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
            
        return self._make_request('GET', endpoint, params)

    def accept_return(self, return_id: str) -> Dict:
        """İadeyi kabul et"""
        endpoint = f"/returns/api/returns/{self.merchant_id}/{return_id}/accept"
        return self._make_request('POST', endpoint)

    def reject_return(self, return_id: str, reject_reason: str) -> Dict:
        """İadeyi reddet"""
        endpoint = f"/returns/api/returns/{self.merchant_id}/{return_id}/reject"
        data = {"rejectReason": reject_reason}
        return self._make_request('POST', endpoint, data)

    # ENTEGRASYON YÖNETİMİ
    def get_integration_status(self) -> Dict:
        """Entegrasyon durumunu getirir"""
        endpoint = f"/integration/api/status/{self.merchant_id}"
        return self._make_request('GET', endpoint)

    def update_integration_settings(self, settings: Dict) -> Dict:
        """Entegrasyon ayarlarını günceller"""
        endpoint = f"/integration/api/settings/{self.merchant_id}"
        return self._make_request('PUT', endpoint, settings)

    # WEBHOOK YÖNETİMİ
    def register_webhook(self, webhook_url: str, events: List[str]) -> Dict:
        """Webhook kaydeder"""
        endpoint = f"/webhooks/api/webhooks/{self.merchant_id}"
        data = {
            "url": webhook_url,
            "events": events
        }
        return self._make_request('POST', endpoint, data)

    def get_webhooks(self) -> Dict:
        """Webhook listesini getirir"""
        endpoint = f"/webhooks/api/webhooks/{self.merchant_id}"
        return self._make_request('GET', endpoint)

    def delete_webhook(self, webhook_id: str) -> Dict:
        """Webhook siler"""
        endpoint = f"/webhooks/api/webhooks/{self.merchant_id}/{webhook_id}"
        return self._make_request('DELETE', endpoint)

    # TEST FONKSİYONLARI
    def test_connection(self) -> Dict:
        """API bağlantısını test eder"""
        try:
            # Kategorileri getirerek test et
            result = self.get_categories()
            if result.get("success", True) and "data" in result:
                return {
                    "success": True,
                    "message": "Hepsiburada API bağlantısı başarılı",
                    "username": self.username,
                    "merchant_id": self.merchant_id,
                    "sandbox": self.sandbox,
                    "token_status": "active" if self.access_token else "inactive"
                }
            else:
                return {
                    "success": False,
                    "message": "API yanıtı beklenmedik format",
                    "response": result
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Hepsiburada API bağlantı hatası: {str(e)}"
            }

    def get_merchant_info(self) -> Dict:
        """Satıcı bilgilerini getirir"""
        endpoint = f"/merchants/api/merchants/{self.merchant_id}"
        return self._make_request('GET', endpoint)

    # BULK İŞLEMLER
    def bulk_update_products(self, products: List[Dict]) -> Dict:
        """Toplu ürün güncelleme"""
        endpoint = f"/products/api/products/{self.merchant_id}/bulk"
        data = {"products": products}
        return self._make_request('PUT', endpoint, data)

    def bulk_update_inventory(self, inventory_updates: List[Dict]) -> Dict:
        """Toplu stok güncelleme"""
        endpoint = f"/products/api/inventory/{self.merchant_id}/bulk"
        data = {"items": inventory_updates}
        return self._make_request('PUT', endpoint, data)

    # PERFORMANS RAPORLARI
    def get_performance_metrics(self, start_date: str, end_date: str) -> Dict:
        """Performans metriklerini getirir"""
        endpoint = f"/analytics/api/performance/{self.merchant_id}"
        params = {
            "startDate": start_date,
            "endDate": end_date
        }
        return self._make_request('GET', endpoint, params)

    def get_listing_quality_score(self) -> Dict:
        """Listeleme kalite skorunu getirir"""
        endpoint = f"/analytics/api/listing-quality/{self.merchant_id}"
        return self._make_request('GET', endpoint)


# Örnek kullanım ve test fonksiyonları
def test_hepsiburada_api():
    """Hepsiburada API'sini test eder"""
    
    # Test credentials (gerçek projede environment variable'lardan alınmalı)
    username = "YOUR_USERNAME"
    password = "YOUR_PASSWORD"
    merchant_id = "YOUR_MERCHANT_ID"
    
    # API client oluştur
    hepsiburada = HepsiburadaMarketplaceAPI(
        username=username,
        password=password,
        merchant_id=merchant_id,
        sandbox=True
    )
    
    print("🔄 Hepsiburada API Bağlantı Testi...")
    connection_test = hepsiburada.test_connection()
    print(f"Bağlantı: {'✅ Başarılı' if connection_test['success'] else '❌ Başarısız'}")
    
    if connection_test['success']:
        print("\n📦 Ürün Listesi Testi...")
        products = hepsiburada.get_products(page=0, size=10)
        print(f"Ürün listesi alındı: {'✅' if products.get('success', True) else '❌'}")
        
        print("\n📋 Kategori Listesi Testi...")
        categories = hepsiburada.get_categories()
        print(f"Kategori listesi alındı: {'✅' if categories.get('success', True) else '❌'}")
        
        print("\n🏷️ Marka Listesi Testi...")
        brands = hepsiburada.get_brands()
        print(f"Marka listesi alındı: {'✅' if brands.get('success', True) else '❌'}")
        
        print("\n📦 Sipariş Listesi Testi...")
        orders = hepsiburada.get_orders(page=0, size=10)
        print(f"Sipariş listesi alındı: {'✅' if orders.get('success', True) else '❌'}")
        
        print("\n🏢 Kargo Firmaları Testi...")
        cargo_companies = hepsiburada.get_cargo_companies()
        print(f"Kargo firmaları alındı: {'✅' if cargo_companies.get('success', True) else '❌'}")


if __name__ == "__main__":
    test_hepsiburada_api()