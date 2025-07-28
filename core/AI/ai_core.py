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

import torch
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModel

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
        
        # AI modelleri ve pipeline'ları
        self.models = {}
        self.pipelines = {}
        self.device = self._get_device()
        
        # Performans metrikleri
        self.metrics = {
            'total_processed': 0,
            'success_rate': 0.0,
            'average_processing_time': 0.0,
            'errors': []
        }
        
        # Thread pool executor
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Başlatma
        self._initialize_models()
        
        self.logger.info("AI Core başlatıldı")
    
    def _get_device(self) -> str:
        """Kullanılacak cihazı belirle (GPU/CPU)"""
        if torch.cuda.is_available():
            device = "cuda"
            self.logger.info(f"GPU kullanılıyor: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            device = "mps"
            self.logger.info("Apple Silicon GPU kullanılıyor")
        else:
            device = "cpu"
            self.logger.info("CPU kullanılıyor")
        
        return device
    
    def _initialize_models(self):
        """AI modellerini başlat"""
        try:
            # Görsel sınıflandırma modeli
            self.pipelines['image_classifier'] = pipeline(
                "image-classification",
                model="microsoft/resnet-50",
                device=0 if self.device == "cuda" else -1
            )
            
            # Nesne algılama modeli (YOLO)
            try:
                from ultralytics import YOLO
                self.models['yolo'] = YOLO('yolov8n.pt')
                self.logger.info("YOLO modeli yüklendi")
            except Exception as e:
                self.logger.warning(f"YOLO modeli yüklenemedi: {e}")
            
            # Metin analizi modeli
            self.pipelines['text_analyzer'] = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                device=0 if self.device == "cuda" else -1
            )
            
            # Embedding modeli
            try:
                from sentence_transformers import SentenceTransformer
                self.models['embedder'] = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("Embedding modeli yüklendi")
            except Exception as e:
                self.logger.warning(f"Embedding modeli yüklenemedi: {e}")
            
            self.logger.info("AI modelleri başarıyla yüklendi")
            
        except Exception as e:
            self.logger.error(f"AI modelleri yüklenirken hata: {e}")
            raise
    
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
        self.metrics['total_processed'] += 1
        
        if success:
            # Ortalama işlem süresini güncelle
            current_avg = self.metrics['average_processing_time']
            total = self.metrics['total_processed']
            self.metrics['average_processing_time'] = (current_avg * (total - 1) + processing_time) / total
        else:
            self.metrics['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'processing_time': processing_time
            })
        
        # Başarı oranını hesapla
        error_count = len(self.metrics['errors'])
        success_count = self.metrics['total_processed'] - error_count
        self.metrics['success_rate'] = success_count / self.metrics['total_processed'] if self.metrics['total_processed'] > 0 else 0
    
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