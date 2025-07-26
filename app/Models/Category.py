"""
Category Model
Kategori modeli ve ilişkileri
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.Database.base_model import BaseModel

class Category(BaseModel):
    """Kategori modeli"""
    
    __table__ = 'categories'
    __fillable__ = [
        'name', 'slug', 'description', 'parent_id', 'image',
        'status', 'sort_order', 'meta_title', 'meta_description'
    ]
    __hidden__ = []
    __timestamps__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._parent = None
        self._children = None
        self._products = None
    
    @property
    def url(self) -> str:
        """Kategori URL'i"""
        return f"/categories/{self.slug or self.id}"
    
    @property
    def image_url(self) -> str:
        """Kategori resim URL'i"""
        if self.image:
            return f"/uploads/categories/{self.image}"
        return "/static/assets/images/default-category.jpg"
    
    @property
    def is_active(self) -> bool:
        """Aktif mi"""
        return self.status == 'active'
    
    @property
    def is_parent(self) -> bool:
        """Üst kategori mi"""
        return self.parent_id is None
    
    @property
    def is_child(self) -> bool:
        """Alt kategori mi"""
        return self.parent_id is not None
    
    def parent(self):
        """Üst kategori"""
        if self._parent is None and self.parent_id:
            self._parent = Category.find(self.parent_id)
        return self._parent
    
    def children(self):
        """Alt kategoriler"""
        if self._children is None:
            self._children = Category.where({'parent_id': self.id, 'status': 'active'})
        return self._children
    
    def products(self):
        """Kategoriye ait ürünler"""
        if self._products is None:
            from .Product import Product
            self._products = Product.where({'category': self.name, 'status': 'active'})
        return self._products
    
    def products_count(self) -> int:
        """Ürün sayısı"""
        return len(self.products())
    
    def all_children(self) -> List['Category']:
        """Tüm alt kategoriler (recursive)"""
        children = []
        for child in self.children():
            children.append(child)
            children.extend(child.all_children())
        return children
    
    def breadcrumb(self) -> List['Category']:
        """Breadcrumb (gezinti) yolu"""
        breadcrumb = []
        current = self
        
        while current:
            breadcrumb.insert(0, current)
            current = current.parent()
        
        return breadcrumb
    
    def to_dict(self) -> Dict[str, Any]:
        """Modeli dictionary'e çevir"""
        data = super().to_dict()
        
        # Ek özellikler ekle
        data['url'] = self.url
        data['image_url'] = self.image_url
        data['is_active'] = self.is_active
        data['is_parent'] = self.is_parent
        data['is_child'] = self.is_child
        data['products_count'] = self.products_count()
        
        # İlişkili veriler
        if self.parent():
            data['parent'] = {
                'id': self.parent().id,
                'name': self.parent().name,
                'url': self.parent().url
            }
        
        if self.children():
            data['children'] = [child.to_dict() for child in self.children()]
        
        return data
    
    @classmethod
    def active(cls) -> List['Category']:
        """Aktif kategorileri getir"""
        return cls.where({'status': 'active'})
    
    @classmethod
    def parents(cls) -> List['Category']:
        """Üst kategorileri getir"""
        return cls.where({'parent_id': None, 'status': 'active'})
    
    @classmethod
    def children_of(cls, parent_id: int) -> List['Category']:
        """Belirli kategorinin alt kategorilerini getir"""
        return cls.where({'parent_id': parent_id, 'status': 'active'})
    
    @classmethod
    def by_slug(cls, slug: str) -> Optional['Category']:
        """Slug'a göre kategori bul"""
        return cls.first({'slug': slug, 'status': 'active'})
    
    @classmethod
    def by_name(cls, name: str) -> Optional['Category']:
        """İsme göre kategori bul"""
        return cls.first({'name': name})
    
    @classmethod
    def tree(cls) -> List[Dict[str, Any]]:
        """Kategori ağacını getir"""
        def build_tree(parent_id=None):
            categories = cls.children_of(parent_id) if parent_id else cls.parents()
            tree = []
            
            for category in categories:
                node = category.to_dict()
                node['children'] = build_tree(category.id)
                tree.append(node)
            
            return tree
        
        return build_tree()
    
    @classmethod
    def create_category(cls, data: Dict[str, Any]) -> Optional['Category']:
        """Yeni kategori oluştur"""
        from core.Services.validators import Validator
        
        # Validasyon
        validator = Validator()
        rules = {
            'name': 'required|min:2|max:100',
            'description': 'max:500'
        }
        
        if 'parent_id' in data and data['parent_id']:
            rules['parent_id'] = 'exists:categories,id'
        
        if not validator.validate(data, rules):
            return None
        
        # Slug oluştur
        if 'slug' not in data:
            from core.Helpers import generate_slug
            data['slug'] = generate_slug(data['name'])
        
        # Kategoriyi oluştur
        category = cls(**data)
        if category.save():
            return category
        
        return None 