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
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix
from core.Route.web_routes import router as web_router
from core.Route.ai_routes import ai_bp
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

# SocketIO'yu başlat
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   async_mode='threading',
                   logger=True,
                   engineio_logger=True)

# Middleware'leri ekle
app.before_request(SessionMiddleware.handle)
app.before_request(AuthMiddleware.handle)

# Route'ları kaydet
web_router['register_routes'](app)

# AI Blueprint'i kaydet
app.register_blueprint(ai_bp)

# Hata yönetimini aktifleştir
app.register_error_handler(Exception, error_handler.handle_error)

# Logging servisini başlat
logger = LoggerService.get_logger()

# Realtime AI Processor'ı başlat
from core.AI.ai_realtime_processor import init_realtime_processor
realtime_processor = init_realtime_processor(socketio)

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """WebSocket bağlantısı kurulduğunda"""
    user_id = session.get('user_id')
    if user_id:
        # Kullanıcıyı kendi odasına ekle
        join_room(f"user_{user_id}")
        emit('connected', {'status': 'connected', 'user_id': user_id})
        logger.info(f"WebSocket bağlantısı kuruldu: User {user_id}")

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket bağlantısı kesildiğinde"""
    user_id = session.get('user_id')
    if user_id:
        leave_room(f"user_{user_id}")
        logger.info(f"WebSocket bağlantısı kesildi: User {user_id}")

@socketio.on('join_room')
def handle_join_room(data):
    """Odaya katılma"""
    room = data.get('room')
    if room:
        join_room(room)
        emit('room_joined', {'room': room})

@socketio.on('leave_room')
def handle_leave_room(data):
    """Odadan ayrılma"""
    room = data.get('room')
    if room:
        leave_room(room)
        emit('room_left', {'room': room})

@socketio.on('ai_task')
def handle_ai_task(data):
    """AI görevi gönderme"""
    user_id = session.get('user_id')
    if user_id:
        # Görevi realtime processor'a gönder
        task_type = data.get('task_type')
        task_data = data.get('task_data', {})
        priority = data.get('priority', 5)
        
        # Asenkron görev gönderimi için thread kullan
        import threading
        def submit_task():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            task_id = loop.run_until_complete(
                realtime_processor.submit_task(
                    task_type=task_type,
                    user_id=user_id,
                    data=task_data,
                    priority=priority
                )
            )
            
            emit('task_submitted', {'task_id': task_id}, room=f"user_{user_id}")
        
        thread = threading.Thread(target=submit_task)
        thread.start()

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
        
    # WebSocket desteği ile sunucuyu başlat
    socketio.run(app, debug=True, port=5000)