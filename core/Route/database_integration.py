"""
Route ve Database Entegrasyonu
Model-based routing, dinamik içerik yönetimi ve veritabanı entegrasyonu
"""

from typing import Dict, List, Any, Optional, Union, Callable
from functools import wraps
import logging
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request

# Database modüllerini import et
try:
    from core.Database import BaseModel, table, search, paginate
    from core.Database.base_model import BaseModel as DBBaseModel
    from core.Database.query_builder import QueryBuilder
    from core.Database.pagination import Pagination
    from core.Database.search import SearchEngine
except ImportError:
    print("Database modülü bulunamadı. Lütfen core/Database klasörünü kontrol edin.")
    BaseModel = None
    table = None
    search = None
    paginate = None

# Route modüllerini import et
from .router import Router, get, post, put, delete, route
from .seo_manager import SEOManager, generate_meta_html
from .sitemap import SitemapGenerator
from .url_generator import URLGenerator

# Mock request objesi (gerçek implementasyonda framework'ten gelecek)
class MockRequest:
    def __init__(self, method='GET', path='', data=None, params=None):
        self.method = method
        self.path = path
        self.data = data or {}
        self.params = params or {}
    
    def get(self, key, default=None):
        return self.params.get(key, default)

# Global request objesi
request = MockRequest()

