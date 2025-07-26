"""
Gelişmiş Arama ve Filtreleme Sistemi
Full-text search, çoklu filtre ve sıralama desteği
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from .query_builder import QueryBuilder
import re

class SearchEngine:
    """Gelişmiş arama motoru"""
    
    def __init__(self, query_builder: QueryBuilder):
        self.query_builder = query_builder
        self.search_fields = []
        self.filter_conditions = {}
        self.sort_conditions = []
        self.search_query = ""
    
    def search(self, query: str, fields: List[str] = None) -> 'SearchEngine':
        """Arama sorgusu ekle"""
        self.search_query = query.strip()
        if fields:
            self.search_fields = fields
        return self
    
    def filter(self, conditions: Dict[str, Any]) -> 'SearchEngine':
        """Filtre koşulları ekle"""
        self.filter_conditions.update(conditions)
        return self
    
    def filter_range(self, field: str, min_value: Any = None, max_value: Any = None) -> 'SearchEngine':
        """Aralık filtresi ekle"""
        if min_value is not None or max_value is not None:
            self.filter_conditions[f"{field}_range"] = {
                'min': min_value,
                'max': max_value
            }
        return self
    
    def filter_in(self, field: str, values: List[Any]) -> 'SearchEngine':
        """IN filtresi ekle"""
        if values:
            self.filter_conditions[f"{field}_in"] = values
        return self
    
    def filter_not_in(self, field: str, values: List[Any]) -> 'SearchEngine':
        """NOT IN filtresi ekle"""
        if values:
            self.filter_conditions[f"{field}_not_in"] = values
        return self
    
    def filter_null(self, field: str, is_null: bool = True) -> 'SearchEngine':
        """NULL filtresi ekle"""
        self.filter_conditions[f"{field}_null"] = is_null
        return self
    
    def filter_like(self, field: str, pattern: str) -> 'SearchEngine':
        """LIKE filtresi ekle"""
        self.filter_conditions[f"{field}_like"] = pattern
        return self
    
    def sort(self, field: str, direction: str = 'ASC') -> 'SearchEngine':
        """Sıralama ekle"""
        self.sort_conditions.append((field, direction.upper()))
        return self
    
    def sort_by_relevance(self, search_fields: List[str] = None) -> 'SearchEngine':
        """Arama sonuçlarını ilgililik sırasına göre sırala"""
        if search_fields:
            self.search_fields = search_fields
        
        if self.search_query and self.search_fields:
            # MySQL'de MATCH AGAINST kullanarak relevance sıralama
            match_fields = ', '.join(self.search_fields)
            self.query_builder.order_by(
                f"MATCH({match_fields}) AGAINST(%s IN BOOLEAN MODE)",
                'DESC'
            )
        
        return self
    
    def _apply_search(self):
        """Arama koşullarını uygula"""
        if not self.search_query or not self.search_fields:
            return
        
        # Basit LIKE araması (full-text search yoksa)
        search_conditions = []
        search_values = []
        
        for field in self.search_fields:
            search_conditions.append(f"{field} LIKE %s")
            search_values.append(f"%{self.search_query}%")
        
        if search_conditions:
            # OR ile birleştir
            self.query_builder.where_conditions.append(f"({' OR '.join(search_conditions)})")
            self.query_builder.where_values.extend(search_values)
    
    def _apply_filters(self):
        """Filtre koşullarını uygula"""
        for field, value in self.filter_conditions.items():
            if field.endswith('_range'):
                base_field = field.replace('_range', '')
                range_data = value
                
                if range_data.get('min') is not None:
                    self.query_builder.where(base_field, '>=', range_data['min'])
                
                if range_data.get('max') is not None:
                    self.query_builder.where(base_field, '<=', range_data['max'])
            
            elif field.endswith('_in'):
                base_field = field.replace('_in', '')
                self.query_builder.where_in(base_field, value)
            
            elif field.endswith('_not_in'):
                base_field = field.replace('_not_in', '')
                self.query_builder.where_not_in(base_field, value)
            
            elif field.endswith('_null'):
                base_field = field.replace('_null', '')
                if value:
                    self.query_builder.where_null(base_field)
                else:
                    self.query_builder.where_not_null(base_field)
            
            elif field.endswith('_like'):
                base_field = field.replace('_like', '')
                self.query_builder.where_like(base_field, value)
            
            else:
                # Normal eşitlik filtresi
                self.query_builder.where(field, '=', value)
    
    def _apply_sorting(self):
        """Sıralama koşullarını uygula"""
        for field, direction in self.sort_conditions:
            self.query_builder.order_by(field, direction)
    
    def execute(self) -> List[Dict[str, Any]]:
        """Arama ve filtreleme uygula"""
        # Koşulları uygula
        self._apply_search()
        self._apply_filters()
        self._apply_sorting()
        
        # Sorguyu çalıştır
        return self.query_builder.get()
    
    def count(self) -> int:
        """Filtrelenmiş sonuç sayısını getir"""
        # Koşulları uygula
        self._apply_search()
        self._apply_filters()
        
        # Sayım yap
        return self.query_builder.count()
    
    def paginate(self, page: int, per_page: int) -> Dict[str, Any]:
        """Sayfalama ile arama yap"""
        # Koşulları uygula
        self._apply_search()
        self._apply_filters()
        self._apply_sorting()
        
        # Sayfalama uygula
        total = self.query_builder.count()
        self.query_builder.paginate(page, per_page)
        items = self.query_builder.get()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
            'has_previous': page > 1,
            'has_next': page * per_page < total
        }

class AdvancedSearch:
    """Gelişmiş arama sınıfı"""
    
    def __init__(self, table: str):
        self.table = table
        self.query_builder = QueryBuilder(table)
        self.search_engine = SearchEngine(self.query_builder)
    
    def search(self, query: str, fields: List[str] = None) -> 'AdvancedSearch':
        """Arama sorgusu ekle"""
        self.search_engine.search(query, fields)
        return self
    
    def filter(self, conditions: Dict[str, Any]) -> 'AdvancedSearch':
        """Filtre koşulları ekle"""
        self.search_engine.filter(conditions)
        return self
    
    def filter_range(self, field: str, min_value: Any = None, max_value: Any = None) -> 'AdvancedSearch':
        """Aralık filtresi ekle"""
        self.search_engine.filter_range(field, min_value, max_value)
        return self
    
    def filter_in(self, field: str, values: List[Any]) -> 'AdvancedSearch':
        """IN filtresi ekle"""
        self.search_engine.filter_in(field, values)
        return self
    
    def sort(self, field: str, direction: str = 'ASC') -> 'AdvancedSearch':
        """Sıralama ekle"""
        self.search_engine.sort(field, direction)
        return self
    
    def sort_by_relevance(self, search_fields: List[str] = None) -> 'AdvancedSearch':
        """İlgililik sırasına göre sırala"""
        self.search_engine.sort_by_relevance(search_fields)
        return self
    
    def get(self) -> List[Dict[str, Any]]:
        """Sonuçları getir"""
        return self.search_engine.execute()
    
    def count(self) -> int:
        """Sonuç sayısını getir"""
        return self.search_engine.count()
    
    def paginate(self, page: int, per_page: int) -> Dict[str, Any]:
        """Sayfalama ile getir"""
        return self.search_engine.paginate(page, per_page)

class SearchFilter:
    """Arama filtresi yardımcı sınıfı"""
    
    @staticmethod
    def parse_search_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """URL parametrelerinden arama koşullarını parse et"""
        search_conditions = {}
        
        for key, value in params.items():
            if not value:
                continue
            
            # Arama sorgusu
            if key == 'q':
                search_conditions['search_query'] = value
            
            # Aralık filtreleri
            elif key.endswith('_min'):
                field = key.replace('_min', '')
                if field not in search_conditions:
                    search_conditions[field] = {}
                search_conditions[field]['min'] = value
            
            elif key.endswith('_max'):
                field = key.replace('_max', '')
                if field not in search_conditions:
                    search_conditions[field] = {}
                search_conditions[field]['max'] = value
            
            # Liste filtreleri
            elif key.endswith('[]'):
                field = key.replace('[]', '')
                if isinstance(value, list):
                    search_conditions[field] = value
                else:
                    search_conditions[field] = [value]
            
            # Boolean filtreler
            elif value in ['true', 'false', '1', '0']:
                search_conditions[key] = value in ['true', '1']
            
            # Normal filtreler
            else:
                search_conditions[key] = value
        
        return search_conditions
    
    @staticmethod
    def build_search_url(base_url: str, params: Dict[str, Any]) -> str:
        """Arama parametrelerinden URL oluştur"""
        if not params:
            return base_url
        
        param_strings = []
        for key, value in params.items():
            if value is not None:
                if isinstance(value, list):
                    for item in value:
                        param_strings.append(f"{key}[]={item}")
                else:
                    param_strings.append(f"{key}={value}")
        
        if param_strings:
            return f"{base_url}?{'&'.join(param_strings)}"
        else:
            return base_url

# Kullanım kolaylığı için fonksiyonlar
def search(table: str, query: str = "", fields: List[str] = None) -> AdvancedSearch:
    """Yeni arama başlat"""
    search_instance = AdvancedSearch(table)
    if query:
        search_instance.search(query, fields)
    return search_instance

def filter_table(table: str, conditions: Dict[str, Any]) -> AdvancedSearch:
    """Tabloyu filtrele"""
    search_instance = AdvancedSearch(table)
    search_instance.filter(conditions)
    return search_instance 