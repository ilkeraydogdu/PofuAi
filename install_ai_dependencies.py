#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi AI Dependencies Installer
===============================

AI sistemi için gerekli Python bağımlılıklarını yükler
"""

import os
import sys
import subprocess
import time
from datetime import datetime


def run_command(command, description=""):
    """Komut çalıştır ve sonucu göster"""
    print(f"🔄 {description}")
    print(f"   Command: {command}")
    
    try:
        start_time = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        end_time = time.time()
        
        if result.returncode == 0:
            print(f"✅ Success ({end_time - start_time:.1f}s)")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}...")
        else:
            print(f"❌ Failed ({end_time - start_time:.1f}s)")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()[:200]}...")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def check_python_version():
    """Python versiyonunu kontrol et"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required!")
        return False
    
    print("✅ Python version OK")
    return True


def check_pip():
    """pip'in varlığını kontrol et"""
    print("📦 Checking pip...")
    
    result = subprocess.run("pip --version", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ pip found: {result.stdout.strip()}")
        return True
    else:
        print("❌ pip not found!")
        return False


def upgrade_pip():
    """pip'i güncelle"""
    return run_command(
        "python -m pip install --upgrade pip",
        "Upgrading pip to latest version"
    )


def install_basic_dependencies():
    """Temel bağımlılıkları yükle"""
    basic_packages = [
        "wheel",
        "setuptools",
        "numpy>=1.26.0",
        "pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "scikit-learn>=1.3.0",
        "matplotlib>=3.7.0",
        "pandas>=2.2.0"
    ]
    
    print("📚 Installing basic dependencies...")
    
    for package in basic_packages:
        if not run_command(
            f"pip install {package}",
            f"Installing {package}"
        ):
            print(f"⚠️  Failed to install {package}, continuing...")
    
    return True


def install_ai_dependencies():
    """AI bağımlılıklarını yükle"""
    # CPU versiyonları (daha küçük ve uyumlu)
    ai_packages = [
        "torch>=2.0.0 torchvision>=0.15.0 --index-url https://download.pytorch.org/whl/cpu",
        "transformers>=4.30.0",
        "scikit-learn>=1.3.0",
        "face-recognition>=1.3.0",
        "imagehash>=4.3.0"
    ]
    
    print("🤖 Installing AI dependencies...")
    
    for package in ai_packages:
        if not run_command(
            f"pip install {package}",
            f"Installing {package.split()[0]}"
        ):
            print(f"⚠️  Failed to install {package}, this may affect AI functionality")
    
    return True


def install_optional_dependencies():
    """Opsiyonel bağımlılıkları yükle"""
    optional_packages = [
        "redis>=4.6.0",
        "celery>=5.3.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "aiofiles>=23.0.0",
        "aiohttp>=3.8.0",
        "sentence-transformers>=2.2.0",
        "nltk>=3.8.0",
        "spacy>=3.6.0"
    ]
    
    print("🔧 Installing optional dependencies...")
    
    for package in optional_packages:
        if not run_command(
            f"pip install {package}",
            f"Installing {package}"
        ):
            print(f"⚠️  Failed to install {package}, skipping...")
    
    return True


def create_directories():
    """Gerekli dizinleri oluştur"""
    directories = [
        "storage/images",
        "storage/thumbnails", 
        "storage/backups",
        "storage/temp",
        "test_images"
    ]
    
    print("📁 Creating directories...")
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created: {directory}")
        except Exception as e:
            print(f"❌ Failed to create {directory}: {e}")
    
    return True


def test_imports():
    """Kritik modüllerin import edilebilirliğini test et"""
    test_modules = [
        ("numpy", "np"),
        ("PIL", "Image"),
        ("cv2", None),
        ("sklearn", None),
        ("torch", None),
        ("transformers", None),
        ("face_recognition", None)
    ]
    
    print("🧪 Testing imports...")
    
    failed_imports = []
    
    for module_name, alias in test_modules:
        try:
            if alias:
                exec(f"import {module_name} as {alias}")
            else:
                exec(f"import {module_name}")
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            failed_imports.append(module_name)
        except Exception as e:
            print(f"⚠️  {module_name}: {e}")
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {', '.join(failed_imports)}")
        print("   Some AI features may not work properly.")
        return False
    else:
        print("\n✅ All critical modules imported successfully!")
        return True


def download_sample_models():
    """Örnek modelleri indir (opsiyonel)"""
    print("🔽 Downloading sample AI models...")
    
    try:
        # NLTK data
        run_command(
            "python -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords')\"",
            "Downloading NLTK data"
        )
        
        # SpaCy model (küçük İngilizce model)
        run_command(
            "python -m spacy download en_core_web_sm",
            "Downloading SpaCy English model"
        )
        
    except Exception as e:
        print(f"⚠️  Model download failed: {e}")
        print("   Models can be downloaded later manually.")
    
    return True


def create_sample_test_image():
    """Örnek test görseli oluştur"""
    print("🖼️  Creating sample test image...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Basit test görseli oluştur
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='lightblue')
        draw = ImageDraw.Draw(image)
        
        # Basit şekiller çiz
        draw.rectangle([50, 50, 200, 200], fill='red', outline='black', width=3)
        draw.ellipse([300, 100, 500, 300], fill='green', outline='black', width=3)
        draw.polygon([(600, 100), (700, 50), (750, 150), (650, 200)], fill='yellow', outline='black', width=3)
        
        # Metin ekle
        try:
            # Varsayılan font kullan
            draw.text((50, 250), "PofuAi AI Test Image", fill='black')
            draw.text((50, 280), f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}", fill='black')
            draw.text((50, 310), "This is a sample image for AI testing", fill='black')
        except:
            # Font bulunamazsa basit metin
            draw.text((50, 250), "Test Image", fill='black')
        
        # Kaydet
        test_image_path = os.path.join("test_images", "sample_test_image.png")
        image.save(test_image_path)
        
        print(f"✅ Sample test image created: {test_image_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample image: {e}")
        return False


def main():
    """Ana kurulum fonksiyonu"""
    print("🚀 PofuAi AI Dependencies Installer")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    steps = [
        ("Check Python Version", check_python_version),
        ("Check pip", check_pip),
        ("Upgrade pip", upgrade_pip),
        ("Install Basic Dependencies", install_basic_dependencies),
        ("Install AI Dependencies", install_ai_dependencies),
        ("Install Optional Dependencies", install_optional_dependencies),
        ("Create Directories", create_directories),
        ("Test Imports", test_imports),
        ("Download Sample Models", download_sample_models),
        ("Create Sample Test Image", create_sample_test_image)
    ]
    
    results = {}
    start_time = time.time()
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        
        try:
            step_start = time.time()
            result = step_func()
            step_time = time.time() - step_start
            
            results[step_name] = {
                'success': result,
                'time': step_time
            }
            
            status = "✅ COMPLETED" if result else "❌ FAILED"
            print(f"{status} - {step_name} ({step_time:.1f}s)")
            
        except Exception as e:
            results[step_name] = {
                'success': False,
                'time': 0,
                'error': str(e)
            }
            print(f"❌ FAILED - {step_name} (Error: {e})")
    
    total_time = time.time() - start_time
    
    # Özet rapor
    print("\n" + "=" * 50)
    print("📋 INSTALLATION SUMMARY")
    print("=" * 50)
    
    successful = sum(1 for result in results.values() if result['success'])
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    print(f"📊 Success Rate: {successful/total:.1%}")
    print(f"⏱️  Total Time: {total_time:.1f}s")
    
    # Detaylı sonuçlar
    print("\n📊 Detailed Results:")
    for step_name, result in results.items():
        status = "✅" if result['success'] else "❌"
        time_str = f"{result['time']:.1f}s"
        error_str = f" (Error: {result.get('error', '')})" if not result['success'] and 'error' in result else ""
        print(f"   {status} {step_name}: {time_str}{error_str}")
    
    # Sonraki adımlar
    print("\n🎯 Next Steps:")
    print("1. Run the AI system test: python test_ai_system.py")
    print("2. Add your own test images to the 'test_images' directory")
    print("3. Start the Flask application: python app.py")
    print("4. Test AI endpoints via API: /api/ai/system-status")
    
    if successful == total:
        print("\n🎉 Installation completed successfully!")
        print("   All AI features should be available.")
    elif successful >= total * 0.7:  # 70% başarı
        print("\n⚠️  Installation mostly successful!")
        print("   Some optional features may not be available.")
    else:
        print("\n❌ Installation had significant issues!")
        print("   Please check the errors above and retry.")
    
    print(f"\n🏁 Installation finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)