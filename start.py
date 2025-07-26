#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi Application Starter

Bu script, PofuAi uygulamasını başlatmak için kullanılır.
"""

import os
import sys
import subprocess
import signal
import time

# Proje kök dizini
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

def check_dependencies():
    """Bağımlılıkları kontrol et"""
    print("🔍 Checking dependencies...")
    
    try:
        import flask
        import mysql.connector
        import pandas
        import numpy
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Installing dependencies...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", "requirements.txt"
            ])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def create_directories():
    """Gerekli dizinleri oluştur"""
    print("📁 Creating required directories...")
    
    required_dirs = [
        "storage/sessions",
        "storage/logs", 
        "storage/uploads",
        "public/static/assets/css",
        "public/static/assets/js",
        "public/static/assets/images",
    ]
    
    for dir_path in required_dirs:
        full_path = os.path.join(ROOT_DIR, dir_path)
        os.makedirs(full_path, exist_ok=True)
    
    print("✅ Directories created")

def run_tests():
    """Sistem testlerini çalıştır"""
    print("\n🧪 Running system tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=True, text=True, cwd=ROOT_DIR)
        
        if result.returncode == 0:
            print("✅ All system tests passed")
            return True
        else:
            print("❌ Some system tests failed:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def start_application(port=5000, host='127.0.0.1', debug=True):
    """Uygulamayı başlat"""
    print(f"\n🚀 Starting PofuAi application on {host}:{port}")
    print(f"🌐 Application will be available at: http://{host}:{port}")
    print("🔧 Debug mode:", "ON" if debug else "OFF")
    print("\n" + "="*50)
    print("Press Ctrl+C to stop the application")
    print("="*50 + "\n")
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development' if debug else 'production'
    os.environ['FLASK_DEBUG'] = '1' if debug else '0'
    
    try:
        # Import and run the app
        import importlib.util
        spec = importlib.util.spec_from_file_location("app_module", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        app = app_module.app
        app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Application failed to start: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Ana fonksiyon"""
    print("🎯 PofuAi Application Starter")
    print("="*40)
    
    # Dependency check
    if not check_dependencies():
        print("❌ Cannot start application due to missing dependencies")
        return 1
    
    # Create directories
    create_directories()
    
    # Run tests
    if not run_tests():
        response = input("\n⚠️  Tests failed. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("🛑 Application startup cancelled")
            return 1
    
    # Start application
    try:
        start_application()
        return 0
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())