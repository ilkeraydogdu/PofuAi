#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi Advanced AI Core Module
==============================

Gelişmiş AI özellikleri:
- Rol tabanlı kişiselleştirilmiş AI hizmetleri
- Sosyal medya şablon üretimi
- AI ile ürün düzenleme
- Çoklu dil desteği
- Gelişmiş görüntü işleme
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
import base64
from io import BytesIO

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import cv2
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import openai
from googletrans import Translator

from core.Services.logger import LoggerService
from core.Database.connection import DatabaseConnection
from core.AI.ai_core import ai_core


class AdvancedAICore:
    """
    Gelişmiş AI çekirdeği sınıfı
    Rol tabanlı ve kişiselleştirilmiş AI hizmetleri sunar
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AdvancedAICore, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Advanced AI Core başlatıcı"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.logger = LoggerService.get_logger()
        self.db = DatabaseConnection()
        self.ai_core = ai_core
        
        # AI modelleri ve pipeline'ları
        self.models = {}
        self.pipelines = {}
        self.device = self._get_device()
        
        # Çeviri servisi
        self.translator = Translator()
        
        # OpenAI API (opsiyonel)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Rol bazlı özellikler
        self.role_features = {
            'admin': ['all'],
            'seller': ['template_generation', 'product_enhancement', 'sales_analytics', 'multi_channel'],
            'user': ['basic_templates', 'product_view'],
            'premium': ['advanced_templates', 'ai_assistant', 'bulk_operations']
        }
        
        # Sosyal medya şablon boyutları
        self.template_sizes = {
            'instagram_post': (1080, 1080),
            'instagram_story': (1080, 1920),
            'facebook_post': (1200, 630),
            'twitter_post': (1200, 675),
            'linkedin_post': (1200, 627),
            'telegram_post': (1280, 720),
            'whatsapp_status': (1080, 1920)
        }
        
        # Thread pool executor
        self.executor = ThreadPoolExecutor(max_workers=6)
        
        # Başlatma
        self._initialize_advanced_models()
        
        self.logger.info("Advanced AI Core başlatıldı")
    
    def _get_device(self) -> str:
        """Kullanılacak cihazı belirle (GPU/CPU)"""
        if torch.cuda.is_available():
            device = "cuda"
            self.logger.info(f"GPU kullanılıyor: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            device = "mps"
            self.logger.info("Apple Silicon GPU kullanılıyor")
        else:
            device = "cpu"
            self.logger.info("CPU kullanılıyor")
        
        return device
    
    def _initialize_advanced_models(self):
        """Gelişmiş AI modellerini başlat"""
        try:
            # Metin üretimi modeli (Türkçe destekli)
            self.pipelines['text_generator'] = pipeline(
                "text-generation",
                model="dbmdz/bert-base-turkish-cased",
                device=0 if self.device == "cuda" else -1,
                max_length=200
            )
            
            # Görüntü segmentasyon modeli
            try:
                from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
                self.models['segmentation_processor'] = SegformerImageProcessor.from_pretrained("nvidia/segformer-b0-finetuned-ade-512-512")
                self.models['segmentation_model'] = SegformerForSemanticSegmentation.from_pretrained("nvidia/segformer-b0-finetuned-ade-512-512")
                self.logger.info("Segmentasyon modeli yüklendi")
            except Exception as e:
                self.logger.warning(f"Segmentasyon modeli yüklenemedi: {e}")
            
            # Stil transfer modeli
            try:
                import torch.hub
                self.models['style_transfer'] = torch.hub.load('pytorch/vision:v0.10.0', 'vgg19', pretrained=True)
                self.logger.info("Stil transfer modeli yüklendi")
            except Exception as e:
                self.logger.warning(f"Stil transfer modeli yüklenemedi: {e}")
            
            # OCR modeli
            try:
                import easyocr
                self.models['ocr'] = easyocr.Reader(['tr', 'en'])
                self.logger.info("OCR modeli yüklendi")
            except Exception as e:
                self.logger.warning(f"OCR modeli yüklenemedi: {e}")
            
            self.logger.info("Gelişmiş AI modelleri başarıyla yüklendi")
            
        except Exception as e:
            self.logger.error(f"Gelişmiş AI modelleri yüklenirken hata: {e}")
            raise
    
    async def generate_social_media_template(
        self,
        user_id: int,
        user_role: str,
        template_type: str,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sosyal medya şablonu oluştur
        
        Args:
            user_id: Kullanıcı ID'si
            user_role: Kullanıcı rolü
            template_type: Şablon tipi
            content_data: İçerik verileri
            
        Returns:
            Oluşturulan şablon bilgileri
        """
        try:
            # Rol kontrolü
            if not self._check_feature_access(user_role, 'template_generation'):
                return {
                    'success': False,
                    'error': 'Bu özelliğe erişim yetkiniz yok',
                    'code': 'ACCESS_DENIED'
                }
            
            # Şablon boyutunu al
            template_size = self.template_sizes.get(template_type, (1080, 1080))
            
            # Arka plan oluştur
            background = await self._create_background(template_size, content_data)
            
            # Ürün görselini ekle
            if content_data.get('product_image'):
                background = await self._add_product_image(background, content_data)
            
            # Metin ekle (AI ile oluşturulmuş veya kullanıcı metni)
            if content_data.get('generate_text', False):
                text = await self._generate_marketing_text(content_data)
            else:
                text = content_data.get('text', '')
            
            if text:
                background = await self._add_text_to_image(background, text, content_data)
            
            # Logo/watermark ekle
            if content_data.get('add_watermark', True):
                background = await self._add_watermark(background, user_id)
            
            # Görüntüyü kaydet
            save_path = await self._save_template(background, user_id, template_type)
            
            # Veritabanına kaydet
            template_info = await self._save_template_to_db(
                user_id=user_id,
                template_type=template_type,
                content_data=content_data,
                file_path=save_path
            )
            
            return {
                'success': True,
                'template_info': template_info,
                'download_url': f"/api/ai/download-template/{template_info['id']}",
                'preview_url': f"/api/ai/preview-template/{template_info['id']}"
            }
            
        except Exception as e:
            self.logger.error(f"Şablon oluşturma hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'TEMPLATE_GENERATION_ERROR'
            }
    
    async def _create_background(self, size: Tuple[int, int], content_data: Dict[str, Any]) -> Image.Image:
        """Arka plan oluştur"""
        width, height = size
        background_style = content_data.get('background_style', 'gradient')
        
        if background_style == 'gradient':
            # Gradient arka plan
            colors = content_data.get('gradient_colors', ['#FF6B6B', '#4ECDC4'])
            background = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(background)
            
            # Basit gradient efekti
            for i in range(height):
                ratio = i / height
                r1, g1, b1 = self._hex_to_rgb(colors[0])
                r2, g2, b2 = self._hex_to_rgb(colors[1])
                
                r = int(r1 * (1 - ratio) + r2 * ratio)
                g = int(g1 * (1 - ratio) + g2 * ratio)
                b = int(b1 * (1 - ratio) + b2 * ratio)
                
                draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        elif background_style == 'solid':
            # Düz renk arka plan
            color = content_data.get('background_color', '#FFFFFF')
            background = Image.new('RGB', (width, height), color)
        
        elif background_style == 'texture':
            # Dokulu arka plan
            texture_type = content_data.get('texture_type', 'paper')
            background = await self._create_texture_background(size, texture_type)
        
        else:
            # Varsayılan beyaz arka plan
            background = Image.new('RGB', (width, height), 'white')
        
        return background
    
    async def _add_product_image(self, background: Image.Image, content_data: Dict[str, Any]) -> Image.Image:
        """Ürün görselini arka plana ekle"""
        try:
            product_image_path = content_data['product_image']
            product_image = Image.open(product_image_path)
            
            # Görüntüyü yeniden boyutlandır
            max_size = content_data.get('product_max_size', (400, 400))
            product_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Arka planı kaldır (opsiyonel)
            if content_data.get('remove_product_background', False):
                product_image = await self._remove_background(product_image)
            
            # Gölge efekti ekle
            if content_data.get('add_shadow', True):
                product_image = await self._add_shadow_effect(product_image)
            
            # Pozisyonu belirle
            x = content_data.get('product_x', (background.width - product_image.width) // 2)
            y = content_data.get('product_y', (background.height - product_image.height) // 2)
            
            # Ürün görselini yapıştır
            background.paste(product_image, (x, y), product_image if product_image.mode == 'RGBA' else None)
            
        except Exception as e:
            self.logger.error(f"Ürün görseli ekleme hatası: {e}")
        
        return background
    
    async def _generate_marketing_text(self, content_data: Dict[str, Any]) -> str:
        """AI ile pazarlama metni oluştur"""
        try:
            product_name = content_data.get('product_name', 'Ürün')
            category = content_data.get('category', 'genel')
            target_audience = content_data.get('target_audience', 'herkes')
            
            # OpenAI API varsa kullan
            if self.openai_api_key:
                prompt = f"""
                Ürün: {product_name}
                Kategori: {category}
                Hedef Kitle: {target_audience}
                
                Bu ürün için kısa, etkileyici ve satış odaklı bir sosyal medya metni oluştur.
                Metin maksimum 2-3 cümle olmalı ve emoji içerebilir.
                """
                
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=100,
                    temperature=0.8
                )
                
                return response.choices[0].text.strip()
            
            else:
                # Basit template tabanlı metin üretimi
                templates = [
                    f"🎯 {product_name} ile hayatınızı kolaylaştırın! Hemen keşfedin! ✨",
                    f"⭐ Yeni {product_name} stoklarımızda! Sınırlı sayıda, kaçırmayın! 🛍️",
                    f"🔥 {product_name} - {target_audience} için özel fiyat! Detaylar için tıklayın 👆",
                    f"💎 Kaliteli {product_name} arayanlar buraya! En uygun fiyat garantisi ✅"
                ]
                
                import random
                return random.choice(templates)
                
        except Exception as e:
            self.logger.error(f"Metin üretme hatası: {e}")
            return f"{content_data.get('product_name', 'Ürün')} - Özel Fırsat!"
    
    async def _add_text_to_image(self, image: Image.Image, text: str, content_data: Dict[str, Any]) -> Image.Image:
        """Görüntüye metin ekle"""
        try:
            draw = ImageDraw.Draw(image)
            
            # Font ayarları
            font_size = content_data.get('font_size', 48)
            font_color = content_data.get('text_color', '#000000')
            
            # Sistem fontunu kullan
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Metin pozisyonu
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (image.width - text_width) // 2
            y = content_data.get('text_y', 100)
            
            # Arka plan kutusu (opsiyonel)
            if content_data.get('text_background', True):
                padding = 20
                draw.rectangle(
                    [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                    fill=(255, 255, 255, 200)
                )
            
            # Metni çiz
            draw.text((x, y), text, font=font, fill=font_color)
            
        except Exception as e:
            self.logger.error(f"Metin ekleme hatası: {e}")
        
        return image
    
    async def edit_product_with_ai(
        self,
        user_id: int,
        user_role: str,
        product_id: int,
        edit_instructions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI ile ürün düzenleme (Admin özel)
        
        Args:
            user_id: Kullanıcı ID'si
            user_role: Kullanıcı rolü
            product_id: Ürün ID'si
            edit_instructions: Düzenleme talimatları
            
        Returns:
            Düzenleme sonuçları
        """
        try:
            # Admin kontrolü
            if user_role != 'admin':
                return {
                    'success': False,
                    'error': 'Bu özellik sadece adminler için kullanılabilir',
                    'code': 'ADMIN_ONLY'
                }
            
            # Ürün bilgilerini al
            product = await self._get_product_info(product_id)
            if not product:
                return {
                    'success': False,
                    'error': 'Ürün bulunamadı',
                    'code': 'PRODUCT_NOT_FOUND'
                }
            
            results = {
                'product_id': product_id,
                'edits': {}
            }
            
            # Görüntü düzenleme
            if edit_instructions.get('image_editing'):
                image_result = await self._edit_product_image(
                    product['image_path'],
                    edit_instructions['image_editing']
                )
                results['edits']['image'] = image_result
            
            # Açıklama geliştirme
            if edit_instructions.get('description_enhancement'):
                desc_result = await self._enhance_product_description(
                    product['description'],
                    edit_instructions['description_enhancement']
                )
                results['edits']['description'] = desc_result
            
            # SEO optimizasyonu
            if edit_instructions.get('seo_optimization'):
                seo_result = await self._optimize_product_seo(
                    product,
                    edit_instructions['seo_optimization']
                )
                results['edits']['seo'] = seo_result
            
            # Değişiklikleri kaydet
            if results['edits']:
                await self._save_product_edits(product_id, results['edits'])
                
                return {
                    'success': True,
                    'message': 'Ürün başarıyla düzenlendi',
                    'results': results
                }
            else:
                return {
                    'success': False,
                    'error': 'Düzenlenecek bir şey bulunamadı',
                    'code': 'NO_EDITS'
                }
            
        except Exception as e:
            self.logger.error(f"Ürün düzenleme hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'EDIT_ERROR'
            }
    
    async def get_personalized_ai_service(
        self,
        user_id: int,
        user_role: str,
        service_type: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Kullanıcı rolüne göre kişiselleştirilmiş AI hizmeti
        
        Args:
            user_id: Kullanıcı ID'si
            user_role: Kullanıcı rolü
            service_type: Hizmet tipi
            params: Hizmet parametreleri
            
        Returns:
            AI hizmet sonuçları
        """
        try:
            # Kullanıcı geçmişini analiz et
            user_history = await self._analyze_user_history(user_id)
            
            # Role göre hizmet sun
            if service_type == 'product_recommendation':
                return await self._get_product_recommendations(user_id, user_role, user_history, params)
            
            elif service_type == 'sales_prediction':
                if user_role in ['admin', 'seller']:
                    return await self._predict_sales(user_id, user_history, params)
                else:
                    return {'success': False, 'error': 'Bu hizmet sizin rolünüz için kullanılamaz'}
            
            elif service_type == 'content_optimization':
                return await self._optimize_content(user_id, user_role, params)
            
            elif service_type == 'customer_insights':
                if user_role == 'admin':
                    return await self._get_customer_insights(params)
                else:
                    return {'success': False, 'error': 'Bu hizmet sadece adminler için kullanılabilir'}
            
            else:
                return {'success': False, 'error': 'Geçersiz hizmet tipi'}
            
        except Exception as e:
            self.logger.error(f"Kişiselleştirilmiş AI hizmeti hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    def _check_feature_access(self, user_role: str, feature: str) -> bool:
        """Kullanıcının özelliğe erişim yetkisini kontrol et"""
        role_features = self.role_features.get(user_role, [])
        return 'all' in role_features or feature in role_features
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Hex renk kodunu RGB'ye çevir"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    async def _remove_background(self, image: Image.Image) -> Image.Image:
        """Görüntüden arka planı kaldır"""
        try:
            # Basit bir arka plan kaldırma algoritması
            # Gerçek uygulamada daha gelişmiş bir model kullanılabilir
            import rembg
            
            # PIL Image'ı numpy array'e çevir
            img_array = np.array(image)
            
            # Arka planı kaldır
            output = rembg.remove(img_array)
            
            # Tekrar PIL Image'a çevir
            return Image.fromarray(output)
            
        except Exception as e:
            self.logger.warning(f"Arka plan kaldırma başarısız, orijinal görüntü kullanılıyor: {e}")
            return image
    
    async def _add_shadow_effect(self, image: Image.Image) -> Image.Image:
        """Görüntüye gölge efekti ekle"""
        try:
            # Gölge için yeni bir katman oluştur
            shadow = Image.new('RGBA', (image.width + 20, image.height + 20), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            
            # Gölge dikdörtgeni çiz
            shadow_draw.rectangle([10, 10, image.width + 10, image.height + 10], fill=(0, 0, 0, 100))
            
            # Blur uygula
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=5))
            
            # Orijinal görüntüyü üzerine yapıştır
            shadow.paste(image, (0, 0), image if image.mode == 'RGBA' else None)
            
            return shadow
            
        except Exception as e:
            self.logger.warning(f"Gölge efekti eklenemedi: {e}")
            return image
    
    async def _create_texture_background(self, size: Tuple[int, int], texture_type: str) -> Image.Image:
        """Dokulu arka plan oluştur"""
        width, height = size
        background = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(background)
        
        if texture_type == 'dots':
            # Noktalı doku
            for x in range(0, width, 20):
                for y in range(0, height, 20):
                    draw.ellipse([x, y, x+5, y+5], fill=(230, 230, 230))
        
        elif texture_type == 'lines':
            # Çizgili doku
            for i in range(0, max(width, height), 30):
                draw.line([(i, 0), (i, height)], fill=(240, 240, 240), width=2)
                draw.line([(0, i), (width, i)], fill=(240, 240, 240), width=2)
        
        elif texture_type == 'paper':
            # Kağıt dokusu efekti
            noise = np.random.normal(250, 10, (height, width, 3))
            noise = np.clip(noise, 0, 255).astype(np.uint8)
            background = Image.fromarray(noise)
        
        return background
    
    async def _add_watermark(self, image: Image.Image, user_id: int) -> Image.Image:
        """Görüntüye watermark ekle"""
        try:
            draw = ImageDraw.Draw(image)
            
            # Watermark metni
            watermark_text = "PofuAi"
            
            # Font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Pozisyon (sağ alt köşe)
            text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = image.width - text_width - 10
            y = image.height - text_height - 10
            
            # Yarı saydam beyaz arka plan
            draw.rectangle(
                [x - 5, y - 5, x + text_width + 5, y + text_height + 5],
                fill=(255, 255, 255, 180)
            )
            
            # Watermark metni
            draw.text((x, y), watermark_text, font=font, fill=(100, 100, 100, 200))
            
        except Exception as e:
            self.logger.warning(f"Watermark eklenemedi: {e}")
        
        return image
    
    async def _save_template(self, image: Image.Image, user_id: int, template_type: str) -> str:
        """Şablonu kaydet"""
        try:
            # Kayıt dizini
            save_dir = f"storage/ai_templates/{user_id}"
            os.makedirs(save_dir, exist_ok=True)
            
            # Dosya adı
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{template_type}_{timestamp}.png"
            filepath = os.path.join(save_dir, filename)
            
            # Görüntüyü kaydet
            image.save(filepath, 'PNG', quality=95)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Şablon kaydetme hatası: {e}")
            raise
    
    async def _save_template_to_db(
        self,
        user_id: int,
        template_type: str,
        content_data: Dict[str, Any],
        file_path: str
    ) -> Dict[str, Any]:
        """Şablon bilgilerini veritabanına kaydet"""
        try:
            query = """
            INSERT INTO ai_templates (
                user_id, template_type, content_data, file_path, created_at
            ) VALUES (%s, %s, %s, %s, NOW())
            """
            
            template_id = await self.db.execute_insert(
                query,
                (user_id, template_type, json.dumps(content_data), file_path)
            )
            
            return {
                'id': template_id,
                'user_id': user_id,
                'template_type': template_type,
                'file_path': file_path,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Veritabanına kaydetme hatası: {e}")
            raise
    
    async def _get_product_info(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Ürün bilgilerini getir"""
        try:
            query = """
            SELECT id, name, description, image_path, price, category_id
            FROM products
            WHERE id = %s
            """
            
            result = await self.db.fetch_one(query, (product_id,))
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'description': result[2],
                    'image_path': result[3],
                    'price': result[4],
                    'category_id': result[5]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ürün bilgisi getirme hatası: {e}")
            return None
    
    async def _edit_product_image(self, image_path: str, instructions: Dict[str, Any]) -> Dict[str, Any]:
        """Ürün görselini düzenle"""
        try:
            if not os.path.exists(image_path):
                return {'success': False, 'error': 'Görsel dosyası bulunamadı'}
            
            image = Image.open(image_path)
            original_size = image.size
            
            # Kalite iyileştirme
            if instructions.get('enhance_quality', False):
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.5)
                
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.2)
            
            # Arka plan kaldırma
            if instructions.get('remove_background', False):
                image = await self._remove_background(image)
            
            # Yeniden boyutlandırma
            if instructions.get('resize', False):
                target_size = instructions.get('target_size', (800, 800))
                image.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Filtre uygulama
            if instructions.get('apply_filter', False):
                filter_type = instructions.get('filter_type', 'professional')
                image = await self._apply_image_filter(image, filter_type)
            
            # Watermark ekleme
            if instructions.get('add_watermark', False):
                watermark_text = instructions.get('watermark_text', 'PofuAi')
                image = await self._add_custom_watermark(image, watermark_text)
            
            # Yeni dosya olarak kaydet
            new_path = image_path.replace('.', '_edited.')
            image.save(new_path, quality=95)
            
            return {
                'success': True,
                'original_path': image_path,
                'edited_path': new_path,
                'original_size': original_size,
                'new_size': image.size
            }
            
        except Exception as e:
            self.logger.error(f"Görsel düzenleme hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _enhance_product_description(self, description: str, instructions: Dict[str, Any]) -> Dict[str, Any]:
        """Ürün açıklamasını geliştir"""
        try:
            enhanced_description = description
            
            # Uzunluk optimizasyonu
            if instructions.get('optimize_length', False):
                target_length = instructions.get('target_length', 200)
                if len(description) > target_length:
                    # Kısalt
                    enhanced_description = description[:target_length-3] + "..."
                elif len(description) < target_length * 0.7:
                    # Genişlet
                    enhanced_description = await self._expand_description(description, target_length)
            
            # SEO anahtar kelime ekleme
            if instructions.get('add_seo_keywords', False):
                keywords = instructions.get('keywords', [])
                enhanced_description = await self._add_keywords_to_description(enhanced_description, keywords)
            
            # Satış odaklı dil
            if instructions.get('sales_focused', False):
                enhanced_description = await self._make_description_sales_focused(enhanced_description)
            
            # Teknik detay ekleme
            if instructions.get('add_technical_details', False):
                technical_info = instructions.get('technical_info', {})
                enhanced_description = await self._add_technical_details(enhanced_description, technical_info)
            
            return {
                'success': True,
                'original': description,
                'enhanced': enhanced_description,
                'changes': {
                    'length_change': len(enhanced_description) - len(description),
                    'keywords_added': instructions.get('keywords', [])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Açıklama geliştirme hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _analyze_user_history(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı geçmişini analiz et"""
        try:
            # Son aktiviteler
            activities_query = """
            SELECT activity_type, activity_data, created_at
            FROM user_activities
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 100
            """
            
            activities = await self.db.fetch_all(activities_query, (user_id,))
            
            # Tercihler
            preferences_query = """
            SELECT preference_key, preference_value
            FROM user_preferences
            WHERE user_id = %s
            """
            
            preferences = await self.db.fetch_all(preferences_query, (user_id,))
            
            # AI kullanım istatistikleri
            ai_stats_query = """
            SELECT service_type, COUNT(*) as usage_count
            FROM ai_usage_logs
            WHERE user_id = %s
            GROUP BY service_type
            """
            
            ai_stats = await self.db.fetch_all(ai_stats_query, (user_id,))
            
            return {
                'activities': [{'type': a[0], 'data': a[1], 'created_at': a[2]} for a in activities],
                'preferences': {p[0]: p[1] for p in preferences},
                'ai_usage': {s[0]: s[1] for s in ai_stats}
            }
            
        except Exception as e:
            self.logger.error(f"Kullanıcı geçmişi analiz hatası: {e}")
            return {'activities': [], 'preferences': {}, 'ai_usage': {}}
    
    async def _apply_image_filter(self, image: Image.Image, filter_type: str) -> Image.Image:
        """Görüntüye filtre uygula"""
        try:
            if filter_type == 'professional':
                # Profesyonel görünüm
                image = ImageEnhance.Color(image).enhance(0.9)
                image = ImageEnhance.Brightness(image).enhance(1.1)
                image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150))
            
            elif filter_type == 'vintage':
                # Vintage efekt
                image = ImageEnhance.Color(image).enhance(0.7)
                image = ImageEnhance.Contrast(image).enhance(0.8)
                # Sepia tonu ekle
                sepia = Image.new('RGB', image.size, (112, 66, 20))
                image = Image.blend(image.convert('RGB'), sepia, 0.3)
            
            elif filter_type == 'modern':
                # Modern, canlı görünüm
                image = ImageEnhance.Color(image).enhance(1.3)
                image = ImageEnhance.Contrast(image).enhance(1.2)
                image = ImageEnhance.Sharpness(image).enhance(1.5)
            
            return image
            
        except Exception as e:
            self.logger.warning(f"Filtre uygulama hatası: {e}")
            return image
    
    async def _add_custom_watermark(self, image: Image.Image, watermark_text: str) -> Image.Image:
        """Özel watermark ekle"""
        try:
            # RGBA moduna çevir
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Watermark için overlay oluştur
            txt = Image.new('RGBA', image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt)
            
            # Font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
            except:
                font = ImageFont.load_default()
            
            # Merkeze yerleştir, yarı saydam
            text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (image.width - text_width) // 2
            y = (image.height - text_height) // 2
            
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 80))
            
            # Birleştir
            watermarked = Image.alpha_composite(image, txt)
            
            return watermarked
            
        except Exception as e:
            self.logger.warning(f"Watermark ekleme hatası: {e}")
            return image


# Singleton instance
advanced_ai_core = AdvancedAICore()