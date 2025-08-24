# PofuAI - AI-Powered E-Commerce Platform

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

**Gelişmiş AI teknolojileri ile desteklenen, kurumsal seviye e-ticaret platformu**

</div>

## 🚀 Özellikler

### 🤖 AI & Machine Learning
- **Görüntü İşleme**: Ürün fotoğraflarını otomatik analiz ve optimize etme
- **Doğal Dil İşleme**: Ürün açıklamalarını otomatik oluşturma
- **Sosyal Medya Şablon Üretimi**: AI destekli içerik oluşturma
- **Tahminleme**: Satış ve stok tahminleme modelleri

### 🛒 E-Ticaret Entegrasyonları
- **Trendyol** - Tam entegrasyon
- **Hepsiburada** - Ürün yönetimi
- **N11** - Otomatik senkronizasyon
- **GittiGidiyor** - Toplu işlemler
- **Amazon** - SP-API desteği
- **eBay** - Global satış

### 💳 Ödeme Sistemleri
- **İyzico** - Güvenli ödeme
- **PayTR** - Sanal POS
- **Stripe** - Global ödemeler
- **PayPal** - Uluslararası işlemler

### 📱 Sosyal Medya Yönetimi
- Instagram, Facebook, Twitter/X entegrasyonu
- Otomatik içerik paylaşımı
- Performans analizi
- Toplu şablon üretimi

### 🚚 Kargo Entegrasyonları
- MNG Kargo
- Yurtiçi Kargo
- Aras Kargo
- PTT Kargo
- Sürat Kargo

## 📋 Gereksinimler

- Python 3.11+
- MySQL 8.0+ veya SQLite
- Redis (opsiyonel, cache için)
- Docker & Docker Compose (opsiyonel)

## 🛠️ Kurulum

### 1. Hızlı Kurulum (Docker)

```bash
# Repoyu klonla
git clone https://github.com/yourusername/pofuai.git
cd pofuai

# Environment dosyasını oluştur
cp .env.example .env

# Docker ile başlat
docker-compose up -d

# Tarayıcıda aç
# http://localhost
```

### 2. Manuel Kurulum

```bash
# Repoyu klonla
git clone https://github.com/yourusername/pofuai.git
cd pofuai

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements-minimal.txt

# Veritabanını başlat
python init_database.py

# Uygulamayı başlat
python run_app.py
```

## 🔧 Yapılandırma

### Environment Değişkenleri

`.env` dosyasını düzenleyerek aşağıdaki ayarları yapılandırın:

```env
# Temel Ayarlar
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Veritabanı
DATABASE_URL=mysql://user:pass@localhost/pofuai

# Redis (Cache)
REDIS_URL=redis://localhost:6379/0

# E-Ticaret API'leri
TRENDYOL_API_KEY=your-api-key
HEPSIBURADA_USERNAME=your-username

# Ödeme Sistemleri
IYZICO_API_KEY=your-api-key
PAYTR_MERCHANT_ID=your-merchant-id
```

## 📁 Proje Yapısı

```
pofuai/
├── app/                    # Uygulama modülleri
│   ├── Controllers/        # İstek kontrolcüleri
│   ├── Models/            # Veri modelleri
│   └── Middleware/        # Ara katman yazılımları
├── core/                  # Çekirdek sistem
│   ├── AI/               # AI modülleri
│   ├── Database/         # Veritabanı bağlantıları
│   ├── Services/         # İş mantığı servisleri
│   └── Route/            # URL yönlendirmeleri
├── config/               # Yapılandırma dosyaları
├── public/               # Statik dosyalar
│   ├── Views/           # HTML şablonları
│   └── static/          # CSS, JS, resimler
├── storage/             # Depolama dizini
│   ├── database/        # SQLite veritabanı
│   ├── logs/           # Log dosyaları
│   └── sessions/       # Oturum dosyaları
├── docker-compose.yml   # Docker yapılandırması
├── Dockerfile          # Docker imajı
└── requirements.txt    # Python bağımlılıkları
```

## 🚀 Kullanım

### Demo Giriş Bilgileri

```
Email: admin@example.com
Şifre: password123
```

### API Endpoints

#### Temel Endpoints
- `GET /` - Ana sayfa
- `GET /dashboard` - Kontrol paneli
- `POST /auth/login` - Giriş
- `GET /auth/logout` - Çıkış

#### AI API
- `POST /api/ai/process-image` - Görüntü işleme
- `POST /api/ai/generate-template` - Şablon oluşturma
- `POST /api/ai/analyze-content` - İçerik analizi

#### E-Ticaret API
- `GET /api/products` - Ürün listesi
- `POST /api/products/sync` - Platform senkronizasyonu
- `POST /api/orders/process` - Sipariş işleme

## 🧪 Test

```bash
# Tüm testleri çalıştır
pytest

# Coverage ile test
pytest --cov=app --cov=core

# Sistem testleri
python test_system.py
```

## 🐳 Docker Deployment

### Production Build

```bash
# Production image oluştur
docker build -t pofuai:latest .

# Container'ı başlat
docker run -d \
  --name pofuai \
  -p 80:5000 \
  -v $(pwd)/storage:/app/storage \
  --env-file .env \
  pofuai:latest
```

### Docker Compose ile Full Stack

```bash
# Tüm servisleri başlat (Web, DB, Redis, Nginx)
docker-compose up -d

# Logları izle
docker-compose logs -f

# Durdur
docker-compose down
```

## 📊 Performans

- **Yanıt Süresi**: < 200ms (ortalama)
- **Eşzamanlı Kullanıcı**: 1000+
- **Günlük İşlem**: 100.000+
- **Uptime**: %99.9

## 🔒 Güvenlik

- HTTPS zorunlu (production)
- SQL Injection koruması
- XSS/CSRF koruması
- Rate limiting
- JWT token authentication
- Şifrelenmiş API anahtarları
- Role-based access control (RBAC)

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add feature'`)
4. Branch'i push edin (`git push origin feature/amazing`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim & Destek

- **Email**: support@pofuai.com
- **Website**: https://pofuai.com
- **Documentation**: https://docs.pofuai.com

## 🙏 Teşekkürler

Bu projenin geliştirilmesinde emeği geçen tüm katkıda bulunanlara teşekkür ederiz.

---

<div align="center">
Made with ❤️ by PofuAI Team
</div>