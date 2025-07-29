"""
Enterprise Integration Controller
PraPazar entegrasyon sistemi için enterprise seviyesinde controller
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import request, jsonify
from app.Controllers.BaseController import BaseController
from core.Services.integration_service import (
    integration_service, IntegrationConfig, IntegrationType, IntegrationStatus
)
from core.AI.ai_service import ai_service
from core.Services.error_handler import error_handler

class IntegrationController(BaseController):
    """Enterprise Integration Controller"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
    async def list_integrations(self):
        """Tüm entegrasyonları listele"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Query parameters
            status_filter = request.args.get('status')
            type_filter = request.args.get('type')
            
            # Status enum'a çevir
            status = None
            if status_filter:
                try:
                    status = IntegrationStatus(status_filter)
                except ValueError:
                    return self.error_response('Invalid status parameter', 400)
                    
            # Entegrasyonları getir
            integrations = integration_service.list_integrations(status)
            
            # Response format
            result = []
            for integration in integrations:
                result.append({
                    'id': integration.id,
                    'name': integration.name,
                    'display_name': integration.display_name,
                    'type': integration.type,
                    'status': integration.status,
                    'last_sync': integration.last_sync.isoformat() if integration.last_sync else None,
                    'error_count': integration.error_count,
                    'last_error': integration.last_error,
                    'created_at': integration.created_at.isoformat(),
                    'updated_at': integration.updated_at.isoformat()
                })
                
            return self.json_response({
                'success': True,
                'data': result,
                'total': len(result),
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def get_integration(self, integration_name: str):
        """Belirli bir entegrasyonu getir"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Entegrasyonu getir
            integration = integration_service.get_integration(integration_name)
            if not integration:
                return self.error_response('Integration not found', 404)
                
            # Metrics getir
            metrics = integration_service.get_integration_metrics(integration_name)
            
            # Response
            result = {
                'id': integration.id,
                'name': integration.name,
                'display_name': integration.display_name,
                'type': integration.type,
                'status': integration.status,
                'config': integration.config,
                'last_sync': integration.last_sync.isoformat() if integration.last_sync else None,
                'error_count': integration.error_count,
                'last_error': integration.last_error,
                'created_at': integration.created_at.isoformat(),
                'updated_at': integration.updated_at.isoformat(),
                'metrics': metrics
            }
            
            return self.json_response({
                'success': True,
                'data': result,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def register_integration(self):
        """Yeni entegrasyon kaydet"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Request data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'name': 'required|string',
                'display_name': 'required|string',
                'type': 'required|string'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
                
            # Type enum'a çevir
            try:
                integration_type = IntegrationType(data['type'])
            except ValueError:
                return self.error_response('Invalid integration type', 400)
                
            # Config oluştur
            config = IntegrationConfig(
                name=data['name'],
                display_name=data['display_name'],
                type=integration_type,
                api_key=data.get('api_key'),
                secret_key=data.get('secret_key'),
                webhook_url=data.get('webhook_url'),
                rate_limit=data.get('rate_limit', 100),
                timeout=data.get('timeout', 30),
                retry_count=data.get('retry_count', 3),
                is_premium=data.get('is_premium', False),
                is_coming_soon=data.get('is_coming_soon', False),
                supported_countries=data.get('supported_countries', []),
                supported_currencies=data.get('supported_currencies', []),
                features=data.get('features', []),
                ai_features=data.get('ai_features', [])
            )
            
            # Entegrasyonu kaydet
            success = integration_service.register_integration(config)
            
            if success:
                return self.json_response({
                    'success': True,
                    'message': 'Integration registered successfully',
                    'integration_name': data['name'],
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                return self.error_response('Failed to register integration', 500)
                
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def sync_integration(self, integration_name: str):
        """Entegrasyon senkronizasyonu"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Sync type
            sync_type = request.args.get('type', 'full')
            
            # Senkronizasyon yap
            result = await integration_service.sync_integration(integration_name, sync_type)
            
            return self.json_response({
                'success': True,
                'data': result,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def bulk_sync(self):
        """Toplu senkronizasyon"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Request data
            data = self.get_all_input()
            integration_names = data.get('integrations', [])
            
            # Toplu senkronizasyon
            result = await integration_service.bulk_sync(integration_names)
            
            return self.json_response({
                'success': True,
                'data': result,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def update_integration_status(self, integration_name: str):
        """Entegrasyon durumunu güncelle"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Request data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'status': 'required|string'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
                
            # Status enum'a çevir
            try:
                status = IntegrationStatus(data['status'])
            except ValueError:
                return self.error_response('Invalid status', 400)
                
            # Durumu güncelle
            error_message = data.get('error')
            success = integration_service.update_integration_status(
                integration_name, status, error_message
            )
            
            if success:
                return self.json_response({
                    'success': True,
                    'message': 'Integration status updated successfully',
                    'integration_name': integration_name,
                    'status': status.value,
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                return self.error_response('Failed to update integration status', 500)
                
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def get_integration_metrics(self, integration_name: str):
        """Entegrasyon metriklerini getir"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Metrikleri getir
            metrics = integration_service.get_integration_metrics(integration_name)
            
            return self.json_response({
                'success': True,
                'data': metrics,
                'integration_name': integration_name,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def get_system_health(self):
        """Sistem sağlık durumu"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Sistem sağlığını getir
            health = integration_service.get_system_health()
            
            return self.json_response({
                'success': True,
                'data': health,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    # AI Endpoints
    async def optimize_pricing(self):
        """AI fiyat optimizasyonu"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Request data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'product_id': 'required|string',
                'current_price': 'required|numeric',
                'current_stock': 'required|integer'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
                
            # AI optimizasyonu
            recommendation = await ai_service.optimize_pricing(data)
            
            return self.json_response({
                'success': True,
                'data': {
                    'algorithm': recommendation.algorithm.value,
                    'product_id': recommendation.product_id,
                    'current_value': recommendation.current_value,
                    'recommended_value': recommendation.recommended_value,
                    'confidence_score': recommendation.confidence_score,
                    'reasoning': recommendation.reasoning,
                    'market_conditions': recommendation.market_conditions,
                    'timestamp': recommendation.timestamp.isoformat()
                },
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def predict_stock(self):
        """AI stok tahmini"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Request data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'product_id': 'required|string',
                'current_stock': 'required|integer'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
                
            # AI tahmini
            recommendation = await ai_service.predict_stock(data)
            
            return self.json_response({
                'success': True,
                'data': {
                    'algorithm': recommendation.algorithm.value,
                    'product_id': recommendation.product_id,
                    'current_value': recommendation.current_value,
                    'recommended_value': recommendation.recommended_value,
                    'confidence_score': recommendation.confidence_score,
                    'reasoning': recommendation.reasoning,
                    'market_conditions': recommendation.market_conditions,
                    'timestamp': recommendation.timestamp.isoformat()
                },
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def forecast_sales(self):
        """AI satış tahmini"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Request data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'product_id': 'required|string'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
                
            # Gün sayısı
            days = request.args.get('days', 30, type=int)
            
            # AI tahmini
            forecast = await ai_service.forecast_sales(data, days)
            
            return self.json_response({
                'success': True,
                'data': forecast,
                'product_id': data['product_id'],
                'days': days,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def train_ai_models(self):
        """AI modellerini eğit"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Request data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'training_data': 'required|array'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
                
            # Modelleri eğit
            await ai_service.train_models(data['training_data'])
            
            return self.json_response({
                'success': True,
                'message': 'AI models trained successfully',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def get_ai_status(self):
        """AI sistem durumu"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # AI durumunu getir
            status = ai_service.get_ai_status()
            
            return self.json_response({
                'success': True,
                'data': status,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    # Webhook endpoints
    async def webhook_handler(self, integration_name: str):
        """Webhook handler"""
        try:
            # Webhook data
            data = self.get_all_input()
            headers = dict(request.headers)
            
            # Webhook işleme
            self.logger.info(f"Webhook received for {integration_name}: {data}")
            
            # Entegrasyon durumunu güncelle
            integration_service.update_integration_status(
                integration_name, IntegrationStatus.ACTIVE
            )
            
            return self.json_response({
                'success': True,
                'message': 'Webhook processed successfully',
                'integration_name': integration_name,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    # Utility endpoints
    async def cleanup_old_data(self):
        """Eski verileri temizle"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Gün sayısı
            days = request.args.get('days', 30, type=int)
            
            # Temizlik yap
            success = integration_service.cleanup_old_data(days)
            
            if success:
                return self.json_response({
                    'success': True,
                    'message': 'Old data cleaned successfully',
                    'days': days,
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                return self.error_response('Failed to cleanup old data', 500)
                
        except Exception as e:
            return error_handler.handle_error(e, self.request)
            
    async def initialize_services(self):
        """Servisleri başlat"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
                
            # Integration service
            integration_success = await integration_service.initialize()
            
            # AI service
            ai_success = await ai_service.initialize()
            
            return self.json_response({
                'success': True,
                'data': {
                    'integration_service': integration_success,
                    'ai_service': ai_success
                },
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)

# Global controller instance
integration_controller = IntegrationController()