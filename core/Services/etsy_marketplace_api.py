"""
Etsy Open API v3 - Gerçek Implementasyon
Bu modül Etsy'nin resmi Open API v3'ünü kullanır.
API Dokümantasyonu: https://www.etsy.com/developers/documentation
"""

import requests
import json
import base64
import hashlib
import hmac
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from urllib.parse import urlencode, quote

class EtsyMarketplaceAPI:
    """Etsy Open API v3 Client"""
    
    def __init__(self, client_id: str, client_secret: str, access_token: str = None,
                 refresh_token: str = None, sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.sandbox = sandbox
        
        # API Base URLs
        if sandbox:
            self.base_url = "https://api.etsy.com/v3/application"
        else:
            self.base_url = "https://api.etsy.com/v3/application"
        
        self.auth_url = "https://www.etsy.com/oauth/connect"
        self.token_url = "https://api.etsy.com/v3/public/oauth/token"
        
        self.logger = logging.getLogger(__name__)
        
        # OAuth 2.0 PKCE parameters
        self.code_verifier = None
        self.code_challenge = None
        
    def _generate_pkce_pair(self) -> tuple:
        """Generate PKCE code verifier and challenge"""
        # Generate code verifier
        code_verifier = ''.join(secrets.choice(string.ascii_letters + string.digits + '-._~') for _ in range(128))
        
        # Generate code challenge
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        
        return code_verifier, code_challenge
    
    def get_authorization_url(self, redirect_uri: str, scope: str, state: str = None) -> str:
        """Get OAuth authorization URL"""
        self.code_verifier, self.code_challenge = self._generate_pkce_pair()
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
            'code_challenge': self.code_challenge,
            'code_challenge_method': 'S256'
        }
        
        if state:
            params['state'] = state
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def get_access_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'code': code,
            'code_verifier': self.code_verifier
        }
        
        try:
            response = requests.post(self.token_url, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            
            return token_data
            
        except Exception as e:
            self.logger.error(f"Token request failed: {str(e)}")
            raise
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh access token"""
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'refresh_token': self.refresh_token
        }
        
        try:
            response = requests.post(self.token_url, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            if 'refresh_token' in token_data:
                self.refresh_token = token_data.get('refresh_token')
            
            return token_data
            
        except Exception as e:
            self.logger.error(f"Token refresh failed: {str(e)}")
            raise
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, 
                     data: Dict = None, files: Dict = None) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json' if not files else None
        }
        
        # Remove Content-Type for file uploads
        if files:
            headers.pop('Content-Type', None)
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                if files:
                    response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204:
                return {'success': True}
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    self.logger.error(f"Error details: {error_data}")
                except:
                    pass
            raise Exception(f"Request failed: {str(e)}")
    
    # Shop Management
    def get_shop(self, shop_id: str) -> Dict[str, Any]:
        """Get shop details"""
        return self._make_request('GET', f'shops/{shop_id}')
    
    def get_shop_by_owner_user_id(self, user_id: str) -> Dict[str, Any]:
        """Get shop by owner user ID"""
        return self._make_request('GET', f'users/{user_id}/shops')
    
    def update_shop(self, shop_id: str, shop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update shop details"""
        return self._make_request('PUT', f'shops/{shop_id}', data=shop_data)
    
    # Listing Management
    def get_listings_by_shop(self, shop_id: str, state: str = "active", 
                           limit: int = 25, offset: int = 0) -> Dict[str, Any]:
        """Get shop listings"""
        params = {
            'state': state,
            'limit': limit,
            'offset': offset
        }
        return self._make_request('GET', f'shops/{shop_id}/listings', params=params)
    
    def get_listing(self, listing_id: str, includes: List[str] = None) -> Dict[str, Any]:
        """Get listing details"""
        params = {}
        if includes:
            params['includes'] = ','.join(includes)
        
        return self._make_request('GET', f'listings/{listing_id}', params=params)
    
    def create_draft_listing(self, shop_id: str, listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create draft listing"""
        return self._make_request('POST', f'shops/{shop_id}/listings', data=listing_data)
    
    def update_listing(self, shop_id: str, listing_id: str, 
                      listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update listing"""
        return self._make_request('PUT', f'shops/{shop_id}/listings/{listing_id}', 
                                data=listing_data)
    
    def delete_listing(self, listing_id: str) -> Dict[str, Any]:
        """Delete listing"""
        return self._make_request('DELETE', f'listings/{listing_id}')
    
    # Listing Images
    def upload_listing_image(self, shop_id: str, listing_id: str, 
                           image_file: bytes, filename: str, rank: int = 1) -> Dict[str, Any]:
        """Upload listing image"""
        files = {
            'image': (filename, image_file, 'image/jpeg')
        }
        data = {
            'rank': rank
        }
        
        return self._make_request('POST', f'shops/{shop_id}/listings/{listing_id}/images',
                                data=data, files=files)
    
    def get_listing_images(self, listing_id: str) -> Dict[str, Any]:
        """Get listing images"""
        return self._make_request('GET', f'listings/{listing_id}/images')
    
    def delete_listing_image(self, shop_id: str, listing_id: str, 
                           image_id: str) -> Dict[str, Any]:
        """Delete listing image"""
        return self._make_request('DELETE', f'shops/{shop_id}/listings/{listing_id}/images/{image_id}')
    
    # Inventory Management
    def get_listing_inventory(self, listing_id: str) -> Dict[str, Any]:
        """Get listing inventory"""
        return self._make_request('GET', f'listings/{listing_id}/inventory')
    
    def update_listing_inventory(self, listing_id: str, 
                               inventory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update listing inventory"""
        return self._make_request('PUT', f'listings/{listing_id}/inventory', 
                                data=inventory_data)
    
    # Orders and Receipts
    def get_shop_receipts(self, shop_id: str, limit: int = 25, offset: int = 0,
                         min_created: int = None, max_created: int = None) -> Dict[str, Any]:
        """Get shop receipts"""
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if min_created:
            params['min_created'] = min_created
        if max_created:
            params['max_created'] = max_created
        
        return self._make_request('GET', f'shops/{shop_id}/receipts', params=params)
    
    def get_receipt(self, shop_id: str, receipt_id: str) -> Dict[str, Any]:
        """Get receipt details"""
        return self._make_request('GET', f'shops/{shop_id}/receipts/{receipt_id}')
    
    def update_receipt(self, shop_id: str, receipt_id: str, 
                      receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update receipt"""
        return self._make_request('PUT', f'shops/{shop_id}/receipts/{receipt_id}',
                                data=receipt_data)
    
    def create_receipt_shipment(self, shop_id: str, receipt_id: str,
                              tracking_code: str, carrier_name: str) -> Dict[str, Any]:
        """Create receipt shipment"""
        data = {
            'tracking_code': tracking_code,
            'carrier_name': carrier_name
        }
        
        return self._make_request('POST', f'shops/{shop_id}/receipts/{receipt_id}/tracking',
                                data=data)
    
    # Shipping Profiles
    def get_shop_shipping_profiles(self, shop_id: str) -> Dict[str, Any]:
        """Get shop shipping profiles"""
        return self._make_request('GET', f'shops/{shop_id}/shipping-profiles')
    
    def create_shop_shipping_profile(self, shop_id: str, 
                                   profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create shipping profile"""
        return self._make_request('POST', f'shops/{shop_id}/shipping-profiles',
                                data=profile_data)
    
    def update_shop_shipping_profile(self, shop_id: str, profile_id: str,
                                   profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update shipping profile"""
        return self._make_request('PUT', f'shops/{shop_id}/shipping-profiles/{profile_id}',
                                data=profile_data)
    
    def delete_shop_shipping_profile(self, shop_id: str, profile_id: str) -> Dict[str, Any]:
        """Delete shipping profile"""
        return self._make_request('DELETE', f'shops/{shop_id}/shipping-profiles/{profile_id}')
    
    # Payment Management
    def get_shop_payment_account_ledger_entries(self, shop_id: str, 
                                              min_created: int = None,
                                              max_created: int = None,
                                              limit: int = 25,
                                              offset: int = 0) -> Dict[str, Any]:
        """Get payment ledger entries"""
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if min_created:
            params['min_created'] = min_created
        if max_created:
            params['max_created'] = max_created
        
        return self._make_request('GET', f'shops/{shop_id}/payment-account/ledger-entries',
                                params=params)
    
    def get_payments(self, shop_id: str, receipt_ids: List[str]) -> Dict[str, Any]:
        """Get payments by receipt IDs"""
        params = {
            'receipt_ids': ','.join(receipt_ids)
        }
        
        return self._make_request('GET', f'shops/{shop_id}/payments', params=params)
    
    # Shop Sections
    def get_shop_sections(self, shop_id: str) -> Dict[str, Any]:
        """Get shop sections"""
        return self._make_request('GET', f'shops/{shop_id}/sections')
    
    def create_shop_section(self, shop_id: str, title: str) -> Dict[str, Any]:
        """Create shop section"""
        data = {'title': title}
        return self._make_request('POST', f'shops/{shop_id}/sections', data=data)
    
    def update_shop_section(self, shop_id: str, section_id: str, 
                          title: str) -> Dict[str, Any]:
        """Update shop section"""
        data = {'title': title}
        return self._make_request('PUT', f'shops/{shop_id}/sections/{section_id}',
                                data=data)
    
    def delete_shop_section(self, shop_id: str, section_id: str) -> Dict[str, Any]:
        """Delete shop section"""
        return self._make_request('DELETE', f'shops/{shop_id}/sections/{section_id}')
    
    # Reviews
    def get_reviews_by_listing(self, listing_id: str, limit: int = 25,
                             offset: int = 0) -> Dict[str, Any]:
        """Get reviews for a listing"""
        params = {
            'limit': limit,
            'offset': offset
        }
        
        return self._make_request('GET', f'listings/{listing_id}/reviews', params=params)
    
    def get_reviews_by_shop(self, shop_id: str, limit: int = 25,
                          offset: int = 0) -> Dict[str, Any]:
        """Get reviews for a shop"""
        params = {
            'limit': limit,
            'offset': offset
        }
        
        return self._make_request('GET', f'shops/{shop_id}/reviews', params=params)
    
    # User Management
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user details"""
        return self._make_request('GET', f'users/{user_id}')
    
    def get_me(self) -> Dict[str, Any]:
        """Get current user details"""
        return self._make_request('GET', 'users/me')
    
    # Taxonomy
    def get_seller_taxonomy_nodes(self) -> Dict[str, Any]:
        """Get seller taxonomy"""
        return self._make_request('GET', 'seller-taxonomy/nodes')
    
    def get_buyer_taxonomy_nodes(self) -> Dict[str, Any]:
        """Get buyer taxonomy"""
        return self._make_request('GET', 'buyer-taxonomy/nodes')
    
    # Utility Methods
    def ping(self) -> Dict[str, Any]:
        """Ping API to test connection"""
        return self._make_request('GET', 'ping')
    
    def get_token_scopes(self) -> Dict[str, Any]:
        """Get current token scopes"""
        return self._make_request('GET', 'oauth/scopes')
    
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        try:
            result = self.ping()
            return result.get('application_id') is not None
        except:
            return False
    
    # Analytics and Statistics
    def get_shop_stats(self, shop_id: str) -> Dict[str, Any]:
        """Get shop statistics (requires additional permissions)"""
        # Note: This might require special permissions
        return self._make_request('GET', f'shops/{shop_id}/stats')

# Test function
def test_etsy_api():
    """Test Etsy API functionality"""
    api = EtsyMarketplaceAPI(
        client_id="test_client_id",
        client_secret="test_client_secret",
        sandbox=True
    )
    
    # Generate authorization URL
    auth_url = api.get_authorization_url(
        redirect_uri="https://example.com/callback",
        scope="listings_r listings_w shops_r shops_w",
        state="test_state"
    )
    
    print(f"Authorization URL: {auth_url}")
    print("Etsy API initialized successfully")
    return api

if __name__ == "__main__":
    test_etsy_api()