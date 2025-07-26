"""
Post Model
Post modeli ve ilişkileri
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.Database.base_model import BaseModel

class Post(BaseModel):
    """Post modeli"""
    
    __table__ = 'posts'
    __fillable__ = [
        'title', 'content', 'excerpt', 'slug', 'user_id', 'category',
        'status', 'featured', 'views', 'meta_title', 'meta_description',
        'published_at', 'featured_image'
    ]
    __hidden__ = []
    __timestamps__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._user = None
        self._comments = None
        self._likes = None
        self._tags = None
    
    @property
    def excerpt_text(self) -> str:
        """Özet metni"""
        if self.excerpt:
            return self.excerpt
        return self.content[:150] + '...' if len(self.content) > 150 else self.content
    
    @property
    def url(self) -> str:
        """Post URL'i"""
        return f"/posts/{self.slug or self.id}"
    
    @property
    def featured_image_url(self) -> str:
        """Öne çıkan resim URL'i"""
        if self.featured_image:
            return f"/uploads/posts/{self.featured_image}"
        return "/static/assets/images/default-post.jpg"
    
    @property
    def is_published(self) -> bool:
        """Yayınlanmış mı"""
        return self.status == 'published'
    
    @property
    def is_featured(self) -> bool:
        """Öne çıkan mı"""
        return bool(self.featured)
    
    @property
    def reading_time(self) -> int:
        """Okuma süresi (dakika)"""
        words_per_minute = 200
        word_count = len(self.content.split())
        return max(1, round(word_count / words_per_minute))
    
    def user(self):
        """Post'un yazarı"""
        if self._user is None:
            from .User import User
            self._user = User.find(self.user_id)
        return self._user
    
    def comments(self):
        """Post'un yorumları"""
        if self._comments is None:
            from .Comment import Comment
            self._comments = Comment.where({'post_id': self.id, 'status': 'approved'})
        return self._comments
    
    def likes(self):
        """Post'un beğenileri"""
        if self._likes is None:
            from .Like import Like
            self._likes = Like.where({'post_id': self.id})
        return self._likes
    
    def tags(self):
        """Post'un etiketleri"""
        if self._tags is None:
            from .Tag import Tag
            # Post-tag ilişkisinden etiketleri al
            self._tags = Tag.get_post_tags(self.id)
        return self._tags
    
    def comments_count(self) -> int:
        """Yorum sayısı"""
        return len(self.comments())
    
    def likes_count(self) -> int:
        """Beğeni sayısı"""
        return len(self.likes())
    
    def increment_views(self) -> bool:
        """Görüntülenme sayısını artır"""
        self.views = (self.views or 0) + 1
        return self.save()
    
    def toggle_featured(self) -> bool:
        """Öne çıkan durumunu değiştir"""
        self.featured = not self.featured
        return self.save()
    
    def publish(self) -> bool:
        """Post'u yayınla"""
        self.status = 'published'
        self.published_at = datetime.now()
        return self.save()
    
    def unpublish(self) -> bool:
        """Post'u yayından kaldır"""
        self.status = 'draft'
        self.published_at = None
        return self.save()
    
    def add_tag(self, tag_name: str) -> bool:
        """Etiket ekle"""
        from .Tag import Tag
        tag = Tag.find_or_create({'name': tag_name})
        return self.attach_tag(tag.id)
    
    def remove_tag(self, tag_name: str) -> bool:
        """Etiket kaldır"""
        from .Tag import Tag
        tag = Tag.find_by_name(tag_name)
        if tag:
            return self.detach_tag(tag.id)
        return False
    
    def attach_tag(self, tag_id: int) -> bool:
        """Etiket ilişkisi kur"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO post_tags (post_id, tag_id)
                VALUES (?, ?)
            """, (self.id, tag_id))
            self.db_connection.commit()
            cursor.close()
            return True
        except Exception:
            return False
    
    def detach_tag(self, tag_id: int) -> bool:
        """Etiket ilişkisini kaldır"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                DELETE FROM post_tags WHERE post_id = ? AND tag_id = ?
            """, (self.id, tag_id))
            self.db_connection.commit()
            cursor.close()
            return True
        except Exception:
            return False
    
    def is_liked_by(self, user_id: int) -> bool:
        """Kullanıcı tarafından beğenilmiş mi"""
        from .Like import Like
        return Like.where({'post_id': self.id, 'user_id': user_id}).count() > 0
    
    def like_by(self, user_id: int) -> bool:
        """Kullanıcı tarafından beğen"""
        from .Like import Like
        if not self.is_liked_by(user_id):
            like = Like.create({
                'post_id': self.id,
                'user_id': user_id
            })
            return like is not None
        return False
    
    def unlike_by(self, user_id: int) -> bool:
        """Kullanıcı tarafından beğeniyi kaldır"""
        from .Like import Like
        like = Like.where({'post_id': self.id, 'user_id': user_id}).first()
        if like:
            return like.delete()
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Modeli dictionary'e çevir"""
        data = super().to_dict()
        
        # Ek özellikler ekle
        data['excerpt_text'] = self.excerpt_text
        data['url'] = self.url
        data['featured_image_url'] = self.featured_image_url
        data['is_published'] = self.is_published
        data['is_featured'] = self.is_featured
        data['reading_time'] = self.reading_time
        data['comments_count'] = self.comments_count()
        data['likes_count'] = self.likes_count()
        
        # İlişkili veriler
        if self.user():
            data['user'] = self.user().to_dict()
        
        return data
    
    @classmethod
    def published(cls) -> List['Post']:
        """Yayınlanmış post'ları getir"""
        return cls.where({'status': 'published'})
    
    @classmethod
    def featured(cls) -> List['Post']:
        """Öne çıkan post'ları getir"""
        return cls.where({'featured': True, 'status': 'published'})
    
    @classmethod
    def by_category(cls, category: str) -> List['Post']:
        """Kategoriye göre post'ları getir"""
        return cls.where({'category': category, 'status': 'published'})
    
    @classmethod
    def by_user(cls, user_id: int) -> List['Post']:
        """Kullanıcıya göre post'ları getir"""
        return cls.where({'user_id': user_id})
    
    @classmethod
    def popular(cls, limit: int = 10) -> List['Post']:
        """Popüler post'ları getir"""
        return cls.where({'status': 'published'}).order_by('views', 'desc').limit(limit).get()
    
    @classmethod
    def recent(cls, limit: int = 10) -> List['Post']:
        """Son post'ları getir"""
        return cls.where({'status': 'published'}).order_by('created_at', 'desc').limit(limit).get()
    
    @classmethod
    def search(cls, query: str, limit: int = 10) -> List['Post']:
        """Post'larda arama yap"""
        return cls.where('status', 'published').where_like('title', f'%{query}%').limit(limit).get()
    
    @classmethod
    def create_post(cls, data: Dict[str, Any]) -> Optional['Post']:
        """Yeni post oluştur"""
        from core.Services.validators import Validator
        
        # Validasyon
        validator = Validator()
        rules = {
            'title': 'required|min:3|max:200',
            'content': 'required|min:10',
            'category': 'required|in:technology,science,health,entertainment',
            'user_id': 'required|exists:users,id'
        }
        
        if not validator.validate(data, rules):
            return None
        
        # Slug oluştur
        if 'slug' not in data:
            from core.Helpers import generate_slug
            data['slug'] = generate_slug(data['title'])
        
        # Post'u oluştur
        post = cls(**data)
        if post.save():
            return post
        
        return None 