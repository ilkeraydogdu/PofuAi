"""
Auth Controller
Kullanıcı kimlik doğrulama işlemlerini yönetir
"""
from flask import request, redirect, url_for, flash, session
from datetime import datetime
import hashlib
from app.Controllers.BaseController import BaseController
from app.Models.User import User
from core.Services.auth_service import get_auth_service
from core.Services.notification_service import get_notification_service
from core.Services.mail_service import get_mail_service
from core.Services.token_service import get_token_service
from core.Services.UIService import UIService


class AuthController(BaseController):
    """Kimlik doğrulama kontrolcüsü"""
    
    def __init__(self):
        super().__init__()
        self.auth_service = get_auth_service()
        self.notification_service = get_notification_service()
        self.mail_service = get_mail_service()
        self.token_service = get_token_service()
        self.ui_service = UIService()
    
    def login(self):
        """Giriş sayfası"""
        if request.method == 'POST':
            return self._handle_login()
        
        return self.ui_service.render_auth_page('login')
    
    def register(self):
        """Kayıt sayfası"""
        if request.method == 'POST':
            return self._handle_register()
        
        return self.ui_service.render_auth_page('register')
    
    def check_domain(self):
        """Domain kontrolü"""
        domain = request.args.get('domain')
        
        if not domain:
            return {'valid': False, 'message': 'Domain gerekli'}
        
        exists = self._check_domain_exists(domain)
        
        return {
            'valid': not exists,
            'message': 'Domain kullanımda' if exists else 'Domain müsait'
        }
    
    def _check_domain_exists(self, domain):
        """Domain kullanımda mı kontrol et"""
        # Gerçek uygulamada veritabanından kontrol edilmeli
        existing_domains = ['example.com', 'test.com', 'demo.com']
        return domain.lower() in existing_domains
    
    def forgot_password(self):
        """Şifremi unuttum sayfası"""
        if request.method == 'POST':
            return self._handle_forgot_password()
        
        return self.ui_service.render_auth_page('forgot_password')
    
    def reset_password(self):
        """Şifre sıfırlama sayfası"""
        token = request.args.get('token')
        new_registration = request.args.get('new_registration', False)
        
        if request.method == 'POST':
            return self._handle_reset_password(token)
        
        return self.ui_service.render_auth_page('reset_password', {
            'token': token,
            'new_registration': new_registration
        })
    
    def logout(self):
        """Çıkış işlemi"""
        session.clear()
        flash('Başarıyla çıkış yaptınız.', 'success')
        return redirect(url_for('auth.login'))
    
    def _handle_login(self):
        """Giriş form işleme"""
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('E-posta ve şifre gereklidir.', 'danger')
            return self.ui_service.render_auth_page('login')
        
        # Kullanıcıyı doğrula
        user = self._authenticate_user(email, password)
        
        if user:
            # Oturum başlat
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['is_admin'] = user.get('is_admin', False)
            
            # Giriş bildirimi gönder
            self._send_login_notification(user)
            
            flash(f'Hoş geldiniz, {user["name"]}!', 'success')
            
            # Admin ise admin paneline, değilse ana sayfaya yönlendir
            if user.get('is_admin', False):
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('home.index'))
        else:
            flash('Geçersiz e-posta veya şifre.', 'danger')
            return self.ui_service.render_auth_page('login')
    
    def _handle_register(self):
        """Kayıt form işleme"""
        # Formdan gelen verileri al
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
        }
        
        # Debug: Form verilerini logla
        print(f"DEBUG: Form data received: {data}")
        
        # Captcha doğrulama
        captcha_answer = request.form.get('captcha_answer')
        expected_answer = request.form.get('captcha_expected')
        
        if not captcha_answer or captcha_answer.lower() != expected_answer.lower():
            flash('Captcha doğrulaması başarısız.', 'danger')
            return self.ui_service.render_auth_page('register')
        
        # Kullanım koşulları kontrolü
        terms = request.form.get('terms')
        if not terms:
            flash('Kullanım koşullarını kabul etmelisiniz.', 'danger')
            return self.ui_service.render_auth_page('register')
        
        # Debug: Auth service'i al
        print("DEBUG: Getting auth service...")
        auth_service = get_auth_service()
        print(f"DEBUG: Auth service: {auth_service}")
        
        # Debug: Register user çağrısı
        print("DEBUG: Calling register_user...")
        user = auth_service.register_user(data)
        print(f"DEBUG: Register result: {user}")
        
        if user:
            # Başarılı kayıt - şifre yenileme sayfasına yönlendir
            flash('Kaydınız başarıyla tamamlandı! Giriş bilgileriniz e-posta adresinize gönderildi.', 'success')
            return redirect(url_for('auth.reset_password', token=user.reset_token))
        else:
            # Email kontrolü
            existing_user = User.find_by_email(data.get('email'))
            if existing_user:
                flash('Bu e-posta adresi zaten kullanımda. Lütfen farklı bir e-posta adresi deneyin.', 'danger')
            else:
                flash('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'danger')
            return self.ui_service.render_auth_page('register')
    
    def _handle_forgot_password(self):
        """Şifremi unuttum form işleme"""
        email = request.form.get('email')
        
        if not email:
            flash('E-posta gereklidir.', 'danger')
            return self.ui_service.render_auth_page('forgot_password')
        
        # Kullanıcı var mı kontrol et
        user = self._get_user_by_email(email)
        
        if not user:
            flash('Bu e-posta adresiyle kayıtlı bir hesap bulunamadı.', 'danger')
            return self.ui_service.render_auth_page('forgot_password')
        
        # Şifre sıfırlama token'ı oluştur (TokenService kullanarak)
        token = self.token_service.generate_token(
            user['id'], 
            'reset_password', 
            {'email': user['email'], 'name': user['name']},
            3600  # 1 saat geçerli
        )
        
        # Şifre sıfırlama e-postası gönder
        if self._send_reset_email(user, token):
            flash('Şifre sıfırlama bağlantısı e-posta adresinize gönderildi. Bağlantı 1 saat süreyle geçerlidir.', 'success')
        else:
            flash('E-posta gönderilirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.', 'danger')
        
        return redirect(url_for('auth.login'))
    
    def _handle_reset_password(self, token):
        """Şifre sıfırlama form işleme"""
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Basit doğrulama
        if not password:
            flash('Şifre gereklidir.', 'danger')
            return self.ui_service.render_auth_page('reset_password', {'token': token})
        
        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalıdır.', 'danger')
            return self.ui_service.render_auth_page('reset_password', {'token': token})
        
        if password != password_confirm:
            flash('Şifreler eşleşmiyor.', 'danger')
            return self.ui_service.render_auth_page('reset_password', {'token': token})
        
        # Token'ı doğrula
        valid, token_data = self.token_service.verify_token(token, 'reset_password')
        
        if not valid or not token_data:
            flash('Geçersiz şifre sıfırlama bağlantısı veya süresi dolmuş.', 'danger')
            return redirect(url_for('auth.forgot_password'))
        
        # Kullanıcı ID'sini al
        user_id = token_data.get('user_id')
        
        if not user_id:
            flash('Geçersiz şifre sıfırlama bağlantısı.', 'danger')
            return redirect(url_for('auth.forgot_password'))
        
        # Şifreyi güncelle
        if self._update_password(user_id, password):
            # Token'ı geçersiz kıl
            self.token_service.invalidate_token(token)
            
            flash('Şifreniz başarıyla güncellendi. Yeni şifrenizle giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Şifre güncellenirken bir hata oluştu. Lütfen tekrar deneyin.', 'danger')
            return self.ui_service.render_auth_page('reset_password', {'token': token})
    
    def _authenticate_user(self, email, password):
        """Kullanıcı doğrulama"""
        # Gerçek uygulamada veritabanından kontrol edilmeli
        # Örnek kullanıcı
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if email == 'admin@example.com' and hashed_password == hashlib.sha256('admin123'.encode()).hexdigest():
            return {
                'id': 1,
                'name': 'Admin User',
                'email': 'admin@example.com',
                'is_admin': True
            }
        
        if email == 'user@example.com' and hashed_password == hashlib.sha256('user123'.encode()).hexdigest():
            return {
                'id': 2,
                'name': 'Regular User',
                'email': 'user@example.com',
                'is_admin': False
            }
        
        return None
    
    def _is_email_taken(self, email):
        """E-posta kullanımda mı kontrol et"""
        # Gerçek uygulamada veritabanından kontrol edilmeli
        return email in ['admin@example.com', 'user@example.com']
    
    def _create_user(self, name, email, password, phone=None):
        """Kullanıcı oluştur"""
        # Gerçek uygulamada veritabanına kaydedilmeli
        # Örnek kullanıcı
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        return {
            'id': 3,  # Yeni ID
            'name': name,
            'email': email,
            'phone': phone,
            'password': hashed_password,
            'created_at': datetime.now().isoformat()
        }
    
    def _get_user_by_email(self, email):
        """E-posta ile kullanıcı bul"""
        # Gerçek uygulamada veritabanından kontrol edilmeli
        if email == 'admin@example.com':
            return {
                'id': 1,
                'name': 'Admin User',
                'email': 'admin@example.com'
            }
        
        if email == 'user@example.com':
            return {
                'id': 2,
                'name': 'Regular User',
                'email': 'user@example.com'
            }
        
        return None
    
    def _update_password(self, user_id, password):
        """Şifreyi güncelle"""
        # Gerçek uygulamada veritabanında güncellenmeli
        # Örnek olarak başarılı döndürüyoruz
        return True
    
    def _send_welcome_email(self, user):
        """Hoş geldin e-postası gönder"""
        if not self.mail_service:
            return False
        
        try:
            result = self.mail_service.send_welcome_email(user)
            return result.get('status') == 'success'
        except:
            return False
    
    def _send_reset_email(self, user, token):
        """Şifre sıfırlama e-postası gönder"""
        if not self.mail_service:
            return False
        
        try:
            result = self.mail_service.send_password_reset_email(user, token)
            return result.get('status') == 'success'
        except:
            return False
    
    def _send_welcome_email_with_password(self, user, password):
        """Hoş geldin e-postası gönder (şifre ile birlikte)"""
        if not self.mail_service:
            return False
        
        try:
            # Kullanıcı ve şifre bilgilerini içeren e-posta gönder
            user_with_password = user.copy()
            user_with_password['password_plain'] = password
            
            # Şifre sıfırlama token'ı varsa, reset_url ekle
            app_url = self.get_config('app.url', 'http://localhost:5000')
            login_url = f"{app_url}/auth/login"
            reset_url = ""
            
            # Token varsa reset_url oluştur
            if 'reset_token' in user:
                reset_url = f"{app_url}/auth/reset-password?token={user['reset_token']}"
            
            template_data = {
                'user': user,
                'password': password,
                'app_name': self.get_config('app.name', 'PofuAi'),
                'app_url': app_url,
                'login_url': login_url,
                'reset_url': reset_url,
                'current_year': datetime.now().year,
                'expires_in': '24 saat'  # Geçici şifre geçerlilik süresi
            }
            
            result = self.mail_service.send(
                to=user['email'],
                subject=f"Hoş Geldiniz - {self.get_config('app.name', 'PofuAi')} Hesap Bilgileriniz",
                template='welcome',
                data=template_data
            )
            return result.get('status') == 'success'
        except Exception as e:
            self.log_error(f"Welcome email with password error: {str(e)}")
            return False
    
    def _send_login_notification(self, user):
        """Giriş bildirimi gönder"""
        try:
            notification = {
                'title': 'Yeni Giriş',
                'message': f'{user["name"]} hesabına giriş yapıldı.',
                'type': 'login',
                'data': {
                    'user_id': user['id'],
                    'login_time': datetime.now().isoformat(),
                    'ip_address': request.remote_addr
                }
            }
            
            recipient = {
                'id': user['id'],
                'email': user['email'],
                'name': user['name']
            }
            
            result = self.notification_service.send(notification, recipient)
            return result.get('status') == 'success'
        except Exception as e:
            self.log_error(f"Login notification error: {str(e)}")
            return False
    
    def log_error(self, message):
        """Hata logla"""
        print(f"AuthController Error: {message}") 