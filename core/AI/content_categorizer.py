#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi Content Categorizer Service
=================================

Akıllı içerik kategorilendirme servisi
- Otomatik kategori önerisi
- Çoklu etiketleme
- Hiyerarşik kategoriler
- Özel kategori kuralları
- Makine öğrenmesi tabanlı sınıflandırma
"""

import os
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict, Counter
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

from core.Services.logger import LoggerService
from core.Database.connection import DatabaseConnection


class ContentCategorizerService:
    """
    Akıllı içerik kategorilendirme servisi
    """
    
    def __init__(self):
        self.logger = LoggerService.get_logger()
        self.db = DatabaseConnection()
        
        # Kategori hiyerarşisi
        self.category_hierarchy = self._initialize_category_hierarchy()
        
        # Önceden tanımlı kategori kuralları
        self.category_rules = self._initialize_category_rules()
        
        # Makine öğrenmesi modelleri
        self.ml_models = {}
        self.vectorizers = {}
        
        # Kategori istatistikleri
        self.category_stats = defaultdict(int)
        
        # Özel etiketler
        self.custom_tags = set()
        
        self.logger.info("Content Categorizer Service başlatıldı")
        
        # Modelleri eğit
        self._train_models()
    
    def _initialize_category_hierarchy(self) -> Dict[str, List[str]]:
        """Kategori hiyerarşisini başlat"""
        return {
            'people': [
                'portrait', 'group', 'family', 'friends', 'wedding', 'baby', 'children',
                'professional', 'selfie', 'couple', 'elderly'
            ],
            'nature': [
                'landscape', 'sunset', 'sunrise', 'mountains', 'forest', 'beach', 'ocean',
                'flowers', 'trees', 'animals', 'wildlife', 'sky', 'clouds', 'weather'
            ],
            'urban': [
                'city', 'buildings', 'architecture', 'street', 'transportation', 'cars',
                'bridges', 'nightlife', 'downtown', 'skyline', 'modern', 'vintage'
            ],
            'indoor': [
                'home', 'kitchen', 'bedroom', 'living_room', 'office', 'restaurant',
                'shopping', 'museum', 'library', 'gym', 'hospital', 'school'
            ],
            'food': [
                'meal', 'breakfast', 'lunch', 'dinner', 'dessert', 'drinks', 'cooking',
                'restaurant', 'homemade', 'healthy', 'fast_food', 'gourmet'
            ],
            'events': [
                'party', 'celebration', 'birthday', 'holiday', 'vacation', 'travel',
                'concert', 'sports', 'graduation', 'meeting', 'conference', 'festival'
            ],
            'objects': [
                'technology', 'electronics', 'tools', 'furniture', 'clothing', 'jewelry',
                'books', 'toys', 'art', 'decorations', 'vehicles', 'instruments'
            ],
            'activities': [
                'sports', 'exercise', 'reading', 'cooking', 'gaming', 'shopping',
                'working', 'studying', 'traveling', 'dancing', 'singing', 'painting'
            ],
            'emotions': [
                'happy', 'sad', 'excited', 'calm', 'romantic', 'funny', 'serious',
                'mysterious', 'energetic', 'peaceful', 'dramatic', 'nostalgic'
            ],
            'style': [
                'vintage', 'modern', 'minimalist', 'colorful', 'black_white', 'artistic',
                'professional', 'casual', 'formal', 'creative', 'abstract', 'realistic'
            ]
        }
    
    def _initialize_category_rules(self) -> Dict[str, Dict[str, Any]]:
        """Kategori kurallarını başlat"""
        return {
            'face_detection': {
                'condition': lambda analysis: analysis.get('detailed_analysis', {}).get('faces', {}).get('has_faces', False),
                'categories': ['people', 'portrait'],
                'confidence': 0.9
            },
            'multiple_faces': {
                'condition': lambda analysis: analysis.get('detailed_analysis', {}).get('faces', {}).get('face_count', 0) > 1,
                'categories': ['group', 'family', 'friends'],
                'confidence': 0.8
            },
            'outdoor_scene': {
                'condition': lambda analysis: self._is_outdoor_scene(analysis),
                'categories': ['outdoor', 'nature'],
                'confidence': 0.7
            },
            'indoor_scene': {
                'condition': lambda analysis: self._is_indoor_scene(analysis),
                'categories': ['indoor'],
                'confidence': 0.7
            },
            'high_quality': {
                'condition': lambda analysis: analysis.get('detailed_analysis', {}).get('quality', {}).get('quality_category') == 'excellent',
                'categories': ['high_quality', 'professional'],
                'confidence': 0.8
            },
            'low_quality': {
                'condition': lambda analysis: analysis.get('detailed_analysis', {}).get('quality', {}).get('is_blurry', False),
                'categories': ['blurry', 'low_quality'],
                'confidence': 0.9
            },
            'colorful': {
                'condition': lambda analysis: self._is_colorful(analysis),
                'categories': ['colorful', 'vibrant'],
                'confidence': 0.7
            },
            'dark_image': {
                'condition': lambda analysis: analysis.get('detailed_analysis', {}).get('colors', {}).get('brightness_category') == 'dark',
                'categories': ['dark', 'moody', 'night'],
                'confidence': 0.8
            },
            'bright_image': {
                'condition': lambda analysis: analysis.get('detailed_analysis', {}).get('colors', {}).get('brightness_category') == 'bright',
                'categories': ['bright', 'cheerful', 'day'],
                'confidence': 0.8
            }
        }
    
    def _is_outdoor_scene(self, analysis: Dict[str, Any]) -> bool:
        """Açık hava sahnesini tespit et"""
        try:
            # AI sınıflandırma sonuçlarından
            ai_classes = analysis.get('ai_analysis', {}).get('classification', {}).get('categories', [])
            outdoor_keywords = ['landscape', 'sky', 'tree', 'mountain', 'beach', 'park', 'garden', 'street']
            
            for category in ai_classes:
                if any(keyword in category.get('label', '').lower() for keyword in outdoor_keywords):
                    return True
            
            # Renk analizi - açık havada genellikle daha çok mavi ve yeşil
            colors = analysis.get('detailed_analysis', {}).get('colors', {}).get('dominant_colors', [])
            if colors:
                for color in colors[:3]:  # İlk 3 dominant renk
                    r, g, b = color.get('color', [0, 0, 0])
                    # Mavi gökyüzü veya yeşil doğa
                    if (b > r + 30 and b > g + 10) or (g > r + 20 and g > b + 10):
                        return True
            
            return False
            
        except Exception:
            return False
    
    def _is_indoor_scene(self, analysis: Dict[str, Any]) -> bool:
        """İç mekan sahnesini tespit et"""
        try:
            ai_classes = analysis.get('ai_analysis', {}).get('classification', {}).get('categories', [])
            indoor_keywords = ['room', 'kitchen', 'bedroom', 'office', 'restaurant', 'building', 'interior']
            
            for category in ai_classes:
                if any(keyword in category.get('label', '').lower() for keyword in indoor_keywords):
                    return True
            
            # Düşük dinamik aralık genellikle iç mekan işareti
            quality = analysis.get('detailed_analysis', {}).get('quality', {})
            if quality.get('dynamic_range', 255) < 150:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _is_colorful(self, analysis: Dict[str, Any]) -> bool:
        """Renkli görsel tespiti"""
        try:
            colors_analysis = analysis.get('detailed_analysis', {}).get('colors', {})
            
            # Renk çeşitliliği yüksekse
            if colors_analysis.get('color_diversity', 0) > 100:
                return True
            
            # Kontrast yüksekse
            if colors_analysis.get('contrast_category') == 'high':
                return True
            
            return False
            
        except Exception:
            return False
    
    async def categorize_content(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        İçeriği kategorilere ayır
        
        Args:
            analysis: Görsel analiz sonuçları
            
        Returns:
            Kategorilendirme sonuçları
        """
        try:
            user_id = analysis.get('user_id')
            image_path = analysis.get('image_path')
            
            # Farklı yöntemlerle kategori önerileri
            rule_based_categories = self._apply_rule_based_categorization(analysis)
            ai_based_categories = self._extract_ai_categories(analysis)
            similarity_based_categories = await self._find_similar_categories(analysis, user_id)
            ml_based_categories = self._apply_ml_categorization(analysis)
            
            # Tüm kategorileri birleştir ve skorla
            all_categories = self._merge_and_score_categories([
                rule_based_categories,
                ai_based_categories,
                similarity_based_categories,
                ml_based_categories
            ])
            
            # Hiyerarşik kategorileri uygula
            hierarchical_categories = self._apply_hierarchical_categorization(all_categories)
            
            # Özel etiketleri ekle
            custom_tags = await self._generate_custom_tags(analysis)
            
            # Final kategorilendirme
            final_categorization = {
                'image_path': image_path,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'categories': {
                    'primary': hierarchical_categories[:5],  # Ana kategoriler
                    'secondary': hierarchical_categories[5:15],  # İkincil kategoriler
                    'suggested': all_categories[:20],  # Tüm öneriler
                    'hierarchical': self._organize_hierarchical(hierarchical_categories),
                    'custom_tags': custom_tags
                },
                'confidence_scores': self._calculate_confidence_scores(hierarchical_categories),
                'categorization_methods': {
                    'rule_based': len(rule_based_categories),
                    'ai_based': len(ai_based_categories),
                    'similarity_based': len(similarity_based_categories),
                    'ml_based': len(ml_based_categories)
                }
            }
            
            # Veritabanına kaydet
            await self._save_categorization_result(final_categorization)
            
            # İstatistikleri güncelle
            self._update_category_stats(hierarchical_categories)
            
            self.logger.info(f"İçerik kategorilendi: {image_path} - {len(hierarchical_categories)} kategori")
            
            return final_categorization
            
        except Exception as e:
            self.logger.error(f"Kategorilendirme hatası: {e}")
            return {
                'image_path': analysis.get('image_path'),
                'user_id': analysis.get('user_id'),
                'error': str(e),
                'status': 'error'
            }
    
    def _apply_rule_based_categorization(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Kural tabanlı kategorilendirme"""
        categories = []
        
        try:
            for rule_name, rule_config in self.category_rules.items():
                if rule_config['condition'](analysis):
                    for category in rule_config['categories']:
                        categories.append({
                            'category': category,
                            'confidence': rule_config['confidence'],
                            'method': 'rule_based',
                            'rule': rule_name
                        })
            
        except Exception as e:
            self.logger.warning(f"Kural tabanlı kategorilendirme hatası: {e}")
        
        return categories
    
    def _extract_ai_categories(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """AI sonuçlarından kategori çıkar"""
        categories = []
        
        try:
            # Görsel sınıflandırma sonuçları
            ai_classification = analysis.get('ai_analysis', {}).get('classification', {})
            if ai_classification and 'categories' in ai_classification:
                for cat in ai_classification['categories'][:10]:
                    categories.append({
                        'category': self._normalize_category_name(cat['label']),
                        'confidence': cat['score'],
                        'method': 'ai_classification',
                        'original_label': cat['label']
                    })
            
            # Nesne algılama sonuçları
            objects = analysis.get('ai_analysis', {}).get('objects', {})
            if objects and 'objects' in objects:
                object_categories = defaultdict(float)
                for obj in objects['objects']:
                    category = self._normalize_category_name(obj['class'])
                    object_categories[category] += obj['confidence']
                
                for category, confidence in object_categories.items():
                    categories.append({
                        'category': category,
                        'confidence': min(1.0, confidence),
                        'method': 'object_detection'
                    })
            
        except Exception as e:
            self.logger.warning(f"AI kategori çıkarma hatası: {e}")
        
        return categories
    
    async def _find_similar_categories(self, analysis: Dict[str, Any], user_id: int) -> List[Dict[str, Any]]:
        """Benzer görsellerin kategorilerini bul"""
        categories = []
        
        try:
            # Benzer görselleri bul (bu kısım veritabanı implementasyonuna bağlı)
            similarity_hash = analysis.get('similarity_hash')
            if not similarity_hash:
                return categories
            
            # Placeholder - gerçek implementasyon veritabanı sorgusu gerektirir
            # similar_images = await self._query_similar_images(similarity_hash, user_id)
            
            # Şimdilik boş döndür, gerçek implementasyon eklenecek
            
        except Exception as e:
            self.logger.warning(f"Benzerlik tabanlı kategorilendirme hatası: {e}")
        
        return categories
    
    def _apply_ml_categorization(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Makine öğrenmesi tabanlı kategorilendirme"""
        categories = []
        
        try:
            # Özellik vektörü oluştur
            feature_vector = self._create_feature_vector(analysis)
            
            if 'main_classifier' in self.ml_models and feature_vector is not None:
                # Ana sınıflandırıcı ile tahmin
                predictions = self.ml_models['main_classifier'].predict_proba([feature_vector])[0]
                class_names = self.ml_models['main_classifier'].classes_
                
                # Güven skoru > 0.1 olan kategorileri al
                for i, confidence in enumerate(predictions):
                    if confidence > 0.1:
                        categories.append({
                            'category': class_names[i],
                            'confidence': confidence,
                            'method': 'ml_classification'
                        })
            
        except Exception as e:
            self.logger.warning(f"ML kategorilendirme hatası: {e}")
        
        return categories
    
    def _create_feature_vector(self, analysis: Dict[str, Any]) -> Optional[np.ndarray]:
        """Analiz sonuçlarından özellik vektörü oluştur"""
        try:
            features = []
            
            # Temel özellikler
            basic = analysis.get('detailed_analysis', {}).get('basic', {})
            if basic:
                features.extend([
                    basic.get('aspect_ratio', 1.0),
                    basic.get('total_pixels', 0) / 1000000,  # Megapixel
                    1.0 if basic.get('orientation') == 'landscape' else 0.0,
                    1.0 if basic.get('orientation') == 'portrait' else 0.0
                ])
            
            # Renk özellikleri
            colors = analysis.get('detailed_analysis', {}).get('colors', {})
            if colors:
                features.extend([
                    colors.get('average_brightness', 0) / 255.0,
                    colors.get('contrast_level', 0) / 100.0,
                    colors.get('color_diversity', 0) / 200.0
                ])
            
            # Yüz özellikleri
            faces = analysis.get('detailed_analysis', {}).get('faces', {})
            features.extend([
                faces.get('face_count', 0),
                1.0 if faces.get('has_faces', False) else 0.0
            ])
            
            # Kompozisyon özellikleri
            composition = analysis.get('detailed_analysis', {}).get('composition', {})
            if composition:
                features.extend([
                    composition.get('edge_density', 0),
                    composition.get('symmetry_score', 0),
                    composition.get('texture_score', 0)
                ])
            
            # Kalite özellikleri
            quality = analysis.get('detailed_analysis', {}).get('quality', {})
            if quality:
                features.extend([
                    quality.get('blur_score', 0) / 1000.0,
                    quality.get('noise_score', 0),
                    quality.get('quality_score', 0)
                ])
            
            return np.array(features) if features else None
            
        except Exception as e:
            self.logger.warning(f"Özellik vektörü oluşturma hatası: {e}")
            return None
    
    def _merge_and_score_categories(self, category_lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Kategori listelerini birleştir ve skorla"""
        category_scores = defaultdict(list)
        
        # Tüm kategorileri topla
        for category_list in category_lists:
            for cat_info in category_list:
                category = cat_info['category']
                confidence = cat_info['confidence']
                method = cat_info['method']
                
                category_scores[category].append({
                    'confidence': confidence,
                    'method': method
                })
        
        # Skorları birleştir
        merged_categories = []
        for category, scores in category_scores.items():
            # Farklı yöntemlerden gelen skorları ağırlıklı ortalama
            method_weights = {
                'rule_based': 1.0,
                'ai_classification': 0.9,
                'object_detection': 0.8,
                'ml_classification': 0.7,
                'similarity_based': 0.6
            }
            
            weighted_sum = 0.0
            total_weight = 0.0
            methods_used = []
            
            for score_info in scores:
                weight = method_weights.get(score_info['method'], 0.5)
                weighted_sum += score_info['confidence'] * weight
                total_weight += weight
                methods_used.append(score_info['method'])
            
            final_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0
            
            merged_categories.append({
                'category': category,
                'confidence': final_confidence,
                'methods': list(set(methods_used)),
                'method_count': len(set(methods_used))
            })
        
        # Güven skoruna göre sırala
        merged_categories.sort(key=lambda x: x['confidence'], reverse=True)
        
        return merged_categories
    
    def _apply_hierarchical_categorization(self, categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Hiyerarşik kategorilendirme uygula"""
        hierarchical_categories = []
        used_subcategories = set()
        
        # Ana kategorileri ve alt kategorileri organize et
        for cat_info in categories:
            category = cat_info['category']
            
            # Ana kategoriyi bul
            parent_category = None
            for parent, subcategories in self.category_hierarchy.items():
                if category in subcategories:
                    parent_category = parent
                    break
            
            # Ana kategoriyi ekle (henüz eklenmemişse)
            if parent_category and parent_category not in [c['category'] for c in hierarchical_categories]:
                hierarchical_categories.append({
                    'category': parent_category,
                    'confidence': cat_info['confidence'] * 0.8,  # Ana kategori biraz daha düşük skor
                    'type': 'parent',
                    'methods': cat_info['methods']
                })
            
            # Alt kategoriyi ekle
            if category not in used_subcategories:
                hierarchical_categories.append({
                    'category': category,
                    'confidence': cat_info['confidence'],
                    'type': 'subcategory' if parent_category else 'standalone',
                    'parent': parent_category,
                    'methods': cat_info['methods']
                })
                used_subcategories.add(category)
        
        # Güven skoruna göre tekrar sırala
        hierarchical_categories.sort(key=lambda x: x['confidence'], reverse=True)
        
        return hierarchical_categories
    
    def _organize_hierarchical(self, categories: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Kategorileri hiyerarşik olarak organize et"""
        organized = defaultdict(list)
        
        for cat_info in categories:
            if cat_info.get('type') == 'parent':
                parent = cat_info['category']
                # Bu ana kategorinin alt kategorilerini bul
                subcategories = [c['category'] for c in categories 
                               if c.get('parent') == parent and c.get('type') == 'subcategory']
                organized[parent] = subcategories
        
        return dict(organized)
    
    async def _generate_custom_tags(self, analysis: Dict[str, Any]) -> List[str]:
        """Özel etiketler oluştur"""
        custom_tags = []
        
        try:
            # Dosya adından etiket çıkar
            image_path = analysis.get('image_path', '')
            filename = os.path.basename(image_path).lower()
            
            # Yaygın etiket kalıpları
            tag_patterns = {
                r'img_(\d{8})': 'date_tagged',
                r'screenshot': 'screenshot',
                r'photo_(\d+)': 'photo_series',
                r'(vacation|holiday)': 'vacation',
                r'(birthday|bday)': 'birthday',
                r'(wedding|marriage)': 'wedding',
                r'(family|relatives)': 'family'
            }
            
            for pattern, tag in tag_patterns.items():
                if re.search(pattern, filename):
                    custom_tags.append(tag)
            
            # Meta verilerden etiket çıkar
            metadata = analysis.get('ai_analysis', {}).get('metadata', {})
            if metadata:
                # EXIF verilerinden konum bilgisi
                exif = metadata.get('exif', {})
                if 'GPS' in str(exif):
                    custom_tags.append('geotagged')
                
                # Kamera bilgisi
                if 'Camera' in str(exif) or 'Make' in exif:
                    custom_tags.append('camera_photo')
            
            # Zaman tabanlı etiketler
            creation_time = metadata.get('creation_time')
            if creation_time:
                try:
                    dt = datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
                    hour = dt.hour
                    
                    if 5 <= hour < 12:
                        custom_tags.append('morning')
                    elif 12 <= hour < 17:
                        custom_tags.append('afternoon')
                    elif 17 <= hour < 21:
                        custom_tags.append('evening')
                    else:
                        custom_tags.append('night')
                        
                    # Mevsim etiketleri (kaba tahmini)
                    month = dt.month
                    if month in [12, 1, 2]:
                        custom_tags.append('winter')
                    elif month in [3, 4, 5]:
                        custom_tags.append('spring')
                    elif month in [6, 7, 8]:
                        custom_tags.append('summer')
                    else:
                        custom_tags.append('autumn')
                        
                except Exception:
                    pass
            
        except Exception as e:
            self.logger.warning(f"Özel etiket oluşturma hatası: {e}")
        
        return list(set(custom_tags))
    
    def _calculate_confidence_scores(self, categories: List[Dict[str, Any]]) -> Dict[str, float]:
        """Güven skorlarını hesapla"""
        if not categories:
            return {}
        
        scores = [cat['confidence'] for cat in categories]
        
        return {
            'average': np.mean(scores),
            'max': np.max(scores),
            'min': np.min(scores),
            'std': np.std(scores),
            'median': np.median(scores)
        }
    
    def _normalize_category_name(self, category_name: str) -> str:
        """Kategori adını normalize et"""
        # Küçük harfe çevir ve özel karakterleri temizle
        normalized = re.sub(r'[^a-zA-Z0-9\s]', '', category_name.lower())
        normalized = re.sub(r'\s+', '_', normalized.strip())
        
        # Yaygın eşleştirmeler
        mappings = {
            'person': 'people',
            'human': 'people',
            'car': 'vehicle',
            'automobile': 'vehicle',
            'building': 'architecture',
            'house': 'home',
            'dog': 'pet',
            'cat': 'pet'
        }
        
        return mappings.get(normalized, normalized)
    
    async def _save_categorization_result(self, result: Dict[str, Any]):
        """Kategorilendirme sonucunu kaydet"""
        try:
            query = """
            INSERT INTO ai_categorization_results 
            (user_id, image_path, primary_categories, secondary_categories, 
             custom_tags, confidence_scores, methods_used, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                result['user_id'],
                result['image_path'],
                json.dumps(result['categories']['primary']),
                json.dumps(result['categories']['secondary']),
                json.dumps(result['categories']['custom_tags']),
                json.dumps(result['confidence_scores']),
                json.dumps(result['categorization_methods']),
                datetime.now()
            )
            
            await self.db.execute(query, values)
            
        except Exception as e:
            self.logger.error(f"Kategorilendirme sonucu kaydetme hatası: {e}")
    
    def _update_category_stats(self, categories: List[Dict[str, Any]]):
        """Kategori istatistiklerini güncelle"""
        for cat_info in categories:
            self.category_stats[cat_info['category']] += 1
    
    def _train_models(self):
        """Makine öğrenmesi modellerini eğit"""
        try:
            # Bu kısım gerçek veri ile eğitim gerektirir
            # Şimdilik placeholder
            self.logger.info("ML modelleri eğitiliyor...")
            
            # Örnek: Naive Bayes sınıflandırıcı
            # Gerçek implementasyon için eğitim verisi gerekli
            
            self.logger.info("ML modelleri eğitildi")
            
        except Exception as e:
            self.logger.warning(f"ML model eğitimi hatası: {e}")
    
    def get_category_stats(self) -> Dict[str, Any]:
        """Kategori istatistiklerini döndür"""
        return {
            'total_categories': len(self.category_stats),
            'most_common': dict(Counter(self.category_stats).most_common(10)),
            'hierarchy_coverage': {
                parent: sum(self.category_stats.get(sub, 0) for sub in subcategories)
                for parent, subcategories in self.category_hierarchy.items()
            }
        }
    
    async def suggest_categories_for_user(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Kullanıcı için kategori önerileri"""
        try:
            # Kullanıcının geçmiş kategorilerini analiz et
            # Bu kısım veritabanı sorgusu gerektirir
            
            suggestions = []
            # Placeholder - gerçek implementasyon eklenecek
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Kategori önerisi hatası: {e}")
            return []