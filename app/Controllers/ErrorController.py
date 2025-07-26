"""
Error Controller
Hata sayfaları controller'ı
"""
from flask import request, render_template_string
from app.Controllers.BaseController import BaseController
from core.Services.error_handler import error_handler, ErrorPageComponent

class ErrorController(BaseController):
    """Error controller'ı"""
    
    def __init__(self):
        super().__init__()
        self.error_component = ErrorPageComponent()
    
    def error_404(self, e):
        """404 sayfası"""
        try:
            return self.error_component.render({
                'title': 'Sayfa Bulunamadı',
                'message': 'Aradığınız sayfa bulunamadı.',
                'code': 404
            }), 404
        except Exception as ex:
            return error_handler.handle_error(ex, request)
    
    def error_500(self, e):
        """500 sayfası"""
        try:
            return self.error_component.render({
                'title': 'Sunucu Hatası',
                'message': 'Bir sunucu hatası oluştu.',
                'code': 500
            }), 500
        except Exception as ex:
            return error_handler.handle_error(ex, request)
    
    def error_403(self, e):
        """403 sayfası"""
        try:
            return self.error_component.render({
                'title': 'Erişim Reddedildi',
                'message': 'Bu sayfaya erişim izniniz yok.',
                'code': 403
            }), 403
        except Exception as ex:
            return error_handler.handle_error(ex, request)
    
    def error_401(self, e):
        """401 sayfası"""
        try:
            return self.error_component.render({
                'title': 'Kimlik Doğrulama Gerekli',
                'message': 'Bu sayfaya erişmek için giriş yapmalısınız.',
                'code': 401
            }), 401
        except Exception as ex:
            return error_handler.handle_error(ex, request) 