"""
User Model
Kullanıcı modeli ve ilişkileri
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.Database.base_model import BaseModel

class User(BaseModel):
    """Kullanıcı modeli"""
    
    __table__ = 'users'
    __fillable__ = [
        'name', 'email', 'password', 'username', 'avatar',
        'phone', 'address', 'city', 'country', 'postal_code',
        'role', 'status', 'email_verified_at', 'last_login_at'
    ]
    __hidden__ = ['password', 'remember_token']
    __timestamps__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._posts = None
        self._comments = None
        self._orders = None
    
    @property
    def full_name(self) -> str:
        """Tam adı döndür"""
        return f"{self.name}"
    
    @property
    def avatar_url(self) -> str:
        """Avatar URL'ini döndür"""
        if self.avatar:
            return f"/uploads/avatars/{self.avatar}"
        return "/static/assets/images/avatars/default.png"
    
    @property
    def is_admin(self) -> bool:
        """Admin mi kontrol et"""
        return self.role == 'admin'
    
    @property
    def is_active(self) -> bool:
        """Aktif mi kontrol et"""
        return self.status == 'active'
    
    @property
    def is_verified(self) -> bool:
        """Email doğrulanmış mı kontrol et"""
        return self.email_verified_at is not None
    
    def posts(self):
        """Kullanıcının postları"""
        if self._posts is None:
            from .Post import Post
            self._posts = Post.where({'user_id': self.id})
        return self._posts
    
    def comments(self):
        """Kullanıcının yorumları"""
        if self._comments is None:
            from .Comment import Comment
            self._comments = Comment.where({'user_id': self.id})
        return self._comments
    
    def orders(self):
        """Kullanıcının siparişleri"""
        if self._orders is None:
            from .Order import Order
            self._orders = Order.where({'user_id': self.id})
        return self._orders
    
    def has_role(self, role: str) -> bool:
        """Belirli role sahip mi kontrol et"""
        return self.role == role
    
    def has_permission(self, permission: str) -> bool:
        """Belirli permission'a sahip mi kontrol et"""
        # Basit permission sistemi
        if self.is_admin:
            return True
        
        permissions = {
            'user': ['read_posts', 'create_posts', 'edit_own_posts'],
            'moderator': ['read_posts', 'create_posts', 'edit_posts', 'delete_posts'],
            'admin': ['*']  # Tüm permission'lar
        }
        
        user_permissions = permissions.get(self.role, [])
        return permission in user_permissions or '*' in user_permissions
    
    def update_last_login(self) -> bool:
        """Son giriş zamanını güncelle"""
        self.last_login_at = datetime.now()
        return self.save()
    
    def verify_email(self) -> bool:
        """Email'i doğrula"""
        self.email_verified_at = datetime.now()
        return self.save()
    
    def change_password(self, new_password: str) -> bool:
        """Şifre değiştir"""
        from core.Services.validators import Validator
        from core.Services.base_service import BaseService
        
        # Şifre validasyonu
        validator = Validator()
        if not validator.validate_password(new_password):
            return False
        
        # Şifreyi hash'le
        hasher = BaseService.get_hasher()
        self.password = hasher.hash(new_password)
        
        return self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Modeli dictionary'e çevir"""
        data = super().to_dict()
        
        # Ek özellikler ekle
        data['full_name'] = self.full_name
        data['avatar_url'] = self.avatar_url
        data['is_admin'] = self.is_admin
        data['is_active'] = self.is_active
        data['is_verified'] = self.is_verified
        
        return data
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """Email ile kullanıcı bul"""
        return cls.first({'email': email})
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """Username ile kullanıcı bul"""
        return cls.first({'username': username})
    
    @classmethod
    def active_users(cls) -> List['User']:
        """Aktif kullanıcıları getir"""
        return cls.where({'status': 'active'})
    
    @classmethod
    def admins(cls) -> List['User']:
        """Admin kullanıcıları getir"""
        return cls.where({'role': 'admin'})
    
    @classmethod
    def create_user(cls, data: Dict[str, Any]) -> Optional['User']:
        """Yeni kullanıcı oluştur (sadece ad, e-posta, telefon)"""
        from core.Services.validators import Validator
        from core.Services.base_service import BaseService
        
        # Email kontrolü - aynı email ile kayıtlı kullanıcı var mı?
        existing_user = cls.find_by_email(data.get('email'))
        if existing_user:
            return None  # Email zaten kullanımda
        
        # Validasyon
        validator = Validator()
        rules = {
            'name': 'required|min:2|max:50',
            'email': 'required|email',
            'phone': 'required|min:10|max:20'
        }
        
        if not validator.validate(data, rules):
            return None
        
        # Geçici şifreyi hash'le
        temp_password = data.get('password_plain')
        if temp_password:
            hasher = BaseService.get_hasher()
            data['password'] = hasher.hash(temp_password)
        
        # Kullanıcıyı oluştur
        user = cls(**data)
        if user.save():
            return user
        
        return None 