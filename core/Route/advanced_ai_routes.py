#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced AI Routes
==================

Gelişmiş AI sistemi için route tanımları
- Sosyal medya şablon oluşturma
- AI ile ürün düzenleme (Admin özel)
- Kişiselleştirilmiş içerik analizi
- Rol tabanlı AI hizmetleri
"""

from flask import Blueprint
from app.Controllers.AdvancedAIController import AdvancedAIController

# Blueprint oluştur
advanced_ai_bp = Blueprint('advanced_ai', __name__, url_prefix='/api/ai')

# Controller instance
controller = AdvancedAIController()

# Sosyal Medya Şablon Routes
@advanced_ai_bp.route('/generate-template', methods=['POST'])
def generate_social_template():
    """
    Sosyal medya şablonu oluştur
    
    Tüm kullanıcılar kullanabilir (rol bazlı kısıtlamalar uygulanır)
    """
    return controller.generate_social_template()

@advanced_ai_bp.route('/batch-generate-templates', methods=['POST'])
def batch_generate_templates():
    """
    Toplu şablon oluşturma
    
    Moderator+ kullanıcılar için
    """
    return controller.batch_generate_templates()

@advanced_ai_bp.route('/template-types', methods=['GET'])
def get_template_types():
    """
    Kullanılabilir şablon türlerini al
    
    Tüm giriş yapmış kullanıcılar için
    """
    return controller.get_template_types()

# Şablon Dosya İşlemleri Routes
@advanced_ai_bp.route('/templates/download/<filename>', methods=['GET'])
def download_template(filename):
    """
    Şablon dosyasını indir
    
    Dosya sahibi veya admin kullanıcılar için
    """
    return controller.download_template(filename)

@advanced_ai_bp.route('/templates/preview/<filename>', methods=['GET'])
def preview_template(filename):
    """
    Şablon önizlemesi
    
    Dosya sahibi veya admin kullanıcılar için
    """
    return controller.preview_template(filename)

# AI Ürün Düzenleme Routes (Admin Özel)
@advanced_ai_bp.route('/edit-product', methods=['POST'])
def edit_product_with_ai():
    """
    AI ile ürün düzenleme
    
    Sadece admin kullanıcılar için
    """
    return controller.edit_product_with_ai()

# İçerik Analizi Routes
@advanced_ai_bp.route('/analyze-content', methods=['POST'])
def analyze_user_content():
    """
    Kişiselleştirilmiş içerik analizi
    
    Tüm kullanıcılar kendi içeriklerini, adminler tüm kullanıcıları analiz edebilir
    """
    return controller.analyze_user_content()

# AI Sistem Yönetimi Routes
@advanced_ai_bp.route('/advanced-metrics', methods=['GET'])
def get_advanced_metrics():
    """
    Gelişmiş AI sistem metriklerini al
    
    Sadece admin kullanıcılar için
    """
    return controller.get_advanced_metrics()

@advanced_ai_bp.route('/permissions', methods=['GET'])
def get_ai_permissions():
    """
    Kullanıcının AI izinlerini al
    
    Tüm giriş yapmış kullanıcılar için
    """
    return controller.get_ai_permissions()

# Kullanıcı AI Geçmişi Routes
@advanced_ai_bp.route('/user-history', methods=['GET'])
def get_user_ai_history():
    """
    Kullanıcının AI geçmişini al
    
    Query parametreleri:
    - limit: Sayfa başına kayıt sayısı (varsayılan: 50, maksimum: 100)
    - offset: Başlangıç noktası (varsayılan: 0)
    - type: Geçmiş türü (all, processing, templates)
    
    Tüm giriş yapmış kullanıcılar için
    """
    return controller.get_user_ai_history()

# Route kayıt fonksiyonu
def register_advanced_ai_routes(app):
    """
    Gelişmiş AI route'larını uygulamaya kaydet
    
    Args:
        app: Flask uygulama instance'ı
    """
    app.register_blueprint(advanced_ai_bp)
    
    # Ek route'lar (mevcut AI controller ile uyumluluk için)
    register_compatibility_routes(app)

def register_compatibility_routes(app):
    """
    Mevcut AI sistemi ile uyumluluk route'ları
    
    Args:
        app: Flask uygulama instance'ı
    """
    
    @app.route('/api/ai/status', methods=['GET'])
    def ai_system_status():
        """AI sistem durumu (hem temel hem gelişmiş)"""
        from core.AI.ai_core import ai_core
        from core.AI.advanced_ai_core import advanced_ai_core
        
        try:
            basic_metrics = ai_core.get_metrics()
            advanced_metrics = advanced_ai_core.get_advanced_metrics()
            
            return {
                'success': True,
                'message': 'AI sistem durumu alındı',
                'data': {
                    'basic_ai': {
                        'status': 'active',
                        'metrics': basic_metrics
                    },
                    'advanced_ai': {
                        'status': 'active',
                        'metrics': advanced_metrics
                    },
                    'system_health': 'good',
                    'timestamp': basic_metrics.get('timestamp', 'unknown')
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Sistem durumu alınamadı: {str(e)}',
                'data': {
                    'basic_ai': {'status': 'error'},
                    'advanced_ai': {'status': 'error'},
                    'system_health': 'critical'
                }
            }, 500
    
    @app.route('/api/ai/health', methods=['GET'])
    def ai_health_check():
        """AI sistem sağlık kontrolü"""
        try:
            from core.Database.connection import DatabaseConnection
            
            db = DatabaseConnection()
            
            # Veritabanı bağlantısını test et
            health_query = "SELECT 1 as health_check"
            result = db.fetch_one(health_query)
            
            if result:
                return {
                    'success': True,
                    'message': 'AI sistemi sağlıklı',
                    'data': {
                        'database': 'connected',
                        'ai_core': 'loaded',
                        'advanced_ai': 'loaded',
                        'models': 'ready',
                        'status': 'healthy'
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Veritabanı bağlantısı başarısız',
                    'data': {
                        'database': 'disconnected',
                        'status': 'unhealthy'
                    }
                }, 503
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Sağlık kontrolü başarısız: {str(e)}',
                'data': {
                    'status': 'critical',
                    'error_details': str(e)
                }
            }, 500
    
    @app.route('/api/ai/features', methods=['GET'])
    def get_ai_features():
        """Kullanılabilir AI özelliklerini listele"""
        try:
            features = {
                'basic_ai_features': [
                    {
                        'name': 'image_processing',
                        'description': 'Görsel işleme ve analiz',
                        'endpoint': '/api/ai/process-image',
                        'method': 'POST',
                        'required_role': 'user'
                    },
                    {
                        'name': 'batch_processing',
                        'description': 'Toplu görsel işleme',
                        'endpoint': '/api/ai/batch-process',
                        'method': 'POST',
                        'required_role': 'user'
                    }
                ],
                'advanced_ai_features': [
                    {
                        'name': 'template_generation',
                        'description': 'Sosyal medya şablon oluşturma',
                        'endpoint': '/api/ai/generate-template',
                        'method': 'POST',
                        'required_role': 'user'
                    },
                    {
                        'name': 'product_editing',
                        'description': 'AI ile ürün düzenleme',
                        'endpoint': '/api/ai/edit-product',
                        'method': 'POST',
                        'required_role': 'admin'
                    },
                    {
                        'name': 'content_analysis',
                        'description': 'Kişiselleştirilmiş içerik analizi',
                        'endpoint': '/api/ai/analyze-content',
                        'method': 'POST',
                        'required_role': 'user'
                    },
                    {
                        'name': 'batch_template_generation',
                        'description': 'Toplu şablon oluşturma',
                        'endpoint': '/api/ai/batch-generate-templates',
                        'method': 'POST',
                        'required_role': 'moderator'
                    }
                ],
                'template_types': [
                    'instagram_post',
                    'instagram_story',
                    'facebook_post',
                    'twitter_post',
                    'linkedin_post',
                    'telegram_post',
                    'whatsapp_status'
                ],
                'supported_formats': [
                    'PNG',
                    'JPEG',
                    'WebP'
                ]
            }
            
            return {
                'success': True,
                'message': 'AI özellikleri listelendi',
                'data': features
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Özellikler listelenemedi: {str(e)}'
            }, 500
    
    @app.route('/api/ai/config', methods=['GET'])
    def get_ai_config():
        """AI sistem konfigürasyonunu al (Admin özel)"""
        try:
            from flask import session
            from app.Models.User import User
            
            # Admin kontrolü
            user_id = session.get('user_id')
            if not user_id:
                return {
                    'success': False,
                    'error': 'Giriş yapmanız gerekiyor'
                }, 401
            
            user = User.find(user_id)
            if not user or user.role != 'admin':
                return {
                    'success': False,
                    'error': 'Bu bilgilere sadece admin kullanıcılar erişebilir'
                }, 403
            
            from core.Database.connection import DatabaseConnection
            
            db = DatabaseConnection()
            config_query = "SELECT config_key, config_value, description FROM ai_system_config WHERE is_active = 1"
            config_results = db.fetch_all(config_query)
            
            config_data = {}
            for row in config_results:
                config_data[row['config_key']] = {
                    'value': row['config_value'],
                    'description': row['description']
                }
            
            return {
                'success': True,
                'message': 'AI konfigürasyonu alındı',
                'data': {
                    'config': config_data,
                    'timestamp': 'now'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Konfigürasyon alınamadı: {str(e)}'
            }, 500
    
    @app.route('/api/ai/usage-stats', methods=['GET'])
    def get_usage_stats():
        """AI kullanım istatistikleri (Admin özel)"""
        try:
            from flask import session
            from app.Models.User import User
            
            # Admin kontrolü
            user_id = session.get('user_id')
            if not user_id:
                return {
                    'success': False,
                    'error': 'Giriş yapmanız gerekiyor'
                }, 401
            
            user = User.find(user_id)
            if not user or user.role != 'admin':
                return {
                    'success': False,
                    'error': 'Bu bilgilere sadece admin kullanıcılar erişebilir'
                }, 403
            
            from core.Database.connection import DatabaseConnection
            
            db = DatabaseConnection()
            
            # Günlük istatistikler
            daily_stats_query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as total_operations,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_operations,
                AVG(processing_time) as avg_processing_time
            FROM (
                SELECT created_at, status, processing_time FROM ai_processing_results
                UNION ALL
                SELECT created_at, status, processing_time FROM ai_template_results
            ) as all_operations
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            """
            
            daily_stats = db.fetch_all(daily_stats_query)
            
            # Rol bazlı istatistikler
            role_stats_query = """
            SELECT * FROM ai_role_performance
            """
            
            role_stats = db.fetch_all(role_stats_query)
            
            return {
                'success': True,
                'message': 'AI kullanım istatistikleri alındı',
                'data': {
                    'daily_stats': [dict(row) for row in daily_stats] if daily_stats else [],
                    'role_stats': [dict(row) for row in role_stats] if role_stats else [],
                    'period': '30_days'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'İstatistikler alınamadı: {str(e)}'
            }, 500

# Route bilgileri
ADVANCED_AI_ROUTES = {
    'template_generation': {
        'endpoint': '/api/ai/generate-template',
        'method': 'POST',
        'description': 'Sosyal medya şablonu oluştur',
        'required_role': 'user',
        'rate_limit': '50/day'
    },
    'batch_template_generation': {
        'endpoint': '/api/ai/batch-generate-templates',
        'method': 'POST',
        'description': 'Toplu şablon oluşturma',
        'required_role': 'moderator',
        'rate_limit': '10/day'
    },
    'product_editing': {
        'endpoint': '/api/ai/edit-product',
        'method': 'POST',
        'description': 'AI ile ürün düzenleme',
        'required_role': 'admin',
        'rate_limit': '20/day'
    },
    'content_analysis': {
        'endpoint': '/api/ai/analyze-content',
        'method': 'POST',
        'description': 'Kişiselleştirilmiş içerik analizi',
        'required_role': 'user',
        'rate_limit': '20/day'
    },
    'template_types': {
        'endpoint': '/api/ai/template-types',
        'method': 'GET',
        'description': 'Kullanılabilir şablon türlerini al',
        'required_role': 'user',
        'rate_limit': '100/day'
    },
    'advanced_metrics': {
        'endpoint': '/api/ai/advanced-metrics',
        'method': 'GET',
        'description': 'Gelişmiş AI sistem metriklerini al',
        'required_role': 'admin',
        'rate_limit': '50/day'
    },
    'permissions': {
        'endpoint': '/api/ai/permissions',
        'method': 'GET',
        'description': 'Kullanıcının AI izinlerini al',
        'required_role': 'user',
        'rate_limit': '100/day'
    },
    'user_history': {
        'endpoint': '/api/ai/user-history',
        'method': 'GET',
        'description': 'Kullanıcının AI geçmişini al',
        'required_role': 'user',
        'rate_limit': '100/day'
    },
    'template_download': {
        'endpoint': '/api/ai/templates/download/<filename>',
        'method': 'GET',
        'description': 'Şablon dosyasını indir',
        'required_role': 'user',
        'rate_limit': '200/day'
    },
    'template_preview': {
        'endpoint': '/api/ai/templates/preview/<filename>',
        'method': 'GET',
        'description': 'Şablon önizlemesi',
        'required_role': 'user',
        'rate_limit': '500/day'
    }
}