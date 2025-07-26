#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content Controller

İçerik yönetimi için controller
"""

from app.Controllers.BaseController import BaseController
from core.Services.error_handler import error_handler
from core.Database.connection import get_connection
from flask import request, jsonify, session
import datetime
from typing import Dict, Any

class ContentController(BaseController):
    """İçerik yönetimi controller'ı"""
    
    def __init__(self):
        """Controller'ı başlat"""
        super().__init__()
    
    def index(self):
        """İçerik listesi"""
        try:
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            search = request.args.get('search', '')
            status = request.args.get('status', 'all')
            category = request.args.get('category', 'all')
            
            # İçerikleri getir
            content_data = self._get_content_with_pagination(page, per_page, search, status, category)
            
            data = {
                'title': 'İçerik Yönetimi',
                'content': content_data['content'],
                'pagination': content_data['pagination'],
                'search': search,
                'status': status,
                'category': category,
                'content_stats': self._get_content_stats(),
                'categories': self._get_categories()
            }
            
            return self.view('admin.content.index', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def create(self):
        """Yeni içerik oluştur"""
        try:
            if request.method == 'POST':
                return self._handle_create_content()
            
            data = {
                'title': 'Yeni İçerik Oluştur',
                'categories': self._get_categories(),
                'authors': self._get_authors()
            }
            
            return self.view('admin.content.create', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def edit(self, content_id):
        """İçerik düzenle"""
        try:
            if request.method == 'POST':
                return self._handle_update_content(content_id)
            
            # İçeriği getir
            content = self._get_content_by_id(content_id)
            if not content:
                return self.json_response({
                    'success': False,
                    'message': 'İçerik bulunamadı'
                }, 404)
            
            data = {
                'title': 'İçerik Düzenle',
                'content': content,
                'categories': self._get_categories(),
                'authors': self._get_authors()
            }
            
            return self.view('admin.content.edit', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def delete(self, content_id):
        """İçerik sil"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # İçeriği sil
            cursor.execute("DELETE FROM posts WHERE id = ?", (content_id,))
            conn.commit()
            
            return self.json_response({
                'success': True,
                'message': 'İçerik başarıyla silindi'
            })
            
        except Exception as e:
            return self.json_response({
                'success': False,
                'message': f'İçerik silinirken hata oluştu: {str(e)}'
            }, 500)
    
    def publish(self, content_id):
        """İçeriği yayınla"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # İçeriği yayınla
            cursor.execute("""
                UPDATE posts 
                SET status = 'published', updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (content_id,))
            conn.commit()
            
            return self.json_response({
                'success': True,
                'message': 'İçerik başarıyla yayınlandı'
            })
            
        except Exception as e:
            return self.json_response({
                'success': False,
                'message': f'İçerik yayınlanırken hata oluştu: {str(e)}'
            }, 500)
    
    def unpublish(self, content_id):
        """İçeriği yayından kaldır"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # İçeriği yayından kaldır
            cursor.execute("""
                UPDATE posts 
                SET status = 'draft', updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (content_id,))
            conn.commit()
            
            return self.json_response({
                'success': True,
                'message': 'İçerik yayından kaldırıldı'
            })
            
        except Exception as e:
            return self.json_response({
                'success': False,
                'message': f'İçerik yayından kaldırılırken hata oluştu: {str(e)}'
            }, 500)
    
    def _get_content_with_pagination(self, page, per_page, search, status, category):
        """Sayfalama ile içerikleri getir"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Base query
            where_conditions = []
            params = []
            
            if search:
                where_conditions.append("(p.title LIKE ? OR p.content LIKE ?)")
                params.extend([f"%{search}%", f"%{search}%"])
            
            if status != 'all':
                where_conditions.append("p.status = ?")
                params.append(status)
            
            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Toplam kayıt sayısı
            count_query = f"""
                SELECT COUNT(*) FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                {where_clause}
            """
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()[0]
            
            # Sayfalama hesaplamaları
            total_pages = (total_records + per_page - 1) // per_page
            offset = (page - 1) * per_page
            
            # İçerikleri getir
            content_query = f"""
                SELECT p.id, p.title, p.excerpt, p.status, p.views, p.likes, 
                       p.comments_count, p.created_at, p.updated_at,
                       u.name as author_name
                FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                {where_clause}
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(content_query, params + [per_page, offset])
            content = [
                {
                    'id': row[0],
                    'title': row[1],
                    'excerpt': row[2],
                    'status': row[3],
                    'views': row[4],
                    'likes': row[5],
                    'comments_count': row[6],
                    'created_at': row[7],
                    'updated_at': row[8],
                    'author_name': row[9]
                }
                for row in cursor.fetchall()
            ]
            
            return {
                'content': content,
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
            print(f"Content pagination error: {str(e)}")
            return {
                'content': [],
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
    
    def _get_content_stats(self):
        """İçerik istatistikleri"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Duruma göre içerik sayıları
            cursor.execute("SELECT status, COUNT(*) FROM posts GROUP BY status")
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            stats.update({
                'published': status_counts.get('published', 0),
                'draft': status_counts.get('draft', 0),
                'pending': status_counts.get('pending', 0),
                'archived': status_counts.get('archived', 0)
            })
            
            # Toplam görüntüleme ve beğeni
            cursor.execute("SELECT SUM(views), SUM(likes), SUM(comments_count) FROM posts")
            totals = cursor.fetchone()
            stats.update({
                'total_views': totals[0] or 0,
                'total_likes': totals[1] or 0,
                'total_comments': totals[2] or 0
            })
            
            return stats
            
        except Exception as e:
            print(f"Content stats error: {str(e)}")
            return {}
    
    def _get_categories(self):
        """Kategorileri getir"""
        # Demo kategoriler - gerçek uygulamada veritabanından alınır
        return [
            {'id': 1, 'name': 'Teknoloji', 'slug': 'teknoloji'},
            {'id': 2, 'name': 'Programlama', 'slug': 'programlama'},
            {'id': 3, 'name': 'Veri Bilimi', 'slug': 'veri-bilimi'},
            {'id': 4, 'name': 'Web Geliştirme', 'slug': 'web-gelistirme'},
            {'id': 5, 'name': 'Yapay Zeka', 'slug': 'yapay-zeka'}
        ]
    
    def _get_authors(self):
        """Yazarları getir"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, email FROM users 
                WHERE role IN ('admin', 'editor') AND status = 'active'
                ORDER BY name
            """)
            
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2]
                }
                for row in cursor.fetchall()
            ]
            
        except Exception as e:
            print(f"Authors error: {str(e)}")
            return []
    
    def _get_content_by_id(self, content_id):
        """ID'ye göre içerik getir"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.*, u.name as author_name
                FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                WHERE p.id = ?
            """, (content_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'excerpt': row[3],
                    'status': row[4],
                    'author_id': row[5],
                    'views': row[6],
                    'likes': row[7],
                    'comments_count': row[8],
                    'created_at': row[9],
                    'updated_at': row[10],
                    'author_name': row[11]
                }
            return None
            
        except Exception as e:
            print(f"Get content error: {str(e)}")
            return None
    
    def _handle_create_content(self):
        """Yeni içerik oluşturma işlemi"""
        try:
            data = self._safe_get_input()
            
            # Validation
            if not data.get('title'):
                return self.json_response({
                    'success': False,
                    'message': 'Başlık gereklidir'
                }, 400)
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # İçeriği ekle
            cursor.execute("""
                INSERT INTO posts (title, content, excerpt, status, author_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data.get('title'),
                data.get('content', ''),
                data.get('excerpt', ''),
                data.get('status', 'draft'),
                session.get('user', {}).get('id', 1)
            ))
            
            conn.commit()
            
            return self.json_response({
                'success': True,
                'message': 'İçerik başarıyla oluşturuldu'
            })
            
        except Exception as e:
            return self.json_response({
                'success': False,
                'message': f'İçerik oluşturulurken hata oluştu: {str(e)}'
            }, 500)
    
    def _handle_update_content(self, content_id):
        """İçerik güncelleme işlemi"""
        try:
            data = self._safe_get_input()
            
            # Validation
            if not data.get('title'):
                return self.json_response({
                    'success': False,
                    'message': 'Başlık gereklidir'
                }, 400)
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # İçeriği güncelle
            cursor.execute("""
                UPDATE posts 
                SET title = ?, content = ?, excerpt = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data.get('title'),
                data.get('content', ''),
                data.get('excerpt', ''),
                data.get('status', 'draft'),
                content_id
            ))
            
            conn.commit()
            
            return self.json_response({
                'success': True,
                'message': 'İçerik başarıyla güncellendi'
            })
            
        except Exception as e:
            return self.json_response({
                'success': False,
                'message': f'İçerik güncellenirken hata oluştu: {str(e)}'
            }, 500)