"""
Service Interfaces
Tüm servisler için interface tanımları - Sözleşme tabanlı programlama
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

class IService(ABC):
    """Temel servis interface'i"""
    
    @abstractmethod
    def get_config(self, section: str, key: str = None, default: Any = None) -> Any:
        """Config değerini getir"""
        pass
    
    @abstractmethod
    def log(self, message: str, level: str = 'info', extra: Optional[Dict] = None):
        """Log mesajı"""
        pass
    
    @abstractmethod
    def success_response(self, data: Any = None, message: str = 'İşlem başarılı', status: int = 200) -> Dict:
        """Başarılı response"""
        pass
    
    @abstractmethod
    def error_response(self, error: str = 'Bir hata oluştu', status: int = 500, data: Any = None) -> Dict:
        """Hata response"""
        pass
    
    @abstractmethod
    def handle_exception(self, ex: Exception, custom_message: str = None) -> Dict:
        """Hata yönetimi"""
        pass

class IMailDriver(ABC):
    """Mail sürücü interface'i"""
    
    @abstractmethod
    def send(self, to: str, subject: str, body: str, **kwargs) -> bool:
        """E-posta gönder"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Sürücü kullanılabilir mi"""
        pass

class ICacheDriver(ABC):
    """Cache sürücü interface'i"""
    
    @abstractmethod
    def get(self, key: str) -> Any:
        """Cache'den veri getir"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Cache'e veri kaydet"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Cache'den veri sil"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Cache'de anahtar var mı"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Tüm cache'i temizle"""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Cache boyutunu getir"""
        pass

class IQueueDriver(ABC):
    """Queue sürücü interface'i"""
    
    @abstractmethod
    def push(self, job: 'Job') -> bool:
        """Job'u kuyruğa ekle"""
        pass
    
    @abstractmethod
    def pop(self) -> Optional['Job']:
        """Kuyruktan job al"""
        pass
    
    @abstractmethod
    def get(self, job_id: str) -> Optional['Job']:
        """Job ID ile job getir"""
        pass
    
    @abstractmethod
    def update(self, job: 'Job') -> bool:
        """Job'u güncelle"""
        pass
    
    @abstractmethod
    def delete(self, job_id: str) -> bool:
        """Job'u sil"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Tüm kuyruğu temizle"""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Kuyruk boyutunu getir"""
        pass

class INotificationChannel(ABC):
    """Bildirim kanalı interface'i"""
    
    @abstractmethod
    def send(self, notification: 'Notification') -> bool:
        """Bildirim gönder"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Kanal kullanılabilir mi"""
        pass

class IEventDispatcher(ABC):
    """Event dispatcher interface'i"""
    
    @abstractmethod
    def dispatch(self, event: 'Event') -> bool:
        """Event'i dispatch et"""
        pass
    
    @abstractmethod
    def listen(self, event_name: str, listener: 'EventListener') -> bool:
        """Event listener ekle"""
        pass
    
    @abstractmethod
    def remove_listener(self, event_name: str, listener: 'EventListener') -> bool:
        """Event listener kaldır"""
        pass

class IValidator(ABC):
    """Validator interface'i"""
    
    @abstractmethod
    def validate(self, data: Dict[str, Any], rules: Dict[str, List[str]]) -> Dict[str, Any]:
        """Veri doğrula"""
        pass
    
    @abstractmethod
    def add_rule(self, field: str, rule: 'ValidationRule') -> bool:
        """Kural ekle"""
        pass
    
    @abstractmethod
    def remove_rule(self, field: str, rule_name: str) -> bool:
        """Kural kaldır"""
        pass

class IServiceContainer(ABC):
    """Service container interface'i"""
    
    @abstractmethod
    def register(self, name: str, service: Any, singleton: bool = True) -> bool:
        """Servis kaydet"""
        pass
    
    @abstractmethod
    def resolve(self, name: str) -> Any:
        """Servis çözümle"""
        pass
    
    @abstractmethod
    def has(self, name: str) -> bool:
        """Servis var mı kontrol et"""
        pass
    
    @abstractmethod
    def remove(self, name: str) -> bool:
        """Servis kaldır"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Tüm servisleri temizle"""
        pass

# Type hints için Job ve Notification sınıfları
class Job:
    pass

class Notification:
    pass

class Event:
    pass

class EventListener:
    pass

class ValidationRule:
    pass 