"""
Bildirim servisi modülü
"""
from typing import Dict, Any, List, Optional, Union
from core.Services.base_service import BaseService


class NotificationChannel:
    """Bildirim kanalı temel sınıfı"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
    
    def send(self, notification: Dict[str, Any], recipient: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bildirim gönder
        
        Args:
            notification: Bildirim verileri
            recipient: Alıcı verileri
            
        Returns:
            Dict: Gönderim sonucu
        """
        raise NotImplementedError("Subclasses must implement send method")
    
    def is_enabled(self) -> bool:
        """Kanal aktif mi?"""
        return self.enabled
    
    def get_name(self) -> str:
        """Kanal adını al"""
        return self.__class__.__name__


class EmailChannel(NotificationChannel):
    """E-posta bildirim kanalı"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.mail_service = None
        self._init_mail_service()
    
    def _init_mail_service(self):
        """Mail servisini başlat"""
        try:
            from core.Services.mail_service import MailService
            self.mail_service = MailService()
        except Exception as e:
            self.log(f"Mail service initialization error: {str(e)}", "error")
    
    def send(self, notification: Dict[str, Any], recipient: Dict[str, Any]) -> Dict[str, Any]:
        """
        E-posta bildirimi gönder
        
        Args:
            notification: Bildirim verileri (title, message, template)
            recipient: Alıcı verileri (email, name)
            
        Returns:
            Dict: Gönderim sonucu
        """
        if not self.mail_service:
            return {
                'status': 'error',
                'message': 'Mail service not available'
            }
        
        try:
            # E-posta verilerini hazırla
            email_data = {
                'to': recipient.get('email'),
                'subject': notification.get('title', 'Bildirim'),
                'template': notification.get('template', 'notification'),
                'data': {
                    'message': notification.get('message', ''),
                    'recipient_name': recipient.get('name', ''),
                    **notification.get('data', {})
                }
            }
            
            # E-postayı gönder
            result = self.mail_service.send_email(**email_data)
            
            if result.get('status') == 'success':
                return {
                    'status': 'success',
                    'message': 'Email sent successfully',
                    'data': result.get('data', {})
                }
            else:
                return {
                    'status': 'error',
                    'message': result.get('message', 'Email sending failed')
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Email sending exception: {str(e)}'
            }


class DatabaseChannel(NotificationChannel):
    """Veritabanı bildirim kanalı"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.table_name = self.config.get('table', 'notifications')
    
    def send(self, notification: Dict[str, Any], recipient: Dict[str, Any]) -> Dict[str, Any]:
        """
        Veritabanına bildirim kaydet
        
        Args:
            notification: Bildirim verileri (title, message, type)
            recipient: Alıcı verileri (id, email)
            
        Returns:
            Dict: Kaydetme sonucu
        """
        try:
            # Veritabanı bağlantısını al
            from core.Database.connection import get_connection
            db = get_connection()
            
            # Bildirim verilerini hazırla
            notification_data = {
                'user_id': recipient.get('id'),
                'title': notification.get('title', ''),
                'message': notification.get('message', ''),
                'type': notification.get('type', 'general'),
                'data': notification.get('data', {}),
                'read_at': None,
                'created_at': 'CURRENT_TIMESTAMP'
            }
            
            # Bildirimi kaydet
            result = db.table(self.table_name).insert(notification_data)
            
            if result:
                return {
                    'status': 'success',
                    'message': 'Notification saved to database',
                    'data': {'notification_id': result}
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to save notification to database'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Database notification error: {str(e)}'
            }


