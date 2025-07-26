"""
Error Showcase
Hata türleri ve hata yönetimi örnekleri
"""
from flask import Blueprint, jsonify, abort

def create_error_showcase_blueprint():
    """Hata örnekleri için blueprint"""
    bp = Blueprint('error_showcase', __name__, url_prefix='/examples/errors')
    
    @bp.route('/')
    def index():
        """Hata örnekleri ana sayfası"""
        error_examples = [
            {'name': '400 - Bad Request', 'url': '/examples/errors/400'},
            {'name': '401 - Unauthorized', 'url': '/examples/errors/401'},
            {'name': '403 - Forbidden', 'url': '/examples/errors/403'},
            {'name': '404 - Not Found', 'url': '/examples/errors/404'},
            {'name': '500 - Internal Server Error', 'url': '/examples/errors/500'},
            {'name': 'Python Exception', 'url': '/examples/errors/exception'},
            {'name': 'Database Error', 'url': '/examples/errors/db-error'},
            {'name': 'Validation Error', 'url': '/examples/errors/validation'},
            {'name': 'Custom Error', 'url': '/examples/errors/custom'},
        ]
        
        return jsonify({
            'title': 'Hata Örnekleri',
            'description': 'Çeşitli hata türleri ve hata yönetimi örnekleri',
            'examples': error_examples
        })
    
    @bp.route('/400')
    def bad_request():
        """400 Bad Request hatası örneği"""
        abort(400, description="Bad Request - İstek parametreleri geçersiz")
    
    @bp.route('/401')
    def unauthorized():
        """401 Unauthorized hatası örneği"""
        abort(401, description="Unauthorized - Kimlik doğrulama gerekli")
    
    @bp.route('/403')
    def forbidden():
        """403 Forbidden hatası örneği"""
        abort(403, description="Forbidden - Bu kaynağa erişim yetkiniz yok")
    
    @bp.route('/404')
    def not_found():
        """404 Not Found hatası örneği"""
        abort(404, description="Not Found - Sayfa bulunamadı")
    
    @bp.route('/500')
    def server_error():
        """500 Internal Server Error hatası örneği"""
        abort(500, description="Internal Server Error - Sunucu hatası")
    
    @bp.route('/exception')
    def python_exception():
        """Python exception örneği"""
        # Kasıtlı bir Python exception
        raise ValueError("Bu bir Python exception örneğidir")
    
    @bp.route('/db-error')
    def database_error():
        """Veritabanı hatası örneği"""
        class DatabaseError(Exception):
            pass
        
        raise DatabaseError("Veritabanı bağlantısı kurulamadı veya sorgu çalıştırılamadı")
    
    @bp.route('/validation')
    def validation_error():
        """Doğrulama hatası örneği"""
        errors = {
            'username': ['Username alanı gereklidir', 'Username en az 3 karakter olmalıdır'],
            'email': ['Geçerli bir email adresi giriniz'],
            'password': ['Şifre en az 6 karakter olmalıdır']
        }
        
        return jsonify({
            'status': 'error',
            'message': 'Validation Error - Form alanları doğrulanamadı',
            'errors': errors
        }), 422
    
    @bp.route('/custom')
    def custom_error():
        """Özel hata örneği"""
        # Özel bir hata durumu
        return jsonify({
            'status': 'error',
            'code': 'PAYMENT_FAILED',
            'message': 'Ödeme işlemi başarısız oldu',
            'details': {
                'reason': 'Yetersiz bakiye',
                'transaction_id': '1234567890',
                'time': '2023-05-15T10:30:15Z'
            }
        }), 400
    
    @bp.app_errorhandler(404)
    def handle_404(error):
        """404 hatalarını yakala"""
        if bp.request_context_stack.top is not None and bp.request_context_stack.top.request.path.startswith(bp.url_prefix):
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': 'Not Found - Sayfa bulunamadı',
                'path': bp.request_context_stack.top.request.path
            }), 404
    
    return bp

def get_error_showcase_bp():
    """Error showcase blueprint'ini döndür"""
    return create_error_showcase_blueprint() 