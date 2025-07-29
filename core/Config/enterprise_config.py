"""
Enterprise Configuration Management System
Kurumsal seviye konfigürasyon yönetimi

Özellikler:
- Environment-based configuration
- Secure credential management
- Configuration validation
- Hot-reload support
- Multi-environment support
- Configuration encryption
- Audit logging
- Configuration versioning
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from cryptography.fernet import Fernet
import hashlib
from datetime import datetime
import threading


class Environment(Enum):
    """Ortam türleri"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ConfigFormat(Enum):
    """Konfigürasyon formatları"""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"


@dataclass
class DatabaseConfig:
    """Veritabanı konfigürasyonu"""
    driver: str = "mysql"
    host: str = "localhost"
    port: int = 3306
    database: str = "prapazar_enterprise"
    username: str = "root"
    password: str = ""
    charset: str = "utf8mb4"
    collation: str = "utf8mb4_unicode_ci"
    pool_size: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    ssl_mode: str = "PREFERRED"
    ssl_ca: Optional[str] = None
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    backup_enabled: bool = True
    backup_interval: int = 86400  # 24 hours
    backup_retention: int = 7  # days


@dataclass
class RedisConfig:
    """Redis konfigürasyonu"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    database: int = 0
    ssl: bool = False
    ssl_cert_reqs: str = "required"
    ssl_ca_certs: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    max_connections: int = 100
    retry_on_timeout: bool = True
    health_check_interval: int = 30


@dataclass
class SecurityConfig:
    """Güvenlik konfigürasyonu"""
    secret_key: str = "change-this-super-secret-key-in-production"
    jwt_secret: str = "change-this-jwt-secret-key-in-production"
    jwt_expiration: int = 3600  # seconds
    jwt_refresh_expiration: int = 604800  # 7 days
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = True
    max_login_attempts: int = 5
    login_lockout_duration: int = 900  # 15 minutes
    session_timeout: int = 3600  # 1 hour
    csrf_protection: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # 1 hour
    encryption_key: Optional[str] = None


@dataclass
class LoggingConfig:
    """Logging konfigürasyonu"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "logs/enterprise.log"
    file_max_size: int = 10485760  # 10MB
    file_backup_count: int = 5
    console_enabled: bool = True
    syslog_enabled: bool = False
    syslog_host: str = "localhost"
    syslog_port: int = 514
    json_format: bool = False
    include_caller: bool = True
    audit_enabled: bool = True
    audit_file: str = "logs/audit.log"


@dataclass
class MonitoringConfig:
    """Monitoring konfigürasyonu"""
    enabled: bool = True
    metrics_enabled: bool = True
    health_check_enabled: bool = True
    health_check_interval: int = 60  # seconds
    prometheus_enabled: bool = False
    prometheus_port: int = 9090
    grafana_enabled: bool = False
    grafana_url: str = "http://localhost:3000"
    alerting_enabled: bool = True
    alert_email: str = "admin@prapazar.com"
    alert_webhook: Optional[str] = None
    uptime_threshold: float = 99.9  # percentage
    response_time_threshold: int = 2000  # milliseconds


@dataclass
class IntegrationConfig:
    """Entegrasyon konfigürasyonu"""
    enabled: bool = True
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 300
    rate_limiting_enabled: bool = True
    caching_enabled: bool = True
    cache_ttl: int = 300
    webhook_enabled: bool = True
    webhook_timeout: int = 10
    batch_processing: bool = True
    batch_size: int = 100
    parallel_processing: bool = True
    max_workers: int = 10


@dataclass
class EmailConfig:
    """Email konfigürasyonu"""
    driver: str = "smtp"
    host: str = "smtp.gmail.com"
    port: int = 587
    username: str = ""
    password: str = ""
    encryption: str = "tls"
    from_address: str = "noreply@prapazar.com"
    from_name: str = "PraPazar Enterprise"
    timeout: int = 30
    max_retries: int = 3
    templates_path: str = "templates/emails"
    queue_enabled: bool = True
    queue_driver: str = "redis"


