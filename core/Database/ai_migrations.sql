-- PofuAi AI System Database Migrations
-- AI sistemi için gerekli veritabanı tabloları

-- AI işleme sonuçları tablosu
CREATE TABLE IF NOT EXISTS ai_processing_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    classification JSON,
    objects JSON,
    metadata JSON,
    processing_time DECIMAL(10,3),
    status ENUM('success', 'error', 'processing') DEFAULT 'processing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_image_path (image_path),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- AI kategorilendirme sonuçları tablosu
CREATE TABLE IF NOT EXISTS ai_categorization_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    primary_categories JSON,
    secondary_categories JSON,
    custom_tags JSON,
    confidence_scores JSON,
    methods_used JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_image_path (image_path),
    INDEX idx_created_at (created_at)
);

-- Kullanıcı AI profilleri tablosu
CREATE TABLE IF NOT EXISTS user_ai_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    preferences JSON,
    behavior_patterns JSON,
    content_stats JSON,
    ai_preferences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_updated_at (updated_at)
);

-- Kullanıcı içerik analizi tablosu
CREATE TABLE IF NOT EXISTS user_content_analysis (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    total_images INT DEFAULT 0,
    analysis_period INT DEFAULT 30,
    patterns JSON,
    organization_suggestions JSON,
    personalized_categories JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Depolama organizasyon sonuçları tablosu
CREATE TABLE IF NOT EXISTS storage_organization_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    method ENUM('date', 'category', 'quality', 'hybrid', 'auto') DEFAULT 'auto',
    files_processed INT DEFAULT 0,
    folders_created INT DEFAULT 0,
    files_moved INT DEFAULT 0,
    duplicates_detected INT DEFAULT 0,
    space_saved BIGINT DEFAULT 0,
    processing_time DECIMAL(10,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_method (method),
    INDEX idx_created_at (created_at)
);

-- Depolama temizleme sonuçları tablosu
CREATE TABLE IF NOT EXISTS storage_cleanup_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    duplicates_found INT DEFAULT 0,
    files_removed INT DEFAULT 0,
    space_freed BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Kullanıcı depolama istatistikleri tablosu
CREATE TABLE IF NOT EXISTS user_storage_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    total_files INT DEFAULT 0,
    total_size BIGINT DEFAULT 0,
    duplicates INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_last_updated (last_updated)
);

-- Görsel benzerlik hash'leri tablosu
CREATE TABLE IF NOT EXISTS image_similarity_hashes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    md5_hash VARCHAR(32),
    perceptual_hash VARCHAR(64),
    similarity_hash VARCHAR(64),
    file_size BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_image (user_id, image_path),
    INDEX idx_md5_hash (md5_hash),
    INDEX idx_perceptual_hash (perceptual_hash),
    INDEX idx_similarity_hash (similarity_hash),
    INDEX idx_user_id (user_id)
);

-- AI sistem performans metrikleri tablosu
CREATE TABLE IF NOT EXISTS ai_system_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6),
    metric_data JSON,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metric_name (metric_name),
    INDEX idx_recorded_at (recorded_at)
);

-- Kategori kullanım istatistikleri tablosu
CREATE TABLE IF NOT EXISTS category_usage_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    usage_count INT DEFAULT 1,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_category (user_id, category_name),
    INDEX idx_user_id (user_id),
    INDEX idx_category_name (category_name),
    INDEX idx_usage_count (usage_count)
);

-- AI öğrenme verileri tablosu (model eğitimi için)
CREATE TABLE IF NOT EXISTS ai_training_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    image_path VARCHAR(500),
    ground_truth_categories JSON,
    predicted_categories JSON,
    user_feedback JSON,
    confidence_score DECIMAL(5,4),
    training_set ENUM('train', 'validation', 'test') DEFAULT 'train',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_training_set (training_set),
    INDEX idx_confidence_score (confidence_score)
);

