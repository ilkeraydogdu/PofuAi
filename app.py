#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi Flask Application

Merkezi application dosyası ve routing konfigürasyonu
"""
import os
import re
import sys
from flask import Flask, render_template, session, request, send_from_directory, redirect, g
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix
from core.Route.web_routes import router as web_router
from core.Services.logger import LoggerService
from core.Services.error_handler import error_handler
from app.Middleware.SessionMiddleware import SessionMiddleware
from app.Middleware.AuthMiddleware import AuthMiddleware
from app.Models.User import User
import json

# Proje kök dizini
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Kök dizini sys.path'e ekle
sys.path.append(ROOT_DIR)

# Flask uygulamasını oluştur
app = Flask(__name__, 
            static_folder=os.path.join(ROOT_DIR, 'public/static'),
            template_folder=os.path.join(ROOT_DIR, 'public/Views'))

# ProxyFix middleware'i ekle
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# Uygulama ayarları
app.config.update({
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'your-secret-key'),
    'DEBUG': os.environ.get('FLASK_ENV', 'development') == 'development',
    'SESSION_TYPE': 'filesystem',
    'SESSION_PERMANENT': False,
    'SESSION_USE_SIGNER': True,
    'SESSION_FILE_DIR': os.path.join(ROOT_DIR, 'storage', 'sessions'),
    'SEND_FILE_MAX_AGE_DEFAULT': 0,
    'TRAP_BAD_REQUEST_ERRORS': False,
    'PRESERVE_CONTEXT_ON_EXCEPTION': False
})

# JSON formatını ayarla
app.json.compact = False

# Middleware'leri ekle
app.before_request(SessionMiddleware.handle)
app.before_request(AuthMiddleware.handle)

# Route'ları kaydet
web_router['register_routes'](app)

# Hata yönetimini aktifleştir
app.register_error_handler(Exception, error_handler.handle_error)

# Logging servisini başlat
logger = LoggerService.get_logger()

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
            <style>
                body {{ height: 100vh; display: flex; align-items: center; justify-content: center; }}
                .error-container {{ max-width: 500px; padding: 2rem; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1 class="display-1 text-danger">{code}</h1>
                <h2 class="mb-4">{title}</h2>
                <p class="lead mb-4">{message}</p>
                <a href="/" class="btn btn-primary">Ana Sayfaya Dön</a>
            </div>
        </body>
        </html>
        """

# Hata sayfaları için component
error_page_component = ErrorPageComponent()

# HTML içeriğindeki kaynak yollarını düzeltme yardımcı fonksiyonu
def fix_resource_paths(content):
    """HTML içeriğindeki kaynak yollarını düzelt"""
    # CSS ve JS kaynaklarını düzelt
    content = re.sub(r'(href|src)=(["\'])\/auth\/assets\/', r'\1=\2/static/assets/', content)
    content = re.sub(r'(src)=(["\'])\/auth\/assets\/', r'\1=\2/static/assets/', content)
    return content

# Tasarım dosyaları ve statik dosyalar için özel route'lar
@app.route('/tasarim/<path:filepath>')
def serve_tasarim(filepath):
    """Tasarım dosyalarını static olarak servis et"""
    return send_from_directory(os.path.join(ROOT_DIR, 'tasarım'), filepath)

@app.route('/static/assets/<path:filepath>')
def serve_static_assets(filepath):
    """Static assets'leri servis et"""
    return send_from_directory(os.path.join(ROOT_DIR, 'public/static/assets'), filepath)

@app.route('/favicon.ico')
def favicon():
    """Favicon.ico dosyasını servis et"""
    return send_from_directory(os.path.join(app.root_path, 'public/static/assets/images'), 
                             'favicon-32x32.png', mimetype='image/png')

# Uygulama başlangıç noktası
if __name__ == '__main__':
    # Oturum dizinini oluştur
    session_dir = os.path.join(ROOT_DIR, 'storage', 'sessions')
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
        
    # Geliştirme sunucusunu başlat
    app.run(debug=True)