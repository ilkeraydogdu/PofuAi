#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PofuAi Learning Engine
======================

AI öğrenme ve kişiselleştirme motoru
- Kullanıcı davranışlarını öğrenme
- Kişiselleştirilmiş öneriler
- Model fine-tuning
- Feedback loop
"""

import os
import json
import pickle
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

from core.Services.logger import LoggerService
from core.Database.connection import DatabaseConnection


class UserBehaviorDataset(Dataset):
    """Kullanıcı davranış dataset'i"""
    
    def __init__(self, user_data: List[Dict[str, Any]]):
        self.data = user_data
        self.prepare_features()
    
    def prepare_features(self):
        """Özellikleri hazırla"""
        self.features = []
        self.labels = []
        
        for item in self.data:
            # Özellik vektörü oluştur
            feature_vector = self._extract_features(item)
            self.features.append(feature_vector)
            
            # Etiket (örn: kullanıcının tercih ettiği kategori)
            self.labels.append(item.get('preferred_category', 0))
    
    def _extract_features(self, item: Dict[str, Any]) -> np.ndarray:
        """Özellik çıkarma"""
        features = []
        
        # Zaman özellikleri
        hour = item.get('interaction_hour', 0)
        day_of_week = item.get('day_of_week', 0)
        features.extend([hour / 24, day_of_week / 7])
        
        # İçerik özellikleri
        content_type = item.get('content_type_encoded', 0)
        interaction_type = item.get('interaction_type_encoded', 0)
        features.extend([content_type, interaction_type])
        
        # Davranış özellikleri
        view_duration = item.get('view_duration', 0) / 300  # Normalize to 5 min
        click_rate = item.get('click_rate', 0)
        features.extend([view_duration, click_rate])
        
        return np.array(features, dtype=np.float32)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return torch.tensor(self.features[idx]), torch.tensor(self.labels[idx])


