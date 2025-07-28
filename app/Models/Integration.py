from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json

class IntegrationType(Enum):
    """Entegrasyon tipleri"""
    # E-Ticaret Entegrasyonları
    MARKETPLACE = "marketplace"
    ECOMMERCE_SITE = "ecommerce_site"
    SOCIAL_MEDIA_STORE = "social_media_store"
    INTERNATIONAL = "international"
    
    # Muhasebe ve ERP Entegrasyonları
    ACCOUNTING = "accounting"
    ERP = "erp"
    E_INVOICE = "e_invoice"
    PRE_ACCOUNTING = "pre_accounting"
    
    # Kargo ve Fulfillment Entegrasyonları
    CARGO = "cargo"
    FULFILLMENT = "fulfillment"

class IntegrationStatus(Enum):
    """Entegrasyon durumları"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class Integration:
    """Tüm entegrasyon tiplerini yöneten ana model"""
    
    def __init__(self, integration_id: Optional[str] = None):
        self.id = integration_id
        self.name: str = ""
        self.display_name: str = ""
        self.type: IntegrationType = IntegrationType.MARKETPLACE
        self.status: IntegrationStatus = IntegrationStatus.INACTIVE
        self.config: Dict[str, Any] = {}
        self.features: List[str] = []
        self.api_endpoints: Dict[str, str] = {}
        self.credentials: Dict[str, Any] = {}
        self.settings: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        self.last_sync_at: Optional[datetime] = None
        self.error_log: List[Dict[str, Any]] = []
        self.is_premium: bool = False
        self.is_coming_soon: bool = False
        self.logo_url: str = ""
        self.description: str = ""
        self.documentation_url: str = ""
        self.supported_countries: List[str] = []
        self.supported_currencies: List[str] = []
        self.ai_enabled: bool = True
        self.ai_features: List[str] = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Model'i dictionary'e çevir"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'type': self.type.value,
            'status': self.status.value,
            'config': self.config,
            'features': self.features,
            'api_endpoints': self.api_endpoints,
            'settings': self.settings,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'error_log': self.error_log,
            'is_premium': self.is_premium,
            'is_coming_soon': self.is_coming_soon,
            'logo_url': self.logo_url,
            'description': self.description,
            'documentation_url': self.documentation_url,
            'supported_countries': self.supported_countries,
            'supported_currencies': self.supported_currencies,
            'ai_enabled': self.ai_enabled,
            'ai_features': self.ai_features
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Integration':
        """Dictionary'den model oluştur"""
        integration = cls(data.get('id'))
        integration.name = data.get('name', '')
        integration.display_name = data.get('display_name', '')
        integration.type = IntegrationType(data.get('type', 'marketplace'))
        integration.status = IntegrationStatus(data.get('status', 'inactive'))
        integration.config = data.get('config', {})
        integration.features = data.get('features', [])
        integration.api_endpoints = data.get('api_endpoints', {})
        integration.settings = data.get('settings', {})
        integration.metadata = data.get('metadata', {})
        
        if data.get('created_at'):
            integration.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            integration.updated_at = datetime.fromisoformat(data['updated_at'])
        if data.get('last_sync_at'):
            integration.last_sync_at = datetime.fromisoformat(data['last_sync_at'])
            
        integration.error_log = data.get('error_log', [])
        integration.is_premium = data.get('is_premium', False)
        integration.is_coming_soon = data.get('is_coming_soon', False)
        integration.logo_url = data.get('logo_url', '')
        integration.description = data.get('description', '')
        integration.documentation_url = data.get('documentation_url', '')
        integration.supported_countries = data.get('supported_countries', [])
        integration.supported_currencies = data.get('supported_currencies', [])
        integration.ai_enabled = data.get('ai_enabled', True)
        integration.ai_features = data.get('ai_features', [])
        
        return integration
    
    def activate(self) -> bool:
        """Entegrasyonu aktif et"""
        if self.validate_credentials():
            self.status = IntegrationStatus.ACTIVE
            self.updated_at = datetime.now()
            return True
        return False
    
    def deactivate(self) -> None:
        """Entegrasyonu deaktif et"""
        self.status = IntegrationStatus.INACTIVE
        self.updated_at = datetime.now()
    
    def validate_credentials(self) -> bool:
        """Kimlik bilgilerini doğrula"""
        # Her entegrasyon tipi için özel doğrulama mantığı
        required_fields = self.get_required_credential_fields()
        for field in required_fields:
            if field not in self.credentials or not self.credentials[field]:
                return False
        return True
    
    def get_required_credential_fields(self) -> List[str]:
        """Gerekli kimlik bilgisi alanlarını getir"""
        # Entegrasyon tipine göre gerekli alanları belirle
        base_fields = ['api_key']
        
        if self.type == IntegrationType.MARKETPLACE:
            return base_fields + ['seller_id', 'secret_key']
        elif self.type == IntegrationType.E_INVOICE:
            return base_fields + ['username', 'password', 'company_code']
        elif self.type == IntegrationType.CARGO:
            return base_fields + ['customer_number', 'password']
        elif self.type == IntegrationType.ACCOUNTING:
            return base_fields + ['company_id', 'user_token']
        
        return base_fields
    
    def add_error(self, error_type: str, message: str, details: Optional[Dict] = None) -> None:
        """Hata logu ekle"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'details': details or {}
        }
        self.error_log.append(error_entry)
        self.status = IntegrationStatus.ERROR
        self.updated_at = datetime.now()
    
    def clear_errors(self) -> None:
        """Hata logunu temizle"""
        self.error_log = []
        if self.status == IntegrationStatus.ERROR:
            self.status = IntegrationStatus.INACTIVE
        self.updated_at = datetime.now()
    
    def update_sync_time(self) -> None:
        """Son senkronizasyon zamanını güncelle"""
        self.last_sync_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_ai_feature(self, feature: str) -> None:
        """AI özelliği ekle"""
        if feature not in self.ai_features:
            self.ai_features.append(feature)
            self.updated_at = datetime.now()
    
    def is_ready(self) -> bool:
        """Entegrasyonun kullanıma hazır olup olmadığını kontrol et"""
        return (
            self.status == IntegrationStatus.ACTIVE and
            not self.is_coming_soon and
            self.validate_credentials()
        )