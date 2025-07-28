# PofuAi - Gelişmiş Yapay Zeka Sistemi 🚀

## Genel Bakış

PofuAi projeniz için geliştirilmiş, **rol tabanlı** gelişmiş yapay zeka sistemi. Bu sistem, mevcut AI altyapınızı genişleterek sosyal medya şablon üretimi, AI ile ürün düzenleme ve kişiselleştirilmiş içerik analizi gibi ileri seviye özellikler sunar.

### 🎯 Ana Özellikler

#### 1. **Rol Tabanlı AI Hizmetleri**
- **Admin**: Tüm AI özelliklerine erişim + ürün düzenleme
- **Moderator**: Gelişmiş şablon oluşturma + toplu işlemler
- **Editor**: Temel şablon oluşturma + içerik analizi
- **User**: Kişisel şablon oluşturma + kendi içerik analizi

#### 2. **Sosyal Medya Şablon Üretimi**
- **7 farklı platform desteği**: Instagram, Facebook, Twitter, LinkedIn, Telegram, WhatsApp
- **AI destekli metin üretimi**: Ürün bilgilerine göre otomatik pazarlama metni
- **Görsel işleme**: Arka plan kaldırma, kalite iyileştirme, filtreler
- **Özelleştirilebilir tasarım**: Renk, font, boyut, pozisyon ayarları

#### 3. **AI ile Ürün Düzenleme (Admin Özel)**
- **Görsel optimizasyonu**: Kalite artırma, arka plan kaldırma, yeniden boyutlandırma
- **Açıklama iyileştirme**: AI ile ürün açıklamalarını geliştirme
- **SEO optimizasyonu**: Meta title/description optimizasyonu
- **Fiyat analizi**: Pazar analizi ve fiyat önerileri

#### 4. **Kişiselleştirilmiş İçerik Analizi**
- **Kullanıcı davranış analizi**: Tercihler ve kullanım desenleri
- **İçerik önerileri**: Kişiselleştirilmiş öneriler
- **Pazar trend analizi**: (Moderator+ için)
- **İş zekası raporları**: (Admin için)

## 🏗️ Sistem Mimarisi

### Dosya Yapısı
```
core/AI/
├── advanced_ai_core.py          # Ana gelişmiş AI çekirdeği
├── advanced_ai_helpers.py       # Yardımcı fonksiyonlar
├── ai_core.py                   # Mevcut temel AI sistemi
├── image_recognition.py         # Görsel tanıma servisi
├── content_categorizer.py       # İçerik kategorilendirme
├── user_content_manager.py      # Kullanıcı içerik yönetimi
└── smart_storage.py            # Akıllı depolama sistemi

app/Controllers/
└── AdvancedAIController.py     # Gelişmiş AI controller

core/Route/
└── advanced_ai_routes.py       # Gelişmiş AI route'ları

core/Database/
├── ai_migrations.sql           # Temel AI tabloları
└── advanced_ai_migrations.sql  # Gelişmiş AI tabloları
```

### Veritabanı Tabloları

#### Yeni Tablolar
- `ai_template_results` - Şablon oluşturma sonuçları
- `ai_product_edits` - Ürün düzenleme geçmişi (Admin)
- `ai_analysis_results` - İçerik analizi sonuçları
- `user_ai_permissions` - Kullanıcı AI izinleri
- `ai_template_usage_stats` - Şablon kullanım istatistikleri
- `ai_usage_quotas` - Kullanım kotaları
- `ai_processing_queue` - İşlem kuyruğu
- `ai_user_feedback` - Kullanıcı geri bildirimleri

## 🚀 Kurulum ve Konfigürasyon

### 1. Veritabanı Migrasyonları

```bash
# Gelişmiş AI tablolarını oluştur
mysql -u username -p database_name < core/Database/advanced_ai_migrations.sql
```

### 2. Python Bağımlılıkları

```bash
# Ek bağımlılıklar yükle
pip install scikit-learn opencv-python colorsys transformers[torch]
```

### 3. Uygulama Konfigürasyonu

`app.py` dosyasına route'ları ekleyin:

```python
from core.Route.advanced_ai_routes import register_advanced_ai_routes

# Route'ları kaydet
register_advanced_ai_routes(app)
```

### 4. Dizin Yapısı Oluşturma

