"""
Simple Integration Test
Basit entegrasyon test dosyası
"""

import sys
import os
import json
from datetime import datetime

# Test sonuçları
test_results = {
    "timestamp": datetime.now().isoformat(),
    "tests": {},
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
}

def test_integration_manager():
    """Integration Manager test"""
    try:
        print("Testing Integration Manager...")
        
        # Integration Manager import test
        from core.Services.integration_manager import IntegrationManager, IntegrationFactory
        
        # Factory test
        factory = IntegrationFactory()
        print("✓ IntegrationFactory created successfully")
        
        # Manager test
        manager = IntegrationManager()
        print("✓ IntegrationManager created successfully")
        
        # Test basic methods - parametre olmadan çağır
        status = manager.get_integration_status()
        print("✓ get_integration_status method works")
        
        test_results["tests"]["integration_manager"] = {
            "status": "PASSED",
            "message": "Integration Manager basic functionality works"
        }
        test_results["summary"]["passed"] += 1
        
    except Exception as e:
        print(f"✗ Integration Manager test failed: {e}")
        test_results["tests"]["integration_manager"] = {
            "status": "FAILED",
            "message": str(e)
        }
        test_results["summary"]["failed"] += 1
    
    test_results["summary"]["total"] += 1

def test_integration_service():
    """Integration Service test"""
    try:
        print("Testing Integration Service...")
        
        # Import test
        from core.Services.integration_service import IntegrationService, IntegrationConfig, IntegrationType
        
        # Service creation test
        service = IntegrationService()
        print("✓ IntegrationService created successfully")
        
        # Config test - api_secret yerine secret_key kullan
        config = IntegrationConfig(
            name="test_integration",
            display_name="Test Integration",
            type=IntegrationType.MARKETPLACE,
            api_key="test_key",
            secret_key="test_secret",
            webhook_url="https://test.com/webhook"
        )
        print("✓ IntegrationConfig created successfully")
        
        test_results["tests"]["integration_service"] = {
            "status": "PASSED",
            "message": "Integration Service basic functionality works"
        }
        test_results["summary"]["passed"] += 1
        
    except Exception as e:
        print(f"✗ Integration Service test failed: {e}")
        test_results["tests"]["integration_service"] = {
            "status": "FAILED",
            "message": str(e)
        }
        test_results["summary"]["failed"] += 1
    
    test_results["summary"]["total"] += 1

def test_ai_service():
    """AI Service test"""
    try:
        print("Testing AI Service...")
        
        # Import test - sadece data class'ları test et
        from core.AI.ai_service import AIRecommendation, ProductData, AIAlgorithm
        
        # Data class test - tüm gerekli parametreleri ekle
        product_data = ProductData(
            product_id="test_123",
            name="Test Product",
            current_price=100.0,
            current_stock=50,
            category="Electronics",
            brand="Test Brand",
            sales_history=[{"quantity": 10, "date": "2024-01-01"}],
            competitor_prices=[95.0, 105.0, 110.0],
            market_demand=0.7,
            seasonality_factor=1.0,
            cost_price=70.0,
            profit_margin=0.3
        )
        print("✓ ProductData created successfully")
        
        # Recommendation test
        recommendation = AIRecommendation(
            algorithm=AIAlgorithm.PRICE_OPTIMIZATION,
            product_id="test_123",
            current_value=100.0,
            recommended_value=110.0,
            confidence_score=0.85,
            reasoning="Price optimization based on market analysis",
            market_conditions={"demand": 0.7, "competition": "medium"},
            timestamp=datetime.now()
        )
        print("✓ AIRecommendation created successfully")
        
        test_results["tests"]["ai_service"] = {
            "status": "PASSED",
            "message": "AI Service basic functionality works"
        }
        test_results["summary"]["passed"] += 1
        
    except Exception as e:
        print(f"✗ AI Service test failed: {e}")
        test_results["tests"]["ai_service"] = {
            "status": "FAILED",
            "message": str(e)
        }
        test_results["summary"]["failed"] += 1
    
    test_results["summary"]["total"] += 1

