# PofuAi - Gelişmiş Yapay Zeka Sistemi 🤖

PofuAi projesi için geliştirilmiş enterprise seviye açık kaynak yapay zeka sistemi. Bu sistem, görsel tanıma, akıllı kategorilendirme, kullanıcı bazlı içerik yönetimi ve akıllı depolama özellikleri sunar.

## 🚀 Özellikler

### 🖼️ Görsel Tanıma ve Analiz
- **Çoklu Model Desteği**: ResNet-50, YOLO v8, BERT tabanlı modeller
- **Kapsamlı Görsel Analiz**: Nesne algılama, renk analizi, kompozisyon değerlendirmesi
- **Yüz Tanıma**: Gelişmiş yüz algılama ve tanıma sistemi
- **Kalite Değerlendirmesi**: Otomatik görsel kalite analizi
- **Meta Veri Çıkarma**: EXIF verileri ve dosya bilgileri

### 🏷️ Akıllı Kategorilendirme
- **Otomatik Kategorilendirme**: AI tabanlı akıllı etiketleme
- **Hiyerarşik Kategoriler**: Çok seviyeli kategori sistemi
- **Kişiselleştirilmiş Etiketler**: Kullanıcı davranışlarına göre özel etiketler
- **Çoklu Yöntem Desteği**: Kural tabanlı, ML tabanlı, benzerlik tabanlı
- **Güven Skorları**: Her kategori için detaylı güven değerlendirmesi

### 👤 Kullanıcı Bazlı İçerik Yönetimi
- **Kullanıcı Profil Analizi**: Davranış desenlerini öğrenme
- **Kişiselleştirilmiş Öneriler**: Kullanıcıya özel organizasyon önerileri
- **İçerik Analizi**: Yükleme davranışları ve tercih analizi
- **Otomatik Organizasyon**: Akıllı klasör yapısı önerileri

### 💾 Akıllı Depolama Sistemi
- **Duplicate Detection**: Gelişmiş benzer dosya tespiti
- **Otomatik Organizasyon**: Tarih, kategori, kalite bazlı organizasyon
- **Akıllı Sıkıştırma**: Kalite kaybı olmadan boyut optimizasyonu
- **Depolama Optimizasyonu**: Yer tasarrufu ve performans iyileştirmesi

## 🛠️ Kurulum

### Sistem Gereksinimleri

- **Python**: 3.8 veya üzeri
- **RAM**: En az 4GB (8GB önerilir)
- **Disk**: En az 2GB boş alan
- **İşlemci**: CPU yeterli, GPU opsiyonel

### Hızlı Kurulum

1. **Bağımlılıkları Yükle**:
   ```bash
   python install_ai_dependencies.py
   ```

2. **Veritabanı Tablolarını Oluştur**:
   ```sql
   mysql -u username -p database_name < core/Database/ai_migrations.sql
   ```

3. **AI Sistemini Test Et**:
   ```bash
   python test_ai_system.py
   ```

4. **Uygulamayı Başlat**:
   ```bash
   python app.py
   ```

### Manuel Kurulum

1. **Temel Bağımlılıklar**:
   ```bash
   pip install numpy pillow opencv-python scikit-learn matplotlib pandas
   ```

2. **AI Bağımlılıkları**:
   ```bash
   pip install torch torchvision transformers face-recognition imagehash
   ```

3. **Opsiyonel Bağımlılıklar**:
   ```bash
   pip install sentence-transformers nltk spacy redis celery fastapi
   ```

## 📖 API Kullanımı

### Temel Görsel İşleme

```bash
# Tekil görsel işleme
curl -X POST http://localhost:5000/api/ai/process-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/path/to/image.jpg",
    "user_id": 1,
    "analysis_type": "comprehensive"
  }'
```

### Toplu İşleme

