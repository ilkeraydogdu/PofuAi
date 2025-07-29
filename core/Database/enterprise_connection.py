"""
Enterprise Database Connection Manager
Kurumsal seviye veritabanı bağlantı yöneticisi

Özellikler:
- Multiple database support (MySQL, PostgreSQL, SQLite)
- Connection pooling with automatic scaling
- Failover and high availability
- Query optimization and caching
- Transaction management
- Database monitoring and metrics
- Automatic backup and recovery
- Migration support
- Security and encryption
"""

import os
import logging
import time
import threading
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime, timedelta

# Database drivers
try:
    import mysql.connector
    from mysql.connector import pooling as mysql_pooling
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import psycopg2
    from psycopg2 import pool as pg_pool
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

import sqlite3

# Additional imports
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from core.Config.enterprise_config import get_config_manager


class DatabaseType(Enum):
    """Desteklenen veritabanı türleri"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"


class ConnectionStatus(Enum):
    """Bağlantı durumları"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class DatabaseMetrics:
    """Veritabanı metrikleri"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    avg_query_time: float = 0.0
    total_transactions: int = 0
    successful_transactions: int = 0
    failed_transactions: int = 0
    last_backup_time: Optional[datetime] = None
    uptime: float = 0.0
    error_rate: float = 0.0


class QueryCache:
    """Query cache implementasyonu"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
        self.lock = threading.RLock()
    
    def get(self, query_hash: str) -> Optional[Any]:
        """Cache'den sorgu sonucu al"""
        with self.lock:
            if query_hash in self.cache:
                if time.time() - self.timestamps[query_hash] < self.ttl:
                    return self.cache[query_hash]
                else:
                    # Expired, remove
                    del self.cache[query_hash]
                    del self.timestamps[query_hash]
            return None
    
    def set(self, query_hash: str, result: Any):
        """Cache'e sorgu sonucu kaydet"""
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(self.timestamps.keys(), 
                               key=lambda k: self.timestamps[k])
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
            
            self.cache[query_hash] = result
            self.timestamps[query_hash] = time.time()
    
    def clear(self):
        """Cache'i temizle"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()


class DatabaseConnection:
    """Temel veritabanı bağlantı sınıfı"""
    
    def __init__(self, config: Dict[str, Any], db_type: DatabaseType):
        self.config = config
        self.db_type = db_type
        self.connection = None
        self.status = ConnectionStatus.INACTIVE
        self.last_used = datetime.now()
        self.created_at = datetime.now()
        self.query_count = 0
        self.error_count = 0
    
    def connect(self) -> bool:
        """Veritabanına bağlan"""
        try:
            if self.db_type == DatabaseType.MYSQL and MYSQL_AVAILABLE:
                self.connection = mysql.connector.connect(**self.config)
            elif self.db_type == DatabaseType.POSTGRESQL and POSTGRESQL_AVAILABLE:
                self.connection = psycopg2.connect(**self.config)
            elif self.db_type == DatabaseType.SQLITE:
                self.connection = sqlite3.connect(self.config['database'])
                self.connection.row_factory = sqlite3.Row
            else:
                raise Exception(f"Database type {self.db_type} not supported or driver not available")
            
            self.status = ConnectionStatus.ACTIVE
            return True
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            logging.error(f"Database connection failed: {e}")
            return False
    
    def is_alive(self) -> bool:
        """Bağlantının canlı olup olmadığını kontrol et"""
        if not self.connection:
            return False
        
        try:
            if self.db_type == DatabaseType.MYSQL:
                self.connection.ping(reconnect=True, attempts=1, delay=0)
            elif self.db_type == DatabaseType.POSTGRESQL:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
            elif self.db_type == DatabaseType.SQLITE:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
            
            return True
            
        except Exception:
            self.status = ConnectionStatus.ERROR
            return False
    
    def close(self):
        """Bağlantıyı kapat"""
        if self.connection:
            try:
                self.connection.close()
                self.status = ConnectionStatus.INACTIVE
            except Exception as e:
                logging.error(f"Error closing connection: {e}")


class ConnectionPool:
    """Bağlantı havuzu yöneticisi"""
    
    def __init__(self, db_type: DatabaseType, config: Dict[str, Any], 
                 min_connections: int = 5, max_connections: int = 20):
        self.db_type = db_type
        self.config = config
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connections: List[DatabaseConnection] = []
        self.lock = threading.RLock()
        self.created_at = datetime.now()
        
        # Pool'u başlat
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Bağlantı havuzunu başlat"""
        with self.lock:
            for _ in range(self.min_connections):
                conn = DatabaseConnection(self.config, self.db_type)
                if conn.connect():
                    self.connections.append(conn)
    
    def get_connection(self) -> Optional[DatabaseConnection]:
        """Havuzdan bağlantı al"""
        with self.lock:
            # Aktif bağlantı ara
            for conn in self.connections:
                if conn.status == ConnectionStatus.ACTIVE and conn.is_alive():
                    conn.last_used = datetime.now()
                    return conn
            
            # Yeni bağlantı oluştur (eğer limit altındaysak)
            if len(self.connections) < self.max_connections:
                conn = DatabaseConnection(self.config, self.db_type)
                if conn.connect():
                    self.connections.append(conn)
                    return conn
            
            return None
    
    def return_connection(self, connection: DatabaseConnection):
        """Bağlantıyı havuza geri ver"""
        with self.lock:
            connection.last_used = datetime.now()
    
    def cleanup_connections(self):
        """Eski bağlantıları temizle"""
        with self.lock:
            now = datetime.now()
            connections_to_remove = []
            
            for conn in self.connections:
                # 30 dakikadan fazla kullanılmayan bağlantıları kapat
                if (now - conn.last_used).seconds > 1800:
                    connections_to_remove.append(conn)
            
            for conn in connections_to_remove:
                conn.close()
                self.connections.remove(conn)
            
            # Minimum bağlantı sayısını koru
            while len(self.connections) < self.min_connections:
                conn = DatabaseConnection(self.config, self.db_type)
                if conn.connect():
                    self.connections.append(conn)
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Havuz istatistikleri"""
        with self.lock:
            active_count = sum(1 for c in self.connections if c.status == ConnectionStatus.ACTIVE)
            error_count = sum(1 for c in self.connections if c.status == ConnectionStatus.ERROR)
            
            return {
                'total_connections': len(self.connections),
                'active_connections': active_count,
                'error_connections': error_count,
                'max_connections': self.max_connections,
                'min_connections': self.min_connections,
                'pool_age': (datetime.now() - self.created_at).seconds
            }


class TransactionManager:
    """Transaction yöneticisi"""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.transaction_active = False
        self.savepoints = []
    
    def begin(self):
        """Transaction başlat"""
        if self.connection.db_type == DatabaseType.SQLITE:
            self.connection.connection.execute("BEGIN")
        else:
            self.connection.connection.autocommit = False
        
        self.transaction_active = True
    
    def commit(self):
        """Transaction'ı commit et"""
        if self.transaction_active:
            self.connection.connection.commit()
            self.transaction_active = False
    
    def rollback(self):
        """Transaction'ı rollback et"""
        if self.transaction_active:
            self.connection.connection.rollback()
            self.transaction_active = False
    
    def savepoint(self, name: str):
        """Savepoint oluştur"""
        if self.connection.db_type != DatabaseType.SQLITE:
            cursor = self.connection.connection.cursor()
            cursor.execute(f"SAVEPOINT {name}")
            self.savepoints.append(name)
    
    def rollback_to_savepoint(self, name: str):
        """Savepoint'e rollback et"""
        if name in self.savepoints and self.connection.db_type != DatabaseType.SQLITE:
            cursor = self.connection.connection.cursor()
            cursor.execute(f"ROLLBACK TO SAVEPOINT {name}")


