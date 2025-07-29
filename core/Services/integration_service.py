"""
Enterprise Integration Service
PraPazar entegrasyon sistemi için enterprise seviyesinde servis katmanı
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import redis
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Database Models
Base = declarative_base()

class IntegrationStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    SYNCING = "syncing"
    MAINTENANCE = "maintenance"

class IntegrationType(Enum):
    MARKETPLACE = "marketplace"
    ECOMMERCE = "ecommerce"
    CARGO = "cargo"
    INVOICE = "invoice"
    FULFILLMENT = "fulfillment"
    ACCOUNTING = "accounting"
    SOCIAL_MEDIA = "social_media"

@dataclass
class IntegrationConfig:
    """Entegrasyon konfigürasyonu"""
    name: str
    display_name: str
    type: IntegrationType
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    webhook_url: Optional[str] = None
    rate_limit: int = 100
    timeout: int = 30
    retry_count: int = 3
    is_premium: bool = False
    is_coming_soon: bool = False
    supported_countries: List[str] = None
    supported_currencies: List[str] = None
    features: List[str] = None
    ai_features: List[str] = None

class IntegrationDB(Base):
    """Entegrasyon veritabanı modeli"""
    __tablename__ = 'integrations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(20), default=IntegrationStatus.INACTIVE.value)
    config = Column(JSON, nullable=False)
    last_sync = Column(DateTime)
    error_count = Column(Integer, default=0)
    last_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IntegrationMetrics:
    """Entegrasyon metrikleri"""
    
    def __init__(self):
        self.api_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.response_times = []
        self.last_sync_duration = 0
        self.data_synced = 0
        
    def record_api_call(self, success: bool, response_time: float):
        """API çağrısını kaydet"""
        self.api_calls += 1
        if success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
        self.response_times.append(response_time)
        
    def get_success_rate(self) -> float:
        """Başarı oranını hesapla"""
        if self.api_calls == 0:
            return 0.0
        return (self.successful_calls / self.api_calls) * 100
        
    def get_avg_response_time(self) -> float:
        """Ortalama yanıt süresini hesapla"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