```bash
# Birden fazla görseli işle
curl -X POST http://localhost:5000/api/ai/batch-process \
  -H "Content-Type: application/json" \
  -d '{
    "image_paths": ["/path/to/image1.jpg", "/path/to/image2.jpg"],
    "user_id": 1,
    "analysis_type": "basic"
  }'
```

### Kullanıcı İçerik Analizi

```bash
# Kullanıcının içeriklerini analiz et
curl -X POST http://localhost:5000/api/ai/analyze-user-content \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

### Depolama Optimizasyonu

```bash
# Akıllı depolama organizasyonu
curl -X POST http://localhost:5000/api/ai/organize-storage \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "method": "hybrid"
  }'
```

### Duplicate Temizleme

```bash
# Duplicate dosyaları tespit et ve temizle
curl -X POST http://localhost:5000/api/ai/cleanup-duplicates \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "auto_remove": false
  }'
```

## 🏗️ Mimari

### Sistem Bileşenleri

```
PofuAi AI System
├── core/AI/
│   ├── ai_core.py              # Ana AI çekirdeği
│   ├── image_recognition.py    # Görsel tanıma servisi
│   ├── content_categorizer.py  # İçerik kategorilendirme
│   ├── user_content_manager.py # Kullanıcı içerik yönetimi
│   └── smart_storage.py        # Akıllı depolama sistemi
├── app/Controllers/
│   └── AIController.py         # AI API controller
├── core/Route/
│   └── ai_routes.py           # AI route tanımları
└── core/Database/
    └── ai_migrations.sql      # Veritabanı şeması
```

### Veri Akışı

1. **Görsel Yükleme** → AI Core'a gönderilir
2. **Analiz Süreçleri** → Paralel olarak çalışır:
   - Görsel sınıflandırma
   - Nesne algılama  
   - Meta veri çıkarma
   - Kalite analizi
3. **Kategorilendirme** → Çoklu yöntemle kategori önerisi
4. **Kullanıcı Profili** → Davranış analizi ve güncelleme
5. **Depolama** → Sonuçların veritabanına kaydı

## 🔧 Konfigürasyon

### AI Sistem Ayarları

AI sistemi ayarları `ai_system_config` tablosunda saklanır:

```sql
-- Görsel işleme aktif/pasif
UPDATE ai_system_config SET config_value = 'true' WHERE config_key = 'image_processing_enabled';

-- Benzerlik eşik değeri
UPDATE ai_system_config SET config_value = '0.85' WHERE config_key = 'similarity_threshold';

-- Otomatik kategorilendirme güven eşiği
UPDATE ai_system_config SET config_value = '0.7' WHERE config_key = 'auto_categorization_confidence_threshold';
```

### Performans Optimizasyonu

1. **GPU Kullanımı**:
   ```python
   # CUDA desteği için
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Batch Size Ayarı**:
   ```sql
   UPDATE ai_system_config SET config_value = '32' 
   WHERE config_key = 'max_processing_batch_size';
   ```

3. **Memory Cache**:
   ```python
   # Redis cache için
   pip install redis
   ```

## 📊 Performans ve İzleme

### Sistem Durumu

```bash
# AI sistem durumunu kontrol et
curl http://localhost:5000/api/ai/system-status
```

### Performans Metrikleri

- **İşlem Başarı Oranı**: %95+ hedeflenir
- **Ortalama İşlem Süresi**: <3 saniye/görsel
- **Kategorilendirme Doğruluğu**: %85+ hedeflenir
- **Duplicate Detection**: %98+ doğruluk

### Monitoring

```sql
-- Sistem sağlığını kontrol et
SELECT * FROM ai_system_health;

-- Kullanıcı AI özetini görüntüle
SELECT * FROM user_ai_summary WHERE user_id = 1;
```

## 🧪 Test Etme

### Otomatik Test Süiti

```bash
# Tüm AI sistemini test et
python test_ai_system.py
```

