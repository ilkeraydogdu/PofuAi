"""
Advanced Security Service
Kapsamlı güvenlik yönetimi
"""
import os
import re
import json
import hashlib
import secrets
import time
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from flask import request, session, current_app
from core.Services.base_service import BaseService
from core.Services.logger import LoggerService
from core.Services.cache_service import CacheService
from core.Database.connection import get_connection
from dataclasses import dataclass
from enum import Enum
import bcrypt
import jwt
from cryptography.fernet import Fernet
import base64
import bleach
from urllib.parse import urlparse
import user_agents

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDoS = "ddos"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MALICIOUS_FILE = "malicious_file"
    BOT_ACTIVITY = "bot_activity"

@dataclass
class SecurityEvent:
    event_type: ThreatType
    severity: SecurityLevel
    ip_address: str
    user_agent: str
    timestamp: datetime
    details: Dict[str, Any]
    user_id: Optional[int] = None
    blocked: bool = False

@dataclass
class RateLimitRule:
    endpoint: str
    max_requests: int
    window_seconds: int
    block_duration: int = 300  # 5 dakika
    whitelist_ips: List[str] = None

class SecurityService(BaseService):
    """Kapsamlı güvenlik yönetimi"""
    
    def __init__(self):
        super().__init__()
        self.logger = LoggerService.get_logger()
        self.cache = CacheService()
        self.connection = get_connection()
        self.encryption_key = self._get_encryption_key()
        
        # Güvenlik kuralları
        self.rate_limits = self._load_rate_limit_rules()
        self.blocked_ips = self._load_blocked_ips()
        self.suspicious_patterns = self._load_suspicious_patterns()
        self.allowed_file_types = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
    def _get_encryption_key(self) -> bytes:
        """Şifreleme anahtarını al"""
        key = os.getenv('SECURITY_ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key().decode()
            self.logger.warning("No security encryption key found, generated temporary key")
        return key.encode() if isinstance(key, str) else key
    
    def check_request_security(self, endpoint: str = None) -> Dict[str, Any]:
        """Request güvenlik kontrolü"""
        try:
            if not request:
                return {'allowed': True, 'reason': 'No request context'}
            
            ip_address = self._get_client_ip()
            user_agent = request.headers.get('User-Agent', '')
            endpoint = endpoint or request.endpoint or request.path
            
            security_result = {
                'allowed': True,
                'blocked_reason': None,
                'security_score': 100,
                'threats_detected': [],
                'recommendations': []
            }
            
            # IP blacklist kontrolü
            if self._is_ip_blocked(ip_address):
                security_result['allowed'] = False
                security_result['blocked_reason'] = 'IP address is blocked'
                self._log_security_event(ThreatType.SUSPICIOUS_ACTIVITY, SecurityLevel.HIGH, 
                                        {'reason': 'Blocked IP access attempt'})
                return security_result
            
            # Rate limiting kontrolü
            rate_limit_result = self._check_rate_limit(endpoint, ip_address)
            if not rate_limit_result['allowed']:
                security_result['allowed'] = False
                security_result['blocked_reason'] = 'Rate limit exceeded'
                security_result['security_score'] -= 30
                
            # Bot detection
            bot_score = self._detect_bot_activity(user_agent, ip_address)
            if bot_score > 0.8:
                security_result['security_score'] -= 40
                security_result['threats_detected'].append('High bot probability')
                
            # Suspicious patterns
            suspicious_score = self._check_suspicious_patterns()
            if suspicious_score > 0.7:
                security_result['security_score'] -= 30
                security_result['threats_detected'].append('Suspicious request patterns')
            
            # SQL Injection detection
            if self._detect_sql_injection():
                security_result['security_score'] -= 50
                security_result['threats_detected'].append('SQL injection attempt')
                self._log_security_event(ThreatType.SQL_INJECTION, SecurityLevel.CRITICAL,
                                        {'payload': str(request.args) + str(request.form)})
            
            # XSS detection
            if self._detect_xss():
                security_result['security_score'] -= 40
                security_result['threats_detected'].append('XSS attempt')
                self._log_security_event(ThreatType.XSS, SecurityLevel.HIGH,
                                        {'payload': str(request.args) + str(request.form)})
            
            # CSRF token kontrolü
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                if not self._verify_csrf_token():
                    security_result['security_score'] -= 60
                    security_result['threats_detected'].append('Missing or invalid CSRF token')
            
            # Genel güvenlik skoru değerlendirmesi
            if security_result['security_score'] < 50:
                security_result['allowed'] = False
                security_result['blocked_reason'] = 'Low security score'
            
            return security_result
            
        except Exception as e:
            self.logger.error(f"Security check error: {str(e)}")
            return {'allowed': True, 'reason': 'Security check failed'}
    
    def validate_file_upload(self, file) -> Dict[str, Any]:
        """Dosya yükleme güvenlik kontrolü"""
        try:
            result = {
                'safe': True,
                'issues': [],
                'sanitized_filename': None
            }
            
            if not file or not file.filename:
                result['safe'] = False
                result['issues'].append('No file provided')
                return result
            
            # Dosya boyutu kontrolü
            file.seek(0, 2)  # Dosya sonuna git
            file_size = file.tell()
            file.seek(0)  # Başa dön
            
            if file_size > self.max_file_size:
                result['safe'] = False
                result['issues'].append(f'File too large: {file_size} bytes')
            
            # Dosya uzantısı kontrolü
            filename = file.filename.lower()
            file_ext = filename.split('.')[-1] if '.' in filename else ''
            
            if file_ext not in self.allowed_file_types:
                result['safe'] = False
                result['issues'].append(f'File type not allowed: {file_ext}')
            
            # Dosya adı sanitization
            safe_filename = self._sanitize_filename(filename)
            result['sanitized_filename'] = safe_filename
            
            # Dosya içeriği analizi
            file_content = file.read(1024)  # İlk 1KB'ı oku
            file.seek(0)  # Başa dön
            
            # Malicious content detection
            if self._detect_malicious_content(file_content, file_ext):
                result['safe'] = False
                result['issues'].append('Malicious content detected')
                self._log_security_event(ThreatType.MALICIOUS_FILE, SecurityLevel.HIGH,
                                        {'filename': filename, 'size': file_size})
            
            return result
            
        except Exception as e:
            self.logger.error(f"File validation error: {str(e)}")
            return {'safe': False, 'issues': ['Validation failed']}
    
    def sanitize_input(self, data: Union[str, Dict, List], input_type: str = 'html') -> Any:
        """Input sanitization"""
        try:
            if isinstance(data, str):
                return self._sanitize_string(data, input_type)
            elif isinstance(data, dict):
                return {key: self.sanitize_input(value, input_type) for key, value in data.items()}
            elif isinstance(data, list):
                return [self.sanitize_input(item, input_type) for item in data]
            else:
                return data
                
        except Exception as e:
            self.logger.error(f"Input sanitization error: {str(e)}")
            return data
    
    def _sanitize_string(self, text: str, input_type: str) -> str:
        """String sanitization"""
        if not text:
            return text
        
        if input_type == 'html':
            # HTML sanitization
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'img']
            allowed_attributes = {
                'a': ['href', 'title'],
                'img': ['src', 'alt', 'width', 'height']
            }
            return bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes)
        
        elif input_type == 'sql':
            # SQL injection prevention
            dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
            for char in dangerous_chars:
                text = text.replace(char, '')
            return text
        
        elif input_type == 'filename':
            return self._sanitize_filename(text)
        
        elif input_type == 'url':
            return self._sanitize_url(text)
        
        else:
            # Genel sanitization
            return re.sub(r'[<>"\'\&]', '', text)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Dosya adı sanitization"""
        # Tehlikeli karakterleri kaldır
        filename = re.sub(r'[^\w\-_\.]', '', filename)
        
        # Uzunluk sınırı
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
        
        # Boş veya sadece nokta olan dosya adlarını önle
        if not filename or filename.startswith('.'):
            filename = 'file_' + secrets.token_hex(4) + filename
        
        return filename
    
    def _sanitize_url(self, url: str) -> str:
        """URL sanitization"""
        try:
            parsed = urlparse(url)
            
            # Sadece HTTP/HTTPS protokollerine izin ver
            if parsed.scheme not in ['http', 'https']:
                return ''
            
            # Tehlikeli karakterleri kaldır
            safe_url = re.sub(r'[<>"\'\&]', '', url)
            
            return safe_url
            
        except Exception:
            return ''
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Hassas veri şifreleme"""
        try:
            f = Fernet(base64.urlsafe_b64encode(self.encryption_key[:32]))
            encrypted = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            self.logger.error(f"Encryption error: {str(e)}")
            return data
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Hassas veri şifre çözme"""
        try:
            f = Fernet(base64.urlsafe_b64encode(self.encryption_key[:32]))
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"Decryption error: {str(e)}")
            return encrypted_data
    
    def hash_password(self, password: str) -> str:
        """Şifre hash'leme"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Şifre doğrulama"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            self.logger.error(f"Password verification error: {str(e)}")
            return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Güvenli token oluşturma"""
        return secrets.token_urlsafe(length)
    
    def generate_csrf_token(self) -> str:
        """CSRF token oluşturma"""
        token = secrets.token_urlsafe(32)
        
        # Session'a kaydet
        if 'csrf_tokens' not in session:
            session['csrf_tokens'] = []
        
        session['csrf_tokens'].append({
            'token': token,
            'created_at': time.time()
        })
        
        # Eski token'ları temizle (1 saatten eski)
        current_time = time.time()
        session['csrf_tokens'] = [
            t for t in session['csrf_tokens']
            if current_time - t['created_at'] < 3600
        ]
        
        return token
    
    def _verify_csrf_token(self) -> bool:
        """CSRF token doğrulama"""
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        
        if not token:
            return False
        
        csrf_tokens = session.get('csrf_tokens', [])
        current_time = time.time()
        
        for csrf_token in csrf_tokens:
            if (csrf_token['token'] == token and 
                current_time - csrf_token['created_at'] < 3600):
                return True
        
        return False
    
    def _get_client_ip(self) -> str:
        """Gerçek client IP'sini al"""
        # Proxy arkasında çalışıyorsa
        forwarded_ips = request.headers.get('X-Forwarded-For')
        if forwarded_ips:
            return forwarded_ips.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr or '127.0.0.1'
    
    def _is_ip_blocked(self, ip_address: str) -> bool:
        """IP bloke edilmiş mi?"""
        try:
            # Cache'ten kontrol et
            cache_key = f"blocked_ip_{ip_address}"
            if self.cache.get(cache_key):
                return True
            
            # Database'den kontrol et
            query = """
            SELECT COUNT(*) as count FROM blocked_ips 
            WHERE ip_address = %s AND (expires_at IS NULL OR expires_at > NOW())
            """
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, [ip_address])
            result = cursor.fetchone()
            
            is_blocked = result['count'] > 0
            
            # Cache'e kaydet
            if is_blocked:
                self.cache.set(cache_key, True, 300)  # 5 dakika
            
            return is_blocked
            
        except Exception as e:
            self.logger.error(f"IP block check error: {str(e)}")
            return False
    
    def _check_rate_limit(self, endpoint: str, ip_address: str) -> Dict[str, Any]:
        """Rate limit kontrolü"""
        try:
            # Endpoint için kural bul
            rule = None
            for pattern, limit_rule in self.rate_limits.items():
                if re.match(pattern, endpoint):
                    rule = limit_rule
                    break
            
            if not rule:
                return {'allowed': True, 'remaining': None}
            
            # Whitelist kontrolü
            if rule.whitelist_ips and ip_address in rule.whitelist_ips:
                return {'allowed': True, 'remaining': None}
            
            # Cache key
            cache_key = f"rate_limit_{endpoint}_{ip_address}"
            
            # Mevcut request sayısını al
            current_requests = self.cache.get(cache_key) or 0
            
            if current_requests >= rule.max_requests:
                # Block süresi kontrolü
                block_key = f"rate_limit_block_{ip_address}"
                if not self.cache.get(block_key):
                    self.cache.set(block_key, True, rule.block_duration)
                    self._log_security_event(ThreatType.DDoS, SecurityLevel.MEDIUM,
                                            {'endpoint': endpoint, 'requests': current_requests})
                
                return {'allowed': False, 'remaining': 0}
            
            # Request sayısını artır
            self.cache.set(cache_key, current_requests + 1, rule.window_seconds)
            
            return {
                'allowed': True,
                'remaining': rule.max_requests - current_requests - 1
            }
            
        except Exception as e:
            self.logger.error(f"Rate limit check error: {str(e)}")
            return {'allowed': True, 'remaining': None}
    
    def _detect_bot_activity(self, user_agent: str, ip_address: str) -> float:
        """Bot aktivitesi detection"""
        bot_score = 0.0
        
        try:
            # User agent analizi
            if user_agent:
                ua = user_agents.parse(user_agent)
                
                # Bilinen bot'lar
                if ua.is_bot:
                    bot_score += 0.9
                
                # Şüpheli user agent'lar
                suspicious_ua_patterns = [
                    r'bot', r'crawler', r'spider', r'scraper',
                    r'python', r'curl', r'wget', r'http'
                ]
                
                for pattern in suspicious_ua_patterns:
                    if re.search(pattern, user_agent.lower()):
                        bot_score += 0.3
                        break
            else:
                # User agent yok
                bot_score += 0.5
            
            # Request frequency analizi
            frequency_key = f"request_frequency_{ip_address}"
            request_times = self.cache.get(frequency_key) or []
            
            current_time = time.time()
            # Son 1 dakikadaki request'leri say
            recent_requests = [t for t in request_times if current_time - t < 60]
            
            if len(recent_requests) > 30:  # Dakikada 30'dan fazla request
                bot_score += 0.4
            
            # Request time'ı ekle
            recent_requests.append(current_time)
            self.cache.set(frequency_key, recent_requests[-50:], 300)  # Son 50 request'i tut
            
            return min(bot_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Bot detection error: {str(e)}")
            return 0.0
    
    def _detect_sql_injection(self) -> bool:
        """SQL injection detection"""
        try:
            # SQL injection pattern'leri
            sql_patterns = [
                r"(\bUNION\b.*\bSELECT\b)",
                r"(\bSELECT\b.*\bFROM\b.*\bWHERE\b)",
                r"(\bINSERT\b.*\bINTO\b.*\bVALUES\b)",
                r"(\bDELETE\b.*\bFROM\b.*\bWHERE\b)",
                r"(\bDROP\b.*\bTABLE\b)",
                r"(\bEXEC\b.*\bxp_cmdshell\b)",
                r"(';.*--)",
                r"(\bOR\b.*=.*)",
                r"(\bAND\b.*=.*)",
                r"(1=1|1=0)",
                r"(\bHAVING\b.*\bCOUNT\b)",
                r"(\bWAITFOR\b.*\bDELAY\b)"
            ]
            
            # Tüm input'ları kontrol et
            inputs_to_check = []
            
            # URL parametreleri
            for key, value in request.args.items():
                inputs_to_check.append(f"{key}={value}")
            
            # Form data
            for key, value in request.form.items():
                inputs_to_check.append(f"{key}={value}")
            
            # JSON data
            if request.is_json:
                try:
                    json_data = request.get_json()
                    inputs_to_check.append(str(json_data))
                except:
                    pass
            
            # Pattern matching
            for input_data in inputs_to_check:
                for pattern in sql_patterns:
                    if re.search(pattern, input_data, re.IGNORECASE):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"SQL injection detection error: {str(e)}")
            return False
    
    def _detect_xss(self) -> bool:
        """XSS detection"""
        try:
            # XSS pattern'leri
            xss_patterns = [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"<object[^>]*>",
                r"<embed[^>]*>",
                r"<link[^>]*>",
                r"<meta[^>]*>",
                r"eval\s*\(",
                r"expression\s*\(",
                r"vbscript:",
                r"data:text/html"
            ]
            
            # Tüm input'ları kontrol et
            inputs_to_check = []
            
            for key, value in request.args.items():
                inputs_to_check.append(value)
            
            for key, value in request.form.items():
                inputs_to_check.append(value)
            
            if request.is_json:
                try:
                    json_data = request.get_json()
                    inputs_to_check.append(str(json_data))
                except:
                    pass
            
            # Pattern matching
            for input_data in inputs_to_check:
                for pattern in xss_patterns:
                    if re.search(pattern, input_data, re.IGNORECASE):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"XSS detection error: {str(e)}")
            return False
    
    def _check_suspicious_patterns(self) -> float:
        """Şüpheli pattern kontrolü"""
        suspicion_score = 0.0
        
        try:
            # Path traversal
            if '../' in request.path or '..\\' in request.path:
                suspicion_score += 0.8
            
            # Uzun URL'ler
            if len(request.url) > 2000:
                suspicion_score += 0.3
            
            # Çok fazla parametre
            if len(request.args) > 50:
                suspicion_score += 0.4
            
            # Binary data in parameters
            for value in request.args.values():
                try:
                    value.encode('ascii')
                except UnicodeEncodeError:
                    suspicion_score += 0.2
                    break
            
            return min(suspicion_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Suspicious pattern check error: {str(e)}")
            return 0.0
    
    def _detect_malicious_content(self, content: bytes, file_ext: str) -> bool:
        """Malicious content detection"""
        try:
            # File signature kontrolü
            malicious_signatures = {
                # Executable files
                b'\x4d\x5a': 'exe',  # MZ header
                b'\x7f\x45\x4c\x46': 'elf',  # ELF header
                
                # Script files in images
                b'<?php': 'php',
                b'<script': 'script',
                b'javascript:': 'js',
            }
            
            content_lower = content.lower()
            
            for signature, file_type in malicious_signatures.items():
                if signature in content_lower:
                    return True
            
            # Image dosyalarında script kontrolü
            if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
                script_patterns = [b'<script', b'javascript:', b'<?php', b'<%']
                for pattern in script_patterns:
                    if pattern in content_lower:
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Malicious content detection error: {str(e)}")
            return False
    
    def _log_security_event(self, threat_type: ThreatType, severity: SecurityLevel, 
                           details: Dict[str, Any]):
        """Güvenlik olayını logla"""
        try:
            event = SecurityEvent(
                event_type=threat_type,
                severity=severity,
                ip_address=self._get_client_ip(),
                user_agent=request.headers.get('User-Agent', '') if request else '',
                timestamp=datetime.now(),
                details=details,
                user_id=session.get('user_id') if session else None
            )
            
            # Log'a yaz
            self.logger.warning(f"Security Event: {event}")
            
            # Critical events için immediate action
            if severity == SecurityLevel.CRITICAL:
                self._handle_critical_security_event(event)
            
        except Exception as e:
            self.logger.error(f"Security event logging error: {str(e)}")
    
    def _handle_critical_security_event(self, event: SecurityEvent):
        """Critical güvenlik olayı işleme"""
        try:
            # IP'yi geçici olarak blokla
            self._temporary_ip_block(event.ip_address, 3600)  # 1 saat
            
            # Admin'e bildirim gönder (email, SMS vb.)
            # Bu kısım notification service ile entegre edilecek
            
        except Exception as e:
            self.logger.error(f"Critical security event handling error: {str(e)}")
    
    def _temporary_ip_block(self, ip_address: str, duration: int):
        """Geçici IP blokla"""
        cache_key = f"blocked_ip_{ip_address}"
        self.cache.set(cache_key, True, duration)
    
    def _load_rate_limit_rules(self) -> Dict[str, RateLimitRule]:
        """Rate limit kurallarını yükle"""
        # Varsayılan kurallar
        return {
            r'/api/.*': RateLimitRule('/api/', 100, 60),  # API: 100 req/min
            r'/auth/login': RateLimitRule('/auth/login', 5, 300),  # Login: 5 req/5min
            r'/auth/register': RateLimitRule('/auth/register', 3, 3600),  # Register: 3 req/hour
            r'.*': RateLimitRule('default', 1000, 60)  # Default: 1000 req/min
        }
    
    def _load_blocked_ips(self) -> List[str]:
        """Bloklu IP'leri yükle"""
        try:
            query = "SELECT ip_address FROM blocked_ips WHERE expires_at IS NULL OR expires_at > NOW()"
            cursor = self.connection.cursor()
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []
    
    def _load_suspicious_patterns(self) -> List[str]:
        """Şüpheli pattern'leri yükle"""
        return [
            r'\.\./',  # Path traversal
            r'<script',  # XSS
            r'union.*select',  # SQL injection
            r'exec.*xp_cmdshell',  # Command injection
        ]