@dataclass
class StorageConfig:
    """Depolama konfigürasyonu"""
    driver: str = "local"
    local_path: str = "storage"
    public_path: str = "public/uploads"
    url_prefix: str = "/uploads"
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: List[str] = field(default_factory=lambda: [
        ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx"
    ])
    aws_enabled: bool = False
    aws_bucket: str = ""
    aws_region: str = "us-east-1"
    aws_access_key: str = ""
    aws_secret_key: str = ""
    cdn_enabled: bool = False
    cdn_url: str = ""


@dataclass
class EnterpriseConfig:
    """Ana kurumsal konfigürasyon"""
    app_name: str = "PraPazar Enterprise"
    app_version: str = "1.0.0"
    app_description: str = "Enterprise E-commerce Integration Platform"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    timezone: str = "Europe/Istanbul"
    locale: str = "tr_TR"
    url: str = "http://localhost:5000"
    
    # Alt konfigürasyonlar
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    # Ek ayarlar
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class ConfigValidator:
    """Konfigürasyon doğrulayıcı"""
    
    @staticmethod
    def validate_database_config(config: DatabaseConfig) -> List[str]:
        """Veritabanı konfigürasyonunu doğrula"""
        errors = []
        
        if not config.host:
            errors.append("Database host is required")
        
        if not config.database:
            errors.append("Database name is required")
        
        if config.port < 1 or config.port > 65535:
            errors.append("Database port must be between 1 and 65535")
        
        if config.pool_size < 1:
            errors.append("Database pool size must be at least 1")
        
        return errors
    
    @staticmethod
    def validate_security_config(config: SecurityConfig) -> List[str]:
        """Güvenlik konfigürasyonunu doğrula"""
        errors = []
        
        if len(config.secret_key) < 32:
            errors.append("Secret key must be at least 32 characters long")
        
        if len(config.jwt_secret) < 32:
            errors.append("JWT secret must be at least 32 characters long")
        
        if config.jwt_expiration < 300:  # 5 minutes
            errors.append("JWT expiration must be at least 300 seconds")
        
        if config.password_min_length < 6:
            errors.append("Password minimum length must be at least 6")
        
        return errors
    
    @staticmethod
    def validate_config(config: EnterpriseConfig) -> List[str]:
        """Tüm konfigürasyonu doğrula"""
        errors = []
        
        # Database validation
        errors.extend(ConfigValidator.validate_database_config(config.database))
        
        # Security validation
        errors.extend(ConfigValidator.validate_security_config(config.security))
        
        # App validation
        if not config.app_name:
            errors.append("App name is required")
        
        if not config.url:
            errors.append("App URL is required")
        
        return errors


