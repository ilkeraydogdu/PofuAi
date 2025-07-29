#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi Real-time AI Processor
=============================

Gerçek zamanlı AI işleme modülü - WebSocket ve streaming desteği
"""

import os
import json
import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import uuid
from queue import Queue, Empty
import threading
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
from PIL import Image
import cv2
import torch
from flask_socketio import SocketIO, emit, join_room, leave_room

from core.Services.logger import LoggerService
from core.Database.connection import DatabaseConnection
from core.AI.ai_core import ai_core
from core.AI.ai_enhanced_core import enhanced_ai_core
from core.AI.ai_advanced_features import advanced_ai_features


class ProcessingStatus(Enum):
    """İşlem durumları"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AITask:
    """AI görevi veri yapısı"""
    task_id: str
    task_type: str
    user_id: int
    data: Dict[str, Any]
    status: ProcessingStatus = ProcessingStatus.PENDING
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: float = 0.0
    callback: Optional[Callable] = None


class RealtimeAIProcessor:
    """
    Gerçek zamanlı AI işlemci sınıfı
    """
    
    def __init__(self, socketio: Optional[SocketIO] = None):
        self.logger = LoggerService.get_logger()
        self.db = DatabaseConnection()
        self.socketio = socketio
        
        # Görev kuyrukları
        self.task_queue = asyncio.Queue()
        self.priority_queue = asyncio.PriorityQueue()
        
        # Aktif görevler
        self.active_tasks: Dict[str, AITask] = {}
        
        # İşlem havuzu
        self.worker_pool_size = 4
        self.workers = []
        
        # Performans metrikleri
        self.metrics = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'average_processing_time': 0,
            'current_queue_size': 0
        }
        
        # WebRTC desteği için
        self.video_processors = {}
        
        # Başlatma
        self._start_workers()
        
        self.logger.info("Realtime AI Processor başlatıldı")
    
    def _start_workers(self):
        """İşçi thread'lerini başlat"""
        for i in range(self.worker_pool_size):
            worker = threading.Thread(
                target=self._worker_loop,
                args=(i,),
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
    
    def _worker_loop(self, worker_id: int):
        """İşçi döngüsü"""
        self.logger.info(f"Worker {worker_id} başlatıldı")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while True:
            try:
                # Görev al
                task = loop.run_until_complete(self._get_next_task())
                
                if task:
                    # Görevi işle
                    loop.run_until_complete(self._process_task(task, worker_id))
                else:
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Worker {worker_id} hatası: {e}")
                time.sleep(1)
    
    async def _get_next_task(self) -> Optional[AITask]:
        """Sıradaki görevi al"""
        try:
            # Önce priority queue kontrol et
            if not self.priority_queue.empty():
                _, task = await self.priority_queue.get()
                return task
            
            # Normal queue kontrol et
            if not self.task_queue.empty():
                return await self.task_queue.get()
                
        except:
            pass
        
        return None
    
    async def _process_task(self, task: AITask, worker_id: int):
        """Görevi işle"""
        self.logger.info(f"Worker {worker_id} görevi işliyor: {task.task_id}")
        
        # Durumu güncelle
        task.status = ProcessingStatus.PROCESSING
        task.started_at = datetime.now()
        self.active_tasks[task.task_id] = task
        
        # İlerleme bildirimi
        await self._emit_progress(task, 0, "İşlem başlatıldı")
        
        try:
            # Görev tipine göre işlem
            if task.task_type == "image_analysis":
                result = await self._process_image_analysis(task)
            elif task.task_type == "image_enhancement":
                result = await self._process_image_enhancement(task)
            elif task.task_type == "template_generation":
                result = await self._process_template_generation(task)
            elif task.task_type == "batch_processing":
                result = await self._process_batch(task)
            elif task.task_type == "video_frame":
                result = await self._process_video_frame(task)
            else:
                raise ValueError(f"Bilinmeyen görev tipi: {task.task_type}")
            
            # Başarılı tamamlama
            task.status = ProcessingStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            task.progress = 100
            
            # Metrikleri güncelle
            self.metrics['completed_tasks'] += 1
            self._update_average_processing_time(task)
            
            # Sonuç bildirimi
            await self._emit_result(task)
            
            self.logger.info(f"Görev tamamlandı: {task.task_id}")
            
        except Exception as e:
            # Hata durumu
            task.status = ProcessingStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
            self.metrics['failed_tasks'] += 1
            
            # Hata bildirimi
            await self._emit_error(task)
            
            self.logger.error(f"Görev başarısız: {task.task_id} - {e}")
        
        finally:
            # Aktif görevlerden kaldır
            self.active_tasks.pop(task.task_id, None)
    
    async def submit_task(self, task_type: str, user_id: int, data: Dict[str, Any], 
                         priority: int = 5, callback: Optional[Callable] = None) -> str:
        """
        Yeni görev gönder
        
        Args:
            task_type: Görev tipi
            user_id: Kullanıcı ID
            data: Görev verileri
            priority: Öncelik (1-10, 1 en yüksek)
            callback: Tamamlanma callback'i
            
        Returns:
            Görev ID
        """
        # Görev oluştur
        task = AITask(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            user_id=user_id,
            data=data,
            priority=priority,
            callback=callback
        )
        
        # Kuyruğa ekle
        if priority < 5:
            await self.priority_queue.put((priority, task))
        else:
            await self.task_queue.put(task)
        
        # Metrikleri güncelle
        self.metrics['total_tasks'] += 1
        self.metrics['current_queue_size'] = self.task_queue.qsize() + self.priority_queue.qsize()
        
        self.logger.info(f"Yeni görev eklendi: {task.task_id} (Tip: {task_type}, Öncelik: {priority})")
        
        return task.task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Görev durumunu al"""
        task = self.active_tasks.get(task_id)
        
        if task:
            return {
                'task_id': task.task_id,
                'status': task.status.value,
                'progress': task.progress,
                'created_at': task.created_at.isoformat(),
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'result': task.result,
                'error': task.error
            }
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Görevi iptal et"""
        task = self.active_tasks.get(task_id)
        
        if task and task.status == ProcessingStatus.PENDING:
            task.status = ProcessingStatus.CANCELLED
            self.active_tasks.pop(task_id, None)
            
            await self._emit_cancelled(task)
            
            self.logger.info(f"Görev iptal edildi: {task_id}")
            return True
        
        return False
    
    # İşlem metodları
    async def _process_image_analysis(self, task: AITask) -> Dict[str, Any]:
        """Görsel analizi işle"""
        image_path = task.data.get('image_path')
        analysis_types = task.data.get('analysis_types', ['caption', 'quality', 'aesthetic'])
        
        # İlerleme: %10
        await self._emit_progress(task, 10, "Görsel yükleniyor")
        
        # Gelişmiş analiz
        result = await enhanced_ai_core.advanced_image_analysis(image_path, analysis_types)
        
        # İlerleme: %90
        await self._emit_progress(task, 90, "Analiz tamamlanıyor")
        
        return result
    
    async def _process_image_enhancement(self, task: AITask) -> Dict[str, Any]:
        """Görsel iyileştirme işle"""
        image_path = task.data.get('image_path')
        enhancement_type = task.data.get('enhancement_type', 'auto')
        
        # İlerleme: %20
        await self._emit_progress(task, 20, "Görsel analiz ediliyor")
        
        # İyileştirme
        result = await enhanced_ai_core.smart_image_enhancement(image_path, enhancement_type)
        
        # İlerleme: %80
        await self._emit_progress(task, 80, "İyileştirme uygulanıyor")
        
        return result
    
    async def _process_template_generation(self, task: AITask) -> Dict[str, Any]:
        """Şablon üretimi işle"""
        # İlerleme: %30
        await self._emit_progress(task, 30, "Şablon parametreleri hazırlanıyor")
        
        # Şablon üret
        result = await advanced_ai_features.generate_social_media_template(
            user_id=task.user_id,
            user_role=task.data.get('user_role', 'user'),
            template_request=task.data
        )
        
        # İlerleme: %70
        await self._emit_progress(task, 70, "İçerik önerileri oluşturuluyor")
        
        return result
    
    async def _process_batch(self, task: AITask) -> Dict[str, Any]:
        """Toplu işleme"""
        image_paths = task.data.get('image_paths', [])
        total = len(image_paths)
        results = []
        
        # İlerleme callback'i
        async def progress_callback(progress_data):
            percentage = progress_data['percentage']
            await self._emit_progress(task, percentage, f"İşleniyor: {progress_data['current_file']}")
        
        # Toplu işlem
        result = await enhanced_ai_core.batch_process_with_progress(
            image_paths, 
            callback=progress_callback
        )
        
        return result
    
    async def _process_video_frame(self, task: AITask) -> Dict[str, Any]:
        """Video frame işleme"""
        frame_data = task.data.get('frame_data')
        processing_type = task.data.get('processing_type', 'object_detection')
        
        # Base64'ten görüntüye dönüştür
        import base64
        from io import BytesIO
        
        frame_bytes = base64.b64decode(frame_data)
        image = Image.open(BytesIO(frame_bytes))
        
        # İşleme türüne göre
        if processing_type == 'object_detection':
            # Nesne algılama
            result = await ai_core._detect_objects_from_image(image)
        elif processing_type == 'face_detection':
            # Yüz algılama
            result = await self._detect_faces_in_frame(image)
        else:
            result = {'error': 'Unknown processing type'}
        
        return result
    
    async def _detect_faces_in_frame(self, image: Image.Image) -> Dict[str, Any]:
        """Frame'de yüz algılama"""
        try:
            import face_recognition
            
            # PIL'den numpy array'e
            frame = np.array(image)
            
            # Yüz konumları
            face_locations = face_recognition.face_locations(frame)
            
            # Yüz özellikleri
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            
            faces = []
            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                faces.append({
                    'location': {
                        'top': top,
                        'right': right,
                        'bottom': bottom,
                        'left': left
                    },
                    'width': right - left,
                    'height': bottom - top,
                    'encoding': encoding.tolist()  # JSON serializable
                })
            
            return {
                'faces_detected': len(faces),
                'faces': faces
            }
            
        except Exception as e:
            self.logger.error(f"Yüz algılama hatası: {e}")
            return {'error': str(e)}
    
    # WebSocket bildirimleri
    async def _emit_progress(self, task: AITask, percentage: float, message: str):
        """İlerleme bildirimi gönder"""
        task.progress = percentage
        
        if self.socketio:
            self.socketio.emit('ai_progress', {
                'task_id': task.task_id,
                'progress': percentage,
                'message': message,
                'status': task.status.value
            }, room=f"user_{task.user_id}")
        
        # Callback varsa çağır
        if task.callback:
            await task.callback({
                'type': 'progress',
                'task_id': task.task_id,
                'progress': percentage,
                'message': message
            })
    
    async def _emit_result(self, task: AITask):
        """Sonuç bildirimi gönder"""
        if self.socketio:
            self.socketio.emit('ai_result', {
                'task_id': task.task_id,
                'status': 'completed',
                'result': task.result,
                'processing_time': (task.completed_at - task.started_at).total_seconds()
            }, room=f"user_{task.user_id}")
        
        # Callback varsa çağır
        if task.callback:
            await task.callback({
                'type': 'result',
                'task_id': task.task_id,
                'result': task.result
            })
    
    async def _emit_error(self, task: AITask):
        """Hata bildirimi gönder"""
        if self.socketio:
            self.socketio.emit('ai_error', {
                'task_id': task.task_id,
                'status': 'failed',
                'error': task.error
            }, room=f"user_{task.user_id}")
        
        # Callback varsa çağır
        if task.callback:
            await task.callback({
                'type': 'error',
                'task_id': task.task_id,
                'error': task.error
            })
    
    async def _emit_cancelled(self, task: AITask):
        """İptal bildirimi gönder"""
        if self.socketio:
            self.socketio.emit('ai_cancelled', {
                'task_id': task.task_id,
                'status': 'cancelled'
            }, room=f"user_{task.user_id}")
    
    def _update_average_processing_time(self, task: AITask):
        """Ortalama işlem süresini güncelle"""
        if task.started_at and task.completed_at:
            processing_time = (task.completed_at - task.started_at).total_seconds()
            
            # Hareketli ortalama
            current_avg = self.metrics['average_processing_time']
            completed = self.metrics['completed_tasks']
            
            self.metrics['average_processing_time'] = (
                (current_avg * (completed - 1) + processing_time) / completed
            )
    
    # Video streaming desteği
    async def start_video_stream(self, user_id: int, stream_config: Dict[str, Any]) -> str:
        """Video stream başlat"""
        stream_id = str(uuid.uuid4())
        
        processor = VideoStreamProcessor(
            stream_id=stream_id,
            user_id=user_id,
            config=stream_config,
            ai_processor=self
        )
        
        self.video_processors[stream_id] = processor
        await processor.start()
        
        return stream_id
    
    async def stop_video_stream(self, stream_id: str) -> bool:
        """Video stream durdur"""
        processor = self.video_processors.get(stream_id)
        
        if processor:
            await processor.stop()
            self.video_processors.pop(stream_id, None)
            return True
        
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Performans metriklerini al"""
        return {
            **self.metrics,
            'active_tasks': len(self.active_tasks),
            'active_streams': len(self.video_processors),
            'worker_pool_size': self.worker_pool_size
        }


class VideoStreamProcessor:
    """Video stream işleyici"""
    
    def __init__(self, stream_id: str, user_id: int, config: Dict[str, Any], 
                 ai_processor: RealtimeAIProcessor):
        self.stream_id = stream_id
        self.user_id = user_id
        self.config = config
        self.ai_processor = ai_processor
        self.is_running = False
        self.frame_rate = config.get('frame_rate', 10)
        self.processing_type = config.get('processing_type', 'object_detection')
        
    async def start(self):
        """Stream'i başlat"""
        self.is_running = True
        self.logger.info(f"Video stream başlatıldı: {self.stream_id}")
        
        # Frame işleme döngüsü başlatılabilir
        asyncio.create_task(self._process_frames())
    
    async def stop(self):
        """Stream'i durdur"""
        self.is_running = False
        self.logger.info(f"Video stream durduruldu: {self.stream_id}")
    
    async def _process_frames(self):
        """Frame'leri işle"""
        while self.is_running:
            try:
                # Frame processing logic here
                await asyncio.sleep(1 / self.frame_rate)
            except Exception as e:
                self.logger.error(f"Frame işleme hatası: {e}")
    
    async def process_frame(self, frame_data: bytes) -> Dict[str, Any]:
        """Tek frame işle"""
        # AI görev olarak gönder
        task_id = await self.ai_processor.submit_task(
            task_type='video_frame',
            user_id=self.user_id,
            data={
                'frame_data': frame_data,
                'processing_type': self.processing_type,
                'stream_id': self.stream_id
            },
            priority=3  # Video frame'ler yüksek öncelikli
        )
        
        return {'task_id': task_id}


# Global instance
realtime_processor = None

def init_realtime_processor(socketio: SocketIO):
    """Realtime processor'ı başlat"""
    global realtime_processor
    realtime_processor = RealtimeAIProcessor(socketio)
    return realtime_processor