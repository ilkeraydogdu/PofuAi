#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi AI Core Module
====================

Ana yapay zeka çekirdeği - tüm AI modüllerini koordine eder
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Try to import AI libraries, fallback to mock implementations
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Mock torch module
    class MockTorch:
        @staticmethod
        def cuda_is_available():
            return False
        
        @staticmethod
        def device(device_type):
            return 'cpu'
    
    torch = MockTorch()

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    # Mock transformers
    def pipeline(*args, **kwargs):
        class MockPipeline:
            def __call__(self, text):
                return [{"label": "POSITIVE", "score": 0.9}]
        return MockPipeline()
    
    class AutoTokenizer:
        @staticmethod
        def from_pretrained(*args, **kwargs):
            return None
    
    class AutoModel:
        @staticmethod
        def from_pretrained(*args, **kwargs):
            return None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Mock numpy
    class MockNumpy:
        @staticmethod
        def array(data):
            return data
        
        @staticmethod
        def zeros(shape):
            return [0] * (shape if isinstance(shape, int) else shape[0])
    
    np = MockNumpy()

from core.Services.logger import LoggerService
from core.Database.connection import DatabaseConnection


class AICore:
    """
    Ana AI çekirdeği sınıfı
    Tüm AI modüllerini koordine eder ve yönetir
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AICore, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """AI Core başlatıcı"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.logger = LoggerService.get_logger()
        self.db = DatabaseConnection()
        
        # AI modüllerinin durumunu kontrol et
        self.ai_status = {
            'torch_available': TORCH_AVAILABLE,
            'transformers_available': TRANSFORMERS_AVAILABLE,
            'numpy_available': NUMPY_AVAILABLE
        }
        
        # Device selection
        if TORCH_AVAILABLE:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = 'cpu'
        
        # AI modelleri ve pipeline'ları
        self.models = {}
        self.pipelines = {}
        
        # Performans metrikleri
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0
        }
        
        self.logger.info(f"AI Core başlatıldı - Device: {self.device}")
        self.logger.info(f"AI Status: {self.ai_status}")
        
        # Temel AI servislerini başlat
        self._initialize_services()
    
    def _initialize_services(self):
        """Temel AI servislerini başlat"""
        try:
            # Text analysis pipeline
            if TRANSFORMERS_AVAILABLE:
                self.pipelines['sentiment'] = pipeline('sentiment-analysis')
                self.pipelines['text_classification'] = pipeline('text-classification')
            else:
                # Mock implementations
                self.pipelines['sentiment'] = self._mock_sentiment_analysis
                self.pipelines['text_classification'] = self._mock_text_classification
            
            self.logger.info("AI servisleri başlatıldı")
            
        except Exception as e:
            self.logger.error(f"AI servisleri başlatılırken hata: {e}")
            # Fallback to mock implementations
            self.pipelines['sentiment'] = self._mock_sentiment_analysis
            self.pipelines['text_classification'] = self._mock_text_classification
    
    def _mock_sentiment_analysis(self, text):
        """Mock sentiment analysis"""
        return [{"label": "POSITIVE", "score": 0.8}]
    
    def _mock_text_classification(self, text):
        """Mock text classification"""
        return [{"label": "GENERAL", "score": 0.7}]
    
    async def process_image(self, image_path: str, user_id: int) -> Dict[str, Any]:
        """
        Görsel işleme ana fonksiyonu
        
        Args:
            image_path: İşlenecek görselin yolu
            user_id: Kullanıcı ID'si
            
        Returns:
            İşleme sonuçları
        """
        start_time = datetime.now()
        
        try:
            # Paralel işleme için görevleri hazırla
            tasks = []
            
            # Görsel sınıflandırma
            if 'image_classifier' in self.pipelines:
                tasks.append(self._classify_image(image_path))
            
            # Nesne algılama
            if 'yolo' in self.models:
                tasks.append(self._detect_objects(image_path))
            
            # Meta veri çıkarma
            tasks.append(self._extract_metadata(image_path))
            
            # Tüm görevleri paralel çalıştır
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Sonuçları birleştir
            processed_result = {
                'image_path': image_path,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'classification': results[0] if len(results) > 0 and not isinstance(results[0], Exception) else None,
                'objects': results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None,
                'metadata': results[2] if len(results) > 2 and not isinstance(results[2], Exception) else None,
                'status': 'success'
            }
            
            # Veritabanına kaydet
            await self._save_processing_result(processed_result)
            
            # Metrikleri güncelle
            self._update_metrics(True, processed_result['processing_time'])
            
            self.logger.info(f"Görsel işlendi: {image_path} (Süre: {processed_result['processing_time']:.2f}s)")
            
            return processed_result
            
        except Exception as e:
            error_result = {
                'image_path': image_path,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error'
            }
            
            self._update_metrics(False, 0)
            self.logger.error(f"Görsel işleme hatası: {e}")
            
            return error_result
    
    async def _classify_image(self, image_path: str) -> Dict[str, Any]:
        """Görsel sınıflandırma"""
        try:
            from PIL import Image
            
            image = Image.open(image_path)
            results = self.pipelines['image_classifier'](image)
            
            return {
                'categories': results[:5],  # İlk 5 kategori
                'confidence': results[0]['score'] if results else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Görsel sınıflandırma hatası: {e}")
            return {'error': str(e)}
    
    async def _detect_objects(self, image_path: str) -> Dict[str, Any]:
        """Nesne algılama"""
        try:
            if 'yolo' not in self.models:
                return {'error': 'YOLO modeli mevcut değil'}
            
            results = self.models['yolo'](image_path)
            
            objects = []
            for result in results:
                for box in result.boxes:
                    objects.append({
                        'class': result.names[int(box.cls)],
                        'confidence': float(box.conf),
                        'bbox': box.xyxy.tolist()[0]
                    })
            
            return {
                'objects': objects,
                'count': len(objects)
            }
            
        except Exception as e:
            self.logger.error(f"Nesne algılama hatası: {e}")
            return {'error': str(e)}
    
    async def _extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """Meta veri çıkarma"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            import os
            
            # Dosya bilgileri
            file_stats = os.stat(image_path)
            
            # Görsel bilgileri
            with Image.open(image_path) as img:
                width, height = img.size
                format_info = img.format
                mode = img.mode
                
                # EXIF verileri
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)
            
            return {
                'file_size': file_stats.st_size,
                'creation_time': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                'modification_time': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                'dimensions': {'width': width, 'height': height},
                'format': format_info,
                'mode': mode,
                'exif': exif_data
            }
            
        except Exception as e:
            self.logger.error(f"Meta veri çıkarma hatası: {e}")
            return {'error': str(e)}
    
    async def _save_processing_result(self, result: Dict[str, Any]):
        """İşleme sonuçlarını veritabanına kaydet"""
        try:
            # AI işleme sonuçları tablosuna kaydet
            query = """
            INSERT INTO ai_processing_results 
            (user_id, image_path, classification, objects, metadata, processing_time, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                result['user_id'],
                result['image_path'],
                json.dumps(result.get('classification')),
                json.dumps(result.get('objects')),
                json.dumps(result.get('metadata')),
                result.get('processing_time', 0),
                result['status'],
                datetime.now()
            )
            
            await self.db.execute(query, values)
            
        except Exception as e:
            self.logger.error(f"Sonuç kaydetme hatası: {e}")
    
    def _update_metrics(self, success: bool, processing_time: float):
        """Performans metriklerini güncelle"""
        self.metrics['total_requests'] += 1
        
        if success:
            # Ortalama işlem süresini güncelle
            current_avg = self.metrics['average_response_time']
            total = self.metrics['total_requests']
            self.metrics['average_response_time'] = (current_avg * (total - 1) + processing_time) / total
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
        
        # Başarı oranını hesapla
        total_requests = self.metrics['total_requests']
        successful_requests = self.metrics['successful_requests']
        failed_requests = self.metrics['failed_requests']
        self.metrics['success_rate'] = successful_requests / total_requests if total_requests > 0 else 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Performans metriklerini döndür"""
        return self.metrics.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Yüklü modeller hakkında bilgi"""
        return {
            'device': self.device,
            'models': list(self.models.keys()),
            'pipelines': list(self.pipelines.keys()),
            'status': 'active'
        }
    
    async def batch_process_images(self, image_paths: List[str], user_id: int) -> List[Dict[str, Any]]:
        """Toplu görsel işleme"""
        tasks = [self.process_image(path, user_id) for path in image_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [result if not isinstance(result, Exception) else {'error': str(result)} for result in results]
    
    def shutdown(self):
        """AI Core'u kapat"""
        try:
            self.executor.shutdown(wait=True)
            self.logger.info("AI Core kapatıldı")
        except Exception as e:
            self.logger.error(f"AI Core kapatma hatası: {e}")


# Global AI Core instance
ai_core = AICore()