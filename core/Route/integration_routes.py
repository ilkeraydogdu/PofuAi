#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Routes
==================

Entegrasyon sistemi route tanımlamaları
"""

from flask import Blueprint
from app.Controllers.IntegrationController import IntegrationController


# Blueprint oluştur
integration_bp = Blueprint('integration', __name__, url_prefix='/api/integrations')

# Controller instance
controller = IntegrationController()


# Route tanımlamaları
@integration_bp.route('', methods=['GET'])
async def list_integrations():
    """Kullanıcının entegrasyonlarını listele"""
    return await controller.list_integrations()


@integration_bp.route('', methods=['POST'])
async def add_integration():
    """Yeni entegrasyon ekle"""
    return await controller.add_integration()


@integration_bp.route('/available', methods=['GET'])
async def get_available_integrations():
    """Kullanılabilir entegrasyonları listele"""
    return await controller.get_available_integrations()


@integration_bp.route('/<int:integration_id>', methods=['GET'])
async def get_integration_details(integration_id):
    """Entegrasyon detaylarını getir"""
    return await controller.get_integration_details(integration_id)


@integration_bp.route('/<int:integration_id>/activate', methods=['POST'])
async def activate_integration(integration_id):
    """Entegrasyonu aktifleştir"""
    return await controller.activate_integration(integration_id)


@integration_bp.route('/<int:integration_id>/deactivate', methods=['POST'])
async def deactivate_integration(integration_id):
    """Entegrasyonu deaktif et"""
    return await controller.deactivate_integration(integration_id)


@integration_bp.route('/<int:integration_id>', methods=['DELETE'])
async def delete_integration(integration_id):
    """Entegrasyonu sil"""
    return await controller.delete_integration(integration_id)


@integration_bp.route('/sync/products', methods=['POST'])
async def sync_products():
    """Ürünleri senkronize et"""
    return await controller.sync_products()


@integration_bp.route('/sync/orders', methods=['POST'])
async def sync_orders():
    """Siparişleri senkronize et"""
    return await controller.sync_orders()


@integration_bp.route('/update/stock', methods=['POST'])
async def update_stock():
    """Stok güncelle"""
    return await controller.update_stock()


@integration_bp.route('/sync-logs', methods=['GET'])
async def get_sync_logs():
    """Senkronizasyon loglarını getir"""
    return await controller.get_sync_logs()


def register_integration_routes(app):
    """
    Entegrasyon route'larını uygulamaya kaydet
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(integration_bp)
    
    # Log route registration
    logger = controller.logger
    logger.info(f"Integration routes registered: {len(integration_bp.deferred_functions)} routes")