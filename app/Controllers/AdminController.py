"""
Admin Controller
Admin işlemleri controller'ı
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.Controllers.BaseController import BaseController
from app.Middleware.AuthMiddleware import auth_required, admin_required
from core.Services.error_handler import error_handler
from core.Services.UIService import UIService
from core.Services.ComponentService import ComponentService
from core.Services.auth_page_service import AuthPageService
from app.Models.User import User
from core.Database.connection import get_connection
import json
import datetime
from flask import jsonify, request, session
from typing import Dict, Any

class AdminController(BaseController):
    """Admin controller'ı"""
    
    def __init__(self):
        super().__init__()
        self.auth_service = AuthPageService()
    
    def _safe_get_input(self):
        """Form veya JSON verilerini güvenli bir şekilde al"""
        try:
            if self.request.method == 'POST':
                # Önce form verisini kontrol et
                if self.request.form:
                    return dict(self.request.form)
                    
                # Form yoksa JSON kontrolü yap (güvenli şekilde)
                content_type = self.request.headers.get('Content-Type', '').lower()
                if 'application/json' in content_type:
                    try:
                        json_data = self.request.get_json(silent=True, force=True)
                        if json_data:
                            return json_data
                    except Exception as e:
                        print(f"JSON işleme hatası: {str(e)}")
                        return {}
                else:
                    # JSON olmayan içerik tipleri için boş sözlük döndür
                    print(f"Desteklenmeyen içerik tipi: {content_type}")
                    return {}
            
            # GET parametrelerini kontrol et
            if self.request.args:
                return dict(self.request.args)
                
            # Hiçbir veri bulunamadıysa boş sözlük döndür
            return {}
        except Exception as e:
            print(f"Input işleme hatası: {str(e)}")
            return {}
    
    @admin_required
    def index(self):
        """Admin ana sayfası"""
        try:
            # Dashboard verilerini hazırla
            data = {
                'title': 'Admin Panel - Dashboard',
                'stats': self._get_admin_stats(),
                'recent_activities': self._get_admin_activities(),
                'system_status': self._get_system_status(),
                'quick_actions': self._get_quick_actions()
            }
            
            return self.view('admin.index', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def users(self):
        """Kullanıcı yönetimi sayfası"""
        try:
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            search = request.args.get('search', '')
            status = request.args.get('status', 'all')
            
            # Kullanıcıları getir
            users_data = self._get_users_with_pagination(page, per_page, search, status)
            
            data = {
                'title': 'Kullanıcı Yönetimi',
                'users': users_data['users'],
                'pagination': users_data['pagination'],
                'search': search,
                'status': status,
                'user_stats': self._get_user_stats()
            }
            
            return self.view('admin.users', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def settings(self):
        """Ayarlar sayfası"""
        try:
            if request.method == 'POST':
                return self._handle_settings_update()
            
            # Mevcut ayarları getir
            settings = self._get_current_settings()
            
            data = {
                'title': 'Sistem Ayarları',
                'settings': settings,
                'categories': self._get_settings_categories()
            }
            
            return self.view('admin.settings', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def _get_admin_stats(self):
        """Admin dashboard istatistikleri"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Toplam kullanıcı sayısı
            cursor.execute("SELECT COUNT(*) FROM users")
            result = cursor.fetchone()
            stats['total_users'] = result[0] if result else 0
            
            # Bugün kayıt olan kullanıcılar
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE DATE(created_at) = DATE('now')
            """)
            result = cursor.fetchone()
            stats['new_users_today'] = result[0] if result else 0
            
            # Aktif kullanıcılar (son 7 gün)
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE last_login >= datetime('now', '-7 days')
            """)
            result = cursor.fetchone()
            stats['active_users_week'] = result[0] if result else 0
            
            # Bekleyen onaylar
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE status = 'pending'
            """)
            result = cursor.fetchone()
            stats['pending_approvals'] = result[0] if result else 0
            
            conn.close()
            
            # Ek istatistikler
            stats.update({
                'total_content': 156,
                'published_content': 142,
                'draft_content': 14,
                'total_comments': 1247,
                'pending_comments': 23
            })
            
            return stats
            
        except Exception as e:
            print(f"Admin stats error: {str(e)}")
            return {}
    
    def _get_admin_activities(self):
        """Admin aktiviteleri"""
        try:
            activities = [
                {
                    'type': 'user_action',
                    'title': 'Yeni kullanıcı onaylandı',
                    'description': 'mehmet.yilmaz@example.com kullanıcısı onaylandı',
                    'user': 'Admin',
                    'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'icon': 'person_add',
                    'color': 'success'
                },
                {
                    'type': 'content_action',
                    'title': 'İçerik yayınlandı',
                    'description': 'Flask ile Modern Web Geliştirme makalesi yayınlandı',
                    'user': 'Editor',
                    'time': (datetime.datetime.now() - datetime.timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'),
                    'icon': 'publish',
                    'color': 'primary'
                },
                {
                    'type': 'system_action',
                    'title': 'Sistem güncellemesi',
                    'description': 'Güvenlik yamaları uygulandı',
                    'user': 'System',
                    'time': (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
                    'icon': 'security',
                    'color': 'warning'
                },
                {
                    'type': 'security_action',
                    'title': 'Şüpheli giriş denemesi',
                    'description': 'IP: 192.168.1.100 adresinden başarısız giriş',
                    'user': 'Security System',
                    'time': (datetime.datetime.now() - datetime.timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'),
                    'icon': 'warning',
                    'color': 'danger'
                }
            ]
            
            return activities
            
        except Exception as e:
            print(f"Admin activities error: {str(e)}")
            return []
    
    def _get_system_status(self):
        """Sistem durumu"""
        try:
            import psutil
            
            status = {
                'server_status': 'online',
                'database_status': 'connected',
                'cache_status': 'active',
                'mail_status': 'configured',
                'backup_status': 'completed',
                'last_backup': '2024-01-15 03:00:00',
                'disk_usage': round(psutil.disk_usage('/').percent, 1),
                'memory_usage': round(psutil.virtual_memory().percent, 1),
                'cpu_usage': round(psutil.cpu_percent(interval=1), 1)
            }
            
            return status
            
        except Exception as e:
            print(f"System status error: {str(e)}")
            return {
                'server_status': 'unknown',
                'database_status': 'unknown',
                'cache_status': 'unknown',
                'mail_status': 'unknown',
                'backup_status': 'unknown',
                'last_backup': 'Unknown',
                'disk_usage': 0,
                'memory_usage': 0,
                'cpu_usage': 0
            }
    
    def _get_quick_actions(self):
        """Hızlı işlemler"""
        return [
            {
                'title': 'Yeni Kullanıcı Ekle',
                'description': 'Sisteme yeni kullanıcı ekle',
                'icon': 'person_add',
                'url': '/admin/users/create',
                'color': 'primary'
            },
            {
                'title': 'İçerik Yönetimi',
                'description': 'İçerikleri yönet ve düzenle',
                'icon': 'article',
                'url': '/admin/content',
                'color': 'success'
            },
            {
                'title': 'Sistem Ayarları',
                'description': 'Sistem ayarlarını güncelle',
                'icon': 'settings',
                'url': '/admin/settings',
                'color': 'warning'
            },
            {
                'title': 'Güvenlik Raporları',
                'description': 'Güvenlik loglarını incele',
                'icon': 'security',
                'url': '/admin/security',
                'color': 'danger'
            }
        ]
    
    def _get_users_with_pagination(self, page, per_page, search, status):
        """Sayfalama ile kullanıcıları getir"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Base query
            where_conditions = []
            params = []
            
            if search:
                where_conditions.append("(name LIKE ? OR email LIKE ?)")
                params.extend([f"%{search}%", f"%{search}%"])
            
            if status != 'all':
                where_conditions.append("status = ?")
                params.append(status)
            
            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Toplam kayıt sayısı
            count_query = f"SELECT COUNT(*) FROM users{where_clause}"
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()[0]
            
            # Sayfalama hesaplamaları
            total_pages = (total_records + per_page - 1) // per_page
            offset = (page - 1) * per_page
            
            # Kullanıcıları getir
            users_query = f"""
                SELECT id, name, email, status, role, created_at, last_login
                FROM users{where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(users_query, params + [per_page, offset])
            users = [
                {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'status': row[3],
                    'role': row[4],
                    'created_at': row[5],
                    'last_login': row[6]
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            return {
                'users': users,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_records': total_records,
                    'per_page': per_page,
                    'has_prev': page > 1,
                    'has_next': page < total_pages,
                    'prev_page': page - 1 if page > 1 else None,
                    'next_page': page + 1 if page < total_pages else None
                }
            }
            
        except Exception as e:
            print(f"Users pagination error: {str(e)}")
            return {
                'users': [],
                'pagination': {
                    'current_page': 1,
                    'total_pages': 1,
                    'total_records': 0,
                    'per_page': per_page,
                    'has_prev': False,
                    'has_next': False,
                    'prev_page': None,
                    'next_page': None
                }
            }
    
    def _get_user_stats(self):
        """Kullanıcı istatistikleri"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Duruma göre kullanıcı sayıları
            cursor.execute("SELECT status, COUNT(*) FROM users GROUP BY status")
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            stats.update({
                'active': status_counts.get('active', 0),
                'inactive': status_counts.get('inactive', 0),
                'pending': status_counts.get('pending', 0),
                'banned': status_counts.get('banned', 0)
            })
            
            # Role göre kullanıcı sayıları
            cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
            role_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            stats.update({
                'admin': role_counts.get('admin', 0),
                'editor': role_counts.get('editor', 0),
                'user': role_counts.get('user', 0)
            })
            
            conn.close()
            return stats
            
        except Exception as e:
            print(f"User stats error: {str(e)}")
            return {}
    
    def _get_current_settings(self):
        """Mevcut sistem ayarları"""
        return {
            'site_name': 'PofuAi',
            'site_description': 'Modern AI-powered web platform',
            'admin_email': 'admin@pofuai.com',
            'maintenance_mode': False,
            'user_registration': True,
            'email_verification': True,
            'max_file_size': 10,  # MB
            'allowed_file_types': 'jpg,jpeg,png,gif,pdf,doc,docx',
            'timezone': 'Europe/Istanbul',
            'language': 'tr',
            'theme': 'blue-theme'
        }
    
    def _get_settings_categories(self):
        """Ayar kategorileri"""
        return [
            {
                'name': 'general',
                'title': 'Genel Ayarlar',
                'icon': 'settings',
                'settings': ['site_name', 'site_description', 'admin_email', 'timezone', 'language']
            },
            {
                'name': 'security',
                'title': 'Güvenlik',
                'icon': 'security',
                'settings': ['user_registration', 'email_verification', 'maintenance_mode']
            },
            {
                'name': 'files',
                'title': 'Dosya Yönetimi',
                'icon': 'folder',
                'settings': ['max_file_size', 'allowed_file_types']
            },
            {
                'name': 'appearance',
                'title': 'Görünüm',
                'icon': 'palette',
                'settings': ['theme']
            }
        ]
    
    def _handle_settings_update(self):
        """Ayarları güncelle"""
        try:
            data = self._safe_get_input()
            
            # Ayarları doğrula ve kaydet
            # Bu kısım gerçek bir uygulamada veritabanına kaydedilir
            
            return jsonify({
                'success': True,
                'message': 'Ayarlar başarıyla güncellendi'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Ayarlar güncellenirken hata oluştu: {str(e)}'
            })
    
    @admin_required
    def components(self):
        """Component showcase sayfası"""
        try:
            data = {
                'title': 'UI Components',
                'components': self._get_available_components()
            }
            
            return self.view('admin.components', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)

    @admin_required
    def auth_forms(self):
        """Auth form ayarları sayfası"""
        try:
            # Auth servisinden ayarları al
            settings = {
                'show_social': self.auth_service.config['show_social'],
                'social_providers': self.auth_service.config['social_providers'],
                'login_fields': self.auth_service.get_form_fields(AuthPageService.AuthType.LOGIN),
                'register_fields': self.auth_service.get_form_fields(AuthPageService.AuthType.REGISTER),
                'forgot_password_fields': self.auth_service.get_form_fields(AuthPageService.AuthType.FORGOT_PASSWORD),
                'reset_password_fields': self.auth_service.get_form_fields(AuthPageService.AuthType.RESET_PASSWORD)
            }
            
            # Sayfayı render et
            return self._render_auth_forms_page(settings)
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    def _render_auth_forms_page(self, settings):
        """Auth form ayarları sayfasını render et"""
        # Component servisi ve UI servisi kullan
        component_service = ComponentService()
        ui_service = UIService()
        
        # Base layout için CSS ve JS dosyalarını ekle
        base_layout = ui_service.get_base_layout()
        base_layout.add_css('/static/assets/css/bootstrap.min.css')
        base_layout.add_css('/static/assets/css/bootstrap-extended.css')
        base_layout.add_css('/static/assets/css/pace.min.css')
        base_layout.add_css('/static/assets/css/extra-icons.css')
        
        # jQuery eklentisini ekle (önce yüklenmelidir)
        base_layout.add_js('https://code.jquery.com/jquery-3.6.0.min.js')
        
        # Bootstrap ve diğer JS dosyaları
        base_layout.add_js('/static/assets/js/bootstrap.bundle.min.js')
        
        # Perfect Scrollbar eklentisini ekle
        base_layout.add_css('/static/assets/plugins/perfect-scrollbar/css/perfect-scrollbar.css')
        base_layout.add_js('/static/assets/plugins/perfect-scrollbar/js/perfect-scrollbar.js')
        
        # Metismenu eklentisini ekle
        base_layout.add_css('/static/assets/plugins/metismenu/metisMenu.min.css')
        base_layout.add_js('/static/assets/plugins/metismenu/metisMenu.min.js')
        
        # Navbar HTML'i
        navbar_html = component_service.get_navbar_component().render(
            navbar_type="fixed",
            navbar_style="light",
            brand_name="PofuAi Admin",
            user_name="Admin",
            user_email="admin@example.com",
            show_mega_menu=False
        )
        
        # Sidebar HTML'i (admin menüsü aktif)
        sidebar_html = component_service.get_sidebar_component().render({'active_menu': 'admin_auth_forms'})
        
        # Form alanlarını HTML'e dönüştür
        login_fields_html = self._generate_fields_html(settings['login_fields'], 'login')
        register_fields_html = self._generate_fields_html(settings['register_fields'], 'register')
        forgot_password_fields_html = self._generate_fields_html(settings['forgot_password_fields'], 'forgot_password')
        reset_password_fields_html = self._generate_fields_html(settings['reset_password_fields'], 'reset_password')
        
        # Sosyal medya sağlayıcı checkboxları
        provider_checkboxes = ""
        for provider in ['google', 'facebook', 'twitter', 'github', 'linkedin']:
            checked = "checked" if provider in settings['social_providers'] else ""
            provider_checkboxes += f'''
            <div class="col-md-4 mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="{provider}" name="providers[]" value="{provider}" {checked}>
                    <label class="form-check-label" for="{provider}">{provider.capitalize()}</label>
                </div>
            </div>
            '''
        
        # Sosyal medya ayarları kartı
        social_settings_card = component_service.get_card_component().render({
            'title': 'Sosyal Medya Ayarları',
            'content': f'''
            <form id="socialSettingsForm">
                <div class="mb-3">
                    <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" id="showSocial" name="show_social" {"checked" if settings['show_social'] else ""}>
                        <label class="form-check-label" for="showSocial">Sosyal Medya Girişini Etkinleştir</label>
                    </div>
                </div>
                
                <div class="mb-3">
                    <h6>Sosyal Medya Sağlayıcıları</h6>
                    <div class="row">
                        {provider_checkboxes}
                    </div>
                </div>
                
                <button type="submit" class="btn btn-primary">Kaydet</button>
            </form>
            '''
        })
        
        # Form alanları için tab içerikleri
        login_tab_content = f'''
        <form id="loginFormFieldsForm">
            <input type="hidden" name="form_type" value="login">
            <div class="mb-3">
                <button type="button" class="btn btn-sm btn-outline-primary" id="addLoginField">
                    <i class="material-icons-outlined">add</i> Alan Ekle
                </button>
            </div>
            <div id="loginFieldsList">
                {login_fields_html}
            </div>
            <button type="submit" class="btn btn-primary mt-3">Kaydet</button>
        </form>
        '''
        
        register_tab_content = f'''
        <form id="registerFormFieldsForm">
            <input type="hidden" name="form_type" value="register">
            <div class="mb-3">
                <button type="button" class="btn btn-sm btn-outline-primary" id="addRegisterField">
                    <i class="material-icons-outlined">add</i> Alan Ekle
                </button>
            </div>
            <div id="registerFieldsList">
                {register_fields_html}
            </div>
            <button type="submit" class="btn btn-primary mt-3">Kaydet</button>
        </form>
        '''
        
        forgot_password_tab_content = f'''
        <form id="forgotPasswordFormFieldsForm">
            <input type="hidden" name="form_type" value="forgot_password">
            <div class="mb-3">
                <button type="button" class="btn btn-sm btn-outline-primary" id="addForgotPasswordField">
                    <i class="material-icons-outlined">add</i> Alan Ekle
                </button>
            </div>
            <div id="forgotPasswordFieldsList">
                {forgot_password_fields_html}
            </div>
            <button type="submit" class="btn btn-primary mt-3">Kaydet</button>
        </form>
        '''
        
        reset_password_tab_content = f'''
        <form id="resetPasswordFormFieldsForm">
            <input type="hidden" name="form_type" value="reset_password">
            <div class="mb-3">
                <button type="button" class="btn btn-sm btn-outline-primary" id="addResetPasswordField">
                    <i class="material-icons-outlined">add</i> Alan Ekle
                </button>
            </div>
            <div id="resetPasswordFieldsList">
                {reset_password_fields_html}
            </div>
            <button type="submit" class="btn btn-primary mt-3">Kaydet</button>
        </form>
        '''
        
        # Tabs component ile form alanları tablarını oluştur
        form_fields_tabs = component_service.get_tabs_component().render({
            'tabs': [
                {
                    'id': 'login',
                    'title': 'Giriş Formu',
                    'content': login_tab_content,
                    'active': True
                },
                {
                    'id': 'register',
                    'title': 'Kayıt Formu',
                    'content': register_tab_content
                },
                {
                    'id': 'forgot-password',
                    'title': 'Şifremi Unuttum',
                    'content': forgot_password_tab_content
                },
                {
                    'id': 'reset-password',
                    'title': 'Şifre Sıfırlama',
                    'content': reset_password_tab_content
                }
            ]
        })
        
        # Form alanları kartı
        form_fields_card = component_service.get_card_component().render({
            'title': 'Form Alanları Ayarları',
            'content': form_fields_tabs
        })
        
        # Tasarım ayarları kartı
        design_settings_card = component_service.get_card_component().render({
            'title': 'Tasarım Ayarları',
            'content': '''
            <form id="designSettingsForm">
                <div class="mb-3">
                    <label for="formWidth" class="form-label">Form Genişliği</label>
                    <select class="form-select" id="formWidth" name="form_width">
                        <option value="narrow">Dar</option>
                        <option value="medium" selected>Orta</option>
                        <option value="wide">Geniş</option>
                        <option value="full">Tam Genişlik</option>
                    </select>
                </div>
                
                <div class="mb-3">
                    <label for="formStyle" class="form-label">Form Stili</label>
                    <select class="form-select" id="formStyle" name="form_style">
                        <option value="default" selected>Varsayılan</option>
                        <option value="flat">Düz</option>
                        <option value="rounded">Yuvarlak</option>
                        <option value="floating">Floating Label</option>
                    </select>
                </div>
                
                <div class="mb-3">
                    <label for="buttonStyle" class="form-label">Buton Stili</label>
                    <select class="form-select" id="buttonStyle" name="button_style">
                        <option value="default" selected>Varsayılan</option>
                        <option value="rounded">Yuvarlak</option>
                        <option value="pill">Pill</option>
                        <option value="outline">Outline</option>
                    </select>
                </div>
                
                <button type="submit" class="btn btn-primary">Kaydet</button>
            </form>
            '''
        })
        
        # Ana içerik HTML'i
        content_html = f'''
        <main class="page-content">
            <div class="page-breadcrumb d-none d-sm-flex align-items-center mb-3">
                <div class="breadcrumb-title pe-3">Admin</div>
                <div class="ps-3">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb mb-0 p-0">
                            <li class="breadcrumb-item"><a href="/admin"><i class="material-icons-outlined">home</i></a></li>
                            <li class="breadcrumb-item active" aria-current="page">Auth Form Yönetimi</li>
                        </ol>
                    </nav>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12 mb-4">
                    {social_settings_card}
                </div>
                <div class="col-12 mb-4">
                    {form_fields_card}
                </div>
                <div class="col-12 mb-4">
                    {design_settings_card}
                </div>
            </div>
        </main>
        '''
        
        # Tam sayfa HTML'i
        page_html = f'''
        <div class="wrapper">
            {sidebar_html}
            <div class="page-content-wrapper">
                {navbar_html}
                {content_html}
            </div>
        </div>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Sayfa yüklendiğinde çalışacak JavaScript
            console.log('Auth forms page loaded');
            
            // Sidebar toggle işlevi
            document.querySelector('.btn-toggle').addEventListener('click', function() {{
                document.querySelector('.wrapper').classList.toggle('toggled');
            }});
            
            // Perfect scrollbar başlatma
            if (typeof PerfectScrollbar !== 'undefined') {{
                try {{
                    new PerfectScrollbar(".sidebar-nav");
                }} catch (e) {{
                    console.log("PerfectScrollbar error:", e.message);
                }}
            }}
            
            // Metismenu başlatma
            if (typeof $ !== 'undefined' && $.fn.metisMenu) {{
                try {{
                    $("#sidenav").metisMenu();
                }} catch (e) {{
                    console.log("MetisMenu error:", e.message);
                }}
            }}
            
            // Form alanı ekleme işlevleri
            document.getElementById('addLoginField').addEventListener('click', function() {{
                addFormField('login');
            }});
            
            document.getElementById('addRegisterField').addEventListener('click', function() {{
                addFormField('register');
            }});
            
            document.getElementById('addForgotPasswordField').addEventListener('click', function() {{
                addFormField('forgot_password');
            }});
            
            document.getElementById('addResetPasswordField').addEventListener('click', function() {{
                addFormField('reset_password');
            }});
            
            // Form alanı ekleme fonksiyonu
            function addFormField(formType) {{
                // AJAX ile yeni form alanı oluştur
                fetch('/admin/auth-forms/field?form_type=' + formType)
                    .then(response => response.text())
                    .then(html => {{
                        document.getElementById(formType + 'FieldsList').insertAdjacentHTML('beforeend', html);
                    }})
                    .catch(error => console.error('Error:', error));
            }}
            
            // Form gönderme işleyicileri
            document.getElementById('socialSettingsForm').addEventListener('submit', function(e) {{
                e.preventDefault();
                saveSocialSettings(this);
            }});
            
            document.getElementById('loginFormFieldsForm').addEventListener('submit', function(e) {{
                e.preventDefault();
                saveFormFields(this);
            }});
            
            document.getElementById('registerFormFieldsForm').addEventListener('submit', function(e) {{
                e.preventDefault();
                saveFormFields(this);
            }});
            
            document.getElementById('forgotPasswordFormFieldsForm').addEventListener('submit', function(e) {{
                e.preventDefault();
                saveFormFields(this);
            }});
            
            document.getElementById('resetPasswordFormFieldsForm').addEventListener('submit', function(e) {{
                e.preventDefault();
                saveFormFields(this);
            }});
            
            document.getElementById('designSettingsForm').addEventListener('submit', function(e) {{
                e.preventDefault();
                saveDesignSettings(this);
            }});
            
            // Ayarları kaydetme fonksiyonları
            function saveSocialSettings(form) {{
                const formData = new FormData(form);
                const providers = [];
                
                document.querySelectorAll('input[name="providers[]"]:checked').forEach(el => {{
                    providers.push(el.value);
                }});
                
                const data = {{
                    show_social: formData.get('show_social') === 'on',
                    social_providers: providers
                }};
                
                // AJAX ile ayarları kaydet
                fetch('/admin/auth-settings', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify(data)
                }})
                .then(response => response.json())
                .then(data => {{
                    alert('Sosyal medya ayarları kaydedildi!');
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    alert('Hata oluştu: ' + error);
                }});
            }}
            
            function saveFormFields(form) {{
                // Form alanlarını topla
                const formType = form.querySelector('input[name="form_type"]').value;
                const fieldsContainer = document.getElementById(formType + 'FieldsList');
                const fieldCards = fieldsContainer.querySelectorAll('.card');
                
                const fields = [];
                fieldCards.forEach(card => {{
                    const fieldId = card.dataset.fieldId;
                    const nameInput = card.querySelector('input[name="name"]');
                    const labelInput = card.querySelector('input[name="label"]');
                    const typeSelect = card.querySelector('select[name="type"]');
                    const requiredCheckbox = card.querySelector('input[name="required"]');
                    const orderInput = card.querySelector('input[name="order"]');
                    
                    if (nameInput && labelInput && typeSelect) {{
                        fields.push({{
                            id: fieldId,
                            name: nameInput.value,
                            label: labelInput.value,
                            type: typeSelect.value,
                            required: requiredCheckbox ? requiredCheckbox.checked : false,
                            order: orderInput ? parseInt(orderInput.value) : 0
                        }});
                    }}
                }});
                
                // AJAX ile form alanlarını kaydet
                fetch('/admin/update-form-fields', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        form_type: formType,
                        fields: fields
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    alert('Form alanları kaydedildi!');
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    alert('Hata oluştu: ' + error);
                }});
            }}
            
            function saveDesignSettings(form) {{
                const formData = new FormData(form);
                const data = {{
                    form_width: formData.get('form_width'),
                    form_style: formData.get('form_style'),
                    button_style: formData.get('button_style')
                }};
                
                // AJAX ile tasarım ayarlarını kaydet
                fetch('/admin/update-design-settings', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify(data)
                }})
                .then(response => response.json())
                .then(data => {{
                    alert('Tasarım ayarları kaydedildi!');
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    alert('Hata oluştu: ' + error);
                }});
            }}
        }});
        </script>
        '''
        
        # Base layout ile sayfayı render et
        return base_layout.render_page(page_html, {
            'title': 'Auth Form Yönetimi - PofuAi',
            'theme': 'blue-theme'
        })

    @admin_required
    def get_form_field(self):
        """Form alanı detaylarını getir"""
        try:
            # Geçici olarak yetki kontrolünü atlayalım
            # Input'ları al
            data = self._safe_get_input()
            
            # Alan bilgilerini al
            form_type = data.get('form_type', '')
            field_name = data.get('field_name', '')
            
            if not form_type or not field_name:
                return self.json_response({'error': 'Geçersiz parametreler'}, 400)
                
            # Alanı bul
            field = self.auth_service.get_field_details(form_type, field_name)
            
            if not field:
                return self.json_response({'error': 'Alan bulunamadı'}, 404)
                
            return self.json_response(field)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    @admin_required
    def save_form_field(self):
        """Form alanını kaydet"""
        try:
            # Geçici olarak yetki kontrolünü atlayalım
            # Input'ları al
            data = self._safe_get_input()
            
            # Validasyon
            required_fields = ['form_type', 'field_name', 'field_type', 'label', 'placeholder']
            for field in required_fields:
                if field not in data or not data[field]:
                    return self.json_response({'error': f'{field} alanı gerekli'}, 400)
            
            # Alanı kaydet
            result = self.auth_service.save_field(data)
            
            if not result:
                return self.json_response({'error': 'Alan kaydedilemedi'}, 500)
                
            return self.json_response({'success': True, 'message': 'Alan kaydedildi'})
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def delete_form_field(self):
        """Form alanını sil"""
        try:
            # Geçici olarak yetki kontrolünü atlayalım
            # Input'ları al
            data = self._safe_get_input()
            
            # Validasyon
            form_type = data.get('form_type', '')
            field_name = data.get('field_name', '')
            
            if not form_type or not field_name:
                return self.json_response({'error': 'Geçersiz parametreler'}, 400)
                
            # Alanı sil
            result = self.auth_service.delete_field(form_type, field_name)
            
            if not result:
                return self.json_response({'error': 'Alan silinemedi'}, 500)
                
            return self.json_response({'success': True, 'message': 'Alan silindi'})
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)

    def view(self, template: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """View response'u döndür"""
        data = data or {}
        
        # Eğer template admin.index ise, HTML olarak render et
        if template == 'admin.index':
            try:
                # Admin dashboard HTML'ini oluştur
                html = self._render_admin_dashboard(data)
                
                # HTML içeriğini döndür
                from flask import render_template_string
                return render_template_string(html)
            except Exception as e:
                print(f"Admin dashboard render hatası: {str(e)}")
                # Hata durumunda normal view döndür
        
        # Normal view response'u döndür
        return {
            'type': 'view',
            'template': template,
            'data': data
        }
        
    def _render_admin_dashboard(self, data: Dict[str, Any]) -> str:
        """Admin dashboard HTML'ini oluştur"""
        # İstatistikleri al
        stats = data.get('stats', {})
        
        # Component servisi ve UI servisi kullan
        component_service = ComponentService()
        ui_service = UIService()
        
        # Layout component'lerini oluştur
        base_layout = ui_service.get_base_layout()
        
        # Base layout için CSS ve JS dosyalarını ekle
        base_layout.add_css('/static/assets/css/bootstrap.min.css')
        base_layout.add_css('/static/assets/css/bootstrap-extended.css')
        base_layout.add_css('/static/assets/css/pace.min.css')
        base_layout.add_css('/static/assets/css/extra-icons.css')
        
        # jQuery eklentisini ekle (önce yüklenmelidir)
        base_layout.add_js('https://code.jquery.com/jquery-3.6.0.min.js')
        
        # ApexCharts eklentisini ekle
        base_layout.add_js('/static/assets/plugins/apexchart/apexcharts.min.js')
        
        # Bootstrap ve diğer JS dosyaları
        base_layout.add_js('/static/assets/js/bootstrap.bundle.min.js')
        base_layout.add_js('/static/assets/js/dashboard1.js')
        
        # Perfect Scrollbar eklentisini ekle
        base_layout.add_css('/static/assets/plugins/perfect-scrollbar/css/perfect-scrollbar.css')
        base_layout.add_js('/static/assets/plugins/perfect-scrollbar/js/perfect-scrollbar.js')
        
        # Metismenu eklentisini ekle
        base_layout.add_css('/static/assets/plugins/metismenu/metisMenu.min.css')
        base_layout.add_js('/static/assets/plugins/metismenu/metisMenu.min.js')
        
        # Peity eklentisini ekle
        base_layout.add_js('/static/assets/plugins/peity/jquery.peity.min.js')
        
        # Navbar HTML'i
        navbar_html = component_service.get_navbar_component().render(
            navbar_type="fixed",
            navbar_style="light",
            brand_name="PofuAi Admin",
            user_name="Admin",
            user_email="admin@example.com",
            user_avatar="/static/assets/images/avatars/01.png",
            show_mega_menu=False
        )
        
        # Sidebar HTML'i (admin menüsü aktif)
        sidebar_html = component_service.get_sidebar_component().render({'active_menu': 'admin_index'})
        
        # Yönetim menüsü içeriği
        menu_content = '''
            <div class="list-group">
                <a href="/admin/auth-forms" class="list-group-item list-group-item-action d-flex align-items-center gap-3">
                    <i class="material-icons-outlined">settings</i>
                    Auth Form Yönetimi
                </a>
                <a href="/admin/users" class="list-group-item list-group-item-action d-flex align-items-center gap-3">
                    <i class="material-icons-outlined">people</i>
                    Kullanıcı Yönetimi
                </a>
                <a href="/admin/settings" class="list-group-item list-group-item-action d-flex align-items-center gap-3">
                    <i class="material-icons-outlined">tune</i>
                    Sistem Ayarları
                </a>
            </div>
        '''
        
        # Chart elementleri için HTML
        charts_html = '''
        <!-- ApexCharts için gerekli div elementleri -->
        <div style="display: none;">
            <div id="chart1"></div>
            <div id="chart2"></div>
            <div id="chart3"></div>
            <div id="chart4"></div>
            <div id="chart5"></div>
            <div id="chart6"></div>
            <div id="chart7"></div>
            <div id="chart8"></div>
        </div>
        '''
        
        # Ana içerik HTML'i
        content_html = f'''
        <main class="page-content">
            <div class="page-breadcrumb d-none d-sm-flex align-items-center mb-3">
                <div class="breadcrumb-title pe-3">Dashboard</div>
                <div class="ps-3">
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb mb-0 p-0">
                            <li class="breadcrumb-item"><a href="/"><i class="material-icons-outlined">home</i></a></li>
                            <li class="breadcrumb-item active" aria-current="page">Admin Panel</li>
                        </ol>
                    </nav>
                </div>
            </div>
            
            <div class="row row-cols-1 row-cols-sm-2 row-cols-md-2 row-cols-xl-4 row-cols-xxl-4">
                <div class="col">
                    {component_service.get_info_box_component().render({
                        'title': 'Toplam Kullanıcı',
                        'value': stats.get('users', 0),
                        'icon': 'people',
                        'icon_bg': 'bg-primary',
                        'percent': '+24%'
                    })}
                </div>
                <div class="col">
                    {component_service.get_info_box_component().render({
                        'title': 'İçerikler',
                        'value': stats.get('posts', 0),
                        'icon': 'article',
                        'icon_bg': 'bg-success',
                        'percent': '+14%'
                    })}
                </div>
                <div class="col">
                    {component_service.get_info_box_component().render({
                        'title': 'Yorumlar',
                        'value': stats.get('comments', 0),
                        'icon': 'comment',
                        'icon_bg': 'bg-info',
                        'percent': '+18.7%'
                    })}
                </div>
                <div class="col">
                    {component_service.get_info_box_component().render({
                        'title': 'Ziyaretçiler',
                        'value': stats.get('visitors', 0),
                        'icon': 'visibility',
                        'icon_bg': 'bg-warning',
                        'percent': '+32.6%'
                    })}
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    {component_service.get_card_component().render({
                        'title': 'Yönetim Menüsü',
                        'content': menu_content
                    })}
                </div>
            </div>
            
            {charts_html}
        </main>
        '''
        
        # Tam sayfa HTML'i
        page_html = f'''
        <div class="wrapper">
            {sidebar_html}
            <div class="page-content-wrapper">
                {navbar_html}
                {content_html}
            </div>
        </div>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Sayfa yüklendiğinde çalışacak JavaScript
            console.log('Admin panel yüklendi');
            
            // Sidebar toggle işlevi
            const toggleBtn = document.querySelector('.btn-toggle');
            if (toggleBtn) {{
                toggleBtn.addEventListener('click', function() {{
                    document.querySelector('.wrapper').classList.toggle('toggled');
                }});
            }}
            
            // Perfect scrollbar başlatma
            if (typeof PerfectScrollbar !== 'undefined') {{
                try {{
                    const sidebarNav = document.querySelector(".sidebar-nav");
                    if (sidebarNav) {{
                        new PerfectScrollbar(sidebarNav);
                    }}
                }} catch (e) {{
                    console.log("PerfectScrollbar error:", e.message);
                }}
            }}
            
            // Metismenu başlatma
            if (typeof $ !== 'undefined' && $.fn.metisMenu) {{
                try {{
                    $("#sidenav").metisMenu();
                }} catch (e) {{
                    console.log("MetisMenu error:", e.message);
                }}
            }}
            
            // Peity başlatma
            if (typeof $ !== 'undefined' && $.fn.peity) {{
                try {{
                    $(".data-attributes span").peity("donut");
                }} catch (e) {{
                    console.log("Peity error:", e.message);
                }}
            }}
            
            console.log('Page loaded successfully');
        }});
        </script>
        '''
        
        # Base layout ile sayfayı render et
        return base_layout.render_page(page_html, {
            'title': 'Admin Panel - PofuAi',
            'theme': 'blue-theme'
        })

    @admin_required
    def _generate_fields_html(self, fields, prefix):
        """Form alanlarını HTML'e dönüştür"""
        html = ""
        for field in fields:
            html += f"<div>Field: {field.name}</div>"
        return html
        
    # Eksik Kullanıcı Yönetimi Metodları
    @admin_required
    def create_user(self):
        """Yeni kullanıcı oluşturma formu"""
        try:
            # Form verilerini oluştur
            form_data = {
                'title': 'Kullanıcı Oluştur',
                'form_action': '/admin/users/store',
                'fields': [
                    {'name': 'name', 'type': 'text', 'label': 'Ad Soyad', 'required': True},
                    {'name': 'email', 'type': 'email', 'label': 'E-posta', 'required': True},
                    {'name': 'password', 'type': 'password', 'label': 'Şifre', 'required': True},
                    {'name': 'role', 'type': 'select', 'label': 'Rol', 'options': [
                        {'value': 'user', 'label': 'Kullanıcı'},
                        {'value': 'admin', 'label': 'Yönetici'}
                    ]}
                ]
            }
            
            return self.render_view('admin/users/create', form_data)
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def store_user(self):
        """Yeni kullanıcı oluşturma işlemi"""
        try:
            # Form verilerini al
            form_data = self._safe_get_input()
            
            # Yeni kullanıcı oluştur
            user = User()
            user.name = form_data.get('name', '')
            user.email = form_data.get('email', '')
            user.password = form_data.get('password', '')  # Gerçek uygulamada hash yapılmalı
            user.role = form_data.get('role', 'user')
            
            # Kullanıcıyı kaydet (örnek)
            # user.save()
            
            # Başarılı mesajıyla kullanıcı listesine yönlendir
            return self.redirect('/admin/users', {'message': 'Kullanıcı başarıyla oluşturuldu'})
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def edit_user(self):
        """Kullanıcı düzenleme formu"""
        try:
            # URL'den kullanıcı ID'sini al
            user_id = self.request.view_args.get('id', 0)
            
            # Kullanıcıyı bul (örnek)
            # user = User.find(user_id)
            user = {'id': user_id, 'name': 'Test Kullanıcı', 'email': 'test@example.com', 'role': 'user'}
            
            # Form verilerini oluştur
            form_data = {
                'title': 'Kullanıcı Düzenle',
                'form_action': f'/admin/users/{user_id}/update',
                'user': user,
                'fields': [
                    {'name': 'name', 'type': 'text', 'label': 'Ad Soyad', 'value': user['name'], 'required': True},
                    {'name': 'email', 'type': 'email', 'label': 'E-posta', 'value': user['email'], 'required': True},
                    {'name': 'password', 'type': 'password', 'label': 'Şifre (Değiştirmek için doldurun)'},
                    {'name': 'role', 'type': 'select', 'label': 'Rol', 'value': user['role'], 'options': [
                        {'value': 'user', 'label': 'Kullanıcı'},
                        {'value': 'admin', 'label': 'Yönetici'}
                    ]}
                ]
            }
            
            return self.render_view('admin/users/edit', form_data)
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def update_user(self):
        """Kullanıcı güncelleme işlemi"""
        try:
            # URL'den kullanıcı ID'sini al
            user_id = self.request.view_args.get('id', 0)
            
            # Form verilerini al
            form_data = self._safe_get_input()
            
            # Kullanıcıyı güncelle (örnek)
            # user = User.find(user_id)
            # user.name = form_data.get('name', user.name)
            # user.email = form_data.get('email', user.email)
            # if form_data.get('password'):
            #     user.password = form_data.get('password')  # Gerçek uygulamada hash yapılmalı
            # user.role = form_data.get('role', user.role)
            # user.save()
            
            # Başarılı mesajıyla kullanıcı listesine yönlendir
            return self.redirect('/admin/users', {'message': 'Kullanıcı başarıyla güncellendi'})
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def delete_user(self):
        """Kullanıcı silme işlemi"""
        try:
            # URL'den kullanıcı ID'sini al
            user_id = self.request.view_args.get('id', 0)
            
            # Kullanıcıyı sil (örnek)
            # user = User.find(user_id)
            # user.delete()
            
            # Başarılı mesajıyla kullanıcı listesine yönlendir
            return self.redirect('/admin/users', {'message': 'Kullanıcı başarıyla silindi'})
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # Eksik İçerik Yönetimi Metodları
    @admin_required
    def posts(self):
        """Post yönetimi sayfası"""
        try:
            # Örnek post listesi
            posts = [
                {'id': 1, 'title': 'Örnek Post 1', 'author': 'Admin', 'created_at': '2023-01-01'},
                {'id': 2, 'title': 'Örnek Post 2', 'author': 'Editor', 'created_at': '2023-01-02'},
            ]
            
            return self.render_view('admin/posts/index', {'posts': posts})
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def create_post(self):
        """Yeni post oluşturma formu"""
        try:
            # Form verilerini oluştur
            form_data = {
                'title': 'Post Oluştur',
                'form_action': '/admin/posts/store',
                'fields': [
                    {'name': 'title', 'type': 'text', 'label': 'Başlık', 'required': True},
                    {'name': 'content', 'type': 'textarea', 'label': 'İçerik', 'required': True},
                    {'name': 'category_id', 'type': 'select', 'label': 'Kategori', 'options': [
                        {'value': '1', 'label': 'Genel'},
                        {'value': '2', 'label': 'Teknoloji'},
                        {'value': '3', 'label': 'Yaşam'}
                    ]}
                ]
            }
            
            return self.render_view('admin/posts/create', form_data)
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def store_post(self):
        """Yeni post oluşturma işlemi"""
        try:
            # Form verilerini al
            form_data = self._safe_get_input()
            
            # Yeni post oluştur (örnek)
            # post = Post()
            # post.title = form_data.get('title', '')
            # post.content = form_data.get('content', '')
            # post.category_id = form_data.get('category_id', 1)
            # post.user_id = self.get_current_user().id
            # post.save()
            
            # Başarılı mesajıyla post listesine yönlendir
            return self.redirect('/admin/posts', {'message': 'Post başarıyla oluşturuldu'})
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def edit_post(self):
        """Post düzenleme formu"""
        try:
            # URL'den post ID'sini al
            post_id = self.request.view_args.get('id', 0)
            
            # Post'u bul (örnek)
            # post = Post.find(post_id)
            post = {'id': post_id, 'title': 'Örnek Post', 'content': 'İçerik...', 'category_id': 1}
            
            # Form verilerini oluştur
            form_data = {
                'title': 'Post Düzenle',
                'form_action': f'/admin/posts/{post_id}/update',
                'post': post,
                'fields': [
                    {'name': 'title', 'type': 'text', 'label': 'Başlık', 'value': post['title'], 'required': True},
                    {'name': 'content', 'type': 'textarea', 'label': 'İçerik', 'value': post['content'], 'required': True},
                    {'name': 'category_id', 'type': 'select', 'label': 'Kategori', 'value': post['category_id'], 'options': [
                        {'value': '1', 'label': 'Genel'},
                        {'value': '2', 'label': 'Teknoloji'},
                        {'value': '3', 'label': 'Yaşam'}
                    ]}
                ]
            }
            
            return self.render_view('admin/posts/edit', form_data)
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def update_post(self):
        """Post güncelleme işlemi"""
        try:
            # URL'den post ID'sini al
            post_id = self.request.view_args.get('id', 0)
            
            # Form verilerini al
            form_data = self._safe_get_input()
            
            # Post'u güncelle (örnek)
            # post = Post.find(post_id)
            # post.title = form_data.get('title', post.title)
            # post.content = form_data.get('content', post.content)
            # post.category_id = form_data.get('category_id', post.category_id)
            # post.save()
            
            # Başarılı mesajıyla post listesine yönlendir
            return self.redirect('/admin/posts', {'message': 'Post başarıyla güncellendi'})
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def delete_post(self):
        """Post silme işlemi"""
        try:
            # URL'den post ID'sini al
            post_id = self.request.view_args.get('id', 0)
            
            # Post'u sil (örnek)
            # post = Post.find(post_id)
            # post.delete()
            
            # Başarılı mesajıyla post listesine yönlendir
            return self.redirect('/admin/posts', {'message': 'Post başarıyla silindi'})
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # Eksik Kategori Yönetimi Metodları
    @admin_required
    def categories(self):
        """Kategori yönetimi sayfası"""
        try:
            # Örnek kategori listesi
            categories = [
                {'id': 1, 'name': 'Genel', 'post_count': 5},
                {'id': 2, 'name': 'Teknoloji', 'post_count': 3},
                {'id': 3, 'name': 'Yaşam', 'post_count': 2},
            ]
            
            return self.render_view('admin/categories/index', {'categories': categories})
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # Eksik Ayarlar Yönetimi Metodları
    @admin_required
    def update_settings(self):
        """Site ayarlarını güncelleme işlemi"""
        try:
            # Form verilerini al
            form_data = self._safe_get_input()
            
            # Ayarları güncelle (örnek)
            # settings = Settings.instance()
            # settings.site_name = form_data.get('site_name', settings.site_name)
            # settings.site_description = form_data.get('site_description', settings.site_description)
            # settings.site_keywords = form_data.get('site_keywords', settings.site_keywords)
            # settings.site_logo = form_data.get('site_logo', settings.site_logo)
            # settings.save()
            
            # Başarılı mesajıyla ayarlar sayfasına yönlendir
            return self.redirect('/admin/settings', {'message': 'Ayarlar başarıyla güncellendi'})
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # Eksik Log Yönetimi Metodları
    @admin_required
    def logs(self):
        """Log görüntüleme sayfası"""
        try:
            # Örnek log verileri
            logs = [
                {'id': 1, 'level': 'info', 'message': 'Kullanıcı girişi yapıldı', 'created_at': '2023-01-01 12:00:00'},
                {'id': 2, 'level': 'warning', 'message': 'Hatalı giriş denemesi', 'created_at': '2023-01-01 12:05:00'},
                {'id': 3, 'level': 'error', 'message': 'Veritabanı bağlantı hatası', 'created_at': '2023-01-01 12:10:00'},
            ]
            
            return self.render_view('admin/logs/index', {'logs': logs})
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # Eksik Yedekleme Yönetimi Metodları
    @admin_required
    def backup(self):
        """Yedekleme sayfası"""
        try:
            # Örnek yedek listesi
            backups = [
                {'id': 1, 'name': 'backup_2023_01_01.zip', 'size': '1.2MB', 'created_at': '2023-01-01 12:00:00'},
                {'id': 2, 'name': 'backup_2023_01_02.zip', 'size': '1.3MB', 'created_at': '2023-01-02 12:00:00'},
                {'id': 3, 'name': 'backup_2023_01_03.zip', 'size': '1.4MB', 'created_at': '2023-01-03 12:00:00'},
            ]
            
            return self.render_view('admin/backup/index', {'backups': backups})
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def create_backup(self):
        """Yedekleme oluşturma işlemi"""
        try:
            # Yedekleme işlemi (örnek)
            # backup_service = BackupService()
            # backup_file = backup_service.create_backup()
            
            # Başarılı mesajıyla yedekleme sayfasına yönlendir
            return self.redirect('/admin/backup', {'message': 'Yedekleme başarıyla oluşturuldu'})
        except Exception as e:
            return error_handler.handle_error(e, self.request) 