"""
Comment Model
Yorum modeli ve ilişkileri
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.Database.base_model import BaseModel

class Comment(BaseModel):
    """Yorum modeli"""
    
    __table__ = 'comments'
    __fillable__ = [
        'content', 'user_id', 'post_id', 'parent_id', 'status',
        'is_approved', 'is_spam', 'ip_address', 'user_agent'
    ]
    __hidden__ = ['ip_address', 'user_agent']
    __timestamps__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._user = None
        self._post = None
        self._parent = None
        self._replies = None
    
    @property
    def is_reply(self) -> bool:
        """Yanıt mı"""
        return self.parent_id is not None
    
    @property
    def is_approved(self) -> bool:
        """Onaylanmış mı"""
        return self.status == 'approved'
    
    @property
    def is_pending(self) -> bool:
        """Beklemede mi"""
        return self.status == 'pending'
    
    @property
    def is_spam(self) -> bool:
        """Spam mi"""
        return self.status == 'spam'
    
    def user(self):
        """Yorumun yazarı"""
        if self._user is None:
            from .User import User
            self._user = User.find(self.user_id)
        return self._user
    
    def post(self):
        """Yorumun yapıldığı post"""
        if self._post is None:
            from .Post import Post
            self._post = Post.find(self.post_id)
        return self._post
    
    def parent(self):
        """Üst yorum"""
        if self._parent is None and self.parent_id:
            self._parent = Comment.find(self.parent_id)
        return self._parent
    
    def replies(self):
        """Yanıtlar"""
        if self._replies is None:
            self._replies = Comment.where({'parent_id': self.id, 'status': 'approved'})
        return self._replies
    
    def replies_count(self) -> int:
        """Yanıt sayısı"""
        return len(self.replies())
    
    def approve(self) -> bool:
        """Yorumu onayla"""
        self.status = 'approved'
        return self.save()
    
    def reject(self) -> bool:
        """Yorumu reddet"""
        self.status = 'rejected'
        return self.save()
    
    def mark_as_spam(self) -> bool:
        """Yorumu spam olarak işaretle"""
        self.status = 'spam'
        return self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Modeli dictionary'e çevir"""
        data = super().to_dict()
        
        # Ek özellikler ekle
        data['is_reply'] = self.is_reply
        data['is_approved'] = self.is_approved
        data['is_pending'] = self.is_pending
        data['is_spam'] = self.is_spam
        data['replies_count'] = self.replies_count()
        
        # İlişkili veriler
        if self.user():
            data['user'] = self.user().to_dict()
        
        if self.post():
            data['post'] = {
                'id': self.post().id,
                'title': self.post().title,
                'url': self.post().url
            }
        
        if self.parent():
            data['parent'] = {
                'id': self.parent().id,
                'content': self.parent().content[:100] + '...' if len(self.parent().content) > 100 else self.parent().content
            }
        
        return data
    
    @classmethod
    def approved(cls) -> List['Comment']:
        """Onaylanmış yorumları getir"""
        return cls.where({'status': 'approved'})
    
    @classmethod
    def pending(cls) -> List['Comment']:
        """Bekleyen yorumları getir"""
        return cls.where({'status': 'pending'})
    
    @classmethod
    def spam(cls) -> List['Comment']:
        """Spam yorumları getir"""
        return cls.where({'status': 'spam'})
    
    @classmethod
    def by_post(cls, post_id: int) -> List['Comment']:
        """Post'a ait yorumları getir"""
        return cls.where({'post_id': post_id, 'status': 'approved', 'parent_id': None})
    
    @classmethod
    def by_user(cls, user_id: int) -> List['Comment']:
        """Kullanıcıya ait yorumları getir"""
        return cls.where({'user_id': user_id})
    
    @classmethod
    def recent(cls, limit: int = 10) -> List['Comment']:
        """Son yorumları getir"""
        return cls.where({'status': 'approved'}).order_by('created_at', 'desc').limit(limit).get()
    
    @classmethod
    def create_comment(cls, data: Dict[str, Any]) -> Optional['Comment']:
        """Yeni yorum oluştur"""
        from core.Services.validators import Validator
        
        # Validasyon
        validator = Validator()
        rules = {
            'content': 'required|min:2|max:1000',
            'user_id': 'required|exists:users,id',
            'post_id': 'required|exists:posts,id'
        }
        
        if 'parent_id' in data and data['parent_id']:
            rules['parent_id'] = 'exists:comments,id'
        
        if not validator.validate(data, rules):
            return None
        
        # Spam kontrolü
        if cls._is_spam(data):
            data['status'] = 'spam'
        else:
            data['status'] = 'pending'
        
        # IP adresi ve user agent ekle
        if 'ip_address' not in data:
            data['ip_address'] = cls._get_client_ip()
        
        if 'user_agent' not in data:
            data['user_agent'] = cls._get_user_agent()
        
        # Yorumu oluştur
        comment = cls(**data)
        if comment.save():
            return comment
        
        return None
    
    @classmethod
    def _is_spam(cls, data: Dict[str, Any]) -> bool:
        """Spam kontrolü"""
        # Basit spam kontrolü
        spam_keywords = ['viagra', 'casino', 'loan', 'credit', 'buy now', 'click here']
        content = data.get('content', '').lower()
        
        # Spam anahtar kelimeleri kontrol et
        for keyword in spam_keywords:
            if keyword in content:
                return True
        
        # Çok kısa yorumlar
        if len(content) < 5:
            return True
        
        # Çok uzun yorumlar
        if len(content) > 1000:
            return True
        
        return False
    
    @classmethod
    def _get_client_ip(cls) -> str:
        """Client IP adresini al"""
        # Bu method request context'inde çağrılmalı
        return '127.0.0.1'  # Varsayılan
    
    @classmethod
    def _get_user_agent(cls) -> str:
        """User agent'ı al"""
        # Bu method request context'inde çağrılmalı
        return 'Unknown'  # Varsayılan 