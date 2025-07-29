#!/usr/bin/env python3
"""
Database Setup Script for Marketplace Integrations
Bu script marketplace entegrasyonları için gerekli database schema'sını oluşturur.
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database base
Base = declarative_base()

class Integration(Base):
    """Entegrasyon tablosu"""
    __tablename__ = 'integrations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)  # marketplace, payment, etc.
    status = Column(String(20), default='inactive')  # active, inactive, error
    
    # API Configuration
    api_endpoint = Column(String(500))
    api_key_encrypted = Column(Text)  # Encrypted storage
    secret_key_encrypted = Column(Text)  # Encrypted storage
    additional_config = Column(JSON)  # JSON field for extra config
    
    # Settings
    is_sandbox = Column(Boolean, default=True)
    is_enabled = Column(Boolean, default=False)
    rate_limit = Column(Integer, default=1000)
    timeout = Column(Integer, default=30)
    max_retries = Column(Integer, default=3)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync_at = Column(DateTime)
    
    # Statistics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    last_error = Column(Text)
    last_error_at = Column(DateTime)

class IntegrationLog(Base):
    """Entegrasyon log tablosu"""
    __tablename__ = 'integration_logs'
    
    id = Column(Integer, primary_key=True)
    integration_name = Column(String(100), nullable=False)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    request_data = Column(JSON)
    response_data = Column(JSON)
    execution_time = Column(Float)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    """Ürün tablosu"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    sku = Column(String(100), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    brand = Column(String(200))
    category = Column(String(200))
    
    # Pricing
    list_price = Column(Float)
    sale_price = Column(Float)
    currency = Column(String(3), default='TRY')
    
    # Inventory
    stock_quantity = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProductIntegration(Base):
    """Ürün-Entegrasyon mapping tablosu"""
    __tablename__ = 'product_integrations'
    
    id = Column(Integer, primary_key=True)
    product_sku = Column(String(100), nullable=False)
    integration_name = Column(String(100), nullable=False)
    external_id = Column(String(200))  # External marketplace product ID
    status = Column(String(20), default='pending')  # pending, synced, error
    last_sync_at = Column(DateTime)
    sync_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    """Sipariş tablosu"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String(100), unique=True, nullable=False)
    integration_name = Column(String(100), nullable=False)
    external_order_id = Column(String(200))
    
    # Customer info
    customer_name = Column(String(200))
    customer_email = Column(String(200))
    customer_phone = Column(String(50))
    
    # Order details
    status = Column(String(20), default='pending')
    total_amount = Column(Float)
    currency = Column(String(3), default='TRY')
    
    # Shipping
    shipping_address = Column(JSON)
    billing_address = Column(JSON)
    tracking_number = Column(String(100))
    
    # Timestamps
    order_date = Column(DateTime)
    shipped_date = Column(DateTime)
    delivered_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PaymentTransaction(Base):
    """Ödeme işlemi tablosu"""
    __tablename__ = 'payment_transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(100), unique=True, nullable=False)
    order_number = Column(String(100))
    payment_provider = Column(String(50))  # iyzico, etc.
    
    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='TRY')
    status = Column(String(20))  # success, failed, pending, refunded
    payment_method = Column(String(50))  # credit_card, debit_card, etc.
    
    # Provider specific data
    provider_transaction_id = Column(String(200))
    provider_response = Column(JSON)
    
    # Timestamps
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_database_url():
    """Database URL'ini environment'tan al"""
    return os.getenv('DATABASE_URL', 'sqlite:///marketplace.db')

def create_database_tables(database_url: str = None):
    """Database tablolarını oluştur"""
    if not database_url:
        database_url = get_database_url()
    
    logger.info(f"Creating database tables with URL: {database_url}")
    
    try:
        # Engine oluştur
        engine = create_engine(database_url, echo=False)
        
        # Tabloları oluştur
        Base.metadata.create_all(engine)
        
        logger.info("Database tables created successfully")
        
        # Test connection
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Sample data ekle (eğer yoksa)
        existing_integrations = session.query(Integration).count()
        if existing_integrations == 0:
            logger.info("Adding sample integration data...")
            
            sample_integrations = [
                Integration(
                    name='trendyol',
                    display_name='Trendyol',
                    type='marketplace',
                    api_endpoint='https://api.trendyol.com/sapigw',
                    is_sandbox=True,
                    is_enabled=False
                ),
                Integration(
                    name='hepsiburada',
                    display_name='Hepsiburada',
                    type='marketplace',
                    api_endpoint='https://oms-external-sandbox.hepsiburada.com',
                    is_sandbox=True,
                    is_enabled=False
                ),
                Integration(
                    name='n11',
                    display_name='N11',
                    type='marketplace',
                    api_endpoint='https://api.n11.com/ws',
                    is_sandbox=True,
                    is_enabled=False
                ),
                Integration(
                    name='iyzico',
                    display_name='İyzico',
                    type='payment',
                    api_endpoint='https://sandbox-api.iyzipay.com',
                    is_sandbox=True,
                    is_enabled=False
                )
            ]
            
            for integration in sample_integrations:
                session.add(integration)
            
            session.commit()
            logger.info("Sample integration data added")
        
        session.close()
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def check_database_connection(database_url: str = None):
    """Database bağlantısını kontrol et"""
    if not database_url:
        database_url = get_database_url()
    
    try:
        engine = create_engine(database_url, echo=False)
        connection = engine.connect()
        connection.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def get_database_info(database_url: str = None):
    """Database bilgilerini göster"""
    if not database_url:
        database_url = get_database_url()
    
    try:
        engine = create_engine(database_url, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        info = {
            'database_url': database_url,
            'tables': {
                'integrations': session.query(Integration).count(),
                'integration_logs': session.query(IntegrationLog).count(),
                'products': session.query(Product).count(),
                'product_integrations': session.query(ProductIntegration).count(),
                'orders': session.query(Order).count(),
                'payment_transactions': session.query(PaymentTransaction).count()
            }
        }
        
        session.close()
        return info
        
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return None

def main():
    """Ana fonksiyon"""
    print("🔧 Marketplace Integration Database Setup")
    print("=" * 50)
    
    # Database URL kontrol
    database_url = get_database_url()
    print(f"Database URL: {database_url}")
    
    # Bağlantı testi
    print("\n1️⃣ Testing database connection...")
    if not check_database_connection(database_url):
        print("❌ Database connection failed. Please check your DATABASE_URL.")
        sys.exit(1)
    print("✅ Database connection successful")
    
    # Tabloları oluştur
    print("\n2️⃣ Creating database tables...")
    if create_database_tables(database_url):
        print("✅ Database tables created successfully")
    else:
        print("❌ Failed to create database tables")
        sys.exit(1)
    
    # Database bilgilerini göster
    print("\n3️⃣ Database information:")
    info = get_database_info(database_url)
    if info:
        print(f"Database URL: {info['database_url']}")
        print("Table counts:")
        for table, count in info['tables'].items():
            print(f"  - {table}: {count} records")
    
    print("\n✅ Database setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Set your API credentials in .env file")
    print("2. Enable integrations by setting TRENDYOL_ENABLED=true etc.")
    print("3. Run the integration tests")

if __name__ == "__main__":
    main()