"""
Dev Controller
Development işlemleri controller'ı
"""
from app.Controllers.BaseController import BaseController
from core.Services.error_handler import error_handler
import os
import glob
import psutil
import platform
import sys

class DevController(BaseController):
    """Development controller'ı"""
    
    def test(self):
        """Test sayfası"""
        try:
            user = self.require_role('admin')
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Test verilerini oluştur
            test_data = self._create_test_data()
            
            return self.view('dev.test', {
                'test_data': test_data
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def debug(self):
        """Debug bilgileri"""
        try:
            user = self.require_role('admin')
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Debug bilgilerini topla
            debug_info = self._get_debug_info()
            
            return self.view('dev.debug', {
                'debug_info': debug_info
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def logs(self):
        """Log dosyalarını görüntüle"""
        try:
            user = self.require_role('admin')
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Log dosyalarını listele
            log_files = []
            log_dir = 'storage/Logs'
            if os.path.exists(log_dir):
                # Log dosyalarını bul ve son değiştirilme tarihine göre sırala
                files = glob.glob(os.path.join(log_dir, '*.log'))
                files.sort(key=os.path.getmtime, reverse=True)
                
                for file_path in files:
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    modified_time = os.path.getmtime(file_path)
                    
                    # Dosya içeriğini oku (son 1000 satır)
                    content = ""
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = "".join(f.readlines()[-1000:])
                    except Exception as e:
                        content = f"Dosya okuma hatası: {str(e)}"
                    
                    log_files.append({
                        'name': file_name,
                        'path': file_path,
                        'size': file_size,
                        'size_formatted': self._format_size(file_size),
                        'modified': modified_time,
                        'modified_formatted': self._format_date(modified_time),
                        'content': content
                    })
            
            return self.view('dev.logs', {
                'log_files': log_files
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def clear_cache(self):
        """Cache temizle"""
        try:
            user = self.require_role('admin')
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Cache'i temizle
            from core.Services.cache_service import CacheService
            cache = CacheService()
            cache.clear()
            
            # Log
            self.log('info', 'Cache temizlendi', {
                'admin_id': user.id
            })
            
            return self.json_response({'message': 'Cache başarıyla temizlendi'})
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def warm_cache(self):
        """Cache'i ısıt (ön belleğe al)"""
        try:
            user = self.require_role('admin')
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Cache'i ısıt - sık kullanılan verileri ön belleğe al
            from core.Services.cache_service import CacheService
            cache = CacheService()
            
            # Kullanıcı sayısı
            from app.Models.User import User
            user_count = User.count()
            cache.set('user_count', user_count, 3600)  # 1 saat cache
            
            # Post sayısı
            from app.Models.Post import Post
            post_count = Post.count()
            cache.set('post_count', post_count, 3600)  # 1 saat cache
            
            # Popüler kategoriler
            # categories = Category.popular()
            # cache.set('popular_categories', categories, 3600)
            
            # Popüler postlar
            # popular_posts = Post.popular(5)
            # cache.set('popular_posts', popular_posts, 3600)
            
            # Log
            self.log('info', 'Cache ısıtıldı', {
                'admin_id': user.id
            })
            
            return self.json_response({
                'message': 'Cache başarıyla ısıtıldı',
                'cached_items': [
                    'user_count',
                    'post_count',
                    # 'popular_categories',
                    # 'popular_posts'
                ]
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def clearCache(self):
        """Cache temizle"""
        try:
            user = self.require_role('admin')
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Cache'i temizle
            from core.Services.cache_service import CacheService
            cache = CacheService()
            cache.clear()
            
            # Log
            self.log('info', 'Cache temizlendi', {
                'admin_id': user.id
            })
            
            return self.json_response({'message': 'Cache başarıyla temizlendi'})
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def clearLogs(self):
        """Log dosyalarını temizle"""
        try:
            user = self.require_role('admin')
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Log dosyalarını temizle
            import os
            import glob
            
            log_dir = 'storage/Logs'
            if os.path.exists(log_dir):
                log_files = glob.glob(os.path.join(log_dir, '*.log'))
                for log_file in log_files:
                    try:
                        # Dosyayı temizle (silme, sadece içeriğini temizle)
                        with open(log_file, 'w') as f:
                            f.write('')
                    except Exception as e:
                        self.log('error', f'Log file clear error: {str(e)}')
            
            # Log
            self.log('info', 'Log dosyaları temizlendi', {
                'admin_id': user.id
            })
            
            return self.json_response({'message': 'Log dosyaları başarıyla temizlendi'})
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def _format_size(self, size_bytes):
        """Byte cinsinden boyutu okunabilir formata dönüştür"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0 or unit == 'TB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
    
    def _format_date(self, timestamp):
        """Timestamp'i okunabilir tarih formatına dönüştür"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def _create_test_data(self):
        """Test verilerini oluştur"""
        try:
            from app.Models.User import User
            from app.Models.Post import Post
            
            test_data = {
                'users_created': 0,
                'posts_created': 0,
                'errors': []
            }
            
            # Test kullanıcıları oluştur
            test_users = [
                {
                    'name': 'Test User 1',
                    'email': 'test1@example.com',
                    'password': 'password123',
                    'username': 'testuser1',
                    'role': 'user'
                },
                {
                    'name': 'Test User 2',
                    'email': 'test2@example.com',
                    'password': 'password123',
                    'username': 'testuser2',
                    'role': 'moderator'
                },
                {
                    'name': 'Test Admin',
                    'email': 'admin@example.com',
                    'password': 'password123',
                    'username': 'testadmin',
                    'role': 'admin'
                }
            ]
            
            for user_data in test_users:
                try:
                    # Kullanıcı var mı kontrol et
                    existing_user = User.find_by_email(user_data['email'])
                    if not existing_user:
                        user = User.create_user(user_data)
                        if user:
                            test_data['users_created'] += 1
                        else:
                            test_data['errors'].append(f"Kullanıcı oluşturulamadı: {user_data['email']}")
                except Exception as e:
                    test_data['errors'].append(f"Kullanıcı hatası: {str(e)}")
            
            # Test post'ları oluştur
            test_posts = [
                {
                    'title': 'Test Post 1',
                    'content': 'Bu bir test post\'udur. Lorem ipsum dolor sit amet.',
                    'category': 'technology',
                    'status': 'published'
                },
                {
                    'title': 'Test Post 2',
                    'content': 'Bu ikinci test post\'udur. Consectetur adipiscing elit.',
                    'category': 'science',
                    'status': 'published'
                },
                {
                    'title': 'Test Post 3',
                    'content': 'Bu üçüncü test post\'udur. Sed do eiusmod tempor.',
                    'category': 'health',
                    'status': 'draft'
                }
            ]
            
            # İlk kullanıcıyı bul
            first_user = User.first()
            if first_user:
                for post_data in test_posts:
                    try:
                        post_data['user_id'] = first_user.id
                        post = Post.create(post_data)
                        if post:
                            test_data['posts_created'] += 1
                        else:
                            test_data['errors'].append(f"Post oluşturulamadı: {post_data['title']}")
                    except Exception as e:
                        test_data['errors'].append(f"Post hatası: {str(e)}")
            
            return test_data
            
        except Exception as e:
            return {
                'users_created': 0,
                'posts_created': 0,
                'errors': [f"Genel hata: {str(e)}"]
            }
    
    def _get_debug_info(self):
        """Debug bilgilerini topla"""
        try:
            import sys
            import platform
            import psutil
            
            debug_info = {
                'system': {
                    'platform': platform.platform(),
                    'python_version': sys.version,
                    'architecture': platform.architecture(),
                    'processor': platform.processor()
                },
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                },
                'process': {
                    'pid': os.getpid(),
                    'memory_info': psutil.Process().memory_info()._asdict(),
                    'cpu_percent': psutil.Process().cpu_percent()
                },
                'environment': {
                    'app_env': os.getenv('APP_ENV', 'development'),
                    'debug': self.config.get('app.debug', False),
                    'timezone': self.config.get('app.timezone', 'UTC')
                },
                'database': {
                    'driver': self.config.get('database.driver', 'unknown'),
                    'database': self.config.get('database.database', 'unknown')
                },
                'cache': {
                    'driver': self.config.get('cache.driver', 'unknown')
                },
                'mail': {
                    'driver': self.config.get('mail.driver', 'unknown')
                }
            }
            
            return debug_info
            
        except Exception as e:
            return {
                'error': f"Debug info error: {str(e)}"
            } 