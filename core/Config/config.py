"""
Application Configuration Module
Uygulama yapılandırması
"""
import os
import json
import datetime
from typing import Dict, Any, List, Union, Optional

class Config:
    """Uygulama yapılandırma sınıfı"""
    
    def __init__(self, config_dir: str = None):
        # Kök dizini belirle
        self.root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # Config dizini belirle (default: {root}/storage/config/)
        if config_dir is None:
            self.config_dir = os.path.join(self.root_dir, 'storage', 'config')
        else:
            self.config_dir = os.path.abspath(config_dir)
            
        # Config dizinini oluştur
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Varsayılan yapılandırmalar
        self.config_data = {
            'app': {
                'name': 'PofuAi',
                'env': 'development',
                'debug': True,
                'url': 'http://localhost:5000',
                'root_dir': self.root_dir,
                'timezone': 'Europe/Istanbul',
                'locale': 'tr',
                'secret_key': 'YOUR_SECRET_KEY_HERE',
                'default_currency': 'TRY'
            },
            'database': {
                'driver': 'mysql',  # <-- MySQL kullanılıyor
                'host': 'localhost',  # MySQL sunucu adresiniz
                'port': 3306,         # MySQL portu
                'database': 'pofuai', # Kullanmak istediğiniz veritabanı adı
                'username': 'root',   # MySQL kullanıcı adınız (gerekirse değiştirin)
                'password': '',       # MySQL şifreniz (gerekirse değiştirin)
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'prefix': '',
                'options': {
                    'foreign_keys': True
                }
            },
            'mail': {
                'driver': 'smtp',
                'host': 'smtp.example.com',
                'port': 587,
                'encryption': 'tls',
                'username': '',
                'password': '',
                'from': {
                    'address': 'noreply@example.com',
                    'name': 'PofuAi'
                },
                'reply_to': {
                    'address': 'info@example.com',
                    'name': 'PofuAi Team'
                },
                'templates_dir': os.path.join(self.root_dir, 'public', 'Views', 'emails'),
                'store_sent_emails': True,
                'storage_dir': os.path.join(self.root_dir, 'storage', 'emails')
            },
            'session': {
                'driver': 'file',
                'lifetime': 120,
                'expire_on_close': False,
                'encrypt': False,
                'files': os.path.join(self.root_dir, 'storage', 'sessions'),
                'connection': None,
                'table': 'sessions',
                'cookie': 'pofuai_session',
                'path': '/',
                'domain': None,
                'secure': False,
                'http_only': True,
                'same_site': 'lax',
                'lottery': [2, 100]
            },
            'cache': {
                'driver': 'file',
                'default': 'file',
                'stores': {
                    'file': {
                        'driver': 'file',
                        'path': os.path.join(self.root_dir, 'storage', 'cache'),
                    },
                    'redis': {
                        'driver': 'redis',
                        'host': 'localhost',
                        'port': 6379,
                        'password': None,
                        'database': 0,
                    },
                },
                'prefix': 'pofuai_cache'
            },
            'logger': {
                'driver': 'file',
                'path': os.path.join(self.root_dir, 'storage', 'logs'),
                'filename': f'app_{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
                'level': 'debug',
                'max_files': 30,
                'format': '[%(asctime)s] %(levelname)s: %(message)s'
            },
            'queue': {
                'driver': 'sync',
                'default': 'default',
                'connections': {
                    'sync': {
                        'driver': 'sync',
                    },
                    'redis': {
                        'driver': 'redis',
                        'host': 'localhost',
                        'port': 6379,
                        'password': None,
                        'database': 0,
                        'queue': 'default',
                        'retry_after': 90,
                        'block_for': None,
                        'after_commit': False,
                    }
                },
                'failed': {
                    'driver': 'file',
                    'database': os.path.join(self.root_dir, 'storage', 'queue', 'failed.json'),
                },
            },
            'storage': {
                'driver': 'local',
                'root': os.path.join(self.root_dir, 'storage'),
                'public': os.path.join(self.root_dir, 'public', 'uploads'),
                'url': '/uploads',
                'visibility': 'public',
            },
            'view': {
                'path': os.path.join(self.root_dir, 'public', 'Views'),
                'cache': os.path.join(self.root_dir, 'storage', 'cache', 'views'),
                'extension': '.html'
            },
            'cors': {
                'allowed_origins': ['*'],
                'allowed_origins_patterns': [],
                'allowed_methods': ['*'],
                'allowed_headers': ['*'],
                'exposed_headers': [],
                'max_age': 0,
                'supports_credentials': False,
            },
            'notification': {
                'channels': ['database', 'mail'],
                'database': {
                    'table': 'notifications',
                    'connection': None
                },
                'mail': {
                    'template': 'notification',
                    'from': None,
                    'to': None
                },
                'sms': {
                    'driver': 'twilio',
                    'account_sid': '',
                    'auth_token': '',
                    'from': '',
                    'to': ''
                },
                'push': {
                    'driver': 'firebase',
                    'api_key': '',
                    'project_id': '',
                    'sender_id': '',
                    'app_id': '',
                    'measurement_id': ''
                }
            }
        }
        
        # Yapılandırma dosyalarını yükle
        self._load_configs()
        
        # Debug moduna göre error_reporting ayarla
        if not self.config_data.get('app', {}).get('debug', False):
            import sys
            def excepthook(type, value, traceback):
                # Hata günlüğüne kaydet
                import logging
                logging.error(f"Uncaught exception: {value}", exc_info=(type, value, traceback))
                # Kullanıcıya güvenli bir hata mesajı göster
                print("An error occurred. Please check the logs for details.")
            sys.excepthook = excepthook
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Yapılandırma değerini al
        
        Args:
            key: Yapılandırma anahtarı (dot notation destekler, örn: 'app.name')
            default: Değer bulunamazsa döndürülecek varsayılan değer
            
        Returns:
            Any: Yapılandırma değeri veya varsayılan değer
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Yapılandırma değerini ayarla
        
        Args:
            key: Yapılandırma anahtarı (dot notation destekler, örn: 'app.name')
            value: Ayarlanacak değer
        """
        keys = key.split('.')
        config = self.config_data
        
        # Son anahtar hariç tüm anahtarları dolaş
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Son anahtarı ayarla
        config[keys[-1]] = value
    
    def save(self, group: str = None) -> bool:
        """
        Yapılandırmayı dosyaya kaydet
        
        Args:
            group: Kaydedilecek yapılandırma grubu (örn: 'app', 'database')
                  None ise tüm yapılandırmalar kaydedilir
                  
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            if group is None:
                # Tüm yapılandırmayı kaydet
                for key, value in self.config_data.items():
                    self._save_config_group(key, value)
            else:
                # Sadece belirtilen grubu kaydet
                if group in self.config_data:
                    self._save_config_group(group, self.config_data[group])
                else:
                    return False
                    
            return True
        except Exception as e:
            print(f"Config save error: {str(e)}")
            return False
    
    def reload(self, group: str = None) -> bool:
        """
        Yapılandırmayı yeniden yükle
        
        Args:
            group: Yeniden yüklenecek yapılandırma grubu (örn: 'app', 'database')
                  None ise tüm yapılandırmalar yeniden yüklenir
                  
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            if group is None:
                # Tüm yapılandırmayı yeniden yükle
                self._load_configs()
            else:
                # Sadece belirtilen grubu yeniden yükle
                self._load_config_group(group)
                
            return True
        except Exception as e:
            print(f"Config reload error: {str(e)}")
            return False
    
    def _load_configs(self) -> None:
        """Tüm yapılandırma dosyalarını yükle"""
        # Yapılandırma dosyalarını yükle
        for key in self.config_data.keys():
            self._load_config_group(key)
    
    def _load_config_group(self, group: str) -> None:
        """
        Belirli bir yapılandırma grubunu yükle
        
        Args:
            group: Yapılandırma grubu (örn: 'app', 'database')
        """
        config_file = os.path.join(self.config_dir, f"{group}.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    group_data = json.load(f)
                
                # Varsayılan değerleri güncelle
                if group in self.config_data:
                    self._merge_config(self.config_data[group], group_data)
                else:
                    self.config_data[group] = group_data
            except Exception as e:
                print(f"Config load error: {str(e)}")
    
    def _save_config_group(self, group: str, data: Dict[str, Any]) -> None:
        """
        Belirli bir yapılandırma grubunu dosyaya kaydet
        
        Args:
            group: Yapılandırma grubu (örn: 'app', 'database')
            data: Kaydedilecek veri
        """
        config_file = os.path.join(self.config_dir, f"{group}.json")
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        İki yapılandırma sözlüğünü birleştir (derinlemesine)
        
        Args:
            target: Hedef sözlük (güncellenecek)
            source: Kaynak sözlük (değerleri alınacak)
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value


# Config singleton instance
_config = None

def get_config(key: str = None, default: Any = None) -> Any:
    """
    Config değerini al
    
    Args:
        key: Config anahtarı (dot notation destekler)
        default: Varsayılan değer
        
    Returns:
        Any: Config değeri veya instance
    """
    global _config
    if _config is None:
        _config = Config()
    
    if key is None:
        return _config
    
    return _config.get(key, default) 