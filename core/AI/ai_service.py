"""
Enterprise AI Service
PraPazar entegrasyon sistemi için enterprise seviyesinde AI servisi
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import aiohttp
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

class AIAlgorithm(Enum):
    """AI algoritma türleri"""
    PRICE_OPTIMIZATION = "price_optimization"
    STOCK_PREDICTION = "stock_prediction"
    SALES_FORECAST = "sales_forecast"
    CUSTOMER_SEGMENTATION = "customer_segmentation"
    DEMAND_PREDICTION = "demand_prediction"
    COMPETITIVE_ANALYSIS = "competitive_analysis"

@dataclass
class ProductData:
    """Ürün verisi"""
    product_id: str
    name: str
    current_price: float
    current_stock: int
    category: str
    brand: str
    sales_history: List[Dict]
    competitor_prices: List[float]
    market_demand: float
    seasonality_factor: float
    cost_price: float
    profit_margin: float

@dataclass
class AIRecommendation:
    """AI önerisi"""
    algorithm: AIAlgorithm
    product_id: str
    current_value: Union[float, int]
    recommended_value: Union[float, int]
    confidence_score: float
    reasoning: str
    market_conditions: Dict[str, Any]
    timestamp: datetime

class PriceOptimizationEngine:
    """Fiyat optimizasyon motoru"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    async def train_model(self, training_data: List[ProductData]):
        """Fiyat optimizasyon modelini eğit"""
        try:
            # Veri hazırlama
            features = []
            targets = []
            
            for product in training_data:
                # Özellik vektörü oluştur
                feature_vector = [
                    product.current_price,
                    product.current_stock,
                    product.market_demand,
                    product.seasonality_factor,
                    product.cost_price,
                    product.profit_margin,
                    np.mean(product.competitor_prices) if product.competitor_prices else product.current_price,
                    len(product.sales_history),
                    sum(sale['quantity'] for sale in product.sales_history[-30:]) if product.sales_history else 0
                ]
                
                features.append(feature_vector)
                
                # Hedef: Optimal fiyat (maliyet + %30 kar marjı + piyasa faktörü)
                optimal_price = product.cost_price * 1.3 * (1 + product.market_demand * 0.1)
                targets.append(optimal_price)
            
            # Model eğitimi
            X = np.array(features)
            y = np.array(targets)
            
            # Veriyi ölçeklendir
            X_scaled = self.scaler.fit_transform(X)
            
            # Model oluştur ve eğit
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_scaled, y)
            
            self.is_trained = True
            self.logger.info("Fiyat optimizasyon modeli eğitildi")
            
        except Exception as e:
            self.logger.error(f"Model eğitme hatası: {e}")
            self.is_trained = False
            
    async def optimize_price(self, product: ProductData) -> AIRecommendation:
        """Ürün fiyatını optimize et"""
        try:
            if not self.is_trained:
                # Basit heuristik kullan
                return await self._simple_price_optimization(product)
            
            # Özellik vektörü oluştur
            feature_vector = [
                product.current_price,
                product.current_stock,
                product.market_demand,
                product.seasonality_factor,
                product.cost_price,
                product.profit_margin,
                np.mean(product.competitor_prices) if product.competitor_prices else product.current_price,
                len(product.sales_history),
                sum(sale['quantity'] for sale in product.sales_history[-30:]) if product.sales_history else 0
            ]
            
            # Tahmin yap
            X_scaled = self.scaler.transform([feature_vector])
            predicted_price = self.model.predict(X_scaled)[0]
            
            # Güven skoru hesapla
            confidence = self._calculate_confidence(product)
            
            # Piyasa koşulları
            market_conditions = {
                'competitor_avg_price': np.mean(product.competitor_prices) if product.competitor_prices else product.current_price,
                'market_demand': product.market_demand,
                'seasonality': product.seasonality_factor,
                'stock_level': product.current_stock
            }
            
            return AIRecommendation(
                algorithm=AIAlgorithm.PRICE_OPTIMIZATION,
                product_id=product.product_id,
                current_value=product.current_price,
                recommended_value=predicted_price,
                confidence_score=confidence,
                reasoning=f"AI modeli tarafından optimize edildi. Piyasa koşulları: {market_conditions}",
                market_conditions=market_conditions,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Fiyat optimizasyon hatası: {e}")
            return await self._simple_price_optimization(product)
            
    async def _simple_price_optimization(self, product: ProductData) -> AIRecommendation:
        """Basit fiyat optimizasyonu"""
        # Basit heuristik: Maliyet + %30 kar + piyasa faktörü
        base_price = product.cost_price * 1.3
        market_factor = 1 + (product.market_demand - 0.5) * 0.2
        competitor_factor = 1.0
        
        if product.competitor_prices:
            avg_competitor = np.mean(product.competitor_prices)
            if avg_competitor > 0:
                competitor_factor = avg_competitor / product.current_price
                
        recommended_price = base_price * market_factor * competitor_factor
        
        return AIRecommendation(
            algorithm=AIAlgorithm.PRICE_OPTIMIZATION,
            product_id=product.product_id,
            current_value=product.current_price,
            recommended_value=recommended_price,
            confidence_score=0.7,
            reasoning="Basit heuristik kullanılarak hesaplandı",
            market_conditions={
                'competitor_avg_price': np.mean(product.competitor_prices) if product.competitor_prices else product.current_price,
                'market_demand': product.market_demand
            },
            timestamp=datetime.utcnow()
        )
        
    def _calculate_confidence(self, product: ProductData) -> float:
        """Güven skoru hesapla"""
        confidence = 0.8  # Base confidence
        
        # Veri kalitesi faktörleri
        if len(product.sales_history) > 10:
            confidence += 0.1
        if product.competitor_prices:
            confidence += 0.05
        if product.market_demand > 0.5:
            confidence += 0.05
            
        return min(confidence, 1.0)

class StockPredictionEngine:
    """Stok tahmin motoru"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.is_trained = False
        
    async def train_model(self, training_data: List[ProductData]):
        """Stok tahmin modelini eğit"""
        try:
            features = []
            targets = []
            
            for product in training_data:
                # Satış verilerini analiz et
                if product.sales_history:
                    daily_sales = [sale['quantity'] for sale in product.sales_history[-30:]]
                    avg_daily_sales = np.mean(daily_sales)
                    sales_volatility = np.std(daily_sales)
                    
                    # Özellik vektörü
                    feature_vector = [
                        avg_daily_sales,
                        sales_volatility,
                        product.current_stock,
                        product.market_demand,
                        product.seasonality_factor,
                        len(product.sales_history)
                    ]
                    
                    features.append(feature_vector)
                    
                    # Hedef: Optimal stok seviyesi (30 günlük satış + güvenlik stoku)
                    optimal_stock = int(avg_daily_sales * 30 * 1.2)
                    targets.append(optimal_stock)
            
            if features:
                X = np.array(features)
                y = np.array(targets)
                
                self.model = RandomForestRegressor(n_estimators=100, random_state=42)
                self.model.fit(X, y)
                self.is_trained = True
                
            self.logger.info("Stok tahmin modeli eğitildi")
            
        except Exception as e:
            self.logger.error(f"Stok modeli eğitme hatası: {e}")
            self.is_trained = False
            
    async def predict_stock(self, product: ProductData) -> AIRecommendation:
        """Stok seviyesini tahmin et"""
        try:
            if not product.sales_history:
                # Satış verisi yoksa basit hesaplama
                return await self._simple_stock_prediction(product)
            
            # Son 30 günlük satış verilerini analiz et
            daily_sales = [sale['quantity'] for sale in product.sales_history[-30:]]
            
            if not daily_sales:
                return await self._simple_stock_prediction(product)
            
            avg_daily_sales = np.mean(daily_sales)
            sales_volatility = np.std(daily_sales)
            
            if self.is_trained:
                # Model tahmini
                feature_vector = [
                    avg_daily_sales,
                    sales_volatility,
                    product.current_stock,
                    product.market_demand,
                    product.seasonality_factor,
                    len(product.sales_history)
                ]
                
                predicted_stock = self.model.predict([feature_vector])[0]
            else:
                # Basit hesaplama
                predicted_stock = int(avg_daily_sales * 30 * 1.2)
            
            # Güven skoru
            confidence = self._calculate_stock_confidence(product, daily_sales)
            
            return AIRecommendation(
                algorithm=AIAlgorithm.STOCK_PREDICTION,
                product_id=product.product_id,
                current_value=product.current_stock,
                recommended_value=int(predicted_stock),
                confidence_score=confidence,
                reasoning=f"Günlük ortalama satış: {avg_daily_sales:.1f}, 30 günlük tahmin",
                market_conditions={
                    'avg_daily_sales': avg_daily_sales,
                    'sales_volatility': sales_volatility,
                    'market_demand': product.market_demand
                },
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Stok tahmin hatası: {e}")
            return await self._simple_stock_prediction(product)
            
    async def _simple_stock_prediction(self, product: ProductData) -> AIRecommendation:
        """Basit stok tahmini"""
        # Eğer satış verisi yoksa, mevcut stokun %120'sini öner
        recommended_stock = max(int(product.current_stock * 1.2), 10)
        
        return AIRecommendation(
            algorithm=AIAlgorithm.STOCK_PREDICTION,
            product_id=product.product_id,
            current_value=product.current_stock,
            recommended_value=recommended_stock,
            confidence_score=0.5,
            reasoning="Satış verisi yok, basit heuristik kullanıldı",
            market_conditions={'market_demand': product.market_demand},
            timestamp=datetime.utcnow()
        )
        
    def _calculate_stock_confidence(self, product: ProductData, daily_sales: List[int]) -> float:
        """Stok tahmin güven skoru"""
        confidence = 0.7  # Base confidence
        
        if len(daily_sales) > 20:
            confidence += 0.1
        if np.std(daily_sales) < np.mean(daily_sales) * 0.5:
            confidence += 0.1
        if product.market_demand > 0.5:
            confidence += 0.1
            
        return min(confidence, 1.0)

class SalesForecastEngine:
    """Satış tahmin motoru"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def forecast_sales(self, product: ProductData, days: int = 30) -> Dict[str, Any]:
        """Satış tahmini yap"""
        try:
            if not product.sales_history:
                return {
                    'forecast': [],
                    'confidence': 0.3,
                    'reasoning': 'Satış verisi yok'
                }
            
            # Son satış verilerini analiz et
            recent_sales = [sale['quantity'] for sale in product.sales_history[-90:]]
            
            if len(recent_sales) < 7:
                return {
                    'forecast': [],
                    'confidence': 0.4,
                    'reasoning': 'Yetersiz veri'
                }
            
            # Basit trend analizi
            avg_daily = np.mean(recent_sales)
            trend = self._calculate_trend(recent_sales)
            
            # Tahmin hesapla
            forecast = []
            for day in range(days):
                predicted = avg_daily + (trend * day)
                forecast.append(max(0, int(predicted)))
            
            confidence = self._calculate_forecast_confidence(recent_sales)
            
            return {
                'forecast': forecast,
                'confidence': confidence,
                'reasoning': f'Ortalama günlük satış: {avg_daily:.1f}, Trend: {trend:.2f}',
                'avg_daily_sales': avg_daily,
                'trend': trend
            }
            
        except Exception as e:
            self.logger.error(f"Satış tahmin hatası: {e}")
            return {
                'forecast': [],
                'confidence': 0.2,
                'reasoning': f'Hata: {str(e)}'
            }
            
    def _calculate_trend(self, sales_data: List[int]) -> float:
        """Satış trendini hesapla"""
        if len(sales_data) < 2:
            return 0.0
            
        x = np.arange(len(sales_data))
        y = np.array(sales_data)
        
        # Basit lineer regresyon
        slope = np.polyfit(x, y, 1)[0]
        return slope
        
    def _calculate_forecast_confidence(self, sales_data: List[int]) -> float:
        """Tahmin güven skoru"""
        confidence = 0.6  # Base confidence
        
        if len(sales_data) > 30:
            confidence += 0.2
        if np.std(sales_data) < np.mean(sales_data) * 0.3:
            confidence += 0.1
        if len(sales_data) > 60:
            confidence += 0.1
            
        return min(confidence, 1.0)

class AIService:
    """Enterprise AI Service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.price_engine = PriceOptimizationEngine()
        self.stock_engine = StockPredictionEngine()
        self.sales_engine = SalesForecastEngine()
        
        # Model dosyaları için dizin
        self.model_dir = "models"
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
            
    async def initialize(self):
        """AI servisini başlat"""
        try:
            # Modelleri yükle
            await self._load_models()
            self.logger.info("AI Service başarıyla başlatıldı")
            return True
        except Exception as e:
            self.logger.error(f"AI Service başlatma hatası: {e}")
            return False
            
    async def _load_models(self):
        """Kayıtlı modelleri yükle"""
        try:
            # Fiyat modeli
            price_model_path = os.path.join(self.model_dir, "price_model.pkl")
            if os.path.exists(price_model_path):
                self.price_engine.model = joblib.load(price_model_path)
                self.price_engine.is_trained = True
                
            # Stok modeli
            stock_model_path = os.path.join(self.model_dir, "stock_model.pkl")
            if os.path.exists(stock_model_path):
                self.stock_engine.model = joblib.load(stock_model_path)
                self.stock_engine.is_trained = True
                
        except Exception as e:
            self.logger.warning(f"Model yükleme hatası: {e}")
            
    async def _save_models(self):
        """Modelleri kaydet"""
        try:
            if self.price_engine.is_trained:
                joblib.dump(self.price_engine.model, os.path.join(self.model_dir, "price_model.pkl"))
                
            if self.stock_engine.is_trained:
                joblib.dump(self.stock_engine.model, os.path.join(self.model_dir, "stock_model.pkl"))
                
        except Exception as e:
            self.logger.error(f"Model kaydetme hatası: {e}")
            
    async def optimize_pricing(self, product_data: Dict[str, Any]) -> AIRecommendation:
        """Fiyat optimizasyonu"""
        try:
            # ProductData oluştur
            product = ProductData(
                product_id=product_data.get('product_id', ''),
                name=product_data.get('name', ''),
                current_price=product_data.get('current_price', 0.0),
                current_stock=product_data.get('current_stock', 0),
                category=product_data.get('category', ''),
                brand=product_data.get('brand', ''),
                sales_history=product_data.get('sales_history', []),
                competitor_prices=product_data.get('competitor_prices', []),
                market_demand=product_data.get('market_demand', 0.5),
                seasonality_factor=product_data.get('seasonality_factor', 1.0),
                cost_price=product_data.get('cost_price', 0.0),
                profit_margin=product_data.get('profit_margin', 0.3)
            )
            
            return await self.price_engine.optimize_price(product)
            
        except Exception as e:
            self.logger.error(f"Fiyat optimizasyon hatası: {e}")
            return AIRecommendation(
                algorithm=AIAlgorithm.PRICE_OPTIMIZATION,
                product_id=product_data.get('product_id', ''),
                current_value=product_data.get('current_price', 0.0),
                recommended_value=product_data.get('current_price', 0.0),
                confidence_score=0.0,
                reasoning=f"Hata: {str(e)}",
                market_conditions={},
                timestamp=datetime.utcnow()
            )
            
    async def predict_stock(self, product_data: Dict[str, Any]) -> AIRecommendation:
        """Stok tahmini"""
        try:
            # ProductData oluştur
            product = ProductData(
                product_id=product_data.get('product_id', ''),
                name=product_data.get('name', ''),
                current_price=product_data.get('current_price', 0.0),
                current_stock=product_data.get('current_stock', 0),
                category=product_data.get('category', ''),
                brand=product_data.get('brand', ''),
                sales_history=product_data.get('sales_history', []),
                competitor_prices=product_data.get('competitor_prices', []),
                market_demand=product_data.get('market_demand', 0.5),
                seasonality_factor=product_data.get('seasonality_factor', 1.0),
                cost_price=product_data.get('cost_price', 0.0),
                profit_margin=product_data.get('profit_margin', 0.3)
            )
            
            return await self.stock_engine.predict_stock(product)
            
        except Exception as e:
            self.logger.error(f"Stok tahmin hatası: {e}")
            return AIRecommendation(
                algorithm=AIAlgorithm.STOCK_PREDICTION,
                product_id=product_data.get('product_id', ''),
                current_value=product_data.get('current_stock', 0),
                recommended_value=product_data.get('current_stock', 0),
                confidence_score=0.0,
                reasoning=f"Hata: {str(e)}",
                market_conditions={},
                timestamp=datetime.utcnow()
            )
            
    async def forecast_sales(self, product_data: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """Satış tahmini"""
        try:
            # ProductData oluştur
            product = ProductData(
                product_id=product_data.get('product_id', ''),
                name=product_data.get('name', ''),
                current_price=product_data.get('current_price', 0.0),
                current_stock=product_data.get('current_stock', 0),
                category=product_data.get('category', ''),
                brand=product_data.get('brand', ''),
                sales_history=product_data.get('sales_history', []),
                competitor_prices=product_data.get('competitor_prices', []),
                market_demand=product_data.get('market_demand', 0.5),
                seasonality_factor=product_data.get('seasonality_factor', 1.0),
                cost_price=product_data.get('cost_price', 0.0),
                profit_margin=product_data.get('profit_margin', 0.3)
            )
            
            return await self.sales_engine.forecast_sales(product, days)
            
        except Exception as e:
            self.logger.error(f"Satış tahmin hatası: {e}")
            return {
                'forecast': [],
                'confidence': 0.0,
                'reasoning': f"Hata: {str(e)}"
            }
            
    async def train_models(self, training_data: List[Dict[str, Any]]):
        """AI modellerini eğit"""
        try:
            # Training data'yı ProductData'ya dönüştür
            products = []
            for data in training_data:
                product = ProductData(
                    product_id=data.get('product_id', ''),
                    name=data.get('name', ''),
                    current_price=data.get('current_price', 0.0),
                    current_stock=data.get('current_stock', 0),
                    category=data.get('category', ''),
                    brand=data.get('brand', ''),
                    sales_history=data.get('sales_history', []),
                    competitor_prices=data.get('competitor_prices', []),
                    market_demand=data.get('market_demand', 0.5),
                    seasonality_factor=data.get('seasonality_factor', 1.0),
                    cost_price=data.get('cost_price', 0.0),
                    profit_margin=data.get('profit_margin', 0.3)
                )
                products.append(product)
            
            # Modelleri eğit
            await self.price_engine.train_model(products)
            await self.stock_engine.train_model(products)
            
            # Modelleri kaydet
            await self._save_models()
            
            self.logger.info("AI modelleri eğitildi ve kaydedildi")
            
        except Exception as e:
            self.logger.error(f"Model eğitme hatası: {e}")
            
    def get_ai_status(self) -> Dict[str, Any]:
        """AI sistem durumu"""
        return {
            'price_model_trained': self.price_engine.is_trained,
            'stock_model_trained': self.stock_engine.is_trained,
            'models_loaded': True,
            'timestamp': datetime.utcnow().isoformat()
        }

# Global AI service instance
ai_service = AIService()