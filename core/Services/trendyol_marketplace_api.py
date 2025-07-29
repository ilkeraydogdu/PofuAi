"""
Trendyol Marketplace API Integration
Full implementation with all features
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import base64
import time
from decimal import Decimal

from .base_integration import BaseIntegration, RequestMethod, ValidationError, APIError


class TrendyolMarketplaceAPI(BaseIntegration):
    """
    Trendyol Marketplace API implementation
    
    Documentation: https://developers.trendyol.com/
    """
    
    def _initialize(self):
        """Initialize Trendyol specific settings"""
        self.api_key = self.credentials.get('api_key')
        self.api_secret = self.credentials.get('api_secret')
        self.supplier_id = self.credentials.get('supplier_id')
        
        if not all([self.api_key, self.api_secret, self.supplier_id]):
            raise ValueError("Missing required credentials: api_key, api_secret, supplier_id")
        
        # Set base URLs
        if self.sandbox:
            self.base_url = "https://stageapi.trendyol.com/stageapigw"
        else:
            self.base_url = "https://api.trendyol.com/sapigw"
        
        # Trendyol specific rate limits
        self.min_request_interval = 0.2  # 200ms between requests
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL for endpoint"""
        return f"{self.base_url}/{endpoint.lstrip('/')}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        # Basic auth for Trendyol
        auth_string = f"{self.api_key}:{self.api_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        return {
            'Authorization': f'Basic {auth_b64}',
            'User-Agent': f'{self.supplier_id} - MarketplaceIntegration',
            'Content-Type': 'application/json'
        }
    
    def _test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Get supplier info to test connection
            self.get_supplier_info()
            return True
        except Exception:
            return False
    
    # Supplier Management
    def get_supplier_info(self) -> Dict[str, Any]:
        """Get supplier information"""
        return self.make_request(
            RequestMethod.GET,
            f"suppliers/{self.supplier_id}"
        )
    
    def get_supplier_addresses(self) -> List[Dict[str, Any]]:
        """Get supplier addresses"""
        response = self.make_request(
            RequestMethod.GET,
            f"suppliers/{self.supplier_id}/addresses"
        )
        return response.get('supplierAddresses', [])
    
    # Product Management
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product
        
        Args:
            product_data: Product information including:
                - barcode: Product barcode
                - title: Product title
                - productMainId: Main product ID
                - brandId: Brand ID
                - categoryId: Category ID
                - quantity: Stock quantity
                - stockCode: Stock code
                - dimensionalWeight: Weight in grams
                - description: Product description
                - currencyType: Currency (TRY)
                - listPrice: List price
                - salePrice: Sale price
                - vatRate: VAT rate (0, 1, 8, 18)
                - cargoCompanyId: Cargo company ID
                - images: List of image objects
                - attributes: List of attribute objects
        """
        # Validate required fields
        required_fields = ['barcode', 'title', 'productMainId', 'brandId', 
                          'categoryId', 'quantity', 'stockCode', 'listPrice', 
                          'salePrice', 'cargoCompanyId']
        
        for field in required_fields:
            if field not in product_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Create product batch request
        batch_request = {
            "items": [product_data]
        }
        
        return self.make_request(
            RequestMethod.POST,
            f"suppliers/{self.supplier_id}/v2/products",
            data=batch_request
        )
    
    def update_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing product"""
        batch_request = {
            "items": [product_data]
        }
        
        return self.make_request(
            RequestMethod.PUT,
            f"suppliers/{self.supplier_id}/v2/products",
            data=batch_request
        )
    
    def get_products(self, 
                    page: int = 0,
                    size: int = 50,
                    approved: Optional[bool] = None,
                    barcode: Optional[str] = None,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get products with filters
        
        Args:
            page: Page number (0-based)
            size: Page size (max 200)
            approved: Filter by approval status
            barcode: Filter by barcode
            start_date: Filter by creation date start
            end_date: Filter by creation date end
        """
        params = {
            'page': page,
            'size': min(size, 200)
        }
        
        if approved is not None:
            params['approved'] = str(approved).lower()
        if barcode:
            params['barcode'] = barcode
        if start_date:
            params['startDate'] = int(start_date.timestamp() * 1000)
        if end_date:
            params['endDate'] = int(end_date.timestamp() * 1000)
        
        return self.make_request(
            RequestMethod.GET,
            f"suppliers/{self.supplier_id}/products",
            params=params
        )
    
    def get_product_by_barcode(self, barcode: str) -> Dict[str, Any]:
        """Get single product by barcode"""
        products = self.get_products(barcode=barcode)
        if products.get('content'):
            return products['content'][0]
        raise APIError(f"Product not found: {barcode}")
    
    def update_price_and_stock(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update price and stock for multiple products
        
        Args:
            updates: List of updates, each containing:
                - barcode: Product barcode
                - quantity: New stock quantity (optional)
                - salePrice: New sale price (optional)
                - listPrice: New list price (optional)
        """
        batch_request = {
            "items": updates
        }
        
        return self.make_request(
            RequestMethod.POST,
            f"suppliers/{self.supplier_id}/products/price-and-inventory",
            data=batch_request
        )
    
    def delete_products(self, barcodes: List[str]) -> Dict[str, Any]:
        """Delete products by barcode"""
        batch_request = {
            "items": [{"barcode": barcode} for barcode in barcodes]
        }
        
        return self.make_request(
            RequestMethod.DELETE,
            f"suppliers/{self.supplier_id}/products",
            data=batch_request
        )
    
    # Category & Brand Management
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        response = self.make_request(
            RequestMethod.GET,
            "product-categories"
        )
        return response.get('categories', [])
    
    def get_category_attributes(self, category_id: int) -> List[Dict[str, Any]]:
        """Get attributes for a specific category"""
        response = self.make_request(
            RequestMethod.GET,
            f"product-categories/{category_id}/attributes"
        )
        return response.get('categoryAttributes', [])
    
    def get_brands(self, name: Optional[str] = None, 
                   page: int = 0, 
                   size: int = 50) -> Dict[str, Any]:
        """Get brands with optional name filter"""
        params = {
            'page': page,
            'size': min(size, 200)
        }
        if name:
            params['name'] = name
        
        return self.make_request(
            RequestMethod.GET,
            "brands",
            params=params
        )
    
    def get_brands_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Search brands by name"""
        response = self.make_request(
            RequestMethod.GET,
            f"brands/by-name",
            params={'name': name}
        )
        return response.get('brands', [])
    
    # Order Management
    def get_orders(self,
                   status: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   page: int = 0,
                   size: int = 50) -> Dict[str, Any]:
        """
        Get orders with filters
        
        Args:
            status: Order status (Created, Picking, Invoiced, Shipped, Cancelled, etc.)
            start_date: Start date filter
            end_date: End date filter
            page: Page number
            size: Page size (max 200)
        """
        params = {
            'page': page,
            'size': min(size, 200)
        }
        
        if status:
            params['status'] = status
        if start_date:
            params['startDate'] = int(start_date.timestamp() * 1000)
        if end_date:
            params['endDate'] = int(end_date.timestamp() * 1000)
        
        return self.make_request(
            RequestMethod.GET,
            f"suppliers/{self.supplier_id}/orders",
            params=params
        )
    
    def get_order_by_number(self, order_number: str) -> Dict[str, Any]:
        """Get single order by order number"""
        orders = self.get_orders()
        for order in orders.get('content', []):
            if order.get('orderNumber') == order_number:
                return order
        raise APIError(f"Order not found: {order_number}")
    
    def update_order_status(self, order_number: str, status: str, 
                           params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update order status
        
        Args:
            order_number: Order number
            status: New status (Picking, Invoiced, Shipped, etc.)
            params: Additional parameters like invoiceNumber, trackingNumber
        """
        data = params or {}
        
        # Status-specific endpoints
        if status == "Picking":
            endpoint = f"suppliers/{self.supplier_id}/orders/{order_number}/in-progress"
        elif status == "Invoiced":
            endpoint = f"suppliers/{self.supplier_id}/orders/{order_number}/invoiced"
        elif status == "Shipped":
            endpoint = f"suppliers/{self.supplier_id}/orders/{order_number}/shipped"
        elif status == "Cancelled":
            endpoint = f"suppliers/{self.supplier_id}/orders/{order_number}/cancel"
        else:
            raise ValidationError(f"Invalid order status: {status}")
        
        return self.make_request(
            RequestMethod.PUT,
            endpoint,
            data=data
        )
    
    def split_order_packages(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Split order into multiple packages"""
        return self.make_request(
            RequestMethod.POST,
            f"suppliers/{self.supplier_id}/orders/split-packages",
            data=order_data
        )
    
    # Shipment & Cargo Management
    def get_shipment_providers(self) -> List[Dict[str, Any]]:
        """Get available shipment providers"""
        response = self.make_request(
            RequestMethod.GET,
            "shipment-providers"
        )
        return response.get('content', [])
    
    def create_cargo_label(self, cargo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create cargo label for shipment"""
        return self.make_request(
            RequestMethod.POST,
            f"suppliers/{self.supplier_id}/cargo-labels",
            data=cargo_data
        )
    
    def get_cargo_label(self, cargo_tracking_number: str) -> bytes:
        """Get cargo label PDF"""
        response = self.session.get(
            self._build_url(f"suppliers/{self.supplier_id}/cargo-labels/{cargo_tracking_number}"),
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.content
    
    # Returns & Claims
    def get_returns(self,
                   status: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   page: int = 0,
                   size: int = 50) -> Dict[str, Any]:
        """Get return requests"""
        params = {
            'page': page,
            'size': min(size, 200)
        }
        
        if status:
            params['status'] = status
        if start_date:
            params['startDate'] = int(start_date.timestamp() * 1000)
        if end_date:
            params['endDate'] = int(end_date.timestamp() * 1000)
        
        return self.make_request(
            RequestMethod.GET,
            f"suppliers/{self.supplier_id}/returns",
            params=params
        )
    
    def approve_return(self, return_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Approve return request"""
        return self.make_request(
            RequestMethod.PUT,
            f"suppliers/{self.supplier_id}/returns/{return_id}/approve",
            data=params
        )
    
    def reject_return(self, return_id: str, reject_reason: str) -> Dict[str, Any]:
        """Reject return request"""
        return self.make_request(
            RequestMethod.PUT,
            f"suppliers/{self.supplier_id}/returns/{return_id}/reject",
            data={"rejectReason": reject_reason}
        )
    
    def get_claims(self,
                   status: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   page: int = 0,
                   size: int = 50) -> Dict[str, Any]:
        """Get claim requests"""
        params = {
            'page': page,
            'size': min(size, 200)
        }
        
        if status:
            params['status'] = status
        if start_date:
            params['startDate'] = int(start_date.timestamp() * 1000)
        if end_date:
            params['endDate'] = int(end_date.timestamp() * 1000)
        
        return self.make_request(
            RequestMethod.GET,
            f"suppliers/{self.supplier_id}/claims",
            params=params
        )
    
    def approve_claim(self, claim_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Approve claim request"""
        return self.make_request(
            RequestMethod.PUT,
            f"suppliers/{self.supplier_id}/claims/{claim_id}/approve",
            data=params
        )
    
    # Questions & Answers
    def get_questions(self,
                     status: Optional[str] = None,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     page: int = 0,
                     size: int = 50) -> Dict[str, Any]:
        """Get product questions"""
        params = {
            'page': page,
            'size': min(size, 200)
        }
        
        if status:
            params['status'] = status
        if start_date:
            params['startDate'] = int(start_date.timestamp() * 1000)
        if end_date:
            params['endDate'] = int(end_date.timestamp() * 1000)
        
        return self.make_request(
            RequestMethod.GET,
            f"suppliers/{self.supplier_id}/questions",
            params=params
        )
    
    def answer_question(self, question_id: str, answer: str) -> Dict[str, Any]:
        """Answer a product question"""
        return self.make_request(
            RequestMethod.POST,
            f"suppliers/{self.supplier_id}/questions/{question_id}/answer",
            data={"answer": answer}
        )
    
    # Reporting & Analytics
    def get_settlement_report(self, 
                            start_date: datetime,
                            end_date: datetime,
                            page: int = 0,
                            size: int = 50) -> Dict[str, Any]:
        """Get settlement/payment report"""
        params = {
            'startDate': int(start_date.timestamp() * 1000),
            'endDate': int(end_date.timestamp() * 1000),
            'page': page,
            'size': min(size, 200)
        }
        
        return self.make_request(
            RequestMethod.GET,
            f"suppliers/{self.supplier_id}/settlements",
            params=params
        )
    
    def get_commission_report(self, 
                            start_date: datetime,
                            end_date: datetime) -> Dict[str, Any]:
        """Get commission report"""
        params = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d')
        }
        
        return self.make_request(
            RequestMethod.GET,
            f"suppliers/{self.supplier_id}/commission-report",
            params=params
        )
    
    # Webhook Management
    def create_webhook(self, url: str, events: List[str]) -> Dict[str, Any]:
        """Create webhook subscription"""
        data = {
            "url": url,
            "events": events
        }
        
        return self.make_request(
            RequestMethod.POST,
            f"suppliers/{self.supplier_id}/webhooks",
            data=data
        )
    
    def get_webhooks(self) -> List[Dict[str, Any]]:
        """Get webhook subscriptions"""
        response = self.make_request(
            RequestMethod.GET,
            f"suppliers/{self.supplier_id}/webhooks"
        )
        return response.get('webhooks', [])
    
    def delete_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Delete webhook subscription"""
        return self.make_request(
            RequestMethod.DELETE,
            f"suppliers/{self.supplier_id}/webhooks/{webhook_id}"
        )
    
    # Batch Operations
    def batch_update_products(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Batch update multiple products"""
        return self.batch_operation(
            items=products,
            operation_function=lambda batch: self.update_product({"items": batch}),
            batch_size=100,
            delay_between_batches=1.0
        )
    
    def batch_update_prices(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Batch update prices and stock"""
        return self.batch_operation(
            items=updates,
            operation_function=lambda batch: self.update_price_and_stock(batch),
            batch_size=100,
            delay_between_batches=1.0
        )
    
    # Helper Methods
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products using pagination"""
        return self.paginate_results(
            fetch_function=lambda page, size: self.get_products(page=page, size=size).get('content', []),
            page_size=200
        )
    
    def get_all_orders(self, status: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get all orders using pagination"""
        return self.paginate_results(
            fetch_function=lambda page, size: self.get_orders(
                status=status, 
                start_date=start_date, 
                end_date=end_date,
                page=page, 
                size=size
            ).get('content', []),
            page_size=200
        )
    
    def calculate_commission(self, category_id: int, price: Decimal) -> Decimal:
        """Calculate commission for a product"""
        # This would typically call an API endpoint or use a commission table
        # For now, using a default rate
        commission_rate = Decimal('0.20')  # 20% default
        return price * commission_rate
    
    def format_product_for_trendyol(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format product data for Trendyol API"""
        # Map common fields to Trendyol format
        formatted = {
            'barcode': product_data.get('barcode'),
            'title': product_data.get('name'),
            'productMainId': product_data.get('model_code'),
            'brandId': product_data.get('brand_id'),
            'categoryId': product_data.get('category_id'),
            'quantity': product_data.get('stock', 0),
            'stockCode': product_data.get('sku'),
            'dimensionalWeight': int(product_data.get('weight', 0) * 1000),  # Convert kg to grams
            'description': product_data.get('description', ''),
            'currencyType': 'TRY',
            'listPrice': float(product_data.get('list_price', 0)),
            'salePrice': float(product_data.get('sale_price', 0)),
            'vatRate': product_data.get('vat_rate', 18),
            'cargoCompanyId': product_data.get('cargo_company_id', 10),  # Default cargo
            'images': [],
            'attributes': []
        }
        
        # Add images
        if 'images' in product_data:
            for idx, image_url in enumerate(product_data['images'][:8]):  # Max 8 images
                formatted['images'].append({
                    'url': image_url
                })
        
        # Add attributes
        if 'attributes' in product_data:
            for attr_name, attr_value in product_data['attributes'].items():
                formatted['attributes'].append({
                    'attributeId': attr_name,  # This should be mapped to actual attribute IDs
                    'attributeValueId': attr_value  # This should be mapped to actual value IDs
                })
        
        return formatted


def test_trendyol_api():
    """Test Trendyol API functionality"""
    print("Testing Trendyol Marketplace API...")
    
    # Test credentials (these should come from environment variables)
    credentials = {
        'api_key': 'YOUR_API_KEY',
        'api_secret': 'YOUR_API_SECRET',
        'supplier_id': 'YOUR_SUPPLIER_ID'
    }
    
    try:
        # Initialize API
        api = TrendyolMarketplaceAPI(credentials, sandbox=True)
        
        # Test connection
        if api.validate_credentials():
            print("✅ Connection successful!")
            
            # Get supplier info
            supplier_info = api.get_supplier_info()
            print(f"✅ Supplier: {supplier_info.get('supplierName')}")
            
            # Get categories
            categories = api.get_categories()
            print(f"✅ Found {len(categories)} categories")
            
            # Get brands
            brands = api.get_brands(size=10)
            print(f"✅ Found {brands.get('totalElements', 0)} brands")
            
        else:
            print("❌ Authentication failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_trendyol_api()