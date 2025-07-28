-- PofuAi Advanced AI Features Database Migrations
-- Gelişmiş AI özellikleri için veritabanı tabloları

-- AI ürün düzenleme kayıtları
CREATE TABLE IF NOT EXISTS ai_product_edits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    ai_enhancements JSON,
    edit_history JSON,
    status ENUM('draft', 'applied', 'rejected') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- AI şablon üretim logları
CREATE TABLE IF NOT EXISTS ai_template_generation_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    platform VARCHAR(50) NOT NULL,
    template_type VARCHAR(100),
    template_data JSON,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_platform (platform),
    INDEX idx_template_type (template_type),
    INDEX idx_created_at (created_at)
);

-- Kullanıcı AI servis seviyeleri
CREATE TABLE IF NOT EXISTS user_ai_service_levels (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    service_level ENUM('basic', 'standard', 'premium', 'enterprise') DEFAULT 'standard',
    custom_limits JSON,
    custom_features JSON,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_service_level (service_level),
    INDEX idx_expires_at (expires_at)
);

-- AI içerik optimizasyon sonuçları
CREATE TABLE IF NOT EXISTS ai_content_optimizations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    content_id INT,
    content_type VARCHAR(50),
    original_content JSON,
    optimized_content JSON,
    optimization_score DECIMAL(5,4),
    applied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_content_id (content_id),
    INDEX idx_content_type (content_type),
    INDEX idx_created_at (created_at)
);

-- Sosyal medya şablonları
CREATE TABLE IF NOT EXISTS ai_social_media_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    template_type VARCHAR(100),
    template_data JSON,
    style VARCHAR(50),
    is_public BOOLEAN DEFAULT TRUE,
    created_by INT,
    usage_count INT DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_platform (platform),
    INDEX idx_template_type (template_type),
    INDEX idx_is_public (is_public),
    INDEX idx_created_by (created_by),
    INDEX idx_rating (rating)
);

