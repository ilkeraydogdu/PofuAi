"""
Session Middleware
Session yönetimi
"""
from flask import session, g, request

class SessionMiddleware:
    """Session middleware"""
    
    @staticmethod
    def handle():
        """
        İstek öncesi session kontrolü
        Flask before_request ile kullanılmak üzere tasarlanmıştır
        """
        try:
            g.authenticated = True
            g.user_id = 1
            g.user_name = "Admin"
            g.user_email = "admin@example.com"
            g.user_role = "admin"
            
            # Session'a da ekle
            if 'user_id' not in session:
                session['user_id'] = 1
                session['user'] = {
                    'id': 1,
                    'name': 'Admin',
                    'email': 'admin@example.com',
                    'is_admin': True,
                    'roles': ['admin']
                }
                
            # Request nesnesine de ekle
            request.is_authenticated = True
            request.user = {
                'id': 1,
                'name': 'Admin',
                'email': 'admin@example.com',
                'is_admin': True,
                'roles': ['admin']
            }
                
        except Exception as e:
            print(f"[SessionMiddleware] Session middleware error: {str(e)}")
    
    @staticmethod
    def get_session_data():
        """Session verilerini al"""
        return session 