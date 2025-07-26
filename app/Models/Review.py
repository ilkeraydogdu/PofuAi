"""
Review Model
Ürün yorumu modeli
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.Database.base_model import BaseModel

class Review(BaseModel):
    """Ürün yorumu modeli"""
    
    __table__ = 'reviews'
    __fillable__ = [
        'user_id', 'product_id', 'rating', 'title', 'content',
        'status', 'verified_purchase', 'helpful_votes'
    ]
    __hidden__ = []
    __timestamps__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._user = None
        self._product = None
    
    @property
    def is_approved(self) -> bool:
        """Onaylanmış mı"""
        return self.status == 'approved'
    
    @property
    def is_pending(self) -> bool:
        """Beklemede mi"""
        return self.status == 'pending'
    
    @property
    def is_rejected(self) -> bool:
        """Reddedilmiş mi"""
        return self.status == 'rejected'
    
    @property
    def is_spam(self) -> bool:
        """Spam mi"""
        return self.status == 'spam'
    
    @property
    def rating_stars(self) -> str:
        """Yıldız gösterimi"""
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    def user(self):
        """Yorumu yapan kullanıcı"""
        if self._user is None:
            from .User import User
            self._user = User.find(self.user_id)
        return self._user
    
    def product(self):
        """Yorumlanan ürün"""
        if self._product is None:
            from .Product import Product
            self._product = Product.find(self.product_id)
        return self._product
    
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
    
    def mark_as_helpful(self) -> bool:
        """Faydalı olarak işaretle"""
        self.helpful_votes = (self.helpful_votes or 0) + 1
        return self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Modeli dictionary'e çevir"""
        data = super().to_dict()
        
        # Ek özellikler ekle
        data['is_approved'] = self.is_approved
        data['is_pending'] = self.is_pending
        data['is_rejected'] = self.is_rejected
        data['is_spam'] = self.is_spam
        data['rating_stars'] = self.rating_stars
        
        # İlişkili veriler
        if self.user():
            data['user'] = {
                'id': self.user().id,
                'name': self.user().name,
                'avatar_url': self.user().avatar_url
            }
        
        if self.product():
            data['product'] = {
                'id': self.product().id,
                'name': self.product().name,
                'url': self.product().url
            }
        
        return data
    
    @classmethod
    def approved(cls) -> List['Review']:
        """Onaylanmış yorumları getir"""
        return cls.where({'status': 'approved'})
    
    @classmethod
    def pending(cls) -> List['Review']:
        """Bekleyen yorumları getir"""
        return cls.where({'status': 'pending'})
    
    @classmethod
    def by_product(cls, product_id: int) -> List['Review']:
        """Ürüne ait yorumları getir"""
        return cls.where({'product_id': product_id, 'status': 'approved'})
    
    @classmethod
    def by_user(cls, user_id: int) -> List['Review']:
        """Kullanıcının yorumlarını getir"""
        return cls.where({'user_id': user_id})
    
    @classmethod
    def by_rating(cls, rating: int) -> List['Review']:
        """Puana göre yorumları getir"""
        return cls.where({'rating': rating, 'status': 'approved'})
    
    @classmethod
    def recent(cls, limit: int = 10) -> List['Review']:
        """Son yorumları getir"""
        return cls.where({'status': 'approved'}).order_by('created_at', 'desc').limit(limit).get()
    
    @classmethod
    def helpful(cls, limit: int = 10) -> List['Review']:
        """En faydalı yorumları getir"""
        return cls.where({'status': 'approved'}).order_by('helpful_votes', 'desc').limit(limit).get()
    
    @classmethod
    def create_review(cls, data: Dict[str, Any]) -> Optional['Review']:
        """Yeni yorum oluştur"""
        from core.Services.validators import Validator
        
        # Validasyon
        validator = Validator()
        rules = {
            'rating': 'required|integer|min:1|max:5',
            'title': 'required|min:2|max:200',
            'content': 'required|min:10|max:1000',
            'user_id': 'required|exists:users,id',
            'product_id': 'required|exists:products,id'
        }
        
        if not validator.validate(data, rules):
            return None
        
        # Spam kontrolü
        if cls._is_spam(data):
            data['status'] = 'spam'
        else:
            data['status'] = 'pending'
        
        # Yorumu oluştur
        review = cls(**data)
        if review.save():
            return review
        
        return None
    
    @classmethod
    def _is_spam(cls, data: Dict[str, Any]) -> bool:
        """Spam kontrolü"""
        # Basit spam kontrolü
        spam_keywords = ['viagra', 'casino', 'loan', 'credit', 'buy now', 'click here']
        content = data.get('content', '').lower()
        title = data.get('title', '').lower()
        
        # Spam anahtar kelimeleri kontrol et
        for keyword in spam_keywords:
            if keyword in content or keyword in title:
                return True
        
        # Çok kısa yorumlar
        if len(content) < 10:
            return True
        
        # Çok uzun yorumlar
        if len(content) > 1000:
            return True
        
        return False 