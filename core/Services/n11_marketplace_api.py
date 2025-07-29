"""
N11 Marketplace API - Gerçek Implementasyon
Bu modül N11'in resmi Marketplace API'sini kullanır.
API Dokümantasyonu: https://www.n11.com/
"""

import requests
import json
import hashlib
import hmac
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom

class N11MarketplaceAPI:
    """N11 Marketplace API Client"""
    
    def __init__(self, api_key: str, api_secret: str, sandbox: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.sandbox = sandbox
        
        # API Base URLs
        if sandbox:
            self.base_url = "https://api.n11.com/ws"  # N11 sandbox URL
        else:
            self.base_url = "https://api.n11.com/ws"  # N11 production URL (aynı endpoint)
            
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/xml',
            'User-Agent': 'N11Marketplace-Python-Client/1.0'
        })
        
        self.logger = logging.getLogger(__name__)

    def _generate_signature(self, data: str) -> str:
        """API imzası oluşturur"""
        message = self.api_key + data
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha1
        ).digest()
        return base64.b64encode(signature).decode('utf-8')

    def _create_auth_element(self, root: ET.Element) -> ET.Element:
        """XML auth elementi oluşturur"""
        auth = ET.SubElement(root, "auth")
        ET.SubElement(auth, "appKey").text = self.api_key
        ET.SubElement(auth, "appSecret").text = self.api_secret
        return auth

    def _make_request(self, service: str, xml_data: str) -> Dict:
        """API isteği yapar"""
        url = f"{self.base_url}/{service}"
        
        try:
            response = self.session.post(url, data=xml_data)
            response.raise_for_status()
            
            # XML yanıtını parse et
            root = ET.fromstring(response.content)
            
            # XML'i dictionary'ye çevir
            return self._xml_to_dict(root)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"N11 API request failed: {e}")
            return {"success": False, "error": str(e)}
        except ET.ParseError as e:
            self.logger.error(f"N11 XML parse error: {e}")
            return {"success": False, "error": f"XML parse error: {str(e)}"}

    def _xml_to_dict(self, element: ET.Element) -> Dict:
        """XML elementini dictionary'ye çevirir"""
        result = {}
        
        # Elementte text varsa
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        # Alt elementleri işle
        for child in element:
            child_data = self._xml_to_dict(child)
            
            if child.tag in result:
                # Aynı tag'den birden fazla varsa liste yap
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        # Attributeleri ekle
        if element.attrib:
            result['@attributes'] = element.attrib
            
        return result

    def _dict_to_xml(self, data: Dict, root_name: str = "root") -> str:
        """Dictionary'yi XML'e çevirir"""
        root = ET.Element(root_name)
        self._build_xml_element(root, data)
        
        # XML'i güzel formatla
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def _build_xml_element(self, parent: ET.Element, data: Any):
        """XML elementi oluşturur"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key.startswith('@'):
                    continue
                child = ET.SubElement(parent, key)
                self._build_xml_element(child, value)
        elif isinstance(data, list):
            for item in data:
                self._build_xml_element(parent, item)
        else:
            parent.text = str(data)

    # ÜRÜN YÖNETİMİ
    def save_product(self, product_data: Dict) -> Dict:
        """Ürün kaydet/güncelle"""
        root = ET.Element("productRequest")
        self._create_auth_element(root)
        
        product = ET.SubElement(root, "product")
        
        # Ürün bilgilerini XML'e çevir
        if "productId" in product_data:
            ET.SubElement(product, "id").text = str(product_data["productId"])
        
        ET.SubElement(product, "title").text = product_data.get("title", "")
        ET.SubElement(product, "subtitle").text = product_data.get("subtitle", "")
        ET.SubElement(product, "description").text = product_data.get("description", "")
        
        # Kategori
        category = ET.SubElement(product, "category")
        ET.SubElement(category, "id").text = str(product_data.get("categoryId", ""))
        
        # Fiyat
        ET.SubElement(product, "price").text = str(product_data.get("price", 0))
        ET.SubElement(product, "currencyType").text = product_data.get("currencyType", "TL")
        
        # Stok
        stockItems = ET.SubElement(product, "stockItems")
        stockItem = ET.SubElement(stockItems, "stockItem")
        ET.SubElement(stockItem, "bundle").text = "1"
        ET.SubElement(stockItem, "quantity").text = str(product_data.get("quantity", 0))
        ET.SubElement(stockItem, "sellerStockCode").text = product_data.get("stockCode", "")
        
        # Resimler
        if "images" in product_data:
            images = ET.SubElement(product, "images")
            for i, image_url in enumerate(product_data["images"]):
                image = ET.SubElement(images, "image")
                ET.SubElement(image, "url").text = image_url
                ET.SubElement(image, "order").text = str(i + 1)
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("ProductService.wsdl", xml_data)

    def get_product_list(self, page_index: int = 0, page_size: int = 100) -> Dict:
        """Ürün listesini getirir"""
        root = ET.Element("productListRequest")
        self._create_auth_element(root)
        
        pagingData = ET.SubElement(root, "pagingData")
        ET.SubElement(pagingData, "currentPage").text = str(page_index)
        ET.SubElement(pagingData, "pageSize").text = str(page_size)
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("ProductService.wsdl", xml_data)

    def get_product(self, product_id: str) -> Dict:
        """Tek ürün bilgisini getirir"""
        root = ET.Element("productRequest")
        self._create_auth_element(root)
        
        ET.SubElement(root, "productId").text = product_id
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("ProductService.wsdl", xml_data)

    def delete_product(self, product_id: str) -> Dict:
        """Ürün siler"""
        root = ET.Element("productRequest")
        self._create_auth_element(root)
        
        ET.SubElement(root, "productId").text = product_id
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("ProductService.wsdl", xml_data)

    def update_stock_by_stock_code(self, stock_code: str, quantity: int) -> Dict:
        """Stok koduna göre stok günceller"""
        root = ET.Element("stockUpdateRequest")
        self._create_auth_element(root)
        
        stockItems = ET.SubElement(root, "stockItems")
        stockItem = ET.SubElement(stockItems, "stockItem")
        ET.SubElement(stockItem, "sellerStockCode").text = stock_code
        ET.SubElement(stockItem, "quantity").text = str(quantity)
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("ProductStockService.wsdl", xml_data)

    # SİPARİŞ YÖNETİMİ
    def get_order_list(self, start_date: str = None, end_date: str = None,
                       status: str = None, page_index: int = 0, page_size: int = 100) -> Dict:
        """Sipariş listesini getirir"""
        root = ET.Element("orderListRequest")
        self._create_auth_element(root)
        
        # Tarih filtresi
        if start_date:
            ET.SubElement(root, "startDate").text = start_date
        if end_date:
            ET.SubElement(root, "endDate").text = end_date
        if status:
            ET.SubElement(root, "status").text = status
        
        # Sayfalama
        pagingData = ET.SubElement(root, "pagingData")
        ET.SubElement(pagingData, "currentPage").text = str(page_index)
        ET.SubElement(pagingData, "pageSize").text = str(page_size)
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("OrderService.wsdl", xml_data)

    def get_order_detail(self, order_id: str) -> Dict:
        """Sipariş detayını getirir"""
        root = ET.Element("orderDetailRequest")
        self._create_auth_element(root)
        
        ET.SubElement(root, "orderId").text = order_id
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("OrderService.wsdl", xml_data)

    def ship_order(self, order_item_id: str, tracking_number: str, cargo_company_id: int) -> Dict:
        """Siparişi kargoya verir"""
        root = ET.Element("orderItemShipmentRequest")
        self._create_auth_element(root)
        
        ET.SubElement(root, "orderItemId").text = order_item_id
        ET.SubElement(root, "trackingNumber").text = tracking_number
        ET.SubElement(root, "shipmentCompanyId").text = str(cargo_company_id)
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("OrderService.wsdl", xml_data)

    def accept_order(self, order_item_list: List[str]) -> Dict:
        """Siparişi onayla"""
        root = ET.Element("orderItemAcceptRequest")
        self._create_auth_element(root)
        
        orderItemList = ET.SubElement(root, "orderItemList")
        for item_id in order_item_list:
            orderItem = ET.SubElement(orderItemList, "orderItem")
            ET.SubElement(orderItem, "id").text = item_id
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("OrderService.wsdl", xml_data)

    def reject_order(self, order_item_list: List[Dict]) -> Dict:
        """Siparişi reddet"""
        root = ET.Element("orderItemRejectRequest")
        self._create_auth_element(root)
        
        orderItemList = ET.SubElement(root, "orderItemList")
        for item in order_item_list:
            orderItem = ET.SubElement(orderItemList, "orderItem")
            ET.SubElement(orderItem, "id").text = item["id"]
            ET.SubElement(orderItem, "rejectReason").text = item.get("reason", "")
            ET.SubElement(orderItem, "rejectReasonType").text = item.get("reasonType", "")
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("OrderService.wsdl", xml_data)

    # KATEGORİ YÖNETİMİ
    def get_top_level_categories(self) -> Dict:
        """Ana kategorileri getirir"""
        root = ET.Element("categoryRequest")
        self._create_auth_element(root)
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("CategoryService.wsdl", xml_data)

    def get_sub_categories(self, category_id: str) -> Dict:
        """Alt kategorileri getirir"""
        root = ET.Element("categoryRequest")
        self._create_auth_element(root)
        
        ET.SubElement(root, "categoryId").text = category_id
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("CategoryService.wsdl", xml_data)

    def get_category_attributes(self, category_id: str) -> Dict:
        """Kategori özelliklerini getirir"""
        root = ET.Element("categoryAttributesRequest")
        self._create_auth_element(root)
        
        ET.SubElement(root, "categoryId").text = category_id
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("CategoryService.wsdl", xml_data)

    # KARGO YÖNETİMİ
    def get_shipment_companies(self) -> Dict:
        """Kargo firmalarını listeler"""
        root = ET.Element("shipmentCompanyRequest")
        self._create_auth_element(root)
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("ShipmentService.wsdl", xml_data)

    def get_shipment_template(self, seller_id: str) -> Dict:
        """Kargo şablonunu getirir"""
        root = ET.Element("shipmentTemplateRequest")
        self._create_auth_element(root)
        
        ET.SubElement(root, "sellerId").text = seller_id
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("ShipmentService.wsdl", xml_data)

    # CITY VE DISTRICT
    def get_cities(self) -> Dict:
        """Şehir listesini getirir"""
        root = ET.Element("cityRequest")
        self._create_auth_element(root)
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("CityService.wsdl", xml_data)

    def get_districts(self, city_code: str) -> Dict:
        """İlçe listesini getirir"""
        root = ET.Element("districtRequest")
        self._create_auth_element(root)
        
        ET.SubElement(root, "cityCode").text = city_code
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("CityService.wsdl", xml_data)

    # TEST FONKSİYONLARI
    def test_connection(self) -> Dict:
        """API bağlantısını test eder"""
        try:
            result = self.get_top_level_categories()
            if "category" in str(result) or "result" in result:
                return {
                    "success": True,
                    "message": "N11 API bağlantısı başarılı",
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
                "message": f"N11 API bağlantı hatası: {str(e)}"
            }

    def get_account_info(self) -> Dict:
        """Hesap bilgilerini getirir"""
        root = ET.Element("accountInfoRequest")
        self._create_auth_element(root)
        
        xml_data = ET.tostring(root, encoding='unicode')
        return self._make_request("AccountService.wsdl", xml_data)


# Örnek kullanım ve test fonksiyonları
def test_n11_api():
    """N11 API'sini test eder"""
    
    # Test credentials (gerçek projede environment variable'lardan alınmalı)
    api_key = "YOUR_API_KEY"
    api_secret = "YOUR_API_SECRET"
    
    # API client oluştur
    n11 = N11MarketplaceAPI(
        api_key=api_key,
        api_secret=api_secret,
        sandbox=True
    )
    
    print("🔄 N11 API Bağlantı Testi...")
    connection_test = n11.test_connection()
    print(f"Bağlantı: {'✅ Başarılı' if connection_test['success'] else '❌ Başarısız'}")
    
    if connection_test['success']:
        print("\n📦 Ürün Listesi Testi...")
        products = n11.get_product_list(page_index=0, page_size=10)
        print(f"Ürün listesi alındı: {len(str(products))}")
        
        print("\n📋 Kategori Listesi Testi...")
        categories = n11.get_top_level_categories()
        print(f"Kategori listesi alındı: {len(str(categories))}")
        
        print("\n🏢 Kargo Firmaları Testi...")
        cargo_companies = n11.get_shipment_companies()
        print(f"Kargo firmaları alındı: {len(str(cargo_companies))}")
        
        print("\n📦 Sipariş Listesi Testi...")
        orders = n11.get_order_list(page_index=0, page_size=10)
        print(f"Sipariş listesi alındı: {len(str(orders))}")


if __name__ == "__main__":
    test_n11_api()