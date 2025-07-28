#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced AI System Setup Script
===============================

PofuAi Gelişmiş AI Sistemi kurulum ve konfigürasyon scripti
"""

import os
import sys
import subprocess
import mysql.connector
from pathlib import Path

def print_header():
    """Başlık yazdır"""
    print("=" * 60)
    print("🚀 PofuAi Gelişmiş AI Sistemi Kurulum Scripti")
    print("=" * 60)
    print()

def check_python_version():
    """Python sürümünü kontrol et"""
    print("📋 Python sürümü kontrol ediliyor...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 veya üzeri gerekli!")
        print(f"   Mevcut sürüm: {sys.version}")
        return False
    print(f"✅ Python sürümü uygun: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Bağımlılıkları yükle"""
    print("\n📦 Python bağımlılıkları yükleniyor...")
    
    dependencies = [
        "torch",
        "torchvision", 
        "transformers",
        "scikit-learn",
        "opencv-python",
        "Pillow",
        "numpy",
        "requests",
        "asyncio"
    ]
    
    try:
        for dep in dependencies:
            print(f"   🔄 {dep} yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep, "--quiet"])
            print(f"   ✅ {dep} yüklendi")
        
        print("✅ Tüm bağımlılıklar başarıyla yüklendi!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Bağımlılık yükleme hatası: {e}")
        return False

def create_directories():
    """Gerekli dizinleri oluştur"""
    print("\n📁 Dizin yapısı oluşturuluyor...")
    
    directories = [
        "storage/templates",
        "storage/ai_models",
        "storage/product_edits",
        "storage/user_analyses",
        "public/uploads/templates"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory} oluşturuldu")
    
    # İzinleri ayarla
    os.chmod("storage/templates", 0o755)
    os.chmod("storage/ai_models", 0o755)
    
    print("✅ Dizin yapısı hazır!")
    return True

def setup_database():
    """Veritabanı kurulumu"""
    print("\n🗄️  Veritabanı kurulumu...")
    
    # Veritabanı bilgilerini al
    print("Veritabanı bağlantı bilgilerini girin:")
    host = input("Host (localhost): ") or "localhost"
    user = input("Kullanıcı adı (root): ") or "root"
    password = input("Şifre: ")
    database = input("Veritabanı adı (pofuai): ") or "pofuai"
    
    try:
        # Bağlantı test et
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        cursor = conn.cursor()
        
        # Migration dosyasını çalıştır
        migration_file = "core/Database/advanced_ai_migrations.sql"
        if os.path.exists(migration_file):
            print("   🔄 Gelişmiş AI tabloları oluşturuluyor...")
            
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_commands = f.read().split(';')
                
                for command in sql_commands:
                    command = command.strip()
                    if command and not command.startswith('--'):
                        try:
                            cursor.execute(command)
                        except mysql.connector.Error as e:
                            if "already exists" not in str(e).lower():
                                print(f"   ⚠️  SQL Uyarı: {e}")
            
            conn.commit()
            print("   ✅ Veritabanı tabloları oluşturuldu")
        else:
            print("   ⚠️  Migration dosyası bulunamadı")
        
        cursor.close()
        conn.close()
        
        print("✅ Veritabanı kurulumu tamamlandı!")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Veritabanı bağlantı hatası: {e}")
        return False
    except Exception as e:
        print(f"❌ Veritabanı kurulum hatası: {e}")
        return False

def create_config_file():
    """Konfigürasyon dosyası oluştur"""
    print("\n⚙️  Konfigürasyon dosyası oluşturuluyor...")
    
    config_content = """# PofuAi Gelişmiş AI Sistemi Konfigürasyonu
# Bu dosya setup_advanced_ai.py tarafından oluşturulmuştur

# AI Sistem Ayarları
ADVANCED_AI_ENABLED=true
TEMPLATE_GENERATION_ENABLED=true
PRODUCT_EDITING_ENABLED=true

# Dosya Yolları
TEMPLATE_STORAGE_PATH=storage/templates
AI_MODELS_PATH=storage/ai_models

# Performans Ayarları
MAX_BATCH_SIZE=32
MAX_TEMPLATES_PER_USER_DAILY=50
MAX_PRODUCT_EDITS_PER_ADMIN_DAILY=20

# Güvenlik Ayarları
ENABLE_RATE_LIMITING=true
ENABLE_AUDIT_LOGGING=true

# Model Ayarları
ENABLE_GPU=false
MODEL_CACHE_SIZE=1000
"""
    
    with open('.env.ai', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("   ✅ .env.ai konfigürasyon dosyası oluşturuldu")
    print("✅ Konfigürasyon hazır!")
    return True

def run_tests():
    """Temel testleri çalıştır"""
    print("\n🧪 Sistem testleri çalıştırılıyor...")
    
    try:
        # AI Core modüllerini test et
        print("   🔄 AI modülleri test ediliyor...")
        
        # Temel import testleri
        from core.AI.advanced_ai_core import advanced_ai_core
        print("   ✅ Advanced AI Core yüklendi")
        
        from core.AI.advanced_ai_helpers import ai_helpers
        print("   ✅ AI Helpers yüklendi")
        
        from app.Controllers.AdvancedAIController import AdvancedAIController
        print("   ✅ Advanced AI Controller yüklendi")
        
        # Temel fonksiyonalite testi
        metrics = advanced_ai_core.get_advanced_metrics()
        if metrics:
            print("   ✅ Metrik sistemi çalışıyor")
        
        print("✅ Tüm testler başarılı!")
        return True
        
    except ImportError as e:
        print(f"❌ Modül yükleme hatası: {e}")
        return False
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

def print_usage_instructions():
    """Kullanım talimatlarını yazdır"""
    print("\n" + "=" * 60)
    print("🎉 Kurulum Tamamlandı!")
    print("=" * 60)
    print()
    print("📋 Sonraki Adımlar:")
    print()
    print("1. 🚀 Uygulamayı başlatın:")
    print("   python app.py")
    print()
    print("2. 🧪 API'leri test edin:")
    print("   curl http://localhost:5000/api/ai/status")
    print("   curl http://localhost:5000/api/ai/health")
    print("   curl http://localhost:5000/api/ai/features")
    print()
    print("3. 📖 Dokümantasyonu okuyun:")
    print("   ADVANCED_AI_SYSTEM_README.md")
    print()
    print("4. 🎨 İlk şablonunuzu oluşturun:")
    print("   POST /api/ai/generate-template")
    print()
    print("⚠️  Önemli Notlar:")
    print("   • Admin kullanıcılar ürün düzenleme özelliğini kullanabilir")
    print("   • Şablon dosyaları storage/templates/ dizininde saklanır")
    print("   • Günlük kullanım kotaları rol bazlı olarak uygulanır")
    print("   • Sistem logları storage/logs/ dizininde tutulur")
    print()
    print("🔗 Faydalı Endpoint'ler:")
    print("   • Şablon türleri: GET /api/ai/template-types")
    print("   • Kullanıcı izinleri: GET /api/ai/permissions")
    print("   • AI geçmişi: GET /api/ai/user-history")
    print("   • Sistem metrikleri: GET /api/ai/advanced-metrics (Admin)")
    print()
    print("=" * 60)
    print("🚀 PofuAi Gelişmiş AI Sistemi Hazır!")
    print("=" * 60)

def main():
    """Ana kurulum fonksiyonu"""
    print_header()
    
    # Adım adım kurulum
    steps = [
        ("Python Sürümü Kontrolü", check_python_version),
        ("Bağımlılık Yükleme", install_dependencies),
        ("Dizin Yapısı Oluşturma", create_directories),
        ("Veritabanı Kurulumu", setup_database),
        ("Konfigürasyon Dosyası", create_config_file),
        ("Sistem Testleri", run_tests)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        try:
            if not step_func():
                failed_steps.append(step_name)
                print(f"❌ {step_name} başarısız!")
            else:
                print(f"✅ {step_name} tamamlandı!")
        except Exception as e:
            failed_steps.append(step_name)
            print(f"❌ {step_name} hatası: {e}")
    
    # Sonuçları değerlendir
    if failed_steps:
        print(f"\n⚠️  Bazı adımlar başarısız oldu: {', '.join(failed_steps)}")
        print("Lütfen hataları giderin ve tekrar deneyin.")
        return False
    else:
        print_usage_instructions()
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Kurulum kullanıcı tarafından iptal edildi.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Beklenmeyen hata: {e}")
        sys.exit(1)