"""
URL Generator
URL oluşturma, formatlama ve route yönetimi için yardımcı sınıf
"""
from typing import Dict, List, Any, Optional, Union
import re
from urllib.parse import urlencode

class URLGenerator:
    """URL oluşturma ve yönetim sınıfı"""
    
    def __init__(self, base_url: str = "", routes: Dict[str, Any] = None):
        """
        URL Generator
        
        Args:
            base_url (str): Temel URL (örn: https://example.com)
            routes (Dict): Route isimleri ve yolları sözlüğü
        """
        self.base_url = base_url.rstrip('/')
        self.routes = routes or {}
    
    def url(self, path: str, params: Dict[str, Any] = None, fragment: str = "") -> str:
        """
        URL oluştur
        
        Args:
            path (str): URL yolu (/path/to/resource)
            params (Dict): Query parametreleri
            fragment (str): URL fragment (hash)
            
        Returns:
            str: Oluşturulan URL
        """
        # Path'i normalize et
        if not path.startswith('/') and not path.startswith('http'):
            path = '/' + path
        
        # Base URL ile birleştir
        if path.startswith('/'):
            url = self.base_url + path
        else:
            url = path
        
        # Query parametrelerini ekle
        if params:
            url += '?' + urlencode(params)
        
        # Fragment ekle
        if fragment:
            url += '#' + fragment
        
        return url
    
    def route(self, name: str, params: Dict[str, Any] = None, query: Dict[str, Any] = None) -> str:
        """
        İsimli route'a göre URL oluştur
        
        Args:
            name (str): Route adı
            params (Dict): Route parametreleri
            query (Dict): Query string parametreleri
            
        Returns:
            str: Oluşturulan URL
            
        Raises:
            ValueError: İsimli route bulunamadığında
        """
        if name not in self.routes:
            raise ValueError(f"Route not found: {name}")
        
        route_path = self.routes[name]
        
        # Route parametrelerini değiştir
        if params:
            for key, value in params.items():
                pattern = '{' + key + '}'
                route_path = route_path.replace(pattern, str(value))
        
        # Query string ekle
        if query:
            route_path += '?' + urlencode(query)
        
        # Base URL ekle
        if not route_path.startswith('http'):
            route_path = self.base_url + route_path
        
        return route_path
    
    def register_route(self, name: str, path: str) -> None:
        """
        Yeni bir route kaydet
        
        Args:
            name (str): Route adı
            path (str): Route yolu
        """
        self.routes[name] = path
    
    def register_routes(self, routes: Dict[str, str]) -> None:
        """
        Çoklu route kaydet
        
        Args:
            routes (Dict): Route adları ve yolları
        """
        self.routes.update(routes)
    
    def get_route(self, name: str) -> Optional[str]:
        """
        Route yolunu döndür
        
        Args:
            name (str): Route adı
            
        Returns:
            Optional[str]: Route yolu veya None
        """
        return self.routes.get(name)
    
    def asset_url(self, path: str) -> str:
        """
        Asset URL'i oluştur
        
        Args:
            path (str): Asset yolu
            
        Returns:
            str: Asset URL'i
        """
        # Path'i normalize et
        path = path.lstrip('/')
        
        return f"{self.base_url}/static/{path}"
    
    def image_url(self, path: str, width: int = None, height: int = None) -> str:
        """
        Resim URL'i oluştur
        
        Args:
            path (str): Resim yolu
            width (int, optional): Genişlik
            height (int, optional): Yükseklik
            
        Returns:
            str: Resim URL'i
        """
        # Path'i normalize et
        path = path.lstrip('/')
        
        # Boyut parametreleri ekle
        params = {}
        if width:
            params['w'] = width
        if height:
            params['h'] = height
        
        # URL oluştur
        url = f"{self.base_url}/images/{path}"
        
        # Query string ekle
        if params:
            url += '?' + urlencode(params)
        
        return url
    
    def generate_slug(self, text: str) -> str:
        """
        Slug oluştur
        
        Args:
            text (str): Metin
            
        Returns:
            str: Slug formatında metin
        """
        # Türkçe karakterleri değiştir
        tr_chars = {
            'ç': 'c', 'Ç': 'C',
            'ğ': 'g', 'Ğ': 'G',
            'ı': 'i', 'İ': 'I',
            'ö': 'o', 'Ö': 'O',
            'ş': 's', 'Ş': 'S',
            'ü': 'u', 'Ü': 'U'
        }
        
        for tr_char, en_char in tr_chars.items():
            text = text.replace(tr_char, en_char)
        
        # Küçük harfe çevir
        text = text.lower()
        
        # Alfanumerik olmayan karakterleri tire ile değiştir
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        
        # Boşlukları tire ile değiştir
        text = re.sub(r'\s+', '-', text)
        
        # Birden fazla tireyi tek tireye çevir
        text = re.sub(r'-+', '-', text)
        
        # Başındaki ve sonundaki tireleri kaldır
        text = text.strip('-')
        
        return text
    
    def current_url(self, request = None) -> str:
        """
        Mevcut URL'yi döndür
        
        Args:
            request: Flask request objesi (opsiyonel)
            
        Returns:
            str: Mevcut URL
        """
        if request:
            # Flask request objesi kullan
            path = request.path
            query = request.query_string.decode() if request.query_string else ''
            
            url = self.base_url + path
            if query:
                url += '?' + query
                
            return url
        else:
            # Request olmadan mevcut URL döndürülemez
            return self.base_url
    
    def is_valid_url(self, url: str) -> bool:
        """
        URL'nin geçerli olup olmadığını kontrol et
        
        Args:
            url (str): Kontrol edilecek URL
            
        Returns:
            bool: URL geçerli mi
        """
        pattern = re.compile(
            r'^(?:http|https)://'  # http:// veya https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...veya IP
            r'(?::\d+)?'  # opsiyonel port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(pattern.match(url))
    
    def is_external_url(self, url: str) -> bool:
        """
        URL'nin harici olup olmadığını kontrol et
        
        Args:
            url (str): Kontrol edilecek URL
            
        Returns:
            bool: URL harici mi
        """
        if not url.startswith('http'):
            return False
            
        return not url.startswith(self.base_url)

# Singleton URL Generator instance
_url_generator = None

def get_url_generator() -> URLGenerator:
    """Global URL generator instance'ı döndür"""
    global _url_generator
    if _url_generator is None:
        _url_generator = URLGenerator()
    return _url_generator
    
def url(path: str, params: Dict[str, Any] = None, fragment: str = "") -> str:
    """URL oluştur (helper fonksiyon)"""
    return get_url_generator().url(path, params, fragment)

def route(name: str, params: Dict[str, Any] = None, query: Dict[str, Any] = None) -> str:
    """İsimli route'a göre URL oluştur (helper fonksiyon)"""
    return get_url_generator().route(name, params, query)

def asset_url(path: str) -> str:
    """Asset URL'i oluştur (helper fonksiyon)"""
    return get_url_generator().asset_url(path)

def image_url(path: str, width: int = None, height: int = None) -> str:
    """Resim URL'i oluştur (helper fonksiyon)"""
    return get_url_generator().image_url(path, width, height)

def generate_slug(text: str) -> str:
    """Slug oluştur (helper fonksiyon)"""
    return get_url_generator().generate_slug(text) 