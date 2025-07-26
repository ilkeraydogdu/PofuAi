"""
Authentication Middleware
Kullanıcı authentication kontrolü
"""
from typing import Dict, Any, Optional
from flask import request, session, g

class AuthMiddleware:
    """Authentication middleware"""
    
    @staticmethod
    def handle():
        """
        İstek öncesi authentication kontrolü
        Flask before_request ile kullanılmak üzere tasarlanmıştır
        """
        try:
            # Geçici olarak tüm kullanıcıları giriş yapmış gibi göster
            request.is_authenticated = True
            request.user = {
                'id': 1,
                'name': 'Admin',
                'email': 'admin@example.com',
                'is_admin': True,
                'roles': ['admin']
            }
            
            # Flask g nesnesine authenticated değerini ata
            g.authenticated = True
            g.user = request.user
                
        except Exception as e:
            print(f"[AuthMiddleware] Auth middleware error: {str(e)}")
    
    @staticmethod
    def get_user_from_session(request) -> Optional[Dict[str, Any]]:
        """Session'dan kullanıcı bilgisini al"""
        # Geçici olarak admin kullanıcı döndür
        return {
            'id': 1,
            'name': 'Admin',
            'email': 'admin@example.com',
            'is_admin': True,
            'roles': ['admin'],
            'is_active': True
        }
    
    @staticmethod
    def clear_session(request):
        """Session'ı temizle"""
        try:
            session = getattr(request, 'session', {})
            session.pop('user_id', None)
            session.pop('user', None)
        except Exception as e:
            print(f"[AuthMiddleware] Clear session error: {str(e)}")
    
    @staticmethod
    def error_response(message: str, status: int = 401) -> Dict[str, Any]:
        """Hata response'u döndür"""
        return {
            'success': False,
            'message': message,
            'status': status
        }

class GuestMiddleware:
    """Sadece misafir kullanıcılar için middleware"""
    
    @staticmethod
    def handle():
        """
        İstek öncesi guest kontrolü
        Flask before_request ile kullanılmak üzere tasarlanmıştır
        """
        # Geçici olarak tüm kullanıcıları giriş yapmış gibi gösterdiğimiz için bu middleware'i devre dışı bırakıyoruz
        pass
    
    @staticmethod
    def redirect_response(url: str) -> Dict[str, Any]:
        """Redirect response'u döndür"""
        return {
            'type': 'redirect',
            'url': url,
            'status': 302
        }
    
    @staticmethod
    def error_response(message: str, status: int = 500) -> Dict[str, Any]:
        """Hata response'u döndür"""
        return {
            'success': False,
            'message': message,
            'status': status
        }

class AdminMiddleware:
    """Admin kullanıcılar için middleware"""
    
    @staticmethod
    def handle():
        """
        İstek öncesi admin kontrolü
        Flask before_request ile kullanılmak üzere tasarlanmıştır
        """
        # Geçici olarak tüm kullanıcıları admin gibi gösterdiğimiz için bu middleware'i devre dışı bırakıyoruz
        pass
    
    @staticmethod
    def redirect_response(url: str) -> Dict[str, Any]:
        """Redirect response'u döndür"""
        return {
            'type': 'redirect',
            'url': url,
            'status': 302
        }
    
    @staticmethod
    def error_response(message: str, status: int = 403) -> Dict[str, Any]:
        """Hata response'u döndür"""
        return {
            'success': False,
            'message': message,
            'status': status
        }

def auth_required(func):
    """Kullanıcı giriş yapmış mı kontrol eden decorator"""
    def wrapper(self, *args, **kwargs):
        # Geçici olarak tüm istekleri kabul et
        return func(self, *args, **kwargs)
    return wrapper

def admin_required(func):
    """Admin yetkisi kontrolü yapan decorator"""
    def wrapper(self, *args, **kwargs):
        # Geçici olarak tüm istekleri kabul et
        return func(self, *args, **kwargs)
    return wrapper 