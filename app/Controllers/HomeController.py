"""
Home Controller
Ana sayfa controller'ı
"""
from app.Controllers.BaseController import BaseController
from core.Services.error_handler import error_handler
from app.Models.User import User
from core.Database.connection import get_connection
import os
import re
import datetime
from flask import session, render_template

class HomeController(BaseController):
    """Ana sayfa controller'ı"""
    
    def __init__(self):
        """Controller'ı başlat"""
        super().__init__()
    
    def index(self):
        """Ana sayfa"""
        try:
            # İstatistikleri al
            stats = self._get_stats()
            
            # Son aktiviteleri al
            recent_activities = self._get_recent_activities()
            
            # Popüler içerikleri al
            popular_content = self._get_popular_content()
            
            # Sistem bilgilerini al
            system_info = self._get_system_info()
            
            # Kullanıcı aktivitelerini al
            user_activities = self._get_user_activities()
            
            # API isteği kontrolü - sadece API isteklerine JSON yanıt ver
            if self.is_api_request():
                return self.json_response({
                    'stats': stats,
                    'recent_activities': recent_activities,
                    'popular_content': popular_content,
                    'system_info': system_info,
                    'user_activities': user_activities
                })
            
            # Normal isteklere dashboard view'ını render et
            data = {
                'stats': stats,
                'recent_activities': recent_activities,
                'popular_content': popular_content,
                'system_info': system_info,
                'user_activities': user_activities,
                'active_menu': 'dashboard',
                'title': 'PofuAi | Dashboard',
                'current_user': session.get('user', {})
            }
            
            return render_template('home/index.html', **data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def _get_stats(self):
        """İstatistikleri al"""
        try:
            # Gerçek veritabanı verilerini al
            conn = get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Toplam kullanıcı sayısı
            cursor.execute("SELECT COUNT(*) FROM users")
            result = cursor.fetchone()
            stats['total_users'] = result[0] if result else 0
            
            # Aktif kullanıcı sayısı (son 30 gün içinde giriş yapmış)
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE last_login >= datetime('now', '-30 days')
            """)
            result = cursor.fetchone()
            stats['active_users'] = result[0] if result else 0
            
            # Bugün kayıt olan kullanıcılar
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE DATE(created_at) = DATE('now')
            """)
            result = cursor.fetchone()
            stats['new_users_today'] = result[0] if result else 0
            
            # Bu ay kayıt olan kullanıcılar
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
            """)
            result = cursor.fetchone()
            stats['new_users_month'] = result[0] if result else 0
            
            conn.close()
            
            # Ek istatistikler (demo veriler)
            stats.update({
                'total_posts': 48,
                'published_posts': 36,
                'pending_posts': 12,
                'total_views': 15420,
                'bounce_rate': 35.2,
                'avg_session_duration': '4:32'
            })
            
            return stats
            
        except Exception as e:
            self.log('error', f'Stats error: {str(e)}')
            return {
                'total_users': 0,
                'total_posts': 0,
                'active_users': 0,
                'published_posts': 0,
                'new_users_today': 0,
                'new_users_month': 0,
                'pending_posts': 0,
                'total_views': 0,
                'bounce_rate': 0,
                'avg_session_duration': '0:00'
            }
    
    def _get_recent_activities(self):
        """Son aktiviteleri al"""
        try:
            # Demo aktiviteler - gerçek bir uygulamada veritabanından alınır
            activities = [
                {
                    'type': 'user_register',
                    'title': 'Yeni kullanıcı kaydı',
                    'user': 'john.doe@example.com',
                    'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'icon': 'person_add',
                    'color': 'success'
                },
                {
                    'type': 'login',
                    'title': 'Kullanıcı girişi',
                    'user': 'admin@pofuai.com',
                    'time': (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S'),
                    'icon': 'login',
                    'color': 'info'
                },
                {
                    'type': 'post_create',
                    'title': 'Yeni içerik oluşturuldu',
                    'user': 'editor@pofuai.com',
                    'time': (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
                    'icon': 'article',
                    'color': 'primary'
                },
                {
                    'type': 'system',
                    'title': 'Sistem yedeklemesi tamamlandı',
                    'user': 'System',
                    'time': (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
                    'icon': 'backup',
                    'color': 'warning'
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
                    'title': 'PofuAi ile Yapay Zeka Entegrasyonu',
                    'excerpt': 'Modern web uygulamalarında yapay zeka teknolojilerinin nasıl entegre edileceğini öğrenin...',
                    'views': 2150,
                    'likes': 184,
                    'comments': 23,
                    'user': 'AI Uzmanı',
                    'category': 'Teknoloji',
                    'published_at': '2024-01-15',
                    'url': '/posts/1'
                },
                {
                    'id': 2,
                    'title': 'Flask ile Modern Web Geliştirme',
                    'excerpt': 'Flask framework kullanarak modern, ölçeklenebilir web uygulamaları geliştirme rehberi...',
                    'views': 1850,
                    'likes': 156,
                    'comments': 31,
                    'user': 'Web Developer',
                    'category': 'Programlama',
                    'published_at': '2024-01-12',
                    'url': '/posts/2'
                },
                {
                    'id': 3,
                    'title': 'Veri Analizi ve Görselleştirme',
                    'excerpt': 'Python ve modern araçlar kullanarak veri analizi ve görselleştirme teknikleri...',
                    'views': 1420,
                    'likes': 98,
                    'comments': 17,
                    'user': 'Data Scientist',
                    'category': 'Veri Bilimi',
                    'published_at': '2024-01-10',
                    'url': '/posts/3'
                }
            ]
            
            return content
            
        except Exception as e:
            self.log('error', f'Popular content error: {str(e)}')
            return []
    
    def _get_system_info(self):
        """Sistem bilgilerini al"""
        try:
            import psutil
            import platform
            
            # CPU kullanımı
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # RAM kullanımı
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = round(memory.used / (1024**3), 2)  # GB
            memory_total = round(memory.total / (1024**3), 2)  # GB
            
            # Disk kullanımı
            disk = psutil.disk_usage('/')
            disk_percent = round((disk.used / disk.total) * 100, 1)
            disk_used = round(disk.used / (1024**3), 2)  # GB
            disk_total = round(disk.total / (1024**3), 2)  # GB
            
            system_info = {
                'platform': platform.system(),
                'platform_version': platform.release(),
                'python_version': platform.python_version(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_used': memory_used,
                'memory_total': memory_total,
                'disk_percent': disk_percent,
                'disk_used': disk_used,
                'disk_total': disk_total,
                'uptime': self._get_uptime()
            }
            
            return system_info
            
        except Exception as e:
            self.log('error', f'System info error: {str(e)}')
            return {
                'platform': 'Unknown',
                'platform_version': 'Unknown',
                'python_version': '3.x',
                'cpu_percent': 0,
                'memory_percent': 0,
                'memory_used': 0,
                'memory_total': 0,
                'disk_percent': 0,
                'disk_used': 0,
                'disk_total': 0,
                'uptime': '0 gün'
            }
    
    def _get_uptime(self):
        """Sistem çalışma süresini al"""
        try:
            import psutil
            boot_time = psutil.boot_time()
            current_time = datetime.datetime.now().timestamp()
            uptime_seconds = current_time - boot_time
            uptime_days = int(uptime_seconds // 86400)
            uptime_hours = int((uptime_seconds % 86400) // 3600)
            uptime_minutes = int((uptime_seconds % 3600) // 60)
            
            if uptime_days > 0:
                return f"{uptime_days} gün, {uptime_hours} saat"
            elif uptime_hours > 0:
                return f"{uptime_hours} saat, {uptime_minutes} dakika"
            else:
                return f"{uptime_minutes} dakika"
                
        except Exception:
            return "Bilinmiyor"
    
    def _get_user_activities(self):
        """Kullanıcı aktivite grafiği için veri"""
        try:
            # Son 7 günün aktivitelerini simüle et
            activities = []
            for i in range(7):
                date = datetime.datetime.now() - datetime.timedelta(days=i)
                activities.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'day': date.strftime('%a'),
                    'logins': 15 + (i * 3),
                    'registrations': 2 + i,
                    'posts': 5 + (i * 2)
                })
            
            return list(reversed(activities))
            
        except Exception as e:
            self.log('error', f'User activities error: {str(e)}')
            return []