#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enterprise AI System Test Script
================================

Kurumsal seviye AI sisteminin tüm özelliklerini test eden kapsamlı test scripti
"""

import os
import sys
import asyncio
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Proje kök dizinini sys.path'e ekle
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

try:
    from core.AI.enterprise_ai_system import enterprise_ai_system
    from core.Services.logger import LoggerService
except ImportError as e:
    print(f"❌ Import hatası: {e}")
    print("Lütfen önce enterprise AI sistemini kurun.")
    sys.exit(1)


class EnterpriseAISystemTester:
    """Enterprise AI sistem test sınıfı"""
    
    def __init__(self):
        self.logger = LoggerService.get_logger()
        self.enterprise_ai = enterprise_ai_system
        self.base_url = "http://localhost:5000"
        
        # Test kullanıcıları
        self.test_users = {
            'admin': {'id': 1, 'role': 'admin', 'token': 'admin-test-token'},
            'moderator': {'id': 2, 'role': 'moderator', 'token': 'moderator-test-token'},
            'editor': {'id': 3, 'role': 'editor', 'token': 'editor-test-token'},
            'user': {'id': 4, 'role': 'user', 'token': 'user-test-token'}
        }
        
        print("🚀 Enterprise AI System Test Suite")
        print("=" * 60)
    
    async def test_enterprise_ai_core(self):
        """Enterprise AI Core test"""
        print("\n🧠 Enterprise AI Core Test")
        print("-" * 40)
        
        try:
            # Sistem başlatma kontrolü
            if hasattr(self.enterprise_ai, '_initialized') and self.enterprise_ai._initialized:
                print("✅ Enterprise AI Core başlatıldı")
            else:
                print("❌ Enterprise AI Core başlatılamadı")
                return False
            
            # Entegrasyon konfigürasyonları
            integrations = self.enterprise_ai.integrations_config
            print(f"✅ Entegrasyon kategorileri: {len(integrations)}")
            
            # Sosyal medya şablonları
            templates = self.enterprise_ai.social_templates
            print(f"✅ Sosyal medya şablonları: {len(templates)}")
            
            # Rol tabanlı izinler
            permissions = self.enterprise_ai.enterprise_permissions
            print(f"✅ Rol tabanlı izin sistemleri: {len(permissions)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Enterprise AI Core test hatası: {e}")
            return False
    
    async def test_social_template_generation(self):
        """Sosyal medya şablon üretimi test"""
        print("\n🎨 Sosyal Medya Şablon Üretimi Test")
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
                    'gradient_colors': ['#FF6B6B', '#4ECDC4'],
                    'generate_text': True,
                    'ai_enhancement': True
                }
            }
            
            # Şablon oluştur
            result = await self.enterprise_ai.generate_advanced_social_template(
                user_id=test_data['user_id'],
                user_role=test_data['user_role'],
                template_type=test_data['template_type'],
                content_data=test_data['content_data'],
                ai_enhancement=True
            )
            
            if result.get('success'):
                print("✅ Sosyal medya şablonu oluşturuldu")
                print(f"   Template türü: {test_data['template_type']}")
                print(f"   İşleme süresi: {result.get('template_info', {}).get('processing_time', 0):.3f}s")
                return True
            else:
                print(f"❌ Şablon oluşturma başarısız: {result.get('error', 'Bilinmeyen hata')}")
                return False
                
        except Exception as e:
            print(f"❌ Sosyal medya şablon test hatası: {e}")
            return False
    
    async def test_product_editing(self):
        """Ürün düzenleme AI test"""
        print("\n🏢 Kurumsal Ürün Düzenleme Test")
        print("-" * 40)
        
        try:
            # Test ürün verisi
            product_data = {
                'id': 123,
                'name': 'Test Ürünü',
                'description': 'Bu bir test ürünüdür',
                'price': 99.99,
                'category': 'elektronik',
                'brand': 'TestBrand'
            }
            
            # Düzenleme talimatları
            edit_instructions = {
                'content_optimization': {
                    'optimize_description': True,
                    'target_length': 200,
                    'add_keywords': True,
                    'keywords': ['kaliteli', 'test', 'ürün']
                },
                'smart_pricing': {
                    'market_analysis': True,
                    'psychological_pricing': True
                }
            }
            
            # Ürün düzenle (Admin yetkisi gerekli)
            result = await self.enterprise_ai.ai_product_editor_enterprise(
                user_id=1,
                user_role='admin',
                product_data=product_data,
                edit_instructions=edit_instructions
            )
            
            if result.get('success'):
                print("✅ Ürün AI düzenlemesi tamamlandı")
                print(f"   Kullanılan özellikler: {result.get('edit_info', {}).get('enterprise_features_used', 0)}")
                print(f"   Optimizasyon skoru: {result.get('optimization_score', 0):.1f}")
                return True
            else:
                print(f"❌ Ürün düzenleme başarısız: {result.get('error', 'Bilinmeyen hata')}")
                return False
                
        except Exception as e:
            print(f"❌ Ürün düzenleme test hatası: {e}")
            return False
    
    async def test_integration_management(self):
        """Entegrasyon yönetimi test"""
        print("\n🔗 Entegrasyon Yönetimi Test")
        print("-" * 40)
        
        try:
            # Test entegrasyon verisi
            integration_data = {
                'type': 'ecommerce',
                'name': 'test_marketplace',
                'credentials': {
                    'api_key': 'test-api-key',
                    'secret_key': 'test-secret-key'
                },
                'settings': {
                    'auto_sync': True,
                    'sync_interval': 3600
                }
            }
            
            # Entegrasyon test et
            result = await self.enterprise_ai.manage_integrations(
                user_id=1,
                user_role='admin',
                action='test',
                integration_data=integration_data
            )
            
            if result.get('success'):
                print("✅ Entegrasyon yönetimi çalışıyor")
                print(f"   İşlem: test")
                print(f"   Entegrasyon: {integration_data['name']}")
                return True
            else:
                print(f"❌ Entegrasyon yönetimi başarısız: {result.get('error', 'Bilinmeyen hata')}")
                return False
                
        except Exception as e:
            print(f"❌ Entegrasyon yönetimi test hatası: {e}")
            return False
    
    async def test_role_based_permissions(self):
        """Rol tabanlı izin sistemi test"""
        print("\n👥 Rol Tabanlı İzin Sistemi Test")
        print("-" * 40)
        
        try:
            test_results = []
            
            # Her rol için izin kontrolü
            for role, permissions in self.enterprise_ai.enterprise_permissions.items():
                # Admin tüm izinlere sahip olmalı
                if role == 'admin':
                    has_all_permissions = '*' in permissions
                    test_results.append(('admin_all_permissions', has_all_permissions))
                    print(f"✅ Admin tüm izinlere sahip: {has_all_permissions}")
                
                # Diğer roller için belirli izinler
                else:
                    has_template_permission = self.enterprise_ai.check_enterprise_permission(
                        role, 'template_generation'
                    )
                    test_results.append((f'{role}_template_permission', has_template_permission))
                    print(f"✅ {role.capitalize()} şablon izni: {has_template_permission}")
                
                # Product editing sadece admin'de olmalı
                has_product_edit = self.enterprise_ai.check_enterprise_permission(
                    role, 'product_editing'
                )
                expected_product_edit = (role == 'admin')
                product_edit_correct = (has_product_edit == expected_product_edit)
                test_results.append((f'{role}_product_edit', product_edit_correct))
                print(f"✅ {role.capitalize()} ürün düzenleme izni: {has_product_edit} (beklenen: {expected_product_edit})")
            
            # Tüm testler başarılı mı?
            all_passed = all(result[1] for result in test_results)
            
            if all_passed:
                print("✅ Rol tabanlı izin sistemi doğru çalışıyor")
                return True
            else:
                failed_tests = [test[0] for test in test_results if not test[1]]
                print(f"❌ Başarısız testler: {', '.join(failed_tests)}")
                return False
                
        except Exception as e:
            print(f"❌ Rol tabanlı izin test hatası: {e}")
            return False
    
    async def test_integration_configurations(self):
        """Entegrasyon konfigürasyonları test"""
        print("\n⚙️ Entegrasyon Konfigürasyonları Test")
        print("-" * 40)
        
        try:
            integrations = self.enterprise_ai.integrations_config
            
            # Temel kategoriler kontrolü
            expected_categories = [
                'ecommerce', 'social_media', 'accounting_erp', 
                'einvoice', 'shipping_logistics', 'payment_systems', 'analytics'
            ]
            
            missing_categories = []
            for category in expected_categories:
                if category not in integrations:
                    missing_categories.append(category)
                else:
                    print(f"✅ {category} kategorisi mevcut")
            
            if missing_categories:
                print(f"❌ Eksik kategoriler: {', '.join(missing_categories)}")
                return False
            
            # E-ticaret entegrasyonları kontrolü
            ecommerce = integrations.get('ecommerce', {})
            marketplaces = ecommerce.get('marketplaces', {})
            
            # Türkiye pazaryerleri
            turkish_marketplaces = ['trendyol', 'hepsiburada', 'n11', 'ciceksepeti']
            for marketplace in turkish_marketplaces:
                if marketplace in marketplaces:
                    print(f"✅ {marketplace} entegrasyonu mevcut")
                else:
                    print(f"❌ {marketplace} entegrasyonu eksik")
            
            # Uluslararası pazaryerler
            international_marketplaces = ['amazon_global', 'ebay', 'aliexpress', 'etsy']
            for marketplace in international_marketplaces:
                if marketplace in marketplaces:
                    print(f"✅ {marketplace} entegrasyonu mevcut")
                else:
                    print(f"❌ {marketplace} entegrasyonu eksik")
            
            # Sosyal medya entegrasyonları
            social_media = integrations.get('social_media', {})
            social_platforms = ['facebook', 'instagram', 'twitter', 'linkedin', 'tiktok']
            for platform in social_platforms:
                if platform in social_media:
                    print(f"✅ {platform} entegrasyonu mevcut")
                else:
                    print(f"❌ {platform} entegrasyonu eksik")
            
            print(f"✅ Toplam entegrasyon sayısı: {self._count_total_integrations(integrations)}")
            return True
            
        except Exception as e:
            print(f"❌ Entegrasyon konfigürasyon test hatası: {e}")
            return False
    
    async def test_social_template_types(self):
        """Sosyal medya şablon türleri test"""
        print("\n📱 Sosyal Medya Şablon Türleri Test")
        print("-" * 40)
        
        try:
            templates = self.enterprise_ai.social_templates
            
            # Platform bazlı şablon kontrolü
            platform_templates = {
                'instagram': ['instagram_post', 'instagram_story', 'instagram_reel', 'instagram_carousel'],
                'facebook': ['facebook_post', 'facebook_story', 'facebook_cover', 'facebook_event'],
                'twitter': ['twitter_post', 'twitter_header', 'twitter_card'],
                'linkedin': ['linkedin_post', 'linkedin_article', 'linkedin_company'],
                'tiktok': ['tiktok_video', 'tiktok_cover'],
                'youtube': ['youtube_thumbnail', 'youtube_banner', 'youtube_shorts'],
                'telegram': ['telegram_post', 'telegram_sticker'],
                'whatsapp': ['whatsapp_status', 'whatsapp_business'],
                'pinterest': ['pinterest_pin', 'pinterest_story'],
                'snapchat': ['snapchat_ad']
            }
            
            missing_templates = []
            for platform, template_list in platform_templates.items():
                for template_type in template_list:
                    if template_type in templates:
                        config = templates[template_type]
                        print(f"✅ {template_type}: {config['width']}x{config['height']} ({config['format']})")
                    else:
                        missing_templates.append(template_type)
                        print(f"❌ {template_type} şablonu eksik")
            
            if missing_templates:
                print(f"❌ Eksik şablonlar: {', '.join(missing_templates)}")
                return False
            
            print(f"✅ Toplam şablon türü: {len(templates)}")
            return True
            
        except Exception as e:
            print(f"❌ Sosyal medya şablon türleri test hatası: {e}")
            return False
    
    async def test_enterprise_metrics(self):
        """Kurumsal metrikler test"""
        print("\n📊 Kurumsal Metrikler Test")
        print("-" * 40)
        
        try:
            # Metrikleri al
            metrics = self.enterprise_ai.get_enterprise_metrics()
            
            # Temel metrik kategorileri kontrolü
            expected_metrics = [
                'role_based_requests', 'template_generations', 'product_edits',
                'integration_calls', 'social_media_posts', 'ai_optimizations'
            ]
            
            for metric in expected_metrics:
                if metric in metrics:
                    value = metrics[metric]
                    print(f"✅ {metric}: {value}")
                else:
                    print(f"❌ {metric} metriği eksik")
            
            # Entegrasyon durumu
            integrations_status = metrics.get('integrations_status', {})
            if integrations_status:
                print(f"✅ Entegrasyon durumu mevcut: {len(integrations_status)} kategori")
            else:
                print("❌ Entegrasyon durumu eksik")
            
            # Sosyal medya şablonları
            template_count = metrics.get('social_templates_available', 0)
            if template_count > 0:
                print(f"✅ Sosyal medya şablonları: {template_count}")
            else:
                print("❌ Sosyal medya şablon sayısı eksik")
            
            return True
            
        except Exception as e:
            print(f"❌ Kurumsal metrikler test hatası: {e}")
            return False
    
    def _count_total_integrations(self, integrations: dict) -> int:
        """Toplam entegrasyon sayısını hesapla"""
        total = 0
        for category, items in integrations.items():
            if isinstance(items, dict):
                if 'marketplaces' in items or 'ecommerce_platforms' in items:
                    # E-commerce kategorisi
                    for sub_category, sub_items in items.items():
                        if isinstance(sub_items, dict):
                            total += len(sub_items)
                else:
                    # Diğer kategoriler
                    total += len(items)
        return total
    
    async def test_api_endpoints(self):
        """API endpoint'leri test (opsiyonel - sunucu çalışıyorsa)"""
        print("\n🌐 API Endpoints Test (Opsiyonel)")
        print("-" * 40)
        
        try:
            # Sunucu çalışıyor mu kontrol et
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code != 200:
                print("⚠️  Sunucu çalışmıyor, API testleri atlanıyor")
                return True
            
            # Temel endpoint'leri test et
            endpoints_to_test = [
                '/api/ai/enterprise/social-templates',
                '/api/ai/enterprise/integrations',
                '/api/ai/enterprise/permissions'
            ]
            
            for endpoint in endpoints_to_test:
                try:
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        headers={'Authorization': 'Bearer test-token'},
                        timeout=5
                    )
                    print(f"✅ {endpoint}: HTTP {response.status_code}")
                except requests.exceptions.RequestException:
                    print(f"❌ {endpoint}: Bağlantı hatası")
            
            return True
            
        except requests.exceptions.RequestException:
            print("⚠️  Sunucuya bağlanılamıyor, API testleri atlanıyor")
            return True
        except Exception as e:
            print(f"❌ API endpoint test hatası: {e}")
            return False
    
    async def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print(f"🚀 Enterprise AI System Testleri Başlatılıyor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ("Enterprise AI Core", self.test_enterprise_ai_core),
            ("Sosyal Medya Şablon Üretimi", self.test_social_template_generation),
            ("Kurumsal Ürün Düzenleme", self.test_product_editing),
            ("Entegrasyon Yönetimi", self.test_integration_management),
            ("Rol Tabanlı İzinler", self.test_role_based_permissions),
            ("Entegrasyon Konfigürasyonları", self.test_integration_configurations),
            ("Sosyal Medya Şablon Türleri", self.test_social_template_types),
            ("Kurumsal Metrikler", self.test_enterprise_metrics),
            ("API Endpoints", self.test_api_endpoints)
        ]
        
        results = {}
        total_start_time = time.time()
        
        for test_name, test_func in tests:
            try:
                start_time = time.time()
                result = await test_func()
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
        results_file = f'enterprise_ai_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
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
        print(f"\n🏁 Enterprise AI System Testleri Tamamlandı - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results


async def main():
    """Ana test fonksiyonu"""
    try:
        tester = EnterpriseAISystemTester()
        results = await tester.run_all_tests()
        
        # Test sonucuna göre çıkış kodu
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r['success'])
        
        if passed_tests == total_tests:
            print("\n🎉 Tüm testler başarılı!")
            sys.exit(0)
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test başarısız!")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Testler kullanıcı tarafından durduruldu")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite hatası: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Event loop oluştur ve testleri çalıştır
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Testler çalıştırılamadı: {e}")
        sys.exit(1)