class ConfigEncryption:
    """Konfigürasyon şifreleme"""
    
    def __init__(self, key: Optional[str] = None):
        if key:
            self.cipher_suite = Fernet(key.encode())
        else:
            self.cipher_suite = Fernet(Fernet.generate_key())
    
    def encrypt_value(self, value: str) -> str:
        """Değeri şifrele"""
        return self.cipher_suite.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Değeri çöz"""
        return self.cipher_suite.decrypt(encrypted_value.encode()).decode()
    
    def encrypt_config_dict(self, config_dict: Dict[str, Any], 
                           sensitive_keys: List[str]) -> Dict[str, Any]:
        """Konfigürasyon sözlüğündeki hassas değerleri şifrele"""
        encrypted_config = config_dict.copy()
        
        for key in sensitive_keys:
            if key in encrypted_config and isinstance(encrypted_config[key], str):
                encrypted_config[key] = self.encrypt_value(encrypted_config[key])
        
        return encrypted_config


class EnterpriseConfigManager:
    """Kurumsal konfigürasyon yöneticisi"""
    
    def __init__(self, config_dir: str = None, environment: Environment = None):
        self.config_dir = Path(config_dir or "config")
        self.environment = environment or Environment.DEVELOPMENT
        self.config: Optional[EnterpriseConfig] = None
        self.encryption: Optional[ConfigEncryption] = None
        self.logger = logging.getLogger("ConfigManager")
        self._lock = threading.RLock()
        self._watchers = []
        self._last_modified = {}
        
        # Konfigürasyon dizinini oluştur
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Logging ayarla
        self._setup_logging()
    
    def _setup_logging(self):
        """Logging ayarlarını yap"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def load_config(self, config_path: Optional[str] = None) -> EnterpriseConfig:
        """Konfigürasyonu yükle"""
        with self._lock:
            if config_path:
                config_file = Path(config_path)
            else:
                config_file = self.config_dir / f"{self.environment.value}.json"
            
            if config_file.exists():
                self.config = self._load_from_file(config_file)
            else:
                self.config = self._create_default_config()
                self.save_config(config_file)
            
            # Environment variables ile override
            self._apply_environment_overrides()
            
            # Validation
            errors = ConfigValidator.validate_config(self.config)
            if errors:
                self.logger.warning(f"Configuration validation errors: {errors}")
            
            self.logger.info(f"Configuration loaded for environment: {self.environment.value}")
            return self.config
    
    def _load_from_file(self, config_file: Path) -> EnterpriseConfig:
        """Dosyadan konfigürasyon yükle"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() == '.json':
                    data = json.load(f)
                elif config_file.suffix.lower() in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported config format: {config_file.suffix}")
            
            # Nested dataclass oluştur
            return self._dict_to_config(data)
            
        except Exception as e:
            self.logger.error(f"Error loading config from {config_file}: {e}")
            return self._create_default_config()
    
    def _dict_to_config(self, data: Dict[str, Any]) -> EnterpriseConfig:
        """Dictionary'yi EnterpriseConfig'e dönüştür"""
        config = EnterpriseConfig()
        
        # Ana alanları ayarla
        for key, value in data.items():
            if hasattr(config, key):
                if key == 'environment':
                    setattr(config, key, Environment(value))
                elif key in ['database', 'redis', 'security', 'logging', 
                           'monitoring', 'integration', 'email', 'storage']:
                    # Alt konfigürasyon objelerini oluştur
                    sub_config_class = getattr(config, key).__class__
                    sub_config = sub_config_class(**value) if isinstance(value, dict) else value
                    setattr(config, key, sub_config)
                else:
                    setattr(config, key, value)
        
        return config
    
    def _create_default_config(self) -> EnterpriseConfig:
        """Varsayılan konfigürasyon oluştur"""
        config = EnterpriseConfig()
        config.environment = self.environment
        
        # Environment'a göre ayarlamaları yap
        if self.environment == Environment.PRODUCTION:
            config.debug = False
            config.security.cors_origins = []  # Production'da CORS kısıtla
            config.logging.level = "WARNING"
            config.database.ssl_mode = "REQUIRED"
        elif self.environment == Environment.DEVELOPMENT:
            config.debug = True
            config.logging.level = "DEBUG"
            config.monitoring.enabled = False
        
        return config
    
    def _apply_environment_overrides(self):
        """Environment variables ile konfigürasyonu override et"""
        if not self.config:
            return
        
        # Database overrides
        if os.getenv('DB_HOST'):
            self.config.database.host = os.getenv('DB_HOST')
        if os.getenv('DB_PORT'):
            self.config.database.port = int(os.getenv('DB_PORT'))
        if os.getenv('DB_NAME'):
            self.config.database.database = os.getenv('DB_NAME')
        if os.getenv('DB_USER'):
            self.config.database.username = os.getenv('DB_USER')
        if os.getenv('DB_PASSWORD'):
            self.config.database.password = os.getenv('DB_PASSWORD')
        
        # Redis overrides
        if os.getenv('REDIS_HOST'):
            self.config.redis.host = os.getenv('REDIS_HOST')
        if os.getenv('REDIS_PORT'):
            self.config.redis.port = int(os.getenv('REDIS_PORT'))
        if os.getenv('REDIS_PASSWORD'):
            self.config.redis.password = os.getenv('REDIS_PASSWORD')
        
        # Security overrides
        if os.getenv('SECRET_KEY'):
            self.config.security.secret_key = os.getenv('SECRET_KEY')
        if os.getenv('JWT_SECRET'):
            self.config.security.jwt_secret = os.getenv('JWT_SECRET')
        
        # App overrides
        if os.getenv('APP_URL'):
            self.config.url = os.getenv('APP_URL')
        if os.getenv('APP_DEBUG'):
            self.config.debug = os.getenv('APP_DEBUG').lower() in ['true', '1', 'yes']
    
    def save_config(self, config_path: Optional[Path] = None):
        """Konfigürasyonu kaydet"""
        if not self.config:
            return
        
        with self._lock:
            if config_path:
                config_file = config_path
            else:
                config_file = self.config_dir / f"{self.environment.value}.json"
            
            # Config'i dictionary'ye dönüştür
            config_dict = self._config_to_dict(self.config)
            
            # Hassas verileri şifrele
            if self.encryption:
                sensitive_keys = [
                    'database.password', 'redis.password', 'security.secret_key',
                    'security.jwt_secret', 'email.password', 'storage.aws_secret_key'
                ]
                config_dict = self.encryption.encrypt_config_dict(config_dict, sensitive_keys)
            
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False, default=str)
                
                self.logger.info(f"Configuration saved to {config_file}")
                
            except Exception as e:
                self.logger.error(f"Error saving config to {config_file}: {e}")
    
    def _config_to_dict(self, config: EnterpriseConfig) -> Dict[str, Any]:
        """EnterpriseConfig'i dictionary'ye dönüştür"""
        result = {}
        
        for key, value in config.__dict__.items():
            if hasattr(value, '__dict__'):
                # Alt konfigürasyon objesi
                result[key] = value.__dict__.copy()
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Konfigürasyon değeri al (dot notation destekli)"""
        if not self.config:
            return default
        
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Konfigürasyon değeri ayarla (dot notation destekli)"""
        if not self.config:
            return
        
        keys = key.split('.')
        obj = self.config
        
        # Son anahtar hariç tüm anahtarları dolaş
        for k in keys[:-1]:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            else:
                return
        
        # Son anahtarı ayarla
        if hasattr(obj, keys[-1]):
            setattr(obj, keys[-1], value)
    
    def reload_config(self):
        """Konfigürasyonu yeniden yükle"""
        self.logger.info("Reloading configuration...")
        self.load_config()
    
    def enable_encryption(self, key: Optional[str] = None):
        """Konfigürasyon şifrelemeyi etkinleştir"""
        self.encryption = ConfigEncryption(key)
        self.logger.info("Configuration encryption enabled")
    
    def create_backup(self) -> str:
        """Konfigürasyon yedeği oluştur"""
        if not self.config:
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.config_dir / f"backup_{self.environment.value}_{timestamp}.json"
        
        self.save_config(backup_file)
        return str(backup_file)
    
    def get_config_info(self) -> Dict[str, Any]:
        """Konfigürasyon bilgilerini al"""
        if not self.config:
            return {}
        
        return {
            'app_name': self.config.app_name,
            'app_version': self.config.app_version,
            'environment': self.config.environment.value,
            'debug': self.config.debug,
            'timezone': self.config.timezone,
            'locale': self.config.locale,
            'url': self.config.url,
            'database_driver': self.config.database.driver,
            'cache_enabled': self.config.integration.caching_enabled,
            'monitoring_enabled': self.config.monitoring.enabled,
            'encryption_enabled': self.encryption is not None
        }
    
    def validate_current_config(self) -> List[str]:
        """Mevcut konfigürasyonu doğrula"""
        if not self.config:
            return ["No configuration loaded"]
        
        return ConfigValidator.validate_config(self.config)


# Global instance
_config_manager = None

def get_config_manager(config_dir: str = None, environment: Environment = None) -> EnterpriseConfigManager:
    """Global konfigürasyon yöneticisi instance'ı"""
    global _config_manager
    if _config_manager is None:
        env = environment or Environment(os.getenv('APP_ENV', 'development'))
        _config_manager = EnterpriseConfigManager(config_dir, env)
        _config_manager.load_config()
    return _config_manager


