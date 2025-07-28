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
        
        self.logger.info("AI Controller başlatıldı")
    
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
    
    def get_ai_system_status(self) -> Dict[str, Any]:
        """
        AI sistem durumu
        
        Returns:
            Sistem durumu
        """
        try:
            # AI Core durumu
            ai_core_info = ai_core.get_model_info()
            ai_core_metrics = ai_core.get_metrics()
            
            # Kategori istatistikleri
            category_stats = self.content_categorizer.get_category_stats()
            
            # Depolama özeti
            storage_summary = self.smart_storage.get_storage_summary()
            
            return {
                'success': True,
                'data': {
                    'ai_core': {
                        'info': ai_core_info,
                        'metrics': ai_core_metrics
                    },
                    'categorization': category_stats,
                    'storage': storage_summary,
                    'system_health': {
                        'status': 'healthy',
                        'uptime': 'N/A',  # Bu kısım sistem başlangıcından itibaren hesaplanabilir
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


# Global AI Controller instance
ai_controller = AIController()