#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi AI Controller
===================

AI sistemi için ana controller
- Görsel analizi ve kategorilendirme
- Kullanıcı bazlı içerik yönetimi
- Akıllı depolama işlemleri
- AI sistem yönetimi
- Gelişmiş AI özellikleri (ürün düzenleme, şablon üretimi)
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import request, jsonify, session, current_app

from core.Services.logger import LoggerService
from core.AI.ai_core import ai_core
from core.AI.image_recognition import ImageRecognitionService
from core.AI.content_categorizer import ContentCategorizerService
from core.AI.user_content_manager import UserContentManagerService
from core.AI.smart_storage import SmartStorageService
from core.AI.ai_advanced_features import advanced_ai_features


class AIController:
    """
    AI sistemi ana controller'ı
    """
    
    def __init__(self):
        self.logger = LoggerService.get_logger()
        
        # AI servislerini başlat
        self.image_recognition = ImageRecognitionService()
        self.content_categorizer = ContentCategorizerService()
        self.user_content_manager = UserContentManagerService()
        self.smart_storage = SmartStorageService()
        self.advanced_features = advanced_ai_features
        
        self.logger.info("AI Controller başlatıldı")
    
    def _get_user_role(self) -> str:
        """Kullanıcı rolünü al"""
        # Session'dan kullanıcı bilgisini al
        user = session.get('user', {})
        return user.get('role', 'guest')
    
    async def process_image(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Görsel işleme endpoint'i
        
        Args:
            request_data: İstek verileri
            
        Returns:
            İşleme sonuçları
        """
        try:
            # Parametreleri al
            image_path = request_data.get('image_path')
            user_id = request_data.get('user_id', session.get('user_id', 1))
            analysis_type = request_data.get('analysis_type', 'comprehensive')
            
            if not image_path:
                return {
                    'success': False,
                    'error': 'image_path parametresi gerekli',
                    'code': 'MISSING_PARAMETER'
                }
            
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': 'Belirtilen dosya bulunamadı',
                    'code': 'FILE_NOT_FOUND'
                }
            
            # Analiz türüne göre işlem yap
            if analysis_type == 'comprehensive':
                # Kapsamlı analiz
                analysis_result = await self.image_recognition.analyze_image_comprehensive(
                    image_path, user_id
                )
                
                # Kategorilendirme
                if analysis_result.get('status') != 'error':
                    categorization_result = await self.content_categorizer.categorize_content(
                        analysis_result
                    )
                    analysis_result['categorization'] = categorization_result
            
            elif analysis_type == 'basic':
                # Temel AI Core analizi
                analysis_result = await ai_core.process_image(image_path, user_id)
            
            else:
                return {
                    'success': False,
                    'error': 'Geçersiz analiz türü',
                    'code': 'INVALID_ANALYSIS_TYPE'
                }
            
            # Başarılı sonuç
            return {
                'success': True,
                'data': analysis_result,
                'processing_info': {
                    'analysis_type': analysis_type,
                    'timestamp': datetime.now().isoformat(),
                    'user_id': user_id
                }
            }
            
        except Exception as e:
            self.logger.error(f"Görsel işleme hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'PROCESSING_ERROR'
            }
    
    async def batch_process_images(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Toplu görsel işleme
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Toplu işleme sonuçları
        """
        try:
            image_paths = request_data.get('image_paths', [])
            user_id = request_data.get('user_id', session.get('user_id', 1))
            analysis_type = request_data.get('analysis_type', 'basic')
            
            if not image_paths:
                return {
                    'success': False,
                    'error': 'image_paths parametresi gerekli',
                    'code': 'MISSING_PARAMETER'
                }
            
            # Mevcut dosyaları filtrele
            valid_paths = [path for path in image_paths if os.path.exists(path)]
            
            if not valid_paths:
                return {
                    'success': False,
                    'error': 'Geçerli dosya bulunamadı',
                    'code': 'NO_VALID_FILES'
                }
            
            # Toplu işleme
            if analysis_type == 'basic':
                results = await ai_core.batch_process_images(valid_paths, user_id)
            else:
                # Comprehensive analiz için sıralı işleme
                results = []
                for image_path in valid_paths:
                    try:
                        result = await self.image_recognition.analyze_image_comprehensive(
                            image_path, user_id
                        )
                        results.append(result)
                    except Exception as e:
                        results.append({
                            'image_path': image_path,
                            'error': str(e),
                            'status': 'error'
                        })
            
            # İstatistikleri hesapla
            successful = sum(1 for r in results if r.get('status') != 'error')
            failed = len(results) - successful
            
            return {
                'success': True,
                'data': {
                    'results': results,
                    'statistics': {
                        'total_processed': len(results),
                        'successful': successful,
                        'failed': failed,
                        'success_rate': successful / len(results) if results else 0
                    }
                },
                'processing_info': {
                    'analysis_type': analysis_type,
                    'timestamp': datetime.now().isoformat(),
                    'user_id': user_id
                }
            }
            
        except Exception as e:
            self.logger.error(f"Toplu görsel işleme hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'BATCH_PROCESSING_ERROR'
            }
    
    async def analyze_user_content(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kullanıcı içerik analizi
        
        Args:
            request_data: İstek verileri
            
        Returns:
            İçerik analizi sonuçları
        """
        try:
            user_id = request_data.get('user_id', session.get('user_id', 1))
            
            # Kullanıcı içerik analizi
            analysis_result = await self.user_content_manager.analyze_user_content(user_id)
            
            return {
                'success': True,
                'data': analysis_result
            }
            
        except Exception as e:
            self.logger.error(f"Kullanıcı içerik analizi hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'USER_CONTENT_ANALYSIS_ERROR'
            }
    
    async def organize_storage(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Akıllı depolama organizasyonu
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Organizasyon sonuçları
        """
        try:
            user_id = request_data.get('user_id', session.get('user_id', 1))
            organization_method = request_data.get('method', 'auto')
            
            # Depolama organizasyonu
            organization_result = await self.smart_storage.organize_user_content(
                user_id, organization_method
            )
            
            return {
                'success': True,
                'data': organization_result
            }
            
        except Exception as e:
            self.logger.error(f"Depolama organizasyonu hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'STORAGE_ORGANIZATION_ERROR'
            }
    
    async def cleanup_duplicates(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Duplicate dosyaları temizle
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Temizleme sonuçları
        """
        try:
            user_id = request_data.get('user_id', session.get('user_id', 1))
            auto_remove = request_data.get('auto_remove', False)
            
            # Duplicate temizleme
            cleanup_result = await self.smart_storage.cleanup_duplicates(
                user_id, auto_remove
            )
            
            return {
                'success': True,
                'data': cleanup_result
            }
            
        except Exception as e:
            self.logger.error(f"Duplicate temizleme hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'DUPLICATE_CLEANUP_ERROR'
            }
    
    async def optimize_storage(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tam depolama optimizasyonu
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Optimizasyon sonuçları
        """
        try:
            user_id = request_data.get('user_id', session.get('user_id', 1))
            
            # Tam optimizasyon
            optimization_result = await self.smart_storage.optimize_storage(user_id)
            
            return {
                'success': True,
                'data': optimization_result
            }
            
        except Exception as e:
            self.logger.error(f"Depolama optimizasyonu hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'STORAGE_OPTIMIZATION_ERROR'
            }
    
    async def get_user_recommendations(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kullanıcı önerileri al
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Öneriler
        """
        try:
            user_id = request_data.get('user_id', session.get('user_id', 1))
            
            # Kullanıcı önerileri
            recommendations = await self.user_content_manager.get_user_recommendations(user_id)
            
            return {
                'success': True,
                'data': recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Kullanıcı önerileri alma hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'USER_RECOMMENDATIONS_ERROR'
            }
    
    async def ai_product_editor(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI destekli ürün düzenleme endpoint'i
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Düzenleme sonuçları
        """
        try:
            user_id = request_data.get('user_id', session.get('user_id', 1))
            user_role = self._get_user_role()
            
            # Admin kontrolü
            if user_role != 'admin':
                return {
                    'success': False,
                    'error': 'Bu özellik sadece admin kullanıcılar için aktif',
                    'code': 'ADMIN_ONLY'
                }
            
            # Gelişmiş AI özelliklerini kullan
            result = await self.advanced_features.ai_product_editor(
                user_id=user_id,
                user_role=user_role,
                product_data=request_data.get('product_data', {})
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"AI ürün düzenleme hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'AI_PRODUCT_EDIT_ERROR'
            }
    
    async def generate_social_template(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sosyal medya şablonu üretme endpoint'i
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Şablon verileri
        """
        try:
            user_id = request_data.get('user_id', session.get('user_id', 1))
            user_role = self._get_user_role()
            
            # Gelişmiş AI özelliklerini kullan
            result = await self.advanced_features.generate_social_media_template(
                user_id=user_id,
                user_role=user_role,
                template_request=request_data
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Şablon üretimi hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'TEMPLATE_GENERATION_ERROR'
            }
    
    async def ai_content_management(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI destekli içerik yönetimi endpoint'i
        
        Args:
            request_data: İstek verileri
            
        Returns:
            İçerik yönetimi sonuçları
        """
        try:
            user_id = request_data.get('user_id', session.get('user_id', 1))
            user_role = self._get_user_role()
            action = request_data.get('action', 'analyze')
            content_data = request_data.get('content_data', {})
            
            # Gelişmiş AI özelliklerini kullan
            result = await self.advanced_features.ai_content_manager(
                user_id=user_id,
                user_role=user_role,
                action=action,
                content_data=content_data
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"AI içerik yönetimi hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'AI_CONTENT_MANAGEMENT_ERROR'
            }
    
    async def get_user_ai_capabilities(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kullanıcının AI yeteneklerini al
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Kullanıcı AI yetenekleri
        """
        try:
            user_id = request_data.get('user_id', session.get('user_id', 1))
            user_role = self._get_user_role()
            
            # Kullanıcı AI servis seviyesini al
            service_config = await self.advanced_features.get_user_ai_service_level(
                user_id, user_role
            )
            
            # Kullanıcı AI istatistikleri
            user_stats = await self._get_user_ai_stats(user_id)
            
            return {
                'success': True,
                'data': {
                    'role': user_role,
                    'service_level': service_config.service_level.value,
                    'features': service_config.features,
                    'limits': service_config.limits,
                    'permissions': service_config.permissions,
                    'usage_stats': user_stats,
                    'available_actions': self._get_available_actions(service_config.permissions)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Kullanıcı AI yetenekleri alma hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'USER_AI_CAPABILITIES_ERROR'
            }
    
    async def _get_user_ai_stats(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı AI kullanım istatistikleri"""
        try:
            from core.Database.connection import DatabaseConnection
            db = DatabaseConnection()
            
            with db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # Bugünkü kullanım
                cursor.execute("""
                    SELECT COUNT(*) as daily_usage
                    FROM user_ai_interactions
                    WHERE user_id = %s AND DATE(created_at) = CURDATE()
                """, (user_id,))
                daily_usage = cursor.fetchone()['daily_usage']
                
                # Toplam kullanım
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_interactions,
                        COUNT(DISTINCT interaction_type) as unique_features_used
                    FROM user_ai_interactions
                    WHERE user_id = %s
                """, (user_id,))
                total_stats = cursor.fetchone()
                
                return {
                    'daily_usage': daily_usage,
                    'total_interactions': total_stats['total_interactions'],
                    'unique_features_used': total_stats['unique_features_used']
                }
                
        except Exception as e:
            self.logger.error(f"Kullanıcı AI istatistikleri alma hatası: {e}")
            return {
                'daily_usage': 0,
                'total_interactions': 0,
                'unique_features_used': 0
            }
    
    def _get_available_actions(self, permissions: List[str]) -> List[Dict[str, str]]:
        """İzinlere göre kullanılabilir aksiyonlar"""
        action_map = {
            'product_edit': {
                'name': 'AI Ürün Düzenleme',
                'endpoint': '/api/ai/product-editor',
                'description': 'Ürünlerinizi AI ile düzenleyin ve zenginleştirin'
            },
            'template_generation': {
                'name': 'Şablon Üretimi',
                'endpoint': '/api/ai/generate-template',
                'description': 'Sosyal medya için AI destekli şablon oluşturun'
            },
            'bulk_operations': {
                'name': 'Toplu İşlemler',
                'endpoint': '/api/ai/batch-process',
                'description': 'Birden fazla görseli aynı anda işleyin'
            },
            'ai_training': {
                'name': 'AI Eğitimi',
                'endpoint': '/api/ai/train-model',
                'description': 'AI modellerini özel verilerinizle eğitin'
            },
            'own_content_edit': {
                'name': 'Kendi İçeriğini Düzenle',
                'endpoint': '/api/ai/content-edit',
                'description': 'Kendi içeriklerinizi AI ile düzenleyin'
            },
            'template_use': {
                'name': 'Şablon Kullanımı',
                'endpoint': '/api/ai/use-template',
                'description': 'Hazır şablonları kullanarak içerik oluşturun'
            }
        }
        
        available = []
        for permission in permissions:
            if permission in action_map:
                available.append(action_map[permission])
            elif permission == '*':
                # Admin - tüm aksiyonlar
                available = list(action_map.values())
                break
        
        return available
    
    def get_ai_system_status(self) -> Dict[str, Any]:
        """
        AI sistem durumu (güncellendi)
        
        Returns:
            Sistem durumu
        """
        try:
            # Mevcut sistem durumu
            base_status = super().get_ai_system_status() if hasattr(super(), 'get_ai_system_status') else {}
            
            # AI Core durumu
            ai_core_info = ai_core.get_model_info()
            ai_core_metrics = ai_core.get_metrics()
            
            # Kategori istatistikleri
            category_stats = self.content_categorizer.get_category_stats()
            
            # Depolama özeti
            storage_summary = self.smart_storage.get_storage_summary()
            
            # Gelişmiş özellik durumu
            advanced_status = {
                'product_editor': 'active',
                'template_generator': 'active',
                'content_manager': 'active',
                'role_based_access': 'active'
            }
            
            return {
                'success': True,
                'data': {
                    'ai_core': {
                        'info': ai_core_info,
                        'metrics': ai_core_metrics
                    },
                    'categorization': category_stats,
                    'storage': storage_summary,
                    'advanced_features': advanced_status,
                    'system_health': {
                        'status': 'healthy',
                        'uptime': 'N/A',
                        'last_check': datetime.now().isoformat()
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"AI sistem durumu alma hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'SYSTEM_STATUS_ERROR'
            }
    
    def get_user_profile_summary(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kullanıcı profil özeti
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Profil özeti
        """
        try:
            user_id = request_data.get('user_id', session.get('user_id', 1))
            
            # Kullanıcı profil özeti
            profile_summary = self.user_content_manager.get_user_profile_summary(user_id)
            
            return {
                'success': True,
                'data': profile_summary
            }
            
        except Exception as e:
            self.logger.error(f"Kullanıcı profil özeti alma hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'USER_PROFILE_ERROR'
            }
    
    async def suggest_categories(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kategori önerileri
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Kategori önerileri
        """
        try:
            user_id = request_data.get('user_id', session.get('user_id', 1))
            limit = request_data.get('limit', 20)
            
            # Kategori önerileri
            suggestions = await self.content_categorizer.suggest_categories_for_user(
                user_id, limit
            )
            
            return {
                'success': True,
                'data': {
                    'suggestions': suggestions,
                    'user_id': user_id,
                    'limit': limit
                }
            }
            
        except Exception as e:
            self.logger.error(f"Kategori önerileri alma hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'CATEGORY_SUGGESTIONS_ERROR'
            }
    
    async def find_similar_images(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Benzer görselleri bul
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Benzer görseller
        """
        try:
            image_path = request_data.get('image_path')
            user_id = request_data.get('user_id', session.get('user_id', 1))
            similarity_threshold = request_data.get('similarity_threshold', 0.8)
            
            if not image_path:
                return {
                    'success': False,
                    'error': 'image_path parametresi gerekli',
                    'code': 'MISSING_PARAMETER'
                }
            
            # Benzer görselleri bul
            similar_images = await self.image_recognition.find_similar_images(
                image_path, user_id, similarity_threshold
            )
            
            return {
                'success': True,
                'data': {
                    'similar_images': similar_images,
                    'query_image': image_path,
                    'similarity_threshold': similarity_threshold
                }
            }
            
        except Exception as e:
            self.logger.error(f"Benzer görsel arama hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'SIMILAR_IMAGES_ERROR'
            }
    
    async def generate_thumbnail(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thumbnail oluştur
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Thumbnail oluşturma sonucu
        """
        try:
            image_path = request_data.get('image_path')
            thumbnail_path = request_data.get('thumbnail_path')
            
            if not image_path or not thumbnail_path:
                return {
                    'success': False,
                    'error': 'image_path ve thumbnail_path parametreleri gerekli',
                    'code': 'MISSING_PARAMETER'
                }
            
            # Thumbnail oluştur
            success = await self.image_recognition.generate_thumbnail(
                image_path, thumbnail_path
            )
            
            return {
                'success': success,
                'data': {
                    'thumbnail_created': success,
                    'thumbnail_path': thumbnail_path if success else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Thumbnail oluşturma hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'THUMBNAIL_GENERATION_ERROR'
            }
    
    async def start_realtime_processing(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gerçek zamanlı AI işleme başlat
        
        Args:
            request_data: İstek verileri
            
        Returns:
            İşlem sonucu
        """
        try:
            from core.AI.ai_realtime_processor import realtime_processor
            
            if not realtime_processor:
                return {
                    'success': False,
                    'error': 'Realtime processor başlatılmamış',
                    'code': 'PROCESSOR_NOT_INITIALIZED'
                }
            
            user_id = request_data.get('user_id', session.get('user_id', 1))
            task_type = request_data.get('task_type')
            task_data = request_data.get('task_data', {})
            priority = request_data.get('priority', 5)
            
            # Görev gönder
            task_id = await realtime_processor.submit_task(
                task_type=task_type,
                user_id=user_id,
                data=task_data,
                priority=priority
            )
            
            return {
                'success': True,
                'task_id': task_id,
                'status': 'submitted',
                'message': 'Görev işleme alındı'
            }
            
        except Exception as e:
            self.logger.error(f"Realtime processing başlatma hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'REALTIME_PROCESSING_ERROR'
            }
    
    async def get_task_status(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Görev durumunu sorgula
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Görev durumu
        """
        try:
            from core.AI.ai_realtime_processor import realtime_processor
            
            task_id = request_data.get('task_id')
            if not task_id:
                return {
                    'success': False,
                    'error': 'task_id parametresi gerekli',
                    'code': 'MISSING_PARAMETER'
                }
            
            status = await realtime_processor.get_task_status(task_id)
            
            if status:
                return {
                    'success': True,
                    'data': status
                }
            else:
                return {
                    'success': False,
                    'error': 'Görev bulunamadı',
                    'code': 'TASK_NOT_FOUND'
                }
                
        except Exception as e:
            self.logger.error(f"Görev durumu sorgulama hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'STATUS_QUERY_ERROR'
            }
    
    async def train_user_model(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kullanıcı modelini eğit
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Eğitim sonucu
        """
        try:
            from core.AI.ai_learning_engine import ai_learning_engine
            
            user_id = request_data.get('user_id', session.get('user_id', 1))
            user_role = self._get_user_role()
            
            # İzin kontrolü
            if user_role not in ['admin', 'premium']:
                return {
                    'success': False,
                    'error': 'Model eğitimi için yetkiniz yok',
                    'code': 'PERMISSION_DENIED'
                }
            
            # Model eğitimi
            result = await ai_learning_engine.learn_user_behavior(user_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Model eğitimi hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'TRAINING_ERROR'
            }
    
    async def get_personalized_recommendations(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kişiselleştirilmiş öneriler al
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Öneriler
        """
        try:
            from core.AI.ai_learning_engine import ai_learning_engine
            
            user_id = request_data.get('user_id', session.get('user_id', 1))
            context = request_data.get('context', {})
            
            # Mevcut bağlamı ekle
            context.update({
                'timestamp': datetime.now().isoformat(),
                'session_id': session.get('session_id'),
                'device_type': request.user_agent.platform
            })
            
            # Öneriler al
            result = await ai_learning_engine.get_personalized_recommendations(user_id, context)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Kişiselleştirilmiş öneri hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'RECOMMENDATION_ERROR'
            }
    
    async def submit_feedback(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kullanıcı geri bildirimi gönder
        
        Args:
            request_data: İstek verileri
            
        Returns:
            İşlem sonucu
        """
        try:
            from core.AI.ai_learning_engine import ai_learning_engine
            
            user_id = request_data.get('user_id', session.get('user_id', 1))
            feedback_data = request_data.get('feedback', {})
            
            if not feedback_data:
                return {
                    'success': False,
                    'error': 'feedback parametresi gerekli',
                    'code': 'MISSING_PARAMETER'
                }
            
            # Geri bildirimi işle
            result = await ai_learning_engine.process_user_feedback(user_id, feedback_data)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Geri bildirim gönderme hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'FEEDBACK_ERROR'
            }
    
    async def analyze_user_patterns(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kullanıcı desenlerini analiz et
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Desen analizi
        """
        try:
            from core.AI.ai_learning_engine import ai_learning_engine
            
            user_id = request_data.get('user_id', session.get('user_id', 1))
            
            # Desen analizi
            result = await ai_learning_engine.analyze_user_patterns(user_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Desen analizi hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'PATTERN_ANALYSIS_ERROR'
            }
    
    async def advanced_image_analysis(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gelişmiş görsel analizi
        
        Args:
            request_data: İstek verileri
            
        Returns:
            Analiz sonuçları
        """
        try:
            from core.AI.ai_enhanced_core import enhanced_ai_core
            
            image_path = request_data.get('image_path')
            analysis_types = request_data.get('analysis_types', ['caption', 'quality', 'aesthetic'])
            
            if not image_path:
                return {
                    'success': False,
                    'error': 'image_path parametresi gerekli',
                    'code': 'MISSING_PARAMETER'
                }
            
            # Gelişmiş analiz
            result = await enhanced_ai_core.advanced_image_analysis(image_path, analysis_types)
            
            return {
                'success': True,
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"Gelişmiş görsel analizi hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'ADVANCED_ANALYSIS_ERROR'
            }
    
    async def enhance_image(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Görsel iyileştirme
        
        Args:
            request_data: İstek verileri
            
        Returns:
            İyileştirme sonucu
        """
        try:
            from core.AI.ai_enhanced_core import enhanced_ai_core
            
            image_path = request_data.get('image_path')
            enhancement_type = request_data.get('enhancement_type', 'auto')
            
            if not image_path:
                return {
                    'success': False,
                    'error': 'image_path parametresi gerekli',
                    'code': 'MISSING_PARAMETER'
                }
            
            # Görsel iyileştirme
            result = await enhanced_ai_core.smart_image_enhancement(image_path, enhancement_type)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Görsel iyileştirme hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'ENHANCEMENT_ERROR'
            }
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """
        Gerçek zamanlı AI metrikleri
        
        Returns:
            Metrikler
        """
        try:
            from core.AI.ai_realtime_processor import realtime_processor
            
            if realtime_processor:
                metrics = realtime_processor.get_metrics()
            else:
                metrics = {'message': 'Realtime processor aktif değil'}
            
            return {
                'success': True,
                'data': {
                    'realtime_metrics': metrics,
                    'ai_core_metrics': ai_core.get_metrics(),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Metrik alma hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'METRICS_ERROR'
            }


# Global AI Controller instance
ai_controller = AIController()