```bash
# Şablon depolama dizini
mkdir -p storage/templates
chmod 755 storage/templates
```

## 📖 API Kullanımı

### 🎨 Sosyal Medya Şablon Oluşturma

#### Temel Şablon Oluşturma
```bash
curl -X POST http://localhost:5000/api/ai/generate-template \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "template_type": "instagram_post",
    "content_data": {
      "product_name": "Akıllı Telefon",
      "product_image": "/path/to/product.jpg",
      "text": "Yeni nesil akıllı telefon!",
      "background_style": "gradient",
      "gradient_colors": ["#FF6B6B", "#4ECDC4"],
      "font_size": 48,
      "text_color": "#FFFFFF",
      "category": "elektronik",
      "target_audience": "genç yetişkinler"
    }
  }'
```

#### Toplu Şablon Oluşturma (Moderator+)
```bash
curl -X POST http://localhost:5000/api/ai/batch-generate-templates \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "templates": [
      {
        "template_type": "instagram_post",
        "content_data": {...}
      },
      {
        "template_type": "telegram_post",
        "content_data": {...}
      }
    ]
  }'
```

### 🛠️ AI ile Ürün Düzenleme (Admin Özel)

```bash
curl -X POST http://localhost:5000/api/ai/edit-product \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "product_id": 123,
    "edit_instructions": {
      "image_editing": {
        "enhance_quality": true,
        "remove_background": false,
        "resize": true,
        "target_size": [800, 800],
        "apply_filter": true,
        "filter_type": "professional",
        "add_watermark": true,
        "watermark_text": "PofuAi"
      },
      "description_enhancement": {
        "optimize_length": true,
        "target_length": 200,
        "add_seo_keywords": true,
        "keywords": ["kaliteli", "uygun fiyat"],
        "sales_focused": true
      },
      "seo_optimization": {
        "keywords": ["elektronik", "teknoloji"]
      },
      "price_analysis": {
        "market_analysis": true,
        "psychological_pricing": true
      }
    }
  }'
```

### 📊 İçerik Analizi

```bash
curl -X POST http://localhost:5000/api/ai/analyze-content \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "analysis_type": "comprehensive",
    "target_user_id": 123  // Sadece admin için
  }'
```

## 🎯 Rol Tabanlı İzin Sistemi

### İzin Matrisi

| Özellik | User | Editor | Moderator | Admin |
|---------|------|--------|-----------|-------|
| Temel Şablon Oluşturma | ✅ | ✅ | ✅ | ✅ |
| Gelişmiş Şablon Oluşturma | ❌ | ✅ | ✅ | ✅ |
| Toplu Şablon Oluşturma | ❌ | ❌ | ✅ | ✅ |
| Ürün Düzenleme | ❌ | ❌ | ❌ | ✅ |
| Kişisel İçerik Analizi | ✅ | ✅ | ✅ | ✅ |
| Gelişmiş İçerik Analizi | ❌ | ✅ | ✅ | ✅ |
| Pazar Trend Analizi | ❌ | ❌ | ✅ | ✅ |
| İş Zekası Raporları | ❌ | ❌ | ❌ | ✅ |
| Sistem Metrikleri | ❌ | ❌ | ❌ | ✅ |

### Günlük Kullanım Kotaları

| Rol | Şablon Oluşturma | Ürün Düzenleme | İçerik Analizi |
|-----|------------------|----------------|----------------|
| User | 20 | 0 | 10 |
| Editor | 50 | 0 | 20 |
| Moderator | 100 | 0 | 50 |
| Admin | 200 | 20 | Sınırsız |

## 🎨 Şablon Türleri ve Boyutları

### Desteklenen Platformlar

| Platform | Boyut | Açıklama |
|----------|-------|----------|
| Instagram Post | 1080x1080 | Kare format gönderi |
| Instagram Story | 1080x1920 | Dikey story formatı |
| Facebook Post | 1200x630 | Yatay gönderi formatı |
| Twitter Post | 1200x675 | Twitter gönderi formatı |
| LinkedIn Post | 1200x627 | Profesyonel platform |
| Telegram Post | 1280x720 | Mesajlaşma platformu |
| WhatsApp Status | 1080x1920 | Durum paylaşımı |

### Tasarım Seçenekleri

#### Arka Plan Stilleri
- **Gradient**: İki renk arası geçiş
- **Solid**: Tek renk arka plan
- **Texture**: Doku desenleri (nokta, çizgi, vb.)

