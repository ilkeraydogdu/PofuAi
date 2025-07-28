#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced AI Helpers Module
==========================

Gelişmiş AI sistemi için yardımcı fonksiyonlar
- Ürün düzenleme AI yardımcıları
- İçerik analizi yardımcıları
- Görsel işleme filtreleri
- Renk analizi araçları
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import cv2
import requests
from sklearn.cluster import KMeans
import colorsys

from core.Services.logger import LoggerService
from core.Database.connection import DatabaseConnection


class AdvancedAIHelpers:
    """
    Gelişmiş AI sistemi için yardımcı sınıf
    """
    
    def __init__(self):
        self.logger = LoggerService.get_logger()
        self.db = DatabaseConnection()
    
    # Ürün düzenleme AI yardımcıları
    async def ai_edit_product_images(self, product_data: Dict, edit_instructions: Dict) -> Dict[str, Any]:
        """AI ile ürün görsellerini düzenle"""
        try:
            results = {}
            
            # Mevcut görselleri al
            images = json.loads(product_data.get('images', '[]'))
            if not images:
                return {'error': 'Üründe düzenlenecek görsel bulunamadı'}
            
            # Her görsel için düzenleme yap
            edited_images = []
            for image_path in images:
                full_path = os.path.join('public/uploads/products', image_path)
                
                if os.path.exists(full_path):
                    # Görsel düzenleme işlemleri
                    edited_image = await self._edit_single_product_image(
                        full_path, edit_instructions
                    )
                    
                    if edited_image.get('success'):
                        edited_images.append(edited_image['new_path'])
                    else:
                        edited_images.append(image_path)  # Orijinal dosyayı koru
            
            results['edited_images'] = edited_images
            results['original_count'] = len(images)
            results['edited_count'] = len([img for img in edited_images if img != images[images.index(img)] if img in images])
            results['success'] = True
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ürün görsel düzenleme hatası: {e}")
            return {'error': str(e), 'success': False}
    
    async def _edit_single_product_image(self, image_path: str, instructions: Dict) -> Dict[str, Any]:
        """Tekil ürün görselini düzenle"""
        try:
            # Görseli yükle
            image = Image.open(image_path)
            original_image = image.copy()
            
            # Düzenleme işlemleri
            if instructions.get('enhance_quality'):
                image = self._enhance_product_image_quality(image)
            
            if instructions.get('remove_background'):
                image = self._remove_product_background(image)
            
            if instructions.get('resize'):
                target_size = instructions.get('target_size', (800, 800))
                image = self._smart_resize_product_image(image, target_size)
            
            if instructions.get('apply_filter'):
                filter_type = instructions.get('filter_type', 'professional')
                image = self._apply_product_filter(image, filter_type)
            
            if instructions.get('add_watermark'):
                watermark_text = instructions.get('watermark_text', 'PofuAi')
                image = self._add_watermark_to_product(image, watermark_text)
            
            # Yeni dosya adı oluştur
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            original_name = os.path.basename(image_path)
            name, ext = os.path.splitext(original_name)
            new_filename = f"{name}_edited_{timestamp}{ext}"
            new_path = os.path.join(os.path.dirname(image_path), new_filename)
            
            # Düzenlenmiş görseli kaydet
            image.save(new_path, quality=95, optimize=True)
            
            return {
                'success': True,
                'original_path': image_path,
                'new_path': new_path,
                'changes_applied': list(instructions.keys())
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_path': image_path
            }
    
    def _enhance_product_image_quality(self, image: Image.Image) -> Image.Image:
        """Ürün görsel kalitesini iyileştir"""
        # Keskinlik artırma
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)
        
        # Kontrast iyileştirme
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        # Renk doygunluğu
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.15)
        
        # Parlaklık ayarı
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.05)
        
        return image
    
    def _remove_product_background(self, image: Image.Image) -> Image.Image:
        """Ürün arka planını kaldır (gelişmiş)"""
        # OpenCV kullanarak daha gelişmiş arka plan kaldırma
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # GrabCut algoritması kullan
        mask = np.zeros(cv_image.shape[:2], np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Ön plan için dikdörtgen tanımla (merkezi alan)
        height, width = cv_image.shape[:2]
        rect = (int(width*0.1), int(height*0.1), int(width*0.8), int(height*0.8))
        
        # GrabCut uygula
        cv2.grabCut(cv_image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        
        # Maskeyi düzenle
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        # Sonucu uygula
        result = cv_image * mask2[:, :, np.newaxis]
        
        # PIL formatına geri çevir
        result_pil = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        
        # RGBA formatına çevir ve şeffaflık ekle
        result_rgba = Image.new('RGBA', result_pil.size, (255, 255, 255, 0))
        result_rgba.paste(result_pil, mask=Image.fromarray(mask2 * 255))
        
        return result_rgba
    
    def _smart_resize_product_image(self, image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Akıllı ürün görsel yeniden boyutlandırma"""
        # Aspect ratio'yu koru
        original_ratio = image.width / image.height
        target_ratio = target_size[0] / target_size[1]
        
        if original_ratio > target_ratio:
            # Genişlik öncelikli
            new_width = target_size[0]
            new_height = int(target_size[0] / original_ratio)
        else:
            # Yükseklik öncelikli
            new_height = target_size[1]
            new_width = int(target_size[1] * original_ratio)
        
        # Yeniden boyutlandır
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Hedef boyuta sığdırmak için padding ekle
        final_image = Image.new('RGBA', target_size, (255, 255, 255, 0))
        
        # Merkeze yerleştir
        x = (target_size[0] - new_width) // 2
        y = (target_size[1] - new_height) // 2
        
        final_image.paste(resized, (x, y))
        
        return final_image
    
    def _apply_product_filter(self, image: Image.Image, filter_type: str) -> Image.Image:
        """Ürün görsellerine filtre uygula"""
        if filter_type == 'professional':
            return self._apply_professional_filter(image)
        elif filter_type == 'vintage':
            return self._apply_vintage_filter(image)
        elif filter_type == 'modern':
            return self._apply_modern_filter(image)
        elif filter_type == 'artistic':
            return self._apply_artistic_filter(image)
        else:
            return image
    
    def _apply_professional_filter(self, image: Image.Image) -> Image.Image:
        """Profesyonel filtre uygula"""
        # Hafif keskinlik artırma
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        # Kontrast iyileştirme
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.15)
        
        # Renk doygunluğunu hafif azalt (profesyonel görünüm)
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(0.95)
        
        return image
    
    def _apply_vintage_filter(self, image: Image.Image) -> Image.Image:
        """Vintage filtre uygula"""
        # Sepia efekti
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        pixels = image.load()
        for i in range(image.width):
            for j in range(image.height):
                r, g, b = pixels[i, j]
                
                # Sepia formülü
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                # 255'i geçmeyen değerler
                pixels[i, j] = (min(255, tr), min(255, tg), min(255, tb))
        
        # Hafif bulanıklık ekle
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return image
    
    def _apply_modern_filter(self, image: Image.Image) -> Image.Image:
        """Modern filtre uygula"""
        # Yüksek kontrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.3)
        
        # Renk doygunluğu artırma
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        
        # Keskinlik artırma
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        return image
    
    def _apply_artistic_filter(self, image: Image.Image) -> Image.Image:
        """Artistik filtre uygula"""
        # Edge detection efekti
        edges = image.filter(ImageFilter.FIND_EDGES)
        
        # Orijinal ile karıştır
        blended = Image.blend(image, edges, 0.2)
        
        # Renk doygunluğu artır
        enhancer = ImageEnhance.Color(blended)
        blended = enhancer.enhance(1.4)
        
        return blended
    
    def _add_watermark_to_product(self, image: Image.Image, watermark_text: str) -> Image.Image:
        """Ürün görsellerine watermark ekle"""
        # Şeffaf katman oluştur
        watermark = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark)
        
        # Font ayarları
        try:
            font_size = max(20, min(image.width, image.height) // 20)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Metin boyutunu al
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Sağ alt köşeye yerleştir
        x = image.width - text_width - 20
        y = image.height - text_height - 20
        
        # Şeffaf metin ekle
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
        
        # Orijinal görsel ile birleştir
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        watermarked = Image.alpha_composite(image, watermark)
        
        return watermarked
    
    # Açıklama iyileştirme AI
    async def ai_enhance_product_description(self, product_data: Dict, enhancement_instructions: Dict) -> Dict[str, Any]:
        """AI ile ürün açıklamasını iyileştir"""
        try:
            current_description = product_data.get('description', '')
            product_name = product_data.get('name', '')
            category = product_data.get('category', '')
            
            enhanced_description = current_description
            changes = []
            
            # Uzunluk optimizasyonu
            if enhancement_instructions.get('optimize_length'):
                target_length = enhancement_instructions.get('target_length', 200)
                if len(current_description) < target_length:
                    enhanced_description = self._expand_description(
                        enhanced_description, product_name, category, target_length
                    )
                    changes.append('expanded_content')
                elif len(current_description) > target_length * 1.5:
                    enhanced_description = self._compress_description(
                        enhanced_description, target_length
                    )
                    changes.append('compressed_content')
            
            # SEO anahtar kelimeleri ekleme
            if enhancement_instructions.get('add_seo_keywords'):
                keywords = enhancement_instructions.get('keywords', [])
                enhanced_description = self._add_seo_keywords(
                    enhanced_description, keywords
                )
                changes.append('added_seo_keywords')
            
            # Satış odaklı dil kullanımı
            if enhancement_instructions.get('sales_focused'):
                enhanced_description = self._make_sales_focused(enhanced_description)
                changes.append('sales_optimization')
            
            # Teknik detaylar ekleme
            if enhancement_instructions.get('add_technical_details'):
                technical_info = enhancement_instructions.get('technical_info', {})
                enhanced_description = self._add_technical_details(
                    enhanced_description, technical_info
                )
                changes.append('technical_details')
            
            return {
                'success': True,
                'original_description': current_description,
                'enhanced_description': enhanced_description,
                'changes_applied': changes,
                'improvement_score': self._calculate_improvement_score(
                    current_description, enhanced_description
                )
            }
            
        except Exception as e:
            self.logger.error(f"Açıklama iyileştirme hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    def _expand_description(self, description: str, product_name: str, category: str, target_length: int) -> str:
        """Açıklamayı genişlet"""
        if len(description) >= target_length:
            return description
        
        # Kategori bazlı ek bilgiler
        category_additions = {
            'elektronik': 'Yüksek kaliteli malzemeler kullanılarak üretilmiştir. Uzun ömürlü ve güvenilir performans sunar.',
            'giyim': 'Konforlu kumaş yapısı ile günlük kullanıma uygundur. Şık tasarımı ile her ortamda rahatlıkla kullanılabilir.',
            'ev': 'Ev dekorasyonunuz için mükemmel bir seçim. Kaliteli işçilik ve dayanıklı yapısı ile uzun yıllar kullanabilirsiniz.',
            'spor': 'Aktif yaşam tarzınız için ideal. Profesyonel kalitede üretim ve ergonomik tasarım.',
            'kitap': 'Bilgi dolu içeriği ile kişisel gelişiminize katkı sağlar. Kolay okunabilir format ve kaliteli baskı.'
        }
        
        # Genel ek bilgiler
        general_additions = [
            f"{product_name} özenle seçilmiş malzemelerle üretilmiştir.",
            "Müşteri memnuniyeti bizim önceliğimizdir.",
            "Hızlı kargo ve güvenli teslimat imkanı.",
            "Kalite garantisi ile sunulmaktadır.",
            "Uzman ekibimiz tarafından test edilmiştir."
        ]
        
        expanded = description
        
        # Kategori bazlı ekleme
        if category.lower() in category_additions:
            expanded += " " + category_additions[category.lower()]
        
        # Genel eklemeler
        for addition in general_additions:
            if len(expanded) < target_length:
                expanded += " " + addition
            else:
                break
        
        return expanded[:target_length] if len(expanded) > target_length else expanded
    
    def _compress_description(self, description: str, target_length: int) -> str:
        """Açıklamayı sıkıştır"""
        if len(description) <= target_length:
            return description
        
        # Cümleleri ayır
        sentences = description.split('.')
        
        # Önemli cümleleri koru
        important_keywords = ['kalite', 'özellik', 'avantaj', 'fiyat', 'garanti']
        important_sentences = []
        other_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            is_important = any(keyword in sentence.lower() for keyword in important_keywords)
            if is_important:
                important_sentences.append(sentence)
            else:
                other_sentences.append(sentence)
        
        # Önce önemli cümleleri ekle
        compressed = '. '.join(important_sentences)
        
        # Gerekirse diğer cümleleri ekle
        for sentence in other_sentences:
            if len(compressed + '. ' + sentence) <= target_length:
                compressed += '. ' + sentence
            else:
                break
        
        return compressed
    
    def _add_seo_keywords(self, description: str, keywords: List[str]) -> str:
        """SEO anahtar kelimeleri ekle"""
        enhanced = description
        
        for keyword in keywords:
            if keyword.lower() not in description.lower():
                enhanced += f" {keyword} özelliği ile öne çıkar."
        
        return enhanced
    
    def _make_sales_focused(self, description: str) -> str:
        """Satış odaklı dil kullanımı"""
        sales_phrases = [
            "Sınırlı stok!",
            "Özel fiyat avantajı!",
            "Hemen sipariş verin!",
            "Bu fırsatı kaçırmayın!",
            "Ücretsiz kargo fırsatı!"
        ]
        
        # Rastgele bir satış cümlesi ekle
        import random
        sales_phrase = random.choice(sales_phrases)
        
        return f"{description} {sales_phrase}"
    
    def _add_technical_details(self, description: str, technical_info: Dict) -> str:
        """Teknik detaylar ekle"""
        enhanced = description
        
        if technical_info.get('dimensions'):
            enhanced += f" Boyutlar: {technical_info['dimensions']}"
        
        if technical_info.get('weight'):
            enhanced += f" Ağırlık: {technical_info['weight']}"
        
        if technical_info.get('material'):
            enhanced += f" Malzeme: {technical_info['material']}"
        
        if technical_info.get('color_options'):
            colors = ', '.join(technical_info['color_options'])
            enhanced += f" Renk seçenekleri: {colors}"
        
        return enhanced
    
    def _calculate_improvement_score(self, original: str, enhanced: str) -> float:
        """İyileştirme skorunu hesapla"""
        # Basit metrikler
        length_improvement = min(len(enhanced) / max(len(original), 1), 2.0)
        word_count_improvement = len(enhanced.split()) / max(len(original.split()), 1)
        
        # Anahtar kelime yoğunluğu
        keywords = ['kalite', 'özellik', 'avantaj', 'fiyat', 'garanti', 'hızlı', 'güvenli']
        original_keywords = sum(1 for word in original.lower().split() if word in keywords)
        enhanced_keywords = sum(1 for word in enhanced.lower().split() if word in keywords)
        keyword_improvement = enhanced_keywords / max(original_keywords, 1)
        
        # Genel skor
        score = (length_improvement + word_count_improvement + keyword_improvement) / 3
        return min(score, 5.0)  # Maksimum 5.0 skor
    
    # Renk analizi araçları
    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """Dominant renkleri çıkar"""
        # Görseli küçült (performans için)
        image = image.resize((150, 150))
        
        # RGB formatına çevir
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Pixel verilerini al
        pixels = np.array(image).reshape(-1, 3)
        
        # K-means clustering uygula
        kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Dominant renkleri döndür
        colors = kmeans.cluster_centers_.astype(int)
        return [tuple(color) for color in colors]
    
    def _analyze_color_harmony(self, colors: List[Tuple[int, int, int]]) -> Dict[str, Any]:
        """Renk uyumunu analiz et"""
        if not colors:
            return {'harmony_score': 0, 'harmony_type': 'none'}
        
        # RGB'yi HSV'ye çevir
        hsv_colors = []
        for r, g, b in colors:
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            hsv_colors.append((h*360, s*100, v*100))
        
        # Renk uyum türlerini kontrol et
        harmony_types = []
        
        # Monochromatic (tek renk tonları)
        hues = [h for h, s, v in hsv_colors]
        if max(hues) - min(hues) < 30:
            harmony_types.append('monochromatic')
        
        # Complementary (tamamlayıcı renkler)
        for i, h1 in enumerate(hues):
            for j, h2 in enumerate(hues[i+1:], i+1):
                if abs(h1 - h2) > 150 and abs(h1 - h2) < 210:
                    harmony_types.append('complementary')
                    break
        
        # Triadic (üçlü uyum)
        if len(hues) >= 3:
            sorted_hues = sorted(hues)
            for i in range(len(sorted_hues) - 2):
                diff1 = sorted_hues[i+1] - sorted_hues[i]
                diff2 = sorted_hues[i+2] - sorted_hues[i+1]
                if abs(diff1 - 120) < 30 and abs(diff2 - 120) < 30:
                    harmony_types.append('triadic')
                    break
        
        # Uyum skoru hesapla
        harmony_score = len(harmony_types) * 2.5 if harmony_types else 1.0
        harmony_score = min(harmony_score, 10.0)
        
        return {
            'harmony_score': harmony_score,
            'harmony_types': harmony_types,
            'dominant_hue': max(set(hues), key=hues.count) if hues else 0,
            'color_temperature': self._calculate_color_temperature(colors)
        }
    
    def _calculate_color_temperature(self, colors: List[Tuple[int, int, int]]) -> str:
        """Renk sıcaklığını hesapla"""
        if not colors:
            return 'neutral'
        
        warm_score = 0
        cool_score = 0
        
        for r, g, b in colors:
            # Sıcak renkler (kırmızı, turuncu, sarı ağırlıklı)
            if r > g and r > b:
                warm_score += 1
            elif r > g > b:
                warm_score += 0.5
            
            # Soğuk renkler (mavi, yeşil ağırlıklı)
            elif b > r and b > g:
                cool_score += 1
            elif g > r and g > b:
                cool_score += 0.5
        
        if warm_score > cool_score:
            return 'warm'
        elif cool_score > warm_score:
            return 'cool'
        else:
            return 'neutral'
    
    def _generate_color_palette(self, base_colors: List[Tuple[int, int, int]], palette_type: str = 'complementary') -> List[Tuple[int, int, int]]:
        """Renk paleti oluştur"""
        if not base_colors:
            return []
        
        primary_color = base_colors[0]
        r, g, b = primary_color
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        
        palette = [primary_color]
        
        if palette_type == 'complementary':
            # Tamamlayıcı renk
            comp_h = (h + 0.5) % 1.0
            comp_r, comp_g, comp_b = colorsys.hsv_to_rgb(comp_h, s, v)
            palette.append((int(comp_r*255), int(comp_g*255), int(comp_b*255)))
        
        elif palette_type == 'triadic':
            # Üçlü uyum
            for offset in [1/3, 2/3]:
                tri_h = (h + offset) % 1.0
                tri_r, tri_g, tri_b = colorsys.hsv_to_rgb(tri_h, s, v)
                palette.append((int(tri_r*255), int(tri_g*255), int(tri_b*255)))
        
        elif palette_type == 'analogous':
            # Benzer renkler
            for offset in [-0.1, 0.1]:
                ana_h = (h + offset) % 1.0
                ana_r, ana_g, ana_b = colorsys.hsv_to_rgb(ana_h, s, v)
                palette.append((int(ana_r*255), int(ana_g*255), int(ana_b*255)))
        
        return palette
    
    # Kullanıcı içerik analizi
    async def _get_user_content_data(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı içerik verilerini al"""
        try:
            # Kullanıcının AI işleme geçmişi
            processing_query = """
            SELECT * FROM ai_processing_results 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 100
            """
            processing_results = await self.db.fetch_all(processing_query, (user_id,))
            
            # Kullanıcının şablon geçmişi
            template_query = """
            SELECT * FROM ai_template_results 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 50
            """
            template_results = await self.db.fetch_all(template_query, (user_id,))
            
            # Kullanıcı profili
            profile_query = "SELECT * FROM user_ai_profiles WHERE user_id = %s"
            profile_result = await self.db.fetch_one(profile_query, (user_id,))
            
            return {
                'user_id': user_id,
                'processing_history': [dict(row) for row in processing_results] if processing_results else [],
                'template_history': [dict(row) for row in template_results] if template_results else [],
                'ai_profile': dict(profile_result) if profile_result else {},
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Kullanıcı içerik verisi alma hatası: {e}")
            return {'user_id': user_id, 'error': str(e)}
    
    async def _analyze_user_preferences(self, user_data: Dict) -> Dict[str, Any]:
        """Kullanıcı tercihlerini analiz et"""
        try:
            processing_history = user_data.get('processing_history', [])
            template_history = user_data.get('template_history', [])
            
            # Kategori tercihleri
            category_counts = {}
            for record in processing_history:
                classification = json.loads(record.get('classification', '{}'))
                if 'categories' in classification:
                    for category in classification['categories']:
                        cat_name = category.get('label', 'unknown')
                        category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
            
            # Şablon türü tercihleri
            template_counts = {}
            for record in template_history:
                template_type = record.get('template_type', 'unknown')
                template_counts[template_type] = template_counts.get(template_type, 0) + 1
            
            # En çok kullanılan özellikler
            preferred_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            preferred_templates = sorted(template_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                'preferred_categories': preferred_categories,
                'preferred_templates': preferred_templates,
                'total_processed': len(processing_history),
                'total_templates': len(template_history),
                'activity_score': min((len(processing_history) + len(template_history)) / 10, 10.0)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _analyze_content_patterns(self, user_data: Dict) -> Dict[str, Any]:
        """İçerik desenlerini analiz et"""
        try:
            processing_history = user_data.get('processing_history', [])
            
            if not processing_history:
                return {'patterns': [], 'insights': []}
            
            # Zaman desenleri
            time_patterns = {}
            for record in processing_history:
                created_at = record.get('created_at')
                if created_at:
                    hour = created_at.hour if hasattr(created_at, 'hour') else 12
                    time_patterns[hour] = time_patterns.get(hour, 0) + 1
            
            # En aktif saatler
            peak_hours = sorted(time_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # İşleme başarı oranı
            successful = sum(1 for record in processing_history if record.get('status') == 'success')
            success_rate = (successful / len(processing_history)) * 100 if processing_history else 0
            
            # Ortalama işleme süresi
            processing_times = [record.get('processing_time', 0) for record in processing_history if record.get('processing_time')]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            patterns = []
            insights = []
            
            # Desenler
            if peak_hours:
                patterns.append({
                    'type': 'time_preference',
                    'data': peak_hours,
                    'description': f"En aktif saat: {peak_hours[0][0]}:00"
                })
                insights.append(f"Genellikle saat {peak_hours[0][0]}:00 civarında daha aktifsiniz")
            
            if success_rate > 90:
                insights.append("Yüksek başarı oranınız var, AI özelliklerini etkili kullanıyorsunuz")
            elif success_rate < 70:
                insights.append("AI özelliklerini daha etkili kullanmak için destek alabilirsiniz")
            
            if avg_processing_time > 5:
                insights.append("İşleme süreleriniz ortalamanın üstünde, daha küçük dosyalar kullanmayı deneyin")
            
            return {
                'patterns': patterns,
                'insights': insights,
                'success_rate': success_rate,
                'avg_processing_time': avg_processing_time,
                'peak_activity_hours': [hour for hour, count in peak_hours]
            }
            
        except Exception as e:
            return {'error': str(e)}


# Global helper instance
ai_helpers = AdvancedAIHelpers()