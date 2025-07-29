"""
Database Seed Script
Tüm entegrasyonları ve temel verileri database'e ekler
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

from core.Database.models import Base, Integration, Feature, IntegrationType, IntegrationStatus
from config.integrations_data import INTEGRATIONS_DATA

def get_database_url():
    """Get database URL from environment or use default"""
    return os.getenv(
        'DATABASE_URL',
        'postgresql://marketplace_user:marketplace_pass@localhost:5432/marketplace_db'
    )

def seed_features(session):
    """Seed feature data"""
    features = [
        # Product Management
        {"name": "product_listing", "display_name": "Ürün Listeleme", "category": "product", "description": "Ürünleri platforma listeleme"},
        {"name": "stock_management", "display_name": "Stok Yönetimi", "category": "inventory", "description": "Stok takibi ve güncelleme"},
        {"name": "price_update", "display_name": "Fiyat Güncelleme", "category": "product", "description": "Ürün fiyatlarını güncelleme"},
        {"name": "bulk_upload", "display_name": "Toplu Yükleme", "category": "product", "description": "Excel/CSV ile toplu ürün yükleme"},
        {"name": "category_mapping", "display_name": "Kategori Eşleştirme", "category": "product", "description": "Otomatik kategori eşleştirme"},
        
        # Order Management
        {"name": "order_tracking", "display_name": "Sipariş Takibi", "category": "order", "description": "Sipariş durumu takibi"},
        {"name": "order_processing", "display_name": "Sipariş İşleme", "category": "order", "description": "Sipariş onaylama ve işleme"},
        {"name": "shipping_integration", "display_name": "Kargo Entegrasyonu", "category": "shipping", "description": "Kargo firması entegrasyonu"},
        {"name": "invoice_generation", "display_name": "Fatura Oluşturma", "category": "invoice", "description": "Otomatik fatura oluşturma"},
        {"name": "return_management", "display_name": "İade Yönetimi", "category": "order", "description": "İade ve iptal işlemleri"},
        
        # Reporting & Analytics
        {"name": "sales_reports", "display_name": "Satış Raporları", "category": "reporting", "description": "Detaylı satış raporları"},
        {"name": "performance_analytics", "display_name": "Performans Analizi", "category": "reporting", "description": "Satış performans metrikleri"},
        {"name": "inventory_reports", "display_name": "Stok Raporları", "category": "reporting", "description": "Stok durumu raporları"},
        {"name": "financial_reports", "display_name": "Finansal Raporlar", "category": "reporting", "description": "Gelir-gider raporları"},
        
        # AI Features
        {"name": "ai_pricing", "display_name": "Akıllı Fiyatlandırma", "category": "ai", "description": "AI destekli dinamik fiyatlandırma", "is_ai_powered": True},
        {"name": "demand_forecast", "display_name": "Talep Tahmini", "category": "ai", "description": "AI ile talep tahmini", "is_ai_powered": True},
        {"name": "competitor_analysis", "display_name": "Rakip Analizi", "category": "ai", "description": "AI destekli rakip analizi", "is_ai_powered": True},
        {"name": "customer_insights", "display_name": "Müşteri İçgörüleri", "category": "ai", "description": "AI ile müşteri davranış analizi", "is_ai_powered": True},
        
        # Integration Features
        {"name": "webhook_support", "display_name": "Webhook Desteği", "category": "integration", "description": "Gerçek zamanlı event bildirimleri"},
        {"name": "api_access", "display_name": "API Erişimi", "category": "integration", "description": "RESTful API erişimi"},
        {"name": "batch_operations", "display_name": "Toplu İşlemler", "category": "integration", "description": "Toplu güncelleme ve işlemler"},
        {"name": "real_time_sync", "display_name": "Gerçek Zamanlı Senkronizasyon", "category": "integration", "description": "Anlık veri senkronizasyonu"},
    ]
    
    for feature_data in features:
        feature = Feature(**feature_data)
        session.add(feature)
    
    session.commit()
    print(f"✅ {len(features)} feature added to database")

def get_integration_type(category):
    """Map category to IntegrationType enum"""
    mapping = {
        "marketplaces": IntegrationType.MARKETPLACE,
        "ecommerce_sites": IntegrationType.E_COMMERCE,
        "e_invoice": IntegrationType.E_INVOICE,
        "accounting_erp": IntegrationType.ACCOUNTING,
        "pre_accounting": IntegrationType.ACCOUNTING,
        "cargo": IntegrationType.CARGO,
        "fulfillment": IntegrationType.FULFILLMENT,
        "social_media_stores": IntegrationType.SOCIAL_MEDIA,
        "retail": IntegrationType.E_COMMERCE,
        "international": IntegrationType.MARKETPLACE
    }
    return mapping.get(category, IntegrationType.MARKETPLACE)

def seed_integrations(session):
    """Seed integration data from config"""
    total_count = 0
    
    for category, integrations in INTEGRATIONS_DATA.items():
        if isinstance(integrations, list):
            integration_type = get_integration_type(category)
            
            for integration_data in integrations:
                # Prepare integration record
                integration = Integration(
                    name=integration_data['name'],
                    display_name=integration_data['display_name'],
                    type=integration_type,
                    status=IntegrationStatus.INACTIVE,
                    description=integration_data.get('description', ''),
                    is_premium=integration_data.get('is_premium', False),
                    is_beta=integration_data.get('is_beta', False),
                    supported_countries=integration_data.get('supported_countries', []),
                    supported_currencies=integration_data.get('supported_currencies', []),
                    webhook_supported='webhook' in integration_data.get('features', []),
                    api_key_required=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                # Set URLs based on integration name
                if integration.name == 'trendyol':
                    integration.api_base_url = 'https://api.trendyol.com/sapigw'
                    integration.sandbox_url = 'https://stageapi.trendyol.com/stageapigw'
                    integration.documentation_url = 'https://developers.trendyol.com'
                    integration.website_url = 'https://www.trendyol.com'
                elif integration.name == 'hepsiburada':
                    integration.api_base_url = 'https://mpop.hepsiburada.com'
                    integration.sandbox_url = 'https://sandbox-mpop.hepsiburada.com'
                    integration.documentation_url = 'https://developers.hepsiburada.com'
                    integration.website_url = 'https://www.hepsiburada.com'
                elif integration.name == 'n11':
                    integration.api_base_url = 'https://api.n11.com/ws'
                    integration.sandbox_url = 'https://api.n11.com/ws'
                    integration.documentation_url = 'https://dev.n11.com'
                    integration.website_url = 'https://www.n11.com'
                elif integration.name == 'amazon_tr':
                    integration.api_base_url = 'https://sellingpartnerapi-eu.amazon.com'
                    integration.sandbox_url = 'https://sandbox.sellingpartnerapi-eu.amazon.com'
                    integration.documentation_url = 'https://developer-docs.amazon.com/sp-api/'
                    integration.website_url = 'https://www.amazon.com.tr'
                elif integration.name == 'ciceksepeti':
                    integration.api_base_url = 'https://apis.ciceksepeti.com'
                    integration.sandbox_url = 'https://sandbox-apis.ciceksepeti.com'
                    integration.website_url = 'https://www.ciceksepeti.com'
                elif integration.name == 'pttavm':
                    integration.api_base_url = 'https://api.pttavm.com'
                    integration.website_url = 'https://www.pttavm.com'
                
                # Add rate limits for marketplaces
                if integration_type == IntegrationType.MARKETPLACE:
                    integration.rate_limits = {
                        "requests_per_minute": 60,
                        "requests_per_day": 10000,
                        "burst_limit": 100
                    }
                
                session.add(integration)
                total_count += 1
    
    session.commit()
    print(f"✅ {total_count} integrations added to database")

def main():
    """Main function to seed the database"""
    print("🚀 Starting database seeding...")
    
    # Create database engine
    engine = create_engine(get_database_url())
    
    # Create all tables
    Base.metadata.create_all(engine)
    print("✅ Database tables created")
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if data already exists
        existing_integrations = session.query(Integration).count()
        if existing_integrations > 0:
            print(f"⚠️  Database already contains {existing_integrations} integrations. Skipping seed.")
            return
        
        # Seed data
        seed_features(session)
        seed_integrations(session)
        
        print("\n✅ Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Features: {session.query(Feature).count()}")
        print(f"   - Integrations: {session.query(Integration).count()}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()