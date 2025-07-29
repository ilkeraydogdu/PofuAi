"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2025-01-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('tax_number', sa.String(length=50), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index('idx_user_email', 'users', ['email'], unique=False)
    op.create_index('idx_user_username', 'users', ['username'], unique=False)

    # Create integrations table
    op.create_table('integrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('MARKETPLACE', 'E_COMMERCE', 'E_INVOICE', 'ACCOUNTING', 'ERP', 'CARGO', 'FULFILLMENT', 'PAYMENT', 'SMS', 'EMAIL', 'SOCIAL_MEDIA', name='integrationtype'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'PENDING', 'ERROR', 'SUSPENDED', 'MAINTENANCE', name='integrationstatus'), nullable=True, default='INACTIVE'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('documentation_url', sa.String(length=500), nullable=True),
        sa.Column('api_base_url', sa.String(length=500), nullable=True),
        sa.Column('sandbox_url', sa.String(length=500), nullable=True),
        sa.Column('is_premium', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_beta', sa.Boolean(), nullable=True, default=False),
        sa.Column('supported_countries', sa.JSON(), nullable=True),
        sa.Column('supported_currencies', sa.JSON(), nullable=True),
        sa.Column('rate_limits', sa.JSON(), nullable=True),
        sa.Column('webhook_supported', sa.Boolean(), nullable=True, default=False),
        sa.Column('oauth_supported', sa.Boolean(), nullable=True, default=False),
        sa.Column('api_key_required', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_integration_name', 'integrations', ['name'], unique=False)
    op.create_index('idx_integration_status', 'integrations', ['status'], unique=False)
    op.create_index('idx_integration_type', 'integrations', ['type'], unique=False)

    # Create features table
    op.create_table('features',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('is_ai_powered', sa.Boolean(), nullable=True, default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create categories table
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.Integer(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('path', sa.Text(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True, default=0),
        sa.Column('is_leaf', sa.Boolean(), nullable=True, default=False),
        sa.Column('attributes', sa.JSON(), nullable=True),
        sa.Column('commission_rate', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('integration_id', 'external_id', name='uq_integration_category')
    )
    op.create_index('idx_category_integration', 'categories', ['integration_id'], unique=False)
    op.create_index('idx_category_parent', 'categories', ['parent_id'], unique=False)

    # Create integration_features association table
    op.create_table('integration_features',
        sa.Column('integration_id', sa.Integer(), nullable=True),
        sa.Column('feature_id', sa.Integer(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['feature_id'], ['features.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ondelete='CASCADE')
    )

    # Create user_integrations association table
    op.create_table('user_integrations',
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('integration_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('connected_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create integration_credentials table
    op.create_table('integration_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.Integer(), nullable=False),
        sa.Column('api_key', sa.Text(), nullable=True),
        sa.Column('api_secret', sa.Text(), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('merchant_id', sa.String(length=255), nullable=True),
        sa.Column('store_id', sa.String(length=255), nullable=True),
        sa.Column('supplier_id', sa.String(length=255), nullable=True),
        sa.Column('extra_fields', sa.JSON(), nullable=True),
        sa.Column('is_sandbox', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'integration_id', 'is_sandbox', name='uq_user_integration_sandbox')
    )
    op.create_index('idx_credential_user_integration', 'integration_credentials', ['user_id', 'integration_id'], unique=False)

    # Create products table
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('barcode', sa.String(length=50), nullable=True),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('brand', sa.String(length=255), nullable=True),
        sa.Column('model', sa.String(length=255), nullable=True),
        sa.Column('price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('discounted_price', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('cost', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True, default='TRY'),
        sa.Column('vat_rate', sa.Integer(), nullable=True, default=18),
        sa.Column('stock_quantity', sa.Integer(), nullable=True, default=0),
        sa.Column('reserved_quantity', sa.Integer(), nullable=True, default=0),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('width', sa.Float(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('depth', sa.Float(), nullable=True),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('attributes', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'sku', name='uq_user_sku')
    )
    op.create_index('idx_product_barcode', 'products', ['barcode'], unique=False)
    op.create_index('idx_product_sku', 'products', ['sku'], unique=False)
    op.create_index('idx_product_user', 'products', ['user_id'], unique=False)

    # Create product_listings table
    op.create_table('product_listings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('external_url', sa.String(length=500), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('stock_quantity', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('commission_rate', sa.Float(), nullable=True),
        sa.Column('shipping_template_id', sa.String(length=100), nullable=True),
        sa.Column('last_synced', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'PARTIAL', name='syncstatus'), nullable=True, default='PENDING'),
        sa.Column('sync_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'integration_id', name='uq_product_integration')
    )
    op.create_index('idx_listing_external', 'product_listings', ['external_id'], unique=False)
    op.create_index('idx_listing_integration', 'product_listings', ['integration_id'], unique=False)
    op.create_index('idx_listing_product', 'product_listings', ['product_id'], unique=False)

    # Create orders table
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.Integer(), nullable=True),
        sa.Column('external_order_id', sa.String(length=255), nullable=True),
        sa.Column('order_number', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED', 'RETURNED', name='orderstatus'), nullable=True, default='PENDING'),
        sa.Column('payment_status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'REFUNDED', 'PARTIALLY_REFUNDED', name='paymentstatus'), nullable=True, default='PENDING'),
        sa.Column('subtotal', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('shipping_cost', sa.DECIMAL(precision=10, scale=2), nullable=True, default=0),
        sa.Column('tax_amount', sa.DECIMAL(precision=10, scale=2), nullable=True, default=0),
        sa.Column('discount_amount', sa.DECIMAL(precision=10, scale=2), nullable=True, default=0),
        sa.Column('total_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True, default='TRY'),
        sa.Column('customer_name', sa.String(length=255), nullable=True),
        sa.Column('customer_email', sa.String(length=255), nullable=True),
        sa.Column('customer_phone', sa.String(length=50), nullable=True),
        sa.Column('customer_tax_number', sa.String(length=50), nullable=True),
        sa.Column('shipping_address', sa.JSON(), nullable=True),
        sa.Column('billing_address', sa.JSON(), nullable=True),
        sa.Column('shipping_method', sa.String(length=100), nullable=True),
        sa.Column('tracking_number', sa.String(length=255), nullable=True),
        sa.Column('cargo_company', sa.String(length=100), nullable=True),
        sa.Column('order_date', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('payment_date', sa.DateTime(), nullable=True),
        sa.Column('shipping_date', sa.DateTime(), nullable=True),
        sa.Column('delivery_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('invoice_number', sa.String(length=100), nullable=True),
        sa.Column('invoice_url', sa.String(length=500), nullable=True),
        sa.Column('is_gift', sa.Boolean(), nullable=True, default=False),
        sa.Column('gift_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number')
    )
    op.create_index('idx_order_date', 'orders', ['order_date'], unique=False)
    op.create_index('idx_order_external', 'orders', ['external_order_id'], unique=False)
    op.create_index('idx_order_integration', 'orders', ['integration_id'], unique=False)
    op.create_index('idx_order_number', 'orders', ['order_number'], unique=False)
    op.create_index('idx_order_status', 'orders', ['status'], unique=False)
    op.create_index('idx_order_user', 'orders', ['user_id'], unique=False)

    # Create order_items table
    op.create_table('order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('external_product_id', sa.String(length=255), nullable=True),
        sa.Column('sku', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('discount_amount', sa.DECIMAL(precision=10, scale=2), nullable=True, default=0),
        sa.Column('tax_amount', sa.DECIMAL(precision=10, scale=2), nullable=True, default=0),
        sa.Column('total_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('commission_amount', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('attributes', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create payments table
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.String(length=255), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_gateway', sa.String(length=50), nullable=True),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True, default='TRY'),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'REFUNDED', 'PARTIALLY_REFUNDED', name='paymentstatus'), nullable=True, default='PENDING'),
        sa.Column('gateway_response', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('refunded_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id')
    )

    # Create shipments table
    op.create_table('shipments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('cargo_company', sa.String(length=100), nullable=True),
        sa.Column('tracking_number', sa.String(length=255), nullable=True),
        sa.Column('tracking_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('shipped_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('delivery_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tracking_number')
    )

    # Create tracking_events table
    op.create_table('tracking_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('shipment_id', sa.Integer(), nullable=False),
        sa.Column('event_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['shipment_id'], ['shipments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create inventory_logs table
    op.create_table('inventory_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.Integer(), nullable=True),
        sa.Column('change_type', sa.String(length=50), nullable=True),
        sa.Column('quantity_change', sa.Integer(), nullable=False),
        sa.Column('old_quantity', sa.Integer(), nullable=True),
        sa.Column('new_quantity', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('reference_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create sync_logs table
    op.create_table('sync_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.Integer(), nullable=False),
        sa.Column('sync_type', sa.String(length=50), nullable=True),
        sa.Column('sync_direction', sa.String(length=20), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'PARTIAL', name='syncstatus'), nullable=True, default='PENDING'),
        sa.Column('total_items', sa.Integer(), nullable=True, default=0),
        sa.Column('processed_items', sa.Integer(), nullable=True, default=0),
        sa.Column('success_items', sa.Integer(), nullable=True, default=0),
        sa.Column('failed_items', sa.Integer(), nullable=True, default=0),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sync_created', 'sync_logs', ['created_at'], unique=False)
    op.create_index('idx_sync_user_integration', 'sync_logs', ['user_id', 'integration_id'], unique=False)

    # Create webhooks table
    op.create_table('webhooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('secret_key', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('retry_count', sa.Integer(), nullable=True, default=0),
        sa.Column('max_retries', sa.Integer(), nullable=True, default=3),
        sa.Column('last_triggered', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_webhook_event', 'webhooks', ['event_type'], unique=False)
    op.create_index('idx_webhook_integration', 'webhooks', ['integration_id'], unique=False)
    op.create_index('idx_webhook_user', 'webhooks', ['user_id'], unique=False)

    # Create webhook_events table
    op.create_table('webhook_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('webhook_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.String(length=255), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('attempt_count', sa.Integer(), nullable=True, default=1),
        sa.Column('delivered', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhooks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id')
    )

    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('rate_limit', sa.Integer(), nullable=True, default=1000),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index('idx_api_key', 'api_keys', ['key'], unique=False)
    op.create_index('idx_api_key_user', 'api_keys', ['user_id'], unique=False)

    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notification_created', 'notifications', ['created_at'], unique=False)
    op.create_index('idx_notification_read', 'notifications', ['is_read'], unique=False)
    op.create_index('idx_notification_user', 'notifications', ['user_id'], unique=False)

    # Create settings table
    op.create_table('settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.JSON(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'key', name='uq_user_setting')
    )
    op.create_index('idx_setting_key', 'settings', ['key'], unique=False)
    op.create_index('idx_setting_user', 'settings', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('settings')
    op.drop_table('notifications')
    op.drop_table('api_keys')
    op.drop_table('webhook_events')
    op.drop_table('webhooks')
    op.drop_table('sync_logs')
    op.drop_table('inventory_logs')
    op.drop_table('tracking_events')
    op.drop_table('shipments')
    op.drop_table('payments')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('product_listings')
    op.drop_table('products')
    op.drop_table('integration_credentials')
    op.drop_table('user_integrations')
    op.drop_table('integration_features')
    op.drop_table('categories')
    op.drop_table('features')
    op.drop_table('integrations')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS integrationtype')
    op.execute('DROP TYPE IF EXISTS integrationstatus')
    op.execute('DROP TYPE IF EXISTS orderstatus')
    op.execute('DROP TYPE IF EXISTS paymentstatus')
    op.execute('DROP TYPE IF EXISTS syncstatus')