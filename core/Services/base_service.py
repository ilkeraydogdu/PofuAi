"""
Base Service
Tüm servisler için temel sınıf - Interface, Event ve Validation entegrasyonu
"""

import sys
import os
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import traceback

# Core modüllerini import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.Config.config import get_config
from .interfaces import IService
from .events import Event, EventDispatcher, SystemEvents
# Döngüsel importu önlemek için Validator ve ValidationResult sınıflarını import etmiyoruz
from .service_container import ServiceContainer

# ValidationResult sınıfını burada tanımlıyoruz
class ValidationResult:
    """Validation sonuç sınıfı"""
    
    def __init__(self):
        self.is_valid = True
        self.errors = {}
        self.warnings = {}
    
    def add_error(self, field: str, message: str):
        """Hata ekle"""
        self.is_valid = False
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)
    
    def add_warning(self, field: str, message: str):
        """Uyarı ekle"""
        if field not in self.warnings:
            self.warnings[field] = []
        self.warnings[field].append(message)
    
    def get_errors(self) -> Dict[str, List[str]]:
        """Hataları döndür"""
        return self.errors
    
    def get_warnings(self) -> Dict[str, List[str]]:
        """Uyarıları döndür"""
        return self.warnings
    
    def has_errors(self) -> bool:
        """Hata var mı kontrol et"""
        return not self.is_valid
    
    def has_warnings(self) -> bool:
        """Uyarı var mı kontrol et"""
        return len(self.warnings) > 0
    
    def get_first_error(self) -> Optional[str]:
        """İlk hatayı döndür"""
        for field_errors in self.errors.values():
            if field_errors:
                return field_errors[0]
        return None
    
    def __bool__(self) -> bool:
        """Boolean dönüşümü"""
        return self.is_valid

