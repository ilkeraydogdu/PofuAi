"""
Advanced Session and Cookie Management Service
İleri seviye session ve cookie yönetimi
"""
import os
import json
import redis
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from flask import request, session, make_response, current_app
from core.Services.base_service import BaseService
from core.Services.logger import LoggerService
from core.Services.cache_service import CacheService
from dataclasses import dataclass
from enum import Enum
import jwt
import pickle
import gzip
import base64

class SessionType(Enum):
    REGULAR = "regular"
    SECURE = "secure"
    TEMPORARY = "temporary"
    PERSISTENT = "persistent"
    API = "api"

class CookieType(Enum):
    SESSION = "session"
    PREFERENCE = "preference"
    TRACKING = "tracking"
    SECURITY = "security"
    ANALYTICS = "analytics"

@dataclass
class SessionConfig:
    type: SessionType
    lifetime: int  # seconds
    secure: bool = True
    httponly: bool = True
    samesite: str = 'Lax'
    domain: Optional[str] = None
    path: str = '/'
    encrypt: bool = True

@dataclass
class CookieConfig:
    name: str
    type: CookieType
    lifetime: int
    secure: bool = True
    httponly: bool = False
    samesite: str = 'Lax'
    domain: Optional[str] = None
    path: str = '/'
    encrypt: bool = False

