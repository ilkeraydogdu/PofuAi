#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced AI Core Module
======================

Gelişmiş yapay zeka çekirdeği - rol tabanlı hizmetler ve gelişmiş özellikler
- Rol tabanlı AI hizmetleri
- Ürün düzenleme AI'ı
- Sosyal medya şablon üretimi
- Gelişmiş içerik yönetimi
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
from io import BytesIO

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from transformers import pipeline, AutoTokenizer, AutoModel, BlipProcessor, BlipForConditionalGeneration
import cv2
import requests

from core.Services.logger import LoggerService
from core.Database.connection import DatabaseConnection
from core.AI.ai_core import ai_core


class AdvancedAICore:
    """
    Gelişmiş AI çekirdeği sınıfı
    Rol tabanlı hizmetler ve gelişmiş özellikler sunar
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
        
        # Temel AI Core'u kullan
        self.base_ai = ai_core
        
        # Gelişmiş AI modelleri ve pipeline'ları
        self.advanced_models = {}
        self.advanced_pipelines = {}
        self.device = self.base_ai.device
        
        # Rol tabanlı izinler
        self.role_permissions = {
            'admin': ['*'],  # Tüm özellikler
            'moderator': [
                'basic_editing', 'template_generation', 'content_analysis',
                'batch_processing', 'user_content_management'
            ],
            'editor': [
                'basic_editing', 'template_generation', 'content_analysis'
            ],
            'user': [
                'basic_template_generation', 'personal_content_analysis'
            ]
        }
        
        # Template konfigürasyonları
        self.template_configs = {
            'instagram_post': {'width': 1080, 'height': 1080},
            'instagram_story': {'width': 1080, 'height': 1920},
            'facebook_post': {'width': 1200, 'height': 630},
            'twitter_post': {'width': 1200, 'height': 675},
            'linkedin_post': {'width': 1200, 'height': 627},
            'telegram_post': {'width': 1280, 'height': 720},
            'whatsapp_status': {'width': 1080, 'height': 1920}
        }
        
        # Performans metrikleri
        self.advanced_metrics = {
            'role_based_requests': {},
            'template_generations': 0,
            'product_edits': 0,
            'advanced_analysis': 0
        }
        
        # Thread pool executor
        self.advanced_executor = ThreadPoolExecutor(max_workers=8)
        
        # Başlatma
        self._initialize_advanced_models()
        
        self.logger.info("Advanced AI Core başlatıldı")
    
    def _initialize_advanced_models(self):
        """Gelişmiş AI modellerini başlat"""
        try:
            # Görsel açıklama modeli (BLIP)
            try:
                self.advanced_models['blip_processor'] = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.advanced_models['blip_model'] = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
                self.logger.info("BLIP görsel açıklama modeli yüklendi")
            except Exception as e:
                self.logger.warning(f"BLIP modeli yüklenemedi: {e}")
            
            # Gelişmiş metin üretimi modeli
            try:
                self.advanced_pipelines['text_generator'] = pipeline(
                    "text-generation",
                    model="microsoft/DialoGPT-medium",
                    device=0 if self.device == "cuda" else -1,
                    max_length=200
                )
                self.logger.info("Metin üretimi modeli yüklendi")
            except Exception as e:
                self.logger.warning(f"Metin üretimi modeli yüklenemedi: {e}")
            
            # Stil transfer modeli (basit)
            try:
                self.advanced_models['style_transfer'] = self._init_style_transfer()
                self.logger.info("Stil transfer modeli hazırlandı")
            except Exception as e:
                self.logger.warning(f"Stil transfer modeli yüklenemedi: {e}")
            
            # Renk paleti analizi
            self.advanced_models['color_analyzer'] = self._init_color_analyzer()
            
            self.logger.info("Gelişmiş AI modelleri başarıyla yüklendi")
            
        except Exception as e:
            self.logger.error(f"Gelişmiş AI modelleri yüklenirken hata: {e}")
            raise
    
    def _init_style_transfer(self):
        """Basit stil transfer sistemi"""
        return {
            'filters': {
                'vintage': lambda img: self._apply_vintage_filter(img),
                'modern': lambda img: self._apply_modern_filter(img),
                'professional': lambda img: self._apply_professional_filter(img),
                'artistic': lambda img: self._apply_artistic_filter(img)
            }
        }
    
    def _init_color_analyzer(self):
        """Renk analizi sistemi"""
        return {
            'dominant_colors': self._extract_dominant_colors,
            'color_harmony': self._analyze_color_harmony,
            'palette_generator': self._generate_color_palette
        }
    
    def check_permission(self, user_role: str, required_permission: str) -> bool:
        """Kullanıcı izin kontrolü"""
        if user_role not in self.role_permissions:
            return False
        
        permissions = self.role_permissions[user_role]
        return '*' in permissions or required_permission in permissions
    
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
            template_type: Şablon türü (instagram_post, telegram_post, vb.)
            content_data: İçerik verileri
            
        Returns:
            Oluşturulan şablon bilgileri
        """
        start_time = datetime.now()
        
        try:
            # İzin kontrolü
            required_permission = 'template_generation' if user_role != 'user' else 'basic_template_generation'
            if not self.check_permission(user_role, required_permission):
                return {
                    'success': False,
                    'error': 'Bu işlem için yetkiniz bulunmamaktadır',
                    'code': 'PERMISSION_DENIED'
                }
            
            # Şablon konfigürasyonunu al
            if template_type not in self.template_configs:
                return {
                    'success': False,
                    'error': 'Geçersiz şablon türü',
                    'code': 'INVALID_TEMPLATE_TYPE'
                }
            
            config = self.template_configs[template_type]
            
            # Şablon oluşturma görevleri
            tasks = []
            
            # Arka plan oluştur
            tasks.append(self._generate_background(config, content_data))
            
            # Metin içeriği oluştur
            if content_data.get('generate_text'):
                tasks.append(self._generate_marketing_text(content_data))
            
            # Görsel öğeler ekle
            if content_data.get('product_image'):
                tasks.append(self._process_product_image(content_data['product_image']))
            
            # Paralel işleme
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Şablonu birleştir
            template_result = await self._compose_template(
                config, content_data, results
            )
            
            # Sonucu kaydet
            template_info = {
                'user_id': user_id,
                'template_type': template_type,
                'content_data': content_data,
                'template_path': template_result.get('template_path'),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'status': 'success',
                'created_at': datetime.now().isoformat()
            }
            
            await self._save_template_result(template_info)
            
            # Metrikleri güncelle
            self._update_advanced_metrics('template_generation', user_role)
            
            self.logger.info(f"Sosyal medya şablonu oluşturuldu: {template_type} (Kullanıcı: {user_id})")
            
            return {
                'success': True,
                'template_info': template_info,
                'download_url': template_result.get('download_url'),
                'preview_url': template_result.get('preview_url')
            }
            
        except Exception as e:
            self.logger.error(f"Şablon oluşturma hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'TEMPLATE_GENERATION_ERROR'
            }
    
    async def ai_edit_product(
        self,
        user_id: int,
        user_role: str,
        product_id: int,
        edit_instructions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI ile ürün düzenleme (sadece admin kullanıcılar için)
        
        Args:
            user_id: Kullanıcı ID'si
            user_role: Kullanıcı rolü
            product_id: Ürün ID'si
            edit_instructions: Düzenleme talimatları
            
        Returns:
            Düzenleme sonuçları
        """
        start_time = datetime.now()
        
        try:
            # Admin izin kontrolü
            if not self.check_permission(user_role, 'product_editing') and user_role != 'admin':
                return {
                    'success': False,
                    'error': 'Ürün düzenleme sadece admin kullanıcılar için kullanılabilir',
                    'code': 'ADMIN_ONLY_FEATURE'
                }
            
            # Ürün bilgilerini al
            product_data = await self._get_product_data(product_id)
            if not product_data:
                return {
                    'success': False,
                    'error': 'Ürün bulunamadı',
                    'code': 'PRODUCT_NOT_FOUND'
                }
            
            # AI düzenleme görevleri
            edit_results = {}
            
            # Görsel düzenleme
            if edit_instructions.get('image_editing'):
                image_edit_result = await self._ai_edit_product_images(
                    product_data, edit_instructions['image_editing']
                )
                edit_results['image_editing'] = image_edit_result
            
            # Açıklama düzenleme
            if edit_instructions.get('description_enhancement'):
                description_result = await self._ai_enhance_product_description(
                    product_data, edit_instructions['description_enhancement']
                )
                edit_results['description_enhancement'] = description_result
            
            # SEO optimizasyonu
            if edit_instructions.get('seo_optimization'):
                seo_result = await self._ai_optimize_product_seo(
                    product_data, edit_instructions['seo_optimization']
                )
                edit_results['seo_optimization'] = seo_result
            
            # Fiyat analizi ve önerisi
            if edit_instructions.get('price_analysis'):
                price_result = await self._ai_analyze_product_pricing(
                    product_data, edit_instructions['price_analysis']
                )
                edit_results['price_analysis'] = price_result
            
            # Sonuçları kaydet
            edit_info = {
                'user_id': user_id,
                'product_id': product_id,
                'edit_instructions': edit_instructions,
                'edit_results': edit_results,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'status': 'success',
                'created_at': datetime.now().isoformat()
            }
            
            await self._save_product_edit_result(edit_info)
            
            # Metrikleri güncelle
            self._update_advanced_metrics('product_edit', user_role)
            
            self.logger.info(f"Ürün AI düzenlemesi tamamlandı: {product_id} (Admin: {user_id})")
            
            return {
                'success': True,
                'edit_info': edit_info,
                'changes_summary': self._generate_changes_summary(edit_results)
            }
            
        except Exception as e:
            self.logger.error(f"Ürün düzenleme hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'PRODUCT_EDIT_ERROR'
            }
    
    async def personalized_content_analysis(
        self,
        user_id: int,
        user_role: str,
        analysis_type: str = 'comprehensive'
    ) -> Dict[str, Any]:
        """
        Kişiselleştirilmiş içerik analizi
        
        Args:
            user_id: Kullanıcı ID'si
            user_role: Kullanıcı rolü
            analysis_type: Analiz türü
            
        Returns:
            Analiz sonuçları
        """
        try:
            # İzin kontrolü
            required_permission = 'content_analysis' if user_role != 'user' else 'personal_content_analysis'
            if not self.check_permission(user_role, required_permission):
                return {
                    'success': False,
                    'error': 'Bu analiz için yetkiniz bulunmamaktadır',
                    'code': 'PERMISSION_DENIED'
                }
            
            # Kullanıcı verilerini al
            user_data = await self._get_user_content_data(user_id)
            
            # Analiz görevleri
            analysis_tasks = []
            
            # Temel analiz (tüm roller için)
            analysis_tasks.append(self._analyze_user_preferences(user_data))
            analysis_tasks.append(self._analyze_content_patterns(user_data))
            
            # Gelişmiş analiz (admin, moderator, editor için)
            if user_role in ['admin', 'moderator', 'editor']:
                analysis_tasks.append(self._analyze_market_trends(user_data))
                analysis_tasks.append(self._generate_content_recommendations(user_data))
            
            # Admin özel analiz
            if user_role == 'admin':
                analysis_tasks.append(self._analyze_business_insights(user_data))
                analysis_tasks.append(self._generate_strategic_recommendations(user_data))
            
            # Paralel analiz
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Sonuçları birleştir
            final_analysis = self._combine_analysis_results(analysis_results, user_role)
            
            # Analiz sonucunu kaydet
            await self._save_analysis_result(user_id, final_analysis)
            
            # Metrikleri güncelle
            self._update_advanced_metrics('advanced_analysis', user_role)
            
            return {
                'success': True,
                'analysis': final_analysis,
                'user_role': user_role,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"İçerik analizi hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'ANALYSIS_ERROR'
            }
    
    # Yardımcı metodlar
    async def _generate_background(self, config: Dict, content_data: Dict) -> Dict[str, Any]:
        """Şablon arka planı oluştur"""
        try:
            width, height = config['width'], config['height']
            
            # Gradient arka plan oluştur
            background = Image.new('RGB', (width, height), color='white')
            
            # Gradient efekti
            if content_data.get('background_style') == 'gradient':
                colors = content_data.get('gradient_colors', ['#FF6B6B', '#4ECDC4'])
                background = self._create_gradient_background(width, height, colors)
            
            # Solid renk
            elif content_data.get('background_style') == 'solid':
                color = content_data.get('background_color', '#FFFFFF')
                background = Image.new('RGB', (width, height), color=color)
            
            # Texture arka plan
            elif content_data.get('background_style') == 'texture':
                background = self._create_texture_background(width, height, content_data.get('texture_type', 'paper'))
            
            return {
                'background': background,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    async def _generate_marketing_text(self, content_data: Dict) -> Dict[str, Any]:
        """Pazarlama metni oluştur"""
        try:
            if 'text_generator' not in self.advanced_pipelines:
                return {'text': content_data.get('text', ''), 'status': 'fallback'}
            
            # Prompt oluştur
            prompt = self._create_marketing_prompt(content_data)
            
            # Metin üret
            generated = self.advanced_pipelines['text_generator'](
                prompt, 
                max_length=150, 
                num_return_sequences=1,
                temperature=0.7
            )
            
            generated_text = generated[0]['generated_text'].replace(prompt, '').strip()
            
            return {
                'text': generated_text,
                'original_prompt': prompt,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'text': content_data.get('text', ''),
                'error': str(e),
                'status': 'error'
            }
    
    async def _process_product_image(self, image_path: str) -> Dict[str, Any]:
        """Ürün görselini işle"""
        try:
            # Görseli yükle
            image = Image.open(image_path)
            
            # Arka plan kaldırma (basit)
            processed_image = self._remove_background_simple(image)
            
            # Kalite iyileştirme
            enhanced_image = self._enhance_image_quality(processed_image)
            
            return {
                'processed_image': enhanced_image,
                'original_size': image.size,
                'processed_size': enhanced_image.size,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def _create_gradient_background(self, width: int, height: int, colors: List[str]) -> Image.Image:
        """Gradient arka plan oluştur"""
        # Basit dikey gradient
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Renkleri parse et
        start_color = tuple(int(colors[0][i:i+2], 16) for i in (1, 3, 5))
        end_color = tuple(int(colors[1][i:i+2], 16) for i in (1, 3, 5))
        
        # Gradient çiz
        for y in range(height):
            ratio = y / height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return image
    
    def _create_texture_background(self, width: int, height: int, texture_type: str) -> Image.Image:
        """Texture arka plan oluştur"""
        # Basit texture patterns
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        if texture_type == 'dots':
            for x in range(0, width, 20):
                for y in range(0, height, 20):
                    draw.ellipse([x, y, x+5, y+5], fill='lightgray')
        
        elif texture_type == 'lines':
            for y in range(0, height, 10):
                draw.line([(0, y), (width, y)], fill='lightgray', width=1)
        
        return image
    
    def _remove_background_simple(self, image: Image.Image) -> Image.Image:
        """Basit arka plan kaldırma"""
        # Bu örnekte basit bir threshold yöntemi kullanıyoruz
        # Gerçek uygulamada U-Net veya diğer segmentasyon modelleri kullanılabilir
        
        # RGBA formatına çevir
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Beyaz arka planı şeffaf yap (basit yaklaşım)
        data = image.getdata()
        new_data = []
        
        for item in data:
            # Beyaza yakın pikselleri şeffaf yap
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        
        image.putdata(new_data)
        return image
    
    def _enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """Görsel kalitesini iyileştir"""
        # Keskinlik artırma
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        # Kontrast iyileştirme
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        # Renk doygunluğu
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.1)
        
        return image
    
    async def _compose_template(self, config: Dict, content_data: Dict, results: List) -> Dict[str, Any]:
        """Şablon öğelerini birleştir"""
        try:
            width, height = config['width'], config['height']
            
            # Arka planı al
            background_result = results[0] if len(results) > 0 else None
            if background_result and background_result.get('status') == 'success':
                final_image = background_result['background'].copy()
            else:
                final_image = Image.new('RGB', (width, height), color='white')
            
            # Metin ekle
            if len(results) > 1 and results[1].get('status') == 'success':
                text = results[1]['text']
                final_image = self._add_text_to_image(final_image, text, content_data)
            
            # Ürün görseli ekle
            if len(results) > 2 and results[2].get('status') == 'success':
                product_image = results[2]['processed_image']
                final_image = self._add_product_to_template(final_image, product_image, content_data)
            
            # Dosyayı kaydet
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"template_{timestamp}.png"
            template_path = os.path.join('storage/templates', filename)
            
            # Dizini oluştur
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            
            # Kaydet
            final_image.save(template_path, 'PNG', quality=95)
            
            return {
                'template_path': template_path,
                'download_url': f'/api/templates/download/{filename}',
                'preview_url': f'/api/templates/preview/{filename}',
                'dimensions': (width, height),
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def _add_text_to_image(self, image: Image.Image, text: str, content_data: Dict) -> Image.Image:
        """Görsele metin ekle"""
        draw = ImageDraw.Draw(image)
        
        # Font ayarları
        try:
            font_size = content_data.get('font_size', 48)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Metin rengi
        text_color = content_data.get('text_color', '#000000')
        
        # Metin pozisyonu (ortalanmış)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (image.width - text_width) // 2
        y = content_data.get('text_y', image.height // 4)
        
        # Metin gölgesi
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill='gray')
        
        # Ana metin
        draw.text((x, y), text, font=font, fill=text_color)
        
        return image
    
    def _add_product_to_template(self, template: Image.Image, product_image: Image.Image, content_data: Dict) -> Image.Image:
        """Şablona ürün görseli ekle"""
        # Ürün görselini yeniden boyutlandır
        max_size = content_data.get('product_max_size', (400, 400))
        product_image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Pozisyon hesapla
        x = content_data.get('product_x', (template.width - product_image.width) // 2)
        y = content_data.get('product_y', template.height // 2)
        
        # Ürün görselini yapıştır
        if product_image.mode == 'RGBA':
            template.paste(product_image, (x, y), product_image)
        else:
            template.paste(product_image, (x, y))
        
        return template
    
    def _create_marketing_prompt(self, content_data: Dict) -> str:
        """Pazarlama metni için prompt oluştur"""
        product_name = content_data.get('product_name', 'ürün')
        category = content_data.get('category', 'genel')
        target_audience = content_data.get('target_audience', 'herkes')
        
        prompt = f"Sosyal medya için {product_name} adlı {category} kategorisindeki ürün için {target_audience} hedef kitlesine yönelik çekici bir pazarlama metni:"
        
        return prompt
    
    # Yardımcı metodlar - AI Helpers'dan import et
    async def _ai_edit_product_images(self, product_data: Dict, edit_instructions: Dict) -> Dict[str, Any]:
        """Ürün görsellerini AI ile düzenle"""
        from core.AI.advanced_ai_helpers import ai_helpers
        return await ai_helpers.ai_edit_product_images(product_data, edit_instructions)
    
    async def _ai_enhance_product_description(self, product_data: Dict, enhancement_instructions: Dict) -> Dict[str, Any]:
        """Ürün açıklamasını AI ile iyileştir"""
        from core.AI.advanced_ai_helpers import ai_helpers
        return await ai_helpers.ai_enhance_product_description(product_data, enhancement_instructions)
    
    async def _ai_optimize_product_seo(self, product_data: Dict, seo_instructions: Dict) -> Dict[str, Any]:
        """Ürün SEO optimizasyonu"""
        try:
            current_meta_title = product_data.get('meta_title', '')
            current_meta_description = product_data.get('meta_description', '')
            product_name = product_data.get('name', '')
            
            optimized_meta_title = current_meta_title or f"{product_name} - En İyi Fiyatlarla"
            optimized_meta_description = current_meta_description or f"{product_name} ürünü için en uygun fiyatlar ve hızlı teslimat imkanı."
            
            # SEO anahtar kelimeleri ekle
            if seo_instructions.get('keywords'):
                keywords = seo_instructions['keywords']
                if not any(keyword.lower() in optimized_meta_title.lower() for keyword in keywords):
                    optimized_meta_title += f" | {keywords[0]}"
            
            return {
                'success': True,
                'original_meta_title': current_meta_title,
                'optimized_meta_title': optimized_meta_title,
                'original_meta_description': current_meta_description,
                'optimized_meta_description': optimized_meta_description,
                'seo_score': self._calculate_seo_score(optimized_meta_title, optimized_meta_description)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _ai_analyze_product_pricing(self, product_data: Dict, pricing_instructions: Dict) -> Dict[str, Any]:
        """Ürün fiyat analizi ve önerisi"""
        try:
            current_price = float(product_data.get('price', 0))
            category = product_data.get('category', '')
            
            # Basit fiyat analizi
            suggested_price = current_price
            analysis = []
            
            # Kategori bazlı fiyat önerileri
            if pricing_instructions.get('market_analysis'):
                if category.lower() in ['elektronik', 'technology']:
                    if current_price > 1000:
                        suggested_price = current_price * 0.95  # %5 indirim öner
                        analysis.append("Elektronik kategorisinde rekabetçi fiyat önerisi")
                elif category.lower() in ['giyim', 'fashion']:
                    if current_price < 100:
                        suggested_price = current_price * 1.1  # %10 artış öner
                        analysis.append("Giyim kategorisinde premium fiyatlandırma önerisi")
            
            # Psikolojik fiyatlandırma
            if pricing_instructions.get('psychological_pricing'):
                if suggested_price > 10:
                    # .99 ile bitir
                    suggested_price = int(suggested_price) - 0.01
                    analysis.append("Psikolojik fiyatlandırma uygulandı")
            
            return {
                'success': True,
                'current_price': current_price,
                'suggested_price': suggested_price,
                'price_change_percentage': ((suggested_price - current_price) / current_price) * 100,
                'analysis': analysis,
                'confidence_score': 0.75
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_seo_score(self, title: str, description: str) -> float:
        """SEO skorunu hesapla"""
        score = 0
        
        # Başlık uzunluğu (50-60 karakter ideal)
        if 50 <= len(title) <= 60:
            score += 2
        elif 40 <= len(title) <= 70:
            score += 1
        
        # Açıklama uzunluğu (150-160 karakter ideal)
        if 150 <= len(description) <= 160:
            score += 2
        elif 120 <= len(description) <= 180:
            score += 1
        
        # Anahtar kelime varlığı
        common_keywords = ['kalite', 'fiyat', 'hızlı', 'güvenli', 'teslimat']
        keyword_count = sum(1 for keyword in common_keywords if keyword in description.lower())
        score += min(keyword_count, 3)
        
        return min(score, 10.0)
    
    def _generate_changes_summary(self, edit_results: Dict) -> Dict[str, Any]:
        """Değişiklik özetini oluştur"""
        summary = {
            'total_changes': 0,
            'successful_changes': 0,
            'change_details': []
        }
        
        for change_type, result in edit_results.items():
            summary['total_changes'] += 1
            if result.get('success'):
                summary['successful_changes'] += 1
                summary['change_details'].append({
                    'type': change_type,
                    'status': 'success',
                    'description': self._get_change_description(change_type, result)
                })
            else:
                summary['change_details'].append({
                    'type': change_type,
                    'status': 'failed',
                    'error': result.get('error', 'Bilinmeyen hata')
                })
        
        return summary
    
    def _get_change_description(self, change_type: str, result: Dict) -> str:
        """Değişiklik açıklamasını oluştur"""
        descriptions = {
            'image_editing': f"{result.get('edited_count', 0)} görsel başarıyla düzenlendi",
            'description_enhancement': f"Açıklama iyileştirildi (Skor: {result.get('improvement_score', 0):.1f})",
            'seo_optimization': f"SEO optimizasyonu tamamlandı (Skor: {result.get('seo_score', 0):.1f})",
            'price_analysis': f"Fiyat analizi: %{result.get('price_change_percentage', 0):.1f} değişiklik önerisi"
        }
        return descriptions.get(change_type, f"{change_type} işlemi tamamlandı")
    
    async def _get_product_data(self, product_id: int) -> Optional[Dict]:
        """Ürün verilerini al"""
        try:
            query = "SELECT * FROM products WHERE id = %s"
            result = await self.db.fetch_one(query, (product_id,))
            return dict(result) if result else None
        except Exception as e:
            self.logger.error(f"Ürün veri alma hatası: {e}")
            return None
    
    async def _get_user_content_data(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı içerik verilerini al"""
        from core.AI.advanced_ai_helpers import ai_helpers
        return await ai_helpers._get_user_content_data(user_id)
    
    async def _analyze_user_preferences(self, user_data: Dict) -> Dict[str, Any]:
        """Kullanıcı tercihlerini analiz et"""
        from core.AI.advanced_ai_helpers import ai_helpers
        return await ai_helpers._analyze_user_preferences(user_data)
    
    async def _analyze_content_patterns(self, user_data: Dict) -> Dict[str, Any]:
        """İçerik desenlerini analiz et"""
        from core.AI.advanced_ai_helpers import ai_helpers
        return await ai_helpers._analyze_content_patterns(user_data)
    
    async def _analyze_market_trends(self, user_data: Dict) -> Dict[str, Any]:
        """Pazar trendlerini analiz et"""
        try:
            # Basit trend analizi
            processing_history = user_data.get('processing_history', [])
            
            # Son 30 günün verileri
            recent_data = [
                record for record in processing_history 
                if (datetime.now() - datetime.fromisoformat(record.get('created_at', datetime.now().isoformat()))).days <= 30
            ]
            
            trends = {
                'popular_categories': self._get_popular_categories(recent_data),
                'growth_areas': self._identify_growth_areas(recent_data),
                'seasonal_patterns': self._detect_seasonal_patterns(recent_data)
            }
            
            return {
                'success': True,
                'trends': trends,
                'analysis_period': '30_days',
                'data_points': len(recent_data)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _generate_content_recommendations(self, user_data: Dict) -> Dict[str, Any]:
        """İçerik önerileri oluştur"""
        try:
            preferences = await self._analyze_user_preferences(user_data)
            
            recommendations = []
            
            # Kategori bazlı öneriler
            if preferences.get('preferred_categories'):
                top_category = preferences['preferred_categories'][0][0]
                recommendations.append({
                    'type': 'category_focus',
                    'suggestion': f"{top_category} kategorisinde daha fazla içerik oluşturun",
                    'priority': 'high'
                })
            
            # Şablon önerileri
            if preferences.get('preferred_templates'):
                top_template = preferences['preferred_templates'][0][0]
                recommendations.append({
                    'type': 'template_variety',
                    'suggestion': f"{top_template} dışında farklı şablon türlerini deneyin",
                    'priority': 'medium'
                })
            
            # Aktivite önerileri
            if preferences.get('activity_score', 0) < 5:
                recommendations.append({
                    'type': 'activity_boost',
                    'suggestion': "Daha fazla AI özelliği kullanarak içerik kalitesini artırın",
                    'priority': 'high'
                })
            
            return {
                'success': True,
                'recommendations': recommendations,
                'total_recommendations': len(recommendations)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _analyze_business_insights(self, user_data: Dict) -> Dict[str, Any]:
        """İş zekası analizi (Admin özel)"""
        try:
            processing_history = user_data.get('processing_history', [])
            template_history = user_data.get('template_history', [])
            
            insights = {
                'user_engagement': {
                    'total_activities': len(processing_history) + len(template_history),
                    'avg_daily_usage': self._calculate_daily_usage(processing_history, template_history),
                    'retention_score': self._calculate_retention_score(processing_history)
                },
                'feature_adoption': {
                    'ai_processing_usage': len(processing_history),
                    'template_generation_usage': len(template_history),
                    'most_used_features': self._get_most_used_features(user_data)
                },
                'performance_metrics': {
                    'success_rate': self._calculate_success_rate(processing_history),
                    'avg_processing_time': self._calculate_avg_processing_time(processing_history)
                }
            }
            
            return {
                'success': True,
                'insights': insights,
                'analysis_date': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _generate_strategic_recommendations(self, user_data: Dict) -> Dict[str, Any]:
        """Stratejik öneriler oluştur (Admin özel)"""
        try:
            business_insights = await self._analyze_business_insights(user_data)
            
            strategic_recommendations = []
            
            if business_insights.get('success'):
                insights = business_insights['insights']
                
                # Kullanıcı katılımı önerileri
                engagement = insights.get('user_engagement', {})
                if engagement.get('retention_score', 0) < 0.5:
                    strategic_recommendations.append({
                        'category': 'user_retention',
                        'recommendation': 'Kullanıcı tutma stratejileri geliştirin',
                        'priority': 'critical',
                        'impact': 'high'
                    })
                
                # Özellik benimsenme önerileri
                adoption = insights.get('feature_adoption', {})
                if adoption.get('template_generation_usage', 0) < adoption.get('ai_processing_usage', 0) * 0.3:
                    strategic_recommendations.append({
                        'category': 'feature_promotion',
                        'recommendation': 'Şablon oluşturma özelliğini daha fazla tanıtın',
                        'priority': 'medium',
                        'impact': 'medium'
                    })
                
                # Performans önerileri
                performance = insights.get('performance_metrics', {})
                if performance.get('avg_processing_time', 0) > 5:
                    strategic_recommendations.append({
                        'category': 'performance_optimization',
                        'recommendation': 'Sistem performansını optimize edin',
                        'priority': 'high',
                        'impact': 'high'
                    })
            
            return {
                'success': True,
                'strategic_recommendations': strategic_recommendations,
                'total_recommendations': len(strategic_recommendations)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _combine_analysis_results(self, analysis_results: List, user_role: str) -> Dict[str, Any]:
        """Analiz sonuçlarını birleştir"""
        combined = {
            'user_preferences': {},
            'content_patterns': {},
            'insights': [],
            'recommendations': []
        }
        
        for i, result in enumerate(analysis_results):
            if isinstance(result, Exception):
                continue
                
            if i == 0:  # User preferences
                combined['user_preferences'] = result
            elif i == 1:  # Content patterns
                combined['content_patterns'] = result
            elif i == 2 and user_role in ['admin', 'moderator', 'editor']:  # Market trends
                combined['market_trends'] = result
            elif i == 3 and user_role in ['admin', 'moderator', 'editor']:  # Content recommendations
                combined['recommendations'] = result.get('recommendations', [])
            elif i == 4 and user_role == 'admin':  # Business insights
                combined['business_insights'] = result
            elif i == 5 and user_role == 'admin':  # Strategic recommendations
                combined['strategic_recommendations'] = result.get('strategic_recommendations', [])
        
        return combined
    
    async def _save_analysis_result(self, user_id: int, analysis: Dict):
        """Analiz sonucunu kaydet"""
        try:
            query = """
            INSERT INTO ai_analysis_results 
            (user_id, analysis_data, analysis_type, created_at)
            VALUES (%s, %s, %s, %s)
            """
            values = (
                user_id,
                json.dumps(analysis),
                'personalized_content_analysis',
                datetime.now()
            )
            await self.db.execute(query, values)
        except Exception as e:
            self.logger.error(f"Analiz sonucu kaydetme hatası: {e}")
    
    async def _save_product_edit_result(self, edit_info: Dict):
        """Ürün düzenleme sonucunu kaydet"""
        try:
            query = """
            INSERT INTO ai_product_edits 
            (user_id, product_id, edit_instructions, edit_results, processing_time, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                edit_info['user_id'],
                edit_info['product_id'],
                json.dumps(edit_info['edit_instructions']),
                json.dumps(edit_info['edit_results']),
                edit_info['processing_time'],
                edit_info['status'],
                datetime.now()
            )
            await self.db.execute(query, values)
        except Exception as e:
            self.logger.error(f"Ürün düzenleme sonucu kaydetme hatası: {e}")
    
    # Yardımcı hesaplama metodları
    def _get_popular_categories(self, data: List) -> List:
        """Popüler kategorileri al"""
        category_counts = {}
        for record in data:
            classification = json.loads(record.get('classification', '{}'))
            if 'categories' in classification:
                for category in classification['categories']:
                    cat_name = category.get('label', 'unknown')
                    category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
        
        return sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _identify_growth_areas(self, data: List) -> List:
        """Büyüme alanlarını belirle"""
        # Basit büyüme analizi - son 15 gün vs önceki 15 gün
        now = datetime.now()
        recent_15_days = [
            record for record in data 
            if (now - datetime.fromisoformat(record.get('created_at', now.isoformat()))).days <= 15
        ]
        previous_15_days = [
            record for record in data 
            if 15 < (now - datetime.fromisoformat(record.get('created_at', now.isoformat()))).days <= 30
        ]
        
        recent_categories = self._get_popular_categories(recent_15_days)
        previous_categories = self._get_popular_categories(previous_15_days)
        
        growth_areas = []
        for cat, recent_count in recent_categories:
            previous_count = next((count for prev_cat, count in previous_categories if prev_cat == cat), 0)
            if recent_count > previous_count:
                growth_rate = ((recent_count - previous_count) / max(previous_count, 1)) * 100
                growth_areas.append({'category': cat, 'growth_rate': growth_rate})
        
        return sorted(growth_areas, key=lambda x: x['growth_rate'], reverse=True)[:3]
    
    def _detect_seasonal_patterns(self, data: List) -> Dict:
        """Mevsimsel desenleri tespit et"""
        monthly_counts = {}
        for record in data:
            created_at = datetime.fromisoformat(record.get('created_at', datetime.now().isoformat()))
            month = created_at.month
            monthly_counts[month] = monthly_counts.get(month, 0) + 1
        
        peak_month = max(monthly_counts.items(), key=lambda x: x[1]) if monthly_counts else (1, 0)
        
        return {
            'peak_month': peak_month[0],
            'peak_activity': peak_month[1],
            'monthly_distribution': monthly_counts
        }
    
    def _calculate_daily_usage(self, processing_history: List, template_history: List) -> float:
        """Günlük ortalama kullanımı hesapla"""
        total_activities = len(processing_history) + len(template_history)
        if not total_activities:
            return 0.0
        
        # Son 30 günlük veri
        return total_activities / 30.0
    
    def _calculate_retention_score(self, processing_history: List) -> float:
        """Kullanıcı tutma skorunu hesapla"""
        if not processing_history:
            return 0.0
        
        # Son 7 günde aktivite var mı?
        now = datetime.now()
        recent_activity = any(
            (now - datetime.fromisoformat(record.get('created_at', now.isoformat()))).days <= 7
            for record in processing_history
        )
        
        return 1.0 if recent_activity else 0.3
    
    def _get_most_used_features(self, user_data: Dict) -> List:
        """En çok kullanılan özellikleri al"""
        features = []
        
        if user_data.get('processing_history'):
            features.append({'feature': 'ai_processing', 'usage_count': len(user_data['processing_history'])})
        
        if user_data.get('template_history'):
            features.append({'feature': 'template_generation', 'usage_count': len(user_data['template_history'])})
        
        return sorted(features, key=lambda x: x['usage_count'], reverse=True)
    
    def _calculate_success_rate(self, processing_history: List) -> float:
        """Başarı oranını hesapla"""
        if not processing_history:
            return 0.0
        
        successful = sum(1 for record in processing_history if record.get('status') == 'success')
        return (successful / len(processing_history)) * 100
    
    def _calculate_avg_processing_time(self, processing_history: List) -> float:
        """Ortalama işleme süresini hesapla"""
        times = [record.get('processing_time', 0) for record in processing_history if record.get('processing_time')]
        return sum(times) / len(times) if times else 0.0
    
    async def _save_template_result(self, template_info: Dict):
        """Şablon sonucunu kaydet"""
        try:
            query = """
            INSERT INTO ai_template_results 
            (user_id, template_type, content_data, template_path, processing_time, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                template_info['user_id'],
                template_info['template_type'],
                json.dumps(template_info['content_data']),
                template_info['template_path'],
                template_info['processing_time'],
                template_info['status'],
                datetime.now()
            )
            await self.db.execute(query, values)
        except Exception as e:
            self.logger.error(f"Şablon sonucu kaydetme hatası: {e}")
    
    def _update_advanced_metrics(self, metric_type: str, user_role: str):
        """Gelişmiş metrikleri güncelle"""
        if metric_type in self.advanced_metrics:
            if isinstance(self.advanced_metrics[metric_type], int):
                self.advanced_metrics[metric_type] += 1
        
        # Rol bazlı metrikler
        if user_role not in self.advanced_metrics['role_based_requests']:
            self.advanced_metrics['role_based_requests'][user_role] = 0
        self.advanced_metrics['role_based_requests'][user_role] += 1
    
    def get_advanced_metrics(self) -> Dict[str, Any]:
        """Gelişmiş metrikleri döndür"""
        return {
            **self.base_ai.get_metrics(),
            **self.advanced_metrics,
            'role_permissions': self.role_permissions,
            'template_types': list(self.template_configs.keys())
        }


# Global Advanced AI Core instance
advanced_ai_core = AdvancedAICore()