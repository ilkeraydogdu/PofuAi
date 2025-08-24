#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Initialization Script
Veritabanını ve tabloları oluşturur
"""

import os
import sqlite3
import sys

# Proje kök dizini
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

def create_database():
    """SQLite veritabanını oluştur"""
    db_dir = os.path.join(ROOT_DIR, 'storage', 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    db_path = os.path.join(db_dir, 'pofuai_dev.db')
    
    print(f"Creating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Products tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price DECIMAL(10,2),
            stock INTEGER DEFAULT 0,
            category_id INTEGER,
            user_id INTEGER,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Categories tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(255) UNIQUE,
            parent_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Orders tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount DECIMAL(10,2),
            status VARCHAR(50) DEFAULT 'pending',
            payment_method VARCHAR(50),
            shipping_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Notifications tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(255),
            message TEXT,
            type VARCHAR(50),
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Sessions tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id VARCHAR(255) PRIMARY KEY,
            user_id INTEGER,
            ip_address VARCHAR(45),
            user_agent TEXT,
            payload TEXT,
            last_activity INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Settings tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key VARCHAR(255) UNIQUE NOT NULL,
            value TEXT,
            type VARCHAR(50) DEFAULT 'string',
            group_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Audit logs tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action VARCHAR(255),
            model VARCHAR(100),
            model_id INTEGER,
            old_values TEXT,
            new_values TEXT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Files tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename VARCHAR(255) NOT NULL,
            original_name VARCHAR(255),
            mime_type VARCHAR(100),
            size INTEGER,
            path TEXT,
            url TEXT,
            type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Messages tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            subject VARCHAR(255),
            content TEXT,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    ''')
    
    # İndeksler oluştur
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)')
    
    # Varsayılan admin kullanıcı ekle
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, name, email, password, role, is_active)
        VALUES (1, 'Admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY3pp/eS/gI4pBe', 'admin', 1)
    ''')
    
    # Varsayılan kategoriler ekle
    categories = [
        ('Elektronik', 'elektronik'),
        ('Giyim', 'giyim'),
        ('Ev & Yaşam', 'ev-yasam'),
        ('Kitap', 'kitap'),
        ('Spor', 'spor')
    ]
    
    for name, slug in categories:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (name, slug)
            VALUES (?, ?)
        ''', (name, slug))
    
    # Varsayılan ayarlar ekle
    settings = [
        ('site_name', 'PofuAI', 'string', 'general'),
        ('site_description', 'AI-Powered E-Commerce Platform', 'string', 'general'),
        ('site_url', 'http://localhost:5000', 'string', 'general'),
        ('admin_email', 'admin@example.com', 'string', 'general'),
        ('items_per_page', '20', 'integer', 'general'),
        ('currency', 'TRY', 'string', 'general'),
        ('timezone', 'Europe/Istanbul', 'string', 'general'),
        ('maintenance_mode', 'false', 'boolean', 'general')
    ]
    
    for key, value, type_, group in settings:
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value, type, group_name)
            VALUES (?, ?, ?, ?)
        ''', (key, value, type_, group))
    
    conn.commit()
    conn.close()
    
    print("✅ Database created successfully!")
    print(f"📁 Database location: {db_path}")
    print("👤 Default admin credentials:")
    print("   Email: admin@example.com")
    print("   Password: password123")
    
    return True

if __name__ == "__main__":
    try:
        create_database()
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)