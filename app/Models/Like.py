"""
Like Model
Beğeni modeli ve ilişkileri
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.Database.base_model import BaseModel

class Like(BaseModel):
    """Beğeni modeli"""
    
    __table__ = 'likes'
    __fillable__ = [
        'user_id', 'post_id', 'created_at'
    ]
    __hidden__ = []
    __timestamps__ = False  # Manuel timestamp yönetimi
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._user = None
        self._post = None
    
    def user(self):
        """Beğeniyi yapan kullanıcı"""
        if self._user is None:
            from .User import User
            self._user = User.find(self.user_id)
        return self._user
    
    def post(self):
        """Beğenilen post"""
        if self._post is None:
            from .Post import Post
            self._post = Post.find(self.post_id)
        return self._post
    
    def to_dict(self) -> Dict[str, Any]:
        """Modeli dictionary'e çevir"""
        data = super().to_dict()
        
        # İlişkili veriler
        if self.user():
            data['user'] = {
                'id': self.user().id,
                'name': self.user().name,
                'avatar_url': self.user().avatar_url
            }
        
        if self.post():
            data['post'] = {
                'id': self.post().id,
                'title': self.post().title,
                'url': self.post().url
            }
        
        return data
    
    @classmethod
    def by_post(cls, post_id: int) -> List['Like']:
        """Post'a ait beğenileri getir"""
        return cls.where({'post_id': post_id})
    
    @classmethod
    def by_user(cls, user_id: int) -> List['Like']:
        """Kullanıcının beğenilerini getir"""
        return cls.where({'user_id': user_id})
    
    @classmethod
    def recent(cls, limit: int = 10) -> List['Like']:
        """Son beğenileri getir"""
        return cls.order_by('created_at', 'desc').limit(limit).get()
    
    @classmethod
    def toggle_like(cls, user_id: int, post_id: int) -> bool:
        """Beğeniyi aç/kapat"""
        existing_like = cls.where({'user_id': user_id, 'post_id': post_id}).first()
        
        if existing_like:
            # Beğeniyi kaldır
            return existing_like.delete()
        else:
            # Beğeni ekle
            like = cls.create({
                'user_id': user_id,
                'post_id': post_id,
                'created_at': datetime.now()
            })
            return like is not None
    
    @classmethod
    def has_liked(cls, user_id: int, post_id: int) -> bool:
        """Kullanıcı post'u beğenmiş mi"""
        return cls.where({'user_id': user_id, 'post_id': post_id}).count() > 0
    
    @classmethod
    def count_by_post(cls, post_id: int) -> int:
        """Post'un beğeni sayısı"""
        return cls.where({'post_id': post_id}).count()
    
    @classmethod
    def count_by_user(cls, user_id: int) -> int:
        """Kullanıcının beğeni sayısı"""
        return cls.where({'user_id': user_id}).count() 