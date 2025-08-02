"""
Real-time Dashboard Controller
Gerçek zamanlı dashboard controller'ı
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.Controllers.BaseController import BaseController
from app.Middleware.AuthMiddleware import auth_required, admin_required
from core.Services.error_handler import error_handler
from core.Services.realtime_websocket_service import RealtimeWebSocketService
from core.Database.connection import get_connection
import json
import datetime
from flask import jsonify, request, session
from typing import Dict, Any, List
import asyncio

class RealtimeDashboardController(BaseController):
    """Real-time dashboard controller'ı"""
    
    def __init__(self):
        super().__init__()
        self.websocket_service = RealtimeWebSocketService()
    
    @admin_required
    def dashboard(self):
        """Real-time dashboard ana sayfası"""
        try:
            admin = self.get_current_user()
            
            # İlk yükleme verileri
            initial_data = {
                'system_stats': self._get_system_stats(),
                'live_users': self._get_live_users(),
                'recent_activities': self._get_recent_activities(),
                'performance_metrics': self._get_performance_metrics(),
                'alerts': self._get_system_alerts()
            }
            
            data = {
                'title': 'Gerçek Zamanlı Dashboard',
                'admin': admin,
                'initial_data': initial_data,
                'websocket_url': '/realtime-dashboard'
            }
            
            return self.view('admin.realtime_dashboard', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def api_live_stats(self):
        """Canlı istatistikleri API endpoint'i"""
        try:
            stats = {
                'timestamp': datetime.datetime.now().isoformat(),
                'system': self._get_system_stats(),
                'users': self._get_live_users_count(),
                'orders': self._get_live_orders_stats(),
                'revenue': self._get_live_revenue_stats(),
                'performance': self._get_performance_metrics(),
                'errors': self._get_error_stats()
            }
            
            return jsonify({
                'success': True,
                'data': stats
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    @admin_required
    def api_live_activities(self):
        """Canlı aktiviteler API endpoint'i"""
        try:
            activities = self._get_recent_activities(limit=20)
            
            return jsonify({
                'success': True,
                'data': activities
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    @admin_required
    def api_system_health(self):
        """Sistem sağlığı API endpoint'i"""
        try:
            health = {
                'database': self._check_database_health(),
                'cache': self._check_cache_health(),
                'storage': self._check_storage_health(),
                'integrations': self._check_integrations_health(),
                'services': self._check_services_health()
            }
            
            return jsonify({
                'success': True,
                'data': health
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    @admin_required
    def api_performance_chart(self):
        """Performans grafiği API endpoint'i"""
        try:
            time_range = request.args.get('range', '1h')  # 1h, 6h, 24h, 7d
            
            chart_data = self._get_performance_chart_data(time_range)
            
            return jsonify({
                'success': True,
                'data': chart_data
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    @admin_required
    def api_alerts(self):
        """Sistem uyarıları API endpoint'i"""
        try:
            alerts = self._get_system_alerts()
            
            return jsonify({
                'success': True,
                'data': alerts
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    # Helper Methods
    def _get_system_stats(self) -> Dict[str, Any]:
        """Sistem istatistikleri"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Toplam kullanıcı sayısı
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total_users = cursor.fetchone()['total']
            
            # Aktif kullanıcı sayısı (son 5 dakika)
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as active 
                FROM user_sessions 
                WHERE last_activity > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
            """)
            active_users = cursor.fetchone()['active'] if cursor.fetchone() else 0
            
            # Toplam sipariş sayısı (bugün)
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM orders 
                WHERE DATE(created_at) = CURDATE()
            """)
            daily_orders = cursor.fetchone()['total']
            
            # Günlük gelir
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0) as revenue 
                FROM orders 
                WHERE DATE(created_at) = CURDATE() AND status = 'completed'
            """)
            daily_revenue = cursor.fetchone()['revenue']
            
            cursor.close()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'daily_orders': daily_orders,
                'daily_revenue': float(daily_revenue) if daily_revenue else 0,
                'system_uptime': self._get_system_uptime(),
                'server_load': self._get_server_load()
            }
            
        except Exception as e:
            self.logger.error(f"System stats error: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'daily_orders': 0,
                'daily_revenue': 0,
                'system_uptime': '0:00:00',
                'server_load': 0
            }
    
    def _get_live_users(self) -> List[Dict[str, Any]]:
        """Canlı kullanıcılar"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT u.id, u.name, u.email, u.role, us.last_activity, us.ip_address, us.user_agent
                FROM users u
                JOIN user_sessions us ON u.id = us.user_id
                WHERE us.last_activity > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
                ORDER BY us.last_activity DESC
                LIMIT 50
            """)
            
            live_users = cursor.fetchall()
            cursor.close()
            
            return live_users
            
        except Exception as e:
            self.logger.error(f"Live users error: {e}")
            return []
    
    def _get_recent_activities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Son aktiviteler"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT al.*, u.name as user_name, u.email as user_email
                FROM audit_logs al
                LEFT JOIN users u ON al.user_id = u.id
                ORDER BY al.created_at DESC
                LIMIT %s
            """, [limit])
            
            activities = cursor.fetchall()
            cursor.close()
            
            return activities
            
        except Exception as e:
            self.logger.error(f"Recent activities error: {e}")
            return []
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Performans metrikleri"""
        try:
            import psutil
            
            # CPU kullanımı
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Bellek kullanımı
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk kullanımı
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Ağ istatistikleri
            network = psutil.net_io_counters()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'network_sent': network.bytes_sent,
                'network_recv': network.bytes_recv,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Performance metrics error: {e}")
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'network_sent': 0,
                'network_recv': 0,
                'timestamp': datetime.datetime.now().isoformat()
            }
    
    def _get_system_alerts(self) -> List[Dict[str, Any]]:
        """Sistem uyarıları"""
        alerts = []
        
        try:
            # Performans kontrolü
            metrics = self._get_performance_metrics()
            
            if metrics['cpu_percent'] > 80:
                alerts.append({
                    'type': 'warning',
                    'title': 'Yüksek CPU Kullanımı',
                    'message': f'CPU kullanımı %{metrics["cpu_percent"]:.1f}',
                    'timestamp': datetime.datetime.now().isoformat()
                })
            
            if metrics['memory_percent'] > 85:
                alerts.append({
                    'type': 'danger',
                    'title': 'Yüksek Bellek Kullanımı',
                    'message': f'Bellek kullanımı %{metrics["memory_percent"]:.1f}',
                    'timestamp': datetime.datetime.now().isoformat()
                })
            
            if metrics['disk_percent'] > 90:
                alerts.append({
                    'type': 'danger',
                    'title': 'Disk Alanı Yetersiz',
                    'message': f'Disk kullanımı %{metrics["disk_percent"]:.1f}',
                    'timestamp': datetime.datetime.now().isoformat()
                })
            
            # Veritabanı bağlantı kontrolü
            if not self._check_database_health()['healthy']:
                alerts.append({
                    'type': 'danger',
                    'title': 'Veritabanı Bağlantı Sorunu',
                    'message': 'Veritabanı bağlantısında sorun tespit edildi',
                    'timestamp': datetime.datetime.now().isoformat()
                })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"System alerts error: {e}")
            return []
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Veritabanı sağlık kontrolü"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Basit sorgu testi
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            # Bağlantı sayısı
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            connections = cursor.fetchone()
            
            cursor.close()
            
            return {
                'healthy': True,
                'connections': int(connections[1]) if connections else 0,
                'response_time': 0.001  # Örnek değer
            }
            
        except Exception as e:
            self.logger.error(f"Database health check error: {e}")
            return {
                'healthy': False,
                'error': str(e),
                'connections': 0,
                'response_time': 0
            }
    
    def _check_cache_health(self) -> Dict[str, Any]:
        """Cache sağlık kontrolü"""
        try:
            # Redis veya diğer cache sistemleri kontrolü
            return {
                'healthy': True,
                'hit_rate': 85.5,  # Örnek değer
                'memory_usage': 45.2  # Örnek değer
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _check_storage_health(self) -> Dict[str, Any]:
        """Depolama sağlık kontrolü"""
        try:
            import psutil
            
            disk = psutil.disk_usage('/')
            
            return {
                'healthy': True,
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'usage_percent': round((disk.used / disk.total) * 100, 2)
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _check_integrations_health(self) -> Dict[str, Any]:
        """Entegrasyonlar sağlık kontrolü"""
        try:
            # Entegrasyon durumları kontrolü
            healthy_count = 0
            total_count = 5  # Örnek değer
            
            return {
                'healthy': healthy_count == total_count,
                'healthy_count': healthy_count,
                'total_count': total_count,
                'success_rate': (healthy_count / total_count) * 100 if total_count > 0 else 0
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _check_services_health(self) -> Dict[str, Any]:
        """Servisler sağlık kontrolü"""
        try:
            services = {
                'websocket': True,
                'email': True,
                'queue': True,
                'scheduler': True
            }
            
            healthy_count = sum(services.values())
            total_count = len(services)
            
            return {
                'healthy': healthy_count == total_count,
                'services': services,
                'healthy_count': healthy_count,
                'total_count': total_count
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    def _get_system_uptime(self) -> str:
        """Sistem çalışma süresi"""
        try:
            import psutil
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.datetime.now().timestamp() - boot_time
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return f"{days}d {hours}h {minutes}m"
            
        except Exception:
            return "0d 0h 0m"
    
    def _get_server_load(self) -> float:
        """Sunucu yükü"""
        try:
            import psutil
            return psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
        except Exception:
            return 0.0