class AdvancedSessionService(BaseService):
    """İleri seviye session ve cookie yönetimi"""
    
    def __init__(self):
        super().__init__()
        self.logger = LoggerService.get_logger()
        self.cache = CacheService()
        self.redis_client = self._init_redis()
        self.encryption_key = self._get_encryption_key()
        
        # Session konfigürasyonları
        self.session_configs = {
            SessionType.REGULAR: SessionConfig(
                type=SessionType.REGULAR,
                lifetime=3600,  # 1 saat
                secure=True,
                httponly=True
            ),
            SessionType.SECURE: SessionConfig(
                type=SessionType.SECURE,
                lifetime=1800,  # 30 dakika
                secure=True,
                httponly=True,
                encrypt=True
            ),
            SessionType.TEMPORARY: SessionConfig(
                type=SessionType.TEMPORARY,
                lifetime=300,  # 5 dakika
                secure=True,
                httponly=True
            ),
            SessionType.PERSISTENT: SessionConfig(
                type=SessionType.PERSISTENT,
                lifetime=2592000,  # 30 gün
                secure=True,
                httponly=True,
                encrypt=True
            ),
            SessionType.API: SessionConfig(
                type=SessionType.API,
                lifetime=7200,  # 2 saat
                secure=True,
                httponly=False
            )
        }
        
        # Cookie konfigürasyonları
        self.cookie_configs = {
            'user_preferences': CookieConfig(
                name='user_prefs',
                type=CookieType.PREFERENCE,
                lifetime=2592000,  # 30 gün
                httponly=False,
                encrypt=True
            ),
            'analytics': CookieConfig(
                name='analytics_id',
                type=CookieType.ANALYTICS,
                lifetime=31536000,  # 1 yıl
                httponly=False
            ),
            'security_token': CookieConfig(
                name='csrf_token',
                type=CookieType.SECURITY,
                lifetime=3600,  # 1 saat
                httponly=True,
                secure=True
            )
        }
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Redis bağlantısını başlat"""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()  # Bağlantıyı test et
            return client
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {str(e)}")
            return None
    
    def _get_encryption_key(self) -> bytes:
        """Şifreleme anahtarını al"""
        key = os.getenv('SESSION_ENCRYPTION_KEY')
        if not key:
            key = secrets.token_hex(32)
            self.logger.warning("No encryption key found, generated temporary key")
        return key.encode()[:32]
    
    def create_session(self, user_id: int, session_type: SessionType = SessionType.REGULAR, 
                      data: Dict[str, Any] = None) -> str:
        """Yeni session oluştur"""
        try:
            config = self.session_configs[session_type]
            session_id = self._generate_session_id()
            
            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'type': session_type.value,
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=config.lifetime)).isoformat(),
                'ip_address': request.remote_addr if request else None,
                'user_agent': request.headers.get('User-Agent') if request else None,
                'data': data or {},
                'security': {
                    'fingerprint': self._generate_fingerprint(),
                    'csrf_token': secrets.token_urlsafe(32),
                    'login_attempts': 0,
                    'suspicious_activity': False
                }
            }
            
            # Session'ı kaydet
            self._store_session(session_id, session_data, config)
            
            # Session cookie'sini ayarla
            self._set_session_cookie(session_id, config)
            
            # Activity log
            self._log_session_activity(session_id, 'created', user_id)
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Session creation error: {str(e)}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Session verilerini al"""
        try:
            if not session_id:
                return None
            
            # Redis'ten al
            if self.redis_client:
                session_data = self.redis_client.get(f"session:{session_id}")
                if session_data:
                    data = json.loads(session_data)
                    
                    # Expire kontrolü
                    if self._is_session_expired(data):
                        self.destroy_session(session_id)
                        return None
                    
                    # Activity güncelle
                    self._update_session_activity(session_id, data)
                    
                    return data
            
            # Fallback: Cache'ten al
            session_data = self.cache.get(f"session:{session_id}")
            if session_data:
                if self._is_session_expired(session_data):
                    self.destroy_session(session_id)
                    return None
                
                self._update_session_activity(session_id, session_data)
                return session_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Session retrieval error: {str(e)}")
            return None
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Session verilerini güncelle"""
        try:
            session_data = self.get_session(session_id)
            if not session_data:
                return False
            
            # Veriyi güncelle
            session_data['data'].update(data)
            session_data['last_activity'] = datetime.now().isoformat()
            
            # Kaydet
            config = self.session_configs[SessionType(session_data['type'])]
            self._store_session(session_id, session_data, config)
            
            self._log_session_activity(session_id, 'updated', session_data['user_id'])
            
            return True
            
        except Exception as e:
            self.logger.error(f"Session update error: {str(e)}")
            return False
    
    def destroy_session(self, session_id: str) -> bool:
        """Session'ı yok et"""
        try:
            session_data = self.get_session(session_id)
            if session_data:
                user_id = session_data.get('user_id')
                self._log_session_activity(session_id, 'destroyed', user_id)
            
            # Redis'ten sil
            if self.redis_client:
                self.redis_client.delete(f"session:{session_id}")
            
            # Cache'ten sil
            self.cache.delete(f"session:{session_id}")
            
            # Cookie'yi temizle
            self._clear_session_cookie()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Session destruction error: {str(e)}")
            return False
    
    def set_cookie(self, name: str, value: Any, config_name: str = None, 
                   custom_config: CookieConfig = None) -> bool:
        """Cookie ayarla"""
        try:
            if custom_config:
                config = custom_config
            elif config_name and config_name in self.cookie_configs:
                config = self.cookie_configs[config_name]
            else:
                # Default config
                config = CookieConfig(
                    name=name,
                    type=CookieType.PREFERENCE,
                    lifetime=86400  # 1 gün
                )
            
            # Değeri hazırla
            cookie_value = self._prepare_cookie_value(value, config)
            
            # Response oluştur
            response = make_response()
            response.set_cookie(
                config.name,
                cookie_value,
                max_age=config.lifetime,
                secure=config.secure,
                httponly=config.httponly,
                samesite=config.samesite,
                domain=config.domain,
                path=config.path
            )
            
            # Cookie aktivitesini logla
            self._log_cookie_activity(config.name, 'set', value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cookie setting error: {str(e)}")
            return False
    
    def get_cookie(self, name: str, decrypt: bool = False) -> Optional[Any]:
        """Cookie değerini al"""
        try:
            if not request:
                return None
            
            cookie_value = request.cookies.get(name)
            if not cookie_value:
                return None
            
            # Şifrelenmiş cookie'yi çöz
            if decrypt:
                return self._decrypt_cookie_value(cookie_value)
            
            # JSON parse et
            try:
                return json.loads(cookie_value)
            except json.JSONDecodeError:
                return cookie_value
            
        except Exception as e:
            self.logger.error(f"Cookie retrieval error: {str(e)}")
            return None
    
    def delete_cookie(self, name: str) -> bool:
        """Cookie'yi sil"""
        try:
            response = make_response()
            response.set_cookie(name, '', expires=0)
            
            self._log_cookie_activity(name, 'deleted', None)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cookie deletion error: {str(e)}")
            return False
    
    def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Kullanıcının tüm session'larını al"""
        try:
            sessions = []
            
            if self.redis_client:
                # Redis'ten tüm session'ları tara
                pattern = "session:*"
                for key in self.redis_client.scan_iter(match=pattern):
                    session_data = self.redis_client.get(key)
                    if session_data:
                        data = json.loads(session_data)
                        if data.get('user_id') == user_id:
                            if not self._is_session_expired(data):
                                sessions.append(data)
                            else:
                                # Expired session'ı temizle
                                self.redis_client.delete(key)
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"User sessions retrieval error: {str(e)}")
            return []
    
    def destroy_all_user_sessions(self, user_id: int, except_current: str = None) -> int:
        """Kullanıcının tüm session'larını yok et"""
        try:
            destroyed_count = 0
            sessions = self.get_user_sessions(user_id)
            
            for session_data in sessions:
                session_id = session_data['session_id']
                if except_current and session_id == except_current:
                    continue
                
                if self.destroy_session(session_id):
                    destroyed_count += 1
            
            return destroyed_count
            
        except Exception as e:
            self.logger.error(f"Destroy all sessions error: {str(e)}")
            return 0
    
    def get_session_analytics(self, user_id: int = None, days: int = 30) -> Dict[str, Any]:
        """Session analitikleri"""
        try:
            analytics = {
                'total_sessions': 0,
                'active_sessions': 0,
                'session_types': {},
                'device_types': {},
                'browsers': {},
                'locations': {},
                'daily_activity': {},
                'avg_session_duration': 0,
                'security_events': 0
            }
            
            # Son X günün verilerini analiz et
            start_date = datetime.now() - timedelta(days=days)
            
            # Session loglarını analiz et (örnek implementasyon)
            # Gerçek implementasyonda log tablosundan veri çekilecek
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Session analytics error: {str(e)}")
            return {}
    
    def _generate_session_id(self) -> str:
        """Güvenli session ID oluştur"""
        return secrets.token_urlsafe(32)
    
    def _generate_fingerprint(self) -> str:
        """Browser fingerprint oluştur"""
        if not request:
            return ""
        
        components = [
            request.headers.get('User-Agent', ''),
            request.headers.get('Accept-Language', ''),
            request.headers.get('Accept-Encoding', ''),
            request.remote_addr or '',
        ]
        
        fingerprint_string = '|'.join(components)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()
    
    def _store_session(self, session_id: str, data: Dict[str, Any], config: SessionConfig):
        """Session'ı depola"""
        serialized_data = json.dumps(data, default=str)
        
        if config.encrypt:
            serialized_data = self._encrypt_data(serialized_data)
        
        # Redis'e kaydet
        if self.redis_client:
            self.redis_client.setex(
                f"session:{session_id}",
                config.lifetime,
                serialized_data
            )
        else:
            # Fallback: Cache'e kaydet
            self.cache.set(f"session:{session_id}", data, config.lifetime)
    
    def _set_session_cookie(self, session_id: str, config: SessionConfig):
        """Session cookie'sini ayarla"""
        if not request:
            return
        
        response = make_response()
        response.set_cookie(
            'session_id',
            session_id,
            max_age=config.lifetime,
            secure=config.secure,
            httponly=config.httponly,
            samesite=config.samesite,
            domain=config.domain,
            path=config.path
        )
    
    def _clear_session_cookie(self):
        """Session cookie'sini temizle"""
        response = make_response()
        response.set_cookie('session_id', '', expires=0)
    
    def _is_session_expired(self, session_data: Dict[str, Any]) -> bool:
        """Session'ın süresi dolmuş mu?"""
        try:
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            return datetime.now() > expires_at
        except Exception:
            return True
    
    def _update_session_activity(self, session_id: str, session_data: Dict[str, Any]):
        """Session aktivitesini güncelle"""
        session_data['last_activity'] = datetime.now().isoformat()
        
        # Fingerprint kontrolü
        current_fingerprint = self._generate_fingerprint()
        if session_data['security']['fingerprint'] != current_fingerprint:
            session_data['security']['suspicious_activity'] = True
            self.logger.warning(f"Suspicious activity detected for session {session_id}")
        
        # Güncellemeyi kaydet
        config = self.session_configs[SessionType(session_data['type'])]
        self._store_session(session_id, session_data, config)
    
    def _prepare_cookie_value(self, value: Any, config: CookieConfig) -> str:
        """Cookie değerini hazırla"""
        if isinstance(value, (dict, list)):
            cookie_value = json.dumps(value)
        else:
            cookie_value = str(value)
        
        if config.encrypt:
            cookie_value = self._encrypt_data(cookie_value)
        
        return cookie_value
    
    def _encrypt_data(self, data: str) -> str:
        """Veriyi şifrele"""
        try:
            from cryptography.fernet import Fernet
            key = base64.urlsafe_b64encode(self.encryption_key)
            f = Fernet(key)
            encrypted = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            self.logger.error(f"Encryption error: {str(e)}")
            return data
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Veriyi çöz"""
        try:
            from cryptography.fernet import Fernet
            key = base64.urlsafe_b64encode(self.encryption_key)
            f = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"Decryption error: {str(e)}")
            return encrypted_data
    
    def _decrypt_cookie_value(self, cookie_value: str) -> Any:
        """Şifrelenmiş cookie değerini çöz"""
        decrypted = self._decrypt_data(cookie_value)
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return decrypted
    
    def _log_session_activity(self, session_id: str, action: str, user_id: int = None):
        """Session aktivitesini logla"""
        log_data = {
            'session_id': session_id,
            'action': action,
            'user_id': user_id,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Session activity: {json.dumps(log_data)}")
    
    def _log_cookie_activity(self, cookie_name: str, action: str, value: Any):
        """Cookie aktivitesini logla"""
        log_data = {
            'cookie_name': cookie_name,
            'action': action,
            'has_value': value is not None,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Cookie activity: {json.dumps(log_data)}")