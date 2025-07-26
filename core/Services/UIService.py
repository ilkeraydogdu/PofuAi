"""
UI Service
Component verileri hazırlama ve yönetme servisi
"""
from flask import render_template
from typing import Dict, Any, Optional, List

class UIService:
    """
    UI Component verileri oluşturma ve yönetme servisi.
    Bu servis, controller'lar için component verilerini hazırlar ve şablonları render eder.
    """
    
    def __init__(self):
        """UI Servisini başlat"""
        self.messages = {
            'auth': {
                'register': {
                    'info_title': 'Bilgilendirme',
                    'info_message': 'Kayıt olurken girdiğiniz e-posta adresinize otomatik oluşturulan şifreniz gönderilecektir.',
                    'form_title': 'Kayıt Ol',
                    'form_subtitle': 'Hesabınızı oluşturmak için bilgilerinizi giriniz',
                    'submit_button': 'Kayıt Ol',
                    'login_link': 'Zaten hesabınız var mı? Giriş yapın'
                },
                'login': {
                    'form_title': 'Giriş Yap',
                    'form_subtitle': 'Hesabınıza giriş yapmak için bilgilerinizi giriniz',
                    'remember_me': 'Beni hatırla',
                    'forgot_password': 'Şifrenizi mi unuttunuz?',
                    'submit_button': 'Giriş Yap',
                    'register_link': 'Hesabınız yok mu? Kayıt olun'
                },
                'forgot_password': {
                    'form_title': 'Şifremi Unuttum',
                    'form_subtitle': 'Şifre sıfırlama bağlantısı için e-posta adresinizi giriniz',
                    'submit_button': 'Şifre Sıfırlama Bağlantısı Gönder',
                    'login_link': 'Giriş sayfasına dön'
                },
                'reset_password': {
                    'form_title': 'Şifre Sıfırla',
                    'form_subtitle': 'Lütfen yeni şifrenizi giriniz',
                    'submit_button': 'Şifremi Değiştir',
                    'login_link': 'Giriş sayfasına dön'
                }
            },
            'common': {
                'save': 'Kaydet',
                'cancel': 'İptal',
                'edit': 'Düzenle',
                'delete': 'Sil',
                'back': 'Geri',
                'next': 'İleri',
                'submit': 'Gönder',
                'loading': 'Yükleniyor...'
            }
        }
    
    def get_message(self, path: str, default: str = '') -> str:
        """
        Dinamik mesaj getir
        
        Args:
            path (str): Mesaj yolu (örn: 'auth.register.form_title')
            default (str): Varsayılan değer
            
        Returns:
            str: Mesaj metni
        """
        keys = path.split('.')
        value = self.messages
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value if isinstance(value, str) else default
    
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
        data.update({
            'app_name': 'PofuAi',
            'theme': data.get('theme', 'light'),
            'ui': self,  # UI servisini template'e gönder
        })
        
        # Şablonu render et
        return render_template(f"{template_name}.html", **data)
    
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
        
        # Dinamik mesajları ekle
        data['messages'] = {
            'form_title': self.get_message(f'auth.{page_type}.form_title', ''),
            'form_subtitle': self.get_message(f'auth.{page_type}.form_subtitle', ''),
            'submit_button': self.get_message(f'auth.{page_type}.submit_button', 'Gönder'),
            'info_title': self.get_message(f'auth.{page_type}.info_title', ''),
            'info_message': self.get_message(f'auth.{page_type}.info_message', '')
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
    
    #
    # Alert Component
    #
    def create_alert(self, message, type="info", title=None, 
                   dismissible=True, icon=None):
        """
        Alert component verisi oluştur
        
        Args:
            message (str): Alert mesajı
            type (str): Alert tipi (primary, success, danger, warning, info)
            title (str, optional): Alert başlığı
            dismissible (bool): Kapatılabilir mi
            icon (str, optional): Material icon kodu
            
        Returns:
            dict: Alert component verisi
        """
        return {
            "message": message,
            "type": type,
            "title": title,
            "dismissible": dismissible,
            "icon": icon
        }
    
    #
    # Badge Component
    #
    def create_badge(self, text, style="basic", class_name="bg-primary", 
                    position="top-right", icon=None, button_text=None,
                    button_class=None, rounded=True, sr_text=None):
        """
        Badge component verisi oluştur
        
        Args:
            text (str): Badge metni
            style (str): Badge stili (basic, pill, button, icon, positioned)
            class_name (str): Badge CSS sınıfı
            position (str): Badge pozisyonu (top-right, top-left, bottom-right, bottom-left)
            icon (str, optional): Material icon kodu
            button_text (str, optional): Buton metni (button ve positioned stilleri için)
            button_class (str, optional): Buton CSS sınıfı
            rounded (bool): Yuvarlak kenarlar
            sr_text (str, optional): Screen reader metni
            
        Returns:
            dict: Badge component verisi
        """
        return {
            "text": text,
            "style": style,
            "class": class_name,
            "position": position,
            "icon": icon,
            "button_text": button_text,
            "button_class": button_class,
            "rounded": rounded,
            "sr_text": sr_text
        }
    
    #
    # Button Component
    #
    def create_button(self, text, style="basic", class_name="btn-primary", 
                     size=None, icon=None, icon_position="left",
                     disabled=False, loading=False, full_width=False,
                     rounded=False, href=None, target=None, id=None,
                     custom_classes=None, attributes=None, type="button"):
        """
        Button component verisi oluştur
        
        Args:
            text (str): Buton metni
            style (str): Buton stili (basic, gradient, outline, inverse, raised)
            class_name (str): Buton CSS sınıfı
            size (str, optional): Buton boyutu (sm, lg, xl)
            icon (str, optional): Material icon kodu
            icon_position (str): İkon pozisyonu (left, right)
            disabled (bool): Devre dışı mı
            loading (bool): Yükleniyor mu
            full_width (bool): Tam genişlik
            rounded (bool): Yuvarlak kenarlar
            href (str, optional): Link URL'i
            target (str, optional): Link hedefi (_blank, _self)
            id (str, optional): HTML ID
            custom_classes (str, optional): Ek CSS sınıfları
            attributes (dict, optional): Ek HTML özellikleri
            type (str): Buton tipi (button, submit, reset)
            
        Returns:
            dict: Button component verisi
        """
        return {
            "text": text,
            "style": style,
            "class": class_name,
            "size": size,
            "icon": icon,
            "icon_position": icon_position,
            "disabled": disabled,
            "loading": loading,
            "full_width": full_width,
            "rounded": rounded,
            "href": href,
            "target": target,
            "id": id,
            "custom_classes": custom_classes,
            "attributes": attributes,
            "type": type
        }
    
    #
    # Card Component
    #
    def create_card(self, title=None, subtitle=None, content=None, 
                  header=True, footer=None, class_name=None,
                  header_class=None, body_class=None, footer_class=None):
        """
        Card component verisi oluştur
        
        Args:
            title (str, optional): Kart başlığı
            subtitle (str, optional): Kart alt başlığı
            content (str, optional): Kart içeriği
            header (bool): Başlık gösterilsin mi
            footer (str, optional): Kart footer içeriği
            class_name (str, optional): Kart CSS sınıfı
            header_class (str, optional): Başlık CSS sınıfı
            body_class (str, optional): Gövde CSS sınıfı
            footer_class (str, optional): Footer CSS sınıfı
            
        Returns:
            dict: Card component verisi
        """
        return {
            "title": title,
            "subtitle": subtitle,
            "content": content,
            "header": header,
            "footer": footer,
            "class": class_name,
            "header_class": header_class,
            "body_class": body_class,
            "footer_class": footer_class
        }
    
    #
    # Chip Component
    #
    def create_chip(self, text, style="bg-primary text-white", 
                   size=None, closable=False, image_src=None, 
                   image_alt="Contact Person", id=None):
        """
        Chip component verisi oluştur
        
        Args:
            text (str): Chip metni
            style (str): Chip CSS sınıfı
            size (str, optional): Chip boyutu (sm, md, lg)
            closable (bool): Kapatılabilir mi
            image_src (str, optional): Avatar resim URL'i
            image_alt (str): Avatar alt metni
            id (str, optional): HTML ID
            
        Returns:
            dict: Chip component verisi
        """
        return {
            "text": text,
            "style": style,
            "size": size,
            "closable": closable,
            "image_src": image_src,
            "image_alt": image_alt,
            "id": id
        }
    
    #
    # Modal Component
    #
    def create_modal(self, id, title, content=None, size=None,
                    centered=False, scrollable=False, static=False,
                    footer=None, close_button=True, 
                    primary_button=None, secondary_button=None):
        """
        Modal component verisi oluştur
        
        Args:
            id (str): Modal ID
            title (str): Modal başlığı
            content (str, optional): Modal içeriği
            size (str, optional): Modal boyutu (sm, lg, xl)
            centered (bool): Merkezlenmiş mi
            scrollable (bool): Kaydırılabilir mi
            static (bool): Statik backdrop
            footer (str, optional): Özel footer içeriği
            close_button (bool): Kapat butonu gösterilsin mi
            primary_button (dict, optional): Ana buton bilgisi
            secondary_button (dict, optional): İkincil buton bilgisi
            
        Returns:
            dict: Modal component verisi
        """
        return {
            "id": id,
            "title": title,
            "content": content,
            "size": size,
            "centered": centered,
            "scrollable": scrollable,
            "static": static,
            "footer": footer,
            "close_button": close_button,
            "primary_button": primary_button,
            "secondary_button": secondary_button
        }
    
    #
    # Pagination Component
    #
    def create_pagination(self, current_page, total_pages, size=None,
                         alignment="start", with_arrows=True, with_numbers=True,
                         url_pattern=None):
        """
        Pagination component verisi oluştur
        
        Args:
            current_page (int): Mevcut sayfa
            total_pages (int): Toplam sayfa sayısı
            size (str, optional): Boyut (sm, lg)
            alignment (str): Hizalama (start, center, end)
            with_arrows (bool): Ok butonları gösterilsin mi
            with_numbers (bool): Sayfa numaraları gösterilsin mi
            url_pattern (str, optional): URL şablonu (?page={page})
            
        Returns:
            dict: Pagination component verisi
        """
        return {
            "current_page": current_page,
            "total_pages": total_pages,
            "size": size,
            "alignment": alignment,
            "with_arrows": with_arrows,
            "with_numbers": with_numbers,
            "url_pattern": url_pattern
        }
    
    #
    # Progress Bar Component
    #
    def create_progress_bar(self, bars, height=None, mb=3):
        """
        Progress bar component verisi oluştur
        
        Args:
            bars (list): Bar listesi [{'value': 25, 'style': 'bg-primary', 'width': 25, 'label': '25%'}]
            height (str, optional): Yükseklik (örn: '10px')
            mb (int): Alt margin (mb-3)
            
        Returns:
            dict: Progress bar component verisi
        """
        return {
            "bars": bars,
            "height": height,
            "mb": mb
        }
    
    #
    # Spinner Component
    #
    def create_spinner(self, type="border", size=None, color="primary",
                      text="Yükleniyor...", role="status", aria_hidden=True,
                      custom_style=None):
        """
        Spinner component verisi oluştur
        
        Args:
            type (str): Spinner tipi (border, grow)
            size (str, optional): Spinner boyutu (sm, lg)
            color (str): Spinner rengi (primary, secondary, vb.)
            text (str): Yükleniyor metni
            role (str): ARIA role
            aria_hidden (bool): ARIA hidden
            custom_style (str, optional): Özel CSS stili
            
        Returns:
            dict: Spinner component verisi
        """
        return {
            "type": type,
            "size": size,
            "color": color,
            "text": text,
            "role": role,
            "aria_hidden": aria_hidden,
            "custom_style": custom_style
        }
    
    #
    # Tabs Component
    #
    def create_tabs(self, id, tabs, active_tab=0, style="tabs", 
                   fill=False, justified=False, vertical=False):
        """
        Tabs component verisi oluştur
        
        Args:
            id (str): Tabs ID
            tabs (list): Tab listesi [{'id': 'home', 'title': 'Home', 'content': 'Home content'}]
            active_tab (int): Aktif tab indeksi
            style (str): Tab stili (tabs, pills)
            fill (bool): Doldurucu tabs
            justified (bool): Eşit genişlikli tabs
            vertical (bool): Dikey tabs
            
        Returns:
            dict: Tabs component verisi
        """
        return {
            "id": id,
            "tabs": tabs,
            "active_tab": active_tab,
            "style": style,
            "fill": fill,
            "justified": justified,
            "vertical": vertical
        } 

    def get_base_layout(self):
        """Base layout component döndür"""
        class BaseLayout:
            def __init__(self):
                self.css_files = []
                self.js_files = []
            
            def add_css(self, css_file):
                """CSS dosyası ekle"""
                if css_file not in self.css_files:
                    self.css_files.append(css_file)
                return self
            
            def add_js(self, js_file):
                """JS dosyası ekle"""
                if js_file not in self.js_files:
                    self.js_files.append(js_file)
                return self
            
            def render(self, config):
                """Layout render et"""
                from flask import render_template
                
                # Şablonu render et
                return render_template("layouts/base_layout.html", **config)
        
        return BaseLayout()


# Global UI service instance
_ui_service = None

def get_ui_service() -> UIService:
    """
    UIService singleton instance'ını al
    
    Returns:
        UIService: UI service instance
    """
    global _ui_service
    if _ui_service is None:
        _ui_service = UIService()
    return _ui_service 