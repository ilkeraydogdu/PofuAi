"""
Auth Page Service
Auth sayfaları için merkezi servis - Dinamik ve profesyonel yapı
"""

from typing import Dict, Any, Optional, List
import os
import json
from enum import Enum

# Enum tanımlamaları
class AuthType(Enum):
    """Auth form tipleri"""
    LOGIN = "login"
    REGISTER = "register"
    FORGOT_PASSWORD = "forgot_password"
    RESET_PASSWORD = "reset_password"

class AuthStyle(Enum):
    """Auth form stilleri"""
    BASIC = "basic"
    MODERN = "modern"
    GRADIENT = "gradient"
    DARK = "dark"
    LIGHT = "light"
    BOXED = "boxed"

class FormField:
    """Form alanı için dinamik yapı"""
    def __init__(self, name: str, label: str, field_type: str = "text", 
                 placeholder: str = "", required: bool = True, 
                 validation: Dict[str, Any] = None, options: List[Dict[str, str]] = None):
        self.name = name
        self.label = label
        self.field_type = field_type
        self.placeholder = placeholder
        self.required = required
        self.validation = validation or {}
        self.options = options or []

class AuthComponent:
    """Auth component sınıfı"""
    
    def __init__(self):
        """Auth component başlat"""
        pass
    
    def render_login_form(self, config: Dict[str, Any]) -> str:
        """Login formunu render et"""
        return f"""
        <form id="login-form" method="post" action="{config.get('action', '/auth/login')}">
            <div class="form-body">
                {config.get('form_fields', '')}
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary">{config.get('submit_text', 'Giriş Yap')}</button>
                </div>
            </div>
        </form>
        """
    
    def render_register_form(self, config: Dict[str, Any]) -> str:
        """Register formunu render et"""
        return f"""
        <form id="register-form" method="post" action="{config.get('action', '/auth/register')}">
            <div class="form-body">
                {config.get('form_fields', '')}
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary">{config.get('submit_text', 'Kayıt Ol')}</button>
                </div>
            </div>
        </form>
        """
    
    def render_forgot_password_form(self, config: Dict[str, Any]) -> str:
        """Şifremi unuttum formunu render et"""
        return f"""
        <form id="forgot-password-form" method="post" action="{config.get('action', '/auth/forgot-password')}">
            <div class="form-body">
                {config.get('form_fields', '')}
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary">{config.get('submit_text', 'Şifre Sıfırlama Linki Gönder')}</button>
                </div>
            </div>
        </form>
        """
    
    def render_reset_password_form(self, config: Dict[str, Any]) -> str:
        """Şifre sıfırlama formunu render et"""
        return f"""
        <form id="reset-password-form" method="post" action="{config.get('action', '/auth/reset-password')}">
            <div class="form-body">
                {config.get('form_fields', '')}
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary">{config.get('submit_text', 'Şifremi Sıfırla')}</button>
                </div>
            </div>
        </form>
        """

