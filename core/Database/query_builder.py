"""
Dinamik SQL Sorgu Oluşturucu
WHERE, JOIN, ORDER BY, GROUP BY gibi yapıları destekler
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from .connection import get_db_connection

class QueryBuilder:
    """Dinamik SQL sorgu oluşturucu"""
    
    def __init__(self, table: str):
        self.table = table
        self.select_fields = ['*']
        self.where_conditions = []
        self.where_values = []
        self.join_clauses = []
        self.order_clauses = []
        self.group_clauses = []
        self.limit_value = None
        self.offset_value = None
        self.distinct = False
        # Veritabanı bağlantısını al
        self.db_connection = get_db_connection()
        # SQLite mi kontrol et
        self.is_sqlite = self.db_connection._driver == 'sqlite'
        # Parametre işareti
        self.param_placeholder = '?' if self.is_sqlite else '%s'
    
    def select(self, *fields) -> 'QueryBuilder':
        """SELECT alanlarını belirle"""
        if fields:
            self.select_fields = list(fields)
        return self
    
    def distinct(self) -> 'QueryBuilder':
        """DISTINCT kullan"""
        self.distinct = True
        return self
    
    def where(self, column: str, operator: str, value: Any) -> 'QueryBuilder':
        """WHERE koşulu ekle"""
        self.where_conditions.append(f"{column} {operator} {self.param_placeholder}")
        self.where_values.append(value)
        return self
    
    def where_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        """WHERE IN koşulu ekle"""
        placeholders = ', '.join([self.param_placeholder] * len(values))
        self.where_conditions.append(f"{column} IN ({placeholders})")
        self.where_values.extend(values)
        return self
    
    def where_not_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        """WHERE NOT IN koşulu ekle"""
        placeholders = ', '.join([self.param_placeholder] * len(values))
        self.where_conditions.append(f"{column} NOT IN ({placeholders})")
        self.where_values.extend(values)
        return self
    
    def where_null(self, column: str) -> 'QueryBuilder':
        """WHERE IS NULL koşulu ekle"""
        self.where_conditions.append(f"{column} IS NULL")
        return self
    
    def where_not_null(self, column: str) -> 'QueryBuilder':
        """WHERE IS NOT NULL koşulu ekle"""
        self.where_conditions.append(f"{column} IS NOT NULL")
        return self
    
    def where_between(self, column: str, min_value: Any, max_value: Any) -> 'QueryBuilder':
        """WHERE BETWEEN koşulu ekle"""
        self.where_conditions.append(f"{column} BETWEEN {self.param_placeholder} AND {self.param_placeholder}")
        self.where_values.extend([min_value, max_value])
        return self
    
    def where_like(self, column: str, pattern: str) -> 'QueryBuilder':
        """WHERE LIKE koşulu ekle"""
        self.where_conditions.append(f"{column} LIKE {self.param_placeholder}")
        self.where_values.append(pattern)
        return self
    
    def or_where(self, column: str, operator: str, value: Any) -> 'QueryBuilder':
        """OR WHERE koşulu ekle"""
        if self.where_conditions:
            self.where_conditions.append(f"OR {column} {operator} {self.param_placeholder}")
        else:
            self.where_conditions.append(f"{column} {operator} {self.param_placeholder}")
        self.where_values.append(value)
        return self
    
    def join(self, table: str, first_column: str, operator: str, second_column: str, join_type: str = 'INNER') -> 'QueryBuilder':
        """JOIN ekle"""
        join_clause = f"{join_type} JOIN {table} ON {first_column} {operator} {second_column}"
        self.join_clauses.append(join_clause)
        return self
    
    def left_join(self, table: str, first_column: str, operator: str, second_column: str) -> 'QueryBuilder':
        """LEFT JOIN ekle"""
        return self.join(table, first_column, operator, second_column, 'LEFT')
    
    def right_join(self, table: str, first_column: str, operator: str, second_column: str) -> 'QueryBuilder':
        """RIGHT JOIN ekle"""
        return self.join(table, first_column, operator, second_column, 'RIGHT')
    
    def order_by(self, column: str, direction: str = 'ASC') -> 'QueryBuilder':
        """ORDER BY ekle"""
        self.order_clauses.append(f"{column} {direction.upper()}")
        return self
    
    def group_by(self, *columns) -> 'QueryBuilder':
        """GROUP BY ekle"""
        self.group_clauses.extend(columns)
        return self
    
    def having(self, condition: str, *values) -> 'QueryBuilder':
        """HAVING koşulu ekle"""
        self.where_conditions.append(f"HAVING {condition}")
        self.where_values.extend(values)
        return self
    
    def limit(self, limit: int) -> 'QueryBuilder':
        """LIMIT ekle"""
        self.limit_value = limit
        return self
    
    def offset(self, offset: int) -> 'QueryBuilder':
        """OFFSET ekle"""
        self.offset_value = offset
        return self
    
    def paginate(self, page: int, per_page: int) -> 'QueryBuilder':
        """Sayfalama ekle"""
        offset = (page - 1) * per_page
        self.limit(per_page).offset(offset)
        return self
    
    def _build_select_query(self) -> Tuple[str, List[Any]]:
        """SELECT sorgusu oluştur"""
        # SELECT kısmı
        distinct_clause = "DISTINCT " if self.distinct else ""
        select_clause = f"SELECT {distinct_clause}{', '.join(self.select_fields)}"
        
        # FROM kısmı
        from_clause = f"FROM {self.table}"
        
        # JOIN kısmı
        join_clause = ""
        if self.join_clauses:
            join_clause = " " + " ".join(self.join_clauses)
        
        # WHERE kısmı
        where_clause = ""
        if self.where_conditions:
            where_clause = " WHERE " + " AND ".join(self.where_conditions)
        
        # GROUP BY kısmı
        group_clause = ""
        if self.group_clauses:
            group_clause = f" GROUP BY {', '.join(self.group_clauses)}"
        
        # ORDER BY kısmı
        order_clause = ""
        if self.order_clauses:
            order_clause = f" ORDER BY {', '.join(self.order_clauses)}"
        
        # LIMIT ve OFFSET kısmı
        limit_clause = ""
        if self.limit_value is not None:
            limit_clause = f" LIMIT {self.limit_value}"
            if self.offset_value is not None:
                limit_clause += f" OFFSET {self.offset_value}"
        
        # Sorguyu birleştir
        query = f"{select_clause} {from_clause}{join_clause}{where_clause}{group_clause}{order_clause}{limit_clause}"
        
        return query, self.where_values.copy()
    
    def get(self) -> List[Dict[str, Any]]:
        """Sorguyu çalıştır ve sonuçları getir"""
        query, values = self._build_select_query()
        return self.db_connection.execute_query(query, tuple(values)) or []
    
    def first(self) -> Optional[Dict[str, Any]]:
        """İlk sonucu getir"""
        self.limit(1)
        results = self.get()
        return results[0] if results else None
    
    def count(self) -> int:
        """Kayıt sayısını getir"""
        # Mevcut select alanlarını sakla
        original_select = self.select_fields.copy()
        
        # COUNT için select'i değiştir
        self.select_fields = ['COUNT(*) as count']
        
        result = self.first()
        
        # Orijinal select'i geri yükle
        self.select_fields = original_select
        
        return result['count'] if result else 0
    
    def exists(self) -> bool:
        """Kayıt var mı kontrol et"""
        return self.count() > 0
    
    def pluck(self, column: str) -> List[Any]:
        """Belirli bir sütunu getir"""
        original_select = self.select_fields.copy()
        self.select_fields = [column]
        
        results = self.get()
        
        # Orijinal select'i geri yükle
        self.select_fields = original_select
        
        return [row[column] for row in results]
    
    def pluck_dict(self, key_column: str, value_column: str) -> Dict[str, Any]:
        """Key-value dictionary getir"""
        original_select = self.select_fields.copy()
        self.select_fields = [key_column, value_column]
        
        results = self.get()
        
        # Orijinal select'i geri yükle
        self.select_fields = original_select
        
        return {row[key_column]: row[value_column] for row in results}
    
    def chunk(self, chunk_size: int):
        """Büyük sonuçları parçalara böl"""
        offset = 0
        while True:
            self.offset(offset).limit(chunk_size)
            results = self.get()
            
            if not results:
                break
            
            yield results
            offset += chunk_size
    
    def to_sql(self) -> str:
        """SQL sorgusunu string olarak döndür"""
        query, _ = self._build_select_query()
        return query
    
    def reset(self) -> 'QueryBuilder':
        """Sorgu oluşturucuyu sıfırla"""
        self.select_fields = ['*']
        self.where_conditions = []
        self.where_values = []
        self.join_clauses = []
        self.order_clauses = []
        self.group_clauses = []
        self.limit_value = None
        self.offset_value = None
        self.distinct = False
        return self

# Kullanım kolaylığı için fonksiyon
def table(table_name: str) -> QueryBuilder:
    """Yeni sorgu oluşturucu başlat"""
    return QueryBuilder(table_name) 