-- Advanced AI System Database Migrations
-- Gelişmiş AI sistemi için ek veritabanı tabloları

-- AI şablon sonuçları tablosu
CREATE TABLE IF NOT EXISTS ai_template_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    template_type ENUM('instagram_post', 'instagram_story', 'facebook_post', 'twitter_post', 'linkedin_post', 'telegram_post', 'whatsapp_status') NOT NULL,
    content_data JSON,
    template_path VARCHAR(500),
    processing_time DECIMAL(10,3),
    status ENUM('success', 'error', 'processing') DEFAULT 'processing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_template_type (template_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- AI ürün düzenleme sonuçları tablosu (Admin özel)
CREATE TABLE IF NOT EXISTS ai_product_edits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    edit_instructions JSON,
    edit_results JSON,
    processing_time DECIMAL(10,3),
    status ENUM('success', 'error', 'processing') DEFAULT 'processing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- AI analiz sonuçları tablosu
CREATE TABLE IF NOT EXISTS ai_analysis_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    analysis_data JSON,
    analysis_type VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_analysis_type (analysis_type),
    INDEX idx_created_at (created_at)
);

-- Kullanıcı AI izinleri tablosu
CREATE TABLE IF NOT EXISTS user_ai_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    permission_name VARCHAR(100) NOT NULL,
    granted_by INT,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_permission (user_id, permission_name),
    INDEX idx_user_id (user_id),
    INDEX idx_permission_name (permission_name),
    INDEX idx_is_active (is_active),
    FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE SET NULL
);

-- AI şablon kullanım istatistikleri tablosu
CREATE TABLE IF NOT EXISTS ai_template_usage_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    template_type VARCHAR(50) NOT NULL,
    usage_count INT DEFAULT 1,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_template (user_id, template_type),
    INDEX idx_user_id (user_id),
    INDEX idx_template_type (template_type),
    INDEX idx_usage_count (usage_count)
);

-- AI rol bazlı metrikler tablosu
CREATE TABLE IF NOT EXISTS ai_role_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_role VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6),
    metric_data JSON,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_role (user_role),
    INDEX idx_metric_name (metric_name),
    INDEX idx_recorded_at (recorded_at)
);

-- AI özellik kullanım geçmişi tablosu
CREATE TABLE IF NOT EXISTS ai_feature_usage_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    feature_data JSON,
    execution_time DECIMAL(10,3),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_feature_name (feature_name),
    INDEX idx_success (success),
    INDEX idx_created_at (created_at)
);

-- AI sistem konfigürasyon güncellemeleri
INSERT INTO ai_system_config (config_key, config_value, description) VALUES
('advanced_ai_enabled', 'true', 'Gelişmiş AI sistemi aktif/pasif'),
('template_generation_enabled', 'true', 'Şablon oluşturma sistemi aktif/pasif'),
('product_editing_enabled', 'true', 'AI ürün düzenleme sistemi aktif/pasif'),
('role_based_permissions_enabled', 'true', 'Rol tabanlı izin sistemi aktif/pasif'),
('max_templates_per_user_daily', '50', 'Kullanıcı başına günlük maksimum şablon sayısı'),
('max_product_edits_per_admin_daily', '20', 'Admin başına günlük maksimum ürün düzenleme sayısı'),
('template_storage_path', 'storage/templates', 'Şablon dosyalarının saklanacağı dizin'),
('advanced_ai_cache_enabled', 'true', 'Gelişmiş AI cache sistemi aktif/pasif'),
('ai_model_auto_update', 'false', 'AI modellerinin otomatik güncellenmesi'),
('user_content_analysis_enabled', 'true', 'Kullanıcı içerik analizi aktif/pasif')
ON DUPLICATE KEY UPDATE 
    config_value = VALUES(config_value),
    updated_at = CURRENT_TIMESTAMP;

-- Rol tabanlı varsayılan izinler
INSERT INTO user_ai_permissions (user_id, permission_name, granted_by) 
SELECT 
    u.id, 
    CASE 
        WHEN u.role = 'admin' THEN 'all_permissions'
        WHEN u.role = 'moderator' THEN 'template_generation'
        WHEN u.role = 'editor' THEN 'basic_template_generation'
        ELSE 'basic_template_generation'
    END,
    1
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM user_ai_permissions uap 
    WHERE uap.user_id = u.id
);