Test süiti şunları kontrol eder:
- ✅ AI Core fonksiyonelliği
- ✅ Görsel işleme performansı
- ✅ Kategorilendirme doğruluğu
- ✅ Kullanıcı içerik yönetimi
- ✅ Depolama optimizasyonu
- ✅ Toplu işleme kapasitesi

### Manuel Test

1. **Test Görselleri Ekle**:
   ```bash
   # test_images/ dizinine görsel dosyaları kopyala
   cp /path/to/your/images/* test_images/
   ```

2. **API Test**:
   ```bash
   # Postman veya curl ile API endpoint'lerini test et
   curl -X GET http://localhost:5000/api/ai/system-status
   ```

## 🐛 Sorun Giderme

### Yaygın Sorunlar

1. **Model Yükleme Hatası**:
   ```bash
   # Torch yeniden yükle
   pip uninstall torch torchvision
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   ```

2. **Memory Hatası**:
   ```python
   # Batch size'ı küçült
   UPDATE ai_system_config SET config_value = '16' 
   WHERE config_key = 'max_processing_batch_size';
   ```

3. **Face Recognition Hatası**:
   ```bash
   # dlib bağımlılığı yükle
   pip install cmake
   pip install dlib
   pip install face-recognition
   ```

### Log Kontrolü

```bash
# AI sistem loglarını kontrol et
tail -f storage/logs/app_$(date +%Y-%m-%d).log | grep "AI\|ERROR"
```

### Debug Modu

```python
# app.py içinde debug modunu aktifleştir
app.config['DEBUG'] = True
```

## 🤝 Katkıda Bulunma

### Geliştirme Ortamı

1. **Projeyi Fork Et**
2. **Geliştirme Branch'i Oluştur**:
   ```bash
   git checkout -b feature/ai-improvement
   ```
3. **Değişiklikleri Test Et**:
   ```bash
   python test_ai_system.py
   ```
4. **Pull Request Gönder**

### Kod Standartları

- **Python**: PEP 8 standartlarını takip et
- **Dokümantasyon**: Tüm fonksiyonlar için docstring ekle
- **Test**: Yeni özellikler için test yaz
- **Logging**: Uygun log seviyelerini kullan

### Yeni Model Ekleme

1. **Model Sınıfı Oluştur**:
   ```python
   class NewAIModel:
       def __init__(self):
           # Model yükleme
           pass
       
       async def process(self, image_path):
           # İşleme mantığı
           pass
   ```

2. **AI Core'a Entegre Et**:
   ```python
   # ai_core.py içinde
   self.models['new_model'] = NewAIModel()
   ```

3. **Test Ekle**:
   ```python
   async def test_new_model(self):
       # Test kodu
       pass
   ```

## 📚 Gelişmiş Kullanım

### Özel Model Eğitimi

```python
# Kullanıcı verilerini kullanarak model eğit
from core.AI.ai_core import ai_core

# Eğitim verilerini hazırla
training_data = await get_user_training_data(user_id)

# Modeli eğit
await ai_core.train_user_model(user_id, training_data)
```

### Batch İşleme Optimizasyonu

```python
# Büyük veri setleri için optimize edilmiş işleme
async def process_large_dataset(image_paths, batch_size=32):
    results = []
    
    for i in range(0, len(image_paths), batch_size):
        batch = image_paths[i:i+batch_size]
        batch_results = await ai_core.batch_process_images(batch, user_id)
        results.extend(batch_results)
    
    return results
```

### Gerçek Zamanlı İşleme

```python
# WebSocket ile gerçek zamanlı görsel işleme
from flask_socketio import SocketIO, emit

@socketio.on('process_image')
async def handle_image_processing(data):
    result = await ai_core.process_image(data['image_path'], data['user_id'])
    emit('processing_complete', result)
```

## 🔒 Güvenlik

### Veri Güvenliği

- **Görsel Verileri**: Kullanıcı bazlı izolasyon
- **API Güvenliği**: Rate limiting ve authentication
- **Veritabanı**: Encrypted connections
- **Dosya Depolama**: Secure file handling

