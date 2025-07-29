"""
Hepsiburada Marketplace API Integration
Full implementation with all features
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import time
from decimal import Decimal
import xml.etree.ElementTree as ET
from xml.dom import minidom

from .base_integration import BaseIntegration, RequestMethod, ValidationError, APIError


class HepsiburadaMarketplaceAPI(BaseIntegration):
    """
    Hepsiburada Marketplace API implementation
    
    Documentation: https://developers.hepsiburada.com/
    """
    
    def _initialize(self):
        """Initialize Hepsiburada specific settings"""
        self.username = self.credentials.get('username')
        self.password = self.credentials.get('password')
        self.merchant_id = self.credentials.get('merchant_id')
        
        if not all([self.username, self.password, self.merchant_id]):
            raise ValueError("Missing required credentials: username, password, merchant_id")
        
        # Set base URLs
        if self.sandbox:
            self.base_url = "https://sandbox-mpop.hepsiburada.com"
        else:
            self.base_url = "https://mpop.hepsiburada.com"
        
        # Hepsiburada specific settings
        self.min_request_interval = 0.5  # 500ms between requests
        
        # Get authentication token
        self._authenticate()
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL for endpoint"""
        return f"{self.base_url}/{endpoint.lstrip('/')}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        return headers
    
    def _authenticate(self):
        """Authenticate and get access token"""
        auth_data = {
            'username': self.username,
            'password': self.password,
            'authenticationType': 'MERCHANT'
        }
        
        response = self.session.post(
            self._build_url('authenticate'),
            json=auth_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get('token')
            self.token_expires = datetime.now() + timedelta(hours=23)  # Token valid for 24 hours
        else:
            raise AuthenticationError(f"Authentication failed: {response.text}")
    
    def _check_token_expiry(self):
        """Check if token is expired and renew if necessary"""
        if datetime.now() >= self.token_expires:
            self._authenticate()
    
    def _test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Get merchant info to test connection
            self.get_merchant_info()
            return True
        except Exception:
            return False
    
    def make_request(self, method: RequestMethod, endpoint: str, 
                    data: Optional[Dict] = None, params: Optional[Dict] = None,
                    headers: Optional[Dict] = None, timeout: int = 30) -> Dict[str, Any]:
        """Override to check token expiry"""
        self._check_token_expiry()
        return super().make_request(method, endpoint, data, params, headers, timeout)
    
    # Merchant Management
    def get_merchant_info(self) -> Dict[str, Any]:
        """Get merchant information"""
        return self.make_request(
            RequestMethod.GET,
            f"merchants/{self.merchant_id}"
        )
    
    def get_merchant_categories(self) -> List[Dict[str, Any]]:
        """Get merchant's approved categories"""
        response = self.make_request(
            RequestMethod.GET,
            f"merchants/{self.merchant_id}/categories"
        )
        return response.get('categories', [])
    
    # Product Management
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product listing
        
        Args:
            product_data: Product information including:
                - merchantSku: Unique SKU
                - varyantGroupID: Variant group ID
                - barcode: Product barcode
                - urunAdi: Product name
                - urunAciklamasi: Product description
                - marka: Brand
                - garantiSuresi: Warranty period
                - kg: Weight
                - tax: Tax rate
                - price: Price
                - stock: Stock quantity
                - productImageUrl: Main image URL
                - categoryId: Category ID
                - attributes: Product attributes
        """
        # Validate required fields
        required_fields = ['merchantSku', 'barcode', 'urunAdi', 'marka', 
                          'price', 'stock', 'categoryId']
        
        for field in required_fields:
            if field not in product_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Create product XML
        xml_data = self._build_product_xml([product_data])
        
        return self.make_request(
            RequestMethod.POST,
            'product/import',
            data={'products': xml_data},
            headers={'Content-Type': 'application/xml'}
        )
    
    def update_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing product"""
        xml_data = self._build_product_xml([product_data])
        
        return self.make_request(
            RequestMethod.PUT,
            'product/update',
            data={'products': xml_data},
            headers={'Content-Type': 'application/xml'}
        )
    
    def get_products(self, 
                    offset: int = 0,
                    limit: int = 100,
                    merchant_sku: Optional[str] = None,
                    barcode: Optional[str] = None) -> Dict[str, Any]:
        """
        Get products with filters
        
        Args:
            offset: Pagination offset
            limit: Number of results (max 100)
            merchant_sku: Filter by SKU
            barcode: Filter by barcode
        """
        params = {
            'offset': offset,
            'limit': min(limit, 100)
        }
        
        if merchant_sku:
            params['merchantSku'] = merchant_sku
        if barcode:
            params['barcode'] = barcode
        
        return self.make_request(
            RequestMethod.GET,
            'listings/merchantid/{self.merchant_id}',
            params=params
        )
    
    def update_stock_and_price(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update stock and price for multiple products
        
        Args:
            updates: List of updates containing:
                - merchantSku or hbSku: Product identifier
                - stock: New stock quantity
                - price: New price
        """
        xml_data = self._build_stock_price_xml(updates)
        
        return self.make_request(
            RequestMethod.POST,
            'stock-price/update',
            data={'updates': xml_data},
            headers={'Content-Type': 'application/xml'}
        )
    
    def activate_products(self, skus: List[str]) -> Dict[str, Any]:
        """Activate products by SKU"""
        data = {
            'merchantId': self.merchant_id,
            'skus': skus
        }
        
        return self.make_request(
            RequestMethod.POST,
            'listings/activate',
            data=data
        )
    
    def deactivate_products(self, skus: List[str]) -> Dict[str, Any]:
        """Deactivate products by SKU"""
        data = {
            'merchantId': self.merchant_id,
            'skus': skus
        }
        
        return self.make_request(
            RequestMethod.POST,
            'listings/deactivate',
            data=data
        )
    
    # Category Management
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        response = self.make_request(
            RequestMethod.GET,
            'categories'
        )
        return response.get('categories', [])
    
    def get_category_attributes(self, category_id: str) -> List[Dict[str, Any]]:
        """Get attributes for a specific category"""
        response = self.make_request(
            RequestMethod.GET,
            f'categories/{category_id}/attributes'
        )
        return response.get('attributes', [])
    
    def get_category_commission(self, category_id: str) -> Dict[str, Any]:
        """Get commission rates for a category"""
        return self.make_request(
            RequestMethod.GET,
            f'categories/{category_id}/commission'
        )
    
    # Order Management
    def get_orders(self,
                   status: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   offset: int = 0,
                   limit: int = 100) -> Dict[str, Any]:
        """
        Get orders with filters
        
        Args:
            status: Order status (Open, Delivered, Cancelled, etc.)
            start_date: Start date filter
            end_date: End date filter
            offset: Pagination offset
            limit: Number of results
        """
        params = {
            'merchantId': self.merchant_id,
            'offset': offset,
            'limit': min(limit, 100)
        }
        
        if status:
            params['status'] = status
        if start_date:
            params['beginDate'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['endDate'] = end_date.strftime('%Y-%m-%d')
        
        return self.make_request(
            RequestMethod.GET,
            'orders',
            params=params
        )
    
    def get_order_details(self, order_number: str) -> Dict[str, Any]:
        """Get detailed order information"""
        return self.make_request(
            RequestMethod.GET,
            f'orders/{order_number}'
        )
    
    def package_items(self, package_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create package for order items
        
        Args:
            package_data: Package information including:
                - orderNumber: Order number
                - items: List of items to package
                - parcelQuantity: Number of parcels
        """
        return self.make_request(
            RequestMethod.POST,
            'packages/create',
            data=package_data
        )
    
    def update_tracking_number(self, package_number: str, 
                             tracking_number: str,
                             shipping_company: str) -> Dict[str, Any]:
        """Update package tracking information"""
        data = {
            'trackingNumber': tracking_number,
            'shippingCompany': shipping_company
        }
        
        return self.make_request(
            RequestMethod.PUT,
            f'packages/{package_number}/tracking',
            data=data
        )
    
    def mark_as_shipped(self, package_number: str) -> Dict[str, Any]:
        """Mark package as shipped"""
        return self.make_request(
            RequestMethod.PUT,
            f'packages/{package_number}/shipped'
        )
    
    def cancel_order(self, order_number: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Cancel order items
        
        Args:
            order_number: Order number
            items: List of items to cancel with reasons
        """
        data = {
            'orderNumber': order_number,
            'items': items
        }
        
        return self.make_request(
            RequestMethod.POST,
            'orders/cancel',
            data=data
        )
    
    # Returns Management
    def get_returns(self,
                   status: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   offset: int = 0,
                   limit: int = 100) -> Dict[str, Any]:
        """Get return requests"""
        params = {
            'merchantId': self.merchant_id,
            'offset': offset,
            'limit': min(limit, 100)
        }
        
        if status:
            params['status'] = status
        if start_date:
            params['beginDate'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['endDate'] = end_date.strftime('%Y-%m-%d')
        
        return self.make_request(
            RequestMethod.GET,
            'returns',
            params=params
        )
    
    def approve_return(self, return_id: str) -> Dict[str, Any]:
        """Approve return request"""
        return self.make_request(
            RequestMethod.PUT,
            f'returns/{return_id}/approve'
        )
    
    def reject_return(self, return_id: str, reason: str) -> Dict[str, Any]:
        """Reject return request"""
        data = {'reason': reason}
        
        return self.make_request(
            RequestMethod.PUT,
            f'returns/{return_id}/reject',
            data=data
        )
    
    # Claims Management
    def get_claims(self,
                   status: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   offset: int = 0,
                   limit: int = 100) -> Dict[str, Any]:
        """Get claim requests"""
        params = {
            'merchantId': self.merchant_id,
            'offset': offset,
            'limit': min(limit, 100)
        }
        
        if status:
            params['status'] = status
        if start_date:
            params['beginDate'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['endDate'] = end_date.strftime('%Y-%m-%d')
        
        return self.make_request(
            RequestMethod.GET,
            'claims',
            params=params
        )
    
    def respond_to_claim(self, claim_id: str, response: str) -> Dict[str, Any]:
        """Respond to a claim"""
        data = {'response': response}
        
        return self.make_request(
            RequestMethod.POST,
            f'claims/{claim_id}/respond',
            data=data
        )
    
    # Finance & Reporting
    def get_financial_transactions(self,
                                 transaction_type: Optional[str] = None,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None,
                                 offset: int = 0,
                                 limit: int = 100) -> Dict[str, Any]:
        """Get financial transactions"""
        params = {
            'merchantId': self.merchant_id,
            'offset': offset,
            'limit': min(limit, 100)
        }
        
        if transaction_type:
            params['transactionType'] = transaction_type
        if start_date:
            params['beginDate'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['endDate'] = end_date.strftime('%Y-%m-%d')
        
        return self.make_request(
            RequestMethod.GET,
            'finance/transactions',
            params=params
        )
    
    def get_invoice_details(self, invoice_number: str) -> Dict[str, Any]:
        """Get invoice details"""
        return self.make_request(
            RequestMethod.GET,
            f'finance/invoices/{invoice_number}'
        )
    
    # Cargo Management
    def get_cargo_companies(self) -> List[Dict[str, Any]]:
        """Get available cargo companies"""
        response = self.make_request(
            RequestMethod.GET,
            'cargo-companies'
        )
        return response.get('companies', [])
    
    def create_cargo_label(self, package_number: str) -> bytes:
        """Get cargo label for package"""
        response = self.session.get(
            self._build_url(f'packages/{package_number}/label'),
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.content
    
    # Batch Operations
    def batch_update_products(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Batch update multiple products"""
        return self.batch_operation(
            items=products,
            operation_function=lambda batch: self.update_product({'products': batch}),
            batch_size=50,
            delay_between_batches=1.0
        )
    
    def batch_update_stock_price(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Batch update stock and prices"""
        return self.batch_operation(
            items=updates,
            operation_function=lambda batch: self.update_stock_and_price(batch),
            batch_size=100,
            delay_between_batches=0.5
        )
    
    # Helper Methods
    def _build_product_xml(self, products: List[Dict[str, Any]]) -> str:
        """Build product XML for API"""
        root = ET.Element('products')
        
        for product in products:
            prod_elem = ET.SubElement(root, 'product')
            
            # Add product fields
            for field, value in product.items():
                if field == 'attributes':
                    attrs_elem = ET.SubElement(prod_elem, 'attributes')
                    for attr in value:
                        attr_elem = ET.SubElement(attrs_elem, 'attribute')
                        attr_elem.set('name', attr['name'])
                        attr_elem.text = str(attr['value'])
                elif field == 'images':
                    images_elem = ET.SubElement(prod_elem, 'images')
                    for idx, image_url in enumerate(value):
                        img_elem = ET.SubElement(images_elem, 'image')
                        img_elem.set('order', str(idx))
                        img_elem.text = image_url
                else:
                    elem = ET.SubElement(prod_elem, field)
                    elem.text = str(value)
        
        return self._prettify_xml(root)
    
    def _build_stock_price_xml(self, updates: List[Dict[str, Any]]) -> str:
        """Build stock/price update XML"""
        root = ET.Element('stockPriceUpdates')
        
        for update in updates:
            update_elem = ET.SubElement(root, 'update')
            for field, value in update.items():
                elem = ET.SubElement(update_elem, field)
                elem.text = str(value)
        
        return self._prettify_xml(root)
    
    def _prettify_xml(self, elem) -> str:
        """Return a pretty-printed XML string"""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products using pagination"""
        all_products = []
        offset = 0
        limit = 100
        
        while True:
            response = self.get_products(offset=offset, limit=limit)
            products = response.get('listings', [])
            
            if not products:
                break
            
            all_products.extend(products)
            
            if len(products) < limit:
                break
            
            offset += limit
        
        return all_products
    
    def get_all_orders(self, status: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get all orders using pagination"""
        all_orders = []
        offset = 0
        limit = 100
        
        while True:
            response = self.get_orders(
                status=status,
                start_date=start_date,
                end_date=end_date,
                offset=offset,
                limit=limit
            )
            orders = response.get('orders', [])
            
            if not orders:
                break
            
            all_orders.extend(orders)
            
            if len(orders) < limit:
                break
            
            offset += limit
        
        return all_orders
    
    def calculate_commission(self, category_id: str, price: Decimal) -> Decimal:
        """Calculate commission for a product"""
        commission_info = self.get_category_commission(category_id)
        commission_rate = Decimal(str(commission_info.get('rate', 0.18)))  # Default 18%
        return price * commission_rate
    
    def format_product_for_hepsiburada(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format product data for Hepsiburada API"""
        formatted = {
            'merchantSku': product_data.get('sku'),
            'barcode': product_data.get('barcode'),
            'urunAdi': product_data.get('name'),
            'urunAciklamasi': product_data.get('description', ''),
            'marka': product_data.get('brand'),
            'garantiSuresi': product_data.get('warranty_period', 24),  # Default 24 months
            'kg': product_data.get('weight', 1),
            'tax': product_data.get('vat_rate', 18),
            'price': float(product_data.get('price', 0)),
            'stock': product_data.get('stock', 0),
            'categoryId': product_data.get('category_id'),
            'productImageUrl': product_data.get('main_image', ''),
            'images': product_data.get('images', []),
            'attributes': []
        }
        
        # Add attributes
        if 'attributes' in product_data:
            for attr_name, attr_value in product_data['attributes'].items():
                formatted['attributes'].append({
                    'name': attr_name,
                    'value': attr_value
                })
        
        return formatted


def test_hepsiburada_api():
    """Test Hepsiburada API functionality"""
    print("Testing Hepsiburada Marketplace API...")
    
    # Test credentials (these should come from environment variables)
    credentials = {
        'username': 'YOUR_USERNAME',
        'password': 'YOUR_PASSWORD',
        'merchant_id': 'YOUR_MERCHANT_ID'
    }
    
    try:
        # Initialize API
        api = HepsiburadaMarketplaceAPI(credentials, sandbox=True)
        
        # Test connection
        if api.validate_credentials():
            print("✅ Connection successful!")
            
            # Get merchant info
            merchant_info = api.get_merchant_info()
            print(f"✅ Merchant: {merchant_info.get('merchantName')}")
            
            # Get categories
            categories = api.get_categories()
            print(f"✅ Found {len(categories)} categories")
            
            # Get cargo companies
            cargo_companies = api.get_cargo_companies()
            print(f"✅ Found {len(cargo_companies)} cargo companies")
            
        else:
            print("❌ Authentication failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_hepsiburada_api()