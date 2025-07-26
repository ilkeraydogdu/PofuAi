"""
Veritabanı Sistemi Kullanım Örnekleri
Tüm özelliklerin nasıl kullanılacağını gösterir
"""

from .connection import db
from .base_model import BaseModel
from .query_builder import QueryBuilder, table
from .pagination import Pagination, paginate
from .search import AdvancedSearch, search

# Örnek Model Sınıfı
class User(BaseModel):
    __table__ = 'users'
    __fillable__ = ['name', 'email', 'password', 'status']
    __hidden__ = ['password']

# Örnek Kullanımlar

def example_basic_operations():
    """Temel CRUD işlemleri"""
    print("=== Temel CRUD İşlemleri ===")
    
    # Yeni kullanıcı oluştur
    user = User(name="Ahmet Yılmaz", email="ahmet@example.com", password="123456")
    if user.save():
        print(f"Kullanıcı oluşturuldu: {user.id}")
    
    # Kullanıcı bul
    found_user = User.find(user.id)
    if found_user:
        print(f"Kullanıcı bulundu: {found_user.name}")
    
    # Kullanıcı güncelle
    found_user.email = "ahmet.yilmaz@example.com"
    if found_user.save():
        print("Kullanıcı güncellendi")
    
    # Kullanıcı sil
    if found_user.delete():
        print("Kullanıcı silindi")

def example_query_builder():
    """QueryBuilder kullanımı"""
    print("\n=== QueryBuilder Kullanımı ===")
    
    # Basit sorgu
    users = table('users').where('status', '=', 'active').get()
    print(f"Aktif kullanıcı sayısı: {len(users)}")
    
    # Karmaşık sorgu
    results = (table('users')
               .select('id', 'name', 'email')
               .where('status', '=', 'active')
               .where('created_at', '>=', '2024-01-01')
               .order_by('created_at', 'DESC')
               .limit(10)
               .get())
    
    print(f"Son 10 aktif kullanıcı: {len(results)}")
    
    # JOIN örneği
    user_posts = (table('users')
                  .select('users.name', 'posts.title')
                  .join('posts', 'users.id', '=', 'posts.user_id')
                  .where('users.status', '=', 'active')
                  .get())
    
    print(f"Kullanıcı-post sayısı: {len(user_posts)}")

def example_pagination():
    """Sayfalama kullanımı"""
    print("\n=== Sayfalama Kullanımı ===")
    
    # QueryBuilder ile sayfalama
    query = table('users').where('status', '=', 'active')
    pagination = paginate(query, page=1, per_page=5, base_url="/users")
    
    print(f"Toplam kullanıcı: {pagination.total}")
    print(f"Toplam sayfa: {pagination.total_pages}")
    print(f"Mevcut sayfa: {pagination.page}")
    print(f"Sayfa başına: {pagination.per_page}")
    
    # Navigasyon linkleri
    for link in pagination.get_navigation_links():
        print(f"{link['text']}: {link['url']}")

def example_search():
    """Arama ve filtreleme kullanımı"""
    print("\n=== Arama ve Filtreleme ===")
    
    # Basit arama
    search_results = (search('users', 'ahmet', ['name', 'email'])
                      .filter({'status': 'active'})
                      .sort('created_at', 'DESC')
                      .get())
    
    print(f"Arama sonucu: {len(search_results)} kullanıcı")
    
    # Gelişmiş filtreleme
    advanced_results = (search('users')
                        .filter_range('created_at', '2024-01-01', '2024-12-31')
                        .filter_in('status', ['active', 'pending'])
                        .filter_like('email', '@gmail.com')
                        .sort('name', 'ASC')
                        .paginate(1, 10))
    
    print(f"Filtrelenmiş sonuç: {advanced_results['total']} kullanıcı")

def example_connection_pool():
    """Connection pool kullanımı"""
    print("\n=== Connection Pool Test ===")
    
    # Bağlantı testi
    if db.test_connection():
        print("Veritabanı bağlantısı başarılı")
    else:
        print("Veritabanı bağlantısı başarısız")
    
    # Tablo bilgisi
    table_info = db.get_table_info('users')
    print(f"Users tablosu {len(table_info)} sütuna sahip")

def example_transactions():
    """Transaction kullanımı"""
    print("\n=== Transaction Örneği ===")
    
    # Çoklu sorgu transaction
    queries = [
        ("INSERT INTO users (name, email) VALUES (%s, %s)", ("Test User", "test@example.com")),
        ("UPDATE users SET status = %s WHERE email = %s", ("active", "test@example.com"))
    ]
    
    if db.execute_transaction(queries):
        print("Transaction başarılı")
    else:
        print("Transaction başarısız")

if __name__ == "__main__":
    # Örnekleri çalıştır
    example_basic_operations()
    example_query_builder()
    example_pagination()
    example_search()
    example_connection_pool()
    example_transactions() 