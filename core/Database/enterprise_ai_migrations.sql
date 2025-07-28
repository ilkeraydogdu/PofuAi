-- Enterprise AI System Database Migrations
-- Kurumsal seviye AI sistemi için kapsamlı veritabanı tabloları

-- ============================================================================
-- ENTEGRASYON YÖNETİMİ TABLOLARI
-- ============================================================================

-- Entegrasyon bağlantıları tablosu
CREATE TABLE IF NOT EXISTS enterprise_integrations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    integration_type ENUM('ecommerce', 'social_media', 'accounting_erp', 'einvoice', 'shipping_logistics', 'payment_systems', 'analytics') NOT NULL,
    integration_name VARCHAR(100) NOT NULL,
    integration_category VARCHAR(100),
    api_credentials JSON,
    settings JSON,
    status ENUM('active', 'inactive', 'error', 'pending') DEFAULT 'pending',
    last_sync TIMESTAMP NULL,
    sync_frequency INT DEFAULT 3600,
    error_count INT DEFAULT 0,
    last_error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_integration_type (integration_type),
    INDEX idx_integration_name (integration_name),
    INDEX idx_status (status),
    INDEX idx_last_sync (last_sync),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Entegrasyon logları tablosu
CREATE TABLE IF NOT EXISTS integration_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    integration_id INT NOT NULL,
    action_type ENUM('connect', 'disconnect', 'sync', 'test', 'webhook', 'error') NOT NULL,
    action_data JSON,
    response_data JSON,
    status ENUM('success', 'error', 'warning') NOT NULL,
    processing_time DECIMAL(10,3),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_integration_id (integration_id),
    INDEX idx_action_type (action_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (integration_id) REFERENCES enterprise_integrations(id) ON DELETE CASCADE
);

