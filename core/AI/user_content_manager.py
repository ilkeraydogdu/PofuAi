#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi User Content Manager Service
==================================

Kullanıcı bazlı akıllı içerik yönetim servisi
- Kullanıcı profil analizi
- Kişiselleştirilmiş kategorilendirme
- İçerik önerileri
- Otomatik organizasyon
- Davranış analizi
- Akıllı filtreleme
"""

import os
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import asyncio
from dataclasses import dataclass

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from core.Services.logger import LoggerService
from core.Database.connection import DatabaseConnection


@dataclass
class UserProfile:
    """Kullanıcı profil veri sınıfı"""
    user_id: int
    preferences: Dict[str, Any]
    behavior_patterns: Dict[str, Any]
    content_stats: Dict[str, Any]
    ai_preferences: Dict[str, Any]
    last_updated: datetime


class UserContentManagerService:
    """
    Kullanıcı bazlı akıllı içerik yönetim servisi
    """
    
    def __init__(self):
        self.logger = LoggerService.get_logger()
        self.db = DatabaseConnection()
        
        # Kullanıcı profilleri cache
        self.user_profiles: Dict[int, UserProfile] = {}
        
        # Davranış analizi parametreleri
        self.behavior_window_days = 30
        self.min_images_for_analysis = 10
        
        # Kişiselleştirme modelleri
        self.personalization_models = {}
        
        # İçerik organizasyon kuralları
        self.organization_rules = self._initialize_organization_rules()
        
        self.logger.info("User Content Manager Service başlatıldı")
    
    def _initialize_organization_rules(self) -> Dict[str, Dict[str, Any]]:
        """İçerik organizasyon kurallarını başlat"""
        return {
            'date_based': {
                'enabled': True,
                'folder_format': 'YYYY/MM',
                'priority': 1
            },
            'category_based': {
                'enabled': True,
                'max_categories_per_folder': 3,
                'priority': 2
            },
            'event_based': {
                'enabled': True,
                'event_keywords': ['wedding', 'birthday', 'vacation', 'graduation'],
                'priority': 3
            },
            'quality_based': {
                'enabled': True,
                'quality_threshold': 0.7,
                'separate_low_quality': True,
                'priority': 4
            },
            'face_based': {
                'enabled': True,
                'group_by_faces': True,
                'family_detection': True,
                'priority': 5
            }
        }
    
    async def analyze_user_content(self, user_id: int) -> Dict[str, Any]:
        """
        Kullanıcının içeriklerini analiz et
        
        Args:
            user_id: Kullanıcı ID'si
            
        Returns:
            Kullanıcı içerik analizi
        """
        try:
            # Kullanıcı profilini yükle veya oluştur
            user_profile = await self._get_or_create_user_profile(user_id)
            
            # Kullanıcının görsellerini al
            user_images = await self._get_user_images(user_id)
            
            if len(user_images) < self.min_images_for_analysis:
                return {
                    'user_id': user_id,
                    'status': 'insufficient_data',
                    'message': f'En az {self.min_images_for_analysis} görsel gerekli'
                }
            
            # Paralel analizler
            analysis_tasks = [
                self._analyze_content_patterns(user_images),
                self._analyze_upload_behavior(user_images),
                self._analyze_category_preferences(user_images),
                self._analyze_quality_patterns(user_images),
                self._analyze_face_patterns(user_images),
                self._analyze_temporal_patterns(user_images)
            ]
            
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Sonuçları birleştir
            content_analysis = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'total_images': len(user_images),
                'analysis_period': self.behavior_window_days,
                'patterns': {
                    'content': results[0] if not isinstance(results[0], Exception) else {},
                    'upload_behavior': results[1] if not isinstance(results[1], Exception) else {},
                    'category_preferences': results[2] if not isinstance(results[2], Exception) else {},
                    'quality_patterns': results[3] if not isinstance(results[3], Exception) else {},
                    'face_patterns': results[4] if not isinstance(results[4], Exception) else {},
                    'temporal_patterns': results[5] if not isinstance(results[5], Exception) else {}
                }
            }
            
            # Kullanıcı profilini güncelle
            await self._update_user_profile(user_id, content_analysis)
            
            # Organizasyon önerileri oluştur
            content_analysis['organization_suggestions'] = await self._generate_organization_suggestions(
                user_id, user_images, content_analysis
            )
            
            # Kişiselleştirilmiş kategoriler öner
            content_analysis['personalized_categories'] = await self._suggest_personalized_categories(
                user_id, content_analysis
            )
            
            # Sonuçları kaydet
            await self._save_content_analysis(content_analysis)
            
            self.logger.info(f"Kullanıcı içerik analizi tamamlandı: {user_id}")
            
            return content_analysis
            
        except Exception as e:
            self.logger.error(f"Kullanıcı içerik analizi hatası: {e}")
            return {
                'user_id': user_id,
                'error': str(e),
                'status': 'error'
            }
    
    async def _get_or_create_user_profile(self, user_id: int) -> UserProfile:
        """Kullanıcı profilini al veya oluştur"""
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            # Profil güncel mi kontrol et
            if (datetime.now() - profile.last_updated).days < 1:
                return profile
        
        # Veritabanından profil yükle
        try:
            query = "SELECT * FROM user_ai_profiles WHERE user_id = %s"
            result = await self.db.fetch_one(query, (user_id,))
            
            if result:
                profile = UserProfile(
                    user_id=user_id,
                    preferences=json.loads(result['preferences']),
                    behavior_patterns=json.loads(result['behavior_patterns']),
                    content_stats=json.loads(result['content_stats']),
                    ai_preferences=json.loads(result['ai_preferences']),
                    last_updated=result['updated_at']
                )
            else:
                # Yeni profil oluştur
                profile = UserProfile(
                    user_id=user_id,
                    preferences={},
                    behavior_patterns={},
                    content_stats={},
                    ai_preferences={
                        'auto_categorize': True,
                        'quality_filter': True,
                        'face_grouping': True,
                        'duplicate_detection': True
                    },
                    last_updated=datetime.now()
                )
                
                # Veritabanına kaydet
                await self._save_user_profile(profile)
            
            self.user_profiles[user_id] = profile
            return profile
            
        except Exception as e:
            self.logger.error(f"Kullanıcı profili yükleme hatası: {e}")
            # Varsayılan profil döndür
            return UserProfile(
                user_id=user_id,
                preferences={},
                behavior_patterns={},
                content_stats={},
                ai_preferences={},
                last_updated=datetime.now()
            )
    
    async def _get_user_images(self, user_id: int) -> List[Dict[str, Any]]:
        """Kullanıcının görsellerini al"""
        try:
            # Son X gün içindeki görseller
            date_threshold = datetime.now() - timedelta(days=self.behavior_window_days)
            
            query = """
            SELECT apr.*, acr.primary_categories, acr.secondary_categories, acr.custom_tags
            FROM ai_processing_results apr
            LEFT JOIN ai_categorization_results acr ON apr.image_path = acr.image_path
            WHERE apr.user_id = %s AND apr.created_at >= %s
            ORDER BY apr.created_at DESC
            """
            
            results = await self.db.fetch_all(query, (user_id, date_threshold))
            
            images = []
            for result in results:
                image_data = {
                    'id': result['id'],
                    'user_id': result['user_id'],
                    'image_path': result['image_path'],
                    'classification': json.loads(result['classification']) if result['classification'] else {},
                    'objects': json.loads(result['objects']) if result['objects'] else {},
                    'metadata': json.loads(result['metadata']) if result['metadata'] else {},
                    'processing_time': result['processing_time'],
                    'status': result['status'],
                    'created_at': result['created_at'],
                    'primary_categories': json.loads(result['primary_categories']) if result['primary_categories'] else [],
                    'secondary_categories': json.loads(result['secondary_categories']) if result['secondary_categories'] else [],
                    'custom_tags': json.loads(result['custom_tags']) if result['custom_tags'] else []
                }
                images.append(image_data)
            
            return images
            
        except Exception as e:
            self.logger.error(f"Kullanıcı görselleri alma hatası: {e}")
            return []
    
    async def _analyze_content_patterns(self, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """İçerik desenlerini analiz et"""
        try:
            patterns = {
                'total_images': len(images),
                'successful_processing': sum(1 for img in images if img['status'] == 'success'),
                'average_processing_time': np.mean([img['processing_time'] for img in images if img['processing_time']]),
                'file_formats': Counter(),
                'resolution_distribution': Counter(),
                'orientation_distribution': Counter()
            }
            
            # Dosya formatları ve çözünürlük analizi
            for image in images:
                metadata = image.get('metadata', {})
                if metadata:
                    # Format analizi
                    format_info = metadata.get('format', 'unknown')
                    patterns['file_formats'][format_info] += 1
                    
                    # Çözünürlük analizi
                    dimensions = metadata.get('dimensions', {})
                    if dimensions:
                        width = dimensions.get('width', 0)
                        height = dimensions.get('height', 0)
                        total_pixels = width * height
                        
                        if total_pixels > 8000000:
                            res_category = 'high'
                        elif total_pixels > 2000000:
                            res_category = 'medium'
                        else:
                            res_category = 'low'
                        
                        patterns['resolution_distribution'][res_category] += 1
                        
                        # Orientation
                        if width > height:
                            orientation = 'landscape'
                        elif height > width:
                            orientation = 'portrait'
                        else:
                            orientation = 'square'
                        
                        patterns['orientation_distribution'][orientation] += 1
            
            # En yaygın içerik türleri
            all_categories = []
            for image in images:
                all_categories.extend([cat.get('category', '') for cat in image.get('primary_categories', [])])
            
            patterns['most_common_categories'] = dict(Counter(all_categories).most_common(10))
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"İçerik deseni analizi hatası: {e}")
            return {}
    
    async def _analyze_upload_behavior(self, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Yükleme davranışını analiz et"""
        try:
            behavior = {
                'upload_frequency': {},
                'peak_hours': Counter(),
                'peak_days': Counter(),
                'batch_uploads': 0,
                'single_uploads': 0
            }
            
            # Zaman bazlı analiz
            upload_dates = []
            for image in images:
                created_at = image.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    
                    upload_dates.append(created_at)
                    
                    # Saat analizi
                    behavior['peak_hours'][created_at.hour] += 1
                    
                    # Gün analizi
                    behavior['peak_days'][created_at.strftime('%A')] += 1
            
            # Yükleme sıklığı
            if upload_dates:
                upload_dates.sort()
                date_diff = (upload_dates[-1] - upload_dates[0]).days
                if date_diff > 0:
                    behavior['average_uploads_per_day'] = len(upload_dates) / date_diff
                
                # Batch upload tespiti (1 saat içinde 5+ resim)
                batch_threshold = timedelta(hours=1)
                batch_count = 0
                
                for i in range(len(upload_dates)):
                    batch_size = 1
                    for j in range(i + 1, len(upload_dates)):
                        if upload_dates[j] - upload_dates[i] <= batch_threshold:
                            batch_size += 1
                        else:
                            break
                    
                    if batch_size >= 5:
                        batch_count += 1
                
                behavior['batch_uploads'] = batch_count
                behavior['single_uploads'] = len(upload_dates) - batch_count
            
            return behavior
            
        except Exception as e:
            self.logger.error(f"Yükleme davranışı analizi hatası: {e}")
            return {}
    
    async def _analyze_category_preferences(self, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Kategori tercihlerini analiz et"""
        try:
            preferences = {
                'primary_preferences': Counter(),
                'secondary_preferences': Counter(),
                'tag_preferences': Counter(),
                'category_combinations': Counter()
            }
            
            for image in images:
                # Ana kategoriler
                primary_cats = image.get('primary_categories', [])
                for cat in primary_cats:
                    cat_name = cat.get('category', '')
                    if cat_name:
                        preferences['primary_preferences'][cat_name] += 1
                
                # İkincil kategoriler
                secondary_cats = image.get('secondary_categories', [])
                for cat in secondary_cats:
                    cat_name = cat.get('category', '')
                    if cat_name:
                        preferences['secondary_preferences'][cat_name] += 1
                
                # Özel etiketler
                custom_tags = image.get('custom_tags', [])
                for tag in custom_tags:
                    preferences['tag_preferences'][tag] += 1
                
                # Kategori kombinasyonları
                if len(primary_cats) > 1:
                    cat_names = [cat.get('category', '') for cat in primary_cats[:3]]
                    combination = tuple(sorted(cat_names))
                    preferences['category_combinations'][combination] += 1
            
            # En yaygın tercihleri al
            preferences['top_primary'] = dict(preferences['primary_preferences'].most_common(10))
            preferences['top_secondary'] = dict(preferences['secondary_preferences'].most_common(10))
            preferences['top_tags'] = dict(preferences['tag_preferences'].most_common(10))
            preferences['top_combinations'] = dict(preferences['category_combinations'].most_common(5))
            
            return preferences
            
        except Exception as e:
            self.logger.error(f"Kategori tercihi analizi hatası: {e}")
            return {}
    
    async def _analyze_quality_patterns(self, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Kalite desenlerini analiz et"""
        try:
            quality_data = {
                'quality_distribution': Counter(),
                'average_quality_score': 0.0,
                'blur_tolerance': 0.0,
                'noise_tolerance': 0.0,
                'resolution_preference': Counter()
            }
            
            quality_scores = []
            blur_scores = []
            noise_scores = []
            
            for image in images:
                # Kategorilendirme sonuçlarından kalite bilgisi
                primary_cats = image.get('primary_categories', [])
                for cat in primary_cats:
                    if cat.get('category') in ['high_quality', 'professional']:
                        quality_data['quality_distribution']['high'] += 1
                    elif cat.get('category') in ['low_quality', 'blurry']:
                        quality_data['quality_distribution']['low'] += 1
                    else:
                        quality_data['quality_distribution']['medium'] += 1
                
                # Meta verilerden kalite bilgisi
                metadata = image.get('metadata', {})
                if metadata:
                    dimensions = metadata.get('dimensions', {})
                    if dimensions:
                        width = dimensions.get('width', 0)
                        height = dimensions.get('height', 0)
                        total_pixels = width * height
                        
                        if total_pixels > 8000000:
                            quality_data['resolution_preference']['high'] += 1
                        elif total_pixels > 2000000:
                            quality_data['resolution_preference']['medium'] += 1
                        else:
                            quality_data['resolution_preference']['low'] += 1
            
            # Ortalamalar
            if quality_scores:
                quality_data['average_quality_score'] = np.mean(quality_scores)
            if blur_scores:
                quality_data['blur_tolerance'] = np.mean(blur_scores)
            if noise_scores:
                quality_data['noise_tolerance'] = np.mean(noise_scores)
            
            return quality_data
            
        except Exception as e:
            self.logger.error(f"Kalite deseni analizi hatası: {e}")
            return {}
    
    async def _analyze_face_patterns(self, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Yüz desenlerini analiz et"""
        try:
            face_patterns = {
                'face_frequency': 0.0,
                'group_preference': 0.0,
                'portrait_preference': 0.0,
                'family_content': 0.0
            }
            
            face_images = 0
            group_images = 0
            portrait_images = 0
            family_images = 0
            
            for image in images:
                primary_cats = image.get('primary_categories', [])
                categories = [cat.get('category', '') for cat in primary_cats]
                
                if 'people' in categories or 'portrait' in categories:
                    face_images += 1
                
                if 'group' in categories:
                    group_images += 1
                
                if 'portrait' in categories:
                    portrait_images += 1
                
                if 'family' in categories:
                    family_images += 1
            
            total_images = len(images)
            if total_images > 0:
                face_patterns['face_frequency'] = face_images / total_images
                face_patterns['group_preference'] = group_images / total_images
                face_patterns['portrait_preference'] = portrait_images / total_images
                face_patterns['family_content'] = family_images / total_images
            
            return face_patterns
            
        except Exception as e:
            self.logger.error(f"Yüz deseni analizi hatası: {e}")
            return {}
    
    async def _analyze_temporal_patterns(self, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Zamansal desenler analizi"""
        try:
            temporal = {
                'seasonal_patterns': Counter(),
                'monthly_distribution': Counter(),
                'time_of_day_patterns': Counter()
            }
            
            for image in images:
                # Meta verilerden zaman bilgisi
                metadata = image.get('metadata', {})
                creation_time = metadata.get('creation_time')
                
                if creation_time:
                    try:
                        dt = datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
                        
                        # Mevsimsel desen
                        month = dt.month
                        if month in [12, 1, 2]:
                            season = 'winter'
                        elif month in [3, 4, 5]:
                            season = 'spring'
                        elif month in [6, 7, 8]:
                            season = 'summer'
                        else:
                            season = 'autumn'
                        
                        temporal['seasonal_patterns'][season] += 1
                        temporal['monthly_distribution'][dt.strftime('%B')] += 1
                        
                        # Günün saati
                        hour = dt.hour
                        if 5 <= hour < 12:
                            time_period = 'morning'
                        elif 12 <= hour < 17:
                            time_period = 'afternoon'
                        elif 17 <= hour < 21:
                            time_period = 'evening'
                        else:
                            time_period = 'night'
                        
                        temporal['time_of_day_patterns'][time_period] += 1
                        
                    except Exception:
                        continue
            
            return temporal
            
        except Exception as e:
            self.logger.error(f"Zamansal desen analizi hatası: {e}")
            return {}
    
    async def _generate_organization_suggestions(self, user_id: int, images: List[Dict[str, Any]], 
                                               analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Organizasyon önerileri oluştur"""
        try:
            suggestions = []
            
            # Tarih bazlı organizasyon
            if self.organization_rules['date_based']['enabled']:
                date_suggestion = await self._suggest_date_organization(images, analysis)
                if date_suggestion:
                    suggestions.append(date_suggestion)
            
            # Kategori bazlı organizasyon
            if self.organization_rules['category_based']['enabled']:
                category_suggestion = await self._suggest_category_organization(images, analysis)
                if category_suggestion:
                    suggestions.append(category_suggestion)
            
            # Kalite bazlı organizasyon
            if self.organization_rules['quality_based']['enabled']:
                quality_suggestion = await self._suggest_quality_organization(images, analysis)
                if quality_suggestion:
                    suggestions.append(quality_suggestion)
            
            # Yüz bazlı organizasyon
            if self.organization_rules['face_based']['enabled']:
                face_suggestion = await self._suggest_face_organization(images, analysis)
                if face_suggestion:
                    suggestions.append(face_suggestion)
            
            # Önerileri prioritye göre sırala
            suggestions.sort(key=lambda x: x.get('priority', 999))
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Organizasyon önerisi oluşturma hatası: {e}")
            return []
    
    async def _suggest_date_organization(self, images: List[Dict[str, Any]], 
                                       analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Tarih bazlı organizasyon önerisi"""
        try:
            date_groups = defaultdict(list)
            
            for image in images:
                created_at = image.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    
                    folder_name = created_at.strftime('%Y/%m')
                    date_groups[folder_name].append(image['image_path'])
            
            if len(date_groups) > 1:  # Birden fazla ay varsa öner
                return {
                    'type': 'date_based',
                    'title': 'Tarih Bazlı Organizasyon',
                    'description': f'{len(date_groups)} farklı ay klasörü oluşturulabilir',
                    'folder_structure': dict(date_groups),
                    'estimated_folders': len(date_groups),
                    'priority': 1,
                    'confidence': 0.9
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Tarih organizasyon önerisi hatası: {e}")
            return None
    
    async def _suggest_category_organization(self, images: List[Dict[str, Any]], 
                                           analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Kategori bazlı organizasyon önerisi"""
        try:
            # En yaygın kategorileri al
            category_preferences = analysis.get('patterns', {}).get('category_preferences', {})
            top_categories = category_preferences.get('top_primary', {})
            
            if len(top_categories) >= 3:  # En az 3 ana kategori varsa
                category_groups = defaultdict(list)
                
                for image in images:
                    primary_cats = image.get('primary_categories', [])
                    if primary_cats:
                        main_category = primary_cats[0].get('category', 'other')
                        category_groups[main_category].append(image['image_path'])
                
                return {
                    'type': 'category_based',
                    'title': 'Kategori Bazlı Organizasyon',
                    'description': f'{len(category_groups)} kategori klasörü oluşturulabilir',
                    'folder_structure': dict(category_groups),
                    'estimated_folders': len(category_groups),
                    'priority': 2,
                    'confidence': 0.8
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Kategori organizasyon önerisi hatası: {e}")
            return None
    
    async def _suggest_quality_organization(self, images: List[Dict[str, Any]], 
                                          analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Kalite bazlı organizasyon önerisi"""
        try:
            quality_groups = {'high_quality': [], 'medium_quality': [], 'low_quality': []}
            
            for image in images:
                primary_cats = image.get('primary_categories', [])
                categories = [cat.get('category', '') for cat in primary_cats]
                
                if any(cat in ['high_quality', 'professional'] for cat in categories):
                    quality_groups['high_quality'].append(image['image_path'])
                elif any(cat in ['low_quality', 'blurry'] for cat in categories):
                    quality_groups['low_quality'].append(image['image_path'])
                else:
                    quality_groups['medium_quality'].append(image['image_path'])
            
            # Düşük kalite görseller varsa öner
            if len(quality_groups['low_quality']) > len(images) * 0.1:  # %10'dan fazla
                return {
                    'type': 'quality_based',
                    'title': 'Kalite Bazlı Organizasyon',
                    'description': f'Düşük kalite görseller ayrı klasöre taşınabilir ({len(quality_groups["low_quality"])} görsel)',
                    'folder_structure': {k: v for k, v in quality_groups.items() if v},
                    'estimated_folders': len([v for v in quality_groups.values() if v]),
                    'priority': 4,
                    'confidence': 0.7
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Kalite organizasyon önerisi hatası: {e}")
            return None
    
    async def _suggest_face_organization(self, images: List[Dict[str, Any]], 
                                       analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Yüz bazlı organizasyon önerisi"""
        try:
            face_patterns = analysis.get('patterns', {}).get('face_patterns', {})
            face_frequency = face_patterns.get('face_frequency', 0)
            
            if face_frequency > 0.3:  # %30'dan fazla yüz içeren görsel varsa
                face_groups = {'portraits': [], 'groups': [], 'family': [], 'no_faces': []}
                
                for image in images:
                    primary_cats = image.get('primary_categories', [])
                    categories = [cat.get('category', '') for cat in primary_cats]
                    
                    if 'portrait' in categories:
                        face_groups['portraits'].append(image['image_path'])
                    elif 'group' in categories:
                        face_groups['groups'].append(image['image_path'])
                    elif 'family' in categories:
                        face_groups['family'].append(image['image_path'])
                    elif 'people' not in categories:
                        face_groups['no_faces'].append(image['image_path'])
                
                return {
                    'type': 'face_based',
                    'title': 'Yüz Bazlı Organizasyon',
                    'description': 'Portre, grup ve aile fotoğrafları ayrı klasörlere organize edilebilir',
                    'folder_structure': {k: v for k, v in face_groups.items() if v},
                    'estimated_folders': len([v for v in face_groups.values() if v]),
                    'priority': 5,
                    'confidence': 0.8
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Yüz organizasyon önerisi hatası: {e}")
            return None
    
    async def _suggest_personalized_categories(self, user_id: int, 
                                             analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Kişiselleştirilmiş kategori önerileri"""
        try:
            suggestions = []
            
            # Kullanıcının en çok kullandığı kategoriler
            category_preferences = analysis.get('patterns', {}).get('category_preferences', {})
            top_categories = category_preferences.get('top_primary', {})
            
            # Özel kategori önerileri
            for category, count in top_categories.items():
                if count >= 5:  # En az 5 kez kullanılmış
                    suggestions.append({
                        'category': category,
                        'usage_count': count,
                        'suggestion_type': 'frequent_use',
                        'confidence': min(1.0, count / 20.0)  # Max 20 kullanım için 1.0
                    })
            
            # Kombinasyon önerileri
            top_combinations = category_preferences.get('top_combinations', {})
            for combination, count in top_combinations.items():
                if count >= 3:
                    suggestions.append({
                        'category': ' + '.join(combination),
                        'usage_count': count,
                        'suggestion_type': 'combination',
                        'confidence': min(1.0, count / 10.0)
                    })
            
            # Güven skoruna göre sırala
            suggestions.sort(key=lambda x: x['confidence'], reverse=True)
            
            return suggestions[:10]  # En iyi 10 öneri
            
        except Exception as e:
            self.logger.error(f"Kişiselleştirilmiş kategori önerisi hatası: {e}")
            return []
    
    async def _update_user_profile(self, user_id: int, analysis: Dict[str, Any]):
        """Kullanıcı profilini güncelle"""
        try:
            if user_id not in self.user_profiles:
                await self._get_or_create_user_profile(user_id)
            
            profile = self.user_profiles[user_id]
            
            # Profil verilerini güncelle
            profile.content_stats = analysis.get('patterns', {})
            profile.last_updated = datetime.now()
            
            # Davranış desenlerini güncelle
            upload_behavior = analysis.get('patterns', {}).get('upload_behavior', {})
            if upload_behavior:
                profile.behavior_patterns['upload_behavior'] = upload_behavior
            
            # Tercihler güncelle
            category_prefs = analysis.get('patterns', {}).get('category_preferences', {})
            if category_prefs:
                profile.preferences['categories'] = category_prefs.get('top_primary', {})
            
            # Veritabanına kaydet
            await self._save_user_profile(profile)
            
        except Exception as e:
            self.logger.error(f"Kullanıcı profili güncelleme hatası: {e}")
    
    async def _save_user_profile(self, profile: UserProfile):
        """Kullanıcı profilini kaydet"""
        try:
            query = """
            INSERT INTO user_ai_profiles 
            (user_id, preferences, behavior_patterns, content_stats, ai_preferences, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            preferences = VALUES(preferences),
            behavior_patterns = VALUES(behavior_patterns),
            content_stats = VALUES(content_stats),
            ai_preferences = VALUES(ai_preferences),
            updated_at = VALUES(updated_at)
            """
            
            values = (
                profile.user_id,
                json.dumps(profile.preferences),
                json.dumps(profile.behavior_patterns),
                json.dumps(profile.content_stats),
                json.dumps(profile.ai_preferences),
                profile.last_updated
            )
            
            await self.db.execute(query, values)
            
        except Exception as e:
            self.logger.error(f"Kullanıcı profili kaydetme hatası: {e}")
    
    async def _save_content_analysis(self, analysis: Dict[str, Any]):
        """İçerik analizini kaydet"""
        try:
            query = """
            INSERT INTO user_content_analysis 
            (user_id, total_images, analysis_period, patterns, organization_suggestions, 
             personalized_categories, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                analysis['user_id'],
                analysis['total_images'],
                analysis['analysis_period'],
                json.dumps(analysis['patterns']),
                json.dumps(analysis['organization_suggestions']),
                json.dumps(analysis['personalized_categories']),
                datetime.now()
            )
            
            await self.db.execute(query, values)
            
        except Exception as e:
            self.logger.error(f"İçerik analizi kaydetme hatası: {e}")
    
    async def get_user_recommendations(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı için öneriler al"""
        try:
            profile = await self._get_or_create_user_profile(user_id)
            
            recommendations = {
                'user_id': user_id,
                'organization_tips': [],
                'category_suggestions': [],
                'quality_improvements': [],
                'workflow_optimizations': []
            }
            
            # Son analizi al
            query = """
            SELECT * FROM user_content_analysis 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
            """
            
            result = await self.db.fetch_one(query, (user_id,))
            
            if result:
                analysis = json.loads(result['patterns'])
                
                # Organizasyon önerileri
                recommendations['organization_tips'] = json.loads(result['organization_suggestions'])
                
                # Kategori önerileri
                recommendations['category_suggestions'] = json.loads(result['personalized_categories'])
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Kullanıcı önerileri alma hatası: {e}")
            return {'user_id': user_id, 'error': str(e)}
    
    def get_user_profile_summary(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı profil özeti"""
        try:
            if user_id not in self.user_profiles:
                return {'user_id': user_id, 'status': 'not_found'}
            
            profile = self.user_profiles[user_id]
            
            return {
                'user_id': user_id,
                'last_updated': profile.last_updated.isoformat(),
                'total_categories': len(profile.preferences.get('categories', {})),
                'ai_features_enabled': sum(1 for v in profile.ai_preferences.values() if v),
                'content_summary': {
                    'total_processed': profile.content_stats.get('total_images', 0),
                    'favorite_categories': list(profile.preferences.get('categories', {}).keys())[:5]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Kullanıcı profil özeti hatası: {e}")
            return {'user_id': user_id, 'error': str(e)}