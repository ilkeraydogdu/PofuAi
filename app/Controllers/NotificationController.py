#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Controller

Bildirim yönetimi için controller
"""

from app.Controllers.BaseController import BaseController
from core.Services.error_handler import error_handler
from core.Database.connection import get_connection
from flask import request, jsonify, session
import datetime
from typing import Dict, Any, List

class NotificationController(BaseController):
    """Bildirim yönetimi controller'ı"""
    
    def __init__(self):
        """Controller'ı başlat"""
        super().__init__()
    
    def index(self):
        """Bildirim listesi"""
        try:
            user_id = session.get('user', {}).get('id')
            if not user_id:
                return self.json_response({
                    'success': False,
                    'message': 'Oturum bulunamadı'
                }, 401)
            
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            status = request.args.get('status', 'all')  # all, read, unread
            
            # Bildirimleri getir
            notifications_data = self._get_notifications_with_pagination(user_id, page, per_page, status)
            
            data = {
                'notifications': notifications_data['notifications'],
                'pagination': notifications_data['pagination'],
                'status': status,
                'unread_count': self._get_unread_count(user_id)
            }
            
            return self.json_response({
                'success': True,
                'data': data
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def mark_as_read(self, notification_id):
        """Bildirimi okundu olarak işaretle"""
        try:
            user_id = session.get('user', {}).get('id')
            if not user_id:
                return self.json_response({
                    'success': False,
                    'message': 'Oturum bulunamadı'
                }, 401)
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Bildirimi okundu olarak işaretle
            cursor.execute("""
                UPDATE notifications 
                SET is_read = 1, read_at = CURRENT_TIMESTAMP 
                WHERE id = ? AND user_id = ?
            """, (notification_id, user_id))
            
            conn.commit()
            
            return self.json_response({
                'success': True,
                'message': 'Bildirim okundu olarak işaretlendi'
            })
            
        except Exception as e:
            return self.json_response({
                'success': False,
                'message': f'Bildirim güncellenirken hata oluştu: {str(e)}'
            }, 500)
    
    def mark_all_as_read(self):
        """Tüm bildirimleri okundu olarak işaretle"""
        try:
            user_id = session.get('user', {}).get('id')
            if not user_id:
                return self.json_response({
                    'success': False,
                    'message': 'Oturum bulunamadı'
                }, 401)
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Tüm bildirimleri okundu olarak işaretle
            cursor.execute("""
                UPDATE notifications 
                SET is_read = 1, read_at = CURRENT_TIMESTAMP 
                WHERE user_id = ? AND is_read = 0
            """, (user_id,))
            
            conn.commit()
            
            return self.json_response({
                'success': True,
                'message': 'Tüm bildirimler okundu olarak işaretlendi'
            })
            
        except Exception as e:
            return self.json_response({
                'success': False,
                'message': f'Bildirimler güncellenirken hata oluştu: {str(e)}'
            }, 500)
    
    def delete(self, notification_id):
        """Bildirimi sil"""
        try:
            user_id = session.get('user', {}).get('id')
            if not user_id:
                return self.json_response({
                    'success': False,
                    'message': 'Oturum bulunamadı'
                }, 401)
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Bildirimi sil
            cursor.execute("""
                DELETE FROM notifications 
                WHERE id = ? AND user_id = ?
            """, (notification_id, user_id))
            
            conn.commit()
            
            return self.json_response({
                'success': True,
                'message': 'Bildirim başarıyla silindi'
            })
            
        except Exception as e:
            return self.json_response({
                'success': False,
                'message': f'Bildirim silinirken hata oluştu: {str(e)}'
            }, 500)
    
    def get_unread_count(self):
        """Okunmamış bildirim sayısını getir"""
        try:
            user_id = session.get('user', {}).get('id')
            if not user_id:
                return self.json_response({
                    'success': False,
                    'message': 'Oturum bulunamadı'
                }, 401)
            
            count = self._get_unread_count(user_id)
            
            return self.json_response({
                'success': True,
                'count': count
            })
            
        except Exception as e:
            return self.json_response({
                'success': False,
                'message': f'Bildirim sayısı alınırken hata oluştu: {str(e)}'
            }, 500)
    
    def create_system_notification(self, title: str, message: str, notification_type: str = 'info', user_ids: List[int] = None):
        """Sistem bildirimi oluştur"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Eğer user_ids belirtilmemişse, tüm aktif kullanıcılara gönder
            if user_ids is None:
                cursor.execute("SELECT id FROM users WHERE status = 'active'")
                user_ids = [row[0] for row in cursor.fetchall()]
            
            # Her kullanıcı için bildirim oluştur
            for user_id in user_ids:
                cursor.execute("""
                    INSERT INTO notifications (user_id, title, message, type, is_read, created_at)
                    VALUES (?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
                """, (user_id, title, message, notification_type))
            
            conn.commit()
            
            return {
                'success': True,
                'message': f'{len(user_ids)} kullanıcıya bildirim gönderildi'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Sistem bildirimi oluşturulurken hata oluştu: {str(e)}'
            }
    
    def _get_notifications_with_pagination(self, user_id, page, per_page, status):
        """Sayfalama ile bildirimleri getir"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Base query
            where_conditions = ["user_id = ?"]
            params = [user_id]
            
            if status == 'read':
                where_conditions.append("is_read = 1")
            elif status == 'unread':
                where_conditions.append("is_read = 0")
            
            where_clause = " WHERE " + " AND ".join(where_conditions)
            
            # Toplam kayıt sayısı
            count_query = f"SELECT COUNT(*) FROM notifications{where_clause}"
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()[0]
            
            # Sayfalama hesaplamaları
            total_pages = (total_records + per_page - 1) // per_page
            offset = (page - 1) * per_page
            
            # Bildirimleri getir
            notifications_query = f"""
                SELECT id, title, message, type, is_read, created_at, read_at
                FROM notifications{where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(notifications_query, params + [per_page, offset])
            notifications = [
                {
                    'id': row[0],
                    'title': row[1],
                    'message': row[2],
                    'type': row[3],
                    'is_read': bool(row[4]),
                    'created_at': row[5],
                    'read_at': row[6],
                    'time_ago': self._get_time_ago(row[5])
                }
                for row in cursor.fetchall()
            ]
            
            return {
                'notifications': notifications,
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
            print(f"Notifications pagination error: {str(e)}")
            return {
                'notifications': [],
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
    
    def _get_unread_count(self, user_id):
        """Okunmamış bildirim sayısını getir"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM notifications 
                WHERE user_id = ? AND is_read = 0
            """, (user_id,))
            
            return cursor.fetchone()[0]
            
        except Exception as e:
            print(f"Unread count error: {str(e)}")
            return 0
    
    def _get_time_ago(self, created_at):
        """Zaman farkını hesapla"""
        try:
            if isinstance(created_at, str):
                created_time = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_time = created_at
            
            now = datetime.datetime.now()
            diff = now - created_time
            
            if diff.days > 0:
                return f"{diff.days} gün önce"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} saat önce"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} dakika önce"
            else:
                return "Az önce"
                
        except Exception:
            return "Bilinmiyor"