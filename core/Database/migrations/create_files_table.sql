-- Files table migration
-- Dosya yönetim sistemi için gerekli tablolar

-- Files table
CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    storage_type ENUM('local', 's3', 'azure', 'gcp') DEFAULT 'local',
    is_public BOOLEAN DEFAULT FALSE,
    download_count INT DEFAULT 0,
    metadata JSON,
    expires_at TIMESTAMP NULL,
    folder_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_filename (filename),
    INDEX idx_file_extension (file_extension),
    INDEX idx_file_hash (file_hash),
    INDEX idx_storage_type (storage_type),
    INDEX idx_is_public (is_public),
    INDEX idx_created_at (created_at),
    INDEX idx_folder_id (folder_id),
    INDEX idx_expires_at (expires_at),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (folder_id) REFERENCES file_folders(id) ON DELETE SET NULL
);

-- File folders table
CREATE TABLE IF NOT EXISTS file_folders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id INT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_is_public (is_public),
    INDEX idx_name (name),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES file_folders(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_user_folder (user_id, name, parent_id)
);

-- File shares table (for sharing files between users)
CREATE TABLE IF NOT EXISTS file_shares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NOT NULL,
    shared_by INT NOT NULL,
    shared_with INT NOT NULL,
    permission ENUM('view', 'download', 'edit') DEFAULT 'view',
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_file_id (file_id),
    INDEX idx_shared_by (shared_by),
    INDEX idx_shared_with (shared_with),
    INDEX idx_expires_at (expires_at),
    
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_with) REFERENCES users(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_file_share (file_id, shared_with)
);

-- Files için composite indexes
CREATE INDEX idx_files_user_type ON files(user_id, file_extension, created_at);
CREATE INDEX idx_files_public_type ON files(is_public, file_extension, created_at);
CREATE INDEX idx_files_size_created ON files(file_size, created_at);

-- File folders için composite indexes  
CREATE INDEX idx_folders_user_parent ON file_folders(user_id, parent_id);
CREATE INDEX idx_folders_public_parent ON file_folders(is_public, parent_id);