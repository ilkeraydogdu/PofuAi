"""
User API Controller
User API endpoint'leri
"""
from app.Controllers.BaseController import BaseController
from app.Models.User import User
from core.Services.error_handler import error_handler

class UserApiController(BaseController):
    """User API controller'ı"""
    
    def index(self):
        """User listesi API"""
        try:
            # Admin kontrolü
            user = self.require_role('admin')
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Sayfalama parametreleri
            page = int(self.get_input('page', 1))
            per_page = int(self.get_input('per_page', 10))
            search = self.get_input('search', '')
            role = self.get_input('role', '')
            status = self.get_input('status', '')
            
            # Filtreleme
            query = User.query()
            
            if search:
                query = query.where_like('name', f'%{search}%')
            
            if role:
                query = query.where({'role': role})
            
            if status:
                query = query.where({'status': status})
            
            # Sayfalama
            users = query.paginate(page, per_page)
            
            return self.json_response({
                'success': True,
                'data': [user.to_dict() for user in users['data']],
                'pagination': users['pagination']
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def show(self, id: int):
        """User detayı API"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Kendi profilini veya admin ise başka kullanıcının profilini görüntüle
            if user.id != id and not user.is_admin:
                return self.error_response('Yetkisiz erişim', 403)
            
            target_user = User.find(id)
            
            if not target_user:
                return self.error_response('Kullanıcı bulunamadı', 404)
            
            return self.json_response({
                'success': True,
                'data': target_user.to_dict()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def store(self):
        """User oluşturma API"""
        try:
            # Admin kontrolü
            user = self.require_role('admin')
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Input'ları al
            data = self.get_all_input()
            
            # Validation kuralları
            rules = {
                'name': 'required|min:2|max:50',
                'email': 'required|email|unique:users,email',
                'password': 'required|min:8|confirmed',
                'username': 'required|min:3|max:20|unique:users,username',
                'role': 'in:user,moderator,admin'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # User oluştur
            new_user = User.create_user(data)
            
            if not new_user:
                return self.error_response('Kullanıcı oluşturulamadı', 500)
            
            # Log
            self.log('info', f'API: Yeni kullanıcı oluşturuldu: {new_user.email}', {
                'admin_id': user.id,
                'user_id': new_user.id
            })
            
            return self.json_response({
                'success': True,
                'message': 'Kullanıcı başarıyla oluşturuldu',
                'data': new_user.to_dict()
            }, 201)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def update(self, id: int):
        """User güncelleme API"""
        try:
            current_user = self.require_auth()
            
            if isinstance(current_user, dict):  # Redirect response
                return current_user
            
            target_user = User.find(id)
            
            if not target_user:
                return self.error_response('Kullanıcı bulunamadı', 404)
            
            # Yetki kontrolü
            if current_user.id != id and not current_user.is_admin:
                return self.error_response('Bu kullanıcıyı düzenleme yetkiniz yok', 403)
            
            # Input'ları al
            data = self.get_all_input()
            
            # Validation kuralları
            rules = {
                'name': 'required|min:2|max:50',
                'email': f'required|email|unique:users,email,{id}',
                'username': f'required|min:3|max:20|unique:users,username,{id}',
                'role': 'in:user,moderator,admin',
                'status': 'in:active,inactive'
            }
            
            # Admin değilse role ve status değiştiremez
            if not current_user.is_admin:
                data.pop('role', None)
                data.pop('status', None)
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # User'ı güncelle
            if target_user.update(data):
                # Log
                self.log('info', f'API: Kullanıcı güncellendi: {target_user.email}', {
                    'admin_id': current_user.id,
                    'user_id': target_user.id
                })
                
                return self.json_response({
                    'success': True,
                    'message': 'Kullanıcı başarıyla güncellendi',
                    'data': target_user.to_dict()
                })
            else:
                return self.error_response('Kullanıcı güncellenemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def destroy(self, id: int):
        """User silme API"""
        try:
            current_user = self.require_auth()
            
            if isinstance(current_user, dict):  # Redirect response
                return current_user
            
            target_user = User.find(id)
            
            if not target_user:
                return self.error_response('Kullanıcı bulunamadı', 404)
            
            # Yetki kontrolü
            if current_user.id == id:
                return self.error_response('Kendinizi silemezsiniz', 400)
            
            if not current_user.is_admin:
                return self.error_response('Kullanıcı silme yetkiniz yok', 403)
            
            # User'ı sil
            if target_user.delete():
                # Log
                self.log('info', f'API: Kullanıcı silindi: {target_user.email}', {
                    'admin_id': current_user.id,
                    'user_id': target_user.id
                })
                
                return self.json_response({
                    'success': True,
                    'message': 'Kullanıcı başarıyla silindi'
                })
            else:
                return self.error_response('Kullanıcı silinemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def profile(self):
        """Kullanıcı profili API"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            return self.json_response({
                'success': True,
                'data': user.to_dict()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def updateProfile(self):
        """Profil güncelleme API"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Input'ları al
            data = self.get_all_input()
            
            # Validation kuralları
            rules = {
                'name': 'required|min:2|max:50',
                'phone': 'phone',
                'address': 'max:255',
                'city': 'max:100',
                'country': 'max:100'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Profili güncelle
            if user.update(data):
                return self.json_response({
                    'success': True,
                    'message': 'Profil başarıyla güncellendi',
                    'data': user.to_dict()
                })
            else:
                return self.error_response('Profil güncellenemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def changePassword(self):
        """Şifre değiştirme API"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Input'ları al
            data = self.get_all_input()
            
            # Validation kuralları
            rules = {
                'current_password': 'required',
                'new_password': 'required|min:8|confirmed',
                'new_password_confirmation': 'required'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Mevcut şifreyi kontrol et
            from core.Services.base_service import BaseService
            hasher = BaseService.get_hasher()
            
            if not hasher.check(data['current_password'], user.password):
                return self.error_response('Mevcut şifre yanlış', 400)
            
            # Şifreyi değiştir
            if user.change_password(data['new_password']):
                # Log
                self.log('info', 'API: Şifre değiştirildi', {
                    'user_id': user.id,
                    'email': user.email
                })
                
                return self.json_response({
                    'success': True,
                    'message': 'Şifre başarıyla değiştirildi'
                })
            else:
                return self.error_response('Şifre değiştirilemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def posts(self, id: int):
        """Kullanıcının post'ları API"""
        try:
            user = User.find(id)
            
            if not user:
                return self.error_response('Kullanıcı bulunamadı', 404)
            
            # Sayfalama parametreleri
            page = int(self.get_input('page', 1))
            per_page = int(self.get_input('per_page', 10))
            
            posts = Post.by_user(id).paginate(page, per_page)
            
            return self.json_response({
                'success': True,
                'data': [post.to_dict() for post in posts['data']],
                'pagination': posts['pagination']
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def search(self):
        """Kullanıcı arama API"""
        try:
            query = self.get_input('q', '')
            limit = int(self.get_input('limit', 10))
            
            if not query or len(query) < 2:
                return self.error_response('Arama terimi en az 2 karakter olmalıdır', 400)
            
            users = User.search(query, limit)
            
            return self.json_response({
                'success': True,
                'data': [user.to_dict() for user in users],
                'query': query
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request) 