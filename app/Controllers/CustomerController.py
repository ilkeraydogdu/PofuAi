"""
Customer Controller
Müşteri portal controller'ı
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.Controllers.BaseController import BaseController
from app.Middleware.AuthMiddleware import auth_required
from core.Services.error_handler import error_handler
from core.Services.UIService import UIService
from core.Services.ComponentService import ComponentService
from app.Models.User import User
from app.Models.Product import Product
from app.Models.Order import Order
from app.Models.Review import Review
from app.Models.Notification import Notification
from core.Database.connection import get_connection
import json
import datetime
from flask import jsonify, request, session
from typing import Dict, Any, List

class CustomerController(BaseController):
    """Customer controller'ı"""
    
    def __init__(self):
        super().__init__()
    
    @auth_required
    def dashboard(self):
        """Müşteri ana dashboard"""
        try:
            customer = self.get_current_user()
            
            # Müşteri istatistikleri
            stats = self._get_customer_stats(customer['id'])
            
            # Son siparişler
            recent_orders = self._get_recent_orders(customer['id'])
            
            # Favoriler
            favorites = self._get_customer_favorites(customer['id'])
            
            # Öneriler
            recommendations = self._get_product_recommendations(customer['id'])
            
            # Bildirimler
            notifications = self._get_customer_notifications(customer['id'])
            
            data = {
                'title': 'Müşteri Paneli - Dashboard',
                'customer': customer,
                'stats': stats,
                'recent_orders': recent_orders,
                'favorites': favorites,
                'recommendations': recommendations,
                'notifications': notifications
            }
            
            return self.view('customer.dashboard', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @auth_required
    def orders(self):
        """Sipariş geçmişi"""
        try:
            customer = self.get_current_user()
            
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            status = request.args.get('status', 'all')
            
            # Siparişleri getir
            orders_data = self._get_customer_orders(customer['id'], page, per_page, status)
            
            data = {
                'title': 'Sipariş Geçmişi',
                'customer': customer,
                'orders': orders_data['orders'],
                'pagination': orders_data['pagination'],
                'status': status,
                'order_stats': self._get_customer_order_stats(customer['id'])
            }
            
            return self.view('customer.orders', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @auth_required
    def order_detail(self, order_id: int):
        """Sipariş detayı"""
        try:
            customer = self.get_current_user()
            
            # Sipariş detayını getir
            order = self._get_order_detail(order_id, customer['id'])
            
            if not order:
                return self.error_response('Sipariş bulunamadı', 404)
            
            # Sipariş takip bilgileri
            tracking_info = self._get_order_tracking(order_id)
            
            data = {
                'title': f'Sipariş Detayı - #{order["order_number"]}',
                'customer': customer,
                'order': order,
                'tracking_info': tracking_info
            }
            
            return self.view('customer.order_detail', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @auth_required
    def favorites(self):
        """Favori ürünler"""
        try:
            customer = self.get_current_user()
            
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            category = request.args.get('category', 'all')
            
            # Favori ürünleri getir
            favorites_data = self._get_customer_favorites_paginated(customer['id'], page, per_page, category)
            
            # Kategorileri getir
            categories = self._get_favorite_categories(customer['id'])
            
            data = {
                'title': 'Favori Ürünler',
                'customer': customer,
                'favorites': favorites_data['favorites'],
                'pagination': favorites_data['pagination'],
                'categories': categories,
                'category': category
            }
            
            return self.view('customer.favorites', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @auth_required
    def add_to_favorites(self):
        """Favorilere ekleme"""
        if request.method == 'POST':
            try:
                customer = self.get_current_user()
                data = self._safe_get_input()
                
                product_id = data.get('product_id')
                if not product_id:
                    return self.error_response('Ürün ID gerekli')
                
                # Favorilere ekle
                success = self._add_to_favorites(customer['id'], product_id)
                
                if success:
                    return self.success_response('Ürün favorilere eklendi')
                else:
                    return self.error_response('Ürün favorilere eklenemedi')
                    
            except Exception as e:
                return error_handler.handle_error(e, self.request)
    
    @auth_required
    def remove_from_favorites(self):
        """Favorilerden çıkarma"""
        if request.method == 'POST':
            try:
                customer = self.get_current_user()
                data = self._safe_get_input()
                
                product_id = data.get('product_id')
                if not product_id:
                    return self.error_response('Ürün ID gerekli')
                
                # Favorilerden çıkar
                success = self._remove_from_favorites(customer['id'], product_id)
                
                if success:
                    return self.success_response('Ürün favorilerden çıkarıldı')
                else:
                    return self.error_response('Ürün favorilerden çıkarılamadı')
                    
            except Exception as e:
                return error_handler.handle_error(e, self.request)
    
    @auth_required
    def reviews(self):
        """Değerlendirmeler"""
        try:
            customer = self.get_current_user()
            
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            
            # Değerlendirmeleri getir
            reviews_data = self._get_customer_reviews(customer['id'], page, per_page)
            
            # Değerlendirme bekleyen ürünler
            pending_reviews = self._get_pending_reviews(customer['id'])
            
            data = {
                'title': 'Değerlendirmelerim',
                'customer': customer,
                'reviews': reviews_data['reviews'],
                'pagination': reviews_data['pagination'],
                'pending_reviews': pending_reviews,
                'review_stats': self._get_customer_review_stats(customer['id'])
            }
            
            return self.view('customer.reviews', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @auth_required
    def add_review(self):
        """Değerlendirme ekleme"""
        if request.method == 'GET':
            try:
                customer = self.get_current_user()
                product_id = request.args.get('product_id')
                order_id = request.args.get('order_id')
                
                if not product_id or not order_id:
                    return self.error_response('Ürün ID ve Sipariş ID gerekli')
                
                # Ürün bilgilerini getir
                product = self._get_product_for_review(product_id, order_id, customer['id'])
                
                if not product:
                    return self.error_response('Ürün bulunamadı veya değerlendirme yapma yetkiniz yok')
                
                data = {
                    'title': 'Değerlendirme Yap',
                    'customer': customer,
                    'product': product,
                    'order_id': order_id
                }
                
                return self.view('customer.add_review', data)
                
            except Exception as e:
                return error_handler.handle_error(e, self.request)
        
        elif request.method == 'POST':
            try:
                customer = self.get_current_user()
                data = self._safe_get_input()
                
                # Değerlendirme validasyonu
                validation_result = self._validate_review_data(data)
                if not validation_result['valid']:
                    return self.error_response('Validasyon hatası', validation_result['errors'])
                
                # Değerlendirme oluştur
                review_id = self._create_review(customer['id'], data)
                
                if review_id:
                    return self.success_response('Değerlendirme başarıyla eklendi', {'review_id': review_id})
                else:
                    return self.error_response('Değerlendirme eklenirken hata oluştu')
                    
            except Exception as e:
                return error_handler.handle_error(e, self.request)
    
    @auth_required
    def profile(self):
        """Profil yönetimi"""
        if request.method == 'GET':
            try:
                customer = self.get_current_user()
                
                # Profil bilgilerini getir
                profile_data = self._get_customer_profile(customer['id'])
                
                data = {
                    'title': 'Profil Bilgileri',
                    'customer': customer,
                    'profile': profile_data
                }
                
                return self.view('customer.profile', data)
                
            except Exception as e:
                return error_handler.handle_error(e, self.request)
        
        elif request.method == 'POST':
            try:
                customer = self.get_current_user()
                data = self._safe_get_input()
                
                # Profil güncelleme
                success = self._update_customer_profile(customer['id'], data)
                
                if success:
                    return self.success_response('Profil başarıyla güncellendi')
                else:
                    return self.error_response('Profil güncellenirken hata oluştu')
                    
            except Exception as e:
                return error_handler.handle_error(e, self.request)
    
    @auth_required
    def addresses(self):
        """Adres yönetimi"""
        try:
            customer = self.get_current_user()
            
            # Adresleri getir
            addresses = self._get_customer_addresses(customer['id'])
            
            data = {
                'title': 'Adres Defteri',
                'customer': customer,
                'addresses': addresses
            }
            
            return self.view('customer.addresses', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @auth_required
    def notifications(self):
        """Bildirimler"""
        try:
            customer = self.get_current_user()
            
            # Sayfalama parametreleri
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            filter_type = request.args.get('type', 'all')
            
            # Bildirimleri getir
            notifications_data = self._get_customer_notifications_paginated(customer['id'], page, per_page, filter_type)
            
            # Okunmamış bildirim sayısı
            unread_count = self._get_unread_notifications_count(customer['id'])
            
            data = {
                'title': 'Bildirimler',
                'customer': customer,
                'notifications': notifications_data['notifications'],
                'pagination': notifications_data['pagination'],
                'unread_count': unread_count,
                'filter_type': filter_type
            }
            
            return self.view('customer.notifications', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @auth_required
    def support(self):
        """Destek ve yardım"""
        try:
            customer = self.get_current_user()
            
            # Destek biletleri
            support_tickets = self._get_customer_support_tickets(customer['id'])
            
            # FAQ
            faq_items = self._get_faq_items()
            
            data = {
                'title': 'Destek ve Yardım',
                'customer': customer,
                'support_tickets': support_tickets,
                'faq_items': faq_items
            }
            
            return self.view('customer.support', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # Helper Methods
    def _get_customer_stats(self, customer_id: int) -> Dict[str, Any]:
        """Müşteri istatistikleri"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Toplam sipariş sayısı
            cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = %s", (customer_id,))
            total_orders = cursor.fetchone()[0]
            
            # Toplam harcama
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0) FROM orders 
                WHERE user_id = %s AND status = 'completed'
            """, (customer_id,))
            total_spent = cursor.fetchone()[0]
            
            # Favori ürün sayısı
            cursor.execute("SELECT COUNT(*) FROM user_favorites WHERE user_id = %s", (customer_id,))
            favorite_count = cursor.fetchone()[0]
            
            # Değerlendirme sayısı
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE user_id = %s", (customer_id,))
            review_count = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'total_orders': total_orders,
                'total_spent': float(total_spent) if total_spent else 0,
                'favorite_count': favorite_count,
                'review_count': review_count
            }
            
        except Exception as e:
            self.logger.error(f"Customer stats error: {e}")
            return {
                'total_orders': 0,
                'total_spent': 0,
                'favorite_count': 0,
                'review_count': 0
            }
    
    def _get_recent_orders(self, customer_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Son siparişler"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT o.*, 
                       (SELECT COUNT(*) FROM order_items oi WHERE oi.order_id = o.id) as item_count
                FROM orders o
                WHERE o.user_id = %s
                ORDER BY o.created_at DESC
                LIMIT %s
            """, (customer_id, limit))
            
            orders = cursor.fetchall()
            cursor.close()
            
            return orders
            
        except Exception as e:
            self.logger.error(f"Recent orders error: {e}")
            return []
    
    def _get_customer_favorites(self, customer_id: int, limit: int = 8) -> List[Dict[str, Any]]:
        """Müşteri favorileri"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT p.*, uf.created_at as favorited_at
                FROM products p
                JOIN user_favorites uf ON p.id = uf.product_id
                WHERE uf.user_id = %s
                ORDER BY uf.created_at DESC
                LIMIT %s
            """, (customer_id, limit))
            
            favorites = cursor.fetchall()
            cursor.close()
            
            return favorites
            
        except Exception as e:
            self.logger.error(f"Customer favorites error: {e}")
            return []
    
    def _get_product_recommendations(self, customer_id: int, limit: int = 6) -> List[Dict[str, Any]]:
        """Ürün önerileri"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Basit öneri algoritması - müşterinin geçmiş siparişlerine benzer kategorilerden ürünler
            cursor.execute("""
                SELECT DISTINCT p.*
                FROM products p
                JOIN order_items oi ON p.category_id = oi.product_id
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = %s
                AND p.id NOT IN (
                    SELECT oi2.product_id FROM order_items oi2 
                    JOIN orders o2 ON oi2.order_id = o2.id 
                    WHERE o2.user_id = %s
                )
                ORDER BY p.created_at DESC
                LIMIT %s
            """, (customer_id, customer_id, limit))
            
            recommendations = cursor.fetchall()
            cursor.close()
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Product recommendations error: {e}")
            return []
    
    def _get_customer_notifications(self, customer_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Müşteri bildirimleri"""
        try:
            notification_model = Notification()
            return notification_model.get_user_notifications(customer_id, limit)
            
        except Exception as e:
            self.logger.error(f"Customer notifications error: {e}")
            return []
    
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