-- AI template kategorileri
CREATE TABLE IF NOT EXISTS ai_template_categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    category_description TEXT,
    template_types JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category_name (category_name),
    INDEX idx_is_active (is_active)
);

-- Varsayılan şablon kategorileri
INSERT INTO ai_template_categories (category_name, category_description, template_types) VALUES
('social_media', 'Sosyal medya şablonları', '["instagram_post", "instagram_story", "facebook_post", "twitter_post"]'),
('business', 'İş dünyası şablonları', '["linkedin_post", "business_card", "presentation"]'),
('messaging', 'Mesajlaşma platformları', '["telegram_post", "whatsapp_status"]'),
('e_commerce', 'E-ticaret şablonları', '["product_showcase", "sale_banner", "promotion"]'),
('marketing', 'Pazarlama şablonları', '["advertisement", "campaign", "newsletter"]')
ON DUPLICATE KEY UPDATE 
    category_description = VALUES(category_description),
    template_types = VALUES(template_types),
    updated_at = CURRENT_TIMESTAMP;

-- AI işlem kuyruğu tablosu
CREATE TABLE IF NOT EXISTS ai_processing_queue (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    job_type ENUM('template_generation', 'product_editing', 'content_analysis', 'batch_processing') NOT NULL,
    job_data JSON,
    priority TINYINT DEFAULT 5,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    attempts INT DEFAULT 0,
    max_attempts INT DEFAULT 3,
    scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_job_type (job_type),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_scheduled_at (scheduled_at)
);

-- AI model performans metrikleri
CREATE TABLE IF NOT EXISTS ai_model_performance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    performance_metrics JSON,
    accuracy_score DECIMAL(5,4),
    processing_speed DECIMAL(10,3),
    memory_usage BIGINT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_model_name (model_name),
    INDEX idx_accuracy_score (accuracy_score),
    INDEX idx_is_active (is_active)
);

-- Varsayılan model performans verileri
INSERT INTO ai_model_performance (model_name, model_version, performance_metrics, accuracy_score, processing_speed, memory_usage) VALUES
('resnet-50', '1.0', '{"classification_accuracy": 0.85, "inference_time": 0.12}', 0.8500, 0.120, 500000000),
('yolo-v8', '8.0', '{"detection_accuracy": 0.78, "inference_time": 0.08}', 0.7800, 0.080, 800000000),
('blip-captioning', '1.0', '{"caption_quality": 0.82, "inference_time": 0.25}', 0.8200, 0.250, 1200000000),
('text-generator', '1.0', '{"text_quality": 0.75, "inference_time": 0.18}', 0.7500, 0.180, 600000000)
ON DUPLICATE KEY UPDATE 
    performance_metrics = VALUES(performance_metrics),
    accuracy_score = VALUES(accuracy_score),
    processing_speed = VALUES(processing_speed),
    memory_usage = VALUES(memory_usage),
    last_updated = CURRENT_TIMESTAMP;

-- AI kullanım kotaları tablosu
CREATE TABLE IF NOT EXISTS ai_usage_quotas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    quota_type VARCHAR(100) NOT NULL,
    quota_limit INT NOT NULL,
    quota_used INT DEFAULT 0,
    quota_period ENUM('daily', 'weekly', 'monthly') DEFAULT 'daily',
    reset_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_quota (user_id, quota_type, quota_period),
    INDEX idx_user_id (user_id),
    INDEX idx_quota_type (quota_type),
    INDEX idx_reset_at (reset_at)
);

-- Varsayılan kullanım kotaları
INSERT INTO ai_usage_quotas (user_id, quota_type, quota_limit, quota_period, reset_at) 
SELECT 
    u.id,
    'template_generation',
    CASE 
        WHEN u.role = 'admin' THEN 200
        WHEN u.role = 'moderator' THEN 100
        WHEN u.role = 'editor' THEN 50
        ELSE 20
    END,
    'daily',
    DATE_ADD(CURDATE(), INTERVAL 1 DAY)
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM ai_usage_quotas auq 
    WHERE auq.user_id = u.id AND auq.quota_type = 'template_generation'
);

