"""
PTT AVM Marketplace API Integration
Full implementation with all features
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import hmac
import base64
import time
from decimal import Decimal
import json
import uuid

from .base_integration import BaseIntegration, RequestMethod, ValidationError, APIError, AuthenticationError


class PTTAVMMarketplaceAPI(BaseIntegration):
    """
    PTT AVM Marketplace API implementation
    
    Documentation: https://developer.pttavm.com/
    """
    
    def _initialize(self):
        """Initialize PTT AVM specific settings"""
        self.api_key = self.credentials.get('api_key')
        self.api_secret = self.credentials.get('api_secret')
        self.seller_id = self.credentials.get('seller_id')
        
        if not all([self.api_key, self.api_secret, self.seller_id]):
            raise ValueError("Missing required credentials: api_key, api_secret, seller_id")
        
        # Set base URLs
        if self.sandbox:
            self.base_url = "https://sandbox-api.pttavm.com/v1"
        else:
            self.base_url = "https://api.pttavm.com/v1"
        
        # PTT AVM specific settings
        self.min_request_interval = 0.3  # 300ms between requests
        
        # Session ID for requests
        self.session_id = None
        self.session_expires = datetime.now()
        
        # Get initial session
        self._create_session()
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL for endpoint"""
        return f"{self.base_url}/{endpoint.lstrip('/')}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        self._check_session_expiry()
        
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4())
        
        # Create signature
        signature = self._create_signature(timestamp, nonce)
        
        headers = {
            'X-API-Key': self.api_key,
            'X-Signature': signature,
            'X-Timestamp': timestamp,
            'X-Nonce': nonce,
            'X-Session-Id': self.session_id,
            'X-Seller-Id': self.seller_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        return headers
    
    def _create_signature(self, timestamp: str, nonce: str) -> str:
        """Create HMAC signature for authentication"""
        message = f"{self.api_key}{timestamp}{nonce}{self.seller_id}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _create_session(self):
        """Create a new session"""
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4())
        signature = self._create_signature(timestamp, nonce)
        
        headers = {
            'X-API-Key': self.api_key,
            'X-Signature': signature,
            'X-Timestamp': timestamp,
            'X-Nonce': nonce,
            'Content-Type': 'application/json'
        }
        
        data = {
            'sellerId': self.seller_id
        }
        
        response = self.session.post(
            self._build_url('auth/session'),
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            session_data = response.json()
            self.session_id = session_data['sessionId']
            expires_in = session_data.get('expiresIn', 3600)
            self.session_expires = datetime.now() + timedelta(seconds=expires_in - 60)
        else:
            raise AuthenticationError(f"Failed to create session: {response.text}")
    
    def _check_session_expiry(self):
        """Check if session is expired and renew if necessary"""
        if datetime.now() >= self.session_expires:
            self._create_session()
    
    def _test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Get seller info to test connection
            self.get_seller_info()
            return True
        except Exception:
            return False
    
    # Seller Management
    def get_seller_info(self) -> Dict[str, Any]:
        """Get seller information"""
        return self.make_request(
            RequestMethod.GET,
            f"sellers/{self.seller_id}"
        )
    
    def get_seller_settings(self) -> Dict[str, Any]:
        """Get seller settings"""
        return self.make_request(
            RequestMethod.GET,
            f"sellers/{self.seller_id}/settings"
        )
    
    def update_seller_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update seller settings"""
        return self.make_request(
            RequestMethod.PUT,
            f"sellers/{self.seller_id}/settings",
            data=settings
        )
    
    # Product Management
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product
        
        Args:
            product_data: Product information including:
                - sku: Product SKU
                - title: Product title
                - description: Product description
                - category_id: Category ID
                - brand: Brand name
                - barcode: Product barcode
                - price: Product price
                - stock: Stock quantity
                - images: List of image URLs
                - attributes: Product attributes
                - shipping: Shipping information
        """
        # Validate required fields
        required_fields = ['sku', 'title', 'category_id', 'price', 'stock']
        for field in required_fields:
            if field not in product_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Format product data
        formatted_data = {
            'sellerId': self.seller_id,
            'sku': product_data['sku'],
            'title': product_data['title'],
            'description': product_data.get('description', ''),
            'categoryId': product_data['category_id'],
            'brand': product_data.get('brand', ''),
            'barcode': product_data.get('barcode', ''),
            'price': float(product_data['price']),
            'listPrice': float(product_data.get('list_price', product_data['price'])),
            'stock': product_data['stock'],
            'images': product_data.get('images', []),
            'attributes': product_data.get('attributes', {}),
            'shipping': {
                'deliveryTime': product_data.get('delivery_time', '2-3 iş günü'),
                'shippingPrice': product_data.get('shipping_price', 0),
                'freeShippingThreshold': product_data.get('free_shipping_threshold', 100)
            },
            'status': 'active'
        }
        
        return self.make_request(
            RequestMethod.POST,
            'products',
            data=formatted_data
        )
    
    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing product"""
        return self.make_request(
            RequestMethod.PUT,
            f'products/{product_id}',
            data=product_data
        )
    
    def get_products(self, 
                    page: int = 1,
                    size: int = 100,
                    status: Optional[str] = None,
                    category_id: Optional[str] = None,
                    search: Optional[str] = None) -> Dict[str, Any]:
        """
        Get products with filters
        
        Args:
            page: Page number
            size: Page size
            status: Product status filter
            category_id: Category filter
            search: Search term
        """
        params = {
            'sellerId': self.seller_id,
            'page': page,
            'size': min(size, 100)
        }
        
        if status:
            params['status'] = status
        if category_id:
            params['categoryId'] = category_id
        if search:
            params['search'] = search
        
        return self.make_request(
            RequestMethod.GET,
            'products',
            params=params
        )
    
    def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get single product details"""
        return self.make_request(
            RequestMethod.GET,
            f'products/{product_id}'
        )
    
    def delete_product(self, product_id: str) -> Dict[str, Any]:
        """Delete a product"""
        return self.make_request(
            RequestMethod.DELETE,
            f'products/{product_id}'
        )
    
    def update_stock(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update stock for multiple products
        
        Args:
            updates: List of stock updates containing:
                - sku: Product SKU
                - stock: New stock quantity
        """
        data = {
            'sellerId': self.seller_id,
            'updates': updates
        }
        
        return self.make_request(
            RequestMethod.POST,
            'products/stock/bulk',
            data=data
        )
    
    def update_price(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update prices for multiple products
        
        Args:
            updates: List of price updates containing:
                - sku: Product SKU
                - price: New price
                - listPrice: Optional list price
        """
        data = {
            'sellerId': self.seller_id,
            'updates': updates
        }
        
        return self.make_request(
            RequestMethod.POST,
            'products/price/bulk',
            data=data
        )
    
    # Category Management
    def get_categories(self, parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get categories"""
        params = {}
        if parent_id:
            params['parentId'] = parent_id
        
        response = self.make_request(
            RequestMethod.GET,
            'categories',
            params=params
        )
        
        return response.get('categories', [])
    
    def get_category(self, category_id: str) -> Dict[str, Any]:
        """Get category details"""
        return self.make_request(
            RequestMethod.GET,
            f'categories/{category_id}'
        )
    
    def get_category_attributes(self, category_id: str) -> List[Dict[str, Any]]:
        """Get category attributes"""
        response = self.make_request(
            RequestMethod.GET,
            f'categories/{category_id}/attributes'
        )
        
        return response.get('attributes', [])
    
    def get_category_commission(self, category_id: str) -> Dict[str, Any]:
        """Get category commission rates"""
        return self.make_request(
            RequestMethod.GET,
            f'categories/{category_id}/commission'
        )
    
    # Order Management
    def get_orders(self,
                   status: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   page: int = 1,
                   size: int = 100) -> Dict[str, Any]:
        """
        Get orders with filters
        
        Args:
            status: Order status (new, approved, preparing, shipped, delivered, cancelled)
            start_date: Start date filter
            end_date: End date filter
            page: Page number
            size: Page size
        """
        params = {
            'sellerId': self.seller_id,
            'page': page,
            'size': min(size, 100)
        }
        
        if status:
            params['status'] = status
        if start_date:
            params['startDate'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['endDate'] = end_date.strftime('%Y-%m-%d')
        
        return self.make_request(
            RequestMethod.GET,
            'orders',
            params=params
        )
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get order details"""
        return self.make_request(
            RequestMethod.GET,
            f'orders/{order_id}'
        )
    
    def approve_order(self, order_id: str) -> Dict[str, Any]:
        """Approve an order"""
        data = {
            'sellerId': self.seller_id,
            'status': 'approved'
        }
        
        return self.make_request(
            RequestMethod.PUT,
            f'orders/{order_id}/status',
            data=data
        )
    
    def reject_order(self, order_id: str, reason: str) -> Dict[str, Any]:
        """Reject an order"""
        data = {
            'sellerId': self.seller_id,
            'status': 'rejected',
            'reason': reason
        }
        
        return self.make_request(
            RequestMethod.PUT,
            f'orders/{order_id}/status',
            data=data
        )
    
    def ship_order(self, order_id: str, 
                   tracking_number: str,
                   shipping_company: str) -> Dict[str, Any]:
        """Ship an order"""
        data = {
            'sellerId': self.seller_id,
            'status': 'shipped',
            'trackingNumber': tracking_number,
            'shippingCompany': shipping_company,
            'shippedAt': datetime.now().isoformat()
        }
        
        return self.make_request(
            RequestMethod.PUT,
            f'orders/{order_id}/status',
            data=data
        )
    
    def deliver_order(self, order_id: str) -> Dict[str, Any]:
        """Mark order as delivered"""
        data = {
            'sellerId': self.seller_id,
            'status': 'delivered',
            'deliveredAt': datetime.now().isoformat()
        }
        
        return self.make_request(
            RequestMethod.PUT,
            f'orders/{order_id}/status',
            data=data
        )
    
    def cancel_order(self, order_id: str, reason: str) -> Dict[str, Any]:
        """Cancel an order"""
        data = {
            'sellerId': self.seller_id,
            'status': 'cancelled',
            'reason': reason,
            'cancelledAt': datetime.now().isoformat()
        }
        
        return self.make_request(
            RequestMethod.PUT,
            f'orders/{order_id}/status',
            data=data
        )
    
    def get_order_invoice(self, order_id: str) -> bytes:
        """Get order invoice PDF"""
        response = self.session.get(
            self._build_url(f'orders/{order_id}/invoice'),
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.content
    
    # Shipping Management
    def get_shipping_companies(self) -> List[Dict[str, Any]]:
        """Get available shipping companies"""
        response = self.make_request(
            RequestMethod.GET,
            'shipping/companies'
        )
        
        return response.get('companies', [])
    
    def get_shipping_label(self, order_id: str) -> bytes:
        """Get shipping label for order"""
        response = self.session.get(
            self._build_url(f'orders/{order_id}/shipping-label'),
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.content
    
    def calculate_shipping_cost(self, 
                               from_city: str,
                               to_city: str,
                               weight: float,
                               dimensions: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Calculate shipping cost"""
        data = {
            'fromCity': from_city,
            'toCity': to_city,
            'weight': weight
        }
        
        if dimensions:
            data['dimensions'] = dimensions
        
        return self.make_request(
            RequestMethod.POST,
            'shipping/calculate',
            data=data
        )
    
    # Returns Management
    def get_returns(self,
                    status: Optional[str] = None,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None,
                    page: int = 1,
                    size: int = 100) -> Dict[str, Any]:
        """Get return requests"""
        params = {
            'sellerId': self.seller_id,
            'page': page,
            'size': min(size, 100)
        }
        
        if status:
            params['status'] = status
        if start_date:
            params['startDate'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['endDate'] = end_date.strftime('%Y-%m-%d')
        
        return self.make_request(
            RequestMethod.GET,
            'returns',
            params=params
        )
    
    def get_return(self, return_id: str) -> Dict[str, Any]:
        """Get return details"""
        return self.make_request(
            RequestMethod.GET,
            f'returns/{return_id}'
        )
    
    def approve_return(self, return_id: str, 
                      return_address: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Approve return request"""
        data = {
            'sellerId': self.seller_id,
            'status': 'approved'
        }
        
        if return_address:
            data['returnAddress'] = return_address
        
        return self.make_request(
            RequestMethod.PUT,
            f'returns/{return_id}/status',
            data=data
        )
    
    def reject_return(self, return_id: str, reason: str) -> Dict[str, Any]:
        """Reject return request"""
        data = {
            'sellerId': self.seller_id,
            'status': 'rejected',
            'reason': reason
        }
        
        return self.make_request(
            RequestMethod.PUT,
            f'returns/{return_id}/status',
            data=data
        )
    
    def complete_return(self, return_id: str, 
                       refund_amount: Optional[float] = None) -> Dict[str, Any]:
        """Complete return and process refund"""
        data = {
            'sellerId': self.seller_id,
            'status': 'completed'
        }
        
        if refund_amount:
            data['refundAmount'] = refund_amount
        
        return self.make_request(
            RequestMethod.PUT,
            f'returns/{return_id}/status',
            data=data
        )
    
    # Question & Answer Management
    def get_questions(self,
                      status: Optional[str] = None,
                      product_id: Optional[str] = None,
                      page: int = 1,
                      size: int = 100) -> Dict[str, Any]:
        """Get product questions"""
        params = {
            'sellerId': self.seller_id,
            'page': page,
            'size': min(size, 100)
        }
        
        if status:
            params['status'] = status
        if product_id:
            params['productId'] = product_id
        
        return self.make_request(
            RequestMethod.GET,
            'questions',
            params=params
        )
    
    def answer_question(self, question_id: str, answer: str) -> Dict[str, Any]:
        """Answer a product question"""
        data = {
            'sellerId': self.seller_id,
            'answer': answer,
            'answeredAt': datetime.now().isoformat()
        }
        
        return self.make_request(
            RequestMethod.POST,
            f'questions/{question_id}/answer',
            data=data
        )
    
    # Review Management
    def get_reviews(self,
                    product_id: Optional[str] = None,
                    rating: Optional[int] = None,
                    page: int = 1,
                    size: int = 100) -> Dict[str, Any]:
        """Get product reviews"""
        params = {
            'sellerId': self.seller_id,
            'page': page,
            'size': min(size, 100)
        }
        
        if product_id:
            params['productId'] = product_id
        if rating:
            params['rating'] = rating
        
        return self.make_request(
            RequestMethod.GET,
            'reviews',
            params=params
        )
    
    def respond_to_review(self, review_id: str, response: str) -> Dict[str, Any]:
        """Respond to a review"""
        data = {
            'sellerId': self.seller_id,
            'response': response,
            'respondedAt': datetime.now().isoformat()
        }
        
        return self.make_request(
            RequestMethod.POST,
            f'reviews/{review_id}/response',
            data=data
        )
    
    # Campaign Management
    def get_campaigns(self, 
                      is_active: Optional[bool] = None,
                      page: int = 1,
                      size: int = 100) -> Dict[str, Any]:
        """Get campaigns"""
        params = {
            'page': page,
            'size': min(size, 100)
        }
        
        if is_active is not None:
            params['isActive'] = is_active
        
        return self.make_request(
            RequestMethod.GET,
            'campaigns',
            params=params
        )
    
    def join_campaign(self, campaign_id: str, 
                     products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Join a campaign with products"""
        data = {
            'sellerId': self.seller_id,
            'products': products
        }
        
        return self.make_request(
            RequestMethod.POST,
            f'campaigns/{campaign_id}/join',
            data=data
        )
    
    def leave_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Leave a campaign"""
        data = {
            'sellerId': self.seller_id
        }
        
        return self.make_request(
            RequestMethod.POST,
            f'campaigns/{campaign_id}/leave',
            data=data
        )
    
    # Analytics & Reporting
    def get_sales_report(self, 
                        start_date: datetime,
                        end_date: datetime,
                        group_by: str = 'day') -> Dict[str, Any]:
        """Get sales report"""
        params = {
            'sellerId': self.seller_id,
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'groupBy': group_by
        }
        
        return self.make_request(
            RequestMethod.GET,
            'reports/sales',
            params=params
        )
    
    def get_product_performance(self, 
                               start_date: datetime,
                               end_date: datetime,
                               limit: int = 50) -> Dict[str, Any]:
        """Get product performance report"""
        params = {
            'sellerId': self.seller_id,
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'limit': limit
        }
        
        return self.make_request(
            RequestMethod.GET,
            'reports/products',
            params=params
        )
    
    def get_financial_report(self, 
                            year: int,
                            month: int) -> Dict[str, Any]:
        """Get financial report for a month"""
        params = {
            'sellerId': self.seller_id,
            'year': year,
            'month': month
        }
        
        return self.make_request(
            RequestMethod.GET,
            'reports/financial',
            params=params
        )
    
    def get_inventory_report(self) -> Dict[str, Any]:
        """Get current inventory report"""
        params = {
            'sellerId': self.seller_id
        }
        
        return self.make_request(
            RequestMethod.GET,
            'reports/inventory',
            params=params
        )
    
    # Settlement & Payment
    def get_settlements(self,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       page: int = 1,
                       size: int = 100) -> Dict[str, Any]:
        """Get settlement reports"""
        params = {
            'sellerId': self.seller_id,
            'page': page,
            'size': min(size, 100)
        }
        
        if start_date:
            params['startDate'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['endDate'] = end_date.strftime('%Y-%m-%d')
        
        return self.make_request(
            RequestMethod.GET,
            'settlements',
            params=params
        )
    
    def get_settlement(self, settlement_id: str) -> Dict[str, Any]:
        """Get settlement details"""
        return self.make_request(
            RequestMethod.GET,
            f'settlements/{settlement_id}'
        )
    
    # Helper Methods
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products using pagination"""
        all_products = []
        page = 1
        
        while True:
            response = self.get_products(page=page, size=100)
            products = response.get('products', [])
            
            if not products:
                break
            
            all_products.extend(products)
            
            if len(products) < 100:
                break
            
            page += 1
        
        return all_products
    
    def get_all_orders(self, status: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get all orders using pagination"""
        all_orders = []
        page = 1
        
        while True:
            response = self.get_orders(
                status=status,
                start_date=start_date,
                end_date=end_date,
                page=page,
                size=100
            )
            orders = response.get('orders', [])
            
            if not orders:
                break
            
            all_orders.extend(orders)
            
            if len(orders) < 100:
                break
            
            page += 1
        
        return all_orders
    
    def calculate_commission(self, category_id: str, 
                           price: Decimal) -> Dict[str, Decimal]:
        """Calculate PTT AVM commission"""
        commission_info = self.get_category_commission(category_id)
        
        # Get commission rates
        base_rate = Decimal(str(commission_info.get('baseRate', 0.08)))  # Default 8%
        ptt_rate = Decimal(str(commission_info.get('pttRate', 0.02)))    # Default 2%
        
        # Calculate commissions
        base_commission = price * base_rate
        ptt_commission = price * ptt_rate
        total_commission = base_commission + ptt_commission
        
        return {
            'base_commission': base_commission,
            'ptt_commission': ptt_commission,
            'total_commission': total_commission,
            'net_amount': price - total_commission
        }
    
    def format_product_for_pttavm(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format product data for PTT AVM API"""
        formatted = {
            'sku': product_data.get('sku'),
            'title': product_data.get('name'),
            'description': product_data.get('description', ''),
            'categoryId': product_data.get('category_id'),
            'brand': product_data.get('brand', ''),
            'barcode': product_data.get('barcode', ''),
            'price': float(product_data.get('price', 0)),
            'listPrice': float(product_data.get('list_price', product_data.get('price', 0))),
            'stock': product_data.get('stock', 0),
            'images': product_data.get('images', []),
            'attributes': {},
            'shipping': {
                'deliveryTime': product_data.get('delivery_time', '2-3 iş günü'),
                'shippingPrice': product_data.get('shipping_price', 0),
                'freeShippingThreshold': product_data.get('free_shipping_threshold', 100)
            }
        }
        
        # Add attributes
        if 'attributes' in product_data:
            for attr_name, attr_value in product_data['attributes'].items():
                formatted['attributes'][attr_name] = attr_value
        
        # Add weight if available
        if 'weight' in product_data:
            formatted['weight'] = product_data['weight']
        
        # Add dimensions if available
        if all(key in product_data for key in ['width', 'height', 'depth']):
            formatted['dimensions'] = {
                'width': product_data['width'],
                'height': product_data['height'],
                'depth': product_data['depth']
            }
        
        return formatted


def test_pttavm_api():
    """Test PTT AVM API functionality"""
    print("Testing PTT AVM Marketplace API...")
    
    # Test credentials (these should come from environment variables)
    credentials = {
        'api_key': 'YOUR_API_KEY',
        'api_secret': 'YOUR_API_SECRET',
        'seller_id': 'YOUR_SELLER_ID'
    }
    
    try:
        # Initialize API
        api = PTTAVMMarketplaceAPI(credentials, sandbox=True)
        
        # Test connection
        if api.validate_credentials():
            print("✅ Connection successful!")
            
            # Get seller info
            seller_info = api.get_seller_info()
            print(f"✅ Seller: {seller_info.get('name')}")
            
            # Get categories
            categories = api.get_categories()
            print(f"✅ Found {len(categories)} categories")
            
            # Get shipping companies
            shipping_companies = api.get_shipping_companies()
            print(f"✅ Found {len(shipping_companies)} shipping companies")
            
            # Get active campaigns
            campaigns = api.get_campaigns(is_active=True)
            print(f"✅ Found {campaigns.get('totalCount', 0)} active campaigns")
            
        else:
            print("❌ Authentication failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_pttavm_api()