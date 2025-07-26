"""
Database Route Entegrasyonu Örnekleri
Model-based routing, API routes ve dinamik içerik yönetimi örnekleri
"""

from typing import Dict, List, Any
import json
from flask import Blueprint, render_template, jsonify, request

# Route ve Database modüllerini import et
from .database_integration import (
    ModelRouter, 
    DatabaseRouteHelper,
    model_route,
    database_route,
    search_route,
    create_model_router,
    create_api_routes,
    generate_sitemap_from_models
)

from .router import Router, get, post, put, delete
from .seo_manager import SEOManager
from .sitemap import SitemapGenerator

# Örnek model sınıfları (gerçek projede app/Models/ klasöründen gelecek)
class User:
    """Örnek User modeli"""
    __table__ = 'users'
    __primary_key__ = 'id'
    __fillable__ = ['name', 'email', 'password', 'status']
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def find(cls, id):
        # Gerçek implementasyonda veritabanından veri çekilecek
        return cls(id=id, name=f"User {id}", email=f"user{id}@example.com")
    
    @classmethod
    def all(cls):
        # Gerçek implementasyonda tüm kayıtlar getirilecek
        return [cls(id=1, name="John Doe", email="john@example.com"),
                cls(id=2, name="Jane Smith", email="jane@example.com")]
    
    def save(self):
        # Gerçek implementasyonda kaydetme işlemi yapılacak
        return True
    
    def delete(self):
        # Gerçek implementasyonda silme işlemi yapılacak
        return True
    
    def to_dict(self):
        return {
            'id': getattr(self, 'id', None),
            'name': getattr(self, 'name', ''),
            'email': getattr(self, 'email', ''),
            'status': getattr(self, 'status', 'active')
        }

class Post:
    """Örnek Post modeli"""
    __table__ = 'posts'
    __primary_key__ = 'id'
    __fillable__ = ['title', 'content', 'author_id', 'status', 'seo_title', 'seo_description']
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def find(cls, id):
        return cls(id=id, title=f"Post {id}", content=f"Content for post {id}")
    
    @classmethod
    def all(cls):
        return [cls(id=1, title="İlk Post", content="Bu ilk post içeriği"),
                cls(id=2, title="İkinci Post", content="Bu ikinci post içeriği")]
    
    def save(self):
        return True
    
    def delete(self):
        return True
    
    def to_dict(self):
        return {
            'id': getattr(self, 'id', None),
            'title': getattr(self, 'title', ''),
            'content': getattr(self, 'content', ''),
            'author_id': getattr(self, 'author_id', None),
            'status': getattr(self, 'status', 'published')
        }

class Product:
    """Örnek Product modeli"""
    __table__ = 'products'
    __primary_key__ = 'id'
    __fillable__ = ['name', 'description', 'price', 'category_id', 'stock']
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def find(cls, id):
        return cls(id=id, name=f"Product {id}", price=99.99)
    
    @classmethod
    def all(cls):
        return [cls(id=1, name="Laptop", price=1299.99),
                cls(id=2, name="Mouse", price=29.99)]
    
    def save(self):
        return True
    
    def delete(self):
        return True
    
    def to_dict(self):
        return {
            'id': getattr(self, 'id', None),
            'name': getattr(self, 'name', ''),
            'description': getattr(self, 'description', ''),
            'price': getattr(self, 'price', 0),
            'category_id': getattr(self, 'category_id', None),
            'stock': getattr(self, 'stock', 0)
        }