class BaseService(IService):
    """Tüm servisler için temel sınıf"""
    
    def __init__(self, config_func=None, event_dispatcher: EventDispatcher = None, 
                 validator=None, container: ServiceContainer = None):
        """
        BaseService constructor
        
        Args:
            config_func: Konfigürasyon fonksiyonu
            event_dispatcher: Event dispatcher instance'ı
            validator: Validator instance'ı
            container: Service container instance'ı
        """
        self._config_func = config_func or get_config
        self._event_dispatcher = event_dispatcher or EventDispatcher()
        
        # Validator'ı doğrudan oluşturuyoruz
        if validator is None:
            # Basit bir validator oluştur
            class SimpleValidator:
                def __init__(self):
                    self.errors = {}
                
                def validate(self, data, rules):
                    result = ValidationResult()
                    # Basit validasyon mantığı
                    for field, rule in rules.items():
                        if 'required' in rule and (field not in data or not data[field]):
                            result.add_error(field, f"{field} alanı zorunludur")
                    return result
                
                def get_errors(self):
                    return self.errors
            
            self._validator = SimpleValidator()
        else:
            self._validator = validator
            
        self._container = container or ServiceContainer()
        self._service_name = self.__class__.__name__
        self._started_at = datetime.now()
        self._is_running = False
        
        # Service'i container'a kaydet
        self._register_service()
        
        # Service başlatma event'i gönder
        self._dispatch_service_event(SystemEvents.SERVICE_STARTED)
    
    @staticmethod
    def get_logger():
        """
        Logger instance'ını döndürür
        
        Returns:
            LoggerService: Logger instance'ı
        """
        from core.Services.logger import LoggerService
        return LoggerService.get_logger()
    
    def _register_service(self):
        """Service'i container'a kaydet"""
        try:
            service_name = self._service_name.lower()
            
            # Eğer servis zaten kayıtlıysa tekrar kaydetme
            if self._container.has(service_name):
                return
                
            self._container.register_singleton(service_name, self.__class__)
            self.log(f"Service container'a kaydedildi: {service_name}")
        except Exception as e:
            self.log(f"Service kayıt hatası: {e}", "error")
    
    def _dispatch_service_event(self, event_name: str, data: Dict[str, Any] = None):
        """Service event'i gönder"""
        try:
            event_data = {
                'service_name': self._service_name,
                'timestamp': datetime.now().isoformat(),
                'data': data or {}
            }
            
            event = Event(
                name=event_name,
                data=event_data,
                source=self._service_name
            )
            
            self._event_dispatcher.dispatch(event)
        except Exception as e:
            print(f"Event dispatch hatası: {e}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Config değerini getir
        
        Args:
            key: Yapılandırma anahtarı (dot notation destekler, örn: 'app.name')
            default: Değer bulunamazsa döndürülecek varsayılan değer
            
        Returns:
            Any: Yapılandırma değeri veya varsayılan değer
        """
        try:
            # Yeni config modülü ile uyumlu hale getirme
            config = self._config_func()
            return config.get(key, default)
        except Exception as e:
            self.log(f"Config getirme hatası: {e}", "error")
            return default
    
    def log(self, message: str, level: str = 'info', extra: Optional[Dict] = None):
        """Log mesajı"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_data = {
                'timestamp': timestamp,
                'level': level.upper(),
                'service': self._service_name,
                'message': message,
                'extra': extra or {}
            }
            
            # Log formatını oluştur
            log_message = f"[{timestamp}] [{level.upper()}] [{self._service_name}] {message}"
            
            # Console'a yazdır
            print(log_message)
            
            # Event olarak gönder
            self._dispatch_service_event('service.log', log_data)
            
        except Exception as e:
            print(f"Log yazma hatası: {e}")
    
    def success_response(self, message: str = 'İşlem başarılı', data: Any = None, status: int = 200) -> Dict:
        """Başarılı response"""
        return {
            'status': 'success',
            'message': message,
            'data': data,
            'status_code': status,
            'timestamp': datetime.now().isoformat(),
            'service': self._service_name
        }
    
    def error_response(self, error: str = 'Bir hata oluştu', data: Any = None, status: int = 500) -> Dict:
        """Hata response"""
        error_data = {
            'status': 'error',
            'message': error,
            'data': data,
            'status_code': status,
            'timestamp': datetime.now().isoformat(),
            'service': self._service_name
        }
        
        # Hata event'i gönder
        self._dispatch_service_event(SystemEvents.SERVICE_ERROR, error_data)
        
        return error_data
    
    def handle_exception(self, exception: Exception, custom_message: str = None) -> Dict:
        """
        Exception'ları yönet
        
        Args:
            exception: Exception nesnesi
            custom_message: Özel hata mesajı
            
        Returns:
            Dict: Hata response
        """
        # Exception bilgilerini log'a yaz
        exception_name = exception.__class__.__name__
        exception_message = str(exception)
        
        self.log(f"{exception_name}: {exception_message}", "error", {
            'exception_type': exception_name,
            'traceback': traceback.format_exc()
        })
        
        # Custom message varsa onu kullan, yoksa exception mesajını kullan
        error_message = custom_message or exception_message
        
        return self.error_response(error_message)
    
    def validate_data(self, data: Dict[str, Any], rules: Dict[str, List[str]]) -> ValidationResult:
        """Veri doğrula"""
        try:
            return self._validator.validate(data, rules)
        except Exception as e:
            self.log(f"Validation hatası: {e}", "error")
            result = ValidationResult()
            result.add_error('validation', f"Validation error: {e}")
            return result
    
    def dispatch_event(self, event_name: str, data: Dict[str, Any] = None, 
                      priority: str = 'normal') -> bool:
        """Event gönder"""
        try:
            event = Event(
                name=event_name,
                data=data or {},
                source=self._service_name
            )
            
            return self._event_dispatcher.dispatch(event)
        except Exception as e:
            self.log(f"Event dispatch hatası: {e}", "error")
            return False
    
    def listen_event(self, event_name: str, callback: callable) -> bool:
        """Event dinle"""
        try:
            return self._event_dispatcher.listen_function(event_name, callback)
        except Exception as e:
            self.log(f"Event listener ekleme hatası: {e}", "error")
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """Service bilgilerini getir"""
        return {
            'name': self._service_name,
            'class': self.__class__.__name__,
            'started_at': self._started_at.isoformat(),
            'is_running': self._is_running,
            'uptime': (datetime.now() - self._started_at).total_seconds(),
            'config_sections': ['app', 'database', 'mail', 'cache']  # Sabit liste
        }
    
    def start(self) -> bool:
        """Service'i başlat"""
        try:
            if not self._is_running:
                self._is_running = True
                self.log("Service başlatıldı")
                self._dispatch_service_event(SystemEvents.SERVICE_STARTED)
                return True
            return False
        except Exception as e:
            self.log(f"Service başlatma hatası: {e}", "error")
            return False
    
    def stop(self) -> bool:
        """Service'i durdur"""
        try:
            if self._is_running:
                self._is_running = False
                self.log("Service durduruldu")
                self._dispatch_service_event(SystemEvents.SERVICE_STOPPED)
                return True
            return False
        except Exception as e:
            self.log(f"Service durdurma hatası: {e}", "error")
            return False
    
    def is_running(self) -> bool:
        """Service çalışıyor mu kontrol et"""
        return self._is_running
    
    def get_container(self) -> ServiceContainer:
        """Service container'ı getir"""
        return self._container
    
    def get_event_dispatcher(self) -> EventDispatcher:
        """Event dispatcher'ı getir"""
        return self._event_dispatcher
    
    def get_validator(self) -> ValidationResult:
        """Validator'ı getir"""
        return self._validator
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
        return False  # Exception'ları dışarı çıkar
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self._service_name}(running={self._is_running})"
    
    def __repr__(self) -> str:
        """Representation"""
        return f"<{self.__class__.__name__} name='{self._service_name}' running={self._is_running}>"

# Service dekoratörleri
def service_event(event_name: str):
    """Service event dekoratörü"""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Fonksiyonu çalıştır
            result = func(self, *args, **kwargs)
            
            # Event gönder
            self.dispatch_event(event_name, {
                'function': func.__name__,
                'args': args,
                'kwargs': kwargs,
                'result': result
            })
            
            return result
        return wrapper
    return decorator

def validate_service_input(rules: Dict[str, List[str]]):
    """Service input validation dekoratörü"""
    def decorator(func):
        def wrapper(self, data: Dict[str, Any], *args, **kwargs):
            # Veriyi doğrula
            validation_result = self.validate_data(data, rules)
            
            if validation_result.has_errors():
                return self.error_response(
                    "Validation failed",
                    400,
                    {'errors': validation_result.get_errors()}
                )
            
            # Fonksiyonu çalıştır
            return func(self, data, *args, **kwargs)
        return wrapper
    return decorator

def service_retry(max_attempts: int = 3, delay: float = 1.0):
    """Service retry dekoratörü"""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            import time
            
            for attempt in range(max_attempts):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    
                    self.log(f"Attempt {attempt + 1} failed: {e}, retrying...", "warning")
                    time.sleep(delay)
            
        return wrapper
    return decorator 