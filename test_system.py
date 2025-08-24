#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Test Script
Sistem bileşenlerini test eder
"""

import sys
import os

def test_imports():
    """Temel import'ları test et"""
    print("Testing imports...")
    try:
        import flask
        import mysql.connector
        import pandas
        import numpy
        print("✓ All basic imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_directories():
    """Gerekli dizinlerin varlığını kontrol et"""
    print("Testing directories...")
    required_dirs = [
        "storage",
        "public",
        "core",
        "app",
        "config"
    ]
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ Directory '{dir_name}' exists")
        else:
            print(f"✗ Directory '{dir_name}' missing")
            return False
    
    return True

def test_config():
    """Config sistemini test et"""
    print("Testing configuration...")
    try:
        from core.Config.config import get_config
        config = get_config()
        app_name = config.get('app.name')
        print(f"✓ Config loaded, app name: {app_name}")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("=" * 50)
    print("System Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_directories,
        test_config
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
        print()
    
    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())