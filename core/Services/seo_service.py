"""
Advanced SEO Management Service
Dinamik çok dilli SEO yönetimi
"""
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin, urlparse
from core.Services.base_service import BaseService
from core.Services.logger import LoggerService
from core.Services.cache_service import CacheService
from core.Database.connection import get_connection
from dataclasses import dataclass
from enum import Enum
import requests
import re
from flask import request, current_app

class SEOPageType(Enum):
    HOME = "home"
    CATEGORY = "category"
    PRODUCT = "product"
    POST = "post"
    PAGE = "page"
    USER = "user"
    SEARCH = "search"

@dataclass
class SEOData:
    title: str
    description: str
    keywords: List[str]
    canonical_url: str
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_type: str = "website"
    twitter_card: str = "summary_large_image"
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    structured_data: Optional[Dict] = None
    robots: str = "index,follow"
    hreflang: Optional[Dict[str, str]] = None

@dataclass
class SitemapEntry:
    url: str
    lastmod: datetime
    changefreq: str = "weekly"
    priority: float = 0.5
    alternates: Optional[Dict[str, str]] = None

class SEOService(BaseService):
    """Dinamik çok dilli SEO yönetimi"""
    
    def __init__(self):
        super().__init__()
        self.logger = LoggerService.get_logger()
        self.cache = CacheService()
        self.connection = get_connection()
        self.supported_languages = self._get_supported_languages()
        self.default_language = 'tr'
        self.domain = self._get_domain()
        
    def _get_supported_languages(self) -> List[str]:
        """Desteklenen dilleri al"""
        # Config'ten veya veritabanından al
        return ['tr', 'en', 'de', 'fr', 'es', 'ar', 'ru', 'zh']
    
    def _get_domain(self) -> str:
        """Site domain'ini al"""
        return os.getenv('SITE_DOMAIN', 'https://example.com')
    
    def generate_seo_data(self, page_type: SEOPageType, entity_id: int = None, 
                         language: str = None, custom_data: Dict = None) -> SEOData:
        """Sayfa için SEO verilerini oluştur"""
        try:
            language = language or self.default_language
            cache_key = f"seo_{page_type.value}_{entity_id}_{language}"
            
            # Cache'ten kontrol et
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return SEOData(**cached_data)
            
            # Sayfa tipine göre SEO verilerini oluştur
            if page_type == SEOPageType.HOME:
                seo_data = self._generate_home_seo(language)
            elif page_type == SEOPageType.PRODUCT:
                seo_data = self._generate_product_seo(entity_id, language)
            elif page_type == SEOPageType.POST:
                seo_data = self._generate_post_seo(entity_id, language)
            elif page_type == SEOPageType.CATEGORY:
                seo_data = self._generate_category_seo(entity_id, language)
            elif page_type == SEOPageType.PAGE:
                seo_data = self._generate_page_seo(entity_id, language)
            elif page_type == SEOPageType.USER:
                seo_data = self._generate_user_seo(entity_id, language)
            else:
                seo_data = self._generate_default_seo(language)
            
            # Custom data ile merge et
            if custom_data:
                for key, value in custom_data.items():
                    if hasattr(seo_data, key):
                        setattr(seo_data, key, value)
            
            # Hreflang ekle
            seo_data.hreflang = self._generate_hreflang(page_type, entity_id)
            
            # Cache'e kaydet
            self.cache.set(cache_key, seo_data.__dict__, 3600)
            
            return seo_data
            
        except Exception as e:
            self.logger.error(f"SEO data generation error: {str(e)}")
            return self._generate_default_seo(language or self.default_language)
    
    def _generate_home_seo(self, language: str) -> SEOData:
        """Ana sayfa SEO"""
        site_settings = self._get_site_settings(language)
        
        return SEOData(
            title=site_settings.get('site_title', 'PofuAi'),
            description=site_settings.get('site_description', 'Modern web uygulaması'),
            keywords=site_settings.get('site_keywords', ['web', 'uygulama', 'modern']),
            canonical_url=f"{self.domain}/{language}" if language != self.default_language else self.domain,
            og_title=site_settings.get('og_title', site_settings.get('site_title')),
            og_description=site_settings.get('og_description', site_settings.get('site_description')),
            og_image=f"{self.domain}/static/assets/images/og-image.jpg",
            structured_data=self._generate_organization_schema()
        )
    
    def _generate_product_seo(self, product_id: int, language: str) -> SEOData:
        """Ürün SEO"""
        try:
            query = """
            SELECT p.*, pt.name, pt.description, pt.meta_title, pt.meta_description, pt.keywords
            FROM products p
            LEFT JOIN product_translations pt ON p.id = pt.product_id AND pt.language = %s
            WHERE p.id = %s
            """
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, [language, product_id])
            product = cursor.fetchone()
            
            if not product:
                return self._generate_default_seo(language)
            
            # Fallback to default language if translation not found
            if not product['name']:
                cursor.execute(query, [self.default_language, product_id])
                product = cursor.fetchone()
            
            title = product['meta_title'] or f"{product['name']} - {self._get_site_name()}"
            description = product['meta_description'] or product['description'][:160]
            keywords = json.loads(product['keywords']) if product['keywords'] else []
            
            # Structured data
            structured_data = {
                "@context": "https://schema.org/",
                "@type": "Product",
                "name": product['name'],
                "description": description,
                "image": f"{self.domain}/uploads/products/{product['images']}",
                "offers": {
                    "@type": "Offer",
                    "price": str(product['price']),
                    "priceCurrency": "TRY",
                    "availability": "https://schema.org/InStock" if product['stock_quantity'] > 0 else "https://schema.org/OutOfStock"
                }
            }
            
            return SEOData(
                title=title,
                description=description,
                keywords=keywords,
                canonical_url=f"{self.domain}/{language}/product/{product['slug']}",
                og_title=title,
                og_description=description,
                og_image=f"{self.domain}/uploads/products/{product['images']}",
                og_type="product",
                structured_data=structured_data
            )
            
        except Exception as e:
            self.logger.error(f"Product SEO generation error: {str(e)}")
            return self._generate_default_seo(language)
    
    def _generate_post_seo(self, post_id: int, language: str) -> SEOData:
        """Blog post SEO"""
        try:
            query = """
            SELECT p.*, pt.title, pt.content, pt.meta_title, pt.meta_description, pt.keywords,
                   u.name as author_name
            FROM posts p
            LEFT JOIN post_translations pt ON p.id = pt.post_id AND pt.language = %s
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.id = %s
            """
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, [language, post_id])
            post = cursor.fetchone()
            
            if not post:
                return self._generate_default_seo(language)
            
            title = post['meta_title'] or f"{post['title']} - {self._get_site_name()}"
            description = post['meta_description'] or self._extract_excerpt(post['content'])
            keywords = json.loads(post['keywords']) if post['keywords'] else []
            
            # Structured data
            structured_data = {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": post['title'],
                "description": description,
                "author": {
                    "@type": "Person",
                    "name": post['author_name']
                },
                "datePublished": post['created_at'].isoformat(),
                "dateModified": post['updated_at'].isoformat(),
                "publisher": {
                    "@type": "Organization",
                    "name": self._get_site_name(),
                    "logo": {
                        "@type": "ImageObject",
                        "url": f"{self.domain}/static/assets/images/logo.png"
                    }
                }
            }
            
            return SEOData(
                title=title,
                description=description,
                keywords=keywords,
                canonical_url=f"{self.domain}/{language}/post/{post['slug']}",
                og_title=title,
                og_description=description,
                og_type="article",
                structured_data=structured_data
            )
            
        except Exception as e:
            self.logger.error(f"Post SEO generation error: {str(e)}")
            return self._generate_default_seo(language)
    
    def generate_sitemap(self, language: str = None) -> str:
        """Sitemap oluştur"""
        try:
            language = language or self.default_language
            cache_key = f"sitemap_{language}"
            
            # Cache'ten kontrol et
            cached_sitemap = self.cache.get(cache_key)
            if cached_sitemap:
                return cached_sitemap
            
            # Sitemap entries
            entries = []
            
            # Ana sayfa
            entries.append(SitemapEntry(
                url=f"{self.domain}/{language}" if language != self.default_language else self.domain,
                lastmod=datetime.now(),
                changefreq="daily",
                priority=1.0,
                alternates=self._get_page_alternates('home')
            ))
            
            # Ürünler
            entries.extend(self._get_product_sitemap_entries(language))
            
            # Blog posts
            entries.extend(self._get_post_sitemap_entries(language))
            
            # Kategoriler
            entries.extend(self._get_category_sitemap_entries(language))
            
            # Sayfalar
            entries.extend(self._get_page_sitemap_entries(language))
            
            # XML oluştur
            sitemap_xml = self._build_sitemap_xml(entries)
            
            # Cache'e kaydet
            self.cache.set(cache_key, sitemap_xml, 3600)
            
            return sitemap_xml
            
        except Exception as e:
            self.logger.error(f"Sitemap generation error: {str(e)}")
            return self._generate_empty_sitemap()
    
    def generate_robots_txt(self) -> str:
        """Robots.txt oluştur"""
        try:
            cache_key = "robots_txt"
            
            # Cache'ten kontrol et
            cached_robots = self.cache.get(cache_key)
            if cached_robots:
                return cached_robots
            
            # Site ayarlarını al
            site_settings = self._get_site_settings()
            
            robots_content = [
                "User-agent: *",
                "Allow: /",
                "",
                "# Sitemap URLs"
            ]
            
            # Her dil için sitemap ekle
            for lang in self.supported_languages:
                sitemap_url = f"{self.domain}/sitemap-{lang}.xml"
                robots_content.append(f"Sitemap: {sitemap_url}")
            
            robots_content.extend([
                "",
                "# Disallow sensitive areas",
                "Disallow: /admin/",
                "Disallow: /api/",
                "Disallow: /storage/",
                "Disallow: /config/",
                "Disallow: /core/",
                "Disallow: /*?*",  # Query parameters
                "",
                "# Crawl delay",
                "Crawl-delay: 1"
            ])
            
            # Özel kurallar varsa ekle
            if site_settings.get('robots_custom_rules'):
                robots_content.extend([
                    "",
                    "# Custom rules",
                    site_settings['robots_custom_rules']
                ])
            
            robots_txt = "\n".join(robots_content)
            
            # Cache'e kaydet
            self.cache.set(cache_key, robots_txt, 86400)  # 24 saat
            
            return robots_txt
            
        except Exception as e:
            self.logger.error(f"Robots.txt generation error: {str(e)}")
            return "User-agent: *\nAllow: /"
    
    def generate_structured_data(self, page_type: SEOPageType, entity_id: int = None) -> Dict:
        """Structured data oluştur"""
        try:
            if page_type == SEOPageType.HOME:
                return self._generate_organization_schema()
            elif page_type == SEOPageType.PRODUCT:
                return self._generate_product_schema(entity_id)
            elif page_type == SEOPageType.POST:
                return self._generate_article_schema(entity_id)
            else:
                return self._generate_website_schema()
                
        except Exception as e:
            self.logger.error(f"Structured data generation error: {str(e)}")
            return {}
    
    def analyze_seo_performance(self, url: str = None) -> Dict[str, Any]:
        """SEO performans analizi"""
        try:
            analysis = {
                'score': 0,
                'issues': [],
                'recommendations': [],
                'meta_analysis': {},
                'content_analysis': {},
                'technical_analysis': {}
            }
            
            if url:
                # URL'yi analiz et
                analysis.update(self._analyze_url_seo(url))
            else:
                # Site geneli analiz
                analysis.update(self._analyze_site_seo())
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"SEO analysis error: {str(e)}")
            return {'score': 0, 'issues': ['Analysis failed'], 'recommendations': []}
    
    def submit_to_search_engines(self, urls: List[str] = None) -> Dict[str, Any]:
        """Arama motorlarına URL gönder"""
        try:
            results = {
                'google': {'success': False, 'message': ''},
                'bing': {'success': False, 'message': ''},
                'yandex': {'success': False, 'message': ''}
            }
            
            urls = urls or [self.domain]
            
            # Google Search Console API
            google_result = self._submit_to_google(urls)
            results['google'] = google_result
            
            # Bing Webmaster Tools API
            bing_result = self._submit_to_bing(urls)
            results['bing'] = bing_result
            
            # Yandex Webmaster API
            yandex_result = self._submit_to_yandex(urls)
            results['yandex'] = yandex_result
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search engine submission error: {str(e)}")
            return {'error': str(e)}
    
    def _get_site_settings(self, language: str = None) -> Dict[str, Any]:
        """Site ayarlarını al"""
        try:
            language = language or self.default_language
            
            query = """
            SELECT * FROM site_settings 
            WHERE language = %s OR language IS NULL
            ORDER BY language DESC
            """
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, [language])
            settings = cursor.fetchall()
            
            # Settings'i dict'e çevir
            settings_dict = {}
            for setting in settings:
                settings_dict[setting['key']] = setting['value']
            
            return settings_dict
            
        except Exception as e:
            self.logger.error(f"Site settings error: {str(e)}")
            return {}
    
    def _get_site_name(self) -> str:
        """Site adını al"""
        settings = self._get_site_settings()
        return settings.get('site_name', 'PofuAi')
    
    def _generate_hreflang(self, page_type: SEOPageType, entity_id: int = None) -> Dict[str, str]:
        """Hreflang alternatifleri oluştur"""
        hreflang = {}
        
        base_path = ""
        if page_type == SEOPageType.PRODUCT and entity_id:
            # Ürün slug'ını al
            base_path = f"/product/{self._get_entity_slug('products', entity_id)}"
        elif page_type == SEOPageType.POST and entity_id:
            base_path = f"/post/{self._get_entity_slug('posts', entity_id)}"
        elif page_type == SEOPageType.CATEGORY and entity_id:
            base_path = f"/category/{self._get_entity_slug('categories', entity_id)}"
        
        for lang in self.supported_languages:
            if lang == self.default_language:
                hreflang[lang] = f"{self.domain}{base_path}"
            else:
                hreflang[lang] = f"{self.domain}/{lang}{base_path}"
        
        return hreflang
    
    def _get_entity_slug(self, table: str, entity_id: int) -> str:
        """Entity slug'ını al"""
        try:
            query = f"SELECT slug FROM {table} WHERE id = %s"
            cursor = self.connection.cursor()
            cursor.execute(query, [entity_id])
            result = cursor.fetchone()
            return result[0] if result else str(entity_id)
        except Exception:
            return str(entity_id)
    
    def _extract_excerpt(self, content: str, length: int = 160) -> str:
        """İçerikten özet çıkar"""
        if not content:
            return ""
        
        # HTML etiketlerini temizle
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        # Fazla boşlukları temizle
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Belirtilen uzunlukta kes
        if len(clean_content) <= length:
            return clean_content
        
        # Kelime sınırında kes
        truncated = clean_content[:length]
        last_space = truncated.rfind(' ')
        if last_space > length * 0.8:  # %80'inden fazlaysa kelime sınırında kes
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    def _generate_organization_schema(self) -> Dict:
        """Organizasyon schema'sı"""
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self._get_site_name(),
            "url": self.domain,
            "logo": f"{self.domain}/static/assets/images/logo.png",
            "sameAs": [
                # Sosyal medya hesapları buraya eklenecek
            ]
        }
    
    def _build_sitemap_xml(self, entries: List[SitemapEntry]) -> str:
        """Sitemap XML'i oluştur"""
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        urlset.set("xmlns:xhtml", "http://www.w3.org/1999/xhtml")
        
        for entry in entries:
            url_elem = ET.SubElement(urlset, "url")
            
            # URL
            loc = ET.SubElement(url_elem, "loc")
            loc.text = entry.url
            
            # Last modified
            lastmod = ET.SubElement(url_elem, "lastmod")
            lastmod.text = entry.lastmod.strftime("%Y-%m-%d")
            
            # Change frequency
            changefreq = ET.SubElement(url_elem, "changefreq")
            changefreq.text = entry.changefreq
            
            # Priority
            priority = ET.SubElement(url_elem, "priority")
            priority.text = str(entry.priority)
            
            # Hreflang alternates
            if entry.alternates:
                for lang, alt_url in entry.alternates.items():
                    link = ET.SubElement(url_elem, "{http://www.w3.org/1999/xhtml}link")
                    link.set("rel", "alternate")
                    link.set("hreflang", lang)
                    link.set("href", alt_url)
        
        return ET.tostring(urlset, encoding='unicode', method='xml')
    
    def _get_product_sitemap_entries(self, language: str) -> List[SitemapEntry]:
        """Ürün sitemap entries"""
        entries = []
        try:
            query = """
            SELECT p.id, p.slug, p.updated_at
            FROM products p
            WHERE p.status = 'active'
            ORDER BY p.updated_at DESC
            """
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            products = cursor.fetchall()
            
            for product in products:
                url = f"{self.domain}/{language}/product/{product['slug']}" if language != self.default_language else f"{self.domain}/product/{product['slug']}"
                
                entries.append(SitemapEntry(
                    url=url,
                    lastmod=product['updated_at'],
                    changefreq="weekly",
                    priority=0.8,
                    alternates=self._get_page_alternates('product', product['id'])
                ))
                
        except Exception as e:
            self.logger.error(f"Product sitemap entries error: {str(e)}")
        
        return entries
    
    def _get_page_alternates(self, page_type: str, entity_id: int = None) -> Dict[str, str]:
        """Sayfa alternatifleri"""
        alternates = {}
        
        for lang in self.supported_languages:
            if page_type == 'home':
                if lang == self.default_language:
                    alternates[lang] = self.domain
                else:
                    alternates[lang] = f"{self.domain}/{lang}"
            elif page_type == 'product' and entity_id:
                slug = self._get_entity_slug('products', entity_id)
                if lang == self.default_language:
                    alternates[lang] = f"{self.domain}/product/{slug}"
                else:
                    alternates[lang] = f"{self.domain}/{lang}/product/{slug}"
        
        return alternates
    
    def _generate_default_seo(self, language: str) -> SEOData:
        """Varsayılan SEO verisi"""
        site_settings = self._get_site_settings(language)
        
        return SEOData(
            title=site_settings.get('default_title', 'PofuAi'),
            description=site_settings.get('default_description', 'Modern web uygulaması'),
            keywords=site_settings.get('default_keywords', ['web', 'uygulama']),
            canonical_url=self.domain,
            og_title=site_settings.get('default_title', 'PofuAi'),
            og_description=site_settings.get('default_description', 'Modern web uygulaması'),
            og_image=f"{self.domain}/static/assets/images/og-default.jpg"
        )