class AuthPageService:
    """Auth sayfaları için merkezi servis"""
    
    def __init__(self):
        self.auth_component = AuthComponent()
        self.config = self._get_default_config()
        self.form_configs = self._get_form_configs()
        self._load_config_from_file()
        self._load_form_configs_from_file()
    
    def _get_form_configs(self) -> Dict[AuthType, List[FormField]]:
        """Form konfigürasyonlarını alır"""
        return {
            AuthType.LOGIN: [
                FormField("email", "E-posta", "email", "ornek@email.com", True, 
                         {"pattern": r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", "message": "Geçerli bir email adresi giriniz"}),
                FormField("password", "Şifre", "password", "Şifrenizi girin", True,
                         {"minlength": "6", "message": "Şifre en az 6 karakter olmalıdır"})
            ],
            AuthType.REGISTER: [
                FormField("name", "Ad Soyad", "text", "Ad Soyad", True,
                         {"minlength": "2", "message": "Ad soyad en az 2 karakter olmalıdır"}),
                FormField("email", "E-posta Adresi", "email", "ornek@kullanici.com", True,
                         {"pattern": r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", "message": "Geçerli bir email adresi giriniz"}),
                FormField("username", "Kullanıcı Adı", "text", "Kullanıcı Adı", True,
                         {"minlength": "3", "message": "Kullanıcı adı en az 3 karakter olmalıdır"}),
                FormField("password", "Şifre", "password", "Şifrenizi girin", True,
                         {"minlength": "8", "message": "Şifre en az 8 karakter olmalıdır"}),
                FormField("password_confirmation", "Şifre Tekrarı", "password", "Şifrenizi tekrar girin", True,
                         {"minlength": "8", "message": "Şifre en az 8 karakter olmalıdır"})
            ],
            AuthType.FORGOT_PASSWORD: [
                FormField("email", "E-posta Adresi", "email", "ornek@kullanici.com", True,
                         {"pattern": r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", "message": "Geçerli bir email adresi giriniz"})
            ],
            AuthType.RESET_PASSWORD: [
                FormField("password", "Yeni Şifre", "password", "Yeni şifrenizi girin", True,
                         {"minlength": "8", "message": "Şifre en az 8 karakter olmalıdır"}),
                FormField("password_confirmation", "Şifre Tekrarı", "password", "Şifrenizi tekrar girin", True,
                         {"minlength": "8", "message": "Şifre en az 8 karakter olmalıdır"})
            ]
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Varsayılan konfigürasyon"""
        return {
            'app_name': 'PofuAi',
            'theme': 'blue-theme',
            'language': 'tr',
            'logo_url': '/static/assets/images/logo1.png',
            'favicon_url': '/static/assets/images/favicon-32x32.png',
            'static_base': '/static',
            'auth_style': AuthStyle.BOXED.value,  # Varsayılan olarak boxed
            'show_social': False,  # Varsayılan olarak kapalı
            'social_providers': [
                {
                    'name': 'Google',
                    'display_name': 'Google ile Giriş',
                    'icon': 'bi bi-google fs-5 text-white',
                    'color': 'bg-grd-danger',
                    'image': '/static/assets/images/apps/05.png',
                    'url': 'javascript:;',
                    'enabled': False
                },
                {
                    'name': 'Facebook',
                    'display_name': 'Facebook ile Giriş',
                    'icon': 'bi bi-facebook fs-5 text-white',
                    'color': 'bg-grd-deep-blue',
                    'image': '/static/assets/images/apps/17.png',
                    'url': 'javascript:;',
                    'enabled': False
                },
                {
                    'name': 'LinkedIn',
                    'display_name': 'LinkedIn ile Giriş',
                    'icon': 'bi bi-linkedin fs-5 text-white',
                    'color': 'bg-grd-info',
                    'image': '/static/assets/images/apps/18.png',
                    'url': 'javascript:;',
                    'enabled': False
                },
                {
                    'name': 'GitHub',
                    'display_name': 'GitHub ile Giriş',
                    'icon': 'bi bi-github fs-5 text-white',
                    'color': 'bg-grd-royal',
                    'image': '/static/assets/images/apps/19.png',
                    'url': 'javascript:;',
                    'enabled': False
                }
            ],
            'css_files': [
                '/static/assets/css/pace.min.css',
                '/static/assets/plugins/perfect-scrollbar/css/perfect-scrollbar.css',
                '/static/assets/plugins/metismenu/metisMenu.min.css',
                '/static/assets/plugins/metismenu/mm-vertical.css',
                '/static/assets/css/bootstrap.min.css',
                '/static/assets/css/bootstrap-extended.css',
                '/static/sass/main.css',
                '/static/sass/dark-theme.css',
                '/static/sass/blue-theme.css',
                '/static/sass/responsive.css'
            ],
            'js_files': [
                '/static/assets/js/pace.min.js',
                '/static/assets/js/jquery.min.js',
                '/static/assets/js/bootstrap.bundle.min.js'
            ],
            'external_css': [
                'https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;500;600&display=swap',
                'https://fonts.googleapis.com/css?family=Material+Icons+Outlined'
            ]
        }
    
    def _load_config_from_file(self):
        """Konfigürasyonu dosyadan yükle"""
        config_file = os.path.join('storage', 'config', 'auth_settings.json')
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # Sadece belirli ayarları yükle
                    if 'show_social' in saved_config:
                        self.config['show_social'] = saved_config['show_social']
                    if 'social_providers' in saved_config:
                        for provider in saved_config['social_providers']:
                            for i, default_provider in enumerate(self.config['social_providers']):
                                if default_provider['name'] == provider['name']:
                                    self.config['social_providers'][i]['enabled'] = provider['enabled']
        except Exception:
            # Dosya yoksa veya okuma hatası olursa varsayılan ayarları kullan
            pass
    
    def save_config_to_file(self):
        """Konfigürasyonu dosyaya kaydet"""
        config_file = os.path.join('storage', 'config', 'auth_settings.json')
        config_dir = os.path.dirname(config_file)
        
        # Dizin yoksa oluştur
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Sadece kaydetmek istediğimiz ayarları seç
        save_config = {
            'show_social': self.config['show_social'],
            'social_providers': []
        }
        
        for provider in self.config['social_providers']:
            save_config['social_providers'].append({
                'name': provider['name'],
                'enabled': provider['enabled']
            })
        
        # Dosyaya kaydet
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(save_config, f, ensure_ascii=False, indent=4)
    
    def enable_social_login(self, providers: List[str] = None):
        """Sosyal medya girişini etkinleştir"""
        if providers is None:
            # Tüm provider'ları etkinleştir
            for provider in self.config['social_providers']:
                provider['enabled'] = True
        else:
            # Sadece belirtilen provider'ları etkinleştir
            for provider in self.config['social_providers']:
                provider['enabled'] = provider['name'].lower() in [p.lower() for p in providers]
        
        self.config['show_social'] = True
        self.save_config_to_file()
    
    def disable_social_login(self):
        """Sosyal medya girişini devre dışı bırak"""
        for provider in self.config['social_providers']:
            provider['enabled'] = False
        self.config['show_social'] = False
        self.save_config_to_file()
    
    def get_enabled_social_providers(self) -> List[Dict[str, Any]]:
        """Etkinleştirilmiş sosyal medya sağlayıcılarını al"""
        return [p for p in self.config['social_providers'] if p['enabled']]
    
    def get_form_fields(self, auth_type: AuthType) -> List[FormField]:
        """Auth tipine göre form alanlarını al"""
        return self.form_configs.get(auth_type, [])
    
    def render_form_field(self, field: FormField) -> str:
        """Tek bir form alanını render eder"""
        required_attr = "required" if field.required else ""
        validation_attrs = ""
        
        if field.validation:
            for key, value in field.validation.items():
                if key != "message":
                    validation_attrs += f' {key}="{value}"'
        
        if field.field_type == "select":
            options_html = ""
            for option in field.options:
                options_html += f'<option value="{option["value"]}">{option["label"]}</option>'
            
            return f'''
            <div class="col-12">
                <label for="{field.name}" class="form-label">{field.label}</label>
                <select class="form-select" id="{field.name}" name="{field.name}" {required_attr} {validation_attrs}>
                    <option value="">{field.placeholder}</option>
                    {options_html}
                </select>
            </div>
            '''
        elif field.field_type == "password":
            return f'''
            <div class="col-12">
                <label for="{field.name}" class="form-label">{field.label}</label>
                <div class="input-group" id="show_hide_{field.name}">
                    <input type="password" class="form-control border-end-0" id="{field.name}" name="{field.name}" 
                           placeholder="{field.placeholder}" {required_attr} {validation_attrs}>
                    <a href="javascript:;" class="input-group-text bg-transparent">
                        <i class="bi bi-eye-slash-fill"></i>
                    </a>
                </div>
            </div>
            '''
        else:
            return f'''
            <div class="col-12">
                <label for="{field.name}" class="form-label">{field.label}</label>
                <input type="{field.field_type}" class="form-control" id="{field.name}" name="{field.name}" 
                       placeholder="{field.placeholder}" {required_attr} {validation_attrs}>
            </div>
            '''
    
    def render_dynamic_form(self, auth_type: AuthType) -> str:
        """Dinamik form render eder"""
        fields = self.get_form_fields(auth_type)
        form_fields_html = ""
        
        for field in fields:
            form_fields_html += self.render_form_field(field)
        
        return form_fields_html
    
    def _get_auth_texts(self) -> Dict[str, Dict[str, str]]:
        """Auth sayfaları için metinler"""
        return {
            AuthType.LOGIN: {
                'title': 'Giriş Yap',
                'subtitle': 'Hesabınıza giriş yapın',
                'button_text': 'Giriş Yap',
                'alt_text': 'Hesabınız yok mu?',
                'alt_link_text': 'Kayıt Ol',
                'alt_link': '/auth/register',
                'forgot_password_text': 'Şifremi Unuttum',
                'forgot_password_link': '/auth/forgot-password',
                'remember_me_text': 'Beni Hatırla'
            },
            AuthType.REGISTER: {
                'title': 'Kayıt Ol',
                'subtitle': 'Yeni bir hesap oluşturun',
                'button_text': 'Kayıt Ol',
                'alt_text': 'Zaten bir hesabınız var mı?',
                'alt_link_text': 'Giriş Yap',
                'alt_link': '/auth/login',
                'terms_text': 'Kayıt olarak <a href="javascript:;">Kullanım Şartları</a> ve <a href="javascript:;">Gizlilik Politikası</a>\'nı kabul etmiş olursunuz.'
            },
            AuthType.FORGOT_PASSWORD: {
                'title': 'Şifremi Unuttum',
                'subtitle': 'Şifre sıfırlama bağlantısı için e-posta adresinizi girin',
                'button_text': 'Sıfırlama Bağlantısı Gönder',
                'alt_text': 'Şifrenizi hatırladınız mı?',
                'alt_link_text': 'Giriş Sayfasına Dön',
                'alt_link': '/auth/login',
                'back_link': '/auth/login',
                'back_link_text': 'Giriş Sayfasına Dön'
            },
            AuthType.RESET_PASSWORD: {
                'title': 'Şifre Sıfırlama',
                'subtitle': 'Yeni şifrenizi belirleyin',
                'button_text': 'Şifremi Sıfırla',
                'alt_text': 'Şifrenizi hatırladınız mı?',
                'alt_link_text': 'Giriş Yap',
                'alt_link': '/auth/login'
            }
        }

    def get_page_config(self, auth_type: AuthType, custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = self.config.copy()
        auth_texts = self._get_auth_texts()
        key = auth_type.value
        # Auth tipine göre özel ayarlar
        if key in auth_texts:
            config.update({
                'title': f"{config['app_name']} - {auth_texts[key]['title']}",
                'page_title': auth_texts[key]['title'],
                'page_subtitle': auth_texts[key]['subtitle'],
                'submit_button_text': auth_texts[key]['button_text'],
                'submit_button_class': {
                    'login': 'btn-grd-primary',
                    'register': 'btn-grd-info',
                    'forgot_password': 'btn-grd-warning',
                    'reset_password': 'btn-grd-success',
                }[key],
                'auth_image': {
                    'login': '/static/assets/images/auth/login1.png',
                    'register': '/static/assets/images/auth/register1.png',
                    'forgot_password': '/static/assets/images/auth/forgot-password1.png',
                    'reset_password': '/static/assets/images/auth/forgot-password1.png',
                }[key],
                'auth_image_bg': {
                    'login': 'bg-grd-primary',
                    'register': 'bg-grd-info',
                    'forgot_password': 'bg-grd-warning',
                    'reset_password': 'bg-grd-success',
                }[key],
                'links': {
                    'login': '/auth/login',
                    'register': '/auth/register',
                    'forgot_password': '/auth/forgot-password',
                }
            })
        # Özel konfigürasyon varsa güncelle
        if custom_config:
            config.update(custom_config)
        return config
    
    def render_head(self, config: Dict[str, Any]) -> str:
        """Head bölümünü render eder"""
        css_links = '\n'.join([f'<link rel="stylesheet" href="{css}">' for css in config['css_files']])
        external_css = '\n'.join([f'<link rel="stylesheet" href="{css}">' for css in config['external_css']])
        
        auth_style = config.get('auth_style', AuthStyle.BASIC.value)
        custom_css = ""
        
        if auth_style == AuthStyle.BOXED.value:
            custom_css = '''
            <style>
                .separator {
                    display: flex;
                    align-items: center;
                    text-align: center;
                    margin: 30px 0;
                }
                
                .separator .line {
                    height: 1px;
                    flex: 1;
                    background-color: #dee2e6;
                }
                
                .separator p {
                    padding: 0 10px;
                    color: #6c757d;
                    font-size: 14px;
                }
                
                .btn-filter {
                    border: 1px solid #dee2e6;
                    background-color: transparent;
                    transition: all 0.3s;
                }
                
                .btn-filter:hover {
                    background-color: rgba(0, 0, 0, 0.05);
                }
                
                .vh-100 {
                    min-height: 100vh;
                }
                
                .bg-grd-primary {
                    background: linear-gradient(45deg, #3461ff, #8454eb);
                }
                
                .bg-grd-info {
                    background: linear-gradient(45deg, #14abef, #7659ff);
                }
                
                .bg-grd-warning {
                    background: linear-gradient(45deg, #ffcb0b, #ff6b01);
                }
                
                .bg-grd-success {
                    background: linear-gradient(45deg, #18bb6b, #009688);
                }
                
                .bg-grd-danger {
                    background: linear-gradient(45deg, #f41127, #fc4a1a);
                }
                
                .bg-grd-deep-blue {
                    background: linear-gradient(45deg, #0d6efd, #0143a3);
                }
                
                .bg-grd-royal {
                    background: linear-gradient(45deg, #6a11cb, #2575fc);
                }
                
                .btn-grd-primary {
                    background: linear-gradient(45deg, #3461ff, #8454eb);
                    color: #fff;
                    border: none;
                }
                
                .btn-grd-info {
                    background: linear-gradient(45deg, #14abef, #7659ff);
                    color: #fff;
                    border: none;
                }
                
                .btn-grd-warning {
                    background: linear-gradient(45deg, #ffcb0b, #ff6b01);
                    color: #fff;
                    border: none;
                }
                
                .btn-grd-success {
                    background: linear-gradient(45deg, #18bb6b, #009688);
                    color: #fff;
                    border: none;
                }
            </style>
            '''
        
        return f'''
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>{config['app_name']} - Auth</title>
            <link rel="icon" href="{config['favicon_url']}" type="image/png" />
            {css_links}
            {external_css}
            {custom_css}
            <script src="{config['js_files'][0]}"></script>
        </head>
        '''
    
    def render_scripts(self, config: Dict[str, Any]) -> str:
        """Script bölümünü render eder"""
        js_scripts = '\n'.join([f'<script src="{js}"></script>' for js in config['js_files'][1:]])
        
        return f'''
        {js_scripts}
        <script>
            $(document).ready(function () {{
                // Password show/hide functionality for all password fields
                $("[id^=show_hide_]").each(function() {{
                    $(this).find("a").on('click', function (event) {{
                        event.preventDefault();
                        var input = $(this).siblings('input');
                        var icon = $(this).find('i');
                        
                        if (input.attr("type") == "text") {{
                            input.attr('type', 'password');
                            icon.addClass("bi-eye-slash-fill");
                            icon.removeClass("bi-eye-fill");
                        }} else if (input.attr("type") == "password") {{
                            input.attr('type', 'text');
                            icon.removeClass("bi-eye-slash-fill");
                            icon.addClass("bi-eye-fill");
                        }}
                    }});
                }});
                
                // Form validation
                $("form").on('submit', function(e) {{
                    var isValid = true;
                    var form = $(this);
                    
                    // Check required fields
                    form.find('[required]').each(function() {{
                        if (!$(this).val()) {{
                            isValid = false;
                            $(this).addClass('is-invalid');
                        }} else {{
                            $(this).removeClass('is-invalid');
                        }}
                    }});
                    
                    // Check email validation
                    form.find('input[type="email"]').each(function() {{
                        var email = $(this).val();
                        var emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{{2,}}$/;
                        if (email && !emailRegex.test(email)) {{
                            isValid = false;
                            $(this).addClass('is-invalid');
                        }}
                    }});
                    
                    // Check password confirmation
                    var newPassword = form.find('#password');
                    var confirmPassword = form.find('#password_confirmation');
                    if (newPassword.length && confirmPassword.length) {{
                        if (newPassword.val() !== confirmPassword.val()) {{
                            isValid = false;
                            confirmPassword.addClass('is-invalid');
                        }} else {{
                            confirmPassword.removeClass('is-invalid');
                        }}
                    }}
                    
                    if (!isValid) {{
                        e.preventDefault();
                        alert('Lütfen tüm gerekli alanları doğru şekilde doldurunuz.');
                    }}
                }});
                
                // Remove validation classes on input
                $('input, select').on('input change', function() {{
                    $(this).removeClass('is-invalid');
                }});
            }});
        </script>
        '''
    
    def render_auth_page(self, auth_type: AuthType, custom_config: Optional[Dict[str, Any]] = None) -> str:
        """Auth sayfasını render et"""
        # Sayfa konfigürasyonunu hazırla
        config = self.get_page_config(auth_type, custom_config)
        
        # Form alanlarını render et
        form_fields_html = self.render_dynamic_form(auth_type)
        
        # Sosyal medya butonlarını render et
        social_buttons_html = ""
        if config.get('show_social', False):
            social_providers = self.get_enabled_social_providers()
            if social_providers:
                social_buttons_html = self._render_social_buttons(social_providers, auth_type)
        
        # Buton sınıfını belirle
        submit_button_class = config.get('submit_button_class', 'btn-primary')
        
        # Auth stilini belirle
        auth_style = config.get('auth_style', AuthStyle.BOXED.value)
        
        # Sayfa içeriğini oluştur
        auth_texts = self._get_auth_texts()
        key = auth_type
        page_title = auth_texts[key]['title']
        page_subtitle = auth_texts[key]['subtitle']
        submit_button_text = auth_texts[key]['button_text']
        submit_button_class = config.get('submit_button_class', 'btn-primary')
        
        # Sayfa tipine göre özel içerik
        extra_form_content = ""
        if auth_type == AuthType.LOGIN:
            extra_form_content = '''
            <div class="col-md-6">
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="flexSwitchCheckChecked" name="remember">
                    <label class="form-check-label" for="flexSwitchCheckChecked">Beni Hatırla</label>
                </div>
            </div>
            <div class="col-md-6 text-end">
                <a href="/auth/forgot-password">Şifremi Unuttum?</a>
            </div>
            '''
        elif auth_type == AuthType.REGISTER:
            extra_form_content = '''
            <div class="col-12">
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="flexSwitchCheckChecked" name="terms" required>
                    <label class="form-check-label" for="flexSwitchCheckChecked">Kullanım koşullarını okudum ve kabul ediyorum</label>
                </div>
            </div>
            '''
        
        # Sayfa tipine göre alt bağlantılar
        bottom_links = ""
        if auth_type == AuthType.LOGIN:
            bottom_links = '''
            <div class="col-12">
                <div class="text-start">
                    <p class="mb-0">Henüz hesabınız yok mu? <a href="/auth/register">Kayıt olun</a></p>
                </div>
            </div>
            '''
        elif auth_type == AuthType.REGISTER:
            bottom_links = '''
            <div class="col-12">
                <div class="text-start">
                    <p class="mb-0">Zaten hesabınız var mı? <a href="/auth/login">Giriş yapın</a></p>
                </div>
            </div>
            '''
        elif auth_type == AuthType.FORGOT_PASSWORD:
            bottom_links = '''
            <div class="col-12 mt-3">
                <div class="d-grid">
                    <a href="/auth/login" class="btn btn-grd-primary">Giriş Sayfasına Dön</a>
                </div>
            </div>
            '''
        
        # Form action ve method değerlerini belirle
        form_action = config.get('form_action', f'/auth/{auth_type.value}')
        method = config.get('form_method', 'post')
        token_input = config.get('token_input', '')
        
        # Sosyal medya butonları
        social_buttons = ""
        if config.get('show_social', False):
            social_providers = self.get_enabled_social_providers()
            if social_providers:
                social_buttons_html = ""
                for provider in social_providers:
                    social_buttons_html += f'''
                    <div class="col-12 col-lg-12">
                        <button class="btn btn-filter py-2 px-4 font-text1 fw-bold d-flex align-items-center justify-content-center w-100">
                            <span class=""><img src="{provider['image']}" width="20" class="me-2" alt="">{provider['display_name']}</span>
                        </button>
                    </div>
                    '''
                
                social_buttons = f'''
                <div class="row gy-2 gx-0 my-4">
                    {social_buttons_html}
                </div>
                <div class="separator">
                    <div class="line"></div>
                    <p class="mb-0 fw-bold">VEYA</p>
                    <div class="line"></div>
                </div>
                '''
        
        # Sayfa içeriği - Boxed veya Basic stile göre
        auth_content = ""
        if auth_style == AuthStyle.BOXED.value:
            # Boxed stil için görsel ve içerik
            auth_image = "/static/assets/images/auth/login1.png"
            bg_color = "bg-grd-primary"
            wrapper_class = config.get('wrapper_class', 'mx-3 mx-lg-0')
            
            if auth_type == AuthType.REGISTER:
                auth_image = "/static/assets/images/auth/register1.png"
                bg_color = "bg-grd-info"
            elif auth_type == AuthType.FORGOT_PASSWORD:
                auth_image = "/static/assets/images/auth/forgot-password1.png"
                bg_color = "bg-grd-warning"
            elif auth_type == AuthType.RESET_PASSWORD:
                auth_image = "/static/assets/images/auth/reset-password1.png"
                bg_color = "bg-grd-success"
            
            auth_content = f'''
            <div class="container py-5">
                <div class="row g-4 d-flex justify-content-center align-items-center vh-100 {wrapper_class}">
                    <div class="col-12 col-xl-10">
                        <div class="card rounded-4 overflow-hidden mb-0">
                            <div class="row g-0">
                                <div class="col-lg-6 d-flex">
                                    <div class="card-body">
                                        <img src="{config['logo_url']}" class="mb-4" width="145" alt="">
                                        <h4 class="fw-bold">{page_title}</h4>
                                        <p class="mb-0">{page_subtitle}</p>
                                        {social_buttons}
                                        <div class="form-body mt-4">
                                            <form class="row g-3" action="{form_action}" method="{method}">
                                                {token_input}
                                                {form_fields_html}
                                                {extra_form_content}
                                                <div class="col-12">
                                                    <div class="d-grid">
                                                        <button type="submit" class="btn {submit_button_class}">{submit_button_text}</button>
                                                    </div>
                                                </div>
                                                {bottom_links}
                                            </form>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-lg-6 d-lg-flex d-none">
                                    <div class="p-3 rounded-4 w-100 d-flex align-items-center justify-content-center {bg_color}">
                                        <img src="{auth_image}" class="img-fluid" alt="">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            '''
        else:
            # Basic stil
            auth_content = f'''
            <div class="container py-5">
                <div class="row g-4 d-flex justify-content-center align-items-center vh-100">
                    <div class="col-12 col-lg-4">
                        <div class="card rounded-4 mb-0 border-top border-4 border-primary border-gradient-1">
                            <div class="card-body p-5">
                                <img src="{config['logo_url']}" class="mb-4" width="145" alt="">
                                <h4 class="fw-bold">{page_title}</h4>
                                <p class="mb-0">{page_subtitle}</p>
                                {social_buttons}
                                <div class="form-body mt-4">
                                    <form class="row g-4" action="{form_action}" method="{method}">
                                        {token_input}
                                        {form_fields_html}
                                        {extra_form_content}
                                        <div class="col-12">
                                            <div class="d-grid">
                                                <button type="submit" class="btn {submit_button_class}">{submit_button_text}</button>
                                            </div>
                                        </div>
                                        {bottom_links}
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            '''
        
        # Tam sayfa HTML
        head = self.render_head(config)
        scripts = self.render_scripts(config)
        html = f'''
        <!doctype html>
        <html lang="{config['language']}" data-bs-theme="{config['theme']}">
        {head}
        <body>
            {auth_content}
            {scripts}
        </body>
        </html>
        '''
        return html
    
    def render_login_page(self, custom_config: Optional[Dict[str, Any]] = None) -> str:
        """Login sayfasını render eder"""
        return self.render_auth_page(AuthType.LOGIN, custom_config)
    
    def render_register_page(self, custom_config: Optional[Dict[str, Any]] = None) -> str:
        """Register sayfasını render eder"""
        return self.render_auth_page(AuthType.REGISTER, custom_config)
    
    def render_forgot_password_page(self, custom_config: Optional[Dict[str, Any]] = None) -> str:
        """Forgot password sayfasını render eder"""
        return self.render_auth_page(AuthType.FORGOT_PASSWORD, custom_config)
    
    def render_reset_password_page(self, custom_config: Optional[Dict[str, Any]] = None) -> str:
        """Reset password sayfasını render eder"""
        return self.render_auth_page(AuthType.RESET_PASSWORD, custom_config) 
    
    def update_form_fields(self, auth_type: AuthType, fields: List[FormField]):
        """Form alanlarını güncelle"""
        self.form_configs[auth_type] = fields
        self._save_form_configs_to_file()
    
    def update_design_settings(self, settings: Dict[str, Any]):
        """Tasarım ayarlarını güncelle"""
        for key, value in settings.items():
            if key in self.config:
                self.config[key] = value
        self._save_config_to_file()
    
    def _save_form_configs_to_file(self):
        """Form konfigürasyonlarını dosyaya kaydet"""
        config_file = os.path.join('storage', 'config', 'auth_form_fields.json')
        config_dir = os.path.dirname(config_file)
        
        # Dizin yoksa oluştur
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Kaydetmek için veriyi hazırla
        save_data = {}
        for auth_type, fields in self.form_configs.items():
            save_data[auth_type.value] = []
            for field in fields:
                field_data = {
                    'name': field.name,
                    'label': field.label,
                    'field_type': field.field_type,
                    'placeholder': field.placeholder,
                    'required': field.required,
                    'validation': field.validation
                }
                save_data[auth_type.value].append(field_data)
        
        # Dosyaya kaydet
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)
    
    def _load_form_configs_from_file(self):
        """Form konfigürasyonlarını dosyadan yükle"""
        config_file = os.path.join('storage', 'config', 'auth_form_fields.json')
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    
                    # Her auth tipi için form alanlarını yükle
                    for auth_type_str, fields_data in saved_data.items():
                        auth_type = AuthType(auth_type_str)
                        fields = []
                        
                        for field_data in fields_data:
                            field = FormField(
                                name=field_data['name'],
                                label=field_data['label'],
                                field_type=field_data['field_type'],
                                placeholder=field_data['placeholder'],
                                required=field_data['required'],
                                validation=field_data['validation']
                            )
                            fields.append(field)
                        
                        self.form_configs[auth_type] = fields
        except Exception:
            # Dosya yoksa veya okuma hatası olursa varsayılan ayarları kullan
            pass
    
    def _save_config_to_file(self):
        """Konfigürasyonu dosyaya kaydet"""
        config_file = os.path.join('storage', 'config', 'auth_settings.json')
        config_dir = os.path.dirname(config_file)
        
        # Dizin yoksa oluştur
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Kaydetmek için veriyi hazırla
        save_config = {
            'show_social': self.config['show_social'],
            'social_providers': [],
            'auth_style': self.config['auth_style'],
            'theme': self.config['theme'],
            'logo_url': self.config['logo_url']
        }
        
        for provider in self.config['social_providers']:
            save_config['social_providers'].append({
                'name': provider['name'],
                'enabled': provider['enabled']
            })
        
        # Dosyaya kaydet
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(save_config, f, ensure_ascii=False, indent=4) 