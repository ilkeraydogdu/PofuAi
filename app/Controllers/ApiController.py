"""
API Controller
API endpoint'leri controller'ı
"""
from app.Controllers.BaseController import BaseController
from app.Models.User import User
from app.Models.Post import Post
from core.Services.error_handler import error_handler
import json
import os
import platform
import sys

class ApiController(BaseController):
    """API controller'ı"""
    
    def index(self):
        """API ana sayfası"""
        return self.json_response({
            'message': 'PofuAI API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': [
                '/api/health',
                '/api/version',
                '/api/test',
                '/api/config'
            ]
        })
    
    def test(self):
        """API test endpoint'i"""
        return self.json_response({
            'message': 'API test endpoint',
            'status': 'ok',
            'timestamp': self.get_timestamp()
        })
    
    def health(self):
        """API sağlık durumu"""
        try:
            # Sistem bilgilerini topla
            health_info = {
                'status': 'ok',
                'timestamp': self.get_timestamp(),
                'environment': os.environ.get('FLASK_ENV', 'production'),
                'database_connection': self._check_database_connection(),
                'system': {
                    'python_version': sys.version,
                    'platform': platform.platform(),
                    'memory_usage': self._get_memory_usage(),
                    'cpu_usage': self._get_cpu_usage()
                }
            }
            
            return self.json_response(health_info)
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def version(self):
        """API versiyonu"""
        try:
            version_info = {
                'api_version': '1.0.0',
                'build_date': '2025-07-10',
                'framework_version': 'Flask 2.3.3',
                'supported_endpoints': [
                    '/api/health',
                    '/api/version',
                    '/api/config',
                    '/api/user',
                    '/api/posts',
                    '/api/posts/{id}'
                ]
            }
            
            return self.json_response(version_info)
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def config(self):
        """Genel yapılandırma bilgileri (hassas olmayan)"""
        try:
            # Admin kullanıcı kontrolü
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
                
            if not user.is_admin:
                return self.error_response('Bu endpoint\'e erişim yetkiniz yok', 403)
            
            # Genel yapılandırma bilgilerini topla (hassas bilgiler olmadan!)
            config_info = {
                'app_name': 'PofuAi',
                'debug_mode': os.environ.get('FLASK_DEBUG', '0') == '1',
                'environment': os.environ.get('FLASK_ENV', 'production'),
                'timezone': 'UTC',
                'allowed_upload_types': ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx'],
                'max_upload_size': 5 * 1024 * 1024,  # 5MB
                'pagination': {
                    'default_per_page': 10,
                    'max_per_page': 100
                },
                'features': {
                    'user_registration': True,
                    'email_verification': True,
                    'social_login': True,
                    'api_rate_limiting': True
                }
            }
            
            return self.json_response(config_info)
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def _check_database_connection(self):
        """Veritabanı bağlantısını kontrol et"""
        try:
            # Basit bir sorgu çalıştır
            User.query().select('id').limit(1).execute()
            return True
        except Exception as e:
            self.log('error', f'Veritabanı bağlantı hatası: {str(e)}')
            return False
    
    def _get_memory_usage(self):
        """Bellek kullanımı bilgisi (örnek)"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return {
                'rss': memory_info.rss / (1024 * 1024),  # MB cinsinden
                'vms': memory_info.vms / (1024 * 1024)   # MB cinsinden
            }
        except ImportError:
            return 'psutil kütüphanesi yüklü değil'
        except Exception:
            return 'bilinmiyor'
    
    def _get_cpu_usage(self):
        """CPU kullanımı bilgisi (örnek)"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 'psutil kütüphanesi yüklü değil'
        except Exception:
            return 'bilinmiyor'
    
    def user(self):
        """Mevcut kullanıcı bilgisi"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            return self.json_response(user.to_dict())
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def posts(self):
        """Post listesi"""
        try:
            # Sayfalama parametreleri
            page = int(self.get_input('page', 1))
            per_page = int(self.get_input('per_page', 10))
            search = self.get_input('search', '')
            category = self.get_input('category', '')
            
            # Post'ları getir
            posts = Post.paginate(page, per_page, search=search, category=category)
            
            return self.json_response({
                'posts': posts['data'],
                'pagination': posts['pagination']
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def createPost(self):
        """Post oluştur"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Input'ları al
            data = self.get_all_input()
            data['user_id'] = user.id
            
            # Validation kuralları
            rules = {
                'title': 'required|min:3|max:200',
                'content': 'required|min:10',
                'category': 'required|in:technology,science,health,entertainment'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Post oluştur
            post = Post.create(data)
            
            if not post:
                return self.error_response('Post oluşturulamadı', 500)
            
            # Log
            self.log('info', f'Yeni post oluşturuldu: {post.title}', {
                'user_id': user.id,
                'post_id': post.id
            })
            
            return self.json_response(post.to_dict(), 201)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def post(self, id: int):
        """Post detayı"""
        try:
            post = Post.find(id)
            
            if not post:
                return self.error_response('Post bulunamadı', 404)
            
            # Görüntülenme sayısını artır
            post.increment_views()
            
            return self.json_response(post.to_dict())
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def updatePost(self, id: int):
        """Post güncelle"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            post = Post.find(id)
            
            if not post:
                return self.error_response('Post bulunamadı', 404)
            
            # Yetki kontrolü
            if post.user_id != user.id and not user.is_admin:
                return self.error_response('Bu post\'u düzenleme yetkiniz yok', 403)
            
            # Input'ları al
            data = self.get_all_input()
            
            # Validation kuralları
            rules = {
                'title': 'required|min:3|max:200',
                'content': 'required|min:10',
                'category': 'required|in:technology,science,health,entertainment'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Post'u güncelle
            if post.update(data):
                # Log
                self.log('info', f'Post güncellendi: {post.title}', {
                    'user_id': user.id,
                    'post_id': post.id
                })
                
                return self.json_response(post.to_dict())
            else:
                return self.error_response('Post güncellenemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def deletePost(self, id: int):
        """Post sil"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            post = Post.find(id)
            
            if not post:
                return self.error_response('Post bulunamadı', 404)
            
            # Yetki kontrolü
            if post.user_id != user.id and not user.is_admin:
                return self.error_response('Bu post\'u silme yetkiniz yok', 403)
            
            # Post'u sil
            if post.delete():
                # Log
                self.log('info', f'Post silindi: {post.title}', {
                    'user_id': user.id,
                    'post_id': post.id
                })
                
                return self.json_response({'message': 'Post başarıyla silindi'})
            else:
                return self.error_response('Post silinemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request) 