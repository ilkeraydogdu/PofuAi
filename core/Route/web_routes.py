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
    app.add_url_rule('/dashboard', 'dashboard.index', home_controller.index, methods=['GET'])
    
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
    
    # Dashboard API route'ları
    api_blueprint.add_url_rule('/dashboard/stats', 'dashboard_stats', lambda: home_controller.index(), methods=['GET'])
    api_blueprint.add_url_rule('/dashboard/activities', 'dashboard_activities', lambda: home_controller._get_recent_activities(), methods=['GET'])
    api_blueprint.add_url_rule('/dashboard/system', 'dashboard_system', lambda: home_controller._get_system_info(), methods=['GET'])
    
    # Notification API route'ları
    from app.Controllers.NotificationController import NotificationController
    notification_controller = NotificationController()
    
    api_blueprint.add_url_rule('/notifications', 'notifications_index', notification_controller.index, methods=['GET'])
    api_blueprint.add_url_rule('/notifications/unread-count', 'notifications_unread_count', notification_controller.get_unread_count, methods=['GET'])
    api_blueprint.add_url_rule('/notifications/<int:notification_id>/read', 'notifications_mark_read', notification_controller.mark_as_read, methods=['POST'])
    api_blueprint.add_url_rule('/notifications/mark-all-read', 'notifications_mark_all_read', notification_controller.mark_all_as_read, methods=['POST'])
    api_blueprint.add_url_rule('/notifications/<int:notification_id>/delete', 'notifications_delete', notification_controller.delete, methods=['DELETE'])
    
    # Search API route'ları
    from app.Controllers.SearchController import SearchController
    search_controller = SearchController()
    
    api_blueprint.add_url_rule('/search', 'search', search_controller.search, methods=['GET'])
    api_blueprint.add_url_rule('/search/suggestions', 'search_suggestions', search_controller.suggestions, methods=['GET'])
    
    # Admin route'ları
    from app.Controllers.AdminController import AdminController
    admin_controller = AdminController()
    
    admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')
    app.add_url_rule('/admin', 'admin.index', admin_controller.index, methods=['GET'])
    admin_blueprint.add_url_rule('/users', 'users', admin_controller.users, methods=['GET'])
    admin_blueprint.add_url_rule('/settings', 'settings', admin_controller.settings, methods=['GET', 'POST'])
    admin_blueprint.add_url_rule('/activities', 'activities', lambda: admin_controller.index(), methods=['GET'])
    admin_blueprint.add_url_rule('/reports', 'reports', lambda: admin_controller.index(), methods=['GET'])
    
    # Content Management route'ları
    from app.Controllers.ContentController import ContentController
    content_controller = ContentController()
    
    admin_blueprint.add_url_rule('/content', 'content_index', content_controller.index, methods=['GET'])
    admin_blueprint.add_url_rule('/content/create', 'content_create', content_controller.create, methods=['GET', 'POST'])
    admin_blueprint.add_url_rule('/content/<int:content_id>/edit', 'content_edit', content_controller.edit, methods=['GET', 'POST'])
    admin_blueprint.add_url_rule('/content/<int:content_id>/delete', 'content_delete', content_controller.delete, methods=['DELETE'])
    admin_blueprint.add_url_rule('/content/<int:content_id>/publish', 'content_publish', content_controller.publish, methods=['POST'])
    admin_blueprint.add_url_rule('/content/<int:content_id>/unpublish', 'content_unpublish', content_controller.unpublish, methods=['POST'])
    
    # Hata route'ları
    from app.Controllers.ErrorController import ErrorController
    error_controller = ErrorController()
    
    # Blueprint'leri kaydet
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(component_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(admin_blueprint)
    
    # Register advanced API routes
    try:
        from core.Route.advanced_api_routes import register_advanced_api_routes
        register_advanced_api_routes(app)
    except ImportError as e:
        print(f"Advanced API routes not available: {e}")
    
    # Register AI routes
    try:
        from core.Route.ai_routes import register_ai_routes
        register_ai_routes(app)
    except ImportError as e:
        print(f"AI routes not available: {e}")
    
    # Hata yönetimi
    app.register_error_handler(404, error_controller.error_404)
    app.register_error_handler(500, error_controller.error_500)

# Router dictionary
router = {
    'register_routes': register_routes
}