class ModelRouter:
    """Model tabanlı router sınıfı"""
    
    def __init__(self, model_class: type, base_url: str = "", 
                 seo_manager: SEOManager = None, url_generator: URLGenerator = None):
        self.model_class = model_class
        self.base_url = base_url
        self.seo_manager = seo_manager or SEOManager(base_url)
        self.url_generator = url_generator or URLGenerator(base_url)
        self.router = Router()
        
        # Model bilgilerini al
        self.table_name = getattr(model_class, '__table__', model_class.__name__.lower())
        self.primary_key = getattr(model_class, '__primary_key__', 'id')
        self.fillable = getattr(model_class, '__fillable__', [])
        
        # Route'ları otomatik oluştur
        self._create_default_routes()
    
    def _create_default_routes(self):
        """Varsayılan route'ları oluştur"""
        # Liste sayfası
        @self.router.get(f'/{self.table_name}', name=f'{self.table_name}.index')
        def index():
            return self._handle_index()
        
        # Detay sayfası
        @self.router.get(f'/{self.table_name}/{{id}}', name=f'{self.table_name}.show')
        def show(id):
            return self._handle_show(id)
        
        # Oluşturma sayfası
        @self.router.get(f'/{self.table_name}/create', name=f'{self.table_name}.create')
        def create():
            return self._handle_create()
        
        # Kaydetme
        @self.router.post(f'/{self.table_name}', name=f'{self.table_name}.store')
        def store():
            return self._handle_store()
        
        # Düzenleme sayfası
        @self.router.get(f'/{self.table_name}/{{id}}/edit', name=f'{self.table_name}.edit')
        def edit(id):
            return self._handle_edit(id)
        
        # Güncelleme
        @self.router.put(f'/{self.table_name}/{{id}}', name=f'{self.table_name}.update')
        def update(id):
            return self._handle_update(id)
        
        # Silme
        @self.router.delete(f'/{self.table_name}/{{id}}', name=f'{self.table_name}.destroy')
        def destroy(id):
            return self._handle_destroy(id)
    
    def _handle_index(self, **kwargs) -> Dict[str, Any]:
        """Liste sayfası handler'ı"""
        try:
            # Sayfalama parametreleri
            page = int(kwargs.get('page', 1))
            per_page = int(kwargs.get('per_page', 20))
            
            # Arama parametreleri
            search_query = kwargs.get('q', '')
            search_fields = kwargs.get('search_fields', self.fillable)
            
            # Filtreleme
            filters = {k: v for k, v in kwargs.items() 
                      if k not in ['page', 'per_page', 'q', 'search_fields'] and v}
            
            # Query oluştur
            query = table(self.table_name)
            
            # Arama uygula
            if search_query and search_fields:
                search_instance = search(self.table_name, search_query, search_fields)
                search_instance.filter(filters)
                results = search_instance.paginate(page, per_page)
            else:
                # Normal filtreleme
                for field, value in filters.items():
                    query = query.where(field, '=', value)
                
                # Sayfalama uygula
                results = paginate(query, page, per_page, 
                                 base_url=f"/{self.table_name}",
                                 query_params=kwargs)
            
            # SEO verileri
            seo_data = {
                'title': f'{self.table_name.title()} Listesi',
                'description': f'{self.table_name.title()} listesi ve arama sonuçları',
                'canonical': f"{self.base_url}/{self.table_name}"
            }
            
            return {
                'data': results,
                'seo_data': seo_data,
                'template': f'{self.table_name}/index'
            }
        
        except Exception as e:
            logging.error(f"Index handler hatası: {e}")
            return {'error': str(e), 'status': 500}
    
    def _handle_show(self, id: str, **kwargs) -> Dict[str, Any]:
        """Detay sayfası handler'ı"""
        try:
            # Kaydı bul
            record = self.model_class.find(id)
            if not record:
                return {'error': 'Kayıt bulunamadı', 'status': 404}
            
            # SEO verileri
            seo_data = self._generate_seo_data(record, 'show')
            
            return {
                'data': record,
                'seo_data': seo_data,
                'template': f'{self.table_name}/show'
            }
        
        except Exception as e:
            logging.error(f"Show handler hatası: {e}")
            return {'error': str(e), 'status': 500}
    
    def _handle_create(self, **kwargs) -> Dict[str, Any]:
        """Oluşturma sayfası handler'ı"""
        try:
            # SEO verileri
            seo_data = {
                'title': f'Yeni {self.table_name.title()} Oluştur',
                'description': f'Yeni {self.table_name.title()} oluşturma formu',
                'canonical': f"{self.base_url}/{self.table_name}/create"
            }
            
            return {
                'data': {},
                'seo_data': seo_data,
                'template': f'{self.table_name}/create'
            }
        
        except Exception as e:
            logging.error(f"Create handler hatası: {e}")
            return {'error': str(e), 'status': 500}
    
    def _handle_store(self, **kwargs) -> Dict[str, Any]:
        """Kaydetme handler'ı"""
        try:
            # Form verilerini al
            form_data = kwargs.get('form_data', {})
            
            # Sadece fillable alanları al
            valid_data = {k: v for k, v in form_data.items() 
                         if k in self.fillable or not self.fillable}
            
            # Yeni kayıt oluştur
            record = self.model_class(**valid_data)
            
            if record.save():
                return {
                    'message': 'Kayıt başarıyla oluşturuldu',
                    'data': record,
                    'status': 201,
                    'redirect': f"/{self.table_name}/{record.id}"
                }
            else:
                return {
                    'error': 'Kayıt oluşturulamadı',
                    'status': 400
                }
        
        except Exception as e:
            logging.error(f"Store handler hatası: {e}")
            return {'error': str(e), 'status': 500}
    
    def _handle_edit(self, id: str, **kwargs) -> Dict[str, Any]:
        """Düzenleme sayfası handler'ı"""
        try:
            # Kaydı bul
            record = self.model_class.find(id)
            if not record:
                return {'error': 'Kayıt bulunamadı', 'status': 404}
            
            # SEO verileri
            seo_data = {
                'title': f'{self.table_name.title()} Düzenle',
                'description': f'{self.table_name.title()} düzenleme formu',
                'canonical': f"{self.base_url}/{self.table_name}/{id}/edit"
            }
            
            return {
                'data': record,
                'seo_data': seo_data,
                'template': f'{self.table_name}/edit'
            }
        
        except Exception as e:
            logging.error(f"Edit handler hatası: {e}")
            return {'error': str(e), 'status': 500}
    
    def _handle_update(self, id: str, **kwargs) -> Dict[str, Any]:
        """Güncelleme handler'ı"""
        try:
            # Kaydı bul
            record = self.model_class.find(id)
            if not record:
                return {'error': 'Kayıt bulunamadı', 'status': 404}
            
            # Form verilerini al
            form_data = kwargs.get('form_data', {})
            
            # Sadece fillable alanları güncelle
            for field, value in form_data.items():
                if field in self.fillable or not self.fillable:
                    setattr(record, field, value)
            
            if record.save():
                return {
                    'message': 'Kayıt başarıyla güncellendi',
                    'data': record,
                    'status': 200,
                    'redirect': f"/{self.table_name}/{record.id}"
                }
            else:
                return {
                    'error': 'Kayıt güncellenemedi',
                    'status': 400
                }
        
        except Exception as e:
            logging.error(f"Update handler hatası: {e}")
            return {'error': str(e), 'status': 500}
    
    def _handle_destroy(self, id: str, **kwargs) -> Dict[str, Any]:
        """Silme handler'ı"""
        try:
            # Kaydı bul
            record = self.model_class.find(id)
            if not record:
                return {'error': 'Kayıt bulunamadı', 'status': 404}
            
            if record.delete():
                return {
                    'message': 'Kayıt başarıyla silindi',
                    'status': 200,
                    'redirect': f"/{self.table_name}"
                }
            else:
                return {
                    'error': 'Kayıt silinemedi',
                    'status': 400
                }
        
        except Exception as e:
            logging.error(f"Destroy handler hatası: {e}")
            return {'error': str(e), 'status': 500}
    
    def _generate_seo_data(self, record: BaseModel, action: str = 'show') -> Dict[str, Any]:
        """SEO verilerini oluştur"""
        # Varsayılan SEO verileri
        seo_data = {
            'title': f'{self.table_name.title()} - {getattr(record, "title", record.id)}',
            'description': getattr(record, 'description', f'{self.table_name.title()} detay sayfası'),
            'canonical': f"{self.base_url}/{self.table_name}/{record.id}"
        }
        
        # Özel alanlar varsa kullan
        if hasattr(record, 'seo_title'):
            seo_data['title'] = record.seo_title
        
        if hasattr(record, 'seo_description'):
            seo_data['description'] = record.seo_description
        
        if hasattr(record, 'seo_keywords'):
            seo_data['keywords'] = record.seo_keywords
        
        return seo_data
    
    def add_custom_route(self, path: str, handler: Callable, methods: List[str] = None, 
                        name: str = None, middleware: List[Callable] = None):
        """Özel route ekle"""
        return self.router.add_route(path, handler, methods, name, middleware)
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """Tüm route'ları getir"""
        routes = []
        for route in self.router.routes:
            routes.append({
                'path': route.path,
                'methods': route.methods,
                'name': route.name
            })
        return routes

