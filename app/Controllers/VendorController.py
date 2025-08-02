"""
Vendor Controller
Satıcı yönetim paneli controller'ı
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.Controllers.BaseController import BaseController
from app.Middleware.AuthMiddleware import auth_required, vendor_required
from core.Services.error_handler import error_handler
from core.Services.UIService import UIService
from core.Services.ComponentService import ComponentService
from app.Models.User import User
from app.Models.Product import Product
from app.Models.Order import Order
from core.Database.connection import get_connection
import json
import datetime
from flask import jsonify, request, session
from typing import Dict, Any, List

class VendorController(BaseController):
    """Vendor controller'ı"""
    
    def __init__(self):
        super().__init__()
    
    @vendor_required
    def dashboard(self):
        """Vendor ana dashboard"""
        try:
            vendor = self.get_current_user()
            
            # Vendor istatistikleri
            stats = self._get_vendor_stats(vendor['id'])
            
            # Son siparişler
            recent_orders = self._get_recent_orders(vendor['id'])
            
            # Ürün performansı
            product_performance = self._get_product_performance(vendor['id'])
            
            # Gelir analizi
            revenue_analysis = self._get_revenue_analysis(vendor['id'])
            
            data = {
                'title': 'Satıcı Paneli - Dashboard',
                'vendor': vendor,
                'stats': stats,
                'recent_orders': recent_orders,
                'product_performance': product_performance,
                'revenue_analysis': revenue_analysis,
                'notifications': self._get_vendor_notifications(vendor['id'])
            }
            
            return self.view('vendor.dashboard', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @vendor_required
    def products(self):
        """Ürün yönetimi sayfası"""
        try:
            vendor = self.get_current_user()
            
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            search = request.args.get('search', '')
            category = request.args.get('category', 'all')
            status = request.args.get('status', 'all')
            
            # Ürünleri getir
            products_data = self._get_vendor_products(vendor['id'], page, per_page, search, category, status)
            
            # Kategorileri getir
            categories = self._get_product_categories()
            
            data = {
                'title': 'Ürün Yönetimi',
                'vendor': vendor,
                'products': products_data['products'],
                'pagination': products_data['pagination'],
                'categories': categories,
                'search': search,
                'category': category,
                'status': status,
                'product_stats': self._get_vendor_product_stats(vendor['id'])
            }
            
            return self.view('vendor.products', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @vendor_required
    def add_product(self):
        """Yeni ürün ekleme"""
        if request.method == 'GET':
            try:
                vendor = self.get_current_user()
                categories = self._get_product_categories()
                
                data = {
                    'title': 'Yeni Ürün Ekle',
                    'vendor': vendor,
                    'categories': categories,
                    'integrations': self._get_available_integrations()
                }
                
                return self.view('vendor.add_product', data)
                
            except Exception as e:
                return error_handler.handle_error(e, self.request)
        
        elif request.method == 'POST':
            try:
                vendor = self.get_current_user()
                data = self._safe_get_input()
                
                # Ürün validasyonu
                validation_result = self._validate_product_data(data)
                if not validation_result['valid']:
                    return self.error_response('Validasyon hatası', validation_result['errors'])
                
                # Ürün oluştur
                product_id = self._create_product(vendor['id'], data)
                
                if product_id:
                    # Entegrasyonlara gönder
                    if data.get('auto_publish'):
                        self._publish_to_integrations(product_id, data.get('selected_integrations', []))
                    
                    return self.success_response('Ürün başarıyla eklendi', {'product_id': product_id})
                else:
                    return self.error_response('Ürün eklenirken hata oluştu')
                    
            except Exception as e:
                return error_handler.handle_error(e, self.request)
    
    @vendor_required
    def orders(self):
        """Sipariş yönetimi"""
        try:
            vendor = self.get_current_user()
            
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            status = request.args.get('status', 'all')
            date_range = request.args.get('date_range', '30')
            
            # Siparişleri getir
            orders_data = self._get_vendor_orders(vendor['id'], page, per_page, status, date_range)
            
            data = {
                'title': 'Sipariş Yönetimi',
                'vendor': vendor,
                'orders': orders_data['orders'],
                'pagination': orders_data['pagination'],
                'status': status,
                'date_range': date_range,
                'order_stats': self._get_vendor_order_stats(vendor['id'])
            }
            
            return self.view('vendor.orders', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @vendor_required
    def analytics(self):
        """Analitik ve raporlar"""
        try:
            vendor = self.get_current_user()
            
            # Tarih aralığı
            date_range = request.args.get('date_range', '30')
            
            # Analitik verileri
            analytics_data = {
                'sales_chart': self._get_sales_chart_data(vendor['id'], date_range),
                'product_performance': self._get_detailed_product_performance(vendor['id'], date_range),
                'customer_analytics': self._get_customer_analytics(vendor['id'], date_range),
                'revenue_breakdown': self._get_revenue_breakdown(vendor['id'], date_range),
                'marketplace_performance': self._get_marketplace_performance(vendor['id'], date_range)
            }
            
            data = {
                'title': 'Analitik ve Raporlar',
                'vendor': vendor,
                'date_range': date_range,
                'analytics': analytics_data
            }
            
            return self.view('vendor.analytics', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @vendor_required
    def integrations(self):
        """Entegrasyon yönetimi"""
        try:
            vendor = self.get_current_user()
            
            # Mevcut entegrasyonlar
            active_integrations = self._get_vendor_integrations(vendor['id'])
            
            # Kullanılabilir entegrasyonlar
            available_integrations = self._get_available_integrations()
            
            # Entegrasyon istatistikleri
            integration_stats = self._get_integration_stats(vendor['id'])
            
            data = {
                'title': 'Entegrasyon Yönetimi',
                'vendor': vendor,
                'active_integrations': active_integrations,
                'available_integrations': available_integrations,
                'integration_stats': integration_stats
            }
            
            return self.view('vendor.integrations', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @vendor_required
    def messages(self):
        """Müşteri mesajları"""
        try:
            vendor = self.get_current_user()
            
            # Mesajları getir
            messages = self._get_vendor_messages(vendor['id'])
            
            # Okunmamış mesaj sayısı
            unread_count = self._get_unread_message_count(vendor['id'])
            
            data = {
                'title': 'Müşteri Mesajları',
                'vendor': vendor,
                'messages': messages,
                'unread_count': unread_count
            }
            
            return self.view('vendor.messages', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @vendor_required
    def settings(self):
        """Vendor ayarları"""
        if request.method == 'GET':
            try:
                vendor = self.get_current_user()
                vendor_settings = self._get_vendor_settings(vendor['id'])
                
                data = {
                    'title': 'Satıcı Ayarları',
                    'vendor': vendor,
                    'settings': vendor_settings
                }
                
                return self.view('vendor.settings', data)
                
            except Exception as e:
                return error_handler.handle_error(e, self.request)
        
        elif request.method == 'POST':
            try:
                vendor = self.get_current_user()
                data = self._safe_get_input()
                
                # Ayarları güncelle
                success = self._update_vendor_settings(vendor['id'], data)
                
                if success:
                    return self.success_response('Ayarlar başarıyla güncellendi')
                else:
                    return self.error_response('Ayarlar güncellenirken hata oluştu')
                    
            except Exception as e:
                return error_handler.handle_error(e, self.request)
    
    # Helper Methods
    def _get_vendor_stats(self, vendor_id: int) -> Dict[str, Any]:
        """Vendor istatistikleri"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Toplam ürün sayısı
            cursor.execute("SELECT COUNT(*) FROM products WHERE vendor_id = %s", (vendor_id,))
            total_products = cursor.fetchone()[0]
            
            # Toplam sipariş sayısı
            cursor.execute("""
                SELECT COUNT(*) FROM orders o 
                JOIN order_items oi ON o.id = oi.order_id 
                JOIN products p ON oi.product_id = p.id 
                WHERE p.vendor_id = %s
            """, (vendor_id,))
            total_orders = cursor.fetchone()[0]
            
            # Bu ay gelir
            cursor.execute("""
                SELECT COALESCE(SUM(oi.price * oi.quantity), 0) FROM orders o 
                JOIN order_items oi ON o.id = oi.order_id 
                JOIN products p ON oi.product_id = p.id 
                WHERE p.vendor_id = %s AND MONTH(o.created_at) = MONTH(NOW())
            """, (vendor_id,))
            monthly_revenue = cursor.fetchone()[0]
            
            # Aktif ürün sayısı
            cursor.execute("SELECT COUNT(*) FROM products WHERE vendor_id = %s AND status = 'active'", (vendor_id,))
            active_products = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'total_products': total_products,
                'total_orders': total_orders,
                'monthly_revenue': float(monthly_revenue) if monthly_revenue else 0,
                'active_products': active_products
            }
            
        except Exception as e:
            self.logger.error(f"Vendor stats error: {e}")
            return {
                'total_products': 0,
                'total_orders': 0,
                'monthly_revenue': 0,
                'active_products': 0
            }
    
    def _get_recent_orders(self, vendor_id: int) -> List[Dict[str, Any]]:
        """Son siparişler"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT o.id, o.order_number, o.total_amount, o.status, o.created_at,
                       u.name as customer_name, u.email as customer_email
                FROM orders o 
                JOIN order_items oi ON o.id = oi.order_id 
                JOIN products p ON oi.product_id = p.id 
                JOIN users u ON o.user_id = u.id
                WHERE p.vendor_id = %s
                ORDER BY o.created_at DESC
                LIMIT 10
            """, (vendor_id,))
            
            orders = cursor.fetchall()
            cursor.close()
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Recent orders error: {e}")
            return []
    
    def _get_product_performance(self, vendor_id: int) -> List[Dict[str, Any]]:
        """Ürün performansı"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT p.id, p.name, p.price, 
                       COUNT(oi.id) as order_count,
                       SUM(oi.quantity) as total_sold,
                       SUM(oi.price * oi.quantity) as total_revenue
                FROM products p
                LEFT JOIN order_items oi ON p.id = oi.product_id
                WHERE p.vendor_id = %s
                GROUP BY p.id
                ORDER BY total_revenue DESC
                LIMIT 10
            """, (vendor_id,))
            
            performance = cursor.fetchall()
            cursor.close()
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Product performance error: {e}")
            return []
    
    def _get_revenue_analysis(self, vendor_id: int) -> Dict[str, Any]:
        """Gelir analizi"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Son 12 ay gelir
            cursor.execute("""
                SELECT MONTH(o.created_at) as month, 
                       SUM(oi.price * oi.quantity) as revenue
                FROM orders o 
                JOIN order_items oi ON o.id = oi.order_id 
                JOIN products p ON oi.product_id = p.id 
                WHERE p.vendor_id = %s AND o.created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
                GROUP BY MONTH(o.created_at)
                ORDER BY month
            """, (vendor_id,))
            
            monthly_data = cursor.fetchall()
            cursor.close()
            
            return {
                'monthly_revenue': monthly_data,
                'total_12_month': sum([row[1] for row in monthly_data]) if monthly_data else 0
            }
            
        except Exception as e:
            self.logger.error(f"Revenue analysis error: {e}")
            return {'monthly_revenue': [], 'total_12_month': 0}
    
    def _get_vendor_notifications(self, vendor_id: int) -> List[Dict[str, Any]]:
        """Vendor bildirimleri"""
        # Bu method notification model oluşturulduktan sonra implement edilecek
        return [
            {'message': 'Yeni sipariş alındı', 'type': 'info', 'time': '5 dakika önce'},
            {'message': 'Stok seviyesi düşük', 'type': 'warning', 'time': '1 saat önce'}
        ]
    
    def _safe_get_input(self):
        """Form veya JSON verilerini güvenli bir şekilde al"""
        try:
            if request.method == 'POST':
                if request.form:
                    return dict(request.form)
                elif request.json:
                    return request.json
            elif request.method == 'GET':
                return dict(request.args)
            return {}
        except Exception:
            return {}