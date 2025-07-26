"""
SEO Manager
Sayfa ve içerikler için SEO ayarları ve meta tag yönetimi
"""
from typing import Dict, Any, Optional

class SEOManager:
    """SEO yönetim sınıfı"""
    
    def __init__(self, base_url: str = ''):
        self.base_url = base_url
        self.default_meta = {
            'title': 'PofuAi - Modüler Web Frameworkü',
            'description': 'Modern ve hızlı web uygulamaları için modüler Python frameworkü',
            'keywords': 'python, framework, web, modular, pofu, ai',
            'author': 'PofuAi Team',
            'robots': 'index, follow',
            'viewport': 'width=device-width, initial-scale=1.0'
        }
    
    def generate_meta_html(self, meta_data: Dict[str, Any]) -> str:
        """Meta verilere göre HTML meta etiketleri oluştur"""
        # Default meta değerlerini kullan
        meta = self.default_meta.copy()
        
        # Sağlanan meta verileriyle birleştir
        meta.update(meta_data)
        
        html = []
        
        # Temel meta etiketleri
        html.append(f'<title>{meta.get("title", "")}</title>')
        
        if 'description' in meta:
            html.append(f'<meta name="description" content="{meta["description"]}">')
        
        if 'keywords' in meta:
            html.append(f'<meta name="keywords" content="{meta["keywords"]}">')
        
        if 'author' in meta:
            html.append(f'<meta name="author" content="{meta["author"]}">')
        
        if 'robots' in meta:
            html.append(f'<meta name="robots" content="{meta["robots"]}">')
        
        if 'viewport' in meta:
            html.append(f'<meta name="viewport" content="{meta["viewport"]}">')
        
        # Canonical URL
        if 'canonical' in meta:
            html.append(f'<link rel="canonical" href="{meta["canonical"]}">')
        
        # Open Graph meta etiketleri
        if 'og_title' in meta:
            html.append(f'<meta property="og:title" content="{meta["og_title"]}">')
        
        if 'og_description' in meta:
            html.append(f'<meta property="og:description" content="{meta["og_description"]}">')
        
        if 'og_image' in meta:
            html.append(f'<meta property="og:image" content="{meta["og_image"]}">')
        
        if 'og_url' in meta:
            html.append(f'<meta property="og:url" content="{meta["og_url"]}">')
        elif 'canonical' in meta:
            html.append(f'<meta property="og:url" content="{meta["canonical"]}">')
        
        if 'og_type' in meta:
            html.append(f'<meta property="og:type" content="{meta["og_type"]}">')
        else:
            html.append('<meta property="og:type" content="website">')
        
        # Twitter Card meta etiketleri
        if 'twitter_card' in meta:
            html.append(f'<meta name="twitter:card" content="{meta["twitter_card"]}">')
        else:
            html.append('<meta name="twitter:card" content="summary_large_image">')
        
        if 'twitter_title' in meta:
            html.append(f'<meta name="twitter:title" content="{meta["twitter_title"]}">')
        elif 'og_title' in meta:
            html.append(f'<meta name="twitter:title" content="{meta["og_title"]}">')
        
        if 'twitter_description' in meta:
            html.append(f'<meta name="twitter:description" content="{meta["twitter_description"]}">')
        elif 'og_description' in meta:
            html.append(f'<meta name="twitter:description" content="{meta["og_description"]}">')
        
        if 'twitter_image' in meta:
            html.append(f'<meta name="twitter:image" content="{meta["twitter_image"]}">')
        elif 'og_image' in meta:
            html.append(f'<meta name="twitter:image" content="{meta["og_image"]}">')
        
        if 'twitter_site' in meta:
            html.append(f'<meta name="twitter:site" content="{meta["twitter_site"]}">')
        
        if 'twitter_creator' in meta:
            html.append(f'<meta name="twitter:creator" content="{meta["twitter_creator"]}">')
        
        # Özel meta etiketleri
        if 'custom_meta' in meta and isinstance(meta['custom_meta'], dict):
            for name, content in meta['custom_meta'].items():
                html.append(f'<meta name="{name}" content="{content}">')
        
        return '\n'.join(html)
    
    def get_meta_data_for_page(self, page_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sayfa türüne göre meta verilerini oluştur"""
        meta = {}
        
        if page_type == 'post':
            title = data.get('title', '')
            description = data.get('description', '') or data.get('excerpt', '')
            
            meta = {
                'title': f"{title} | PofuAi Blog",
                'description': description,
                'og_title': title,
                'og_description': description,
                'og_type': 'article',
                'canonical': f"{self.base_url}/posts/{data.get('slug', '')}"
            }
            
            if 'image' in data:
                meta['og_image'] = f"{self.base_url}/images/{data['image']}"
            
            if 'author' in data:
                meta['author'] = data['author']
                meta['twitter_creator'] = f"@{data.get('twitter_handle', '')}"
            
        elif page_type == 'product':
            title = data.get('name', '')
            description = data.get('description', '')
            
            meta = {
                'title': f"{title} | PofuAi Store",
                'description': description,
                'og_title': title,
                'og_description': description,
                'og_type': 'product',
                'canonical': f"{self.base_url}/products/{data.get('slug', '')}"
            }
            
            if 'image' in data:
                meta['og_image'] = f"{self.base_url}/images/products/{data['image']}"
            
        elif page_type == 'category':
            title = data.get('name', '')
            description = data.get('description', '')
            
            meta = {
                'title': f"{title} | PofuAi Categories",
                'description': description,
                'og_title': f"Browse {title}",
                'og_description': description,
                'canonical': f"{self.base_url}/categories/{data.get('slug', '')}"
            }
            
        return meta
    
    def set_default_meta(self, meta: Dict[str, Any]) -> None:
        """Varsayılan meta değerlerini güncelle"""
        self.default_meta.update(meta)

def generate_meta_html(meta_data: Dict[str, Any], base_url: str = '') -> str:
    """Meta HTML oluşturmak için yardımcı fonksiyon"""
    manager = SEOManager(base_url)
    return manager.generate_meta_html(meta_data) 