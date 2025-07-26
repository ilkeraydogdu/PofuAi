"""
Order Item Model
Sipariş kalemi modeli
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.Database.base_model import BaseModel

class OrderItem(BaseModel):
    """Sipariş kalemi modeli"""
    
    __table__ = 'order_items'
    __fillable__ = [
        'order_id', 'product_id', 'product_name', 'quantity',
        'unit_price', 'total_price', 'options'
    ]
    __hidden__ = []
    __timestamps__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._order = None
        self._product = None
    
    @property
    def total(self) -> float:
        """Toplam fiyat"""
        return self.quantity * self.unit_price
    
    def order(self):
        """Bağlı olduğu sipariş"""
        if self._order is None:
            from .Order import Order
            self._order = Order.find(self.order_id)
        return self._order
    
    def product(self):
        """Ürün bilgisi"""
        if self._product is None:
            from .Product import Product
            self._product = Product.find(self.product_id)
        return self._product
    
    def to_dict(self) -> Dict[str, Any]:
        """Modeli dictionary'e çevir"""
        data = super().to_dict()
        
        # Ek özellikler ekle
        data['total'] = self.total
        
        # İlişkili veriler
        if self.product():
            data['product'] = {
                'id': self.product().id,
                'name': self.product().name,
                'image_url': self.product().image_url
            }
        
        return data
    
    @classmethod
    def by_order(cls, order_id: int) -> List['OrderItem']:
        """Siparişe ait kalemleri getir"""
        return cls.where({'order_id': order_id})
    
    @classmethod
    def by_product(cls, product_id: int) -> List['OrderItem']:
        """Ürüne ait sipariş kalemlerini getir"""
        return cls.where({'product_id': product_id}) 