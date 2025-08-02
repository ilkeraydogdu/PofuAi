-- System Settings table migration
-- Sistem ayarları için gerekli tablo

CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) NOT NULL UNIQUE,
    value TEXT NOT NULL,
    type ENUM('string', 'integer', 'float', 'boolean', 'json', 'array') DEFAULT 'string',
    category VARCHAR(50) NOT NULL DEFAULT 'general',
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    updated_by INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_key (`key`),
    INDEX idx_category (category),
    INDEX idx_is_public (is_public),
    INDEX idx_type (type),
    
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- System Settings için composite indexes
CREATE INDEX idx_settings_category_key ON system_settings(category, `key`);
CREATE INDEX idx_settings_public_category ON system_settings(is_public, category);

-- Insert default settings
INSERT INTO system_settings (`key`, value, type, category, description, is_public) VALUES
-- Site Settings
('site_name', 'PofuAi', 'string', 'site', 'Site adı', TRUE),
('site_description', 'E-ticaret ve AI Platformu', 'string', 'site', 'Site açıklaması', TRUE),
('site_url', 'https://pofuai.com', 'string', 'site', 'Site URL', TRUE),
('site_logo', '/static/assets/images/logo.png', 'string', 'site', 'Site logosu', TRUE),
('site_favicon', '/static/assets/images/favicon.ico', 'string', 'site', 'Site favicon', TRUE),
('site_timezone', 'Europe/Istanbul', 'string', 'site', 'Site zaman dilimi', TRUE),
('site_language', 'tr', 'string', 'site', 'Varsayılan dil', TRUE),
('site_currency', 'TRY', 'string', 'site', 'Para birimi', TRUE),

-- Email Settings
('email_smtp_host', 'smtp.gmail.com', 'string', 'email', 'SMTP sunucusu', FALSE),
('email_smtp_port', '587', 'integer', 'email', 'SMTP portu', FALSE),
('email_smtp_username', '', 'string', 'email', 'SMTP kullanıcı adı', FALSE),
('email_smtp_password', '', 'string', 'email', 'SMTP şifresi', FALSE),
('email_from_address', 'noreply@pofuai.com', 'string', 'email', 'Gönderen email adresi', FALSE),
('email_from_name', 'PofuAi', 'string', 'email', 'Gönderen adı', FALSE),

-- Security Settings
('security_password_min_length', '8', 'integer', 'security', 'Minimum şifre uzunluğu', FALSE),
('security_password_require_uppercase', 'true', 'boolean', 'security', 'Büyük harf gerekli', FALSE),
('security_password_require_lowercase', 'true', 'boolean', 'security', 'Küçük harf gerekli', FALSE),
('security_password_require_numbers', 'true', 'boolean', 'security', 'Rakam gerekli', FALSE),
('security_password_require_symbols', 'false', 'boolean', 'security', 'Sembol gerekli', FALSE),
('security_session_timeout', '3600', 'integer', 'security', 'Oturum zaman aşımı (saniye)', FALSE),
('security_max_login_attempts', '5', 'integer', 'security', 'Maksimum giriş denemesi', FALSE),
('security_lockout_duration', '900', 'integer', 'security', 'Hesap kilitleme süresi (saniye)', FALSE),

-- File Upload Settings
('upload_max_file_size', '10485760', 'integer', 'upload', 'Maksimum dosya boyutu (byte)', FALSE),
('upload_allowed_extensions', '["jpg","jpeg","png","gif","pdf","doc","docx"]', 'json', 'upload', 'İzin verilen dosya uzantıları', FALSE),
('upload_path', 'uploads/', 'string', 'upload', 'Upload klasörü', FALSE),
('upload_enable_virus_scan', 'false', 'boolean', 'upload', 'Virüs taraması aktif', FALSE),

-- Cache Settings
('cache_enabled', 'true', 'boolean', 'cache', 'Cache aktif', FALSE),
('cache_default_ttl', '3600', 'integer', 'cache', 'Varsayılan cache süresi (saniye)', FALSE),
('cache_driver', 'redis', 'string', 'cache', 'Cache sürücüsü', FALSE),

-- Database Settings
('database_backup_enabled', 'true', 'boolean', 'database', 'Otomatik yedekleme aktif', FALSE),
('database_backup_frequency', 'daily', 'string', 'database', 'Yedekleme sıklığı', FALSE),
('database_backup_retention', '30', 'integer', 'database', 'Yedek saklama süresi (gün)', FALSE),

-- API Settings
('api_rate_limit_enabled', 'true', 'boolean', 'api', 'API rate limit aktif', FALSE),
('api_rate_limit_requests', '1000', 'integer', 'api', 'Saatlik istek limiti', FALSE),
('api_key_required', 'true', 'boolean', 'api', 'API key gerekli', FALSE),

-- Notification Settings
('notifications_email_enabled', 'true', 'boolean', 'notifications', 'Email bildirimleri aktif', FALSE),
('notifications_sms_enabled', 'false', 'boolean', 'notifications', 'SMS bildirimleri aktif', FALSE),
('notifications_push_enabled', 'true', 'boolean', 'notifications', 'Push bildirimleri aktif', FALSE),

-- Analytics Settings
('analytics_enabled', 'true', 'boolean', 'analytics', 'Analytics aktif', FALSE),
('analytics_google_id', '', 'string', 'analytics', 'Google Analytics ID', FALSE),
('analytics_tracking_enabled', 'true', 'boolean', 'analytics', 'Kullanıcı takibi aktif', FALSE),

-- Maintenance Settings
('maintenance_mode', 'false', 'boolean', 'maintenance', 'Bakım modu aktif', FALSE),
('maintenance_message', 'Site bakımda. Lütfen daha sonra tekrar deneyin.', 'string', 'maintenance', 'Bakım mesajı', FALSE),
('maintenance_allowed_ips', '["127.0.0.1"]', 'json', 'maintenance', 'İzin verilen IP adresleri', FALSE);