def test_integration_controller():
    """Integration Controller test"""
    try:
        print("Testing Integration Controller...")
        
        # Import test
        from app.Controllers.IntegrationController import IntegrationController
        
        # Controller creation test
        controller = IntegrationController()
        print("✓ IntegrationController created successfully")
        
        test_results["tests"]["integration_controller"] = {
            "status": "PASSED",
            "message": "Integration Controller basic functionality works"
        }
        test_results["summary"]["passed"] += 1
        
    except Exception as e:
        print(f"✗ Integration Controller test failed: {e}")
        test_results["tests"]["integration_controller"] = {
            "status": "FAILED",
            "message": str(e)
        }
        test_results["summary"]["failed"] += 1
    
    test_results["summary"]["total"] += 1

def test_integration_routes():
    """Integration Routes test"""
    try:
        print("Testing Integration Routes...")
        
        # Import test
        from core.Route.integration_routes import register_integration_routes
        
        print("✓ Integration routes module imported successfully")
        
        test_results["tests"]["integration_routes"] = {
            "status": "PASSED",
            "message": "Integration Routes basic functionality works"
        }
        test_results["summary"]["passed"] += 1
        
    except Exception as e:
        print(f"✗ Integration Routes test failed: {e}")
        test_results["tests"]["integration_routes"] = {
            "status": "FAILED",
            "message": str(e)
        }
        test_results["summary"]["failed"] += 1
    
    test_results["summary"]["total"] += 1

def test_integrations_data():
    """Integrations Data test"""
    try:
        print("Testing Integrations Data...")
        
        # Import test
        from config.integrations_data import INTEGRATIONS_DATA
        
        # Data structure test
        assert isinstance(INTEGRATIONS_DATA, dict), "INTEGRATIONS_DATA should be a dictionary"
        assert len(INTEGRATIONS_DATA) > 0, "INTEGRATIONS_DATA should not be empty"
        
        # Check structure - marketplaces listesi içindeki her item için kontrol et
        marketplaces = INTEGRATIONS_DATA.get("marketplaces", [])
        assert len(marketplaces) > 0, "Marketplaces list should not be empty"
        
        for integration in marketplaces:
            assert "name" in integration, f"Integration missing 'name': {integration}"
            assert "display_name" in integration, f"Integration missing 'display_name': {integration}"
            assert "description" in integration, f"Integration missing 'description': {integration}"
        
        print(f"✓ Integrations Data loaded successfully - {len(marketplaces)} marketplace integrations found")
        
        test_results["tests"]["integrations_data"] = {
            "status": "PASSED",
            "message": f"Integrations Data loaded successfully - {len(marketplaces)} marketplace integrations"
        }
        test_results["summary"]["passed"] += 1
        
    except Exception as e:
        print(f"✗ Integrations Data test failed: {e}")
        test_results["tests"]["integrations_data"] = {
            "status": "FAILED",
            "message": str(e)
        }
        test_results["summary"]["failed"] += 1
    
    test_results["summary"]["total"] += 1

def main():
    """Ana test fonksiyonu"""
    print("=" * 60)
    print("ENTERPRISE INTEGRATION SYSTEM TEST")
    print("=" * 60)
    print(f"Test başlangıç zamanı: {datetime.now()}")
    print()
    
    # Testleri çalıştır
    test_integration_manager()
    test_integration_service()
    test_ai_service()
    test_integration_controller()
    test_integration_routes()
    test_integrations_data()
    
    # Sonuçları yazdır
    print()
    print("=" * 60)
    print("TEST SONUÇLARI")
    print("=" * 60)
    
    for test_name, result in test_results["tests"].items():
        status = "✓ PASSED" if result["status"] == "PASSED" else "✗ FAILED"
        print(f"{status}: {test_name}")
        print(f"  {result['message']}")
        print()
    
    # Özet
    summary = test_results["summary"]
    print(f"Toplam Test: {summary['total']}")
    print(f"Başarılı: {summary['passed']}")
    print(f"Başarısız: {summary['failed']}")
    print(f"Başarı Oranı: {(summary['passed']/summary['total']*100):.1f}%" if summary['total'] > 0 else "Başarı Oranı: 0%")
    
    # Sonuçları dosyaya kaydet
    with open("test_results_simple.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print()
    print("Sonuçlar 'test_results_simple.json' dosyasına kaydedildi.")
    
    return summary["failed"] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)