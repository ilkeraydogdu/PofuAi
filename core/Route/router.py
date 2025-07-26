"""
Router Service
Gelişmiş route yönetimi
"""
import re
from typing import Dict, Any, List, Optional, Callable, Union
from core.Services.base_service import BaseService
import werkzeug.exceptions

class Route:
    """Route sınıfı"""
    
    def __init__(self, uri, action, controller=None, methods=None, name=None, middleware=None):
        """
        Route sınıfını başlat
        
        Args:
            uri (str): Route URI'si
            action (str): Controller'da çağrılacak method adı
            controller (class): Controller sınıfı
            methods (list): HTTP metodları, varsayılan olarak ['GET']
            name (str): Route adı
            middleware (list): Uygulanacak middleware'ler
        """
        self.uri = uri
        self.action = action
        self.controller = controller
        self.methods = methods or ['GET']
        self.name = name
        self.middleware = middleware or []
        
    def get_uri(self):
        """URI'yi döndürür"""
        return self.uri
        
    def get_action(self):
        """Action'ı döndürür"""
        return self.action
        
    def get_controller(self):
        """Controller'ı döndürür"""
        return self.controller
        
    def get_methods(self):
        """HTTP metodlarını döndürür"""
        return self.methods
        
    def get_name(self):
        """Route adını döndürür"""
        return self.name
        
    def get_middleware(self):
        """Middleware listesini döndürür"""
        return self.middleware