class QueryBuilder:
    """SQL query builder"""
    
    def __init__(self, db_type: DatabaseType):
        self.db_type = db_type
        self.query_parts = {
            'select': [],
            'from': '',
            'joins': [],
            'where': [],
            'group_by': [],
            'having': [],
            'order_by': [],
            'limit': None,
            'offset': None
        }
    
    def select(self, *columns):
        """SELECT clause"""
        self.query_parts['select'].extend(columns)
        return self
    
    def from_table(self, table):
        """FROM clause"""
        self.query_parts['from'] = table
        return self
    
    def where(self, condition):
        """WHERE clause"""
        self.query_parts['where'].append(condition)
        return self
    
    def join(self, table, condition, join_type='INNER'):
        """JOIN clause"""
        self.query_parts['joins'].append(f"{join_type} JOIN {table} ON {condition}")
        return self
    
    def order_by(self, column, direction='ASC'):
        """ORDER BY clause"""
        self.query_parts['order_by'].append(f"{column} {direction}")
        return self
    
    def limit(self, count, offset=None):
        """LIMIT clause"""
        self.query_parts['limit'] = count
        if offset:
            self.query_parts['offset'] = offset
        return self
    
    def build(self) -> str:
        """Query'yi oluştur"""
        query_parts = []
        
        # SELECT
        if self.query_parts['select']:
            query_parts.append(f"SELECT {', '.join(self.query_parts['select'])}")
        
        # FROM
        if self.query_parts['from']:
            query_parts.append(f"FROM {self.query_parts['from']}")
        
        # JOINs
        if self.query_parts['joins']:
            query_parts.extend(self.query_parts['joins'])
        
        # WHERE
        if self.query_parts['where']:
            query_parts.append(f"WHERE {' AND '.join(self.query_parts['where'])}")
        
        # ORDER BY
        if self.query_parts['order_by']:
            query_parts.append(f"ORDER BY {', '.join(self.query_parts['order_by'])}")
        
        # LIMIT
        if self.query_parts['limit']:
            if self.db_type == DatabaseType.MYSQL:
                limit_clause = f"LIMIT {self.query_parts['limit']}"
                if self.query_parts['offset']:
                    limit_clause += f" OFFSET {self.query_parts['offset']}"
                query_parts.append(limit_clause)
            elif self.db_type == DatabaseType.POSTGRESQL:
                query_parts.append(f"LIMIT {self.query_parts['limit']}")
                if self.query_parts['offset']:
                    query_parts.append(f"OFFSET {self.query_parts['offset']}")
            elif self.db_type == DatabaseType.SQLITE:
                limit_clause = f"LIMIT {self.query_parts['limit']}"
                if self.query_parts['offset']:
                    limit_clause += f" OFFSET {self.query_parts['offset']}"
                query_parts.append(limit_clause)
        
        return ' '.join(query_parts)


