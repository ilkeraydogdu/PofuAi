"""
N11 Marketplace API Integration
Full implementation with SOAP/WSDL support
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import time
from decimal import Decimal
from zeep import Client, Settings, Transport
from zeep.exceptions import Fault
from requests import Session
from requests.auth import HTTPBasicAuth

from .base_integration import BaseIntegration, RequestMethod, ValidationError, APIError, AuthenticationError


class N11MarketplaceAPI(BaseIntegration):
    """
    N11 Marketplace API implementation (SOAP/WSDL based)
    
    Documentation: https://dev.n11.com/
    """
    
    # WSDL URLs for different services
    WSDL_URLS = {
        'product': 'https://api.n11.com/ws/ProductService.wsdl',
        'category': 'https://api.n11.com/ws/CategoryService.wsdl',
        'order': 'https://api.n11.com/ws/OrderService.wsdl',
        'shipment': 'https://api.n11.com/ws/ShipmentService.wsdl',
        'shipment_company': 'https://api.n11.com/ws/ShipmentCompanyService.wsdl',
        'city': 'https://api.n11.com/ws/CityService.wsdl',
        'settlement': 'https://api.n11.com/ws/SettlementService.wsdl',
        'ticket': 'https://api.n11.com/ws/TicketService.wsdl',
        'claim': 'https://api.n11.com/ws/ClaimService.wsdl',
        'return': 'https://api.n11.com/ws/ReturnService.wsdl'
    }
    
    def _initialize(self):
        """Initialize N11 specific settings"""
        self.api_key = self.credentials.get('api_key')
        self.api_secret = self.credentials.get('api_secret')
        
        if not all([self.api_key, self.api_secret]):
            raise ValueError("Missing required credentials: api_key, api_secret")
        
        # N11 doesn't have sandbox environment
        self.base_url = "https://api.n11.com/ws"
        
        # N11 specific settings
        self.min_request_interval = 0.3  # 300ms between requests
        
        # Initialize SOAP clients
        self.clients = {}
        self._init_soap_clients()
        
        # Authentication object for all requests
        self.auth = {
            'appKey': self.api_key,
            'appSecret': self.api_secret
        }
    
    def _init_soap_clients(self):
        """Initialize SOAP clients for different services"""
        # Create session with connection pooling
        session = Session()
        session.headers.update({
            'User-Agent': 'N11-Python-Client/1.0'
        })
        
        # SOAP settings
        settings = Settings(
            strict=False,
            xml_huge_tree=True,
            xsd_ignore_sequence_order=True
        )
        
        # Create transport with session
        transport = Transport(session=session, timeout=30, operation_timeout=30)
        
        # Initialize clients for each service
        for service, wsdl_url in self.WSDL_URLS.items():
            try:
                self.clients[service] = Client(
                    wsdl=wsdl_url,
                    settings=settings,
                    transport=transport
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize {service} client: {e}")
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL for endpoint (not used for SOAP)"""
        return f"{self.base_url}/{endpoint}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers (not used for SOAP)"""
        return {}
    
    def _test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Get top level categories to test connection
            self.get_top_level_categories()
            return True
        except Exception:
            return False
    
    def _call_soap_method(self, service: str, method: str, **kwargs) -> Any:
        """Call SOAP method with error handling"""
        if service not in self.clients:
            raise APIError(f"Service {service} not initialized")
        
        try:
            # Add authentication to all requests
            kwargs['auth'] = self.auth
            
            # Get service and method
            service_client = self.clients[service].service
            soap_method = getattr(service_client, method)
            
            # Make SOAP call
            self._check_rate_limit()
            result = soap_method(**kwargs)
            
            # Check for errors in response
            if hasattr(result, 'result') and hasattr(result.result, 'status'):
                if result.result.status != 'success':
                    error_msg = getattr(result.result, 'errorMessage', 'Unknown error')
                    raise APIError(f"N11 API Error: {error_msg}")
            
            return result
            
        except Fault as e:
            self.logger.error(f"SOAP Fault: {e}")
            raise APIError(f"SOAP Fault: {str(e)}")
        except Exception as e:
            self.logger.error(f"SOAP Error: {e}")
            raise APIError(f"SOAP Error: {str(e)}")
    
    # Category Management
    def get_top_level_categories(self) -> List[Dict[str, Any]]:
        """Get top level categories"""
        response = self._call_soap_method('category', 'GetTopLevelCategories')
        
        categories = []
        if hasattr(response, 'categoryList') and response.categoryList:
            for cat in response.categoryList.category:
                categories.append({
                    'id': cat.id,
                    'name': cat.name,
                    'hasSubCategory': getattr(cat, 'hasSubCategory', False)
                })
        
        return categories
    
    def get_sub_categories(self, category_id: int) -> List[Dict[str, Any]]:
        """Get sub categories"""
        response = self._call_soap_method(
            'category', 
            'GetSubCategories',
            categoryId=category_id
        )
        
        categories = []
        if hasattr(response, 'category') and response.category:
            for cat in response.category.subCategoryList.subCategory:
                categories.append({
                    'id': cat.id,
                    'name': cat.name,
                    'hasSubCategory': getattr(cat, 'hasSubCategory', False)
                })
        
        return categories
    
    def get_category_attributes(self, category_id: int) -> Dict[str, Any]:
        """Get category attributes"""
        response = self._call_soap_method(
            'category',
            'GetCategoryAttributes',
            categoryId=category_id
        )
        
        attributes = []
        if hasattr(response, 'category') and hasattr(response.category, 'attributeList'):
            for attr in response.category.attributeList.attribute:
                attribute_data = {
                    'id': attr.id,
                    'name': attr.name,
                    'mandatory': attr.mandatory,
                    'multipleSelect': getattr(attr, 'multipleSelect', False),
                    'values': []
                }
                
                if hasattr(attr, 'valueList') and attr.valueList:
                    for val in attr.valueList.value:
                        attribute_data['values'].append({
                            'id': val.id,
                            'name': val.name
                        })
                
                attributes.append(attribute_data)
        
        return {
            'categoryId': category_id,
            'attributes': attributes
        }
    
    # Product Management
    def save_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save (create or update) a product
        
        Args:
            product_data: Product information including:
                - productSellerCode: Unique seller code
                - title: Product title
                - subtitle: Product subtitle
                - description: Product description
                - category: Category info with id and fullName
                - price: Price value
                - currencyType: Currency (1=TL, 2=USD, 3=EUR)
                - images: List of image objects
                - stockItems: Stock information
                - attributes: Product attributes
                - productCondition: 1=New, 2=Used
                - preparingDay: Preparing days
                - shipmentTemplate: Shipment template name
        """
        # Build product request
        product_request = {
            'productSellerCode': product_data['productSellerCode'],
            'title': product_data['title'],
            'subtitle': product_data.get('subtitle', ''),
            'description': product_data['description'],
            'category': {
                'id': product_data['category']['id']
            },
            'price': float(product_data['price']),
            'currencyType': product_data.get('currencyType', 1),  # Default TL
            'images': {
                'image': []
            },
            'stockItems': {
                'stockItem': []
            },
            'productCondition': product_data.get('productCondition', 1),  # Default New
            'preparingDay': product_data.get('preparingDay', 3),
            'shipmentTemplate': product_data.get('shipmentTemplate', '')
        }
        
        # Add images
        for idx, image in enumerate(product_data.get('images', [])):
            product_request['images']['image'].append({
                'url': image['url'],
                'order': idx + 1
            })
        
        # Add stock items
        for stock_item in product_data.get('stockItems', []):
            product_request['stockItems']['stockItem'].append({
                'sellerStockCode': stock_item.get('sellerStockCode', product_data['productSellerCode']),
                'optionPrice': stock_item.get('optionPrice', 0),
                'quantity': stock_item['quantity'],
                'attributes': {
                    'attribute': stock_item.get('attributes', [])
                }
            })
        
        # Add attributes
        if 'attributes' in product_data:
            product_request['attributes'] = {
                'attribute': product_data['attributes']
            }
        
        response = self._call_soap_method(
            'product',
            'SaveProduct',
            product=product_request
        )
        
        return {
            'success': response.result.status == 'success',
            'productId': getattr(response.product, 'id', None) if hasattr(response, 'product') else None,
            'message': getattr(response.result, 'errorMessage', '')
        }
    
    def get_product_by_seller_code(self, seller_code: str) -> Dict[str, Any]:
        """Get product by seller code"""
        response = self._call_soap_method(
            'product',
            'GetProductBySellerCode',
            sellerCode=seller_code
        )
        
        if hasattr(response, 'product'):
            return self._parse_product(response.product)
        
        return None
    
    def get_product_list(self, page: int = 0, size: int = 100, 
                        status: Optional[str] = None) -> Dict[str, Any]:
        """
        Get product list
        
        Args:
            page: Page number (0-based)
            size: Page size (max 100)
            status: Product status filter
        """
        pagingData = {
            'currentPage': page,
            'pageSize': min(size, 100)
        }
        
        kwargs = {'pagingData': pagingData}
        
        if status:
            kwargs['status'] = status
        
        response = self._call_soap_method(
            'product',
            'GetProductList',
            **kwargs
        )
        
        products = []
        if hasattr(response, 'products') and response.products:
            for product in response.products.product:
                products.append(self._parse_product(product))
        
        return {
            'products': products,
            'totalCount': getattr(response.pagingData, 'totalCount', 0) if hasattr(response, 'pagingData') else 0,
            'currentPage': page,
            'pageSize': size
        }
    
    def update_product_price_by_id(self, product_id: int, price: float,
                                  currency_type: int = 1) -> Dict[str, Any]:
        """Update product price by ID"""
        response = self._call_soap_method(
            'product',
            'UpdateProductPriceById',
            productId=product_id,
            price=price,
            currencyType=currency_type
        )
        
        return {
            'success': response.result.status == 'success',
            'message': getattr(response.result, 'errorMessage', '')
        }
    
    def update_product_price_by_seller_code(self, seller_code: str, price: float,
                                          currency_type: int = 1) -> Dict[str, Any]:
        """Update product price by seller code"""
        response = self._call_soap_method(
            'product',
            'UpdateProductPriceBySellerCode',
            productSellerCode=seller_code,
            price=price,
            currencyType=currency_type
        )
        
        return {
            'success': response.result.status == 'success',
            'message': getattr(response.result, 'errorMessage', '')
        }
    
    def update_stock_by_stock_attributes(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update stock by stock attributes
        
        Args:
            updates: List of stock updates containing:
                - sellerStockCode: Stock code
                - quantity: New quantity
                - version: Stock version (optional)
        """
        stockItems = {
            'stockItem': []
        }
        
        for update in updates:
            stockItems['stockItem'].append({
                'sellerStockCode': update['sellerStockCode'],
                'quantity': update['quantity'],
                'version': update.get('version', '')
            })
        
        response = self._call_soap_method(
            'product',
            'UpdateStockByStockAttributes',
            stockItems=stockItems
        )
        
        return {
            'success': response.result.status == 'success',
            'message': getattr(response.result, 'errorMessage', '')
        }
    
    def delete_product_by_seller_code(self, seller_code: str) -> Dict[str, Any]:
        """Delete product by seller code"""
        response = self._call_soap_method(
            'product',
            'DeleteProductBySellerCode',
            productSellerCode=seller_code
        )
        
        return {
            'success': response.result.status == 'success',
            'message': getattr(response.result, 'errorMessage', '')
        }
    
    # Order Management
    def get_order_list(self, 
                      status: Optional[str] = None,
                      buyer_name: Optional[str] = None,
                      order_number: Optional[str] = None,
                      product_seller_code: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      page: int = 0,
                      size: int = 100) -> Dict[str, Any]:
        """
        Get order list with filters
        
        Args:
            status: Order status (New, Approved, Rejected, Shipped, Delivered, Completed, Claimed, LATE_SHIPMENT)
            buyer_name: Buyer name filter
            order_number: Order number filter
            product_seller_code: Product seller code filter
            start_date: Start date filter
            end_date: End date filter
            page: Page number
            size: Page size
        """
        searchData = {}
        
        if status:
            searchData['status'] = status
        if buyer_name:
            searchData['buyerName'] = buyer_name
        if order_number:
            searchData['orderNumber'] = order_number
        if product_seller_code:
            searchData['productSellerCode'] = product_seller_code
        
        if start_date and end_date:
            searchData['period'] = {
                'startDate': start_date.strftime('%d/%m/%Y'),
                'endDate': end_date.strftime('%d/%m/%Y')
            }
        
        pagingData = {
            'currentPage': page,
            'pageSize': min(size, 100)
        }
        
        response = self._call_soap_method(
            'order',
            'OrderList',
            searchData=searchData,
            pagingData=pagingData
        )
        
        orders = []
        if hasattr(response, 'orderList') and response.orderList:
            for order in response.orderList.order:
                orders.append(self._parse_order(order))
        
        return {
            'orders': orders,
            'totalCount': getattr(response.pagingData, 'totalCount', 0) if hasattr(response, 'pagingData') else 0,
            'currentPage': page,
            'pageSize': size
        }
    
    def get_order_detail(self, order_id: int) -> Dict[str, Any]:
        """Get detailed order information"""
        response = self._call_soap_method(
            'order',
            'OrderDetail',
            orderRequest={'id': order_id}
        )
        
        if hasattr(response, 'orderDetail'):
            return self._parse_order_detail(response.orderDetail)
        
        return None
    
    def accept_order_item(self, order_item_id: int) -> Dict[str, Any]:
        """Accept order item"""
        response = self._call_soap_method(
            'order',
            'OrderItemAccept',
            orderItemList={'orderItem': [{'id': order_item_id}]}
        )
        
        return {
            'success': response.result.status == 'success',
            'message': getattr(response.result, 'errorMessage', '')
        }
    
    def reject_order_item(self, order_item_id: int, reject_reason: str,
                         reject_reason_type: str = 'OUT_OF_STOCK') -> Dict[str, Any]:
        """
        Reject order item
        
        Args:
            order_item_id: Order item ID
            reject_reason: Rejection reason text
            reject_reason_type: Type (OUT_OF_STOCK, OTHER)
        """
        response = self._call_soap_method(
            'order',
            'OrderItemReject',
            orderItemList={'orderItem': [{
                'id': order_item_id,
                'rejectReason': reject_reason,
                'rejectReasonType': reject_reason_type
            }]}
        )
        
        return {
            'success': response.result.status == 'success',
            'message': getattr(response.result, 'errorMessage', '')
        }
    
    def make_order_item_shipment(self, order_item_id: int,
                               shipment_company_id: int,
                               tracking_number: str,
                               shipment_method: int = 1) -> Dict[str, Any]:
        """
        Create shipment for order item
        
        Args:
            order_item_id: Order item ID
            shipment_company_id: Shipment company ID
            tracking_number: Tracking number
            shipment_method: 1=Cargo, 2=Other
        """
        response = self._call_soap_method(
            'shipment',
            'MakeOrderItemShipment',
            orderItemList={'orderItem': [{
                'id': order_item_id,
                'shipmentInfo': {
                    'shipmentCompanyId': shipment_company_id,
                    'trackingNumber': tracking_number,
                    'shipmentMethod': shipment_method
                }
            }]}
        )
        
        return {
            'success': response.result.status == 'success',
            'message': getattr(response.result, 'errorMessage', '')
        }
    
    # Shipment Management
    def get_shipment_companies(self) -> List[Dict[str, Any]]:
        """Get available shipment companies"""
        response = self._call_soap_method(
            'shipment_company',
            'GetShipmentCompanies'
        )
        
        companies = []
        if hasattr(response, 'shipmentCompanies') and response.shipmentCompanies:
            for company in response.shipmentCompanies.shipmentCompany:
                companies.append({
                    'id': company.id,
                    'name': company.name,
                    'shortName': getattr(company, 'shortName', '')
                })
        
        return companies
    
    def get_shipment_template_list(self) -> List[Dict[str, Any]]:
        """Get shipment templates"""
        response = self._call_soap_method(
            'shipment',
            'GetShipmentTemplateList'
        )
        
        templates = []
        if hasattr(response, 'shipmentTemplates') and response.shipmentTemplates:
            for template in response.shipmentTemplates.shipmentTemplate:
                templates.append({
                    'name': template.templateName,
                    'sellerShipmentCode': template.sellerShipmentCode,
                    'installmentSupported': getattr(template, 'installmentSupported', False)
                })
        
        return templates
    
    # Claim Management
    def get_claim_list(self,
                      status: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      page: int = 0,
                      size: int = 100) -> Dict[str, Any]:
        """Get claim list"""
        searchData = {}
        
        if status:
            searchData['claimStatus'] = status
        
        if start_date and end_date:
            searchData['searchPeriod'] = {
                'startDate': start_date.strftime('%d/%m/%Y'),
                'endDate': end_date.strftime('%d/%m/%Y')
            }
        
        pagingData = {
            'currentPage': page,
            'pageSize': min(size, 100)
        }
        
        response = self._call_soap_method(
            'claim',
            'ClaimList',
            searchData=searchData,
            pagingData=pagingData
        )
        
        claims = []
        if hasattr(response, 'claimList') and response.claimList:
            for claim in response.claimList.claim:
                claims.append({
                    'id': claim.id,
                    'orderId': claim.orderId,
                    'orderItemId': claim.orderItemId,
                    'claimStatus': claim.claimStatus,
                    'claimType': claim.claimType,
                    'claimReason': getattr(claim, 'claimReason', ''),
                    'createDate': claim.createDate
                })
        
        return {
            'claims': claims,
            'totalCount': getattr(response.pagingData, 'totalCount', 0) if hasattr(response, 'pagingData') else 0,
            'currentPage': page,
            'pageSize': size
        }
    
    # Return Management
    def get_return_list(self,
                       status: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       page: int = 0,
                       size: int = 100) -> Dict[str, Any]:
        """Get return list"""
        searchData = {}
        
        if status:
            searchData['returnStatus'] = status
        
        if start_date and end_date:
            searchData['searchPeriod'] = {
                'startDate': start_date.strftime('%d/%m/%Y'),
                'endDate': end_date.strftime('%d/%m/%Y')
            }
        
        pagingData = {
            'currentPage': page,
            'pageSize': min(size, 100)
        }
        
        response = self._call_soap_method(
            'return',
            'ReturnList',
            searchData=searchData,
            pagingData=pagingData
        )
        
        returns = []
        if hasattr(response, 'returnList') and response.returnList:
            for ret in response.returnList.return_:
                returns.append({
                    'id': ret.id,
                    'orderId': ret.orderId,
                    'orderItemId': ret.orderItemId,
                    'returnStatus': ret.returnStatus,
                    'returnReason': getattr(ret, 'returnReason', ''),
                    'createDate': ret.createDate
                })
        
        return {
            'returns': returns,
            'totalCount': getattr(response.pagingData, 'totalCount', 0) if hasattr(response, 'pagingData') else 0,
            'currentPage': page,
            'pageSize': size
        }
    
    # City Management
    def get_cities(self) -> List[Dict[str, Any]]:
        """Get all cities"""
        response = self._call_soap_method('city', 'GetCities')
        
        cities = []
        if hasattr(response, 'cities') and response.cities:
            for city in response.cities.city:
                cities.append({
                    'code': city.code,
                    'name': city.name
                })
        
        return cities
    
    def get_districts(self, city_code: str) -> List[Dict[str, Any]]:
        """Get districts for a city"""
        response = self._call_soap_method(
            'city',
            'GetDistricts',
            cityCode=city_code
        )
        
        districts = []
        if hasattr(response, 'districts') and response.districts:
            for district in response.districts.district:
                districts.append({
                    'id': district.id,
                    'name': district.name
                })
        
        return districts
    
    # Helper Methods
    def _parse_product(self, product) -> Dict[str, Any]:
        """Parse product object from SOAP response"""
        parsed = {
            'id': getattr(product, 'id', None),
            'productSellerCode': getattr(product, 'productSellerCode', ''),
            'title': getattr(product, 'title', ''),
            'subtitle': getattr(product, 'subtitle', ''),
            'displayPrice': getattr(product, 'displayPrice', 0),
            'price': getattr(product, 'price', 0),
            'productCondition': getattr(product, 'productCondition', ''),
            'approvalStatus': getattr(product, 'approvalStatus', ''),
            'saleStatus': getattr(product, 'saleStatus', ''),
            'stockItems': []
        }
        
        # Parse stock items
        if hasattr(product, 'stockItems') and product.stockItems:
            for stock_item in product.stockItems.stockItem:
                parsed['stockItems'].append({
                    'id': getattr(stock_item, 'id', None),
                    'sellerStockCode': getattr(stock_item, 'sellerStockCode', ''),
                    'quantity': getattr(stock_item, 'quantity', 0),
                    'version': getattr(stock_item, 'version', '')
                })
        
        return parsed
    
    def _parse_order(self, order) -> Dict[str, Any]:
        """Parse order object from SOAP response"""
        return {
            'id': order.id,
            'orderNumber': order.orderNumber,
            'createDate': order.createDate,
            'paymentType': getattr(order, 'paymentType', ''),
            'status': order.status,
            'totalAmount': getattr(order, 'totalAmount', 0),
            'buyerName': getattr(order, 'buyerName', ''),
            'citizenshipId': getattr(order, 'citizenshipId', '')
        }
    
    def _parse_order_detail(self, order_detail) -> Dict[str, Any]:
        """Parse order detail object"""
        parsed = {
            'id': order_detail.id,
            'orderNumber': order_detail.orderNumber,
            'createDate': order_detail.createDate,
            'paymentType': order_detail.paymentType,
            'status': order_detail.status,
            'totalAmount': order_detail.totalAmount,
            'buyer': {},
            'billingAddress': {},
            'shippingAddress': {},
            'items': []
        }
        
        # Parse buyer info
        if hasattr(order_detail, 'buyer'):
            parsed['buyer'] = {
                'id': order_detail.buyer.id,
                'fullName': order_detail.buyer.fullName,
                'email': getattr(order_detail.buyer, 'email', ''),
                'gsm': getattr(order_detail.buyer, 'gsm', ''),
                'tcId': getattr(order_detail.buyer, 'tcId', ''),
                'taxId': getattr(order_detail.buyer, 'taxId', ''),
                'taxOffice': getattr(order_detail.buyer, 'taxOffice', '')
            }
        
        # Parse addresses
        for addr_type in ['billingAddress', 'shippingAddress']:
            if hasattr(order_detail, addr_type):
                addr = getattr(order_detail, addr_type)
                parsed[addr_type] = {
                    'address': addr.address,
                    'fullName': addr.fullName,
                    'city': addr.city,
                    'district': getattr(addr, 'district', ''),
                    'gsm': getattr(addr, 'gsm', '')
                }
        
        # Parse order items
        if hasattr(order_detail, 'itemList') and order_detail.itemList:
            for item in order_detail.itemList.item:
                parsed['items'].append({
                    'id': item.id,
                    'productId': item.productId,
                    'productSellerCode': item.productSellerCode,
                    'productName': item.productName,
                    'price': item.price,
                    'quantity': item.quantity,
                    'shipmentInfo': {
                        'trackingNumber': getattr(item.shipmentInfo, 'trackingNumber', '') if hasattr(item, 'shipmentInfo') else '',
                        'shipmentCompanyName': getattr(item.shipmentInfo, 'shipmentCompanyName', '') if hasattr(item, 'shipmentInfo') else ''
                    },
                    'status': item.status
                })
        
        return parsed
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products using pagination"""
        all_products = []
        page = 0
        size = 100
        
        while True:
            response = self.get_product_list(page=page, size=size)
            products = response.get('products', [])
            
            if not products:
                break
            
            all_products.extend(products)
            
            if len(products) < size:
                break
            
            page += 1
        
        return all_products
    
    def get_all_orders(self, status: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get all orders using pagination"""
        all_orders = []
        page = 0
        size = 100
        
        while True:
            response = self.get_order_list(
                status=status,
                start_date=start_date,
                end_date=end_date,
                page=page,
                size=size
            )
            orders = response.get('orders', [])
            
            if not orders:
                break
            
            all_orders.extend(orders)
            
            if len(orders) < size:
                break
            
            page += 1
        
        return all_orders
    
    def format_product_for_n11(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format product data for N11 API"""
        formatted = {
            'productSellerCode': product_data.get('sku'),
            'title': product_data.get('name'),
            'subtitle': product_data.get('subtitle', ''),
            'description': product_data.get('description', ''),
            'category': {
                'id': product_data.get('category_id')
            },
            'price': float(product_data.get('price', 0)),
            'currencyType': 1,  # TL
            'images': [],
            'stockItems': [{
                'sellerStockCode': product_data.get('sku'),
                'quantity': product_data.get('stock', 0),
                'attributes': []
            }],
            'productCondition': 1,  # New
            'preparingDay': product_data.get('preparing_day', 3),
            'shipmentTemplate': product_data.get('shipment_template', '')
        }
        
        # Add images
        for image_url in product_data.get('images', []):
            formatted['images'].append({
                'url': image_url
            })
        
        # Add attributes
        if 'attributes' in product_data:
            for attr_id, attr_value_id in product_data['attributes'].items():
                formatted['stockItems'][0]['attributes'].append({
                    'attributeId': attr_id,
                    'attributeValueId': attr_value_id
                })
        
        return formatted


def test_n11_api():
    """Test N11 API functionality"""
    print("Testing N11 Marketplace API...")
    
    # Test credentials (these should come from environment variables)
    credentials = {
        'api_key': 'YOUR_API_KEY',
        'api_secret': 'YOUR_API_SECRET'
    }
    
    try:
        # Initialize API
        api = N11MarketplaceAPI(credentials)
        
        # Test connection
        if api.validate_credentials():
            print("✅ Connection successful!")
            
            # Get top level categories
            categories = api.get_top_level_categories()
            print(f"✅ Found {len(categories)} top level categories")
            
            # Get shipment companies
            companies = api.get_shipment_companies()
            print(f"✅ Found {len(companies)} shipment companies")
            
            # Get cities
            cities = api.get_cities()
            print(f"✅ Found {len(cities)} cities")
            
        else:
            print("❌ Authentication failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_n11_api()