-- AI feedback tablosu
CREATE TABLE IF NOT EXISTS ai_user_feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    feature_name VARCHAR(100) NOT NULL,
    rating TINYINT CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    suggestion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_feature_name (feature_name),
    INDEX idx_rating (rating),
    INDEX idx_created_at (created_at)
);

-- Performans için ek indeksler
CREATE INDEX idx_ai_template_user_type_created ON ai_template_results(user_id, template_type, created_at);
CREATE INDEX idx_ai_product_edits_user_product ON ai_product_edits(user_id, product_id);
CREATE INDEX idx_ai_analysis_user_type_created ON ai_analysis_results(user_id, analysis_type, created_at);
CREATE INDEX idx_ai_permissions_user_active ON user_ai_permissions(user_id, is_active);
CREATE INDEX idx_ai_queue_status_priority ON ai_processing_queue(status, priority);
CREATE INDEX idx_ai_usage_user_type_period ON ai_usage_quotas(user_id, quota_type, quota_period);

-- Trigger'lar için stored procedure'lar
DELIMITER //

-- Şablon kullanım istatistiklerini güncelle
CREATE TRIGGER update_template_usage_stats
AFTER INSERT ON ai_template_results
FOR EACH ROW
BEGIN
    INSERT INTO ai_template_usage_stats (user_id, template_type, usage_count, last_used)
    VALUES (NEW.user_id, NEW.template_type, 1, NOW())
    ON DUPLICATE KEY UPDATE 
        usage_count = usage_count + 1,
        last_used = NOW();
END//

-- Kullanım kotalarını güncelle
CREATE TRIGGER update_usage_quotas
AFTER INSERT ON ai_template_results
FOR EACH ROW
BEGIN
    UPDATE ai_usage_quotas 
    SET quota_used = quota_used + 1,
        updated_at = NOW()
    WHERE user_id = NEW.user_id 
        AND quota_type = 'template_generation'
        AND quota_period = 'daily'
        AND reset_at > NOW();
END//

-- AI özellik kullanım geçmişi kaydet
CREATE TRIGGER log_ai_feature_usage
AFTER INSERT ON ai_template_results
FOR EACH ROW
BEGIN
    INSERT INTO ai_feature_usage_history (user_id, feature_name, feature_data, execution_time, success)
    VALUES (
        NEW.user_id, 
        'template_generation', 
        JSON_OBJECT('template_type', NEW.template_type, 'status', NEW.status),
        NEW.processing_time,
        NEW.status = 'success'
    );
END//

DELIMITER ;

