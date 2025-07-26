"""
Page Controller
Statik sayfalar controller'ı
"""
from app.Controllers.BaseController import BaseController
from core.Services.error_handler import error_handler

class PageController(BaseController):
    """Sayfa controller'ı"""
    
    def about(self):
        """Hakkımızda sayfası"""
        try:
            return self.view('pages.about', {
                'title': 'Hakkımızda',
                'description': 'PofuAi hakkında bilgiler'
            })
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def contact(self):
        """İletişim sayfası"""
        try:
            return self.view('pages.contact', {
                'title': 'İletişim',
                'description': 'Bizimle iletişime geçin'
            })
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def send_contact(self):
        """İletişim formu gönderimi"""
        try:
            # Input'ları al
            data = self.get_all_input()
            
            # Validation kuralları
            rules = {
                'name': 'required|min:2|max:50',
                'email': 'required|email',
                'subject': 'required|min:3|max:100',
                'message': 'required|min:10|max:1000'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Email gönder
            from core.Services.mail_service import MailService
            mail_service = MailService()
            
            mail_service.send(
                to=self.config.get('mail.from.address'),
                subject=f"İletişim Formu: {data['subject']}",
                template='emails.contact',
                data={
                    'name': data['name'],
                    'email': data['email'],
                    'subject': data['subject'],
                    'message': data['message']
                }
            )
            
            # Log
            self.log('info', 'İletişim formu gönderildi', {
                'name': data['name'],
                'email': data['email'],
                'subject': data['subject']
            })
            
            return self.json_response({'message': 'Mesajınız başarıyla gönderildi'})
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def privacy(self):
        """Gizlilik politikası"""
        try:
            return self.view('pages.privacy', {
                'title': 'Gizlilik Politikası',
                'description': 'Gizlilik politikamız'
            })
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def terms(self):
        """Kullanım şartları"""
        try:
            return self.view('pages.terms', {
                'title': 'Kullanım Şartları',
                'description': 'Kullanım şartlarımız'
            })
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def faq(self):
        """Sık sorulan sorular"""
        try:
            faqs = [
                {
                    'question': 'PofuAi nedir?',
                    'answer': 'PofuAi modern web teknolojileri ile geliştirilmiş bir platformdur.'
                },
                {
                    'question': 'Nasıl kayıt olabilirim?',
                    'answer': 'Ana sayfadaki kayıt ol butonuna tıklayarak ücretsiz hesap oluşturabilirsiniz.'
                },
                {
                    'question': 'Şifremi unuttum, ne yapmalıyım?',
                    'answer': 'Giriş sayfasındaki "Şifremi unuttum" linkine tıklayarak şifrenizi sıfırlayabilirsiniz.'
                },
                {
                    'question': 'İçerik paylaşabilir miyim?',
                    'answer': 'Evet, kayıt olduktan sonra içerik paylaşabilir ve diğer kullanıcılarla etkileşime geçebilirsiniz.'
                },
                {
                    'question': 'Verilerim güvende mi?',
                    'answer': 'Evet, tüm verileriniz şifrelenmiş olarak saklanır ve güvenlik standartlarına uygun olarak korunur.'
                }
            ]
            
            return self.view('pages.faq', {
                'title': 'Sık Sorulan Sorular',
                'description': 'Sık sorulan sorular ve cevapları',
                'faqs': faqs
            })
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def help(self):
        """Yardım sayfası"""
        try:
            help_sections = [
                {
                    'title': 'Başlangıç Rehberi',
                    'content': 'Platformu kullanmaya başlamak için temel bilgiler.'
                },
                {
                    'title': 'İçerik Paylaşma',
                    'content': 'Nasıl içerik paylaşacağınızı öğrenin.'
                },
                {
                    'title': 'Profil Yönetimi',
                    'content': 'Profilinizi nasıl düzenleyeceğinizi öğrenin.'
                },
                {
                    'title': 'Güvenlik',
                    'content': 'Hesabınızı güvende tutmak için ipuçları.'
                }
            ]
            
            return self.view('pages.help', {
                'title': 'Yardım',
                'description': 'Kullanım kılavuzu ve yardım',
                'help_sections': help_sections
            })
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def maintenance(self):
        """Bakım sayfası"""
        try:
            return self.view('pages.maintenance', {
                'title': 'Bakım Modu',
                'description': 'Sistem bakımda, lütfen bekleyin.'
            })
        except Exception as e:
            return error_handler.handle_error(e, self.request) 