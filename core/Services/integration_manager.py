"""
Integration Manager - Central hub for all integrations
Manages initialization and access to all marketplace, payment, and service integrations
"""

from typing import Dict, Any, Optional, Type, List
from enum import Enum
import logging
import os
from datetime import datetime

# Import all integration classes
from .base_integration import BaseIntegration, IntegrationError

# Marketplace APIs
from .trendyol_marketplace_api import TrendyolMarketplaceAPI
from .hepsiburada_marketplace_api import HepsiburadaMarketplaceAPI
from .n11_marketplace_api import N11MarketplaceAPI
from .amazon_tr_marketplace_api import AmazonTRMarketplaceAPI
from .ciceksepeti_marketplace_api import CiceksepetiMarketplaceAPI
from .pttavm_marketplace_api import PTTAVMMarketplaceAPI

# Payment APIs
from .iyzico_payment_api import IyzicoPaymentAPI
from .paytr_payment_api import PayTRPaymentAPI
from .stripe_payment_api import StripePaymentAPI
from .paypal_payment_api import PayPalPaymentAPI

# E-Invoice APIs
from .uyumsoft_einvoice_api import UyumsoftEInvoiceAPI
from .logo_einvoice_api import LogoEInvoiceAPI
from .mikro_einvoice_api import MikroEInvoiceAPI
from .foriba_einvoice_api import ForibaEInvoiceAPI
from .edmbilisim_einvoice_api import EDMBilisimEInvoiceAPI
from .izibiz_einvoice_api import IzibizEInvoiceAPI
from .fitbulut_einvoice_api import FitbulutEInvoiceAPI
from .kolaysoft_einvoice_api import KolaysoftEInvoiceAPI
from .nesbilgi_einvoice_api import NesbilgiEInvoiceAPI
from .edonusum_einvoice_api import EDonusumEInvoiceAPI
from .ingbank_einvoice_api import INGBankEInvoiceAPI
from .qnbfinansbank_einvoice_api import QNBFinansbankEInvoiceAPI
from .protel_einvoice_api import ProtelEInvoiceAPI
from .sovos_einvoice_api import SovosEInvoiceAPI
from .digital_planet_einvoice_api import DigitalPlanetEInvoiceAPI

# Accounting/ERP APIs
from .logo_tiger_api import LogoTigerAPI
from .netsis_api import NetsisAPI
from .mikro_api import MikroAPI
from .eta_api import ETAAPI
from .zirve_api import ZirveAPI
from .orka_api import OrkaAPI
from .akınsoft_api import AkinsoftAPI
from .link_api import LinkAPI
from .uyumsoft_api import UyumsoftAPI
from .sentez_api import SentezAPI
from .dia_api import DiaAPI
from .vega_api import VegaAPI
from .workcube_api import WorkcubeAPI

# Pre-Accounting APIs
from .parasut_api import ParasutAPI
from .kolaybi_api import KolaybiAPI
from .muhasebetr_api import MuhasebeTRAPI
from .altinrota_api import AltinrotaAPI

# Cargo APIs
from .yurtici_kargo_api import YurticiKargoAPI
from .aras_kargo_api import ArasKargoAPI
from .mng_kargo_api import MNGKargoAPI
from .ptt_kargo_api import PTTKargoAPI
from .ups_kargo_api import UPSKargoAPI
from .sendeo_api import SendeoAPI
from .suratcargo_api import SuratCargoAPI
from .horoz_lojistik_api import HorozLojistikAPI
from .borusan_lojistik_api import BorusanLojistikAPI
from .ekol_lojistik_api import EkolLojistikAPI
from .netlog_lojistik_api import NetlogLojistikAPI
from .kargonet_api import KargonetAPI
from .kolay_gelsin_api import KolayGelsinAPI
from .trendyol_express_api import TrendyolExpressAPI
from .hepsijet_api import HepsiJetAPI
from .getir_api import GetirAPI
from .banabi_api import BanabiAPI

# Fulfillment APIs
from .octopus_api import OctopusAPI
from .shiphero_api import ShipheroAPI
from .fulfillmentbox_api import FulfillmentBoxAPI
from .deposco_api import DeposcoAPI
from .shipbob_api import ShipBobAPI

