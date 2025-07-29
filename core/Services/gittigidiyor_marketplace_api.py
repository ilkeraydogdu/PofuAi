"""
GittiGidiyor Marketplace API - Gerçek Implementasyon
Bu modül GittiGidiyor'un resmi API'sini kullanır.
API Dokümantasyonu: https://dev.gittigidiyor.com/
"""

import requests
import json
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from urllib.parse import urlencode, quote
import xml.etree.ElementTree as ET

class GittiGidiyorMarketplaceAPI:
    """GittiGidiyor Marketplace API Client"""
    
    def __init__(self, api_key: str, secret_key: str, sandbox: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.sandbox = sandbox
        
        # API Base URLs
        if sandbox:
            self.base_url = "https://dev.gittigidiyor.com:8443/listingapi/ws"
        else:
            self.base_url = "https://www.gittigidiyor.com/listingapi/ws"
            
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/xml; charset=utf-8',
            'User-Agent': 'GittiGidiyor-Python-Client/1.0'
        })
        
        self.logger = logging.getLogger(__name__)

    def _generate_signature(self, method: str, url: str, params: Dict = None) -> str:
        """API imzası oluşturur"""
        # OAuth 1.0a imza oluşturma
        normalized_params = []
        
        if params:
            for key, value in sorted(params.items()):
                normalized_params.append(f"{quote(str(key))}={quote(str(value))}")
        
        param_string = "&".join(normalized_params)
        
        base_string = f"{method.upper()}&{quote(url)}&{quote(param_string)}"
        
        signing_key = f"{quote(self.secret_key)}&"
        
        signature = hmac.new(
            signing_key.encode('utf-8'),
            base_string.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> Dict:
        """API isteği yapar"""
        url = f"{self.base_url}{endpoint}"
        
        # OAuth parametreleri
        oauth_params = {
            'oauth_consumer_key': self.api_key,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(datetime.now().timestamp())),
            'oauth_nonce': hashlib.md5(str(datetime.now()).encode()).hexdigest(),
            'oauth_version': '1.0'
        }
        
        if params:
            oauth_params.update(params)
        
        # İmza oluştur
        oauth_params['oauth_signature'] = self._generate_signature(method, url, oauth_params)
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=oauth_params)
            elif method.upper() == 'POST':
                if data:
                    # XML data gönder
                    xml_data = self._dict_to_xml(data)
                    response = self.session.post(url, data=xml_data, params=oauth_params)
                else:
                    response = self.session.post(url, params=oauth_params)
            elif method.upper() == 'PUT':
                if data:
                    xml_data = self._dict_to_xml(data)
                    response = self.session.put(url, data=xml_data, params=oauth_params)
                else:
                    response = self.session.put(url, params=oauth_params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=oauth_params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            
            # XML yanıtını parse et
            if response.content:
                root = ET.fromstring(response.content)
                return self._xml_to_dict(root)
            else:
                return {"success": True}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GittiGidiyor API request failed: {e}")
            if hasattr(e, 'response') and e.response:
                self.logger.error(f"Response: {e.response.text}")
            return {"success": False, "error": str(e)}

    def _dict_to_xml(self, data: Dict, root_name: str = "request") -> str:
        """Dictionary'yi XML'e çevirir"""
        root = ET.Element(root_name)
        self._build_xml_element(root, data)
        return ET.tostring(root, encoding='unicode')

    def _build_xml_element(self, parent: ET.Element, data: Any):
        """XML elementi oluşturur"""
        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(parent, key)
                self._build_xml_element(child, value)
        elif isinstance(data, list):
            for item in data:
                self._build_xml_element(parent, item)
        else:
            parent.text = str(data)

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

    # ÜRÜN YÖNETİMİ
    def insert_product(self, product_data: Dict) -> Dict:
        """Yeni ürün ekler"""
        endpoint = "/insertProduct"
        
        # GittiGidiyor ürün formatına çevir
        gg_product = {
            "product": {
                "title": product_data.get("title"),
                "subtitle": product_data.get("subtitle", ""),
                "specs": product_data.get("specs", ""),
                "description": product_data.get("description"),
                "categoryCode": product_data.get("category_code"),
                "format": product_data.get("format", "Store"),  # Store, Auction
                "startPrice": product_data.get("start_price"),
                "buyNowPrice": product_data.get("buy_now_price"),
                "netEarning": product_data.get("net_earning"),
                "productCondition": product_data.get("condition", "Yeni"),
                "collectable": product_data.get("collectable", False),
                "color": product_data.get("color", ""),
                "size": product_data.get("size", ""),
                "pageTemplate": product_data.get("page_template", 1),
                "listingDays": product_data.get("listing_days", 30),
                "itemCount": product_data.get("item_count", 1),
                "boldOption": product_data.get("bold_option", False),
                "catalogId": product_data.get("catalog_id"),
                "cargoDetail": {
                    "cargoCompany": product_data.get("cargo_company", "Aras Kargo"),
                    "cargoPaymentType": product_data.get("cargo_payment", "Satici"),
                    "cargoPrice": product_data.get("cargo_price", 0)
                }
            }
        }
        
        # Resimler ekle
        if "images" in product_data:
            gg_product["product"]["photos"] = {
                "photo": [{"url": img} for img in product_data["images"]]
            }
        
        return self._make_request('POST', endpoint, gg_product)

    def update_product(self, product_id: str, product_data: Dict) -> Dict:
        """Ürün günceller"""
        endpoint = "/changeProduct"
        
        update_data = {
            "product": {
                "productId": product_id,
                **product_data
            }
        }
        
        return self._make_request('POST', endpoint, update_data)

    def get_product(self, product_id: str) -> Dict:
        """Tek ürün bilgisini getirir"""
        endpoint = "/getProduct"
        params = {"productId": product_id}
        return self._make_request('GET', endpoint, params=params)

    def get_products(self, start_offset: int = 0, row_count: int = 100,
                    with_data: bool = True) -> Dict:
        """Ürün listesini getirir"""
        endpoint = "/getProducts"
        
        params = {
            "startOffSet": start_offset,
            "rowCount": row_count,
            "withData": str(with_data).lower()
        }
        
        return self._make_request('GET', endpoint, params=params)

    def delete_product(self, product_id: str) -> Dict:
        """Ürün siler"""
        endpoint = "/deleteProduct"
        params = {"productId": product_id}
        return self._make_request('DELETE', endpoint, params=params)

    def change_product_status(self, product_id: str, status: str) -> Dict:
        """Ürün durumunu değiştirir"""
        endpoint = "/changeProductStatus"
        
        data = {
            "productId": product_id,
            "status": status  # "A" (Aktif), "P" (Pasif), "S" (Satıldı)
        }
        
        return self._make_request('POST', endpoint, data)

    # STOK YÖNETİMİ
    def update_stock(self, product_id: str, stock_count: int) -> Dict:
        """Stok günceller"""
        endpoint = "/updateStock"
        
        data = {
            "productId": product_id,
            "itemCount": stock_count
        }
        
        return self._make_request('POST', endpoint, data)

    def get_stock(self, product_id: str) -> Dict:
        """Stok bilgisini getirir"""
        endpoint = "/getStock"
        params = {"productId": product_id}
        return self._make_request('GET', endpoint, params=params)

    # SİPARİŞ YÖNETİMİ
    def get_sales(self, start_date: str = None, end_date: str = None,
                 start_offset: int = 0, row_count: int = 100) -> Dict:
        """Satış listesini getirir"""
        endpoint = "/getSales"
        
        params = {
            "startOffSet": start_offset,
            "rowCount": row_count
        }
        
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
            
        return self._make_request('GET', endpoint, params=params)

    def get_sale_detail(self, sale_id: str) -> Dict:
        """Satış detayını getirir"""
        endpoint = "/getSaleDetail"
        params = {"saleId": sale_id}
        return self._make_request('GET', endpoint, params=params)

    def ship_sale(self, sale_id: str, cargo_company: str, tracking_number: str) -> Dict:
        """Satışı kargoya verir"""
        endpoint = "/shipSale"
        
        data = {
            "saleId": sale_id,
            "cargoCompany": cargo_company,
            "trackingNumber": tracking_number
        }
        
        return self._make_request('POST', endpoint, data)

    def get_sale_invoice(self, sale_id: str) -> Dict:
        """Satış faturasını getirir"""
        endpoint = "/getSaleInvoice"
        params = {"saleId": sale_id}
        return self._make_request('GET', endpoint, params=params)

    # KATEGORİ YÖNETİMİ
    def get_categories(self, parent_id: str = None) -> Dict:
        """Kategori listesini getirir"""
        endpoint = "/getCategories"
        
        params = {}
        if parent_id:
            params["parentId"] = parent_id
            
        return self._make_request('GET', endpoint, params=params)

    def get_category_specs(self, category_code: str) -> Dict:
        """Kategori özelliklerini getirir"""
        endpoint = "/getCategorySpecs"
        params = {"categoryCode": category_code}
        return self._make_request('GET', endpoint, params=params)

    def search_category(self, keyword: str) -> Dict:
        """Kategori arar"""
        endpoint = "/searchCategory"
        params = {"keyword": keyword}
        return self._make_request('GET', endpoint, params=params)

    # KARGO YÖNETİMİ
    def get_cargo_companies(self) -> Dict:
        """Kargo firmalarını listeler"""
        endpoint = "/getCargoCompanies"
        return self._make_request('GET', endpoint)

    def calculate_cargo_price(self, cargo_company: str, city_code: str,
                             weight: float = 1.0) -> Dict:
        """Kargo ücreti hesaplar"""
        endpoint = "/calculateCargoPrice"
        
        params = {
            "cargoCompany": cargo_company,
            "cityCode": city_code,
            "weight": weight
        }
        
        return self._make_request('GET', endpoint, params=params)

    # MESAJLAŞMA
    def get_messages(self, start_offset: int = 0, row_count: int = 50) -> Dict:
        """Mesaj listesini getirir"""
        endpoint = "/getMessages"
        
        params = {
            "startOffSet": start_offset,
            "rowCount": row_count
        }
        
        return self._make_request('GET', endpoint, params=params)

    def get_message_detail(self, message_id: str) -> Dict:
        """Mesaj detayını getirir"""
        endpoint = "/getMessageDetail"
        params = {"messageId": message_id}
        return self._make_request('GET', endpoint, params=params)

    def send_message(self, recipient: str, subject: str, message: str,
                    sale_id: str = None) -> Dict:
        """Mesaj gönderir"""
        endpoint = "/sendMessage"
        
        data = {
            "recipient": recipient,
            "subject": subject,
            "message": message
        }
        
        if sale_id:
            data["saleId"] = sale_id
            
        return self._make_request('POST', endpoint, data)

    # RAPORLAMA
    def get_store_statistics(self, start_date: str = None, end_date: str = None) -> Dict:
        """Mağaza istatistiklerini getirir"""
        endpoint = "/getStoreStatistics"
        
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
            
        return self._make_request('GET', endpoint, params=params)

    def get_product_statistics(self, product_id: str) -> Dict:
        """Ürün istatistiklerini getirir"""
        endpoint = "/getProductStatistics"
        params = {"productId": product_id}
        return self._make_request('GET', endpoint, params=params)

    # KULLANICI YÖNETİMİ
    def get_user_info(self) -> Dict:
        """Kullanıcı bilgilerini getirir"""
        endpoint = "/getUserInfo"
        return self._make_request('GET', endpoint)

    def update_user_info(self, user_data: Dict) -> Dict:
        """Kullanıcı bilgilerini günceller"""
        endpoint = "/updateUserInfo"
        return self._make_request('POST', endpoint, user_data)

    # ÖDEME YÖNETİMİ
    def get_payment_options(self) -> Dict:
        """Ödeme seçeneklerini getirir"""
        endpoint = "/getPaymentOptions"
        return self._make_request('GET', endpoint)

    def set_payment_options(self, payment_data: Dict) -> Dict:
        """Ödeme seçeneklerini ayarlar"""
        endpoint = "/setPaymentOptions"
        return self._make_request('POST', endpoint, payment_data)

    # PROMOSYON YÖNETİMİ
    def get_promotions(self) -> Dict:
        """Promosyon listesini getirir"""
        endpoint = "/getPromotions"
        return self._make_request('GET', endpoint)

    def create_promotion(self, promotion_data: Dict) -> Dict:
        """Promosyon oluşturur"""
        endpoint = "/createPromotion"
        return self._make_request('POST', endpoint, promotion_data)

    def update_promotion(self, promotion_id: str, promotion_data: Dict) -> Dict:
        """Promosyon günceller"""
        endpoint = "/updatePromotion"
        
        data = {
            "promotionId": promotion_id,
            **promotion_data
        }
        
        return self._make_request('POST', endpoint, data)

    def delete_promotion(self, promotion_id: str) -> Dict:
        """Promosyon siler"""
        endpoint = "/deletePromotion"
        params = {"promotionId": promotion_id}
        return self._make_request('DELETE', endpoint, params=params)

    # TEST FONKSİYONLARI
    def test_connection(self) -> Dict:
        """API bağlantısını test eder"""
        try:
            result = self.get_user_info()
            if "user" in result or result.get("success", True):
                return {
                    "success": True,
                    "message": "GittiGidiyor API bağlantısı başarılı",
                    "api_key": self.api_key[:8] + "...",
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
                "message": f"GittiGidiyor API bağlantı hatası: {str(e)}"
            }

    def format_gg_datetime(self, dt: datetime) -> str:
        """Datetime'ı GittiGidiyor API formatına çevirir"""
        return dt.strftime("%d/%m/%Y")

    # YARDIMCI FONKSİYONLAR
    def get_category_path(self, category_code: str) -> List[str]:
        """Kategori yolunu getirir"""
        # Bu fonksiyon kategori hiyerarşisini takip eder
        categories = []
        current_code = category_code
        
        while current_code:
            try:
                category_info = self.get_category_specs(current_code)
                if "category" in category_info:
                    categories.insert(0, category_info["category"]["name"])
                    current_code = category_info["category"].get("parentCode")
                else:
                    break
            except:
                break
                
        return categories

    def validate_product_data(self, product_data: Dict) -> List[str]:
        """Ürün verilerini doğrular"""
        errors = []
        
        required_fields = ["title", "description", "category_code", "start_price"]
        for field in required_fields:
            if field not in product_data or not product_data[field]:
                errors.append(f"Gerekli alan eksik: {field}")
        
        if "title" in product_data and len(product_data["title"]) > 60:
            errors.append("Başlık 60 karakterden uzun olamaz")
            
        if "start_price" in product_data and product_data["start_price"] <= 0:
            errors.append("Başlangıç fiyatı 0'dan büyük olmalı")
            
        return errors


# Örnek kullanım ve test fonksiyonları
def test_gittigidiyor_api():
    """GittiGidiyor API'sini test eder"""
    
    # Test credentials (gerçek projede environment variable'lardan alınmalı)
    api_key = "YOUR_API_KEY"
    secret_key = "YOUR_SECRET_KEY"
    
    # API client oluştur
    gg = GittiGidiyorMarketplaceAPI(
        api_key=api_key,
        secret_key=secret_key,
        sandbox=True
    )
    
    print("🔄 GittiGidiyor API Bağlantı Testi...")
    connection_test = gg.test_connection()
    print(f"Bağlantı: {'✅ Başarılı' if connection_test['success'] else '❌ Başarısız'}")
    
    if connection_test['success']:
        print("\n👤 Kullanıcı Bilgileri Testi...")
        user_info = gg.get_user_info()
        print(f"Kullanıcı bilgileri alındı: {'✅' if 'user' in user_info else '❌'}")
        
        print("\n📦 Ürün Listesi Testi...")
        products = gg.get_products(row_count=10)
        print(f"Ürün listesi alındı: {'✅' if 'products' in products else '❌'}")
        
        print("\n📋 Kategori Listesi Testi...")
        categories = gg.get_categories()
        print(f"Kategori listesi alındı: {'✅' if 'categories' in categories else '❌'}")
        
        print("\n💰 Satış Listesi Testi...")
        sales = gg.get_sales(row_count=10)
        print(f"Satış listesi alındı: {'✅' if 'sales' in sales else '❌'}")
        
        print("\n🚚 Kargo Firmaları Testi...")
        cargo_companies = gg.get_cargo_companies()
        print(f"Kargo firmaları alındı: {'✅' if 'cargoCompanies' in cargo_companies else '❌'}")


if __name__ == "__main__":
    test_gittigidiyor_api()