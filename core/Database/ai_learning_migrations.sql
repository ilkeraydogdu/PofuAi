-- PofuAi Learning Engine Database Migrations
-- AI öğrenme ve geri bildirim sistemi için tablolar

-- Kullanıcı AI geri bildirimleri
CREATE TABLE IF NOT EXISTS ai_user_feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    feedback_type ENUM('rating', 'preference', 'correction', 'suggestion') NOT NULL,
    feedback_data JSON,
    item_id VARCHAR(100),
    item_type VARCHAR(50),
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_feedback_type (feedback_type),
    INDEX idx_created_at (created_at),
    INDEX idx_processed (processed)
);

-- Kullanıcı öğrenme modelleri
CREATE TABLE IF NOT EXISTS user_learning_models (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    model_version VARCHAR(50),
    model_path VARCHAR(500),
    training_data JSON,
    performance_metrics JSON,
    last_trained TIMESTAMP,
    next_training TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_last_trained (last_trained),
    INDEX idx_next_training (next_training)
);

-- Kişiselleştirilmiş öneriler
CREATE TABLE IF NOT EXISTS personalized_recommendations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    recommendation_type VARCHAR(50),
    recommendation_data JSON,
    context JSON,
    score DECIMAL(5,4),
    clicked BOOLEAN DEFAULT FALSE,
    feedback_rating INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_type (recommendation_type),
    INDEX idx_created_at (created_at),
    INDEX idx_score (score)
);

-- Kullanıcı davranış desenleri
CREATE TABLE IF NOT EXISTS user_behavior_patterns (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    pattern_type VARCHAR(50),
    pattern_data JSON,
    confidence_score DECIMAL(5,4),
    validity_period_days INT DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_pattern_type (pattern_type),
    INDEX idx_expires_at (expires_at)
);

-- AI görev kuyruğu
CREATE TABLE IF NOT EXISTS ai_task_queue (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id VARCHAR(36) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    task_data JSON,
    priority INT DEFAULT 5,
    status ENUM('pending', 'processing', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
    progress DECIMAL(5,2) DEFAULT 0,
    result JSON,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    INDEX idx_task_id (task_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_priority_status (priority, status),
    INDEX idx_created_at (created_at)
);

-- Gelişmiş görsel analiz sonuçları
CREATE TABLE IF NOT EXISTS advanced_image_analysis (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    analysis_type VARCHAR(50),
    caption_data JSON,
    quality_metrics JSON,
    aesthetic_scores JSON,
    emotion_data JSON,
    segmentation_data JSON,
    processing_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_image_path (image_path),
    INDEX idx_analysis_type (analysis_type),
    INDEX idx_created_at (created_at)
);

-- Görsel iyileştirme kayıtları
CREATE TABLE IF NOT EXISTS image_enhancements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    original_path VARCHAR(500) NOT NULL,
    enhanced_path VARCHAR(500) NOT NULL,
    enhancement_type VARCHAR(50),
    enhancement_params JSON,
    quality_improvement JSON,
    file_size_original BIGINT,
    file_size_enhanced BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_original_path (original_path),
    INDEX idx_enhancement_type (enhancement_type),
    INDEX idx_created_at (created_at)
);

-- Kullanıcı tercih profilleri
CREATE TABLE IF NOT EXISTS user_preference_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    preference_type VARCHAR(50),
    preference_key VARCHAR(100),
    preference_value JSON,
    confidence DECIMAL(5,4),
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_pref (user_id, preference_type, preference_key),
    INDEX idx_user_id (user_id),
    INDEX idx_preference_type (preference_type),
    INDEX idx_confidence (confidence)
);

-- AI model performans logları
CREATE TABLE IF NOT EXISTS ai_model_performance_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model_type VARCHAR(50),
    model_version VARCHAR(50),
    user_id INT,
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    inference_time_ms INT,
    memory_usage_mb INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_type (model_type),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Gerçek zamanlı işlem metrikleri
CREATE TABLE IF NOT EXISTS realtime_processing_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    metric_date DATE NOT NULL,
    total_tasks INT DEFAULT 0,
    completed_tasks INT DEFAULT 0,
    failed_tasks INT DEFAULT 0,
    cancelled_tasks INT DEFAULT 0,
    avg_processing_time_ms INT,
    max_queue_size INT,
    worker_utilization DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date (metric_date),
    INDEX idx_metric_date (metric_date)
);

-- Trigger: Otomatik pattern expiry
DELIMITER //

CREATE TRIGGER set_pattern_expiry
BEFORE INSERT ON user_behavior_patterns
FOR EACH ROW
BEGIN
    IF NEW.expires_at IS NULL THEN
        SET NEW.expires_at = DATE_ADD(NOW(), INTERVAL NEW.validity_period_days DAY);
    END IF;
END//

DELIMITER ;

-- View: Kullanıcı AI özeti (genişletilmiş)
CREATE OR REPLACE VIEW user_ai_learning_summary AS
SELECT 
    u.user_id,
    COUNT(DISTINCT uf.id) as total_feedbacks,
    COUNT(DISTINCT pr.id) as total_recommendations,
    AVG(pr.score) as avg_recommendation_score,
    COUNT(DISTINCT pr.id) as recommendations_clicked,
    AVG(pr.feedback_rating) as avg_feedback_rating,
    COUNT(DISTINCT bp.id) as behavior_patterns,
    MAX(ulm.last_trained) as last_model_training,
    COUNT(DISTINCT aia.id) as advanced_analyses,
    COUNT(DISTINCT ie.id) as image_enhancements
FROM (SELECT DISTINCT user_id FROM users) u
LEFT JOIN ai_user_feedback uf ON u.user_id = uf.user_id
LEFT JOIN personalized_recommendations pr ON u.user_id = pr.user_id
LEFT JOIN user_behavior_patterns bp ON u.user_id = bp.user_id AND bp.expires_at > NOW()
LEFT JOIN user_learning_models ulm ON u.user_id = ulm.user_id
LEFT JOIN advanced_image_analysis aia ON u.user_id = aia.user_id
LEFT JOIN image_enhancements ie ON u.user_id = ie.user_id
GROUP BY u.user_id;

-- View: AI sistem performansı
CREATE OR REPLACE VIEW ai_system_performance AS
SELECT 
    'task_completion_rate' as metric,
    ROUND(
        (SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 
        2
    ) as value,
    'percentage' as unit
FROM ai_task_queue 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
UNION ALL
SELECT 
    'avg_task_duration' as metric,
    ROUND(AVG(TIMESTAMPDIFF(SECOND, started_at, completed_at)), 2) as value,
    'seconds' as unit
FROM ai_task_queue 
WHERE status = 'completed' AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
UNION ALL
SELECT 
    'recommendation_accuracy' as metric,
    ROUND(AVG(CASE WHEN clicked = TRUE THEN 1 ELSE 0 END) * 100, 2) as value,
    'percentage' as unit
FROM personalized_recommendations 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
UNION ALL
SELECT 
    'user_satisfaction' as metric,
    ROUND(AVG(feedback_rating), 2) as value,
    'rating' as unit
FROM personalized_recommendations 
WHERE feedback_rating IS NOT NULL AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY);

-- İndeksler
CREATE INDEX idx_task_queue_composite ON ai_task_queue(user_id, status, priority);
CREATE INDEX idx_recommendations_composite ON personalized_recommendations(user_id, created_at, score);
CREATE INDEX idx_feedback_composite ON ai_user_feedback(user_id, feedback_type, processed);
CREATE INDEX idx_analysis_composite ON advanced_image_analysis(user_id, analysis_type, created_at);