class Router:
    """Gelişmiş router sistemi"""
    
    def __init__(self):
        self.routes = []
        self.middleware = {}
        self.prefix = ''
        self.namespace = ''
        self.logger = BaseService.get_logger()
        self._setup_default_middleware()
    
    def _setup_default_middleware(self):
        """Varsayılan middleware'leri ayarla"""
        from app.Middleware.AuthMiddleware import AuthMiddleware, GuestMiddleware, AdminMiddleware
        
        self.middleware['auth'] = AuthMiddleware()
        self.middleware['guest'] = GuestMiddleware()
        self.middleware['admin'] = AdminMiddleware()
    
    def group(self, prefix: str = '', namespace: str = '', middleware: List[str] = None, **options):
        """Route grubu oluştur"""
        old_prefix = self.prefix
        old_namespace = self.namespace
        
        self.prefix = old_prefix + prefix
        self.namespace = old_namespace + namespace
        
        def decorator(func):
            func()
            self.prefix = old_prefix
            self.namespace = old_namespace
            return func
        
        return decorator
    
    def get(self, uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
        """GET route tanımla"""
        return self.add_route(['GET'], uri, action, name, middleware)
    
    def post(self, uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
        """POST route tanımla"""
        return self.add_route(['POST'], uri, action, name, middleware)
    
    def put(self, uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
        """PUT route tanımla"""
        return self.add_route(['PUT'], uri, action, name, middleware)
    
    def patch(self, uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
        """PATCH route tanımla"""
        return self.add_route(['PATCH'], uri, action, name, middleware)
    
    def delete(self, uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
        """DELETE route tanımla"""
        return self.add_route(['DELETE'], uri, action, name, middleware)
    
    def match(self, methods: List[str], uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
        """Çoklu HTTP metodu route tanımla"""
        return self.add_route(methods, uri, action, name, middleware)
    
    def any(self, uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
        """Tüm HTTP metodları için route tanımla"""
        return self.add_route(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], uri, action, name, middleware)
    
    def add(self, route: Route):
        """Route nesnesi ekle"""
        uri = self.prefix + route.get_uri()
        controller = route.get_controller()
        action = route.get_action()
        methods = route.get_methods()
        name = route.get_name()
        middleware = route.get_middleware()
        
        # Controller'dan instance oluştur
        controller_instance = controller()
        
        # Action'ı controller instance'ı ile eşleştir
        action_fn = getattr(controller_instance, action, None)
        
        if not action_fn:
            raise ValueError(f"Action {action} not found in controller {controller.__name__}")
        
        # Route pattern'ini oluştur
        pattern = self._create_pattern(uri)
        
        # Route'u kaydet
        route_data = {
            'methods': methods,
            'uri': uri,
            'pattern': pattern,
            'controller': controller,
            'action': action,
            'name': name,
            'middleware': middleware,
            'namespace': self.namespace
        }
        
        self.routes.append(route_data)
        
        # Log
        self.logger.debug(f"Route added: {methods} {uri} -> {controller.__name__}@{action}")
        
        return route_data
    
    def resource(self, name: str, controller: str, options: Dict[str, Any] = None):
        """Resource route'ları oluştur"""
        options = options or {}
        
        # Controller namespace'i
        controller_class = f"{self.namespace}{controller}" if self.namespace else controller
        
        # Route'ları oluştur
        routes = [
            ('GET', f'/{name}', f'{controller_class}@index', f'{name}.index'),
            ('GET', f'/{name}/create', f'{controller_class}@create', f'{name}.create'),
            ('POST', f'/{name}', f'{controller_class}@store', f'{name}.store'),
            ('GET', f'/{name}/{{id}}', f'{controller_class}@show', f'{name}.show'),
            ('GET', f'/{name}/{{id}}/edit', f'{controller_class}@edit', f'{name}.edit'),
            ('PUT', f'/{name}/{{id}}', f'{controller_class}@update', f'{name}.update'),
            ('DELETE', f'/{name}/{{id}}', f'{controller_class}@delete', f'{name}.delete'),
        ]
        
        # Özel route'ları ekle
        if 'only' in options:
            routes = [route for route in routes if route[3] in options['only']]
        
        if 'except' in options:
            routes = [route for route in routes if route[3] not in options['except']]
        
        # Route'ları kaydet
        for method, uri, action, route_name in routes:
            middleware = options.get('middleware', [])
            self.add_route([method], uri, action, route_name, middleware)
    
    def api_resource(self, name: str, controller: str, options: Dict[str, Any] = None):
        """API resource route'ları oluştur"""
        options = options or {}
        options['api'] = True
        self.resource(name, controller, options)
    
    def add_route(self, methods: List[str], uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
        """Route ekle"""
        # URI'yi prefix ile birleştir
        full_uri = self.prefix + uri
        
        # Route pattern'ini oluştur
        pattern = self._create_pattern(full_uri)
        
        # Route'u kaydet
        route = {
            'methods': methods,
            'uri': full_uri,
            'pattern': pattern,
            'action': action,
            'name': name,
            'middleware': middleware or [],
            'namespace': self.namespace
        }
        
        self.routes.append(route)
        
        # Log
        self.logger.debug(f"Route added: {methods} {full_uri} -> {action}")
        
        return route
    
    def _create_pattern(self, uri: str) -> str:
        """URI'den regex pattern oluştur"""
        # Parametreleri regex ile değiştir
        pattern = re.sub(r'\{([^}]+)\}', r'(?P<\1>[^/]+)', uri)
        pattern = f"^{pattern}$"
        return pattern
    
    def dispatch(self, request) -> Dict[str, Any]:
        """Request'i dispatch et"""
        try:
            # İçerik tipi kontrolü
            if request.method in ['POST', 'PUT', 'PATCH'] and request.headers.get('Content-Type'):
                content_type = request.headers.get('Content-Type', '').lower()
                
                # İçerik tipi kontrolü
                valid_content_types = [
                    'application/json', 
                    'application/x-www-form-urlencoded', 
                    'multipart/form-data'
                ]
                
                # İçerik tipi kontrolü - kısmi eşleşme yeterli (charset vb. parametreler olabilir)
                is_valid = any(valid_type in content_type for valid_type in valid_content_types)
                
                # JSON içeriği kontrolü
                if 'application/json' in content_type:
                    try:
                        # JSON verilerini güvenli bir şekilde kontrol et
                        if request.get_data():
                            json_data = request.get_json(silent=True, force=True)
                            if json_data is None:
                                self.logger.warning(f"Geçersiz JSON verisi, path: {request.path}")
                                return self._handle_error_response(request, 400, "Geçersiz JSON verisi")
                    except Exception as e:
                        self.logger.error(f"JSON işleme hatası: {str(e)}, path: {request.path}")
                        return self._handle_error_response(request, 400, f"JSON işleme hatası: {str(e)}")
                
                # İçerik tipi geçerli değilse hata döndür
                if not is_valid and request.get_data():
                    self.logger.warning(f"Desteklenmeyen içerik tipi: {content_type}, path: {request.path}")
                    return self._handle_error_response(request, 415, "Desteklenmeyen içerik tipi")
            
            # Route'u bul
            route = self._find_route(request)
            
            if not route:
                return self._handle_404(request)
            
            # Middleware'leri çalıştır
            middleware_response = self._run_middleware(request, route)
            if middleware_response:
                return middleware_response
            
            # Controller'ı çalıştır
            return self._run_controller(request, route)
            
        except werkzeug.exceptions.HTTPException as e:
            # HTTP hataları
            self.logger.warning(f"HTTP hatası: {e.code} {e.description}, path: {request.path}")
            return self._handle_error_response(request, e.code, e.description)
        except Exception as e:
            # Genel hatalar
            self.logger.error(f"Dispatch hatası: {str(e)}, path: {request.path}")
            return self._handle_500(request, e)
    
    def _find_route(self, request) -> Optional[Dict[str, Any]]:
        """Request için uygun route'u bul"""
        method = request.method
        path = request.path
        
        for route in self.routes:
            if method in route['methods']:
                match = re.match(route['pattern'], path)
                if match:
                    # Parametreleri request'e ekle
                    request.route_params = match.groupdict()
                    return route
        
        return None
    
    def _run_middleware(self, request, route: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Middleware'leri çalıştır"""
        middleware_list = route.get('middleware', [])
        
        for middleware_name in middleware_list:
            if middleware_name in self.middleware:
                middleware = self.middleware[middleware_name]
                response = middleware.handle(request, lambda req: None)
                if response:
                    return response
        
        return None
    
    def _run_controller(self, request, route: Dict[str, Any]) -> Dict[str, Any]:
        """Controller'ı çalıştır"""
        action = route['action']
        
        try:
            # Eğer action bir sınıf metodu ise (classmethod veya staticmethod değil),
            # önce controller sınıfını örneklemek gerekiyor
            if hasattr(action, '__self__') and action.__self__ and type(action.__self__) is type:
                # Bu, bir sınıf üzerindeki örnek metodunu temsil ediyor
                controller_class = action.__self__
                method_name = action.__name__
                
                # Controller instance'ı oluştur
                controller = controller_class()
                
                # Request'i set et
                if hasattr(controller, 'set_request'):
                    controller.set_request(request)
                elif hasattr(controller, 'request'):
                    controller.request = request
                
                # Method'u çağır
                method = getattr(controller, method_name)
                
                # Route parametrelerini method'a geçir
                params = getattr(request, 'route_params', {})
                if params:
                    return method(**params)
                else:
                    return method()
            
            if callable(action):
                # Closure/function veya statik metod
                return action(request)
            
            # Controller@method formatı
            if '@' in action:
                controller_name, method_name = action.split('@')
                
                # Controller'ı import et
                controller_class = self._load_controller(controller_name)
                if not controller_class:
                    return self._handle_500(request, Exception(f"Controller not found: {controller_name}"))
                
                # Controller instance'ı oluştur
                controller = controller_class()
                if hasattr(controller, 'set_request'):
                    controller.set_request(request)
                elif hasattr(controller, 'request'):
                    controller.request = request
                
                # Method'u çağır
                if hasattr(controller, method_name):
                    method = getattr(controller, method_name)
                    
                    # Route parametrelerini method'a geçir
                    params = getattr(request, 'route_params', {})
                    result = None
                    
                    if params:
                        result = method(**params)
                    else:
                        result = method()
                    
                    # Eğer sonuç zaten bir Flask yanıtı ise (tuple veya Response), doğrudan döndür
                    if isinstance(result, tuple) or hasattr(result, 'get_data'):
                        return result
                    
                    # Eski format yanıt işleme
                    if isinstance(result, dict):
                        if 'type' in result:
                            if result['type'] == 'redirect':
                                from flask import redirect
                                return redirect(result['url'], code=result.get('status', 302))
                            elif result['type'] == 'view':
                                from flask import render_template
                                return render_template(f"{result['template']}.html", **result.get('data', {}))
                    
                    # Diğer durumlar için sonucu olduğu gibi döndür
                    return result
                else:
                    return self._handle_500(request, Exception(f"Method not found: {method_name}"))
            
            return self._handle_500(request, Exception(f"Invalid action format: {action}"))
        except werkzeug.exceptions.UnsupportedMediaType as e:
            # JSON içerik tipi hatalarını burada yakala
            self.logger.error(f"Controller içerik tipi hatası: {str(e)}")
            return self._handle_error_response(request, 415, "Desteklenmeyen içerik tipi")
        except Exception as e:
            return self._handle_500(request, e)
    
    def _load_controller(self, controller_name: str):
        """Controller'ı yükle"""
        try:
            # Controller path'ini oluştur
            if self.namespace:
                module_path = f"{self.namespace}.{controller_name}"
            else:
                module_path = f"app.Controllers.{controller_name}"
            
            # Module'ü import et
            import importlib
            module = importlib.import_module(module_path)
            
            # Controller class'ını al
            return getattr(module, controller_name)
            
        except Exception as e:
            self.logger.error(f"Controller load error: {str(e)}")
            return None
    
    def _handle_404(self, request) -> Dict[str, Any]:
        """404 handler"""
        from core.Services.error_handler import error_handler
        return error_handler.handle_http_error(404, 'Sayfa bulunamadı', request)
    
    def _handle_500(self, request, exception) -> Dict[str, Any]:
        """500 handler"""
        from core.Services.error_handler import error_handler
        return error_handler.handle_error(exception, request)
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Tüm route'ları döndürür"""
        return self.routes
    
    def get_route_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """İsme göre route döndürür"""
        for route in self.routes:
            if route['name'] == name:
                return route
        return None
    
    def url(self, name: str, params: Dict[str, Any] = None) -> str:
        """Route adına göre URL oluştur"""
        route = self.get_route_by_name(name)
        if not route:
            return ''
        
        uri = route['uri']
        
        # Parametreleri replace et
        if params:
            for key, value in params.items():
                uri = re.sub(f'{{{key}}}', str(value), uri)
        
        return uri
    
    def register_middleware(self, name: str, middleware):
        """Middleware kaydet"""
        self.middleware[name] = middleware
    
    def clear_routes(self):
        """Tüm route'ları temizler"""
        self.routes = []
        
    def register(self, app):
        """Flask app'e route'ları kaydet"""
        for route in self.routes:
            app.add_url_rule(
                route['uri'], 
                endpoint=route['name'] or None, 
                view_func=self._create_flask_view(route),
                methods=route['methods']
            )
    
    def _create_flask_view(self, route):
        """Flask view fonksiyonu oluştur"""
        action = route['action']
        controller = route.get('controller')
        
        def view_func(**kwargs):
            from flask import request
            
            # Request'e route parametrelerini ekle
            request.route_params = kwargs
            
            # Eğer controller ve action string ise, bunları ayrıştır ve çağır
            if isinstance(action, str) and '@' in action:
                return self._run_controller(request, route)
            
            # Eğer controller class ise ve action string ise
            if controller and isinstance(action, str):
                # Controller instance oluştur
                instance = controller()
                instance.set_request(request)
                
                # Action'ı çağır
                method = getattr(instance, action)
                return method(**kwargs) if kwargs else method()
                
            # Eğer action callable ise, doğrudan çağır
            if callable(action):
                return action(request, **kwargs)
                
            # Bu noktada route hatalı
            return self._handle_500(request, Exception(f"Invalid route configuration: {route}"))
        
        return view_func
    
    def _handle_error_response(self, request, status_code, message):
        """Özel hata yanıtı oluştur"""
        from flask import render_template, jsonify
        
        # API isteği kontrolü
        if self._is_api_request(request):
            return jsonify({
                'status': 'error',
                'code': status_code,
                'message': message
            }), status_code
            
        # Web isteği için hata sayfası
        from core.Components.feedback.error_page import ErrorPageComponent
        error_page = ErrorPageComponent()
        return error_page.render_error(status_code, message), status_code
        
    def _is_api_request(self, request):
        """API isteği mi kontrolü"""
        return (
            request.path.startswith('/api/') or
            request.headers.get('Accept') == 'application/json' or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        )

# Global router instance
_router = None

def get_router() -> Router:
    """Global router instance'ını döndürür"""
    global _router
    if _router is None:
        _router = Router()
    return _router

# Helper functions
def route(methods: List[str], uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
    """Route ekle"""
    return get_router().add_route(methods, uri, action, name, middleware)

def get(uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
    """GET route ekle"""
    return get_router().get(uri, action, name, middleware)

def post(uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
    """POST route ekle"""
    return get_router().post(uri, action, name, middleware)

def put(uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
    """PUT route ekle"""
    return get_router().put(uri, action, name, middleware)

def delete(uri: str, action: Union[str, Callable], name: str = None, middleware: List[str] = None):
    """DELETE route ekle"""
    return get_router().delete(uri, action, name, middleware)

def resource(name: str, controller: str, options: Dict[str, Any] = None):
    """Resource routes ekle"""
    return get_router().resource(name, controller, options)

def api_resource(name: str, controller: str, options: Dict[str, Any] = None):
    """API resource routes ekle"""
    return get_router().api_resource(name, controller, options) 