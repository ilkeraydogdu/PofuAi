#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi Smart Storage Service
===========================

Akıllı depolama sistemi servisi
- Otomatik dosya organizasyonu
- Duplicate detection
- Akıllı sıkıştırma
- Depolama optimizasyonu
- Yedekleme stratejileri
- Performans izleme
"""

import os
import shutil
import hashlib
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
import threading
from pathlib import Path
import time

import numpy as np
from PIL import Image
try:
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False
    # Mock imagehash
    class MockImageHash:
        @staticmethod
        def average_hash(image):
            return "mock_hash"
        
        @staticmethod
        def phash(image):
            return "mock_phash"
        
        @staticmethod
        def hex_to_hash(hex_str):
            class MockHash:
                def __init__(self):
                    self.hash = [0] * 64
                
                def __sub__(self, other):
                    return 0
            
            return MockHash()
    
    imagehash = MockImageHash()

from core.Services.logger import LoggerService
from core.Database.connection import DatabaseConnection


class SmartStorageService:
    """
    Akıllı depolama sistemi servisi
    """
    
    def __init__(self):
        self.logger = LoggerService.get_logger()
        self.db = DatabaseConnection()
        
        # Depolama konfigürasyonu
        self.storage_config = self._initialize_storage_config()
        
        # Dosya hash'leri cache
        self.file_hashes: Dict[str, str] = {}
        self.similarity_hashes: Dict[str, str] = {}
        
        # Duplicate detection
        self.duplicate_groups: Dict[str, List[str]] = defaultdict(list)
        
        # Depolama istatistikleri
        self.storage_stats = {
            'total_files': 0,
            'total_size': 0,
            'duplicates_found': 0,
            'space_saved': 0,
            'compression_ratio': 0.0
        }
        
        # Thread locks
        self._hash_lock = threading.Lock()
        self._stats_lock = threading.Lock()
        
        self.logger.info("Smart Storage Service başlatıldı")
    
    def _initialize_storage_config(self) -> Dict[str, Any]:
        """Depolama konfigürasyonunu başlat"""
        return {
            'base_path': os.path.join(os.getcwd(), 'storage', 'images'),
            'thumbnail_path': os.path.join(os.getcwd(), 'storage', 'thumbnails'),
            'backup_path': os.path.join(os.getcwd(), 'storage', 'backups'),
            'temp_path': os.path.join(os.getcwd(), 'storage', 'temp'),
            'organization': {
                'method': 'hybrid',  # date, category, quality, hybrid
                'create_thumbnails': True,
                'compress_originals': False,
                'max_file_size': 50 * 1024 * 1024,  # 50MB
                'allowed_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
            },
            'duplicate_detection': {
                'enabled': True,
                'similarity_threshold': 0.95,
                'hash_algorithms': ['md5', 'phash'],
                'auto_remove': False
            },
            'compression': {
                'enabled': True,
                'quality': 85,
                'progressive': True,
                'optimize': True
            },
            'backup': {
                'enabled': True,
                'frequency': 'daily',
                'retention_days': 30,
                'compress_backups': True
            }
        }
    
    async def organize_user_content(self, user_id: int, organization_method: str = 'auto') -> Dict[str, Any]:
        """
        Kullanıcı içeriğini organize et
        
        Args:
            user_id: Kullanıcı ID'si
            organization_method: Organizasyon yöntemi
            
        Returns:
            Organizasyon sonuçları
        """
        try:
            start_time = time.time()
            
            # Kullanıcının dosyalarını al
            user_files = await self._get_user_files(user_id)
            
            if not user_files:
                return {
                    'user_id': user_id,
                    'status': 'no_files',
                    'message': 'Organize edilecek dosya bulunamadı'
                }
            
            # Organizasyon planını oluştur
            organization_plan = await self._create_organization_plan(user_id, user_files, organization_method)
            
            # Duplicate detection
            duplicates = await self._detect_duplicates(user_files)
            
            # Dosyaları organize et
            organization_results = await self._execute_organization_plan(organization_plan)
            
            # Thumbnail'ları oluştur
            thumbnail_results = await self._generate_thumbnails(user_files)
            
            # Compression uygula
            compression_results = await self._apply_compression(user_files)
            
            # İstatistikleri güncelle
            await self._update_storage_stats(user_id, user_files, duplicates)
            
            # Sonuçları birleştir
            results = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'processing_time': time.time() - start_time,
                'organization': {
                    'method': organization_method,
                    'files_processed': len(user_files),
                    'folders_created': organization_results.get('folders_created', 0),
                    'files_moved': organization_results.get('files_moved', 0),
                    'errors': organization_results.get('errors', [])
                },
                'duplicates': {
                    'detected': len(duplicates),
                    'groups': duplicates,
                    'space_wasted': sum(self._get_file_size(files[0]) * (len(files) - 1) 
                                      for files in duplicates.values())
                },
                'thumbnails': {
                    'created': thumbnail_results.get('created', 0),
                    'failed': thumbnail_results.get('failed', 0)
                },
                'compression': {
                    'processed': compression_results.get('processed', 0),
                    'space_saved': compression_results.get('space_saved', 0),
                    'ratio': compression_results.get('ratio', 0.0)
                },
                'storage_stats': self._get_user_storage_stats(user_id)
            }
            
            # Sonuçları kaydet
            await self._save_organization_results(results)
            
            self.logger.info(f"Kullanıcı içeriği organize edildi: {user_id} - {len(user_files)} dosya")
            
            return results
            
        except Exception as e:
            self.logger.error(f"İçerik organizasyon hatası: {e}")
            return {
                'user_id': user_id,
                'error': str(e),
                'status': 'error'
            }
    
    async def _get_user_files(self, user_id: int) -> List[Dict[str, Any]]:
        """Kullanıcının dosyalarını al"""
        try:
            query = """
            SELECT apr.image_path, apr.created_at, apr.metadata,
                   acr.primary_categories, acr.secondary_categories
            FROM ai_processing_results apr
            LEFT JOIN ai_categorization_results acr ON apr.image_path = acr.image_path
            WHERE apr.user_id = %s AND apr.status = 'success'
            ORDER BY apr.created_at DESC
            """
            
            results = await self.db.fetch_all(query, (user_id,))
            
            files = []
            for result in results:
                if os.path.exists(result['image_path']):
                    file_info = {
                        'path': result['image_path'],
                        'created_at': result['created_at'],
                        'metadata': json.loads(result['metadata']) if result['metadata'] else {},
                        'primary_categories': json.loads(result['primary_categories']) if result['primary_categories'] else [],
                        'secondary_categories': json.loads(result['secondary_categories']) if result['secondary_categories'] else [],
                        'size': self._get_file_size(result['image_path']),
                        'hash': None  # Lazy loading
                    }
                    files.append(file_info)
            
            return files
            
        except Exception as e:
            self.logger.error(f"Kullanıcı dosyaları alma hatası: {e}")
            return []
    
    async def _create_organization_plan(self, user_id: int, files: List[Dict[str, Any]], 
                                      method: str) -> Dict[str, Any]:
        """Organizasyon planını oluştur"""
        try:
            plan = {
                'method': method,
                'user_id': user_id,
                'base_path': os.path.join(self.storage_config['base_path'], str(user_id)),
                'folders': {},
                'moves': []
            }
            
            # Otomatik yöntem seçimi
            if method == 'auto':
                method = await self._determine_best_organization_method(files)
                plan['method'] = method
            
            # Yönteme göre klasör yapısını oluştur
            if method == 'date':
                plan = await self._create_date_organization_plan(plan, files)
            elif method == 'category':
                plan = await self._create_category_organization_plan(plan, files)
            elif method == 'quality':
                plan = await self._create_quality_organization_plan(plan, files)
            elif method == 'hybrid':
                plan = await self._create_hybrid_organization_plan(plan, files)
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Organizasyon planı oluşturma hatası: {e}")
            return {'method': method, 'user_id': user_id, 'folders': {}, 'moves': []}
    
    async def _determine_best_organization_method(self, files: List[Dict[str, Any]]) -> str:
        """En iyi organizasyon yöntemini belirle"""
        try:
            # Dosya sayısı ve çeşitliliğe göre karar ver
            total_files = len(files)
            
            # Tarih çeşitliliği
            dates = set()
            for file_info in files:
                created_at = file_info.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    dates.add(created_at.strftime('%Y-%m'))
            
            # Kategori çeşitliliği
            categories = set()
            for file_info in files:
                for cat in file_info.get('primary_categories', []):
                    categories.add(cat.get('category', ''))
            
            # Karar algoritması
            if total_files > 1000:
                return 'hybrid'  # Çok dosya varsa hibrit
            elif len(dates) > 6:
                return 'date'  # 6 aydan fazla tarih aralığı varsa tarih bazlı
            elif len(categories) > 10:
                return 'category'  # 10'dan fazla kategori varsa kategori bazlı
            else:
                return 'hybrid'  # Varsayılan hibrit
                
        except Exception as e:
            self.logger.error(f"Organizasyon yöntemi belirleme hatası: {e}")
            return 'hybrid'
    
    async def _create_date_organization_plan(self, plan: Dict[str, Any], 
                                           files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tarih bazlı organizasyon planı"""
        try:
            for file_info in files:
                created_at = file_info.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    
                    # YYYY/MM formatında klasör
                    folder_name = created_at.strftime('%Y/%m')
                    folder_path = os.path.join(plan['base_path'], folder_name)
                    
                    if folder_name not in plan['folders']:
                        plan['folders'][folder_name] = {
                            'path': folder_path,
                            'files': []
                        }
                    
                    plan['folders'][folder_name]['files'].append(file_info['path'])
                    plan['moves'].append({
                        'source': file_info['path'],
                        'destination': os.path.join(folder_path, os.path.basename(file_info['path']))
                    })
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Tarih organizasyon planı hatası: {e}")
            return plan
    
    async def _create_category_organization_plan(self, plan: Dict[str, Any], 
                                               files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Kategori bazlı organizasyon planı"""
        try:
            for file_info in files:
                primary_cats = file_info.get('primary_categories', [])
                
                if primary_cats:
                    # İlk kategoriyi al
                    main_category = primary_cats[0].get('category', 'uncategorized')
                else:
                    main_category = 'uncategorized'
                
                folder_path = os.path.join(plan['base_path'], main_category)
                
                if main_category not in plan['folders']:
                    plan['folders'][main_category] = {
                        'path': folder_path,
                        'files': []
                    }
                
                plan['folders'][main_category]['files'].append(file_info['path'])
                plan['moves'].append({
                    'source': file_info['path'],
                    'destination': os.path.join(folder_path, os.path.basename(file_info['path']))
                })
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Kategori organizasyon planı hatası: {e}")
            return plan
    
    async def _create_quality_organization_plan(self, plan: Dict[str, Any], 
                                              files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Kalite bazlı organizasyon planı"""
        try:
            for file_info in files:
                # Kategorilerden kalite bilgisini çıkar
                categories = [cat.get('category', '') for cat in file_info.get('primary_categories', [])]
                
                if any(cat in ['high_quality', 'professional'] for cat in categories):
                    quality_folder = 'high_quality'
                elif any(cat in ['low_quality', 'blurry'] for cat in categories):
                    quality_folder = 'low_quality'
                else:
                    quality_folder = 'medium_quality'
                
                folder_path = os.path.join(plan['base_path'], quality_folder)
                
                if quality_folder not in plan['folders']:
                    plan['folders'][quality_folder] = {
                        'path': folder_path,
                        'files': []
                    }
                
                plan['folders'][quality_folder]['files'].append(file_info['path'])
                plan['moves'].append({
                    'source': file_info['path'],
                    'destination': os.path.join(folder_path, os.path.basename(file_info['path']))
                })
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Kalite organizasyon planı hatası: {e}")
            return plan
    
    async def _create_hybrid_organization_plan(self, plan: Dict[str, Any], 
                                             files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Hibrit organizasyon planı (tarih + kategori)"""
        try:
            for file_info in files:
                # Tarih klasörü
                created_at = file_info.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_folder = created_at.strftime('%Y/%m')
                else:
                    date_folder = 'unknown_date'
                
                # Kategori alt klasörü
                primary_cats = file_info.get('primary_categories', [])
                if primary_cats:
                    category_folder = primary_cats[0].get('category', 'uncategorized')
                else:
                    category_folder = 'uncategorized'
                
                # Hibrit yol: YYYY/MM/category
                hybrid_folder = f"{date_folder}/{category_folder}"
                folder_path = os.path.join(plan['base_path'], hybrid_folder)
                
                if hybrid_folder not in plan['folders']:
                    plan['folders'][hybrid_folder] = {
                        'path': folder_path,
                        'files': []
                    }
                
                plan['folders'][hybrid_folder]['files'].append(file_info['path'])
                plan['moves'].append({
                    'source': file_info['path'],
                    'destination': os.path.join(folder_path, os.path.basename(file_info['path']))
                })
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Hibrit organizasyon planı hatası: {e}")
            return plan
    
    async def _execute_organization_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Organizasyon planını uygula"""
        try:
            results = {
                'folders_created': 0,
                'files_moved': 0,
                'errors': []
            }
            
            # Klasörleri oluştur
            for folder_name, folder_info in plan['folders'].items():
                folder_path = folder_info['path']
                try:
                    os.makedirs(folder_path, exist_ok=True)
                    results['folders_created'] += 1
                except Exception as e:
                    results['errors'].append(f"Klasör oluşturma hatası {folder_path}: {e}")
            
            # Dosyaları taşı
            for move in plan['moves']:
                try:
                    source = move['source']
                    destination = move['destination']
                    
                    # Hedef klasörün var olduğundan emin ol
                    os.makedirs(os.path.dirname(destination), exist_ok=True)
                    
                    # Dosyayı taşı (aynı adda dosya varsa yeniden adlandır)
                    if os.path.exists(destination):
                        base, ext = os.path.splitext(destination)
                        counter = 1
                        while os.path.exists(f"{base}_{counter}{ext}"):
                            counter += 1
                        destination = f"{base}_{counter}{ext}"
                    
                    shutil.move(source, destination)
                    results['files_moved'] += 1
                    
                    # Veritabanındaki yolu güncelle
                    await self._update_file_path_in_db(source, destination)
                    
                except Exception as e:
                    results['errors'].append(f"Dosya taşıma hatası {source}: {e}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Organizasyon planı uygulama hatası: {e}")
            return {'folders_created': 0, 'files_moved': 0, 'errors': [str(e)]}
    
    async def _detect_duplicates(self, files: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Duplicate dosyaları tespit et"""
        try:
            if not self.storage_config['duplicate_detection']['enabled']:
                return {}
            
            duplicates = defaultdict(list)
            
            # MD5 hash'leri hesapla
            hash_to_files = defaultdict(list)
            
            for file_info in files:
                file_path = file_info['path']
                
                # MD5 hash hesapla
                md5_hash = await self._calculate_file_hash(file_path, 'md5')
                if md5_hash:
                    hash_to_files[md5_hash].append(file_path)
            
            # Duplicate grupları oluştur
            for hash_value, file_list in hash_to_files.items():
                if len(file_list) > 1:
                    duplicates[hash_value] = file_list
            
            # Perceptual hash ile benzer görselleri bul
            if 'phash' in self.storage_config['duplicate_detection']['hash_algorithms']:
                similar_groups = await self._find_similar_images(files)
                duplicates.update(similar_groups)
            
            return dict(duplicates)
            
        except Exception as e:
            self.logger.error(f"Duplicate detection hatası: {e}")
            return {}
    
    async def _calculate_file_hash(self, file_path: str, algorithm: str = 'md5') -> Optional[str]:
        """Dosya hash'i hesapla"""
        try:
            with self._hash_lock:
                cache_key = f"{file_path}_{algorithm}"
                if cache_key in self.file_hashes:
                    return self.file_hashes[cache_key]
            
            if algorithm == 'md5':
                hash_obj = hashlib.md5()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_obj.update(chunk)
                file_hash = hash_obj.hexdigest()
            else:
                return None
            
            with self._hash_lock:
                self.file_hashes[cache_key] = file_hash
            
            return file_hash
            
        except Exception as e:
            self.logger.error(f"Dosya hash hesaplama hatası: {e}")
            return None
    
    async def _find_similar_images(self, files: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Benzer görselleri bul (perceptual hashing)"""
        try:
            similar_groups = defaultdict(list)
            hash_to_files = defaultdict(list)
            
            for file_info in files:
                file_path = file_info['path']
                
                try:
                    with Image.open(file_path) as img:
                        # Perceptual hash hesapla
                        if IMAGEHASH_AVAILABLE:
                            phash = imagehash.phash(img)
                        else:
                            phash = "mock_phash"
                        hash_to_files[str(phash)].append(file_path)
                except Exception as e:
                    self.logger.warning(f"Perceptual hash hesaplanamadı {file_path}: {e}")
                    continue
            
            # Benzer hash'leri grupla
            threshold = self.storage_config['duplicate_detection']['similarity_threshold']
            processed_hashes = set()
            
            for hash1, files1 in hash_to_files.items():
                if hash1 in processed_hashes:
                    continue
                
                similar_files = files1.copy()
                
                for hash2, files2 in hash_to_files.items():
                    if hash1 == hash2 or hash2 in processed_hashes:
                        continue
                    
                    # Hash benzerliğini hesapla
                    try:
                        if IMAGEHASH_AVAILABLE:
                            h1 = imagehash.hex_to_hash(hash1)
                            h2 = imagehash.hex_to_hash(hash2)
                        else:
                            # Mock comparison
                            similarity = 0.8 if hash1 == hash2 else 0.2
                            if similarity >= threshold:
                                similar_files.append({
                                    'file1': files1[0],
                                    'file2': files2[0],
                                    'similarity': similarity
                                })
                            continue
                        similarity = 1.0 - (h1 - h2) / len(h1.hash) ** 2
                        
                        if similarity >= threshold:
                            similar_files.extend(files2)
                            processed_hashes.add(hash2)
                    except Exception:
                        continue
                
                if len(similar_files) > 1:
                    similar_groups[f"similar_{hash1}"] = similar_files
                
                processed_hashes.add(hash1)
            
            return dict(similar_groups)
            
        except Exception as e:
            self.logger.error(f"Benzer görsel bulma hatası: {e}")
            return {}
    
    async def _generate_thumbnails(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Thumbnail'ları oluştur"""
        try:
            if not self.storage_config['organization']['create_thumbnails']:
                return {'created': 0, 'failed': 0}
            
            results = {'created': 0, 'failed': 0}
            thumbnail_size = (256, 256)
            
            # Thumbnail klasörünü oluştur
            os.makedirs(self.storage_config['thumbnail_path'], exist_ok=True)
            
            for file_info in files:
                file_path = file_info['path']
                
                try:
                    # Thumbnail yolunu oluştur
                    filename = os.path.basename(file_path)
                    name, ext = os.path.splitext(filename)
                    thumbnail_name = f"{name}_thumb.jpg"
                    thumbnail_path = os.path.join(self.storage_config['thumbnail_path'], thumbnail_name)
                    
                    # Thumbnail zaten varsa atla
                    if os.path.exists(thumbnail_path):
                        continue
                    
                    # Thumbnail oluştur
                    with Image.open(file_path) as img:
                        # RGBA'yı RGB'ye çevir
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        
                        # Aspect ratio'yu koru
                        img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                        
                        # Kaydet
                        img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
                        results['created'] += 1
                
                except Exception as e:
                    self.logger.warning(f"Thumbnail oluşturma hatası {file_path}: {e}")
                    results['failed'] += 1
            
            return results
            
        except Exception as e:
            self.logger.error(f"Thumbnail oluşturma genel hatası: {e}")
            return {'created': 0, 'failed': 0}
    
    async def _apply_compression(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Dosyalara sıkıştırma uygula"""
        try:
            if not self.storage_config['compression']['enabled']:
                return {'processed': 0, 'space_saved': 0, 'ratio': 0.0}
            
            results = {'processed': 0, 'space_saved': 0, 'ratio': 0.0}
            quality = self.storage_config['compression']['quality']
            
            total_original_size = 0
            total_compressed_size = 0
            
            for file_info in files:
                file_path = file_info['path']
                
                try:
                    # Orijinal boyut
                    original_size = os.path.getsize(file_path)
                    
                    # Sadece büyük dosyaları sıkıştır
                    if original_size < 1024 * 1024:  # 1MB'dan küçükse atla
                        continue
                    
                    # Geçici dosya oluştur
                    temp_path = file_path + '.temp'
                    
                    with Image.open(file_path) as img:
                        # RGBA'yı RGB'ye çevir
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        
                        # Sıkıştırılmış halde kaydet
                        img.save(temp_path, 'JPEG', 
                                quality=quality,
                                optimize=self.storage_config['compression']['optimize'],
                                progressive=self.storage_config['compression']['progressive'])
                    
                    # Yeni boyut
                    compressed_size = os.path.getsize(temp_path)
                    
                    # Eğer sıkıştırma faydalıysa (en az %10 tasarruf) uygula
                    if compressed_size < original_size * 0.9:
                        shutil.move(temp_path, file_path)
                        
                        total_original_size += original_size
                        total_compressed_size += compressed_size
                        results['processed'] += 1
                    else:
                        # Faydalı değilse geçici dosyayı sil
                        os.remove(temp_path)
                
                except Exception as e:
                    self.logger.warning(f"Sıkıştırma hatası {file_path}: {e}")
                    # Geçici dosyayı temizle
                    temp_path = file_path + '.temp'
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            
            # İstatistikleri hesapla
            if total_original_size > 0:
                results['space_saved'] = total_original_size - total_compressed_size
                results['ratio'] = total_compressed_size / total_original_size
            
            return results
            
        except Exception as e:
            self.logger.error(f"Sıkıştırma genel hatası: {e}")
            return {'processed': 0, 'space_saved': 0, 'ratio': 0.0}
    
    def _get_file_size(self, file_path: str) -> int:
        """Dosya boyutunu al"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0
    
    async def _update_file_path_in_db(self, old_path: str, new_path: str):
        """Veritabanındaki dosya yolunu güncelle"""
        try:
            # AI processing results tablosunu güncelle
            query1 = "UPDATE ai_processing_results SET image_path = %s WHERE image_path = %s"
            await self.db.execute(query1, (new_path, old_path))
            
            # AI categorization results tablosunu güncelle
            query2 = "UPDATE ai_categorization_results SET image_path = %s WHERE image_path = %s"
            await self.db.execute(query2, (new_path, old_path))
            
        except Exception as e:
            self.logger.error(f"Veritabanı yol güncelleme hatası: {e}")
    
    async def _update_storage_stats(self, user_id: int, files: List[Dict[str, Any]], 
                                  duplicates: Dict[str, List[str]]):
        """Depolama istatistiklerini güncelle"""
        try:
            with self._stats_lock:
                # Toplam dosya sayısı ve boyutu
                total_size = sum(file_info['size'] for file_info in files)
                
                # Duplicate istatistikleri
                duplicate_count = sum(len(file_list) - 1 for file_list in duplicates.values())
                
                # İstatistikleri güncelle
                self.storage_stats.update({
                    'total_files': len(files),
                    'total_size': total_size,
                    'duplicates_found': duplicate_count
                })
            
            # Kullanıcı bazlı istatistikleri kaydet
            await self._save_user_storage_stats(user_id, {
                'total_files': len(files),
                'total_size': total_size,
                'duplicates': duplicate_count,
                'last_updated': datetime.now()
            })
            
        except Exception as e:
            self.logger.error(f"İstatistik güncelleme hatası: {e}")
    
    def _get_user_storage_stats(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı depolama istatistiklerini al"""
        try:
            # Bu kısım cache'den veya veritabanından alınabilir
            return {
                'user_id': user_id,
                'total_files': self.storage_stats.get('total_files', 0),
                'total_size': self.storage_stats.get('total_size', 0),
                'duplicates_found': self.storage_stats.get('duplicates_found', 0),
                'space_saved': self.storage_stats.get('space_saved', 0)
            }
        except Exception as e:
            self.logger.error(f"Kullanıcı istatistikleri alma hatası: {e}")
            return {}
    
    async def _save_organization_results(self, results: Dict[str, Any]):
        """Organizasyon sonuçlarını kaydet"""
        try:
            query = """
            INSERT INTO storage_organization_results 
            (user_id, method, files_processed, folders_created, files_moved, 
             duplicates_detected, space_saved, processing_time, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                results['user_id'],
                results['organization']['method'],
                results['organization']['files_processed'],
                results['organization']['folders_created'],
                results['organization']['files_moved'],
                results['duplicates']['detected'],
                results['compression']['space_saved'],
                results['processing_time'],
                datetime.now()
            )
            
            await self.db.execute(query, values)
            
        except Exception as e:
            self.logger.error(f"Organizasyon sonuçları kaydetme hatası: {e}")
    
    async def _save_user_storage_stats(self, user_id: int, stats: Dict[str, Any]):
        """Kullanıcı depolama istatistiklerini kaydet"""
        try:
            query = """
            INSERT INTO user_storage_stats 
            (user_id, total_files, total_size, duplicates, last_updated)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            total_files = VALUES(total_files),
            total_size = VALUES(total_size),
            duplicates = VALUES(duplicates),
            last_updated = VALUES(last_updated)
            """
            
            values = (
                user_id,
                stats['total_files'],
                stats['total_size'],
                stats['duplicates'],
                stats['last_updated']
            )
            
            await self.db.execute(query, values)
            
        except Exception as e:
            self.logger.error(f"Kullanıcı istatistikleri kaydetme hatası: {e}")
    
    async def cleanup_duplicates(self, user_id: int, auto_remove: bool = False) -> Dict[str, Any]:
        """Duplicate dosyaları temizle"""
        try:
            # Kullanıcının dosyalarını al
            user_files = await self._get_user_files(user_id)
            
            # Duplicate'leri tespit et
            duplicates = await self._detect_duplicates(user_files)
            
            cleanup_results = {
                'user_id': user_id,
                'duplicates_found': len(duplicates),
                'files_removed': 0,
                'space_freed': 0,
                'groups': []
            }
            
            for group_id, file_list in duplicates.items():
                if len(file_list) > 1:
                    # İlk dosyayı koru, diğerlerini sil
                    keep_file = file_list[0]
                    remove_files = file_list[1:]
                    
                    group_info = {
                        'group_id': group_id,
                        'keep': keep_file,
                        'remove': remove_files,
                        'space_freed': 0
                    }
                    
                    if auto_remove:
                        for remove_file in remove_files:
                            try:
                                file_size = self._get_file_size(remove_file)
                                os.remove(remove_file)
                                
                                # Veritabanından da kaldır
                                await self._remove_file_from_db(remove_file)
                                
                                cleanup_results['files_removed'] += 1
                                cleanup_results['space_freed'] += file_size
                                group_info['space_freed'] += file_size
                                
                            except Exception as e:
                                self.logger.error(f"Duplicate dosya silme hatası {remove_file}: {e}")
                    
                    cleanup_results['groups'].append(group_info)
            
            # Sonuçları kaydet
            await self._save_cleanup_results(cleanup_results)
            
            return cleanup_results
            
        except Exception as e:
            self.logger.error(f"Duplicate temizleme hatası: {e}")
            return {
                'user_id': user_id,
                'error': str(e),
                'status': 'error'
            }
    
    async def _remove_file_from_db(self, file_path: str):
        """Dosyayı veritabanından kaldır"""
        try:
            # AI processing results'tan sil
            query1 = "DELETE FROM ai_processing_results WHERE image_path = %s"
            await self.db.execute(query1, (file_path,))
            
            # AI categorization results'tan sil
            query2 = "DELETE FROM ai_categorization_results WHERE image_path = %s"
            await self.db.execute(query2, (file_path,))
            
        except Exception as e:
            self.logger.error(f"Veritabanından dosya kaldırma hatası: {e}")
    
    async def _save_cleanup_results(self, results: Dict[str, Any]):
        """Temizleme sonuçlarını kaydet"""
        try:
            query = """
            INSERT INTO storage_cleanup_results 
            (user_id, duplicates_found, files_removed, space_freed, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            values = (
                results['user_id'],
                results['duplicates_found'],
                results['files_removed'],
                results['space_freed'],
                datetime.now()
            )
            
            await self.db.execute(query, values)
            
        except Exception as e:
            self.logger.error(f"Temizleme sonuçları kaydetme hatası: {e}")
    
    def get_storage_summary(self) -> Dict[str, Any]:
        """Depolama özeti"""
        try:
            return {
                'total_files': self.storage_stats['total_files'],
                'total_size_mb': self.storage_stats['total_size'] / (1024 * 1024),
                'duplicates_found': self.storage_stats['duplicates_found'],
                'space_saved_mb': self.storage_stats['space_saved'] / (1024 * 1024),
                'compression_ratio': self.storage_stats['compression_ratio'],
                'storage_efficiency': 1.0 - (self.storage_stats['duplicates_found'] / max(1, self.storage_stats['total_files']))
            }
        except Exception as e:
            self.logger.error(f"Depolama özeti hatası: {e}")
            return {}
    
    async def optimize_storage(self, user_id: int) -> Dict[str, Any]:
        """Depolama optimizasyonu yap"""
        try:
            # Tüm optimizasyon işlemlerini sırayla çalıştır
            organization_results = await self.organize_user_content(user_id, 'auto')
            cleanup_results = await self.cleanup_duplicates(user_id, auto_remove=True)
            
            optimization_summary = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'organization': organization_results,
                'cleanup': cleanup_results,
                'total_space_saved': (
                    organization_results.get('compression', {}).get('space_saved', 0) +
                    cleanup_results.get('space_freed', 0)
                ),
                'optimization_score': self._calculate_optimization_score(organization_results, cleanup_results)
            }
            
            return optimization_summary
            
        except Exception as e:
            self.logger.error(f"Depolama optimizasyonu hatası: {e}")
            return {
                'user_id': user_id,
                'error': str(e),
                'status': 'error'
            }
    
    def _calculate_optimization_score(self, org_results: Dict[str, Any], 
                                    cleanup_results: Dict[str, Any]) -> float:
        """Optimizasyon skorunu hesapla"""
        try:
            score = 0.0
            
            # Organizasyon skoru (0-40 puan)
            files_organized = org_results.get('organization', {}).get('files_moved', 0)
            if files_organized > 0:
                score += min(40, files_organized / 10)  # Her 10 dosya için 1 puan, max 40
            
            # Duplicate temizleme skoru (0-30 puan)
            files_removed = cleanup_results.get('files_removed', 0)
            if files_removed > 0:
                score += min(30, files_removed * 2)  # Her duplicate için 2 puan, max 30
            
            # Sıkıştırma skoru (0-30 puan)
            compression_ratio = org_results.get('compression', {}).get('ratio', 1.0)
            if compression_ratio < 1.0:
                score += (1.0 - compression_ratio) * 30  # Sıkıştırma oranına göre puan
            
            return min(100.0, score)  # Max 100 puan
            
        except Exception as e:
            self.logger.error(f"Optimizasyon skoru hesaplama hatası: {e}")
            return 0.0