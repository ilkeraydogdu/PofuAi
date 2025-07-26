"""
Route Sistemi Kullanım Örnekleri
Router, SEO, Sitemap ve URL yönetimi örnekleri
"""

from .router import Router, get, post, put, delete, route
from .seo_manager import SEOManager, generate_meta_html
from .sitemap import SitemapGenerator, create_sitemap
from .url_generator import URLGenerator, url_for, asset_url
from .middleware import AuthMiddleware, SEOMiddleware, SecurityMiddleware

# Router örnekleri
def example_router():
    """Router kullanım örnekleri"""
    print("=== Router Örnekleri ===")
    
    # Basit rota tanımlama
    @get('/')
    def home():
        return {'message': 'Ana sayfa', 'title': 'PofuAi - Ana Sayfa'}
    
    @get('/hakkimizda')
    def about():
        return {'message': 'Hakkımızda sayfası', 'title': 'Hakkımızda'}
    
    @get('/iletisim')
    def contact():
        return {'message': 'İletişim sayfası', 'title': 'İletişim'}
    
    # Parametreli rota
    @get('/blog/{id}')
    def blog_post(id):
        return {'message': f'Blog yazısı {id}', 'title': f'Blog Yazısı {id}'}
    
    # POST rota
    @post('/api/users')
    def create_user():
        return {'message': 'Kullanıcı oluşturuldu', 'status': 'success'}
    
    # PUT rota
    @put('/api/users/{id}')
    def update_user(id):
        return {'message': f'Kullanıcı {id} güncellendi', 'status': 'success'}
    
    # DELETE rota
    @delete('/api/users/{id}')
    def delete_user(id):
        return {'message': f'Kullanıcı {id} silindi', 'status': 'success'}
    
    # Rota grubu
    with router.group('/api/v1', middleware=[AuthMiddleware()]):
        @router.get('/posts')
        def get_posts():
            return {'posts': [], 'status': 'success'}
        
        @router.post('/posts')
        def create_post():
            return {'message': 'Post oluşturuldu', 'status': 'success'}

# SEO örnekleri
def example_seo():
    """SEO yönetimi örnekleri"""
    print("\n=== SEO Örnekleri ===")
    
    # SEO Manager oluştur
    seo = SEOManager(base_url="https://pofuai.com")
    
    # Sayfa verileri
    page_data = {
        'title': 'PofuAi - Yapay Zeka Destekli Platform',
        'description': 'Modern ve ölçeklenebilir yapay zeka destekli web platformu. AI teknolojileri ile güçlendirilmiş çözümler.',
        'keywords': ['yapay zeka', 'AI', 'platform', 'teknoloji', 'çözümler'],
        'canonical': 'https://pofuai.com',
        'og_image': 'https://pofuai.com/images/og-image.jpg',
        'og_type': 'website',
        'twitter_card': 'summary_large_image',
        'schema': {
            'type': 'Organization',
            'name': 'PofuAi',
            'url': 'https://pofuai.com',
            'description': 'Yapay zeka destekli platform'
        }
    }
    
    # Meta tag'leri oluştur
    meta_tags = seo.generate_meta_tags(page_data)
    print("Meta Tags:", meta_tags)
    
    # HTML formatında meta tag'ler
    meta_html = seo.generate_meta_html(meta_tags)
    print("Meta HTML:", meta_html[:200] + "...")
    
    # Blog yazısı için SEO
    blog_data = {
        'title': 'Yapay Zeka ve Gelecek',
        'description': 'Yapay zeka teknolojilerinin gelecekteki rolü ve etkileri hakkında detaylı analiz.',
        'content': 'Yapay zeka teknolojileri günümüzde...',
        'author_name': 'Ahmet Yılmaz',
        'date_published': '2024-01-15T10:00:00Z',
        'schema': {
            'type': 'Article',
            'author_name': 'Ahmet Yılmaz',
            'publisher_name': 'PofuAi'
        }
    }
    
    blog_meta = seo.generate_meta_tags(blog_data)
    print("Blog Meta Tags:", blog_meta)

# Sitemap örnekleri
def example_sitemap():
    """Sitemap oluşturma örnekleri"""
    print("\n=== Sitemap Örnekleri ===")
    
    # Sitemap generator oluştur
    sitemap = SitemapGenerator(base_url="https://pofuai.com", output_dir="public")
    
    # Statik sayfalar ekle
    static_pages = [
        {'url': '/', 'priority': 1.0, 'changefreq': 'daily'},
        {'url': '/hakkimizda', 'priority': 0.8, 'changefreq': 'monthly'},
        {'url': '/iletisim', 'priority': 0.8, 'changefreq': 'monthly'},
        {'url': '/blog', 'priority': 0.9, 'changefreq': 'weekly'},
        {'url': '/urunler', 'priority': 0.9, 'changefreq': 'weekly'}
    ]
    
    sitemap.add_static_pages(static_pages)
    
    # Blog yazıları ekle
    blog_posts = [
        {'slug': 'yapay-zeka-ve-gelecek', 'updated_at': '2024-01-15'},
        {'slug': 'ai-teknolojileri', 'updated_at': '2024-01-10'},
        {'slug': 'machine-learning', 'updated_at': '2024-01-05'}
    ]
    
    sitemap.add_blog_posts(blog_posts)
    
    # Ürün sayfaları ekle
    products = [
        {
            'slug': 'ai-platform',
            'name': 'AI Platform',
            'description': 'Yapay zeka platformu',
            'image': 'https://pofuai.com/images/ai-platform.jpg',
            'updated_at': '2024-01-12'
        }
    ]
    
    sitemap.add_product_pages(products)
    
    # Sitemap'i kaydet
    filepath = sitemap.save_sitemap("sitemap.xml")
    print(f"Sitemap kaydedildi: {filepath}")
    
    # Robots.txt oluştur
    robots_path = sitemap.save_robots_txt()
    print(f"Robots.txt kaydedildi: {robots_path}")
    
    # İstatistikler
    stats = sitemap.get_statistics()
    print("Sitemap İstatistikleri:", stats)