-- AI sistem sağlık kontrolü için güncellenmiş view
CREATE OR REPLACE VIEW ai_system_health_advanced AS
SELECT 
    'processing_success_rate' as metric,
    ROUND(
        (SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 
        2
    ) as value,
    'percentage' as unit
FROM ai_processing_results 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
UNION ALL
SELECT 
    'template_success_rate' as metric,
    ROUND(
        (SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 
        2
    ) as value,
    'percentage' as unit
FROM ai_template_results 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
UNION ALL
SELECT 
    'average_template_processing_time' as metric,
    ROUND(AVG(processing_time), 3) as value,
    'seconds' as unit
FROM ai_template_results 
WHERE status = 'success' AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
UNION ALL
SELECT 
    'total_templates_generated_today' as metric,
    COUNT(*) as value,
    'count' as unit
FROM ai_template_results 
WHERE DATE(created_at) = CURDATE()
UNION ALL
SELECT 
    'active_ai_users_today' as metric,
    COUNT(DISTINCT user_id) as value,
    'count' as unit
FROM (
    SELECT user_id FROM ai_processing_results WHERE DATE(created_at) = CURDATE()
    UNION
    SELECT user_id FROM ai_template_results WHERE DATE(created_at) = CURDATE()
) as active_users
UNION ALL
SELECT 
    'admin_product_edits_today' as metric,
    COUNT(*) as value,
    'count' as unit
FROM ai_product_edits 
WHERE DATE(created_at) = CURDATE();

-- Kullanıcı AI özeti için güncellenmiş view
CREATE OR REPLACE VIEW user_ai_summary_advanced AS
SELECT 
    u.user_id,
    COUNT(apr.id) as total_processed,
    COUNT(CASE WHEN apr.status = 'success' THEN 1 END) as successful_processed,
    COUNT(atr.id) as total_templates,
    COUNT(CASE WHEN atr.status = 'success' THEN 1 END) as successful_templates,
    COUNT(ape.id) as total_product_edits,
    COUNT(DISTINCT DATE(apr.created_at)) + COUNT(DISTINCT DATE(atr.created_at)) as active_days,
    COALESCE(uss.total_files, 0) as total_files,
    COALESCE(uss.total_size, 0) as total_size,
    COALESCE(uss.duplicates, 0) as duplicates,
    GREATEST(
        COALESCE(MAX(apr.created_at), '1970-01-01'),
        COALESCE(MAX(atr.created_at), '1970-01-01'),
        COALESCE(MAX(ape.created_at), '1970-01-01')
    ) as last_activity
FROM (SELECT DISTINCT user_id FROM ai_processing_results 
      UNION SELECT DISTINCT user_id FROM ai_template_results
      UNION SELECT DISTINCT user_id FROM ai_product_edits) u
LEFT JOIN ai_processing_results apr ON u.user_id = apr.user_id
LEFT JOIN ai_template_results atr ON u.user_id = atr.user_id
LEFT JOIN ai_product_edits ape ON u.user_id = ape.user_id
LEFT JOIN user_storage_stats uss ON u.user_id = uss.user_id
GROUP BY u.user_id, uss.total_files, uss.total_size, uss.duplicates;

-- AI rol bazlı performans view'ı
CREATE OR REPLACE VIEW ai_role_performance AS
SELECT 
    u.role,
    COUNT(atr.id) as template_count,
    AVG(atr.processing_time) as avg_template_time,
    COUNT(ape.id) as product_edit_count,
    AVG(ape.processing_time) as avg_edit_time,
    COUNT(DISTINCT u.user_id) as active_users,
    (COUNT(CASE WHEN atr.status = 'success' THEN 1 END) * 100.0 / NULLIF(COUNT(atr.id), 0)) as template_success_rate,
    (COUNT(CASE WHEN ape.status = 'success' THEN 1 END) * 100.0 / NULLIF(COUNT(ape.id), 0)) as edit_success_rate
FROM users u
LEFT JOIN ai_template_results atr ON u.id = atr.user_id AND atr.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
LEFT JOIN ai_product_edits ape ON u.id = ape.user_id AND ape.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
WHERE u.role IN ('admin', 'moderator', 'editor', 'user')
GROUP BY u.role;

-- Temizlik işlemleri için stored procedure
DELIMITER //

CREATE PROCEDURE CleanupAIData()
BEGIN
    -- 90 gün önceki template sonuçlarını temizle
    DELETE FROM ai_template_results 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
    
    -- 180 gün önceki analiz sonuçlarını temizle
    DELETE FROM ai_analysis_results 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 180 DAY);
    
    -- Tamamlanan işlem kuyruğu kayıtlarını temizle (7 gün)
    DELETE FROM ai_processing_queue 
    WHERE status IN ('completed', 'failed') 
        AND completed_at < DATE_SUB(NOW(), INTERVAL 7 DAY);
    
    -- Süresi dolmuş kotaları sıfırla
    UPDATE ai_usage_quotas 
    SET quota_used = 0, reset_at = CASE 
        WHEN quota_period = 'daily' THEN DATE_ADD(CURDATE(), INTERVAL 1 DAY)
        WHEN quota_period = 'weekly' THEN DATE_ADD(DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY), INTERVAL 1 WEEK)
        WHEN quota_period = 'monthly' THEN DATE_ADD(DATE_SUB(CURDATE(), INTERVAL DAY(CURDATE())-1 DAY), INTERVAL 1 MONTH)
    END
    WHERE reset_at <= NOW();
    
    -- Kullanılmayan template dosyalarını temizle (veritabanında kaydı olmayan)
    -- Bu işlem uygulama seviyesinde yapılmalı
    
END//

DELIMITER ;

-- Otomatik temizlik için event scheduler (opsiyonel)
-- SET GLOBAL event_scheduler = ON;
-- CREATE EVENT IF NOT EXISTS ai_daily_cleanup
-- ON SCHEDULE EVERY 1 DAY
-- STARTS CURRENT_TIMESTAMP
-- DO CALL CleanupAIData();