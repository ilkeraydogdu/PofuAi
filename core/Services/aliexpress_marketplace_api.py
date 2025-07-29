"""
AliExpress Open Platform API - Gerçek Implementasyon
Bu modül AliExpress'in resmi Open Platform API'sini kullanır.
API Dokümantasyonu: https://openservice.aliexpress.com/doc/doc.htm
"""

import requests
import json
import hashlib
import hmac
import base64
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from urllib.parse import urlencode, quote

class AliExpressMarketplaceAPI:
    """AliExpress Open Platform API Client"""
    
    def __init__(self, app_key: str, app_secret: str, access_token: str = None, 
                 sandbox: bool = True):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.sandbox = sandbox
        
        # API Base URLs
        if sandbox:
            self.base_url = "https://api-sg.aliexpress.com/sync"
            self.auth_url = "https://oauth.aliexpress.com/token"
        else:
            self.base_url = "https://gw.api.alibaba.com/openapi"
            self.auth_url = "https://oauth.alibaba.com/token"
        
        self.logger = logging.getLogger(__name__)
        
    def _generate_signature(self, params: Dict[str, Any], method: str = "POST") -> str:
        """Generate API signature"""
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Create query string
        query_string = ""
        for key, value in sorted_params:
            if value is not None:
                query_string += f"{key}{value}"
        
        # Create signature string
        sign_string = self.app_secret + query_string + self.app_secret
        
        # Generate MD5 hash
        signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        return signature
    
    def _make_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request"""
        # Add common parameters
        common_params = {
            'method': method,
            'app_key': self.app_key,
            'timestamp': str(int(time.time() * 1000)),
            'format': 'json',
            'v': '2.0',
            'sign_method': 'md5'
        }
        
        if self.access_token:
            common_params['access_token'] = self.access_token
        
        # Merge parameters
        all_params = {**common_params, **params}
        
        # Generate signature
        signature = self._generate_signature(all_params)
        all_params['sign'] = signature
        
        try:
            response = requests.post(self.base_url, data=all_params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if 'error_response' in result:
                self.logger.error(f"API Error: {result['error_response']}")
                raise Exception(f"API Error: {result['error_response']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")
    
    def get_access_token(self, code: str) -> Dict[str, Any]:
        """Get access token using authorization code"""
        params = {
            'client_id': self.app_key,
            'client_secret': self.app_secret,
            'grant_type': 'authorization_code',
            'code': code
        }
        
        try:
            response = requests.post(self.auth_url, data=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Token request failed: {str(e)}")
            raise
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        params = {
            'client_id': self.app_key,
            'client_secret': self.app_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        try:
            response = requests.post(self.auth_url, data=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Token refresh failed: {str(e)}")
            raise
    
    # Product Management
    def get_product_list(self, page_size: int = 20, current_page: int = 1, 
                        product_status_type: str = "onSelling") -> Dict[str, Any]:
        """Get product list"""
        params = {
            'page_size': page_size,
            'current_page': current_page,
            'product_status_type': product_status_type
        }
        
        return self._make_request('aliexpress.postproduct.redefining.findaeproductbyidfordropshipper', params)
    
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get product details"""
        params = {
            'product_id': product_id
        }
        
        return self._make_request('aliexpress.postproduct.redefining.queryproductbyid', params)
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new product"""
        params = {
            'ae_product': json.dumps(product_data)
        }
        
        return self._make_request('aliexpress.postproduct.redefining.postmultipleproduct', params)
    
    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing product"""
        params = {
            'product_id': product_id,
            'ae_product': json.dumps(product_data)
        }
        
        return self._make_request('aliexpress.postproduct.redefining.editproductcidattidsku', params)
    
    def update_product_stock(self, product_id: str, sku_stock_list: List[Dict]) -> Dict[str, Any]:
        """Update product stock"""
        params = {
            'product_id': product_id,
            'multiple_sku_update_list': json.dumps(sku_stock_list)
        }
        
        return self._make_request('aliexpress.postproduct.redefining.setshopwindowproduct', params)
    
    def update_product_price(self, product_id: str, sku_price_list: List[Dict]) -> Dict[str, Any]:
        """Update product prices"""
        params = {
            'product_id': product_id,
            'multiple_sku_update_list': json.dumps(sku_price_list)
        }
        
        return self._make_request('aliexpress.postproduct.redefining.editproductcidattidsku', params)
    
    # Order Management
    def get_order_list(self, page_size: int = 20, current_page: int = 1,
                      order_status: str = None, create_date_start: str = None,
                      create_date_end: str = None) -> Dict[str, Any]:
        """Get order list"""
        params = {
            'page_size': page_size,
            'current_page': current_page
        }
        
        if order_status:
            params['order_status'] = order_status
        if create_date_start:
            params['create_date_start'] = create_date_start
        if create_date_end:
            params['create_date_end'] = create_date_end
        
        return self._make_request('aliexpress.trade.new.redefining.findorderlistquery', params)
    
    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get order details"""
        params = {
            'order_id': order_id
        }
        
        return self._make_request('aliexpress.trade.new.redefining.findorderbyid', params)
    
    def ship_order(self, order_id: str, tracking_number: str, 
                   logistics_service: str) -> Dict[str, Any]:
        """Ship order"""
        params = {
            'order_id': order_id,
            'tracking_number': tracking_number,
            'logistics_service': logistics_service
        }
        
        return self._make_request('aliexpress.logistics.redefining.createwarehouse', params)
    
    # Category Management
    def get_categories(self) -> Dict[str, Any]:
        """Get product categories"""
        return self._make_request('aliexpress.postproduct.redefining.getproductcategoryinfo', {})
    
    def get_category_attributes(self, category_id: str) -> Dict[str, Any]:
        """Get category attributes"""
        params = {
            'cate_id': category_id
        }
        
        return self._make_request('aliexpress.postproduct.redefining.categoryforecast', params)
    
    # Logistics Management
    def get_logistics_services(self) -> Dict[str, Any]:
        """Get available logistics services"""
        return self._make_request('aliexpress.logistics.redefining.getlogisticsselleraddresses', {})
    
    def create_logistics_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create logistics order"""
        params = {
            'logistics_order': json.dumps(order_data)
        }
        
        return self._make_request('aliexpress.logistics.redefining.createwarehouse', params)
    
    def track_logistics(self, logistics_no: str) -> Dict[str, Any]:
        """Track logistics"""
        params = {
            'logistics_no': logistics_no
        }
        
        return self._make_request('aliexpress.logistics.redefining.querylogisticsorderdetail', params)
    
    # Store Management
    def get_store_info(self) -> Dict[str, Any]:
        """Get store information"""
        return self._make_request('aliexpress.merchant.redefining.querysellerinfo', {})
    
    def get_store_categories(self) -> Dict[str, Any]:
        """Get store categories"""
        return self._make_request('aliexpress.postproduct.redefining.getproductcategoryinfo', {})
    
    # Marketing & Promotion
    def get_promotion_list(self, page_size: int = 20, current_page: int = 1) -> Dict[str, Any]:
        """Get promotion list"""
        params = {
            'page_size': page_size,
            'current_page': current_page
        }
        
        return self._make_request('aliexpress.marketing.redefining.getpromotionlist', params)
    
    def create_promotion(self, promotion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create promotion"""
        params = {
            'promotion_info': json.dumps(promotion_data)
        }
        
        return self._make_request('aliexpress.marketing.redefining.createpromotion', params)
    
    # Analytics & Reports
    def get_product_analytics(self, product_id: str, start_date: str, 
                            end_date: str) -> Dict[str, Any]:
        """Get product analytics"""
        params = {
            'product_id': product_id,
            'start_date': start_date,
            'end_date': end_date
        }
        
        return self._make_request('aliexpress.data.redefining.queryproductanalysisdata', params)
    
    def get_store_analytics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get store analytics"""
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        return self._make_request('aliexpress.data.redefining.querystoreanalysisdata', params)
    
    # Utility Methods
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        try:
            result = self.get_store_info()
            return 'aliexpress_merchant_redefining_querysellerinfo_response' in result
        except:
            return False
    
    def get_supported_countries(self) -> Dict[str, Any]:
        """Get supported countries for shipping"""
        return self._make_request('aliexpress.logistics.redefining.getlogisticssellershippinginfo', {})
    
    def get_freight_template(self, template_id: str = None) -> Dict[str, Any]:
        """Get freight template"""
        params = {}
        if template_id:
            params['template_id'] = template_id
        
        return self._make_request('aliexpress.freight.redefining.getfreightsettingbytemplateid', params)

# Test function
def test_aliexpress_api():
    """Test AliExpress API functionality"""
    api = AliExpressMarketplaceAPI(
        app_key="test_key",
        app_secret="test_secret",
        sandbox=True
    )
    
    print("AliExpress API initialized successfully")
    return api

if __name__ == "__main__":
    test_aliexpress_api()