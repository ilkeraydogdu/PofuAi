"""
Message Model
Mesajlaşma sistemi modeli
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.Database.base_model import BaseModel
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

class Message(BaseModel):
    """Mesaj modeli"""
    
    table_name = 'messages'
    
    def __init__(self):
        super().__init__()
        self.fillable = [
            'sender_id', 'receiver_id', 'subject', 'content', 'message_type',
            'is_read', 'read_at', 'parent_id', 'attachments', 'priority'
        ]
        
        self.validation_rules = {
            'sender_id': 'required|integer',
            'receiver_id': 'required|integer',
            'subject': 'required|string|max:255',
            'content': 'required|string',
            'message_type': 'string|in:private,support,system,announcement',
            'priority': 'string|in:low,normal,high,urgent'
        }
    
    def send_message(self, data: Dict[str, Any]) -> int:
        """Mesaj gönder"""
        try:
            # Mesaj verisi hazırla
            message_data = {
                'sender_id': data['sender_id'],
                'receiver_id': data['receiver_id'],
                'subject': data['subject'],
                'content': data['content'],
                'message_type': data.get('message_type', 'private'),
                'priority': data.get('priority', 'normal'),
                'parent_id': data.get('parent_id'),
                'attachments': json.dumps(data.get('attachments', [])) if data.get('attachments') else None,
                'is_read': False,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Validasyon
            if not self.validate(message_data):
                return 0
            
            # Veritabanına kaydet
            cursor = self.db.cursor()
            
            columns = ', '.join([k for k, v in message_data.items() if v is not None])
            placeholders = ', '.join(['%s'] * len([v for v in message_data.values() if v is not None]))
            values = [v for v in message_data.values() if v is not None]
            
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            
            cursor.execute(query, values)
            message_id = cursor.lastrowid
            
            self.db.commit()
            cursor.close()
            
            return message_id
            
        except Exception as e:
            self.logger.error(f"Send message error: {e}")
            return 0
    
    def get_user_messages(self, user_id: int, message_type: str = 'all', 
                         limit: int = 50, page: int = 1) -> Dict[str, Any]:
        """Kullanıcının mesajlarını getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            offset = (page - 1) * limit
            
            # Base query
            base_query = f"""
                FROM {self.table_name} m
                LEFT JOIN users sender ON m.sender_id = sender.id
                LEFT JOIN users receiver ON m.receiver_id = receiver.id
                WHERE (m.sender_id = %s OR m.receiver_id = %s)
            """
            params = [user_id, user_id]
            
            # Message type filter
            if message_type != 'all':
                base_query += " AND m.message_type = %s"
                params.append(message_type)
            
            # Count query
            count_query = f"SELECT COUNT(*) as total {base_query}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # Main query
            query = f"""
                SELECT m.*, 
                       sender.name as sender_name, sender.email as sender_email,
                       receiver.name as receiver_name, receiver.email as receiver_email
                {base_query}
                ORDER BY m.created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            messages = cursor.fetchall()
            
            # Parse attachments
            for message in messages:
                if message['attachments']:
                    message['attachments'] = json.loads(message['attachments'])
                else:
                    message['attachments'] = []
            
            cursor.close()
            
            # Pagination info
            total_pages = (total + limit - 1) // limit
            
            return {
                'messages': messages,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_items': total,
                    'per_page': limit,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
            
        except Exception as e:
            self.logger.error(f"Get user messages error: {e}")
            return {'messages': [], 'pagination': {}}
    
    def get_conversation(self, user1_id: int, user2_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """İki kullanıcı arasındaki konuşmayı getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            query = f"""
                SELECT m.*, 
                       sender.name as sender_name, sender.email as sender_email,
                       receiver.name as receiver_name, receiver.email as receiver_email
                FROM {self.table_name} m
                LEFT JOIN users sender ON m.sender_id = sender.id
                LEFT JOIN users receiver ON m.receiver_id = receiver.id
                WHERE ((m.sender_id = %s AND m.receiver_id = %s) 
                       OR (m.sender_id = %s AND m.receiver_id = %s))
                ORDER BY m.created_at ASC
                LIMIT %s
            """
            
            cursor.execute(query, [user1_id, user2_id, user2_id, user1_id, limit])
            messages = cursor.fetchall()
            
            # Parse attachments
            for message in messages:
                if message['attachments']:
                    message['attachments'] = json.loads(message['attachments'])
                else:
                    message['attachments'] = []
            
            cursor.close()
            return messages
            
        except Exception as e:
            self.logger.error(f"Get conversation error: {e}")
            return []
    
    def mark_as_read(self, message_id: int, user_id: int) -> bool:
        """Mesajı okundu olarak işaretle"""
        try:
            cursor = self.db.cursor()
            
            query = f"""
                UPDATE {self.table_name} 
                SET is_read = TRUE, read_at = %s, updated_at = %s
                WHERE id = %s AND receiver_id = %s
            """
            
            cursor.execute(query, [datetime.now(), datetime.now(), message_id, user_id])
            success = cursor.rowcount > 0
            
            self.db.commit()
            cursor.close()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Mark message as read error: {e}")
            return False
    
    def mark_conversation_as_read(self, user1_id: int, user2_id: int) -> bool:
        """Konuşmayı okundu olarak işaretle"""
        try:
            cursor = self.db.cursor()
            
            query = f"""
                UPDATE {self.table_name} 
                SET is_read = TRUE, read_at = %s, updated_at = %s
                WHERE sender_id = %s AND receiver_id = %s AND is_read = FALSE
            """
            
            cursor.execute(query, [datetime.now(), datetime.now(), user2_id, user1_id])
            
            self.db.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Mark conversation as read error: {e}")
            return False
    
    def get_unread_count(self, user_id: int) -> int:
        """Okunmamış mesaj sayısı"""
        try:
            cursor = self.db.cursor()
            
            query = f"""
                SELECT COUNT(*) FROM {self.table_name} 
                WHERE receiver_id = %s AND is_read = FALSE
            """
            
            cursor.execute(query, [user_id])
            count = cursor.fetchone()[0]
            cursor.close()
            
            return count
            
        except Exception as e:
            self.logger.error(f"Get unread count error: {e}")
            return 0
    
    def get_message_thread(self, message_id: int) -> List[Dict[str, Any]]:
        """Mesaj thread'ini getir (parent-child ilişkisi)"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            # Ana mesajı bul
            cursor.execute(f"SELECT parent_id FROM {self.table_name} WHERE id = %s", [message_id])
            message = cursor.fetchone()
            
            if not message:
                return []
            
            # Root mesaj ID'sini bul
            root_id = message['parent_id'] if message['parent_id'] else message_id
            
            # Thread'deki tüm mesajları getir
            query = f"""
                SELECT m.*, 
                       sender.name as sender_name, sender.email as sender_email,
                       receiver.name as receiver_name, receiver.email as receiver_email
                FROM {self.table_name} m
                LEFT JOIN users sender ON m.sender_id = sender.id
                LEFT JOIN users receiver ON m.receiver_id = receiver.id
                WHERE (m.id = %s OR m.parent_id = %s)
                ORDER BY m.created_at ASC
            """
            
            cursor.execute(query, [root_id, root_id])
            thread_messages = cursor.fetchall()
            
            # Parse attachments
            for msg in thread_messages:
                if msg['attachments']:
                    msg['attachments'] = json.loads(msg['attachments'])
                else:
                    msg['attachments'] = []
            
            cursor.close()
            return thread_messages
            
        except Exception as e:
            self.logger.error(f"Get message thread error: {e}")
            return []
    
    def delete_message(self, message_id: int, user_id: int) -> bool:
        """Mesajı sil (sadece gönderen silebilir)"""
        try:
            cursor = self.db.cursor()
            
            query = f"DELETE FROM {self.table_name} WHERE id = %s AND sender_id = %s"
            cursor.execute(query, [message_id, user_id])
            
            success = cursor.rowcount > 0
            self.db.commit()
            cursor.close()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Delete message error: {e}")
            return False
    
    def get_message_stats(self, user_id: int) -> Dict[str, Any]:
        """Mesaj istatistikleri"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            # Toplam gönderilen
            cursor.execute(f"SELECT COUNT(*) as sent FROM {self.table_name} WHERE sender_id = %s", [user_id])
            sent_count = cursor.fetchone()['sent']
            
            # Toplam alınan
            cursor.execute(f"SELECT COUNT(*) as received FROM {self.table_name} WHERE receiver_id = %s", [user_id])
            received_count = cursor.fetchone()['received']
            
            # Okunmamış
            cursor.execute(f"SELECT COUNT(*) as unread FROM {self.table_name} WHERE receiver_id = %s AND is_read = FALSE", [user_id])
            unread_count = cursor.fetchone()['unread']
            
            # Tür bazında sayılar
            cursor.execute(f"""
                SELECT message_type, COUNT(*) as count
                FROM {self.table_name} 
                WHERE receiver_id = %s
                GROUP BY message_type
            """, [user_id])
            by_type = cursor.fetchall()
            
            cursor.close()
            
            return {
                'sent_count': sent_count,
                'received_count': received_count,
                'unread_count': unread_count,
                'by_type': {item['message_type']: item['count'] for item in by_type}
            }
            
        except Exception as e:
            self.logger.error(f"Get message stats error: {e}")
            return {'sent_count': 0, 'received_count': 0, 'unread_count': 0, 'by_type': {}}
    
    def search_messages(self, user_id: int, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Mesajlarda arama"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            query = f"""
                SELECT m.*, 
                       sender.name as sender_name, sender.email as sender_email,
                       receiver.name as receiver_name, receiver.email as receiver_email
                FROM {self.table_name} m
                LEFT JOIN users sender ON m.sender_id = sender.id
                LEFT JOIN users receiver ON m.receiver_id = receiver.id
                WHERE (m.sender_id = %s OR m.receiver_id = %s)
                AND (m.subject LIKE %s OR m.content LIKE %s)
                ORDER BY m.created_at DESC
                LIMIT %s
            """
            
            search_pattern = f"%{search_term}%"
            cursor.execute(query, [user_id, user_id, search_pattern, search_pattern, limit])
            messages = cursor.fetchall()
            
            # Parse attachments
            for message in messages:
                if message['attachments']:
                    message['attachments'] = json.loads(message['attachments'])
                else:
                    message['attachments'] = []
            
            cursor.close()
            return messages
            
        except Exception as e:
            self.logger.error(f"Search messages error: {e}")
            return []
    
    def cleanup_old_messages(self, days: int = 365) -> int:
        """Eski mesajları temizle"""
        try:
            cursor = self.db.cursor()
            
            query = f"""
                DELETE FROM {self.table_name} 
                WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
                AND message_type != 'system'
            """
            
            cursor.execute(query, [days])
            deleted_count = cursor.rowcount
            
            self.db.commit()
            cursor.close()
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Cleanup old messages error: {e}")
            return 0

# Message türleri
MESSAGE_TYPES = {
    'private': 'Özel Mesaj',
    'support': 'Destek Talebi',
    'system': 'Sistem Mesajı',
    'announcement': 'Duyuru'
}

# Message priority levels
MESSAGE_PRIORITIES = {
    'low': 'Düşük',
    'normal': 'Normal',
    'high': 'Yüksek',
    'urgent': 'Acil'
}