-- Kullanıcı şablon kullanımları
CREATE TABLE IF NOT EXISTS user_template_usage (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    template_id INT NOT NULL,
    customizations JSON,
    output_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_template_id (template_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (template_id) REFERENCES ai_social_media_templates(id)
);

-- AI içerik zamanlamaları
CREATE TABLE IF NOT EXISTS ai_content_schedules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    content_id INT,
    platform VARCHAR(50),
    scheduled_time TIMESTAMP NOT NULL,
    content_data JSON,
    ai_suggestions JSON,
    status ENUM('pending', 'published', 'failed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_scheduled_time (scheduled_time),
    INDEX idx_status (status),
    INDEX idx_platform (platform)
);

-- AI model eğitim kayıtları
CREATE TABLE IF NOT EXISTS ai_model_training_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    model_type VARCHAR(100),
    training_data JSON,
    performance_metrics JSON,
    status ENUM('pending', 'training', 'completed', 'failed') DEFAULT 'pending',
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_model_type (model_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- Kullanıcı AI özellik izinleri
CREATE TABLE IF NOT EXISTS user_ai_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    permission_key VARCHAR(100) NOT NULL,
    granted_by INT,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_permission (user_id, permission_key),
    INDEX idx_user_id (user_id),
    INDEX idx_permission_key (permission_key),
    INDEX idx_expires_at (expires_at)
);

-- AI performans metrikleri (genişletilmiş)
CREATE TABLE IF NOT EXISTS ai_performance_metrics_extended (
    id INT PRIMARY KEY AUTO_INCREMENT,
    metric_type VARCHAR(100) NOT NULL,
    user_id INT,
    feature_name VARCHAR(100),
    response_time_ms INT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metric_type (metric_type),
    INDEX idx_user_id (user_id),
    INDEX idx_feature_name (feature_name),
    INDEX idx_created_at (created_at),
    INDEX idx_success (success)
);

-- Varsayılan şablonları ekle
INSERT INTO ai_social_media_templates (name, platform, template_type, template_data, style, created_by) VALUES
('Ürün Tanıtım - Modern', 'instagram', 'product_showcase', '{"layout": "grid", "elements": ["product_image", "title", "price", "cta"]}', 'modern', NULL),
('Ürün Tanıtım - Elegant', 'instagram', 'product_showcase', '{"layout": "minimal", "elements": ["product_image", "brand", "description"]}', 'elegant', NULL),
('Duyuru - Renkli', 'instagram', 'announcement', '{"layout": "centered", "elements": ["announcement_text", "date", "logo"]}', 'playful', NULL),
('Ürün Kartı', 'telegram', 'product_showcase', '{"layout": "card", "elements": ["image", "title", "price", "description", "button"]}', 'modern', NULL),
('Facebook Reklam', 'facebook', 'advertisement', '{"layout": "landscape", "elements": ["hero_image", "headline", "description", "cta"]}', 'modern', NULL)
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

-- AI özellik kullanım istatistikleri view
CREATE OR REPLACE VIEW ai_feature_usage_stats AS
SELECT 
    uai.user_id,
    uai.interaction_type as feature,
    COUNT(*) as usage_count,
    AVG(uai.response_time) as avg_response_time,
    MAX(uai.created_at) as last_used,
    COALESCE(usl.service_level, 'standard') as service_level
FROM user_ai_interactions uai
LEFT JOIN user_ai_service_levels usl ON uai.user_id = usl.user_id
GROUP BY uai.user_id, uai.interaction_type, usl.service_level;

-- Kullanıcı AI özeti view (genişletilmiş)
CREATE OR REPLACE VIEW user_ai_summary_extended AS
SELECT 
    u.user_id,
    u.total_processed,
    u.successful_processed,
    u.active_days,
    u.total_files,
    u.total_size,
    u.duplicates,
    u.last_activity,
    COALESCE(usl.service_level, 'standard') as service_level,
    COUNT(DISTINCT ate.id) as product_edits,
    COUNT(DISTINCT atgl.id) as templates_generated,
    COUNT(DISTINCT aco.id) as content_optimizations
FROM user_ai_summary u
LEFT JOIN user_ai_service_levels usl ON u.user_id = usl.user_id
LEFT JOIN ai_product_edits ate ON u.user_id = ate.user_id
LEFT JOIN ai_template_generation_log atgl ON u.user_id = atgl.user_id
LEFT JOIN ai_content_optimizations aco ON u.user_id = aco.user_id
GROUP BY u.user_id, u.total_processed, u.successful_processed, u.active_days, 
         u.total_files, u.total_size, u.duplicates, u.last_activity, usl.service_level;

-- Trigger: Kullanıcı AI etkileşimlerini logla
DELIMITER //

CREATE TRIGGER log_ai_interaction_extended
AFTER INSERT ON ai_processing_results
FOR EACH ROW
BEGIN
    INSERT INTO user_ai_interactions (user_id, interaction_type, interaction_data, response_time, created_at)
    VALUES (NEW.user_id, 'image_process', JSON_OBJECT('image_path', NEW.image_path), NEW.processing_time, NOW());
END//

CREATE TRIGGER log_template_interaction
AFTER INSERT ON ai_template_generation_log
FOR EACH ROW
BEGIN
    INSERT INTO user_ai_interactions (user_id, interaction_type, interaction_data, response_time, created_at)
    VALUES (NEW.user_id, 'template_generation', JSON_OBJECT('platform', NEW.platform, 'type', NEW.template_type), 0, NOW());
END//

CREATE TRIGGER log_product_edit_interaction
AFTER INSERT ON ai_product_edits
FOR EACH ROW
BEGIN
    INSERT INTO user_ai_interactions (user_id, interaction_type, interaction_data, response_time, created_at)
    VALUES (NEW.user_id, 'product_edit', JSON_OBJECT('product_id', NEW.product_id), 0, NOW());
END//

DELIMITER ;

-- İndeksler ve performans optimizasyonu
CREATE INDEX idx_ai_product_edits_composite ON ai_product_edits(user_id, product_id, status);
CREATE INDEX idx_template_log_composite ON ai_template_generation_log(user_id, platform, created_at);
CREATE INDEX idx_content_schedule_composite ON ai_content_schedules(user_id, scheduled_time, status);
CREATE INDEX idx_performance_metrics_composite ON ai_performance_metrics_extended(user_id, feature_name, created_at);