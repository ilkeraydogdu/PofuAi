"""
Order Model
Sipariş modeli ve ilişkileri
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.Database.base_model import BaseModel

class Order(BaseModel):
    """Sipariş modeli"""
    
    __table__ = 'orders'
    __fillable__ = [
        'user_id', 'order_number', 'status', 'total_amount',
        'shipping_address', 'billing_address', 'payment_method',
        'payment_status', 'notes', 'tracking_number'
    ]
    __hidden__ = []
    __timestamps__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._user = None
        self._items = None
    
    @property
    def is_pending(self) -> bool:
        """Beklemede mi"""
        return self.status == 'pending'
    
    @property
    def is_processing(self) -> bool:
        """İşleniyor mu"""
        return self.status == 'processing'
    
    @property
    def is_shipped(self) -> bool:
        """Kargolandı mı"""
        return self.status == 'shipped'
    
    @property
    def is_delivered(self) -> bool:
        """Teslim edildi mi"""
        return self.status == 'delivered'
    
    @property
    def is_cancelled(self) -> bool:
        """İptal edildi mi"""
        return self.status == 'cancelled'
    
    @property
    def is_paid(self) -> bool:
        """Ödendi mi"""
        return self.payment_status == 'paid'
    
    @property
    def is_pending_payment(self) -> bool:
        """Ödeme bekliyor mu"""
        return self.payment_status == 'pending'
    
    @property
    def is_failed_payment(self) -> bool:
        """Ödeme başarısız mı"""
        return self.payment_status == 'failed'
    
    def user(self):
        """Siparişin sahibi"""
        if self._user is None:
            from .User import User
            self._user = User.find(self.user_id)
        return self._user
    
    def items(self):
        """Sipariş kalemleri"""
        if self._items is None:
            from .OrderItem import OrderItem
            self._items = OrderItem.where({'order_id': self.id})
        return self._items
    
    def items_count(self) -> int:
        """Kalem sayısı"""
        return len(self.items())
    
    def total_items(self) -> int:
        """Toplam ürün sayısı"""
        total = 0
        for item in self.items():
            total += item.quantity
        return total
    
    def mark_as_paid(self) -> bool:
        """Ödendi olarak işaretle"""
        self.payment_status = 'paid'
        return self.save()
    
    def mark_as_processing(self) -> bool:
        """İşleniyor olarak işaretle"""
        self.status = 'processing'
        return self.save()
    
    def mark_as_shipped(self, tracking_number: str = None) -> bool:
        """Kargolandı olarak işaretle"""
        self.status = 'shipped'
        if tracking_number:
            self.tracking_number = tracking_number
        return self.save()
    
    def mark_as_delivered(self) -> bool:
        """Teslim edildi olarak işaretle"""
        self.status = 'delivered'
        return self.save()
    
    def cancel(self, reason: str = None) -> bool:
        """Siparişi iptal et"""
        self.status = 'cancelled'
        if reason:
            self.notes = f"İptal nedeni: {reason}"
        return self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Modeli dictionary'e çevir"""
        data = super().to_dict()
        
        # Ek özellikler ekle
        data['is_pending'] = self.is_pending
        data['is_processing'] = self.is_processing
        data['is_shipped'] = self.is_shipped
        data['is_delivered'] = self.is_delivered
        data['is_cancelled'] = self.is_cancelled
        data['is_paid'] = self.is_paid
        data['is_pending_payment'] = self.is_pending_payment
        data['is_failed_payment'] = self.is_failed_payment
        data['items_count'] = self.items_count()
        data['total_items'] = self.total_items()
        
        # İlişkili veriler
        if self.user():
            data['user'] = {
                'id': self.user().id,
                'name': self.user().name,
                'email': self.user().email
            }
        
        if self.items():
            data['items'] = [item.to_dict() for item in self.items()]
        
        return data
    
    @classmethod
    def generate_order_number(cls) -> str:
        """Sipariş numarası oluştur"""
        import random
        import string
        
        # Yıl + ay + gün + rastgele 4 karakter
        now = datetime.now()
        date_part = now.strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"ORD{date_part}{random_part}"
    
    @classmethod
    def by_user(cls, user_id: int) -> List['Order']:
        """Kullanıcının siparişlerini getir"""
        return cls.where({'user_id': user_id}).order_by('created_at', 'desc')
    
    @classmethod
    def by_status(cls, status: str) -> List['Order']:
        """Duruma göre siparişleri getir"""
        return cls.where({'status': status})
    
    @classmethod
    def by_payment_status(cls, payment_status: str) -> List['Order']:
        """Ödeme durumuna göre siparişleri getir"""
        return cls.where({'payment_status': payment_status})
    
    @classmethod
    def recent(cls, limit: int = 10) -> List['Order']:
        """Son siparişleri getir"""
        return cls.order_by('created_at', 'desc').limit(limit).get()
    
    @classmethod
    def pending_payment(cls) -> List['Order']:
        """Ödeme bekleyen siparişleri getir"""
        return cls.where({'payment_status': 'pending'})
    
    @classmethod
    def create_order(cls, user_id: int, items: List[Dict[str, Any]], **kwargs) -> Optional['Order']:
        """Yeni sipariş oluştur"""
        try:
            # Sipariş numarası oluştur
            order_number = cls.generate_order_number()
            
            # Toplam tutarı hesapla
            total_amount = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
            
            # Sipariş oluştur
            order_data = {
                'user_id': user_id,
                'order_number': order_number,
                'total_amount': total_amount,
                'status': 'pending',
                'payment_status': 'pending',
                **kwargs
            }
            
            order = cls(**order_data)
            if order.save():
                # Sipariş kalemlerini oluştur
                from .OrderItem import OrderItem
                for item_data in items:
                    item_data['order_id'] = order.id
                    OrderItem.create(item_data)
                
                return order
            
            return None
            
        except Exception as e:
            print(f"Order creation error: {str(e)}")
            return None 