"""
Email Components
E-posta şablonları ve bileşenleri
"""
import os
import re
import jinja2
from typing import Dict, Any, List, Optional

class EmailComponentManager:
    """E-posta bileşenleri ve şablonları yönetici sınıfı"""
    
    def __init__(self, template_dir: str = None):
        """
        E-posta bileşenleri yöneticisini başlat
        
        Args:
            template_dir: E-posta şablonlarının bulunduğu dizin
        """
        # Şablon dizinini belirle
        if template_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            self.template_dir = os.path.join(base_dir, 'public', 'Views', 'emails')
        else:
            self.template_dir = template_dir
        
        # Şablon dizini yoksa oluştur
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Jinja2 environment oluştur
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Jinja2 filtrelerini ekle
        self._add_filters()
        
        # Varsayılan şablonları oluştur
        self._create_default_templates()
    
    def render(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Şablonu render et
        
        Args:
            template_name: Şablon adı
            data: Şablon değişkenleri
            
        Returns:
            str: Render edilmiş HTML
        """
        try:
            # Şablonu yükle
            template = self.env.get_template(f"{template_name}.html")
            
            # Şablonu render et
            rendered = template.render(**data)
            return rendered
            
        except jinja2.exceptions.TemplateNotFound:
            # Şablon bulunamadıysa varsayılan şablonu oluştur ve tekrar dene
            self._create_default_template(template_name)
            
            try:
                template = self.env.get_template(f"{template_name}.html")
                return template.render(**data)
            except:
                # Hala başarısız olursa, fallback şablonu kullan
                app_name = data.get('app_name', 'Uygulama')
                user_name = data.get('user', {}).get('name', 'Kullanıcı')
                
                return f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{app_name}</title>
                </head>
                <body>
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
                        <h2>{app_name}</h2>
                        <p>Merhaba {user_name},</p>
                        <p>Bu bir otomatik e-postadır.</p>
                        <p>İyi günler dileriz,<br>{app_name} Ekibi</p>
                    </div>
                </body>
                </html>
                """
    
    def _add_filters(self):
        """Jinja2 filtrelerini ekle"""
        # Tarih formatı filtresi
        def format_date(date, format='%d.%m.%Y'):
            if hasattr(date, 'strftime'):
                return date.strftime(format)
            return date
        
        self.env.filters['format_date'] = format_date
        
        # Para birimi formatı filtresi
        def format_currency(value, currency='₺'):
            try:
                return f"{float(value):,.2f} {currency}"
            except (ValueError, TypeError):
                return value
        
        self.env.filters['format_currency'] = format_currency
    
    def get_available_templates(self) -> List[str]:
        """
        Mevcut şablonları listele
        
        Returns:
            List[str]: Şablon adları listesi
        """
        try:
            templates = []
            
            # Dizin yoksa oluştur
            if not os.path.exists(self.template_dir):
                os.makedirs(self.template_dir)
                
            for filename in os.listdir(self.template_dir):
                if filename.endswith('.html'):
                    templates.append(filename[:-5])  # .html uzantısını kaldır
            return templates
        except Exception:
            return []
    
    def _create_default_templates(self):
        """
        Varsayılan şablonları oluştur
        
        Şablonlar:
            - base: Temel e-posta şablonu
            - welcome: Hoş geldiniz e-postası
            - password_reset: Şifre sıfırlama e-postası
            - notification: Bildirim e-postası
            - contact: İletişim formu e-postası
            - order_confirmation: Sipariş onay e-postası
        """
        templates = {
            'base': self._get_base_template(),
            'welcome': self._get_welcome_template(),
            'password_reset': self._get_password_reset_template(),
            'notification': self._get_notification_template(),
            'contact': self._get_contact_template(),
            'order_confirmation': self._get_order_confirmation_template()
        }
        
        for name, content in templates.items():
            self._create_template_file(name, content)
    
    def _create_default_template(self, template_name: str):
        """
        Belirli bir varsayılan şablonu oluştur
        
        Args:
            template_name: Şablon adı
        """
        # Şablon içeriğini belirle
        content = None
        
        if template_name == 'base':
            content = self._get_base_template()
        elif template_name == 'welcome':
            content = self._get_welcome_template()
        elif template_name == 'password_reset':
            content = self._get_password_reset_template()
        elif template_name == 'notification':
            content = self._get_notification_template()
        elif template_name == 'contact':
            content = self._get_contact_template()
        elif template_name == 'order_confirmation':
            content = self._get_order_confirmation_template()
            
        # Şablonu oluştur
        if content:
            self._create_template_file(template_name, content)
    
    def _create_template_file(self, name: str, content: str):
        """
        Şablon dosyası oluştur
        
        Args:
            name: Şablon adı
            content: Şablon içeriği
        """
        template_path = os.path.join(self.template_dir, f"{name}.html")
        
        # Şablon yoksa veya içeriği değiştiyse oluştur
        if not os.path.exists(template_path):
            try:
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                print(f"Template file creation error: {e}")
    
    def _get_base_template(self) -> str:
        """
        Temel e-posta şablonu
        
        Returns:
            str: Şablon HTML içeriği
        """
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid #eee;
        }
        .logo {
            max-width: 150px;
            height: auto;
        }
        .content {
            padding: 20px 0;
        }
        .footer {
            text-align: center;
            padding: 20px 0;
            color: #777;
            font-size: 14px;
            border-top: 1px solid #eee;
        }
        .button {
            display: inline-block;
            background-color: #3461ff;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 4px;
            margin: 20px 0;
            font-weight: bold;
        }
        .button:hover {
            background-color: #2a4fd6;
        }
        @media only screen and (max-width: 620px) {
            .container {
                width: 100%;
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{{ app_url }}/static/assets/images/logo-icon.png" alt="{{ app_name }} Logo" class="logo">
        </div>
        <div class="content">
            {% block content %}{% endblock %}
        </div>
        <div class="footer">
            <p>&copy; {{ current_year }} {{ app_name }}. Tüm hakları saklıdır.</p>
            {% if recipient_email %}
            <p>Bu e-posta {{ recipient_email }} adresine gönderilmiştir.</p>
            {% endif %}
            {% block footer_extra %}{% endblock %}
        </div>
    </div>
</body>
</html>"""
    
    def _get_welcome_template(self) -> str:
        """
        Hoş geldiniz e-posta şablonu
        
        Returns:
            str: Şablon HTML içeriği
        """
        return """{% extends "base.html" %}

{% block content %}
<h2>Merhaba {{ user.name }},</h2>
<p>{{ app_name }}'ye hoş geldiniz! Hesabınız başarıyla oluşturuldu.</p>

<p>{{ app_name }} ile yapabilecekleriniz:</p>
<ul>
    <li>İçerik oluşturma ve yönetme</li>
    <li>Yapay zeka araçlarını kullanma</li>
    <li>Analizleri takip etme</li>
    <li>Ve çok daha fazlası...</li>
</ul>

<p>Hemen giriş yaparak platformumuzu keşfetmeye başlayabilirsiniz:</p>
<a href="{{ login_url }}" class="button">Giriş Yap</a>

<p>Herhangi bir sorunuz olursa, <a href="mailto:{{ support_email }}">{{ support_email }}</a> adresinden bize ulaşabilirsiniz.</p>

<p>Teşekkürler,<br>{{ app_name }} Ekibi</p>
{% endblock %}

{% block footer_extra %}
<p>Bu e-postayı almak istemiyorsanız, <a href="{{ app_url }}/unsubscribe?email={{ user.email }}">abonelikten çıkabilirsiniz</a>.</p>
{% endblock %}"""
    
    def _get_password_reset_template(self) -> str:
        """
        Şifre sıfırlama e-posta şablonu
        
        Returns:
            str: Şablon HTML içeriği
        """
        return """{% extends "base.html" %}

{% block content %}
<h2>Merhaba {{ user.name }},</h2>

<p>{{ app_name }} hesabınız için şifre sıfırlama talebinde bulundunuz.</p>

<p>Şifrenizi sıfırlamak için aşağıdaki butona tıklayın:</p>
<a href="{{ reset_url }}" class="button">Şifremi Sıfırla</a>

<p>Bu bağlantı {{ expires_in }} içinde sona erecektir.</p>

<p>Eğer şifre sıfırlama talebinde bulunmadıysanız, bu e-postayı görmezden gelebilirsiniz.</p>

<p>Güvenlik nedeniyle, bu e-postayı kimseyle paylaşmayın.</p>

<p>Yardıma ihtiyacınız olursa, <a href="mailto:{{ support_email }}">{{ support_email }}</a> adresinden bize ulaşabilirsiniz.</p>

<p>Teşekkürler,<br>{{ app_name }} Ekibi</p>
{% endblock %}"""
    
    def _get_notification_template(self) -> str:
        """
        Bildirim e-posta şablonu
        
        Returns:
            str: Şablon HTML içeriği
        """
        return """{% extends "base.html" %}

{% block content %}
<h2>Merhaba {{ user.name }},</h2>

<p>{{ notification.message }}</p>

{% if notification.action_url %}
<a href="{{ notification.action_url }}" class="button">{{ notification.action_text|default('Detayları Görüntüle') }}</a>
{% endif %}

<p>{{ app_name }}'yi kullandığınız için teşekkür ederiz.</p>

<p>Saygılarımızla,<br>{{ app_name }} Ekibi</p>
{% endblock %}

{% block footer_extra %}
<p>Bildirim e-postalarını almak istemiyorsanız, <a href="{{ app_url }}/settings/notifications">bildirim ayarlarınızı</a> güncelleyebilirsiniz.</p>
{% endblock %}"""
    
    def _get_contact_template(self) -> str:
        """
        İletişim formu e-posta şablonu
        
        Returns:
            str: Şablon HTML içeriği
        """
        return """{% extends "base.html" %}

{% block content %}
<h2>İletişim Formu Mesajı</h2>

<div style="margin-top: 20px;">
    <p><strong>İsim:</strong> {{ name }}</p>
    <p><strong>E-posta:</strong> {{ email }}</p>
    <p><strong>Konu:</strong> {{ subject }}</p>
    <p><strong>Mesaj:</strong></p>
    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 4px; margin: 10px 0;">
        {{ message }}
    </div>
    <p><strong>Tarih:</strong> {{ timestamp }}</p>
</div>

{% if app_url %}
<p>
    <a href="{{ app_url }}/admin/contacts" class="button">Tüm İletişim Mesajlarını Görüntüle</a>
</p>
{% endif %}
{% endblock %}"""
    
    def _get_order_confirmation_template(self) -> str:
        """
        Sipariş onay e-posta şablonu
        
        Returns:
            str: Şablon HTML içeriği
        """
        return """{% extends "base.html" %}

{% block content %}
<h2>Siparişiniz Onaylandı</h2>

<p>Merhaba {{ user.name }},</p>

<p>Siparişiniz başarıyla oluşturuldu. Sipariş detayları aşağıdadır:</p>

<div style="background-color: #f9f9f9; padding: 15px; border-radius: 4px; margin: 20px 0;">
    <p><strong>Sipariş Numarası:</strong> {{ order.id }}</p>
    <p><strong>Tarih:</strong> {{ order.created_at|format_date }}</p>
    <p><strong>Toplam Tutar:</strong> {{ order.total|format_currency }}</p>
</div>

<h3>Sipariş Ürünleri</h3>

<table style="width: 100%; border-collapse: collapse;">
    <thead>
        <tr>
            <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Ürün</th>
            <th style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;">Adet</th>
            <th style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;">Fiyat</th>
            <th style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;">Toplam</th>
        </tr>
    </thead>
    <tbody>
        {% for item in order.items %}
        <tr>
            <td style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">{{ item.product_name }}</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;">{{ item.quantity }}</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;">{{ item.price|format_currency }}</td>
            <td style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;">{{ item.total|format_currency }}</td>
        </tr>
        {% endfor %}
        <tr>
            <td colspan="3" style="text-align: right; padding: 8px; font-weight: bold;">Ara Toplam:</td>
            <td style="text-align: right; padding: 8px;">{{ order.subtotal|format_currency }}</td>
        </tr>
        {% if order.shipping_cost %}
        <tr>
            <td colspan="3" style="text-align: right; padding: 8px;">Kargo:</td>
            <td style="text-align: right; padding: 8px;">{{ order.shipping_cost|format_currency }}</td>
        </tr>
        {% endif %}
        {% if order.tax %}
        <tr>
            <td colspan="3" style="text-align: right; padding: 8px;">KDV:</td>
            <td style="text-align: right; padding: 8px;">{{ order.tax|format_currency }}</td>
        </tr>
        {% endif %}
        <tr>
            <td colspan="3" style="text-align: right; padding: 8px; font-weight: bold;">Genel Toplam:</td>
            <td style="text-align: right; padding: 8px; font-weight: bold;">{{ order.total|format_currency }}</td>
        </tr>
    </tbody>
</table>

<p>Siparişinizi <a href="{{ app_url }}/account/orders/{{ order.id }}">hesabınızdan</a> takip edebilirsiniz.</p>

<p>Satın aldığınız için teşekkür ederiz!</p>

<p>Saygılarımızla,<br>{{ app_name }} Ekibi</p>
{% endblock %}"""


# EmailComponentManager singleton instance'ı
_email_component_manager = None

def get_email_component_manager(template_dir: str = None) -> EmailComponentManager:
    """
    EmailComponentManager singleton instance'ını al
    
    Args:
        template_dir: E-posta şablonlarının bulunduğu dizin
        
    Returns:
        EmailComponentManager: Email component manager instance
    """
    global _email_component_manager
    if _email_component_manager is None:
        _email_component_manager = EmailComponentManager(template_dir)
    return _email_component_manager 