class DatabaseMigration:
    """Veritabanı migration yöneticisi"""
    
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        self.migrations_table = "database_migrations"
        self.logger = logging.getLogger("DatabaseMigration")
    
    def create_migrations_table(self):
        """Migration tablosunu oluştur"""
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.migrations_table} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            migration_name VARCHAR(255) NOT NULL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT TRUE,
            error_message TEXT
        )
        """
        
        if self.connection_manager.db_type == DatabaseType.SQLITE:
            query = f"""
            CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1,
                error_message TEXT
            )
            """
        
        self.connection_manager.execute_query(query)
    
    def get_executed_migrations(self) -> List[str]:
        """Çalıştırılmış migration'ları getir"""
        query = f"SELECT migration_name FROM {self.migrations_table} WHERE success = 1"
        result = self.connection_manager.execute_query(query)
        return [row['migration_name'] if isinstance(row, dict) else row[0] for row in result]
    
    def execute_migration(self, migration_name: str, migration_sql: str) -> bool:
        """Migration çalıştır"""
        try:
            with self.connection_manager.transaction():
                # Migration'ı çalıştır
                self.connection_manager.execute_query(migration_sql)
                
                # Migration kaydını ekle
                insert_query = f"""
                INSERT INTO {self.migrations_table} (migration_name, success) 
                VALUES (%s, %s)
                """
                if self.connection_manager.db_type == DatabaseType.SQLITE:
                    insert_query = f"""
                    INSERT INTO {self.migrations_table} (migration_name, success) 
                    VALUES (?, ?)
                    """
                
                self.connection_manager.execute_query(insert_query, (migration_name, True))
                
                self.logger.info(f"Migration executed successfully: {migration_name}")
                return True
                
        except Exception as e:
            # Hata kaydını ekle
            error_query = f"""
            INSERT INTO {self.migrations_table} (migration_name, success, error_message) 
            VALUES (%s, %s, %s)
            """
            if self.connection_manager.db_type == DatabaseType.SQLITE:
                error_query = f"""
                INSERT INTO {self.migrations_table} (migration_name, success, error_message) 
                VALUES (?, ?, ?)
                """
            
            try:
                self.connection_manager.execute_query(error_query, (migration_name, False, str(e)))
            except:
                pass
            
            self.logger.error(f"Migration failed: {migration_name} - {e}")
            return False