def get_config(key: str = None, default: Any = None) -> Any:
    """Konfigürasyon değeri al"""
    manager = get_config_manager()
    if key is None:
        return manager.config
    return manager.get(key, default)


# Configuration templates for different environments
CONFIG_TEMPLATES = {
    Environment.DEVELOPMENT: {
        "app_name": "PraPazar Enterprise (Dev)",
        "debug": True,
        "database": {
            "host": "localhost",
            "port": 3306,
            "database": "prapazar_dev",
            "username": "root",
            "password": "",
            "pool_size": 5
        },
        "redis": {
            "host": "localhost",
            "port": 6379,
            "database": 0
        },
        "logging": {
            "level": "DEBUG",
            "console_enabled": True,
            "file_enabled": True
        },
        "monitoring": {
            "enabled": False
        }
    },
    Environment.PRODUCTION: {
        "app_name": "PraPazar Enterprise",
        "debug": False,
        "database": {
            "host": "prod-db-host",
            "port": 3306,
            "database": "prapazar_prod",
            "username": "prapazar_user",
            "password": "secure-password-change-this",
            "pool_size": 20,
            "ssl_mode": "REQUIRED"
        },
        "redis": {
            "host": "prod-redis-host",
            "port": 6379,
            "password": "redis-password-change-this",
            "ssl": True
        },
        "security": {
            "secret_key": "super-secure-secret-key-change-this-in-production",
            "jwt_secret": "super-secure-jwt-secret-change-this-in-production",
            "cors_origins": ["https://yourdomain.com"],
            "rate_limit_enabled": True
        },
        "logging": {
            "level": "INFO",
            "console_enabled": False,
            "file_enabled": True,
            "syslog_enabled": True
        },
        "monitoring": {
            "enabled": True,
            "prometheus_enabled": True,
            "grafana_enabled": True,
            "alerting_enabled": True
        }
    }
}


