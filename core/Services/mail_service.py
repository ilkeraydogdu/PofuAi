"""
Mail Service
Email gönderme servisi
"""
import smtplib
import ssl
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Dict, Any, List, Optional
from core.Services.base_service import BaseService

class MailService(BaseService):
    """Email gönderme servisi"""
    
    def __init__(self):
        super().__init__()
        self.mail_config = self.get_config('mail') or {}
        
        # Email component manager'ı yükle
        try:
            # Template dizinini ayarla
            templates_dir = os.path.join(self.get_config('app.root_dir', ''), 'public', 'Views', 'emails')
            
            from core.Components.communication.email_components import EmailComponentManager
            self.email_component_manager = EmailComponentManager(templates_dir)
        except ImportError as e:
            self.log(f"Email component manager import error: {e}", "warning")
            self.email_component_manager = None
    
    def send(self, to: str, subject: str, body: str = None, template: str = None, data: Dict[str, Any] = None, attachments: List[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Email gönder
        
        Args:
            to: Alıcı email adresi
            subject: Email konusu
            body: Email içeriği (HTML)
            template: Kullanılacak şablon adı
            data: Şablon değişkenleri
            attachments: Dosya ekleri
            **kwargs: Ek parametreler
            
        Returns:
            Dict: Gönderim sonucu
        """
        try:
            # Template kullanılıyorsa body'yi oluştur
            if template and not body:
                body = self._render_template(template, data or {})
            
            # Email mesajını oluştur
            message = self._create_message(to, subject, body, attachments, **kwargs)
            
            # Email'i gönder
            sent = self._send_message(message)
            
            if sent:
                self.log(f"Email successfully sent to {to}", "info")
                return self.success_response("Email sent", {
                    "to": to, 
                    "subject": subject,
                    "template": template,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                return self.error_response("Failed to send email")
                
        except Exception as e:
            self.log(f"Mail send error: {str(e)}", "error")
            return self.error_response(f"Mail send error: {str(e)}")
    
    def send_to_multiple(self, recipients: List[str], subject: str, body: str = None, template: str = None, data: Dict[str, Any] = None, attachments: List[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Birden fazla kişiye email gönder"""
        try:
            results = []
            success_count = 0
            failed_count = 0
            
            for recipient in recipients:
                result = self.send(recipient, subject, body, template, data, attachments, **kwargs)
                results.append(result)
                if result.get('status') == 'success':
                    success_count += 1
                else:
                    failed_count += 1
            
            if failed_count == 0:
                return self.success_response(f"Sent emails to {success_count} recipients", {
                    "success_count": success_count,
                    "total": len(recipients),
                    "results": results
                })
            else:
                return self.error_response(f"Failed to send {failed_count} of {len(recipients)} emails", {
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "total": len(recipients),
                    "results": results
                })
            
        except Exception as e:
            self.log(f"Multiple mail send error: {str(e)}", "error")
            return self.error_response(f"Multiple mail send error: {str(e)}")
    
    def send_welcome_email(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hoş geldin e-postası gönder
        
        Args:
            user: Kullanıcı verileri
            
        Returns:
            Dict: Gönderim sonucu
        """
        # Kullanıcı kontrolü
        if not user or 'email' not in user or 'name' not in user:
            return self.error_response('Geçersiz kullanıcı verileri')
        
        # Şablon verileri
        template_data = {
            'user': user,
            'app_name': self.get_config('app.name', 'PofuAi'),
            'login_url': f"{self.get_config('app.url', 'http://localhost:5000')}/auth/login",
            'current_year': datetime.now().year
        }
        
        # Otomatik oluşturulan şifre varsa ekle
        if 'password_plain' in user:
            template_data['password'] = user['password_plain']
        
        # E-posta gönder
        return self.send(
            to=user['email'],
            subject=f"Hoş Geldiniz - {self.get_config('app.name', 'PofuAi')}",
            template='welcome',
            data=template_data
        )
    
    def send_password_reset_email(self, user: Dict[str, Any], reset_token: str) -> Dict[str, Any]:
        """
        Şifre sıfırlama email'i gönder
        
        Args:
            user: Kullanıcı bilgileri (name, email gerekli)
            reset_token: Şifre sıfırlama token'ı
            
        Returns:
            Dict: Gönderim sonucu
        """
        app_url = self.get_config('app.url', 'http://localhost:5000')
        support_email = self.mail_config.get('from', {}).get('address', 'support@example.com')
        reset_url = f"{app_url}/auth/reset-password?token={reset_token}"
        
        template_data = {
            'user': user,
            'reset_url': reset_url,
            'reset_token': reset_token,
            'expires_in': '1 saat',
            'support_email': support_email,
            'app_name': self.get_config('app.name', 'PofuAi'),
            'current_year': datetime.now().year
        }
        
        return self.send(
            to=user['email'],
            subject='Şifre Sıfırlama',
            template='password_reset',
            data=template_data
        )
    
    def send_contact_form_email(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        İletişim formu email'i gönder
        
        Args:
            form_data: Form bilgileri (name, email, subject, message gerekli)
            
        Returns:
            Dict: Gönderim sonucu
        """
        admin_email = self.get_config('admin.email', self.mail_config.get('from', {}).get('address', 'admin@example.com'))
        
        template_data = {
            'name': form_data.get('name', ''),
            'email': form_data.get('email', ''),
            'subject': form_data.get('subject', ''),
            'message': form_data.get('message', ''),
            'timestamp': form_data.get('timestamp', datetime.now().strftime('%d.%m.%Y %H:%M')),
            'app_name': self.get_config('app.name', 'PofuAi'),
            'current_year': datetime.now().year
        }
        
        return self.send(
            to=admin_email,
            subject=f"İletişim Formu: {form_data.get('subject', 'Konu Belirtilmemiş')}",
            template='contact',
            data=template_data
        )
    
    def send_notification_email(self, user: Dict[str, Any], notification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bildirim email'i gönder
        
        Args:
            user: Kullanıcı bilgileri (name, email gerekli)
            notification: Bildirim bilgileri (title, message gerekli)
            
        Returns:
            Dict: Gönderim sonucu
        """
        app_url = self.get_config('app.url', 'http://localhost:5000')
        
        template_data = {
            'user': user,
            'notification': notification,
            'app_url': app_url,
            'app_name': self.get_config('app.name', 'PofuAi'),
            'current_year': datetime.now().year
        }
        
        return self.send(
            to=user['email'],
            subject=notification.get('title', 'Yeni Bildirim'),
            template='notification',
            data=template_data
        )
    
    def send_welcome_email_with_password(self, user: Dict[str, Any], password: str) -> Dict[str, Any]:
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
                'current_year': datetime.now().year
            }
            
            result = self.send(
                to=user['email'],
                subject=f"Hoş Geldiniz - {self.get_config('app.name', 'PofuAi')} Hesap Bilgileriniz",
                template='welcome',
                data=template_data
            )
            return result
        except Exception as e:
            self.log(f"Welcome email with password error: {str(e)}", "error")
            return self.error_response(f"Welcome email with password error: {str(e)}")
    
    def _create_message(self, to: str, subject: str, body: str, attachments: List[Dict[str, Any]] = None, **kwargs) -> MIMEMultipart:
        """Email mesajını oluştur"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.mail_config.get('from', {}).get('address', 'noreply@example.com')
        message["To"] = to
        
        # CC ve BCC ekle
        if 'cc' in kwargs:
            message["Cc"] = kwargs['cc'] if isinstance(kwargs['cc'], str) else ", ".join(kwargs['cc'])
        if 'bcc' in kwargs:
            message["Bcc"] = kwargs['bcc'] if isinstance(kwargs['bcc'], str) else ", ".join(kwargs['bcc'])
        
        # HTML body
        html_part = MIMEText(body, "html")
        message.attach(html_part)
        
        # Plain text body (HTML'den text çıkar)
        text_part = MIMEText(self._html_to_text(body), "plain")
        message.attach(text_part)
        
        # Attachments
        if attachments:
            for attachment in attachments:
                self._add_attachment(message, attachment)
        
        return message
    
    def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """Email'e ek dosya ekle"""
        try:
            # Dosya path veya binary data olabilir
            if 'path' in attachment:
                file_path = attachment.get('path')
                file_name = attachment.get('name') or os.path.basename(file_path)
                
                with open(file_path, 'rb') as f:
                    content = f.read()
            elif 'data' in attachment:
                content = attachment.get('data')
                file_name = attachment.get('name', 'attachment')
            else:
                self.log("Attachment requires 'path' or 'data'", "warning")
                return
            
            part = MIMEApplication(content, Name=file_name)
            
            # Content-Disposition header'ı ekle
            part['Content-Disposition'] = f'attachment; filename="{file_name}"'
            message.attach(part)
            
        except Exception as e:
            self.log(f"Add attachment error: {str(e)}", "error")
    
    def _send_message(self, message: MIMEMultipart) -> bool:
        """Email mesajını gönder"""
        try:
            # SMTP bağlantısı
            host = self.mail_config.get('host', 'localhost')
            port = int(self.mail_config.get('port', 587))
            username = self.mail_config.get('username', '')
            password = self.mail_config.get('password', '')
            encryption = self.mail_config.get('encryption', 'tls')
            
            # SMTP bağlantısı
            if encryption == 'ssl':
                server = smtplib.SMTP_SSL(host, port)
            else:
                server = smtplib.SMTP(host, port)
                if encryption == 'tls':
                    server.starttls(context=ssl.create_default_context())
            
            # Authentication
            if username and password:
                server.login(username, password)
            
            # Email gönder
            server.send_message(message)
            server.quit()
            
            self.log(f"Email sent successfully to {message['To']}", "info")
            return True
            
        except Exception as e:
            self.log(f"SMTP send error: {str(e)}", "error")
            return False
    
    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Email template'ini render et"""
        try:
            # Temel verileri ekle
            render_data = {
                'app_name': self.get_config('app.name', 'PofuAi'),
                'current_year': datetime.now().year,
                'support_email': self.mail_config.get('from', {}).get('address', 'support@example.com'),
                'app_url': self.get_config('app.url', 'http://localhost:5000')
            }
            
            # Kullanıcı verilerini ekle
            render_data.update(data)
            
            # Email component manager kullanarak template render et
            if self.email_component_manager:
                return self.email_component_manager.render(template, render_data)
            else:
                # Fallback template
                return self._render_fallback_template(template, render_data)
            
        except Exception as e:
            self.log(f"Template render error: {str(e)}", "error")
            # Basit fallback template
            return f"""
            <html>
                <body>
                    <h2>{self.get_config('app.name', 'PofuAi')}</h2>
                    <p>Merhaba {data.get('user', {}).get('name', 'Kullanıcı')},</p>
                    <p>Bu bir otomatik e-postadır.</p>
                    <p>İyi günler dileriz,<br>{self.get_config('app.name', 'PofuAi')} Ekibi</p>
                </body>
            </html>
            """
    
    def _render_fallback_template(self, template: str, data: Dict[str, Any]) -> str:
        """Fallback template'i render et"""
        app_name = data.get('app_name', 'PofuAi')
        user_name = data.get('user', {}).get('name', 'Kullanıcı')
        current_year = data.get('current_year', datetime.now().year)
        
        # Temel HTML şablonu
        base_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{app_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #fff; padding: 20px; }}
                .header {{ background: #3461ff; color: #fff; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #888; border-top: 1px solid #eee; }}
                .button {{ display: inline-block; padding: 10px 20px; background: #3461ff; color: #fff; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{app_name}</h2>
                </div>
                <div class="content">
                    {content}
                </div>
                <div class="footer">
                    <p>&copy; {current_year} {app_name}. Tüm hakları saklıdır.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Template türüne göre içeriği oluştur
        if template == 'welcome':
            content = f"""
                <h3>Hoş Geldiniz!</h3>
                <p>Merhaba {user_name},</p>
                <p>{app_name}'ye hoş geldiniz! Hesabınız başarıyla oluşturuldu.</p>
                <p>Giriş yapmak için:</p>
                <p><a href="{data.get('login_url', '#')}" class="button">Giriş Yap</a></p>
                <p>Teşekkürler,<br>{app_name} Ekibi</p>
            """
        elif template == 'password_reset':
            content = f"""
                <h3>Şifre Sıfırlama</h3>
                <p>Merhaba {user_name},</p>
                <p>{app_name} hesabınız için şifre sıfırlama talebinde bulundunuz.</p>
                <p>Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın:</p>
                <p><a href="{data.get('reset_url', '#')}" class="button">Şifremi Sıfırla</a></p>
                <p>Bu bağlantı {data.get('expires_in', '1 saat')} içinde sona erecektir.</p>
                <p>Teşekkürler,<br>{app_name} Ekibi</p>
            """
        elif template == 'notification':
            notification = data.get('notification', {})
            content = f"""
                <h3>{notification.get('title', 'Yeni Bildirim')}</h3>
                <p>Merhaba {user_name},</p>
                <p>{notification.get('message', 'Yeni bir bildiriminiz var.')}</p>
                <p>Saygılarımızla,<br>{app_name} Ekibi</p>
            """
        elif template == 'contact':
            content = f"""
                <h3>İletişim Formu Mesajı</h3>
                <p><strong>İsim:</strong> {data.get('name', '')}</p>
                <p><strong>E-posta:</strong> {data.get('email', '')}</p>
                <p><strong>Konu:</strong> {data.get('subject', '')}</p>
                <p><strong>Mesaj:</strong></p>
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 4px; margin: 10px 0;">
                    {data.get('message', '')}
                </div>
                <p><strong>Tarih:</strong> {data.get('timestamp', '')}</p>
            """
        else:
            content = f"""
                <h3>{data.get('subject', 'Bildirim')}</h3>
                <p>Merhaba {user_name},</p>
                <p>Bu bir otomatik e-postadır.</p>
                <p>İyi günler dileriz,<br>{app_name} Ekibi</p>
            """
        
        # İçeriği şablona yerleştir
        return base_html.replace("{content_placeholder}", content)
    
    def _html_to_text(self, html: str) -> str:
        """HTML'den text çıkar"""
        try:
            import re
            
            # HTML tag'lerini kaldır
            text = re.sub(r'<[^>]+>', '', html)
            
            # HTML entities'leri decode et
            text = text.replace('&nbsp;', ' ')
            text = text.replace('&amp;', '&')
            text = text.replace('&lt;', '<')
            text = text.replace('&gt;', '>')
            text = text.replace('&quot;', '"')
            
            # Fazla boşlukları temizle
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
            
        except Exception as e:
            self.log(f"HTML to text error: {str(e)}", "error")
            return html
    
    def get_available_templates(self) -> List[str]:
        """Mevcut email template'lerini listele"""
        if self.email_component_manager:
            return self.email_component_manager.get_available_templates()
        else:
            return ['welcome', 'password_reset', 'notification', 'contact']

# Global mail service instance
_mail_service = None

def get_mail_service() -> MailService:
    """Global mail service instance'ını al"""
    global _mail_service
    if _mail_service is None:
        _mail_service = MailService()
    return _mail_service 