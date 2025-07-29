"""
Enterprise Integration Manager - Kurumsal Seviye Entegrasyon Yöneticisi
Bu modül, PraPazar'ın tüm entegrasyonlarını kurumsal seviyede yönetir.

Özellikler:
- Gelişmiş hata yönetimi ve recovery mekanizmaları
- Circuit breaker pattern implementasyonu
- Rate limiting ve throttling
- Comprehensive logging ve monitoring
- Security ve authentication
- Performance optimization
- Real-time monitoring ve alerting
- Multi-tenant support
- Async/await desteği
- Retry mechanisms
- Health checks
- Metrics collection
"""

import asyncio
import json
import logging
import time
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import jwt
from cryptography.fernet import Fernet
import redis
from contextlib import asynccontextmanager


class IntegrationStatus(Enum):
    """Entegrasyon durumları"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    SUSPENDED = "suspended"


class IntegrationPriority(Enum):
    """Entegrasyon öncelik seviyeleri"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IntegrationType(Enum):
    """Entegrasyon türleri"""
    MARKETPLACE = "marketplace"
    ECOMMERCE = "ecommerce"
    PAYMENT = "payment"
    SHIPPING = "shipping"
    FULFILLMENT = "fulfillment"
    ACCOUNTING = "accounting"
    INVOICE = "invoice"
    SOCIAL_MEDIA = "social_media"
    ANALYTICS = "analytics"


@dataclass
class IntegrationConfig:
    """Entegrasyon konfigürasyonu"""
    name: str
    display_name: str
    type: IntegrationType
    priority: IntegrationPriority
    status: IntegrationStatus
    api_endpoint: str
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    rate_limit: int = 1000  # requests per hour
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 300  # seconds
    health_check_interval: int = 60  # seconds
    enable_caching: bool = True
    cache_ttl: int = 300  # seconds
    enable_logging: bool = True
    enable_metrics: bool = True
    custom_headers: Optional[Dict[str, str]] = None
    webhook_url: Optional[str] = None
    features: Optional[List[str]] = None
    ai_features: Optional[List[str]] = None
    supported_countries: Optional[List[str]] = None
    supported_currencies: Optional[List[str]] = None
    is_premium: bool = False


@dataclass
class IntegrationMetrics:
    """Entegrasyon metrikleri"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_error_time: Optional[datetime] = None
    error_rate: float = 0.0
    uptime_percentage: float = 100.0
    circuit_breaker_trips: int = 0


class CircuitBreakerState(Enum):
    """Circuit breaker durumları"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Circuit breaker implementasyonu"""
    failure_threshold: int = 5
    timeout: int = 300
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None

    def should_allow_request(self) -> bool:
        """İsteğe izin verilmeli mi?"""
        now = datetime.now()
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if self.next_attempt_time and now >= self.next_attempt_time:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        else:  # HALF_OPEN
            return True

    def record_success(self):
        """Başarılı istek kaydı"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.next_attempt_time = None

    def record_failure(self):
        """Başarısız istek kaydı"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.next_attempt_time = datetime.now() + timedelta(seconds=self.timeout)