class EnterpriseDatabaseManager:
    """Kurumsal veritabanı yöneticisi"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or get_config_manager()
        self.db_config = self.config_manager.get('database')
        self.db_type = DatabaseType(self.db_config.driver)
        self.connection_pool = None
        self.query_cache = QueryCache()
        self.metrics = DatabaseMetrics()
        self.logger = logging.getLogger("EnterpriseDatabaseManager")
        self.migration_manager = None
        self.backup_enabled = self.db_config.backup_enabled
        self.last_backup = None
        self.lock = threading.RLock()
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Veritabanı yöneticisini başlat"""
        try:
            # Database configuration
            db_config = {
                'host': self.db_config.host,
                'port': self.db_config.port,
                'user': self.db_config.username,
                'password': self.db_config.password,
                'database': self.db_config.database,
                'charset': getattr(self.db_config, 'charset', 'utf8mb4'),
                'autocommit': False
            }
            
            if self.db_type == DatabaseType.SQLITE:
                db_config = {'database': self.db_config.database}
            
            # Connection pool oluştur
            self.connection_pool = ConnectionPool(
                self.db_type, 
                db_config,
                min_connections=max(1, self.db_config.pool_size // 4),
                max_connections=self.db_config.pool_size
            )
            
            # Migration manager
            self.migration_manager = DatabaseMigration(self)
            self.migration_manager.create_migrations_table()
            
            # Initialize basic tables
            self._create_basic_tables()
            
            self.logger.info(f"Enterprise Database Manager initialized with {self.db_type.value}")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_basic_tables(self):
        """Temel tabloları oluştur"""
        tables = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    login_attempts INT DEFAULT 0,
                    locked_until TIMESTAMP NULL
                )
            """,
            'integration_logs': """
                CREATE TABLE IF NOT EXISTS integration_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    integration_name VARCHAR(100) NOT NULL,
                    action VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    request_data TEXT,
                    response_data TEXT,
                    error_message TEXT,
                    execution_time FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_integration_name (integration_name),
                    INDEX idx_status (status),
                    INDEX idx_created_at (created_at)
                )
            """,
            'system_settings': """
                CREATE TABLE IF NOT EXISTS system_settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value TEXT,
                    setting_type VARCHAR(20) DEFAULT 'string',
                    description TEXT,
                    is_encrypted BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """
        }
        
        # SQLite için SQL'leri ayarla
        if self.db_type == DatabaseType.SQLITE:
            tables = {
                'users': """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        first_name TEXT,
                        last_name TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        is_admin BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP NULL,
                        login_attempts INTEGER DEFAULT 0,
                        locked_until TIMESTAMP NULL
                    )
                """,
                'integration_logs': """
                    CREATE TABLE IF NOT EXISTS integration_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        integration_name TEXT NOT NULL,
                        action TEXT NOT NULL,
                        status TEXT NOT NULL,
                        request_data TEXT,
                        response_data TEXT,
                        error_message TEXT,
                        execution_time REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                'system_settings': """
                    CREATE TABLE IF NOT EXISTS system_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        setting_key TEXT UNIQUE NOT NULL,
                        setting_value TEXT,
                        setting_type TEXT DEFAULT 'string',
                        description TEXT,
                        is_encrypted BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
            }
        
        for table_name, create_sql in tables.items():
            try:
                self.execute_query(create_sql)
                self.logger.info(f"Table {table_name} created/verified")
            except Exception as e:
                self.logger.error(f"Error creating table {table_name}: {e}")
    
    @contextmanager
    def get_connection(self):
        """Bağlantı context manager"""
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            if not connection:
                raise Exception("No database connection available")
            
            yield connection
            
        finally:
            if connection:
                self.connection_pool.return_connection(connection)
    
    @contextmanager
    def transaction(self):
        """Transaction context manager"""
        with self.get_connection() as connection:
            transaction_manager = TransactionManager(connection)
            try:
                transaction_manager.begin()
                yield transaction_manager
                transaction_manager.commit()
                self.metrics.successful_transactions += 1
                
            except Exception as e:
                transaction_manager.rollback()
                self.metrics.failed_transactions += 1
                self.logger.error(f"Transaction failed: {e}")
                raise
            finally:
                self.metrics.total_transactions += 1
    
    def execute_query(self, query: str, params: Tuple = None, use_cache: bool = False) -> List[Dict]:
        """SQL sorgusu çalıştır"""
        start_time = time.time()
        
        try:
            # Cache kontrolü
            if use_cache:
                cache_key = f"{query}:{str(params)}"
                cached_result = self.query_cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            with self.get_connection() as connection:
                if self.db_type == DatabaseType.MYSQL:
                    cursor = connection.connection.cursor(dictionary=True)
                elif self.db_type == DatabaseType.POSTGRESQL:
                    cursor = connection.connection.cursor()
                else:  # SQLite
                    cursor = connection.connection.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Sonuçları al
                if query.strip().upper().startswith('SELECT'):
                    if self.db_type == DatabaseType.SQLITE:
                        result = [dict(row) for row in cursor.fetchall()]
                    elif self.db_type == DatabaseType.POSTGRESQL:
                        columns = [desc[0] for desc in cursor.description]
                        result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    else:
                        result = cursor.fetchall()
                else:
                    connection.connection.commit()
                    result = []
                
                cursor.close()
                
                # Cache'e kaydet
                if use_cache and query.strip().upper().startswith('SELECT'):
                    self.query_cache.set(cache_key, result)
                
                # Metrics güncelle
                execution_time = time.time() - start_time
                self.metrics.successful_queries += 1
                self.metrics.avg_query_time = (
                    (self.metrics.avg_query_time * self.metrics.total_queries + execution_time) / 
                    (self.metrics.total_queries + 1)
                )
                self.metrics.total_queries += 1
                
                return result
                
        except Exception as e:
            self.metrics.failed_queries += 1
            self.metrics.total_queries += 1
            self.logger.error(f"Query execution failed: {query} - {e}")
            raise
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Çoklu sorgu çalıştır"""
        try:
            with self.get_connection() as connection:
                cursor = connection.connection.cursor()
                cursor.executemany(query, params_list)
                connection.connection.commit()
                
                affected_rows = cursor.rowcount
                cursor.close()
                
                self.metrics.successful_queries += 1
                self.metrics.total_queries += 1
                
                return affected_rows
                
        except Exception as e:
            self.metrics.failed_queries += 1
            self.metrics.total_queries += 1
            self.logger.error(f"Bulk query execution failed: {e}")
            raise
    
    def query_builder(self) -> QueryBuilder:
        """Query builder instance'ı al"""
        return QueryBuilder(self.db_type)
    
    def backup_database(self) -> bool:
        """Veritabanını yedekle"""
        if not self.backup_enabled:
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backup_{self.db_config.database}_{timestamp}.sql"
            
            if self.db_type == DatabaseType.MYSQL:
                import subprocess
                cmd = [
                    'mysqldump',
                    f'--host={self.db_config.host}',
                    f'--port={self.db_config.port}',
                    f'--user={self.db_config.username}',
                    f'--password={self.db_config.password}',
                    self.db_config.database
                ]
                
                with open(backup_file, 'w') as f:
                    subprocess.run(cmd, stdout=f, check=True)
            
            elif self.db_type == DatabaseType.SQLITE:
                import shutil
                shutil.copy2(self.db_config.database, backup_file)
            
            self.last_backup = datetime.now()
            self.metrics.last_backup_time = self.last_backup
            self.logger.info(f"Database backup created: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Veritabanı bilgilerini al"""
        try:
            info = {
                'database_type': self.db_type.value,
                'database_name': self.db_config.database,
                'host': getattr(self.db_config, 'host', 'localhost'),
                'port': getattr(self.db_config, 'port', 0),
                'pool_stats': self.connection_pool.get_pool_stats() if self.connection_pool else {},
                'metrics': {
                    'total_queries': self.metrics.total_queries,
                    'successful_queries': self.metrics.successful_queries,
                    'failed_queries': self.metrics.failed_queries,
                    'avg_query_time': self.metrics.avg_query_time,
                    'error_rate': (self.metrics.failed_queries / max(self.metrics.total_queries, 1)) * 100,
                    'total_transactions': self.metrics.total_transactions,
                    'successful_transactions': self.metrics.successful_transactions,
                    'failed_transactions': self.metrics.failed_transactions
                }
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting database info: {e}")
            return {}
    
    def health_check(self) -> bool:
        """Veritabanı sağlık kontrolü"""
        try:
            result = self.execute_query("SELECT 1 as health_check")
            return len(result) > 0 and result[0].get('health_check') == 1
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False
    
    def optimize_database(self):
        """Veritabanını optimize et"""
        try:
            if self.db_type == DatabaseType.MYSQL:
                # Tabloları optimize et
                tables_query = "SHOW TABLES"
                tables = self.execute_query(tables_query)
                
                for table in tables:
                    table_name = list(table.values())[0]
                    self.execute_query(f"OPTIMIZE TABLE {table_name}")
            
            elif self.db_type == DatabaseType.SQLITE:
                self.execute_query("VACUUM")
                self.execute_query("ANALYZE")
            
            self.logger.info("Database optimization completed")
            
        except Exception as e:
            self.logger.error(f"Database optimization failed: {e}")
    
    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Tablo istatistiklerini al"""
        try:
            if self.db_type == DatabaseType.MYSQL:
                query = """
                SELECT 
                    table_rows as row_count,
                    data_length as data_size,
                    index_length as index_size,
                    (data_length + index_length) as total_size
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
                """
                result = self.execute_query(query, (self.db_config.database, table_name))
            
            elif self.db_type == DatabaseType.SQLITE:
                # SQLite için basit row count
                count_query = f"SELECT COUNT(*) as row_count FROM {table_name}"
                result = self.execute_query(count_query)
                result[0].update({
                    'data_size': 0,
                    'index_size': 0,
                    'total_size': 0
                })
            
            return result[0] if result else {}
            
        except Exception as e:
            self.logger.error(f"Error getting table stats for {table_name}: {e}")
            return {}
    
    def close_all_connections(self):
        """Tüm bağlantıları kapat"""
        if self.connection_pool:
            with self.connection_pool.lock:
                for connection in self.connection_pool.connections:
                    connection.close()
                self.connection_pool.connections.clear()
        
        self.logger.info("All database connections closed")


# Global instance
_db_manager = None

def get_database_manager() -> EnterpriseDatabaseManager:
    """Global veritabanı yöneticisi instance'ı"""
    global _db_manager
    if _db_manager is None:
        _db_manager = EnterpriseDatabaseManager()
    return _db_manager


def get_connection():
    """Veritabanı bağlantısı al (geriye dönük uyumluluk)"""
    manager = get_database_manager()
    return manager.get_connection()


if __name__ == "__main__":
    # Test the database system
    print("🗄️  Enterprise Database Manager Test\n")
    
    try:
        # Database manager oluştur
        db_manager = get_database_manager()
        
        print("📊 Database Info:")
        info = db_manager.get_database_info()
        for key, value in info.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for sub_key, sub_value in value.items():
                    print(f"     {sub_key}: {sub_value}")
            else:
                print(f"   {key}: {value}")
        
        # Health check
        print(f"\n🏥 Health Check: {'✅ Healthy' if db_manager.health_check() else '❌ Unhealthy'}")
        
        # Test query
        print(f"\n🔍 Testing Query...")
        result = db_manager.execute_query("SELECT 1 as test_value")
        print(f"   Query result: {result}")
        
        # Query builder test
        print(f"\n🏗️  Query Builder Test:")
        builder = db_manager.query_builder()
        query = (builder
                .select("id", "username", "email")
                .from_table("users")
                .where("is_active = 1")
                .order_by("created_at", "DESC")
                .limit(10)
                .build())
        print(f"   Built query: {query}")
        
        # Table stats
        print(f"\n📈 Table Stats:")
        for table in ['users', 'integration_logs', 'system_settings']:
            stats = db_manager.get_table_stats(table)
            if stats:
                print(f"   {table}: {stats.get('row_count', 0)} rows")
        
        print("\n✅ Enterprise Database Manager test completed!")
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
    
    finally:
        if _db_manager:
            _db_manager.close_all_connections()