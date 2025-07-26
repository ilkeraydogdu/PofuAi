"""
Sayfalama Sistemi
Sayfa bilgileri, navigasyon ve URL yönetimi
"""

from typing import List, Dict, Any, Optional
from math import ceil
from .query_builder import QueryBuilder

class Pagination:
    """Sayfalama sınıfı"""
    
    def __init__(self, items: List[Any], total: int, page: int, per_page: int, 
                 base_url: str = "", query_params: Dict[str, Any] = None):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.base_url = base_url
        self.query_params = query_params or {}
        
        # Hesaplanan değerler
        self.total_pages = ceil(total / per_page) if total > 0 else 0
        self.has_previous = page > 1
        self.has_next = page < self.total_pages
        self.previous_page = page - 1 if self.has_previous else None
        self.next_page = page + 1 if self.has_next else None
        
        # Sayfa aralığı
        self.start_index = (page - 1) * per_page + 1 if total > 0 else 0
        self.end_index = min(page * per_page, total)
    
    @classmethod
    def from_query_builder(cls, query_builder: QueryBuilder, page: int, per_page: int,
                          base_url: str = "", query_params: Dict[str, Any] = None) -> 'Pagination':
        """QueryBuilder'dan sayfalama oluştur"""
        # Toplam kayıt sayısını al
        total = query_builder.count()
        
        # Sayfalama uygula
        query_builder.paginate(page, per_page)
        items = query_builder.get()
        
        return cls(items, total, page, per_page, base_url, query_params)
    
    def get_page_url(self, page_number: int) -> str:
        """Belirli bir sayfa için URL oluştur"""
        if not self.base_url:
            return ""
        
        # Query parametrelerini kopyala
        params = self.query_params.copy()
        params['page'] = page_number
        
        # URL parametrelerini oluştur
        param_strings = []
        for key, value in params.items():
            if value is not None:
                param_strings.append(f"{key}={value}")
        
        if param_strings:
            return f"{self.base_url}?{'&'.join(param_strings)}"
        else:
            return self.base_url
    
    def get_previous_url(self) -> Optional[str]:
        """Önceki sayfa URL'i"""
        if self.has_previous:
            return self.get_page_url(self.previous_page)
        return None
    
    def get_next_url(self) -> Optional[str]:
        """Sonraki sayfa URL'i"""
        if self.has_next:
            return self.get_page_url(self.next_page)
        return None
    
    def get_first_url(self) -> str:
        """İlk sayfa URL'i"""
        return self.get_page_url(1)
    
    def get_last_url(self) -> str:
        """Son sayfa URL'i"""
        return self.get_page_url(self.total_pages)
    
    def get_page_range(self, delta: int = 2) -> List[int]:
        """Sayfa aralığını getir"""
        if self.total_pages <= 0:
            return []
        
        start = max(1, self.page - delta)
        end = min(self.total_pages, self.page + delta)
        
        return list(range(start, end + 1))
    
    def get_navigation_links(self, delta: int = 2) -> List[Dict[str, Any]]:
        """Navigasyon linklerini getir"""
        links = []
        
        # İlk sayfa
        if self.page > 1:
            links.append({
                'page': 1,
                'url': self.get_first_url(),
                'text': 'İlk',
                'is_current': False,
                'is_disabled': False
            })
        
        # Önceki sayfa
        if self.has_previous:
            links.append({
                'page': self.previous_page,
                'url': self.get_previous_url(),
                'text': 'Önceki',
                'is_current': False,
                'is_disabled': False
            })
        
        # Sayfa aralığı
        for page_num in self.get_page_range(delta):
            links.append({
                'page': page_num,
                'url': self.get_page_url(page_num),
                'text': str(page_num),
                'is_current': page_num == self.page,
                'is_disabled': False
            })
        
        # Sonraki sayfa
        if self.has_next:
            links.append({
                'page': self.next_page,
                'url': self.get_next_url(),
                'text': 'Sonraki',
                'is_current': False,
                'is_disabled': False
            })
        
        # Son sayfa
        if self.page < self.total_pages:
            links.append({
                'page': self.total_pages,
                'url': self.get_last_url(),
                'text': 'Son',
                'is_current': False,
                'is_disabled': False
            })
        
        return links
    
    def to_dict(self) -> Dict[str, Any]:
        """Sayfalama bilgilerini dictionary'e çevir"""
        return {
            'items': self.items,
            'total': self.total,
            'page': self.page,
            'per_page': self.per_page,
            'total_pages': self.total_pages,
            'has_previous': self.has_previous,
            'has_next': self.has_next,
            'previous_page': self.previous_page,
            'next_page': self.next_page,
            'start_index': self.start_index,
            'end_index': self.end_index,
            'navigation_links': self.get_navigation_links()
        }
    
    def __len__(self) -> int:
        """Mevcut sayfadaki öğe sayısı"""
        return len(self.items)
    
    def __iter__(self):
        """Öğeleri iterate et"""
        return iter(self.items)
    
    def __getitem__(self, index):
        """Öğelere erişim"""
        return self.items[index]

class Paginator:
    """Sayfalama yardımcı sınıfı"""
    
    def __init__(self, query_builder: QueryBuilder, per_page: int = 20):
        self.query_builder = query_builder
        self.per_page = per_page
    
    def paginate(self, page: int, base_url: str = "", 
                 query_params: Dict[str, Any] = None) -> Pagination:
        """Sayfalama uygula"""
        return Pagination.from_query_builder(
            self.query_builder, 
            page, 
            self.per_page, 
            base_url, 
            query_params
        )
    
    def simple_paginate(self, page: int) -> Dict[str, Any]:
        """Basit sayfalama (sadece önceki/sonraki)"""
        total = self.query_builder.count()
        self.query_builder.paginate(page, self.per_page)
        items = self.query_builder.get()
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': self.per_page,
            'has_previous': page > 1,
            'has_next': page * self.per_page < total,
            'previous_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page * self.per_page < total else None
        }

# Kullanım kolaylığı için fonksiyonlar
def paginate(query_builder: QueryBuilder, page: int, per_page: int = 20,
             base_url: str = "", query_params: Dict[str, Any] = None) -> Pagination:
    """QueryBuilder'dan sayfalama oluştur"""
    return Pagination.from_query_builder(query_builder, page, per_page, base_url, query_params)

def simple_paginate(query_builder: QueryBuilder, page: int, per_page: int = 20) -> Dict[str, Any]:
    """Basit sayfalama oluştur"""
    paginator = Paginator(query_builder, per_page)
    return paginator.simple_paginate(page) 