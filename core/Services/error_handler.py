"""
Error Handler
Merkezi hata yönetim servisi
"""

from typing import Dict, Any, Optional, Union
import traceback
import sys
import os
from datetime import datetime
from flask import request, render_template_string

# Hata sayfaları için basit component
class ErrorPageComponent:
    """Hata sayfaları için basit component"""
    
    def render(self, config):
        """Hata sayfasını render et"""
        title = config.get('title', 'Hata')
        message = config.get('message', 'Bir hata oluştu.')
        code = config.get('code', 500)
        
        return f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link href="/static/assets/css/bootstrap.min.css" rel="stylesheet">
            <link href="/static/assets/css/bootstrap-extended.css" rel="stylesheet">
            <link href="/static/assets/plugins/perfect-scrollbar/css/perfect-scrollbar.css" rel="stylesheet">
            <link href="/static/assets/plugins/metismenu/metisMenu.min.css" rel="stylesheet">
            <link href="/static/sass/main.css" rel="stylesheet">
            <link href="/static/sass/blue-theme.css" rel="stylesheet">
            <link href="/static/sass/responsive.css" rel="stylesheet">
            <style>
                body {{
                    background: linear-gradient(to right, #0d6efd, #0dcaf0);
                    height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .error-container {{
                    max-width: 600px;
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                    padding: 3rem;
                    text-align: center;
                }}
                .error-code {{
                    font-size: 8rem;
                    font-weight: 700;
                    background: linear-gradient(45deg, #0d6efd, #0dcaf0);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 1rem;
                    line-height: 1;
                }}
                .error-title {{
                    font-size: 2rem;
                    margin-bottom: 1.5rem;
                    color: #333;
                }}
                .error-message {{
                    font-size: 1.2rem;
                    margin-bottom: 2rem;
                    color: #666;
                }}
                .btn-home {{
                    background: linear-gradient(45deg, #0d6efd, #0dcaf0);
                    border: none;
                    padding: 12px 30px;
                    font-size: 1.1rem;
                    font-weight: 500;
                    transition: all 0.3s;
                }}
                .btn-home:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 5px 15px rgba(13, 110, 253, 0.3);
                }}
                .error-img {{
                    max-width: 250px;
                    margin-bottom: 2rem;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-code">{code}</div>
                <h1 class="error-title">{title}</h1>
                <p class="error-message">{message}</p>
                <a href="/" class="btn btn-primary btn-home">Ana Sayfaya Dön</a>
            </div>
            
            <script src="/static/assets/js/jquery.min.js"></script>
            <script src="/static/assets/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """

import sys
import traceback
from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from core.Services.logger import LoggerService

class ErrorHandler:
    """
    Error Handler Servisi
    Uygulamada oluşan hataları yönetir ve işler
    """
    
    def __init__(self):
        """Error handler başlat"""
        self.logger = LoggerService.get_logger()
        self.error_page_component = ErrorPageComponent()
    
    def handle_error(self, error, request=None):
        """
        Hatayı işle ve uygun yanıtı döndür
        
        Args:
            error: Yakalanan hata
            request: HTTP isteği (opsiyonel)
            
        Returns:
            Flask Response: Hata yanıtı
        """
        # Hata detaylarını logla
        self._log_error(error, request)
        
        # HTTP hatası ise
        if isinstance(error, HTTPException):
            return self.handle_http_error(error)
        
        # Diğer hatalar
        return self._handle_general_error(error)
    
    def _log_error(self, error, request=None):
        """
        Hatayı detaylı bir şekilde logla
        
        Args:
            error: Yakalanan hata
            request: HTTP isteği (opsiyonel)
        """
        # Hata mesajı
        error_message = f"Hata: {str(error)}"
        
        # Traceback bilgisi
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        traceback_str = ''.join(tb)
        
        # İstek bilgileri
        request_info = {}
        if request:
            # İstek bilgilerini topla
            request_info = {
                'method': getattr(request, 'method', 'UNKNOWN'),
                'path': getattr(request, 'path', 'UNKNOWN'),
                'remote_addr': getattr(request, 'remote_addr', 'UNKNOWN'),
                'user_agent': request.headers.get('User-Agent', 'UNKNOWN') if hasattr(request, 'headers') else 'UNKNOWN',
                'content_type': request.headers.get('Content-Type', 'UNKNOWN') if hasattr(request, 'headers') else 'UNKNOWN'
            }
            
            # Form veya JSON verileri
            if hasattr(request, 'form') and request.form:
                request_info['form_data'] = dict(request.form)
            
            # JSON verisi kontrolü - doğrudan get_json çağrısı yapmadan
            if hasattr(request, 'headers') and 'application/json' in request.headers.get('Content-Type', '').lower():
                try:
                    # JSON verilerini güvenli bir şekilde kontrol et (force=True ile)
                    if request.get_data():
                        json_data = request.get_json(silent=True, force=True)
                        if json_data:
                            request_info['json_data'] = json_data
                except Exception as json_error:
                    request_info['json_error'] = str(json_error)
        
        # Tam hata bilgisini logla
        log_message = f"{error_message}\n"
        log_message += f"Traceback:\n{traceback_str}\n"
        
        if request_info:
            log_message += f"Request Info:\n"
            for key, value in request_info.items():
                log_message += f"  {key}: {value}\n"
        
        self.logger.error(log_message)
    
    def handle_http_error(self, error, message=None, request=None):
        """
        HTTP hatalarını işle
        
        Args:
            error: HTTP hatası veya status kodu
            message: Özel hata mesajı (opsiyonel)
            request: HTTP isteği (opsiyonel)
            
        Returns:
            Flask Response: Hata yanıtı
        """
        # Error mesajı ve status kodu oluştur
        if isinstance(error, HTTPException):
            status_code = error.code
            error_message = message or error.description or str(error)
        elif isinstance(error, int):
            status_code = error
            error_message = message or f"HTTP {status_code}"
        else:
            status_code = 500
            error_message = message or str(error)
        
        # İstek bilgilerini al
        req = request or (hasattr(error, 'request') and error.request) or getattr(error, 'request', None)
        
        # AJAX/API isteği kontrolü
        if self._is_ajax_request(req):
            response = {
                'status': 'error',
                'code': status_code,
                'message': error_message
            }
            
            # Content type hatası için özel bilgi
            if status_code == 415:
                acceptable_types = ['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data']
                content_type = req.headers.get('Content-Type', 'UNKNOWN') if req and hasattr(req, 'headers') else 'UNKNOWN'
                response['detail'] = {
                    'received_content_type': content_type,
                    'acceptable_types': acceptable_types,
                    'tip': 'İstek Content-Type değerini uygun bir değerle ayarlayın veya form verisi gönderin.'
                }
                
            return jsonify(response), status_code
        
        # Status koduna göre hata sayfası
        if status_code == 404:
            return self.error_page_component.render({'code': 404, 'title': 'Sayfa Bulunamadı', 'message': 'Aradığınız sayfa bulunamadı.'}), 404
        elif status_code == 403:
            return self.error_page_component.render({'code': 403, 'title': 'Yetkisiz Erişim', 'message': 'Bu sayfaya erişim yetkiniz yok.'}), 403
        elif status_code == 500:
            return self.error_page_component.render({'code': 500, 'title': 'Sunucu Hatası', 'message': 'Sunucu tarafında bir hata oluştu.'}), 500
        elif status_code == 401:
            return self.error_page_component.render({'code': 401, 'title': 'Yetkilendirme Gerekli', 'message': 'Bu sayfaya erişim için yetkilendirme gerekli.'}), 401
        elif status_code == 400:
            return self.error_page_component.render({'code': 400, 'title': 'Geçersiz İstek', 'message': 'İstek formatı veya içeriği geçersiz.'}), 400
        elif status_code == 415:  # Unsupported Media Type
            return self.error_page_component.render(
                415, 
                "Unsupported Media Type", 
                "Gönderilen içerik tipi desteklenmiyor. JSON içeriği için 'Content-Type: application/json' header'ı kullanın."
            ), 415
        
        # Genel hata sayfası
        return self.error_page_component.render({
            'code': status_code,
            'title': 'Hata',
            'message': error_message
        }), status_code
    
    def _handle_general_error(self, error: Exception) -> str:
        """Genel hataları işle"""
        # Hata mesajını ve stack trace'i al
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        # Hata detaylarını logla
        self.logger.error(f"Hata: {error_message}")
        self.logger.error(f"Traceback:\n{stack_trace}")
        
        # Hata sayfasını render et
        return self.error_page_component.render({
            'title': 'Sunucu Hatası',
            'message': 'Bir sunucu hatası oluştu. Lütfen daha sonra tekrar deneyiniz.',
            'code': 500
        }), 500
    
    def _is_ajax_request(self, req=None):
        """
        AJAX/API isteği mi kontrol et
        
        Args:
            req: İstek nesnesi (opsiyonel)
            
        Returns:
            bool: AJAX isteği ise True
        """
        # İstek nesnesini al
        current_request = req or request
        
        if not current_request:
            return False
        
        # Header ve path kontrolü
        if hasattr(current_request, 'headers') and hasattr(current_request, 'path'):
            return (
                current_request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                current_request.headers.get('Accept', '').startswith('application/json') or
                current_request.path.startswith('/api/')
            )
            
        return False
    
    def _is_debug_mode(self):
        """
        Debug mod mu kontrol et
        
        Returns:
            bool: Debug mod aktifse True
        """
        if hasattr(sys, 'gettrace') and sys.gettrace():
            return True
            
        if hasattr(request, 'app') and hasattr(request.app, 'debug'):
            return request.app.debug
            
        return False

# Global error handler instance
error_handler = ErrorHandler() 