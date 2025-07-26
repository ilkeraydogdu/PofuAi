"""
Service Architecture Example Usage
Yeni service mimarisinin kullanım örnekleri
"""

from typing import Dict, Any, List
from datetime import datetime

from .base_service import BaseService, service_event, validate_service_input, service_retry
from .mail_service import MailService, SMTPDriver
from .cache_service import CacheService, FileCacheDriver
from .queue_service import QueueService, FileQueueDriver, Job, JobPriority
from .notification_service import NotificationService, EmailChannel, NotificationPriority
from .events import Event, SystemEvents, on_event
from .validators import ValidationResult
from .service_container import ServiceContainer, register_service, resolve_service

class UserService(BaseService):
    """Kullanıcı servisi - Yeni architecture örneği"""
    
    def __init__(self):
        super().__init__()
        self._mail_service = None
        self._cache_service = None
        self._queue_service = None
        self._notification_service = None
        
        # Event listener'ları ekle
        self._setup_event_listeners()
    
    def _setup_event_listeners(self):
        """Event listener'ları kur"""
        self.listen_event(SystemEvents.USER_REGISTERED, self._on_user_registered)
        self.listen_event(SystemEvents.USER_LOGIN, self._on_user_login)
    
    @service_event("user.service.method_called")
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı getir"""
        try:
            # Cache'den kontrol et
            cache_key = f"user:{user_id}"
            cached_user = self._get_cache_service().get(cache_key)
            
            if cached_user:
                self.dispatch_event(SystemEvents.CACHE_HIT, {'key': cache_key})
                return self.success_response(cached_user, "Kullanıcı cache'den getirildi")
            
            # Veritabanından getir (simüle edilmiş)
            user = self._fetch_user_from_db(user_id)
            
            if user:
                # Cache'e kaydet
                self._get_cache_service().set(cache_key, user, ttl=3600)
                self.dispatch_event(SystemEvents.CACHE_MISS, {'key': cache_key})
                
                return self.success_response(user, "Kullanıcı getirildi")
            else:
                return self.error_response("Kullanıcı bulunamadı", 404)
                
        except Exception as e:
            return self.handle_exception(e)
    
    @validate_service_input({
        'email': ['required', 'email'],
        'password': ['required', 'min_length:8'],
        'name': ['required', 'min_length:2', 'max_length:50'],
        'phone': ['phone']
    })
    @service_event("user.service.registration")
    def register_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Kullanıcı kaydı"""
        try:
            # Kullanıcı oluştur (simüle edilmiş)
            user = {
                'id': self._generate_user_id(),
                'email': data['email'],
                'name': data['name'],
                'phone': data.get('phone'),
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            # Event gönder
            self.dispatch_event(SystemEvents.USER_REGISTERED, {
                'user_id': user['id'],
                'email': user['email']
            })
            
            # Hoş geldin e-postası gönder
            self._send_welcome_email(user)
            
            return self.success_response(user, "Kullanıcı başarıyla kaydedildi")
            
        except Exception as e:
            return self.handle_exception(e)
    
    @validate_service_input({
        'email': ['required', 'email'],
        'password': ['required']
    })
    @service_retry(max_attempts=3, delay=1.0)
    def login_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Kullanıcı girişi"""
        try:
            # Giriş doğrulama (simüle edilmiş)
            user = self._authenticate_user(data['email'], data['password'])
            
            if user:
                # Login event'i gönder
                self.dispatch_event(SystemEvents.USER_LOGIN, {
                    'user_id': user['id'],
                    'email': user['email']
                })
                
                return self.success_response({
                    'user': user,
                    'token': self._generate_token(user['id'])
                }, "Giriş başarılı")
            else:
                return self.error_response("Geçersiz e-posta veya şifre", 401)
                
        except Exception as e:
            return self.handle_exception(e)
    
    def _on_user_registered(self, event: Event):
        """Kullanıcı kayıt event'i dinleyicisi"""
        user_data = event.data
        self.log(f"Yeni kullanıcı kaydı: {user_data['email']}")
        
        # Queue'ya job ekle
        job = Job(
            name="send_welcome_notification",
            data={'user_id': user_data['user_id']},
            priority=JobPriority.NORMAL
        )
        
        self._get_queue_service().push(job)
    
    def _on_user_login(self, event: Event):
        """Kullanıcı giriş event'i dinleyicisi"""
        user_data = event.data
        self.log(f"Kullanıcı girişi: {user_data['email']}")
        
        # Son giriş zamanını güncelle
        self._update_last_login(user_data['user_id'])
    
    def _get_cache_service(self) -> CacheService:
        """Cache servisini getir"""
        if not self._cache_service:
            self._cache_service = resolve_service('cache_service')
        return self._cache_service
    
    def _get_queue_service(self) -> QueueService:
        """Queue servisini getir"""
        if not self._queue_service:
            self._queue_service = resolve_service('queue_service')
        return self._queue_service
    
    def _get_mail_service(self) -> MailService:
        """Mail servisini getir"""
        if not self._mail_service:
            self._mail_service = resolve_service('mail_service')
        return self._mail_service
    
    def _get_notification_service(self) -> NotificationService:
        """Notification servisini getir"""
        if not self._notification_service:
            self._notification_service = resolve_service('notification_service')
        return self._notification_service
    
    def _fetch_user_from_db(self, user_id: int) -> Dict[str, Any]:
        """Veritabanından kullanıcı getir (simüle edilmiş)"""
        # Simüle edilmiş veritabanı sorgusu
        return {
            'id': user_id,
            'email': f'user{user_id}@example.com',
            'name': f'User {user_id}',
            'created_at': datetime.now().isoformat()
        }
    
    def _generate_user_id(self) -> int:
        """Kullanıcı ID'si oluştur"""
        import random
        return random.randint(1000, 9999)
    
    def _generate_token(self, user_id: int) -> str:
        """Token oluştur"""
        import hashlib
        return hashlib.md5(f"{user_id}_{datetime.now()}".encode()).hexdigest()
    
    def _authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Kullanıcı doğrula (simüle edilmiş)"""
        # Simüle edilmiş doğrulama
        if email == "test@example.com" and password == "password123":
            return {
                'id': 1,
                'email': email,
                'name': 'Test User'
            }
        return None
    
    def _send_welcome_email(self, user: Dict[str, Any]):
        """Hoş geldin e-postası gönder"""
        try:
            mail_service = self._get_mail_service()
            
            mail_service.send(
                to=user['email'],
                subject="Hoş Geldiniz!",
                body=f"Merhaba {user['name']}, hesabınız başarıyla oluşturuldu.",
                template="welcome_email",
                template_data={'user': user}
            )
            
        except Exception as e:
            self.log(f"Hoş geldin e-postası gönderilemedi: {e}", "error")
    
    def _update_last_login(self, user_id: int):
        """Son giriş zamanını güncelle"""
        # Simüle edilmiş güncelleme
        self.log(f"Son giriş zamanı güncellendi: {user_id}")

"""
Example Usage
Örnek kullanımlar
"""

def mail_service_example():
    """Mail servisi örnek kullanımı"""
    from core.Services.mail_service import get_mail_service
    
    # Mail servisini al
    mail_service = get_mail_service()
    
    # Basit email gönderimi
    mail_service.send(
        to="user@example.com",
        subject="Test Email",
        body="<h1>Merhaba!</h1><p>Bu bir test emailidir.</p>"
    )
    
    # Template ile email gönderimi
    user = {
        "id": 1,
        "name": "Test Kullanıcı",
        "email": "user@example.com"
    }
    
    mail_service.send_welcome_email(user)
    
    # Şifre sıfırlama emaili
    mail_service.send_password_reset_email(
        user=user,
        reset_url="https://pofuai.com/reset-password?token=abc123"
    )
    
    # İletişim formu emaili
    form_data = {
        "name": "İletişim Eden",
        "email": "contact@example.com",
        "subject": "Bilgi Talebi",
        "message": "Merhaba, ürünleriniz hakkında bilgi almak istiyorum.",
        "timestamp": "01.08.2023 14:30"
    }
    
    mail_service.send_contact_form_email(form_data)
    
    # Bildirim emaili
    notification = {
        "id": 1,
        "title": "Yeni Yorum",
        "message": "Gönderinize yeni bir yorum yapıldı.",
        "action_url": "https://pofuai.com/posts/1#comments",
        "action_text": "Yorumu Görüntüle"
    }
    
    mail_service.send_notification_email(user, notification)
    
    # Ekli dosya ile email gönderimi
    attachments = [
        {
            "path": "storage/files/document.pdf",
            "name": "Belge.pdf"
        }
    ]
    
    mail_service.send(
        to="user@example.com",
        subject="Ekli Dosya",
        body="<h1>Merhaba!</h1><p>Ekteki dosyayı inceleyebilirsiniz.</p>",
        attachments=attachments
    )
    
    # Birden fazla kişiye email gönderimi
    recipients = [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com"
    ]
    
    mail_service.send_to_multiple(
        recipients=recipients,
        subject="Toplu Email",
        body="<h1>Merhaba!</h1><p>Bu bir toplu emaildir.</p>"
    )
    
    # Test ortamında gönderilen emailleri görüntüleme
    sent_emails = mail_service.get_sent_emails()
    print(f"Gönderilen email sayısı: {len(sent_emails)}")
    
    # Mevcut email şablonlarını listele
    templates = mail_service.get_available_templates()
    print(f"Mevcut şablonlar: {templates}")

# Service Container Kurulumu
def setup_service_container():
    """Service container'ı kur"""
    
    # Mail Service
    register_service('mail_service', MailService())
    
    # Cache Service
    cache_service = CacheService()
    cache_service.set_driver('file', FileCacheDriver())
    register_service('cache_service', cache_service)
    
    # Queue Service
    queue_service = QueueService()
    queue_service.set_driver('file', FileQueueDriver())
    register_service('queue_service', queue_service)
    
    # Notification Service
    notification_service = NotificationService()
    notification_service.add_channel('email', EmailChannel())
    register_service('notification_service', notification_service)
    
    # User Service
    user_service = UserService()
    register_service('user_service', user_service)

# Kullanım Örnekleri
def example_usage():
    """Kullanım örnekleri"""
    
    # Service container'ı kur
    setup_service_container()
    
    # User service'i al
    user_service = resolve_service('user_service')
    
    print("=== Service Architecture Örnekleri ===\n")
    
    # 1. Kullanıcı Kaydı
    print("1. Kullanıcı Kaydı:")
    registration_data = {
        'email': 'test@example.com',
        'password': 'password123',
        'name': 'Test User',
        'phone': '+90 555 123 4567'
    }
    
    result = user_service.register_user(registration_data)
    print(f"Sonuç: {result}\n")
    
    # 2. Kullanıcı Girişi
    print("2. Kullanıcı Girişi:")
    login_data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    result = user_service.login_user(login_data)
    print(f"Sonuç: {result}\n")
    
    # 3. Kullanıcı Getirme (Cache ile)
    print("3. Kullanıcı Getirme:")
    result = user_service.get_user(1)
    print(f"Sonuç: {result}\n")
    
    # 4. Service Bilgileri
    print("4. Service Bilgileri:")
    service_info = user_service.get_service_info()
    print(f"Service Info: {service_info}\n")
    
    # 5. Event Geçmişi
    print("5. Event Geçmişi:")
    event_dispatcher = user_service.get_event_dispatcher()
    history = event_dispatcher.get_event_history(limit=5)
    for event in history:
        print(f"Event: {event.name} - {event.data}")

# Event Listener Örnekleri
@on_event(SystemEvents.MAIL_SENT)
def on_mail_sent(event: Event):
    """Mail gönderildiğinde çalışır"""
    print(f"Mail gönderildi: {event.data}")

@on_event(SystemEvents.CACHE_HIT)
def on_cache_hit(event: Event):
    """Cache hit olduğunda çalışır"""
    print(f"Cache hit: {event.data}")

@on_event(SystemEvents.JOB_COMPLETED)
def on_job_completed(event: Event):
    """Job tamamlandığında çalışır"""
    print(f"Job tamamlandı: {event.data}")

if __name__ == "__main__":
    example_usage()
    mail_service_example() 