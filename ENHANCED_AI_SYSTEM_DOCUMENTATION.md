# PofuAi Gelişmiş AI Sistemi Dokümantasyonu

## 🚀 Genel Bakış

PofuAi, son teknoloji AI modellerini kullanarak kullanıcılara kişiselleştirilmiş ve akıllı hizmetler sunan gelişmiş bir AI sistemidir. Sistem, görüntü işleme, doğal dil işleme, gerçek zamanlı analiz ve öğrenme yeteneklerini bir araya getirmektedir.

## 📋 İçindekiler

1. [Sistem Mimarisi](#sistem-mimarisi)
2. [Temel Bileşenler](#temel-bileşenler)
3. [Gelişmiş Özellikler](#gelişmiş-özellikler)
4. [API Referansı](#api-referansı)
5. [Kullanım Örnekleri](#kullanım-örnekleri)
6. [Performans ve Optimizasyon](#performans-ve-optimizasyon)
7. [Güvenlik](#güvenlik)
8. [Kurulum ve Yapılandırma](#kurulum-ve-yapılandırma)

## 🏗️ Sistem Mimarisi

### Katmanlı Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                     Kullanıcı Arayüzü                       │
│                  (Web, Mobile, API Clients)                 │
├─────────────────────────────────────────────────────────────┤
│                    WebSocket Layer                          │
│                 (Gerçek Zamanlı İletişim)                   │
├─────────────────────────────────────────────────────────────┤
│                      API Gateway                            │
│                  (REST API Endpoints)                       │
├─────────────────────────────────────────────────────────────┤
│                   AI Controller Layer                       │
│              (İstek Yönetimi ve Yönlendirme)               │
├─────────────────────────────────────────────────────────────┤
│                    AI Core Services                         │
│  ┌─────────────┬──────────────┬──────────────┬────────────┐│
│  │Enhanced Core│Learning Engine│Realtime Proc.│Adv.Features││
│  └─────────────┴──────────────┴──────────────┴────────────┘│
├─────────────────────────────────────────────────────────────┤
│                     Model Layer                             │
│  (CLIP, BLIP, GPT-2, YOLO, Custom Models)                 │
├─────────────────────────────────────────────────────────────┤
│                   Data & Storage Layer                      │
│              (MySQL, File Storage, Cache)                   │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Temel Bileşenler

### 1. AI Core (`ai_core.py`)
Temel AI işlevselliğini sağlayan merkezi modül.

**Özellikler:**
- Model yönetimi ve yükleme
- Görüntü sınıflandırma (ResNet-50)
- Nesne algılama (YOLO)
- Metin analizi
- Performans metrikleri

### 2. Enhanced AI Core (`ai_enhanced_core.py`)
Gelişmiş AI yetenekleri sunan modül.

**Özellikler:**
- CLIP modeli ile görsel-metin eşleştirme
- BLIP modeli ile görsel açıklama üretimi
- Çoklu dil desteği (TR-EN çeviri)
- Görsel kalite değerlendirme
- Estetik analiz
- Akıllı görsel iyileştirme

### 3. Learning Engine (`ai_learning_engine.py`)
Kullanıcı davranışlarını öğrenen ve kişiselleştirme sağlayan modül.

**Özellikler:**
- Kullanıcı davranış analizi
- Kişiselleştirilmiş model eğitimi
- Öneri sistemi
- Geri bildirim işleme
- Desen tanıma

### 4. Realtime Processor (`ai_realtime_processor.py`)
Gerçek zamanlı AI işleme ve görev yönetimi.

**Özellikler:**
- Asenkron görev kuyruğu
- Öncelik bazlı işleme
- WebSocket bildirimleri
- Video stream işleme
- İlerleme takibi

### 5. Advanced Features (`ai_advanced_features.py`)
Rol bazlı gelişmiş AI özellikleri.

**Özellikler:**
- AI destekli ürün düzenleme (Admin only)
- Sosyal medya şablon üretimi
- İçerik yönetimi ve optimizasyonu
- Rol bazlı erişim kontrolü

## 🌟 Gelişmiş Özellikler

### 1. Görsel Analiz ve İşleme

#### Gelişmiş Görsel Analizi
```python
# Endpoint: POST /api/ai/analysis/advanced
{
    "image_path": "/path/to/image.jpg",
    "analysis_types": ["caption", "quality", "emotion", "segmentation", "aesthetic"]
}

# Yanıt:
{
    "success": true,
    "data": {
        "analyses": {
            "caption": {
                "caption_en": "A beautiful sunset over the ocean",
                "caption_tr": "Okyanus üzerinde güzel bir gün batımı",
                "keywords": ["sunset", "ocean", "sky"],
                "confidence": 0.95
            },
            "quality": {
                "resolution": [1920, 1080],
                "sharpness_score": 0.85,
                "overall_score": 0.82,
                "quality_level": "excellent"
            },
            "aesthetic": {
                "aesthetic_score": 0.78,
                "composition": {...},
                "color_harmony": {...},
                "recommendations": [...]
            }
        }
    }
}
```

#### Akıllı Görsel İyileştirme
```python
# Endpoint: POST /api/ai/enhance-image
{
    "image_path": "/path/to/image.jpg",
    "enhancement_type": "auto"  # auto, artistic, manual
}

# Yanıt:
{
    "success": true,
    "original_path": "/path/to/image.jpg",
    "enhanced_path": "/path/to/image_enhanced.jpg",
    "improvements": {
        "sharpness_improvement": 0.15,
        "contrast_improvement": 0.12,
        "overall_improvement": 0.18
    }
}
```

### 2. Kişiselleştirme ve Öğrenme

#### Model Eğitimi
```python
# Endpoint: POST /api/ai/learning/train
{
    "user_id": 123
}

# Yanıt:
{
    "success": true,
    "model_updated": true,
    "performance": {
        "avg_loss": 0.023,
        "data_points": 150
    },
    "next_update": "2024-01-15T10:00:00"
}
```

#### Kişiselleştirilmiş Öneriler
```python
# Endpoint: POST /api/ai/learning/recommendations
{
    "user_id": 123,
    "context": {
        "current_page": "products",
        "time_of_day": "evening",
        "device": "mobile"
    }
}

# Yanıt:
{
    "success": true,
    "recommendations": [...],
    "personalization_level": "high"
}
```

### 3. Gerçek Zamanlı İşleme

#### WebSocket Bağlantısı
```javascript
// Client-side JavaScript
const socket = io();

socket.on('connect', () => {
    console.log('Connected to AI system');
});

// AI görevi gönder
socket.emit('ai_task', {
    task_type: 'image_analysis',
    task_data: {
        image_path: '/path/to/image.jpg'
    },
    priority: 3
});

// İlerleme takibi
socket.on('ai_progress', (data) => {
    console.log(`Task ${data.task_id}: ${data.progress}% - ${data.message}`);
});

// Sonuç
socket.on('ai_result', (data) => {
    console.log('Task completed:', data.result);
});
```

### 4. Rol Bazlı AI Hizmetleri

#### Hizmet Seviyeleri

| Rol | Seviye | Özellikler | Günlük Limit |
|-----|--------|------------|--------------|
| Admin | Enterprise | Tüm özellikler | Sınırsız |
| Moderator | Premium | Gelişmiş özellikler | 1000 |
| User | Standard | Temel özellikler | 100 |
| Guest | Basic | Sadece görüntüleme | 10 |

#### AI Ürün Editörü (Admin Only)
```python
# Endpoint: POST /api/ai/product-editor
{
    "product_id": "prod_123",
    "product_data": {
        "name": "Ürün Adı",
        "image": "/path/to/product.jpg",
        "category": "elektronik"
    }
}

# Yanıt:
{
    "success": true,
    "enhanced_data": {
        "ai_description": "AI tarafından oluşturulan açıklama...",
        "suggested_categories": ["elektronik", "teknoloji"],
        "seo_keywords": ["keyword1", "keyword2"],
        "quality_score": 0.85,
        "price_suggestion": {...}
    }
}
```

## 📡 API Referansı

### Temel Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/api/ai/analyze` | Temel görsel analizi |
| POST | `/api/ai/categorize` | Akıllı kategorizasyon |
| POST | `/api/ai/product-editor` | AI ürün düzenleme (Admin) |
| POST | `/api/ai/generate-template` | Şablon üretimi |
| GET | `/api/ai/status` | Sistem durumu |

### Gelişmiş Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/api/ai/analysis/advanced` | Gelişmiş görsel analizi |
| POST | `/api/ai/enhance-image` | Görsel iyileştirme |
| POST | `/api/ai/realtime/submit` | Gerçek zamanlı görev |
| GET | `/api/ai/realtime/status/:id` | Görev durumu |
| POST | `/api/ai/learning/train` | Model eğitimi |
| POST | `/api/ai/learning/recommendations` | Öneriler |
| POST | `/api/ai/learning/feedback` | Geri bildirim |
| POST | `/api/ai/learning/patterns` | Desen analizi |

## 💻 Kullanım Örnekleri

### 1. Toplu Görsel İşleme
```python
import requests

# Toplu görsel analizi
response = requests.post('http://localhost:5000/api/ai/realtime/submit', json={
    'task_type': 'batch_processing',
    'task_data': {
        'image_paths': [
            '/path/to/image1.jpg',
            '/path/to/image2.jpg',
            '/path/to/image3.jpg'
        ]
    },
    'priority': 2
})

task_id = response.json()['task_id']

# Durumu kontrol et
status = requests.get(f'http://localhost:5000/api/ai/realtime/status/{task_id}')
print(status.json())
```

### 2. Sosyal Medya Şablon Üretimi
```python
# Instagram story şablonu
response = requests.post('http://localhost:5000/api/ai/generate-template', json={
    'platform': 'instagram',
    'template_type': 'story',
    'content': {
        'title': 'Yeni Ürün',
        'description': 'Harika indirimler!',
        'image': '/path/to/product.jpg'
    },
    'style': 'modern'
})

template = response.json()
print(f"Şablon URL: {template['template_url']}")
print(f"Önerilen hashtag'ler: {template['suggested_hashtags']}")
```

### 3. Kullanıcı Geri Bildirimi
```python
# Öneri değerlendirmesi
response = requests.post('http://localhost:5000/api/ai/learning/feedback', json={
    'type': 'rating',
    'item_id': 'rec_123',
    'item_type': 'product_recommendation',
    'rating': 5,
    'comment': 'Harika bir öneri!'
})
```

## ⚡ Performans ve Optimizasyon

### Model Yükleme Stratejileri

1. **Lazy Loading**: Modeller sadece gerektiğinde yüklenir
2. **Model Caching**: Yüklenen modeller bellekte tutulur
3. **Device Optimization**: CUDA/MPS/CPU otomatik seçimi

### Paralel İşleme

- Asenkron görev işleme
- Worker pool (varsayılan: 4 worker)
- Öncelik bazlı kuyruk yönetimi

### Performans Metrikleri

```python
# Endpoint: GET /api/ai/realtime/metrics
{
    "realtime_metrics": {
        "total_tasks": 1523,
        "completed_tasks": 1456,
        "failed_tasks": 12,
        "average_processing_time": 2.34,
        "active_tasks": 5,
        "worker_pool_size": 4
    },
    "ai_core_metrics": {
        "models_loaded": 8,
        "total_predictions": 15234,
        "average_inference_time": 0.123
    }
}
```

## 🔒 Güvenlik

### Rol Bazlı Erişim Kontrolü (RBAC)

- Admin: Tüm AI özelliklerine erişim
- Moderator: Gelişmiş özellikler (ürün düzenleme hariç)
- User: Temel AI özellikleri
- Guest: Sadece görüntüleme

### API Güvenliği

- Session bazlı kimlik doğrulama
- Rate limiting
- Input validation
- SQL injection koruması

### Veri Güvenliği

- Kullanıcı verilerinin anonimleştirilmesi
- Model eğitiminde gizlilik koruması
- Güvenli dosya yükleme ve saklama

## 🛠️ Kurulum ve Yapılandırma

### Gereksinimler

```bash
# Python 3.8+
# MySQL 5.7+
# Redis (opsiyonel, cache için)

# Python paketleri
pip install -r requirements.txt
```

### requirements.txt
```
flask==2.3.0
flask-socketio==5.3.0
torch==2.0.0
torchvision==0.15.0
transformers==4.30.0
opencv-python==4.7.0
pillow==9.5.0
numpy==1.24.0
scikit-learn==1.2.0
mysql-connector-python==8.0.33
```

### Yapılandırma

```python
# config/ai_config.py
AI_CONFIG = {
    'model_cache_dir': 'storage/models',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'supported_formats': ['jpg', 'jpeg', 'png', 'webp'],
    'worker_pool_size': 4,
    'task_timeout': 300,  # 5 dakika
    'model_update_frequency': 7  # gün
}
```

### Veritabanı Kurulumu

```bash
# AI tabloları oluştur
mysql -u root -p < core/Database/ai_migrations.sql
mysql -u root -p < core/Database/ai_learning_migrations.sql
```

### Başlatma

```bash
# Development
python app.py

# Production (Gunicorn ile)
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

## 📈 Gelecek Geliştirmeler

1. **Video Analizi**: Gerçek zamanlı video işleme ve analiz
2. **Ses İşleme**: Konuşma tanıma ve sentez
3. **3D Model İşleme**: 3D görsel analiz ve düzenleme
4. **Federated Learning**: Gizlilik korumalı dağıtık öğrenme
5. **AutoML**: Otomatik model seçimi ve optimizasyon

## 🤝 Katkıda Bulunma

AI sistemini geliştirmek için:

1. Yeni model entegrasyonları
2. Performans optimizasyonları
3. Yeni özellik önerileri
4. Bug raporları ve düzeltmeler

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

**Not**: Bu dokümantasyon, PofuAi Gelişmiş AI Sistemi'nin mevcut durumunu yansıtmaktadır ve sürekli güncellenmektedir.