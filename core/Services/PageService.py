"""
Page Service
Sayfa render işlemleri için servis
"""
from flask import render_template
from typing import Dict, Any, Optional, List
import os
import json

class PageContent:
    """Sayfa içeriği sınıfı"""
    
    def __init__(self, 
                 title: str = "", 
                 subtitle: str = "", 
                 description: str = "", 
                 meta_tags: Dict[str, str] = None,
                 content_blocks: Dict[str, Any] = None,
                 page_config: Dict[str, Any] = None):
        """
        Sayfa içeriği oluştur
        
        Args:
            title (str): Sayfa başlığı
            subtitle (str): Sayfa alt başlığı
            description (str): Sayfa açıklaması (meta)
            meta_tags (Dict[str, str]): Meta etiketleri
            content_blocks (Dict[str, Any]): İçerik blokları
            page_config (Dict[str, Any]): Sayfa yapılandırması
        """
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.meta_tags = meta_tags or {}
        self.content_blocks = content_blocks or {}
        self.page_config = page_config or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Dict nesnesine dönüştür"""
        return {
            'title': self.title,
            'subtitle': self.subtitle,
            'description': self.description,
            'meta_tags': self.meta_tags,
            'content_blocks': self.content_blocks,
            'page_config': self.page_config
        }

class PageService:
    """
    Sayfa render işlemleri için servis.
    Bu servis, tüm sayfa render işlemlerini tek bir yerden yönetir.
    """
    
    def __init__(self):
        """Page servisini başlat"""
        self.global_data = {
            'app_name': 'PofuAi',
            'theme': 'light'
        }
        # Merkezi sayfa içerik veritabanı
        self.page_contents = self._load_page_contents()
        # Dinamik metinler
        self.texts = self._load_text_contents()
    
    def _load_page_contents(self) -> Dict[str, PageContent]:
        """
        Sayfa içeriklerini yükle - normalde bir veritabanından yüklenir,
        şimdilik örnek verilerle dolduralım
        """
        pages = {}
        
        # Ana sayfa
        pages['home/index'] = PageContent(
            title='Dashboard',
            subtitle='PofuAi Dashboard',
            description='PofuAi yönetim paneli ana sayfası',
            content_blocks={
                'welcome_message': 'PofuAi yönetim paneline hoş geldiniz!',
                'stats_title': 'İstatistikler',
                'recent_activities_title': 'Son Aktiviteler',
                'popular_content_title': 'Popüler İçerikler'
            },
            page_config={
                'show_stats': True,
                'show_graphs': True,
                'show_recent_activities': True,
                'show_popular_content': True
            }
        )
        
        # Auth sayfaları
        pages['auth/login'] = PageContent(
            title='Giriş',
            subtitle='Hesabınıza giriş yapın',
            description='PofuAi kullanıcı girişi',
            content_blocks={
                'form_title': 'Giriş Yap',
                'form_subtitle': 'Hesabınıza giriş yapmak için bilgilerinizi giriniz',
                'remember_me': 'Beni hatırla',
                'forgot_password': 'Şifrenizi mi unuttunuz?',
                'submit_button': 'Giriş Yap',
                'register_link': 'Hesabınız yok mu? Kayıt olun'
            }
        )
        
        pages['auth/register'] = PageContent(
            title='Kayıt',
            subtitle='Yeni hesap oluşturun',
            description='PofuAi kullanıcı kaydı',
            content_blocks={
                'form_title': 'Kayıt Ol',
                'form_subtitle': 'Hesabınızı oluşturmak için bilgilerinizi giriniz',
                'info_title': 'Bilgilendirme',
                'info_message': 'Kayıt olurken kullandığınız mail adresinize giriş bilgileriniz gönderilecektir.',
                'submit_button': 'Kayıt Ol',
                'login_link': 'Zaten hesabınız var mı? Giriş yapın'
            }
        )
        
        pages['auth/forgot_password'] = PageContent(
            title='Şifremi Unuttum',
            subtitle='Şifre sıfırlama',
            description='PofuAi şifre sıfırlama',
            content_blocks={
                'form_title': 'Şifremi Unuttum',
                'form_subtitle': 'Şifre sıfırlama bağlantısı için e-posta adresinizi giriniz',
                'submit_button': 'Şifre Sıfırlama Bağlantısı Gönder',
                'login_link': 'Giriş sayfasına dön'
            }
        )
        
        pages['auth/reset_password'] = PageContent(
            title='Şifre Sıfırla',
            subtitle='Yeni şifre oluştur',
            description='PofuAi şifre sıfırlama',
            content_blocks={
                'form_title': 'Şifre Sıfırla',
                'form_subtitle': 'Lütfen yeni şifrenizi giriniz',
                'submit_button': 'Şifremi Değiştir',
                'login_link': 'Giriş sayfasına dön'
            }
        )
        
        # Hata sayfaları
        pages['errors/404'] = PageContent(
            title='Sayfa Bulunamadı',
            subtitle='404 Hatası',
            description='Sayfa bulunamadı',
            content_blocks={
                'error_title': 'Sayfa Bulunamadı',
                'error_message': 'Aradığınız sayfa bulunamadı veya taşınmış olabilir.',
                'back_link': 'Ana sayfaya dön'
            }
        )
        
        pages['errors/500'] = PageContent(
            title='Sunucu Hatası',
            subtitle='500 Hatası',
            description='Sunucu hatası',
            content_blocks={
                'error_title': 'Sunucu Hatası',
                'error_message': 'Bir sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin.',
                'back_link': 'Ana sayfaya dön'
            }
        )
        
        return pages
    
    def _load_text_contents(self) -> Dict[str, Dict[str, Any]]:
        """
        Metin içeriklerini yükle - normalde bir veritabanından veya dosyadan yüklenir
        """
        return {
            'common': {
                'save': 'Kaydet',
                'cancel': 'İptal',
                'edit': 'Düzenle',
                'delete': 'Sil',
                'back': 'Geri',
                'next': 'İleri',
                'submit': 'Gönder',
                'loading': 'Yükleniyor...',
                'search': 'Ara',
                'filter': 'Filtrele',
                'actions': 'İşlemler',
                'view': 'Görüntüle',
                'create': 'Oluştur',
                'update': 'Güncelle',
                'remove': 'Kaldır'
            },
            'navigation': {
                'dashboard': 'Dashboard',
                'users': 'Kullanıcılar',
                'posts': 'İçerikler',
                'products': 'Ürünler',
                'orders': 'Siparişler',
                'settings': 'Ayarlar',
                'profile': 'Profil',
                'logout': 'Çıkış'
            },
            'auth': {
                'login': {
                    'title': 'Giriş',
                    'form_title': 'Giriş Yap',
                    'form_subtitle': 'Hesabınıza giriş yapmak için bilgilerinizi giriniz',
                    'email_label': 'E-posta',
                    'password_label': 'Şifre',
                    'remember_me': 'Beni hatırla',
                    'forgot_password': 'Şifrenizi mi unuttunuz?',
                    'submit_button': 'Giriş Yap',
                    'register_link': 'Hesabınız yok mu? Kayıt olun'
                },
                'register': {
                    'title': 'Kayıt',
                    'form_title': 'Kayıt Ol',
                    'form_subtitle': 'Hesabınızı oluşturmak için bilgilerinizi giriniz',
                    'name_label': 'Ad Soyad',
                    'email_label': 'E-posta',
                    'password_label': 'Şifre',
                    'password_confirm_label': 'Şifre Tekrarı',
                    'terms_label': 'Kullanım koşullarını okudum ve kabul ediyorum',
                    'submit_button': 'Kayıt Ol',
                    'login_link': 'Zaten hesabınız var mı? Giriş yapın',
                    'info_title': 'Bilgilendirme',
                    'info_message': 'Kayıt olurken kullandığınız mail adresinize giriş bilgileriniz gönderilecektir.'
                },
                'forgot_password': {
                    'title': 'Şifremi Unuttum',
                    'form_title': 'Şifremi Unuttum',
                    'form_subtitle': 'Şifre sıfırlama bağlantısı için e-posta adresinizi giriniz',
                    'email_label': 'E-posta',
                    'submit_button': 'Şifre Sıfırlama Bağlantısı Gönder',
                    'login_link': 'Giriş sayfasına dön'
                },
                'reset_password': {
                    'title': 'Şifre Sıfırla',
                    'form_title': 'Şifre Sıfırla',
                    'form_subtitle': 'Lütfen yeni şifrenizi giriniz',
                    'password_label': 'Yeni Şifre',
                    'password_confirm_label': 'Şifre Tekrarı',
                    'submit_button': 'Şifremi Değiştir',
                    'login_link': 'Giriş sayfasına dön'
                }
            }
        }
    
    def get_text(self, path: str, default: str = '') -> str:
        """
        Dinamik metin getir
        
        Args:
            path (str): Metin yolu (örn: 'auth.register.form_title')
            default (str): Varsayılan değer
            
        Returns:
            str: Metin içeriği
        """
        keys = path.split('.')
        value = self.texts
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value if isinstance(value, str) else default
    
    def get_page_content(self, page_name: str) -> PageContent:
        """
        Sayfa içeriğini getir
        
        Args:
            page_name (str): Sayfa adı (örn: 'home/index')
            
        Returns:
            PageContent: Sayfa içeriği
        """
        if page_name in self.page_contents:
            return self.page_contents[page_name]
        
        # Sayfa bulunamazsa boş bir sayfa içeriği döndür
        return PageContent(
            title=page_name.split('/')[-1].capitalize(),
            subtitle='',
            description=''
        )
    
    def set_page_content(self, page_name: str, content: PageContent):
        """
        Sayfa içeriğini ayarla
        
        Args:
            page_name (str): Sayfa adı
            content (PageContent): Sayfa içeriği
        """
        self.page_contents[page_name] = content
    
    def update_page_content_block(self, page_name: str, block_name: str, content: str):
        """
        Sayfa içeriğindeki bir bloğu güncelle
        
        Args:
            page_name (str): Sayfa adı
            block_name (str): Blok adı
            content (str): Yeni içerik
        """
        if page_name in self.page_contents:
            self.page_contents[page_name].content_blocks[block_name] = content
    
    def set_global_data(self, key: str, value: Any):
        """
        Global veri ekle
        
        Args:
            key (str): Veri anahtarı
            value (Any): Veri değeri
        """
        self.global_data[key] = value
    
    def render_template(self, template_name: str, data: Dict[str, Any] = None) -> str:
        """
        Şablonu render et
        
        Args:
            template_name (str): Şablon adı
            data (Dict[str, Any], optional): Şablona gönderilecek veriler
            
        Returns:
            str: Render edilmiş HTML içeriği
        """
        data = data or {}
        
        # Global verileri ekle
        merged_data = self.global_data.copy()
        
        # Sayfa içeriğini ekle
        page_content = self.get_page_content(template_name)
        merged_data['page'] = page_content.to_dict()
        
        # Dinamik metinleri ekle
        merged_data['text'] = self.texts
        
        # PageService'i şablona gönder
        merged_data['page_service'] = self
        
        # Kullanıcı verilerini ekle
        merged_data.update(data)
        
        # Şablonu render et
        return render_template(f"{template_name}.html", **merged_data)
    
    def render_auth_page(self, page_type: str, data: Dict[str, Any] = None) -> str:
        """
        Auth sayfasını render et
        
        Args:
            page_type (str): Sayfa tipi (login, register, forgot_password, reset_password)
            data (Dict[str, Any], optional): Şablona gönderilecek veriler
            
        Returns:
            str: Render edilmiş HTML içeriği
        """
        data = data or {}
        
        # Sayfa içeriğini al
        page_content = self.get_page_content(f"auth/{page_type}")
        
        # Messages nesnesi oluştur (geriye dönük uyumluluk için)
        data['messages'] = {
            'form_title': page_content.content_blocks.get('form_title', ''),
            'form_subtitle': page_content.content_blocks.get('form_subtitle', ''),
            'submit_button': page_content.content_blocks.get('submit_button', 'Gönder'),
            'info_title': page_content.content_blocks.get('info_title', ''),
            'info_message': page_content.content_blocks.get('info_message', '')
        }
        
        # Token ekle (reset_password için)
        if page_type == 'reset_password' and 'token' in data:
            data['token'] = data['token']
        
        # Şablonu render et
        return self.render_template(f"auth/{page_type}", data)
    
    def render_page(self, page_name: str, data: Dict[str, Any] = None) -> str:
        """
        Sayfayı render et
        
        Args:
            page_name (str): Sayfa adı
            data (Dict[str, Any], optional): Şablona gönderilecek veriler
            
        Returns:
            str: Render edilmiş HTML içeriği
        """
        data = data or {}
        
        # Aktif menü bilgisini ekle
        if 'active_menu' not in data:
            data['active_menu'] = page_name.split('/')[-1]
        
        # Şablonu render et
        return self.render_template(page_name, data)
    
    def render_admin_page(self, page_name: str, data: Dict[str, Any] = None) -> str:
        """
        Admin sayfasını render et
        
        Args:
            page_name (str): Sayfa adı
            data (Dict[str, Any], optional): Şablona gönderilecek veriler
            
        Returns:
            str: Render edilmiş HTML içeriği
        """
        data = data or {}
        
        # Admin şablonunu kullan
        data['is_admin'] = True
        
        # Şablonu render et
        return self.render_template(f"admin/{page_name}", data)
    
    def render_error_page(self, error_code: int, message: str = None) -> str:
        """
        Hata sayfasını render et
        
        Args:
            error_code (int): Hata kodu
            message (str, optional): Hata mesajı
            
        Returns:
            str: Render edilmiş HTML içeriği
        """
        # Hata sayfası içeriğini al
        error_page = self.get_page_content(f"errors/{error_code}")
        
        data = {
            'error_code': error_code,
            'message': message or error_page.content_blocks.get('error_message', f'Hata {error_code}')
        }
        
        # Şablonu render et
        return self.render_template('errors/error', data)
    
    def export_page_contents(self, file_path: str = 'storage/config/page_contents.json'):
        """
        Sayfa içeriklerini dışa aktar
        
        Args:
            file_path (str): Dosya yolu
        """
        # Dizini oluştur
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Verileri dönüştür
        contents = {}
        for page_name, content in self.page_contents.items():
            contents[page_name] = content.to_dict()
        
        # JSON dosyasına yaz
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(contents, f, ensure_ascii=False, indent=4)
    
    def import_page_contents(self, file_path: str = 'storage/config/page_contents.json'):
        """
        Sayfa içeriklerini içe aktar
        
        Args:
            file_path (str): Dosya yolu
        """
        if not os.path.exists(file_path):
            return
        
        # JSON dosyasından oku
        with open(file_path, 'r', encoding='utf-8') as f:
            contents = json.load(f)
        
        # PageContent nesnelerine dönüştür
        for page_name, content in contents.items():
            self.page_contents[page_name] = PageContent(
                title=content.get('title', ''),
                subtitle=content.get('subtitle', ''),
                description=content.get('description', ''),
                meta_tags=content.get('meta_tags', {}),
                content_blocks=content.get('content_blocks', {}),
                page_config=content.get('page_config', {})
            ) 