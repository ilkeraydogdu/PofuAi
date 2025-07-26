"""
QueueService
Arka plan işlerini (background jobs) ve kuyruk işlemlerini yöneten servis.
"""

import json
import time
import uuid
import threading
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import pickle
import sqlite3
from pathlib import Path

from .base_service import BaseService

class JobStatus(Enum):
    """Job durumları"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobPriority(Enum):
    """Job öncelikleri"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

class Job:
    """Kuyruk işi sınıfı"""
    
    def __init__(self, job_type: str, data: Dict[str, Any], priority: JobPriority = JobPriority.NORMAL):
        self.id = str(uuid.uuid4())
        self.type = job_type
        self.data = data
        self.priority = priority
        self.status = JobStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.attempts = 0
        self.max_attempts = 3
        self.error_message = None
        self.result = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Job'u dictionary'e çevir"""
        return {
            'id': self.id,
            'type': self.type,
            'data': self.data,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'error_message': self.error_message,
            'result': self.result
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Dictionary'den Job oluştur"""
        job = cls(data['type'], data['data'], JobPriority(data['priority']))
        job.id = data['id']
        job.status = JobStatus(data['status'])
        job.created_at = datetime.fromisoformat(data['created_at'])
        
        if data['started_at']:
            job.started_at = datetime.fromisoformat(data['started_at'])
        if data['completed_at']:
            job.completed_at = datetime.fromisoformat(data['completed_at'])
        
        job.attempts = data['attempts']
        job.max_attempts = data['max_attempts']
        job.error_message = data['error_message']
        job.result = data['result']
        
        return job

class QueueDriver:
    """Queue sürücü arayüzü"""
    
    def push(self, job: Job) -> bool:
        """Job'u kuyruğa ekle"""
        raise NotImplementedError("push metodu override edilmeli")
    
    def pop(self) -> Optional[Job]:
        """Kuyruktan job al"""
        raise NotImplementedError("pop metodu override edilmeli")
    
    def get(self, job_id: str) -> Optional[Job]:
        """Job ID ile job getir"""
        raise NotImplementedError("get metodu override edilmeli")
    
    def update(self, job: Job) -> bool:
        """Job'u güncelle"""
        raise NotImplementedError("update metodu override edilmeli")
    
    def delete(self, job_id: str) -> bool:
        """Job'u sil"""
        raise NotImplementedError("delete metodu override edilmeli")
    
    def clear(self) -> bool:
        """Tüm kuyruğu temizle"""
        raise NotImplementedError("clear metodu override edilmeli")
    
    def size(self) -> int:
        """Kuyruk boyutunu getir"""
        raise NotImplementedError("size metodu override edilmeli")

