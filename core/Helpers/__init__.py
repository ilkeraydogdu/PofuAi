"""
Helper Functions
Tüm uygulama genelinde kullanılan yardımcı fonksiyonlar
"""
import os
import hashlib
import random
import string
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse

# Global değişkenler
_app_url = None
_asset_url = None

def set_app_url(url: str):
    """Uygulama URL'ini ayarla"""
    global _app_url
    _app_url = url.rstrip('/')

def set_asset_url(url: str):
    """Asset URL'ini ayarla"""
    global _asset_url
    _asset_url = url.rstrip('/')

def asset(path: str) -> str:
    """Asset URL'ini oluştur"""
    if not path.startswith(('http://', 'https://', '//')):
        if _asset_url:
            return urljoin(_asset_url + '/', path.lstrip('/'))
        return f"/static/{path.lstrip('/')}"
    return path

def url(name: str = None, params: Dict[str, Any] = None) -> str:
    """URL oluştur"""
    if name is None:
        return _app_url or '/'
    
    # Route name'den URL oluştur (basit implementasyon)
    routes = {
        'home': '/',
        'login': '/login',
        'register': '/register',
        'profile': '/profile',
        'users': '/users',
        'posts': '/posts',
        'admin': '/admin'
    }
    
    base_url = routes.get(name, f'/{name}')
    
    if params:
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    return base_url

def redirect(path: str, status: int = 302) -> Dict[str, Any]:
    """Redirect response'u oluştur"""
    return {
        'type': 'redirect',
        'url': path,
        'status': status
    }

def view(name: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """View response'u oluştur"""
    return {
        'type': 'view',
        'template': name,
        'data': data or {}
    }

def csrf_token() -> str:
    """CSRF token oluştur"""
    return hashlib.md5(f"{random.random()}{datetime.now()}".encode()).hexdigest()

def old(key: str, default: str = '') -> str:
    """Eski form değerini al"""
    # Session'dan eski değeri al
    return default

def error(key: str) -> str:
    """Hata mesajını al"""
    # Session'dan hata mesajını al
    return ''

def has_error(key: str) -> bool:
    """Hata var mı kontrol et"""
    return bool(error(key))

def is_active(path: str) -> str:
    """Aktif link kontrolü"""
    # Basit implementasyon
    return 'active' if path in request.path else ''

def format_date(date: Union[str, datetime], format: str = '%d.%m.%Y') -> str:
    """Tarihi formatla"""
    if isinstance(date, str):
        date = datetime.fromisoformat(date.replace('Z', '+00:00'))
    return date.strftime(format)

def format_datetime(date: Union[str, datetime], format: str = '%d.%m.%Y %H:%M') -> str:
    """Tarih ve saati formatla"""
    if isinstance(date, str):
        date = datetime.fromisoformat(date.replace('Z', '+00:00'))
    return date.strftime(format)

def time_ago(date: Union[str, datetime]) -> str:
    """Geçen süreyi hesapla"""
    if isinstance(date, str):
        date = datetime.fromisoformat(date.replace('Z', '+00:00'))
    
    now = datetime.now()
    diff = now - date
    
    if diff.days > 0:
        return f"{diff.days} gün önce"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} saat önce"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} dakika önce"
    else:
        return "Az önce"

def format_number(number: Union[int, float], decimals: int = 0) -> str:
    """Sayıyı formatla"""
    if decimals > 0:
        return f"{number:,.{decimals}f}"
    return f"{number:,}"

def format_currency(amount: Union[int, float], currency: str = '₺') -> str:
    """Para birimini formatla"""
    return f"{currency}{format_number(amount, 2)}"

def format_file_size(size: int) -> str:
    """Dosya boyutunu formatla"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def generate_random_string(length: int = 10) -> str:
    """Rastgele string oluştur"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_slug(text: str) -> str:
    """Slug oluştur"""
    import re
    # Türkçe karakterleri değiştir
    text = text.lower()
    text = text.replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i')
    text = text.replace('ö', 'o').replace('ş', 's').replace('ü', 'u')
    # Sadece harf, rakam ve tire bırak
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    # Boşlukları tire ile değiştir
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def mask_email(email: str) -> str:
    """Email'i maskele"""
    if '@' not in email:
        return email
    
    username, domain = email.split('@')
    if len(username) <= 2:
        masked_username = username
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
    
    return f"{masked_username}@{domain}"

def mask_phone(phone: str) -> str:
    """Telefon numarasını maskele"""
    if len(phone) <= 4:
        return phone
    
    return phone[:2] + '*' * (len(phone) - 4) + phone[-2:]

def truncate(text: str, length: int = 100, suffix: str = '...') -> str:
    """Metni kısalt"""
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix

def excerpt(text: str, length: int = 150) -> str:
    """Metin özeti oluştur"""
    text = truncate(text, length)
    # Son kelimeyi tamamla
    if ' ' in text:
        text = text.rsplit(' ', 1)[0]
    return text + '...'

def is_mobile() -> bool:
    """Mobil cihaz mı kontrol et"""
    # Basit user agent kontrolü
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'blackberry']
    return any(keyword in user_agent for keyword in mobile_keywords)

def is_ajax() -> bool:
    """AJAX request mi kontrol et"""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

def get_client_ip() -> str:
    """Client IP adresini al"""
    # Proxy header'ları kontrol et
    for header in ['X-Forwarded-For', 'X-Real-IP', 'X-Client-IP']:
        ip = request.headers.get(header)
        if ip:
            return ip.split(',')[0].strip()
    
    return request.remote_addr

def get_user_agent() -> str:
    """User agent'ı al"""
    return request.headers.get('User-Agent', '')

def is_secure() -> bool:
    """HTTPS mi kontrol et"""
    return request.is_secure

def get_domain() -> str:
    """Domain'i al"""
    return request.host

def get_scheme() -> str:
    """Scheme'i al (http/https)"""
    return request.scheme

# Global request objesi (Flask/Django benzeri)
request = None

def set_request(req):
    """Global request objesini ayarla"""
    global request
    request = req 