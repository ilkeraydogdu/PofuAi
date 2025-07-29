"""
Stripe Payment API Implementation
Dünya çapında kullanılan Stripe ödeme sistemi entegrasyonu

Bu modül Stripe'ın Payment Intents, Checkout Sessions,
Subscriptions ve diğer ödeme çözümlerini destekler.
"""

import stripe
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import hashlib
import hmac

from .base_service import BaseService


class StripePaymentAPI(BaseService):
    """Stripe Payment API Implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.secret_key = config.get('secret_key')
        self.publishable_key = config.get('publishable_key')
        self.webhook_secret = config.get('webhook_secret')
        self.api_version = config.get('api_version', '2023-10-16')
        
        # Stripe API'yi yapılandır
        stripe.api_key = self.secret_key
        stripe.api_version = self.api_version
        
        # Test kartları
        self.test_cards = {
            'visa': '4242424242424242',
            'visa_debit': '4000056655665556',
            'mastercard': '5555555555554444',
            'mastercard_debit': '5200828282828210',
            'amex': '378282246310005',
            'declined_card': '4000000000000002',
            'insufficient_funds': '4000000000009995',
            'expired_card': '4000000000000069',
            'incorrect_cvc': '4000000000000127',
            'processing_error': '4000000000000119',
            '3ds_required': '4000002500003155',
            '3ds_optional': '4000002760003184'
        }
    
    def create_payment_intent(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Payment Intent oluşturma
        
        Args:
            payment_data: Ödeme bilgileri
            
        Returns:
            API yanıtı
        """
        try:
            # Zorunlu alanlar
            if 'amount' not in payment_data:
                raise ValueError("Amount gerekli")
            
            # Payment Intent parametrelerini hazırla
            intent_params = {
                'amount': int(payment_data['amount'] * 100),  # Cent cinsine çevir
                'currency': payment_data.get('currency', 'usd'),
                'automatic_payment_methods': {
                    'enabled': True
                },
                'metadata': payment_data.get('metadata', {})
            }
            
            # Müşteri bilgileri
            if 'customer_id' in payment_data:
                intent_params['customer'] = payment_data['customer_id']
            elif 'customer_email' in payment_data:
                # Müşteri oluştur
                customer = stripe.Customer.create(
                    email=payment_data['customer_email'],
                    name=payment_data.get('customer_name'),
                    metadata=payment_data.get('customer_metadata', {})
                )
                intent_params['customer'] = customer.id
            
            # Açıklama
            if 'description' in payment_data:
                intent_params['description'] = payment_data['description']
            
            # Fatura bilgileri
            if 'receipt_email' in payment_data:
                intent_params['receipt_email'] = payment_data['receipt_email']
            
            # Shipping bilgileri
            if 'shipping' in payment_data:
                intent_params['shipping'] = payment_data['shipping']
            
            # 3D Secure ayarları
            if payment_data.get('require_3ds'):
                intent_params['payment_method_options'] = {
                    'card': {
                        'request_three_d_secure': 'automatic'
                    }
                }
            
            # Payment Intent oluştur
            intent = stripe.PaymentIntent.create(**intent_params)
            
            return {
                'success': True,
                'payment_intent_id': intent.id,
                'client_secret': intent.client_secret,
                'status': intent.status,
                'amount': intent.amount / 100,
                'currency': intent.currency,
                'data': intent
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe Payment Intent hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code if hasattr(e, 'code') else None
            }
        except Exception as e:
            self.logger.error(f"Payment Intent oluşturma hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_checkout_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Checkout Session oluşturma
        
        Args:
            session_data: Session bilgileri
            
        Returns:
            API yanıtı
        """
        try:
            # Zorunlu alanlar
            if 'line_items' not in session_data:
                raise ValueError("Line items gerekli")
            if 'success_url' not in session_data:
                raise ValueError("Success URL gerekli")
            if 'cancel_url' not in session_data:
                raise ValueError("Cancel URL gerekli")
            
            # Session parametrelerini hazırla
            session_params = {
                'payment_method_types': session_data.get('payment_methods', ['card']),
                'line_items': session_data['line_items'],
                'mode': session_data.get('mode', 'payment'),
                'success_url': session_data['success_url'],
                'cancel_url': session_data['cancel_url']
            }
            
            # Müşteri bilgileri
            if 'customer_id' in session_data:
                session_params['customer'] = session_data['customer_id']
            elif 'customer_email' in session_data:
                session_params['customer_email'] = session_data['customer_email']
            
            # Fatura ayarları
            if session_data.get('collect_billing_address'):
                session_params['billing_address_collection'] = 'required'
            
            if session_data.get('collect_shipping_address'):
                session_params['shipping_address_collection'] = {
                    'allowed_countries': session_data.get('allowed_countries', ['US'])
                }
            
            # Metadata
            if 'metadata' in session_data:
                session_params['metadata'] = session_data['metadata']
            
            # Abonelik modu için
            if session_data.get('mode') == 'subscription':
                if 'subscription_data' in session_data:
                    session_params['subscription_data'] = session_data['subscription_data']
            
            # Checkout Session oluştur
            session = stripe.checkout.Session.create(**session_params)
            
            return {
                'success': True,
                'session_id': session.id,
                'checkout_url': session.url,
                'status': session.status,
                'data': session
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe Checkout Session hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code if hasattr(e, 'code') else None
            }
        except Exception as e:
            self.logger.error(f"Checkout Session oluşturma hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_subscription(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Abonelik oluşturma
        
        Args:
            subscription_data: Abonelik bilgileri
            
        Returns:
            API yanıtı
        """
        try:
            # Zorunlu alanlar
            if 'customer_id' not in subscription_data:
                raise ValueError("Customer ID gerekli")
            if 'price_id' not in subscription_data:
                raise ValueError("Price ID gerekli")
            
            # Abonelik parametrelerini hazırla
            subscription_params = {
                'customer': subscription_data['customer_id'],
                'items': [
                    {
                        'price': subscription_data['price_id'],
                        'quantity': subscription_data.get('quantity', 1)
                    }
                ]
            }
            
            # Deneme süresi
            if 'trial_period_days' in subscription_data:
                subscription_params['trial_period_days'] = subscription_data['trial_period_days']
            
            # Kupon
            if 'coupon' in subscription_data:
                subscription_params['coupon'] = subscription_data['coupon']
            
            # Metadata
            if 'metadata' in subscription_data:
                subscription_params['metadata'] = subscription_data['metadata']
            
            # Ödeme davranışı
            subscription_params['payment_behavior'] = subscription_data.get('payment_behavior', 'default_incomplete')
            
            # Expand ayarları
            subscription_params['expand'] = ['latest_invoice.payment_intent']
            
            # Abonelik oluştur
            subscription = stripe.Subscription.create(**subscription_params)
            
            return {
                'success': True,
                'subscription_id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice.payment_intent else None,
                'data': subscription
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe Subscription hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code if hasattr(e, 'code') else None
            }
        except Exception as e:
            self.logger.error(f"Subscription oluşturma hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Müşteri oluşturma
        
        Args:
            customer_data: Müşteri bilgileri
            
        Returns:
            API yanıtı
        """
        try:
            # Müşteri parametrelerini hazırla
            customer_params = {}
            
            if 'email' in customer_data:
                customer_params['email'] = customer_data['email']
            
            if 'name' in customer_data:
                customer_params['name'] = customer_data['name']
            
            if 'phone' in customer_data:
                customer_params['phone'] = customer_data['phone']
            
            if 'description' in customer_data:
                customer_params['description'] = customer_data['description']
            
            if 'address' in customer_data:
                customer_params['address'] = customer_data['address']
            
            if 'shipping' in customer_data:
                customer_params['shipping'] = customer_data['shipping']
            
            if 'metadata' in customer_data:
                customer_params['metadata'] = customer_data['metadata']
            
            # Müşteri oluştur
            customer = stripe.Customer.create(**customer_params)
            
            return {
                'success': True,
                'customer_id': customer.id,
                'email': customer.email,
                'name': customer.name,
                'data': customer
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe Customer hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code if hasattr(e, 'code') else None
            }
        except Exception as e:
            self.logger.error(f"Customer oluşturma hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_refund(self, refund_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        İade oluşturma
        
        Args:
            refund_data: İade bilgileri
            
        Returns:
            API yanıtı
        """
        try:
            # Zorunlu alanlar
            if 'payment_intent_id' not in refund_data and 'charge_id' not in refund_data:
                raise ValueError("Payment Intent ID veya Charge ID gerekli")
            
            # İade parametrelerini hazırla
            refund_params = {}
            
            if 'payment_intent_id' in refund_data:
                refund_params['payment_intent'] = refund_data['payment_intent_id']
            elif 'charge_id' in refund_data:
                refund_params['charge'] = refund_data['charge_id']
            
            if 'amount' in refund_data:
                refund_params['amount'] = int(refund_data['amount'] * 100)
            
            if 'reason' in refund_data:
                refund_params['reason'] = refund_data['reason']
            
            if 'metadata' in refund_data:
                refund_params['metadata'] = refund_data['metadata']
            
            # İade oluştur
            refund = stripe.Refund.create(**refund_params)
            
            return {
                'success': True,
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'status': refund.status,
                'reason': refund.reason,
                'data': refund
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe Refund hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code if hasattr(e, 'code') else None
            }
        except Exception as e:
            self.logger.error(f"Refund oluşturma hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_webhook(self, payload: str, signature: str) -> Dict[str, Any]:
        """
        Webhook doğrulama
        
        Args:
            payload: Webhook payload
            signature: Stripe signature
            
        Returns:
            Doğrulama sonucu
        """
        try:
            # Webhook'u doğrula
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            return {
                'success': True,
                'event': event,
                'event_type': event['type'],
                'data': event['data']['object']
            }
            
        except ValueError as e:
            self.logger.error(f"Webhook payload hatası: {str(e)}")
            return {
                'success': False,
                'error': 'Invalid payload'
            }
        except stripe.error.SignatureVerificationError as e:
            self.logger.error(f"Webhook signature hatası: {str(e)}")
            return {
                'success': False,
                'error': 'Invalid signature'
            }
        except Exception as e:
            self.logger.error(f"Webhook doğrulama hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Payment Intent bilgilerini getir
        
        Args:
            payment_intent_id: Payment Intent ID
            
        Returns:
            Payment Intent bilgileri
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'success': True,
                'payment_intent_id': intent.id,
                'status': intent.status,
                'amount': intent.amount / 100,
                'currency': intent.currency,
                'client_secret': intent.client_secret,
                'data': intent
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Payment Intent getirme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code if hasattr(e, 'code') else None
            }
    
    def cancel_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Payment Intent iptal etme
        
        Args:
            payment_intent_id: Payment Intent ID
            
        Returns:
            İptal sonucu
        """
        try:
            intent = stripe.PaymentIntent.cancel(payment_intent_id)
            
            return {
                'success': True,
                'payment_intent_id': intent.id,
                'status': intent.status,
                'data': intent
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Payment Intent iptal hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code if hasattr(e, 'code') else None
            }
    
    def list_customers(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Müşteri listesi
        
        Args:
            filters: Filtreleme parametreleri
            
        Returns:
            Müşteri listesi
        """
        try:
            params = filters or {}
            customers = stripe.Customer.list(**params)
            
            return {
                'success': True,
                'customers': customers.data,
                'has_more': customers.has_more,
                'data': customers
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Customer listesi hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code if hasattr(e, 'code') else None
            }
    
    def get_test_cards(self) -> Dict[str, Any]:
        """Test kartları bilgilerini döndür"""
        return {
            'success': True,
            'cards': self.test_cards,
            'info': {
                'visa': 'Başarılı ödeme',
                'visa_debit': 'Başarılı debit kart ödemesi',
                'mastercard': 'Başarılı Mastercard ödemesi',
                'declined_card': 'Reddedilen kart',
                'insufficient_funds': 'Yetersiz bakiye',
                'expired_card': 'Süresi dolmuş kart',
                'incorrect_cvc': 'Yanlış CVC',
                'processing_error': 'İşlem hatası',
                '3ds_required': '3D Secure gerekli',
                '3ds_optional': '3D Secure opsiyonel'
            }
        }
    
    def format_line_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ürün listesini Stripe formatına çevir
        
        Args:
            items: Ürün listesi
            
        Returns:
            Stripe formatında line items
        """
        line_items = []
        for item in items:
            line_item = {
                'price_data': {
                    'currency': item.get('currency', 'usd'),
                    'product_data': {
                        'name': item.get('name', 'Ürün'),
                    },
                    'unit_amount': int(item.get('price', 0) * 100),
                },
                'quantity': item.get('quantity', 1),
            }
            
            # Ürün açıklaması
            if 'description' in item:
                line_item['price_data']['product_data']['description'] = item['description']
            
            # Ürün görseli
            if 'images' in item:
                line_item['price_data']['product_data']['images'] = item['images']
            
            line_items.append(line_item)
        
        return line_items