#### Filtre Türleri
- **Professional**: İş dünyası için optimize
- **Vintage**: Nostaljik görünüm
- **Modern**: Yüksek kontrast ve canlı renkler
- **Artistic**: Sanatsal efektler

## 📊 Sistem Metrikleri ve İzleme

### Performans Metrikleri

```bash
# Sistem durumu kontrolü
curl http://localhost:5000/api/ai/status

# Sağlık kontrolü
curl http://localhost:5000/api/ai/health

# Gelişmiş metrikler (Admin)
curl http://localhost:5000/api/ai/advanced-metrics \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Kullanım İstatistikleri

```bash
# Kullanım istatistikleri (Admin)
curl http://localhost:5000/api/ai/usage-stats \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Kullanıcı geçmişi
curl "http://localhost:5000/api/ai/user-history?limit=50&type=templates" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Gelişmiş Konfigürasyon

### AI Sistem Ayarları

Veritabanındaki `ai_system_config` tablosunda yapılandırılabilir:

```sql
-- Şablon oluşturma limitlerini ayarla
UPDATE ai_system_config 
SET config_value = '100' 
WHERE config_key = 'max_templates_per_user_daily';

-- Gelişmiş AI özelliklerini aç/kapat
UPDATE ai_system_config 
SET config_value = 'true' 
WHERE config_key = 'advanced_ai_enabled';
```

### Özelleştirilebilir Ayarlar

| Ayar | Varsayılan | Açıklama |
|------|------------|----------|
| `advanced_ai_enabled` | true | Gelişmiş AI sistemi |
| `template_generation_enabled` | true | Şablon oluşturma |
| `product_editing_enabled` | true | Ürün düzenleme |
| `max_templates_per_user_daily` | 50 | Günlük şablon limiti |
| `template_storage_path` | storage/templates | Şablon dizini |

## 🧪 Test Etme

### Otomatik Test Süiti

```bash
# Gelişmiş AI sistemini test et
python test_advanced_ai_system.py
```

### Manuel Test Senaryoları

1. **Şablon Oluşturma Testi**
   ```bash
   # Test verisi ile şablon oluştur
   curl -X POST http://localhost:5000/api/ai/generate-template \
     -H "Content-Type: application/json" \
     -d @test_data/template_request.json
   ```

2. **Ürün Düzenleme Testi (Admin)**
   ```bash
   # Test ürünü düzenle
   curl -X POST http://localhost:5000/api/ai/edit-product \
     -H "Content-Type: application/json" \
     -d @test_data/product_edit_request.json
   ```

3. **İçerik Analizi Testi**
   ```bash
   # Kullanıcı içeriğini analiz et
   curl -X POST http://localhost:5000/api/ai/analyze-content \
     -H "Content-Type: application/json" \
     -d '{"analysis_type": "comprehensive"}'
   ```

## 🚨 Sorun Giderme

### Yaygın Sorunlar

#### 1. Şablon Oluşturma Hatası
```bash
# Şablon dizinini kontrol et
ls -la storage/templates/
chmod 755 storage/templates/

# Log dosyasını kontrol et
tail -f storage/logs/app_$(date +%Y-%m-%d).log | grep "template"
```

#### 2. İzin Hatası
```sql
-- Kullanıcı izinlerini kontrol et
SELECT * FROM user_ai_permissions WHERE user_id = YOUR_USER_ID;

-- İzin ekle
INSERT INTO user_ai_permissions (user_id, permission_name, granted_by) 
VALUES (YOUR_USER_ID, 'template_generation', 1);
```

#### 3. Model Yükleme Hatası
```bash
# Bağımlılıkları yeniden yükle
pip install --upgrade torch torchvision transformers
pip install scikit-learn opencv-python
```

### Debug Modu

```python
# advanced_ai_core.py içinde debug aktifleştir
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performans Optimizasyonu

### Sistem Gereksinimleri

**Minimum Gereksinimler:**
- CPU: 4 core
- RAM: 8GB
- Disk: 5GB boş alan
- Python: 3.8+

**Önerilen Gereksinimler:**
- CPU: 8+ core
- RAM: 16GB+
- GPU: NVIDIA GTX 1060+ (opsiyonel)
- Disk: SSD, 10GB+ boş alan

### Optimizasyon İpuçları

1. **GPU Kullanımı**
   ```bash
   # CUDA desteği ile PyTorch yükle
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Batch İşleme**
   ```sql
   -- Batch boyutunu ayarla
   UPDATE ai_system_config 
   SET config_value = '16' 
   WHERE config_key = 'max_processing_batch_size';
   ```

