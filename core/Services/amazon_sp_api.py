"""
Amazon Selling Partner API - Gerçek Implementasyon
Bu modül Amazon'un resmi Selling Partner API'sini kullanır.
API Dokümantasyonu: https://developer-docs.amazon.com/sp-api/
"""

import requests
import json
import hashlib
import hmac
import base64
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from urllib.parse import urlencode, quote
import uuid

class AmazonSPAPI:
    """Amazon Selling Partner API Client"""
    
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, 
                 region: str = "NA", sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.region = region
        self.sandbox = sandbox
        
        # API Base URLs
        self.region_endpoints = {
            "NA": "https://sellingpartnerapi-na.amazon.com" if not sandbox else "https://sandbox.sellingpartnerapi-na.amazon.com",
            "EU": "https://sellingpartnerapi-eu.amazon.com" if not sandbox else "https://sandbox.sellingpartnerapi-eu.amazon.com", 
            "FE": "https://sellingpartnerapi-fe.amazon.com" if not sandbox else "https://sandbox.sellingpartnerapi-fe.amazon.com"
        }
        
        self.base_url = self.region_endpoints.get(region, self.region_endpoints["NA"])
        
        # Marketplace IDs
        self.marketplace_ids = {
            "US": "ATVPDKIKX0DER",
            "CA": "A2EUQ1WTGCTBG2", 
            "MX": "A1AM78C64UM0Y8",
            "UK": "A1F83G8C2ARO7P",
            "DE": "A1PA6795UKMFR9",
            "FR": "A13V1IB3VIYZZH",
            "IT": "APJ6JRA9NG5V4",
            "ES": "A1RKKUPIHCS9HS",
            "TR": "A33AVAJ2PDY3EV",  # Amazon Türkiye
            "JP": "A1VC38T7YXB528",
            "AU": "A39IBJ37TRP1C6",
            "IN": "A21TJRUUN4KGV",
            "SG": "A19VAU5U5O7RUS"
        }
        
        self.session = requests.Session()
        self.access_token = None
        self.token_expires_at = None
        
        self.logger = logging.getLogger(__name__)

    def _get_access_token(self) -> str:
        """LWA access token alır"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
            
        try:
            token_url = "https://api.amazon.com/auth/o2/token"
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.access_token
            
        except Exception as e:
            self.logger.error(f"Token alınamadı: {e}")
            raise

    def _sign_request(self, method: str, uri: str, query_string: str = "", payload: str = "") -> Dict[str, str]:
        """AWS Signature Version 4 ile istek imzalar"""
        # Bu örnekte basitleştirilmiş imzalama kullanıyoruz
        # Gerçek implementasyonda AWS SDK kullanılmalı
        access_token = self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "AmazonSP-Python-Client/1.0",
            "x-amz-access-token": access_token
        }
        
        return headers

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict:
        """API isteği yapar"""
        url = f"{self.base_url}{endpoint}"
        
        query_string = ""
        if params:
            query_string = urlencode(params)
            
        payload = ""
        if data:
            payload = json.dumps(data)
            
        headers = self._sign_request(method, endpoint, query_string, payload)
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Amazon SP-API request failed: {e}")
            if hasattr(e, 'response') and e.response:
                self.logger.error(f"Response: {e.response.text}")
            return {"success": False, "error": str(e)}

    # SELLER YÖNETİMİ
    def get_marketplace_participations(self) -> Dict:
        """Satıcının katıldığı pazaryerlerini getirir"""
        endpoint = "/sellers/v1/marketplaceParticipations"
        return self._make_request('GET', endpoint)

    def get_seller_account_info(self) -> Dict:
        """Satıcı hesap bilgilerini getirir"""
        endpoint = "/sellers/v1/account"
        return self._make_request('GET', endpoint)

    # ÜRÜN YÖNETİMİ - Catalog Items API
    def search_catalog_items(self, keywords: str, marketplace_id: str, 
                           page_size: int = 10, page_token: str = None) -> Dict:
        """Katalog ürünlerini arar"""
        endpoint = "/catalog/2022-04-01/items"
        
        params = {
            "keywords": keywords,
            "marketplaceIds": marketplace_id,
            "pageSize": page_size
        }
        
        if page_token:
            params["pageToken"] = page_token
            
        return self._make_request('GET', endpoint, params)

    def get_catalog_item(self, asin: str, marketplace_id: str) -> Dict:
        """Tek katalog ürünü getirir"""
        endpoint = f"/catalog/2022-04-01/items/{asin}"
        
        params = {
            "marketplaceIds": marketplace_id,
            "includedData": "attributes,dimensions,identifiers,images,productTypes,relationships,salesRanks"
        }
        
        return self._make_request('GET', endpoint, params)

    # ENVANTER YÖNETİMİ - FBA Inventory API
    def get_inventory_summaries(self, marketplace_ids: List[str], details: bool = True) -> Dict:
        """FBA envanter özetlerini getirir"""
        endpoint = "/fba/inventory/v1/summaries"
        
        params = {
            "details": str(details).lower(),
            "marketplaceIds": ",".join(marketplace_ids)
        }
        
        return self._make_request('GET', endpoint, params)

    def get_inventory_age(self, marketplace_id: str) -> Dict:
        """Envanter yaşlandırma raporunu getirir"""
        endpoint = "/fba/inventory/v1/inventoryAge"
        
        params = {
            "marketplaceIds": marketplace_id
        }
        
        return self._make_request('GET', endpoint, params)

    # SİPARİŞ YÖNETİMİ - Orders API
    def get_orders(self, marketplace_ids: List[str], created_after: str = None,
                   created_before: str = None, order_statuses: List[str] = None,
                   max_results_per_page: int = 100) -> Dict:
        """Siparişleri getirir"""
        endpoint = "/orders/v0/orders"
        
        params = {
            "MarketplaceIds": ",".join(marketplace_ids),
            "MaxResultsPerPage": max_results_per_page
        }
        
        if created_after:
            params["CreatedAfter"] = created_after
        if created_before:
            params["CreatedBefore"] = created_before
        if order_statuses:
            params["OrderStatuses"] = ",".join(order_statuses)
            
        return self._make_request('GET', endpoint, params)

    def get_order(self, order_id: str) -> Dict:
        """Tek sipariş bilgisini getirir"""
        endpoint = f"/orders/v0/orders/{order_id}"
        return self._make_request('GET', endpoint)

    def get_order_items(self, order_id: str) -> Dict:
        """Sipariş öğelerini getirir"""
        endpoint = f"/orders/v0/orders/{order_id}/orderItems"
        return self._make_request('GET', endpoint)

    def get_order_address(self, order_id: str) -> Dict:
        """Sipariş adresini getirir (RDT gerekli)"""
        endpoint = f"/orders/v0/orders/{order_id}/address"
        return self._make_request('GET', endpoint)

    def get_order_buyer_info(self, order_id: str) -> Dict:
        """Sipariş alıcı bilgilerini getirir (RDT gerekli)"""
        endpoint = f"/orders/v0/orders/{order_id}/buyerInfo"
        return self._make_request('GET', endpoint)

    # ÜRÜN LİSTELEME - Listings Items API
    def get_listings_item(self, seller_id: str, sku: str, marketplace_ids: List[str]) -> Dict:
        """Listeleme öğesini getirir"""
        endpoint = f"/listings/2021-08-01/items/{seller_id}/{sku}"
        
        params = {
            "marketplaceIds": ",".join(marketplace_ids),
            "includedData": "summaries,attributes,issues,offers,fulfillmentAvailability"
        }
        
        return self._make_request('GET', endpoint, params)

    def put_listings_item(self, seller_id: str, sku: str, marketplace_ids: List[str], 
                         product_data: Dict) -> Dict:
        """Listeleme öğesi oluşturur/günceller"""
        endpoint = f"/listings/2021-08-01/items/{seller_id}/{sku}"
        
        params = {
            "marketplaceIds": ",".join(marketplace_ids)
        }
        
        return self._make_request('PUT', endpoint, params, product_data)

    def patch_listings_item(self, seller_id: str, sku: str, marketplace_ids: List[str],
                           patches: List[Dict]) -> Dict:
        """Listeleme öğesini kısmi günceller"""
        endpoint = f"/listings/2021-08-01/items/{seller_id}/{sku}"
        
        params = {
            "marketplaceIds": ",".join(marketplace_ids)
        }
        
        data = {
            "productType": "PRODUCT",  # Bu değer ürün tipine göre değişmeli
            "patches": patches
        }
        
        return self._make_request('PATCH', endpoint, params, data)

    def delete_listings_item(self, seller_id: str, sku: str, marketplace_ids: List[str]) -> Dict:
        """Listeleme öğesini siler"""
        endpoint = f"/listings/2021-08-01/items/{seller_id}/{sku}"
        
        params = {
            "marketplaceIds": ",".join(marketplace_ids)
        }
        
        return self._make_request('DELETE', endpoint, params)

    # FİYATLANDIRMA - Product Pricing API
    def get_pricing(self, marketplace_id: str, asins: List[str] = None, 
                   skus: List[str] = None, item_type: str = "Asin") -> Dict:
        """Ürün fiyatlarını getirir"""
        endpoint = "/products/pricing/v0/price"
        
        params = {
            "MarketplaceId": marketplace_id,
            "ItemType": item_type
        }
        
        if asins:
            params["Asins"] = ",".join(asins)
        if skus:
            params["Skus"] = ",".join(skus)
            
        return self._make_request('GET', endpoint, params)

    def get_competitive_pricing(self, marketplace_id: str, asins: List[str] = None,
                               skus: List[str] = None, item_type: str = "Asin") -> Dict:
        """Rekabetçi fiyatları getirir"""
        endpoint = "/products/pricing/v0/competitivePrice"
        
        params = {
            "MarketplaceId": marketplace_id,
            "ItemType": item_type
        }
        
        if asins:
            params["Asins"] = ",".join(asins)
        if skus:
            params["Skus"] = ",".join(skus)
            
        return self._make_request('GET', endpoint, params)

    # RAPORLAMA - Reports API
    def create_report(self, report_type: str, marketplace_ids: List[str],
                     start_time: str = None, end_time: str = None) -> Dict:
        """Rapor oluşturur"""
        endpoint = "/reports/2021-06-30/reports"
        
        data = {
            "reportType": report_type,
            "marketplaceIds": marketplace_ids
        }
        
        if start_time:
            data["dataStartTime"] = start_time
        if end_time:
            data["dataEndTime"] = end_time
            
        return self._make_request('POST', endpoint, data=data)

    def get_report(self, report_id: str) -> Dict:
        """Rapor durumunu getirir"""
        endpoint = f"/reports/2021-06-30/reports/{report_id}"
        return self._make_request('GET', endpoint)

    def get_report_document(self, report_document_id: str) -> Dict:
        """Rapor belgesini getirir"""
        endpoint = f"/reports/2021-06-30/documents/{report_document_id}"
        return self._make_request('GET', endpoint)

    # FEEDS API - Toplu İşlemler
    def create_feed(self, feed_type: str, marketplace_ids: List[str], 
                   input_feed_document_id: str) -> Dict:
        """Feed oluşturur"""
        endpoint = "/feeds/2021-06-30/feeds"
        
        data = {
            "feedType": feed_type,
            "marketplaceIds": marketplace_ids,
            "inputFeedDocumentId": input_feed_document_id
        }
        
        return self._make_request('POST', endpoint, data=data)

    def get_feed(self, feed_id: str) -> Dict:
        """Feed durumunu getirir"""
        endpoint = f"/feeds/2021-06-30/feeds/{feed_id}"
        return self._make_request('GET', endpoint)

    def create_feed_document(self, content_type: str) -> Dict:
        """Feed belgesi oluşturur"""
        endpoint = "/feeds/2021-06-30/documents"
        
        data = {
            "contentType": content_type
        }
        
        return self._make_request('POST', endpoint, data=data)

    # FBA YÖNETİMİ - Fulfillment Inbound API
    def create_inbound_shipment_plan(self, ship_from_address: Dict, 
                                   inbound_shipment_plan_request_items: List[Dict],
                                   marketplace_id: str) -> Dict:
        """FBA gönderim planı oluşturur"""
        endpoint = "/fba/inbound/v0/plans"
        
        data = {
            "ShipFromAddress": ship_from_address,
            "InboundShipmentPlanRequestItems": inbound_shipment_plan_request_items,
            "MarketplaceId": marketplace_id
        }
        
        return self._make_request('POST', endpoint, data=data)

    def create_inbound_shipment(self, shipment_id: str, inbound_shipment_header: Dict) -> Dict:
        """FBA gönderimi oluşturur"""
        endpoint = f"/fba/inbound/v0/shipments/{shipment_id}"
        
        data = {
            "InboundShipmentHeader": inbound_shipment_header
        }
        
        return self._make_request('POST', endpoint, data=data)

    def get_inbound_shipment(self, shipment_id: str) -> Dict:
        """FBA gönderim bilgilerini getirir"""
        endpoint = f"/fba/inbound/v0/shipments/{shipment_id}"
        return self._make_request('GET', endpoint)

    # NOTIFICATIONS API
    def create_subscription(self, notification_type: str, destination_id: str) -> Dict:
        """Bildirim aboneliği oluşturur"""
        endpoint = "/notifications/v1/subscriptions"
        
        data = {
            "notificationType": notification_type,
            "destinationId": destination_id
        }
        
        return self._make_request('POST', endpoint, data=data)

    def get_subscription(self, notification_type: str) -> Dict:
        """Bildirim aboneliğini getirir"""
        endpoint = f"/notifications/v1/subscriptions/{notification_type}"
        return self._make_request('GET', endpoint)

    def delete_subscription(self, notification_type: str, destination_id: str) -> Dict:
        """Bildirim aboneliğini siler"""
        endpoint = f"/notifications/v1/subscriptions/{notification_type}/{destination_id}"
        return self._make_request('DELETE', endpoint)

    # TEST FONKSİYONLARI
    def test_connection(self) -> Dict:
        """API bağlantısını test eder"""
        try:
            result = self.get_marketplace_participations()
            if "payload" in result:
                return {
                    "success": True,
                    "message": "Amazon SP-API bağlantısı başarılı",
                    "client_id": self.client_id[:8] + "...",
                    "region": self.region,
                    "sandbox": self.sandbox
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
                "message": f"Amazon SP-API bağlantı hatası: {str(e)}"
            }

    # YARDIMCI FONKSİYONLAR
    def get_marketplace_id(self, country_code: str) -> str:
        """Ülke koduna göre marketplace ID döndürür"""
        return self.marketplace_ids.get(country_code.upper(), self.marketplace_ids["US"])

    def format_datetime(self, dt: datetime) -> str:
        """Datetime'ı Amazon API formatına çevirir"""
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# Örnek kullanım ve test fonksiyonları
def test_amazon_sp_api():
    """Amazon SP-API'sini test eder"""
    
    # Test credentials (gerçek projede environment variable'lardan alınmalı)
    client_id = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"
    refresh_token = "YOUR_REFRESH_TOKEN"
    
    # API client oluştur
    amazon = AmazonSPAPI(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        region="NA",  # NA, EU, FE
        sandbox=True
    )
    
    print("🔄 Amazon SP-API Bağlantı Testi...")
    connection_test = amazon.test_connection()
    print(f"Bağlantı: {'✅ Başarılı' if connection_test['success'] else '❌ Başarısız'}")
    
    if connection_test['success']:
        print("\n🏪 Pazaryeri Katılımları Testi...")
        participations = amazon.get_marketplace_participations()
        print(f"Pazaryerleri alındı: {'✅' if 'payload' in participations else '❌'}")
        
        print("\n📦 Sipariş Listesi Testi...")
        marketplace_ids = [amazon.get_marketplace_id("US")]
        orders = amazon.get_orders(
            marketplace_ids=marketplace_ids,
            created_after=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        print(f"Siparişler alındı: {'✅' if 'payload' in orders else '❌'}")
        
        print("\n📋 Katalog Arama Testi...")
        catalog_search = amazon.search_catalog_items(
            keywords="laptop",
            marketplace_id=marketplace_ids[0]
        )
        print(f"Katalog arama yapıldı: {'✅' if 'payload' in catalog_search else '❌'}")
        
        print("\n📊 Envanter Özeti Testi...")
        inventory = amazon.get_inventory_summaries(marketplace_ids)
        print(f"Envanter alındı: {'✅' if 'payload' in inventory else '❌'}")


if __name__ == "__main__":
    test_amazon_sp_api()