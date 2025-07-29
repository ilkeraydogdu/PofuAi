"""
Product Model
Gelişmiş ürün yönetimi modeli
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from core.Database.base_model import BaseModel
import json

class Product(BaseModel):
    """Ürün modeli"""
    
    __table__ = 'products'
    __fillable__ = [
        'name', 'slug', 'description', 'short_description',
        'sku', 'barcode', 'price', 'compare_price', 'cost_price',
        'currency', 'quantity', 'min_quantity', 'max_quantity',
        'category_id', 'brand_id', 'vendor_id', 'user_id',
        'status', 'visibility', 'featured', 'digital',
        'weight', 'length', 'width', 'height', 'weight_unit', 'dimension_unit',
        'seo_title', 'seo_description', 'seo_keywords',
        'tags', 'attributes', 'variations', 'images', 'videos',
        'marketplace_data', 'ai_optimized', 'ai_score',
        'rating', 'review_count', 'sold_count', 'view_count',
        'published_at', 'expires_at'
    ]
    __hidden__ = ['cost_price']
    __timestamps__ = True
    
    # Ürün durumları
    STATUS_DRAFT = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_OUT_OF_STOCK = 'out_of_stock'
    STATUS_DISCONTINUED = 'discontinued'
    
    # Görünürlük seviyeleri
    VISIBILITY_PUBLIC = 'public'
    VISIBILITY_PRIVATE = 'private'
    VISIBILITY_HIDDEN = 'hidden'
    VISIBILITY_CATALOG = 'catalog'
    VISIBILITY_SEARCH = 'search'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._category = None
        self._brand = None
        self._reviews = None
        self._related_products = None
        self._marketplace_listings = None
    
    @property
    def is_available(self) -> bool:
        """Ürün satışa uygun mu"""
        return (
            self.status == self.STATUS_ACTIVE and 
            self.quantity > 0 and
            self.visibility in [self.VISIBILITY_PUBLIC, self.VISIBILITY_CATALOG, self.VISIBILITY_SEARCH]
        )
    
    @property
    def is_on_sale(self) -> bool:
        """İndirimde mi"""
        return self.compare_price and self.price < self.compare_price
    
    @property
    def discount_percentage(self) -> int:
        """İndirim yüzdesi"""
        if not self.is_on_sale:
            return 0
        return int(((self.compare_price - self.price) / self.compare_price) * 100)
    
    @property
    def profit_margin(self) -> Decimal:
        """Kar marjı"""
        if not self.cost_price:
            return Decimal('0')
        return ((self.price - self.cost_price) / self.price) * 100
    
    @property
    def image_urls(self) -> List[str]:
        """Görsel URL'lerini döndür"""
        if not self.images:
            return []
        try:
            images = json.loads(self.images) if isinstance(self.images, str) else self.images
            return [f"/uploads/products/{img}" for img in images]
        except:
            return []
    
    @property
    def main_image_url(self) -> str:
        """Ana görsel URL'i"""
        urls = self.image_urls
        return urls[0] if urls else "/static/assets/images/no-product.png"
    
    @property
    def attribute_list(self) -> Dict[str, Any]:
        """Ürün özelliklerini döndür"""
        if not self.attributes:
            return {}
        try:
            return json.loads(self.attributes) if isinstance(self.attributes, str) else self.attributes
        except:
            return {}
    
    @property
    def tag_list(self) -> List[str]:
        """Etiketleri liste olarak döndür"""
        if not self.tags:
            return []
        try:
            if isinstance(self.tags, str):
                return [tag.strip() for tag in self.tags.split(',')]
            return self.tags
        except:
            return []
    
    def category(self) -> Optional['Category']:
        """Kategoriyi getir"""
        if self._category is None and self.category_id:
            from app.Models.Category import Category
            self._category = Category.find(self.category_id)
        return self._category
    
    def brand(self) -> Optional['Brand']:
        """Markayı getir"""
        if self._brand is None and self.brand_id:
            from app.Models.Brand import Brand
            self._brand = Brand.find(self.brand_id)
        return self._brand
    
    def reviews(self) -> List['Review']:
        """Yorumları getir"""
        if self._reviews is None:
            from app.Models.Review import Review
            self._reviews = Review.where({'product_id': self.id})
        return self._reviews
    
    def related_products(self, limit: int = 4) -> List['Product']:
        """İlgili ürünleri getir"""
        if self._related_products is None:
            # Aynı kategorideki diğer ürünler
            query = """
            SELECT * FROM products 
            WHERE category_id = %s AND id != %s AND status = %s
            ORDER BY rating DESC, sold_count DESC
            LIMIT %s
            """
            self._related_products = self.raw(
                query, 
                (self.category_id, self.id, self.STATUS_ACTIVE, limit)
            )
        return self._related_products
    
    def update_stock(self, quantity: int, operation: str = 'set') -> bool:
        """Stok güncelle"""
        if operation == 'set':
            self.quantity = quantity
        elif operation == 'add':
            self.quantity += quantity
        elif operation == 'subtract':
            self.quantity = max(0, self.quantity - quantity)
        
        # Stok durumunu güncelle
        if self.quantity == 0:
            self.status = self.STATUS_OUT_OF_STOCK
        elif self.status == self.STATUS_OUT_OF_STOCK and self.quantity > 0:
            self.status = self.STATUS_ACTIVE
        
        return self.save()
    
    def update_price(self, new_price: Decimal, compare_price: Optional[Decimal] = None) -> bool:
        """Fiyat güncelle"""
        self.price = new_price
        if compare_price is not None:
            self.compare_price = compare_price
        
        # Fiyat geçmişini kaydet
        self._log_price_history(new_price, compare_price)
        
        return self.save()
    
    def _log_price_history(self, price: Decimal, compare_price: Optional[Decimal] = None):
        """Fiyat geçmişini logla"""
        query = """
        INSERT INTO product_price_history 
        (product_id, price, compare_price, changed_by, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute(query, (
            self.id,
            price,
            compare_price,
            self.user_id,
            datetime.now()
        ))
    
    def add_review(self, user_id: int, rating: int, comment: str) -> bool:
        """Yorum ekle"""
        from app.Models.Review import Review
        
        review = Review(
            product_id=self.id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            status='approved'
        )
        
        if review.save():
            # Ürün istatistiklerini güncelle
            self._update_review_stats()
            return True
        
        return False
    
    def _update_review_stats(self):
        """Yorum istatistiklerini güncelle"""
        query = """
        SELECT 
            COUNT(*) as count,
            AVG(rating) as avg_rating
        FROM reviews
        WHERE product_id = %s AND status = 'approved'
        """
        result = self.db.fetch_one(query, (self.id,))
        
        if result:
            self.review_count = result['count']
            self.rating = round(result['avg_rating'], 1) if result['avg_rating'] else 0
            self.save()
    
    def increment_view_count(self) -> bool:
        """Görüntülenme sayısını artır"""
        self.view_count = (self.view_count or 0) + 1
        return self.save()
    
    def increment_sold_count(self, quantity: int = 1) -> bool:
        """Satış sayısını artır"""
        self.sold_count = (self.sold_count or 0) + quantity
        return self.save()
    
    def sync_to_marketplace(self, marketplace: str, data: Dict[str, Any]) -> bool:
        """Pazaryeri senkronizasyonu"""
        marketplace_data = self.get_marketplace_data()
        marketplace_data[marketplace] = {
            'listing_id': data.get('listing_id'),
            'status': data.get('status', 'active'),
            'url': data.get('url'),
            'synced_at': datetime.now().isoformat(),
            'data': data
        }
        
        self.marketplace_data = json.dumps(marketplace_data)
        return self.save()
    
    def get_marketplace_data(self) -> Dict[str, Any]:
        """Pazaryeri verilerini getir"""
        if not self.marketplace_data:
            return {}
        try:
            return json.loads(self.marketplace_data)
        except:
            return {}
    
    def optimize_with_ai(self, marketplace: Optional[str] = None) -> Dict[str, Any]:
        """AI ile ürünü optimize et"""
        from core.AI.advanced_ai_core import advanced_ai_core
        
        # AI optimizasyonu için veri hazırla
        product_data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'category': self.category().name if self.category() else 'General',
            'features': self.attribute_list,
            'images': self.image_urls
        }
        
        # AI optimizasyonu çalıştır
        if marketplace:
            optimization = advanced_ai_core.optimize_product_listing(
                product_data, 
                marketplace, 
                'editor'
            )
            
            # Optimizasyon sonuçlarını kaydet
            if optimization and not optimization.get('error'):
                self.ai_optimized = True
                self.ai_score = optimization.get('seo_score', 0)
                self.save()
            
            return optimization
        
        return {'error': 'Marketplace not specified'}
    
    def duplicate(self, new_name: Optional[str] = None) -> Optional['Product']:
        """Ürünü kopyala"""
        data = self.to_dict()
        
        # Kopyalanmaması gereken alanları temizle
        exclude_fields = ['id', 'created_at', 'updated_at', 'sold_count', 'view_count', 'rating', 'review_count']
        for field in exclude_fields:
            data.pop(field, None)
        
        # Yeni isim ver
        data['name'] = new_name or f"{self.name} - Kopya"
        data['slug'] = None  # Otomatik oluşturulacak
        data['sku'] = f"{self.sku}_COPY" if self.sku else None
        data['status'] = self.STATUS_DRAFT
        
        # Yeni ürün oluştur
        new_product = Product(**data)
        if new_product.save():
            return new_product
        
        return None
    
    def get_price_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Fiyat geçmişini getir"""
        query = """
        SELECT price, compare_price, created_at
        FROM product_price_history
        WHERE product_id = %s AND created_at >= %s
        ORDER BY created_at DESC
        """
        
        since_date = datetime.now() - timedelta(days=days)
        return self.db.fetch_all(query, (self.id, since_date))
    
    def calculate_shipping_cost(self, destination: Dict[str, Any]) -> Decimal:
        """Kargo ücretini hesapla"""
        if self.digital:
            return Decimal('0')
        
        # Basit kargo hesaplama (ağırlık bazlı)
        base_cost = Decimal('10')  # Sabit ücret
        weight_cost = Decimal(str(self.weight or 0)) * Decimal('0.5')
        
        # Mesafe bazlı ek ücret (basitleştirilmiş)
        distance_multiplier = Decimal('1')
        if destination.get('country') != 'TR':
            distance_multiplier = Decimal('3')
        elif destination.get('city') not in ['İstanbul', 'Ankara', 'İzmir']:
            distance_multiplier = Decimal('1.5')
        
        total_cost = (base_cost + weight_cost) * distance_multiplier
        
        # Ücretsiz kargo kontrolü
        if self.price >= 200:  # 200 TL üzeri ücretsiz kargo
            return Decimal('0')
        
        return round(total_cost, 2)
    
    @classmethod
    def search(cls, query: str, filters: Dict[str, Any] = None) -> List['Product']:
        """Ürün ara"""
        sql = """
        SELECT * FROM products 
        WHERE (name LIKE %s OR description LIKE %s OR tags LIKE %s)
        AND status = %s
        """
        params = [f'%{query}%', f'%{query}%', f'%{query}%', cls.STATUS_ACTIVE]
        
        # Filtreler
        if filters:
            if filters.get('category_id'):
                sql += " AND category_id = %s"
                params.append(filters['category_id'])
            
            if filters.get('brand_id'):
                sql += " AND brand_id = %s"
                params.append(filters['brand_id'])
            
            if filters.get('min_price'):
                sql += " AND price >= %s"
                params.append(filters['min_price'])
            
            if filters.get('max_price'):
                sql += " AND price <= %s"
                params.append(filters['max_price'])
            
            if filters.get('in_stock'):
                sql += " AND quantity > 0"
        
        sql += " ORDER BY rating DESC, sold_count DESC LIMIT 50"
        
        return cls.raw(sql, params)
    
    @classmethod
    def trending(cls, limit: int = 10) -> List['Product']:
        """Trend ürünleri getir"""
        query = """
        SELECT * FROM products
        WHERE status = %s AND quantity > 0
        ORDER BY 
            (view_count * 0.3 + sold_count * 0.7) DESC,
            rating DESC
        LIMIT %s
        """
        return cls.raw(query, (cls.STATUS_ACTIVE, limit))
    
    @classmethod
    def best_sellers(cls, category_id: Optional[int] = None, limit: int = 10) -> List['Product']:
        """En çok satanları getir"""
        query = "SELECT * FROM products WHERE status = %s"
        params = [cls.STATUS_ACTIVE]
        
        if category_id:
            query += " AND category_id = %s"
            params.append(category_id)
        
        query += " ORDER BY sold_count DESC LIMIT %s"
        params.append(limit)
        
        return cls.raw(query, params) 