# Additional Marketplace APIs
from .epttavm_api import EPttAvmAPI
from .morhipo_api import MorhipoAPI
from .boyner_api import BoynerAPI
from .evidea_api import EvideaAPI
from .koton_api import KotonAPI
from .lcwaikiki_api import LCWaikikiAPI
from .defacto_api import DefactoAPI
from .mavi_api import MaviAPI
from .teknosa_api import TeknosaAPI
from .vatan_api import VatanAPI
from .mediamarkt_api import MediaMarktAPI
from .carrefoursa_api import CarrefourSAAPI
from .migros_sanal_market_api import MigrosSanalMarketAPI
from .a101_api import A101API
from .sok_market_api import SokMarketAPI
from .gratis_api import GratisAPI
from .watsons_api import WatsonsAPI
from .rossmann_api import RossmannAPI
from .koçtaş_api import KoctasAPI
from .bauhaus_api import BauhausAPI
from .ikea_api import IkeaAPI
from .adidas_api import AdidasAPI
from .nike_api import NikeAPI
from .decathlon_api import DecathlonAPI
from .intersport_api import IntersportAPI

# E-Commerce Platform APIs
from .ideasoft_api import IdeasoftAPI
from .tsoft_api import TSoftAPI
from .shopify_api import ShopifyAPI
from .woocommerce_api import WooCommerceAPI
from .magento_api import MagentoAPI
from .opencart_api import OpenCartAPI
from .prestashop_api import PrestaShopAPI

# International Marketplace APIs
from .etsy_api import EtsyAPI
from .ebay_api import EbayAPI
from .aliexpress_api import AliExpressAPI
from .wish_api import WishAPI
from .walmart_api import WalmartAPI

# Social Media Store APIs
from .facebook_shops_api import FacebookShopsAPI
from .instagram_shopping_api import InstagramShoppingAPI
from .tiktok_shop_api import TikTokShopAPI
from .pinterest_shopping_api import PinterestShoppingAPI

# SMS APIs
from .netgsm_api import NetGSMAPI
from .iletimerkezi_api import IletiMerkeziAPI
from .masgsm_api import MasGSMAPI
from .jetsms_api import JetSMSAPI
from .vatansms_api import VatanSMSAPI

# Email APIs
from .sendgrid_api import SendGridAPI
from .mailchimp_api import MailChimpAPI
from .mailgun_api import MailgunAPI
from .sendinblue_api import SendinBlueAPI
from .elastic_email_api import ElasticEmailAPI


class IntegrationType(Enum):
    """Integration types enumeration"""
    MARKETPLACE = "marketplace"
    ECOMMERCE = "ecommerce"
    PAYMENT = "payment"
    E_INVOICE = "e_invoice"
    ACCOUNTING_ERP = "accounting_erp"
    PRE_ACCOUNTING = "pre_accounting"
    CARGO = "cargo"
    FULFILLMENT = "fulfillment"
    SMS = "sms"
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    INTERNATIONAL = "international"
    RETAIL = "retail"