class DatabaseRouteHelper:
    """Veritabanı route yardımcı sınıfı"""
    
    def __init__(self, base_url: str = ""):
        self.base_url = base_url
        self.seo_manager = SEOManager(base_url)
        self.url_generator = URLGenerator(base_url)
        self.sitemap_generator = SitemapGenerator(base_url)
    
    def create_model_router(self, model_class: type) -> ModelRouter:
        """Model router oluştur"""
        return ModelRouter(model_class, self.base_url, self.seo_manager, self.url_generator)
    
    def generate_sitemap_from_models(self, models: List[type]) -> str:
        """Modellerden sitemap oluştur"""
        for model_class in models:
            table_name = getattr(model_class, '__table__', model_class.__name__.lower())
            
            # Tüm kayıtları al
            records = model_class.all()
            
            for record in records:
                # URL pattern'i oluştur
                url_pattern = f"/{table_name}/{record.id}"
                
                # SEO verilerini al
                seo_data = self._get_record_seo_data(record, table_name)
                
                # Sitemap'e ekle
                self.sitemap_generator.add_url(
                    url=url_pattern,
                    lastmod=getattr(record, 'updated_at', None),
                    changefreq='weekly',
                    priority=0.7
                )
        
        # Sitemap'i kaydet
        return self.sitemap_generator.save_sitemap()
    
    def _get_record_seo_data(self, record: BaseModel, table_name: str) -> Dict[str, Any]:
        """Kayıt SEO verilerini al"""
        return {
            'title': getattr(record, 'title', f'{table_name.title()} - {record.id}'),
            'description': getattr(record, 'description', f'{table_name.title()} detay sayfası'),
            'keywords': getattr(record, 'keywords', ''),
            'canonical': f"{self.base_url}/{table_name}/{record.id}"
        }
    
    def create_api_routes(self, model_class: type, prefix: str = "api") -> Router:
        """API route'ları oluştur"""
        router = Router()
        table_name = getattr(model_class, '__table__', model_class.__name__.lower())
        
        # GET /api/table - Liste
        @router.get(f'/{prefix}/{table_name}')
        def api_index():
            try:
                page = int(request.get('page', 1))
                per_page = int(request.get('per_page', 20))
                
                query = table(table_name)
                results = paginate(query, page, per_page)
                
                return {
                    'status': 'success',
                    'data': results['items'],
                    'pagination': {
                        'current_page': results['page'],
                        'total_pages': results['total_pages'],
                        'total_items': results['total']
                    }
                }
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        
        # GET /api/table/{id} - Detay
        @router.get(f'/{prefix}/{table_name}/{{id}}')
        def api_show(id):
            try:
                record = model_class.find(id)
                if record:
                    return {'status': 'success', 'data': record.to_dict()}
                else:
                    return {'status': 'error', 'message': 'Kayıt bulunamadı'}, 404
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        
        # POST /api/table - Oluştur
        @router.post(f'/{prefix}/{table_name}')
        def api_store():
            try:
                form_data = request.get('form_data', {})
                record = model_class(**form_data)
                
                if record.save():
                    return {'status': 'success', 'data': record.to_dict()}, 201
                else:
                    return {'status': 'error', 'message': 'Kayıt oluşturulamadı'}, 400
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        
        # PUT /api/table/{id} - Güncelle
        @router.put(f'/{prefix}/{table_name}/{{id}}')
        def api_update(id):
            try:
                record = model_class.find(id)
                if not record:
                    return {'status': 'error', 'message': 'Kayıt bulunamadı'}, 404
                
                form_data = request.get('form_data', {})
                for field, value in form_data.items():
                    setattr(record, field, value)
                
                if record.save():
                    return {'status': 'success', 'data': record.to_dict()}
                else:
                    return {'status': 'error', 'message': 'Kayıt güncellenemedi'}, 400
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        
        # DELETE /api/table/{id} - Sil
        @router.delete(f'/{prefix}/{table_name}/{{id}}')
        def api_destroy(id):
            try:
                record = model_class.find(id)
                if not record:
                    return {'status': 'error', 'message': 'Kayıt bulunamadı'}, 404
                
                if record.delete():
                    return {'status': 'success', 'message': 'Kayıt silindi'}
                else:
                    return {'status': 'error', 'message': 'Kayıt silinemedi'}, 400
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        
        return router

