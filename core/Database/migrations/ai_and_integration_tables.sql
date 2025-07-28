-- AI ve Entegrasyon Sistemi Tabloları
-- =====================================

-- AI Şablon tablosu
CREATE TABLE IF NOT EXISTS ai_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    template_type VARCHAR(50) NOT NULL,
    content_data JSON,
    file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_template (user_id, template_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- AI Ürün düzenleme logları
CREATE TABLE IF NOT EXISTS ai_product_edits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    edit_type VARCHAR(50),
    edit_data JSON,
    before_data JSON,
    after_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_edits (product_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Kullanıcı aktiviteleri
CREATE TABLE IF NOT EXISTS user_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    activity_data JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_activity (user_id, activity_type, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Kullanıcı tercihleri
CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_preference (user_id, preference_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- AI kullanım logları
CREATE TABLE IF NOT EXISTS ai_usage_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    request_data JSON,
    response_data JSON,
    processing_time FLOAT,
    tokens_used INT DEFAULT 0,
    cost DECIMAL(10, 4) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_ai_usage (user_id, service_type, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Entegrasyonlar tablosu
CREATE TABLE IF NOT EXISTS integrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    integration_type VARCHAR(50) NOT NULL, -- marketplace, ecommerce, accounting, shipping, social
    integration_name VARCHAR(100) NOT NULL, -- trendyol, shopify, logo, yurtici, facebook
    config JSON, -- API keys, secrets, endpoints vb.
    is_active BOOLEAN DEFAULT FALSE,
    last_connected_at TIMESTAMP NULL,
    last_sync_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_integrations (user_id, integration_type, is_active),
    INDEX idx_integration_name (integration_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ürün eşleştirmeleri (internal <-> external)
CREATE TABLE IF NOT EXISTS product_mappings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    integration_id INT NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    external_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (integration_id) REFERENCES integrations(id) ON DELETE CASCADE,
    UNIQUE KEY unique_product_mapping (product_id, integration_id),
    INDEX idx_external_id (external_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sipariş tablosu (entegrasyonlardan gelen)
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    integration_id INT NOT NULL,
    external_order_id VARCHAR(255) NOT NULL,
    order_number VARCHAR(100),
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    customer_phone VARCHAR(50),
    shipping_address JSON,
    billing_address JSON,
    items JSON, -- Sipariş kalemleri
    subtotal DECIMAL(10, 2) DEFAULT 0,
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'TRY',
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    shipping_method VARCHAR(100),
    shipping_tracking_number VARCHAR(255),
    status VARCHAR(50) NOT NULL, -- pending, processing, shipped, delivered, cancelled, refunded
    notes TEXT,
    order_date TIMESTAMP NOT NULL,
    shipped_date TIMESTAMP NULL,
    delivered_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (integration_id) REFERENCES integrations(id) ON DELETE CASCADE,
    UNIQUE KEY unique_external_order (integration_id, external_order_id),
    INDEX idx_user_orders (user_id, status, order_date),
    INDEX idx_order_number (order_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Senkronizasyon logları
CREATE TABLE IF NOT EXISTS sync_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    integration_id INT,
    sync_type VARCHAR(50) NOT NULL, -- products, orders, stock, price
    sync_direction VARCHAR(10) DEFAULT 'both', -- in, out, both
    total_items INT DEFAULT 0,
    successful_items INT DEFAULT 0,
    failed_items INT DEFAULT 0,
    sync_results JSON,
    error_details JSON,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NULL,
    duration_seconds INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (integration_id) REFERENCES integrations(id) ON DELETE SET NULL,
    INDEX idx_sync_logs (user_id, sync_type, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Entegrasyon webhook'ları
CREATE TABLE IF NOT EXISTS integration_webhooks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    integration_id INT NOT NULL,
    webhook_url VARCHAR(500) NOT NULL,
    webhook_secret VARCHAR(255),
    events JSON, -- Hangi eventler için webhook çağrılacak
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP NULL,
    failure_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (integration_id) REFERENCES integrations(id) ON DELETE CASCADE,
    INDEX idx_webhook_active (integration_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- AI modeli performans metrikleri
CREATE TABLE IF NOT EXISTS ai_model_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    metric_value FLOAT NOT NULL,
    metadata JSON,
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_metrics (model_name, metric_type, measured_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Kullanıcı AI kotaları
CREATE TABLE IF NOT EXISTS user_ai_quotas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    quota_type VARCHAR(50) NOT NULL, -- template_generation, product_editing, api_calls
    quota_limit INT NOT NULL,
    used_quota INT DEFAULT 0,
    reset_period VARCHAR(20) DEFAULT 'monthly', -- daily, weekly, monthly
    last_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_quota (user_id, quota_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Entegrasyon hata logları
CREATE TABLE IF NOT EXISTS integration_error_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    integration_id INT NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    error_details JSON,
    request_data JSON,
    response_data JSON,
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (integration_id) REFERENCES integrations(id) ON DELETE CASCADE,
    INDEX idx_integration_errors (integration_id, error_type, occurred_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Varsayılan AI kotaları ekle
INSERT INTO user_ai_quotas (user_id, quota_type, quota_limit) 
SELECT id, 'template_generation', 100 FROM users WHERE role = 'user'
ON DUPLICATE KEY UPDATE quota_limit = 100;

INSERT INTO user_ai_quotas (user_id, quota_type, quota_limit) 
SELECT id, 'template_generation', 1000 FROM users WHERE role = 'premium'
ON DUPLICATE KEY UPDATE quota_limit = 1000;

INSERT INTO user_ai_quotas (user_id, quota_type, quota_limit) 
SELECT id, 'template_generation', -1 FROM users WHERE role IN ('admin', 'seller')
ON DUPLICATE KEY UPDATE quota_limit = -1; -- Sınırsız

-- Örnek entegrasyonlar (demo için)
INSERT INTO integrations (user_id, integration_type, integration_name, config, is_active) VALUES
(1, 'marketplace', 'trendyol', '{"api_key": "demo_key", "api_secret": "demo_secret", "seller_id": "12345"}', FALSE),
(1, 'marketplace', 'hepsiburada', '{"username": "demo_user", "password": "demo_pass", "merchant_id": "67890"}', FALSE),
(1, 'ecommerce', 'shopify', '{"shop_domain": "demo.myshopify.com", "api_key": "demo_key", "password": "demo_pass"}', FALSE),
(1, 'accounting', 'parasut', '{"company_id": "12345", "client_id": "demo_client", "client_secret": "demo_secret"}', FALSE),
(1, 'shipping', 'yurtici', '{"username": "demo", "password": "demo", "customer_number": "12345"}', FALSE)
ON DUPLICATE KEY UPDATE config = VALUES(config);