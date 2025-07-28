#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced AI Controller
======================

Gelişmiş AI sistemi controller'ı
- Rol tabanlı AI hizmetleri
- Sosyal medya şablon üretimi
- AI ile ürün düzenleme (Admin özel)
- Kişiselleştirilmiş içerik analizi
- Gelişmiş AI yönetimi
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import request, jsonify, session, current_app, send_file, abort

from app.Controllers.BaseController import BaseController
from core.Services.logger import LoggerService
from core.AI.advanced_ai_core import advanced_ai_core
from core.Services.validators import Validator


class AdvancedAIController(BaseController):
    """
    Gelişmiş AI sistemi controller'ı
    """
    
    def __init__(self):
        super().__init__()
        self.logger = LoggerService.get_logger()
        self.validator = Validator()
        self.advanced_ai = advanced_ai_core
        
        self.logger.info("Advanced AI Controller başlatıldı")
    
    async def generate_social_template(self):
        """
        Sosyal medya şablonu oluştur
        
        POST /api/ai/generate-template
        
        Body:
        {
            "template_type": "instagram_post|telegram_post|facebook_post|...",
            "content_data": {
                "product_name": "Ürün Adı",
                "product_image": "/path/to/image.jpg",
                "text": "Özel metin",
                "generate_text": true,
                "background_style": "gradient|solid|texture",
                "gradient_colors": ["#FF6B6B", "#4ECDC4"],
                "background_color": "#FFFFFF",
                "texture_type": "paper|dots|lines",
                "font_size": 48,
                "text_color": "#000000",
                "text_y": 100,
                "product_max_size": [400, 400],
                "product_x": 340,
                "product_y": 400,
                "category": "elektronik",
                "target_audience": "genç yetişkinler"
            }
        }
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Request verilerini al
            data = request.get_json()
            if not data:
                return self.error_response('Geçersiz JSON verisi', 400)
            
            # Validasyon
            validation_rules = {
                'template_type': 'required|in:instagram_post,instagram_story,facebook_post,twitter_post,linkedin_post,telegram_post,whatsapp_status',
                'content_data': 'required|dict'
            }
            
            validation_result = self.validator.validate(data, validation_rules)
            if not validation_result['is_valid']:
                return self.error_response('Validasyon hatası', 400, validation_result['errors'])
            
            # Kullanıcı rolünü al
            user_role = user.get('role', 'user')
            
            # AI ile şablon oluştur
            result = await self.advanced_ai.generate_social_media_template(
                user_id=user['id'],
                user_role=user_role,
                template_type=data['template_type'],
                content_data=data['content_data']
            )
            
            if result.get('success'):
                self.logger.info(f"Sosyal medya şablonu oluşturuldu: {data['template_type']} (Kullanıcı: {user['id']})")
                return self.success_response(
                    'Şablon başarıyla oluşturuldu',
                    {
                        'template_info': result['template_info'],
                        'download_url': result.get('download_url'),
                        'preview_url': result.get('preview_url')
                    }
                )
            else:
                return self.error_response(
                    result.get('error', 'Şablon oluşturulamadı'),
                    400,
                    {'code': result.get('code')}
                )
        
        except Exception as e:
            self.logger.error(f"Şablon oluşturma hatası: {e}")
            return self.error_response('Şablon oluşturulurken hata oluştu', 500)
    
    async def edit_product_with_ai(self):
        """
        AI ile ürün düzenleme (Sadece Admin)
        
        POST /api/ai/edit-product
        
        Body:
        {
            "product_id": 123,
            "edit_instructions": {
                "image_editing": {
                    "enhance_quality": true,
                    "remove_background": false,
                    "resize": true,
                    "target_size": [800, 800],
                    "apply_filter": true,
                    "filter_type": "professional",
                    "add_watermark": true,
                    "watermark_text": "PofuAi"
                },
                "description_enhancement": {
                    "optimize_length": true,
                    "target_length": 200,
                    "add_seo_keywords": true,
                    "keywords": ["kaliteli", "uygun fiyat"],
                    "sales_focused": true,
                    "add_technical_details": true,
                    "technical_info": {
                        "dimensions": "20x15x10 cm",
                        "weight": "500g",
                        "material": "Plastik",
                        "color_options": ["Kırmızı", "Mavi", "Yeşil"]
                    }
                },
                "seo_optimization": {
                    "keywords": ["elektronik", "teknoloji"]
                },
                "price_analysis": {
                    "market_analysis": true,
                    "psychological_pricing": true
                }
            }
        }
        """
        try:
            # Admin kontrolü
            user = self.require_role('admin')
            if not user:
                return self.error_response('Bu işlem sadece admin kullanıcılar için kullanılabilir', 403)
            
            # Request verilerini al
            data = request.get_json()
            if not data:
                return self.error_response('Geçersiz JSON verisi', 400)
            
            # Validasyon
            validation_rules = {
                'product_id': 'required|integer',
                'edit_instructions': 'required|dict'
            }
            
            validation_result = self.validator.validate(data, validation_rules)
            if not validation_result['is_valid']:
                return self.error_response('Validasyon hatası', 400, validation_result['errors'])
            
            # AI ile ürün düzenle
            result = await self.advanced_ai.ai_edit_product(
                user_id=user['id'],
                user_role=user['role'],
                product_id=data['product_id'],
                edit_instructions=data['edit_instructions']
            )
            
            if result.get('success'):
                self.logger.info(f"Ürün AI düzenlemesi tamamlandı: {data['product_id']} (Admin: {user['id']})")
                return self.success_response(
                    'Ürün başarıyla düzenlendi',
                    {
                        'edit_info': result['edit_info'],
                        'changes_summary': result.get('changes_summary')
                    }
                )
            else:
                return self.error_response(
                    result.get('error', 'Ürün düzenlenemedi'),
                    400,
                    {'code': result.get('code')}
                )
        
        except Exception as e:
            self.logger.error(f"Ürün düzenleme hatası: {e}")
            return self.error_response('Ürün düzenlenirken hata oluştu', 500)
    
    async def analyze_user_content(self):
        """
        Kişiselleştirilmiş içerik analizi
        
        POST /api/ai/analyze-content
        
        Body:
        {
            "analysis_type": "comprehensive|basic",
            "target_user_id": 123  // Opsiyonel, admin kullanıcılar için
        }
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Request verilerini al
            data = request.get_json() or {}
            
            # Analiz edilecek kullanıcıyı belirle
            target_user_id = data.get('target_user_id')
            if target_user_id and user['role'] != 'admin':
                return self.error_response('Başka kullanıcıları analiz etme yetkiniz yok', 403)
            
            analysis_user_id = target_user_id or user['id']
            analysis_type = data.get('analysis_type', 'comprehensive')
            
            # AI ile içerik analizi
            result = await self.advanced_ai.personalized_content_analysis(
                user_id=analysis_user_id,
                user_role=user['role'],
                analysis_type=analysis_type
            )
            
            if result.get('success'):
                self.logger.info(f"İçerik analizi tamamlandı: Kullanıcı {analysis_user_id} (Analiz eden: {user['id']})")
                return self.success_response(
                    'İçerik analizi tamamlandı',
                    {
                        'analysis': result['analysis'],
                        'user_role': result['user_role'],
                        'analysis_date': result['analysis_date']
                    }
                )
            else:
                return self.error_response(
                    result.get('error', 'Analiz yapılamadı'),
                    400,
                    {'code': result.get('code')}
                )
        
        except Exception as e:
            self.logger.error(f"İçerik analizi hatası: {e}")
            return self.error_response('İçerik analizi yapılırken hata oluştu', 500)
    
    def get_advanced_metrics(self):
        """
        Gelişmiş AI sistem metriklerini al
        
        GET /api/ai/advanced-metrics
        """
        try:
            # Admin kontrolü
            user = self.require_role('admin')
            if not user:
                return self.error_response('Bu bilgilere sadece admin kullanıcılar erişebilir', 403)
            
            # Gelişmiş metrikleri al
            metrics = self.advanced_ai.get_advanced_metrics()
            
            return self.success_response(
                'Gelişmiş metrikler alındı',
                {
                    'metrics': metrics,
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Metrik alma hatası: {e}")
            return self.error_response('Metrikler alınırken hata oluştu', 500)
    
    def get_template_types(self):
        """
        Kullanılabilir şablon türlerini al
        
        GET /api/ai/template-types
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Şablon türlerini al
            template_configs = self.advanced_ai.template_configs
            
            # Kullanıcı rolüne göre izinleri kontrol et
            available_templates = {}
            for template_type, config in template_configs.items():
                # Temel şablon oluşturma izni kontrolü
                if self.advanced_ai.check_permission(user['role'], 'basic_template_generation'):
                    available_templates[template_type] = {
                        'dimensions': config,
                        'description': self._get_template_description(template_type)
                    }
            
            return self.success_response(
                'Şablon türleri alındı',
                {
                    'available_templates': available_templates,
                    'user_role': user['role'],
                    'permissions': self.advanced_ai.role_permissions.get(user['role'], [])
                }
            )
        
        except Exception as e:
            self.logger.error(f"Şablon türleri alma hatası: {e}")
            return self.error_response('Şablon türleri alınırken hata oluştu', 500)
    
    def download_template(self, filename):
        """
        Şablon dosyasını indir
        
        GET /api/ai/templates/download/<filename>
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Dosya yolu
            template_path = os.path.join('storage/templates', filename)
            
            # Dosya varlığını kontrol et
            if not os.path.exists(template_path):
                return self.error_response('Dosya bulunamadı', 404)
            
            # Güvenlik kontrolü - sadece kendi şablonlarını indirebilir (admin hariç)
            if user['role'] != 'admin':
                # TODO: Şablon sahipliği kontrolü eklenebilir
                pass
            
            return send_file(
                template_path,
                as_attachment=True,
                download_name=filename,
                mimetype='image/png'
            )
        
        except Exception as e:
            self.logger.error(f"Şablon indirme hatası: {e}")
            return self.error_response('Dosya indirilemedi', 500)
    
    def preview_template(self, filename):
        """
        Şablon önizlemesi
        
        GET /api/ai/templates/preview/<filename>
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Dosya yolu
            template_path = os.path.join('storage/templates', filename)
            
            # Dosya varlığını kontrol et
            if not os.path.exists(template_path):
                return self.error_response('Dosya bulunamadı', 404)
            
            return send_file(
                template_path,
                mimetype='image/png'
            )
        
        except Exception as e:
            self.logger.error(f"Şablon önizleme hatası: {e}")
            return self.error_response('Önizleme gösterilemedi', 500)
    
    async def batch_generate_templates(self):
        """
        Toplu şablon oluşturma
        
        POST /api/ai/batch-generate-templates
        
        Body:
        {
            "templates": [
                {
                    "template_type": "instagram_post",
                    "content_data": {...}
                },
                {
                    "template_type": "telegram_post",
                    "content_data": {...}
                }
            ]
        }
        """
        try:
            # Moderator+ kontrolü
            user = self.require_auth()
            if not user or not self.advanced_ai.check_permission(user['role'], 'batch_processing'):
                return self.error_response('Bu işlem için yetkiniz bulunmamaktadır', 403)
            
            # Request verilerini al
            data = request.get_json()
            if not data or 'templates' not in data:
                return self.error_response('Şablon listesi gerekli', 400)
            
            templates = data['templates']
            if len(templates) > 10:  # Maksimum 10 şablon
                return self.error_response('Maksimum 10 şablon oluşturabilirsiniz', 400)
            
            # Toplu işleme
            results = []
            for template_config in templates:
                try:
                    result = await self.advanced_ai.generate_social_media_template(
                        user_id=user['id'],
                        user_role=user['role'],
                        template_type=template_config['template_type'],
                        content_data=template_config['content_data']
                    )
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'error': str(e),
                        'template_type': template_config.get('template_type', 'unknown')
                    })
            
            # Başarı istatistikleri
            successful = sum(1 for result in results if result.get('success'))
            failed = len(results) - successful
            
            self.logger.info(f"Toplu şablon oluşturma tamamlandı: {successful} başarılı, {failed} başarısız (Kullanıcı: {user['id']})")
            
            return self.success_response(
                'Toplu şablon oluşturma tamamlandı',
                {
                    'results': results,
                    'statistics': {
                        'total': len(results),
                        'successful': successful,
                        'failed': failed,
                        'success_rate': (successful / len(results)) * 100 if results else 0
                    }
                }
            )
        
        except Exception as e:
            self.logger.error(f"Toplu şablon oluşturma hatası: {e}")
            return self.error_response('Toplu işlem yapılırken hata oluştu', 500)
    
    async def get_user_ai_history(self):
        """
        Kullanıcının AI geçmişini al
        
        GET /api/ai/user-history?limit=50&offset=0&type=all
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            # Query parametreleri
            limit = min(int(request.args.get('limit', 50)), 100)  # Maksimum 100
            offset = int(request.args.get('offset', 0))
            history_type = request.args.get('type', 'all')  # all, processing, templates
            
            # Veritabanından geçmişi al
            history_data = await self._get_user_ai_history_from_db(
                user['id'], limit, offset, history_type
            )
            
            return self.success_response(
                'AI geçmişi alındı',
                {
                    'history': history_data['items'],
                    'pagination': {
                        'limit': limit,
                        'offset': offset,
                        'total': history_data['total'],
                        'has_more': offset + limit < history_data['total']
                    }
                }
            )
        
        except Exception as e:
            self.logger.error(f"AI geçmişi alma hatası: {e}")
            return self.error_response('Geçmiş alınırken hata oluştu', 500)
    
    def get_ai_permissions(self):
        """
        Kullanıcının AI izinlerini al
        
        GET /api/ai/permissions
        """
        try:
            # Giriş kontrolü
            user = self.require_auth()
            if not user:
                return self.error_response('Giriş yapmanız gerekiyor', 401)
            
            user_role = user['role']
            permissions = self.advanced_ai.role_permissions.get(user_role, [])
            
            # İzin detayları
            permission_details = {
                'basic_template_generation': 'Temel şablon oluşturma',
                'template_generation': 'Gelişmiş şablon oluşturma',
                'content_analysis': 'İçerik analizi',
                'batch_processing': 'Toplu işleme',
                'user_content_management': 'Kullanıcı içerik yönetimi',
                'product_editing': 'Ürün düzenleme (Admin özel)',
                'personal_content_analysis': 'Kişisel içerik analizi'
            }
            
            available_permissions = []
            for permission in permissions:
                if permission == '*':
                    available_permissions = list(permission_details.keys())
                    break
                elif permission in permission_details:
                    available_permissions.append(permission)
            
            return self.success_response(
                'AI izinleri alındı',
                {
                    'user_role': user_role,
                    'permissions': available_permissions,
                    'permission_details': {
                        perm: permission_details[perm] 
                        for perm in available_permissions 
                        if perm in permission_details
                    },
                    'is_admin': user_role == 'admin'
                }
            )
        
        except Exception as e:
            self.logger.error(f"İzin alma hatası: {e}")
            return self.error_response('İzinler alınırken hata oluştu', 500)
    
    # Yardımcı metodlar
    def _get_template_description(self, template_type: str) -> str:
        """Şablon türü açıklaması"""
        descriptions = {
            'instagram_post': 'Instagram gönderi şablonu (1080x1080)',
            'instagram_story': 'Instagram hikaye şablonu (1080x1920)',
            'facebook_post': 'Facebook gönderi şablonu (1200x630)',
            'twitter_post': 'Twitter gönderi şablonu (1200x675)',
            'linkedin_post': 'LinkedIn gönderi şablonu (1200x627)',
            'telegram_post': 'Telegram gönderi şablonu (1280x720)',
            'whatsapp_status': 'WhatsApp durum şablonu (1080x1920)'
        }
        return descriptions.get(template_type, f'{template_type} şablonu')
    
    async def _get_user_ai_history_from_db(self, user_id: int, limit: int, offset: int, history_type: str) -> Dict:
        """Veritabanından kullanıcı AI geçmişini al"""
        try:
            items = []
            total = 0
            
            if history_type in ['all', 'processing']:
                # AI işleme geçmişi
                processing_query = """
                SELECT 'processing' as type, id, image_path, status, processing_time, created_at
                FROM ai_processing_results 
                WHERE user_id = %s 
                ORDER BY created_at DESC
                """
                if history_type == 'processing':
                    processing_query += f" LIMIT {limit} OFFSET {offset}"
                
                processing_results = await self.db.fetch_all(processing_query, (user_id,))
                for row in processing_results:
                    items.append(dict(row))
            
            if history_type in ['all', 'templates']:
                # Şablon geçmişi
                template_query = """
                SELECT 'template' as type, id, template_type, template_path, processing_time, created_at
                FROM ai_template_results 
                WHERE user_id = %s 
                ORDER BY created_at DESC
                """
                if history_type == 'templates':
                    template_query += f" LIMIT {limit} OFFSET {offset}"
                
                template_results = await self.db.fetch_all(template_query, (user_id,))
                for row in template_results:
                    items.append(dict(row))
            
            # Toplam sayı
            if history_type == 'all':
                count_query = """
                SELECT 
                    (SELECT COUNT(*) FROM ai_processing_results WHERE user_id = %s) +
                    (SELECT COUNT(*) FROM ai_template_results WHERE user_id = %s) as total
                """
                count_result = await self.db.fetch_one(count_query, (user_id, user_id))
                total = count_result['total'] if count_result else 0
                
                # Sıralama ve sayfalama
                items.sort(key=lambda x: x['created_at'], reverse=True)
                items = items[offset:offset + limit]
            
            elif history_type == 'processing':
                count_query = "SELECT COUNT(*) as total FROM ai_processing_results WHERE user_id = %s"
                count_result = await self.db.fetch_one(count_query, (user_id,))
                total = count_result['total'] if count_result else 0
            
            elif history_type == 'templates':
                count_query = "SELECT COUNT(*) as total FROM ai_template_results WHERE user_id = %s"
                count_result = await self.db.fetch_one(count_query, (user_id,))
                total = count_result['total'] if count_result else 0
            
            return {
                'items': items,
                'total': total
            }
            
        except Exception as e:
            self.logger.error(f"AI geçmişi veritabanı hatası: {e}")
            return {'items': [], 'total': 0}