# Dekoratör fonksiyonları
def model_route(model_class: type, base_url: str = ""):
    """Model route dekoratörü"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            router = ModelRouter(model_class, base_url)
            return func(router, *args, **kwargs)
        return wrapper
    return decorator

def database_route(table_name: str, base_url: str = ""):
    """Database route dekoratörü"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Query builder oluştur
            query = table(table_name)
            return func(query, *args, **kwargs)
        return wrapper
    return decorator

def search_route(table_name: str, search_fields: List[str] = None):
    """Arama route dekoratörü"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            search_query = kwargs.get('q', '')
            search_instance = search(table_name, search_query, search_fields)
            return func(search_instance, *args, **kwargs)
        return wrapper
    return decorator

# Global helper instance
db_route_helper = DatabaseRouteHelper()

# Kullanım kolaylığı için fonksiyonlar
def create_model_router(model_class: type, base_url: str = "") -> ModelRouter:
    """Model router oluştur"""
    return db_route_helper.create_model_router(model_class)

def create_api_routes(model_class: type, prefix: str = "api") -> Router:
    """API route'ları oluştur"""
    return db_route_helper.create_api_routes(model_class, prefix)

def generate_sitemap_from_models(models: List[type], base_url: str = "") -> str:
    """Modellerden sitemap oluştur"""
    helper = DatabaseRouteHelper(base_url)
    return helper.generate_sitemap_from_models(models)

# Database integration blueprint
def create_database_integration_blueprint():
    """Database entegrasyonu için blueprint oluştur"""
    bp = Blueprint('database_integration', __name__, url_prefix='/database')
    
    @bp.route('/')
    def index():
        """Örnek sayfası"""
        return jsonify({
            'title': 'Database Integration',
            'description': 'Model ve veritabanı tabanlı route\'lar oluşturma'
        })
    
    @bp.route('/models')
    def models():
        """Model örnekleri"""
        model_examples = [
            {
                'name': 'User',
                'routes': [
                    '/users',
                    '/users/create',
                    '/users/{id}',
                    '/users/{id}/edit'
                ]
            },
            {
                'name': 'Post',
                'routes': [
                    '/posts',
                    '/posts/create',
                    '/posts/{id}',
                    '/posts/{id}/edit'
                ]
            }
        ]
        
        return jsonify({
            'title': 'Model Router Examples',
            'examples': model_examples
        })
    
    @bp.route('/api')
    def api():
        """API örnekleri"""
        api_examples = [
            {
                'name': 'User API',
                'routes': [
                    'GET /api/users',
                    'POST /api/users',
                    'GET /api/users/{id}',
                    'PUT /api/users/{id}',
                    'DELETE /api/users/{id}'
                ]
            },
            {
                'name': 'Post API',
                'routes': [
                    'GET /api/posts',
                    'POST /api/posts',
                    'GET /api/posts/{id}',
                    'PUT /api/posts/{id}',
                    'DELETE /api/posts/{id}'
                ]
            }
        ]
        
        return jsonify({
            'title': 'API Examples',
            'examples': api_examples
        })
    
    return bp

def get_database_integration_bp():
    """Database integration blueprint'ini döndür"""
    return create_database_integration_blueprint() 