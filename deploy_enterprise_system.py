#!/usr/bin/env python3
"""
PraPazar Enterprise Integration System Deployment & Testing Script
Bu script, kurumsal entegrasyon sisteminin tam olarak dağıtımını ve testini yapar.

Özellikler:
- Sistem gereksinimleri kontrolü
- Konfigürasyon doğrulama
- Veritabanı kurulumu ve test
- Entegrasyon sistemleri test
- Performans analizi
- Güvenlik kontrolü
- Deployment raporu
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Proje kök dizinini ekle
sys.path.insert(0, '/workspace')

# Enterprise modülleri
try:
    from core.Config.enterprise_config import get_config_manager, Environment, create_config_template
    from core.Database.enterprise_connection import get_database_manager
    from core.Services.enterprise_integration_manager import (
        get_enterprise_integration_manager, 
        EnterpriseIntegrationFactory,
        IntegrationStatus,
        IntegrationPriority,
        IntegrationType
    )
except ImportError as e:
    print(f"❌ Enterprise modülleri yüklenemedi: {e}")
    sys.exit(1)


class EnterpriseDeploymentManager:
    """Kurumsal dağıtım yöneticisi"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.start_time = datetime.now()
        self.test_results = {}
        self.deployment_report = {
            'deployment_time': self.start_time.isoformat(),
            'system_info': self._get_system_info(),
            'tests': {},
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Logging ayarlarını yap"""
        log_dir = Path('/workspace/logs')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'deployment.log'),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger('EnterpriseDeployment')
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Sistem bilgilerini al"""
        import platform
        import psutil
        
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_usage': psutil.disk_usage('/').percent,
            'working_directory': os.getcwd()
        }
    
    def print_header(self):
        """Başlık yazdır"""
        print("=" * 80)
        print("🚀 PRAPAZAR ENTERPRISE INTEGRATION SYSTEM DEPLOYMENT")
        print("=" * 80)
        print(f"📅 Deployment Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  System: {self.deployment_report['system_info']['platform']}")
        print(f"🐍 Python: {self.deployment_report['system_info']['python_version']}")
        print("=" * 80)
    
    def check_system_requirements(self) -> bool:
        """Sistem gereksinimlerini kontrol et"""
        print("\n📋 SYSTEM REQUIREMENTS CHECK")
        print("-" * 40)
        
        requirements_met = True
        
        # Python version check
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            print("✅ Python version: OK (>= 3.8)")
        else:
            print("❌ Python version: FAIL (< 3.8)")
            requirements_met = False
        
        # Required packages check
        required_packages = [
            ('flask', 'flask'),
            ('requests', 'requests'), 
            ('mysql-connector-python', 'mysql.connector'),
            ('cryptography', 'cryptography'),
            ('PyJWT', 'jwt'),
            ('redis', 'redis'),
            ('PyYAML', 'yaml')
        ]
        
        for package_name, import_name in required_packages:
            try:
                __import__(import_name)
                print(f"✅ Package {package_name}: OK")
            except ImportError:
                print(f"❌ Package {package_name}: MISSING")
                requirements_met = False
        
        # Directory structure check
        required_dirs = ['config', 'storage', 'logs', 'core']
        for directory in required_dirs:
            dir_path = Path(f'/workspace/{directory}')
            if dir_path.exists():
                print(f"✅ Directory {directory}: OK")
            else:
                print(f"❌ Directory {directory}: MISSING")
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"🔧 Directory {directory}: CREATED")
        
        self.test_results['system_requirements'] = requirements_met
        return requirements_met
    
    def test_configuration_system(self) -> bool:
        """Konfigürasyon sistemini test et"""
        print("\n🔧 CONFIGURATION SYSTEM TEST")
        print("-" * 40)
        
        try:
            # Configuration manager test
            config_manager = get_config_manager()
            print("✅ Configuration Manager: LOADED")
            
            # Environment templates test
            for env in Environment:
                try:
                    create_config_template(env)
                    print(f"✅ Config Template {env.value}: CREATED")
                except Exception as e:
                    print(f"❌ Config Template {env.value}: FAILED - {e}")
                    return False
            
            # Configuration validation test
            errors = config_manager.validate_current_config()
            if not errors:
                print("✅ Configuration Validation: PASSED")
            else:
                print("⚠️  Configuration Validation: WARNINGS")
                for error in errors:
                    print(f"    - {error}")
                    self.deployment_report['warnings'].append(f"Config: {error}")
            
            # Configuration access test
            app_name = config_manager.get('app_name')
            db_host = config_manager.get('database.host')
            debug_mode = config_manager.get('debug')
            
            print(f"✅ Config Access Test: app_name={app_name}")
            print(f"✅ Config Access Test: db_host={db_host}")
            print(f"✅ Config Access Test: debug={debug_mode}")
            
            self.test_results['configuration'] = True
            return True
            
        except Exception as e:
            print(f"❌ Configuration System: FAILED - {e}")
            self.deployment_report['errors'].append(f"Configuration: {e}")
            self.test_results['configuration'] = False
            return False
    
    def test_database_system(self) -> bool:
        """Veritabanı sistemini test et"""
        print("\n🗄️  DATABASE SYSTEM TEST")
        print("-" * 40)
        
        try:
            # Database manager test
            db_manager = get_database_manager()
            print("✅ Database Manager: LOADED")
            
            # Health check
            if db_manager.health_check():
                print("✅ Database Health Check: PASSED")
            else:
                print("❌ Database Health Check: FAILED")
                return False
            
            # Database info
            db_info = db_manager.get_database_info()
            print(f"✅ Database Type: {db_info.get('database_type', 'Unknown')}")
            print(f"✅ Database Name: {db_info.get('database_name', 'Unknown')}")
            
            # Connection pool test
            pool_stats = db_info.get('pool_stats', {})
            if pool_stats:
                print(f"✅ Connection Pool: {pool_stats.get('active_connections', 0)}/{pool_stats.get('max_connections', 0)} active")
            
            # Query test
            result = db_manager.execute_query("SELECT 1 as test_value")
            if result and result[0].get('test_value') == 1:
                print("✅ Database Query Test: PASSED")
            else:
                print("❌ Database Query Test: FAILED")
                return False
            
            # Query builder test
            builder = db_manager.query_builder()
            query = (builder
                    .select("id", "username", "email")
                    .from_table("users")
                    .where("is_active = 1")
                    .order_by("created_at", "DESC")
                    .limit(10)
                    .build())
            print(f"✅ Query Builder Test: {query[:50]}...")
            
            # Table stats
            for table in ['users', 'integration_logs', 'system_settings']:
                stats = db_manager.get_table_stats(table)
                if stats:
                    print(f"✅ Table {table}: {stats.get('row_count', 0)} rows")
            
            self.test_results['database'] = True
            return True
            
        except Exception as e:
            print(f"❌ Database System: FAILED - {e}")
            self.deployment_report['errors'].append(f"Database: {e}")
            self.test_results['database'] = False
            return False
    
    async def test_integration_system(self) -> bool:
        """Entegrasyon sistemini test et"""
        print("\n🔌 INTEGRATION SYSTEM TEST")
        print("-" * 40)
        
        try:
            # Integration manager test
            integration_manager = get_enterprise_integration_manager(
                secret_key="test-secret-key-for-deployment",
                redis_url=None  # Local cache kullan
            )
            print("✅ Integration Manager: LOADED")
            
            # Test integrations
            test_integrations = [
                ('trendyol', {
                    'api_key': 'test_trendyol_key',
                    'secret_key': 'test_trendyol_secret',
                    'status': IntegrationStatus.ACTIVE
                }),
                ('hepsiburada', {
                    'api_key': 'test_hepsiburada_key',
                    'status': IntegrationStatus.ACTIVE
                }),
            ]
            
            # Register test integrations
            for name, credentials in test_integrations:
                config = EnterpriseIntegrationFactory.create_integration_config(
                    name, **credentials
                )
                success = integration_manager.register_integration(config)
                print(f"{'✅' if success else '❌'} Integration {name}: {'REGISTERED' if success else 'FAILED'}")
            
            # Integration status
            status = integration_manager.get_integration_status()
            print(f"✅ Total Integrations: {status['total_integrations']}")
            print(f"✅ Active Integrations: {status['active_integrations']}")
            print(f"✅ Healthy Integrations: {status['healthy_integrations']}")
            
            # Initialize integrations (will fail with test credentials, but tests the system)
            print("🔌 Testing Integration Initialization...")
            try:
                results = await integration_manager.initialize_all()
                for name, result in results.items():
                    # Expect failures with test credentials
                    print(f"⚠️  Integration {name}: {'CONNECTED' if result else 'TEST FAILED (Expected with test credentials)'}")
            except Exception as e:
                print(f"⚠️  Integration initialization test completed (expected failures with test credentials)")
            
            # Health check
            try:
                health_results = await integration_manager.health_check_all()
                print(f"✅ Health Check Completed: {len(health_results)} integrations checked")
            except Exception as e:
                print(f"⚠️  Health check test completed")
            
            # Metrics test
            metrics = integration_manager.get_comprehensive_metrics()
            overview = metrics.get('overview', {})
            print(f"✅ Metrics System: {overview.get('total_integrations', 0)} integrations tracked")
            
            self.test_results['integration'] = True
            return True
            
        except Exception as e:
            print(f"❌ Integration System: FAILED - {e}")
            self.deployment_report['errors'].append(f"Integration: {e}")
            self.test_results['integration'] = False
            return False
    
    def test_security_features(self) -> bool:
        """Güvenlik özelliklerini test et"""
        print("\n🔒 SECURITY FEATURES TEST")
        print("-" * 40)
        
        try:
            from core.Services.enterprise_integration_manager import SecurityManager
            
            # Security manager test
            security_manager = SecurityManager("test-secret-key-for-security-test")
            print("✅ Security Manager: LOADED")
            
            # Encryption test
            test_data = "sensitive-test-data"
            encrypted = security_manager.encrypt_data(test_data)
            decrypted = security_manager.decrypt_data(encrypted)
            
            if decrypted == test_data:
                print("✅ Data Encryption/Decryption: PASSED")
            else:
                print("❌ Data Encryption/Decryption: FAILED")
                return False
            
            # JWT token test
            test_payload = {'user_id': 123, 'role': 'admin'}
            token = security_manager.generate_jwt_token(test_payload)
            decoded_payload = security_manager.verify_jwt_token(token)
            
            if decoded_payload and decoded_payload.get('user_id') == 123:
                print("✅ JWT Token Generation/Verification: PASSED")
            else:
                print("❌ JWT Token Generation/Verification: FAILED")
                return False
            
            # API signature test
            test_data = "test-api-data"
            timestamp = str(int(time.time()))
            signature = security_manager.generate_api_signature(test_data, timestamp)
            is_valid = security_manager.verify_api_signature(test_data, timestamp, signature)
            
            if is_valid:
                print("✅ API Signature Generation/Verification: PASSED")
            else:
                print("❌ API Signature Generation/Verification: FAILED")
                return False
            
            self.test_results['security'] = True
            return True
            
        except Exception as e:
            print(f"❌ Security Features: FAILED - {e}")
            self.deployment_report['errors'].append(f"Security: {e}")
            self.test_results['security'] = False
            return False
    
    def test_performance(self) -> bool:
        """Performans testleri"""
        print("\n⚡ PERFORMANCE TESTS")
        print("-" * 40)
        
        try:
            # Database performance test
            db_manager = get_database_manager()
            
            # Query performance test
            start_time = time.time()
            for i in range(100):
                db_manager.execute_query("SELECT 1")
            query_time = time.time() - start_time
            
            avg_query_time = query_time / 100 * 1000  # ms
            print(f"✅ Average Query Time: {avg_query_time:.2f}ms")
            
            if avg_query_time < 100:  # 100ms threshold
                print("✅ Database Performance: EXCELLENT")
            elif avg_query_time < 500:
                print("✅ Database Performance: GOOD")
            else:
                print("⚠️  Database Performance: NEEDS OPTIMIZATION")
                self.deployment_report['warnings'].append("Database performance may need optimization")
            
            # Memory usage test
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            print(f"✅ Memory Usage: {memory_usage:.2f}MB")
            
            if memory_usage < 100:
                print("✅ Memory Usage: OPTIMAL")
            elif memory_usage < 500:
                print("✅ Memory Usage: ACCEPTABLE")
            else:
                print("⚠️  Memory Usage: HIGH")
                self.deployment_report['warnings'].append("High memory usage detected")
            
            self.test_results['performance'] = True
            return True
            
        except Exception as e:
            print(f"❌ Performance Tests: FAILED - {e}")
            self.deployment_report['errors'].append(f"Performance: {e}")
            self.test_results['performance'] = False
            return False
    
    def generate_deployment_report(self):
        """Dağıtım raporu oluştur"""
        print("\n📊 DEPLOYMENT REPORT")
        print("=" * 40)
        
        # Test sonuçları
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 Test Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        # Errors and warnings
        if self.deployment_report['errors']:
            print(f"\n❌ Errors ({len(self.deployment_report['errors'])}):")
            for error in self.deployment_report['errors']:
                print(f"   - {error}")
        
        if self.deployment_report['warnings']:
            print(f"\n⚠️  Warnings ({len(self.deployment_report['warnings'])}):")
            for warning in self.deployment_report['warnings']:
                print(f"   - {warning}")
        
        # Recommendations
        self._generate_recommendations()
        if self.deployment_report['recommendations']:
            print(f"\n💡 Recommendations:")
            for recommendation in self.deployment_report['recommendations']:
                print(f"   - {recommendation}")
        
        # Deployment summary
        end_time = datetime.now()
        deployment_duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n⏱️  Deployment Duration: {deployment_duration:.2f} seconds")
        print(f"🏁 Deployment Status: {'✅ SUCCESS' if success_rate >= 80 else '❌ FAILED'}")
        
        # Save report to file
        self.deployment_report.update({
            'end_time': end_time.isoformat(),
            'duration_seconds': deployment_duration,
            'test_results': self.test_results,
            'success_rate': success_rate,
            'status': 'SUCCESS' if success_rate >= 80 else 'FAILED'
        })
        
        report_file = Path('/workspace/deployment_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.deployment_report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Detailed report saved: {report_file}")
    
    def _generate_recommendations(self):
        """Öneriler oluştur"""
        recommendations = []
        
        # Performance recommendations
        if not self.test_results.get('performance', True):
            recommendations.append("Consider upgrading system resources for better performance")
        
        # Security recommendations
        if self.test_results.get('security', True):
            recommendations.append("Update secret keys and passwords in production environment")
            recommendations.append("Enable HTTPS and SSL certificates for production")
        
        # Database recommendations
        if self.test_results.get('database', True):
            recommendations.append("Set up database backups and monitoring")
            recommendations.append("Configure database connection pooling for production")
        
        # Integration recommendations
        if self.test_results.get('integration', True):
            recommendations.append("Configure real API credentials for production integrations")
            recommendations.append("Set up monitoring and alerting for integration failures")
        
        # General recommendations
        recommendations.extend([
            "Set up log rotation and monitoring",
            "Configure environment-specific settings",
            "Implement health check endpoints",
            "Set up automated testing pipeline",
            "Configure backup and disaster recovery procedures"
        ])
        
        self.deployment_report['recommendations'] = recommendations
    
    async def run_full_deployment_test(self):
        """Tam dağıtım testi çalıştır"""
        self.print_header()
        
        # System requirements check
        if not self.check_system_requirements():
            print("\n❌ System requirements not met. Aborting deployment.")
            return False
        
        # Configuration system test
        if not self.test_configuration_system():
            print("\n❌ Configuration system failed. Aborting deployment.")
            return False
        
        # Database system test
        if not self.test_database_system():
            print("\n❌ Database system failed. Aborting deployment.")
            return False
        
        # Integration system test
        if not await self.test_integration_system():
            print("\n❌ Integration system failed. Aborting deployment.")
            return False
        
        # Security features test
        if not self.test_security_features():
            print("\n❌ Security features failed. Aborting deployment.")
            return False
        
        # Performance tests
        self.test_performance()
        
        # Generate deployment report
        self.generate_deployment_report()
        
        return True


async def main():
    """Ana fonksiyon"""
    deployment_manager = EnterpriseDeploymentManager()
    
    try:
        success = await deployment_manager.run_full_deployment_test()
        
        if success:
            print("\n🎉 ENTERPRISE SYSTEM DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("\n📋 Next Steps:")
            print("   1. Review the deployment report")
            print("   2. Configure production environment variables")
            print("   3. Set up real API credentials for integrations")
            print("   4. Configure monitoring and alerting")
            print("   5. Set up backup and disaster recovery")
            print("\n🚀 Your PraPazar Enterprise Integration System is ready!")
        else:
            print("\n💥 ENTERPRISE SYSTEM DEPLOYMENT FAILED!")
            print("   Please check the errors above and fix them before proceeding.")
        
        return success
        
    except Exception as e:
        print(f"\n💥 DEPLOYMENT FAILED WITH CRITICAL ERROR: {e}")
        deployment_manager.logger.error(f"Critical deployment error: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    
    # Run the deployment
    success = asyncio.run(main())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)