### Privacy

- **GDPR Uyumluluğu**: Kullanıcı verilerinin silinebilirliği
- **Veri Anonimleştirme**: Kişisel bilgilerin korunması
- **Audit Logging**: Tüm işlemlerin loglanması

## 📈 Performans Optimizasyonu

### Hardware Önerileri

- **CPU**: Intel i7 veya AMD Ryzen 7 (8+ cores)
- **RAM**: 16GB+ (32GB önerilir)
- **GPU**: NVIDIA GTX 1060+ (opsiyonel ama önerilir)
- **Storage**: SSD (NVMe önerilir)

### Software Optimizasyonu

1. **Model Caching**:
   ```python
   # Model sonuçlarını cache'le
   @lru_cache(maxsize=1000)
   def cached_model_inference(image_hash):
       return model.predict(image_hash)
   ```

2. **Async Processing**:
   ```python
   # Paralel işleme için asyncio kullan
   tasks = [process_image(path) for path in image_paths]
   results = await asyncio.gather(*tasks)
   ```

3. **Database Optimization**:
   ```sql
   -- Performans için indeksler
   CREATE INDEX idx_ai_processing_user_status ON ai_processing_results(user_id, status);
   CREATE INDEX idx_image_hash ON image_similarity_hashes(md5_hash);
   ```

## 🔄 Güncelleme ve Bakım

### Sistem Güncellemeleri

```bash
# AI bağımlılıklarını güncelle
pip install --upgrade torch torchvision transformers

# Veritabanı migrasyonlarını çalıştır
mysql -u username -p database_name < core/Database/ai_migrations_v2.sql
```

### Model Güncellemeleri

```python
# Yeni model versiyonlarını yükle
await ai_core.update_models()

# Model performansını test et
await ai_core.validate_models()
```

### Veri Temizleme

```sql
-- Eski işleme sonuçlarını temizle (90 gün öncesi)
DELETE FROM ai_processing_results 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- Kullanılmayan hash'leri temizle
DELETE FROM image_similarity_hashes 
WHERE image_path NOT IN (SELECT DISTINCT image_path FROM ai_processing_results);
```

## 📞 Destek

### Dokümantasyon

- **API Dokümantasyonu**: `/api/ai/docs`
- **Model Dokümantasyonu**: `docs/models/`
- **Deployment Guide**: `docs/deployment/`

### Topluluk

- **GitHub Issues**: Bug raporları ve özellik istekleri
- **Discussions**: Genel sorular ve tartışmalar
- **Wiki**: Detaylı kullanım örnekleri

### Profesyonel Destek

Enterprise kullanım için profesyonel destek mevcuttur:
- Model özelleştirme
- Performans optimizasyonu
- Özel entegrasyon
- SLA garantisi

---

## 🎉 Sonuç

PofuAi AI Sistemi, modern görsel içerik yönetimi için kapsamlı bir çözüm sunar. Enterprise seviye performans, kullanıcı dostu API'ler ve gelişmiş özelliklerle projelerinizi bir sonraki seviyeye taşır.

**Özellikler Özeti**:
- 🖼️ Gelişmiş görsel tanıma ve analiz
- 🏷️ Akıllı kategorilendirme sistemi  
- 👤 Kişiselleştirilmiş kullanıcı deneyimi
- 💾 Optimize edilmiş depolama yönetimi
- ⚡ Yüksek performans ve ölçeklenebilirlik
- 🔒 Güvenli ve privacy-friendly
- 🧪 Kapsamlı test coverage
- 📊 Detaylı monitoring ve analytics

**Başlamak için**:
1. `python install_ai_dependencies.py` - Bağımlılıkları yükle
2. `python test_ai_system.py` - Sistemi test et  
3. `python app.py` - Uygulamayı başlat
4. API'leri keşfet ve geliştirmeye başla!

---

*PofuAi AI System - Görsellerinizi Akıllıca Yönetin* 🚀