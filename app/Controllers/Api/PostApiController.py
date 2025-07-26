"""
Post API Controller
Post API endpoint'leri
"""
from app.Controllers.BaseController import BaseController
from app.Models.Post import Post
from core.Services.error_handler import error_handler

class PostApiController(BaseController):
    """Post API controller'ı"""
    
    def index(self):
        """Post listesi API"""
        try:
            # Sayfalama parametreleri
            page = int(self.get_input('page', 1))
            per_page = int(self.get_input('per_page', 10))
            search = self.get_input('search', '')
            category = self.get_input('category', '')
            user_id = self.get_input('user_id', '')
            
            # Filtreleme
            query = Post.where({'status': 'published'})
            
            if search:
                query = query.where_like('title', f'%{search}%')
            
            if category:
                query = query.where({'category': category})
            
            if user_id:
                query = query.where({'user_id': user_id})
            
            # Sayfalama
            posts = query.paginate(page, per_page)
            
            return self.json_response({
                'success': True,
                'data': [post.to_dict() for post in posts['data']],
                'pagination': posts['pagination']
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def show(self, id: int):
        """Post detayı API"""
        try:
            post = Post.find(id)
            
            if not post or not post.is_published:
                return self.error_response('Post bulunamadı', 404)
            
            # Görüntülenme sayısını artır
            post.increment_views()
            
            return self.json_response({
                'success': True,
                'data': post.to_dict()
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def store(self):
        """Post oluşturma API"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            # Input'ları al
            data = self.get_all_input()
            data['user_id'] = user.id
            
            # Validation kuralları
            rules = {
                'title': 'required|min:3|max:200',
                'content': 'required|min:10',
                'category': 'required|in:technology,science,health,entertainment'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Post oluştur
            post = Post.create_post(data)
            
            if not post:
                return self.error_response('Post oluşturulamadı', 500)
            
            # Log
            self.log('info', f'API: Yeni post oluşturuldu: {post.title}', {
                'user_id': user.id,
                'post_id': post.id
            })
            
            return self.json_response({
                'success': True,
                'message': 'Post başarıyla oluşturuldu',
                'data': post.to_dict()
            }, 201)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def update(self, id: int):
        """Post güncelleme API"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            post = Post.find(id)
            
            if not post:
                return self.error_response('Post bulunamadı', 404)
            
            # Yetki kontrolü
            if post.user_id != user.id and not user.is_admin:
                return self.error_response('Bu post\'u düzenleme yetkiniz yok', 403)
            
            # Input'ları al
            data = self.get_all_input()
            
            # Validation kuralları
            rules = {
                'title': 'required|min:3|max:200',
                'content': 'required|min:10',
                'category': 'required|in:technology,science,health,entertainment'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Post'u güncelle
            if post.update(data):
                # Log
                self.log('info', f'API: Post güncellendi: {post.title}', {
                    'user_id': user.id,
                    'post_id': post.id
                })
                
                return self.json_response({
                    'success': True,
                    'message': 'Post başarıyla güncellendi',
                    'data': post.to_dict()
                })
            else:
                return self.error_response('Post güncellenemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def destroy(self, id: int):
        """Post silme API"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            post = Post.find(id)
            
            if not post:
                return self.error_response('Post bulunamadı', 404)
            
            # Yetki kontrolü
            if post.user_id != user.id and not user.is_admin:
                return self.error_response('Bu post\'u silme yetkiniz yok', 403)
            
            # Post'u sil
            if post.delete():
                # Log
                self.log('info', f'API: Post silindi: {post.title}', {
                    'user_id': user.id,
                    'post_id': post.id
                })
                
                return self.json_response({
                    'success': True,
                    'message': 'Post başarıyla silindi'
                })
            else:
                return self.error_response('Post silinemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def like(self, id: int):
        """Post beğenme API"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            post = Post.find(id)
            
            if not post or not post.is_published:
                return self.error_response('Post bulunamadı', 404)
            
            # Beğeniyi aç/kapat
            success = Post.toggle_like(user.id, post.id)
            
            if success:
                return self.json_response({
                    'success': True,
                    'message': 'Beğeni durumu güncellendi',
                    'liked': post.is_liked_by(user.id)
                })
            else:
                return self.error_response('Beğeni işlemi başarısız', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def comment(self, id: int):
        """Post yorumlama API"""
        try:
            user = self.require_auth()
            
            if isinstance(user, dict):  # Redirect response
                return user
            
            post = Post.find(id)
            
            if not post or not post.is_published:
                return self.error_response('Post bulunamadı', 404)
            
            # Input'ları al
            data = self.get_all_input()
            data['user_id'] = user.id
            data['post_id'] = post.id
            
            # Validation kuralları
            rules = {
                'content': 'required|min:2|max:1000'
            }
            
            # Validasyon
            if not self.validator.validate(data, rules):
                return self.error_response('Validation hatası', 422, self.validator.get_errors())
            
            # Yorum oluştur
            from app.Models.Comment import Comment
            comment = Comment.create_comment(data)
            
            if comment:
                return self.json_response({
                    'success': True,
                    'message': 'Yorum başarıyla eklendi',
                    'data': comment.to_dict()
                }, 201)
            else:
                return self.error_response('Yorum eklenemedi', 500)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def popular(self):
        """Popüler post'lar API"""
        try:
            limit = int(self.get_input('limit', 10))
            
            posts = Post.popular(limit)
            
            return self.json_response({
                'success': True,
                'data': [post.to_dict() for post in posts]
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def recent(self):
        """Son post'lar API"""
        try:
            limit = int(self.get_input('limit', 10))
            
            posts = Post.recent(limit)
            
            return self.json_response({
                'success': True,
                'data': [post.to_dict() for post in posts]
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def search(self):
        """Post arama API"""
        try:
            query = self.get_input('q', '')
            limit = int(self.get_input('limit', 10))
            
            if not query or len(query) < 2:
                return self.error_response('Arama terimi en az 2 karakter olmalıdır', 400)
            
            posts = Post.search(query, limit)
            
            return self.json_response({
                'success': True,
                'data': [post.to_dict() for post in posts],
                'query': query
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request) 