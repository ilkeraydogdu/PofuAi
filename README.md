# PofuAi - Flask Web Application

PofuAi, modern web teknolojileri kullanılarak geliştirilmiş tam özellikli bir Flask web uygulamasıdır.

## 🚀 Özellikler

- **Modüler Mimari**: MVC tasarım deseni ile organize edilmiş kod yapısı
- **Güvenli Kimlik Doğrulama**: Session tabanlı kullanıcı yönetimi
- **Hata Yönetimi**: Merkezi hata yakalama ve loglama sistemi
- **API Desteği**: RESTful API endpoints
- **Veritabanı Modelleri**: MySQL ve SQLite desteği
- **Modern UI**: Bootstrap tabanlı responsive tasarım
- **Logging**: Detaylı sistem logları
- **Test Sistemi**: Otomatik sistem testleri

## 📁 Proje Yapısı

```
PofuAi/
├── app/                    # Ana uygulama paketi
│   ├── Controllers/        # Kontrolcüler
│   ├── Models/            # Veritabanı modelleri
│   └── Middleware/        # Middleware sınıfları
├── core/                  # Çekirdek sistem
│   ├── Services/          # Servis sınıfları
│   ├── Route/            # Route yönetimi
│   ├── Config/           # Konfigürasyon
│   └── Database/         # Veritabanı bağlantıları
├── public/               # Statik dosyalar
│   ├── Views/           # Template dosyaları
│   └── static/          # CSS, JS, resimler
├── storage/             # Uygulama verileri
│   ├── logs/           # Log dosyaları
│   ├── sessions/       # Session dosyaları
│   └── uploads/        # Yüklenen dosyalar
├── app.py              # Ana uygulama dosyası
├── start.py           # Uygulama başlatıcı
├── test_system.py     # Sistem test scripti
└── requirements.txt   # Python bağımlılıkları
```

## 🛠️ Kurulum

### Gereksinimler

- Python 3.8+
- pip (Python paket yöneticisi)

### Adım 1: Projeyi İndirin

```bash
git clone <repository-url>
cd PofuAi
```

### Adım 2: Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

veya sistem paketleri için:

```bash
pip install --break-system-packages -r requirements.txt
```

### Adım 3: Uygulamayı Başlatın

En kolay yol:
```bash
python3 start.py
```

Manuel başlatma:
```bash
python3 app.py
```

## 🧪 Test Etme

Sistem testlerini çalıştırmak için:

```bash
python3 test_system.py
```

Bu test şunları kontrol eder:
- Tüm modüllerin import edilebilirliği
- Gerekli dizinlerin varlığı
- Flask uygulamasının başlatılabilirliği
- Veritabanı modellerinin çalışabilirliği
- Servislerin fonksiyonelliği

## 🌐 Kullanım

Uygulama başlatıldıktan sonra:

1. Tarayıcınızda `http://127.0.0.1:5000` adresine gidin
2. Ana sayfa otomatik olarak login sayfasına yönlendirecektir
3. Geçici olarak tüm kullanıcılar admin olarak giriş yapmış sayılır

### Ana Rotalar

- `/` - Ana sayfa (login'e yönlendirme)
- `/auth/login` - Giriş sayfası
- `/auth/register` - Kayıt sayfası
- `/dashboard` - Dashboard
- `/admin` - Admin paneli
- `/api/` - API endpoints

## 🔧 Konfigürasyon

### Ortam Değişkenleri

```bash
export SECRET_KEY="your-secret-key"
export FLASK_ENV="development"
export DATABASE_URL="mysql://user:pass@localhost/dbname"
```

### Veritabanı

Uygulama hem MySQL hem de SQLite destekler. Varsayılan olarak SQLite kullanılır.

### Logging

Loglar `storage/logs/` dizininde tarih bazlı dosyalarda saklanır:
- `app_YYYY-MM-DD.log` - Günlük log dosyaları
- Otomatik log rotasyonu (10MB, 5 backup)

## 🛡️ Güvenlik

- Session tabanlı kimlik doğrulama
- CSRF koruması
- SQL injection koruması
- XSS koruması
- Güvenli dosya yükleme

## 📝 API Dokümantasyonu

### Kimlik Doğrulama API

```
POST /api/auth/login
POST /api/auth/register
POST /api/auth/logout
```

### Kullanıcı API

```
GET /api/users
GET /api/users/{id}
PUT /api/users/{id}
DELETE /api/users/{id}
```

### Bildirim API

```
GET /api/notifications
POST /api/notifications/{id}/read
POST /api/notifications/mark-all-read
```

## 🔍 Hata Ayıklama

### Log Dosyalarını İnceleme

```bash
tail -f storage/logs/app_$(date +%Y-%m-%d).log
```

### Debug Modu

Debug modu aktifken:
- Detaylı hata mesajları görüntülenir
- Otomatik reload aktiftir
- Debug toolbar kullanılabilir

### Yaygın Sorunlar

1. **Port zaten kullanımda**: Farklı bir port kullanın
   ```bash
   python3 app.py --port 8000
   ```

2. **Bağımlılık eksik**: requirements.txt'yi yeniden yükleyin
   ```bash
   pip install -r requirements.txt
   ```

3. **Dizin izinleri**: storage/ dizinine yazma izni verin
   ```bash
   chmod -R 755 storage/
   ```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 Destek

Sorularınız için:
- Issue açın
- Dokümantasyonu inceleyin
- Log dosyalarını kontrol edin

## 🔄 Sürüm Geçmişi

### v1.0.0
- İlk stabil sürüm
- Temel CRUD işlemleri
- Kullanıcı yönetimi
- API endpoints

---

**Not**: Bu uygulama geliştirme aşamasındadır. Production kullanımı için ek güvenlik önlemleri alınmalıdır.