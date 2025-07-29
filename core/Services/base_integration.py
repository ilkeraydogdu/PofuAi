"""
Base Integration Class
Tüm entegrasyonlar için temel sınıf
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from enum import Enum
import json
from cryptography.fernet import Fernet
import os

class IntegrationError(Exception):
    """Base exception for integration errors"""
    pass

class AuthenticationError(IntegrationError):
    """Authentication related errors"""
    pass

class RateLimitError(IntegrationError):
    """Rate limit exceeded errors"""
    pass

class ValidationError(IntegrationError):
    """Data validation errors"""
    pass

class APIError(IntegrationError):
    """General API errors"""
    pass

class RequestMethod(Enum):
    """HTTP request methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

class BaseIntegration(ABC):
    """Base class for all integrations"""
    
    def __init__(self, credentials: Dict[str, Any], sandbox: bool = False):
        """
        Initialize base integration
        
        Args:
            credentials: API credentials dictionary
            sandbox: Whether to use sandbox environment
        """
        self.credentials = credentials
        self.sandbox = sandbox
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Setup session with retry strategy
        self.session = self._create_session()
        
        # Rate limiting
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        # Encryption for sensitive data
        self.cipher_suite = self._get_cipher_suite()
        
        # Initialize specific integration
        self._initialize()
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Default headers
        session.headers.update({
            'User-Agent': 'MarketplaceIntegration/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        return session
    
    def _get_cipher_suite(self) -> Optional[Fernet]:
        """Get encryption cipher suite"""
        encryption_key = os.getenv('MARKETPLACE_ENCRYPTION_KEY')
        if encryption_key:
            return Fernet(encryption_key.encode())
        return None
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if self.cipher_suite:
            return self.cipher_suite.encrypt(data.encode()).decode()
        return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if self.cipher_suite:
            return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
        return encrypted_data
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_time = time.time()
        
        # Check minimum interval between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        # Check rate limit reset
        if self.rate_limit_remaining is not None and self.rate_limit_remaining <= 0:
            if self.rate_limit_reset and self.rate_limit_reset > current_time:
                wait_time = self.rate_limit_reset - current_time
                self.logger.warning(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _update_rate_limit(self, headers: Dict[str, str]):
        """Update rate limit information from response headers"""
        # Common rate limit headers
        rate_limit_headers = {
            'X-RateLimit-Remaining': 'rate_limit_remaining',
            'X-RateLimit-Reset': 'rate_limit_reset',
            'X-Rate-Limit-Remaining': 'rate_limit_remaining',
            'X-Rate-Limit-Reset': 'rate_limit_reset'
        }
        
        for header, attr in rate_limit_headers.items():
            if header in headers:
                if attr == 'rate_limit_remaining':
                    self.rate_limit_remaining = int(headers[header])
                elif attr == 'rate_limit_reset':
                    self.rate_limit_reset = int(headers[header])
    
    def make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout in seconds
            
        Returns:
            Response data as dictionary
        """
        self._check_rate_limit()
        
        url = self._build_url(endpoint)
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)
        
        try:
            self.logger.debug(f"{method.value} {url}")
            
            response = self.session.request(
                method=method.value,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
                timeout=timeout
            )
            
            # Update rate limit info
            self._update_rate_limit(response.headers)
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise APIError(f"Request failed: {str(e)}")
    
    def _handle_http_error(self, error: requests.exceptions.HTTPError):
        """Handle HTTP errors"""
        response = error.response
        status_code = response.status_code
        
        try:
            error_data = response.json()
            error_message = self._extract_error_message(error_data)
        except:
            error_message = response.text
        
        self.logger.error(f"HTTP {status_code}: {error_message}")
        
        if status_code == 401:
            raise AuthenticationError(error_message)
        elif status_code == 429:
            raise RateLimitError(error_message)
        elif status_code == 400:
            raise ValidationError(error_message)
        else:
            raise APIError(f"HTTP {status_code}: {error_message}")
    
    def _extract_error_message(self, error_data: Dict) -> str:
        """Extract error message from response data"""
        # Common error message fields
        for field in ['message', 'error', 'error_message', 'detail', 'errors']:
            if field in error_data:
                if isinstance(error_data[field], str):
                    return error_data[field]
                elif isinstance(error_data[field], list) and error_data[field]:
                    return str(error_data[field][0])
                elif isinstance(error_data[field], dict):
                    return json.dumps(error_data[field])
        
        return json.dumps(error_data)
    
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        try:
            # Make a simple API call to validate credentials
            self._test_connection()
            return True
        except AuthenticationError:
            return False
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False
    
    def paginate_results(
        self,
        fetch_function,
        page_size: int = 100,
        max_pages: Optional[int] = None,
        **kwargs
    ) -> List[Any]:
        """
        Generic pagination handler
        
        Args:
            fetch_function: Function to fetch a page of results
            page_size: Number of items per page
            max_pages: Maximum number of pages to fetch
            **kwargs: Additional arguments for fetch function
            
        Returns:
            List of all results
        """
        all_results = []
        page = 1
        
        while True:
            try:
                # Fetch page
                results = fetch_function(page=page, size=page_size, **kwargs)
                
                if not results:
                    break
                
                all_results.extend(results)
                
                # Check if we've reached max pages
                if max_pages and page >= max_pages:
                    break
                
                # Check if there are more pages
                if len(results) < page_size:
                    break
                
                page += 1
                
            except Exception as e:
                self.logger.error(f"Pagination error on page {page}: {e}")
                break
        
        return all_results
    
    def batch_operation(
        self,
        items: List[Any],
        operation_function,
        batch_size: int = 100,
        delay_between_batches: float = 0.5
    ) -> Tuple[List[Any], List[Any]]:
        """
        Process items in batches
        
        Args:
            items: List of items to process
            operation_function: Function to process a batch
            batch_size: Number of items per batch
            delay_between_batches: Delay in seconds between batches
            
        Returns:
            Tuple of (successful_results, failed_items)
        """
        successful_results = []
        failed_items = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            try:
                results = operation_function(batch)
                successful_results.extend(results)
            except Exception as e:
                self.logger.error(f"Batch operation failed: {e}")
                failed_items.extend(batch)
            
            # Delay between batches
            if i + batch_size < len(items):
                time.sleep(delay_between_batches)
        
        return successful_results, failed_items
    
    def format_datetime(self, dt: datetime) -> str:
        """Format datetime for API"""
        return dt.isoformat()
    
    def parse_datetime(self, dt_str: str) -> datetime:
        """Parse datetime from API"""
        # Try common formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        
        # If all formats fail, try ISO format
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    
    # Abstract methods to be implemented by subclasses
    @abstractmethod
    def _initialize(self):
        """Initialize specific integration settings"""
        pass
    
    @abstractmethod
    def _build_url(self, endpoint: str) -> str:
        """Build full URL for endpoint"""
        pass
    
    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        pass
    
    @abstractmethod
    def _test_connection(self) -> bool:
        """Test API connection"""
        pass