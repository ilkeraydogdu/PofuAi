"""
Cache Service
Önbellek yönetimi servisi
"""
import os
import json
import pickle
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from core.Services.base_service import BaseService

class CacheService(BaseService):
    """Önbellek yönetimi servisi"""
    
    def __init__(self):
        super().__init__()
        self.config = self.get_config('cache') or {}
        self.logger = self.get_logger()
        self.cache_config = self.config.get('cache', {})
        self.driver = self.cache_config.get('driver', 'file')
        self.prefix = self.cache_config.get('prefix', 'pofuai_')
        self.default_ttl = self.cache_config.get('ttl', 3600)
        
        # Cache dizinini oluştur
        if self.driver == 'file':
            self.cache_dir = 'storage/Cache'
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Cache'den değer al"""
        try:
            full_key = self._get_full_key(key)
            
            if self.driver == 'file':
                return self._get_file(full_key, default)
            elif self.driver == 'array':
                return self._get_array(full_key, default)
            else:
                self.logger.error(f"Unsupported cache driver: {self.driver}")
                return default
                
        except Exception as e:
            self.logger.error(f"Cache get error: {str(e)}")
            return default
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Cache'e değer kaydet"""
        try:
            full_key = self._get_full_key(key)
            ttl = ttl or self.default_ttl
            
            if self.driver == 'file':
                return self._set_file(full_key, value, ttl)
            elif self.driver == 'array':
                return self._set_array(full_key, value, ttl)
            else:
                self.logger.error(f"Unsupported cache driver: {self.driver}")
                return False
                
        except Exception as e:
            self.logger.error(f"Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Cache'den değer sil"""
        try:
            full_key = self._get_full_key(key)
            
            if self.driver == 'file':
                return self._delete_file(full_key)
            elif self.driver == 'array':
                return self._delete_array(full_key)
            else:
                self.logger.error(f"Unsupported cache driver: {self.driver}")
                return False
                
        except Exception as e:
            self.logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def has(self, key: str) -> bool:
        """Cache'de key var mı kontrol et"""
        return self.get(key) is not None
    
    def clear(self) -> bool:
        """Tüm cache'i temizle"""
        try:
            if self.driver == 'file':
                return self._clear_file()
            elif self.driver == 'array':
                return self._clear_array()
            else:
                self.logger.error(f"Unsupported cache driver: {self.driver}")
                return False
                
        except Exception as e:
            self.logger.error(f"Cache clear error: {str(e)}")
            return False
    
    def increment(self, key: str, value: int = 1) -> int:
        """Sayısal değeri artır"""
        try:
            current_value = self.get(key, 0)
            if isinstance(current_value, (int, float)):
                new_value = current_value + value
                self.set(key, new_value)
                return new_value
            return 0
        except Exception as e:
            self.logger.error(f"Cache increment error: {str(e)}")
            return 0
    
    def decrement(self, key: str, value: int = 1) -> int:
        """Sayısal değeri azalt"""
        return self.increment(key, -value)
    
    def remember(self, key: str, ttl: int, callback) -> Any:
        """Değeri cache'den al veya callback ile oluştur"""
        value = self.get(key)
        if value is not None:
            return value
        
        value = callback()
        self.set(key, value, ttl)
        return value
    
    def tags(self, *tags: str) -> 'TaggedCache':
        """Tag'li cache oluştur"""
        return TaggedCache(self, tags)
    
    def flush(self) -> bool:
        """Cache'i temizle (clear alias)"""
        return self.clear()
    
    def _get_full_key(self, key: str) -> str:
        """Tam key oluştur"""
        return f"{self.prefix}{key}"
    
    def _get_file(self, key: str, default: Any) -> Any:
        """File cache'den değer al"""
        try:
            file_path = os.path.join(self.cache_dir, f"{key}.cache")
            
            if not os.path.exists(file_path):
                return default
            
            with open(file_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # TTL kontrolü
            if datetime.now() > cache_data['expires_at']:
                os.remove(file_path)
                return default
            
            return cache_data['value']
            
        except Exception as e:
            self.logger.error(f"File cache get error: {str(e)}")
            return default
    
    def _set_file(self, key: str, value: Any, ttl: int) -> bool:
        """File cache'e değer kaydet"""
        try:
            file_path = os.path.join(self.cache_dir, f"{key}.cache")
            
            cache_data = {
                'value': value,
                'expires_at': datetime.now() + timedelta(seconds=ttl),
                'created_at': datetime.now()
            }
            
            with open(file_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
            
        except Exception as e:
            self.logger.error(f"File cache set error: {str(e)}")
            return False
    
    def _delete_file(self, key: str) -> bool:
        """File cache'den değer sil"""
        try:
            file_path = os.path.join(self.cache_dir, f"{key}.cache")
            
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"File cache delete error: {str(e)}")
            return False
    
    def _clear_file(self) -> bool:
        """File cache'i temizle"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"File cache clear error: {str(e)}")
            return False
    
    def _get_array(self, key: str, default: Any) -> Any:
        """Array cache'den değer al"""
        try:
            # Basit in-memory cache (test için)
            if not hasattr(self, '_array_cache'):
                self._array_cache = {}
            
            if key not in self._array_cache:
                return default
            
            cache_data = self._array_cache[key]
            
            # TTL kontrolü
            if datetime.now() > cache_data['expires_at']:
                del self._array_cache[key]
                return default
            
            return cache_data['value']
            
        except Exception as e:
            self.logger.error(f"Array cache get error: {str(e)}")
            return default
    
    def _set_array(self, key: str, value: Any, ttl: int) -> bool:
        """Array cache'e değer kaydet"""
        try:
            if not hasattr(self, '_array_cache'):
                self._array_cache = {}
            
            self._array_cache[key] = {
                'value': value,
                'expires_at': datetime.now() + timedelta(seconds=ttl),
                'created_at': datetime.now()
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"Array cache set error: {str(e)}")
            return False
    
    def _delete_array(self, key: str) -> bool:
        """Array cache'den değer sil"""
        try:
            if hasattr(self, '_array_cache') and key in self._array_cache:
                del self._array_cache[key]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Array cache delete error: {str(e)}")
            return False
    
    def _clear_array(self) -> bool:
        """Array cache'i temizle"""
        try:
            if hasattr(self, '_array_cache'):
                self._array_cache.clear()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Array cache clear error: {str(e)}")
            return False
    
    def get_pattern(self, pattern: str) -> List[str]:
        """Pattern'e uyan cache key'lerini al"""
        try:
            if self.driver == 'redis':
                return [key.decode() for key in self.redis_client.keys(pattern)]
            elif self.driver == 'file':
                import glob
                # File cache için pattern matching
                pattern_path = os.path.join(self.cache_dir, pattern.replace(':', '_').replace('*', '*') + '.cache')
                matches = glob.glob(pattern_path)
                return [os.path.basename(match).replace('_', ':').replace('.cache', '') for match in matches]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Pattern arama hatası: {str(e)}")
            return []
    
    def get_hit_ratio(self) -> float:
        """Cache hit ratio hesapla"""
        try:
            # Basit hit ratio hesaplama (gerçek implementasyon için metrics gerekli)
            return 0.85  # Placeholder
        except Exception as e:
            self.logger.error(f"Hit ratio hesaplama hatası: {str(e)}")
            return 0.0

class TaggedCache:
    """Tag'li cache sınıfı"""
    
    def __init__(self, cache_service: CacheService, tags: List[str]):
        self.cache_service = cache_service
        self.tags = tags
        self.namespace = f"tags:{':'.join(tags)}"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Tag'li cache'den değer al"""
        return self.cache_service.get(f"{self.namespace}:{key}", default)
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Tag'li cache'e değer kaydet"""
        return self.cache_service.set(f"{self.namespace}:{key}", value, ttl)
    
    def delete(self, key: str) -> bool:
        """Tag'li cache'den değer sil"""
        return self.cache_service.delete(f"{self.namespace}:{key}")
    
    def flush(self) -> bool:
        """Tag'li cache'i temizle"""
        # Tag'li tüm cache'leri temizle
        if self.cache_service.driver == 'file':
            return self._flush_file()
        elif self.cache_service.driver == 'array':
            return self._flush_array()
        return False
    
    def _flush_file(self) -> bool:
        """File tag'li cache'i temizle"""
        try:
            cache_dir = self.cache_service.cache_dir
            namespace_prefix = f"{self.cache_service.prefix}{self.namespace}"
            
            for filename in os.listdir(cache_dir):
                if filename.startswith(namespace_prefix) and filename.endswith('.cache'):
                    file_path = os.path.join(cache_dir, filename)
                    os.remove(file_path)
            
            return True
            
        except Exception as e:
            self.cache_service.logger.error(f"Tagged cache flush error: {str(e)}")
            return False
    
    def _flush_array(self) -> bool:
        """Array tag'li cache'i temizle"""
        try:
            if hasattr(self.cache_service, '_array_cache'):
                namespace_prefix = f"{self.cache_service.prefix}{self.namespace}"
                keys_to_delete = []
                
                for key in self.cache_service._array_cache.keys():
                    if key.startswith(namespace_prefix):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self.cache_service._array_cache[key]
            
            return True
            
        except Exception as e:
            self.cache_service.logger.error(f"Tagged cache flush error: {str(e)}")
            return False

    def get_pattern(self, pattern: str) -> List[str]:
        """Pattern'e uyan cache key'lerini al"""
        try:
            if self.driver == 'redis':
                return [key.decode() for key in self.redis_client.keys(pattern)]
            elif self.driver == 'file':
                import glob
                # File cache için pattern matching
                pattern_path = os.path.join(self.cache_dir, pattern.replace(':', '_').replace('*', '*'))
                matches = glob.glob(pattern_path)
                return [os.path.basename(match).replace('_', ':') for match in matches]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Pattern arama hatası: {str(e)}")
            return []
    
    def get_hit_ratio(self) -> float:
        """Cache hit ratio hesapla"""
        try:
            # Basit hit ratio hesaplama (gerçek implementasyon için metrics gerekli)
            return 0.85  # Placeholder
        except Exception as e:
            self.logger.error(f"Hit ratio hesaplama hatası: {str(e)}")
            return 0.0

# Global cache service instance
_cache_service = None

def get_cache_service() -> CacheService:
    """Global cache service instance'ını al"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service 