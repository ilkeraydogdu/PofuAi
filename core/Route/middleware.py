"""
Route Middleware
Route sistemine middleware desteği
"""
from typing import Dict, Any, Callable, Optional, List
import time
from functools import wraps

class RouteMiddleware:
    """Route Middleware temel sınıfı"""
    
    def __init__(self):
        """Middleware sınıfını başlat"""
        pass
    
    def handle(self, request: Any, next_handler: Callable) -> Any:
        """
        Middleware işlem fonksiyonu
        
        Args:
            request: HTTP isteği
            next_handler: Bir sonraki middleware veya handler
            
        Returns:
            Any: İşlenen yanıt
        """
        # Middleware işlemini uygula
        # Bu temel sınıfta sadece bir sonraki işleyiciyi çağır
        return next_handler(request)
    
    def terminate(self, request: Any, response: Any) -> None:
        """
        İstek işlendikten sonra çalışan sonlandırma fonksiyonu
        
        Args:
            request: HTTP isteği
            response: HTTP yanıtı
        """
        pass

class AuthMiddleware(RouteMiddleware):
    """Kimlik doğrulama middleware'i"""
    
    def handle(self, request: Any, next_handler: Callable) -> Any:
        """
        Kullanıcı kimlik doğrulamasını kontrol et
        
        Args:
            request: HTTP isteği
            next_handler: Bir sonraki middleware veya handler
            
        Returns:
            Any: İşlenen yanıt
        """
        # Session üzerinden kimlik kontrolü
        try:
            from flask import session, redirect, url_for
            
            # Session'da auth key kontrolü
            if not session.get('auth'):
                # Login sayfasına yönlendir
                return redirect(url_for('auth_login'))
                
            # Kullanıcı doğrulandı, devam et
            return next_handler(request)
            
        except ImportError:
            # Flask import edilemedi, basit kontrol
            if hasattr(request, 'session') and not request.session.get('auth'):
                # Redirect için json yanıt
                return {
                    'status': 'error',
                    'message': 'Unauthorized',
                    'code': 401,
                    'redirect': '/auth/login'
                }
            
            return next_handler(request)

class GuestMiddleware(RouteMiddleware):
    """Misafir kullanıcı middleware'i"""
    
    def handle(self, request: Any, next_handler: Callable) -> Any:
        """
        Sadece misafir kullanıcıların erişebileceği route'lar için kontrol
        
        Args:
            request: HTTP isteği
            next_handler: Bir sonraki middleware veya handler
            
        Returns:
            Any: İşlenen yanıt
        """
        # Session üzerinden kimlik kontrolü
        try:
            from flask import session, redirect, url_for
            
            # Session'da auth key kontrolü (kullanıcı giriş yapmışsa)
            if session.get('auth'):
                # Ana sayfaya yönlendir
                return redirect(url_for('home'))
                
            # Kullanıcı misafir, devam et
            return next_handler(request)
            
        except ImportError:
            # Flask import edilemedi, basit kontrol
            if hasattr(request, 'session') and request.session.get('auth'):
                # Redirect için json yanıt
                return {
                    'status': 'error',
                    'message': 'Already authenticated',
                    'code': 400,
                    'redirect': '/'
                }
            
            return next_handler(request)

class AdminMiddleware(RouteMiddleware):
    """Admin kullanıcı middleware'i"""
    
    def handle(self, request: Any, next_handler: Callable) -> Any:
        """
        Sadece admin kullanıcıların erişebileceği route'lar için kontrol
        
        Args:
            request: HTTP isteği
            next_handler: Bir sonraki middleware veya handler
            
        Returns:
            Any: İşlenen yanıt
        """
        # Session üzerinden admin kontrolü
        try:
            from flask import session, redirect, url_for
            
            # Session'da auth ve admin key kontrolü
            if not session.get('auth') or not session.get('is_admin'):
                # Login sayfasına yönlendir
                return redirect(url_for('auth_login'))
                
            # Admin kullanıcı, devam et
            return next_handler(request)
            
        except ImportError:
            # Flask import edilemedi, basit kontrol
            if (not hasattr(request, 'session') or 
                not request.session.get('auth') or 
                not request.session.get('is_admin')):
                # Redirect için json yanıt
                return {
                    'status': 'error',
                    'message': 'Unauthorized for admin',
                    'code': 403,
                    'redirect': '/auth/login'
                }
            
            return next_handler(request)

