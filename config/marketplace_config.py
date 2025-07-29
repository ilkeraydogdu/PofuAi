#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marketplace Configuration System
Environment-based API key management
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class MarketplaceConfig:
    """Marketplace API configuration"""
    api_key: str
    api_secret: str
    supplier_id: Optional[str] = None
    sandbox: bool = True
    base_url: Optional[str] = None

class MarketplaceConfigManager:
    """Centralized marketplace configuration manager"""
    
    def __init__(self):
        self.configs = {}
        self._load_configs()
    
    def _load_configs(self):
        """Load all marketplace configurations from environment variables"""
        
        # Trendyol Configuration
        self.configs['trendyol'] = MarketplaceConfig(
            api_key=os.getenv('TRENDYOL_API_KEY', 'demo_api_key'),
            api_secret=os.getenv('TRENDYOL_API_SECRET', 'demo_api_secret'),
            supplier_id=os.getenv('TRENDYOL_SUPPLIER_ID', 'demo_supplier_id'),
            sandbox=os.getenv('TRENDYOL_SANDBOX', 'true').lower() == 'true'
        )
        
        # N11 Configuration
        self.configs['n11'] = MarketplaceConfig(
            api_key=os.getenv('N11_API_KEY', 'demo_api_key'),
            api_secret=os.getenv('N11_API_SECRET', 'demo_api_secret'),
            sandbox=os.getenv('N11_SANDBOX', 'true').lower() == 'true'
        )
        
        # Hepsiburada Configuration
        self.configs['hepsiburada'] = MarketplaceConfig(
            api_key=os.getenv('HEPSIBURADA_API_KEY', 'demo_api_key'),
            api_secret=os.getenv('HEPSIBURADA_API_SECRET', 'demo_api_secret'),
            supplier_id=os.getenv('HEPSIBURADA_MERCHANT_ID', 'demo_merchant_id'),
            sandbox=os.getenv('HEPSIBURADA_SANDBOX', 'true').lower() == 'true'
        )
        
        # GittiGidiyor Configuration
        self.configs['gittigidiyor'] = MarketplaceConfig(
            api_key=os.getenv('GITTIGIDIYOR_API_KEY', 'demo_api_key'),
            api_secret=os.getenv('GITTIGIDIYOR_API_SECRET', 'demo_api_secret'),
            sandbox=os.getenv('GITTIGIDIYOR_SANDBOX', 'true').lower() == 'true'
        )
        
        # Çiçeksepeti Configuration
        self.configs['ciceksepeti'] = MarketplaceConfig(
            api_key=os.getenv('CICEKSEPETI_API_KEY', 'demo_api_key'),
            api_secret=os.getenv('CICEKSEPETI_API_SECRET', 'demo_api_secret'),
            sandbox=os.getenv('CICEKSEPETI_SANDBOX', 'true').lower() == 'true'
        )
        
        # Amazon Configuration
        self.configs['amazon'] = MarketplaceConfig(
            api_key=os.getenv('AMAZON_ACCESS_KEY', 'demo_access_key'),
            api_secret=os.getenv('AMAZON_SECRET_KEY', 'demo_secret_key'),
            supplier_id=os.getenv('AMAZON_SELLER_ID', 'demo_seller_id'),
            sandbox=os.getenv('AMAZON_SANDBOX', 'true').lower() == 'true'
        )
        
        # eBay Configuration
        self.configs['ebay'] = MarketplaceConfig(
            api_key=os.getenv('EBAY_APP_ID', 'demo_app_id'),
            api_secret=os.getenv('EBAY_CERT_ID', 'demo_cert_id'),
            sandbox=os.getenv('EBAY_SANDBOX', 'true').lower() == 'true'
        )
        
        # Etsy Configuration
        self.configs['etsy'] = MarketplaceConfig(
            api_key=os.getenv('ETSY_API_KEY', 'demo_api_key'),
            api_secret=os.getenv('ETSY_API_SECRET', 'demo_api_secret'),
            sandbox=os.getenv('ETSY_SANDBOX', 'true').lower() == 'true'
        )
        
        # AliExpress Configuration
        self.configs['aliexpress'] = MarketplaceConfig(
            api_key=os.getenv('ALIEXPRESS_APP_KEY', 'demo_app_key'),
            api_secret=os.getenv('ALIEXPRESS_APP_SECRET', 'demo_app_secret'),
            sandbox=os.getenv('ALIEXPRESS_SANDBOX', 'true').lower() == 'true'
        )
        
        # Payment Gateway Configurations
        
        # İyzico Configuration
        self.configs['iyzico'] = MarketplaceConfig(
            api_key=os.getenv('IYZICO_API_KEY', 'demo_api_key'),
            api_secret=os.getenv('IYZICO_SECRET_KEY', 'demo_secret_key'),
            sandbox=os.getenv('IYZICO_SANDBOX', 'true').lower() == 'true'
        )
        
        # PayTR Configuration
        self.configs['paytr'] = MarketplaceConfig(
            api_key=os.getenv('PAYTR_MERCHANT_ID', 'demo_merchant_id'),
            api_secret=os.getenv('PAYTR_MERCHANT_KEY', 'demo_merchant_key'),
            sandbox=os.getenv('PAYTR_SANDBOX', 'true').lower() == 'true'
        )
        
        # Stripe Configuration
        self.configs['stripe'] = MarketplaceConfig(
            api_key=os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_demo'),
            api_secret=os.getenv('STRIPE_SECRET_KEY', 'sk_test_demo'),
            sandbox=os.getenv('STRIPE_SANDBOX', 'true').lower() == 'true'
        )
    
    def get_config(self, marketplace: str) -> Optional[MarketplaceConfig]:
        """Get configuration for specific marketplace"""
        return self.configs.get(marketplace.lower())
    
    def is_production_ready(self, marketplace: str) -> bool:
        """Check if marketplace configuration is production ready"""
        config = self.get_config(marketplace)
        if not config:
            return False
        
        # Check if using demo/placeholder values
        demo_values = ['demo_', 'YOUR_', 'test_', 'pk_test_', 'sk_test_']
        
        for demo_value in demo_values:
            if (demo_value in config.api_key or 
                demo_value in config.api_secret or 
                (config.supplier_id and demo_value in config.supplier_id)):
                return False
        
        return True
    
    def get_production_ready_marketplaces(self) -> list:
        """Get list of production-ready marketplaces"""
        ready_marketplaces = []
        for marketplace in self.configs.keys():
            if self.is_production_ready(marketplace):
                ready_marketplaces.append(marketplace)
        return ready_marketplaces
    
    def get_demo_marketplaces(self) -> list:
        """Get list of marketplaces using demo credentials"""
        demo_marketplaces = []
        for marketplace in self.configs.keys():
            if not self.is_production_ready(marketplace):
                demo_marketplaces.append(marketplace)
        return demo_marketplaces

