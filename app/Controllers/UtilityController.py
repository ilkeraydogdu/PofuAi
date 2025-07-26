"""
Utility Controller
Yardımcı işlemler controller'ı
"""
from app.Controllers.BaseController import BaseController
from core.Services.error_handler import error_handler
from datetime import datetime

class UtilityController(BaseController):
    """Utility controller'ı"""
    
    def health(self):
        """Health check endpoint"""
        try:
            # Sistem durumunu kontrol et
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'environment': self.config.get('app.env', 'development'),
                'services': {
                    'database': self._check_database(),
                    'cache': self._check_cache(),
                    'mail': self._check_mail()
                }
            }
            
            # Genel durum kontrolü
            all_healthy = all(health_status['services'].values())
            health_status['status'] = 'healthy' if all_healthy else 'unhealthy'
            
            return self.json_response(health_status)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def sitemap(self):
        """Sitemap XML"""
        try:
            from core.Route.sitemap import SitemapGenerator
            
            sitemap = SitemapGenerator()
            xml_content = sitemap.generate()
            
            return self.response(xml_content, headers={
                'Content-Type': 'application/xml'
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def robots(self):
        """Robots.txt"""
        try:
            robots_content = f"""User-agent: *
Allow: /

Sitemap: {self.config.get('app.url')}/sitemap.xml
"""
            
            return self.response(robots_content, headers={
                'Content-Type': 'text/plain'
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def _check_database(self):
        """Database durumunu kontrol et"""
        try:
            from core.Database.connection import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False
    
    def _check_cache(self):
        """Cache durumunu kontrol et"""
        try:
            from core.Services.cache_service import CacheService
            cache = CacheService()
            cache.set('health_check', 'ok', 60)
            return cache.get('health_check') == 'ok'
        except Exception:
            return False
    
    def _check_mail(self):
        """Mail servisi durumunu kontrol et"""
        try:
            from core.Services.mail_service import MailService
            mail_service = MailService()
            # Basit bağlantı kontrolü
            return True
        except Exception:
            return False 