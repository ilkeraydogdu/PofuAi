"""
Advanced Reporting Service
İleri seviye dinamik raporlama sistemi
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from core.Services.base_service import BaseService
from core.Database.connection import get_connection
from core.Services.cache_service import CacheService
from core.Services.logger import LoggerService
import sqlite3
import mysql.connector
from dataclasses import dataclass
from enum import Enum

class ReportType(Enum):
    USER_BEHAVIOR = "user_behavior"
    SALES_ANALYSIS = "sales_analysis"
    SYSTEM_PERFORMANCE = "system_performance"
    SEO_METRICS = "seo_metrics"
    SECURITY_AUDIT = "security_audit"
    CUSTOM_QUERY = "custom_query"

@dataclass
class ReportFilter:
    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, in, like, between
    value: Any
    logic: str = "AND"  # AND, OR

@dataclass
class ReportConfig:
    name: str
    type: ReportType
    filters: List[ReportFilter]
    groupby: List[str]
    orderby: List[Dict[str, str]]
    limit: Optional[int] = None
    date_range: Optional[Dict[str, datetime]] = None
    custom_fields: Optional[List[str]] = None

class AdvancedReportingService(BaseService):
    """İleri seviye raporlama servisi"""
    
    def __init__(self):
        super().__init__()
        self.cache = CacheService()
        self.logger = LoggerService.get_logger()
        self.connection = get_connection()
        
    def generate_user_behavior_report(self, config: ReportConfig) -> Dict[str, Any]:
        """Kullanıcı davranış raporu"""
        try:
            query = """
            SELECT 
                u.id,
                u.name,
                u.email,
                u.role,
                u.created_at,
                u.last_login_at,
                COUNT(DISTINCT p.id) as post_count,
                COUNT(DISTINCT c.id) as comment_count,
                COUNT(DISTINCT o.id) as order_count,
                COALESCE(SUM(o.total_amount), 0) as total_spent,
                AVG(o.total_amount) as avg_order_value,
                COUNT(DISTINCT DATE(o.created_at)) as active_days,
                (
                    SELECT COUNT(*) FROM user_sessions us 
                    WHERE us.user_id = u.id 
                    AND us.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                ) as sessions_last_30_days,
                CASE 
                    WHEN u.last_login_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 'Active'
                    WHEN u.last_login_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 'Inactive'
                    ELSE 'Dormant'
                END as user_status,
                CASE
                    WHEN COALESCE(SUM(o.total_amount), 0) > 1000 THEN 'High Value'
                    WHEN COALESCE(SUM(o.total_amount), 0) > 500 THEN 'Medium Value'
                    WHEN COALESCE(SUM(o.total_amount), 0) > 0 THEN 'Low Value'
                    ELSE 'No Purchase'
                END as customer_segment
            FROM users u
            LEFT JOIN posts p ON u.id = p.user_id
            LEFT JOIN comments c ON u.id = c.user_id
            LEFT JOIN orders o ON u.id = o.user_id
            WHERE 1=1
            """
            
            # Filtreleri uygula
            query, params = self._apply_filters(query, config.filters)
            
            # Gruplama ve sıralama
            if config.groupby:
                query += f" GROUP BY {', '.join(config.groupby)}"
            else:
                query += " GROUP BY u.id"
                
            if config.orderby:
                order_clauses = []
                for order in config.orderby:
                    field = order.get('field')
                    direction = order.get('direction', 'ASC')
                    order_clauses.append(f"{field} {direction}")
                query += f" ORDER BY {', '.join(order_clauses)}"
            
            if config.limit:
                query += f" LIMIT {config.limit}"
            
            # Sorguyu çalıştır
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or [])
            results = cursor.fetchall()
            
            # Analiz ekle
            analysis = self._analyze_user_behavior(results)
            
            # Öneriler oluştur
            recommendations = self._generate_user_recommendations(results, analysis)
            
            report = {
                'type': 'user_behavior',
                'generated_at': datetime.now().isoformat(),
                'config': config.__dict__,
                'data': results,
                'analysis': analysis,
                'recommendations': recommendations,
                'summary': {
                    'total_users': len(results),
                    'active_users': len([u for u in results if u['user_status'] == 'Active']),
                    'high_value_customers': len([u for u in results if u['customer_segment'] == 'High Value']),
                    'total_revenue': sum([u['total_spent'] for u in results]),
                    'avg_customer_value': np.mean([u['total_spent'] for u in results]) if results else 0
                }
            }
            
            # Cache'e kaydet
            cache_key = f"report_user_behavior_{hash(str(config.__dict__))}"
            self.cache.set(cache_key, report, 3600)  # 1 saat
            
            return report
            
        except Exception as e:
            self.logger.error(f"User behavior report error: {str(e)}")
            raise
    
    def generate_sales_analysis_report(self, config: ReportConfig) -> Dict[str, Any]:
        """Satış analiz raporu"""
        try:
            query = """
            SELECT 
                DATE(o.created_at) as order_date,
                COUNT(DISTINCT o.id) as order_count,
                COUNT(DISTINCT o.user_id) as unique_customers,
                SUM(o.total_amount) as total_revenue,
                AVG(o.total_amount) as avg_order_value,
                SUM(oi.quantity) as total_items_sold,
                COUNT(DISTINCT oi.product_id) as unique_products_sold,
                p.category,
                p.name as product_name,
                SUM(oi.quantity * oi.price) as product_revenue,
                SUM(oi.quantity) as product_quantity_sold,
                CASE 
                    WHEN DAYOFWEEK(o.created_at) IN (1,7) THEN 'Weekend'
                    ELSE 'Weekday'
                END as day_type,
                HOUR(o.created_at) as order_hour,
                u.city as customer_city,
                u.country as customer_country
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            JOIN users u ON o.user_id = u.id
            WHERE o.status = 'completed'
            """
            
            # Filtreleri uygula
            query, params = self._apply_filters(query, config.filters)
            
            # Gruplama
            if config.groupby:
                query += f" GROUP BY {', '.join(config.groupby)}"
            else:
                query += " GROUP BY DATE(o.created_at)"
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or [])
            results = cursor.fetchall()
            
            # Trend analizi
            trends = self._analyze_sales_trends(results)
            
            # Ürün performans analizi
            product_performance = self._analyze_product_performance(results)
            
            # Müşteri segmentasyonu
            customer_segments = self._analyze_customer_segments(results)
            
            # Tahminleme
            forecasting = self._generate_sales_forecast(results)
            
            report = {
                'type': 'sales_analysis',
                'generated_at': datetime.now().isoformat(),
                'data': results,
                'trends': trends,
                'product_performance': product_performance,
                'customer_segments': customer_segments,
                'forecasting': forecasting,
                'summary': {
                    'total_revenue': sum([r['total_revenue'] for r in results]),
                    'total_orders': sum([r['order_count'] for r in results]),
                    'avg_order_value': np.mean([r['avg_order_value'] for r in results]) if results else 0,
                    'best_selling_day': max(results, key=lambda x: x['total_revenue'])['order_date'] if results else None
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Sales analysis report error: {str(e)}")
            raise
    
    def generate_system_performance_report(self, config: ReportConfig) -> Dict[str, Any]:
        """Sistem performans raporu"""
        try:
            # Sistem metrikleri
            system_metrics = self._get_system_metrics()
            
            # Database performansı
            db_performance = self._analyze_database_performance()
            
            # Cache performansı
            cache_performance = self._analyze_cache_performance()
            
            # API performansı
            api_performance = self._analyze_api_performance()
            
            # Güvenlik metrikleri
            security_metrics = self._get_security_metrics()
            
            # Hata analizi
            error_analysis = self._analyze_system_errors()
            
            report = {
                'type': 'system_performance',
                'generated_at': datetime.now().isoformat(),
                'system_metrics': system_metrics,
                'database_performance': db_performance,
                'cache_performance': cache_performance,
                'api_performance': api_performance,
                'security_metrics': security_metrics,
                'error_analysis': error_analysis,
                'recommendations': self._generate_performance_recommendations()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"System performance report error: {str(e)}")
            raise
    
    def generate_custom_report(self, config: ReportConfig) -> Dict[str, Any]:
        """Özel sorgu raporu"""
        try:
            if not config.custom_fields:
                raise ValueError("Custom fields required for custom report")
            
            # Güvenlik kontrolü - sadece belirli tablolara erişim
            allowed_tables = ['users', 'posts', 'comments', 'orders', 'products', 'categories']
            
            # Dinamik sorgu oluştur
            query = self._build_custom_query(config)
            
            # SQL injection kontrolü
            if not self._validate_query_security(query):
                raise ValueError("Query contains potentially dangerous operations")
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Otomatik analiz
            analysis = self._auto_analyze_data(results)
            
            report = {
                'type': 'custom_report',
                'generated_at': datetime.now().isoformat(),
                'query': query,
                'data': results,
                'analysis': analysis,
                'row_count': len(results)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Custom report error: {str(e)}")
            raise
    
    def export_report(self, report: Dict[str, Any], format: str = 'json') -> str:
        """Raporu dışa aktar"""
        try:
            if format.lower() == 'json':
                return json.dumps(report, indent=2, default=str)
            
            elif format.lower() == 'csv':
                if 'data' in report and isinstance(report['data'], list):
                    df = pd.DataFrame(report['data'])
                    return df.to_csv(index=False)
                
            elif format.lower() == 'excel':
                if 'data' in report and isinstance(report['data'], list):
                    df = pd.DataFrame(report['data'])
                    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    df.to_excel(filename, index=False)
                    return filename
            
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Export report error: {str(e)}")
            raise
    
    def _apply_filters(self, query: str, filters: List[ReportFilter]) -> tuple:
        """Filtreleri sorguya uygula"""
        if not filters:
            return query, []
        
        conditions = []
        params = []
        
        for filter in filters:
            if filter.operator == 'eq':
                conditions.append(f"{filter.field} = %s")
                params.append(filter.value)
            elif filter.operator == 'ne':
                conditions.append(f"{filter.field} != %s")
                params.append(filter.value)
            elif filter.operator == 'gt':
                conditions.append(f"{filter.field} > %s")
                params.append(filter.value)
            elif filter.operator == 'lt':
                conditions.append(f"{filter.field} < %s")
                params.append(filter.value)
            elif filter.operator == 'gte':
                conditions.append(f"{filter.field} >= %s")
                params.append(filter.value)
            elif filter.operator == 'lte':
                conditions.append(f"{filter.field} <= %s")
                params.append(filter.value)
            elif filter.operator == 'like':
                conditions.append(f"{filter.field} LIKE %s")
                params.append(f"%{filter.value}%")
            elif filter.operator == 'in':
                placeholders = ','.join(['%s'] * len(filter.value))
                conditions.append(f"{filter.field} IN ({placeholders})")
                params.extend(filter.value)
            elif filter.operator == 'between':
                conditions.append(f"{filter.field} BETWEEN %s AND %s")
                params.extend(filter.value)
        
        if conditions:
            # İlk filtre için AND/OR mantığını uygula
            filter_query = " AND " + " AND ".join(conditions)
            query += filter_query
        
        return query, params
    
    def _analyze_user_behavior(self, data: List[Dict]) -> Dict[str, Any]:
        """Kullanıcı davranış analizi"""
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        
        analysis = {
            'engagement_score': self._calculate_engagement_score(df),
            'churn_risk': self._calculate_churn_risk(df),
            'lifetime_value': self._calculate_customer_lifetime_value(df),
            'behavior_patterns': self._identify_behavior_patterns(df),
            'seasonal_trends': self._analyze_seasonal_trends(df)
        }
        
        return analysis
    
    def _calculate_engagement_score(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Engagement skoru hesapla"""
        # Basit engagement skoru: posts + comments + orders
        df['engagement_score'] = (
            df['post_count'] * 3 +
            df['comment_count'] * 2 +
            df['order_count'] * 5 +
            df['sessions_last_30_days'] * 1
        )
        
        return {
            'avg_score': float(df['engagement_score'].mean()),
            'median_score': float(df['engagement_score'].median()),
            'top_10_percent': float(df['engagement_score'].quantile(0.9)),
            'distribution': df['engagement_score'].describe().to_dict()
        }
    
    def _generate_user_recommendations(self, data: List[Dict], analysis: Dict) -> List[str]:
        """Kullanıcı önerileri oluştur"""
        recommendations = []
        
        if not data:
            return recommendations
        
        df = pd.DataFrame(data)
        
        # Churn riski yüksek kullanıcılar
        dormant_users = len(df[df['user_status'] == 'Dormant'])
        if dormant_users > len(df) * 0.3:
            recommendations.append(f"Yüksek churn riski: {dormant_users} kullanıcı uzun süredir aktif değil. Re-engagement kampanyası düşünün.")
        
        # Düşük engagement
        low_engagement = len(df[df.get('engagement_score', 0) < analysis.get('engagement_score', {}).get('avg_score', 0)])
        if low_engagement > len(df) * 0.5:
            recommendations.append("Kullanıcı engagement'ı düşük. Gamification veya reward sistemi ekleyin.")
        
        # Satın alma davranışı
        no_purchase = len(df[df['customer_segment'] == 'No Purchase'])
        if no_purchase > len(df) * 0.6:
            recommendations.append("Çok sayıda kullanıcı hiç satın alma yapmamış. Onboarding sürecini gözden geçirin.")
        
        return recommendations
    
    def get_user_purchase_prediction(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcının satın alabileceği ürünleri tahmin et"""
        try:
            # Kullanıcı profili analizi
            user_profile = self._get_user_profile_analysis(user_id)
            
            # Satın alma geçmişi
            purchase_history = self._get_user_purchase_history(user_id)
            
            # Benzer kullanıcılar
            similar_users = self._find_similar_users(user_id)
            
            # Ürün önerileri
            product_recommendations = self._generate_product_recommendations(
                user_profile, purchase_history, similar_users
            )
            
            # Fiyat analizi
            price_analysis = self._analyze_user_price_preferences(user_id)
            
            # Kategori tercihleri
            category_preferences = self._analyze_category_preferences(user_id)
            
            # Sezonsal analiz
            seasonal_preferences = self._analyze_seasonal_preferences(user_id)
            
            return {
                'user_id': user_id,
                'profile': user_profile,
                'purchase_history': purchase_history,
                'similar_users': similar_users,
                'product_recommendations': product_recommendations,
                'price_analysis': price_analysis,
                'category_preferences': category_preferences,
                'seasonal_preferences': seasonal_preferences,
                'confidence_score': self._calculate_prediction_confidence(user_profile, purchase_history)
            }
            
        except Exception as e:
            self.logger.error(f"User purchase prediction error: {str(e)}")
            raise
    
    def _get_user_profile_analysis(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı profil analizi"""
        query = """
        SELECT 
            u.*,
            COUNT(DISTINCT o.id) as total_orders,
            COALESCE(SUM(o.total_amount), 0) as total_spent,
            AVG(o.total_amount) as avg_order_value,
            COUNT(DISTINCT p.id) as posts_created,
            COUNT(DISTINCT c.id) as comments_made,
            DATEDIFF(NOW(), u.created_at) as days_since_registration,
            DATEDIFF(NOW(), u.last_login_at) as days_since_last_login
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        LEFT JOIN posts p ON u.id = p.user_id
        LEFT JOIN comments c ON u.id = c.user_id
        WHERE u.id = %s
        GROUP BY u.id
        """
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, [user_id])
        result = cursor.fetchone()
        
        if result:
            # Kullanıcı segmenti belirle
            result['user_segment'] = self._determine_user_segment(result)
            result['engagement_level'] = self._calculate_user_engagement_level(result)
            result['purchase_power'] = self._estimate_purchase_power(result)
        
        return result or {}
    
    def _determine_user_segment(self, user_data: Dict) -> str:
        """Kullanıcı segmentini belirle"""
        total_spent = user_data.get('total_spent', 0)
        total_orders = user_data.get('total_orders', 0)
        days_active = user_data.get('days_since_registration', 0)
        
        if total_spent > 2000 and total_orders > 10:
            return 'VIP Customer'
        elif total_spent > 1000 and total_orders > 5:
            return 'Premium Customer'
        elif total_spent > 500 and total_orders > 2:
            return 'Regular Customer'
        elif total_orders > 0:
            return 'Occasional Buyer'
        else:
            return 'Browser'
    
    def _estimate_purchase_power(self, user_data: Dict) -> Dict[str, Any]:
        """Satın alma gücü tahmini"""
        avg_order = user_data.get('avg_order_value', 0)
        total_orders = user_data.get('total_orders', 0)
        
        # Basit model
        if avg_order > 500:
            power_level = 'High'
            budget_range = {'min': 200, 'max': 1000}
        elif avg_order > 200:
            power_level = 'Medium'
            budget_range = {'min': 50, 'max': 500}
        elif avg_order > 0:
            power_level = 'Low'
            budget_range = {'min': 10, 'max': 200}
        else:
            power_level = 'Unknown'
            budget_range = {'min': 0, 'max': 100}
        
        return {
            'level': power_level,
            'estimated_budget_range': budget_range,
            'avg_order_value': avg_order,
            'purchase_frequency': 'High' if total_orders > 10 else 'Medium' if total_orders > 3 else 'Low'
        }