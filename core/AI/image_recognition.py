#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi Image Recognition Service
===============================

Gelişmiş görsel tanıma ve analiz servisi
- Çoklu model desteği
- Yüz tanıma
- Nesne algılama
- Sahne analizi
- Renk analizi
- Benzerlik karşılaştırması
"""

import os
import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
import json
from PIL import Image, ImageEnhance, ImageFilter
import face_recognition
import torch
import torchvision.transforms as transforms
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

from core.Services.logger import LoggerService
from .ai_core import ai_core


class ImageRecognitionService:
    """
    Gelişmiş görsel tanıma servisi
    """
    
    def __init__(self):
        self.logger = LoggerService.get_logger()
        self.ai_core = ai_core
        
        # Görsel işleme parametreleri
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        self.max_image_size = (2048, 2048)
        self.thumbnail_size = (256, 256)
        
        # Renk analizi için K-means parametreleri
        self.color_clusters = 5
        
        # Yüz tanıma modeli
        self.face_encodings_cache = {}
        
        self.logger.info("Image Recognition Service başlatıldı")
    
    async def analyze_image_comprehensive(self, image_path: str, user_id: int) -> Dict[str, Any]:
        """
        Kapsamlı görsel analizi
        
        Args:
            image_path: Analiz edilecek görselin yolu
            user_id: Kullanıcı ID'si
            
        Returns:
            Detaylı analiz sonuçları
        """
        try:
            if not self._is_valid_image(image_path):
                raise ValueError(f"Geçersiz görsel dosyası: {image_path}")
            
            # Görsel hash'i oluştur (duplicate detection için)
            image_hash = self._generate_image_hash(image_path)
            
            # Paralel analiz görevleri
            analysis_tasks = [
                self._analyze_basic_properties(image_path),
                self._analyze_colors(image_path),
                self._detect_faces(image_path),
                self._analyze_composition(image_path),
                self._extract_visual_features(image_path),
                self._analyze_quality(image_path)
            ]
            
            # AI Core ile temel işleme
            ai_result = await self.ai_core.process_image(image_path, user_id)
            
            # Tüm analizleri birleştir
            comprehensive_analysis = {
                'image_path': image_path,
                'user_id': user_id,
                'image_hash': image_hash,
                'timestamp': datetime.now().isoformat(),
                'ai_analysis': ai_result,
                'detailed_analysis': {}
            }
            
            # Detaylı analizleri sırayla çalıştır
            analysis_names = ['basic', 'colors', 'faces', 'composition', 'features', 'quality']
            for i, task_name in enumerate(analysis_names):
                try:
                    if i < len(analysis_tasks):
                        result = await analysis_tasks[i]
                        comprehensive_analysis['detailed_analysis'][task_name] = result
                except Exception as e:
                    self.logger.warning(f"{task_name} analizi başarısız: {e}")
                    comprehensive_analysis['detailed_analysis'][task_name] = {'error': str(e)}
            
            # Kategorilendirme önerisi
            comprehensive_analysis['suggested_categories'] = self._suggest_categories(comprehensive_analysis)
            
            # Benzerlik hash'i (duplicate detection için)
            comprehensive_analysis['similarity_hash'] = self._generate_similarity_hash(image_path)
            
            self.logger.info(f"Kapsamlı görsel analizi tamamlandı: {image_path}")
            
            return comprehensive_analysis
            
        except Exception as e:
            self.logger.error(f"Kapsamlı görsel analizi hatası: {e}")
            return {
                'image_path': image_path,
                'user_id': user_id,
                'error': str(e),
                'status': 'error'
            }
    
    def _is_valid_image(self, image_path: str) -> bool:
        """Görsel dosyasının geçerliliğini kontrol et"""
        if not os.path.exists(image_path):
            return False
        
        _, ext = os.path.splitext(image_path.lower())
        if ext not in self.supported_formats:
            return False
        
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def _generate_image_hash(self, image_path: str) -> str:
        """Görsel için MD5 hash oluştur"""
        hash_md5 = hashlib.md5()
        with open(image_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _generate_similarity_hash(self, image_path: str) -> str:
        """Benzerlik karşılaştırması için perceptual hash"""
        try:
            import imagehash
            with Image.open(image_path) as img:
                # Resize to standard size for consistent hashing
                img = img.resize((256, 256))
                phash = imagehash.phash(img)
                return str(phash)
        except Exception as e:
            self.logger.warning(f"Similarity hash oluşturulamadı: {e}")
            return ""
    
    async def _analyze_basic_properties(self, image_path: str) -> Dict[str, Any]:
        """Temel görsel özellikleri analizi"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                format_info = img.format
                mode = img.mode
                
                # Aspect ratio
                aspect_ratio = width / height
                
                # Orientation
                if width > height:
                    orientation = 'landscape'
                elif height > width:
                    orientation = 'portrait'
                else:
                    orientation = 'square'
                
                # Resolution category
                total_pixels = width * height
                if total_pixels > 8000000:  # 8MP+
                    resolution_category = 'high'
                elif total_pixels > 2000000:  # 2MP+
                    resolution_category = 'medium'
                else:
                    resolution_category = 'low'
                
                return {
                    'dimensions': {'width': width, 'height': height},
                    'format': format_info,
                    'mode': mode,
                    'aspect_ratio': round(aspect_ratio, 2),
                    'orientation': orientation,
                    'total_pixels': total_pixels,
                    'resolution_category': resolution_category,
                    'file_size': os.path.getsize(image_path)
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    async def _analyze_colors(self, image_path: str) -> Dict[str, Any]:
        """Renk analizi"""
        try:
            with Image.open(image_path) as img:
                # RGB'ye çevir
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize for performance
                img = img.resize((200, 200))
                
                # Numpy array'e çevir
                img_array = np.array(img)
                pixels = img_array.reshape(-1, 3)
                
                # K-means ile dominant renkleri bul
                kmeans = KMeans(n_clusters=self.color_clusters, random_state=42, n_init=10)
                kmeans.fit(pixels)
                
                colors = kmeans.cluster_centers_.astype(int)
                labels = kmeans.labels_
                
                # Renk yüzdelerini hesapla
                color_percentages = []
                for i in range(self.color_clusters):
                    percentage = np.sum(labels == i) / len(labels) * 100
                    color_percentages.append({
                        'color': colors[i].tolist(),
                        'hex': '#{:02x}{:02x}{:02x}'.format(colors[i][0], colors[i][1], colors[i][2]),
                        'percentage': round(percentage, 2)
                    })
                
                # Renkleri yüzdeye göre sırala
                color_percentages.sort(key=lambda x: x['percentage'], reverse=True)
                
                # Renk çeşitliliği analizi
                color_diversity = self._calculate_color_diversity(colors)
                
                # Brightness analizi
                brightness = np.mean(pixels)
                
                # Contrast analizi
                contrast = np.std(pixels)
                
                return {
                    'dominant_colors': color_percentages,
                    'color_diversity': color_diversity,
                    'average_brightness': round(brightness, 2),
                    'contrast_level': round(contrast, 2),
                    'brightness_category': self._categorize_brightness(brightness),
                    'contrast_category': self._categorize_contrast(contrast)
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_color_diversity(self, colors: np.ndarray) -> float:
        """Renk çeşitliliğini hesapla"""
        try:
            # Renklerin birbirinden uzaklığını hesapla
            distances = []
            for i in range(len(colors)):
                for j in range(i + 1, len(colors)):
                    distance = np.linalg.norm(colors[i] - colors[j])
                    distances.append(distance)
            
            return round(np.mean(distances), 2) if distances else 0.0
        except:
            return 0.0
    
    def _categorize_brightness(self, brightness: float) -> str:
        """Parlaklık kategorisi"""
        if brightness < 85:
            return 'dark'
        elif brightness < 170:
            return 'medium'
        else:
            return 'bright'
    
    def _categorize_contrast(self, contrast: float) -> str:
        """Kontrast kategorisi"""
        if contrast < 30:
            return 'low'
        elif contrast < 60:
            return 'medium'
        else:
            return 'high'
    
    async def _detect_faces(self, image_path: str) -> Dict[str, Any]:
        """Yüz algılama ve tanıma"""
        try:
            # Görseli yükle
            image = face_recognition.load_image_file(image_path)
            
            # Yüz konumlarını bul
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                return {
                    'face_count': 0,
                    'faces': [],
                    'has_faces': False
                }
            
            # Yüz encodings'lerini çıkar
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            faces_data = []
            for i, (face_encoding, face_location) in enumerate(zip(face_encodings, face_locations)):
                top, right, bottom, left = face_location
                
                face_data = {
                    'face_id': f"face_{i}",
                    'location': {
                        'top': top,
                        'right': right,
                        'bottom': bottom,
                        'left': left
                    },
                    'size': {
                        'width': right - left,
                        'height': bottom - top
                    },
                    'encoding': face_encoding.tolist()  # Benzerlik karşılaştırması için
                }
                
                faces_data.append(face_data)
            
            return {
                'face_count': len(face_locations),
                'faces': faces_data,
                'has_faces': True,
                'face_density': len(face_locations) / (image.shape[0] * image.shape[1]) * 1000000  # faces per megapixel
            }
            
        except Exception as e:
            self.logger.warning(f"Yüz algılama hatası: {e}")
            return {
                'face_count': 0,
                'faces': [],
                'has_faces': False,
                'error': str(e)
            }
    
    async def _analyze_composition(self, image_path: str) -> Dict[str, Any]:
        """Kompozisyon analizi"""
        try:
            # OpenCV ile görsel yükle
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Görsel yüklenemedi")
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (height * width)
            
            # Rule of thirds analizi
            thirds_analysis = self._analyze_rule_of_thirds(gray)
            
            # Symmetry analizi
            symmetry_score = self._analyze_symmetry(gray)
            
            # Texture analizi
            texture_score = self._analyze_texture(gray)
            
            return {
                'edge_density': round(edge_density, 4),
                'rule_of_thirds': thirds_analysis,
                'symmetry_score': round(symmetry_score, 3),
                'texture_score': round(texture_score, 3),
                'composition_quality': self._rate_composition(edge_density, symmetry_score, texture_score)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_rule_of_thirds(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """Rule of thirds analizi"""
        try:
            height, width = gray_image.shape
            
            # Üçte bir çizgileri
            h_third1, h_third2 = height // 3, 2 * height // 3
            w_third1, w_third2 = width // 3, 2 * width // 3
            
            # Intersection points
            intersections = [
                (h_third1, w_third1), (h_third1, w_third2),
                (h_third2, w_third1), (h_third2, w_third2)
            ]
            
            # Her intersection point etrafındaki aktiviteyi kontrol et
            region_size = min(height, width) // 20
            interest_scores = []
            
            for y, x in intersections:
                y_start = max(0, y - region_size)
                y_end = min(height, y + region_size)
                x_start = max(0, x - region_size)
                x_end = min(width, x + region_size)
                
                region = gray_image[y_start:y_end, x_start:x_end]
                interest_score = np.std(region)  # Variance as interest measure
                interest_scores.append(interest_score)
            
            return {
                'intersection_scores': [round(score, 2) for score in interest_scores],
                'average_interest': round(np.mean(interest_scores), 2),
                'follows_rule': np.max(interest_scores) > np.mean(gray_image) * 0.5
            }
            
        except Exception:
            return {'error': 'Rule of thirds analizi başarısız'}
    
    def _analyze_symmetry(self, gray_image: np.ndarray) -> float:
        """Simetri analizi"""
        try:
            height, width = gray_image.shape
            
            # Vertical symmetry
            left_half = gray_image[:, :width//2]
            right_half = gray_image[:, width//2:]
            right_half_flipped = np.fliplr(right_half)
            
            # Resize to match if needed
            min_width = min(left_half.shape[1], right_half_flipped.shape[1])
            left_half = left_half[:, :min_width]
            right_half_flipped = right_half_flipped[:, :min_width]
            
            # Calculate similarity
            diff = np.abs(left_half.astype(float) - right_half_flipped.astype(float))
            symmetry_score = 1.0 - (np.mean(diff) / 255.0)
            
            return max(0.0, symmetry_score)
            
        except Exception:
            return 0.0
    
    def _analyze_texture(self, gray_image: np.ndarray) -> float:
        """Texture analizi"""
        try:
            # Local Binary Pattern benzeri basit texture measure
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            texture_response = cv2.filter2D(gray_image, -1, kernel)
            texture_score = np.std(texture_response) / 255.0
            
            return min(1.0, texture_score)
            
        except Exception:
            return 0.0
    
    def _rate_composition(self, edge_density: float, symmetry: float, texture: float) -> str:
        """Kompozisyon kalitesi değerlendirmesi"""
        score = (edge_density * 0.3 + symmetry * 0.4 + texture * 0.3)
        
        if score > 0.7:
            return 'excellent'
        elif score > 0.5:
            return 'good'
        elif score > 0.3:
            return 'average'
        else:
            return 'poor'
    
    async def _extract_visual_features(self, image_path: str) -> Dict[str, Any]:
        """Görsel özellik çıkarma (deep learning features)"""
        try:
            # Bu fonksiyon AI Core'daki embedding modelini kullanabilir
            if 'embedder' in self.ai_core.models:
                # Sentence transformer ile görsel embedding
                # Not: Bu normalde görsel için değil ama örnek olarak
                pass
            
            # Basit histogram tabanlı özellikler
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img = img.resize((224, 224))  # Standard size
                img_array = np.array(img)
                
                # Color histograms
                hist_r = np.histogram(img_array[:,:,0], bins=32, range=(0, 256))[0]
                hist_g = np.histogram(img_array[:,:,1], bins=32, range=(0, 256))[0]
                hist_b = np.histogram(img_array[:,:,2], bins=32, range=(0, 256))[0]
                
                # Normalize histograms
                hist_r = hist_r / np.sum(hist_r)
                hist_g = hist_g / np.sum(hist_g)
                hist_b = hist_b / np.sum(hist_b)
                
                return {
                    'color_histogram_r': hist_r.tolist(),
                    'color_histogram_g': hist_g.tolist(),
                    'color_histogram_b': hist_b.tolist(),
                    'feature_vector_size': len(hist_r) * 3
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    async def _analyze_quality(self, image_path: str) -> Dict[str, Any]:
        """Görsel kalitesi analizi"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Görsel yüklenemedi")
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Blur detection (Laplacian variance)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Noise estimation
            noise_score = self._estimate_noise(gray)
            
            # Dynamic range
            dynamic_range = np.max(gray) - np.min(gray)
            
            # Overall quality score
            quality_score = self._calculate_quality_score(blur_score, noise_score, dynamic_range)
            
            return {
                'blur_score': round(blur_score, 2),
                'noise_score': round(noise_score, 2),
                'dynamic_range': int(dynamic_range),
                'quality_score': round(quality_score, 2),
                'quality_category': self._categorize_quality(quality_score),
                'is_blurry': blur_score < 100,
                'is_noisy': noise_score > 0.1
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _estimate_noise(self, gray_image: np.ndarray) -> float:
        """Gürültü tahmini"""
        try:
            # Wavelet denoising approach
            H, W = gray_image.shape
            M = [[1, -2, 1],
                 [-2, 4, -2],
                 [1, -2, 1]]
            
            M = np.array(M)
            sigma = np.sum(np.sum(np.absolute(cv2.filter2D(gray_image, -1, M))))
            sigma = sigma * np.sqrt(0.5 * np.pi) / (6 * (W-2) * (H-2))
            
            return sigma / 255.0  # Normalize
            
        except Exception:
            return 0.0
    
    def _calculate_quality_score(self, blur: float, noise: float, dynamic_range: int) -> float:
        """Genel kalite skoru hesaplama"""
        # Normalize components
        blur_norm = min(1.0, blur / 500.0)  # Higher is better
        noise_norm = max(0.0, 1.0 - noise * 10)  # Lower is better
        range_norm = dynamic_range / 255.0  # Higher is better
        
        # Weighted average
        quality = (blur_norm * 0.4 + noise_norm * 0.3 + range_norm * 0.3)
        
        return quality
    
    def _categorize_quality(self, quality_score: float) -> str:
        """Kalite kategorisi"""
        if quality_score > 0.8:
            return 'excellent'
        elif quality_score > 0.6:
            return 'good'
        elif quality_score > 0.4:
            return 'average'
        else:
            return 'poor'
    
    def _suggest_categories(self, analysis: Dict[str, Any]) -> List[str]:
        """Analiz sonuçlarına göre kategori önerisi"""
        categories = []
        
        try:
            # AI analizi sonuçlarından
            if 'ai_analysis' in analysis and 'classification' in analysis['ai_analysis']:
                ai_classes = analysis['ai_analysis']['classification']
                if ai_classes and 'categories' in ai_classes:
                    for cat in ai_classes['categories'][:3]:  # Top 3
                        if cat['score'] > 0.1:
                            categories.append(cat['label'].lower())
            
            # Yüz varsa
            if analysis.get('detailed_analysis', {}).get('faces', {}).get('has_faces'):
                categories.append('people')
                categories.append('portrait')
            
            # Renk analizinden
            colors_analysis = analysis.get('detailed_analysis', {}).get('colors', {})
            if colors_analysis and 'brightness_category' in colors_analysis:
                brightness = colors_analysis['brightness_category']
                if brightness == 'dark':
                    categories.append('dark')
                    categories.append('moody')
                elif brightness == 'bright':
                    categories.append('bright')
                    categories.append('cheerful')
            
            # Kompozisyon analizinden
            composition = analysis.get('detailed_analysis', {}).get('composition', {})
            if composition and composition.get('composition_quality') == 'excellent':
                categories.append('professional')
                categories.append('high-quality')
            
            # Kalite analizinden
            quality = analysis.get('detailed_analysis', {}).get('quality', {})
            if quality:
                if quality.get('is_blurry'):
                    categories.append('blurry')
                if quality.get('quality_category') == 'excellent':
                    categories.append('high-resolution')
            
            # Duplicate'leri kaldır
            categories = list(set(categories))
            
        except Exception as e:
            self.logger.warning(f"Kategori önerisi hatası: {e}")
        
        return categories[:10]  # Maximum 10 kategori
    
    async def find_similar_images(self, image_path: str, user_id: int, similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Benzer görselleri bul"""
        try:
            # Bu görsel için similarity hash
            target_hash = self._generate_similarity_hash(image_path)
            if not target_hash:
                return []
            
            # Veritabanından kullanıcının diğer görsellerini al
            # Bu kısım veritabanı implementasyonuna bağlı
            # Şimdilik placeholder
            
            similar_images = []
            # Implementation needed based on database structure
            
            return similar_images
            
        except Exception as e:
            self.logger.error(f"Benzer görsel arama hatası: {e}")
            return []
    
    async def generate_thumbnail(self, image_path: str, thumbnail_path: str) -> bool:
        """Thumbnail oluştur"""
        try:
            with Image.open(image_path) as img:
                # Aspect ratio'yu koru
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                
                # JPEG olarak kaydet
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Thumbnail oluşturma hatası: {e}")
            return False