class CORSMiddleware(RouteMiddleware):
    """CORS (Cross-Origin Resource Sharing) middleware"""
    
    def __init__(self, allowed_origins: List[str] = None, 
                 allowed_methods: List[str] = None,
                 allowed_headers: List[str] = None):
        """
        CORS middleware başlat
        
        Args:
            allowed_origins: İzin verilen originler ['*', 'https://example.com']
            allowed_methods: İzin verilen HTTP metodları ['GET', 'POST', 'PUT', 'DELETE']
            allowed_headers: İzin verilen HTTP başlıkları ['Content-Type', 'Authorization']
        """
        super().__init__()
        self.allowed_origins = allowed_origins or ['*']
        self.allowed_methods = allowed_methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        self.allowed_headers = allowed_headers or ['Content-Type', 'X-Requested-With', 'Authorization']
    
    def handle(self, request: Any, next_handler: Callable) -> Any:
        """
        CORS başlıklarını ekle
        
        Args:
            request: HTTP isteği
            next_handler: Bir sonraki middleware veya handler
            
        Returns:
            Any: İşlenen yanıt
        """
        try:
            from flask import request as flask_request, Response, make_response
            
            # CORS OPTIONS isteği kontrolü
            if flask_request.method == 'OPTIONS':
                response = make_response()
                response.headers.add('Access-Control-Allow-Origin', self._get_origin_header())
                response.headers.add('Access-Control-Allow-Methods', ', '.join(self.allowed_methods))
                response.headers.add('Access-Control-Allow-Headers', ', '.join(self.allowed_headers))
                response.headers.add('Access-Control-Max-Age', '86400')  # 24 saat
                return response
                
            # Normal istek için devam et
            response = next_handler(request)
            
            # Response nesnesine dönüştür
            if not isinstance(response, Response):
                response = make_response(response)
                
            # CORS başlıkları ekle
            response.headers.add('Access-Control-Allow-Origin', self._get_origin_header())
            return response
            
        except ImportError:
            # Flask import edilemedi, normal yanıt döndür
            return next_handler(request)
    
    def _get_origin_header(self) -> str:
        """İstek origin başlığına göre izin verilen origin döndür"""
        try:
            from flask import request
            
            # Tüm originlere izin veriliyorsa
            if '*' in self.allowed_origins:
                return '*'
            
            # Origin başlığını al
            request_origin = request.headers.get('Origin')
            
            # Origin başlığı yoksa veya izin verilen listede değilse
            if not request_origin or request_origin not in self.allowed_origins:
                return self.allowed_origins[0] if self.allowed_origins else ''
                
            return request_origin
            
        except ImportError:
            # Flask import edilemedi
            return '*' if '*' in self.allowed_origins else (self.allowed_origins[0] if self.allowed_origins else '')

class RateLimitMiddleware(RouteMiddleware):
    """İstek hızı sınırlama middleware'i"""
    
    def __init__(self, requests_per_minute: int = 60, 
                 key_prefix: str = 'rate_limit', 
                 block_duration: int = 60):
        """
        Rate limit middleware başlat
        
        Args:
            requests_per_minute: Dakikada izin verilen maksimum istek sayısı
            key_prefix: Önbellek anahtarı öneki
            block_duration: Limit aşımında engelleme süresi (saniye)
        """
        super().__init__()
        self.requests_per_minute = requests_per_minute
        self.key_prefix = key_prefix
        self.block_duration = block_duration
        self.cache = {}  # Simple in-memory cache
    
    def handle(self, request: Any, next_handler: Callable) -> Any:
        """
        İstek hızını kontrol et
        
        Args:
            request: HTTP isteği
            next_handler: Bir sonraki middleware veya handler
            
        Returns:
            Any: İşlenen yanıt
        """
        try:
            from flask import request as flask_request, jsonify, make_response
            
            # İstek IP adresi
            client_ip = flask_request.remote_addr
            
            # Cache anahtarı
            cache_key = f"{self.key_prefix}:{client_ip}"
            
            # İstek sayısı ve zaman kontrolü
            current_time = time.time()
            
            if cache_key in self.cache:
                # Cache kaydı çek
                cache_data = self.cache[cache_key]
                
                # Bir dakika geçtiyse sıfırla
                if current_time - cache_data['first_request_time'] >= 60:
                    self.cache[cache_key] = {
                        'count': 1,
                        'first_request_time': current_time,
                        'block_until': 0
                    }
                else:
                    # Engelleme süresi kontrol
                    if cache_data.get('block_until', 0) > current_time:
                        # Hala engelleme süresi içinde
                        response = make_response(jsonify({
                            'status': 'error',
                            'message': 'Rate limit exceeded',
                            'code': 429,
                            'retry_after': int(cache_data['block_until'] - current_time)
                        }))
                        response.status_code = 429
                        response.headers.add('Retry-After', str(int(cache_data['block_until'] - current_time)))
                        return response
                    
                    # İstek sayısını arttır
                    cache_data['count'] += 1
                    
                    # Limit aşımı kontrolü
                    if cache_data['count'] > self.requests_per_minute:
                        # Engelleme başlat
                        cache_data['block_until'] = current_time + self.block_duration
                        
                        # Hata yanıtı
                        response = make_response(jsonify({
                            'status': 'error',
                            'message': 'Rate limit exceeded',
                            'code': 429,
                            'retry_after': self.block_duration
                        }))
                        response.status_code = 429
                        response.headers.add('Retry-After', str(self.block_duration))
                        return response
            else:
                # İlk istek
                self.cache[cache_key] = {
                    'count': 1,
                    'first_request_time': current_time,
                    'block_until': 0
                }
                
            # Normal yanıt
            response = next_handler(request)
            
            # Response nesnesine dönüştür
            if not isinstance(response, (dict, str)):
                return response
            
            response = make_response(response)
            
            # Rate limit başlıkları ekle
            remaining = max(0, self.requests_per_minute - self.cache[cache_key]['count'])
            reset_time = int(60 - (current_time - self.cache[cache_key]['first_request_time']))
            
            response.headers.add('X-RateLimit-Limit', str(self.requests_per_minute))
            response.headers.add('X-RateLimit-Remaining', str(remaining))
            response.headers.add('X-RateLimit-Reset', str(reset_time))
            
            return response
            
        except ImportError:
            # Flask import edilemedi, normal yanıt döndür
            return next_handler(request)

