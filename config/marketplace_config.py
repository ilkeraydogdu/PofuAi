"""
Marketplace Integration Configuration Management
Bu modül marketplace entegrasyonları için güvenli configuration yönetimi sağlar.
"""

import os
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from cryptography.fernet import Fernet
import json

logger = logging.getLogger(__name__)

@dataclass
class MarketplaceCredentials:
    """Marketplace API credentials"""
    api_key: str
    api_secret: str
    additional_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}

class ConfigurationManager:
    """Marketplace configuration manager with security"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or os.getenv('MARKETPLACE_ENCRYPTION_KEY')
        self.fernet = None
        
        if self.encryption_key:
            try:
                self.fernet = Fernet(self.encryption_key.encode())
            except Exception as e:
                logger.warning(f"Encryption key setup failed: {e}")
        
        self._load_environment_config()
    
    def _load_environment_config(self):
        """Environment variables'lardan config yükle"""
        self.config = {
            'trendyol': {
                'enabled': os.getenv('TRENDYOL_ENABLED', 'false').lower() == 'true',
                'api_key': os.getenv('TRENDYOL_API_KEY', ''),
                'api_secret': os.getenv('TRENDYOL_API_SECRET', ''),
                'supplier_id': os.getenv('TRENDYOL_SUPPLIER_ID', ''),
                'sandbox': os.getenv('TRENDYOL_SANDBOX', 'true').lower() == 'true',
                'rate_limit': int(os.getenv('TRENDYOL_RATE_LIMIT', '1000')),
                'timeout': int(os.getenv('TRENDYOL_TIMEOUT', '30'))
            },
            'hepsiburada': {
                'enabled': os.getenv('HEPSIBURADA_ENABLED', 'false').lower() == 'true',
                'username': os.getenv('HEPSIBURADA_USERNAME', ''),
                'password': os.getenv('HEPSIBURADA_PASSWORD', ''),
                'merchant_id': os.getenv('HEPSIBURADA_MERCHANT_ID', ''),
                'sandbox': os.getenv('HEPSIBURADA_SANDBOX', 'true').lower() == 'true',
                'rate_limit': int(os.getenv('HEPSIBURADA_RATE_LIMIT', '1000')),
                'timeout': int(os.getenv('HEPSIBURADA_TIMEOUT', '30'))
            },
            'n11': {
                'enabled': os.getenv('N11_ENABLED', 'false').lower() == 'true',
                'api_key': os.getenv('N11_API_KEY', ''),
                'api_secret': os.getenv('N11_API_SECRET', ''),
                'sandbox': os.getenv('N11_SANDBOX', 'true').lower() == 'true',
                'rate_limit': int(os.getenv('N11_RATE_LIMIT', '1000')),
                'timeout': int(os.getenv('N11_TIMEOUT', '30'))
            },
            'iyzico': {
                'enabled': os.getenv('IYZICO_ENABLED', 'false').lower() == 'true',
                'api_key': os.getenv('IYZICO_API_KEY', ''),
                'secret_key': os.getenv('IYZICO_SECRET_KEY', ''),
                'sandbox': os.getenv('IYZICO_SANDBOX', 'true').lower() == 'true',
                'rate_limit': int(os.getenv('IYZICO_RATE_LIMIT', '1000')),
                'timeout': int(os.getenv('IYZICO_TIMEOUT', '30'))
            },
            'global': {
                'max_retries': int(os.getenv('MARKETPLACE_MAX_RETRIES', '3')),
                'backoff_factor': float(os.getenv('MARKETPLACE_BACKOFF_FACTOR', '1.0')),
                'enable_logging': os.getenv('MARKETPLACE_ENABLE_LOGGING', 'true').lower() == 'true',
                'enable_metrics': os.getenv('MARKETPLACE_ENABLE_METRICS', 'true').lower() == 'true',
                'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
                'database_url': os.getenv('DATABASE_URL', 'sqlite:///marketplace.db')
            }
        }
    
    def get_marketplace_config(self, marketplace_name: str) -> Dict[str, Any]:
        """Belirtilen marketplace için config döndür"""
        if marketplace_name not in self.config:
            raise ValueError(f"Unknown marketplace: {marketplace_name}")
        
        config = self.config[marketplace_name].copy()
        
        # Encrypted credentials varsa decrypt et
        if self.fernet:
            for key in ['api_key', 'api_secret', 'password', 'secret_key']:
                if key in config and config[key]:
                    try:
                        config[key] = self._decrypt_value(config[key])
                    except Exception:
                        # Eğer decrypt edilemezse, plain text olarak bırak
                        pass
        
        return config
    
    def get_credentials(self, marketplace_name: str) -> MarketplaceCredentials:
        """Marketplace credentials'larını güvenli şekilde döndür"""
        config = self.get_marketplace_config(marketplace_name)
        
        if marketplace_name == 'trendyol':
            return MarketplaceCredentials(
                api_key=config['api_key'],
                api_secret=config['api_secret'],
                additional_params={'supplier_id': config['supplier_id']}
            )
        elif marketplace_name == 'hepsiburada':
            return MarketplaceCredentials(
                api_key=config['username'],
                api_secret=config['password'],
                additional_params={'merchant_id': config['merchant_id']}
            )
        elif marketplace_name == 'n11':
            return MarketplaceCredentials(
                api_key=config['api_key'],
                api_secret=config['api_secret']
            )
        elif marketplace_name == 'iyzico':
            return MarketplaceCredentials(
                api_key=config['api_key'],
                api_secret=config['secret_key']
            )
        else:
            raise ValueError(f"Unknown marketplace: {marketplace_name}")
    
    def _encrypt_value(self, value: str) -> str:
        """Değeri şifrele"""
        if not self.fernet:
            return value
        return self.fernet.encrypt(value.encode()).decode()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Şifrelenmiş değeri çöz"""
        if not self.fernet:
            return encrypted_value
        return self.fernet.decrypt(encrypted_value.encode()).decode()
    
    def validate_config(self, marketplace_name: str) -> Dict[str, Any]:
        """Marketplace config'ini validate et"""
        config = self.get_marketplace_config(marketplace_name)
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Temel validasyonlar
        if not config.get('enabled'):
            validation_result['warnings'].append(f"{marketplace_name} is disabled")
        
        # Marketplace-specific validasyonlar
        if marketplace_name == 'trendyol':
            required_fields = ['api_key', 'api_secret', 'supplier_id']
        elif marketplace_name == 'hepsiburada':
            required_fields = ['username', 'password', 'merchant_id']
        elif marketplace_name == 'n11':
            required_fields = ['api_key', 'api_secret']
        elif marketplace_name == 'iyzico':
            required_fields = ['api_key', 'secret_key']
        else:
            validation_result['errors'].append(f"Unknown marketplace: {marketplace_name}")
            validation_result['valid'] = False
            return validation_result
        
        # Required fields kontrolü
        for field in required_fields:
            if not config.get(field):
                validation_result['errors'].append(f"Missing required field: {field}")
                validation_result['valid'] = False
        
        # Test credentials kontrolü
        test_values = ['YOUR_API_KEY', 'YOUR_API_SECRET', 'YOUR_SUPPLIER_ID', 
                      'YOUR_USERNAME', 'YOUR_PASSWORD', 'YOUR_MERCHANT_ID', 'YOUR_SECRET_KEY']
        
        for field, value in config.items():
            if isinstance(value, str) and value in test_values:
                validation_result['warnings'].append(f"Test credential detected in {field}")
        
        return validation_result
    
    def get_all_marketplace_status(self) -> Dict[str, Dict[str, Any]]:
        """Tüm marketplace'lerin durumunu döndür"""
        status = {}
        
        for marketplace in ['trendyol', 'hepsiburada', 'n11', 'iyzico']:
            validation = self.validate_config(marketplace)
            config = self.get_marketplace_config(marketplace)
            
            status[marketplace] = {
                'enabled': config.get('enabled', False),
                'sandbox': config.get('sandbox', True),
                'valid_config': validation['valid'],
                'errors': validation['errors'],
                'warnings': validation['warnings']
            }
        
        return status
    
    def save_encrypted_credentials(self, marketplace_name: str, credentials: Dict[str, str]):
        """Credentials'ları şifreleyerek kaydet (production için)"""
        if not self.fernet:
            logger.warning("No encryption key available, credentials will be stored in plain text")
            return False
        
        # Bu method production ortamında credentials'ları güvenli şekilde saklamak için kullanılabilir
        # Şimdilik sadece logging yapıyoruz
        logger.info(f"Encrypted credentials would be saved for {marketplace_name}")
        return True

# Global configuration manager instance
config_manager = ConfigurationManager()

def get_marketplace_config(marketplace_name: str) -> Dict[str, Any]:
    """Marketplace config'ini döndür"""
    return config_manager.get_marketplace_config(marketplace_name)

def get_marketplace_credentials(marketplace_name: str) -> MarketplaceCredentials:
    """Marketplace credentials'larını döndür"""
    return config_manager.get_credentials(marketplace_name)

def validate_marketplace_config(marketplace_name: str) -> Dict[str, Any]:
    """Marketplace config'ini validate et"""
    return config_manager.validate_config(marketplace_name)

def get_all_marketplace_status() -> Dict[str, Dict[str, Any]]:
    """Tüm marketplace'lerin durumunu döndür"""
    return config_manager.get_all_marketplace_status()