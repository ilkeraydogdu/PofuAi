"""
Base Model
Tüm modellerin temel sınıfı
"""

from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime
import json
from .connection import get_db_connection

class BaseModel:
    """Temel model sınıfı"""
    
    __table__ = None
    __primary_key__ = 'id'
    __fillable__ = []
    __hidden__ = []
    __timestamps__ = True
    __dates__ = ['created_at', 'updated_at']
    
    # Veritabanı bağlantısı ve parametre işareti
    _db_connection = get_db_connection()
    _is_sqlite = _db_connection._driver == 'sqlite'
    _param_placeholder = '?' if _is_sqlite else '%s'
    
    def __init__(self, **kwargs):
        """Model başlat"""
        self._data = {}
        self._original = {}
        self._exists = False
        self._dirty = set()
        
        # Verileri doldur
        for key, value in kwargs.items():
            self._data[key] = value
            self._original[key] = value
            
        # ID varsa, kayıt var demektir
        if self.__primary_key__ in self._data:
            self._exists = True
    
    def __getattr__(self, name):
        """Özellik erişimi"""
        if name in self._data:
            return self._data[name]
        
        # Property'leri kontrol et
        if hasattr(self.__class__, name):
            attr = getattr(self.__class__, name)
            if hasattr(attr, '__get__'):
                return attr.__get__(self, self.__class__)
        
        raise AttributeError(f"'{self.__class__.__name__}' nesnesi '{name}' özelliğine sahip değil")
    
    def __setattr__(self, name, value):
        """Özellik değiştirme"""
        # Özel değişkenler için normal davranış
        if name.startswith('_') or name in dir(self.__class__):
            super().__setattr__(name, value)
            return
            
        # Model verisi olarak işle
        self._data[name] = value
        self._dirty.add(name)
    
    def __getitem__(self, key):
        """Dictionary benzeri erişim"""
        return self._data[key]
    
    def __setitem__(self, key, value):
        """Dictionary benzeri atama"""
        self._data[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Modeli dictionary'e çevir"""
        result = {}
        for key, value in self._data.items():
            if key not in self.__hidden__:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, (dict, list)):
                    result[key] = json.dumps(value, ensure_ascii=False)
                else:
                    result[key] = value
        return result
    
    def to_json(self) -> str:
        """Modeli JSON'a çevir"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def save(self) -> bool:
        """Kaydet (insert veya update)"""
        if self._exists:
            return self._update()
        return self._insert()
    
    def _insert(self) -> bool:
        """Yeni kayıt ekle"""
        if not self.__table__:
            raise ValueError("Tablo adı belirtilmemiş")
        
        # Doldurulabilir alanları filtrele
        data = {}
        for key, value in self._data.items():
            if not self.__fillable__ or key in self.__fillable__:
                data[key] = value
        
        # Timestamp ekle
        if self.__timestamps__:
            now = datetime.now()
            if 'created_at' not in data:
                data['created_at'] = now
            if 'updated_at' not in data:
                data['updated_at'] = now
        
        # Boş sorgu kontrolü
        if not data:
            return False
        
        # SQL sorgusu oluştur
        fields = list(data.keys())
        placeholders = [self._param_placeholder] * len(fields)
        values = list(data.values())
        
        query = f"INSERT INTO {self.__table__} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        
        try:
            with self._db_connection.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(values))
                
                # Son eklenen ID'yi al
                if self._is_sqlite:
                    last_id = cursor.lastrowid
                else:
                    last_id = cursor.lastrowid
                
                if last_id:
                    self._data[self.__primary_key__] = last_id
                
                conn.commit()
                self._exists = True
                self._dirty.clear()
                self._original = self._data.copy()
                
                cursor.close()
                return True
                
        except Exception as e:
            print(f"Kayıt ekleme hatası: {e}")
            return False
    
    def _update(self) -> bool:
        """Mevcut kaydı güncelle"""
        if not self.__table__:
            raise ValueError("Tablo adı belirtilmemiş")
            
        if not self._dirty:
            return True  # Değişiklik yok
            
        # Doldurulabilir ve değişmiş alanları filtrele
        data = {}
        for key in self._dirty:
            if not self.__fillable__ or key in self.__fillable__:
                data[key] = self._data[key]
        
        # Timestamp güncelle
        if self.__timestamps__ and 'updated_at' not in data:
            data['updated_at'] = datetime.now()
            
        # Boş sorgu kontrolü
        if not data:
            return True
            
        # SQL sorgusu oluştur
        set_clauses = [f"{field} = {self._param_placeholder}" for field in data.keys()]
        values = list(data.values())
        values.append(self._data[self.__primary_key__])
        
        query = f"UPDATE {self.__table__} SET {', '.join(set_clauses)} WHERE {self.__primary_key__} = {self._param_placeholder}"
        
        try:
            with self._db_connection.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(values))
                conn.commit()
                
                self._dirty.clear()
                self._original = self._data.copy()
                
                cursor.close()
                return True
                
        except Exception as e:
            print(f"Kayıt güncelleme hatası: {e}")
            return False
    
    def delete(self) -> bool:
        """Kayıt sil"""
        if not self._exists:
            return False
        
        if not self.__table__:
            raise ValueError("Tablo adı belirtilmemiş")
        
        query = f"DELETE FROM {self.__table__} WHERE {self.__primary_key__} = {self._param_placeholder}"
        
        try:
            with self._db_connection.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (self._data[self.__primary_key__],))
                conn.commit()
                
                self._exists = False
                cursor.close()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Silme hatası: {e}")
            return False
    
    @classmethod
    def find(cls, id_value: Any) -> Optional['BaseModel']:
        """ID ile bul"""
        if not cls.__table__:
            raise ValueError("Tablo adı belirtilmemiş")
        
        query = f"SELECT * FROM {cls.__table__} WHERE {cls.__primary_key__} = {cls._param_placeholder}"
        result = cls._db_connection.execute_query(query, (id_value,))
        
        if result:
            return cls(**result[0])
        return None
    
    @classmethod
    def all(cls) -> List['BaseModel']:
        """Tüm kayıtları getir"""
        if not cls.__table__:
            raise ValueError("Tablo adı belirtilmemiş")
        
        query = f"SELECT * FROM {cls.__table__}"
        result = cls._db_connection.execute_query(query)
        
        return [cls(**row) for row in result] if result else []
    
    @classmethod
    def where(cls, conditions: Dict[str, Any]) -> List['BaseModel']:
        """Koşullara göre ara"""
        if not cls.__table__:
            raise ValueError("Tablo adı belirtilmemiş")
        
        if not conditions:
            return cls.all()
        
        where_clause = ' AND '.join([f"{k} = {cls._param_placeholder}" for k in conditions.keys()])
        query = f"SELECT * FROM {cls.__table__} WHERE {where_clause}"
        values = tuple(conditions.values())
        
        result = cls._db_connection.execute_query(query, values)
        return [cls(**row) for row in result] if result else []
    
    @classmethod
    def first(cls, conditions: Dict[str, Any] = None) -> Optional['BaseModel']:
        """İlk kaydı getir"""
        if conditions:
            results = cls.where(conditions)
        else:
            results = cls.all()
        
        return results[0] if results else None
    
    @classmethod
    def count(cls, conditions: Dict[str, Any] = None) -> int:
        """
        Kayıt sayısını döndürür
        
        Args:
            conditions: Koşullar dictionary'si
            
        Returns:
            int: Kayıt sayısı
        """
        if not cls.__table__:
            raise ValueError("Tablo adı belirtilmemiş")
        
        query = f"SELECT COUNT(*) as count FROM {cls.__table__}"
        values = None
        
        if conditions:
            where_clause = ' AND '.join([f"{k} = {cls._param_placeholder}" for k in conditions.keys()])
            query += f" WHERE {where_clause}"
            values = tuple(conditions.values())
        
        result = cls._db_connection.execute_query(query, values)
        return result[0]['count'] if result else 0
    
    @classmethod
    def order_by(cls, column: str, direction: str = 'desc') -> 'QueryResult':
        """
        ORDER BY koşulu ekleyerek sorgu oluştur
        
        Args:
            column: Sıralama sütunu
            direction: Sıralama yönü (asc/desc)
            
        Returns:
            QueryResult: Sorgu sonuç nesnesi
        """
        from .query_builder import QueryBuilder
        builder = QueryBuilder(cls.__table__)
        builder.order_by(column, direction)
        return QueryResult(cls, builder)
    
    @classmethod
    def limit(cls, limit: int) -> 'QueryResult':
        """
        LIMIT koşulu ekleyerek sorgu oluştur
        
        Args:
            limit: Maksimum kayıt sayısı
            
        Returns:
            QueryResult: Sorgu sonuç nesnesi
        """
        from .query_builder import QueryBuilder
        builder = QueryBuilder(cls.__table__)
        builder.limit(limit)
        return QueryResult(cls, builder)
    
    @classmethod
    def query(cls) -> 'QueryResult':
        """
        QueryResult nesnesi oluştur
        
        Returns:
            QueryResult: Sorgu sonuç nesnesi
        """
        from .query_builder import QueryBuilder
        builder = QueryBuilder(cls.__table__)
        return QueryResult(cls, builder)
    
    def refresh(self) -> bool:
        """Veritabanından yeniden yükle"""
        if not self._exists:
            return False
            
        refreshed = self.__class__.find(self._data[self.__primary_key__])
        if refreshed:
            self._data = refreshed._data
            self._original = refreshed._original
            return True
            
        return False
        
    def is_dirty(self) -> bool:
        """Değişiklik var mı kontrol et"""
        for key, value in self._data.items():
            if key not in self._original or self._original[key] != value:
                return True
        return False
        
    def get_changes(self) -> Dict[str, Any]:
        """Değişiklikleri getir"""
        changes = {}
        for key, value in self._data.items():
            if key not in self._original or self._original[key] != value:
                changes[key] = {
                    'old': self._original.get(key),
                    'new': value
                }
        return changes

class QueryResult:
    """Sorgu sonuç sınıfı"""
    
    def __init__(self, model_class, query_builder):
        self.model_class = model_class
        self.query_builder = query_builder
    
    def order_by(self, column: str, direction: str = 'desc') -> 'QueryResult':
        """ORDER BY ekle"""
        self.query_builder.order_by(column, direction)
        return self
    
    def limit(self, limit: int) -> 'QueryResult':
        """LIMIT ekle"""
        self.query_builder.limit(limit)
        return self
    
    def offset(self, offset: int) -> 'QueryResult':
        """OFFSET ekle"""
        self.query_builder.offset(offset)
        return self
    
    def where(self, column: str, operator: str = '=', value: Any = None) -> 'QueryResult':
        """WHERE koşulu ekle"""
        # Eğer tek parametre ile çağrıldıysa (Dictionary)
        if isinstance(column, dict) and operator == '=' and value is None:
            for k, v in column.items():
                self.query_builder.where(k, '=', v)
        else:
            self.query_builder.where(column, operator, value)
        return self
    
    def where_like(self, column: str, pattern: str) -> 'QueryResult':
        """WHERE LIKE koşulu ekle"""
        self.query_builder.where_like(column, pattern)
        return self
    
    def get(self) -> List[BaseModel]:
        """Sorguyu çalıştır ve model listesi döndür"""
        results = self.query_builder.get()
        return [self.model_class(**row) for row in results] if results else []
    
    def first(self) -> Optional[BaseModel]:
        """İlk sonucu model olarak döndür"""
        self.query_builder.limit(1)
        results = self.get()
        return results[0] if results else None
    
    def count(self) -> int:
        """Kayıt sayısını döndür"""
        return self.query_builder.count()
    
    def paginate(self, page: int, per_page: int) -> Dict[str, Any]:
        """Sayfalama yap"""
        total = self.count()
        self.query_builder.paginate(page, per_page)
        
        results = self.get()
        
        return {
            'data': results,
            'pagination': {
                'total': total,
                'per_page': per_page,
                'current_page': page,
                'last_page': (total + per_page - 1) // per_page,
                'from': (page - 1) * per_page + 1 if results else 0,
                'to': min(page * per_page, total) if results else 0
            }
        } 