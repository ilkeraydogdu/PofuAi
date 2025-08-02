"""
Audit Log Model
Sistem aktivite takip modeli
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.Database.base_model import BaseModel
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

class AuditLog(BaseModel):
    """Audit log modeli"""
    
    table_name = 'audit_logs'
    
    def __init__(self):
        super().__init__()
        self.fillable = [
            'user_id', 'action', 'model_type', 'model_id', 'old_values', 
            'new_values', 'ip_address', 'user_agent', 'url', 'method'
        ]
        
        self.validation_rules = {
            'action': 'required|string|max:50',
            'model_type': 'string|max:100',
            'ip_address': 'string|max:45',
            'method': 'string|max:10'
        }
    
    def log_action(self, data: Dict[str, Any]) -> int:
        """Aktivite kaydet"""
        try:
            # Audit log verisi hazırla
            log_data = {
                'user_id': data.get('user_id'),
                'action': data['action'],
                'model_type': data.get('model_type'),
                'model_id': data.get('model_id'),
                'old_values': json.dumps(data.get('old_values', {})) if data.get('old_values') else None,
                'new_values': json.dumps(data.get('new_values', {})) if data.get('new_values') else None,
                'ip_address': data.get('ip_address'),
                'user_agent': data.get('user_agent'),
                'url': data.get('url'),
                'method': data.get('method'),
                'created_at': datetime.now()
            }
            
            # Validasyon
            if not self.validate(log_data):
                return 0
            
            # Veritabanına kaydet
            cursor = self.db.cursor()
            
            columns = ', '.join([k for k, v in log_data.items() if v is not None])
            placeholders = ', '.join(['%s'] * len([v for v in log_data.values() if v is not None]))
            values = [v for v in log_data.values() if v is not None]
            
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            
            cursor.execute(query, values)
            log_id = cursor.lastrowid
            
            self.db.commit()
            cursor.close()
            
            return log_id
            
        except Exception as e:
            self.logger.error(f"Audit log creation error: {e}")
            return 0
    
    def get_user_activities(self, user_id: int, limit: int = 100, 
                           action_filter: str = None) -> List[Dict[str, Any]]:
        """Kullanıcı aktivitelerini getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            query = f"""
                SELECT al.*, u.name as user_name, u.email as user_email
                FROM {self.table_name} al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE al.user_id = %s
            """
            params = [user_id]
            
            if action_filter:
                query += " AND al.action LIKE %s"
                params.append(f"%{action_filter}%")
            
            query += " ORDER BY al.created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            activities = cursor.fetchall()
            
            # JSON alanları parse et
            for activity in activities:
                if activity['old_values']:
                    activity['old_values'] = json.loads(activity['old_values'])
                if activity['new_values']:
                    activity['new_values'] = json.loads(activity['new_values'])
            
            cursor.close()
            return activities
            
        except Exception as e:
            self.logger.error(f"Get user activities error: {e}")
            return []
    
    def get_model_history(self, model_type: str, model_id: int) -> List[Dict[str, Any]]:
        """Model geçmişini getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            query = f"""
                SELECT al.*, u.name as user_name, u.email as user_email
                FROM {self.table_name} al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE al.model_type = %s AND al.model_id = %s
                ORDER BY al.created_at DESC
            """
            
            cursor.execute(query, [model_type, model_id])
            history = cursor.fetchall()
            
            # JSON alanları parse et
            for record in history:
                if record['old_values']:
                    record['old_values'] = json.loads(record['old_values'])
                if record['new_values']:
                    record['new_values'] = json.loads(record['new_values'])
            
            cursor.close()
            return history
            
        except Exception as e:
            self.logger.error(f"Get model history error: {e}")
            return []
    
    def get_system_activities(self, limit: int = 500, 
                             date_from: datetime = None,
                             date_to: datetime = None,
                             action_filter: str = None) -> List[Dict[str, Any]]:
        """Sistem aktivitelerini getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            query = f"""
                SELECT al.*, u.name as user_name, u.email as user_email
                FROM {self.table_name} al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE 1=1
            """
            params = []
            
            if date_from:
                query += " AND al.created_at >= %s"
                params.append(date_from)
            
            if date_to:
                query += " AND al.created_at <= %s"
                params.append(date_to)
            
            if action_filter:
                query += " AND al.action LIKE %s"
                params.append(f"%{action_filter}%")
            
            query += " ORDER BY al.created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            activities = cursor.fetchall()
            
            # JSON alanları parse et
            for activity in activities:
                if activity['old_values']:
                    activity['old_values'] = json.loads(activity['old_values'])
                if activity['new_values']:
                    activity['new_values'] = json.loads(activity['new_values'])
            
            cursor.close()
            return activities
            
        except Exception as e:
            self.logger.error(f"Get system activities error: {e}")
            return []
    
    def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Güvenlik olaylarını getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            security_actions = [
                'login', 'logout', 'login_failed', 'password_changed',
                'email_changed', 'account_locked', 'permission_changed',
                'unauthorized_access', 'suspicious_activity'
            ]
            
            placeholders = ', '.join(['%s'] * len(security_actions))
            query = f"""
                SELECT al.*, u.name as user_name, u.email as user_email
                FROM {self.table_name} al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE al.action IN ({placeholders})
                ORDER BY al.created_at DESC
                LIMIT %s
            """
            
            params = security_actions + [limit]
            cursor.execute(query, params)
            events = cursor.fetchall()
            
            cursor.close()
            return events
            
        except Exception as e:
            self.logger.error(f"Get security events error: {e}")
            return []
    
    def get_activity_stats(self, date_from: datetime = None, 
                          date_to: datetime = None) -> Dict[str, Any]:
        """Aktivite istatistikleri"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            # Tarih filtresi
            date_filter = ""
            params = []
            
            if date_from:
                date_filter += " AND created_at >= %s"
                params.append(date_from)
            
            if date_to:
                date_filter += " AND created_at <= %s"
                params.append(date_to)
            
            # Toplam aktivite sayısı
            query = f"SELECT COUNT(*) as total FROM {self.table_name} WHERE 1=1{date_filter}"
            cursor.execute(query, params)
            total = cursor.fetchone()['total']
            
            # Aksiyon bazında sayılar
            query = f"""
                SELECT action, COUNT(*) as count
                FROM {self.table_name} 
                WHERE 1=1{date_filter}
                GROUP BY action
                ORDER BY count DESC
            """
            cursor.execute(query, params)
            by_action = cursor.fetchall()
            
            # Kullanıcı bazında sayılar
            query = f"""
                SELECT u.name, u.email, COUNT(*) as count
                FROM {self.table_name} al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE al.user_id IS NOT NULL{date_filter}
                GROUP BY al.user_id
                ORDER BY count DESC
                LIMIT 10
            """
            cursor.execute(query, params)
            by_user = cursor.fetchall()
            
            # Günlük aktivite
            query = f"""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM {self.table_name}
                WHERE 1=1{date_filter}
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 30
            """
            cursor.execute(query, params)
            daily_activity = cursor.fetchall()
            
            cursor.close()
            
            return {
                'total': total,
                'by_action': by_action,
                'by_user': by_user,
                'daily_activity': daily_activity
            }
            
        except Exception as e:
            self.logger.error(f"Get activity stats error: {e}")
            return {'total': 0, 'by_action': [], 'by_user': [], 'daily_activity': []}
    
    def cleanup_old_logs(self, days: int = 90) -> int:
        """Eski logları temizle"""
        try:
            cursor = self.db.cursor()
            
            query = f"""
                DELETE FROM {self.table_name} 
                WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            
            cursor.execute(query, [days])
            deleted_count = cursor.rowcount
            
            self.db.commit()
            cursor.close()
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Cleanup old logs error: {e}")
            return 0

