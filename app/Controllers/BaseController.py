"""
Base Controller
Tüm controller'lar için temel sınıf
"""
from typing import Dict, Any, Optional, Union
from core.Config.config import get_config
from core.Services.service_container import ServiceContainer
from flask import request, session, render_template, jsonify, redirect, make_response
import os
from core.Config.config import Config
from core.Helpers import validator
from core.Services.base_service import BaseService
import json

class BaseController:
    """Tüm controller'lar için temel sınıf"""
    
    def __init__(self):
        self.request = request
        self.validator = validator
        self.config = Config()
        self.logger = BaseService.get_logger()
        self.response_data = {}
        self.services = ServiceContainer()
    
    def set_request(self, request):
        """
        Request nesnesini ayarla
        
        Args:
            request (Flask.Request): HTTP request nesnesi
        """
        self.request = request
        
        # Güvenli JSON işleme ekle
        if not hasattr(self.request, 'safe_json'):
            def safe_json():
                """JSON verisini güvenli bir şekilde döndürür"""
                if request.is_json:
                    try:
                        return request.get_json(silent=True)
                    except:
                        return {}
                return {}
            
            self.request.safe_json = safe_json
            
        return self
    
    def set_response(self, response):
        """Response nesnesini ayarla"""
        self.response = response
        return self
    
    def get_input(self, key: str = None, default: Any = None) -> Any:
        """Request input'unu al"""
        if not self.request:
            return default
        
        if key is None:
            return self.request.get_json() if self.request.is_json else self.request.form.to_dict()
        
        return self.request.args.get(key) or self.request.form.get(key) or default
    
    def get_json_input(self):
        """Request'ten JSON veriyi al"""
        try:
            # İstek JSON formatında mı?
            if self.request.is_json:
                return self.request.get_json()
                
            # Form verisi varsa
            if self.request.method in ['POST', 'PUT']:
                # Form içinde JSON string kontrolü
                if self.request.form:
                    if 'json' in self.request.form:
                        try:
                            return json.loads(self.request.form.get('json'))
                        except:
                            pass
                    # Form verisini dict olarak döndür
                    return self.request.form.to_dict()
                
                # Raw body'i JSON olarak parse etmeyi dene
                if self.request.data:
                    try:
                        return json.loads(self.request.data)
                    except:
                        # JSON olarak parse edilemezse body'i string olarak döndür
                        return {"body": self.request.data.decode('utf-8', errors='ignore')}
            
            # URL parametrelerini dict olarak döndür
            if self.request.args:
                return self.request.args.to_dict()
                
            return {}
        except Exception as e:
            self.log('error', f'Input parse error: {str(e)}')
            return {}
    
    def get_all_input(self) -> Dict[str, Any]:
        """Tüm input'ları al"""
        if not self.request:
            return {}
        
        data = {}
        # URL parametrelerini ekle
        if self.request.args:
            data.update(self.request.args.to_dict())
        
        # Form verilerini ekle
        if self.request.form:
            form_data = self.request.form.to_dict()
            # Form veri içinde json string varsa parse et
            if 'json' in form_data:
                try:
                    json_data = json.loads(form_data['json'])
                    if isinstance(json_data, dict):
                        data.update(json_data)
                        # json anahtarını silmeyi unutma
                        form_data.pop('json')
                except:
                    pass
            data.update(form_data)
        
        # JSON verisini ekle
        if self.request.is_json:
            json_data = self.request.get_json() or {}
            if isinstance(json_data, dict):
                data.update(json_data)
        
        # JSON olmayan raw body varsa parse etmeyi dene
        elif self.request.data and not data and self.request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body_data = json.loads(self.request.data)
                if isinstance(body_data, dict):
                    data.update(body_data)
            except:
                pass
        
        return data
    
    def validate_input(self, data: Dict[str, Any], rules: Dict[str, str]) -> Dict[str, Any]:
        """Input'ları doğrula"""
        from core.Services.validators import Validator
        validator = Validator()
        return validator.validate(data, rules)
    
    def json_response(self, data: Any, status: int = 200, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """JSON response döndür"""
        from flask import jsonify
        
        response = {
            'success': 200 <= status < 300,
            'data': data
        }
        
        return jsonify(response), status
    
    def error_response(self, message: str, status: int = 400, errors: Dict[str, Any] = None) -> Dict[str, Any]:
        """Hata response'u döndür"""
        from flask import jsonify
        
        response = {
            'success': False,
            'message': message
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), status
    
    def redirect(self, url: str, status: int = 302) -> Dict[str, Any]:
        """Redirect response'u döndür"""
        from flask import redirect as flask_redirect
        return flask_redirect(url, code=status)
    
    def view(self, template: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """View response'u döndür"""
        from flask import render_template
        
        data = data or {}
        
        # Global data ekle
        data['app_name'] = self.config.get('app.name', 'PofuAi')
        data['app_env'] = self.config.get('app.env', 'production')
        data['app_debug'] = self.config.get('app.debug', False)
        
        # Session varsa ekle
        if hasattr(self.request, 'session'):
            data['session'] = self.request.session
            
        return render_template(f"{template}.html", **data)
    
    def render_component(self, component_name: str, method: str = 'render_examples', **kwargs) -> str:
        """Component render et"""
        try:
            # Yeni component servisini kullan
            from core.Services.ComponentService import ComponentService
            component_service = ComponentService()
            
            if component_service.component_exists(component_name):
                # Component verisi hazırla
                from core.Services.UIService import UIService
                ui_service = UIService()
                
                # Uygun component verisi hazırla ve şablonu render et
                component_data = kwargs
                return component_service.render_component(component_name, component_data)
            
            return f"<div>Component bulunamadı: {component_name}</div>"
        except Exception as e:
            return f"<div>Component yüklenemedi: {component_name} - Hata: {str(e)}</div>"
    
    def log(self, level: str, message: str, context: Dict[str, Any] = None):
        """Log kaydet"""
        if not self.logger:
            return
        
        log_data = {
            'ip': self.get_client_ip(),
            'user_id': self.get_user_id(),
            'url': self.request.path,
            'method': self.request.method
        }
        
        if context:
            log_data.update(context)
        
        if level == 'debug':
            self.logger.debug(message, extra=log_data)
        elif level == 'info':
            self.logger.info(message, extra=log_data)
        elif level == 'warning':
            self.logger.warning(message, extra=log_data)
        elif level == 'error':
            self.logger.error(message, extra=log_data)
        elif level == 'critical':
            self.logger.critical(message, extra=log_data)
        else:
            self.logger.info(message, extra=log_data)
    
    def get_user(self):
        """Mevcut kullanıcıyı al"""
        from app.Models.User import User
        user_id = self.get_user_id()
        if not user_id:
            return None
        return User.find(user_id)
    
    def is_admin(self) -> bool:
        """Admin kontrolü yap"""
        user = self.get_user()
        if not user:
            return False
        return user.is_admin
    
    def require_auth(self):
        """Oturum kontrolü yap"""
        user = self.get_user()
        if not user:
            if self.is_api_request():
                return self.error_response('Unauthorized', 401)
            else:
                return self.redirect('/login')
        return user
    
    def require_role(self, role: str):
        """Rol kontrolü yap"""
        user = self.require_auth()
        if isinstance(user, dict):  # Redirect yanıtı
            return user
        
        if not user.has_role(role):
            if self.is_api_request():
                return self.error_response('Forbidden', 403)
            else:
                return self.redirect('/unauthorized')
        return user
    
    def is_authenticated(self):
        """Oturum açılmış mı kontrolü"""
        return self.get_user() is not None
    
    def set_user_id(self, user_id):
        """Session'a user_id set et"""
        from flask import session
        session['user_id'] = user_id
        return self
    
    def clear_session(self):
        """Session'ı temizle"""
        from flask import session
        session.clear()
        return self
    
    def get_json_data(self, silent=True, force=True):
        """JSON verisi al"""
        try:
            if self.request.is_json:
                return self.request.get_json(silent=silent, force=force)
            
            # Form verisi varsa, 'json' field kontrolü yap
            if self.request.form and 'json' in self.request.form:
                json_str = self.request.form['json']
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            # Raw body'i JSON olarak parse etmeyi dene
            if self.request.data:
                data = self.request.data.decode('utf-8', errors='ignore')
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    pass
            
            # URL parametrelerini dict olarak döndür
            if self.request.args:
                return self.request.args.to_dict()
                    
            return {}
        except Exception as e:
            if not silent:
                raise e
            return {}
    
    # CRUD metotları
    
    def index(self):
        """Index metodunu uygula"""
        return self.error_response('Not Implemented', 501)
    
    def show(self, id: Union[int, str]):
        """Show metodunu uygula"""
        return self.error_response('Not Implemented', 501)
    
    def create(self):
        """Create metodunu uygula"""
        return self.error_response('Not Implemented', 501)
    
    def store(self):
        """Store metodunu uygula"""
        return self.error_response('Not Implemented', 501)
    
    def edit(self, id: Union[int, str]):
        """Edit metodunu uygula"""
        return self.error_response('Not Implemented', 501)
    
    def update(self, id: Union[int, str]):
        """Update metodunu uygula"""
        return self.error_response('Not Implemented', 501)
    
    def delete(self, id: Union[int, str]):
        """Delete metodunu uygula"""
        return self.error_response('Not Implemented', 501)
    
    def get_client_ip(self):
        """Gerçek IP adresini al"""
        if self.request:
            return self.request.headers.get('X-Forwarded-For', self.request.remote_addr)
        return '0.0.0.0'
    
    def get_user_id(self):
        """Session'dan user_id al"""
        from flask import session
        return session.get('user_id')
    
    def render_view(self, view_name, data=None):
        """View render et"""
        data = data or {}
        
        # API istekleri için JSON yanıt döndür
        if self.is_api_request():
            return self.json_response(data)
        
        # Normal isteklere view döndür
        return self.view(view_name, data)
    
    def is_api_request(self):
        """API isteği mi kontrolü"""
        return (
            self.request.path.startswith('/api/') or
            self.request.headers.get('Accept') == 'application/json' or
            self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        )
    
    def api_response(self, data=None, error=None, status=200):
        """API yanıtı döndür"""
        response = {
            'success': error is None,
        }
        
        if data is not None:
            response['data'] = data
            
        if error is not None:
            response['error'] = error
            
        return jsonify(response), status
    
    def response_with_view_fallback(self, data=None, view_name=None, status=200):
        """API isteği veya view isteğine göre yanıt döndür"""
        if self.is_api_request():
            return self.json_response(data, status)
        
        if view_name:
            return self.view(view_name, data)
            
        # Varsayılan olarak JSON yanıt döndür
        return self.json_response(data, status) 