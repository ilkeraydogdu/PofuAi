"""
Service Container
Servis konteyneri
"""
from typing import Dict, Any, Optional, Type

class ServiceContainer:
    """
    Servis konteyneri.
    Bu sınıf, servislerin merkezi yönetimini sağlar.
    """
    
    _instances = {}
    _services = {}
    
    def __init__(self):
        """Servis konteynerini başlat"""
        pass
    
    def register(self, name: str, service_class: Type, *args, **kwargs):
        """
        Servis kaydet
        
        Args:
            name (str): Servis adı
            service_class (Type): Servis sınıfı
            *args: Servis sınıfı için argümanlar
            **kwargs: Servis sınıfı için anahtar kelime argümanları
        """
        self._services[name] = {
            'class': service_class,
            'args': args,
            'kwargs': kwargs,
            'singleton': True
        }
    
    def register_singleton(self, name: str, service_class: Type, *args, **kwargs):
        """
        Singleton servis kaydet
        
        Args:
            name (str): Servis adı
            service_class (Type): Servis sınıfı
            *args: Servis sınıfı için argümanlar
            **kwargs: Servis sınıfı için anahtar kelime argümanları
        """
        # Eğer servis zaten kayıtlıysa tekrar kaydetme
        if name in self._services:
            return
            
        self._services[name] = {
            'class': service_class,
            'args': args,
            'kwargs': kwargs,
            'singleton': True
        }
    
    def register_instance(self, name: str, instance: Any):
        """
        Servis örneğini kaydet
        
        Args:
            name (str): Servis adı
            instance (Any): Servis örneği
        """
        self._instances[name] = instance
    
    def get(self, name: str) -> Any:
        """
        Servis al
        
        Args:
            name (str): Servis adı
            
        Returns:
            Any: Servis örneği
        """
        # Eğer servis örneği zaten varsa, onu döndür
        if name in self._instances:
            return self._instances[name]
        
        # Eğer servis tanımı varsa, örneği oluştur
        if name in self._services:
            service = self._services[name]
            instance = service['class'](*service['args'], **service['kwargs'])
            
            # Eğer singleton ise, örneği sakla
            if service['singleton']:
                self._instances[name] = instance
                
            return instance
        
        # Eğer servis tanımı yoksa, dinamik olarak oluşturmayı dene
        try:
            if name == 'ui_service':
                from core.Services.UIService import get_ui_service
                instance = get_ui_service()
                self._instances[name] = instance
                return instance
            elif name == 'component_service':
                from core.Services.ComponentService import ComponentService
                instance = ComponentService()
                self._instances[name] = instance
                return instance
            elif name == 'page_service':
                from core.Services.PageService import PageService
                instance = PageService()
                self._instances[name] = instance
                return instance
            elif name == 'auth_service':
                from core.Services.auth_service import get_auth_service
                instance = get_auth_service()
                self._instances[name] = instance
                return instance
            elif name == 'mail_service':
                from core.Services.mail_service import get_mail_service
                instance = get_mail_service()
                self._instances[name] = instance
                return instance
            elif name == 'cache_service':
                from core.Services.cache_service import get_cache_service
                instance = get_cache_service()
                self._instances[name] = instance
                return instance
            elif name == 'notification_service':
                from core.Services.notification_service import get_notification_service
                instance = get_notification_service()
                self._instances[name] = instance
                return instance
            elif name == 'token_service':
                from core.Services.token_service import get_token_service
                instance = get_token_service()
                self._instances[name] = instance
                return instance
            elif name == 'logger':
                from core.Services.logger import LoggerService
                instance = LoggerService.get_logger()
                self._instances[name] = instance
                return instance
        except ImportError:
            pass
        
        # Servis bulunamadı
        raise KeyError(f"Service not found: {name}")
    
    def has(self, name: str) -> bool:
        """
        Servis var mı kontrolü
        
        Args:
            name (str): Servis adı
            
        Returns:
            bool: Servis varsa True, yoksa False
        """
        return name in self._instances or name in self._services
    
    def remove(self, name: str):
        """
        Servis kaldır
        
        Args:
            name (str): Servis adı
        """
        if name in self._instances:
            del self._instances[name]
            
        if name in self._services:
            del self._services[name] 