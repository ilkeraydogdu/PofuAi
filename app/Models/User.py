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
        'role', 'status', 'email_verified_at', 'last_login_at',
        'two_factor_enabled', 'two_factor_secret', 'preferences',
        'subscription_plan', 'subscription_expires_at', 'api_key',
        'notification_settings', 'language', 'timezone'
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
    
    @property
    def has_two_factor(self) -> bool:
        """İki faktörlü doğrulama aktif mi"""
        return self.two_factor_enabled == True
    
    @property
    def subscription_active(self) -> bool:
        """Abonelik aktif mi"""
        if not self.subscription_expires_at:
            return False
        return datetime.now() < datetime.fromisoformat(self.subscription_expires_at)
    
    @property
    def notification_preferences(self) -> Dict[str, bool]:
        """Bildirim tercihlerini döndür"""
        if not self.notification_settings:
            return {
                'email': True,
                'sms': False,
                'push': True,
                'marketing': False
            }
        try:
            import json
            return json.loads(self.notification_settings)
        except:
            return {}
    
    def update_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Kullanıcı tercihlerini güncelle"""
        import json
        self.preferences = json.dumps(preferences)
        return self.save()
    
    def update_notification_settings(self, settings: Dict[str, bool]) -> bool:
        """Bildirim ayarlarını güncelle"""
        import json
        self.notification_settings = json.dumps(settings)
        return self.save()
    
    def generate_api_key(self) -> str:
        """Yeni API anahtarı oluştur"""
        import secrets
        self.api_key = secrets.token_urlsafe(32)
        self.save()
        return self.api_key
    
    def enable_two_factor(self) -> str:
        """İki faktörlü doğrulamayı etkinleştir"""
        import pyotp
        secret = pyotp.random_base32()
        self.two_factor_secret = secret
        self.two_factor_enabled = True
        self.save()
        return secret
    
    def disable_two_factor(self) -> bool:
        """İki faktörlü doğrulamayı devre dışı bırak"""
        self.two_factor_enabled = False
        self.two_factor_secret = None
        return self.save()
    
    def verify_two_factor_token(self, token: str) -> bool:
        """İki faktörlü doğrulama tokenını kontrol et"""
        if not self.has_two_factor or not self.two_factor_secret:
            return False
        
        import pyotp
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(token, valid_window=1)
    
    def update_subscription(self, plan: str, expires_at: datetime) -> bool:
        """Abonelik bilgilerini güncelle"""
        self.subscription_plan = plan
        self.subscription_expires_at = expires_at.isoformat()
        return self.save()
    
    def get_activity_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Kullanıcı aktivite loglarını getir"""
        query = """
        SELECT * FROM user_activity_logs 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
        """
        return self.db.fetch_all(query, (self.id, limit))
    
    def log_activity(self, action: str, details: Dict[str, Any] = None) -> bool:
        """Kullanıcı aktivitesini logla"""
        import json
        query = """
        INSERT INTO user_activity_logs (user_id, action, details, ip_address, user_agent, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            self.id,
            action,
            json.dumps(details or {}),
            details.get('ip_address', ''),
            details.get('user_agent', ''),
            datetime.now()
        )
        return self.db.execute(query, values) is not None 