# URL Generator örnekleri
def example_url_generator():
    """URL oluşturma örnekleri"""
    print("\n=== URL Generator Örnekleri ===")
    
    # URL Generator oluştur
    url_gen = URLGenerator(base_url="https://pofuai.com", secure=True)
    
    # Named route'ları kaydet
    url_gen.register_named_route('home', '/')
    url_gen.register_named_route('blog', '/blog/{id}')
    url_gen.register_named_route('user', '/user/{id}/profile')
    
    # URL'ler oluştur
    home_url = url_gen.route('home')
    print(f"Ana sayfa URL: {home_url}")
    
    blog_url = url_gen.route('blog', {'id': 123})
    print(f"Blog URL: {blog_url}")
    
    user_url = url_gen.route('user', {'id': 'ahmet'})
    print(f"Kullanıcı URL: {user_url}")
    
    # Asset URL'leri
    css_url = url_gen.css('style')
    print(f"CSS URL: {css_url}")
    
    js_url = url_gen.js('app')
    print(f"JavaScript URL: {js_url}")
    
    image_url = url_gen.image('logo.png')
    print(f"Resim URL: {image_url}")
    
    # API URL'leri
    api_url = url_gen.api('users')
    print(f"API URL: {api_url}")
    
    # Admin URL'leri
    admin_url = url_gen.admin('dashboard')
    print(f"Admin URL: {admin_url}")
    
    # İmzalı URL
    signed_url = url_gen.signed_url('/download/file.pdf', expires=3600)
    print(f"İmzalı URL: {signed_url}")
    
    # URL doğrulama
    is_valid = url_gen.is_valid_url('https://pofuai.com')
    print(f"URL geçerli mi: {is_valid}")

# Middleware örnekleri
def example_middleware():
    """Middleware kullanım örnekleri"""
    print("\n=== Middleware Örnekleri ===")
    
    # Auth middleware
    auth_middleware = AuthMiddleware(
        redirect_url="/login",
        public_routes=['/', '/login', '/register', '/blog']
    )
    
    # SEO middleware
    seo_middleware = SEOMiddleware()
    
    # Security middleware
    security_middleware = SecurityMiddleware()
    
    # Test request
    test_request = {
        'method': 'GET',
        'path': '/admin/dashboard',
        'ip': '192.168.1.1',
        'headers': {
            'User-Agent': 'Mozilla/5.0',
            'X-Requested-With': 'XMLHttpRequest'
        },
        'session': {
            'user': {'id': 1, 'name': 'Ahmet'}
        }
    }
    
    # Middleware'leri test et
    print("Auth Middleware Test:")
    auth_result = auth_middleware.handle(test_request)
    print(f"Sonuç: {auth_result}")
    
    print("\nSEO Middleware Test:")
    seo_result = seo_middleware.handle(test_request)
    print(f"Sonuç: {seo_result}")
    print(f"SEO Data: {test_request.get('seo_data')}")
    
    print("\nSecurity Middleware Test:")
    security_result = security_middleware.handle(test_request)
    print(f"Sonuç: {security_result}")

# Entegrasyon örneği
def example_integration():
    """Tüm sistemlerin entegrasyonu"""
    print("\n=== Entegrasyon Örneği ===")
    
    # Router oluştur
    router = Router()
    
    # SEO Manager
    seo = SEOManager(base_url="https://pofuai.com")
    
    # URL Generator
    url_gen = URLGenerator(base_url="https://pofuai.com")
    
    # Blog sayfası handler'ı
    @router.get('/blog/{slug}', name='blog.show')
    def show_blog_post(slug):
        # Blog verilerini al (veritabanından)
        blog_data = {
            'title': f'Blog Yazısı - {slug}',
            'content': 'Blog içeriği...',
            'author': 'Ahmet Yılmaz',
            'published_at': '2024-01-15'
        }
        
        # SEO verilerini hazırla
        seo_data = {
            'title': blog_data['title'],
            'description': blog_data['content'][:160] + '...',
            'canonical': url_gen.url(f'/blog/{slug}'),
            'og_type': 'article',
            'schema': {
                'type': 'Article',
                'author_name': blog_data['author'],
                'date_published': blog_data['published_at']
            }
        }
        
        # Meta tag'leri oluştur
        meta_html = seo.generate_meta_html(seo_data)
        
        return {
            'html': f'<html><head>{meta_html}</head><body>Blog içeriği...</body></html>',
            'data': blog_data
        }
    
    # URL oluştur
    blog_url = url_gen.route('blog.show', {'slug': 'yapay-zeka-ve-gelecek'})
    print(f"Blog URL: {blog_url}")
    
    # Sitemap'e ekle
    sitemap = SitemapGenerator(base_url="https://pofuai.com")
    sitemap.add_url(blog_url, changefreq='monthly', priority=0.7)
    
    print("Entegrasyon tamamlandı!")

if __name__ == "__main__":
    # Örnekleri çalıştır
    example_router()
    example_seo()
    example_sitemap()
    example_url_generator()
    example_middleware()
    example_integration() 