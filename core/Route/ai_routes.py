#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi AI Routes
===============

AI sistemi için route tanımlamaları
"""

from flask import Blueprint, request, jsonify
import asyncio
from functools import wraps

from app.Controllers.AIController import ai_controller
from core.Services.logger import LoggerService

# Blueprint oluştur
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')
logger = LoggerService.get_logger()


def async_route(f):
    """Async route decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return decorated_function


# Temel AI işlemleri
@ai_bp.route('/process-image', methods=['POST'])
@async_route
async def process_image():
    """Görsel işleme endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.process_image(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Process image route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/batch-process', methods=['POST'])
@async_route
async def batch_process():
    """Toplu görsel işleme endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.batch_process_images(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Batch process route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


# Kullanıcı içerik yönetimi
@ai_bp.route('/analyze-user-content', methods=['POST'])
@async_route
async def analyze_user_content():
    """Kullanıcı içerik analizi endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.analyze_user_content(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Analyze user content route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/user-recommendations', methods=['POST'])
@async_route
async def get_user_recommendations():
    """Kullanıcı önerileri endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.get_user_recommendations(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"User recommendations route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


# Depolama işlemleri
@ai_bp.route('/organize-storage', methods=['POST'])
@async_route
async def organize_storage():
    """Depolama organizasyonu endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.organize_storage(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Organize storage route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/cleanup-duplicates', methods=['POST'])
@async_route
async def cleanup_duplicates():
    """Duplicate temizleme endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.cleanup_duplicates(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Cleanup duplicates route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/optimize-storage', methods=['POST'])
@async_route
async def optimize_storage():
    """Depolama optimizasyonu endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.optimize_storage(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Optimize storage route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


# Kategorilendirme işlemleri
@ai_bp.route('/suggest-categories', methods=['POST'])
@async_route
async def suggest_categories():
    """Kategori önerileri endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.suggest_categories(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Suggest categories route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


# Benzerlik araması
@ai_bp.route('/find-similar-images', methods=['POST'])
@async_route
async def find_similar_images():
    """Benzer görsel arama endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.find_similar_images(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Find similar images route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


# Thumbnail işlemleri
@ai_bp.route('/generate-thumbnail', methods=['POST'])
@async_route
async def generate_thumbnail():
    """Thumbnail oluşturma endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.generate_thumbnail(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Generate thumbnail route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


# Gelişmiş AI özellikleri (YENİ)
@ai_bp.route('/product-editor', methods=['POST'])
@async_route
async def ai_product_editor():
    """AI destekli ürün düzenleme endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.ai_product_editor(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"AI product editor route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/generate-template', methods=['POST'])
@async_route
async def generate_social_template():
    """Sosyal medya şablonu üretme endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.generate_social_template(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Generate template route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/content-management', methods=['POST'])
@async_route
async def ai_content_management():
    """AI destekli içerik yönetimi endpoint'i"""
    try:
        data = request.get_json()
        result = await ai_controller.ai_content_management(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"AI content management route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/user-capabilities', methods=['GET', 'POST'])
@async_route
async def get_user_ai_capabilities():
    """Kullanıcı AI yetenekleri endpoint'i"""
    try:
        data = request.get_json() if request.method == 'POST' else {}
        result = await ai_controller.get_user_ai_capabilities(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"User AI capabilities route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


# Sistem durumu ve profil
@ai_bp.route('/system-status', methods=['GET'])
def get_ai_system_status():
    """AI sistem durumu endpoint'i"""
    try:
        result = ai_controller.get_ai_system_status()
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"System status route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


@ai_bp.route('/user-profile-summary', methods=['POST'])
def get_user_profile_summary():
    """Kullanıcı profil özeti endpoint'i"""
    try:
        data = request.get_json()
        result = ai_controller.get_user_profile_summary(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"User profile summary route error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ROUTE_ERROR'
        }), 500


# Health check
@ai_bp.route('/health', methods=['GET'])
def health_check():
    """AI sistemi health check endpoint'i"""
    return jsonify({
        'success': True,
        'message': 'AI system is running',
        'timestamp': datetime.now().isoformat()
    }), 200


# API dokümantasyonu
@ai_bp.route('/docs', methods=['GET'])
def api_documentation():
    """AI API dokümantasyonu"""
    docs = {
        'success': True,
        'endpoints': [
            {
                'path': '/api/ai/process-image',
                'method': 'POST',
                'description': 'Tekil görsel işleme',
                'parameters': {
                    'image_path': 'string (required)',
                    'user_id': 'integer (optional)',
                    'analysis_type': 'string (optional: comprehensive|basic)'
                }
            },
            {
                'path': '/api/ai/batch-process',
                'method': 'POST',
                'description': 'Toplu görsel işleme',
                'parameters': {
                    'image_paths': 'array (required)',
                    'user_id': 'integer (optional)',
                    'analysis_type': 'string (optional: comprehensive|basic)'
                }
            },
            {
                'path': '/api/ai/product-editor',
                'method': 'POST',
                'description': 'AI destekli ürün düzenleme (Admin only)',
                'parameters': {
                    'product_data': 'object (required)',
                    'user_id': 'integer (optional)'
                }
            },
            {
                'path': '/api/ai/generate-template',
                'method': 'POST',
                'description': 'Sosyal medya şablonu üretimi',
                'parameters': {
                    'platform': 'string (instagram|facebook|twitter|telegram)',
                    'type': 'string (product_showcase|announcement|etc)',
                    'product_info': 'object',
                    'style': 'string (modern|elegant|playful)'
                }
            },
            {
                'path': '/api/ai/content-management',
                'method': 'POST',
                'description': 'AI destekli içerik yönetimi',
                'parameters': {
                    'action': 'string (analyze|optimize|schedule)',
                    'content_data': 'object',
                    'user_id': 'integer (optional)'
                }
            },
            {
                'path': '/api/ai/user-capabilities',
                'method': 'GET|POST',
                'description': 'Kullanıcının AI yeteneklerini görüntüle',
                'parameters': {
                    'user_id': 'integer (optional)'
                }
            },
            {
                'path': '/api/ai/system-status',
                'method': 'GET',
                'description': 'AI sistem durumu'
            }
        ]
    }
    return jsonify(docs), 200


# Import datetime for health check
from datetime import datetime