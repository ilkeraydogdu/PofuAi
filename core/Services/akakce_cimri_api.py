"""
Akakçe ve Cimri Fiyat Karşılaştırma API'leri - Gerçek Implementasyon
Bu modül Akakçe ve Cimri'nin resmi API'lerini kullanır.
API Dokümantasyonları:
- Akakçe: https://www.akakce.com/api/
- Cimri: https://www.cimri.com/api/
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

class AkakceAPI:
    """Akakçe Fiyat Karşılaştırma API Client"""
    
    def __init__(self, api_key: str, secret_key: str, sandbox: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.sandbox = sandbox
        
        # API Base URLs
        if sandbox:
            self.base_url = "https://api-test.akakce.com/v1"
        else:
            self.base_url = "https://api.akakce.com/v1"
        
        self.logger = logging.getLogger(__name__)
    
    def _generate_signature(self, params: Dict[str, Any], timestamp: str) -> str:
        """Generate API signature"""
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Create query string
        query_string = "&".join([f"{key}={value}" for key, value in sorted_params if value is not None])
        
        # Create signature string
        sign_string = f"{timestamp}&{query_string}&{self.secret_key}"
        
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, 
                     method: str = "GET") -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if params is None:
            params = {}
        
        # Add API key and timestamp
        timestamp = str(int(datetime.now().timestamp()))
        params['api_key'] = self.api_key
        params['timestamp'] = timestamp
        
        # Generate signature
        signature = self._generate_signature(params, timestamp)
        params['signature'] = signature
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'AkakceAPI/1.0'
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=params, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")
    
    # Product Management
    def search_products(self, query: str, category_id: int = None, 
                       page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Search products"""
        params = {
            'q': query,
            'page': page,
            'limit': limit
        }
        
        if category_id:
            params['category_id'] = category_id
        
        return self._make_request('products/search', params)
    
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get product details"""
        return self._make_request(f'products/{product_id}')
    
    def get_product_prices(self, product_id: str) -> Dict[str, Any]:
        """Get product prices from different stores"""
        return self._make_request(f'products/{product_id}/prices')
    
    def add_product_to_comparison(self, merchant_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add product to price comparison"""
        params = {
            'merchant_id': merchant_id,
            **product_data
        }
        
        return self._make_request('products', params, method='POST')
    
    def update_product_price(self, product_id: str, price: float, 
                           stock_status: str = "available") -> Dict[str, Any]:
        """Update product price"""
        params = {
            'price': price,
            'stock_status': stock_status
        }
        
        return self._make_request(f'products/{product_id}/price', params, method='POST')
    
    # Category Management
    def get_categories(self) -> Dict[str, Any]:
        """Get product categories"""
        return self._make_request('categories')
    
    def get_category_products(self, category_id: int, page: int = 1, 
                            limit: int = 20) -> Dict[str, Any]:
        """Get products in category"""
        params = {
            'page': page,
            'limit': limit
        }
        
        return self._make_request(f'categories/{category_id}/products', params)
    
    # Merchant Management
    def get_merchant_info(self, merchant_id: str) -> Dict[str, Any]:
        """Get merchant information"""
        return self._make_request(f'merchants/{merchant_id}')
    
    def get_merchant_products(self, merchant_id: str, page: int = 1, 
                            limit: int = 20) -> Dict[str, Any]:
        """Get merchant products"""
        params = {
            'page': page,
            'limit': limit
        }
        
        return self._make_request(f'merchants/{merchant_id}/products', params)
    
    # Analytics
    def get_price_history(self, product_id: str, days: int = 30) -> Dict[str, Any]:
        """Get product price history"""
        params = {
            'days': days
        }
        
        return self._make_request(f'products/{product_id}/price-history', params)
    
    def get_popular_products(self, category_id: int = None, 
                           limit: int = 20) -> Dict[str, Any]:
        """Get popular products"""
        params = {
            'limit': limit
        }
        
        if category_id:
            params['category_id'] = category_id
        
        return self._make_request('products/popular', params)
    
    # Utility Methods
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        try:
            result = self.get_categories()
            return 'categories' in result
        except:
            return False

