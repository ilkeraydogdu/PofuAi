"""
Event System
Event-driven architecture için event dispatcher ve event sistemi
"""

import asyncio
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from .interfaces import IEventDispatcher

class EventPriority(Enum):
    """Event öncelikleri"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Event:
    """Event sınıfı"""
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: EventPriority = EventPriority.NORMAL
    source: str = "system"
    is_propagating: bool = True
    
    def stop_propagation(self):
        """Event yayılımını durdur"""
        self.is_propagating = False

class EventListener:
    """Event listener sınıfı"""
    
    def __init__(self, callback: Callable, priority: EventPriority = EventPriority.NORMAL):
        self.callback = callback
        self.priority = priority
        self.is_async = asyncio.iscoroutinefunction(callback)
    
    async def handle_async(self, event: Event) -> bool:
        """Async event'i işle"""
        try:
            if self.is_async:
                await self.callback(event)
            else:
                self.callback(event)
            return True
        except Exception as e:
            print(f"Event listener hatası: {e}")
            return False
    
    def handle_sync(self, event: Event) -> bool:
        """Sync event'i işle"""
        try:
            if self.is_async:
                # Async callback'i sync context'te çalıştır
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.callback(event))
                finally:
                    loop.close()
            else:
                self.callback(event)
            return True
        except Exception as e:
            print(f"Event listener hatası: {e}")
            return False

class EventDispatcher(IEventDispatcher):
    """Event dispatcher sınıfı"""
    
    def __init__(self):
        self._listeners: Dict[str, List[EventListener]] = {}
        self._wildcard_listeners: List[EventListener] = []
        self._event_history: List[Event] = []
        self._max_history: int = 1000
    
    def dispatch(self, event: Event) -> bool:
        """Event'i dispatch et"""
        try:
            # Event'i geçmişe ekle
            self._add_to_history(event)
            
            # Wildcard listener'ları çalıştır
            for listener in self._wildcard_listeners:
                if not event.is_propagating:
                    break
                listener.handle_sync(event)
            
            # Event'e özel listener'ları çalıştır
            if event.name in self._listeners:
                # Önceliğe göre sırala
                listeners = sorted(
                    self._listeners[event.name],
                    key=lambda x: x.priority.value,
                    reverse=True
                )
                
                for listener in listeners:
                    if not event.is_propagating:
                        break
                    listener.handle_sync(event)
            
            return True
            
        except Exception as e:
            print(f"Event dispatch hatası: {e}")
            return False
    
    async def dispatch_async(self, event: Event) -> bool:
        """Event'i async olarak dispatch et"""
        try:
            # Event'i geçmişe ekle
            self._add_to_history(event)
            
            # Wildcard listener'ları çalıştır
            for listener in self._wildcard_listeners:
                if not event.is_propagating:
                    break
                await listener.handle_async(event)
            
            # Event'e özel listener'ları çalıştır
            if event.name in self._listeners:
                # Önceliğe göre sırala
                listeners = sorted(
                    self._listeners[event.name],
                    key=lambda x: x.priority.value,
                    reverse=True
                )
                
                for listener in listeners:
                    if not event.is_propagating:
                        break
                    await listener.handle_async(event)
            
            return True
            
        except Exception as e:
            print(f"Async event dispatch hatası: {e}")
            return False
    
    def listen(self, event_name: str, listener: EventListener) -> bool:
        """Event listener ekle"""
        try:
            if event_name == "*":
                self._wildcard_listeners.append(listener)
            else:
                if event_name not in self._listeners:
                    self._listeners[event_name] = []
                self._listeners[event_name].append(listener)
            
            return True
        except Exception as e:
            print(f"Event listener ekleme hatası: {e}")
            return False
    
    def listen_function(self, event_name: str, callback: Callable, 
                       priority: EventPriority = EventPriority.NORMAL) -> bool:
        """Fonksiyon listener ekle"""
        listener = EventListener(callback, priority)
        return self.listen(event_name, listener)
    
    def remove_listener(self, event_name: str, listener: EventListener) -> bool:
        """Event listener kaldır"""
        try:
            if event_name == "*":
                if listener in self._wildcard_listeners:
                    self._wildcard_listeners.remove(listener)
            else:
                if event_name in self._listeners and listener in self._listeners[event_name]:
                    self._listeners[event_name].remove(listener)
            
            return True
        except Exception as e:
            print(f"Event listener kaldırma hatası: {e}")
            return False
    
    def remove_all_listeners(self, event_name: str = None) -> bool:
        """Tüm listener'ları kaldır"""
        try:
            if event_name is None:
                self._listeners.clear()
                self._wildcard_listeners.clear()
            else:
                if event_name in self._listeners:
                    del self._listeners[event_name]
            
            return True
        except Exception as e:
            print(f"Tüm listener'ları kaldırma hatası: {e}")
            return False
    
    def get_listeners(self, event_name: str = None) -> List[EventListener]:
        """Listener'ları getir"""
        try:
            if event_name is None:
                all_listeners = []
                for listeners in self._listeners.values():
                    all_listeners.extend(listeners)
                all_listeners.extend(self._wildcard_listeners)
                return all_listeners
            else:
                return self._listeners.get(event_name, [])
        except Exception as e:
            print(f"Listener getirme hatası: {e}")
            return []
    
    def get_event_history(self, event_name: str = None, limit: int = None) -> List[Event]:
        """Event geçmişini getir"""
        try:
            history = self._event_history
            
            if event_name:
                history = [e for e in history if e.name == event_name]
            
            if limit:
                history = history[-limit:]
            
            return history
        except Exception as e:
            print(f"Event geçmişi getirme hatası: {e}")
            return []
    
    def clear_history(self) -> bool:
        """Event geçmişini temizle"""
        try:
            self._event_history.clear()
            return True
        except Exception as e:
            print(f"Event geçmişi temizleme hatası: {e}")
            return False
    
    def _add_to_history(self, event: Event):
        """Event'i geçmişe ekle"""
        self._event_history.append(event)
        
        # Maksimum geçmiş sayısını kontrol et
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
    
    def set_max_history(self, max_history: int):
        """Maksimum geçmiş sayısını ayarla"""
        self._max_history = max_history

# Global event dispatcher
_dispatcher: Optional[EventDispatcher] = None

def get_dispatcher() -> EventDispatcher:
    """Global event dispatcher'ı getir"""
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = EventDispatcher()
    return _dispatcher

def dispatch_event(event: Event) -> bool:
    """Global dispatcher ile event gönder"""
    return get_dispatcher().dispatch(event)

def listen_event(event_name: str, callback: Callable, 
                priority: EventPriority = EventPriority.NORMAL) -> bool:
    """Global dispatcher'a event listener ekle"""
    return get_dispatcher().listen_function(event_name, callback, priority)

# Event dekoratörü
def on_event(event_name: str, priority: EventPriority = EventPriority.NORMAL):
    """Event listener dekoratörü"""
    def decorator(func: Callable) -> Callable:
        listen_event(event_name, func, priority)
        return func
    return decorator

# Önceden tanımlı event'ler
class SystemEvents:
    """Sistem event'leri"""
    SERVICE_STARTED = "service.started"
    SERVICE_STOPPED = "service.stopped"
    SERVICE_ERROR = "service.error"
    
    MAIL_SENT = "mail.sent"
    MAIL_FAILED = "mail.failed"
    
    CACHE_HIT = "cache.hit"
    CACHE_MISS = "cache.miss"
    
    JOB_STARTED = "job.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_FAILED = "notification.failed"
    
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout" 