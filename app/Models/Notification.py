"""
Notification Model
Bildirim yönetimi modeli
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.Database.base_model import BaseModel
from datetime import datetime
from typing import Dict, Any, List, Optional

class Notification(BaseModel):
    """Bildirim modeli"""
    
    table_name = 'notifications'
    
    def __init__(self):
        super().__init__()
        self.fillable = [
            'user_id', 'type', 'title', 'message', 'data', 
            'read_at', 'action_url', 'icon', 'priority', 'channel'
        ]
        
        self.validation_rules = {
            'user_id': 'required|integer',
            'type': 'required|string|max:50',
            'title': 'required|string|max:255',
            'message': 'required|string',
            'priority': 'string|in:low,normal,high,urgent',
            'channel': 'string|in:web,email,sms,push'
        }
    
    def create_notification(self, data: Dict[str, Any]) -> int:
        """Yeni bildirim oluştur"""
        try:
            # Varsayılan değerler
            notification_data = {
                'user_id': data['user_id'],
                'type': data['type'],
                'title': data['title'],
                'message': data['message'],
                'data': data.get('data', '{}'),
                'action_url': data.get('action_url'),
                'icon': data.get('icon', 'notifications'),
                'priority': data.get('priority', 'normal'),
                'channel': data.get('channel', 'web'),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Validasyon
            if not self.validate(notification_data):
                return 0
            
            # Veritabanına kaydet
            cursor = self.db.cursor()
            
            columns = ', '.join(notification_data.keys())
            placeholders = ', '.join(['%s'] * len(notification_data))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            
            cursor.execute(query, list(notification_data.values()))
            notification_id = cursor.lastrowid
            
            self.db.commit()
            cursor.close()
            
            return notification_id
            
        except Exception as e:
            self.logger.error(f"Notification creation error: {e}")
            return 0
    
    def get_user_notifications(self, user_id: int, limit: int = 50, 
                              unread_only: bool = False) -> List[Dict[str, Any]]:
        """Kullanıcının bildirimlerini getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE user_id = %s
            """
            params = [user_id]
            
            if unread_only:
                query += " AND read_at IS NULL"
            
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            notifications = cursor.fetchall()
            cursor.close()
            
            return notifications
            
        except Exception as e:
            self.logger.error(f"Get user notifications error: {e}")
            return []
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Bildirimi okundu olarak işaretle"""
        try:
            cursor = self.db.cursor()
            
            query = f"""
                UPDATE {self.table_name} 
                SET read_at = %s, updated_at = %s 
                WHERE id = %s AND user_id = %s
            """
            
            cursor.execute(query, [datetime.now(), datetime.now(), notification_id, user_id])
            success = cursor.rowcount > 0
            
            self.db.commit()
            cursor.close()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Mark notification as read error: {e}")
            return False
    
    def mark_all_as_read(self, user_id: int) -> bool:
        """Tüm bildirimleri okundu olarak işaretle"""
        try:
            cursor = self.db.cursor()
            
            query = f"""
                UPDATE {self.table_name} 
                SET read_at = %s, updated_at = %s 
                WHERE user_id = %s AND read_at IS NULL
            """
            
            cursor.execute(query, [datetime.now(), datetime.now(), user_id])
            
            self.db.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Mark all notifications as read error: {e}")
            return False
    
    def get_unread_count(self, user_id: int) -> int:
        """Okunmamış bildirim sayısı"""
        try:
            cursor = self.db.cursor()
            
            query = f"""
                SELECT COUNT(*) FROM {self.table_name} 
                WHERE user_id = %s AND read_at IS NULL
            """
            
            cursor.execute(query, [user_id])
            count = cursor.fetchone()[0]
            cursor.close()
            
            return count
            
        except Exception as e:
            self.logger.error(f"Get unread count error: {e}")
            return 0
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Bildirimi sil"""
        try:
            cursor = self.db.cursor()
            
            query = f"DELETE FROM {self.table_name} WHERE id = %s AND user_id = %s"
            cursor.execute(query, [notification_id, user_id])
            
            success = cursor.rowcount > 0
            self.db.commit()
            cursor.close()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Delete notification error: {e}")
            return False
    
    def cleanup_old_notifications(self, days: int = 30) -> int:
        """Eski bildirimleri temizle"""
        try:
            cursor = self.db.cursor()
            
            query = f"""
                DELETE FROM {self.table_name} 
                WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
                AND read_at IS NOT NULL
            """
            
            cursor.execute(query, [days])
            deleted_count = cursor.rowcount
            
            self.db.commit()
            cursor.close()
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Cleanup old notifications error: {e}")
            return 0
    
    def get_notification_stats(self, user_id: int) -> Dict[str, Any]:
        """Bildirim istatistikleri"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            # Toplam, okunmuş, okunmamış sayıları
            query = f"""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN read_at IS NOT NULL THEN 1 ELSE 0 END) as read_count,
                    SUM(CASE WHEN read_at IS NULL THEN 1 ELSE 0 END) as unread_count
                FROM {self.table_name} 
                WHERE user_id = %s
            """
            
            cursor.execute(query, [user_id])
            stats = cursor.fetchone()
            
            # Tür bazında sayılar
            query = f"""
                SELECT type, COUNT(*) as count
                FROM {self.table_name} 
                WHERE user_id = %s
                GROUP BY type
            """
            
            cursor.execute(query, [user_id])
            type_stats = cursor.fetchall()
            
            cursor.close()
            
            return {
                'total': stats['total'],
                'read_count': stats['read_count'],
                'unread_count': stats['unread_count'],
                'by_type': {item['type']: item['count'] for item in type_stats}
            }
            
        except Exception as e:
            self.logger.error(f"Get notification stats error: {e}")
            return {'total': 0, 'read_count': 0, 'unread_count': 0, 'by_type': {}}

# Notification türleri
NOTIFICATION_TYPES = {
    'order_new': 'Yeni Sipariş',
    'order_updated': 'Sipariş Güncellendi',
    'order_cancelled': 'Sipariş İptal Edildi',
    'payment_received': 'Ödeme Alındı',
    'product_low_stock': 'Stok Azalıyor',
    'product_out_of_stock': 'Stok Bitti',
    'message_new': 'Yeni Mesaj',
    'review_new': 'Yeni Değerlendirme',
    'system_maintenance': 'Sistem Bakımı',
    'account_security': 'Hesap Güvenliği',
    'integration_error': 'Entegrasyon Hatası',
    'integration_success': 'Entegrasyon Başarılı'
}

# Notification priority levels
NOTIFICATION_PRIORITIES = {
    'low': 'Düşük',
    'normal': 'Normal',
    'high': 'Yüksek',
    'urgent': 'Acil'
}

# Notification channels
NOTIFICATION_CHANNELS = {
    'web': 'Web',
    'email': 'E-posta',
    'sms': 'SMS',
    'push': 'Push Notification'
}