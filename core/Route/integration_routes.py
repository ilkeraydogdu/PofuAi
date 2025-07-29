"""
Enterprise Integration Routes
PraPazar entegrasyon sistemi için enterprise seviyesinde route'lar
"""

from flask import Blueprint
from app.Controllers.IntegrationController import integration_controller

def register_integration_routes(app):
    """Entegrasyon route'larını kaydet"""
    
    # Integration Blueprint
    integration_bp = Blueprint('integration', __name__, url_prefix='/api/integrations')
    
    # ===== ENTEGRASYON YÖNETİMİ =====
    
    @integration_bp.route('/', methods=['GET'])
    def list_integrations():
        """Tüm entegrasyonları listele"""
        return integration_controller.list_integrations()
    
    @integration_bp.route('/<integration_name>', methods=['GET'])
    def get_integration(integration_name):
        """Belirli bir entegrasyonu getir"""
        return integration_controller.get_integration(integration_name)
    
    @integration_bp.route('/', methods=['POST'])
    def register_integration():
        """Yeni entegrasyon kaydet"""
        return integration_controller.register_integration()
    
    @integration_bp.route('/<integration_name>/sync', methods=['POST'])
    def sync_integration(integration_name):
        """Entegrasyon senkronizasyonu"""
        return integration_controller.sync_integration(integration_name)
    
    @integration_bp.route('/bulk-sync', methods=['POST'])
    def bulk_sync():
        """Toplu senkronizasyon"""
        return integration_controller.bulk_sync()
    
    @integration_bp.route('/<integration_name>/status', methods=['PUT'])
    def update_integration_status(integration_name):
        """Entegrasyon durumunu güncelle"""
        return integration_controller.update_integration_status(integration_name)
    
    @integration_bp.route('/<integration_name>/metrics', methods=['GET'])
    def get_integration_metrics(integration_name):
        """Entegrasyon metriklerini getir"""
        return integration_controller.get_integration_metrics(integration_name)
    
    @integration_bp.route('/health', methods=['GET'])
    def get_system_health():
        """Sistem sağlık durumu"""
        return integration_controller.get_system_health()
    
    # ===== AI ENDPOINTS =====
    
    @integration_bp.route('/ai/optimize-pricing', methods=['POST'])
    def optimize_pricing():
        """AI fiyat optimizasyonu"""
        return integration_controller.optimize_pricing()
    
    @integration_bp.route('/ai/predict-stock', methods=['POST'])
    def predict_stock():
        """AI stok tahmini"""
        return integration_controller.predict_stock()
    
    @integration_bp.route('/ai/forecast-sales', methods=['POST'])
    def forecast_sales():
        """AI satış tahmini"""
        return integration_controller.forecast_sales()
    
    @integration_bp.route('/ai/train-models', methods=['POST'])
    def train_ai_models():
        """AI modellerini eğit"""
        return integration_controller.train_ai_models()
    
    @integration_bp.route('/ai/status', methods=['GET'])
    def get_ai_status():
        """AI sistem durumu"""
        return integration_controller.get_ai_status()
    
    # ===== WEBHOOK ENDPOINTS =====
    
    @integration_bp.route('/<integration_name>/webhook', methods=['POST'])
    def webhook_handler(integration_name):
        """Webhook handler"""
        return integration_controller.webhook_handler(integration_name)
    
    # ===== UTILITY ENDPOINTS =====
    
    @integration_bp.route('/cleanup', methods=['POST'])
    def cleanup_old_data():
        """Eski verileri temizle"""
        return integration_controller.cleanup_old_data()
    
    @integration_bp.route('/initialize', methods=['POST'])
    def initialize_services():
        """Servisleri başlat"""
        return integration_controller.initialize_services()
    
    # Blueprint'i app'e kaydet
    app.register_blueprint(integration_bp)
    
    # ===== MARKETPLACE ENTEGRASYONLARI =====
    
    marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/api/marketplace')
    
    @marketplace_bp.route('/trendyol/sync', methods=['POST'])
    def trendyol_sync():
        """Trendyol senkronizasyonu"""
        return integration_controller.sync_integration('trendyol')
    
    @marketplace_bp.route('/hepsiburada/sync', methods=['POST'])
    def hepsiburada_sync():
        """Hepsiburada senkronizasyonu"""
        return integration_controller.sync_integration('hepsiburada')
    
    @marketplace_bp.route('/n11/sync', methods=['POST'])
    def n11_sync():
        """N11 senkronizasyonu"""
        return integration_controller.sync_integration('n11')
    
    @marketplace_bp.route('/amazon/sync', methods=['POST'])
    def amazon_sync():
        """Amazon senkronizasyonu"""
        return integration_controller.sync_integration('amazon_tr')
    
    @marketplace_bp.route('/pttavm/sync', methods=['POST'])
    def pttavm_sync():
        """PTT AVM senkronizasyonu"""
        return integration_controller.sync_integration('pttavm')
    
    app.register_blueprint(marketplace_bp)
    
    # ===== E-COMMERCE ENTEGRASYONLARI =====
    
    ecommerce_bp = Blueprint('ecommerce', __name__, url_prefix='/api/ecommerce')
    
    @ecommerce_bp.route('/woocommerce/sync', methods=['POST'])
    def woocommerce_sync():
        """WooCommerce senkronizasyonu"""
        return integration_controller.sync_integration('woocommerce')
    
    @ecommerce_bp.route('/shopify/sync', methods=['POST'])
    def shopify_sync():
        """Shopify senkronizasyonu"""
        return integration_controller.sync_integration('shopify')
    
    @ecommerce_bp.route('/magento/sync', methods=['POST'])
    def magento_sync():
        """Magento senkronizasyonu"""
        return integration_controller.sync_integration('magento')
    
    @ecommerce_bp.route('/ticimax/sync', methods=['POST'])
    def ticimax_sync():
        """Ticimax senkronizasyonu"""
        return integration_controller.sync_integration('ticimax')
    
    app.register_blueprint(ecommerce_bp)
    
    # ===== CARGO ENTEGRASYONLARI =====
    
    cargo_bp = Blueprint('cargo', __name__, url_prefix='/api/cargo')
    
    @cargo_bp.route('/yurtici/sync', methods=['POST'])
    def yurtici_sync():
        """Yurtiçi Kargo senkronizasyonu"""
        return integration_controller.sync_integration('yurtici')
    
    @cargo_bp.route('/aras/sync', methods=['POST'])
    def aras_sync():
        """Aras Kargo senkronizasyonu"""
        return integration_controller.sync_integration('aras')
    
    @cargo_bp.route('/mng/sync', methods=['POST'])
    def mng_sync():
        """MNG Kargo senkronizasyonu"""
        return integration_controller.sync_integration('mng')
    
    @cargo_bp.route('/ptt/sync', methods=['POST'])
    def ptt_sync():
        """PTT Kargo senkronizasyonu"""
        return integration_controller.sync_integration('ptt')
    
    app.register_blueprint(cargo_bp)
    
    # ===== INVOICE ENTEGRASYONLARI =====
    
    invoice_bp = Blueprint('invoice', __name__, url_prefix='/api/invoice')
    
    @invoice_bp.route('/qnb-efatura/sync', methods=['POST'])
    def qnb_efatura_sync():
        """QNB E-Fatura senkronizasyonu"""
        return integration_controller.sync_integration('qnb_efatura')
    
    @invoice_bp.route('/nilvera/sync', methods=['POST'])
    def nilvera_sync():
        """Nilvera E-Fatura senkronizasyonu"""
        return integration_controller.sync_integration('nilvera')
    
    @invoice_bp.route('/foriba/sync', methods=['POST'])
    def foriba_sync():
        """Foriba E-Fatura senkronizasyonu"""
        return integration_controller.sync_integration('foriba')
    
    app.register_blueprint(invoice_bp)
    
    # ===== FULFILLMENT ENTEGRASYONLARI =====
    
    fulfillment_bp = Blueprint('fulfillment', __name__, url_prefix='/api/fulfillment')
    
    @fulfillment_bp.route('/oplog/sync', methods=['POST'])
    def oplog_sync():
        """Oplog Fulfillment senkronizasyonu"""
        return integration_controller.sync_integration('oplog')
    
    @fulfillment_bp.route('/hepsilojistik/sync', methods=['POST'])
    def hepsilojistik_sync():
        """Hepsilojistik Fulfillment senkronizasyonu"""
        return integration_controller.sync_integration('hepsilojistik')
    
    @fulfillment_bp.route('/navlungo/sync', methods=['POST'])
    def navlungo_sync():
        """Navlungo Fulfillment senkronizasyonu"""
        return integration_controller.sync_integration('navlungo')
    
    app.register_blueprint(fulfillment_bp)
    
    # ===== ACCOUNTING ENTEGRASYONLARI =====
    
    accounting_bp = Blueprint('accounting', __name__, url_prefix='/api/accounting')
    
    @accounting_bp.route('/logo/sync', methods=['POST'])
    def logo_sync():
        """Logo entegrasyonu"""
        return integration_controller.sync_integration('logo')
    
    @accounting_bp.route('/mikro/sync', methods=['POST'])
    def mikro_sync():
        """Mikro entegrasyonu"""
        return integration_controller.sync_integration('mikro')
    
    @accounting_bp.route('/netsis/sync', methods=['POST'])
    def netsis_sync():
        """Netsis entegrasyonu"""
        return integration_controller.sync_integration('netsis')
    
    app.register_blueprint(accounting_bp)
    
    # ===== SOCIAL MEDIA ENTEGRASYONLARI =====
    
    social_bp = Blueprint('social', __name__, url_prefix='/api/social')
    
    @social_bp.route('/facebook-shop/sync', methods=['POST'])
    def facebook_shop_sync():
        """Facebook Shop senkronizasyonu"""
        return integration_controller.sync_integration('facebook_shop')
    
    @social_bp.route('/instagram-shop/sync', methods=['POST'])
    def instagram_shop_sync():
        """Instagram Shop senkronizasyonu"""
        return integration_controller.sync_integration('instagram_shop')
    
    @social_bp.route('/google-merchant/sync', methods=['POST'])
    def google_merchant_sync():
        """Google Merchant senkronizasyonu"""
        return integration_controller.sync_integration('google_merchant')
    
    app.register_blueprint(social_bp)
    
    # ===== INTERNATIONAL ENTEGRASYONLARI =====
    
    international_bp = Blueprint('international', __name__, url_prefix='/api/international')
    
    @international_bp.route('/amazon-global/sync', methods=['POST'])
    def amazon_global_sync():
        """Amazon Global senkronizasyonu"""
        return integration_controller.sync_integration('amazon_global')
    
    @international_bp.route('/ebay/sync', methods=['POST'])
    def ebay_sync():
        """eBay senkronizasyonu"""
        return integration_controller.sync_integration('ebay')
    
    @international_bp.route('/aliexpress/sync', methods=['POST'])
    def aliexpress_sync():
        """AliExpress senkronizasyonu"""
        return integration_controller.sync_integration('aliexpress')
    
    app.register_blueprint(international_bp)
    
    # ===== BATCH OPERATIONS =====
    
    batch_bp = Blueprint('batch', __name__, url_prefix='/api/batch')
    
    @batch_bp.route('/sync-all-marketplaces', methods=['POST'])
    def sync_all_marketplaces():
        """Tüm pazaryerlerini senkronize et"""
        marketplaces = [
            'trendyol', 'hepsiburada', 'n11', 'amazon_tr', 'pttavm',
            'ciceksepeti', 'akakce', 'cimri', 'modanisa'
        ]
        return integration_controller.bulk_sync()
    
    @batch_bp.route('/sync-all-cargo', methods=['POST'])
    def sync_all_cargo():
        """Tüm kargo şirketlerini senkronize et"""
        cargo_companies = [
            'yurtici', 'aras', 'mng', 'ptt', 'ups', 'surat'
        ]
        return integration_controller.bulk_sync()
    
    @batch_bp.route('/sync-all-invoices', methods=['POST'])
    def sync_all_invoices():
        """Tüm e-fatura sistemlerini senkronize et"""
        invoice_systems = [
            'qnb_efatura', 'nilvera', 'foriba', 'uyumsoft'
        ]
        return integration_controller.bulk_sync()
    
    app.register_blueprint(batch_bp)
    
    # ===== MONITORING ENDPOINTS =====
    
    monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')
    
    @monitoring_bp.route('/status', methods=['GET'])
    def get_system_status():
        """Sistem durumu"""
        return integration_controller.get_system_health()
    
    @monitoring_bp.route('/metrics', methods=['GET'])
    def get_system_metrics():
        """Sistem metrikleri"""
        return integration_controller.get_system_health()
    
    @monitoring_bp.route('/ai-status', methods=['GET'])
    def get_ai_system_status():
        """AI sistem durumu"""
        return integration_controller.get_ai_status()
    
    app.register_blueprint(monitoring_bp)
    
    # ===== WEBHOOK ENDPOINTS =====
    
    webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')
    
    @webhook_bp.route('/trendyol', methods=['POST'])
    def trendyol_webhook():
        """Trendyol webhook"""
        return integration_controller.webhook_handler('trendyol')
    
    @webhook_bp.route('/hepsiburada', methods=['POST'])
    def hepsiburada_webhook():
        """Hepsiburada webhook"""
        return integration_controller.webhook_handler('hepsiburada')
    
    @webhook_bp.route('/n11', methods=['POST'])
    def n11_webhook():
        """N11 webhook"""
        return integration_controller.webhook_handler('n11')
    
    @webhook_bp.route('/amazon', methods=['POST'])
    def amazon_webhook():
        """Amazon webhook"""
        return integration_controller.webhook_handler('amazon_tr')
    
    @webhook_bp.route('/yurtici', methods=['POST'])
    def yurtici_webhook():
        """Yurtiçi Kargo webhook"""
        return integration_controller.webhook_handler('yurtici')
    
    @webhook_bp.route('/aras', methods=['POST'])
    def aras_webhook():
        """Aras Kargo webhook"""
        return integration_controller.webhook_handler('aras')
    
    app.register_blueprint(webhook_bp)
    
    print("✅ Integration routes registered successfully")
    
    return True