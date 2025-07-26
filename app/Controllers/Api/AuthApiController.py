"""
Auth API Controller
Authentication API endpoint'leri
"""
from app.Controllers.BaseController import BaseController
from app.Models.User import User
from core.Services.error_handler import error_handler
from core.Services.base_service import BaseService

class AuthApiController(BaseController):
    """Auth API controller'ı"""
    
    def login(self):
        """Login API"""
        try:
            # Input'ları al
            data = self.get_all_input()
            
            # Validation kuralları
            rules = {
                'email': 'required|email',
                'password': 'required'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Kullanıcıyı bul
            user = User.find_by_email(data['email'])
            
            if not user:
                return self.error_response('Geçersiz email veya şifre', 401)
            
            # Şifreyi kontrol et
            hasher = BaseService.get_hasher()
            if not hasher.check(data['password'], user.password):
                return self.error_response('Geçersiz email veya şifre', 401)
            
            # Kullanıcı aktif mi kontrol et
            if not user.is_active:
                return self.error_response('Hesabınız aktif değil', 401)
            
            # JWT token oluştur
            token = self._generate_jwt_token(user)
            
            # Son giriş zamanını güncelle
            user.update_last_login()
            
            # Log
            self.log('info', f'API: Kullanıcı giriş yaptı: {user.email}', {
                'user_id': user.id,
                'email': user.email,
                'ip': self.get_client_ip()
            })
            
            return self.json_response({
                'success': True,
                'message': 'Giriş başarılı',
                'data': {
                    'user': user.to_dict(),
                    'token': token,
                    'token_type': 'Bearer',
                    'expires_in': 3600  # 1 saat
                }
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def register(self):
        """Register API"""
        try:
            # Input'ları al
            data = self.get_all_input()
            
            # Validation kuralları
            rules = {
                'name': 'required|min:2|max:50',
                'email': 'required|email|unique:users,email',
                'password': 'required|min:8|confirmed',
                'password_confirmation': 'required',
                'username': 'required|min:3|max:20|unique:users,username',
                'terms': 'required'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Kullanıcı oluştur
            user = User.create_user(data)
            
            if not user:
                return self.error_response('Kullanıcı oluşturulamadı', 500)
            
            # JWT token oluştur
            token = self._generate_jwt_token(user)
            
            # Hoş geldin email'i gönder
            self._send_welcome_email(user)
            
            # Log
            self.log('info', f'API: Yeni kullanıcı kaydoldu: {user.email}', {
                'user_id': user.id,
                'email': user.email,
                'ip': self.get_client_ip()
            })
            
            return self.json_response({
                'success': True,
                'message': 'Kayıt başarılı',
                'data': {
                    'user': user.to_dict(),
                    'token': token,
                    'token_type': 'Bearer',
                    'expires_in': 3600  # 1 saat
                }
            }, 201)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def logout(self):
        """Logout API"""
        try:
            user = self.get_user()
            
            if user:
                # Log
                self.log('info', f'API: Kullanıcı çıkış yaptı: {user.get("email")}', {
                    'user_id': user.get('id'),
                    'email': user.get('email'),
                    'ip': self.get_client_ip()
                })
            
            # Token'ı blacklist'e ekle
            token = self._get_token_from_header()
            if token:
                self._blacklist_token(token)
            
            return self.json_response({
                'success': True,
                'message': 'Çıkış başarılı'
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def refresh(self):
        """Token yenileme API"""
        try:
            token = self._get_token_from_header()
            
            if not token:
                return self.error_response('Token gerekli', 401)
            
            # Token'ı doğrula ve yenile
            new_token = self._refresh_jwt_token(token)
            
            if new_token:
                return self.json_response({
                    'success': True,
                    'message': 'Token yenilendi',
                    'data': {
                        'token': new_token,
                        'token_type': 'Bearer',
                        'expires_in': 3600  # 1 saat
                    }
                })
            else:
                return self.error_response('Geçersiz token', 401)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def forgotPassword(self):
        """Şifre sıfırlama API"""
        try:
            # Input'ları al
            data = self.get_all_input()
            
            # Validation kuralları
            rules = {
                'email': 'required|email'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Kullanıcıyı bul
            user = User.find_by_email(data['email'])
            
            if not user:
                # Güvenlik için aynı mesajı döndür
                return self.json_response({
                    'success': True,
                    'message': 'Şifre sıfırlama linki gönderildi'
                })
            
            # Şifre sıfırlama token'ı oluştur
            token = self._create_password_reset_token(user)
            
            # Email gönder
            self._send_password_reset_email(user, token)
            
            # Log
            self.log('info', f'API: Şifre sıfırlama isteği: {user.email}', {
                'user_id': user.id,
                'email': user.email,
                'ip': self.get_client_ip()
            })
            
            return self.json_response({
                'success': True,
                'message': 'Şifre sıfırlama linki gönderildi'
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def resetPassword(self):
        """Şifre sıfırlama işlemi API"""
        try:
            # Input'ları al
            data = self.get_all_input()
            
            # Validation kuralları
            rules = {
                'token': 'required',
                'password': 'required|min:8|confirmed',
                'password_confirmation': 'required'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Token'ı doğrula
            user = self._verify_password_reset_token(data['token'])
            
            if not user:
                return self.error_response('Geçersiz veya süresi dolmuş token', 400)
            
            # Şifreyi değiştir
            if user.change_password(data['password']):
                # Token'ı geçersiz kıl
                self._invalidate_password_reset_token(data['token'])
                
                # Log
                self.log('info', f'API: Şifre sıfırlandı: {user.email}', {
                    'user_id': user.id,
                    'email': user.email,
                    'ip': self.get_client_ip()
                })
                
                return self.json_response({
                    'success': True,
                    'message': 'Şifre başarıyla sıfırlandı'
                })
            else:
                return self.error_response('Şifre değiştirilemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def _generate_jwt_token(self, user) -> str:
        """JWT token oluştur"""
        import jwt
        import datetime
        
        payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'iat': datetime.datetime.utcnow()
        }
        
        secret = self.config.get('app.jwt_secret', 'your-secret-key')
        return jwt.encode(payload, secret, algorithm='HS256')
    
    def _refresh_jwt_token(self, token: str) -> str:
        """JWT token yenile"""
        import jwt
        
        try:
            secret = self.config.get('app.jwt_secret', 'your-secret-key')
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            
            # Kullanıcıyı bul
            user = User.find(payload['user_id'])
            if not user or not user.is_active:
                return None
            
            # Yeni token oluştur
            return self._generate_jwt_token(user)
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def _get_token_from_header(self) -> str:
        """Header'dan token al"""
        auth_header = self.request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # 'Bearer ' kısmını çıkar
        
        return None
    
    def _blacklist_token(self, token: str):
        """Token'ı blacklist'e ekle"""
        from core.Services.cache_service import CacheService
        cache = CacheService()
        
        # Token'ı 1 saat boyunca blacklist'te tut
        cache.set(f'blacklist_{token}', True, 3600)
    
    def _create_password_reset_token(self, user) -> str:
        """Şifre sıfırlama token'ı oluştur"""
        import secrets
        token = secrets.token_urlsafe(32)
        
        # Token'ı cache'e kaydet (1 saat geçerli)
        from core.Services.cache_service import CacheService
        cache = CacheService()
        cache.set(f'password_reset_{token}', user.id, 3600)
        
        return token
    
    def _verify_password_reset_token(self, token: str):
        """Şifre sıfırlama token'ını doğrula"""
        from core.Services.cache_service import CacheService
        cache = CacheService()
        
        user_id = cache.get(f'password_reset_{token}')
        if user_id:
            return User.find(user_id)
        
        return None
    
    def _invalidate_password_reset_token(self, token: str):
        """Şifre sıfırlama token'ını geçersiz kıl"""
        from core.Services.cache_service import CacheService
        cache = CacheService()
        cache.delete(f'password_reset_{token}')
    
    def _send_welcome_email(self, user):
        """Hoş geldin email'i gönder"""
        try:
            from core.Services.mail_service import MailService
            mail_service = MailService()
            
            mail_service.send(
                to=user.email,
                subject='PofuAi\'ye Hoş Geldiniz!',
                template='emails.welcome',
                data={'user': user.to_dict()}
            )
        except Exception as e:
            self.log('error', f'Welcome email error: {str(e)}')
    
    def _send_password_reset_email(self, user, token):
        """Şifre sıfırlama email'i gönder"""
        try:
            from core.Services.mail_service import MailService
            mail_service = MailService()
            
            reset_url = f"{self.config.get('app.url')}/auth/reset-password/{token}"
            
            mail_service.send(
                to=user.email,
                subject='Şifre Sıfırlama',
                template='emails.password-reset',
                data={
                    'user': user.to_dict(),
                    'reset_url': reset_url
                }
            )
        except Exception as e:
            self.log('error', f'Password reset email error: {str(e)}') 