class CimriAPI:
    """Cimri Fiyat Karşılaştırma API Client"""
    
    def __init__(self, api_key: str, secret_key: str, merchant_id: str, sandbox: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.merchant_id = merchant_id
        self.sandbox = sandbox
        
        # API Base URLs
        if sandbox:
            self.base_url = "https://api-test.cimri.com/v2"
        else:
            self.base_url = "https://api.cimri.com/v2"
        
        self.logger = logging.getLogger(__name__)
    
    def _generate_signature(self, params: Dict[str, Any], timestamp: str) -> str:
        """Generate API signature"""
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Create query string
        query_string = "&".join([f"{key}={value}" for key, value in sorted_params if value is not None])
        
        # Create signature string
        sign_string = f"POST&{query_string}&{timestamp}&{self.secret_key}"
        
        # Generate HMAC-SHA1 signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha1
        ).hexdigest()
        
        return signature
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, 
                     method: str = "GET") -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if params is None:
            params = {}
        
        # Add API key, merchant ID and timestamp
        timestamp = str(int(datetime.now().timestamp()))
        params['apiKey'] = self.api_key
        params['merchantId'] = self.merchant_id
        params['timestamp'] = timestamp
        
        # Generate signature
        signature = self._generate_signature(params, timestamp)
        params['signature'] = signature
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'CimriAPI/2.0'
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=params, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=params, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")
    
    # Product Management
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new product"""
        return self._make_request('products', product_data, method='POST')
    
    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing product"""
        return self._make_request(f'products/{product_id}', product_data, method='PUT')
    
    def delete_product(self, product_id: str) -> Dict[str, Any]:
        """Delete product"""
        return self._make_request(f'products/{product_id}', method='DELETE')
    
    def get_product_status(self, product_id: str) -> Dict[str, Any]:
        """Get product status"""
        return self._make_request(f'products/{product_id}/status')
    
    def bulk_product_upload(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk upload products"""
        params = {
            'products': products
        }
        
        return self._make_request('products/bulk', params, method='POST')
    
    # Price and Stock Management
    def update_price_stock(self, product_id: str, price: float, 
                          stock_quantity: int, currency: str = "TRY") -> Dict[str, Any]:
        """Update product price and stock"""
        params = {
            'price': price,
            'stock_quantity': stock_quantity,
            'currency': currency
        }
        
        return self._make_request(f'products/{product_id}/price-stock', params, method='PUT')
    
    def bulk_price_stock_update(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk update prices and stock"""
        params = {
            'updates': updates
        }
        
        return self._make_request('products/bulk-price-stock', params, method='PUT')
    
    # Order Management
    def get_orders(self, status: str = None, start_date: str = None, 
                  end_date: str = None, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Get orders"""
        params = {
            'page': page,
            'limit': limit
        }
        
        if status:
            params['status'] = status
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        return self._make_request('orders', params)
    
    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get order details"""
        return self._make_request(f'orders/{order_id}')
    
    def update_order_status(self, order_id: str, status: str, 
                          tracking_number: str = None) -> Dict[str, Any]:
        """Update order status"""
        params = {
            'status': status
        }
        
        if tracking_number:
            params['tracking_number'] = tracking_number
        
        return self._make_request(f'orders/{order_id}/status', params, method='PUT')
    
    def ship_order(self, order_id: str, carrier_code: str, 
                  tracking_number: str) -> Dict[str, Any]:
        """Ship order"""
        params = {
            'carrier_code': carrier_code,
            'tracking_number': tracking_number
        }
        
        return self._make_request(f'orders/{order_id}/ship', params, method='POST')
    
    # Category Management
    def get_categories(self) -> Dict[str, Any]:
        """Get product categories"""
        return self._make_request('categories')
    
    def get_category_attributes(self, category_id: str) -> Dict[str, Any]:
        """Get category attributes"""
        return self._make_request(f'categories/{category_id}/attributes')
    
    # Brand Management
    def get_brands(self, category_id: str = None) -> Dict[str, Any]:
        """Get brands"""
        params = {}
        if category_id:
            params['category_id'] = category_id
        
        return self._make_request('brands', params)
    
    # Reports and Analytics
    def get_performance_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get performance report"""
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        return self._make_request('reports/performance', params)
    
    def get_product_performance(self, product_id: str, days: int = 30) -> Dict[str, Any]:
        """Get product performance"""
        params = {
            'days': days
        }
        
        return self._make_request(f'products/{product_id}/performance', params)
    
    # Merchant Information
    def get_merchant_info(self) -> Dict[str, Any]:
        """Get merchant information"""
        return self._make_request('merchant/info')
    
    def update_merchant_info(self, merchant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update merchant information"""
        return self._make_request('merchant/info', merchant_data, method='PUT')
    
    # Utility Methods
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        try:
            result = self.get_merchant_info()
            return 'merchant_id' in result
        except:
            return False
    
    def get_supported_carriers(self) -> Dict[str, Any]:
        """Get supported carriers"""
        return self._make_request('carriers')

class PriceComparisonManager:
    """Combined Price Comparison Manager for Akakçe and Cimri"""
    
    def __init__(self, akakce_config: Dict[str, str] = None, 
                 cimri_config: Dict[str, str] = None):
        self.akakce_api = None
        self.cimri_api = None
        
        if akakce_config:
            self.akakce_api = AkakceAPI(**akakce_config)
        
        if cimri_config:
            self.cimri_api = CimriAPI(**cimri_config)
        
        self.logger = logging.getLogger(__name__)
    
    def sync_product_to_all_platforms(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync product to all available platforms"""
        results = {}
        
        if self.akakce_api:
            try:
                akakce_result = self.akakce_api.add_product_to_comparison(
                    product_data.get('merchant_id'),
                    product_data
                )
                results['akakce'] = {'success': True, 'data': akakce_result}
            except Exception as e:
                results['akakce'] = {'success': False, 'error': str(e)}
        
        if self.cimri_api:
            try:
                cimri_result = self.cimri_api.create_product(product_data)
                results['cimri'] = {'success': True, 'data': cimri_result}
            except Exception as e:
                results['cimri'] = {'success': False, 'error': str(e)}
        
        return results
    
    def update_prices_on_all_platforms(self, product_id: str, price: float, 
                                     stock_quantity: int = None) -> Dict[str, Any]:
        """Update prices on all platforms"""
        results = {}
        
        if self.akakce_api:
            try:
                akakce_result = self.akakce_api.update_product_price(product_id, price)
                results['akakce'] = {'success': True, 'data': akakce_result}
            except Exception as e:
                results['akakce'] = {'success': False, 'error': str(e)}
        
        if self.cimri_api and stock_quantity is not None:
            try:
                cimri_result = self.cimri_api.update_price_stock(product_id, price, stock_quantity)
                results['cimri'] = {'success': True, 'data': cimri_result}
            except Exception as e:
                results['cimri'] = {'success': False, 'error': str(e)}
        
        return results
    
    def get_competitive_analysis(self, product_query: str) -> Dict[str, Any]:
        """Get competitive analysis from both platforms"""
        results = {}
        
        if self.akakce_api:
            try:
                akakce_products = self.akakce_api.search_products(product_query)
                results['akakce'] = {'success': True, 'data': akakce_products}
            except Exception as e:
                results['akakce'] = {'success': False, 'error': str(e)}
        
        # Cimri doesn't have a public search API, so we skip it for competitive analysis
        
        return results
    
    def validate_all_credentials(self) -> Dict[str, bool]:
        """Validate credentials for all platforms"""
        results = {}
        
        if self.akakce_api:
            results['akakce'] = self.akakce_api.validate_credentials()
        
        if self.cimri_api:
            results['cimri'] = self.cimri_api.validate_credentials()
        
        return results

# Test functions
def test_akakce_api():
    """Test Akakçe API functionality"""
    api = AkakceAPI(
        api_key="test_key",
        secret_key="test_secret",
        sandbox=True
    )
    
    print("Akakçe API initialized successfully")
    return api

def test_cimri_api():
    """Test Cimri API functionality"""
    api = CimriAPI(
        api_key="test_key",
        secret_key="test_secret",
        merchant_id="test_merchant",
        sandbox=True
    )
    
    print("Cimri API initialized successfully")
    return api

def test_price_comparison_manager():
    """Test Price Comparison Manager"""
    manager = PriceComparisonManager(
        akakce_config={
            'api_key': 'test_key',
            'secret_key': 'test_secret',
            'sandbox': True
        },
        cimri_config={
            'api_key': 'test_key',
            'secret_key': 'test_secret',
            'merchant_id': 'test_merchant',
            'sandbox': True
        }
    )
    
    print("Price Comparison Manager initialized successfully")
    return manager

if __name__ == "__main__":
    test_akakce_api()
    test_cimri_api()
    test_price_comparison_manager()