class FileQueueDriver(QueueDriver):
    """Dosya tabanlı queue sürücüsü"""
    
    def __init__(self, config: Dict[str, Any]):
        self.queue_path = Path(config.get('path', 'storage/Queue'))
        self.queue_path.mkdir(parents=True, exist_ok=True)
        self.pending_file = self.queue_path / "pending.json"
        self.processing_file = self.queue_path / "processing.json"
        self.completed_file = self.queue_path / "completed.json"
        self.failed_file = self.queue_path / "failed.json"
        
        # Dosyaları oluştur
        for file_path in [self.pending_file, self.processing_file, self.completed_file, self.failed_file]:
            if not file_path.exists():
                file_path.write_text('[]', encoding='utf-8')
    
    def _load_jobs(self, file_path: Path) -> List[Job]:
        """Dosyadan job'ları yükle"""
        try:
            data = json.loads(file_path.read_text(encoding='utf-8'))
            return [Job.from_dict(job_data) for job_data in data]
        except Exception:
            return []
    
    def _save_jobs(self, file_path: Path, jobs: List[Job]):
        """Job'ları dosyaya kaydet"""
        try:
            job_data = [job.to_dict() for job in jobs]
            file_path.write_text(json.dumps(job_data, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            print(f"Job kaydetme hatası: {e}")
    
    def push(self, job: Job) -> bool:
        """Job'u kuyruğa ekle"""
        try:
            jobs = self._load_jobs(self.pending_file)
            jobs.append(job)
            # Önceliğe göre sırala
            jobs.sort(key=lambda x: x.priority.value, reverse=True)
            self._save_jobs(self.pending_file, jobs)
            return True
        except Exception as e:
            print(f"Job ekleme hatası: {e}")
            return False
    
    def pop(self) -> Optional[Job]:
        """Kuyruktan job al"""
        try:
            pending_jobs = self._load_jobs(self.pending_file)
            if not pending_jobs:
                return None
            
            # En yüksek öncelikli job'u al
            job = pending_jobs.pop(0)
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.now()
            
            # Pending listesini güncelle
            self._save_jobs(self.pending_file, pending_jobs)
            
            # Processing listesine ekle
            processing_jobs = self._load_jobs(self.processing_file)
            processing_jobs.append(job)
            self._save_jobs(self.processing_file, processing_jobs)
            
            return job
        except Exception as e:
            print(f"Job alma hatası: {e}")
            return None
    
    def get(self, job_id: str) -> Optional[Job]:
        """Job ID ile job getir"""
        try:
            # Tüm dosyalarda ara
            for file_path in [self.pending_file, self.processing_file, self.completed_file, self.failed_file]:
                jobs = self._load_jobs(file_path)
                for job in jobs:
                    if job.id == job_id:
                        return job
            return None
        except Exception as e:
            print(f"Job getirme hatası: {e}")
            return None
    
    def update(self, job: Job) -> bool:
        """Job'u güncelle"""
        try:
            # Job'u tüm dosyalardan sil
            for file_path in [self.pending_file, self.processing_file, self.completed_file, self.failed_file]:
                jobs = self._load_jobs(file_path)
                jobs = [j for j in jobs if j.id != job.id]
                self._save_jobs(file_path, jobs)
            
            # Duruma göre uygun dosyaya ekle
            if job.status == JobStatus.PENDING:
                self.push(job)
            elif job.status == JobStatus.PROCESSING:
                processing_jobs = self._load_jobs(self.processing_file)
                processing_jobs.append(job)
                self._save_jobs(self.processing_file, processing_jobs)
            elif job.status == JobStatus.COMPLETED:
                completed_jobs = self._load_jobs(self.completed_file)
                completed_jobs.append(job)
                self._save_jobs(self.completed_file, completed_jobs)
            elif job.status == JobStatus.FAILED:
                failed_jobs = self._load_jobs(self.failed_file)
                failed_jobs.append(job)
                self._save_jobs(self.failed_file, failed_jobs)
            
            return True
        except Exception as e:
            print(f"Job güncelleme hatası: {e}")
            return False
    
    def delete(self, job_id: str) -> bool:
        """Job'u sil"""
        try:
            # Job'u tüm dosyalardan sil
            for file_path in [self.pending_file, self.processing_file, self.completed_file, self.failed_file]:
                jobs = self._load_jobs(file_path)
                jobs = [j for j in jobs if j.id != job_id]
                self._save_jobs(file_path, jobs)
            return True
        except Exception as e:
            print(f"Job silme hatası: {e}")
            return False
    
    def clear(self) -> bool:
        """Tüm kuyruğu temizle"""
        try:
            for file_path in [self.pending_file, self.processing_file, self.completed_file, self.failed_file]:
                file_path.write_text('[]', encoding='utf-8')
            return True
        except Exception as e:
            print(f"Queue temizleme hatası: {e}")
            return False
    
    def size(self) -> int:
        """Kuyruk boyutunu getir"""
        try:
            pending_jobs = self._load_jobs(self.pending_file)
            return len(pending_jobs)
        except Exception:
            return 0

class QueueService(BaseService):
    """Kuyruk işlemleri için merkezi servis"""
    
    def __init__(self):
        super().__init__()
        self.queue_config = self.get_config('queue', {})
        self.driver = self._create_driver()
        self.workers = []
        self.job_handlers = {}
        self.is_running = False
    
    def _create_driver(self) -> QueueDriver:
        """Queue sürücüsü oluştur"""
        driver_name = self.queue_config.get('driver', 'file')
        
        if driver_name == 'file':
            return FileQueueDriver(self.queue_config)
        else:
            raise ValueError(f"Desteklenmeyen queue sürücüsü: {driver_name}")
    
    def add_job(self, job_type: str, data: Dict[str, Any], 
                priority: JobPriority = JobPriority.NORMAL) -> Dict[str, Any]:
        """Yeni job ekle"""
        try:
            job = Job(job_type, data, priority)
            success = self.driver.push(job)
            
            if success:
                self.log(f"Job eklendi: {job.id} ({job_type})")
                return self.success_response(
                    data={'job_id': job.id, 'type': job_type},
                    message="Job kuyruğa eklendi"
                )
            else:
                return self.error_response("Job eklenemedi")
                
        except Exception as e:
            return self.handle_exception(e, "Job ekleme hatası")
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Job bilgilerini getir"""
        try:
            job = self.driver.get(job_id)
            
            if job:
                return self.success_response(
                    data=job.to_dict(),
                    message="Job bilgileri getirildi"
                )
            else:
                return self.error_response("Job bulunamadı", status=404)
                
        except Exception as e:
            return self.handle_exception(e, "Job getirme hatası")
    
    def delete_job(self, job_id: str) -> Dict[str, Any]:
        """Job'u sil"""
        try:
            success = self.driver.delete(job_id)
            
            if success:
                self.log(f"Job silindi: {job_id}")
                return self.success_response(
                    data={'job_id': job_id},
                    message="Job silindi"
                )
            else:
                return self.error_response("Job silinemedi")
                
        except Exception as e:
            return self.handle_exception(e, "Job silme hatası")
    
    def clear_queue(self) -> Dict[str, Any]:
        """Tüm kuyruğu temizle"""
        try:
            success = self.driver.clear()
            
            if success:
                self.log("Queue temizlendi")
                return self.success_response(message="Queue temizlendi")
            else:
                return self.error_response("Queue temizlenemedi")
                
        except Exception as e:
            return self.handle_exception(e, "Queue temizleme hatası")
    
    def register_handler(self, job_type: str, handler: Callable):
        """Job handler'ı kaydet"""
        self.job_handlers[job_type] = handler
        self.log(f"Job handler kaydedildi: {job_type}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Queue istatistiklerini getir"""
        try:
            stats = {
                'queue_size': self.driver.size(),
                'worker_count': len(self.workers),
                'is_running': self.is_running,
                'registered_handlers': list(self.job_handlers.keys())
            }
            
            return self.success_response(data=stats)
            
        except Exception as e:
            return self.handle_exception(e, "Queue stats hatası")

# Önceden tanımlanmış işler
class JobHandlers:
    """Önceden tanımlanmış iş handler'ları"""
    
    @staticmethod
    def send_email(data: Dict[str, Any]):
        """Email gönderme işi"""
        from core.Services.mail_service import get_mail_service
        
        mail_service = get_mail_service()
        return mail_service.send(
            to=data['to'],
            subject=data['subject'],
            body=data.get('body'),
            template=data.get('template'),
            data=data.get('template_data')
        )
    
    @staticmethod
    def send_notification(data: Dict[str, Any]):
        """Bildirim gönderme işi"""
        from core.Services.notification_service import get_notification_service
        
        notification_service = get_notification_service()
        return notification_service.send(
            user_id=data['user_id'],
            title=data['title'],
            message=data['message'],
            type=data.get('type', 'info'),
            data=data.get('data')
        )
    
    @staticmethod
    def process_image(data: Dict[str, Any]):
        """Resim işleme işi"""
        # Resim işleme mantığı
        pass
    
    @staticmethod
    def generate_report(data: Dict[str, Any]):
        """Rapor oluşturma işi"""
        # Rapor oluşturma mantığı
        pass

# Global queue service instance
_queue_service = None

def get_queue_service() -> QueueService:
    """Global queue service instance'ını al"""
    global _queue_service
    if _queue_service is None:
        _queue_service = QueueService()
        
        # Önceden tanımlanmış işleri kaydet
        _queue_service.register_handler('send_email', JobHandlers.send_email)
        _queue_service.register_handler('send_notification', JobHandlers.send_notification)
        _queue_service.register_handler('process_image', JobHandlers.process_image)
        _queue_service.register_handler('generate_report', JobHandlers.generate_report)
    
    return _queue_service 