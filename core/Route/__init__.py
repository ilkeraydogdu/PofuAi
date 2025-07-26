"""
PofuAi Route Sistemi
Gelişmiş routing, SEO yönetimi, sitemap oluşturma ve veritabanı entegrasyonu
"""

# Ana route modülleri
from .router import Router, get, post, put, delete, route, Route
from .seo_manager import SEOManager, generate_meta_html
from .sitemap import SitemapGenerator
from .url_generator import URLGenerator
from .middleware import RouteMiddleware, auth_middleware, cors_middleware, rate_limit_middleware

# Database entegrasyonu
from .database_integration import (
    ModelRouter,
    DatabaseRouteHelper,
    model_route,
    database_route,
    search_route,
    create_model_router,
    create_api_routes,
    generate_sitemap_from_models,
    db_route_helper
)

# Ana sınıflar
__all__ = [
    # Router
    'Router',
    'Route',
    'get',
    'post', 
    'put',
    'delete',
    'route',
    
    # SEO
    'SEOManager',
    'generate_meta_html',
    
    # Sitemap
    'SitemapGenerator',
    
    # URL Generator
    'URLGenerator',
    
    # Middleware
    'RouteMiddleware',
    'auth_middleware',
    'cors_middleware', 
    'rate_limit_middleware',
    
    # Database Integration
    'ModelRouter',
    'DatabaseRouteHelper',
    'model_route',
    'database_route',
    'search_route',
    'create_model_router',
    'create_api_routes',
    'generate_sitemap_from_models',
    'db_route_helper'
]

# Versiyon bilgisi
__version__ = "2.0.0"
__author__ = "PofuAi Team"
__description__ = "Gelişmiş routing sistemi ile veritabanı entegrasyonu" 