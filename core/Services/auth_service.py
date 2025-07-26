"""
Auth Service
Merkezi kullanıcı kayıt ve kimlik doğrulama servisi
"""
from typing import Dict, Any, Optional
from app.Models.User import User
from core.Services.mail_service import MailService, get_mail_service
from core.Services.token_service import get_token_service
from core.Services.base_service import BaseService

class AuthService(BaseService):
    """Kullanıcı kayıt ve kimlik doğrulama için merkezi servis"""
    def __init__(self):
        super().__init__()
        self.mail_service = get_mail_service()
        self.token_service = get_token_service()

    def register_user(self, data: Dict[str, Any], send_email: bool = True) -> Optional[User]:
        """
        Merkezi kullanıcı kayıt akışı
        - Form verilerini güvenlik temizliği
        - Geçici şifre üretimi
        - Mail gönderimi (başarılı ise veritabanına kayıt)
        - Şifre yenileme sayfasına yönlendirme
        """
        # Form verilerini güvenlik temizliği
        cleaned_data = self._clean_form_data(data)
        
        # Önce geçici şifre üret
        temp_password = cleaned_data.get('password_plain')
        if not temp_password:
            temp_password = self.token_service.generate_memorable_password()

        # Geçici kullanıcı verisi oluştur (veritabanına kaydetmeden)
        temp_user_data = {
            'name': cleaned_data.get('name'),
            'email': cleaned_data.get('email'),
            'phone': cleaned_data.get('phone'),
            'password_plain': temp_password
        }

        # Şifre sıfırlama token'ı oluştur
        reset_token = self.token_service.generate_token(
            'temp_user',  # Geçici kullanıcı için
            'reset_password',
            {'email': data.get('email'), 'name': data.get('name')},
            7200  # 2 saat geçerli
        )

        # Geçici şifreyi sakla
        temp_password_token = self.token_service.store_temporary_password(
            'temp_user',  # Geçici kullanıcı için
            temp_password,
            86400  # 24 saat geçerli
        )

        # Hoş geldin e-postası gönder
        mail_sent = False
        if send_email:
            app_url = self.get_config('app.url', 'http://localhost:5000')
            login_url = f"{app_url}/auth/login"
            reset_url = f"{app_url}/auth/reset-password?token={reset_token}"
            template_data = {
                'user': temp_user_data,
                'password': temp_password,
                'app_name': self.get_config('app.name', 'PofuAi'),
                'app_url': app_url,
                'login_url': login_url,
                'reset_url': reset_url,
                'current_year': self.get_current_year(),
                'expires_in': '24 saat'
            }
            
            mail_result = self.mail_service.send(
                to=data.get('email'),
                subject=f"Hoş Geldiniz - {self.get_config('app.name', 'PofuAi')} Hesap Bilgileriniz",
                template='welcome',
                data=template_data
            )
            
            mail_sent = mail_result.get('status') == 'success'
            
            # Mail gönderim sonucunu logla
            if mail_sent:
                self.log(f"Hoş geldin maili başarıyla gönderildi: {data.get('email')}", "info")
            else:
                self.log(f"Mail gönderimi başarısız: {data.get('email')} - {mail_result.get('message', 'Bilinmeyen hata')}", "error")

        # Mail gönderimi başarılı ise kullanıcıyı veritabanına kaydet
        if mail_sent:
            user = User.create_user(data)
            if user:
                # Kullanıcıya token bilgilerini ekle
                user.reset_token = reset_token
                user.temp_password_token = temp_password_token
                user.password_plain = temp_password
                self.log(f"Kullanıcı başarıyla kaydedildi: {user.email}", "info")
                return user
            else:
                self.log("Kullanıcı veritabanına kaydedilemedi", "error")
                return None
        else:
            self.log("Mail gönderimi başarısız olduğu için kullanıcı kaydedilmedi", "error")
            return None

    def _clean_form_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Form verilerini güvenlik temizliği
        - XSS koruması
        - SQL Injection koruması
        - Özel karakter temizliği
        """
        import html
        import re
        
        cleaned_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # HTML karakterlerini temizle
                cleaned_value = html.escape(value.strip())
                
                # Özel karakterleri temizle
                cleaned_value = re.sub(r'[<>"\']', '', cleaned_value)
                
                # Çoklu boşlukları tek boşluğa çevir
                cleaned_value = re.sub(r'\s+', ' ', cleaned_value)
                
                cleaned_data[key] = cleaned_value
            else:
                cleaned_data[key] = value
        
        return cleaned_data

    def get_current_year(self):
        from datetime import datetime
        return datetime.now().year

# Singleton erişim
_auth_service_instance = None
def get_auth_service() -> AuthService:
    global _auth_service_instance
    if _auth_service_instance is None:
        _auth_service_instance = AuthService()
    return _auth_service_instance 