class RateLimiter:
    """Rate limiting implementasyonu"""
    
    def __init__(self, max_requests: int, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = threading.Lock()

    def is_allowed(self) -> bool:
        """Rate limit kontrolü"""
        with self.lock:
            now = time.time()
            # Eski istekleri temizle
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False

    def get_remaining_requests(self) -> int:
        """Kalan istek sayısı"""
        with self.lock:
            now = time.time()
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            return max(0, self.max_requests - len(self.requests))


class SecurityManager:
    """Güvenlik yöneticisi"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.cipher_suite = Fernet(Fernet.generate_key())
        self.token_blacklist = set()

    def encrypt_data(self, data: str) -> str:
        """Veriyi şifrele"""
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Veriyi çöz"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

    def generate_jwt_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """JWT token oluştur"""
        payload['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
        payload['iat'] = datetime.utcnow()
        payload['jti'] = str(uuid.uuid4())
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """JWT token doğrula"""
        try:
            if token in self.token_blacklist:
                return None
            
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def blacklist_token(self, token: str):
        """Token'ı blacklist'e ekle"""
        self.token_blacklist.add(token)

    def generate_api_signature(self, data: str, timestamp: str) -> str:
        """API imzası oluştur"""
        message = f"{data}{timestamp}{self.secret_key}"
        return hashlib.sha256(message.encode()).hexdigest()

    def verify_api_signature(self, data: str, timestamp: str, signature: str) -> bool:
        """API imzasını doğrula"""
        expected_signature = self.generate_api_signature(data, timestamp)
        return signature == expected_signature


class CacheManager:
    """Cache yöneticisi"""
    
    def __init__(self, redis_url: str = None):
        self.redis_client = None
        self.local_cache = {}
        self.cache_ttl = {}
        
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
            except:
                logging.warning("Redis bağlantısı başarısız, local cache kullanılıyor")

    def get(self, key: str) -> Optional[Any]:
        """Cache'den veri al"""
        try:
            if self.redis_client:
                data = self.redis_client.get(key)
                return json.loads(data) if data else None
            else:
                # Local cache
                if key in self.local_cache:
                    if key in self.cache_ttl and time.time() > self.cache_ttl[key]:
                        del self.local_cache[key]
                        del self.cache_ttl[key]
                        return None
                    return self.local_cache[key]
                return None
        except Exception as e:
            logging.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """Cache'e veri kaydet"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, ttl, json.dumps(value))
            else:
                # Local cache
                self.local_cache[key] = value
                self.cache_ttl[key] = time.time() + ttl
        except Exception as e:
            logging.error(f"Cache set error: {e}")

    def delete(self, key: str):
        """Cache'den veri sil"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                if key in self.local_cache:
                    del self.local_cache[key]
                if key in self.cache_ttl:
                    del self.cache_ttl[key]
        except Exception as e:
            logging.error(f"Cache delete error: {e}")

    def clear(self):
        """Cache'i temizle"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.local_cache.clear()
                self.cache_ttl.clear()
        except Exception as e:
            logging.error(f"Cache clear error: {e}")


class BaseEnterpriseIntegration(ABC):
    """Kurumsal entegrasyon temel sınıfı"""
    
    def __init__(self, config: IntegrationConfig, 
                 security_manager: SecurityManager,
                 cache_manager: CacheManager):
        self.config = config
        self.security_manager = security_manager
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(f"Integration.{config.name}")
        self.metrics = IntegrationMetrics()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_threshold,
            timeout=config.circuit_breaker_timeout
        )
        self.rate_limiter = RateLimiter(config.rate_limit)
        self.session = self._create_session()
        self.last_health_check = None
        self.is_healthy = True

    def _create_session(self) -> requests.Session:
        """HTTP session oluştur"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=self.config.retry_count,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Default headers
        session.headers.update({
            'User-Agent': 'PraPazar-Enterprise-Integration/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        if self.config.custom_headers:
            session.headers.update(self.config.custom_headers)
            
        return session

    async def execute_with_circuit_breaker(self, func: Callable, *args, **kwargs) -> Any:
        """Circuit breaker ile işlem yürüt"""
        if not self.circuit_breaker.should_allow_request():
            raise Exception(f"Circuit breaker is OPEN for {self.config.name}")
        
        try:
            start_time = time.time()
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Metrics güncelle
            self.metrics.successful_requests += 1
            self.metrics.last_success_time = datetime.now()
            response_time = time.time() - start_time
            self._update_avg_response_time(response_time)
            
            self.circuit_breaker.record_success()
            return result
            
        except Exception as e:
            self.metrics.failed_requests += 1
            self.metrics.last_error_time = datetime.now()
            self.circuit_breaker.record_failure()
            self.logger.error(f"Integration {self.config.name} failed: {e}")
            raise

    def _update_avg_response_time(self, response_time: float):
        """Ortalama response time güncelle"""
        total_requests = self.metrics.total_requests + 1
        current_avg = self.metrics.avg_response_time
        self.metrics.avg_response_time = ((current_avg * self.metrics.total_requests) + response_time) / total_requests
        self.metrics.total_requests = total_requests

    def _check_rate_limit(self) -> bool:
        """Rate limit kontrolü"""
        return self.rate_limiter.is_allowed()

    async def health_check(self) -> bool:
        """Sağlık kontrolü"""
        try:
            # Basit ping isteği
            response = self.session.get(f"{self.config.api_endpoint}/health", timeout=5)
            self.is_healthy = response.status_code == 200
            self.last_health_check = datetime.now()
            return self.is_healthy
        except:
            self.is_healthy = False
            self.last_health_check = datetime.now()
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Metrikleri al"""
        self.metrics.error_rate = (
            self.metrics.failed_requests / max(self.metrics.total_requests, 1) * 100
        )
        return asdict(self.metrics)

    @abstractmethod
    async def connect(self) -> bool:
        """Entegrasyona bağlan"""
        pass

    @abstractmethod
    async def get_products(self, **kwargs) -> List[Dict]:
        """Ürünleri getir"""
        pass

    @abstractmethod
    async def update_stock(self, product_id: str, stock: int) -> bool:
        """Stok güncelle"""
        pass

    @abstractmethod
    async def update_price(self, product_id: str, price: float) -> bool:
        """Fiyat güncelle"""
        pass

    @abstractmethod
    async def get_orders(self, **kwargs) -> List[Dict]:
        """Siparişleri getir"""
        pass


class TrendyolEnterpriseIntegration(BaseEnterpriseIntegration):
    """Trendyol Kurumsal Entegrasyonu"""
    
    async def connect(self) -> bool:
        """Trendyol API'ye bağlan"""
        if not self._check_rate_limit():
            raise Exception("Rate limit exceeded")
            
        async def _connect():
            headers = {
                'Authorization': f'Basic {self.config.api_key}:{self.config.secret_key}',
                'User-Agent': 'PraPazar-Trendyol-Integration/1.0'
            }
            
            response = self.session.get(
                f"{self.config.api_endpoint}/suppliers/check-status",
                headers=headers,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                self.logger.info("Trendyol entegrasyonu başarıyla bağlandı")
                return True
            else:
                raise Exception(f"Trendyol connection failed: {response.status_code}")
        
        return await self.execute_with_circuit_breaker(_connect)

    async def get_products(self, **kwargs) -> List[Dict]:
        """Trendyol ürünlerini getir"""
        cache_key = f"trendyol_products_{hashlib.md5(str(kwargs).encode()).hexdigest()}"
        
        # Cache kontrol
        if self.config.enable_caching:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                return cached_data

        async def _get_products():
            headers = {
                'Authorization': f'Basic {self.config.api_key}:{self.config.secret_key}'
            }
            
            params = {
                'page': kwargs.get('page', 0),
                'size': kwargs.get('size', 50)
            }
            
            response = self.session.get(
                f"{self.config.api_endpoint}/suppliers/products",
                headers=headers,
                params=params,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('content', [])
                
                # Cache'e kaydet
                if self.config.enable_caching:
                    self.cache_manager.set(cache_key, products, self.config.cache_ttl)
                
                self.logger.info(f"Trendyol'dan {len(products)} ürün getirildi")
                return products
            else:
                raise Exception(f"Trendyol get products failed: {response.status_code}")
        
        return await self.execute_with_circuit_breaker(_get_products)

    async def update_stock(self, product_id: str, stock: int) -> bool:
        """Trendyol stok güncelle"""
        async def _update_stock():
            headers = {
                'Authorization': f'Basic {self.config.api_key}:{self.config.secret_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'items': [{
                    'barcode': product_id,
                    'quantity': stock
                }]
            }
            
            response = self.session.post(
                f"{self.config.api_endpoint}/suppliers/stock-updates",
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Trendyol stok güncellendi: {product_id} -> {stock}")
                return True
            else:
                raise Exception(f"Trendyol stock update failed: {response.status_code}")
        
        return await self.execute_with_circuit_breaker(_update_stock)

    async def update_price(self, product_id: str, price: float) -> bool:
        """Trendyol fiyat güncelle"""
        async def _update_price():
            headers = {
                'Authorization': f'Basic {self.config.api_key}:{self.config.secret_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'items': [{
                    'barcode': product_id,
                    'salePrice': price,
                    'listPrice': price * 1.1  # %10 liste fiyatı marjı
                }]
            }
            
            response = self.session.post(
                f"{self.config.api_endpoint}/suppliers/price-updates",
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Trendyol fiyat güncellendi: {product_id} -> {price}")
                return True
            else:
                raise Exception(f"Trendyol price update failed: {response.status_code}")
        
        return await self.execute_with_circuit_breaker(_update_price)

    async def get_orders(self, **kwargs) -> List[Dict]:
        """Trendyol siparişlerini getir"""
        cache_key = f"trendyol_orders_{hashlib.md5(str(kwargs).encode()).hexdigest()}"
        
        # Cache kontrol
        if self.config.enable_caching:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                return cached_data

        async def _get_orders():
            headers = {
                'Authorization': f'Basic {self.config.api_key}:{self.config.secret_key}'
            }
            
            params = {
                'page': kwargs.get('page', 0),
                'size': kwargs.get('size', 50),
                'orderByField': 'PackageLastModifiedDate',
                'orderByDirection': 'DESC'
            }
            
            # Tarih filtresi
            if 'start_date' in kwargs:
                params['startDate'] = kwargs['start_date']
            if 'end_date' in kwargs:
                params['endDate'] = kwargs['end_date']
            
            response = self.session.get(
                f"{self.config.api_endpoint}/suppliers/orders",
                headers=headers,
                params=params,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('content', [])
                
                # Cache'e kaydet
                if self.config.enable_caching:
                    self.cache_manager.set(cache_key, orders, 60)  # 1 dakika cache
                
                self.logger.info(f"Trendyol'dan {len(orders)} sipariş getirildi")
                return orders
            else:
                raise Exception(f"Trendyol get orders failed: {response.status_code}")
        
        return await self.execute_with_circuit_breaker(_get_orders)


class HepsiburadaEnterpriseIntegration(BaseEnterpriseIntegration):
    """Hepsiburada Kurumsal Entegrasyonu"""
    
    async def connect(self) -> bool:
        """Hepsiburada API'ye bağlan"""
        if not self._check_rate_limit():
            raise Exception("Rate limit exceeded")
            
        async def _connect():
            headers = {
                'Authorization': f'Bearer {self.config.api_key}',
                'User-Agent': 'PraPazar-Hepsiburada-Integration/1.0'
            }
            
            response = self.session.get(
                f"{self.config.api_endpoint}/merchants/me",
                headers=headers,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                self.logger.info("Hepsiburada entegrasyonu başarıyla bağlandı")
                return True
            else:
                raise Exception(f"Hepsiburada connection failed: {response.status_code}")
        
        return await self.execute_with_circuit_breaker(_connect)

    async def get_products(self, **kwargs) -> List[Dict]:
        """Hepsiburada ürünlerini getir"""
        cache_key = f"hepsiburada_products_{hashlib.md5(str(kwargs).encode()).hexdigest()}"
        
        if self.config.enable_caching:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                return cached_data

        async def _get_products():
            headers = {
                'Authorization': f'Bearer {self.config.api_key}'
            }
            
            params = {
                'offset': kwargs.get('offset', 0),
                'limit': kwargs.get('limit', 50)
            }
            
            response = self.session.get(
                f"{self.config.api_endpoint}/products",
                headers=headers,
                params=params,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('listings', [])
                
                if self.config.enable_caching:
                    self.cache_manager.set(cache_key, products, self.config.cache_ttl)
                
                self.logger.info(f"Hepsiburada'dan {len(products)} ürün getirildi")
                return products
            else:
                raise Exception(f"Hepsiburada get products failed: {response.status_code}")
        
        return await self.execute_with_circuit_breaker(_get_products)

    async def update_stock(self, product_id: str, stock: int) -> bool:
        """Hepsiburada stok güncelle"""
        async def _update_stock():
            headers = {
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'merchantSku': product_id,
                'availableStock': stock
            }
            
            response = self.session.put(
                f"{self.config.api_endpoint}/products/{product_id}/price-inventory",
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code in [200, 204]:
                self.logger.info(f"Hepsiburada stok güncellendi: {product_id} -> {stock}")
                return True
            else:
                raise Exception(f"Hepsiburada stock update failed: {response.status_code}")
        
        return await self.execute_with_circuit_breaker(_update_stock)

    async def update_price(self, product_id: str, price: float) -> bool:
        """Hepsiburada fiyat güncelle"""
        async def _update_price():
            headers = {
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'merchantSku': product_id,
                'price': price
            }
            
            response = self.session.put(
                f"{self.config.api_endpoint}/products/{product_id}/price-inventory",
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code in [200, 204]:
                self.logger.info(f"Hepsiburada fiyat güncellendi: {product_id} -> {price}")
                return True
            else:
                raise Exception(f"Hepsiburada price update failed: {response.status_code}")
        
        return await self.execute_with_circuit_breaker(_update_price)

    async def get_orders(self, **kwargs) -> List[Dict]:
        """Hepsiburada siparişlerini getir"""
        cache_key = f"hepsiburada_orders_{hashlib.md5(str(kwargs).encode()).hexdigest()}"
        
        if self.config.enable_caching:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                return cached_data

        async def _get_orders():
            headers = {
                'Authorization': f'Bearer {self.config.api_key}'
            }
            
            params = {
                'offset': kwargs.get('offset', 0),
                'limit': kwargs.get('limit', 50)
            }
            
            # Durum filtresi
            if 'status' in kwargs:
                params['status'] = kwargs['status']
            
            response = self.session.get(
                f"{self.config.api_endpoint}/orders",
                headers=headers,
                params=params,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('orders', [])
                
                if self.config.enable_caching:
                    self.cache_manager.set(cache_key, orders, 60)
                
                self.logger.info(f"Hepsiburada'dan {len(orders)} sipariş getirildi")
                return orders
            else:
                raise Exception(f"Hepsiburada get orders failed: {response.status_code}")
        
        return await self.execute_with_circuit_breaker(_get_orders)


class EnterpriseIntegrationManager:
    """Kurumsal Entegrasyon Yöneticisi"""
    
    def __init__(self, secret_key: str, redis_url: str = None):
        self.integrations: Dict[str, BaseEnterpriseIntegration] = {}
        self.security_manager = SecurityManager(secret_key)
        self.cache_manager = CacheManager(redis_url)
        self.logger = logging.getLogger("EnterpriseIntegrationManager")
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.health_check_interval = 60
        self.monitoring_enabled = True
        self._setup_logging()

    def _setup_logging(self):
        """Logging ayarlarını yap"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('integration_logs.log'),
                logging.StreamHandler()
            ]
        )

    def register_integration(self, config: IntegrationConfig) -> bool:
        """Entegrasyon kaydet"""
        try:
            # Entegrasyon türüne göre uygun sınıfı seç
            integration_classes = {
                'trendyol': TrendyolEnterpriseIntegration,
                'hepsiburada': HepsiburadaEnterpriseIntegration,
                # Diğer entegrasyonlar buraya eklenecek
            }
            
            integration_class = integration_classes.get(config.name)
            if not integration_class:
                # Generic integration kullan
                integration_class = BaseEnterpriseIntegration
            
            integration = integration_class(config, self.security_manager, self.cache_manager)
            self.integrations[config.name] = integration
            
            self.logger.info(f"Entegrasyon kaydedildi: {config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Entegrasyon kayıt hatası {config.name}: {e}")
            return False

    async def initialize_all(self) -> Dict[str, bool]:
        """Tüm entegrasyonları başlat"""
        results = {}
        tasks = []
        
        for name, integration in self.integrations.items():
            if integration.config.status == IntegrationStatus.ACTIVE:
                task = asyncio.create_task(self._initialize_integration(name, integration))
                tasks.append(task)
        
        if tasks:
            completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, (name, _) in enumerate(self.integrations.items()):
                if i < len(completed_tasks):
                    result = completed_tasks[i]
                    if isinstance(result, Exception):
                        results[name] = False
                        self.logger.error(f"❌ {name} başlatma hatası: {result}")
                    else:
                        results[name] = result
                        status = "✅" if result else "❌"
                        self.logger.info(f"{status} {name} {'başarıyla başlatıldı' if result else 'başlatılamadı'}")
        
        return results

    async def _initialize_integration(self, name: str, integration: BaseEnterpriseIntegration) -> bool:
        """Tekil entegrasyon başlat"""
        try:
            return await integration.connect()
        except Exception as e:
            self.logger.error(f"Integration {name} initialization failed: {e}")
            return False

    async def sync_all_products(self, **kwargs) -> Dict[str, List[Dict]]:
        """Tüm entegrasyonlardan ürünleri senkronize et"""
        results = {}
        tasks = []
        
        for name, integration in self.integrations.items():
            if integration.config.status == IntegrationStatus.ACTIVE:
                task = asyncio.create_task(self._sync_products(name, integration, **kwargs))
                tasks.append(task)
        
        if tasks:
            completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, (name, _) in enumerate(self.integrations.items()):
                if i < len(completed_tasks):
                    result = completed_tasks[i]
                    if isinstance(result, Exception):
                        results[name] = []
                        self.logger.error(f"Product sync error for {name}: {result}")
                    else:
                        results[name] = result
        
        return results

    async def _sync_products(self, name: str, integration: BaseEnterpriseIntegration, **kwargs) -> List[Dict]:
        """Tekil entegrasyon ürün senkronizasyonu"""
        try:
            products = await integration.get_products(**kwargs)
            for product in products:
                product['source'] = name
                product['sync_time'] = datetime.now().isoformat()
            return products
        except Exception as e:
            self.logger.error(f"Product sync failed for {name}: {e}")
            return []

    async def update_all_stocks(self, product_mapping: Dict[str, str], stock: int) -> Dict[str, bool]:
        """Tüm entegrasyonlarda stok güncelle"""
        results = {}
        tasks = []
        
        for name, integration in self.integrations.items():
            if integration.config.status == IntegrationStatus.ACTIVE and name in product_mapping:
                product_id = product_mapping[name]
                task = asyncio.create_task(self._update_stock(name, integration, product_id, stock))
                tasks.append(task)
        
        if tasks:
            completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, (name, _) in enumerate(self.integrations.items()):
                if i < len(completed_tasks):
                    result = completed_tasks[i]
                    results[name] = not isinstance(result, Exception) and result
        
        return results

    async def _update_stock(self, name: str, integration: BaseEnterpriseIntegration, 
                          product_id: str, stock: int) -> bool:
        """Tekil entegrasyon stok güncelleme"""
        try:
            return await integration.update_stock(product_id, stock)
        except Exception as e:
            self.logger.error(f"Stock update failed for {name}: {e}")
            return False

    async def update_all_prices(self, product_mapping: Dict[str, str], price: float) -> Dict[str, bool]:
        """Tüm entegrasyonlarda fiyat güncelle"""
        results = {}
        tasks = []
        
        for name, integration in self.integrations.items():
            if integration.config.status == IntegrationStatus.ACTIVE and name in product_mapping:
                product_id = product_mapping[name]
                task = asyncio.create_task(self._update_price(name, integration, product_id, price))
                tasks.append(task)
        
        if tasks:
            completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, (name, _) in enumerate(self.integrations.items()):
                if i < len(completed_tasks):
                    result = completed_tasks[i]
                    results[name] = not isinstance(result, Exception) and result
        
        return results

    async def _update_price(self, name: str, integration: BaseEnterpriseIntegration, 
                          product_id: str, price: float) -> bool:
        """Tekil entegrasyon fiyat güncelleme"""
        try:
            return await integration.update_price(product_id, price)
        except Exception as e:
            self.logger.error(f"Price update failed for {name}: {e}")
            return False

    async def get_all_orders(self, **kwargs) -> Dict[str, List[Dict]]:
        """Tüm entegrasyonlardan siparişleri getir"""
        results = {}
        tasks = []
        
        for name, integration in self.integrations.items():
            if integration.config.status == IntegrationStatus.ACTIVE:
                task = asyncio.create_task(self._get_orders(name, integration, **kwargs))
                tasks.append(task)
        
        if tasks:
            completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, (name, _) in enumerate(self.integrations.items()):
                if i < len(completed_tasks):
                    result = completed_tasks[i]
                    if isinstance(result, Exception):
                        results[name] = []
                        self.logger.error(f"Order sync error for {name}: {result}")
                    else:
                        results[name] = result
        
        return results

    async def _get_orders(self, name: str, integration: BaseEnterpriseIntegration, **kwargs) -> List[Dict]:
        """Tekil entegrasyon sipariş getirme"""
        try:
            orders = await integration.get_orders(**kwargs)
            for order in orders:
                order['source'] = name
                order['sync_time'] = datetime.now().isoformat()
            return orders
        except Exception as e:
            self.logger.error(f"Order sync failed for {name}: {e}")
            return []

    def get_integration_status(self) -> Dict[str, Any]:
        """Entegrasyon durumlarını getir"""
        status = {
            'total_integrations': len(self.integrations),
            'active_integrations': sum(1 for i in self.integrations.values() 
                                     if i.config.status == IntegrationStatus.ACTIVE),
            'healthy_integrations': sum(1 for i in self.integrations.values() if i.is_healthy),
            'integrations': {},
            'summary': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }
        
        for name, integration in self.integrations.items():
            metrics = integration.get_metrics()
            status['integrations'][name] = {
                'status': integration.config.status.value,
                'priority': integration.config.priority.value,
                'type': integration.config.type.value,
                'is_healthy': integration.is_healthy,
                'last_health_check': integration.last_health_check.isoformat() if integration.last_health_check else None,
                'circuit_breaker_state': integration.circuit_breaker.state.value,
                'metrics': metrics,
                'rate_limit_remaining': integration.rate_limiter.get_remaining_requests()
            }
            
            # Özet istatistikler
            priority = integration.config.priority.value
            if priority in status['summary']:
                status['summary'][priority] += 1
        
        return status

    async def health_check_all(self) -> Dict[str, bool]:
        """Tüm entegrasyonların sağlık kontrolü"""
        results = {}
        tasks = []
        
        for name, integration in self.integrations.items():
            task = asyncio.create_task(integration.health_check())
            tasks.append((name, task))
        
        for name, task in tasks:
            try:
                result = await task
                results[name] = result
                if not result:
                    self.logger.warning(f"Health check failed for {name}")
            except Exception as e:
                results[name] = False
                self.logger.error(f"Health check error for {name}: {e}")
        
        return results

    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Kapsamlı metrikler"""
        total_requests = sum(i.metrics.total_requests for i in self.integrations.values())
        total_successful = sum(i.metrics.successful_requests for i in self.integrations.values())
        total_failed = sum(i.metrics.failed_requests for i in self.integrations.values())
        
        return {
            'overview': {
                'total_requests': total_requests,
                'successful_requests': total_successful,
                'failed_requests': total_failed,
                'overall_success_rate': (total_successful / max(total_requests, 1)) * 100,
                'total_integrations': len(self.integrations),
                'healthy_integrations': sum(1 for i in self.integrations.values() if i.is_healthy)
            },
            'by_integration': {
                name: integration.get_metrics() 
                for name, integration in self.integrations.items()
            },
            'by_priority': self._get_metrics_by_priority(),
            'by_type': self._get_metrics_by_type()
        }

    def _get_metrics_by_priority(self) -> Dict[str, Dict[str, Any]]:
        """Öncelik bazında metrikler"""
        priority_metrics = {}
        
        for integration in self.integrations.values():
            priority = integration.config.priority.value
            if priority not in priority_metrics:
                priority_metrics[priority] = {
                    'count': 0,
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'avg_response_time': 0.0
                }
            
            metrics = priority_metrics[priority]
            metrics['count'] += 1
            metrics['total_requests'] += integration.metrics.total_requests
            metrics['successful_requests'] += integration.metrics.successful_requests
            metrics['failed_requests'] += integration.metrics.failed_requests
            metrics['avg_response_time'] += integration.metrics.avg_response_time
        
        # Ortalamaları hesapla
        for priority, metrics in priority_metrics.items():
            if metrics['count'] > 0:
                metrics['avg_response_time'] /= metrics['count']
                metrics['success_rate'] = (metrics['successful_requests'] / max(metrics['total_requests'], 1)) * 100
        
        return priority_metrics

    def _get_metrics_by_type(self) -> Dict[str, Dict[str, Any]]:
        """Tür bazında metrikler"""
        type_metrics = {}
        
        for integration in self.integrations.values():
            integration_type = integration.config.type.value
            if integration_type not in type_metrics:
                type_metrics[integration_type] = {
                    'count': 0,
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'avg_response_time': 0.0
                }
            
            metrics = type_metrics[integration_type]
            metrics['count'] += 1
            metrics['total_requests'] += integration.metrics.total_requests
            metrics['successful_requests'] += integration.metrics.successful_requests
            metrics['failed_requests'] += integration.metrics.failed_requests
            metrics['avg_response_time'] += integration.metrics.avg_response_time
        
        # Ortalamaları hesapla
        for integration_type, metrics in type_metrics.items():
            if metrics['count'] > 0:
                metrics['avg_response_time'] /= metrics['count']
                metrics['success_rate'] = (metrics['successful_requests'] / max(metrics['total_requests'], 1)) * 100
        
        return type_metrics

    async def start_monitoring(self):
        """Monitoring başlat"""
        if not self.monitoring_enabled:
            return
        
        while self.monitoring_enabled:
            try:
                # Health check
                await self.health_check_all()
                
                # Metrics log
                metrics = self.get_comprehensive_metrics()
                self.logger.info(f"System Metrics: {json.dumps(metrics['overview'], indent=2)}")
                
                # Circuit breaker durumları
                for name, integration in self.integrations.items():
                    if integration.circuit_breaker.state != CircuitBreakerState.CLOSED:
                        self.logger.warning(f"Circuit breaker {integration.circuit_breaker.state.value} for {name}")
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.health_check_interval)

    def stop_monitoring(self):
        """Monitoring durdur"""
        self.monitoring_enabled = False

    def shutdown(self):
        """Sistem kapatma"""
        self.logger.info("Enterprise Integration Manager kapatılıyor...")
        
        # Monitoring durdur
        self.stop_monitoring()
        
        # Thread pool kapat
        self.executor.shutdown(wait=True)
        
        # Cache temizle
        self.cache_manager.clear()
        
        self.logger.info("Enterprise Integration Manager kapatıldı")


# Factory pattern for integration creation
class EnterpriseIntegrationFactory:
    """Kurumsal entegrasyon fabrikası"""
    
    @staticmethod
    def create_integration_config(name: str, **kwargs) -> IntegrationConfig:
        """Entegrasyon konfigürasyonu oluştur"""
        
        # Önceden tanımlı konfigürasyonlar
        predefined_configs = {
            'trendyol': {
                'display_name': 'Trendyol',
                'type': IntegrationType.MARKETPLACE,
                'priority': IntegrationPriority.CRITICAL,
                'api_endpoint': 'https://api.trendyol.com/sapigw/suppliers',
                'rate_limit': 1000,
                'features': ['products', 'orders', 'stock', 'price'],
                'ai_features': ['smart_pricing', 'demand_forecast'],
                'supported_countries': ['TR'],
                'supported_currencies': ['TRY']
            },
            'hepsiburada': {
                'display_name': 'Hepsiburada',
                'type': IntegrationType.MARKETPLACE,
                'priority': IntegrationPriority.CRITICAL,
                'api_endpoint': 'https://mpop-sit.hepsiburada.com',
                'rate_limit': 800,
                'features': ['products', 'orders', 'stock', 'price'],
                'ai_features': ['competitor_analysis', 'sales_prediction'],
                'supported_countries': ['TR'],
                'supported_currencies': ['TRY']
            }
        }
        
        base_config = predefined_configs.get(name, {
            'display_name': name.title(),
            'type': IntegrationType.MARKETPLACE,
            'priority': IntegrationPriority.MEDIUM,
            'api_endpoint': f'https://api.{name}.com',
            'rate_limit': 500
        })
        
        # Override with provided kwargs
        base_config.update(kwargs)
        base_config['name'] = name
        base_config['status'] = IntegrationStatus.INACTIVE
        
        return IntegrationConfig(**base_config)


# Global instance
_enterprise_manager = None

def get_enterprise_integration_manager(secret_key: str = None, redis_url: str = None) -> EnterpriseIntegrationManager:
    """Global enterprise integration manager instance"""
    global _enterprise_manager
    if _enterprise_manager is None:
        if not secret_key:
            secret_key = "your-super-secret-key-change-this-in-production"
        _enterprise_manager = EnterpriseIntegrationManager(secret_key, redis_url)
    return _enterprise_manager


# Example usage and test function
async def main():
    """Ana test fonksiyonu"""
    
    print("🚀 Enterprise Integration Manager başlatılıyor...\n")
    
    # Manager oluştur
    manager = get_enterprise_integration_manager(
        secret_key="super-secret-enterprise-key-2025",
        redis_url=None  # Local cache kullanılacak
    )
    
    # Kritik entegrasyonları kaydet
    critical_integrations = [
        ('trendyol', {'api_key': 'your_trendyol_api_key', 'secret_key': 'your_trendyol_secret'}),
        ('hepsiburada', {'api_key': 'your_hepsiburada_api_key'}),
    ]
    
    for name, credentials in critical_integrations:
        config = EnterpriseIntegrationFactory.create_integration_config(
            name, 
            status=IntegrationStatus.ACTIVE,
            **credentials
        )
        success = manager.register_integration(config)
        print(f"{'✅' if success else '❌'} {name} entegrasyonu {'kaydedildi' if success else 'kaydedilemedi'}")
    
    print("\n📊 Entegrasyon durumu:")
    status = manager.get_integration_status()
    print(f"   Toplam: {status['total_integrations']}")
    print(f"   Aktif: {status['active_integrations']}")
    print(f"   Sağlıklı: {status['healthy_integrations']}")
    
    # Entegrasyonları başlat
    print("\n🔌 Entegrasyonlar başlatılıyor...")
    results = await manager.initialize_all()
    
    for name, result in results.items():
        print(f"   {'✅' if result else '❌'} {name}: {'Başarılı' if result else 'Başarısız'}")
    
    # Sağlık kontrolü
    print("\n🏥 Sağlık kontrolü yapılıyor...")
    health_results = await manager.health_check_all()
    
    for name, healthy in health_results.items():
        print(f"   {'💚' if healthy else '💔'} {name}: {'Sağlıklı' if healthy else 'Sorunlu'}")
    
    # Kapsamlı metrikler
    print("\n📈 Sistem metrikleri:")
    metrics = manager.get_comprehensive_metrics()
    overview = metrics['overview']
    print(f"   Toplam İstek: {overview['total_requests']}")
    print(f"   Başarı Oranı: %{overview['overall_success_rate']:.1f}")
    print(f"   Sağlıklı Entegrasyon: {overview['healthy_integrations']}/{overview['total_integrations']}")
    
    # Monitoring başlat (background)
    print("\n👁️  Monitoring başlatılıyor...")
    monitoring_task = asyncio.create_task(manager.start_monitoring())
    
    # 10 saniye bekle
    await asyncio.sleep(10)
    
    # Monitoring durdur
    manager.stop_monitoring()
    
    # Sistem kapat
    manager.shutdown()
    
    print("\n✅ Enterprise Integration Manager test tamamlandı!")


if __name__ == "__main__":
    # Logging ayarla
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ana fonksiyonu çalıştır
    asyncio.run(main())