-- E-ticaret senkronizasyon tablosu
CREATE TABLE IF NOT EXISTS ecommerce_sync_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    integration_id INT NOT NULL,
    product_id INT,
    external_product_id VARCHAR(255),
    sync_type ENUM('product', 'inventory', 'price', 'order', 'category') NOT NULL,
    sync_direction ENUM('import', 'export', 'bidirectional') NOT NULL,
    sync_data JSON,
    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_status ENUM('success', 'error', 'pending') DEFAULT 'pending',
    error_message TEXT,
    INDEX idx_integration_id (integration_id),
    INDEX idx_product_id (product_id),
    INDEX idx_external_product_id (external_product_id),
    INDEX idx_sync_type (sync_type),
    INDEX idx_last_sync (last_sync),
    FOREIGN KEY (integration_id) REFERENCES enterprise_integrations(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- ============================================================================
-- SOSYAL MEDYA YÖNETİMİ TABLOLARI
-- ============================================================================

-- Sosyal medya hesapları tablosu
CREATE TABLE IF NOT EXISTS social_media_accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    platform ENUM('instagram', 'facebook', 'twitter', 'linkedin', 'tiktok', 'youtube', 'pinterest', 'snapchat', 'telegram', 'whatsapp') NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_id VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP NULL,
    account_data JSON,
    status ENUM('active', 'inactive', 'expired', 'error') DEFAULT 'active',
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_platform (platform),
    INDEX idx_status (status),
    INDEX idx_token_expires_at (token_expires_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Sosyal medya gönderileri tablosu
CREATE TABLE IF NOT EXISTS social_media_posts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    account_id INT NOT NULL,
    template_id INT,
    post_type ENUM('image', 'video', 'carousel', 'story', 'reel') NOT NULL,
    content JSON,
    media_urls JSON,
    scheduled_at TIMESTAMP NULL,
    posted_at TIMESTAMP NULL,
    external_post_id VARCHAR(255),
    status ENUM('draft', 'scheduled', 'posted', 'failed', 'deleted') DEFAULT 'draft',
    engagement_data JSON,
    performance_metrics JSON,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_account_id (account_id),
    INDEX idx_template_id (template_id),
    INDEX idx_status (status),
    INDEX idx_scheduled_at (scheduled_at),
    INDEX idx_posted_at (posted_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES social_media_accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES ai_template_results(id) ON DELETE SET NULL
);

-- İçerik zamanlayıcısı tablosu
CREATE TABLE IF NOT EXISTS content_schedules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    schedule_name VARCHAR(255) NOT NULL,
    content_type ENUM('template_generation', 'product_promotion', 'social_campaign') NOT NULL,
    schedule_data JSON,
    content_config JSON,
    target_accounts JSON,
    frequency ENUM('once', 'daily', 'weekly', 'monthly', 'custom') NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NULL,
    next_execution TIMESTAMP,
    status ENUM('active', 'paused', 'completed', 'error') DEFAULT 'active',
    execution_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    error_count INT DEFAULT 0,
    last_execution TIMESTAMP NULL,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_content_type (content_type),
    INDEX idx_status (status),
    INDEX idx_next_execution (next_execution),
    INDEX idx_start_date (start_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================================
-- KURUMSAL ÜRÜN YÖNETİMİ TABLOLARI
-- ============================================================================

-- Ürün düzenleme geçmişi tablosu (genişletilmiş)
CREATE TABLE IF NOT EXISTS enterprise_product_edits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    edit_type ENUM('ai_enhancement', 'bulk_edit', 'integration_sync', 'scheduled_update') NOT NULL,
    edit_instructions JSON,
    edit_results JSON,
    before_data JSON,
    after_data JSON,
    platforms_affected JSON,
    processing_time DECIMAL(10,3),
    optimization_score DECIMAL(5,2),
    status ENUM('success', 'error', 'processing', 'partial') DEFAULT 'processing',
    error_details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_edit_type (edit_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Ürün SEO optimizasyonu tablosu
CREATE TABLE IF NOT EXISTS product_seo_optimization (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    platform VARCHAR(100) NOT NULL,
    original_title TEXT,
    optimized_title TEXT,
    original_description TEXT,
    optimized_description TEXT,
    meta_keywords JSON,
    seo_score DECIMAL(5,2),
    optimization_suggestions JSON,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product_id (product_id),
    INDEX idx_platform (platform),
    INDEX idx_seo_score (seo_score),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Rekabet analizi tablosu
CREATE TABLE IF NOT EXISTS competitor_analysis (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    competitor_name VARCHAR(255),
    competitor_product_url TEXT,
    competitor_price DECIMAL(10,2),
    competitor_features JSON,
    comparison_data JSON,
    market_position ENUM('leader', 'challenger', 'follower', 'niche') DEFAULT 'follower',
    competitive_advantage JSON,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product_id (product_id),
    INDEX idx_competitor_name (competitor_name),
    INDEX idx_analysis_date (analysis_date),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ============================================================================
-- KURUMSAL ANALİTİK VE RAPORLAMA TABLOLARI
-- ============================================================================

-- Kurumsal metrikler tablosu
CREATE TABLE IF NOT EXISTS enterprise_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    metric_category ENUM('system', 'user', 'integration', 'ai_model', 'business') NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6),
    metric_data JSON,
    aggregation_period ENUM('real_time', 'hourly', 'daily', 'weekly', 'monthly') NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metric_category (metric_category),
    INDEX idx_metric_name (metric_name),
    INDEX idx_aggregation_period (aggregation_period),
    INDEX idx_recorded_at (recorded_at)
);

-- Özel dashboard'lar tablosu
CREATE TABLE IF NOT EXISTS custom_dashboards (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    dashboard_name VARCHAR(255) NOT NULL,
    dashboard_config JSON,
    widget_layout JSON,
    permissions JSON,
    is_public BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_is_public (is_public),
    INDEX idx_is_default (is_default),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Zamanlanmış raporlar tablosu
CREATE TABLE IF NOT EXISTS scheduled_reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    report_name VARCHAR(255) NOT NULL,
    report_type ENUM('analytics', 'performance', 'integration', 'user_activity', 'business_intelligence') NOT NULL,
    report_config JSON,
    schedule_config JSON,
    delivery_method ENUM('email', 'dashboard', 'api', 'file_export') NOT NULL,
    recipients JSON,
    last_generated TIMESTAMP NULL,
    next_generation TIMESTAMP,
    status ENUM('active', 'paused', 'error') DEFAULT 'active',
    generation_count INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_report_type (report_type),
    INDEX idx_status (status),
    INDEX idx_next_generation (next_generation),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================================
-- WEBHOOK VE BİLDİRİM TABLOLARI
-- ============================================================================

-- Webhook konfigürasyonları tablosu
CREATE TABLE IF NOT EXISTS webhook_configurations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    webhook_name VARCHAR(255) NOT NULL,
    webhook_url TEXT NOT NULL,
    event_types JSON,
    headers JSON,
    authentication JSON,
    retry_config JSON,
    status ENUM('active', 'inactive', 'error') DEFAULT 'active',
    last_triggered TIMESTAMP NULL,
    success_count INT DEFAULT 0,
    error_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_last_triggered (last_triggered),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Webhook delivery log tablosu
CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    webhook_id INT NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSON,
    response_code INT,
    response_body TEXT,
    response_time DECIMAL(10,3),
    status ENUM('success', 'failed', 'retrying') NOT NULL,
    attempt_count INT DEFAULT 1,
    delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_webhook_id (webhook_id),
    INDEX idx_event_type (event_type),
    INDEX idx_status (status),
    INDEX idx_delivered_at (delivered_at),
    FOREIGN KEY (webhook_id) REFERENCES webhook_configurations(id) ON DELETE CASCADE
);

-- Gerçek zamanlı bildirimler tablosu
CREATE TABLE IF NOT EXISTS real_time_notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    notification_type ENUM('system', 'integration', 'ai_process', 'user_action', 'error') NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    data JSON,
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    is_read BOOLEAN DEFAULT FALSE,
    action_url TEXT,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_notification_type (notification_type),
    INDEX idx_priority (priority),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at),
    INDEX idx_expires_at (expires_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================================
-- SİSTEM YÖNETİMİ VE YAPILANDIRMA TABLOLARI
-- ============================================================================

-- Sistem konfigürasyonu tablosu (genişletilmiş)
CREATE TABLE IF NOT EXISTS enterprise_system_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_category ENUM('ai_models', 'integrations', 'performance', 'security', 'features') NOT NULL,
    config_key VARCHAR(100) NOT NULL,
    config_value TEXT,
    config_data JSON,
    is_encrypted BOOLEAN DEFAULT FALSE,
    requires_restart BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_category_key (config_category, config_key),
    INDEX idx_config_category (config_category),
    INDEX idx_config_key (config_key)
);

-- AI model performans takibi tablosu (genişletilmiş)
CREATE TABLE IF NOT EXISTS ai_model_performance_tracking (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    performance_metrics JSON,
    accuracy_metrics JSON,
    speed_metrics JSON,
    memory_usage BIGINT,
    gpu_usage DECIMAL(5,2),
    error_rate DECIMAL(5,4),
    usage_count INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    benchmark_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_model_name (model_name),
    INDEX idx_model_version (model_version),
    INDEX idx_last_updated (last_updated),
    INDEX idx_is_active (is_active)
);

-- Sistem yedekleme tablosu
CREATE TABLE IF NOT EXISTS system_backups (
    id INT PRIMARY KEY AUTO_INCREMENT,
    backup_name VARCHAR(255) NOT NULL,
    backup_type ENUM('full', 'incremental', 'differential', 'ai_models', 'user_data') NOT NULL,
    backup_path TEXT,
    backup_size BIGINT,
    compression_type ENUM('none', 'gzip', 'zip', 'tar') DEFAULT 'gzip',
    encryption_enabled BOOLEAN DEFAULT TRUE,
    backup_metadata JSON,
    status ENUM('in_progress', 'completed', 'failed', 'corrupted') DEFAULT 'in_progress',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    error_message TEXT,
    created_by INT,
    INDEX idx_backup_type (backup_type),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at),
    INDEX idx_created_by (created_by),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================================
-- KULLANICI YÖNETİMİ VE ROL TABANLI ÖZELLİKLER
-- ============================================================================

-- Gelişmiş kullanıcı izinleri tablosu
CREATE TABLE IF NOT EXISTS enterprise_user_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    permission_category ENUM('ai_features', 'integrations', 'system_admin', 'reporting', 'user_management') NOT NULL,
    permission_name VARCHAR(100) NOT NULL,
    permission_data JSON,
    granted_by INT,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    usage_limit INT NULL,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_permission (user_id, permission_category, permission_name),
    INDEX idx_user_id (user_id),
    INDEX idx_permission_category (permission_category),
    INDEX idx_permission_name (permission_name),
    INDEX idx_is_active (is_active),
    INDEX idx_expires_at (expires_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Kullanıcı aktivite izleme tablosu (genişletilmiş)
CREATE TABLE IF NOT EXISTS user_activity_tracking (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    activity_type ENUM('login', 'logout', 'api_call', 'feature_usage', 'integration_action', 'admin_action') NOT NULL,
    activity_category VARCHAR(100),
    activity_details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(255),
    request_id VARCHAR(255),
    processing_time DECIMAL(10,3),
    status ENUM('success', 'error', 'warning') DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_activity_type (activity_type),
    INDEX idx_activity_category (activity_category),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_session_id (session_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Kullanıcı kullanım kotaları tablosu (genişletilmiş)
CREATE TABLE IF NOT EXISTS enterprise_usage_quotas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    quota_category ENUM('ai_processing', 'template_generation', 'integration_calls', 'api_requests', 'storage') NOT NULL,
    quota_type VARCHAR(100) NOT NULL,
    quota_limit BIGINT NOT NULL,
    quota_used BIGINT DEFAULT 0,
    quota_period ENUM('hourly', 'daily', 'weekly', 'monthly', 'yearly') DEFAULT 'daily',
    reset_at TIMESTAMP,
    warning_threshold DECIMAL(3,2) DEFAULT 0.8,
    warning_sent BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_quota (user_id, quota_category, quota_type, quota_period),
    INDEX idx_user_id (user_id),
    INDEX idx_quota_category (quota_category),
    INDEX idx_quota_type (quota_type),
    INDEX idx_reset_at (reset_at),
    INDEX idx_is_active (is_active),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================================
-- VERİ EXPORT VE IMPORT TABLOLARI
-- ============================================================================

-- Veri export işlemleri tablosu
CREATE TABLE IF NOT EXISTS data_exports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    export_name VARCHAR(255) NOT NULL,
    export_type ENUM('analytics', 'user_data', 'integration_data', 'ai_results', 'system_logs') NOT NULL,
    export_format ENUM('csv', 'json', 'xml', 'xlsx', 'pdf') NOT NULL,
    export_config JSON,
    file_path TEXT,
    file_size BIGINT,
    compression_enabled BOOLEAN DEFAULT TRUE,
    encryption_enabled BOOLEAN DEFAULT TRUE,
    status ENUM('queued', 'processing', 'completed', 'failed', 'expired') DEFAULT 'queued',
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    expires_at TIMESTAMP,
    download_count INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_export_type (export_type),
    INDEX idx_status (status),
    INDEX idx_expires_at (expires_at),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Veri import işlemleri tablosu
CREATE TABLE IF NOT EXISTS data_imports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    import_name VARCHAR(255) NOT NULL,
    import_type ENUM('products', 'users', 'integrations', 'templates', 'analytics') NOT NULL,
    import_format ENUM('csv', 'json', 'xml', 'xlsx') NOT NULL,
    source_file_path TEXT,
    import_config JSON,
    mapping_config JSON,
    validation_rules JSON,
    status ENUM('queued', 'processing', 'completed', 'failed', 'partial') DEFAULT 'queued',
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    total_records INT DEFAULT 0,
    processed_records INT DEFAULT 0,
    success_records INT DEFAULT 0,
    error_records INT DEFAULT 0,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    error_log TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_import_type (import_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================================
-- VARSAYILAN VERİLER VE KONFİGÜRASYONLAR
-- ============================================================================

-- Enterprise sistem konfigürasyonları
INSERT INTO enterprise_system_config (config_category, config_key, config_value, description) VALUES
('ai_models', 'max_concurrent_processes', '16', 'Maksimum eşzamanlı AI işlem sayısı'),
('ai_models', 'model_cache_size', '2048', 'AI model cache boyutu (MB)'),
('ai_models', 'auto_model_update', 'false', 'AI modellerinin otomatik güncellenmesi'),
('integrations', 'max_integrations_per_user', '50', 'Kullanıcı başına maksimum entegrasyon sayısı'),
('integrations', 'default_sync_interval', '3600', 'Varsayılan senkronizasyon aralığı (saniye)'),
('integrations', 'webhook_timeout', '30', 'Webhook timeout süresi (saniye)'),
('performance', 'max_template_generation_queue', '100', 'Maksimum şablon oluşturma kuyruğu'),
('performance', 'cache_ttl', '1800', 'Cache yaşam süresi (saniye)'),
('performance', 'rate_limit_per_minute', '1000', 'Dakika başına rate limit'),
('security', 'api_key_expiry_days', '90', 'API key geçerlilik süresi (gün)'),
('security', 'session_timeout_minutes', '480', 'Oturum timeout süresi (dakika)'),
('security', 'max_login_attempts', '5', 'Maksimum giriş deneme sayısı'),
('features', 'enterprise_features_enabled', 'true', 'Kurumsal özellikler aktif'),
('features', 'social_media_auto_post', 'true', 'Sosyal medya otomatik paylaşım'),
('features', 'advanced_analytics', 'true', 'Gelişmiş analitik özellikleri')
ON DUPLICATE KEY UPDATE 
    config_value = VALUES(config_value),
    updated_at = CURRENT_TIMESTAMP;

-- Varsayılan kullanıcı kotaları (rol bazlı)
INSERT INTO enterprise_usage_quotas (user_id, quota_category, quota_type, quota_limit, quota_period, reset_at) 
SELECT 
    u.id,
    'template_generation',
    'daily_templates',
    CASE 
        WHEN u.role = 'admin' THEN 500
        WHEN u.role = 'moderator' THEN 200
        WHEN u.role = 'editor' THEN 100
        ELSE 50
    END,
    'daily',
    DATE_ADD(CURDATE(), INTERVAL 1 DAY)
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM enterprise_usage_quotas euq 
    WHERE euq.user_id = u.id AND euq.quota_category = 'template_generation'
);

-- AI processing kotaları
INSERT INTO enterprise_usage_quotas (user_id, quota_category, quota_type, quota_limit, quota_period, reset_at) 
SELECT 
    u.id,
    'ai_processing',
    'daily_processing',
    CASE 
        WHEN u.role = 'admin' THEN 1000
        WHEN u.role = 'moderator' THEN 500
        WHEN u.role = 'editor' THEN 200
        ELSE 100
    END,
    'daily',
    DATE_ADD(CURDATE(), INTERVAL 1 DAY)
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM enterprise_usage_quotas euq 
    WHERE euq.user_id = u.id AND euq.quota_category = 'ai_processing'
);

-- Entegrasyon kotaları
INSERT INTO enterprise_usage_quotas (user_id, quota_category, quota_type, quota_limit, quota_period, reset_at) 
SELECT 
    u.id,
    'integration_calls',
    'hourly_calls',
    CASE 
        WHEN u.role = 'admin' THEN 10000
        WHEN u.role = 'moderator' THEN 5000
        WHEN u.role = 'editor' THEN 2000
        ELSE 1000
    END,
    'hourly',
    DATE_ADD(NOW(), INTERVAL 1 HOUR)
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM enterprise_usage_quotas euq 
    WHERE euq.user_id = u.id AND euq.quota_category = 'integration_calls'
);

-- ============================================================================
-- GELİŞMİŞ VIEW'LAR VE STORED PROCEDURE'LAR
-- ============================================================================

-- Kurumsal dashboard özet view'ı
CREATE OR REPLACE VIEW enterprise_dashboard_summary AS
SELECT 
    'total_users' as metric,
    COUNT(*) as value,
    'count' as unit
FROM users
UNION ALL
SELECT 
    'active_integrations' as metric,
    COUNT(*) as value,
    'count' as unit
FROM enterprise_integrations WHERE status = 'active'
UNION ALL
SELECT 
    'templates_generated_today' as metric,
    COUNT(*) as value,
    'count' as unit
FROM ai_template_results WHERE DATE(created_at) = CURDATE()
UNION ALL
SELECT 
    'social_posts_today' as metric,
    COUNT(*) as value,
    'count' as unit
FROM social_media_posts WHERE DATE(created_at) = CURDATE()
UNION ALL
SELECT 
    'products_edited_today' as metric,
    COUNT(*) as value,
    'count' as unit
FROM enterprise_product_edits WHERE DATE(created_at) = CURDATE()
UNION ALL
SELECT 
    'system_health_score' as metric,
    ROUND(
        (SELECT COUNT(*) FROM enterprise_integrations WHERE status = 'active') * 100.0 / 
        NULLIF((SELECT COUNT(*) FROM enterprise_integrations), 0), 2
    ) as value,
    'percentage' as unit;

-- Entegrasyon durumu özet view'ı
CREATE OR REPLACE VIEW integration_status_summary AS
SELECT 
    integration_type,
    integration_name,
    COUNT(*) as total_connections,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_connections,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_connections,
    AVG(CASE WHEN last_sync IS NOT NULL THEN 
        TIMESTAMPDIFF(HOUR, last_sync, NOW()) ELSE NULL END) as avg_hours_since_sync,
    MAX(last_sync) as last_successful_sync
FROM enterprise_integrations
GROUP BY integration_type, integration_name;

-- Kullanıcı aktivite özet view'ı
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.role,
    COUNT(DISTINCT DATE(uat.created_at)) as active_days_last_30,
    COUNT(uat.id) as total_activities_last_30,
    COUNT(CASE WHEN uat.activity_type = 'api_call' THEN 1 END) as api_calls_last_30,
    COUNT(CASE WHEN uat.activity_type = 'feature_usage' THEN 1 END) as feature_usage_last_30,
    MAX(uat.created_at) as last_activity
FROM users u
LEFT JOIN user_activity_tracking uat ON u.id = uat.user_id 
    AND uat.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY u.id, u.username, u.role;

-- ============================================================================
-- TRIGGER'LAR VE STORED PROCEDURE'LAR
-- ============================================================================

DELIMITER //

-- Entegrasyon durumu değiştiğinde log oluştur
CREATE TRIGGER log_integration_status_change
AFTER UPDATE ON enterprise_integrations
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO integration_logs (
            integration_id, 
            action_type, 
            action_data, 
            status,
            created_at
        ) VALUES (
            NEW.id,
            'status_change',
            JSON_OBJECT(
                'old_status', OLD.status,
                'new_status', NEW.status,
                'error_message', NEW.last_error_message
            ),
            CASE WHEN NEW.status = 'error' THEN 'error' ELSE 'success' END,
            NOW()
        );
    END IF;
END//

-- Kullanıcı aktivitesi kaydedildiğinde kotaları güncelle
CREATE TRIGGER update_usage_quotas_on_activity
AFTER INSERT ON user_activity_tracking
FOR EACH ROW
BEGIN
    -- API call kotasını güncelle
    IF NEW.activity_type = 'api_call' THEN
        UPDATE enterprise_usage_quotas 
        SET quota_used = quota_used + 1,
            updated_at = NOW()
        WHERE user_id = NEW.user_id 
            AND quota_category = 'api_requests'
            AND quota_period = 'hourly'
            AND reset_at > NOW()
            AND is_active = TRUE;
    END IF;
    
    -- Feature usage kotasını güncelle
    IF NEW.activity_type = 'feature_usage' THEN
        UPDATE enterprise_usage_quotas 
        SET quota_used = quota_used + 1,
            updated_at = NOW()
        WHERE user_id = NEW.user_id 
            AND quota_category = 'ai_processing'
            AND quota_period = 'daily'
            AND reset_at > NOW()
            AND is_active = TRUE;
    END IF;
END//

-- Şablon oluşturulduğunda kotaları güncelle
CREATE TRIGGER update_template_quotas
AFTER INSERT ON ai_template_results
FOR EACH ROW
BEGIN
    UPDATE enterprise_usage_quotas 
    SET quota_used = quota_used + 1,
        updated_at = NOW()
    WHERE user_id = NEW.user_id 
        AND quota_category = 'template_generation'
        AND quota_type = 'daily_templates'
        AND reset_at > NOW()
        AND is_active = TRUE;
        
    -- Kotanın %80'ine ulaşıldıysa uyarı gönder
    UPDATE enterprise_usage_quotas 
    SET warning_sent = TRUE
    WHERE user_id = NEW.user_id 
        AND quota_category = 'template_generation'
        AND quota_type = 'daily_templates'
        AND quota_used >= (quota_limit * warning_threshold)
        AND warning_sent = FALSE
        AND is_active = TRUE;
END//

-- Kurumsal temizlik procedure'ü
CREATE PROCEDURE CleanupEnterpriseData()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE cleanup_date DATE;
    
    -- 6 ay önceki tarih
    SET cleanup_date = DATE_SUB(CURDATE(), INTERVAL 6 MONTH);
    
    -- Eski entegrasyon loglarını temizle
    DELETE FROM integration_logs WHERE created_at < cleanup_date;
    
    -- Eski webhook delivery loglarını temizle
    DELETE FROM webhook_deliveries WHERE delivered_at < cleanup_date;
    
    -- Eski kullanıcı aktivite kayıtlarını temizle (1 yıl öncesi)
    DELETE FROM user_activity_tracking WHERE created_at < DATE_SUB(CURDATE(), INTERVAL 1 YEAR);
    
    -- Süresi dolmuş bildirimleri temizle
    DELETE FROM real_time_notifications WHERE expires_at < NOW();
    
    -- Eski export dosyalarını temizle
    DELETE FROM data_exports WHERE status = 'expired' OR expires_at < NOW();
    
    -- Süresi dolmuş kotaları sıfırla
    UPDATE enterprise_usage_quotas 
    SET quota_used = 0, 
        warning_sent = FALSE,
        reset_at = CASE 
            WHEN quota_period = 'hourly' THEN DATE_ADD(NOW(), INTERVAL 1 HOUR)
            WHEN quota_period = 'daily' THEN DATE_ADD(CURDATE(), INTERVAL 1 DAY)
            WHEN quota_period = 'weekly' THEN DATE_ADD(DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY), INTERVAL 1 WEEK)
            WHEN quota_period = 'monthly' THEN DATE_ADD(DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE())-1 DAY), INTERVAL 1 MONTH)
            WHEN quota_period = 'yearly' THEN DATE_ADD(DATE_SUB(CURDATE(), INTERVAL DAYOFYEAR(CURDATE())-1 DAY), INTERVAL 1 YEAR)
        END
    WHERE reset_at <= NOW() AND is_active = TRUE;
    
    -- Sistem metriklerini optimize et
    DELETE FROM enterprise_metrics 
    WHERE recorded_at < DATE_SUB(NOW(), INTERVAL 90 DAY)
        AND aggregation_period = 'real_time';
        
    DELETE FROM enterprise_metrics 
    WHERE recorded_at < DATE_SUB(NOW(), INTERVAL 1 YEAR)
        AND aggregation_period = 'hourly';
END//

DELIMITER ;

-- Otomatik temizlik için event scheduler (opsiyonel)
-- SET GLOBAL event_scheduler = ON;
-- CREATE EVENT IF NOT EXISTS enterprise_daily_cleanup
-- ON SCHEDULE EVERY 1 DAY
-- STARTS CURRENT_TIMESTAMP
-- DO CALL CleanupEnterpriseData();

-- ============================================================================
-- İNDEXLER VE PERFORMANS OPTİMİZASYONU
-- ============================================================================

-- Composite indexler
CREATE INDEX idx_enterprise_integrations_user_type_status ON enterprise_integrations(user_id, integration_type, status);
CREATE INDEX idx_social_media_posts_user_status_scheduled ON social_media_posts(user_id, status, scheduled_at);
CREATE INDEX idx_enterprise_product_edits_product_created ON enterprise_product_edits(product_id, created_at);
CREATE INDEX idx_user_activity_tracking_user_type_created ON user_activity_tracking(user_id, activity_type, created_at);
CREATE INDEX idx_enterprise_metrics_category_name_recorded ON enterprise_metrics(metric_category, metric_name, recorded_at);
CREATE INDEX idx_webhook_deliveries_webhook_status_delivered ON webhook_deliveries(webhook_id, status, delivered_at);

-- Full-text search indexler
ALTER TABLE social_media_posts ADD FULLTEXT(content);
ALTER TABLE real_time_notifications ADD FULLTEXT(title, message);
ALTER TABLE scheduled_reports ADD FULLTEXT(report_name);

-- JSON indexler (MySQL 8.0+)
-- ALTER TABLE enterprise_integrations ADD INDEX idx_integration_settings ((CAST(settings->'$.auto_sync' AS UNSIGNED)));
-- ALTER TABLE social_media_posts ADD INDEX idx_post_content_type ((CAST(content->'$.type' AS CHAR(50))));

-- ============================================================================
-- GÜVENLİK VE YETKİLENDİRME
-- ============================================================================

-- Hassas verilerin şifrelenmesi için trigger'lar
DELIMITER //

CREATE TRIGGER encrypt_integration_credentials
BEFORE INSERT ON enterprise_integrations
FOR EACH ROW
BEGIN
    -- API credentials'ları şifrele (gerçek implementasyonda AES_ENCRYPT kullanın)
    IF NEW.api_credentials IS NOT NULL THEN
        SET NEW.api_credentials = JSON_SET(
            NEW.api_credentials, 
            '$.encrypted', 
            TRUE,
            '$.encrypted_at',
            NOW()
        );
    END IF;
END//

CREATE TRIGGER encrypt_webhook_auth
BEFORE INSERT ON webhook_configurations
FOR EACH ROW
BEGIN
    -- Authentication bilgilerini şifrele
    IF NEW.authentication IS NOT NULL THEN
        SET NEW.authentication = JSON_SET(
            NEW.authentication, 
            '$.encrypted', 
            TRUE,
            '$.encrypted_at',
            NOW()
        );
    END IF;
END//

DELIMITER ;

-- Audit log tablosu
CREATE TABLE IF NOT EXISTS enterprise_audit_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource_type (resource_type),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);