def create_config_template(environment: Environment, output_path: str = None):
    """Konfigürasyon şablonu oluştur"""
    template = CONFIG_TEMPLATES.get(environment, CONFIG_TEMPLATES[Environment.DEVELOPMENT])
    
    if output_path:
        config_file = Path(output_path)
    else:
        config_file = Path(f"config/{environment.value}.json")
    
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"Configuration template created: {config_file}")


if __name__ == "__main__":
    # Test the configuration system
    print("🔧 Enterprise Configuration Manager Test\n")
    
    # Create templates for all environments
    for env in Environment:
        create_config_template(env)
        print(f"✅ {env.value} template created")
    
    # Test configuration loading
    manager = get_config_manager()
    config = manager.config
    
    print(f"\n📊 Configuration Info:")
    info = manager.get_config_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Test validation
    print(f"\n🔍 Configuration Validation:")
    errors = manager.validate_current_config()
    if errors:
        for error in errors:
            print(f"   ❌ {error}")
    else:
        print("   ✅ Configuration is valid")
    
    # Test get/set
    print(f"\n🔧 Configuration Access Test:")
    print(f"   App Name: {manager.get('app_name')}")
    print(f"   Database Host: {manager.get('database.host')}")
    print(f"   Debug Mode: {manager.get('debug')}")
    
    # Create backup
    backup_file = manager.create_backup()
    print(f"\n💾 Backup created: {backup_file}")
    
    print("\n✅ Enterprise Configuration Manager test completed!")