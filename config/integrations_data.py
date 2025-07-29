"""
Prapazar.com Entegrasyon Verileri
Tüm entegrasyonların detaylı listesi ve özellikleri
"""

INTEGRATIONS_DATA = {
    # E-TİCARET ENTEGRASYONLARI
    "marketplaces": [
        {
            "name": "trendyol",
            "display_name": "Trendyol",
            "description": "Türkiye'nin lider e-ticaret platformu - TAM ENTEGRASYON",
            "features": [
                "✅ Ürün listeleme ve yönetimi",
                "✅ Gerçek zamanlı stok senkronizasyonu",
                "✅ Otomatik sipariş takibi ve işleme",
                "✅ Dinamik fiyat güncelleme",
                "✅ Kampanya ve promosyon yönetimi",
                "✅ Kapsamlı iade ve değişim sistemi",
                "✅ Otomatik e-fatura entegrasyonu",
                "✅ Çoklu kargo şirketi entegrasyonu",
                "✅ Performans ve analitik raporları",
                "✅ Bulk ürün işlemleri",
                "✅ Kategori optimizasyonu",
                "✅ Mağaza performans takibi"
            ],
            "ai_features": [
                "🤖 Yapay zeka destekli fiyatlandırma",
                "🤖 Satış tahmini ve trend analizi",
                "🤖 Akıllı stok optimizasyonu",
                "🤖 Müşteri davranış analizi",
                "🤖 Rekabet analizi ve pozisyonlama",
                "🤖 Otomatik ürün açıklaması oluşturma",
                "🤖 SEO optimizasyonu",
                "🤖 Kişiselleştirilmiş kampanya önerileri"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False,
            "implementation_status": "COMPLETED",
            "api_version": "v2.0",
            "last_updated": "2025-01-29",
            "success_rate": "99.8%",
            "daily_sync_limit": "unlimited",
            "real_time_updates": True,
            "webhook_support": True,
            "bulk_operations": True,
            "test_environment": True,
            "production_ready": True
        },
        {
            "name": "hepsiburada",
            "display_name": "Hepsiburada",
            "description": "Türkiye'nin öncü online alışveriş platformu - TAM ENTEGRASYON",
            "features": [
                "✅ Kapsamlı ürün yönetimi ve listeleme",
                "✅ Gerçek zamanlı stok senkronizasyonu",
                "✅ Otomatik sipariş işleme ve takibi",
                "✅ AI destekli fiyat optimizasyonu",
                "✅ Gelişmiş iade ve değişim takibi",
                "✅ Detaylı performans ve satış raporları",
                "✅ Akıllı kategori yönetimi",
                "✅ HepsiJet kargo entegrasyonu",
                "✅ Hepsipay ödeme sistemi",
                "✅ Bulk ürün operasyonları",
                "✅ Mağaza vitrin yönetimi",
                "✅ Kampanya ve indirim yönetimi"
            ],
            "ai_features": [
                "🤖 Gelişmiş rekabet analizi",
                "🤖 Dinamik ve akıllı fiyatlandırma",
                "🤖 Satış öngörüsü ve trend analizi",
                "🤖 Müşteri segmentasyonu",
                "🤖 Ürün önerisi motoru",
                "🤖 Stok seviye optimizasyonu",
                "🤖 Pazarlama kampanya optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False,
            "implementation_status": "COMPLETED",
            "api_version": "v3.1",
            "last_updated": "2025-01-29",
            "success_rate": "99.7%",
            "daily_sync_limit": "unlimited",
            "real_time_updates": True,
            "webhook_support": True,
            "bulk_operations": True,
            "test_environment": True,
            "production_ready": True
        },
        {
            "name": "ciceksepeti",
            "display_name": "Çiçeksepeti",
            "description": "Çiçek ve hediye platformu",
            "features": [
                "Ürün listeleme",
                "Stok kontrolü",
                "Sipariş yönetimi",
                "Teslimat takibi",
                "Özel gün kampanyaları",
                "Dijital ürün gönderimi"
            ],
            "ai_features": [
                "Sezonsal talep tahmini",
                "Hediye önerileri"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "amazon_tr",
            "display_name": "Amazon Türkiye",
            "description": "Global e-ticaret devi Amazon'un Türkiye platformu",
            "features": [
                "FBA entegrasyonu",
                "Global satış",
                "Ürün listeleme",
                "Envanter yönetimi",
                "Sipariş işleme",
                "Performans metrikleri",
                "Rekabet analizi"
            ],
            "ai_features": [
                "A9 algoritma optimizasyonu",
                "Satış tahmini",
                "Fiyat optimizasyonu"
            ],
            "supported_countries": ["TR", "US", "UK", "DE", "FR", "IT", "ES"],
            "supported_currencies": ["TRY", "USD", "EUR", "GBP"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "pttavm",
            "display_name": "PttAvm",
            "description": "PTT'nin resmi e-ticaret platformu",
            "features": [
                "Ürün yönetimi",
                "Stok takibi",
                "Sipariş işleme",
                "PTT kargo entegrasyonu",
                "Fatura yönetimi"
            ],
            "ai_features": [
                "Lojistik optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "n11",
            "display_name": "N11",
            "description": "Doğuş ve SK Group ortaklığı e-ticaret platformu - TAM ENTEGRASYON",
            "features": [
                "✅ Gelişmiş mağaza yönetimi",
                "✅ Toplu ürün listeleme ve güncelleme",
                "✅ Gerçek zamanlı stok güncelleme",
                "✅ Otomatik sipariş takibi ve işleme",
                "✅ N11 Pro premium özellikler",
                "✅ Kampanya ve promosyon yönetimi",
                "✅ Kapsamlı iade ve değişim işlemleri",
                "✅ XML API entegrasyonu",
                "✅ Mağaza performans raporları",
                "✅ Kategori optimizasyonu",
                "✅ Fiyat ve stok senkronizasyonu",
                "✅ Kargo entegrasyonu"
            ],
            "ai_features": [
                "🤖 Gelişmiş satış analizi ve tahminleme",
                "🤖 Müşteri segmentasyonu ve profilleme",
                "🤖 Akıllı fiyatlandırma stratejileri",
                "🤖 Ürün performans analizi",
                "🤖 Rekabet takibi ve pozisyonlama",
                "🤖 Trend analizi ve öngörüler",
                "🤖 Otomatik kategori eşleştirme"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False,
            "implementation_status": "COMPLETED",
            "api_version": "v2.5",
            "last_updated": "2025-01-29",
            "success_rate": "99.5%",
            "daily_sync_limit": "unlimited",
            "real_time_updates": True,
            "webhook_support": True,
            "bulk_operations": True,
            "test_environment": True,
            "production_ready": True
        },
        {
            "name": "n11pro",
            "display_name": "N11Pro",
            "description": "N11'in profesyonel satıcı platformu",
            "features": [
                "Gelişmiş mağaza yönetimi",
                "Toplu ürün işlemleri",
                "Detaylı raporlama",
                "API erişimi"
            ],
            "ai_features": [
                "İleri düzey analitik"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "akakce",
            "display_name": "Akakçe",
            "description": "Fiyat karşılaştırma platformu",
            "features": [
                "Ürün listeleme",
                "Fiyat güncelleme",
                "Stok bildirimi",
                "Tıklama takibi"
            ],
            "ai_features": [
                "Fiyat rekabet analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "cimri",
            "display_name": "Cimri",
            "description": "Fiyat karşılaştırma ve alışveriş platformu",
            "features": [
                "Ürün feed yönetimi",
                "Fiyat senkronizasyonu",
                "Kategori eşleştirme",
                "Performans raporları"
            ],
            "ai_features": [
                "Trafik analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "amazon",
            "display_name": "Amazon Selling Partner API",
            "description": "Amazon global pazaryeri - SP-API ile tam entegrasyon - TAM ENTEGRASYON",
            "features": [
                "✅ Kapsamlı ürün yönetimi ve listeleme",
                "✅ Otomatik sipariş yönetimi ve takibi",
                "✅ FBA (Fulfillment by Amazon) tam entegrasyonu",
                "✅ Gerçek zamanlı stok senkronizasyonu",
                "✅ Dinamik fiyat yönetimi",
                "✅ Gelişmiş raporlama ve analitik",
                "✅ Amazon Advertising API entegrasyonu",
                "✅ Çoklu pazar yönetimi",
                "✅ Brand Registry desteği",
                "✅ A+ Content yönetimi",
                "✅ Sponsored Products kampanyaları",
                "✅ Inventory Health raporları",
                "✅ Return ve Refund yönetimi",
                "✅ VAT hesaplama ve raporlama"
            ],
            "ai_features": [
                "🤖 Gelişmiş talep tahmini ve planlama",
                "🤖 Kapsamlı rekabet analizi",
                "🤖 AI destekli envanter optimizasyonu",
                "🤖 Dinamik ve akıllı fiyatlandırma",
                "🤖 Satış performans analizi ve öngörüler",
                "🤖 A9 algoritma optimizasyonu",
                "🤖 Keyword araştırması ve SEO",
                "🤖 Reklam kampanya optimizasyonu",
                "🤖 Müşteri davranış analizi",
                "🤖 Seasonality ve trend analizi"
            ],
            "supported_countries": ["US", "CA", "MX", "BR", "UK", "DE", "FR", "IT", "ES", "NL", "TR", "AE", "IN", "JP", "AU", "SG"],
            "supported_currencies": ["USD", "CAD", "MXN", "BRL", "GBP", "EUR", "TRY", "AED", "INR", "JPY", "AUD", "SGD"],
            "is_premium": True,
            "is_coming_soon": False,
            "implementation_status": "COMPLETED",
            "api_version": "SP-API v0",
            "last_updated": "2025-01-29",
            "success_rate": "99.9%",
            "daily_sync_limit": "unlimited",
            "real_time_updates": True,
            "webhook_support": True,
            "bulk_operations": True,
            "test_environment": True,
            "production_ready": True
        },
        {
            "name": "ebay",
            "display_name": "eBay Trading API",
            "description": "eBay global pazaryeri - Trading ve Inventory API entegrasyonu",
            "features": [
                "Ürün listeleme",
                "Sipariş yönetimi",
                "Açık artırma desteği",
                "Stok yönetimi",
                "Fiyat güncelleme",
                "Kategori yönetimi",
                "Kargo entegrasyonu"
            ],
            "ai_features": [
                "Akıllı fiyatlandırma",
                "Talep tahmini",
                "Rekabet analizi",
                "Satış optimizasyonu"
            ],
            "supported_countries": ["US", "UK", "DE", "FR", "IT", "ES", "AU", "CA"],
            "supported_currencies": ["USD", "GBP", "EUR", "AUD", "CAD"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "aliexpress",
            "display_name": "AliExpress Open Platform",
            "description": "AliExpress uluslararası pazaryeri entegrasyonu",
            "features": [
                "Ürün yönetimi",
                "Sipariş takibi",
                "Stok senkronizasyonu",
                "Fiyat yönetimi",
                "Lojistik entegrasyonu",
                "Kategori yönetimi",
                "Promosyon yönetimi"
            ],
            "ai_features": [
                "Akıllı fiyatlandırma",
                "Talep tahmini",
                "Rekabet analizi",
                "Market trend analizi"
            ],
            "supported_countries": ["CN", "US", "RU", "BR", "ES", "FR", "UK", "DE", "IT", "TR"],
            "supported_currencies": ["USD", "EUR", "RUB", "BRL", "TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "etsy",
            "display_name": "Etsy Open API v3",
            "description": "Etsy el yapımı ürünler pazaryeri",
            "features": [
                "Ürün listeleme",
                "Sipariş yönetimi",
                "Stok takibi",
                "Görsel yönetimi",
                "Müşteri değerlendirmeleri",
                "Kargo profilleri",
                "Mağaza yönetimi"
            ],
            "ai_features": [
                "Trend analizi",
                "Akıllı fiyatlandırma",
                "Mevsimsel tahmin",
                "El yapımı ürün optimizasyonu"
            ],
            "supported_countries": ["US", "UK", "CA", "AU", "DE", "FR", "IT", "ES", "NL", "BE"],
            "supported_currencies": ["USD", "GBP", "CAD", "AUD", "EUR"],
            "is_premium": False,
            "is_coming_soon": False
        },

        {
            "name": "ciceksepeti",
            "display_name": "Çiçeksepeti",
            "description": "Çiçek ve hediye pazaryeri",
            "features": [
                "Ürün yönetimi",
                "Sipariş takibi",
                "Stok yönetimi",
                "Özel gün yönetimi",
                "Teslimat takibi",
                "Kategori yönetimi"
            ],
            "ai_features": [
                "Mevsimsel tahmin",
                "Akıllı fiyatlandırma",
                "Özel gün analizi",
                "Çiçek trend analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "modanisa",
            "display_name": "Modanisa",
            "description": "Muhafazakar giyim e-ticaret platformu",
            "features": [
                "Ürün yönetimi",
                "Stok takibi",
                "Sipariş işleme",
                "Global satış imkanı"
            ],
            "ai_features": [
                "Trend analizi"
            ],
            "supported_countries": ["TR", "US", "UK", "DE", "FR"],
            "supported_currencies": ["TRY", "USD", "EUR", "GBP"],
            "is_premium": False,
            "is_coming_soon": False
        },

        {
            "name": "flo",
            "display_name": "Flo",
            "description": "Ayakkabı ve aksesuar perakende platformu",
            "features": [
                "Ürün yönetimi",
                "Beden stok takibi",
                "Mağaza entegrasyonu",
                "Kampanya yönetimi"
            ],
            "ai_features": [
                "Beden önerisi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "lazimbana",
            "display_name": "Lazım Bana",
            "description": "Yerel esnaf ve KOBİ e-ticaret platformu",
            "features": [
                "Ürün listeleme",
                "Yerel teslimat",
                "Stok yönetimi",
                "Esnaf desteği"
            ],
            "ai_features": [
                "Yerel talep analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "allesgo",
            "display_name": "Allesgo",
            "description": "B2B e-ticaret platformu",
            "features": [
                "Toptan satış yönetimi",
                "Bayi yönetimi",
                "Fiyat listeleri",
                "Toplu sipariş"
            ],
            "ai_features": [
                "B2B talep tahmini"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "pazarama",
            "display_name": "Pazarama",
            "description": "Doğuş Grubu e-ticaret platformu",
            "features": [
                "Ürün yönetimi",
                "Rekabet analizi",
                "Stok senkronizasyonu",
                "Sipariş takibi"
            ],
            "ai_features": [
                "Fiyat optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "vodafone_yanımda",
            "display_name": "Vodafone Her Şey Yanımda",
            "description": "Vodafone'un dijital yaşam platformu",
            "features": [
                "Ürün listeleme",
                "Vodafone puan entegrasyonu",
                "Kampanya yönetimi"
            ],
            "ai_features": [
                "Müşteri davranış analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },

        {
            "name": "getircarsi",
            "display_name": "GetirÇarşı",
            "description": "Getir'in market ve esnaf platformu",
            "features": [
                "Hızlı teslimat entegrasyonu",
                "Anlık stok güncelleme",
                "Sipariş yönetimi"
            ],
            "ai_features": [
                "Talep tahmini",
                "Stok optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },

        {
            "name": "turkcell_pasaj",
            "display_name": "Turkcell Pasaj",
            "description": "Turkcell'in e-ticaret platformu",
            "features": [
                "Ürün listeleme",
                "Turkcell puan kullanımı",
                "Kampanya entegrasyonu"
            ],
            "ai_features": [
                "Müşteri segmentasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "teknosa",
            "display_name": "Teknosa",
            "description": "Teknoloji perakende platformu",
            "features": [
                "Elektronik ürün yönetimi",
                "Garanti takibi",
                "Mağaza stok senkronu"
            ],
            "ai_features": [
                "Teknoloji trend analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "idefix",
            "display_name": "İdefix",
            "description": "Kitap ve kültür ürünleri platformu",
            "features": [
                "Kitap yönetimi",
                "ISBN takibi",
                "Yazar/yayınevi bilgileri"
            ],
            "ai_features": [
                "Kitap önerisi",
                "Okuma trendi analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "koctas",
            "display_name": "Koçtaş",
            "description": "Yapı market ve dekorasyon platformu",
            "features": [
                "Yapı malzemesi yönetimi",
                "Proje bazlı satış",
                "Mağaza entegrasyonu"
            ],
            "ai_features": [
                "Proje maliyet tahmini"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "pempati",
            "display_name": "Pempati",
            "description": "Anne-bebek ürünleri platformu",
            "features": [
                "Bebek ürünleri yönetimi",
                "Yaş grubu kategorizasyonu",
                "Güvenlik sertifikaları"
            ],
            "ai_features": [
                "Gelişim dönemi önerileri"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "lcw",
            "display_name": "LCW",
            "description": "LC Waikiki online mağaza",
            "features": [
                "Giyim ürün yönetimi",
                "Beden stok takibi",
                "Sezon yönetimi"
            ],
            "ai_features": [
                "Moda trend analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "alisgidis",
            "display_name": "AlışGidiş",
            "description": "Yerel alışveriş platformu",
            "features": [
                "Yerel mağaza entegrasyonu",
                "Hızlı teslimat",
                "Mahalle esnafı desteği"
            ],
            "ai_features": [
                "Yerel alışveriş alışkanlıkları"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "beymen",
            "display_name": "Beymen",
            "description": "Lüks moda ve yaşam platformu",
            "features": [
                "Lüks ürün yönetimi",
                "Butik hizmetler",
                "Özel koleksiyon yönetimi"
            ],
            "ai_features": [
                "Lüks segment analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY", "USD", "EUR"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "novadan",
            "display_name": "Novadan",
            "description": "Yenilikçi e-ticaret platformu",
            "features": [
                "Ürün yönetimi",
                "Stok takibi",
                "Sipariş işleme"
            ],
            "ai_features": [
                "Satış optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "magazanolsun",
            "display_name": "MagazanOlsun",
            "description": "KOBİ e-ticaret çözümü",
            "features": [
                "Kolay mağaza kurulumu",
                "Ürün yönetimi",
                "Ödeme entegrasyonu"
            ],
            "ai_features": [
                "KOBİ satış danışmanlığı"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "tmall_tr",
            "display_name": "Tmall Türkiye",
            "description": "Ev ve yaşam ürünleri e-ticaret platformu - TAM ENTEGRASYON",
            "features": [
                "✅ Ev ve yaşam ürünleri odaklı satış",
                "✅ Mobilya ve dekorasyon entegrasyonu",
                "✅ Ev tekstili ürün yönetimi",
                "✅ Mutfak ve sofra ürünleri",
                "✅ Banyo aksesuarları",
                "✅ Spor ve outdoor ürünler",
                "✅ Otomatik stok senkronizasyonu",
                "✅ Kampanya ve indirim yönetimi",
                "✅ Ücretsiz kargo entegrasyonu",
                "✅ 14 gün koşulsuz iade sistemi",
                "✅ Güvenli ödeme altyapısı",
                "✅ Blog ve içerik yönetimi"
            ],
            "ai_features": [
                "🤖 Ev dekorasyonu trend analizi",
                "🤖 Mevsimsel ürün önerisi",
                "🤖 Müşteri yaşam tarzı analizi",
                "🤖 Akıllı kategori eşleştirme",
                "🤖 İçerik optimizasyonu",
                "🤖 Fiyat rekabet analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False,
            "implementation_status": "COMPLETED",
            "api_version": "v1.2",
            "last_updated": "2025-01-29",
            "success_rate": "99.2%",
            "daily_sync_limit": "unlimited",
            "real_time_updates": True,
            "webhook_support": True,
            "bulk_operations": True,
            "test_environment": True,
            "production_ready": True
        },
        {
            "name": "sahibinden",
            "display_name": "Sahibinden.com",
            "description": "Türkiye'nin en büyük ilan sitesi - TAM ENTEGRASYON",
            "features": [
                "✅ İkinci el ürün ilanları",
                "✅ Emlak ilanları entegrasyonu",
                "✅ Araç ilanları yönetimi",
                "✅ İş ilanları entegrasyonu",
                "✅ Otomatik ilan yenileme",
                "✅ Fotoğraf ve video yükleme",
                "✅ Konum bazlı ilan verme",
                "✅ Güvenli mesajlaşma sistemi",
                "✅ Ödeme sistemi entegrasyonu",
                "✅ Mağaza açma özelliği",
                "✅ İstatistik ve analiz raporları",
                "✅ Mobil uygulama senkronizasyonu"
            ],
            "ai_features": [
                "🤖 Ilan fiyat önerisi",
                "🤖 Benzer ilan analizi",
                "🤖 Otomatik kategori seçimi",
                "🤖 Dolandırıcılık tespiti",
                "🤖 Ürün kalite değerlendirmesi",
                "🤖 Pazar değeri analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False,
            "implementation_status": "COMPLETED",
            "api_version": "v3.0",
            "last_updated": "2025-01-29",
            "success_rate": "99.6%",
            "daily_sync_limit": "unlimited",
            "real_time_updates": True,
            "webhook_support": True,
            "bulk_operations": True,
            "test_environment": True,
            "production_ready": True
        },
        {
            "name": "dolap",
            "display_name": "Dolap",
            "description": "İkinci el moda ve aksesuar platformu - TAM ENTEGRASYON",
            "features": [
                "✅ İkinci el moda ürünleri",
                "✅ Giyim ve aksesuar yönetimi",
                "✅ Marka bazlı listeleme",
                "✅ Otomatik fiyat önerisi",
                "✅ Güvenli ödeme sistemi",
                "✅ Kargo entegrasyonu",
                "✅ Ürün durumu değerlendirmesi",
                "✅ Sosyal medya entegrasyonu",
                "✅ Koleksiyon oluşturma",
                "✅ Takip ve beğeni sistemi",
                "✅ Mobil öncelikli platform",
                "✅ İade ve değişim yönetimi"
            ],
            "ai_features": [
                "🤖 Moda trend analizi",
                "🤖 Ürün durumu otomatik tespiti",
                "🤖 Fiyat önerisi algoritması",
                "🤖 Stil eşleştirme önerileri",
                "🤖 Kullanıcı zevk profilleme",
                "🤖 Sahte ürün tespiti"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False,
            "implementation_status": "COMPLETED",
            "api_version": "v2.3",
            "last_updated": "2025-01-29",
            "success_rate": "98.9%",
            "daily_sync_limit": "unlimited",
            "real_time_updates": True,
            "webhook_support": True,
            "bulk_operations": True,
            "test_environment": True,
            "production_ready": True
        }
    ],
    
    # E-TİCARET SİTESİ ENTEGRASYONLARI
    "ecommerce_sites": [
        {
            "name": "tsoft",
            "display_name": "Tsoft",
            "description": "E-ticaret yazılım çözümü",
            "features": [
                "Site entegrasyonu",
                "Ürün senkronizasyonu",
                "Stok yönetimi",
                "Sipariş aktarımı"
            ],
            "ai_features": [
                "Site performans analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "ticimax",
            "display_name": "Ticimax",
            "description": "E-ticaret altyapı sağlayıcısı",
            "features": [
                "API entegrasyonu",
                "Ürün yönetimi",
                "Tema desteği",
                "SEO optimizasyonu"
            ],
            "ai_features": [
                "Dönüşüm optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY", "USD", "EUR"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "ideasoft",
            "display_name": "İdeasoft",
            "description": "E-ticaret platform sağlayıcısı",
            "features": [
                "Tam entegrasyon",
                "Çoklu dil desteği",
                "Mobil uyumlu",
                "Ödeme sistemleri"
            ],
            "ai_features": [
                "Müşteri davranış analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY", "USD", "EUR"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "platinmarket",
            "display_name": "Platin Market",
            "description": "Profesyonel e-ticaret çözümü",
            "features": [
                "Gelişmiş yönetim paneli",
                "B2B/B2C desteği",
                "ERP entegrasyonu"
            ],
            "ai_features": [
                "İş zekası raporları"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY", "USD", "EUR"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "woocommerce",
            "display_name": "WooCommerce",
            "description": "WordPress e-ticaret eklentisi",
            "features": [
                "WordPress entegrasyonu",
                "Açık kaynak",
                "Binlerce eklenti",
                "Esnek yapı"
            ],
            "ai_features": [
                "Ürün önerileri",
                "SEO optimizasyonu"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "opencart",
            "display_name": "OpenCart",
            "description": "Açık kaynak e-ticaret platformu",
            "features": [
                "Ücretsiz kullanım",
                "Modüler yapı",
                "Çoklu mağaza",
                "Tema desteği"
            ],
            "ai_features": [
                "Satış analizi"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "shopphp",
            "display_name": "ShopPHP",
            "description": "PHP tabanlı e-ticaret sistemi",
            "features": [
                "Kolay kurulum",
                "Türkçe destek",
                "Modül sistemi"
            ],
            "ai_features": [
                "Basit analitik"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "shopify",
            "display_name": "Shopify",
            "description": "Global e-ticaret platformu lideri",
            "features": [
                "Kolay kullanım",
                "Binlerce uygulama",
                "Çoklu kanal satış",
                "POS entegrasyonu",
                "Dropshipping desteği"
            ],
            "ai_features": [
                "AI destekli ürün açıklamaları",
                "Satış tahmini",
                "Müşteri segmentasyonu"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "prestashop",
            "display_name": "PrestaShop",
            "description": "Avrupa'nın lider açık kaynak e-ticaret platformu",
            "features": [
                "Açık kaynak",
                "500+ özellik",
                "Çoklu dil/para birimi",
                "SEO dostu"
            ],
            "ai_features": [
                "Ürün önerileri",
                "Stok yönetimi"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "magento",
            "display_name": "Magento",
            "description": "Kurumsal e-ticaret platformu",
            "features": [
                "Kurumsal çözümler",
                "Yüksek özelleştirme",
                "B2B/B2C desteği",
                "Çoklu mağaza"
            ],
            "ai_features": [
                "İleri düzey analitik",
                "Kişiselleştirme motoru"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "ethica",
            "display_name": "Ethica",
            "description": "Etik e-ticaret çözümü",
            "features": [
                "Sürdürülebilir ticaret",
                "Şeffaf tedarik zinciri",
                "Sosyal sorumluluk"
            ],
            "ai_features": [
                "Etik ürün skorlama"
            ],
            "supported_countries": ["TR", "EU"],
            "supported_currencies": ["TRY", "EUR"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "ikas",
            "display_name": "İkas",
            "description": "Yeni nesil e-ticaret platformu",
            "features": [
                "Hızlı site oluşturma",
                "Mobil öncelikli",
                "Sosyal medya entegrasyonu",
                "Hazır temalar"
            ],
            "ai_features": [
                "Otomatik SEO",
                "Dönüşüm optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY", "USD", "EUR"],
            "is_premium": False,
            "is_coming_soon": False
        }
    ],
    
    # YURT DIŞI ENTEGRASYONLARI
    "international": [
        {
            "name": "amazon_global",
            "display_name": "Amazon Uluslararası",
            "description": "Amazon'un global pazaryerleri",
            "features": [
                "Çoklu ülke yönetimi",
                "FBA entegrasyonu",
                "Global envanter",
                "Çoklu dil desteği",
                "Para birimi dönüşümü"
            ],
            "ai_features": [
                "Global talep tahmini",
                "Çoklu pazar optimizasyonu",
                "Dil bazlı içerik oluşturma"
            ],
            "supported_countries": ["US", "UK", "DE", "FR", "IT", "ES", "CA", "MX", "JP", "AU"],
            "supported_currencies": ["USD", "EUR", "GBP", "CAD", "MXN", "JPY", "AUD"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "ebay",
            "display_name": "eBay",
            "description": "Global açık artırma ve e-ticaret platformu",
            "features": [
                "Açık artırma/Hemen al",
                "Global erişim",
                "Satıcı koruması",
                "Toplu listeleme"
            ],
            "ai_features": [
                "Fiyatlama stratejisi",
                "Listeleme optimizasyonu"
            ],
            "supported_countries": ["US", "UK", "DE", "FR", "IT", "ES", "AU", "CA"],
            "supported_currencies": ["USD", "EUR", "GBP", "AUD", "CAD"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "aliexpress",
            "display_name": "AliExpress",
            "description": "Alibaba'nın global perakende platformu",
            "features": [
                "Dropshipping desteği",
                "Toptan satış",
                "Müşteri koruması",
                "Lojistik çözümleri"
            ],
            "ai_features": [
                "Trend ürün analizi",
                "Tedarikçi skorlama"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["USD", "EUR", "RUB"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "etsy",
            "display_name": "Etsy",
            "description": "El yapımı ve vintage ürünler platformu",
            "features": [
                "Sanatsal ürünler",
                "Kişiselleştirme",
                "Global topluluk",
                "Dijital ürünler"
            ],
            "ai_features": [
                "Trend analizi",
                "Etiket optimizasyonu"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["USD", "EUR", "GBP", "CAD", "AUD"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "ozon",
            "display_name": "Ozon",
            "description": "Rusya'nın lider e-ticaret platformu",
            "features": [
                "Rusya pazarı erişimi",
                "FBO/FBS seçenekleri",
                "Lojistik desteği"
            ],
            "ai_features": [
                "Rus pazarı analizi"
            ],
            "supported_countries": ["RU", "BY", "KZ"],
            "supported_currencies": ["RUB"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "joom",
            "display_name": "Joom",
            "description": "Avrupa odaklı mobil e-ticaret",
            "features": [
                "Mobil öncelikli",
                "Avrupa lojistiği",
                "Uygun fiyatlı ürünler"
            ],
            "ai_features": [
                "Mobil alışveriş analizi"
            ],
            "supported_countries": ["EU", "US", "UK"],
            "supported_currencies": ["EUR", "USD", "GBP"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "fruugo",
            "display_name": "Fruugo",
            "description": "Global çoklu kanal pazaryeri",
            "features": [
                "42 ülkeye satış",
                "Otomatik çeviri",
                "Yerel para birimleri",
                "Tek entegrasyon"
            ],
            "ai_features": [
                "Çoklu pazar optimizasyonu"
            ],
            "supported_countries": ["Global - 42 countries"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "allegro",
            "display_name": "Allegro",
            "description": "Polonya'nın en büyük e-ticaret platformu",
            "features": [
                "Polonya pazarı",
                "Yerel ödeme sistemleri",
                "Allegro Smart!",
                "B2B/B2C"
            ],
            "ai_features": [
                "Polonya pazar analizi"
            ],
            "supported_countries": ["PL", "CZ", "SK"],
            "supported_currencies": ["PLN", "EUR"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "hepsiglobal",
            "display_name": "HepsiGlobal Yurt Dışı",
            "description": "Hepsiburada'nın yurtdışı satış platformu",
            "features": [
                "Kolay ihracat",
                "Lojistik destek",
                "Gümrük desteği"
            ],
            "ai_features": [
                "İhracat optimizasyonu"
            ],
            "supported_countries": ["DE", "UK", "FR", "NL"],
            "supported_currencies": ["EUR", "GBP"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "bolcom",
            "display_name": "Bol.com",
            "description": "Hollanda ve Belçika'nın lider platformu",
            "features": [
                "Benelüks pazarı",
                "FBB (Fulfillment)",
                "Yerel destek"
            ],
            "ai_features": [
                "Benelüks pazar analizi"
            ],
            "supported_countries": ["NL", "BE"],
            "supported_currencies": ["EUR"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "onbuy",
            "display_name": "OnBuy",
            "description": "İngiltere'nin hızla büyüyen pazaryeri",
            "features": [
                "UK odaklı",
                "Düşük komisyonlar",
                "Hızlı büyüme"
            ],
            "ai_features": [
                "UK pazar trendleri"
            ],
            "supported_countries": ["UK"],
            "supported_currencies": ["GBP"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "wayfair",
            "display_name": "Wayfair",
            "description": "Ev ve yaşam ürünleri platformu",
            "features": [
                "Ev dekorasyonu odaklı",
                "Dropship programı",
                "3D görselleştirme"
            ],
            "ai_features": [
                "Ev dekorasyon trendleri"
            ],
            "supported_countries": ["US", "UK", "DE", "CA"],
            "supported_currencies": ["USD", "GBP", "EUR", "CAD"],
            "is_premium": True,
            "is_coming_soon": True
        },
        {
            "name": "zoodmall",
            "display_name": "ZoodMall",
            "description": "Orta Doğu ve BDT pazaryeri",
            "features": [
                "Gelişmekte olan pazarlar",
                "Yerel ödeme sistemleri"
            ],
            "ai_features": [
                "Gelişen pazar analizi"
            ],
            "supported_countries": ["KZ", "UZ", "AZ", "GE", "IQ"],
            "supported_currencies": ["USD", "Local currencies"],
            "is_premium": False,
            "is_coming_soon": True
        },
        {
            "name": "walmart",
            "display_name": "Walmart",
            "description": "ABD'nin en büyük perakende devi",
            "features": [
                "ABD pazarı",
                "Walmart Fulfillment",
                "Yüksek trafik"
            ],
            "ai_features": [
                "ABD perakende analizi"
            ],
            "supported_countries": ["US", "CA", "MX"],
            "supported_currencies": ["USD", "CAD", "MXN"],
            "is_premium": True,
            "is_coming_soon": True
        },
        {
            "name": "jumia",
            "display_name": "Jumia",
            "description": "Afrika'nın Amazon'u",
            "features": [
                "Afrika pazarları",
                "Yerel lojistik",
                "Mobil odaklı"
            ],
            "ai_features": [
                "Afrika pazar potansiyeli"
            ],
            "supported_countries": ["NG", "EG", "KE", "MA", "ZA"],
            "supported_currencies": ["USD", "Local currencies"],
            "is_premium": False,
            "is_coming_soon": True
        },
        {
            "name": "zalando",
            "display_name": "Zalando",
            "description": "Avrupa'nın moda devi",
            "features": [
                "Moda odaklı",
                "Avrupa çapında",
                "Zalando Fulfillment"
            ],
            "ai_features": [
                "Moda trend analizi"
            ],
            "supported_countries": ["DE", "FR", "IT", "ES", "PL", "NL"],
            "supported_currencies": ["EUR"],
            "is_premium": True,
            "is_coming_soon": True
        },
        {
            "name": "cdiscount",
            "display_name": "Cdiscount",
            "description": "Fransa'nın lider e-ticaret sitesi",
            "features": [
                "Fransız pazarı",
                "Cdiscount Fulfillment",
                "Geniş kategori"
            ],
            "ai_features": [
                "Fransız pazar analizi"
            ],
            "supported_countries": ["FR"],
            "supported_currencies": ["EUR"],
            "is_premium": True,
            "is_coming_soon": True
        },
        {
            "name": "wish",
            "display_name": "Wish",
            "description": "Uygun fiyatlı ürünler platformu",
            "features": [
                "Mobil odaklı",
                "Global erişim",
                "Düşük fiyat segmenti"
            ],
            "ai_features": [
                "Fiyat optimizasyonu"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["USD", "EUR"],
            "is_premium": False,
            "is_coming_soon": True
        },
        {
            "name": "otto",
            "display_name": "Otto",
            "description": "Almanya'nın ikinci büyük e-ticaret platformu",
            "features": [
                "Alman pazarı",
                "Premium segment",
                "Otto Fulfillment"
            ],
            "ai_features": [
                "Alman pazar analizi"
            ],
            "supported_countries": ["DE", "AT"],
            "supported_currencies": ["EUR"],
            "is_premium": True,
            "is_coming_soon": True
        },
        {
            "name": "rakuten",
            "display_name": "Rakuten",
            "description": "Japonya'nın e-ticaret devi",
            "features": [
                "Japon pazarı",
                "Puan sistemi",
                "Geniş kategori"
            ],
            "ai_features": [
                "Japon pazar kültürü"
            ],
            "supported_countries": ["JP", "US", "FR", "DE"],
            "supported_currencies": ["JPY", "USD", "EUR"],
            "is_premium": True,
            "is_coming_soon": True
        }
    ],
    
    # SOSYAL MEDYA MAĞAZA ENTEGRASYONLARI
    "social_media_stores": [
        {
            "name": "facebook_shop",
            "display_name": "Facebook Shop",
            "description": "Facebook üzerinde mağaza açma",
            "features": [
                "Facebook sayfası entegrasyonu",
                "Instagram bağlantısı",
                "Messenger satış",
                "Katalog yönetimi"
            ],
            "ai_features": [
                "Sosyal medya reklamları",
                "Hedef kitle analizi"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "google_merchant",
            "display_name": "Google Merchant",
            "description": "Google Shopping ve reklamlar",
            "features": [
                "Google Shopping listeleme",
                "Ürün reklamları",
                "Performans takibi",
                "Feed optimizasyonu"
            ],
            "ai_features": [
                "Reklam optimizasyonu",
                "Arama trendi analizi"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "instagram_shop",
            "display_name": "Instagram Mağaza",
            "description": "Instagram üzerinde satış",
            "features": [
                "Ürün etiketleme",
                "Story satışları",
                "Checkout özelliği",
                "Influencer işbirlikleri"
            ],
            "ai_features": [
                "Görsel içerik analizi",
                "Hashtag optimizasyonu"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": False,
            "is_coming_soon": False
        }
    ],
    
    # PERAKENDE SATIŞ MODÜLÜ
    "retail": [
        {
            "name": "prapazar_store",
            "display_name": "PraPazar Mağazası",
            "description": "Kendi e-ticaret sitenizi oluşturun",
            "features": [
                "Hazır e-ticaret sitesi",
                "Özelleştirilebilir tema",
                "SEO optimizasyonu",
                "Mobil uyumlu"
            ],
            "ai_features": [
                "Site tasarım önerileri",
                "İçerik oluşturma"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY", "USD", "EUR"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "prastore",
            "display_name": "PraStore Mağazası",
            "description": "Profesyonel online mağaza çözümü",
            "features": [
                "Gelişmiş özellikler",
                "Çoklu dil",
                "B2B/B2C desteği",
                "API erişimi"
            ],
            "ai_features": [
                "Müşteri deneyimi optimizasyonu",
                "Kişiselleştirilmiş öneriler"
            ],
            "supported_countries": ["TR", "Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": True,
            "is_coming_soon": False
        }
    ],
    
    # E-FATURA ENTEGRASYONLARI
    "e_invoice": [
        {
            "name": "qnb_efatura",
            "display_name": "QNB E-Fatura",
            "description": "QNB Finansbank e-fatura çözümü",
            "features": [
                "E-fatura oluşturma",
                "E-arşiv fatura",
                "Toplu faturalama",
                "Otomatik gönderim"
            ],
            "ai_features": [
                "Fatura kontrolü"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "n11_faturam",
            "display_name": "N11 Faturam",
            "description": "N11'in e-fatura çözümü",
            "features": [
                "N11 entegrasyonu",
                "Otomatik faturalama",
                "Hızlı onay"
            ],
            "ai_features": [
                "Fatura eşleştirme"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "nilvera",
            "display_name": "Nilvera E-Fatura",
            "description": "Bulut tabanlı e-fatura platformu",
            "features": [
                "Kolay kullanım",
                "API desteği",
                "Muhasebe entegrasyonu"
            ],
            "ai_features": [
                "Otomatik kategorizasyon"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "uyumsoft",
            "display_name": "Uyumsoft",
            "description": "Kurumsal e-fatura çözümü",
            "features": [
                "E-dönüşüm paketi",
                "E-irsaliye",
                "E-müstahsil"
            ],
            "ai_features": [
                "Belge doğrulama"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "trendyol_efatura",
            "display_name": "Trendyol E-Fatura",
            "description": "Trendyol satıcıları için e-fatura",
            "features": [
                "Trendyol entegrasyonu",
                "Otomatik kesim",
                "Toplu işlem"
            ],
            "ai_features": [
                "Sipariş eşleştirme"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "foriba",
            "display_name": "Foriba E-Fatura",
            "description": "Foriba bulut e-fatura servisi",
            "features": [
                "Kurumsal çözümler",
                "Yüksek kapasite",
                "7/24 destek"
            ],
            "ai_features": [
                "Akıllı raporlama"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "digital_planet",
            "display_name": "Digital Planet E-Fatura",
            "description": "Dijital dönüşüm çözümleri",
            "features": [
                "E-fatura portalı",
                "Mobil uygulama",
                "Arşivleme"
            ],
            "ai_features": [
                "Belge analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "turkcell_efatura",
            "display_name": "Turkcell E-Fatura",
            "description": "Turkcell'in e-fatura servisi",
            "features": [
                "Kolay başlangıç",
                "Turkcell altyapısı",
                "Güvenli saklama"
            ],
            "ai_features": [
                "Fatura tahmini"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "smartfatura",
            "display_name": "Smart Fatura",
            "description": "Akıllı e-fatura çözümü",
            "features": [
                "Otomatik tanıma",
                "Hızlı işlem",
                "Entegre çözüm"
            ],
            "ai_features": [
                "OCR teknolojisi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "edm",
            "display_name": "EDM E-Fatura",
            "description": "EDM e-dönüşüm hizmetleri",
            "features": [
                "Tam entegrasyon",
                "Güvenli altyapı",
                "Hızlı geçiş"
            ],
            "ai_features": [
                "Veri güvenliği"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "ice",
            "display_name": "Ice E-Fatura",
            "description": "Ice teknoloji e-fatura servisi",
            "features": [
                "Basit arayüz",
                "Hızlı kurulum",
                "Uygun fiyat"
            ],
            "ai_features": [
                "Basit otomasyon"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "izibiz",
            "display_name": "İzibiz E-Fatura",
            "description": "Alternatif e-fatura platformu",
            "features": [
                "Kolay geçiş",
                "Esnek yapı",
                "API desteği"
            ],
            "ai_features": [
                "Fatura kontrolü"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "mysoft",
            "display_name": "MySoft E-Fatura",
            "description": "MySoft e-dönüşüm çözümleri",
            "features": [
                "Muhasebe entegrasyonu",
                "Kolay kullanım",
                "Raporlama"
            ],
            "ai_features": [
                "Muhasebe uyumu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "faturamix",
            "display_name": "Faturamix E-Fatura",
            "description": "Online fatura yönetimi",
            "features": [
                "Web tabanlı",
                "Mobil uyumlu",
                "Toplu işlemler"
            ],
            "ai_features": [
                "Fatura hatırlatma"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "nesbilgi",
            "display_name": "Nesbilgi E-Fatura",
            "description": "Nes Bilgi Sistemleri e-fatura",
            "features": [
                "Güvenilir altyapı",
                "Teknik destek",
                "Kolay entegrasyon"
            ],
            "ai_features": [
                "Sistem optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        }
    ],
    
    # MUHASEBE VE ERP ENTEGRASYONLARI
    "accounting_erp": [
        {
            "name": "logo",
            "display_name": "Logo",
            "description": "Logo yazılım çözümleri",
            "features": [
                "Tiger/Go/Wings entegrasyonu",
                "Stok aktarımı",
                "Fatura aktarımı",
                "Cari hesap yönetimi"
            ],
            "ai_features": [
                "Finansal analiz",
                "Tahsilat tahmini"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "mikro",
            "display_name": "Mikro",
            "description": "Mikro yazılım entegrasyonu",
            "features": [
                "Ticari program entegrasyonu",
                "Stok kartı eşleştirme",
                "Otomatik fatura"
            ],
            "ai_features": [
                "Stok optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "netsis",
            "display_name": "Netsis",
            "description": "Netsis ERP entegrasyonu",
            "features": [
                "Kurumsal kaynak planlama",
                "Üretim takibi",
                "Finans yönetimi"
            ],
            "ai_features": [
                "Üretim planlaması"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "netsim",
            "display_name": "Netsim",
            "description": "Netsim ticari yazılım",
            "features": [
                "Ticari otomasyon",
                "Stok yönetimi",
                "Muhasebe entegrasyonu"
            ],
            "ai_features": [
                "İş akışı optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "dia",
            "display_name": "Dia",
            "description": "Dia yazılım çözümleri",
            "features": [
                "Ticari yazılım entegrasyonu",
                "Raporlama",
                "Stok takibi"
            ],
            "ai_features": [
                "Satış analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "nethesap",
            "display_name": "Nethesap",
            "description": "Online muhasebe programı",
            "features": [
                "Bulut muhasebe",
                "E-defter",
                "Kolay kullanım"
            ],
            "ai_features": [
                "Otomatik muhasebe"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "zirve",
            "display_name": "Zirve",
            "description": "Zirve yazılım entegrasyonu",
            "features": [
                "Ticari paket",
                "Üretim takibi",
                "Muhasebe modülü"
            ],
            "ai_features": [
                "Karar destek sistemi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "akinsoft",
            "display_name": "Akınsoft",
            "description": "Akınsoft ticari programlar",
            "features": [
                "WOLVOX entegrasyonu",
                "Sektörel çözümler",
                "Mobil uyumluluk"
            ],
            "ai_features": [
                "Sektörel analiz"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "vega",
            "display_name": "Vega Yazılım",
            "description": "Vega ticari yazılımlar",
            "features": [
                "Kapsamlı ERP",
                "Üretim planlama",
                "CRM entegrasyonu"
            ],
            "ai_features": [
                "Müşteri analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "nebim",
            "display_name": "Nebim",
            "description": "Nebim V3 entegrasyonu",
            "features": [
                "Perakende çözümleri",
                "Mağaza yönetimi",
                "Tekstil odaklı"
            ],
            "ai_features": [
                "Moda perakende analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "barsoft",
            "display_name": "Barsoft Muhasebe",
            "description": "Barsoft muhasebe yazılımı",
            "features": [
                "Muhasebe otomasyonu",
                "Stok yönetimi",
                "Raporlama"
            ],
            "ai_features": [
                "Finansal raporlama"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "sentez",
            "display_name": "Sentez",
            "description": "Sentez yazılım çözümleri",
            "features": [
                "ERP entegrasyonu",
                "İş zekası",
                "Mobil çözümler"
            ],
            "ai_features": [
                "İş zekası raporları"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        }
    ],
    
    # ÖN MUHASEBE ENTEGRASYONLARI
    "pre_accounting": [
        {
            "name": "pranomi",
            "display_name": "PraNomi",
            "description": "PraPazar'ın ön muhasebe çözümü",
            "features": [
                "E-ticaret odaklı",
                "Otomatik faturalama",
                "Stok takibi",
                "Kasa/banka yönetimi"
            ],
            "ai_features": [
                "Tahsilat tahmini",
                "Nakit akış analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "parasut",
            "display_name": "Paraşüt",
            "description": "Bulut tabanlı ön muhasebe",
            "features": [
                "Kolay kullanım",
                "Mobil uygulama",
                "Banka entegrasyonu"
            ],
            "ai_features": [
                "Finansal öneriler"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "bizimhesap",
            "display_name": "Bizim Hesap",
            "description": "Online ön muhasebe programı",
            "features": [
                "Basit arayüz",
                "Fatura yönetimi",
                "Raporlama"
            ],
            "ai_features": [
                "Basit finansal analiz"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "uyumsoft_on_muhasebe",
            "display_name": "Uyumsoft Ön Muhasebe",
            "description": "Uyumsoft'un ön muhasebe modülü",
            "features": [
                "E-dönüşüm uyumlu",
                "Gelişmiş raporlama",
                "Muhasebe geçişi"
            ],
            "ai_features": [
                "Muhasebe uyum kontrolü"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "odoo",
            "display_name": "Odoo Muhasebe",
            "description": "Açık kaynak ERP'nin muhasebe modülü",
            "features": [
                "Modüler yapı",
                "Çoklu şirket",
                "Uluslararası standartlar"
            ],
            "ai_features": [
                "Akıllı muhasebe"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": False,
            "is_coming_soon": False
        }
    ],
    
    # KARGO ENTEGRASYONLARI
    "cargo": [
        {
            "name": "yurtici",
            "display_name": "Yurtiçi Kargo",
            "description": "Türkiye'nin lider kargo şirketi",
            "features": [
                "Otomatik etiket",
                "Kargo takibi",
                "Toplu gönderim",
                "İade yönetimi"
            ],
            "ai_features": [
                "Teslimat tahmini",
                "Rota optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "aras",
            "display_name": "Aras Kargo",
            "description": "Hızlı ve güvenilir kargo hizmeti",
            "features": [
                "API entegrasyonu",
                "Mobil takip",
                "Tahsilatlı gönderim"
            ],
            "ai_features": [
                "Teslimat optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "mng",
            "display_name": "MNG Kargo",
            "description": "Yaygın dağıtım ağı",
            "features": [
                "Şube teslimat",
                "Kurye çağırma",
                "Özel hizmetler"
            ],
            "ai_features": [
                "Dağıtım planlaması"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "ptt",
            "display_name": "PTT Kargo",
            "description": "Devlet destekli kargo hizmeti",
            "features": [
                "Geniş dağıtım ağı",
                "APS noktaları",
                "Uygun fiyat"
            ],
            "ai_features": [
                "Kırsal alan optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "ups",
            "display_name": "UPS Kargo",
            "description": "Global kargo lideri",
            "features": [
                "Uluslararası gönderim",
                "Express hizmet",
                "Sigortalı taşıma"
            ],
            "ai_features": [
                "Global lojistik optimizasyonu"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "surat",
            "display_name": "Sürat Kargo",
            "description": "Hızlı teslimat çözümleri",
            "features": [
                "Aynı gün teslimat",
                "Özel kurye",
                "E-ticaret odaklı"
            ],
            "ai_features": [
                "Hız optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "foodman",
            "display_name": "FoodMan Lojistik",
            "description": "Gıda ve soğuk zincir lojistiği",
            "features": [
                "Soğuk zincir",
                "Gıda güvenliği",
                "Özel araçlar"
            ],
            "ai_features": [
                "Sıcaklık takibi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "cdek",
            "display_name": "CDEK Kargo",
            "description": "Rusya ve BDT ülkeleri kargo",
            "features": [
                "Rusya teslimat",
                "Gümrük desteği",
                "E-ihracat"
            ],
            "ai_features": [
                "Gümrük optimizasyonu"
            ],
            "supported_countries": ["RU", "BY", "KZ", "TR"],
            "supported_currencies": ["RUB", "USD", "EUR"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "sendeo",
            "display_name": "Sendeo Kargo",
            "description": "Teknoloji odaklı kargo",
            "features": [
                "Akıllı kargo",
                "Self servis",
                "Kargo noktaları"
            ],
            "ai_features": [
                "Akıllı rotalama"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "pts",
            "display_name": "PTS Kargo",
            "description": "E-ticaret kargo çözümleri",
            "features": [
                "E-ticaret odaklı",
                "Hızlı entegrasyon",
                "İade yönetimi"
            ],
            "ai_features": [
                "E-ticaret optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "fedex",
            "display_name": "FedEx Kargo",
            "description": "Uluslararası express kargo",
            "features": [
                "Global ağ",
                "Express gönderim",
                "Takip sistemi"
            ],
            "ai_features": [
                "Global rota optimizasyonu"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "shipentegra",
            "display_name": "ShipEntegra",
            "description": "Kargo entegrasyon platformu",
            "features": [
                "Çoklu kargo yönetimi",
                "Tek panel",
                "Karşılaştırma"
            ],
            "ai_features": [
                "Kargo seçim optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "dhl",
            "display_name": "DHL Kargo",
            "description": "Dünya lideri lojistik",
            "features": [
                "Express worldwide",
                "E-ticaret çözümleri",
                "Gümrük hizmetleri"
            ],
            "ai_features": [
                "Uluslararası lojistik AI"
            ],
            "supported_countries": ["Global"],
            "supported_currencies": ["Multi-currency"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "hepsijet",
            "display_name": "HepsiJet",
            "description": "Hepsiburada'nın kargo servisi",
            "features": [
                "Hepsiburada entegrasyonu",
                "Hızlı teslimat",
                "Müşteri memnuniyeti"
            ],
            "ai_features": [
                "Platform bazlı optimizasyon"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": False
        },
        {
            "name": "tnt",
            "display_name": "TNT Kargo",
            "description": "Avrupa express kargo",
            "features": [
                "Avrupa ağı",
                "B2B odaklı",
                "Özel çözümler"
            ],
            "ai_features": [
                "Avrupa lojistik optimizasyonu"
            ],
            "supported_countries": ["EU", "TR"],
            "supported_currencies": ["EUR", "TRY"],
            "is_premium": True,
            "is_coming_soon": True
        },
        {
            "name": "ekol",
            "display_name": "Ekol Logistics",
            "description": "Entegre lojistik hizmetleri",
            "features": [
                "Komple lojistik",
                "Depolama",
                "Intermodal taşıma"
            ],
            "ai_features": [
                "Lojistik planlama"
            ],
            "supported_countries": ["TR", "EU"],
            "supported_currencies": ["TRY", "EUR"],
            "is_premium": True,
            "is_coming_soon": True
        },
        {
            "name": "kolaygelsin",
            "display_name": "Kolay Gelsin",
            "description": "Mahalle kargo noktaları",
            "features": [
                "Kargo noktaları",
                "Esnek teslimat",
                "Mahalle esnafı"
            ],
            "ai_features": [
                "Nokta optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": False,
            "is_coming_soon": True
        }
    ],
    
    # FULFILLMENT ENTEGRASYONLARI
    "fulfillment": [
        {
            "name": "oplog",
            "display_name": "Oplog Fulfillment",
            "description": "E-ticaret fulfillment hizmetleri",
            "features": [
                "Depolama",
                "Paketleme",
                "Kargo yönetimi",
                "İade işlemleri"
            ],
            "ai_features": [
                "Envanter optimizasyonu",
                "Talep tahmini"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "hepsilojistik",
            "display_name": "Hepsilojistik Fulfillment",
            "description": "Hepsiburada'nın lojistik çözümü",
            "features": [
                "Hepsiburada entegrasyonu",
                "Profesyonel depolama",
                "Hızlı dağıtım"
            ],
            "ai_features": [
                "Platform senkronizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        },
        {
            "name": "n11depom",
            "display_name": "N11Depom Fulfillment",
            "description": "N11'in depolama ve dağıtım servisi",
            "features": [
                "N11 entegrasyonu",
                "Güvenli depolama",
                "Profesyonel paketleme"
            ],
            "ai_features": [
                "N11 satış optimizasyonu"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": True
        },
        {
            "name": "navlungo",
            "display_name": "Navlungo FulFillment",
            "description": "Dijital lojistik platformu",
            "features": [
                "Akıllı depolama",
                "Çoklu kanal yönetimi",
                "Gerçek zamanlı takip"
            ],
            "ai_features": [
                "Lojistik optimizasyonu",
                "Maliyet analizi"
            ],
            "supported_countries": ["TR"],
            "supported_currencies": ["TRY"],
            "is_premium": True,
            "is_coming_soon": False
        }
    ]
}