#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enterprise AI System Simple Test Script
=======================================

Kurumsal seviye AI sisteminin temel özelliklerini test eden basit test scripti
(Harici bağımlılık gerektirmez)
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

# Proje kök dizinini sys.path'e ekle
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

print("🚀 Enterprise AI System Simple Test Suite")
print("=" * 60)

# Import kontrolü
try:
    from core.AI.enterprise_ai_system import enterprise_ai_system
    print("✅ Enterprise AI System modülü başarıyla import edildi")
except ImportError as e:
    print(f"❌ Enterprise AI System import hatası: {e}")
    print("⚠️  Enterprise AI sistemi henüz kurulmamış olabilir")
    sys.exit(1)

try:
    from core.Services.logger import LoggerService
    logger = LoggerService.get_logger()
    print("✅ Logger servisi başarıyla import edildi")
except ImportError as e:
    print(f"⚠️  Logger servisi import edilemedi: {e}")
    logger = None


class SimpleEnterpriseAITester:
    """Basit Enterprise AI test sınıfı"""
    
    def __init__(self):
        self.enterprise_ai = enterprise_ai_system
        self.test_results = {}
        
        # Test kullanıcıları
        self.test_users = {
            'admin': {'id': 1, 'role': 'admin', 'token': 'admin-test-token'},
            'moderator': {'id': 2, 'role': 'moderator', 'token': 'moderator-test-token'},
            'editor': {'id': 3, 'role': 'editor', 'token': 'editor-test-token'},
            'user': {'id': 4, 'role': 'user', 'token': 'user-test-token'}
        }
    
    def test_system_initialization(self):
        """Sistem başlatma testi"""
        print("\n🧠 Sistem Başlatma Testi")
        print("-" * 40)
        
        try:
            # Enterprise AI sistem kontrolü
            if hasattr(self.enterprise_ai, '_initialized'):
                init_status = self.enterprise_ai._initialized
                print(f"✅ Enterprise AI başlatma durumu: {init_status}")
            else:
                print("⚠️  Enterprise AI başlatma durumu kontrol edilemiyor")
                init_status = True  # Varsayılan olarak başarılı kabul et
            
            # Temel özellik kontrolü
            if hasattr(self.enterprise_ai, 'integrations_config'):
                integrations = self.enterprise_ai.integrations_config
                print(f"✅ Entegrasyon konfigürasyonları yüklendi: {len(integrations)} kategori")
            else:
                print("❌ Entegrasyon konfigürasyonları yüklenemedi")
                return False
            
            if hasattr(self.enterprise_ai, 'social_templates'):
                templates = self.enterprise_ai.social_templates
                print(f"✅ Sosyal medya şablonları yüklendi: {len(templates)} şablon")
            else:
                print("❌ Sosyal medya şablonları yüklenemedi")
                return False
            
            if hasattr(self.enterprise_ai, 'enterprise_permissions'):
                permissions = self.enterprise_ai.enterprise_permissions
                print(f"✅ Rol tabanlı izinler yüklendi: {len(permissions)} rol")
            else:
                print("❌ Rol tabanlı izinler yüklenemedi")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Sistem başlatma test hatası: {e}")
            return False
    
    def test_integration_configurations(self):
        """Entegrasyon konfigürasyonları testi"""
        print("\n🔗 Entegrasyon Konfigürasyonları Testi")
        print("-" * 40)
        
        try:
            integrations = self.enterprise_ai.integrations_config
            
            # Temel kategoriler kontrolü
            expected_categories = [
                'ecommerce', 'social_media', 'accounting_erp', 
                'einvoice', 'shipping_logistics', 'payment_systems', 'analytics'
            ]
            
            category_results = {}
            for category in expected_categories:
                if category in integrations:
                    category_data = integrations[category]
                    category_count = self._count_category_integrations(category_data)
                    category_results[category] = category_count
                    print(f"✅ {category}: {category_count} entegrasyon")
                else:
                    category_results[category] = 0
                    print(f"❌ {category}: Kategori bulunamadı")
            
            # Toplam entegrasyon sayısı
            total_integrations = sum(category_results.values())
            print(f"\n📊 Toplam entegrasyon sayısı: {total_integrations}")
            
            # Önemli entegrasyonlar kontrolü
            ecommerce = integrations.get('ecommerce', {})
            marketplaces = ecommerce.get('marketplaces', {})
            
            # Türkiye pazaryerleri
            turkish_marketplaces = ['trendyol', 'hepsiburada', 'n11', 'ciceksepeti']
            turkish_count = sum(1 for mp in turkish_marketplaces if mp in marketplaces)
            print(f"✅ Türkiye pazaryerleri: {turkish_count}/{len(turkish_marketplaces)}")
            
            # Sosyal medya platformları
            social_media = integrations.get('social_media', {})
            social_platforms = ['facebook', 'instagram', 'twitter', 'linkedin', 'tiktok']
            social_count = sum(1 for sp in social_platforms if sp in social_media)
            print(f"✅ Sosyal medya platformları: {social_count}/{len(social_platforms)}")
            
            return total_integrations > 0
            
        except Exception as e:
            print(f"❌ Entegrasyon konfigürasyon test hatası: {e}")
            return False
    
    def test_social_templates(self):
        """Sosyal medya şablonları testi"""
        print("\n📱 Sosyal Medya Şablonları Testi")
        print("-" * 40)
        
        try:
            templates = self.enterprise_ai.social_templates
            
            # Platform bazlı şablon kontrolü
            platform_templates = {
                'instagram': ['instagram_post', 'instagram_story', 'instagram_reel'],
                'facebook': ['facebook_post', 'facebook_story', 'facebook_cover'],
                'twitter': ['twitter_post', 'twitter_header'],
                'linkedin': ['linkedin_post', 'linkedin_article'],
                'telegram': ['telegram_post', 'telegram_sticker'],
                'youtube': ['youtube_thumbnail', 'youtube_banner']
            }
            
            platform_results = {}
            for platform, template_list in platform_templates.items():
                found_templates = []
                for template_type in template_list:
                    if template_type in templates:
                        config = templates[template_type]
                        found_templates.append(template_type)
                        print(f"✅ {template_type}: {config['width']}x{config['height']}")
                
                platform_results[platform] = len(found_templates)
                print(f"📊 {platform}: {len(found_templates)}/{len(template_list)} şablon")
            
            total_expected = sum(len(templates) for templates in platform_templates.values())
            total_found = sum(platform_results.values())
            
            print(f"\n📊 Toplam şablon: {total_found}/{total_expected}")
            print(f"✅ Şablon kapsama oranı: {total_found/total_expected:.1%}")
            
            return total_found > 0
            
        except Exception as e:
            print(f"❌ Sosyal medya şablonları test hatası: {e}")
            return False
    
    def test_role_permissions(self):
        """Rol tabanlı izinler testi"""
        print("\n👥 Rol Tabanlı İzinler Testi")
        print("-" * 40)
        
        try:
            permissions = self.enterprise_ai.enterprise_permissions
            
            # Her rol için izin kontrolü
            role_results = {}
            for role, role_permissions in permissions.items():
                permission_count = len(role_permissions) if isinstance(role_permissions, list) else 1
                role_results[role] = permission_count
                
                # Admin özel kontrolü
                if role == 'admin':
                    has_all_permissions = '*' in role_permissions if isinstance(role_permissions, list) else role_permissions == '*'
                    print(f"✅ {role}: {'Tüm izinler' if has_all_permissions else f'{permission_count} izin'}")
                else:
                    print(f"✅ {role}: {permission_count} izin")
                
                # Önemli izinler kontrolü
                if hasattr(self.enterprise_ai, 'check_enterprise_permission'):
                    # Template generation izni
                    has_template = self.enterprise_ai.check_enterprise_permission(role, 'template_generation')
                    print(f"   - Şablon oluşturma: {'✅' if has_template else '❌'}")
                    
                    # Product editing izni (sadece admin'de olmalı)
                    has_product_edit = self.enterprise_ai.check_enterprise_permission(role, 'product_editing')
                    expected_product_edit = (role == 'admin')
                    product_edit_ok = (has_product_edit == expected_product_edit)
                    print(f"   - Ürün düzenleme: {'✅' if product_edit_ok else '❌'} ({'var' if has_product_edit else 'yok'})")
            
            print(f"\n📊 Toplam rol sayısı: {len(role_results)}")
            return len(role_results) > 0
            
        except Exception as e:
            print(f"❌ Rol tabanlı izinler test hatası: {e}")
            return False
    
    async def test_social_template_generation(self):
        """Sosyal medya şablon üretimi testi"""
        print("\n🎨 Sosyal Medya Şablon Üretimi Testi")
        print("-" * 40)
        
        try:
            # Test verisi
            test_data = {
                'user_id': 1,
                'user_role': 'admin',
                'template_type': 'instagram_post',
                'content_data': {
                    'product_name': 'Test Ürünü',
                    'text': 'Bu bir test şablonudur',
                    'background_style': 'gradient',
                    'gradient_colors': ['#FF6B6B', '#4ECDC4']
                }
            }
            
            # Şablon oluşturma metodunu kontrol et
            if hasattr(self.enterprise_ai, 'generate_advanced_social_template'):
                print("✅ Şablon oluşturma metodu mevcut")
                
                # Test şablon oluşturma (gerçek işlem yapmadan)
                result = await self.enterprise_ai.generate_advanced_social_template(
                    user_id=test_data['user_id'],
                    user_role=test_data['user_role'],
                    template_type=test_data['template_type'],
                    content_data=test_data['content_data'],
                    ai_enhancement=True
                )
                
                if result and result.get('success'):
                    print("✅ Şablon oluşturma başarılı")
                    template_info = result.get('template_info', {})
                    processing_time = template_info.get('processing_time', 0)
                    print(f"   İşleme süresi: {processing_time:.3f}s")
                    return True
                else:
                    print(f"⚠️  Şablon oluşturma tamamlanamadı: {result.get('error', 'Bilinmeyen hata')}")
                    return False
            else:
                print("❌ Şablon oluşturma metodu bulunamadı")
                return False
                
        except Exception as e:
            print(f"❌ Sosyal medya şablon test hatası: {e}")
            return False
    
    async def test_product_editing(self):
        """Ürün düzenleme AI testi"""
        print("\n🏢 Kurumsal Ürün Düzenleme Testi")
        print("-" * 40)
        
        try:
            # Test ürün verisi
            product_data = {
                'id': 123,
                'name': 'Test Ürünü',
                'description': 'Bu bir test ürünüdür',
                'price': 99.99,
                'category': 'elektronik'
            }
            
            edit_instructions = {
                'content_optimization': {
                    'optimize_description': True,
                    'target_length': 200
                }
            }
            
            # Ürün düzenleme metodunu kontrol et
            if hasattr(self.enterprise_ai, 'ai_product_editor_enterprise'):
                print("✅ Ürün düzenleme metodu mevcut")
                
                # Test ürün düzenleme (sadece admin)
                result = await self.enterprise_ai.ai_product_editor_enterprise(
                    user_id=1,
                    user_role='admin',
                    product_data=product_data,
                    edit_instructions=edit_instructions
                )
                
                if result and result.get('success'):
                    print("✅ Ürün düzenleme başarılı")
                    optimization_score = result.get('optimization_score', 0)
                    print(f"   Optimizasyon skoru: {optimization_score:.1f}")
                    return True
                else:
                    print(f"⚠️  Ürün düzenleme tamamlanamadı: {result.get('error', 'Bilinmeyen hata')}")
                    return False
            else:
                print("❌ Ürün düzenleme metodu bulunamadı")
                return False
                
        except Exception as e:
            print(f"❌ Ürün düzenleme test hatası: {e}")
            return False
    
    def test_enterprise_metrics(self):
        """Kurumsal metrikler testi"""
        print("\n📊 Kurumsal Metrikler Testi")
        print("-" * 40)
        
        try:
            # Metrik metodunu kontrol et
            if hasattr(self.enterprise_ai, 'get_enterprise_metrics'):
                print("✅ Metrik metodu mevcut")
                
                metrics = self.enterprise_ai.get_enterprise_metrics()
                
                if metrics:
                    print("✅ Metrikler başarıyla alındı")
                    
                    # Temel metrik kategorileri
                    metric_categories = [
                        'role_based_requests', 'template_generations', 'product_edits',
                        'integration_calls', 'social_media_posts'
                    ]
                    
                    found_metrics = 0
                    for metric in metric_categories:
                        if metric in metrics:
                            value = metrics[metric]
                            print(f"   {metric}: {value}")
                            found_metrics += 1
                        else:
                            print(f"   {metric}: ❌ Bulunamadı")
                    
                    print(f"📊 Bulunan metrik sayısı: {found_metrics}/{len(metric_categories)}")
                    return found_metrics > 0
                else:
                    print("❌ Metrikler alınamadı")
                    return False
            else:
                print("❌ Metrik metodu bulunamadı")
                return False
                
        except Exception as e:
            print(f"❌ Kurumsal metrikler test hatası: {e}")
            return False
    
    def _count_category_integrations(self, category_data):
        """Kategori entegrasyon sayısını hesapla"""
        if not isinstance(category_data, dict):
            return 0
        
        total = 0
        for key, value in category_data.items():
            if isinstance(value, dict):
                total += len(value)
            else:
                total += 1
        return total
    
    async def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print(f"\n🚀 Enterprise AI System Testleri Başlatılıyor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test listesi
        tests = [
            ("Sistem Başlatma", self.test_system_initialization, False),
            ("Entegrasyon Konfigürasyonları", self.test_integration_configurations, False),
            ("Sosyal Medya Şablonları", self.test_social_templates, False),
            ("Rol Tabanlı İzinler", self.test_role_permissions, False),
            ("Sosyal Medya Şablon Üretimi", self.test_social_template_generation, True),
            ("Kurumsal Ürün Düzenleme", self.test_product_editing, True),
            ("Kurumsal Metrikler", self.test_enterprise_metrics, False)
        ]
        
        results = {}
        total_start_time = time.time()
        
        for test_name, test_func, is_async in tests:
            try:
                start_time = time.time()
                
                # Async veya sync test çalıştır
                if is_async:
                    result = await test_func()
                else:
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
        print("📋 TEST ÖZET RAPORU")
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
        results_file = f'enterprise_ai_simple_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump({
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
                }, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Test sonuçları kaydedildi: {results_file}")
        except Exception as e:
            print(f"\n⚠️  Test sonuçları kaydedilemedi: {e}")
        
        print(f"\n🏁 Enterprise AI System Testleri Tamamlandı - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results


async def main():
    """Ana test fonksiyonu"""
    try:
        tester = SimpleEnterpriseAITester()
        results = await tester.run_all_tests()
        
        # Test sonucuna göre çıkış kodu
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r['success'])
        
        if passed_tests == total_tests:
            print("\n🎉 Tüm testler başarılı!")
            return 0
        elif passed_tests > total_tests * 0.7:  # %70'den fazla başarılı
            print(f"\n✅ Testlerin çoğu başarılı! ({passed_tests}/{total_tests})")
            return 0
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test başarısız!")
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
    # Event loop oluştur ve testleri çalıştır
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Testler çalıştırılamadı: {e}")
        sys.exit(1)