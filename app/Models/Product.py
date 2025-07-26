"""
Product Model
Ürün modeli ve ilişkileri
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.Database.base_model import BaseModel

class Product(BaseModel):
    """Ürün modeli"""
    
    __table__ = 'products'
    __fillable__ = [
        'name', 'description', 'slug', 'price', 'sale_price',
        'category', 'brand', 'sku', 'stock_quantity', 'weight',
        'dimensions', 'images', 'status', 'featured', 'meta_title',
        'meta_description'
    ]
    __hidden__ = []
    __timestamps__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._category = None
        self._reviews = None
    
    @property
    def current_price(self) -> float:
        """Güncel fiyat (indirimli varsa)"""
        return self.sale_price if self.sale_price else self.price
    
    @property
    def is_on_sale(self) -> bool:
        """İndirimde mi"""
        return self.sale_price is not None and self.sale_price < self.price
    
    @property
    def discount_percentage(self) -> int:
        """İndirim yüzdesi"""
        if self.is_on_sale:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0
    
    @property
    def is_in_stock(self) -> bool:
        """Stokta var mı"""
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self) -> bool:
        """Stok az mı"""
        return 0 < self.stock_quantity <= 10
    
    @property
    def is_out_of_stock(self) -> bool:
        """Stokta yok mu"""
        return self.stock_quantity <= 0
    
    @property
    def url(self) -> str:
        """Ürün URL'i"""
        return f"/products/{self.slug or self.id}"
    
    @property
    def image_url(self) -> str:
        """Ana resim URL'i"""
        if self.images:
            import json
            try:
                image_list = json.loads(self.images)
                if image_list:
                    return f"/uploads/products/{image_list[0]}"
            except:
                pass
        return "/static/assets/images/default-product.jpg"
    
    @property
    def image_urls(self) -> List[str]:
        """Tüm resim URL'leri"""
        if self.images:
            import json
            try:
                image_list = json.loads(self.images)
                return [f"/uploads/products/{img}" for img in image_list]
            except:
                pass
        return [self.image_url]
    
    def category(self):
        """Ürün kategorisi"""
        if self._category is None:
            from .Category import Category
            self._category = Category.find_by_name(self.category)
        return self._category
    
    def reviews(self):
        """Ürün yorumları"""
        if self._reviews is None:
            from .Review import Review
            self._reviews = Review.where({'product_id': self.id, 'status': 'approved'})
        return self._reviews
    
    def average_rating(self) -> float:
        """Ortalama puan"""
        reviews = self.reviews()
        if not reviews:
            return 0.0
        
        total_rating = sum(review.rating for review in reviews)
        return round(total_rating / len(reviews), 1)
    
    def reviews_count(self) -> int:
        """Yorum sayısı"""
        return len(self.reviews())
    
    def decrease_stock(self, quantity: int) -> bool:
        """Stok azalt"""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            return self.save()
        return False
    
    def increase_stock(self, quantity: int) -> bool:
        """Stok artır"""
        self.stock_quantity += quantity
        return self.save()
    
    def toggle_featured(self) -> bool:
        """Öne çıkan durumunu değiştir"""
        self.featured = not self.featured
        return self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Modeli dictionary'e çevir"""
        data = super().to_dict()
        
        # Ek özellikler ekle
        data['current_price'] = self.current_price
        data['is_on_sale'] = self.is_on_sale
        data['discount_percentage'] = self.discount_percentage
        data['is_in_stock'] = self.is_in_stock
        data['is_low_stock'] = self.is_low_stock
        data['is_out_of_stock'] = self.is_out_of_stock
        data['url'] = self.url
        data['image_url'] = self.image_url
        data['image_urls'] = self.image_urls
        data['average_rating'] = self.average_rating()
        data['reviews_count'] = self.reviews_count()
        
        return data
    
    @classmethod
    def active(cls) -> List['Product']:
        """Aktif ürünleri getir"""
        return cls.where({'status': 'active'})
    
    @classmethod
    def featured(cls) -> List['Product']:
        """Öne çıkan ürünleri getir"""
        return cls.where({'featured': True, 'status': 'active'})
    
    @classmethod
    def on_sale(cls) -> List['Product']:
        """İndirimdeki ürünleri getir"""
        return cls.where('sale_price', '>', 0).where({'status': 'active'})
    
    @classmethod
    def by_category(cls, category: str) -> List['Product']:
        """Kategoriye göre ürünleri getir"""
        return cls.where({'category': category, 'status': 'active'})
    
    @classmethod
    def by_brand(cls, brand: str) -> List['Product']:
        """Markaya göre ürünleri getir"""
        return cls.where({'brand': brand, 'status': 'active'})
    
    @classmethod
    def in_stock(cls) -> List['Product']:
        """Stokta olan ürünleri getir"""
        return cls.where('stock_quantity', '>', 0).where({'status': 'active'})
    
    @classmethod
    def low_stock(cls) -> List['Product']:
        """Stoku az olan ürünleri getir"""
        return cls.where('stock_quantity', '<=', 10).where('stock_quantity', '>', 0)
    
    @classmethod
    def out_of_stock(cls) -> List['Product']:
        """Stokta olmayan ürünleri getir"""
        return cls.where('stock_quantity', '<=', 0)
    
    @classmethod
    def search(cls, query: str, limit: int = 10) -> List['Product']:
        """Ürünlerde arama yap"""
        return cls.where({'status': 'active'}).where_like('name', f'%{query}%').limit(limit).get()
    
    @classmethod
    def popular(cls, limit: int = 10) -> List['Product']:
        """Popüler ürünleri getir"""
        # Satış sayısına göre sırala (basit implementasyon)
        return cls.where({'status': 'active'}).order_by('created_at', 'desc').limit(limit).get()
    
    @classmethod
    def create_product(cls, data: Dict[str, Any]) -> Optional['Product']:
        """Yeni ürün oluştur"""
        from core.Services.validators import Validator
        
        # Validasyon
        validator = Validator()
        rules = {
            'name': 'required|min:2|max:200',
            'description': 'required|min:10',
            'price': 'required|numeric|min:0',
            'category': 'required',
            'stock_quantity': 'required|integer|min:0'
        }
        
        if not validator.validate(data, rules):
            return None
        
        # Slug oluştur
        if 'slug' not in data:
            from core.Helpers import generate_slug
            data['slug'] = generate_slug(data['name'])
        
        # SKU oluştur
        if 'sku' not in data:
            data['sku'] = cls._generate_sku(data['name'])
        
        # Ürünü oluştur
        product = cls(**data)
        if product.save():
            return product
        
        return None
    
    @classmethod
    def _generate_sku(cls, name: str) -> str:
        """SKU oluştur"""
        import random
        import string
        
        # İsmin ilk 3 harfi + rastgele 4 karakter
        prefix = name[:3].upper()
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"{prefix}{random_part}" 