class PushChannel(NotificationChannel):
    """Push bildirim kanalı"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.api_key = self.config.get('api_key')
        self.api_url = self.config.get('api_url')
    
    def send(self, notification: Dict[str, Any], recipient: Dict[str, Any]) -> Dict[str, Any]:
        """
        Push bildirimi gönder
        
        Args:
            notification: Bildirim verileri (title, message, data)
            recipient: Alıcı verileri (device_token, platform)
            
        Returns:
            Dict: Gönderim sonucu
        """
        if not self.api_key or not self.api_url:
            return {
                'status': 'error',
                'message': 'Push notification not configured'
            }
        
        try:
            # Push bildirim verilerini hazırla
            push_data = {
                'to': recipient.get('device_token'),
                'notification': {
                    'title': notification.get('title', ''),
                    'body': notification.get('message', ''),
                    'data': notification.get('data', {})
                },
                'priority': 'high'
            }
            
            # HTTP isteği gönder (basit implementasyon)
            import requests
            headers = {
                'Authorization': f'key={self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(self.api_url, json=push_data, headers=headers)
            
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'message': 'Push notification sent',
                    'data': response.json()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Push notification failed: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Push notification error: {str(e)}'
            }


class NotificationService(BaseService):
    """Bildirim servisi"""
    
    def __init__(self):
        super().__init__()
        self.channels = {}
        self.config = self.get_config('notification') or {}
        self.notification_config = self.config.get('notifications', {})
        self._load_default_channels()
    
    def _load_default_channels(self):
        """Varsayılan kanalları yükle"""
        try:
            # E-posta kanalı
            mail_config = self.notification_config.get('mail', {})
            self.add_channel('mail', EmailChannel(mail_config))
            
            # Veritabanı kanalı
            db_config = self.notification_config.get('database', {})
            self.add_channel('database', DatabaseChannel(db_config))
            
            # Push kanalı (opsiyonel)
            push_config = self.notification_config.get('push', {})
            if push_config.get('enabled', False):
                self.add_channel('push', PushChannel(push_config))
                
        except Exception as e:
            self.log(f"Error loading notification channels: {str(e)}", "error")
    
    def add_channel(self, name: str, channel: NotificationChannel) -> bool:
        """
        Bildirim kanalı ekle

        Args:
            name: Kanal adı
            channel: Kanal nesnesi

        Returns:
            bool: Başarılı ise True
        """
        if not isinstance(channel, NotificationChannel):
            self.log(f"Invalid notification channel: {name}", "error")
            return False

        self.channels[name] = channel
        self.log(f"Notification channel added: {name}")
        return True

    def send(self, notification: Dict[str, Any], recipient: Dict[str, Any], 
             channels: List[str] = None) -> Dict[str, Any]:
        """
        Bildirimi gönder
        
        Args:
            notification: Bildirim verileri (title, message, data)
            recipient: Alıcı verileri (id, email, device_token)
            channels: Kullanılacak kanal adları (None ise tüm kanallar)
            
        Returns:
            Dict: Gönderim sonuçları
        """
        results = {}
        success_count = 0
        error_count = 0

        # Kullanılacak kanalları belirle
        if channels is None:
            use_channels = list(self.channels.keys())
        else:
            use_channels = [c for c in channels if c in self.channels]
        
        # Her kanala bildirim gönder
        for channel_name in use_channels:
            channel = self.channels[channel_name]
            
            if not channel.is_enabled():
                results[channel_name] = {
                    'status': 'error',
                    'message': 'Channel is disabled'
                }
                error_count += 1
                continue
            
            # Bildirimi gönder
            try:
                result = channel.send(notification, recipient)
                results[channel_name] = result
                
                if result.get('status') == 'success':
                    success_count += 1
                else:
                    error_count += 1
                
            except Exception as e:
                results[channel_name] = {
                    'status': 'error',
                    'message': f'Exception: {str(e)}'
                }
                error_count += 1
        
        # Genel sonucu oluştur
        if error_count == 0 and success_count > 0:
            return self.success_response(f"Notification sent via {success_count} channels", {
                'results': results,
                'success_count': success_count,
                'error_count': error_count
            })
        elif success_count > 0:
            return self.success_response(f"Notification sent via {success_count} channels with {error_count} errors", {
                'results': results,
                'success_count': success_count,
                'error_count': error_count
            })
        else:
            return self.error_response(f"Failed to send notification via any channel", {
                'results': results,
                'success_count': success_count,
                'error_count': error_count
            })
    
    def send_to_user(self, user_id: Union[int, str], notification: Dict[str, Any], 
                     channels: List[str] = None) -> Dict[str, Any]:
        """
        Kullanıcıya bildirim gönder
        
        Args:
            user_id: Kullanıcı ID
            notification: Bildirim verileri (title, message, data)
            channels: Kullanılacak kanal adları (None ise tüm kanallar)
            
        Returns:
            Dict: Gönderim sonucu
        """
        # Kullanıcı bilgilerini al
        user = self._get_user(user_id)
        
        if not user:
            return self.error_response(f"User not found: {user_id}")
        
        # Bildirimi gönder
        return self.send(notification, user, channels)
    
    def send_to_users(self, user_ids: List[Union[int, str]], notification: Dict[str, Any],
                      channels: List[str] = None) -> Dict[str, Any]:
        """
        Birden fazla kullanıcıya bildirim gönder
        
        Args:
            user_ids: Kullanıcı ID'leri
            notification: Bildirim verileri (title, message, data)
            channels: Kullanılacak kanal adları (None ise tüm kanallar)
            
        Returns:
            Dict: Gönderim sonucu
        """
        results = {}
        success_count = 0
        error_count = 0
        
        for user_id in user_ids:
            result = self.send_to_user(user_id, notification, channels)
            results[str(user_id)] = result
            
            if result.get('status') == 'success':
                success_count += 1
            else:
                error_count += 1
        
        # Genel sonucu oluştur
        if error_count == 0:
            return self.success_response(f"Notification sent to {success_count} users", {
                'results': results,
                'success_count': success_count,
                'error_count': error_count,
                'total': len(user_ids)
            })
        elif success_count > 0:
            return self.success_response(f"Notification sent to {success_count} users with {error_count} errors", {
                'results': results,
                'success_count': success_count,
                'error_count': error_count,
                'total': len(user_ids)
            })
        else:
            return self.error_response(f"Failed to send notification to any user", {
                'results': results,
                'success_count': success_count,
                'error_count': error_count,
                'total': len(user_ids)
            })
    
    def _get_user(self, user_id: Union[int, str]) -> Optional[Dict[str, Any]]:
        """
        Kullanıcı bilgilerini al
        
        Args:
            user_id: Kullanıcı ID
            
        Returns:
            Dict: Kullanıcı bilgileri veya None
        """
        try:
            # Veritabanı bağlantısını al
            from core.Database.connection import get_connection
            db = get_connection()
            
            # Kullanıcıyı sorgula
            user = db.table('users').where('id', user_id).first()
            
            if user:
                return user
            else:
                self.log(f"User not found: {user_id}", "warning")
                return None
                
        except Exception as e:
            self.log(f"Error getting user: {str(e)}", "error")
            return None


# Global notification service instance
_notification_service = None

def get_notification_service() -> NotificationService:
    """Global notification service instance'ını al"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service 