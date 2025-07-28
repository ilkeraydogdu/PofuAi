#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi AI System Test Script
============================

AI sisteminin tüm özelliklerini test eden demo script
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

from core.AI.ai_core import ai_core
from core.AI.image_recognition import ImageRecognitionService
from core.AI.content_categorizer import ContentCategorizerService
from core.AI.user_content_manager import UserContentManagerService
from core.AI.smart_storage import SmartStorageService
from core.Services.logger import LoggerService


class AISystemTester:
    """AI sistem test sınıfı"""
    
    def __init__(self):
        self.logger = LoggerService.get_logger()
        
        # Test kullanıcısı
        self.test_user_id = 999
        
        # Test görselleri için dizin
        self.test_images_dir = os.path.join(ROOT_DIR, 'test_images')
        self.create_test_images_dir()
        
        # AI servislerini başlat
        self.image_recognition = ImageRecognitionService()
        self.content_categorizer = ContentCategorizerService()
        self.user_content_manager = UserContentManagerService()
        self.smart_storage = SmartStorageService()
        
        print("🤖 PofuAi AI System Test Suite")
        print("=" * 50)
    
    def create_test_images_dir(self):
        """Test görselleri dizinini oluştur"""
        os.makedirs(self.test_images_dir, exist_ok=True)
        
        # Eğer test görselleri yoksa, örnek dosyalar oluştur
        if not os.listdir(self.test_images_dir):
            print("⚠️  Test görselleri bulunamadı.")
            print(f"📁 Lütfen {self.test_images_dir} dizinine test görselleri ekleyin.")
            print("🖼️  Desteklenen formatlar: .jpg, .jpeg, .png, .bmp, .tiff, .webp")
    
    def get_test_images(self):
        """Test görsellerini al"""
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        test_images = []
        for file in os.listdir(self.test_images_dir):
            if any(file.lower().endswith(ext) for ext in supported_formats):
                test_images.append(os.path.join(self.test_images_dir, file))
        
        return test_images
    
    async def test_ai_core(self):
        """AI Core test"""
        print("\n🧠 AI Core Test")
        print("-" * 30)
        
        try:
            # Model bilgilerini al
            model_info = ai_core.get_model_info()
            print(f"✅ Device: {model_info.get('device', 'Unknown')}")
            print(f"✅ Models: {', '.join(model_info.get('models', []))}")
            print(f"✅ Pipelines: {', '.join(model_info.get('pipelines', []))}")
            
            # Performans metrikleri
            metrics = ai_core.get_metrics()
            print(f"📊 Total Processed: {metrics.get('total_processed', 0)}")
            print(f"📊 Success Rate: {metrics.get('success_rate', 0):.2%}")
            print(f"📊 Avg Processing Time: {metrics.get('average_processing_time', 0):.3f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ AI Core test failed: {e}")
            return False
    
    async def test_image_processing(self):
        """Görsel işleme test"""
        print("\n🖼️  Image Processing Test")
        print("-" * 30)
        
        test_images = self.get_test_images()
        
        if not test_images:
            print("⚠️  No test images found. Skipping image processing test.")
            return False
        
        try:
            # İlk görseli test et
            test_image = test_images[0]
            print(f"🔍 Processing: {os.path.basename(test_image)}")
            
            start_time = time.time()
            
            # Temel AI Core işleme
            basic_result = await ai_core.process_image(test_image, self.test_user_id)
            basic_time = time.time() - start_time
            
            print(f"✅ Basic processing completed in {basic_time:.3f}s")
            print(f"📊 Status: {basic_result.get('status', 'Unknown')}")
            
            # Kapsamlı analiz
            start_time = time.time()
            comprehensive_result = await self.image_recognition.analyze_image_comprehensive(
                test_image, self.test_user_id
            )
            comprehensive_time = time.time() - start_time
            
            print(f"✅ Comprehensive analysis completed in {comprehensive_time:.3f}s")
            
            # Sonuçları göster
            if comprehensive_result.get('detailed_analysis'):
                analysis = comprehensive_result['detailed_analysis']
                
                # Temel özellikler
                basic = analysis.get('basic', {})
                if basic:
                    dims = basic.get('dimensions', {})
                    print(f"📐 Dimensions: {dims.get('width', 0)}x{dims.get('height', 0)}")
                    print(f"📐 Orientation: {basic.get('orientation', 'Unknown')}")
                
                # Renk analizi
                colors = analysis.get('colors', {})
                if colors and 'dominant_colors' in colors:
                    print(f"🎨 Dominant colors: {len(colors['dominant_colors'])}")
                    print(f"🎨 Brightness: {colors.get('brightness_category', 'Unknown')}")
                
                # Yüz analizi
                faces = analysis.get('faces', {})
                if faces:
                    print(f"👥 Faces detected: {faces.get('face_count', 0)}")
                
                # Kalite analizi
                quality = analysis.get('quality', {})
                if quality:
                    print(f"⭐ Quality: {quality.get('quality_category', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Image processing test failed: {e}")
            return False
    
    async def test_categorization(self):
        """Kategorilendirme test"""
        print("\n🏷️  Categorization Test")
        print("-" * 30)
        
        test_images = self.get_test_images()
        
        if not test_images:
            print("⚠️  No test images found. Skipping categorization test.")
            return False
        
        try:
            # İlk görseli analiz et
            test_image = test_images[0]
            
            # Önce görsel analizi yap
            analysis_result = await self.image_recognition.analyze_image_comprehensive(
                test_image, self.test_user_id
            )
            
            if analysis_result.get('status') == 'error':
                print("❌ Image analysis failed, skipping categorization")
                return False
            
            # Kategorilendirme yap
            start_time = time.time()
            categorization_result = await self.content_categorizer.categorize_content(
                analysis_result
            )
            categorization_time = time.time() - start_time
            
            print(f"✅ Categorization completed in {categorization_time:.3f}s")
            
            # Sonuçları göster
            categories = categorization_result.get('categories', {})
            
            primary = categories.get('primary', [])
            if primary:
                print(f"🏆 Primary categories: {len(primary)}")
                for i, cat in enumerate(primary[:3]):
                    print(f"   {i+1}. {cat.get('category', 'Unknown')} (confidence: {cat.get('confidence', 0):.2f})")
            
            secondary = categories.get('secondary', [])
            if secondary:
                print(f"🥈 Secondary categories: {len(secondary)}")
            
            custom_tags = categories.get('custom_tags', [])
            if custom_tags:
                print(f"🏷️  Custom tags: {', '.join(custom_tags[:5])}")
            
            # Kategori istatistikleri
            category_stats = self.content_categorizer.get_category_stats()
            print(f"📊 Total categories in system: {category_stats.get('total_categories', 0)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Categorization test failed: {e}")
            return False
    
    async def test_user_content_management(self):
        """Kullanıcı içerik yönetimi test"""
        print("\n👤 User Content Management Test")
        print("-" * 30)
        
        try:
            # Kullanıcı profil özeti
            profile_summary = self.user_content_manager.get_user_profile_summary(self.test_user_id)
            print(f"👤 User Profile Status: {profile_summary.get('status', 'Unknown')}")
            
            # Kullanıcı içerik analizi (eğer yeterli veri varsa)
            content_analysis = await self.user_content_manager.analyze_user_content(self.test_user_id)
            
            if content_analysis.get('status') == 'insufficient_data':
                print("⚠️  Insufficient data for user content analysis")
                print(f"📊 Message: {content_analysis.get('message', 'No message')}")
            else:
                print("✅ User content analysis completed")
                patterns = content_analysis.get('patterns', {})
                
                # İçerik desenleri
                content_patterns = patterns.get('content', {})
                if content_patterns:
                    print(f"📊 Total images: {content_patterns.get('total_images', 0)}")
                    print(f"📊 Successful processing: {content_patterns.get('successful_processing', 0)}")
            
            # Kullanıcı önerileri
            recommendations = await self.user_content_manager.get_user_recommendations(self.test_user_id)
            print(f"💡 Recommendations available: {len(recommendations.get('organization_tips', []))}")
            
            return True
            
        except Exception as e:
            print(f"❌ User content management test failed: {e}")
            return False
    
    async def test_smart_storage(self):
        """Akıllı depolama test"""
        print("\n💾 Smart Storage Test")
        print("-" * 30)
        
        try:
            # Depolama özeti
            storage_summary = self.smart_storage.get_storage_summary()
            print(f"📊 Total files: {storage_summary.get('total_files', 0)}")
            print(f"📊 Total size: {storage_summary.get('total_size_mb', 0):.2f} MB")
            print(f"📊 Duplicates found: {storage_summary.get('duplicates_found', 0)}")
            print(f"📊 Storage efficiency: {storage_summary.get('storage_efficiency', 0):.2%}")
            
            # Kullanıcı için duplicate detection test
            cleanup_result = await self.smart_storage.cleanup_duplicates(
                self.test_user_id, auto_remove=False
            )
            
            if cleanup_result.get('status') != 'error':
                print(f"🔍 Duplicates detected: {cleanup_result.get('duplicates_found', 0)}")
                print(f"🔍 Potential space to free: {cleanup_result.get('space_freed', 0)} bytes")
            
            return True
            
        except Exception as e:
            print(f"❌ Smart storage test failed: {e}")
            return False
    
    async def test_batch_processing(self):
        """Toplu işleme test"""
        print("\n⚡ Batch Processing Test")
        print("-" * 30)
        
        test_images = self.get_test_images()
        
        if len(test_images) < 2:
            print("⚠️  Need at least 2 test images for batch processing test.")
            return False
        
        try:
            # İlk 3 görseli (veya mevcut olanları) toplu işle
            batch_images = test_images[:3]
            print(f"🔄 Processing {len(batch_images)} images in batch...")
            
            start_time = time.time()
            batch_results = await ai_core.batch_process_images(batch_images, self.test_user_id)
            batch_time = time.time() - start_time
            
            print(f"✅ Batch processing completed in {batch_time:.3f}s")
            
            # Sonuçları analiz et
            successful = sum(1 for result in batch_results if result.get('status') != 'error')
            failed = len(batch_results) - successful
            
            print(f"📊 Successful: {successful}/{len(batch_results)}")
            print(f"📊 Failed: {failed}/{len(batch_results)}")
            print(f"📊 Success rate: {successful/len(batch_results):.2%}")
            print(f"📊 Average time per image: {batch_time/len(batch_results):.3f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Batch processing test failed: {e}")
            return False
    
    async def test_system_performance(self):
        """Sistem performans test"""
        print("\n⚡ System Performance Test")
        print("-" * 30)
        
        try:
            # AI Core metrikleri
            metrics = ai_core.get_metrics()
            
            print("📊 Performance Metrics:")
            print(f"   Total processed: {metrics.get('total_processed', 0)}")
            print(f"   Success rate: {metrics.get('success_rate', 0):.2%}")
            print(f"   Average processing time: {metrics.get('average_processing_time', 0):.3f}s")
            print(f"   Errors: {len(metrics.get('errors', []))}")
            
            # Model bilgileri
            model_info = ai_core.get_model_info()
            print(f"🤖 AI Models Status: {model_info.get('status', 'Unknown')}")
            print(f"🤖 Device: {model_info.get('device', 'Unknown')}")
            print(f"🤖 Active models: {len(model_info.get('models', []))}")
            print(f"🤖 Active pipelines: {len(model_info.get('pipelines', []))}")
            
            return True
            
        except Exception as e:
            print(f"❌ System performance test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print(f"🚀 Starting AI System Tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ("AI Core", self.test_ai_core),
            ("Image Processing", self.test_image_processing),
            ("Categorization", self.test_categorization),
            ("User Content Management", self.test_user_content_management),
            ("Smart Storage", self.test_smart_storage),
            ("Batch Processing", self.test_batch_processing),
            ("System Performance", self.test_system_performance)
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
                
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"\n{status} - {test_name} ({test_time:.3f}s)")
                
            except Exception as e:
                results[test_name] = {
                    'success': False,
                    'time': 0,
                    'error': str(e)
                }
                print(f"\n❌ FAILED - {test_name} (Error: {e})")
        
        total_time = time.time() - total_start_time
        
        # Özet rapor
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in results.values() if result['success'])
        total = len(results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📊 Success Rate: {passed/total:.2%}")
        print(f"⏱️  Total Time: {total_time:.3f}s")
        
        # Detaylı sonuçlar
        print("\n📊 Detailed Results:")
        for test_name, result in results.items():
            status = "✅" if result['success'] else "❌"
            time_str = f"{result['time']:.3f}s"
            error_str = f" (Error: {result.get('error', '')})" if not result['success'] and 'error' in result else ""
            print(f"   {status} {test_name}: {time_str}{error_str}")
        
        print(f"\n🏁 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results


async def main():
    """Ana test fonksiyonu"""
    try:
        tester = AISystemTester()
        results = await tester.run_all_tests()
        
        # Test sonuçlarını dosyaya kaydet
        results_file = os.path.join(ROOT_DIR, f'ai_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'summary': {
                    'total_tests': len(results),
                    'passed': sum(1 for r in results.values() if r['success']),
                    'failed': sum(1 for r in results.values() if not r['success']),
                    'success_rate': sum(1 for r in results.values() if r['success']) / len(results)
                }
            }, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Test results saved to: {results_file}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Event loop oluştur ve testleri çalıştır
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        sys.exit(1)