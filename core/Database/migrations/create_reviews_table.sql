-- Reviews table migration
-- Değerlendirme ve rating sistemi için gerekli tablolar

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    order_id INT NULL,
    rating TINYINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255) NOT NULL,
    comment TEXT NOT NULL,
    pros TEXT,
    cons TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by INT NULL,
    approved_at TIMESTAMP NULL,
    helpful_count INT DEFAULT 0,
    not_helpful_count INT DEFAULT 0,
    images JSON,
    response_text TEXT,
    response_date TIMESTAMP NULL,
    response_by INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_order_id (order_id),
    INDEX idx_rating (rating),
    INDEX idx_is_verified (is_verified),
    INDEX idx_is_approved (is_approved),
    INDEX idx_created_at (created_at),
    INDEX idx_helpful_count (helpful_count),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (response_by) REFERENCES users(id) ON DELETE SET NULL,
    
    UNIQUE KEY unique_user_product_review (user_id, product_id)
);

-- Review helpfulness table (for tracking helpful/not helpful votes)
CREATE TABLE IF NOT EXISTS review_helpfulness (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    user_id INT NOT NULL,
    is_helpful BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_review_id (review_id),
    INDEX idx_user_id (user_id),
    INDEX idx_is_helpful (is_helpful),
    
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_user_review_vote (review_id, user_id)
);

-- Review reports table (for reporting inappropriate reviews)
CREATE TABLE IF NOT EXISTS review_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    reported_by INT NOT NULL,
    reason ENUM('spam', 'inappropriate', 'fake', 'offensive', 'other') NOT NULL,
    description TEXT,
    status ENUM('pending', 'reviewed', 'resolved', 'dismissed') DEFAULT 'pending',
    resolved_by INT NULL,
    resolved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_review_id (review_id),
    INDEX idx_reported_by (reported_by),
    INDEX idx_status (status),
    INDEX idx_reason (reason),
    
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (reported_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Review images table (for storing review images separately)
CREATE TABLE IF NOT EXISTS review_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_review_id (review_id),
    INDEX idx_sort_order (sort_order),
    
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
);

-- Reviews için composite indexes
CREATE INDEX idx_reviews_product_rating ON reviews(product_id, rating, is_approved);
CREATE INDEX idx_reviews_product_approved ON reviews(product_id, is_approved, created_at);
CREATE INDEX idx_reviews_user_approved ON reviews(user_id, is_approved, created_at);
CREATE INDEX idx_reviews_verified_approved ON reviews(is_verified, is_approved, created_at);

-- Update products table to include review statistics
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS average_rating DECIMAL(3,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS review_count INT DEFAULT 0,
ADD INDEX idx_average_rating (average_rating),
ADD INDEX idx_review_count (review_count);