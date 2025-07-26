"""
Tag Model
Etiket modeli ve ilişkileri
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.Database.base_model import BaseModel

class Tag(BaseModel):
    """Etiket modeli"""
    
    __table__ = 'tags'
    __fillable__ = [
        'name', 'slug', 'description', 'color', 'icon'
    ]
    __hidden__ = []
    __timestamps__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._posts = None
    
    @property
    def url(self) -> str:
        """Tag URL'i"""
        return f"/tags/{self.slug or self.id}"
    
    def posts(self):
        """Tag'e ait post'lar"""
        if self._posts is None:
            from .Post import Post
            # Post-tag ilişkisinden post'ları al
            self._posts = Post.get_by_tag(self.id)
        return self._posts
    
    def posts_count(self) -> int:
        """Post sayısı"""
        return len(self.posts())
    
    def to_dict(self) -> Dict[str, Any]:
        """Modeli dictionary'e çevir"""
        data = super().to_dict()
        
        # Ek özellikler ekle
        data['url'] = self.url
        data['posts_count'] = self.posts_count()
        
        return data
    
    @classmethod
    def popular(cls, limit: int = 10) -> List['Tag']:
        """Popüler etiketleri getir"""
        # Post sayısına göre sırala
        return cls.order_by('posts_count', 'desc').limit(limit).get()
    
    @classmethod
    def by_name(cls, name: str) -> Optional['Tag']:
        """İsme göre etiket bul"""
        return cls.first({'name': name})
    
    @classmethod
    def by_slug(cls, slug: str) -> Optional['Tag']:
        """Slug'a göre etiket bul"""
        return cls.first({'slug': slug})
    
    @classmethod
    def get_post_tags(cls, post_id: int) -> List['Tag']:
        """Post'un etiketlerini getir"""
        try:
            cursor = cls.db_connection.cursor()
            cursor.execute("""
                SELECT t.* FROM tags t
                INNER JOIN post_tags pt ON t.id = pt.tag_id
                WHERE pt.post_id = ?
            """, (post_id,))
            
            tags = []
            for row in cursor.fetchall():
                tag_data = dict(zip([col[0] for col in cursor.description], row))
                tags.append(cls(**tag_data))
            
            cursor.close()
            return tags
            
        except Exception:
            return []
    
    @classmethod
    def find_or_create(cls, data: Dict[str, Any]) -> 'Tag':
        """Etiket bul veya oluştur"""
        tag = cls.by_name(data['name'])
        
        if not tag:
            # Slug oluştur
            if 'slug' not in data:
                from core.Helpers import generate_slug
                data['slug'] = generate_slug(data['name'])
            
            tag = cls(**data)
            tag.save()
        
        return tag 