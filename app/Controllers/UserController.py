"""
User Controller
Kullanıcı işlemleri controller'ı
"""
from typing import Dict, Any, Optional
from app.Controllers.BaseController import BaseController
from app.Models.User import User
from core.Services.validators import Validator
from core.Services.error_handler import error_handler
import os
from datetime import datetime

class UserController(BaseController):
    """Kullanıcı controller'ı"""
    
    def __init__(self):
        super().__init__()
        self.validator = Validator()
    
    def index(self):
        """Kullanıcı listesi"""
        try:
            # Sayfalama parametreleri
            page = int(self.get_input('page', 1))
            per_page = int(self.get_input('per_page', 10))
            search = self.get_input('search', '')
            
            # Kullanıcıları getir
            users = User.paginate(page, per_page, search=search)
            
            return self.json_response({
                'users': users['data'],
                'pagination': users['pagination']
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def show(self, id: int):
        """Kullanıcı detayı"""
        try:
            user = User.find(id)
            
            if not user:
                return self.error_response('Kullanıcı bulunamadı', 404)
            
            return self.json_response(user.to_dict())
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def create(self):
        """Kullanıcı oluşturma formu"""
        try:
            return self.view('users.create')
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def store(self):
        """Kullanıcı kaydetme"""
        try:
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
            
            # Kullanıcı oluştur
            user = User.create_user(data)
            
            if not user:
                return self.error_response('Kullanıcı oluşturulamadı', 500)
            
            # Log
            self.log('info', f'Yeni kullanıcı oluşturuldu: {user.email}', {
                'user_id': user.id,
                'email': user.email
            })
            
            return self.json_response(user.to_dict(), 201)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def edit(self, id: int):
        """Kullanıcı düzenleme formu"""
        try:
            user = User.find(id)
            
            if not user:
                return self.error_response('Kullanıcı bulunamadı', 404)
            
            return self.view('users.edit', {'user': user.to_dict()})
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def update(self, id: int):
        """Kullanıcı güncelleme"""
        try:
            user = User.find(id)
            
            if not user:
                return self.error_response('Kullanıcı bulunamadı', 404)
            
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
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Kullanıcıyı güncelle
            if user.update(data):
                # Log
                self.log('info', f'Kullanıcı güncellendi: {user.email}', {
                    'user_id': user.id,
                    'email': user.email
                })
                
                return self.json_response(user.to_dict())
            else:
                return self.error_response('Kullanıcı güncellenemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def delete(self, id: int):
        """Kullanıcı silme"""
        try:
            user = User.find(id)
            
            if not user:
                return self.error_response('Kullanıcı bulunamadı', 404)
            
            # Kendini silmeye çalışıyor mu kontrol et
            current_user = self.get_user()
            if current_user and current_user['id'] == id:
                return self.error_response('Kendinizi silemezsiniz', 400)
            
            # Kullanıcıyı sil
            if user.delete():
                # Log
                self.log('info', f'Kullanıcı silindi: {user.email}', {
                    'user_id': user.id,
                    'email': user.email
                })
                
                return self.json_response({'message': 'Kullanıcı başarıyla silindi'})
            else:
                return self.error_response('Kullanıcı silinemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def profile(self):
        """Kullanıcı profili"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            return self.view('users.profile', {'user': user.to_dict()})
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def update_profile(self):
        """Profil güncelleme"""
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
                return self.json_response(user.to_dict())
            else:
                return self.error_response('Profil güncellenemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def change_password(self):
        """Şifre değiştirme"""
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
                self.log('info', 'Şifre değiştirildi', {
                    'user_id': user.id,
                    'email': user.email
                })
                
                return self.json_response({'message': 'Şifre başarıyla değiştirildi'})
            else:
                return self.error_response('Şifre değiştirilemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def upload_avatar(self):
        """Avatar yükleme"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Dosya kontrolü
            if 'avatar' not in self.request.files:
                return self.error_response('Avatar dosyası gerekli', 400)
            
            file = self.request.files['avatar']
            
            if file.filename == '':
                return self.error_response('Dosya seçilmedi', 400)
            
            # Dosya validasyonu
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            
            if file_extension not in allowed_extensions:
                return self.error_response('Geçersiz dosya türü', 400)
            
            # Dosya boyutu kontrolü (5MB)
            if len(file.read()) > 5 * 1024 * 1024:
                return self.error_response('Dosya boyutu çok büyük', 400)
            
            file.seek(0)  # Dosya pointer'ını başa al
            
            # Dosyayı kaydet
            filename = f"avatar_{user.id}_{int(datetime.now().timestamp())}.{file_extension}"
            upload_path = f"storage/uploads/avatars/{filename}"
            
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)
            
            # Kullanıcı avatar'ını güncelle
            user.avatar = filename
            user.save()
            
            return self.json_response({
                'message': 'Avatar başarıyla yüklendi',
                'avatar_url': user.avatar_url
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def search(self):
        """Kullanıcı arama"""
        try:
            query = self.get_input('q', '')
            
            if not query or len(query) < 2:
                return self.json_response({'users': []})
            
            # Kullanıcıları ara
            users = User.search(query, limit=10)
            
            return self.json_response({'users': users})
            
        except Exception as e:
            return error_handler.handle_error(e, self.request) 