# Global instance
marketplace_config = MarketplaceConfigManager()

# Convenience functions
def get_marketplace_config(marketplace: str) -> Optional[MarketplaceConfig]:
    """Get marketplace configuration"""
    return marketplace_config.get_config(marketplace)

def is_marketplace_production_ready(marketplace: str) -> bool:
    """Check if marketplace is production ready"""
    return marketplace_config.is_production_ready(marketplace)

# Environment setup helper
def create_env_template():
    """Create .env template file with all required variables"""
    env_template = """# Marketplace API Configuration
# Copy this file to .env and fill in your actual API credentials

# Trendyol
TRENDYOL_API_KEY=your_trendyol_api_key
TRENDYOL_API_SECRET=your_trendyol_api_secret
TRENDYOL_SUPPLIER_ID=your_supplier_id
TRENDYOL_SANDBOX=true

# N11
N11_API_KEY=your_n11_api_key
N11_API_SECRET=your_n11_api_secret
N11_SANDBOX=true

# Hepsiburada
HEPSIBURADA_API_KEY=your_hepsiburada_api_key
HEPSIBURADA_API_SECRET=your_hepsiburada_api_secret
HEPSIBURADA_MERCHANT_ID=your_merchant_id
HEPSIBURADA_SANDBOX=true

# GittiGidiyor
GITTIGIDIYOR_API_KEY=your_gittigidiyor_api_key
GITTIGIDIYOR_API_SECRET=your_gittigidiyor_api_secret
GITTIGIDIYOR_SANDBOX=true

# Çiçeksepeti
CICEKSEPETI_API_KEY=your_ciceksepeti_api_key
CICEKSEPETI_API_SECRET=your_ciceksepeti_api_secret
CICEKSEPETI_SANDBOX=true

# Amazon
AMAZON_ACCESS_KEY=your_amazon_access_key
AMAZON_SECRET_KEY=your_amazon_secret_key
AMAZON_SELLER_ID=your_seller_id
AMAZON_SANDBOX=true

# eBay
EBAY_APP_ID=your_ebay_app_id
EBAY_CERT_ID=your_ebay_cert_id
EBAY_SANDBOX=true

# Etsy
ETSY_API_KEY=your_etsy_api_key
ETSY_API_SECRET=your_etsy_api_secret
ETSY_SANDBOX=true

# AliExpress
ALIEXPRESS_APP_KEY=your_aliexpress_app_key
ALIEXPRESS_APP_SECRET=your_aliexpress_app_secret
ALIEXPRESS_SANDBOX=true

# Payment Gateways

# İyzico
IYZICO_API_KEY=your_iyzico_api_key
IYZICO_SECRET_KEY=your_iyzico_secret_key
IYZICO_SANDBOX=true

# PayTR
PAYTR_MERCHANT_ID=your_paytr_merchant_id
PAYTR_MERCHANT_KEY=your_paytr_merchant_key
PAYTR_SANDBOX=true

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_SANDBOX=true

# Database Configuration
DATABASE_URL=sqlite:///storage/database/app.db
DATABASE_POOL_SIZE=10

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_USE_TLS=true

# Security
SECRET_KEY=your_very_secret_key_here_change_in_production
JWT_SECRET_KEY=your_jwt_secret_key_here

# Application
FLASK_ENV=development
DEBUG=true
"""
    
    return env_template

if __name__ == "__main__":
    # Create .env template if run directly
    template = create_env_template()
    with open('.env.template', 'w') as f:
        f.write(template)
    print("✅ Created .env.template file")
    
    # Show current configuration status
    print("\n📊 Marketplace Configuration Status:")
    print("=" * 50)
    
    ready = marketplace_config.get_production_ready_marketplaces()
    demo = marketplace_config.get_demo_marketplaces()
    
    if ready:
        print("✅ Production Ready:")
        for marketplace in ready:
            print(f"   - {marketplace.title()}")
    
    if demo:
        print("\n⚠️  Using Demo Credentials:")
        for marketplace in demo:
            print(f"   - {marketplace.title()}")
    
    print(f"\n📈 Total Marketplaces: {len(marketplace_config.configs)}")
    print(f"✅ Production Ready: {len(ready)}")
    print(f"⚠️  Demo Mode: {len(demo)}")