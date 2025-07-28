#!/usr/bin/env python3
"""
Basic Advanced Features Test
Temel ileri seviye özelliklerin testi
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Import testleri"""
    print("🔍 Testing Advanced Imports...")
    
    tests = [
        ("Advanced Reporting", "core.Services.advanced_reporting_service", "AdvancedReportingService"),
        ("Advanced Session", "core.Services.advanced_session_service", "AdvancedSessionService"),
        ("SEO Service", "core.Services.seo_service", "SEOService"),
        ("Security Service", "core.Services.security_service", "SecurityService"),
        ("Performance Optimizer", "core.Services.performance_optimizer", "PerformanceOptimizer"),
        ("Admin Report Controller", "app.Controllers.AdminReportController", "AdminReportController")
    ]
    
    passed = 0
    for name, module, class_name in tests:
        try:
            module_obj = __import__(module, fromlist=[class_name])
            class_obj = getattr(module_obj, class_name)
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {str(e)}")
    
    return passed, len(tests)

def test_basic_functionality():
    """Temel fonksiyonalite testleri"""
    print("🔍 Testing Basic Functionality...")
    
    passed = 0
    total = 0
    
    # Security Service - Password hashing
    try:
        from core.Services.security_service import SecurityService
        security = SecurityService()
        
        password = "test123"
        hashed = security.hash_password(password)
        is_valid = security.verify_password(password, hashed)
        
        if is_valid:
            print("  ✅ Security - Password hashing works")
            passed += 1
        else:
            print("  ❌ Security - Password hashing failed")
        total += 1
    except Exception as e:
        print(f"  ❌ Security test failed: {str(e)}")
        total += 1
    
    # SEO Service - Robots.txt
    try:
        from core.Services.seo_service import SEOService
        seo = SEOService()
        
        robots = seo.generate_robots_txt()
        if robots and len(robots) > 10:
            print(f"  ✅ SEO - Robots.txt generated ({len(robots)} chars)")
            passed += 1
        else:
            print("  ❌ SEO - Robots.txt generation failed")
        total += 1
    except Exception as e:
        print(f"  ❌ SEO test failed: {str(e)}")
        total += 1
    
    # Performance Optimizer - System monitoring
    try:
        from core.Services.performance_optimizer import PerformanceOptimizer
        optimizer = PerformanceOptimizer()
        
        perf_data = optimizer.monitor_system_performance()
        if perf_data and 'cpu_usage' in perf_data:
            print(f"  ✅ Performance - System monitoring works (CPU: {perf_data.get('cpu_usage', 0):.1f}%)")
            passed += 1
        else:
            print("  ❌ Performance - System monitoring failed")
        total += 1
    except Exception as e:
        print(f"  ❌ Performance test failed: {str(e)}")
        total += 1
    
    return passed, total

def main():
    """Ana test fonksiyonu"""
    print("🚀 Basic Advanced Features Test Starting...\n")
    
    # Import testleri
    import_passed, import_total = test_imports()
    print(f"📊 Import Results: {import_passed}/{import_total} passed\n")
    
    # Fonksiyonalite testleri
    func_passed, func_total = test_basic_functionality()
    print(f"📊 Functionality Results: {func_passed}/{func_total} passed\n")
    
    total_passed = import_passed + func_passed
    total_tests = import_total + func_total
    
    print(f"📊 Overall Results: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All basic advanced features are working!")
        
        print("\n" + "="*50)
        print("📋 BASIC ADVANCED FEATURES STATUS")
        print("="*50)
        print("✅ Service Imports - Working")
        print("✅ Security System - Basic functions working")
        print("✅ SEO Management - Basic functions working")
        print("✅ Performance Monitoring - Basic functions working")
        print("="*50)
        
        print("\n🎯 Ready for Advanced Testing:")
        print("🔒 Advanced Security Features")
        print("📊 Advanced Reporting System")
        print("🌐 Multi-language SEO")
        print("⚡ Performance Optimization")
        print("🎛️ Admin Panel Integration")
        
    else:
        print(f"⚠️ {total_tests - total_passed} features need attention")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)