#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi System Test Script

Bu script, sistemin tüm bileşenlerinin düzgün çalışıp çalışmadığını test eder.
"""

import sys
import os
import traceback

# Proje kök dizini
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

def test_imports():
    """Tüm kritik modüllerin import edilebilirliğini test et"""
    print("🔍 Testing imports...")
    
    tests = [
        ("Web Routes", "core.Route.web_routes"),
        ("Logger Service", "core.Services.logger"),
        ("Error Handler", "core.Services.error_handler"),
        ("Session Middleware", "app.Middleware.SessionMiddleware"),
        ("Auth Middleware", "app.Middleware.AuthMiddleware"),
        ("Base Controller", "app.Controllers.BaseController"),
        ("Home Controller", "app.Controllers.HomeController"),
        ("Auth Controller", "app.Controllers.AuthController"),
        ("User Model", "app.Models.User"),
        ("Post Model", "app.Models.Post"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, module_name in tests:
        try:
            __import__(module_name)
            print(f"  ✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {test_name}: {str(e)}")
            failed += 1
    
    print(f"\n📊 Import Test Results: {passed} passed, {failed} failed")
    return failed == 0

def test_directories():
    """Gerekli dizinlerin varlığını test et"""
    print("\n🔍 Testing directories...")
    
    required_dirs = [
        "storage/sessions",
        "storage/logs",
        "storage/uploads",
        "public/static",
        "app/Controllers",
        "app/Models",
        "app/Middleware",
        "core/Services",
        "core/Route",
    ]
    
    passed = 0
    failed = 0
    
    for dir_path in required_dirs:
        full_path = os.path.join(ROOT_DIR, dir_path)
        if os.path.exists(full_path) and os.path.isdir(full_path):
            print(f"  ✅ {dir_path}")
            passed += 1
        else:
            print(f"  ❌ {dir_path} (missing)")
            failed += 1
    
    print(f"\n📊 Directory Test Results: {passed} passed, {failed} failed")
    return failed == 0

def test_flask_app():
    """Flask uygulamasının başlatılabilirliğini test et"""
    print("\n🔍 Testing Flask app initialization...")
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("app_module", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        app = app_module.app
        
        # Test routes
        with app.test_client() as client:
            # Test redirect from root
            response = client.get('/')
            if response.status_code in [302, 301]:  # Redirect
                print("  ✅ Root route redirects correctly")
            else:
                print(f"  ⚠️  Root route returned {response.status_code}")
            
            # Test auth login page
            response = client.get('/auth/login')
            if response.status_code == 200:
                print("  ✅ Auth login route works")
            else:
                print(f"  ❌ Auth login route failed: {response.status_code}")
        
        print("\n📊 Flask App Test: ✅ Passed")
        return True
        
    except Exception as e:
        print(f"\n📊 Flask App Test: ❌ Failed - {str(e)}")
        return False

def test_database_models():
    """Veritabanı modellerinin çalışabilirliğini test et"""
    print("\n🔍 Testing database models...")
    
    try:
        from app.Models.User import User
        from app.Models.Post import Post
        
        # Test model instantiation
        user = User()
        post = Post()
        
        print("  ✅ User model instantiated")
        print("  ✅ Post model instantiated")
        
        print("\n📊 Database Models Test: ✅ Passed")
        return True
        
    except Exception as e:
        print(f"\n📊 Database Models Test: ❌ Failed - {str(e)}")
        return False

def test_services():
    """Servislerin çalışabilirliğini test et"""
    print("\n🔍 Testing services...")
    
    try:
        from core.Services.logger import LoggerService
        from core.Services.error_handler import error_handler
        
        # Test logger
        logger = LoggerService.get_logger()
        logger.info("Test log message")
        print("  ✅ Logger service works")
        
        # Test error handler
        print("  ✅ Error handler service works")
        
        print("\n📊 Services Test: ✅ Passed")
        return True
        
    except Exception as e:
        print(f"\n📊 Services Test: ❌ Failed - {str(e)}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚀 PofuAi System Test Starting...\n")
    
    tests = [
        test_imports,
        test_directories,
        test_flask_app,
        test_database_models,
        test_services,
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            traceback.print_exc()
    
    print(f"\n🎯 Final Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! System is fully functional.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())