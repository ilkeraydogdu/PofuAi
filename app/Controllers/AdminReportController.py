"""
Admin Report Controller
Admin paneli için gelişmiş raporlama sistemi
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.Controllers.BaseController import BaseController
from app.Middleware.AuthMiddleware import admin_required
from core.Services.advanced_reporting_service import AdvancedReportingService, ReportType, ReportConfig, ReportFilter
from core.Services.advanced_session_service import AdvancedSessionService
from core.Services.seo_service import SEOService
from core.Services.security_service import SecurityService
from core.Services.performance_optimizer import PerformanceOptimizer
from core.Services.error_handler import error_handler
from flask import jsonify, request, render_template, make_response
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta

class AdminReportController(BaseController):
    """Admin raporlama controller'ı"""
    
    def __init__(self):
        super().__init__()
        self.reporting_service = AdvancedReportingService()
        self.session_service = AdvancedSessionService()
        self.seo_service = SEOService()
        self.security_service = SecurityService()
        self.performance_optimizer = PerformanceOptimizer()
    
    @admin_required
    def index(self):
        """Raporlama ana sayfası"""
        try:
            data = {
                'title': 'Gelişmiş Raporlama Sistemi',
                'report_types': [
                    {'id': 'user_behavior', 'name': 'Kullanıcı Davranış Analizi', 'icon': 'fas fa-users'},
                    {'id': 'sales_analysis', 'name': 'Satış Analizi', 'icon': 'fas fa-chart-line'},
                    {'id': 'system_performance', 'name': 'Sistem Performansı', 'icon': 'fas fa-tachometer-alt'},
                    {'id': 'seo_metrics', 'name': 'SEO Metrikleri', 'icon': 'fas fa-search'},
                    {'id': 'security_audit', 'name': 'Güvenlik Denetimi', 'icon': 'fas fa-shield-alt'},
                    {'id': 'session_analytics', 'name': 'Session Analitikleri', 'icon': 'fas fa-clock'},
                    {'id': 'custom_query', 'name': 'Özel Sorgu', 'icon': 'fas fa-database'}
                ],
                'quick_stats': self._get_quick_stats()
            }
            
            return self.view('admin.reports.index', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def generate_report(self):
        """Rapor oluştur"""
        try:
            if request.method == 'GET':
                # Rapor oluşturma formu
                report_type = request.args.get('type', 'user_behavior')
                
                data = {
                    'title': 'Rapor Oluştur',
                    'report_type': report_type,
                    'available_fields': self._get_available_fields(report_type),
                    'filter_options': self._get_filter_options(report_type)
                }
                
                return self.view('admin.reports.generate', data)
            
            elif request.method == 'POST':
                # Rapor oluştur
                form_data = self._safe_get_input()
                
                report_type = ReportType(form_data.get('report_type', 'user_behavior'))
                
                # Filtreleri oluştur
                filters = []
                if form_data.get('filters'):
                    for filter_data in form_data['filters']:
                        filters.append(ReportFilter(
                            field=filter_data['field'],
                            operator=filter_data['operator'],
                            value=filter_data['value']
                        ))
                
                # Rapor konfigürasyonu
                config = ReportConfig(
                    name=form_data.get('name', 'Özel Rapor'),
                    type=report_type,
                    filters=filters,
                    groupby=form_data.get('groupby', []),
                    orderby=form_data.get('orderby', []),
                    limit=form_data.get('limit'),
                    custom_fields=form_data.get('custom_fields')
                )
                
                # Raporu oluştur
                if report_type == ReportType.USER_BEHAVIOR:
                    report = self.reporting_service.generate_user_behavior_report(config)
                elif report_type == ReportType.SALES_ANALYSIS:
                    report = self.reporting_service.generate_sales_analysis_report(config)
                elif report_type == ReportType.SYSTEM_PERFORMANCE:
                    report = self.reporting_service.generate_system_performance_report(config)
                elif report_type == ReportType.CUSTOM_QUERY:
                    report = self.reporting_service.generate_custom_report(config)
                else:
                    report = {'error': 'Desteklenmeyen rapor türü'}
                
                # Export format
                export_format = form_data.get('export_format', 'json')
                
                if export_format == 'json':
                    return jsonify(report)
                elif export_format == 'csv':
                    csv_data = self.reporting_service.export_report(report, 'csv')
                    response = make_response(csv_data)
                    response.headers['Content-Type'] = 'text/csv'
                    response.headers['Content-Disposition'] = f'attachment; filename=report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                    return response
                else:
                    return jsonify(report)
                    
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def user_purchase_prediction(self):
        """Kullanıcı satın alma tahmini"""
        try:
            user_id = request.args.get('user_id', type=int)
            
            if not user_id:
                return jsonify({'error': 'User ID gerekli'})
            
            prediction = self.reporting_service.get_user_purchase_prediction(user_id)
            
            return jsonify(prediction)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def session_analytics(self):
        """Session analitikleri"""
        try:
            user_id = request.args.get('user_id', type=int)
            days = request.args.get('days', 30, type=int)
            
            analytics = self.session_service.get_session_analytics(user_id, days)
            
            return jsonify(analytics)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def seo_report(self):
        """SEO raporu"""
        try:
            url = request.args.get('url')
            
            seo_analysis = self.seo_service.analyze_seo_performance(url)
            
            return jsonify(seo_analysis)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def security_audit(self):
        """Güvenlik denetimi"""
        try:
            days = request.args.get('days', 7, type=int)
            
            # Güvenlik metrikleri
            security_report = {
                'timestamp': datetime.now().isoformat(),
                'period_days': days,
                'security_events': self._get_security_events(days),
                'blocked_ips': self._get_blocked_ips(),
                'suspicious_activities': self._get_suspicious_activities(days),
                'recommendations': self._get_security_recommendations()
            }
            
            return jsonify(security_report)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def performance_report(self):
        """Performans raporu"""
        try:
            days = request.args.get('days', 7, type=int)
            
            performance_report = self.performance_optimizer.get_performance_report(days)
            
            return jsonify(performance_report)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def real_time_metrics(self):
        """Gerçek zamanlı metrikler"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'active_users': self._get_active_users_count(),
                'current_sessions': self._get_current_sessions_count(),
                'system_performance': self.performance_optimizer.monitor_system_performance(),
                'recent_activities': self._get_recent_activities(),
                'security_alerts': self._get_recent_security_alerts()
            }
            
            return jsonify(metrics)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def export_report(self):
        """Rapor dışa aktar"""
        try:
            report_id = request.args.get('report_id')
            format_type = request.args.get('format', 'json')
            
            # Raporu cache'ten veya database'den al
            report = self._get_saved_report(report_id)
            
            if not report:
                return jsonify({'error': 'Rapor bulunamadı'})
            
            # Export
            exported_data = self.reporting_service.export_report(report, format_type)
            
            if format_type == 'json':
                return jsonify({'data': exported_data})
            elif format_type == 'csv':
                response = make_response(exported_data)
                response.headers['Content-Type'] = 'text/csv'
                response.headers['Content-Disposition'] = f'attachment; filename=report_{report_id}.csv'
                return response
            elif format_type == 'excel':
                # Excel dosyası oluşturuldu
                return jsonify({'download_url': f'/admin/reports/download/{exported_data}'})
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def dashboard_widgets(self):
        """Dashboard widget'ları"""
        try:
            widgets = {
                'user_stats': self._get_user_widget_data(),
                'sales_stats': self._get_sales_widget_data(),
                'performance_stats': self._get_performance_widget_data(),
                'security_stats': self._get_security_widget_data(),
                'seo_stats': self._get_seo_widget_data()
            }
            
            return jsonify(widgets)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def _get_quick_stats(self) -> Dict[str, Any]:
        """Hızlı istatistikler"""
        try:
            return {
                'total_users': self._count_total_users(),
                'active_users_today': self._count_active_users_today(),
                'total_orders': self._count_total_orders(),
                'revenue_today': self._get_revenue_today(),
                'system_health': self._get_system_health_score(),
                'security_score': self._get_security_score()
            }
        except Exception:
            return {}
    
    def _get_available_fields(self, report_type: str) -> List[str]:
        """Rapor türü için mevcut alanlar"""
        fields_map = {
            'user_behavior': ['id', 'name', 'email', 'role', 'created_at', 'last_login_at', 'post_count', 'comment_count', 'order_count'],
            'sales_analysis': ['order_date', 'order_count', 'total_revenue', 'avg_order_value', 'product_name', 'category'],
            'system_performance': ['timestamp', 'cpu_usage', 'memory_usage', 'disk_usage', 'response_time'],
            'custom_query': ['*']
        }
        
        return fields_map.get(report_type, [])
    
    def _get_filter_options(self, report_type: str) -> Dict[str, List[str]]:
        """Rapor türü için filtre seçenekleri"""
        return {
            'operators': ['eq', 'ne', 'gt', 'lt', 'gte', 'lte', 'like', 'in', 'between'],
            'date_ranges': ['today', 'yesterday', 'last_7_days', 'last_30_days', 'last_90_days', 'custom'],
            'user_roles': ['admin', 'user', 'moderator'],
            'order_statuses': ['pending', 'completed', 'cancelled', 'refunded']
        }
    
    def _get_security_events(self, days: int) -> List[Dict[str, Any]]:
        """Güvenlik olayları"""
        # Bu method gerçek implementasyonda security service'ten veri çekecek
        return []
    
    def _get_blocked_ips(self) -> List[str]:
        """Bloklu IP'ler"""
        # Bu method gerçek implementasyonda security service'ten veri çekecek
        return []
    
    def _get_suspicious_activities(self, days: int) -> List[Dict[str, Any]]:
        """Şüpheli aktiviteler"""
        # Bu method gerçek implementasyonda security service'ten veri çekecek
        return []
    
    def _get_security_recommendations(self) -> List[str]:
        """Güvenlik önerileri"""
        return [
            "2FA aktifleştirmeyi düşünün",
            "Güçlü şifre politikası uygulayın",
            "Düzenli güvenlik güncellemeleri yapın",
            "Log monitoring sistemini aktifleştirin"
        ]
    
    def _get_active_users_count(self) -> int:
        """Aktif kullanıcı sayısı"""
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE last_login_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)"
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception:
            return 0
    
    def _get_current_sessions_count(self) -> int:
        """Mevcut session sayısı"""
        # Session service'ten alınacak
        return 0
    
    def _get_recent_activities(self) -> List[Dict[str, Any]]:
        """Son aktiviteler"""
        return []
    
    def _get_recent_security_alerts(self) -> List[Dict[str, Any]]:
        """Son güvenlik uyarıları"""
        return []
    
    def _get_saved_report(self, report_id: str) -> Dict[str, Any]:
        """Kaydedilmiş raporu al"""
        # Cache veya database'den rapor verisi
        return {}
    
    def _get_user_widget_data(self) -> Dict[str, Any]:
        """Kullanıcı widget verisi"""
        return {
            'total_users': self._count_total_users(),
            'new_users_today': self._count_new_users_today(),
            'active_users': self._count_active_users_today(),
            'user_growth': self._calculate_user_growth()
        }
    
    def _get_sales_widget_data(self) -> Dict[str, Any]:
        """Satış widget verisi"""
        return {
            'total_revenue': self._get_total_revenue(),
            'revenue_today': self._get_revenue_today(),
            'orders_today': self._count_orders_today(),
            'avg_order_value': self._get_avg_order_value()
        }
    
    def _get_performance_widget_data(self) -> Dict[str, Any]:
        """Performans widget verisi"""
        perf_data = self.performance_optimizer.monitor_system_performance()
        return {
            'cpu_usage': perf_data.get('cpu_usage', 0),
            'memory_usage': perf_data.get('memory', {}).get('percent', 0),
            'disk_usage': perf_data.get('disk', {}).get('percent', 0),
            'response_time': self._get_avg_response_time()
        }
    
    def _get_security_widget_data(self) -> Dict[str, Any]:
        """Güvenlik widget verisi"""
        return {
            'security_score': self._get_security_score(),
            'blocked_attempts': self._count_blocked_attempts_today(),
            'active_threats': self._count_active_threats(),
            'last_security_scan': self._get_last_security_scan_date()
        }
    
    def _get_seo_widget_data(self) -> Dict[str, Any]:
        """SEO widget verisi"""
        return {
            'seo_score': self._get_average_seo_score(),
            'indexed_pages': self._count_indexed_pages(),
            'organic_traffic': self._get_organic_traffic_today(),
            'keyword_rankings': self._get_keyword_rankings_count()
        }
    
    # Helper methods (placeholder implementations)
    def _count_total_users(self) -> int:
        try:
            query = "SELECT COUNT(*) as count FROM users"
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception:
            return 0
    
    def _count_active_users_today(self) -> int:
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE last_login_at >= CURDATE()"
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception:
            return 0
    
    def _count_total_orders(self) -> int:
        try:
            query = "SELECT COUNT(*) as count FROM orders"
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception:
            return 0
    
    def _get_revenue_today(self) -> float:
        try:
            query = "SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders WHERE DATE(created_at) = CURDATE() AND status = 'completed'"
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchone()
            return float(result['revenue']) if result else 0.0
        except Exception:
            return 0.0
    
    def _get_system_health_score(self) -> int:
        """Sistem sağlık skoru (0-100)"""
        return 85  # Placeholder
    
    def _get_security_score(self) -> int:
        """Güvenlik skoru (0-100)"""
        return 92  # Placeholder