class IntegrationService:
    """Enterprise Integration Service"""
    
    def __init__(self, db_url: str = None, redis_url: str = None):
        self.logger = logging.getLogger(__name__)
        self.db_url = db_url or "sqlite:///integrations.db"
        self.redis_url = redis_url or "redis://localhost:6379"
        
        # Database setup
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Redis setup
        try:
            self.redis = redis.from_url(self.redis_url)
            self.redis.ping()
        except Exception as e:
            self.logger.warning(f"Redis bağlantısı kurulamadı: {e}")
            self.redis = None
            
        # Metrics storage
        self.metrics: Dict[str, IntegrationMetrics] = {}
        
        # Rate limiting
        self.rate_limits: Dict[str, Dict] = {}
        
        # Active integrations
        self.active_integrations: Dict[str, Any] = {}
        
    async def initialize(self):
        """Servisi başlat"""
        try:
            # Database bağlantısını test et
            with self.Session() as session:
                session.execute("SELECT 1")
                
            # Redis bağlantısını test et
            if self.redis:
                self.redis.ping()
                
            self.logger.info("Integration Service başarıyla başlatıldı")
            return True
        except Exception as e:
            self.logger.error(f"Integration Service başlatma hatası: {e}")
            return False
            
    def register_integration(self, config: IntegrationConfig) -> bool:
        """Yeni entegrasyon kaydet"""
        try:
            with self.Session() as session:
                # Mevcut entegrasyonu kontrol et
                existing = session.query(IntegrationDB).filter_by(name=config.name).first()
                
                if existing:
                    # Güncelle
                    existing.display_name = config.display_name
                    existing.type = config.type.value
                    existing.config = asdict(config)
                    existing.updated_at = datetime.utcnow()
                else:
                    # Yeni oluştur
                    integration = IntegrationDB(
                        name=config.name,
                        display_name=config.display_name,
                        type=config.type.value,
                        config=asdict(config),
                        status=IntegrationStatus.INACTIVE.value
                    )
                    session.add(integration)
                    
                session.commit()
                
                # Metrics başlat
                self.metrics[config.name] = IntegrationMetrics()
                
                # Rate limit ayarla
                self.rate_limits[config.name] = {
                    'calls': 0,
                    'reset_time': datetime.utcnow() + timedelta(minutes=1)
                }
                
                self.logger.info(f"Entegrasyon kaydedildi: {config.name}")
                return True
                
        except SQLAlchemyError as e:
            self.logger.error(f"Database hatası: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Entegrasyon kaydetme hatası: {e}")
            return False
            
    def get_integration(self, name: str) -> Optional[IntegrationDB]:
        """Entegrasyon bilgilerini getir"""
        try:
            with self.Session() as session:
                return session.query(IntegrationDB).filter_by(name=name).first()
        except Exception as e:
            self.logger.error(f"Entegrasyon getirme hatası: {e}")
            return None
            
    def list_integrations(self, status: Optional[IntegrationStatus] = None) -> List[IntegrationDB]:
        """Entegrasyon listesini getir"""
        try:
            with self.Session() as session:
                query = session.query(IntegrationDB)
                if status:
                    query = query.filter_by(status=status.value)
                return query.all()
        except Exception as e:
            self.logger.error(f"Entegrasyon listesi getirme hatası: {e}")
            return []
            
    def update_integration_status(self, name: str, status: IntegrationStatus, error: str = None) -> bool:
        """Entegrasyon durumunu güncelle"""
        try:
            with self.Session() as session:
                integration = session.query(IntegrationDB).filter_by(name=name).first()
                if integration:
                    integration.status = status.value
                    integration.updated_at = datetime.utcnow()
                    
                    if status == IntegrationStatus.ERROR:
                        integration.error_count += 1
                        integration.last_error = error
                    elif status == IntegrationStatus.ACTIVE:
                        integration.error_count = 0
                        integration.last_error = None
                        
                    session.commit()
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Durum güncelleme hatası: {e}")
            return False
            
    async def sync_integration(self, name: str, sync_type: str = "full") -> Dict[str, Any]:
        """Entegrasyon senkronizasyonu"""
        start_time = datetime.utcnow()
        
        try:
            # Rate limit kontrolü
            if not self._check_rate_limit(name):
                return {
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'integration': name
                }
                
            # Durumu güncelle
            self.update_integration_status(name, IntegrationStatus.SYNCING)
            
            # Senkronizasyon işlemi
            integration = self.get_integration(name)
            if not integration:
                return {
                    'success': False,
                    'error': 'Integration not found',
                    'integration': name
                }
                
            # Simüle edilmiş senkronizasyon
            await asyncio.sleep(2)  # Simüle edilmiş API çağrısı
            
            # Başarılı sonuç
            sync_duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Metrics güncelle
            if name in self.metrics:
                self.metrics[name].record_api_call(True, sync_duration)
                self.metrics[name].last_sync_duration = sync_duration
                
            # Durumu güncelle
            self.update_integration_status(name, IntegrationStatus.ACTIVE)
            
            # Cache'e kaydet
            if self.redis:
                cache_key = f"sync:{name}:{sync_type}"
                cache_data = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'duration': sync_duration,
                    'type': sync_type,
                    'success': True
                }
                self.redis.setex(cache_key, 3600, json.dumps(cache_data))
                
            return {
                'success': True,
                'integration': name,
                'duration': sync_duration,
                'type': sync_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Hata durumu
            sync_duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Metrics güncelle
            if name in self.metrics:
                self.metrics[name].record_api_call(False, sync_duration)
                
            # Durumu güncelle
            self.update_integration_status(name, IntegrationStatus.ERROR, str(e))
            
            return {
                'success': False,
                'error': str(e),
                'integration': name,
                'duration': sync_duration
            }
            
    def _check_rate_limit(self, name: str) -> bool:
        """Rate limit kontrolü"""
        if name not in self.rate_limits:
            return True
            
        limit_info = self.rate_limits[name]
        now = datetime.utcnow()
        
        # Reset time kontrolü
        if now > limit_info['reset_time']:
            limit_info['calls'] = 0
            limit_info['reset_time'] = now + timedelta(minutes=1)
            
        # Limit kontrolü
        if limit_info['calls'] >= 100:  # 100 calls per minute
            return False
            
        limit_info['calls'] += 1
        return True
        
    def get_integration_metrics(self, name: str) -> Dict[str, Any]:
        """Entegrasyon metriklerini getir"""
        metrics = self.metrics.get(name)
        if not metrics:
            return {}
            
        return {
            'api_calls': metrics.api_calls,
            'successful_calls': metrics.successful_calls,
            'failed_calls': metrics.failed_calls,
            'success_rate': metrics.get_success_rate(),
            'avg_response_time': metrics.get_avg_response_time(),
            'last_sync_duration': metrics.last_sync_duration,
            'data_synced': metrics.data_synced
        }
        
    def get_system_health(self) -> Dict[str, Any]:
        """Sistem sağlık durumu"""
        try:
            with self.Session() as session:
                total_integrations = session.query(IntegrationDB).count()
                active_integrations = session.query(IntegrationDB).filter_by(
                    status=IntegrationStatus.ACTIVE.value
                ).count()
                error_integrations = session.query(IntegrationDB).filter_by(
                    status=IntegrationStatus.ERROR.value
                ).count()
                
            return {
                'total_integrations': total_integrations,
                'active_integrations': active_integrations,
                'error_integrations': error_integrations,
                'health_percentage': (active_integrations / total_integrations * 100) if total_integrations > 0 else 0,
                'database_status': 'healthy',
                'redis_status': 'connected' if self.redis else 'disconnected',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
            
    async def bulk_sync(self, integration_names: List[str] = None) -> Dict[str, Any]:
        """Toplu senkronizasyon"""
        if not integration_names:
            integrations = self.list_integrations()
            integration_names = [i.name for i in integrations]
            
        results = {}
        for name in integration_names:
            result = await self.sync_integration(name)
            results[name] = result
            
        return {
            'total': len(integration_names),
            'successful': len([r for r in results.values() if r['success']]),
            'failed': len([r for r in results.values() if not r['success']]),
            'results': results
        }
        
    def cleanup_old_data(self, days: int = 30) -> bool:
        """Eski verileri temizle"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with self.Session() as session:
                # Eski hata kayıtlarını temizle
                session.query(IntegrationDB).filter(
                    IntegrationDB.updated_at < cutoff_date,
                    IntegrationDB.status == IntegrationStatus.ERROR.value
                ).update({
                    'last_error': None,
                    'error_count': 0
                })
                
                session.commit()
                
            return True
        except Exception as e:
            self.logger.error(f"Veri temizleme hatası: {e}")
            return False

# Global service instance
integration_service = IntegrationService()