# Audit action types
AUDIT_ACTIONS = {
    # User actions
    'user_created': 'Kullanıcı Oluşturuldu',
    'user_updated': 'Kullanıcı Güncellendi',
    'user_deleted': 'Kullanıcı Silindi',
    'login': 'Giriş Yapıldı',
    'logout': 'Çıkış Yapıldı',
    'login_failed': 'Başarısız Giriş',
    'password_changed': 'Şifre Değiştirildi',
    
    # Product actions
    'product_created': 'Ürün Oluşturuldu',
    'product_updated': 'Ürün Güncellendi',
    'product_deleted': 'Ürün Silindi',
    'product_published': 'Ürün Yayınlandı',
    'product_unpublished': 'Ürün Yayından Kaldırıldı',
    
    # Order actions
    'order_created': 'Sipariş Oluşturuldu',
    'order_updated': 'Sipariş Güncellendi',
    'order_cancelled': 'Sipariş İptal Edildi',
    'order_completed': 'Sipariş Tamamlandı',
    
    # System actions
    'system_backup': 'Sistem Yedeği',
    'system_maintenance': 'Sistem Bakımı',
    'integration_added': 'Entegrasyon Eklendi',
    'integration_removed': 'Entegrasyon Kaldırıldı',
    'settings_changed': 'Ayarlar Değiştirildi',
    
    # Security actions
    'unauthorized_access': 'Yetkisiz Erişim',
    'suspicious_activity': 'Şüpheli Aktivite',
    'account_locked': 'Hesap Kilitlendi',
    'permission_changed': 'Yetki Değiştirildi'
}