"""
eBay Marketplace API - Gerçek Implementasyon
Bu modül eBay'in resmi Trading ve Inventory API'lerini kullanır.
API Dokümantasyonu: https://developer.ebay.com/
"""

import requests
import json
import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from urllib.parse import urlencode, quote
import xml.etree.ElementTree as ET
from xml.dom import minidom

class eBayMarketplaceAPI:
    """eBay Marketplace API Client"""
    
    def __init__(self, client_id: str, client_secret: str, refresh_token: str = None,
                 dev_id: str = None, cert_id: str = None, token: str = None,
                 sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.dev_id = dev_id  # Trading API için gerekli
        self.cert_id = cert_id  # Trading API için gerekli
        self.token = token  # Trading API için gerekli
        self.sandbox = sandbox
        
        # API Base URLs
        if sandbox:
            self.rest_base_url = "https://api.sandbox.ebay.com"
            self.trading_base_url = "https://api.sandbox.ebay.com/ws/api.dll"
            self.oauth_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
        else:
            self.rest_base_url = "https://api.ebay.com"
            self.trading_base_url = "https://api.ebay.com/ws/api.dll"
            self.oauth_url = "https://api.ebay.com/identity/v1/oauth2/token"
            
        # Site IDs
        self.site_ids = {
            "US": 0,
            "UK": 3,
            "AU": 15,
            "AT": 16,
            "BE_FR": 23,
            "FR": 71,
            "DE": 77,
            "IT": 101,
            "BE_NL": 123,
            "NL": 146,
            "ES": 186,
            "CH": 193,
            "TW": 196,
            "HK": 201,
            "SG": 216,
            "MY": 207,
            "PH": 211,
            "IN": 203,
            "IE": 205,
            "CA": 2
        }
        
        self.session = requests.Session()
        self.access_token = None
        self.token_expires_at = None
        
        self.logger = logging.getLogger(__name__)

    def _get_oauth_token(self) -> str:
        """OAuth 2.0 access token alır"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
            
        try:
            # Base64 encode client credentials
            credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            
            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "scope": "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.marketing.readonly https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory.readonly https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account.readonly https://api.ebay.com/oauth/api_scope/sell.account https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly https://api.ebay.com/oauth/api_scope/sell.fulfillment https://api.ebay.com/oauth/api_scope/sell.analytics.readonly"
            }
            
            response = requests.post(self.oauth_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 7200)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.access_token
            
        except Exception as e:
            self.logger.error(f"OAuth token alınamadı: {e}")
            raise

    def _make_rest_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                          data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """REST API isteği yapar"""
        url = f"{self.rest_base_url}{endpoint}"
        
        # OAuth token al
        access_token = self._get_oauth_token()
        
        request_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "eBayMarketplace-Python-Client/1.0"
        }
        
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=request_headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=request_headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=request_headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=request_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            
            if response.content:
                return response.json()
            else:
                return {"success": True}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"eBay REST API request failed: {e}")
            if hasattr(e, 'response') and e.response:
                self.logger.error(f"Response: {e.response.text}")
            return {"success": False, "error": str(e)}

    def _make_trading_request(self, call_name: str, request_data: Dict, site_id: int = 0) -> Dict:
        """Trading API isteği yapar (XML)"""
        try:
            # XML request oluştur
            root = ET.Element(f"{call_name}Request")
            root.set("xmlns", "urn:ebay:apis:eBLBaseComponents")
            
            # RequesterCredentials ekle
            creds = ET.SubElement(root, "RequesterCredentials")
            ET.SubElement(creds, "eBayAuthToken").text = self.token
            
            # Request data'yı XML'e çevir
            self._dict_to_xml(root, request_data)
            
            xml_request = ET.tostring(root, encoding='unicode')
            
            headers = {
                "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
                "X-EBAY-API-DEV-NAME": self.dev_id,
                "X-EBAY-API-APP-NAME": self.client_id,
                "X-EBAY-API-CERT-NAME": self.cert_id,
                "X-EBAY-API-CALL-NAME": call_name,
                "X-EBAY-API-SITEID": str(site_id),
                "Content-Type": "text/xml"
            }
            
            response = requests.post(self.trading_base_url, data=xml_request, headers=headers)
            response.raise_for_status()
            
            # XML response'u parse et
            root = ET.fromstring(response.content)
            return self._xml_to_dict(root)
            
        except Exception as e:
            self.logger.error(f"eBay Trading API request failed: {e}")
            return {"success": False, "error": str(e)}

    def _dict_to_xml(self, parent: ET.Element, data: Dict):
        """Dictionary'yi XML elementine çevirir"""
        for key, value in data.items():
            if isinstance(value, dict):
                child = ET.SubElement(parent, key)
                self._dict_to_xml(child, value)
            elif isinstance(value, list):
                for item in value:
                    child = ET.SubElement(parent, key)
                    if isinstance(item, dict):
                        self._dict_to_xml(child, item)
                    else:
                        child.text = str(item)
            else:
                child = ET.SubElement(parent, key)
                child.text = str(value)

    def _xml_to_dict(self, element: ET.Element) -> Dict:
        """XML elementini dictionary'ye çevirir"""
        result = {}
        
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        for child in element:
            child_data = self._xml_to_dict(child)
            
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        if element.attrib:
            result['@attributes'] = element.attrib
            
        return result

    # INVENTORY API - REST
    def create_inventory_location(self, merchant_location_key: str, location_data: Dict) -> Dict:
        """Envanter lokasyonu oluşturur"""
        endpoint = f"/sell/inventory/v1/location/{merchant_location_key}"
        return self._make_rest_request('POST', endpoint, data=location_data)

    def get_inventory_locations(self) -> Dict:
        """Envanter lokasyonlarını listeler"""
        endpoint = "/sell/inventory/v1/location"
        return self._make_rest_request('GET', endpoint)

    def create_or_replace_inventory_item(self, sku: str, inventory_item: Dict) -> Dict:
        """Envanter öğesi oluşturur/günceller"""
        endpoint = f"/sell/inventory/v1/inventory_item/{sku}"
        return self._make_rest_request('PUT', endpoint, data=inventory_item)

    def get_inventory_item(self, sku: str) -> Dict:
        """Envanter öğesini getirir"""
        endpoint = f"/sell/inventory/v1/inventory_item/{sku}"
        return self._make_rest_request('GET', endpoint)

    def get_inventory_items(self, limit: int = 25, offset: int = 0) -> Dict:
        """Envanter öğelerini listeler"""
        endpoint = "/sell/inventory/v1/inventory_item"
        params = {"limit": limit, "offset": offset}
        return self._make_rest_request('GET', endpoint, params)

    def delete_inventory_item(self, sku: str) -> Dict:
        """Envanter öğesini siler"""
        endpoint = f"/sell/inventory/v1/inventory_item/{sku}"
        return self._make_rest_request('DELETE', endpoint)

    def create_offer(self, offer_data: Dict) -> Dict:
        """Teklif oluşturur"""
        endpoint = "/sell/inventory/v1/offer"
        return self._make_rest_request('POST', endpoint, data=offer_data)

    def get_offer(self, offer_id: str) -> Dict:
        """Teklif bilgilerini getirir"""
        endpoint = f"/sell/inventory/v1/offer/{offer_id}"
        return self._make_rest_request('GET', endpoint)

    def get_offers(self, sku: str = None, marketplace_id: str = None, 
                   limit: int = 25, offset: int = 0) -> Dict:
        """Teklifleri listeler"""
        endpoint = "/sell/inventory/v1/offer"
        
        params = {"limit": limit, "offset": offset}
        if sku:
            params["sku"] = sku
        if marketplace_id:
            params["marketplace_id"] = marketplace_id
            
        return self._make_rest_request('GET', endpoint, params)

    def update_offer(self, offer_id: str, offer_data: Dict) -> Dict:
        """Teklifi günceller"""
        endpoint = f"/sell/inventory/v1/offer/{offer_id}"
        return self._make_rest_request('PUT', endpoint, data=offer_data)

    def delete_offer(self, offer_id: str) -> Dict:
        """Teklifi siler"""
        endpoint = f"/sell/inventory/v1/offer/{offer_id}"
        return self._make_rest_request('DELETE', endpoint)

    def publish_offer(self, offer_id: str) -> Dict:
        """Teklifi yayınlar (listing oluşturur)"""
        endpoint = f"/sell/inventory/v1/offer/{offer_id}/publish"
        return self._make_rest_request('POST', endpoint)

    def withdraw_offer(self, offer_id: str) -> Dict:
        """Teklifi geri çeker"""
        endpoint = f"/sell/inventory/v1/offer/{offer_id}/withdraw"
        return self._make_rest_request('POST', endpoint)

    def get_listing_fees(self, offer_id: str) -> Dict:
        """Listeleme ücretlerini getirir"""
        endpoint = f"/sell/inventory/v1/offer/{offer_id}/listing_fees"
        return self._make_rest_request('GET', endpoint)

    # FULFILLMENT API - Sipariş Yönetimi
    def get_orders(self, filter: str = None, limit: int = 50, offset: int = 0) -> Dict:
        """Siparişleri getirir"""
        endpoint = "/sell/fulfillment/v1/order"
        
        params = {"limit": limit, "offset": offset}
        if filter:
            params["filter"] = filter
            
        return self._make_rest_request('GET', endpoint, params)

    def get_order(self, order_id: str) -> Dict:
        """Tek sipariş bilgisini getirir"""
        endpoint = f"/sell/fulfillment/v1/order/{order_id}"
        return self._make_rest_request('GET', endpoint)

    def ship_order(self, order_id: str, shipment_data: Dict) -> Dict:
        """Siparişi kargoya verir"""
        endpoint = f"/sell/fulfillment/v1/order/{order_id}/shipping_fulfillment"
        return self._make_rest_request('POST', endpoint, data=shipment_data)

    def get_shipping_fulfillments(self, order_id: str) -> Dict:
        """Kargo takip bilgilerini getirir"""
        endpoint = f"/sell/fulfillment/v1/order/{order_id}/shipping_fulfillment"
        return self._make_rest_request('GET', endpoint)

    # ACCOUNT API - Hesap Yönetimi
    def get_payment_policies(self, marketplace_id: str) -> Dict:
        """Ödeme politikalarını getirir"""
        endpoint = "/sell/account/v1/payment_policy"
        params = {"marketplace_id": marketplace_id}
        return self._make_rest_request('GET', endpoint, params)

    def get_fulfillment_policies(self, marketplace_id: str) -> Dict:
        """Kargo politikalarını getirir"""
        endpoint = "/sell/account/v1/fulfillment_policy"
        params = {"marketplace_id": marketplace_id}
        return self._make_rest_request('GET', endpoint, params)

    def get_return_policies(self, marketplace_id: str) -> Dict:
        """İade politikalarını getirir"""
        endpoint = "/sell/account/v1/return_policy"
        params = {"marketplace_id": marketplace_id}
        return self._make_rest_request('GET', endpoint, params)

    def create_payment_policy(self, policy_data: Dict) -> Dict:
        """Ödeme politikası oluşturur"""
        endpoint = "/sell/account/v1/payment_policy"
        return self._make_rest_request('POST', endpoint, data=policy_data)

    def create_fulfillment_policy(self, policy_data: Dict) -> Dict:
        """Kargo politikası oluşturur"""
        endpoint = "/sell/account/v1/fulfillment_policy"
        return self._make_rest_request('POST', endpoint, data=policy_data)

    def create_return_policy(self, policy_data: Dict) -> Dict:
        """İade politikası oluşturur"""
        endpoint = "/sell/account/v1/return_policy"
        return self._make_rest_request('POST', endpoint, data=policy_data)

    # BROWSE API - Ürün Arama
    def search_items(self, q: str = None, category_ids: str = None, 
                    filter: str = None, limit: int = 50, offset: int = 0) -> Dict:
        """Ürün arar"""
        endpoint = "/buy/browse/v1/item_summary/search"
        
        params = {"limit": limit, "offset": offset}
        if q:
            params["q"] = q
        if category_ids:
            params["category_ids"] = category_ids
        if filter:
            params["filter"] = filter
            
        return self._make_rest_request('GET', endpoint, params)

    def get_item(self, item_id: str) -> Dict:
        """Tek ürün bilgisini getirir"""
        endpoint = f"/buy/browse/v1/item/{item_id}"
        return self._make_rest_request('GET', endpoint)

    def get_items_by_item_group(self, item_group_id: str) -> Dict:
        """Ürün grubundaki ürünleri getirir"""
        endpoint = f"/buy/browse/v1/item/get_items_by_item_group"
        params = {"item_group_id": item_group_id}
        return self._make_rest_request('GET', endpoint, params)

    # TRADING API - XML Tabanlı (Legacy)
    def add_item(self, item_data: Dict, site_id: int = 0) -> Dict:
        """Ürün listeler (Trading API)"""
        return self._make_trading_request('AddItem', {'Item': item_data}, site_id)

    def revise_item(self, item_id: str, item_data: Dict, site_id: int = 0) -> Dict:
        """Ürün günceller (Trading API)"""
        request_data = {
            'Item': {
                'ItemID': item_id,
                **item_data
            }
        }
        return self._make_trading_request('ReviseItem', request_data, site_id)

    def end_item(self, item_id: str, ending_reason: str = "NotAvailable", site_id: int = 0) -> Dict:
        """Ürün listesini sonlandırır (Trading API)"""
        request_data = {
            'ItemID': item_id,
            'EndingReason': ending_reason
        }
        return self._make_trading_request('EndItem', request_data, site_id)

    def get_item(self, item_id: str, site_id: int = 0) -> Dict:
        """Ürün bilgilerini getirir (Trading API)"""
        request_data = {'ItemID': item_id}
        return self._make_trading_request('GetItem', request_data, site_id)

    def get_my_ebay_selling(self, active_list: bool = True, sold_list: bool = False,
                           unsold_list: bool = False, site_id: int = 0) -> Dict:
        """Satış listesini getirir (Trading API)"""
        request_data = {
            'ActiveList': {'Include': active_list},
            'SoldList': {'Include': sold_list},
            'UnsoldList': {'Include': unsold_list}
        }
        return self._make_trading_request('GetMyeBaySelling', request_data, site_id)

    def get_orders(self, order_role: str = "Seller", order_status: str = None,
                   create_time_from: str = None, create_time_to: str = None,
                   site_id: int = 0) -> Dict:
        """Siparişleri getirir (Trading API)"""
        request_data = {'OrderRole': order_role}
        
        if order_status:
            request_data['OrderStatus'] = order_status
        if create_time_from:
            request_data['CreateTimeFrom'] = create_time_from
        if create_time_to:
            request_data['CreateTimeTo'] = create_time_to
            
        return self._make_trading_request('GetOrders', request_data, site_id)

    def complete_sale(self, item_id: str, transaction_id: str = None,
                     tracking_number: str = None, carrier: str = None,
                     site_id: int = 0) -> Dict:
        """Satışı tamamlar (Trading API)"""
        request_data = {
            'ItemID': item_id,
            'Shipped': True
        }
        
        if transaction_id:
            request_data['TransactionID'] = transaction_id
        if tracking_number:
            request_data['Shipment'] = {
                'ShipmentTrackingNumber': tracking_number,
                'ShippingCarrierUsed': carrier or 'Other'
            }
            
        return self._make_trading_request('CompleteSale', request_data, site_id)

    def get_categories(self, category_site_id: int = 0, category_parent: str = None,
                      level_limit: int = 1, site_id: int = 0) -> Dict:
        """Kategorileri getirir (Trading API)"""
        request_data = {
            'CategorySiteID': category_site_id,
            'LevelLimit': level_limit
        }
        
        if category_parent:
            request_data['CategoryParent'] = category_parent
            
        return self._make_trading_request('GetCategories', request_data, site_id)

    def get_category_features(self, category_id: str = None, site_id: int = 0) -> Dict:
        """Kategori özelliklerini getirir (Trading API)"""
        request_data = {}
        if category_id:
            request_data['CategoryID'] = category_id
            
        return self._make_trading_request('GetCategoryFeatures', request_data, site_id)

    # TEST FONKSİYONLARI
    def test_connection(self) -> Dict:
        """API bağlantısını test eder"""
        try:
            # REST API test
            result = self.get_inventory_locations()
            if "locations" in result or result.get("success", True):
                return {
                    "success": True,
                    "message": "eBay API bağlantısı başarılı",
                    "client_id": self.client_id[:8] + "...",
                    "sandbox": self.sandbox,
                    "api_type": "REST"
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
                "message": f"eBay API bağlantı hatası: {str(e)}"
            }

    def get_site_id(self, country_code: str) -> int:
        """Ülke koduna göre site ID döndürür"""
        return self.site_ids.get(country_code.upper(), 0)

    def format_ebay_datetime(self, dt: datetime) -> str:
        """Datetime'ı eBay API formatına çevirir"""
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


# Örnek kullanım ve test fonksiyonları
def test_ebay_api():
    """eBay API'sini test eder"""
    
    # Test credentials (gerçek projede environment variable'lardan alınmalı)
    client_id = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"
    refresh_token = "YOUR_REFRESH_TOKEN"
    
    # Trading API için (opsiyonel)
    dev_id = "YOUR_DEV_ID"
    cert_id = "YOUR_CERT_ID"
    token = "YOUR_AUTH_TOKEN"
    
    # API client oluştur
    ebay = eBayMarketplaceAPI(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        dev_id=dev_id,
        cert_id=cert_id,
        token=token,
        sandbox=True
    )
    
    print("🔄 eBay API Bağlantı Testi...")
    connection_test = ebay.test_connection()
    print(f"Bağlantı: {'✅ Başarılı' if connection_test['success'] else '❌ Başarısız'}")
    
    if connection_test['success']:
        print("\n📍 Envanter Lokasyonları Testi...")
        locations = ebay.get_inventory_locations()
        print(f"Lokasyonlar alındı: {'✅' if 'locations' in locations or locations.get('success', True) else '❌'}")
        
        print("\n📦 Envanter Öğeleri Testi...")
        inventory_items = ebay.get_inventory_items(limit=10)
        print(f"Envanter öğeleri alındı: {'✅' if 'inventoryItems' in inventory_items or inventory_items.get('success', True) else '❌'}")
        
        print("\n💰 Teklifler Testi...")
        offers = ebay.get_offers(limit=10)
        print(f"Teklifler alındı: {'✅' if 'offers' in offers or offers.get('success', True) else '❌'}")
        
        print("\n📋 Sipariş Listesi Testi...")
        orders = ebay.get_orders(limit=10)
        print(f"Siparişler alındı: {'✅' if 'orders' in orders or orders.get('success', True) else '❌'}")
        
        print("\n🔍 Ürün Arama Testi...")
        search_results = ebay.search_items(q="laptop", limit=5)
        print(f"Arama sonuçları alındı: {'✅' if 'itemSummaries' in search_results or search_results.get('success', True) else '❌'}")


if __name__ == "__main__":
    test_ebay_api()