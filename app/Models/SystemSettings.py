"""
System Settings Model
Sistem ayarları modeli
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.Database.base_model import BaseModel
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

class SystemSettings(BaseModel):
    """Sistem ayarları modeli"""
    
    table_name = 'system_settings'
    
    def __init__(self):
        super().__init__()
        self.fillable = [
            'key', 'value', 'type', 'category', 'description', 'is_public', 'updated_by'
        ]
        
        self.validation_rules = {
            'key': 'required|string|max:100',
            'value': 'required',
            'type': 'required|string|in:string,integer,float,boolean,json,array',
            'category': 'required|string|max:50'
        }
        
        # Default settings
        self.default_settings = {
            # Site Settings
            'site_name': {'value': 'PofuAi', 'type': 'string', 'category': 'site', 'description': 'Site adı'},
            'site_description': {'value': 'E-ticaret ve AI Platformu', 'type': 'string', 'category': 'site', 'description': 'Site açıklaması'},
            'site_url': {'value': 'https://pofuai.com', 'type': 'string', 'category': 'site', 'description': 'Site URL'},
            'site_logo': {'value': '/static/assets/images/logo.png', 'type': 'string', 'category': 'site', 'description': 'Site logosu'},
            'site_favicon': {'value': '/static/assets/images/favicon.ico', 'type': 'string', 'category': 'site', 'description': 'Site favicon'},
            'site_timezone': {'value': 'Europe/Istanbul', 'type': 'string', 'category': 'site', 'description': 'Site zaman dilimi'},
            'site_language': {'value': 'tr', 'type': 'string', 'category': 'site', 'description': 'Varsayılan dil'},
            'site_currency': {'value': 'TRY', 'type': 'string', 'category': 'site', 'description': 'Para birimi'},
            
            # Email Settings
            'email_smtp_host': {'value': 'smtp.gmail.com', 'type': 'string', 'category': 'email', 'description': 'SMTP sunucusu'},
            'email_smtp_port': {'value': '587', 'type': 'integer', 'category': 'email', 'description': 'SMTP portu'},
            'email_smtp_username': {'value': '', 'type': 'string', 'category': 'email', 'description': 'SMTP kullanıcı adı'},
            'email_smtp_password': {'value': '', 'type': 'string', 'category': 'email', 'description': 'SMTP şifresi'},
            'email_from_address': {'value': 'noreply@pofuai.com', 'type': 'string', 'category': 'email', 'description': 'Gönderen email adresi'},
            'email_from_name': {'value': 'PofuAi', 'type': 'string', 'category': 'email', 'description': 'Gönderen adı'},
            
            # Security Settings
            'security_password_min_length': {'value': '8', 'type': 'integer', 'category': 'security', 'description': 'Minimum şifre uzunluğu'},
            'security_password_require_uppercase': {'value': 'true', 'type': 'boolean', 'category': 'security', 'description': 'Büyük harf gerekli'},
            'security_password_require_lowercase': {'value': 'true', 'type': 'boolean', 'category': 'security', 'description': 'Küçük harf gerekli'},
            'security_password_require_numbers': {'value': 'true', 'type': 'boolean', 'category': 'security', 'description': 'Rakam gerekli'},
            'security_password_require_symbols': {'value': 'false', 'type': 'boolean', 'category': 'security', 'description': 'Sembol gerekli'},
            'security_session_timeout': {'value': '3600', 'type': 'integer', 'category': 'security', 'description': 'Oturum zaman aşımı (saniye)'},
            'security_max_login_attempts': {'value': '5', 'type': 'integer', 'category': 'security', 'description': 'Maksimum giriş denemesi'},
            'security_lockout_duration': {'value': '900', 'type': 'integer', 'category': 'security', 'description': 'Hesap kilitleme süresi (saniye)'},
            
            # File Upload Settings
            'upload_max_file_size': {'value': '10485760', 'type': 'integer', 'category': 'upload', 'description': 'Maksimum dosya boyutu (byte)'},
            'upload_allowed_extensions': {'value': '["jpg","jpeg","png","gif","pdf","doc","docx"]', 'type': 'json', 'category': 'upload', 'description': 'İzin verilen dosya uzantıları'},
            'upload_path': {'value': 'uploads/', 'type': 'string', 'category': 'upload', 'description': 'Upload klasörü'},
            'upload_enable_virus_scan': {'value': 'false', 'type': 'boolean', 'category': 'upload', 'description': 'Virüs taraması aktif'},
            
            # Cache Settings
            'cache_enabled': {'value': 'true', 'type': 'boolean', 'category': 'cache', 'description': 'Cache aktif'},
            'cache_default_ttl': {'value': '3600', 'type': 'integer', 'category': 'cache', 'description': 'Varsayılan cache süresi (saniye)'},
            'cache_driver': {'value': 'redis', 'type': 'string', 'category': 'cache', 'description': 'Cache sürücüsü'},
            
            # Database Settings
            'database_backup_enabled': {'value': 'true', 'type': 'boolean', 'category': 'database', 'description': 'Otomatik yedekleme aktif'},
            'database_backup_frequency': {'value': 'daily', 'type': 'string', 'category': 'database', 'description': 'Yedekleme sıklığı'},
            'database_backup_retention': {'value': '30', 'type': 'integer', 'category': 'database', 'description': 'Yedek saklama süresi (gün)'},
            
            # API Settings
            'api_rate_limit_enabled': {'value': 'true', 'type': 'boolean', 'category': 'api', 'description': 'API rate limit aktif'},
            'api_rate_limit_requests': {'value': '1000', 'type': 'integer', 'category': 'api', 'description': 'Saatlik istek limiti'},
            'api_key_required': {'value': 'true', 'type': 'boolean', 'category': 'api', 'description': 'API key gerekli'},
            
            # Notification Settings
            'notifications_email_enabled': {'value': 'true', 'type': 'boolean', 'category': 'notifications', 'description': 'Email bildirimleri aktif'},
            'notifications_sms_enabled': {'value': 'false', 'type': 'boolean', 'category': 'notifications', 'description': 'SMS bildirimleri aktif'},
            'notifications_push_enabled': {'value': 'true', 'type': 'boolean', 'category': 'notifications', 'description': 'Push bildirimleri aktif'},
            
            # Analytics Settings
            'analytics_enabled': {'value': 'true', 'type': 'boolean', 'category': 'analytics', 'description': 'Analytics aktif'},
            'analytics_google_id': {'value': '', 'type': 'string', 'category': 'analytics', 'description': 'Google Analytics ID'},
            'analytics_tracking_enabled': {'value': 'true', 'type': 'boolean', 'category': 'analytics', 'description': 'Kullanıcı takibi aktif'},
            
            # Maintenance Settings
            'maintenance_mode': {'value': 'false', 'type': 'boolean', 'category': 'maintenance', 'description': 'Bakım modu aktif'},
            'maintenance_message': {'value': 'Site bakımda. Lütfen daha sonra tekrar deneyin.', 'type': 'string', 'category': 'maintenance', 'description': 'Bakım mesajı'},
            'maintenance_allowed_ips': {'value': '["127.0.0.1"]', 'type': 'json', 'category': 'maintenance', 'description': 'İzin verilen IP adresleri'},
        }
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Ayar değerini getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE `key` = %s", [key])
            setting = cursor.fetchone()
            cursor.close()
            
            if setting:
                return self._parse_value(setting['value'], setting['type'])
            
            # Default ayarları kontrol et
            if key in self.default_settings:
                return self._parse_value(
                    self.default_settings[key]['value'], 
                    self.default_settings[key]['type']
                )
            
            return default
            
        except Exception as e:
            self.logger.error(f"Get setting error: {e}")
            return default
    
    def set_setting(self, key: str, value: Any, setting_type: str = None, 
                   category: str = 'general', description: str = '', user_id: int = None) -> bool:
        """Ayar değerini kaydet"""
        try:
            # Tip belirleme
            if setting_type is None:
                setting_type = self._detect_type(value)
            
            # Değeri string'e çevir
            string_value = self._serialize_value(value, setting_type)
            
            cursor = self.db.cursor()
            
            # Mevcut ayarı kontrol et
            cursor.execute(f"SELECT id FROM {self.table_name} WHERE `key` = %s", [key])
            existing = cursor.fetchone()
            
            if existing:
                # Güncelle
                cursor.execute(f"""
                    UPDATE {self.table_name} 
                    SET value = %s, type = %s, category = %s, description = %s, 
                        updated_by = %s, updated_at = %s
                    WHERE `key` = %s
                """, [string_value, setting_type, category, description, user_id, datetime.now(), key])
            else:
                # Yeni ekle
                cursor.execute(f"""
                    INSERT INTO {self.table_name} 
                    (`key`, value, type, category, description, updated_by, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, [key, string_value, setting_type, category, description, user_id, datetime.now(), datetime.now()])
            
            self.db.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Set setting error: {e}")
            return False
    
    def get_settings_by_category(self, category: str) -> Dict[str, Any]:
        """Kategoriye göre ayarları getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE category = %s ORDER BY `key`", [category])
            settings = cursor.fetchall()
            cursor.close()
            
            result = {}
            for setting in settings:
                result[setting['key']] = {
                    'value': self._parse_value(setting['value'], setting['type']),
                    'type': setting['type'],
                    'description': setting['description'],
                    'is_public': setting['is_public']
                }
            
            # Default ayarları da ekle
            for key, default_setting in self.default_settings.items():
                if default_setting['category'] == category and key not in result:
                    result[key] = {
                        'value': self._parse_value(default_setting['value'], default_setting['type']),
                        'type': default_setting['type'],
                        'description': default_setting['description'],
                        'is_public': False
                    }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Get settings by category error: {e}")
            return {}
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Tüm ayarları getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY category, `key`")
            settings = cursor.fetchall()
            cursor.close()
            
            result = {}
            for setting in settings:
                result[setting['key']] = {
                    'value': self._parse_value(setting['value'], setting['type']),
                    'type': setting['type'],
                    'category': setting['category'],
                    'description': setting['description'],
                    'is_public': setting['is_public']
                }
            
            # Default ayarları da ekle
            for key, default_setting in self.default_settings.items():
                if key not in result:
                    result[key] = {
                        'value': self._parse_value(default_setting['value'], default_setting['type']),
                        'type': default_setting['type'],
                        'category': default_setting['category'],
                        'description': default_setting['description'],
                        'is_public': False
                    }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Get all settings error: {e}")
            return {}
    
    def get_public_settings(self) -> Dict[str, Any]:
        """Public ayarları getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE is_public = TRUE ORDER BY `key`")
            settings = cursor.fetchall()
            cursor.close()
            
            result = {}
            for setting in settings:
                result[setting['key']] = self._parse_value(setting['value'], setting['type'])
            
            return result
            
        except Exception as e:
            self.logger.error(f"Get public settings error: {e}")
            return {}
    
    def delete_setting(self, key: str) -> bool:
        """Ayarı sil"""
        try:
            cursor = self.db.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE `key` = %s", [key])
            
            success = cursor.rowcount > 0
            self.db.commit()
            cursor.close()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Delete setting error: {e}")
            return False
    
    def reset_to_defaults(self, category: str = None) -> bool:
        """Varsayılan ayarlara sıfırla"""
        try:
            cursor = self.db.cursor()
            
            if category:
                # Belirli kategoriyi sıfırla
                cursor.execute(f"DELETE FROM {self.table_name} WHERE category = %s", [category])
                
                # Default ayarları ekle
                for key, default_setting in self.default_settings.items():
                    if default_setting['category'] == category:
                        cursor.execute(f"""
                            INSERT INTO {self.table_name} 
                            (`key`, value, type, category, description, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, [
                            key, 
                            default_setting['value'], 
                            default_setting['type'], 
                            default_setting['category'], 
                            default_setting['description'],
                            datetime.now(),
                            datetime.now()
                        ])
            else:
                # Tüm ayarları sıfırla
                cursor.execute(f"DELETE FROM {self.table_name}")
                
                # Tüm default ayarları ekle
                for key, default_setting in self.default_settings.items():
                    cursor.execute(f"""
                        INSERT INTO {self.table_name} 
                        (`key`, value, type, category, description, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, [
                        key, 
                        default_setting['value'], 
                        default_setting['type'], 
                        default_setting['category'], 
                        default_setting['description'],
                        datetime.now(),
                        datetime.now()
                    ])
            
            self.db.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Reset to defaults error: {e}")
            return False
    
    def export_settings(self, category: str = None) -> Dict[str, Any]:
        """Ayarları export et"""
        try:
            if category:
                return self.get_settings_by_category(category)
            else:
                return self.get_all_settings()
                
        except Exception as e:
            self.logger.error(f"Export settings error: {e}")
            return {}
    
    def import_settings(self, settings: Dict[str, Any], user_id: int = None) -> bool:
        """Ayarları import et"""
        try:
            for key, setting_data in settings.items():
                if isinstance(setting_data, dict):
                    self.set_setting(
                        key, 
                        setting_data['value'], 
                        setting_data.get('type'),
                        setting_data.get('category', 'general'),
                        setting_data.get('description', ''),
                        user_id
                    )
                else:
                    self.set_setting(key, setting_data, user_id=user_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Import settings error: {e}")
            return False
    
    # Helper Methods
    def _parse_value(self, value: str, value_type: str) -> Any:
        """String değeri tipine göre parse et"""
        try:
            if value_type == 'boolean':
                return value.lower() in ('true', '1', 'yes', 'on')
            elif value_type == 'integer':
                return int(value)
            elif value_type == 'float':
                return float(value)
            elif value_type == 'json':
                return json.loads(value)
            elif value_type == 'array':
                return json.loads(value) if isinstance(value, str) else value
            else:  # string
                return value
                
        except Exception as e:
            self.logger.error(f"Parse value error: {e}")
            return value
    
    def _serialize_value(self, value: Any, value_type: str) -> str:
        """Değeri string'e serialize et"""
        try:
            if value_type in ['json', 'array']:
                return json.dumps(value)
            elif value_type == 'boolean':
                return 'true' if value else 'false'
            else:
                return str(value)
                
        except Exception as e:
            self.logger.error(f"Serialize value error: {e}")
            return str(value)
    
    def _detect_type(self, value: Any) -> str:
        """Değerin tipini otomatik belirle"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, (list, dict)):
            return 'json'
        else:
            return 'string'

# Setting categories
SETTING_CATEGORIES = {
    'site': 'Site Ayarları',
    'email': 'Email Ayarları',
    'security': 'Güvenlik Ayarları',
    'upload': 'Dosya Upload Ayarları',
    'cache': 'Cache Ayarları',
    'database': 'Veritabanı Ayarları',
    'api': 'API Ayarları',
    'notifications': 'Bildirim Ayarları',
    'analytics': 'Analytics Ayarları',
    'maintenance': 'Bakım Ayarları',
    'general': 'Genel Ayarlar'
}