3. **Cache Optimizasyonu**
   ```sql
   -- Cache'i aktifleştir
   UPDATE ai_system_config 
   SET config_value = 'true' 
   WHERE config_key = 'advanced_ai_cache_enabled';
   ```

## 🔒 Güvenlik

### Veri Güvenliği
- **Rol tabanlı erişim kontrolü**: Her özellik için ayrı izin kontrolü
- **Dosya güvenliği**: Şablon dosyaları kullanıcı bazlı izolasyon
- **API güvenliği**: Rate limiting ve authentication
- **Veritabanı güvenliği**: Prepared statements ve input validation

### Privacy Uyumluluğu
- **GDPR uyumlu**: Kullanıcı verilerinin silinebilirliği
- **Veri anonimleştirme**: Kişisel bilgilerin korunması
- **Audit logging**: Tüm işlemlerin loglanması
- **Veri saklama politikaları**: Otomatik temizlik işlemleri

## 🔄 Bakım ve Güncelleme

### Otomatik Temizlik

```sql
-- Temizlik prosedürünü çalıştır
CALL CleanupAIData();

-- Otomatik temizlik aktifleştir (opsiyonel)
SET GLOBAL event_scheduler = ON;
```

### Veri Yedekleme

```bash
# AI verilerini yedekle
mysqldump -u username -p database_name \
  ai_template_results ai_product_edits ai_analysis_results \
  > ai_backup_$(date +%Y%m%d).sql
```

### Sistem Güncellemeleri

```bash
# Bağımlılıkları güncelle
pip install --upgrade -r requirements.txt

# Yeni migrasyonları çalıştır
mysql -u username -p database_name < new_migrations.sql
```

## 🎯 Gelecek Planları

### Yakın Dönem Geliştirmeler
- [ ] **Gerçek zamanlı şablon önizleme**
- [ ] **Daha fazla sosyal medya platformu desteği**
- [ ] **Video şablon oluşturma**
- [ ] **AI ile otomatik hashtag önerisi**

### Uzun Vadeli Hedefler
- [ ] **Makine öğrenmesi ile kişiselleştirme**
- [ ] **Çoklu dil desteği**
- [ ] **API rate limiting iyileştirmeleri**
- [ ] **Mobil uygulama entegrasyonu**

## 📞 Destek ve İletişim

### Teknik Destek
- **Dokümantasyon**: Bu README dosyası
- **API Dokümantasyonu**: `/api/ai/features` endpoint'i
- **Log Dosyaları**: `storage/logs/` dizini
- **Debug Bilgileri**: `/api/ai/health` endpoint'i

### Geliştirici Kaynakları
- **Kod Örnekleri**: `examples/` dizini
- **Test Verileri**: `test_data/` dizini
- **API Collection**: Postman koleksiyonu mevcut

---

## 🎉 Sonuç

Bu gelişmiş AI sistemi, PofuAi projenizi bir sonraki seviyeye taşıyacak kapsamlı özellikler sunar:

### ✨ Temel Avantajlar
- **Rol tabanlı hizmetler**: Her kullanıcı tipine özel AI deneyimi
- **Sosyal medya entegrasyonu**: 7 farklı platform için otomatik şablon üretimi
- **Admin özel araçlar**: AI ile ürün düzenleme ve gelişmiş analitik
- **Ölçeklenebilir mimari**: Büyüyen kullanıcı tabanına uygun tasarım
- **Güvenli ve hızlı**: Enterprise seviye güvenlik ve performans

### 🚀 Hemen Başlayın
1. **Kurulum**: Veritabanı migrasyonlarını çalıştırın
2. **Test**: Örnek API çağrıları ile sistemi test edin
3. **Özelleştirme**: Kendi ihtiyaçlarınıza göre ayarlayın
4. **Geliştirme**: Yeni özellikler ekleyin ve sistemi genişletin

**PofuAi Gelişmiş AI Sistemi - Yapay Zeka ile Geleceği Şekillendirin!** 🚀✨