class IntegrationManager:
    """
    Central manager for all integrations
    Handles initialization, caching, and access to integration instances
    """
    
    # Integration class mapping
    INTEGRATION_CLASSES = {
        # Marketplace APIs
        'trendyol': TrendyolMarketplaceAPI,
        'hepsiburada': HepsiburadaMarketplaceAPI,
        'n11': N11MarketplaceAPI,
        'amazon_tr': AmazonTRMarketplaceAPI,
        'ciceksepeti': CiceksepetiMarketplaceAPI,
        'pttavm': PTTAVMMarketplaceAPI,
        'epttavm': EPttAvmAPI,
        'morhipo': MorhipoAPI,
        'boyner': BoynerAPI,
        'evidea': EvideaAPI,
        'koton': KotonAPI,
        'lcwaikiki': LCWaikikiAPI,
        'defacto': DefactoAPI,
        'mavi': MaviAPI,
        'teknosa': TeknosaAPI,
        'vatan': VatanAPI,
        'mediamarkt': MediaMarktAPI,
        'carrefoursa': CarrefourSAAPI,
        'migros_sanal_market': MigrosSanalMarketAPI,
        'a101': A101API,
        'sok_market': SokMarketAPI,
        'gratis': GratisAPI,
        'watsons': WatsonsAPI,
        'rossmann': RossmannAPI,
        'koçtaş': KoctasAPI,
        'bauhaus': BauhausAPI,
        'ikea': IkeaAPI,
        'adidas': AdidasAPI,
        'nike': NikeAPI,
        'decathlon': DecathlonAPI,
        'intersport': IntersportAPI,
        
        # E-Commerce Platforms
        'ideasoft': IdeasoftAPI,
        'tsoft': TSoftAPI,
        'shopify': ShopifyAPI,
        'woocommerce': WooCommerceAPI,
        'magento': MagentoAPI,
        'opencart': OpenCartAPI,
        'prestashop': PrestaShopAPI,
        
        # International Marketplaces
        'etsy': EtsyAPI,
        'ebay': EbayAPI,
        'aliexpress': AliExpressAPI,
        'wish': WishAPI,
        'walmart': WalmartAPI,
        
        # Social Media Stores
        'facebook_shops': FacebookShopsAPI,
        'instagram_shopping': InstagramShoppingAPI,
        'tiktok_shop': TikTokShopAPI,
        'pinterest_shopping': PinterestShoppingAPI,
        
        # Payment APIs
        'iyzico': IyzicoPaymentAPI,
        'paytr': PayTRPaymentAPI,
        'stripe': StripePaymentAPI,
        'paypal': PayPalPaymentAPI,
        
        # E-Invoice APIs
        'uyumsoft_einvoice': UyumsoftEInvoiceAPI,
        'logo_einvoice': LogoEInvoiceAPI,
        'mikro_einvoice': MikroEInvoiceAPI,
        'foriba': ForibaEInvoiceAPI,
        'edmbilisim': EDMBilisimEInvoiceAPI,
        'izibiz': IzibizEInvoiceAPI,
        'fitbulut': FitbulutEInvoiceAPI,
        'kolaysoft': KolaysoftEInvoiceAPI,
        'nesbilgi': NesbilgiEInvoiceAPI,
        'edonusum': EDonusumEInvoiceAPI,
        'ingbank_einvoice': INGBankEInvoiceAPI,
        'qnbfinansbank_einvoice': QNBFinansbankEInvoiceAPI,
        'protel': ProtelEInvoiceAPI,
        'sovos': SovosEInvoiceAPI,
        'digital_planet': DigitalPlanetEInvoiceAPI,
        
        # Accounting/ERP APIs
        'logo_tiger': LogoTigerAPI,
        'netsis': NetsisAPI,
        'mikro': MikroAPI,
        'eta': ETAAPI,
        'zirve': ZirveAPI,
        'orka': OrkaAPI,
        'akinsoft': AkinsoftAPI,
        'link': LinkAPI,
        'uyumsoft': UyumsoftAPI,
        'sentez': SentezAPI,
        'dia': DiaAPI,
        'vega': VegaAPI,
        'workcube': WorkcubeAPI,
        
        # Pre-Accounting APIs
        'parasut': ParasutAPI,
        'kolaybi': KolaybiAPI,
        'muhasebetr': MuhasebeTRAPI,
        'altinrota': AltinrotaAPI,
        
        # Cargo APIs
        'yurtici_kargo': YurticiKargoAPI,
        'aras_kargo': ArasKargoAPI,
        'mng_kargo': MNGKargoAPI,
        'ptt_kargo': PTTKargoAPI,
        'ups_kargo': UPSKargoAPI,
        'sendeo': SendeoAPI,
        'surat_kargo': SuratCargoAPI,
        'horoz_lojistik': HorozLojistikAPI,
        'borusan_lojistik': BorusanLojistikAPI,
        'ekol_lojistik': EkolLojistikAPI,
        'netlog_lojistik': NetlogLojistikAPI,
        'kargonet': KargonetAPI,
        'kolay_gelsin': KolayGelsinAPI,
        'trendyol_express': TrendyolExpressAPI,
        'hepsijet': HepsiJetAPI,
        'getir': GetirAPI,
        'banabi': BanabiAPI,
        
        # Fulfillment APIs
        'octopus': OctopusAPI,
        'shiphero': ShipheroAPI,
        'fulfillmentbox': FulfillmentBoxAPI,
        'deposco': DeposcoAPI,
        'shipbob': ShipBobAPI,
        
        # SMS APIs
        'netgsm': NetGSMAPI,
        'iletimerkezi': IletiMerkeziAPI,
        'masgsm': MasGSMAPI,
        'jetsms': JetSMSAPI,
        'vatansms': VatanSMSAPI,
        
        # Email APIs
        'sendgrid': SendGridAPI,
        'mailchimp': MailChimpAPI,
        'mailgun': MailgunAPI,
        'sendinblue': SendinBlueAPI,
        'elastic_email': ElasticEmailAPI
    }
    
    def __init__(self):
        """Initialize Integration Manager"""
        self.logger = logging.getLogger(__name__)
        self.integrations = {}  # Cache for initialized integrations
        self.credentials = {}   # Store for integration credentials
        
    def load_credentials_from_env(self):
        """Load all integration credentials from environment variables"""
        # Load marketplace credentials
        for integration_name in self.INTEGRATION_CLASSES.keys():
            prefix = integration_name.upper()
            
            # Common credential patterns
            api_key = os.getenv(f'{prefix}_API_KEY')
            api_secret = os.getenv(f'{prefix}_API_SECRET')
            
            if api_key:
                self.credentials[integration_name] = {
                    'api_key': api_key,
                    'api_secret': api_secret,
                    'username': os.getenv(f'{prefix}_USERNAME'),
                    'password': os.getenv(f'{prefix}_PASSWORD'),
                    'merchant_id': os.getenv(f'{prefix}_MERCHANT_ID'),
                    'seller_id': os.getenv(f'{prefix}_SELLER_ID'),
                    'supplier_id': os.getenv(f'{prefix}_SUPPLIER_ID'),
                    'branch_id': os.getenv(f'{prefix}_BRANCH_ID'),
                    'client_id': os.getenv(f'{prefix}_CLIENT_ID'),
                    'client_secret': os.getenv(f'{prefix}_CLIENT_SECRET'),
                    'refresh_token': os.getenv(f'{prefix}_REFRESH_TOKEN'),
                    'store_url': os.getenv(f'{prefix}_STORE_URL'),
                    'webhook_secret': os.getenv(f'{prefix}_WEBHOOK_SECRET')
                }
                
                # Clean up None values
                self.credentials[integration_name] = {
                    k: v for k, v in self.credentials[integration_name].items() 
                    if v is not None
                }
    
    def set_credentials(self, integration_name: str, credentials: Dict[str, Any]):
        """Set credentials for a specific integration"""
        if integration_name not in self.INTEGRATION_CLASSES:
            raise ValueError(f"Unknown integration: {integration_name}")
        
        self.credentials[integration_name] = credentials
        
        # If integration is already initialized, reinitialize with new credentials
        if integration_name in self.integrations:
            del self.integrations[integration_name]
    
    def get_integration(self, integration_name: str, 
                       credentials: Optional[Dict[str, Any]] = None,
                       sandbox: bool = False) -> BaseIntegration:
        """
        Get an integration instance
        
        Args:
            integration_name: Name of the integration
            credentials: Optional credentials (uses stored if not provided)
            sandbox: Whether to use sandbox/test mode
            
        Returns:
            Integration instance
        """
        if integration_name not in self.INTEGRATION_CLASSES:
            raise ValueError(f"Unknown integration: {integration_name}")
        
        # Create cache key
        cache_key = f"{integration_name}_{sandbox}"
        
        # Check cache
        if cache_key in self.integrations and not credentials:
            return self.integrations[cache_key]
        
        # Get credentials
        if not credentials:
            if integration_name not in self.credentials:
                raise ValueError(f"No credentials found for {integration_name}")
            credentials = self.credentials[integration_name]
        
        # Get integration class
        integration_class = self.INTEGRATION_CLASSES[integration_name]
        
        # Initialize integration
        try:
            integration = integration_class(credentials=credentials, sandbox=sandbox)
            
            # Cache if using stored credentials
            if not credentials or credentials == self.credentials.get(integration_name):
                self.integrations[cache_key] = integration
            
            self.logger.info(f"Initialized {integration_name} integration")
            return integration
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {integration_name}: {e}")
            raise IntegrationError(f"Failed to initialize {integration_name}: {e}")
    
    def test_integration(self, integration_name: str, 
                        credentials: Optional[Dict[str, Any]] = None,
                        sandbox: bool = True) -> Dict[str, Any]:
        """
        Test an integration connection
        
        Returns:
            Test result with success status and details
        """
        try:
            integration = self.get_integration(integration_name, credentials, sandbox)
            
            # Test connection
            is_valid = integration.validate_credentials()
            
            result = {
                'success': is_valid,
                'integration': integration_name,
                'sandbox': sandbox,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add integration-specific test results
            if hasattr(integration, 'get_test_info'):
                result['details'] = integration.get_test_info()
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'integration': integration_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def test_all_integrations(self, sandbox: bool = True) -> Dict[str, Dict[str, Any]]:
        """Test all configured integrations"""
        results = {}
        
        for integration_name in self.credentials.keys():
            results[integration_name] = self.test_integration(integration_name, sandbox=sandbox)
        
        return results
    
    def get_integration_info(self, integration_name: str) -> Dict[str, Any]:
        """Get information about an integration"""
        if integration_name not in self.INTEGRATION_CLASSES:
            raise ValueError(f"Unknown integration: {integration_name}")
        
        integration_class = self.INTEGRATION_CLASSES[integration_name]
        
        info = {
            'name': integration_name,
            'class': integration_class.__name__,
            'module': integration_class.__module__,
            'configured': integration_name in self.credentials,
            'cached': any(key.startswith(integration_name) for key in self.integrations.keys())
        }
        
        # Add docstring if available
        if integration_class.__doc__:
            info['description'] = integration_class.__doc__.strip()
        
        return info
    
    def list_integrations(self, integration_type: Optional[IntegrationType] = None) -> List[str]:
        """List available integrations"""
        all_integrations = list(self.INTEGRATION_CLASSES.keys())
        
        if not integration_type:
            return all_integrations
        
        # Filter by type (this would need type metadata in INTEGRATION_CLASSES)
        # For now, return all
        return all_integrations
    
    def clear_cache(self, integration_name: Optional[str] = None):
        """Clear integration cache"""
        if integration_name:
            # Clear specific integration
            keys_to_remove = [k for k in self.integrations.keys() if k.startswith(integration_name)]
            for key in keys_to_remove:
                del self.integrations[key]
        else:
            # Clear all
            self.integrations.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get integration manager statistics"""
        return {
            'total_integrations': len(self.INTEGRATION_CLASSES),
            'configured_integrations': len(self.credentials),
            'cached_instances': len(self.integrations),
            'integration_types': {
                'marketplace': len([k for k in self.INTEGRATION_CLASSES.keys() if 'marketplace' in k or k in ['trendyol', 'hepsiburada', 'n11', 'amazon_tr', 'ciceksepeti', 'pttavm']]),
                'payment': len([k for k in self.INTEGRATION_CLASSES.keys() if 'payment' in k or k in ['iyzico', 'paytr', 'stripe', 'paypal']]),
                'einvoice': len([k for k in self.INTEGRATION_CLASSES.keys() if 'einvoice' in k]),
                'accounting': len([k for k in self.INTEGRATION_CLASSES.keys() if k in ['logo_tiger', 'netsis', 'mikro', 'eta', 'zirve', 'orka', 'akinsoft', 'link', 'uyumsoft', 'sentez', 'dia', 'vega', 'workcube', 'parasut', 'kolaybi', 'muhasebetr', 'altinrota']]),
                'cargo': len([k for k in self.INTEGRATION_CLASSES.keys() if 'kargo' in k or 'cargo' in k or 'lojistik' in k or k in ['sendeo', 'kargonet', 'kolay_gelsin', 'trendyol_express', 'hepsijet', 'getir', 'banabi']]),
                'fulfillment': len([k for k in self.INTEGRATION_CLASSES.keys() if k in ['octopus', 'shiphero', 'fulfillmentbox', 'deposco', 'shipbob']]),
                'communication': len([k for k in self.INTEGRATION_CLASSES.keys() if k in ['netgsm', 'iletimerkezi', 'masgsm', 'jetsms', 'vatansms', 'sendgrid', 'mailchimp', 'mailgun', 'sendinblue', 'elastic_email']])
            }
        }


# Singleton instance
integration_manager = IntegrationManager()


def get_integration(integration_name: str, **kwargs) -> BaseIntegration:
    """Convenience function to get integration instance"""
    return integration_manager.get_integration(integration_name, **kwargs)


def test_integration(integration_name: str, **kwargs) -> Dict[str, Any]:
    """Convenience function to test integration"""
    return integration_manager.test_integration(integration_name, **kwargs)