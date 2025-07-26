"""
Home Controller
Ana sayfa controller'ı
"""
from app.Controllers.BaseController import BaseController
from core.Services.error_handler import error_handler
from core.Services.PageService import PageService
from core.Services.ComponentService import ComponentService
import os
import re

class HomeController(BaseController):
    """Ana sayfa controller'ı"""
    
    def __init__(self):
        """Controller'ı başlat"""
        super().__init__()
        self.page_service = PageService()
        self.component_service = ComponentService()
    
    def index(self):
        """Ana sayfa"""
        try:
            # İstatistikleri al
            stats = self._get_stats()
            
            # Son aktiviteleri al
            recent_activities = self._get_recent_activities()
            
            # Popüler içerikleri al
            popular_content = self._get_popular_content()
            
            # API isteği kontrolü - sadece API isteklerine JSON yanıt ver
            if self.is_api_request():
                return self.json_response({
                    'stats': stats,
                    'recent_activities': recent_activities,
                    'popular_content': popular_content
                })
            
            # Normal isteklere dashboard view'ını render et
            data = {
                'stats': stats,
                'recent_activities': recent_activities,
                'popular_content': popular_content,
                'active_menu': 'dashboard',
                'title': 'PofuAi | Dashboard'
            }
            
            return self.page_service.render_page('home/index', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def _get_stats(self):
        """İstatistikleri al"""
        try:
            # Veritabanı olmadan çalışabilmesi için istatistikleri sabit değerlerle doldur
            stats = {
                'total_users': 125,
                'total_posts': 48,
                'active_users': 78,
                'published_posts': 36
            }
            
            return stats
            
        except Exception as e:
            self.log('error', f'Stats error: {str(e)}')
            return {
                'total_users': 0,
                'total_posts': 0,
                'active_users': 0,
                'published_posts': 0
            }
    
    def _get_recent_activities(self):
        """Son aktiviteleri al"""
        try:
            # Demo aktiviteler
            activities = [
                {
                    'type': 'post',
                    'title': 'Lorem ipsum dolor sit amet',
                    'user': 'Admin',
                    'time': '2023-06-26 09:45:00',
                    'url': '/posts/1'
                },
                {
                    'type': 'post',
                    'title': 'Consectetur adipiscing elit',
                    'user': 'Demo User',
                    'time': '2023-06-25 14:30:00',
                    'url': '/posts/2'
                },
                {
                    'type': 'post',
                    'title': 'Sed do eiusmod tempor incididunt',
                    'user': 'Test User',
                    'time': '2023-06-24 11:20:00',
                    'url': '/posts/3'
                }
            ]
            
            return activities
            
        except Exception as e:
            self.log('error', f'Recent activities error: {str(e)}')
            return []
    
    def _get_popular_content(self):
        """Popüler içerikleri al"""
        try:
            # Demo içerikler
            content = [
                {
                    'id': 1,
                    'title': 'En Popüler İçerik',
                    'excerpt': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit...',
                    'views': 1250,
                    'likes': 84,
                    'user': 'Admin',
                    'url': '/posts/1'
                },
                {
                    'id': 2,
                    'title': 'İkinci Popüler İçerik',
                    'excerpt': 'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua...',
                    'views': 950,
                    'likes': 67,
                    'user': 'Demo User',
                    'url': '/posts/2'
                },
                {
                    'id': 3,
                    'title': 'Üçüncü Popüler İçerik',
                    'excerpt': 'Ut enim ad minim veniam, quis nostrud exercitation ullamco...',
                    'views': 820,
                    'likes': 52,
                    'user': 'Test User',
                    'url': '/posts/3'
                }
            ]
            
            return content
            
        except Exception as e:
            self.log('error', f'Popular content error: {str(e)}')
            return []