-- Kullanıcı AI etkileşim geçmişi tablosu
CREATE TABLE IF NOT EXISTS user_ai_interactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    interaction_type ENUM('image_process', 'categorize', 'organize', 'cleanup', 'search') NOT NULL,
    interaction_data JSON,
    response_time DECIMAL(10,3),
    satisfaction_score TINYINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_interaction_type (interaction_type),
    INDEX idx_created_at (created_at)
);

-- AI sistem konfigürasyonu tablosu
CREATE TABLE IF NOT EXISTS ai_system_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSON,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (config_key),
    INDEX idx_is_active (is_active)
);

-- Başlangıç konfigürasyon verileri
INSERT INTO ai_system_config (config_key, config_value, description) VALUES
('image_processing_enabled', 'true', 'Görsel işleme sistemi aktif/pasif'),
('categorization_enabled', 'true', 'Otomatik kategorilendirme aktif/pasif'),
('storage_optimization_enabled', 'true', 'Depolama optimizasyonu aktif/pasif'),
('duplicate_detection_enabled', 'true', 'Duplicate detection aktif/pasif'),
('max_processing_batch_size', '50', 'Toplu işlemede maksimum dosya sayısı'),
('similarity_threshold', '0.85', 'Benzerlik algılama eşik değeri'),
('auto_categorization_confidence_threshold', '0.7', 'Otomatik kategorilendirme güven eşiği'),
('storage_cleanup_auto_remove', 'false', 'Otomatik duplicate silme'),
('user_profile_analysis_frequency', '7', 'Kullanıcı profil analizi sıklığı (gün)'),
('ai_model_update_frequency', '30', 'AI model güncelleme sıklığı (gün)')
ON DUPLICATE KEY UPDATE 
    config_value = VALUES(config_value),
    updated_at = CURRENT_TIMESTAMP;

-- Varsayılan kategori hiyerarşisi
CREATE TABLE IF NOT EXISTS ai_category_hierarchy (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parent_category VARCHAR(100),
    child_category VARCHAR(100) NOT NULL,
    hierarchy_level TINYINT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_parent_category (parent_category),
    INDEX idx_child_category (child_category),
    INDEX idx_hierarchy_level (hierarchy_level)
);

-- Başlangıç kategori hiyerarşisi verileri
INSERT INTO ai_category_hierarchy (parent_category, child_category, hierarchy_level) VALUES
('people', 'portrait', 2),
('people', 'group', 2),
('people', 'family', 2),
('people', 'friends', 2),
('people', 'wedding', 2),
('people', 'baby', 2),
('people', 'children', 2),
('people', 'professional', 2),
('people', 'selfie', 2),
('people', 'couple', 2),
('people', 'elderly', 2),
('nature', 'landscape', 2),
('nature', 'sunset', 2),
('nature', 'sunrise', 2),
('nature', 'mountains', 2),
('nature', 'forest', 2),
('nature', 'beach', 2),
('nature', 'ocean', 2),
('nature', 'flowers', 2),
('nature', 'trees', 2),
('nature', 'animals', 2),
('nature', 'wildlife', 2),
('nature', 'sky', 2),
('nature', 'clouds', 2),
('nature', 'weather', 2),
('urban', 'city', 2),
('urban', 'buildings', 2),
('urban', 'architecture', 2),
('urban', 'street', 2),
('urban', 'transportation', 2),
('urban', 'cars', 2),
('urban', 'bridges', 2),
('urban', 'nightlife', 2),
('urban', 'downtown', 2),
('urban', 'skyline', 2),
('urban', 'modern', 2),
('urban', 'vintage', 2),
('indoor', 'home', 2),
('indoor', 'kitchen', 2),
('indoor', 'bedroom', 2),
('indoor', 'living_room', 2),
('indoor', 'office', 2),
('indoor', 'restaurant', 2),
('indoor', 'shopping', 2),
('indoor', 'museum', 2),
('indoor', 'library', 2),
('indoor', 'gym', 2),
('indoor', 'hospital', 2),
('indoor', 'school', 2),
('food', 'meal', 2),
('food', 'breakfast', 2),
('food', 'lunch', 2),
('food', 'dinner', 2),
('food', 'dessert', 2),
('food', 'drinks', 2),
('food', 'cooking', 2),
('food', 'restaurant', 2),
('food', 'homemade', 2),
('food', 'healthy', 2),
('food', 'fast_food', 2),
('food', 'gourmet', 2),
('events', 'party', 2),
('events', 'celebration', 2),
('events', 'birthday', 2),
('events', 'holiday', 2),
('events', 'vacation', 2),
('events', 'travel', 2),
('events', 'concert', 2),
('events', 'sports', 2),
('events', 'graduation', 2),
('events', 'meeting', 2),
('events', 'conference', 2),
('events', 'festival', 2)
ON DUPLICATE KEY UPDATE 
    is_active = VALUES(is_active),
    hierarchy_level = VALUES(hierarchy_level);

