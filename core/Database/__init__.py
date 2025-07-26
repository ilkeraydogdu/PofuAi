"""
PofuAi Database Module
Merkezi veritabanı yönetimi ve işlemleri
"""

# Lazy loading için connection'ı import etme
# from .connection import DatabaseConnection
from .base_model import BaseModel
from .query_builder import QueryBuilder
from .pagination import Pagination
from .search import SearchEngine

# Helper fonksiyonlar
def table(table_name: str) -> QueryBuilder:
    """Tablo için query builder oluştur"""
    return QueryBuilder(table_name)

def search(table_name: str, query: str, fields: list = None) -> SearchEngine:
    """Arama motoru oluştur"""
    return SearchEngine(table_name, query, fields or [])

def paginate(query_builder, page: int = 1, per_page: int = 20, 
             base_url: str = "", query_params: dict = None) -> dict:
    """Sayfalama işlemi"""
    pagination = Pagination(query_builder, page, per_page, base_url, query_params)
    return pagination.get_results()

def get_db_connection():
    """Database connection instance'ını getir (lazy loading)"""
    from .connection import get_db_connection as _get_db
    return _get_db()

__all__ = [
    'BaseModel', 
    'QueryBuilder',
    'Pagination',
    'SearchEngine',
    'table',
    'search', 
    'paginate',
    'get_db_connection'
] 