def create_database_examples_blueprint():
    """Database örnekleri için blueprint oluştur"""
    bp = Blueprint('database_examples', __name__, url_prefix='/examples/database')
    
    @bp.route('/')
    def index():
        """Örnek sayfası"""
        examples = [
            {'name': 'Basic Model Router', 'url': '/examples/database/basic-model-router'},
            {'name': 'Custom Model Routes', 'url': '/examples/database/custom-model-routes'},
            {'name': 'API Routes', 'url': '/examples/database/api-routes'},
            {'name': 'Decorator Usage', 'url': '/examples/database/decorator-usage'},
            {'name': 'Sitemap Generation', 'url': '/examples/database/sitemap-generation'},
            {'name': 'SEO Integration', 'url': '/examples/database/seo-integration'},
            {'name': 'Advanced Queries', 'url': '/examples/database/advanced-queries'},
            {'name': 'Middleware Integration', 'url': '/examples/database/middleware-integration'}
        ]
        
        return jsonify({
            'title': 'Database Entegrasyonu Örnekleri',
            'description': 'Model-based routing, API routes ve dinamik içerik yönetimi örnekleri',
            'examples': examples
        })
    
    @bp.route('/basic-model-router')
    def basic_model_router():
        """Temel Model Router örneği"""
        user_router = create_model_router(User, base_url="https://example.com")
        routes = user_router.get_routes()
        
        route_list = []
        for route in routes:
            route_list.append({
                'methods': route['methods'],
                'path': route['uri'],
                'name': route['name']
            })
        
        return jsonify({
            'title': 'Temel Model Router Örneği',
            'routes': route_list,
            'model': 'User'
        })
    
    @bp.route('/custom-model-routes')
    def custom_model_routes():
        """Özel Model Route örneği"""
        post_router = ModelRouter(Post, base_url="https://blog.example.com")
        
        # Özel route ekle (örnek olarak)
        custom_routes = [
            {'methods': ['GET'], 'path': '/posts/category/{category}', 'name': 'posts.category'},
            {'methods': ['POST'], 'path': '/api/posts/search', 'name': 'posts.search'}
        ]
        
        return jsonify({
            'title': 'Özel Model Route Örneği',
            'model': 'Post',
            'custom_routes': custom_routes
        })
    
    @bp.route('/api-routes')
    def api_routes():
        """API Route örneği"""
        product_routes = [
            {'methods': ['GET'], 'path': '/api/v1/products', 'name': 'product.index'},
            {'methods': ['POST'], 'path': '/api/v1/products', 'name': 'product.store'},
            {'methods': ['GET'], 'path': '/api/v1/products/{id}', 'name': 'product.show'},
            {'methods': ['PUT', 'PATCH'], 'path': '/api/v1/products/{id}', 'name': 'product.update'},
            {'methods': ['DELETE'], 'path': '/api/v1/products/{id}', 'name': 'product.destroy'},
            {'methods': ['GET'], 'path': '/api/v1/products/featured', 'name': 'product.featured'},
            {'methods': ['GET'], 'path': '/api/v1/products/categories/{category_id}', 'name': 'product.category'}
        ]
        
        return jsonify({
            'title': 'API Routes Örneği',
            'model': 'Product',
            'routes': product_routes
        })
    
    @bp.route('/decorator-usage')
    def decorator_usage():
        """Dekoratör kullanımı örneği"""
        decorators = [
            {
                'name': '@model_route',
                'description': 'Model sınıfından router oluşturmak için kullanılır',
                'example': '@model_route(User, base_url="https://admin.example.com")'
            },
            {
                'name': '@database_route',
                'description': 'Veritabanı sorguları için route oluşturmak için kullanılır',
                'example': '@database_route("users", base_url="https://api.example.com")'
            },
            {
                'name': '@search_route',
                'description': 'Arama işlemleri için route oluşturmak için kullanılır',
                'example': '@search_route("posts", search_fields=["title", "content"])'
            }
        ]
        
        return jsonify({
            'title': 'Dekoratör Kullanımı Örneği',
            'decorators': decorators
        })
    
    @bp.route('/sitemap-generation')
    def sitemap_generation():
        """Sitemap oluşturma örneği"""
        models = ['User', 'Post', 'Product']
        sitemap_items = [
            {'url': 'https://example.com/users', 'changefreq': 'daily', 'priority': 0.8},
            {'url': 'https://example.com/posts', 'changefreq': 'daily', 'priority': 0.8},
            {'url': 'https://example.com/products', 'changefreq': 'daily', 'priority': 0.8},
            {'url': 'https://example.com/users/1', 'changefreq': 'weekly', 'priority': 0.6},
            {'url': 'https://example.com/posts/1', 'changefreq': 'weekly', 'priority': 0.6},
            {'url': 'https://example.com/products/1', 'changefreq': 'weekly', 'priority': 0.6}
        ]
        
        return jsonify({
            'title': 'Sitemap Oluşturma Örneği',
            'models': models,
            'example_sitemap_items': sitemap_items,
            'base_url': 'https://example.com'
        })
    
    @bp.route('/seo-integration')
    def seo_integration():
        """SEO entegrasyonu örneği"""
        seo_examples = [
            {
                'title': 'Post SEO',
                'model': 'Post',
                'fields': ['seo_title', 'seo_description', 'seo_keywords'],
                'meta_tags': '<meta name="title" content="İlk Post">\n<meta name="description" content="Bu ilk post içeriği">\n<meta name="keywords" content="post,blog,içerik">'
            },
            {
                'title': 'Product SEO',
                'model': 'Product',
                'fields': ['seo_title', 'seo_description', 'seo_keywords'],
                'meta_tags': '<meta name="title" content="Laptop">\n<meta name="description" content="Yüksek performanslı laptop">\n<meta name="keywords" content="laptop,bilgisayar,teknoloji">'
            }
        ]
        
        return jsonify({
            'title': 'SEO Entegrasyonu Örneği',
            'examples': seo_examples
        })
    
    @bp.route('/advanced-queries')
    def advanced_queries():
        """Gelişmiş sorgular örneği"""
        queries = [
            {
                'name': 'Filtreleme',
                'example': 'query.where("status", "=", "published").where("author_id", "=", 1).get()'
            },
            {
                'name': 'Sıralama',
                'example': 'query.orderBy("created_at", "desc").limit(10).get()'
            },
            {
                'name': 'İlişkili veriler',
                'example': 'query.with("author").with("comments").findOrFail(1)'
            },
            {
                'name': 'Grup ve hesaplama',
                'example': 'query.select("category_id").count("id").groupBy("category_id").get()'
            }
        ]
        
        return jsonify({
            'title': 'Gelişmiş Sorgular Örneği',
            'queries': queries
        })
    
    @bp.route('/middleware-integration')
    def middleware_integration():
        """Middleware entegrasyonu örneği"""
        middlewares = [
            {
                'name': 'auth',
                'description': 'Kullanıcı kimlik doğrulaması yapar'
            },
            {
                'name': 'admin',
                'description': 'Kullanıcının admin olup olmadığını kontrol eder'
            },
            {
                'name': 'rate_limit',
                'description': 'İstek sayısını sınırlar'
            },
            {
                'name': 'cors',
                'description': 'Cross-Origin Resource Sharing ayarlarını yapar'
            },
            {
                'name': 'log',
                'description': 'İstekleri loglar'
            }
        ]
        
        examples = [
            {
                'route': '/admin/users',
                'middlewares': ['auth', 'admin'],
                'description': 'Sadece admin kullanıcıların erişebileceği route'
            },
            {
                'route': '/api/users',
                'middlewares': ['auth', 'rate_limit'],
                'description': 'Kimlik doğrulaması gerektiren ve istek limiti olan API route'
            },
            {
                'route': '/api/logged',
                'middlewares': ['log'],
                'description': 'İstekleri loglayan API route'
            }
        ]
        
        return jsonify({
            'title': 'Middleware Entegrasyonu Örneği',
            'middlewares': middlewares,
            'examples': examples
        })
    
    return bp

def get_database_examples_bp():
    """Database örnekleri blueprint'ini döndür"""
    return create_database_examples_blueprint() 