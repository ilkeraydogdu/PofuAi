#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enterprise AI System Structure Test
===================================

Kurumsal AI sisteminin dosya yapısını ve temel konfigürasyonları test eder
(AI/ML bağımlılıkları gerektirmez)
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

print("🚀 Enterprise AI System Structure Test")
print("=" * 60)

class EnterpriseAIStructureTester:
    """Enterprise AI sistem yapısı test sınıfı"""
    
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_results = {}
        
    def test_file_structure(self):
        """Dosya yapısı testi"""
        print("\n📁 Dosya Yapısı Testi")
        print("-" * 40)
        
        # Kontrol edilecek dosyalar
        required_files = {
            'core/AI/enterprise_ai_system.py': 'Enterprise AI Core System',
            'app/Controllers/EnterpriseAIController.py': 'Enterprise AI Controller',
            'core/Route/enterprise_ai_routes.py': 'Enterprise AI Routes',
            'core/Database/enterprise_ai_migrations.sql': 'Enterprise AI Database Schema',
            'ENTERPRISE_AI_SYSTEM_README.md': 'Enterprise AI Documentation'
        }
        
        missing_files = []
        existing_files = []
        
        for file_path, description in required_files.items():
            full_path = os.path.join(self.root_dir, file_path)
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path)
                existing_files.append((file_path, description, file_size))
                print(f"✅ {description}: {file_path} ({file_size:,} bytes)")
            else:
                missing_files.append((file_path, description))
                print(f"❌ {description}: {file_path} - BULUNAMADI")
        
        print(f"\n📊 Dosya Durumu:")
        print(f"   ✅ Mevcut: {len(existing_files)}")
        print(f"   ❌ Eksik: {len(missing_files)}")
        
        return len(missing_files) == 0
    
    def test_database_schema(self):
        """Veritabanı şeması testi"""
        print("\n🗄️ Veritabanı Şeması Testi")
        print("-" * 40)
        
        try:
            schema_file = os.path.join(self.root_dir, 'core/Database/enterprise_ai_migrations.sql')
            
            if not os.path.exists(schema_file):
                print("❌ Veritabanı şema dosyası bulunamadı")
                return False
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_content = f.read()
            
            # Temel tablo kontrolü
            required_tables = [
                'enterprise_integrations',
                'integration_logs',
                'social_media_accounts',
                'social_media_posts',
                'enterprise_product_edits',
                'enterprise_metrics',
                'webhook_configurations',
                'enterprise_user_permissions'
            ]
            
            found_tables = []
            for table in required_tables:
                if f"CREATE TABLE {table}" in schema_content or f"CREATE TABLE IF NOT EXISTS {table}" in schema_content:
                    found_tables.append(table)
                    print(f"✅ Tablo: {table}")
                else:
                    print(f"❌ Tablo: {table} - BULUNAMADI")
            
            # View kontrolü
            if 'CREATE VIEW' in schema_content:
                view_count = schema_content.count('CREATE VIEW')
                print(f"✅ View'lar: {view_count} adet")
            else:
                print("⚠️  View bulunamadı")
            
            # Trigger kontrolü
            if 'CREATE TRIGGER' in schema_content:
                trigger_count = schema_content.count('CREATE TRIGGER')
                print(f"✅ Trigger'lar: {trigger_count} adet")
            else:
                print("⚠️  Trigger bulunamadı")
            
            # Stored procedure kontrolü
            if 'CREATE PROCEDURE' in schema_content:
                procedure_count = schema_content.count('CREATE PROCEDURE')
                print(f"✅ Stored Procedure'lar: {procedure_count} adet")
            else:
                print("⚠️  Stored Procedure bulunamadı")
            
            print(f"\n📊 Veritabanı Özeti:")
            print(f"   📋 Tablolar: {len(found_tables)}/{len(required_tables)}")
            print(f"   📄 Dosya boyutu: {len(schema_content):,} karakter")
            
            return len(found_tables) >= len(required_tables) * 0.8  # %80 başarı oranı
            
        except Exception as e:
            print(f"❌ Veritabanı şema test hatası: {e}")
            return False
    
    def test_api_routes(self):
        """API route'ları testi"""
        print("\n🌐 API Route'ları Testi")
        print("-" * 40)
        
        try:
            routes_file = os.path.join(self.root_dir, 'core/Route/enterprise_ai_routes.py')
            
            if not os.path.exists(routes_file):
                print("❌ Route dosyası bulunamadı")
                return False
            
            with open(routes_file, 'r', encoding='utf-8') as f:
                routes_content = f.read()
            
            # Temel route kontrolü
            expected_routes = [
                'generate-social-template',
                'edit-product',
                'manage-integrations',
                'integrations',
                'social-templates',
                'metrics',
                'permissions'
            ]
            
            found_routes = []
            for route in expected_routes:
                if route in routes_content:
                    found_routes.append(route)
                    print(f"✅ Route: /{route}")
                else:
                    print(f"❌ Route: /{route} - BULUNAMADI")
            
            # Blueprint kontrolü
            if 'Blueprint' in routes_content:
                print("✅ Flask Blueprint tanımlandı")
            else:
                print("❌ Flask Blueprint bulunamadı")
            
            # Controller import kontrolü
            if 'EnterpriseAIController' in routes_content:
                print("✅ Enterprise AI Controller import edildi")
            else:
                print("❌ Enterprise AI Controller import edilmedi")
            
            print(f"\n📊 Route Özeti:")
            print(f"   🛣️  Route'lar: {len(found_routes)}/{len(expected_routes)}")
            print(f"   📄 Dosya boyutu: {len(routes_content):,} karakter")
            
            return len(found_routes) >= len(expected_routes) * 0.7  # %70 başarı oranı
            
        except Exception as e:
            print(f"❌ API route test hatası: {e}")
            return False
    
    def test_controller_methods(self):
        """Controller metodları testi"""
        print("\n🎮 Controller Metodları Testi")
        print("-" * 40)
        
        try:
            controller_file = os.path.join(self.root_dir, 'app/Controllers/EnterpriseAIController.py')
            
            if not os.path.exists(controller_file):
                print("❌ Controller dosyası bulunamadı")
                return False
            
            with open(controller_file, 'r', encoding='utf-8') as f:
                controller_content = f.read()
            
            # Temel method kontrolü
            expected_methods = [
                'generate_advanced_social_template',
                'ai_product_editor_enterprise',
                'manage_integrations',
                'get_available_integrations',
                'get_social_template_types',
                'get_enterprise_metrics',
                'get_user_enterprise_permissions'
            ]
            
            found_methods = []
            for method in expected_methods:
                if f"def {method}" in controller_content:
                    found_methods.append(method)
                    print(f"✅ Method: {method}()")
                else:
                    print(f"❌ Method: {method}() - BULUNAMADI")
            
            # Class kontrolü
            if 'class EnterpriseAIController' in controller_content:
                print("✅ EnterpriseAIController sınıfı tanımlandı")
            else:
                print("❌ EnterpriseAIController sınıfı bulunamadı")
            
            # Import kontrolü
            if 'enterprise_ai_system' in controller_content:
                print("✅ Enterprise AI System import edildi")
            else:
                print("❌ Enterprise AI System import edilmedi")
            
            print(f"\n📊 Controller Özeti:")
            print(f"   🔧 Metodlar: {len(found_methods)}/{len(expected_methods)}")
            print(f"   📄 Dosya boyutu: {len(controller_content):,} karakter")
            
            return len(found_methods) >= len(expected_methods) * 0.7  # %70 başarı oranı
            
        except Exception as e:
            print(f"❌ Controller test hatası: {e}")
            return False
    
    def test_documentation(self):
        """Dokümantasyon testi"""
        print("\n📚 Dokümantasyon Testi")
        print("-" * 40)
        
        try:
            doc_file = os.path.join(self.root_dir, 'ENTERPRISE_AI_SYSTEM_README.md')
            
            if not os.path.exists(doc_file):
                print("❌ Dokümantasyon dosyası bulunamadı")
                return False
            
            with open(doc_file, 'r', encoding='utf-8') as f:
                doc_content = f.read()
            
            # Temel bölüm kontrolü
            expected_sections = [
                '# Enterprise AI System',
                '## ✨ Özellikler',
                '## 🚀 Kurulum',
                '## 💡 Kullanım Örnekleri',
                '## 📚 API Dokümantasyonu',
                '## 👥 Rol Tabanlı Sistem',
                '## 🔗 Entegrasyonlar'
            ]
            
            found_sections = []
            for section in expected_sections:
                if section in doc_content:
                    found_sections.append(section)
                    print(f"✅ Bölüm: {section}")
                else:
                    print(f"❌ Bölüm: {section} - BULUNAMADI")
            
            # İçerik kalitesi kontrolü
            word_count = len(doc_content.split())
            if word_count > 1000:
                print(f"✅ Kapsamlı dokümantasyon: {word_count:,} kelime")
            elif word_count > 500:
                print(f"⚠️  Orta seviye dokümantasyon: {word_count:,} kelime")
            else:
                print(f"❌ Yetersiz dokümantasyon: {word_count:,} kelime")
            
            # Kod örnekleri kontrolü
            if '```' in doc_content:
                code_blocks = doc_content.count('```') // 2
                print(f"✅ Kod örnekleri: {code_blocks} blok")
            else:
                print("⚠️  Kod örnekleri bulunamadı")
            
            print(f"\n📊 Dokümantasyon Özeti:")
            print(f"   📑 Bölümler: {len(found_sections)}/{len(expected_sections)}")
            print(f"   📝 Kelime sayısı: {word_count:,}")
            print(f"   📄 Dosya boyutu: {len(doc_content):,} karakter")
            
            return len(found_sections) >= len(expected_sections) * 0.7  # %70 başarı oranı
            
        except Exception as e:
            print(f"❌ Dokümantasyon test hatası: {e}")
            return False
    
    def test_integration_config(self):
        """Entegrasyon konfigürasyonu testi"""
        print("\n🔗 Entegrasyon Konfigürasyonu Testi")
        print("-" * 40)
        
        try:
            ai_system_file = os.path.join(self.root_dir, 'core/AI/enterprise_ai_system.py')
            
            if not os.path.exists(ai_system_file):
                print("❌ Enterprise AI sistem dosyası bulunamadı")
                return False
            
            with open(ai_system_file, 'r', encoding='utf-8') as f:
                ai_content = f.read()
            
            # Entegrasyon kategorileri kontrolü
            integration_categories = [
                'ecommerce',
                'social_media',
                'accounting_erp',
                'einvoice',
                'shipping_logistics',
                'payment_systems',
                'analytics'
            ]
            
            found_categories = []
            for category in integration_categories:
                if f"'{category}'" in ai_content or f'"{category}"' in ai_content:
                    found_categories.append(category)
                    print(f"✅ Kategori: {category}")
                else:
                    print(f"❌ Kategori: {category} - BULUNAMADI")
            
            # Türk e-ticaret siteleri kontrolü
            turkish_sites = ['trendyol', 'hepsiburada', 'n11', 'ciceksepeti']
            found_turkish = []
            for site in turkish_sites:
                if site in ai_content:
                    found_turkish.append(site)
                    print(f"✅ Türk E-ticaret: {site}")
                else:
                    print(f"❌ Türk E-ticaret: {site} - BULUNAMADI")
            
            # Sosyal medya platformları kontrolü
            social_platforms = ['facebook', 'instagram', 'twitter', 'linkedin', 'tiktok', 'telegram']
            found_social = []
            for platform in social_platforms:
                if platform in ai_content:
                    found_social.append(platform)
                    print(f"✅ Sosyal Medya: {platform}")
                else:
                    print(f"❌ Sosyal Medya: {platform} - BULUNAMADI")
            
            print(f"\n📊 Entegrasyon Özeti:")
            print(f"   📂 Kategoriler: {len(found_categories)}/{len(integration_categories)}")
            print(f"   🇹🇷 Türk E-ticaret: {len(found_turkish)}/{len(turkish_sites)}")
            print(f"   📱 Sosyal Medya: {len(found_social)}/{len(social_platforms)}")
            
            total_expected = len(integration_categories) + len(turkish_sites) + len(social_platforms)
            total_found = len(found_categories) + len(found_turkish) + len(found_social)
            
            return total_found >= total_expected * 0.8  # %80 başarı oranı
            
        except Exception as e:
            print(f"❌ Entegrasyon konfigürasyon test hatası: {e}")
            return False
    
    def test_app_integration(self):
        """Ana uygulama entegrasyonu testi"""
        print("\n🔧 Ana Uygulama Entegrasyonu Testi")
        print("-" * 40)
        
        try:
            app_file = os.path.join(self.root_dir, 'app.py')
            
            if not os.path.exists(app_file):
                print("❌ Ana uygulama dosyası bulunamadı")
                return False
            
            with open(app_file, 'r', encoding='utf-8') as f:
                app_content = f.read()
            
            # Enterprise AI route kayıt kontrolü
            if 'register_enterprise_ai_routes' in app_content:
                print("✅ Enterprise AI route'ları kaydedildi")
            else:
                print("❌ Enterprise AI route'ları kaydedilmedi")
                return False
            
            # Import kontrolü
            if 'enterprise_ai_routes' in app_content:
                print("✅ Enterprise AI routes import edildi")
            else:
                print("❌ Enterprise AI routes import edilmedi")
            
            # Hata yönetimi kontrolü
            if 'try:' in app_content and 'except' in app_content:
                print("✅ Hata yönetimi mevcut")
            else:
                print("⚠️  Hata yönetimi eksik")
            
            print(f"\n📊 Uygulama Entegrasyonu:")
            print(f"   📄 Dosya boyutu: {len(app_content):,} karakter")
            
            return True
            
        except Exception as e:
            print(f"❌ Uygulama entegrasyon test hatası: {e}")
            return False
    
    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print(f"\n🚀 Enterprise AI Structure Testleri Başlatılıyor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test listesi
        tests = [
            ("Dosya Yapısı", self.test_file_structure),
            ("Veritabanı Şeması", self.test_database_schema),
            ("API Route'ları", self.test_api_routes),
            ("Controller Metodları", self.test_controller_methods),
            ("Dokümantasyon", self.test_documentation),
            ("Entegrasyon Konfigürasyonu", self.test_integration_config),
            ("Ana Uygulama Entegrasyonu", self.test_app_integration)
        ]
        
        results = {}
        total_start_time = time.time()
        
        for test_name, test_func in tests:
            try:
                start_time = time.time()
                result = test_func()
                test_time = time.time() - start_time
                
                results[test_name] = {
                    'success': result,
                    'time': test_time
                }
                
                status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
                print(f"\n{status} - {test_name} ({test_time:.3f}s)")
                
            except Exception as e:
                results[test_name] = {
                    'success': False,
                    'time': 0,
                    'error': str(e)
                }
                print(f"\n❌ BAŞARISIZ - {test_name} (Hata: {e})")
        
        total_time = time.time() - total_start_time
        
        # Özet rapor
        print("\n" + "=" * 60)
        print("📋 YAPISAL TEST ÖZET RAPORU")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result['success'])
        total = len(results)
        
        print(f"✅ Başarılı: {passed}/{total}")
        print(f"❌ Başarısız: {total - passed}/{total}")
        print(f"📊 Başarı Oranı: {passed/total:.2%}")
        print(f"⏱️  Toplam Süre: {total_time:.3f}s")
        
        # Detaylı sonuçlar
        print("\n📊 Detaylı Sonuçlar:")
        for test_name, result in results.items():
            status = "✅" if result['success'] else "❌"
            time_str = f"{result['time']:.3f}s"
            error_str = f" (Hata: {result.get('error', '')})" if not result['success'] and 'error' in result else ""
            print(f"   {status} {test_name}: {time_str}{error_str}")
        
        # Sistem bilgileri
        print(f"\n🖥️  Sistem Bilgileri:")
        print(f"   Python: {sys.version.split()[0]}")
        print(f"   Platform: {sys.platform}")
        print(f"   Test Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Sonuç dosyasına kaydet
        results_file = f'enterprise_ai_structure_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        'timestamp': datetime.now().isoformat(),
                        'system_info': {
                            'python_version': sys.version.split()[0],
                            'platform': sys.platform
                        },
                        'results': results,
                        'summary': {
                            'total_tests': total,
                            'passed': passed,
                            'failed': total - passed,
                            'success_rate': passed / total,
                            'total_time': total_time
                        }
                    },
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            
            print(f"\n💾 Test sonuçları kaydedildi: {results_file}")
        except Exception as e:
            print(f"\n⚠️  Test sonuçları kaydedilemedi: {e}")
        
        print(f"\n🏁 Enterprise AI Structure Testleri Tamamlandı - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Genel değerlendirme
        if passed == total:
            print("\n🎉 Mükemmel! Tüm yapısal testler başarılı!")
            print("🚀 Enterprise AI sistemi tamamen hazır!")
        elif passed >= total * 0.8:
            print(f"\n✅ Harika! Testlerin %{passed/total*100:.0f}'i başarılı!")
            print("🔧 Birkaç küçük düzenleme ile sistem hazır olacak.")
        elif passed >= total * 0.6:
            print(f"\n⚠️  İyi! Testlerin %{passed/total*100:.0f}'i başarılı!")
            print("🛠️  Bazı önemli düzenlemeler gerekiyor.")
        else:
            print(f"\n❌ Dikkat! Sadece %{passed/total*100:.0f} test başarılı!")
            print("🔨 Sistemde önemli eksiklikler var, gözden geçirin.")
        
        return results


def main():
    """Ana test fonksiyonu"""
    try:
        tester = EnterpriseAIStructureTester()
        results = tester.run_all_tests()
        
        # Test sonucuna göre çıkış kodu
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r['success'])
        
        if passed_tests >= total_tests * 0.8:  # %80'den fazla başarılı
            return 0
        else:
            return 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Testler kullanıcı tarafından durduruldu")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite hatası: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Testler çalıştırılamadı: {e}")
        sys.exit(1)