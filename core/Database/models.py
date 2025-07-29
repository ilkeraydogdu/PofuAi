"""
Database Models for Marketplace Integration System
Tüm entegrasyon, ürün, sipariş ve diğer modeller
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Table, Index, UniqueConstraint, CheckConstraint,
    Enum as SQLEnum, DECIMAL, BigInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

Base = declarative_base()

# Association Tables
integration_features = Table(
    'integration_features',
    Base.metadata,
    Column('integration_id', Integer, ForeignKey('integrations.id', ondelete='CASCADE')),
    Column('feature_id', Integer, ForeignKey('features.id', ondelete='CASCADE')),
    Column('enabled', Boolean, default=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

user_integrations = Table(
    'user_integrations',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('integration_id', Integer, ForeignKey('integrations.id', ondelete='CASCADE')),
    Column('is_active', Boolean, default=True),
    Column('connected_at', DateTime, default=datetime.utcnow)
)

# Enums
class IntegrationType(Enum):
    MARKETPLACE = "marketplace"
    E_COMMERCE = "e_commerce"
    E_INVOICE = "e_invoice"
    ACCOUNTING = "accounting"
    ERP = "erp"
    CARGO = "cargo"
    FULFILLMENT = "fulfillment"
    PAYMENT = "payment"
    SMS = "sms"
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"

class IntegrationStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"
    SUSPENDED = "suspended"
    MAINTENANCE = "maintenance"

class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    RETURNED = "returned"

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class SyncStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


# Main Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    company_name = Column(String(255))
    tax_number = Column(String(50))
    phone = Column(String(20))
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    integrations = relationship('Integration', secondary=user_integrations, back_populates='users')
    api_keys = relationship('ApiKey', back_populates='user', cascade='all, delete-orphan')
    products = relationship('Product', back_populates='user', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')
    sync_logs = relationship('SyncLog', back_populates='user')
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
    )


class Integration(Base):
    __tablename__ = 'integrations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    type = Column(SQLEnum(IntegrationType), nullable=False)
    status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.INACTIVE)
    description = Column(Text)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    documentation_url = Column(String(500))
    api_base_url = Column(String(500))
    sandbox_url = Column(String(500))
    is_premium = Column(Boolean, default=False)
    is_beta = Column(Boolean, default=False)
    supported_countries = Column(JSON, default=list)
    supported_currencies = Column(JSON, default=list)
    rate_limits = Column(JSON)  # {"requests_per_minute": 60, "requests_per_day": 10000}
    webhook_supported = Column(Boolean, default=False)
    oauth_supported = Column(Boolean, default=False)
    api_key_required = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship('User', secondary=user_integrations, back_populates='integrations')
    features = relationship('Feature', secondary=integration_features, back_populates='integrations')
    credentials = relationship('IntegrationCredential', back_populates='integration', cascade='all, delete-orphan')
    sync_logs = relationship('SyncLog', back_populates='integration')
    webhooks = relationship('Webhook', back_populates='integration', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_integration_name', 'name'),
        Index('idx_integration_type', 'type'),
        Index('idx_integration_status', 'status'),
    )


class Feature(Base):
    __tablename__ = 'features'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # 'product', 'order', 'inventory', 'reporting', etc.
    is_ai_powered = Column(Boolean, default=False)
    
    # Relationships
    integrations = relationship('Integration', secondary=integration_features, back_populates='features')


class IntegrationCredential(Base):
    __tablename__ = 'integration_credentials'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    integration_id = Column(Integer, ForeignKey('integrations.id', ondelete='CASCADE'), nullable=False)
    api_key = Column(Text)  # Encrypted
    api_secret = Column(Text)  # Encrypted
    access_token = Column(Text)  # Encrypted
    refresh_token = Column(Text)  # Encrypted
    merchant_id = Column(String(255))
    store_id = Column(String(255))
    supplier_id = Column(String(255))
    extra_fields = Column(JSON)  # For integration-specific fields
    is_sandbox = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User')
    integration = relationship('Integration', back_populates='credentials')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'integration_id', 'is_sandbox', name='uq_user_integration_sandbox'),
        Index('idx_credential_user_integration', 'user_id', 'integration_id'),
    )


class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    sku = Column(String(100), nullable=False)
    barcode = Column(String(50))
    name = Column(String(500), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('categories.id'))
    brand = Column(String(255))
    model = Column(String(255))
    price = Column(DECIMAL(10, 2), nullable=False)
    discounted_price = Column(DECIMAL(10, 2))
    cost = Column(DECIMAL(10, 2))
    currency = Column(String(3), default='TRY')
    vat_rate = Column(Integer, default=18)
    stock_quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    weight = Column(Float)  # in kg
    width = Column(Float)   # in cm
    height = Column(Float)  # in cm
    depth = Column(Float)   # in cm
    images = Column(JSON, default=list)  # List of image URLs
    attributes = Column(JSON, default=dict)  # Dynamic attributes
    tags = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='products')
    category = relationship('Category', back_populates='products')
    listings = relationship('ProductListing', back_populates='product', cascade='all, delete-orphan')
    inventory_logs = relationship('InventoryLog', back_populates='product')
    
    @hybrid_property
    def available_stock(self):
        return self.stock_quantity - self.reserved_quantity
    
    __table_args__ = (
        UniqueConstraint('user_id', 'sku', name='uq_user_sku'),
        Index('idx_product_sku', 'sku'),
        Index('idx_product_barcode', 'barcode'),
        Index('idx_product_user', 'user_id'),
    )


class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey('integrations.id'))
    parent_id = Column(Integer, ForeignKey('categories.id'))
    external_id = Column(String(100))  # Category ID in the marketplace
    name = Column(String(255), nullable=False)
    path = Column(Text)  # Full category path like "Electronics > Phones > Smartphones"
    level = Column(Integer, default=0)
    is_leaf = Column(Boolean, default=False)
    attributes = Column(JSON)  # Required/optional attributes for this category
    commission_rate = Column(Float)
    
    # Relationships
    integration = relationship('Integration')
    parent = relationship('Category', remote_side=[id])
    children = relationship('Category', back_populates='parent')
    products = relationship('Product', back_populates='category')
    
    __table_args__ = (
        UniqueConstraint('integration_id', 'external_id', name='uq_integration_category'),
        Index('idx_category_integration', 'integration_id'),
        Index('idx_category_parent', 'parent_id'),
    )


class ProductListing(Base):
    __tablename__ = 'product_listings'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    integration_id = Column(Integer, ForeignKey('integrations.id'), nullable=False)
    external_id = Column(String(255))  # Product ID in the marketplace
    external_url = Column(String(500))
    title = Column(String(500))  # Title used in the marketplace (might differ)
    description = Column(Text)    # Description used in the marketplace
    price = Column(DECIMAL(10, 2))
    stock_quantity = Column(Integer)
    status = Column(String(50))  # 'active', 'inactive', 'pending', 'rejected'
    rejection_reason = Column(Text)
    commission_rate = Column(Float)
    shipping_template_id = Column(String(100))
    last_synced = Column(DateTime)
    sync_status = Column(SQLEnum(SyncStatus), default=SyncStatus.PENDING)
    sync_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship('Product', back_populates='listings')
    integration = relationship('Integration')
    
    __table_args__ = (
        UniqueConstraint('product_id', 'integration_id', name='uq_product_integration'),
        Index('idx_listing_product', 'product_id'),
        Index('idx_listing_integration', 'integration_id'),
        Index('idx_listing_external', 'external_id'),
    )


class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    integration_id = Column(Integer, ForeignKey('integrations.id'))
    external_order_id = Column(String(255))  # Order ID in the marketplace
    order_number = Column(String(100), unique=True, nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    shipping_cost = Column(DECIMAL(10, 2), default=0)
    tax_amount = Column(DECIMAL(10, 2), default=0)
    discount_amount = Column(DECIMAL(10, 2), default=0)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='TRY')
    
    # Customer Information
    customer_name = Column(String(255))
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    customer_tax_number = Column(String(50))
    
    # Shipping Information
    shipping_address = Column(JSON)
    billing_address = Column(JSON)
    shipping_method = Column(String(100))
    tracking_number = Column(String(255))
    cargo_company = Column(String(100))
    
    # Dates
    order_date = Column(DateTime, default=datetime.utcnow)
    payment_date = Column(DateTime)
    shipping_date = Column(DateTime)
    delivery_date = Column(DateTime)
    
    # Additional fields
    notes = Column(Text)
    invoice_number = Column(String(100))
    invoice_url = Column(String(500))
    is_gift = Column(Boolean, default=False)
    gift_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='orders')
    integration = relationship('Integration')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    payments = relationship('Payment', back_populates='order', cascade='all, delete-orphan')
    shipments = relationship('Shipment', back_populates='order', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_order_user', 'user_id'),
        Index('idx_order_integration', 'integration_id'),
        Index('idx_order_external', 'external_order_id'),
        Index('idx_order_number', 'order_number'),
        Index('idx_order_status', 'status'),
        Index('idx_order_date', 'order_date'),
    )


class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    external_product_id = Column(String(255))
    sku = Column(String(100))
    name = Column(String(500), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0)
    tax_amount = Column(DECIMAL(10, 2), default=0)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    commission_amount = Column(DECIMAL(10, 2))
    attributes = Column(JSON)  # Size, color, etc.
    
    # Relationships
    order = relationship('Order', back_populates='items')
    product = relationship('Product')


class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    transaction_id = Column(String(255), unique=True)
    payment_method = Column(String(50))  # 'credit_card', 'debit_card', 'transfer', etc.
    payment_gateway = Column(String(50))  # 'iyzico', 'paytr', 'stripe', etc.
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='TRY')
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    gateway_response = Column(JSON)
    error_message = Column(Text)
    paid_at = Column(DateTime)
    refunded_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship('Order', back_populates='payments')


class Shipment(Base):
    __tablename__ = 'shipments'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    cargo_company = Column(String(100))
    tracking_number = Column(String(255), unique=True)
    tracking_url = Column(String(500))
    status = Column(String(50))  # 'preparing', 'shipped', 'in_transit', 'delivered'
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    delivery_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = relationship('Order', back_populates='shipments')
    tracking_events = relationship('TrackingEvent', back_populates='shipment', cascade='all, delete-orphan')


class TrackingEvent(Base):
    __tablename__ = 'tracking_events'
    
    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey('shipments.id', ondelete='CASCADE'), nullable=False)
    event_date = Column(DateTime, nullable=False)
    status = Column(String(100))
    location = Column(String(255))
    description = Column(Text)
    
    # Relationships
    shipment = relationship('Shipment', back_populates='tracking_events')


class InventoryLog(Base):
    __tablename__ = 'inventory_logs'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    integration_id = Column(Integer, ForeignKey('integrations.id'))
    change_type = Column(String(50))  # 'sale', 'return', 'adjustment', 'restock'
    quantity_change = Column(Integer, nullable=False)  # Positive or negative
    old_quantity = Column(Integer)
    new_quantity = Column(Integer)
    reason = Column(Text)
    reference_id = Column(String(255))  # Order ID, return ID, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    product = relationship('Product', back_populates='inventory_logs')
    integration = relationship('Integration')
    user = relationship('User')


class SyncLog(Base):
    __tablename__ = 'sync_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    integration_id = Column(Integer, ForeignKey('integrations.id'), nullable=False)
    sync_type = Column(String(50))  # 'products', 'orders', 'inventory', 'categories'
    sync_direction = Column(String(20))  # 'import', 'export', 'bidirectional'
    status = Column(SQLEnum(SyncStatus), default=SyncStatus.PENDING)
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    success_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    error_details = Column(JSON)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='sync_logs')
    integration = relationship('Integration', back_populates='sync_logs')
    
    __table_args__ = (
        Index('idx_sync_user_integration', 'user_id', 'integration_id'),
        Index('idx_sync_created', 'created_at'),
    )


class Webhook(Base):
    __tablename__ = 'webhooks'
    
    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey('integrations.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_type = Column(String(100), nullable=False)  # 'order.created', 'product.updated', etc.
    url = Column(String(500), nullable=False)
    secret_key = Column(String(255))  # For webhook signature verification
    is_active = Column(Boolean, default=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_triggered = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    integration = relationship('Integration', back_populates='webhooks')
    user = relationship('User')
    events = relationship('WebhookEvent', back_populates='webhook', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_webhook_integration', 'integration_id'),
        Index('idx_webhook_user', 'user_id'),
        Index('idx_webhook_event', 'event_type'),
    )


class WebhookEvent(Base):
    __tablename__ = 'webhook_events'
    
    id = Column(Integer, primary_key=True)
    webhook_id = Column(Integer, ForeignKey('webhooks.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(String(255), unique=True)
    payload = Column(JSON)
    response_status = Column(Integer)
    response_body = Column(Text)
    error_message = Column(Text)
    attempt_count = Column(Integer, default=1)
    delivered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime)
    
    # Relationships
    webhook = relationship('Webhook', back_populates='events')


class ApiKey(Base):
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    key = Column(String(255), unique=True, nullable=False)
    name = Column(String(100))
    permissions = Column(JSON)  # List of allowed endpoints/operations
    rate_limit = Column(Integer, default=1000)  # Requests per hour
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='api_keys')
    
    __table_args__ = (
        Index('idx_api_key', 'key'),
        Index('idx_api_key_user', 'user_id'),
    )


class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    type = Column(String(50))  # 'order', 'sync', 'error', 'info'
    title = Column(String(255), nullable=False)
    message = Column(Text)
    data = Column(JSON)  # Additional data
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    
    # Relationships
    user = relationship('User')
    
    __table_args__ = (
        Index('idx_notification_user', 'user_id'),
        Index('idx_notification_created', 'created_at'),
        Index('idx_notification_read', 'is_read'),
    )


class Setting(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(JSON)
    category = Column(String(50))  # 'general', 'sync', 'notification', etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'key', name='uq_user_setting'),
        Index('idx_setting_user', 'user_id'),
        Index('idx_setting_key', 'key'),
    )