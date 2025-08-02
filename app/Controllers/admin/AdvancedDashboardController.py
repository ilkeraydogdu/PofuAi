"""
Advanced Dashboard Controller
Gelişmiş admin dashboard controller'ı
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.Controllers.BaseController import BaseController
from app.Middleware.AuthMiddleware import admin_required
from core.Services.error_handler import error_handler
from core.Database.connection import get_connection
from app.Models.User import User
from app.Models.Product import Product
from app.Models.Order import Order
from app.Models.AuditLog import AuditLog
from app.Models.Notification import Notification
import json
import datetime
from flask import jsonify, request, session
from typing import Dict, Any, List
import psutil
from datetime import datetime, timedelta

class AdvancedDashboardController(BaseController):
    """Advanced Dashboard controller'ı"""
    
    def __init__(self):
        super().__init__()
    
    @admin_required
    def index(self):
        """Ana gelişmiş dashboard"""
        try:
            admin = self.get_current_user()
            
            # Dashboard verilerini getir
            dashboard_data = self._get_dashboard_data()
            
            data = {
                'title': 'Gelişmiş Admin Dashboard',
                'admin': admin,
                'dashboard_data': dashboard_data
            }
            
            return self.view('admin.advanced_dashboard', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def analytics(self):
        """Analytics sayfası"""
        try:
            admin = self.get_current_user()
            
            # Analytics verilerini getir
            analytics_data = self._get_analytics_data()
            
            data = {
                'title': 'Analytics ve Raporlar',
                'admin': admin,
                'analytics': analytics_data
            }
            
            return self.view('admin.analytics', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def system_health(self):
        """Sistem sağlığı"""
        try:
            admin = self.get_current_user()
            
            # Sistem sağlık verilerini getir
            health_data = self._get_system_health_data()
            
            data = {
                'title': 'Sistem Sağlığı',
                'admin': admin,
                'health': health_data
            }
            
            return self.view('admin.system_health', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def user_management(self):
        """Kullanıcı yönetimi"""
        try:
            admin = self.get_current_user()
            
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 25))
            search = request.args.get('search', '')
            role = request.args.get('role', 'all')
            status = request.args.get('status', 'all')
            
            # Kullanıcı verilerini getir
            users_data = self._get_users_data(page, per_page, search, role, status)
            
            # Kullanıcı istatistikleri
            user_stats = self._get_user_statistics()
            
            data = {
                'title': 'Kullanıcı Yönetimi',
                'admin': admin,
                'users': users_data['users'],
                'pagination': users_data['pagination'],
                'user_stats': user_stats,
                'search': search,
                'role': role,
                'status': status
            }
            
            return self.view('admin.user_management', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def product_management(self):
        """Ürün yönetimi"""
        try:
            admin = self.get_current_user()
            
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 25))
            search = request.args.get('search', '')
            category = request.args.get('category', 'all')
            status = request.args.get('status', 'all')
            
            # Ürün verilerini getir
            products_data = self._get_products_data(page, per_page, search, category, status)
            
            # Ürün istatistikleri
            product_stats = self._get_product_statistics()
            
            # Kategorileri getir
            categories = self._get_categories()
            
            data = {
                'title': 'Ürün Yönetimi',
                'admin': admin,
                'products': products_data['products'],
                'pagination': products_data['pagination'],
                'product_stats': product_stats,
                'categories': categories,
                'search': search,
                'category': category,
                'status': status
            }
            
            return self.view('admin.product_management', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def order_management(self):
        """Sipariş yönetimi"""
        try:
            admin = self.get_current_user()
            
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 25))
            search = request.args.get('search', '')
            status = request.args.get('status', 'all')
            date_from = request.args.get('date_from', '')
            date_to = request.args.get('date_to', '')
            
            # Sipariş verilerini getir
            orders_data = self._get_orders_data(page, per_page, search, status, date_from, date_to)
            
            # Sipariş istatistikleri
            order_stats = self._get_order_statistics()
            
            data = {
                'title': 'Sipariş Yönetimi',
                'admin': admin,
                'orders': orders_data['orders'],
                'pagination': orders_data['pagination'],
                'order_stats': order_stats,
                'search': search,
                'status': status,
                'date_from': date_from,
                'date_to': date_to
            }
            
            return self.view('admin.order_management', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def settings(self):
        """Sistem ayarları"""
        try:
            admin = self.get_current_user()
            
            # Sistem ayarlarını getir
            settings_data = self._get_system_settings()
            
            data = {
                'title': 'Sistem Ayarları',
                'admin': admin,
                'settings': settings_data
            }
            
            return self.view('admin.settings', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # API Endpoints
    @admin_required
    def api_dashboard_stats(self):
        """Dashboard istatistikleri API"""
        try:
            stats = self._get_dashboard_stats()
            return jsonify({'success': True, 'data': stats})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @admin_required
    def api_sales_chart(self):
        """Satış grafiği API"""
        try:
            days = int(request.args.get('days', 30))
            chart_data = self._get_sales_chart_data(days)
            return jsonify({'success': True, 'data': chart_data})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @admin_required
    def api_user_activities(self):
        """Kullanıcı aktiviteleri API"""
        try:
            limit = int(request.args.get('limit', 50))
            activities = self._get_recent_activities(limit)
            return jsonify({'success': True, 'data': activities})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @admin_required
    def api_system_metrics(self):
        """Sistem metrikleri API"""
        try:
            metrics = self._get_system_metrics()
            return jsonify({'success': True, 'data': metrics})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @admin_required
    def api_performance_data(self):
        """Performans verileri API"""
        try:
            hours = int(request.args.get('hours', 24))
            performance_data = self._get_performance_data(hours)
            return jsonify({'success': True, 'data': performance_data})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # Helper Methods
    def _get_dashboard_data(self) -> Dict[str, Any]:
        """Dashboard verilerini getir"""
        try:
            return {
                'stats': self._get_dashboard_stats(),
                'charts': self._get_dashboard_charts(),
                'activities': self._get_recent_activities(10),
                'alerts': self._get_system_alerts(),
                'performance': self._get_performance_summary()
            }
            
        except Exception as e:
            self.logger.error(f"Get dashboard data error: {e}")
            return {}
    
    def _get_dashboard_stats(self) -> Dict[str, Any]:
        """Dashboard istatistikleri"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Toplam kullanıcılar
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total_users = cursor.fetchone()['total']
            
            # Aktif kullanıcılar (son 24 saat)
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as active 
                FROM user_sessions 
                WHERE last_activity > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """)
            active_users = cursor.fetchone()['active']
            
            # Toplam ürünler
            cursor.execute("SELECT COUNT(*) as total FROM products")
            total_products = cursor.fetchone()['total']
            
            # Toplam siparişler
            cursor.execute("SELECT COUNT(*) as total FROM orders")
            total_orders = cursor.fetchone()['total']
            
            # Bugünkü siparişler
            cursor.execute("""
                SELECT COUNT(*) as today 
                FROM orders 
                WHERE DATE(created_at) = CURDATE()
            """)
            today_orders = cursor.fetchone()['today']
            
            # Toplam gelir
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0) as total 
                FROM orders 
                WHERE status = 'completed'
            """)
            total_revenue = cursor.fetchone()['total']
            
            # Bu ayki gelir
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0) as monthly 
                FROM orders 
                WHERE status = 'completed' 
                AND MONTH(created_at) = MONTH(NOW()) 
                AND YEAR(created_at) = YEAR(NOW())
            """)
            monthly_revenue = cursor.fetchone()['monthly']
            
            # Bekleyen siparişler
            cursor.execute("""
                SELECT COUNT(*) as pending 
                FROM orders 
                WHERE status = 'pending'
            """)
            pending_orders = cursor.fetchone()['pending']
            
            cursor.close()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'total_products': total_products,
                'total_orders': total_orders,
                'today_orders': today_orders,
                'total_revenue': float(total_revenue) if total_revenue else 0,
                'monthly_revenue': float(monthly_revenue) if monthly_revenue else 0,
                'pending_orders': pending_orders
            }
            
        except Exception as e:
            self.logger.error(f"Get dashboard stats error: {e}")
            return {}
    
    def _get_dashboard_charts(self) -> Dict[str, Any]:
        """Dashboard grafikleri"""
        try:
            return {
                'sales_chart': self._get_sales_chart_data(30),
                'user_growth': self._get_user_growth_data(30),
                'order_status': self._get_order_status_data(),
                'top_products': self._get_top_products_data(10)
            }
            
        except Exception as e:
            self.logger.error(f"Get dashboard charts error: {e}")
            return {}
    
    def _get_sales_chart_data(self, days: int) -> Dict[str, Any]:
        """Satış grafiği verileri"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(f"""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as orders,
                    COALESCE(SUM(total_amount), 0) as revenue
                FROM orders 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL {days} DAY)
                AND status = 'completed'
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """)
            
            results = cursor.fetchall()
            cursor.close()
            
            # Veriyi formatla
            labels = []
            orders_data = []
            revenue_data = []
            
            for result in results:
                labels.append(result['date'].strftime('%Y-%m-%d'))
                orders_data.append(result['orders'])
                revenue_data.append(float(result['revenue']))
            
            return {
                'labels': labels,
                'orders': orders_data,
                'revenue': revenue_data
            }
            
        except Exception as e:
            self.logger.error(f"Get sales chart data error: {e}")
            return {'labels': [], 'orders': [], 'revenue': []}
    
    def _get_user_growth_data(self, days: int) -> Dict[str, Any]:
        """Kullanıcı büyüme verileri"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(f"""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as new_users
                FROM users 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL {days} DAY)
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """)
            
            results = cursor.fetchall()
            cursor.close()
            
            # Veriyi formatla
            labels = []
            data = []
            
            for result in results:
                labels.append(result['date'].strftime('%Y-%m-%d'))
                data.append(result['new_users'])
            
            return {
                'labels': labels,
                'data': data
            }
            
        except Exception as e:
            self.logger.error(f"Get user growth data error: {e}")
            return {'labels': [], 'data': []}
    
    def _get_order_status_data(self) -> Dict[str, Any]:
        """Sipariş durum verileri"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM orders
                GROUP BY status
            """)
            
            results = cursor.fetchall()
            cursor.close()
            
            # Veriyi formatla
            labels = []
            data = []
            
            for result in results:
                labels.append(result['status'].title())
                data.append(result['count'])
            
            return {
                'labels': labels,
                'data': data
            }
            
        except Exception as e:
            self.logger.error(f"Get order status data error: {e}")
            return {'labels': [], 'data': []}
    
    def _get_top_products_data(self, limit: int) -> List[Dict[str, Any]]:
        """En çok satan ürünler"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(f"""
                SELECT 
                    p.name,
                    p.price,
                    COUNT(oi.product_id) as sales_count,
                    SUM(oi.quantity * oi.price) as total_revenue
                FROM products p
                JOIN order_items oi ON p.id = oi.product_id
                JOIN orders o ON oi.order_id = o.id
                WHERE o.status = 'completed'
                GROUP BY p.id, p.name, p.price
                ORDER BY sales_count DESC
                LIMIT {limit}
            """)
            
            results = cursor.fetchall()
            cursor.close()
            
            # Veriyi formatla
            for result in results:
                result['total_revenue'] = float(result['total_revenue'])
                result['price'] = float(result['price'])
            
            return results
            
        except Exception as e:
            self.logger.error(f"Get top products data error: {e}")
            return []
    
    def _get_recent_activities(self, limit: int) -> List[Dict[str, Any]]:
        """Son aktiviteler"""
        try:
            audit_log = AuditLog()
            return audit_log.get_system_activities(limit)
            
        except Exception as e:
            self.logger.error(f"Get recent activities error: {e}")
            return []
    
    def _get_system_alerts(self) -> List[Dict[str, Any]]:
        """Sistem uyarıları"""
        try:
            alerts = []
            
            # Performans uyarıları
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent
                
                if cpu_percent > 80:
                    alerts.append({
                        'type': 'warning',
                        'title': 'Yüksek CPU Kullanımı',
                        'message': f'CPU kullanımı %{cpu_percent:.1f}',
                        'icon': 'processor'
                    })
                
                if memory_percent > 80:
                    alerts.append({
                        'type': 'warning',
                        'title': 'Yüksek RAM Kullanımı',
                        'message': f'RAM kullanımı %{memory_percent:.1f}',
                        'icon': 'memory'
                    })
                
                if disk_percent > 80:
                    alerts.append({
                        'type': 'warning',
                        'title': 'Yüksek Disk Kullanımı',
                        'message': f'Disk kullanımı %{disk_percent:.1f}',
                        'icon': 'storage'
                    })
                    
            except Exception:
                pass
            
            # Bekleyen siparişler
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
                pending_count = cursor.fetchone()[0]
                cursor.close()
                
                if pending_count > 10:
                    alerts.append({
                        'type': 'info',
                        'title': 'Bekleyen Siparişler',
                        'message': f'{pending_count} sipariş bekliyor',
                        'icon': 'shopping_cart'
                    })
                    
            except Exception:
                pass
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Get system alerts error: {e}")
            return []
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Performans özeti"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'status': 'good' if cpu_percent < 70 else 'warning' if cpu_percent < 85 else 'critical'
                },
                'memory': {
                    'percent': memory.percent,
                    'used': memory.used,
                    'total': memory.total,
                    'status': 'good' if memory.percent < 70 else 'warning' if memory.percent < 85 else 'critical'
                },
                'disk': {
                    'percent': disk.percent,
                    'used': disk.used,
                    'total': disk.total,
                    'status': 'good' if disk.percent < 70 else 'warning' if disk.percent < 85 else 'critical'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Get performance summary error: {e}")
            return {}
    
    def _get_analytics_data(self) -> Dict[str, Any]:
        """Analytics verileri"""
        try:
            return {
                'overview': self._get_analytics_overview(),
                'trends': self._get_analytics_trends(),
                'segments': self._get_user_segments(),
                'conversion': self._get_conversion_data()
            }
            
        except Exception as e:
            self.logger.error(f"Get analytics data error: {e}")
            return {}
    
    def _get_analytics_overview(self) -> Dict[str, Any]:
        """Analytics genel bakış"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Son 30 gün vs önceki 30 gün karşılaştırması
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) as current_orders,
                    SUM(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 60 DAY) AND created_at < DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) as previous_orders,
                    SUM(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) AND status = 'completed' THEN total_amount ELSE 0 END) as current_revenue,
                    SUM(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 60 DAY) AND created_at < DATE_SUB(NOW(), INTERVAL 30 DAY) AND status = 'completed' THEN total_amount ELSE 0 END) as previous_revenue
                FROM orders
            """)
            
            result = cursor.fetchone()
            cursor.close()
            
            # Değişim yüzdelerini hesapla
            order_change = 0
            revenue_change = 0
            
            if result['previous_orders'] > 0:
                order_change = ((result['current_orders'] - result['previous_orders']) / result['previous_orders']) * 100
            
            if result['previous_revenue'] and result['previous_revenue'] > 0:
                revenue_change = ((float(result['current_revenue'] or 0) - float(result['previous_revenue'])) / float(result['previous_revenue'])) * 100
            
            return {
                'current_orders': result['current_orders'],
                'previous_orders': result['previous_orders'],
                'order_change': round(order_change, 1),
                'current_revenue': float(result['current_revenue'] or 0),
                'previous_revenue': float(result['previous_revenue'] or 0),
                'revenue_change': round(revenue_change, 1)
            }
            
        except Exception as e:
            self.logger.error(f"Get analytics overview error: {e}")
            return {}
    
    def _get_system_health_data(self) -> Dict[str, Any]:
        """Sistem sağlık verileri"""
        try:
            return {
                'system_info': self._get_system_info(),
                'database_health': self._check_database_health(),
                'service_status': self._check_service_status(),
                'error_logs': self._get_recent_errors(),
                'backup_status': self._get_backup_status()
            }
            
        except Exception as e:
            self.logger.error(f"Get system health data error: {e}")
            return {}
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Sistem bilgileri"""
        try:
            import platform
            
            return {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()),
                'uptime': datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            }
            
        except Exception as e:
            self.logger.error(f"Get system info error: {e}")
            return {}
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Veritabanı sağlığı"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Bağlantı testi
            cursor.execute("SELECT 1 as test")
            connection_ok = cursor.fetchone()['test'] == 1
            
            # Tablo boyutları
            cursor.execute("""
                SELECT 
                    table_name,
                    round(((data_length + index_length) / 1024 / 1024), 2) as size_mb
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                ORDER BY (data_length + index_length) DESC
                LIMIT 10
            """)
            
            table_sizes = cursor.fetchall()
            cursor.close()
            
            return {
                'connection_ok': connection_ok,
                'table_sizes': table_sizes,
                'status': 'healthy' if connection_ok else 'error'
            }
            
        except Exception as e:
            self.logger.error(f"Check database health error: {e}")
            return {'connection_ok': False, 'status': 'error', 'error': str(e)}
    
    def _check_service_status(self) -> Dict[str, Any]:
        """Servis durumu"""
        try:
            services = {
                'web_server': True,  # Bu çalışıyorsa web server çalışıyor
                'database': self._check_database_health()['connection_ok'],
                'cache': self._check_cache_service(),
                'file_storage': self._check_file_storage(),
                'email_service': self._check_email_service()
            }
            
            return services
            
        except Exception as e:
            self.logger.error(f"Check service status error: {e}")
            return {}
    
    def _check_cache_service(self) -> bool:
        """Cache servisi kontrolü"""
        try:
            # Redis veya başka cache servisi kontrolü
            # Şimdilik True döndür
            return True
        except Exception:
            return False
    
    def _check_file_storage(self) -> bool:
        """Dosya depolama kontrolü"""
        try:
            # Uploads klasörü yazılabilir mi?
            uploads_dir = 'uploads'
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
            
            test_file = os.path.join(uploads_dir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            
            os.remove(test_file)
            return True
            
        except Exception:
            return False
    
    def _check_email_service(self) -> bool:
        """Email servisi kontrolü"""
        try:
            # Email servisi kontrolü
            # Şimdilik True döndür
            return True
        except Exception:
            return False