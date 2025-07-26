#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Search Controller

Arama işlemleri için controller
"""

from app.Controllers.BaseController import BaseController
from core.Services.error_handler import error_handler
from core.Database.connection import get_connection
from flask import request, jsonify
import datetime
from typing import Dict, Any, List

class SearchController(BaseController):
    """Arama controller'ı"""
    
    def __init__(self):
        """Controller'ı başlat"""
        super().__init__()
    
    def search(self):
        """Genel arama"""
        try:
            query = request.args.get('q', '').strip()
            search_type = request.args.get('type', 'all')  # all, users, content, comments
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            
            if not query:
                return self.json_response({
                    'success': False,
                    'message': 'Arama terimi gereklidir'
                }, 400)
            
            results = {}
            
            if search_type in ['all', 'users']:
                results['users'] = self._search_users(query, page if search_type == 'users' else 1, per_page)
            
            if search_type in ['all', 'content']:
                results['content'] = self._search_content(query, page if search_type == 'content' else 1, per_page)
            
            if search_type in ['all', 'comments']:
                results['comments'] = self._search_comments(query, page if search_type == 'comments' else 1, per_page)
            
            # Genel arama için toplam sonuç sayısını hesapla
            total_results = sum(
                result.get('pagination', {}).get('total_records', 0) 
                for result in results.values()
            )
            
            return self.json_response({
                'success': True,
                'query': query,
                'search_type': search_type,
                'total_results': total_results,
                'results': results
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def suggestions(self):
        """Arama önerileri"""
        try:
            query = request.args.get('q', '').strip()
            limit = int(request.args.get('limit', 10))
            
            if len(query) < 2:
                return self.json_response({
                    'success': True,
                    'suggestions': []
                })
            
            suggestions = []
            
            # Kullanıcı önerileri
            user_suggestions = self._get_user_suggestions(query, limit // 3)
            suggestions.extend([
                {
                    'type': 'user',
                    'title': suggestion['name'],
                    'subtitle': suggestion['email'],
                    'url': f'/admin/users/{suggestion["id"]}'
                }
                for suggestion in user_suggestions
            ])
            
            # İçerik önerileri
            content_suggestions = self._get_content_suggestions(query, limit // 3)
            suggestions.extend([
                {
                    'type': 'content',
                    'title': suggestion['title'],
                    'subtitle': f'Yazar: {suggestion["author_name"]}',
                    'url': f'/admin/content/{suggestion["id"]}/edit'
                }
                for suggestion in content_suggestions
            ])
            
            # Sistem önerileri
            system_suggestions = self._get_system_suggestions(query)
            suggestions.extend(system_suggestions)
            
            return self.json_response({
                'success': True,
                'suggestions': suggestions[:limit]
            })
            
        except Exception as e:
            return self.json_response({
                'success': False,
                'message': f'Öneriler alınırken hata oluştu: {str(e)}'
            }, 500)
    
    def _search_users(self, query, page, per_page):
        """Kullanıcı araması"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Toplam kayıt sayısı
            count_query = """
                SELECT COUNT(*) FROM users 
                WHERE name LIKE ? OR email LIKE ? OR username LIKE ?
            """
            search_term = f"%{query}%"
            cursor.execute(count_query, (search_term, search_term, search_term))
            total_records = cursor.fetchone()[0]
            
            # Sayfalama hesaplamaları
            total_pages = (total_records + per_page - 1) // per_page
            offset = (page - 1) * per_page
            
            # Kullanıcıları getir
            users_query = """
                SELECT id, name, email, username, role, status, created_at
                FROM users 
                WHERE name LIKE ? OR email LIKE ? OR username LIKE ?
                ORDER BY name
                LIMIT ? OFFSET ?
            """
            cursor.execute(users_query, (search_term, search_term, search_term, per_page, offset))
            users = [
                {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'username': row[3],
                    'role': row[4],
                    'status': row[5],
                    'created_at': row[6]
                }
                for row in cursor.fetchall()
            ]
            
            return {
                'users': users,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_records': total_records,
                    'per_page': per_page,
                    'has_prev': page > 1,
                    'has_next': page < total_pages
                }
            }
            
        except Exception as e:
            print(f"User search error: {str(e)}")
            return {'users': [], 'pagination': {'total_records': 0}}
    
    def _search_content(self, query, page, per_page):
        """İçerik araması"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Toplam kayıt sayısı
            count_query = """
                SELECT COUNT(*) FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                WHERE p.title LIKE ? OR p.content LIKE ? OR p.excerpt LIKE ?
            """
            search_term = f"%{query}%"
            cursor.execute(count_query, (search_term, search_term, search_term))
            total_records = cursor.fetchone()[0]
            
            # Sayfalama hesaplamaları
            total_pages = (total_records + per_page - 1) // per_page
            offset = (page - 1) * per_page
            
            # İçerikleri getir
            content_query = """
                SELECT p.id, p.title, p.excerpt, p.status, p.views, p.likes,
                       p.created_at, u.name as author_name
                FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                WHERE p.title LIKE ? OR p.content LIKE ? OR p.excerpt LIKE ?
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(content_query, (search_term, search_term, search_term, per_page, offset))
            content = [
                {
                    'id': row[0],
                    'title': row[1],
                    'excerpt': row[2],
                    'status': row[3],
                    'views': row[4],
                    'likes': row[5],
                    'created_at': row[6],
                    'author_name': row[7]
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
                    'has_next': page < total_pages
                }
            }
            
        except Exception as e:
            print(f"Content search error: {str(e)}")
            return {'content': [], 'pagination': {'total_records': 0}}
    
    def _search_comments(self, query, page, per_page):
        """Yorum araması"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Toplam kayıt sayısı
            count_query = """
                SELECT COUNT(*) FROM comments c
                LEFT JOIN users u ON c.user_id = u.id
                LEFT JOIN posts p ON c.post_id = p.id
                WHERE c.content LIKE ?
            """
            search_term = f"%{query}%"
            cursor.execute(count_query, (search_term,))
            total_records = cursor.fetchone()[0]
            
            # Sayfalama hesaplamaları
            total_pages = (total_records + per_page - 1) // per_page
            offset = (page - 1) * per_page
            
            # Yorumları getir
            comments_query = """
                SELECT c.id, c.content, c.status, c.created_at,
                       u.name as user_name, p.title as post_title
                FROM comments c
                LEFT JOIN users u ON c.user_id = u.id
                LEFT JOIN posts p ON c.post_id = p.id
                WHERE c.content LIKE ?
                ORDER BY c.created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(comments_query, (search_term, per_page, offset))
            comments = [
                {
                    'id': row[0],
                    'content': row[1],
                    'status': row[2],
                    'created_at': row[3],
                    'user_name': row[4],
                    'post_title': row[5]
                }
                for row in cursor.fetchall()
            ]
            
            return {
                'comments': comments,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_records': total_records,
                    'per_page': per_page,
                    'has_prev': page > 1,
                    'has_next': page < total_pages
                }
            }
            
        except Exception as e:
            print(f"Comments search error: {str(e)}")
            return {'comments': [], 'pagination': {'total_records': 0}}
    
    def _get_user_suggestions(self, query, limit):
        """Kullanıcı önerileri"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT id, name, email FROM users 
                WHERE name LIKE ? OR email LIKE ? OR username LIKE ?
                ORDER BY name
                LIMIT ?
            """, (search_term, search_term, search_term, limit))
            
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2]
                }
                for row in cursor.fetchall()
            ]
            
        except Exception as e:
            print(f"User suggestions error: {str(e)}")
            return []
    
    def _get_content_suggestions(self, query, limit):
        """İçerik önerileri"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT p.id, p.title, u.name as author_name
                FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                WHERE p.title LIKE ? OR p.content LIKE ?
                ORDER BY p.title
                LIMIT ?
            """, (search_term, search_term, limit))
            
            return [
                {
                    'id': row[0],
                    'title': row[1],
                    'author_name': row[2]
                }
                for row in cursor.fetchall()
            ]
            
        except Exception as e:
            print(f"Content suggestions error: {str(e)}")
            return []
    
    def _get_system_suggestions(self, query):
        """Sistem önerileri"""
        system_pages = [
            {'title': 'Dashboard', 'url': '/dashboard', 'keywords': ['dashboard', 'anasayfa', 'ana sayfa', 'home']},
            {'title': 'Kullanıcı Yönetimi', 'url': '/admin/users', 'keywords': ['kullanıcı', 'user', 'users', 'yönetim']},
            {'title': 'İçerik Yönetimi', 'url': '/admin/content', 'keywords': ['içerik', 'content', 'makale', 'post']},
            {'title': 'Sistem Ayarları', 'url': '/admin/settings', 'keywords': ['ayar', 'settings', 'config', 'yapılandırma']},
            {'title': 'Bildirimler', 'url': '/notifications', 'keywords': ['bildirim', 'notification', 'alert']},
        ]
        
        suggestions = []
        query_lower = query.lower()
        
        for page in system_pages:
            if (query_lower in page['title'].lower() or 
                any(keyword in query_lower for keyword in page['keywords'])):
                suggestions.append({
                    'type': 'system',
                    'title': page['title'],
                    'subtitle': 'Sistem Sayfası',
                    'url': page['url']
                })
        
        return suggestions