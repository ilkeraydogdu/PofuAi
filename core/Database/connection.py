"""
MySQL Veritabanı Bağlantı Yöneticisi
Connection pool ve hata yönetimi ile güvenli bağlantı
"""

try:
    import mysql.connector
    from mysql.connector import pooling
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

import logging
import os
import sqlite3
from contextlib import contextmanager

class DatabaseConnection:
    """Veritabanı bağlantı yöneticisi"""
    
    _instance = None
    _pool = None
    _config = None
    _conn = None
    _driver = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._config:
            self._load_config()
            self._create_connection()
    
    def _load_config(self):
        """Veritabanı konfigürasyonunu yükle"""
        try:
            # Config dosyasından yükle
            from core.Config.config import get_config
            config = get_config()
            
            self._driver = config.get('database.driver', 'sqlite')
            
            if self._driver == 'mysql':
                self._config = {
                    'host': config.get('database.host', 'localhost'),
                    'user': config.get('database.username', 'root'),
                    'password': config.get('database.password', ''),
                    'database': config.get('database.database', 'pofuai'),
                    'charset': 'utf8mb4',
                    'collation': 'utf8mb4_unicode_ci',
                    'autocommit': True,
                    'pool_name': 'pofuai_pool',
                    'pool_size': 10,
                    'pool_reset_session': True
                }
            else:  # sqlite
                # Config'den tam yol al
                db_path = config.get('database.database_path', None)
                
                if not db_path:
                    # Varsayılan yol
                    app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    db_path = os.path.join(app_root, 'storage', 'database', 'pofuai_dev.db')
                
                self._config = {
                    'database': db_path,
                }
                
        except Exception as e:
            logging.error(f"Konfigürasyon yükleme hatası: {e}")
            # Varsayılan değerlerle devam et
            self._driver = 'sqlite'
            app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self._config = {
                'database': os.path.join(app_root, 'storage', 'database', 'pofuai_dev.db'),
            }
    
    def _create_connection(self):
        """Veritabanı bağlantısı oluştur"""
        try:
            if self._driver == 'mysql' and MYSQL_AVAILABLE:
                self._create_pool()
            else:  # sqlite
                db_path = self._config['database']
                
                # Dizin yoksa oluştur
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                
                # SQLite bağlantısı oluştur
                self._conn = sqlite3.connect(db_path, check_same_thread=False)
                self._conn.row_factory = sqlite3.Row
                
                # SQLite'ı başlat - basit şema kontrol et
                self._init_sqlite_schema()
                
                logging.info(f"SQLite veritabanı bağlantısı başarıyla oluşturuldu: {db_path}")
                
        except Exception as e:
            logging.error(f"Veritabanı bağlantı hatası: {e}")
            # Demo modunda çalış - dummy bağlantı
            self._driver = 'memory'
            self._conn = None
    
    def _init_sqlite_schema(self):
        """SQLite şemasını başlat"""
        try:
            cursor = self._conn.cursor()
            
            # SQLite versiyonunu kontrol et
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()[0]
            logging.info(f"SQLite versiyonu: {version}")
            
            # Tablo var mı kontrol et
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            if not cursor.fetchone():
                logging.info("Users tablosu bulunamadı, oluşturuluyor...")
                
                # Örnek tablo oluştur
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                ''')
                self._conn.commit()
                
                logging.info("Users tablosu oluşturuldu.")
            
            cursor.close()
            
        except Exception as e:
            logging.error(f"SQLite şema başlatma hatası: {e}")
    
    def _create_pool(self):
        """MySQL connection pool oluştur"""
        if not MYSQL_AVAILABLE:
            logging.warning("MySQL connector not available, falling back to SQLite")
            self._driver = 'sqlite'
            return
            
        try:
            self._pool = mysql.connector.pooling.MySQLConnectionPool(**self._config)
            logging.info("MySQL connection pool başarıyla oluşturuldu")
        except mysql.connector.Error as e:
            logging.error(f"MySQL bağlantı hatası: {e}")
            # Demo modunda çalış
            self._driver = 'memory'
            self._pool = None
    
    def get_raw_connection(self):
        """Ham bağlantı döndür"""
        if self._driver == 'sqlite' and self._conn:
            return self._conn
        return None

    def get_cursor(self):
        """Basit cursor döndür (SQLite için)"""
        if self._driver == 'sqlite' and self._conn:
            return self._conn.cursor()
        return None

    @contextmanager
    def get_connection(self):
        """Güvenli bağlantı context manager"""
        connection = None
        try:
            if self._driver == 'mysql' and self._pool:
                connection = self._pool.get_connection()
                yield connection
            elif self._driver == 'sqlite' and self._conn:
                yield self._conn
            else:
                # Demo mod - dummy bağlantı
                yield None
        except Exception as e:
            if connection and self._driver == 'mysql':
                connection.rollback()
            elif self._conn and self._driver == 'sqlite':
                self._conn.rollback()
            logging.error(f"Veritabanı işlem hatası: {e}")
            raise
        finally:
            if connection and self._driver == 'mysql':
                connection.close()
    
    def execute_query(self, query: str, params: tuple = None):
        """Tek sorgu çalıştır"""
        try:
            if self._driver == 'memory':
                # Demo mod - boş liste döndür
                return []
                
            with self.get_connection() as conn:
                if self._driver == 'mysql':
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute(query, params or ())
                    result = cursor.fetchall()
                    cursor.close()
                    return result
                elif self._driver == 'sqlite':
                    if params:
                        cursor = conn.execute(query, params)
                    else:
                        cursor = conn.execute(query)
                    result = cursor.fetchall()
                    return [dict(row) for row in result]
                    
        except Exception as e:
            logging.error(f"Sorgu hatası: {query} - {e}")
            return []
    
    def execute_many(self, query: str, params_list: list) -> int:
        """Çoklu sorgu çalıştır"""
        try:
            if self._driver == 'memory':
                # Demo mod
                return 0
                
            with self.get_connection() as conn:
                if self._driver == 'mysql':
                    cursor = conn.cursor()
                    cursor.executemany(query, params_list)
                    conn.commit()
                    rowcount = cursor.rowcount
                    cursor.close()
                    return rowcount
                elif self._driver == 'sqlite':
                    cursor = conn.executemany(query, params_list)
                    conn.commit()
                    return cursor.rowcount
                    
        except Exception as e:
            logging.error(f"Çoklu sorgu hatası: {e}")
            return 0
    
    def execute_transaction(self, queries: list) -> bool:
        """Transaction ile çoklu sorgu çalıştır"""
        try:
            if self._driver == 'memory':
                # Demo mod
                return True
                
            with self.get_connection() as conn:
                if self._driver == 'mysql':
                    cursor = conn.cursor()
                    for query, params in queries:
                        cursor.execute(query, params or ())
                    conn.commit()
                    cursor.close()
                    return True
                elif self._driver == 'sqlite':
                    for query, params in queries:
                        conn.execute(query, params or ())
                    conn.commit()
                    return True
                    
        except Exception as e:
            logging.error(f"Transaction hatası: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Bağlantıyı test et"""
        try:
            if self._driver == 'memory':
                # Demo mod
                return True
                
            with self.get_connection() as conn:
                if self._driver == 'mysql':
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    cursor.close()
                    return True
                elif self._driver == 'sqlite':
                    cursor = conn.execute("SELECT 1")
                    cursor.fetchone()
                    return True
                    
        except Exception as e:
            logging.error(f"Bağlantı testi başarısız: {e}")
            return False
    
    def close_connection(self):
        """Bağlantıyı kapat"""
        try:
            if self._driver == 'mysql' and self._pool:
                self._pool.close()
                logging.info("MySQL connection pool kapatıldı")
            elif self._driver == 'sqlite' and self._conn:
                self._conn.close()
                logging.info("SQLite bağlantısı kapatıldı")
        except Exception as e:
            logging.error(f"Bağlantı kapatma hatası: {e}")

# Global instance (lazy loading)
_db_instance = None

def get_db_connection() -> DatabaseConnection:
    """Veritabanı bağlantısı al"""
    return DatabaseConnection()

def get_connection():
    """Veritabanı bağlantısı al (geriye dönük uyumluluk için)"""
    db = get_db_connection()
    return db.get_raw_connection() 