class PersonalizationModel(nn.Module):
    """Kişiselleştirme için neural network modeli"""
    
    def __init__(self, input_size: int, hidden_size: int = 64, num_classes: int = 10):
        super(PersonalizationModel, self).__init__()
        
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.2)
        
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.2)
        
        self.fc3 = nn.Linear(hidden_size // 2, num_classes)
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.dropout1(x)
        
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.dropout2(x)
        
        x = self.fc3(x)
        return x
    
    def predict_proba(self, x):
        """Olasılık tahmini"""
        with torch.no_grad():
            logits = self.forward(x)
            return self.softmax(logits)


class AILearningEngine:
    """
    AI öğrenme motoru
    """
    
    def __init__(self):
        self.logger = LoggerService.get_logger()
        self.db = DatabaseConnection()
        
        # Model depolama
        self.models_dir = "storage/ai_models"
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Kullanıcı modelleri
        self.user_models: Dict[int, PersonalizationModel] = {}
        
        # Öğrenme parametreleri
        self.learning_config = {
            'batch_size': 32,
            'learning_rate': 0.001,
            'epochs': 10,
            'min_data_points': 50,
            'update_frequency_days': 7
        }
        
        # Öneri motoru
        self.recommendation_engine = RecommendationEngine(self.db)
        
        # Feedback processor
        self.feedback_processor = FeedbackProcessor(self.db)
        
        self.logger.info("AI Learning Engine başlatıldı")
    
    async def learn_user_behavior(self, user_id: int) -> Dict[str, Any]:
        """
        Kullanıcı davranışlarını öğren
        
        Args:
            user_id: Kullanıcı ID
            
        Returns:
            Öğrenme sonuçları
        """
        try:
            # Kullanıcı verilerini al
            user_data = await self._get_user_interaction_data(user_id)
            
            if len(user_data) < self.learning_config['min_data_points']:
                return {
                    'success': False,
                    'message': 'Yeterli veri yok',
                    'data_points': len(user_data),
                    'required': self.learning_config['min_data_points']
                }
            
            # Dataset oluştur
            dataset = UserBehaviorDataset(user_data)
            dataloader = DataLoader(
                dataset, 
                batch_size=self.learning_config['batch_size'],
                shuffle=True
            )
            
            # Model oluştur veya yükle
            model = self._get_or_create_user_model(user_id, input_size=6)
            
            # Eğitim
            optimizer = optim.Adam(model.parameters(), lr=self.learning_config['learning_rate'])
            criterion = nn.CrossEntropyLoss()
            
            model.train()
            total_loss = 0
            
            for epoch in range(self.learning_config['epochs']):
                epoch_loss = 0
                
                for batch_features, batch_labels in dataloader:
                    optimizer.zero_grad()
                    
                    outputs = model(batch_features)
                    loss = criterion(outputs, batch_labels)
                    
                    loss.backward()
                    optimizer.step()
                    
                    epoch_loss += loss.item()
                
                total_loss += epoch_loss
                self.logger.debug(f"Epoch {epoch+1}/{self.learning_config['epochs']}, Loss: {epoch_loss:.4f}")
            
            # Modeli kaydet
            self._save_user_model(user_id, model)
            
            # Öğrenme istatistikleri
            avg_loss = total_loss / self.learning_config['epochs']
            
            # Kullanıcı profili güncelle
            await self._update_user_ai_profile(user_id, {
                'last_training': datetime.now().isoformat(),
                'model_performance': {
                    'avg_loss': avg_loss,
                    'data_points': len(user_data),
                    'epochs': self.learning_config['epochs']
                }
            })
            
            return {
                'success': True,
                'model_updated': True,
                'performance': {
                    'avg_loss': avg_loss,
                    'data_points': len(user_data)
                },
                'next_update': (datetime.now() + timedelta(days=self.learning_config['update_frequency_days'])).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Kullanıcı davranış öğrenme hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_personalized_recommendations(self, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kişiselleştirilmiş öneriler al
        
        Args:
            user_id: Kullanıcı ID
            context: Bağlam bilgileri (zaman, konum, vb.)
            
        Returns:
            Öneriler
        """
        try:
            # Kullanıcı modeli var mı kontrol et
            if user_id not in self.user_models:
                self._load_user_model(user_id)
            
            if user_id in self.user_models:
                # Model bazlı öneriler
                model = self.user_models[user_id]
                
                # Mevcut bağlamı özellik vektörüne dönüştür
                feature_vector = self._context_to_features(context)
                feature_tensor = torch.tensor(feature_vector, dtype=torch.float32).unsqueeze(0)
                
                # Tahmin yap
                predictions = model.predict_proba(feature_tensor)
                top_categories = torch.topk(predictions, k=5).indices[0].tolist()
                
                # Kategorilere göre öneriler al
                recommendations = await self.recommendation_engine.get_recommendations(
                    user_id=user_id,
                    preferred_categories=top_categories,
                    context=context
                )
            else:
                # Fallback: Genel öneriler
                recommendations = await self.recommendation_engine.get_general_recommendations(
                    user_id=user_id,
                    context=context
                )
            
            return {
                'success': True,
                'recommendations': recommendations,
                'personalization_level': 'high' if user_id in self.user_models else 'low',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Kişiselleştirilmiş öneri hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_user_feedback(self, user_id: int, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kullanıcı geri bildirimini işle
        
        Args:
            user_id: Kullanıcı ID
            feedback_data: Geri bildirim verileri
            
        Returns:
            İşlem sonucu
        """
        try:
            # Geri bildirimi kaydet
            feedback_id = await self.feedback_processor.save_feedback(user_id, feedback_data)
            
            # Geri bildirim türüne göre işlem
            feedback_type = feedback_data.get('type')
            
            if feedback_type == 'rating':
                # Puanlama geri bildirimi
                await self._process_rating_feedback(user_id, feedback_data)
                
            elif feedback_type == 'preference':
                # Tercih geri bildirimi
                await self._process_preference_feedback(user_id, feedback_data)
                
            elif feedback_type == 'correction':
                # Düzeltme geri bildirimi
                await self._process_correction_feedback(user_id, feedback_data)
            
            # Model güncelleme gerekiyor mu kontrol et
            if await self._should_update_model(user_id):
                asyncio.create_task(self.learn_user_behavior(user_id))
            
            return {
                'success': True,
                'feedback_id': feedback_id,
                'processed': True,
                'message': 'Geri bildiriminiz alındı ve işlendi'
            }
            
        except Exception as e:
            self.logger.error(f"Geri bildirim işleme hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_user_patterns(self, user_id: int) -> Dict[str, Any]:
        """
        Kullanıcı desenlerini analiz et
        
        Args:
            user_id: Kullanıcı ID
            
        Returns:
            Desen analizi
        """
        try:
            # Kullanıcı etkileşim verilerini al
            interactions = await self._get_user_interaction_data(user_id, days=30)
            
            if not interactions:
                return {
                    'success': False,
                    'message': 'Analiz için yeterli veri yok'
                }
            
            # Zaman desenleri
            time_patterns = self._analyze_time_patterns(interactions)
            
            # İçerik tercihleri
            content_preferences = self._analyze_content_preferences(interactions)
            
            # Davranış kümeleri
            behavior_clusters = self._analyze_behavior_clusters(interactions)
            
            # Trend analizi
            trends = self._analyze_trends(interactions)
            
            return {
                'success': True,
                'patterns': {
                    'time_patterns': time_patterns,
                    'content_preferences': content_preferences,
                    'behavior_clusters': behavior_clusters,
                    'trends': trends
                },
                'analysis_period': '30 days',
                'data_points': len(interactions)
            }
            
        except Exception as e:
            self.logger.error(f"Kullanıcı desen analizi hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Yardımcı metodlar
    async def _get_user_interaction_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Kullanıcı etkileşim verilerini al"""
        query = """
            SELECT 
                interaction_type,
                interaction_data,
                response_time,
                created_at,
                HOUR(created_at) as interaction_hour,
                DAYOFWEEK(created_at) as day_of_week
            FROM user_ai_interactions
            WHERE user_id = %s
            AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ORDER BY created_at DESC
        """
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (user_id, days))
            results = cursor.fetchall()
            
            # JSON verilerini parse et
            for result in results:
                if result['interaction_data']:
                    result['interaction_data'] = json.loads(result['interaction_data'])
            
            return results
    
    def _get_or_create_user_model(self, user_id: int, input_size: int) -> PersonalizationModel:
        """Kullanıcı modelini al veya oluştur"""
        if user_id in self.user_models:
            return self.user_models[user_id]
        
        # Kayıtlı model var mı kontrol et
        model_path = os.path.join(self.models_dir, f"user_{user_id}_model.pth")
        
        if os.path.exists(model_path):
            model = PersonalizationModel(input_size)
            model.load_state_dict(torch.load(model_path))
            self.user_models[user_id] = model
            return model
        
        # Yeni model oluştur
        model = PersonalizationModel(input_size)
        self.user_models[user_id] = model
        return model
    
    def _save_user_model(self, user_id: int, model: PersonalizationModel):
        """Kullanıcı modelini kaydet"""
        model_path = os.path.join(self.models_dir, f"user_{user_id}_model.pth")
        torch.save(model.state_dict(), model_path)
        self.logger.info(f"Kullanıcı modeli kaydedildi: {user_id}")
    
    def _load_user_model(self, user_id: int) -> bool:
        """Kullanıcı modelini yükle"""
        model_path = os.path.join(self.models_dir, f"user_{user_id}_model.pth")
        
        if os.path.exists(model_path):
            model = PersonalizationModel(input_size=6)
            model.load_state_dict(torch.load(model_path))
            self.user_models[user_id] = model
            return True
        
        return False
    
    def _context_to_features(self, context: Dict[str, Any]) -> np.ndarray:
        """Bağlamı özellik vektörüne dönüştür"""
        features = []
        
        # Zaman özellikleri
        now = datetime.now()
        features.append(now.hour / 24)
        features.append(now.weekday() / 7)
        
        # Bağlam özellikleri
        features.append(context.get('content_type_encoded', 0))
        features.append(context.get('interaction_type_encoded', 0))
        features.append(context.get('session_duration', 0) / 300)
        features.append(context.get('previous_interactions', 0) / 10)
        
        return np.array(features, dtype=np.float32)
    
    async def _update_user_ai_profile(self, user_id: int, profile_data: Dict[str, Any]):
        """Kullanıcı AI profilini güncelle"""
        query = """
            INSERT INTO user_ai_profiles (user_id, ai_preferences, updated_at)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE
            ai_preferences = JSON_MERGE_PATCH(ai_preferences, VALUES(ai_preferences)),
            updated_at = NOW()
        """
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id, json.dumps(profile_data)))
            conn.commit()
    
    async def _should_update_model(self, user_id: int) -> bool:
        """Model güncellenmeli mi kontrol et"""
        # Son güncelleme zamanını kontrol et
        query = """
            SELECT JSON_EXTRACT(ai_preferences, '$.last_training') as last_training
            FROM user_ai_profiles
            WHERE user_id = %s
        """
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result and result['last_training']:
                last_training = datetime.fromisoformat(result['last_training'].strip('"'))
                days_since = (datetime.now() - last_training).days
                return days_since >= self.learning_config['update_frequency_days']
        
        return True
    
    def _analyze_time_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Zaman desenlerini analiz et"""
        hour_distribution = {}
        day_distribution = {}
        
        for interaction in interactions:
            hour = interaction['interaction_hour']
            day = interaction['day_of_week']
            
            hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
            day_distribution[day] = day_distribution.get(day, 0) + 1
        
        # En aktif saatler
        peak_hours = sorted(hour_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # En aktif günler
        peak_days = sorted(day_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'peak_hours': [h for h, _ in peak_hours],
            'peak_days': [d for d, _ in peak_days],
            'hour_distribution': hour_distribution,
            'day_distribution': day_distribution
        }
    
    def _analyze_content_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """İçerik tercihlerini analiz et"""
        content_types = {}
        interaction_types = {}
        
        for interaction in interactions:
            # İçerik tipi
            if interaction['interaction_data']:
                content_type = interaction['interaction_data'].get('content_type', 'unknown')
                content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # Etkileşim tipi
            int_type = interaction['interaction_type']
            interaction_types[int_type] = interaction_types.get(int_type, 0) + 1
        
        return {
            'preferred_content_types': sorted(content_types.items(), key=lambda x: x[1], reverse=True),
            'interaction_distribution': interaction_types
        }
    
    def _analyze_behavior_clusters(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Davranış kümelerini analiz et"""
        if len(interactions) < 10:
            return {'clusters': [], 'message': 'Kümeleme için yeterli veri yok'}
        
        # Özellik vektörleri oluştur
        features = []
        for interaction in interactions:
            feature = [
                interaction['interaction_hour'] / 24,
                interaction['day_of_week'] / 7,
                interaction.get('response_time', 0) / 1000
            ]
            features.append(feature)
        
        # K-means kümeleme
        n_clusters = min(3, len(interactions) // 10)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(features)
        
        # Küme özelliklerini analiz et
        cluster_info = []
        for i in range(n_clusters):
            cluster_indices = np.where(clusters == i)[0]
            cluster_features = [features[idx] for idx in cluster_indices]
            
            avg_hour = np.mean([f[0] * 24 for f in cluster_features])
            avg_day = np.mean([f[1] * 7 for f in cluster_features])
            
            cluster_info.append({
                'cluster_id': i,
                'size': len(cluster_indices),
                'avg_hour': round(avg_hour, 1),
                'avg_day': round(avg_day, 1),
                'description': self._describe_cluster(avg_hour, avg_day)
            })
        
        return {
            'num_clusters': n_clusters,
            'clusters': cluster_info
        }
    
    def _describe_cluster(self, avg_hour: float, avg_day: float) -> str:
        """Küme açıklaması oluştur"""
        # Saat açıklaması
        if avg_hour < 6:
            time_desc = "Gece"
        elif avg_hour < 12:
            time_desc = "Sabah"
        elif avg_hour < 18:
            time_desc = "Öğleden sonra"
        else:
            time_desc = "Akşam"
        
        # Gün açıklaması
        if avg_day < 2:
            day_desc = "Hafta başı"
        elif avg_day < 5:
            day_desc = "Hafta içi"
        else:
            day_desc = "Hafta sonu"
        
        return f"{day_desc} {time_desc} kullanıcısı"
    
    def _analyze_trends(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Trend analizi"""
        # Günlük etkileşim sayısı
        daily_counts = {}
        
        for interaction in interactions:
            date = interaction['created_at'].date()
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        # Trend hesaplama (basit linear regression)
        if len(daily_counts) > 7:
            dates = sorted(daily_counts.keys())
            counts = [daily_counts[d] for d in dates]
            
            # Basit trend: Son 7 gün vs önceki 7 gün
            recent_avg = np.mean(counts[-7:])
            previous_avg = np.mean(counts[-14:-7]) if len(counts) > 14 else np.mean(counts[:-7])
            
            trend = "increasing" if recent_avg > previous_avg else "decreasing"
            trend_percentage = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
        else:
            trend = "insufficient_data"
            trend_percentage = 0
        
        return {
            'activity_trend': trend,
            'trend_percentage': round(trend_percentage, 1),
            'daily_average': round(np.mean(list(daily_counts.values())), 1) if daily_counts else 0
        }
    
    async def _process_rating_feedback(self, user_id: int, feedback_data: Dict[str, Any]):
        """Puanlama geri bildirimini işle"""
        # Puanlama verilerini güncelle
        rating = feedback_data.get('rating')
        item_id = feedback_data.get('item_id')
        item_type = feedback_data.get('item_type')
        
        # Kullanıcı tercihlerini güncelle
        if rating >= 4:  # Pozitif geri bildirim
            await self._update_positive_preference(user_id, item_type, item_id)
        elif rating <= 2:  # Negatif geri bildirim
            await self._update_negative_preference(user_id, item_type, item_id)
    
    async def _process_preference_feedback(self, user_id: int, feedback_data: Dict[str, Any]):
        """Tercih geri bildirimini işle"""
        preference_type = feedback_data.get('preference_type')
        preference_value = feedback_data.get('preference_value')
        
        # Kullanıcı tercihlerini güncelle
        await self._update_user_preference(user_id, preference_type, preference_value)
    
    async def _process_correction_feedback(self, user_id: int, feedback_data: Dict[str, Any]):
        """Düzeltme geri bildirimini işle"""
        # Model düzeltme verilerini kaydet
        correction_type = feedback_data.get('correction_type')
        original_value = feedback_data.get('original_value')
        corrected_value = feedback_data.get('corrected_value')
        
        # Eğitim verilerine ekle
        await self._add_training_correction(user_id, correction_type, original_value, corrected_value)
    
    async def _update_positive_preference(self, user_id: int, item_type: str, item_id: str):
        """Pozitif tercihi güncelle"""
        # Implementasyon...
        pass
    
    async def _update_negative_preference(self, user_id: int, item_type: str, item_id: str):
        """Negatif tercihi güncelle"""
        # Implementasyon...
        pass
    
    async def _update_user_preference(self, user_id: int, preference_type: str, preference_value: Any):
        """Kullanıcı tercihini güncelle"""
        # Implementasyon...
        pass
    
    async def _add_training_correction(self, user_id: int, correction_type: str, 
                                     original_value: Any, corrected_value: Any):
        """Eğitim düzeltmesi ekle"""
        # Implementasyon...
        pass


class RecommendationEngine:
    """Öneri motoru"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.logger = LoggerService.get_logger()
    
    async def get_recommendations(self, user_id: int, preferred_categories: List[int], 
                                context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Öneriler al"""
        # Kategori bazlı öneriler
        recommendations = []
        
        for category_id in preferred_categories[:3]:
            items = await self._get_category_items(category_id, limit=5)
            recommendations.extend(items)
        
        # Sıralama ve filtreleme
        recommendations = self._rank_recommendations(recommendations, context)
        
        return recommendations[:10]
    
    async def get_general_recommendations(self, user_id: int, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genel öneriler al"""
        # Popüler içerikler
        popular_items = await self._get_popular_items(limit=10)
        
        # Sıralama
        recommendations = self._rank_recommendations(popular_items, context)
        
        return recommendations
    
    async def _get_category_items(self, category_id: int, limit: int) -> List[Dict[str, Any]]:
        """Kategori öğelerini al"""
        # Implementasyon...
        return []
    
    async def _get_popular_items(self, limit: int) -> List[Dict[str, Any]]:
        """Popüler öğeleri al"""
        # Implementasyon...
        return []
    
    def _rank_recommendations(self, items: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Önerileri sırala"""
        # Basit sıralama
        return sorted(items, key=lambda x: x.get('score', 0), reverse=True)


class FeedbackProcessor:
    """Geri bildirim işleyici"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.logger = LoggerService.get_logger()
    
    async def save_feedback(self, user_id: int, feedback_data: Dict[str, Any]) -> int:
        """Geri bildirimi kaydet"""
        query = """
            INSERT INTO ai_user_feedback 
            (user_id, feedback_type, feedback_data, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                user_id,
                feedback_data.get('type'),
                json.dumps(feedback_data)
            ))
            conn.commit()
            return cursor.lastrowid


# Global instance
ai_learning_engine = AILearningEngine()