#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi AI Routes
===============

AI sistemi için route tanımları
"""

import asyncio
from flask import Blueprint, request, jsonify, session
from functools import wraps

from app.Controllers.AIController import ai_controller
from core.Services.logger import LoggerService

# Blueprint oluştur
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')
logger = LoggerService.get_logger()


def async_route(f):
    """Async fonksiyonları Flask route'larında kullanmak için decorator"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(f(*args, **kwargs))
        except Exception as e:
            logger.error(f"Async route hatası: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'code': 'ASYNC_ERROR'
            }), 500
        finally:
            loop.close()
    return wrapper


@ai_bp.route('/process-image', methods=['POST'])
@async_route
async def process_image():
    """
    Tekil görsel işleme endpoint'i
    
    POST /api/ai/process-image
    {
        "image_path": "/path/to/image.jpg",
        "user_id": 1,
        "analysis_type": "comprehensive"  // comprehensive, basic
    }
    """
    try:
        data = request.get_json() or {}
        result = await ai_controller.process_image(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Process image route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/batch-process', methods=['POST'])
@async_route
async def batch_process_images():
    """
    Toplu görsel işleme endpoint'i
    
    POST /api/ai/batch-process
    {
        "image_paths": ["/path/to/image1.jpg", "/path/to/image2.jpg"],
        "user_id": 1,
        "analysis_type": "basic"
    }
    """
    try:
        data = request.get_json() or {}
        result = await ai_controller.batch_process_images(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Batch process route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/analyze-user-content', methods=['POST'])
@async_route
async def analyze_user_content():
    """
    Kullanıcı içerik analizi endpoint'i
    
    POST /api/ai/analyze-user-content
    {
        "user_id": 1
    }
    """
    try:
        data = request.get_json() or {}
        result = await ai_controller.analyze_user_content(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Analyze user content route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/organize-storage', methods=['POST'])
@async_route
async def organize_storage():
    """
    Akıllı depolama organizasyonu endpoint'i
    
    POST /api/ai/organize-storage
    {
        "user_id": 1,
        "method": "auto"  // auto, date, category, quality, hybrid
    }
    """
    try:
        data = request.get_json() or {}
        result = await ai_controller.organize_storage(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Organize storage route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/cleanup-duplicates', methods=['POST'])
@async_route
async def cleanup_duplicates():
    """
    Duplicate dosya temizleme endpoint'i
    
    POST /api/ai/cleanup-duplicates
    {
        "user_id": 1,
        "auto_remove": false
    }
    """
    try:
        data = request.get_json() or {}
        result = await ai_controller.cleanup_duplicates(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Cleanup duplicates route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/optimize-storage', methods=['POST'])
@async_route
async def optimize_storage():
    """
    Tam depolama optimizasyonu endpoint'i
    
    POST /api/ai/optimize-storage
    {
        "user_id": 1
    }
    """
    try:
        data = request.get_json() or {}
        result = await ai_controller.optimize_storage(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Optimize storage route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/recommendations', methods=['GET'])
@async_route
async def get_user_recommendations():
    """
    Kullanıcı önerileri endpoint'i
    
    GET /api/ai/recommendations?user_id=1
    """
    try:
        data = {
            'user_id': request.args.get('user_id', type=int)
        }
        result = await ai_controller.get_user_recommendations(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Get recommendations route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/system-status', methods=['GET'])
def get_ai_system_status():
    """
    AI sistem durumu endpoint'i
    
    GET /api/ai/system-status
    """
    try:
        result = ai_controller.get_ai_system_status()
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"System status route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/user-profile', methods=['GET'])
def get_user_profile_summary():
    """
    Kullanıcı profil özeti endpoint'i
    
    GET /api/ai/user-profile?user_id=1
    """
    try:
        data = {
            'user_id': request.args.get('user_id', type=int)
        }
        result = ai_controller.get_user_profile_summary(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"User profile route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/suggest-categories', methods=['GET'])
@async_route
async def suggest_categories():
    """
    Kategori önerileri endpoint'i
    
    GET /api/ai/suggest-categories?user_id=1&limit=20
    """
    try:
        data = {
            'user_id': request.args.get('user_id', type=int),
            'limit': request.args.get('limit', 20, type=int)
        }
        result = await ai_controller.suggest_categories(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Suggest categories route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/find-similar', methods=['POST'])
@async_route
async def find_similar_images():
    """
    Benzer görsel arama endpoint'i
    
    POST /api/ai/find-similar
    {
        "image_path": "/path/to/image.jpg",
        "user_id": 1,
        "similarity_threshold": 0.8
    }
    """
    try:
        data = request.get_json() or {}
        result = await ai_controller.find_similar_images(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Find similar route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/generate-thumbnail', methods=['POST'])
@async_route
async def generate_thumbnail():
    """
    Thumbnail oluşturma endpoint'i
    
    POST /api/ai/generate-thumbnail
    {
        "image_path": "/path/to/image.jpg",
        "thumbnail_path": "/path/to/thumbnail.jpg"
    }
    """
    try:
        data = request.get_json() or {}
        result = await ai_controller.generate_thumbnail(data)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Generate thumbnail route hatası: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


# Blueprint'i export et
def register_ai_routes(app):
    """AI route'larını uygulamaya kaydet"""
    app.register_blueprint(ai_bp)
    logger.info("AI routes kaydedildi")