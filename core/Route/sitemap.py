"""
Sitemap Generator
Dinamik sitemap oluşturma ve SEO optimizasyonu
"""
from typing import Dict, List, Any, Optional
import os
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

class SitemapGenerator:
    """Sitemap XML oluşturma sınıfı"""
    
    def __init__(self, base_url: str = "", output_path: str = "public/sitemap.xml"):
        """
        Sitemap Generator
        
        Args:
            base_url (str): Site ana URL'i (örn: https://example.com)
            output_path (str): Sitemap çıktı dosyası yolu
        """
        self.base_url = base_url.rstrip('/')
        self.output_path = output_path
        self.urls = []
    
    def add_url(self, url: str, lastmod: Optional[str] = None, 
              changefreq: str = "weekly", priority: float = 0.5):
        """
        URL ekle
        
        Args:
            url (str): URL yolu (/ ile başlamalı)
            lastmod (str, optional): Son değişiklik tarihi (ISO 8601 formatında)
            changefreq (str): Değişim sıklığı ("always", "hourly", "daily", "weekly", "monthly", "yearly", "never")
            priority (float): Öncelik (0.0-1.0 arası)
        """
        if not url.startswith('/') and not url.startswith('http'):
            url = '/' + url
        
        if url.startswith('/'):
            full_url = f"{self.base_url}{url}"
        else:
            full_url = url
        
        # Son değişiklik tarihi verilmemişse bugünü kullan
        if not lastmod:
            lastmod = datetime.now().strftime("%Y-%m-%d")
        
        # URL ekle
        self.urls.append({
            'loc': full_url,
            'lastmod': lastmod,
            'changefreq': changefreq,
            'priority': str(priority)
        })
    
    def add_urls_from_list(self, urls: List[Dict[str, Any]]):
        """
        URL listesinden toplu ekle
        
        Args:
            urls (List[Dict]): URL bilgilerini içeren sözlük listesi
        """
        for url_data in urls:
            self.add_url(
                url=url_data.get('url', ''),
                lastmod=url_data.get('lastmod'),
                changefreq=url_data.get('changefreq', 'weekly'),
                priority=url_data.get('priority', 0.5)
            )
    
    def generate_sitemap(self) -> str:
        """Sitemap XML içeriğini oluştur"""
        # XML kök elementi
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        # Her URL için eleman ekle
        for url_data in self.urls:
            url_elem = ET.SubElement(urlset, 'url')
            
            # URL location
            loc = ET.SubElement(url_elem, 'loc')
            loc.text = url_data['loc']
            
            # Son değişiklik tarihi
            if url_data.get('lastmod'):
                lastmod = ET.SubElement(url_elem, 'lastmod')
                lastmod.text = url_data['lastmod']
            
            # Değişim sıklığı
            if url_data.get('changefreq'):
                changefreq = ET.SubElement(url_elem, 'changefreq')
                changefreq.text = url_data['changefreq']
            
            # Öncelik
            if url_data.get('priority'):
                priority = ET.SubElement(url_elem, 'priority')
                priority.text = url_data['priority']
        
        # XML'i düzgün bir şekilde formatla
        rough_xml = ET.tostring(urlset, encoding='UTF-8')
        reparsed = minidom.parseString(rough_xml)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding='UTF-8').decode('UTF-8')
        
        return pretty_xml
    
    def save_sitemap(self) -> str:
        """
        Sitemap XML dosyasını oluştur ve kaydet
        
        Returns:
            str: Kaydedilen dosyanın yolu
        """
        xml_content = self.generate_sitemap()
        
        # Yolu oluştur
        dir_path = os.path.dirname(self.output_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        # Dosyayı yaz
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return self.output_path
    
    def add_pages_from_directory(self, directory_path: str, 
                              url_prefix: str = "/", 
                              file_extensions: List[str] = None,
                              priority: float = 0.5,
                              changefreq: str = "weekly"):
        """
        Belirtilen dizindeki dosyalara göre URL'leri ekle
        
        Args:
            directory_path (str): Dizin yolu
            url_prefix (str): URL ön eki
            file_extensions (List[str], optional): Dosya uzantıları filtreleme ["html", "php"]
            priority (float): Öncelik (0.0-1.0 arası)
            changefreq (str): Değişim sıklığı
        """
        if not file_extensions:
            file_extensions = ["html", "php", "htm"]
        
        # Klasör yoksa çık
        if not os.path.exists(directory_path):
            return
        
        # Dizindeki dosyaları dolaş
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_ext = file.split(".")[-1].lower()
                
                if file_ext in file_extensions:
                    # Dosya yolunu al
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory_path)
                    
                    # index.* dosyalarının adını URL yolundan kaldır
                    if file.startswith("index."):
                        rel_path = os.path.dirname(rel_path)
                    else:
                        # Uzantıyı kaldır
                        rel_path = os.path.splitext(rel_path)[0]
                    
                    # URL yolunu oluştur
                    url_path = url_prefix.rstrip('/') + '/' + rel_path.replace('\\', '/')
                    
                    # Son değişiklik tarihini al
                    lastmod = datetime.fromtimestamp(os.path.getmtime(file_path))
                    lastmod_str = lastmod.strftime("%Y-%m-%d")
                    
                    # URL'yi ekle
                    self.add_url(url_path, lastmod_str, changefreq, priority)

def generate_sitemap_from_models(models: List[Any], base_url: str = "", 
                               output_path: str = "public/sitemap.xml") -> str:
    """
    Modellerden sitemap oluştur
    
    Args:
        models (List): Modellerin listesi
        base_url (str): Site URL'i
        output_path (str): Çıktı dosya yolu
        
    Returns:
        str: Kaydedilen sitemap dosyasının yolu
    """
    sitemap = SitemapGenerator(base_url, output_path)
    
    # Ana sayfa ekle
    sitemap.add_url('/', None, 'daily', 1.0)
    
    # Her model için URL ekle
    for model in models:
        # Model adına göre URL yapısı oluştur
        model_name = model.__name__.lower()
        
        # Koleksiyon URL'i
        sitemap.add_url(f'/{model_name}s', None, 'daily', 0.8)
        
        # Tüm kayıtlar
        try:
            items = model.all()
            for item in items:
                item_id = getattr(item, 'id', None)
                if item_id:
                    sitemap.add_url(f'/{model_name}s/{item_id}', None, 'weekly', 0.6)
        except Exception:
            pass
    
    # Sitemap'i kaydet ve döndür
    return sitemap.save_sitemap() 