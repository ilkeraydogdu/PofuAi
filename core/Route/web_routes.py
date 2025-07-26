"""
Web Routes
Tüm web route'larını tanımlar
"""
from flask import Blueprint, Flask, redirect

def register_routes(app: Flask):
    """
    Route'ları kaydet
    
    Args:
        app (Flask): Flask uygulaması
    """
    # Ana route'lar
    from app.Controllers.HomeController import HomeController
    home_controller = HomeController()
    
    app.add_url_rule('/', 'home.index', lambda: redirect('/auth/login'), methods=['GET'])
    
    # Auth route'ları
    from app.Controllers.AuthController import AuthController
    auth_controller = AuthController()
    
    auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')
    auth_blueprint.add_url_rule('/login', 'login', auth_controller.login, methods=['GET', 'POST'])
    auth_blueprint.add_url_rule('/register', 'register', auth_controller.register, methods=['GET', 'POST'])
    auth_blueprint.add_url_rule('/forgot-password', 'forgot_password', auth_controller.forgot_password, methods=['GET', 'POST'])
    auth_blueprint.add_url_rule('/reset-password', 'reset_password', auth_controller.reset_password, methods=['GET', 'POST'])
    auth_blueprint.add_url_rule('/logout', 'logout', auth_controller.logout, methods=['GET'])
    auth_blueprint.add_url_rule('/check-domain', 'check_domain', auth_controller.check_domain, methods=['GET'])
    
    # Component route'ları
    from app.Controllers.ComponentController import ComponentController
    component_controller = ComponentController()
    
    component_blueprint = Blueprint('components', __name__, url_prefix='/components')
    component_blueprint.add_url_rule('/', 'index', component_controller.index, methods=['GET'])
    component_blueprint.add_url_rule('/<component_name>', 'show_component', component_controller.show_component, methods=['GET'])
    
    # User route'ları
    from app.Controllers.UserController import UserController
    user_controller = UserController()
    
    user_blueprint = Blueprint('user', __name__, url_prefix='/user')
    user_blueprint.add_url_rule('/profile', 'profile', user_controller.profile, methods=['GET', 'POST'])
    
    # API route'ları
    from app.Controllers.ApiController import ApiController
    api_controller = ApiController()
    
    api_blueprint = Blueprint('api', __name__, url_prefix='/api')
    api_blueprint.add_url_rule('/', 'index', api_controller.index, methods=['GET'])
    api_blueprint.add_url_rule('/test', 'test', api_controller.test, methods=['GET'])
    
    # Admin route'ları
    from app.Controllers.AdminController import AdminController
    admin_controller = AdminController()
    
    admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')
    app.add_url_rule('/admin', 'admin.index', admin_controller.index, methods=['GET'])
    
    # Hata route'ları
    from app.Controllers.ErrorController import ErrorController
    error_controller = ErrorController()
    
    # Blueprint'leri kaydet
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(component_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(admin_blueprint)
    
    # Hata yönetimi
    app.register_error_handler(404, error_controller.error_404)
    app.register_error_handler(500, error_controller.error_500)

# Router dictionary
router = {
    'register_routes': register_routes
}
