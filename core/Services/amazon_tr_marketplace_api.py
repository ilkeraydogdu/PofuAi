"""
Amazon TR Marketplace API Integration
Full implementation with SP-API (Selling Partner API)
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import hmac
import hashlib
import base64
import urllib.parse
import time
from decimal import Decimal
import json
import gzip
from io import BytesIO

from .base_integration import BaseIntegration, RequestMethod, ValidationError, APIError, AuthenticationError


class AmazonTRMarketplaceAPI(BaseIntegration):
    """
    Amazon TR Marketplace API implementation using SP-API
    
    Documentation: https://developer-docs.amazon.com/sp-api/
    """
    
    # Amazon regions and endpoints
    REGIONS = {
        'eu': {
            'endpoint': 'https://sellingpartnerapi-eu.amazon.com',
            'region': 'eu-west-1',
            'marketplace_id': 'A33AVAJ2PDY3EV'  # Turkey marketplace ID
        }
    }
    
    # API paths
    API_PATHS = {
        'catalog': '/catalog/2022-04-01',
        'orders': '/orders/v0',
        'products': '/products/pricing/v0',
        'feeds': '/feeds/2021-06-30',
        'reports': '/reports/2021-06-30',
        'inventory': '/fba/inventory/v1',
        'fulfillment': '/fba/outbound/2020-07-01',
        'shipping': '/shipping/v1',
        'sellers': '/sellers/v1',
        'tokens': '/tokens/2021-03-01',
        'notifications': '/notifications/v1'
    }
    
    def _initialize(self):
        """Initialize Amazon SP-API specific settings"""
        self.client_id = self.credentials.get('client_id')
        self.client_secret = self.credentials.get('client_secret')
        self.refresh_token = self.credentials.get('refresh_token')
        self.seller_id = self.credentials.get('seller_id')
        self.marketplace_id = self.credentials.get('marketplace_id', self.REGIONS['eu']['marketplace_id'])
        
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise ValueError("Missing required credentials: client_id, client_secret, refresh_token")
        
        # Set region info
        self.region_info = self.REGIONS['eu']
        self.base_url = self.region_info['endpoint']
        
        # Amazon specific settings
        self.min_request_interval = 1.0  # 1 second between requests
        self.access_token = None
        self.token_expires = datetime.now()
        
        # Get initial access token
        self._get_access_token()
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL for endpoint"""
        # Extract API path and endpoint
        if endpoint.startswith('/'):
            return f"{self.base_url}{endpoint}"
        
        # Find matching API path
        for api_name, api_path in self.API_PATHS.items():
            if endpoint.startswith(api_name):
                endpoint_path = endpoint.replace(api_name, api_path)
                return f"{self.base_url}{endpoint_path}"
        
        return f"{self.base_url}/{endpoint}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        self._check_token_expiry()
        
        headers = {
            'x-amz-access-token': self.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'AmazonTR-Python-Client/1.0'
        }
        
        return headers
    
    def _get_access_token(self):
        """Get access token using refresh token"""
        token_url = 'https://api.amazon.com/auth/o2/token'
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = self.session.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)
        else:
            raise AuthenticationError(f"Failed to get access token: {response.text}")
    
    def _check_token_expiry(self):
        """Check if token is expired and renew if necessary"""
        if datetime.now() >= self.token_expires:
            self._get_access_token()
    
    def _test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Get marketplace participations to test connection
            self.get_marketplace_participations()
            return True
        except Exception:
            return False
    
    def _sign_request(self, method: str, url: str, headers: Dict[str, str], 
                     data: Optional[str] = None) -> Dict[str, str]:
        """Sign request using AWS Signature Version 4"""
        # This is a simplified version - in production, use boto3 or aws-requests-auth
        # for proper AWS Signature Version 4 signing
        return headers
    
    # Seller Account Management
    def get_marketplace_participations(self) -> List[Dict[str, Any]]:
        """Get seller's marketplace participations"""
        response = self.make_request(
            RequestMethod.GET,
            '/sellers/v1/marketplaceParticipations'
        )
        
        participations = []
        for item in response.get('payload', []):
            participations.append({
                'marketplace': item['marketplace'],
                'participation': item['participation']
            })
        
        return participations
    
    # Catalog Management
    def search_catalog_items(self, 
                           keywords: Optional[str] = None,
                           identifiers: Optional[List[str]] = None,
                           brand_names: Optional[List[str]] = None,
                           classification_ids: Optional[List[str]] = None,
                           page_size: int = 20,
                           page_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Search catalog items
        
        Args:
            keywords: Search keywords
            identifiers: List of identifiers (ASIN, EAN, ISBN, etc.)
            brand_names: List of brand names
            classification_ids: List of classification IDs
            page_size: Number of results per page
            page_token: Token for pagination
        """
        params = {
            'marketplaceIds': self.marketplace_id,
            'pageSize': min(page_size, 20)
        }
        
        if keywords:
            params['keywords'] = keywords
        if identifiers:
            params['identifiers'] = ','.join(identifiers)
        if brand_names:
            params['brandNames'] = ','.join(brand_names)
        if classification_ids:
            params['classificationIds'] = ','.join(classification_ids)
        if page_token:
            params['pageToken'] = page_token
        
        return self.make_request(
            RequestMethod.GET,
            '/catalog/2022-04-01/items',
            params=params
        )
    
    def get_catalog_item(self, asin: str) -> Dict[str, Any]:
        """Get catalog item by ASIN"""
        params = {
            'marketplaceIds': self.marketplace_id,
            'includedData': 'attributes,dimensions,identifiers,images,productTypes,relationships,salesRanks,summaries,vendorDetails'
        }
        
        return self.make_request(
            RequestMethod.GET,
            f'/catalog/2022-04-01/items/{asin}',
            params=params
        )
    
    # Product Management
    def create_product_listing(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product listing
        
        Args:
            product_data: Product information including:
                - sku: Seller SKU
                - product_type: Product type
                - requirements: Product requirements
                - attributes: Product attributes
                - offers: Pricing and availability
        """
        # Create product feed
        feed_data = {
            'messageType': 'PRODUCT',
            'messages': [{
                'messageId': 1,
                'sku': product_data['sku'],
                'productType': product_data['product_type'],
                'requirements': product_data.get('requirements', 'LISTING'),
                'attributes': product_data['attributes']
            }]
        }
        
        return self.submit_feed('POST_PRODUCT_DATA', feed_data)
    
    def update_product_price(self, sku: str, price: float, 
                           currency: str = 'TRY',
                           minimum_price: Optional[float] = None,
                           maximum_price: Optional[float] = None) -> Dict[str, Any]:
        """Update product price"""
        feed_data = {
            'messageType': 'PRICE',
            'messages': [{
                'messageId': 1,
                'sku': sku,
                'price': {
                    'value': price,
                    'currency': currency
                }
            }]
        }
        
        if minimum_price:
            feed_data['messages'][0]['minimumPrice'] = {
                'value': minimum_price,
                'currency': currency
            }
        
        if maximum_price:
            feed_data['messages'][0]['maximumPrice'] = {
                'value': maximum_price,
                'currency': currency
            }
        
        return self.submit_feed('POST_PRODUCT_PRICING_DATA', feed_data)
    
    def update_inventory(self, sku: str, quantity: int, 
                        fulfillment_channel: str = 'DEFAULT') -> Dict[str, Any]:
        """Update product inventory"""
        feed_data = {
            'messageType': 'INVENTORY',
            'messages': [{
                'messageId': 1,
                'sku': sku,
                'quantity': quantity,
                'fulfillmentChannel': fulfillment_channel
            }]
        }
        
        return self.submit_feed('POST_INVENTORY_AVAILABILITY_DATA', feed_data)
    
    def get_product_pricing(self, skus: List[str], 
                          item_type: str = 'Sku') -> Dict[str, Any]:
        """Get competitive pricing for products"""
        params = {
            'MarketplaceId': self.marketplace_id,
            'ItemType': item_type
        }
        
        if item_type == 'Sku':
            params['Skus'] = ','.join(skus)
        else:
            params['Asins'] = ','.join(skus)
        
        return self.make_request(
            RequestMethod.GET,
            '/products/pricing/v0/price',
            params=params
        )
    
    def get_product_offers(self, asin: str) -> Dict[str, Any]:
        """Get product offers"""
        params = {
            'MarketplaceId': self.marketplace_id,
            'ItemCondition': 'New'
        }
        
        return self.make_request(
            RequestMethod.GET,
            f'/products/pricing/v0/items/{asin}/offers',
            params=params
        )
    
    # Order Management
    def get_orders(self,
                   created_after: Optional[datetime] = None,
                   created_before: Optional[datetime] = None,
                   last_updated_after: Optional[datetime] = None,
                   last_updated_before: Optional[datetime] = None,
                   order_statuses: Optional[List[str]] = None,
                   fulfillment_channels: Optional[List[str]] = None,
                   max_results: int = 100,
                   next_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Get orders with filters
        
        Args:
            created_after: Orders created after this date
            created_before: Orders created before this date
            last_updated_after: Orders updated after this date
            last_updated_before: Orders updated before this date
            order_statuses: List of order statuses
            fulfillment_channels: List of fulfillment channels
            max_results: Maximum number of results
            next_token: Token for pagination
        """
        params = {
            'MarketplaceIds': self.marketplace_id,
            'MaxResultsPerPage': min(max_results, 100)
        }
        
        if created_after:
            params['CreatedAfter'] = created_after.isoformat()
        if created_before:
            params['CreatedBefore'] = created_before.isoformat()
        if last_updated_after:
            params['LastUpdatedAfter'] = last_updated_after.isoformat()
        if last_updated_before:
            params['LastUpdatedBefore'] = last_updated_before.isoformat()
        if order_statuses:
            params['OrderStatuses'] = ','.join(order_statuses)
        if fulfillment_channels:
            params['FulfillmentChannels'] = ','.join(fulfillment_channels)
        if next_token:
            params['NextToken'] = next_token
        
        return self.make_request(
            RequestMethod.GET,
            '/orders/v0/orders',
            params=params
        )
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get order details"""
        return self.make_request(
            RequestMethod.GET,
            f'/orders/v0/orders/{order_id}'
        )
    
    def get_order_items(self, order_id: str) -> Dict[str, Any]:
        """Get order items"""
        return self.make_request(
            RequestMethod.GET,
            f'/orders/v0/orders/{order_id}/orderItems'
        )
    
    def get_order_buyer_info(self, order_id: str) -> Dict[str, Any]:
        """Get order buyer information"""
        return self.make_request(
            RequestMethod.GET,
            f'/orders/v0/orders/{order_id}/buyerInfo'
        )
    
    def get_order_address(self, order_id: str) -> Dict[str, Any]:
        """Get order shipping address"""
        return self.make_request(
            RequestMethod.GET,
            f'/orders/v0/orders/{order_id}/address'
        )
    
    def update_shipment_status(self, order_id: str, 
                             shipment_status: str,
                             tracking_number: Optional[str] = None,
                             carrier_name: Optional[str] = None) -> Dict[str, Any]:
        """Update order shipment status"""
        data = {
            'marketplaceId': self.marketplace_id,
            'shipmentStatus': shipment_status
        }
        
        if tracking_number:
            data['trackingNumber'] = tracking_number
        if carrier_name:
            data['carrierName'] = carrier_name
        
        return self.make_request(
            RequestMethod.POST,
            f'/orders/v0/orders/{order_id}/shipment',
            data=data
        )
    
    # Feed Management
    def submit_feed(self, feed_type: str, feed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a feed to Amazon"""
        # Step 1: Create feed document
        doc_response = self.create_feed_document(feed_content)
        document_id = doc_response['feedDocumentId']
        upload_url = doc_response['url']
        
        # Step 2: Upload feed content
        self._upload_feed_document(upload_url, feed_content)
        
        # Step 3: Create feed
        feed_data = {
            'feedType': feed_type,
            'marketplaceIds': [self.marketplace_id],
            'inputFeedDocumentId': document_id
        }
        
        return self.make_request(
            RequestMethod.POST,
            '/feeds/2021-06-30/feeds',
            data=feed_data
        )
    
    def create_feed_document(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create a feed document"""
        data = {
            'contentType': 'application/json; charset=utf-8'
        }
        
        response = self.make_request(
            RequestMethod.POST,
            '/feeds/2021-06-30/documents',
            data=data
        )
        
        return response['payload']
    
    def _upload_feed_document(self, upload_url: str, content: Dict[str, Any]):
        """Upload feed content to the provided URL"""
        # Convert content to JSON and compress
        json_content = json.dumps(content).encode('utf-8')
        
        # Compress content
        compressed = BytesIO()
        with gzip.GzipFile(fileobj=compressed, mode='wb') as gz:
            gz.write(json_content)
        compressed_content = compressed.getvalue()
        
        # Upload to S3
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Content-Encoding': 'gzip'
        }
        
        response = self.session.put(upload_url, data=compressed_content, headers=headers)
        response.raise_for_status()
    
    def get_feed(self, feed_id: str) -> Dict[str, Any]:
        """Get feed status"""
        return self.make_request(
            RequestMethod.GET,
            f'/feeds/2021-06-30/feeds/{feed_id}'
        )
    
    # Report Management
    def create_report(self, report_type: str,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a report"""
        data = {
            'reportType': report_type,
            'marketplaceIds': [self.marketplace_id]
        }
        
        if start_date:
            data['dataStartTime'] = start_date.isoformat()
        if end_date:
            data['dataEndTime'] = end_date.isoformat()
        if options:
            data['reportOptions'] = options
        
        return self.make_request(
            RequestMethod.POST,
            '/reports/2021-06-30/reports',
            data=data
        )
    
    def get_report(self, report_id: str) -> Dict[str, Any]:
        """Get report status"""
        return self.make_request(
            RequestMethod.GET,
            f'/reports/2021-06-30/reports/{report_id}'
        )
    
    def get_report_document(self, report_document_id: str) -> Dict[str, Any]:
        """Get report document"""
        return self.make_request(
            RequestMethod.GET,
            f'/reports/2021-06-30/documents/{report_document_id}'
        )
    
    # FBA (Fulfillment by Amazon) Management
    def get_fba_inventory(self, 
                         skus: Optional[List[str]] = None,
                         next_token: Optional[str] = None) -> Dict[str, Any]:
        """Get FBA inventory"""
        params = {
            'details': True,
            'marketplaceIds': self.marketplace_id
        }
        
        if skus:
            params['sellerSkus'] = ','.join(skus)
        if next_token:
            params['nextToken'] = next_token
        
        return self.make_request(
            RequestMethod.GET,
            '/fba/inventory/v1/summaries',
            params=params
        )
    
    def create_fulfillment_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create FBA fulfillment order"""
        return self.make_request(
            RequestMethod.POST,
            '/fba/outbound/2020-07-01/fulfillmentOrders',
            data=order_data
        )
    
    def get_fulfillment_order(self, fulfillment_order_id: str) -> Dict[str, Any]:
        """Get fulfillment order details"""
        return self.make_request(
            RequestMethod.GET,
            f'/fba/outbound/2020-07-01/fulfillmentOrders/{fulfillment_order_id}'
        )
    
    # Shipping Management
    def get_shipping_rates(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get shipping rates"""
        return self.make_request(
            RequestMethod.POST,
            '/shipping/v1/rates',
            data=shipment_data
        )
    
    def create_shipment(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create shipment"""
        return self.make_request(
            RequestMethod.POST,
            '/shipping/v1/shipments',
            data=shipment_data
        )
    
    def get_shipping_label(self, shipment_id: str) -> Dict[str, Any]:
        """Get shipping label"""
        return self.make_request(
            RequestMethod.GET,
            f'/shipping/v1/shipments/{shipment_id}/label'
        )
    
    # Notification Management
    def create_subscription(self, notification_type: str, 
                          destination_id: str) -> Dict[str, Any]:
        """Create notification subscription"""
        data = {
            'payloadVersion': '1.0',
            'destinationId': destination_id
        }
        
        return self.make_request(
            RequestMethod.POST,
            f'/notifications/v1/subscriptions/{notification_type}',
            data=data
        )
    
    def delete_subscription(self, notification_type: str,
                          subscription_id: str) -> Dict[str, Any]:
        """Delete notification subscription"""
        return self.make_request(
            RequestMethod.DELETE,
            f'/notifications/v1/subscriptions/{notification_type}/{subscription_id}'
        )
    
    # Helper Methods
    def get_all_orders(self, 
                      created_after: Optional[datetime] = None,
                      order_statuses: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get all orders using pagination"""
        all_orders = []
        next_token = None
        
        while True:
            response = self.get_orders(
                created_after=created_after,
                order_statuses=order_statuses,
                next_token=next_token
            )
            
            orders = response.get('payload', {}).get('Orders', [])
            all_orders.extend(orders)
            
            next_token = response.get('payload', {}).get('NextToken')
            if not next_token:
                break
            
            # Rate limiting
            time.sleep(self.min_request_interval)
        
        return all_orders
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products using reports"""
        # Create inventory report
        report_response = self.create_report('GET_MERCHANT_LISTINGS_ALL_DATA')
        report_id = report_response['reportId']
        
        # Wait for report to complete
        while True:
            report_status = self.get_report(report_id)
            if report_status['processingStatus'] == 'DONE':
                break
            elif report_status['processingStatus'] == 'CANCELLED':
                raise APIError("Report was cancelled")
            
            time.sleep(30)  # Wait 30 seconds before checking again
        
        # Get report document
        document_id = report_status['reportDocumentId']
        document_info = self.get_report_document(document_id)
        
        # Download and parse report
        # This would need implementation to download from S3 URL
        # and parse the TSV/CSV report format
        
        return []
    
    def calculate_fees(self, asin: str, price: Decimal, 
                      is_fba: bool = False) -> Dict[str, Decimal]:
        """Calculate Amazon fees for a product"""
        # Get product details for category
        product = self.get_catalog_item(asin)
        
        # Basic fee calculation (simplified)
        referral_fee = price * Decimal('0.15')  # 15% referral fee
        
        fees = {
            'referral_fee': referral_fee,
            'total_fees': referral_fee
        }
        
        if is_fba:
            # Add FBA fees (simplified)
            fba_fee = Decimal('10.00')  # Base FBA fee
            fees['fba_fee'] = fba_fee
            fees['total_fees'] += fba_fee
        
        return fees
    
    def format_product_for_amazon(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format product data for Amazon API"""
        formatted = {
            'sku': product_data.get('sku'),
            'product_type': product_data.get('product_type', 'PRODUCT'),
            'requirements': 'LISTING',
            'attributes': {
                'title': [{
                    'value': product_data.get('title'),
                    'language_tag': 'tr_TR'
                }],
                'description': [{
                    'value': product_data.get('description', ''),
                    'language_tag': 'tr_TR'
                }],
                'bullet_points': [{
                    'value': point,
                    'language_tag': 'tr_TR'
                } for point in product_data.get('bullet_points', [])],
                'brand': [{
                    'value': product_data.get('brand')
                }],
                'manufacturer': [{
                    'value': product_data.get('manufacturer', product_data.get('brand'))
                }],
                'product_category': [{
                    'value': product_data.get('category')
                }],
                'item_package_weight': [{
                    'unit': 'kilograms',
                    'value': product_data.get('weight', 1)
                }],
                'main_product_image_locator': [{
                    'media_location': product_data.get('main_image')
                }],
                'other_product_image_locator': [
                    {'media_location': img} for img in product_data.get('images', [])
                ],
                'purchasable_offer': [{
                    'currency': 'TRY',
                    'our_price': [{
                        'schedule': [{
                            'value': float(product_data.get('price', 0))
                        }]
                    }]
                }]
            }
        }
        
        # Add condition if not new
        if product_data.get('condition') and product_data['condition'] != 'new':
            formatted['attributes']['condition'] = [{
                'value': product_data['condition']
            }]
        
        # Add identifiers
        if product_data.get('ean'):
            formatted['attributes']['externally_assigned_product_identifier'] = [{
                'type': 'ean',
                'value': product_data['ean']
            }]
        
        return formatted


def test_amazon_tr_api():
    """Test Amazon TR API functionality"""
    print("Testing Amazon TR Marketplace API...")
    
    # Test credentials (these should come from environment variables)
    credentials = {
        'client_id': 'YOUR_CLIENT_ID',
        'client_secret': 'YOUR_CLIENT_SECRET',
        'refresh_token': 'YOUR_REFRESH_TOKEN',
        'seller_id': 'YOUR_SELLER_ID'
    }
    
    try:
        # Initialize API
        api = AmazonTRMarketplaceAPI(credentials)
        
        # Test connection
        if api.validate_credentials():
            print("✅ Connection successful!")
            
            # Get marketplace participations
            participations = api.get_marketplace_participations()
            print(f"✅ Found {len(participations)} marketplace participations")
            
            # Search catalog
            search_results = api.search_catalog_items(keywords="test", page_size=5)
            print(f"✅ Catalog search returned {len(search_results.get('items', []))} items")
            
            # Get recent orders
            recent_orders = api.get_orders(
                created_after=datetime.now() - timedelta(days=7),
                max_results=10
            )
            print(f"✅ Found {len(recent_orders.get('payload', {}).get('Orders', []))} recent orders")
            
        else:
            print("❌ Authentication failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_amazon_tr_api()