class LoggingMiddleware(RouteMiddleware):
    """İstek loglama middleware'i"""
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Logging middleware başlat
        
        Args:
            log_file: Log dosyası yolu (None ise konsola yazdırır)
        """
        super().__init__()
        self.log_file = log_file
    
    def handle(self, request: Any, next_handler: Callable) -> Any:
        """
        İstek başlangıcında log kaydı oluştur
        
        Args:
            request: HTTP isteği
            next_handler: Bir sonraki middleware veya handler
            
        Returns:
            Any: İşlenen yanıt
        """
        # İstek başlangıç zamanı
        start_time = time.time()
        
        # İstek detayları
        try:
            from flask import request as flask_request
            
            method = flask_request.method
            path = flask_request.path
            ip = flask_request.remote_addr
            user_agent = flask_request.headers.get('User-Agent', '')
            
        except ImportError:
            method = getattr(request, 'method', 'UNKNOWN')
            path = getattr(request, 'path', '/unknown')
            ip = getattr(request, 'remote_addr', '0.0.0.0')
            user_agent = getattr(request, 'headers', {}).get('User-Agent', '')
        
        # İsteği işle
        response = next_handler(request)
        
        # İşlem süresi
        duration = time.time() - start_time
        
        # Yanıt durumu
        if hasattr(response, 'status_code'):
            status_code = response.status_code
        else:
            status_code = 200
        
        # Log mesajı
        log_message = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {ip} {method} {path} {status_code} {duration:.4f}s \"{user_agent}\""
        
        # Log'u yaz
        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(log_message + '\n')
            except:
                print(log_message)
        else:
            print(log_message)
        
        return response

# Dekoratörler

def auth_middleware(f):
    """Auth middleware dekoratörü"""
    middleware = AuthMiddleware()
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        return middleware.handle(request, lambda req: f(*args, **kwargs))
    
    return decorated_function

def guest_middleware(f):
    """Guest middleware dekoratörü"""
    middleware = GuestMiddleware()
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        return middleware.handle(request, lambda req: f(*args, **kwargs))
    
    return decorated_function

def admin_middleware(f):
    """Admin middleware dekoratörü"""
    middleware = AdminMiddleware()
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        return middleware.handle(request, lambda req: f(*args, **kwargs))
    
    return decorated_function

def cors_middleware(allowed_origins=None, allowed_methods=None, allowed_headers=None):
    """CORS middleware dekoratörü"""
    middleware = CORSMiddleware(allowed_origins, allowed_methods, allowed_headers)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            return middleware.handle(request, lambda req: f(*args, **kwargs))
        
        return decorated_function
    
    return decorator

def rate_limit_middleware(requests_per_minute=60, key_prefix='rate_limit', block_duration=60):
    """Rate limit middleware dekoratörü"""
    middleware = RateLimitMiddleware(requests_per_minute, key_prefix, block_duration)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            return middleware.handle(request, lambda req: f(*args, **kwargs))
        
        return decorated_function
    
    return decorator 