-- Performans için indeksler
CREATE INDEX idx_ai_processing_user_status ON ai_processing_results(user_id, status);
CREATE INDEX idx_ai_categorization_user_created ON ai_categorization_results(user_id, created_at);
CREATE INDEX idx_storage_org_user_method ON storage_organization_results(user_id, method);
CREATE INDEX idx_similarity_user_hash ON image_similarity_hashes(user_id, md5_hash);
CREATE INDEX idx_category_usage_user_count ON category_usage_stats(user_id, usage_count DESC);
CREATE INDEX idx_ai_interactions_user_type ON user_ai_interactions(user_id, interaction_type);

-- Trigger'lar için stored procedure'lar
DELIMITER //

-- Kategori kullanım istatistiklerini güncelle
CREATE TRIGGER update_category_usage_stats
AFTER INSERT ON ai_categorization_results
FOR EACH ROW
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE category_name VARCHAR(100);
    DECLARE category_cursor CURSOR FOR 
        SELECT JSON_UNQUOTE(JSON_EXTRACT(category, '$.category'))
        FROM JSON_TABLE(NEW.primary_categories, '$[*]' COLUMNS (category JSON PATH '$')) AS t;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN category_cursor;
    category_loop: LOOP
        FETCH category_cursor INTO category_name;
        IF done THEN
            LEAVE category_loop;
        END IF;
        
        INSERT INTO category_usage_stats (user_id, category_name, usage_count, last_used)
        VALUES (NEW.user_id, category_name, 1, NOW())
        ON DUPLICATE KEY UPDATE 
            usage_count = usage_count + 1,
            last_used = NOW();
    END LOOP;
    CLOSE category_cursor;
END//

DELIMITER ;

-- AI sistem sağlık kontrolü için view
CREATE OR REPLACE VIEW ai_system_health AS
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
    'average_processing_time' as metric,
    ROUND(AVG(processing_time), 3) as value,
    'seconds' as unit
FROM ai_processing_results 
WHERE status = 'success' AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
UNION ALL
SELECT 
    'total_images_processed_today' as metric,
    COUNT(*) as value,
    'count' as unit
FROM ai_processing_results 
WHERE DATE(created_at) = CURDATE()
UNION ALL
SELECT 
    'active_users_today' as metric,
    COUNT(DISTINCT user_id) as value,
    'count' as unit
FROM ai_processing_results 
WHERE DATE(created_at) = CURDATE();

-- Kullanıcı AI özeti için view
CREATE OR REPLACE VIEW user_ai_summary AS
SELECT 
    u.user_id,
    COUNT(apr.id) as total_processed,
    COUNT(CASE WHEN apr.status = 'success' THEN 1 END) as successful_processed,
    COUNT(DISTINCT DATE(apr.created_at)) as active_days,
    COALESCE(uss.total_files, 0) as total_files,
    COALESCE(uss.total_size, 0) as total_size,
    COALESCE(uss.duplicates, 0) as duplicates,
    MAX(apr.created_at) as last_activity
FROM (SELECT DISTINCT user_id FROM ai_processing_results) u
LEFT JOIN ai_processing_results apr ON u.user_id = apr.user_id
LEFT JOIN user_storage_stats uss ON u.user_id = uss.user_id
GROUP BY u.user_id, uss.total_files, uss.total_size, uss.duplicates;