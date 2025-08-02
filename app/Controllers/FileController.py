"""
File Controller
Dosya yönetim controller'ı
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.Controllers.BaseController import BaseController
from app.Middleware.AuthMiddleware import auth_required, admin_required
from core.Services.error_handler import error_handler
from app.Models.File import File
from core.Database.connection import get_connection
import json
import datetime
from flask import jsonify, request, session, send_file, abort
from typing import Dict, Any, List, Optional
from werkzeug.utils import secure_filename

class FileController(BaseController):
    """File controller'ı"""
    
    def __init__(self):
        super().__init__()
        self.file_model = File()
    
    @auth_required
    def upload(self):
        """Dosya yükleme"""
        if request.method == 'POST':
            try:
                user = self.get_current_user()
                
                # Check if file is present
                if 'file' not in request.files:
                    return self.error_response('No file selected')
                
                file = request.files['file']
                if file.filename == '':
                    return self.error_response('No file selected')
                
                # Prepare file data
                file_data = {
                    'original_filename': secure_filename(file.filename),
                    'size': self._get_file_size(file),
                    'mime_type': file.mimetype,
                    'content': file.read(),
                    'is_public': request.form.get('is_public', 'false').lower() == 'true',
                    'folder_id': request.form.get('folder_id')
                }
                
                # Reset file pointer
                file.seek(0)
                
                # Upload file
                result = self.file_model.upload_file(file_data, user['id'])
                
                if result['success']:
                    return self.success_response('File uploaded successfully', {
                        'file_id': result['file_id'],
                        'file_url': result['file_url'],
                        'filename': result['filename']
                    })
                else:
                    return self.error_response(result['error'])
                    
            except Exception as e:
                return error_handler.handle_error(e, self.request)
        
        else:
            # GET request - show upload form
            try:
                user = self.get_current_user()
                
                # Get user's storage stats
                storage_stats = self.file_model.get_storage_stats(user['id'])
                
                # Get folders for dropdown
                folders = self._get_user_folders(user['id'])
                
                data = {
                    'title': 'Dosya Yükle',
                    'user': user,
                    'storage_stats': storage_stats,
                    'folders': folders,
                    'allowed_types': self.file_model.allowed_types,
                    'max_sizes': self.file_model.max_sizes
                }
                
                return self.view('files.upload', data)
                
            except Exception as e:
                return error_handler.handle_error(e, self.request)
    
    @auth_required
    def index(self):
        """Dosya listesi"""
        try:
            user = self.get_current_user()
            
            # Get parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            file_type = request.args.get('type', 'all')
            folder_id = request.args.get('folder_id')
            
            if folder_id:
                folder_id = int(folder_id)
            
            # Get user files
            files_data = self.file_model.get_user_files(
                user['id'], folder_id, file_type, per_page, page
            )
            
            # Get storage stats
            storage_stats = self.file_model.get_storage_stats(user['id'])
            
            # Get folders
            folders = self._get_user_folders(user['id'])
            
            data = {
                'title': 'Dosyalarım',
                'user': user,
                'files': files_data['files'],
                'pagination': files_data['pagination'],
                'storage_stats': storage_stats,
                'folders': folders,
                'current_folder_id': folder_id,
                'current_type': file_type,
                'allowed_types': self.file_model.allowed_types
            }
            
            return self.view('files.index', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @auth_required
    def download(self, file_id: int):
        """Dosya indirme"""
        try:
            user = self.get_current_user()
            
            # Get file info
            file_info = self.file_model.get_file_by_id(file_id, user['id'])
            
            if not file_info:
                abort(404)
            
            # Check access permissions
            if file_info['user_id'] != user['id'] and not file_info['is_public']:
                abort(403)
            
            # Increment download count
            self.file_model.increment_download_count(file_id)
            
            # Send file
            try:
                return send_file(
                    file_info['file_path'],
                    as_attachment=True,
                    download_name=file_info['original_filename'],
                    mimetype=file_info['mime_type']
                )
            except FileNotFoundError:
                return self.error_response('File not found on storage', 404)
                
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @auth_required
    def view(self, file_id: int):
        """Dosya görüntüleme"""
        try:
            user = self.get_current_user()
            
            # Get file info
            file_info = self.file_model.get_file_by_id(file_id, user['id'])
            
            if not file_info:
                return self.error_response('File not found', 404)
            
            # Check access permissions
            if file_info['user_id'] != user['id'] and not file_info['is_public']:
                return self.error_response('Access denied', 403)
            
            data = {
                'title': f'Dosya: {file_info["original_filename"]}',
                'user': user,
                'file': file_info
            }
            
            return self.view('files.view', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @auth_required
    def delete(self, file_id: int):
        """Dosya silme"""
        if request.method == 'POST':
            try:
                user = self.get_current_user()
                
                # Delete file
                success = self.file_model.delete_file(file_id, user['id'])
                
                if success:
                    return self.success_response('File deleted successfully')
                else:
                    return self.error_response('Failed to delete file')
                    
            except Exception as e:
                return error_handler.handle_error(e, self.request)
    
    @auth_required
    def api_upload(self):
        """API dosya yükleme"""
        try:
            user = self.get_current_user()
            
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file provided'})
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'})
            
            # Prepare file data
            file_data = {
                'original_filename': secure_filename(file.filename),
                'size': self._get_file_size(file),
                'mime_type': file.mimetype,
                'content': file.read(),
                'is_public': request.form.get('is_public', 'false').lower() == 'true',
                'folder_id': request.form.get('folder_id')
            }
            
            # Upload file
            result = self.file_model.upload_file(file_data, user['id'])
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @auth_required
    def api_files(self):
        """API dosya listesi"""
        try:
            user = self.get_current_user()
            
            # Get parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            file_type = request.args.get('type', 'all')
            folder_id = request.args.get('folder_id')
            
            if folder_id:
                folder_id = int(folder_id)
            
            # Get files
            files_data = self.file_model.get_user_files(
                user['id'], folder_id, file_type, per_page, page
            )
            
            return jsonify({
                'success': True,
                'data': files_data
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @auth_required
    def api_storage_stats(self):
        """API depolama istatistikleri"""
        try:
            user = self.get_current_user()
            
            # Get storage stats
            storage_stats = self.file_model.get_storage_stats(user['id'])
            
            return jsonify({
                'success': True,
                'data': storage_stats
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @admin_required
    def admin_index(self):
        """Admin dosya yönetimi"""
        try:
            admin = self.get_current_user()
            
            # Get parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 50))
            user_id = request.args.get('user_id')
            file_type = request.args.get('type', 'all')
            
            # Get all files with user info
            files_data = self._get_all_files(page, per_page, user_id, file_type)
            
            # Get system storage stats
            system_stats = self._get_system_storage_stats()
            
            # Get users for filter dropdown
            users = self._get_users_with_files()
            
            data = {
                'title': 'Dosya Yönetimi - Admin',
                'admin': admin,
                'files': files_data['files'],
                'pagination': files_data['pagination'],
                'system_stats': system_stats,
                'users': users,
                'current_user_id': user_id,
                'current_type': file_type,
                'allowed_types': self.file_model.allowed_types
            }
            
            return self.view('admin.files.index', data)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    @admin_required
    def admin_delete(self, file_id: int):
        """Admin dosya silme"""
        if request.method == 'POST':
            try:
                # Get file info
                file_info = self.file_model.get_file_by_id(file_id)
                
                if not file_info:
                    return self.error_response('File not found')
                
                # Admin can delete any file
                success = self.file_model.delete_file(file_id, file_info['user_id'])
                
                if success:
                    return self.success_response('File deleted successfully')
                else:
                    return self.error_response('Failed to delete file')
                    
            except Exception as e:
                return error_handler.handle_error(e, self.request)
    
    # Helper Methods
    def _get_file_size(self, file) -> int:
        """Dosya boyutunu al"""
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        return size
    
    def _get_user_folders(self, user_id: int) -> List[Dict[str, Any]]:
        """Kullanıcının klasörlerini getir"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT id, name, description
                FROM file_folders
                WHERE user_id = %s OR is_public = TRUE
                ORDER BY name
            """, [user_id])
            
            folders = cursor.fetchall()
            cursor.close()
            
            return folders
            
        except Exception as e:
            self.logger.error(f"Get user folders error: {e}")
            return []
    
    def _get_all_files(self, page: int, per_page: int, user_id: Optional[int] = None, 
                      file_type: str = 'all') -> Dict[str, Any]:
        """Tüm dosyaları getir (admin)"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            offset = (page - 1) * per_page
            
            # Base query
            base_query = """
                FROM files f
                LEFT JOIN users u ON f.user_id = u.id
                LEFT JOIN file_folders ff ON f.folder_id = ff.id
                WHERE 1=1
            """
            params = []
            
            # User filter
            if user_id:
                base_query += " AND f.user_id = %s"
                params.append(user_id)
            
            # File type filter
            if file_type != 'all':
                file_model = File()
                extensions = file_model.allowed_types.get(file_type, [])
                if extensions:
                    placeholders = ', '.join(['%s'] * len(extensions))
                    base_query += f" AND f.file_extension IN ({placeholders})"
                    params.extend(extensions)
            
            # Count query
            count_query = f"SELECT COUNT(*) as total {base_query}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # Main query
            query = f"""
                SELECT f.*, u.name as user_name, u.email as user_email, ff.name as folder_name
                {base_query}
                ORDER BY f.created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([per_page, offset])
            
            cursor.execute(query, params)
            files = cursor.fetchall()
            
            # Process files
            file_model = File()
            for file in files:
                file['file_url'] = file_model._generate_file_url(file['id'], file['filename'])
                file['file_category'] = file_model._get_file_category(file['file_extension'])
                file['formatted_size'] = file_model._format_file_size(file['file_size'])
                if file['metadata']:
                    file['metadata'] = json.loads(file['metadata'])
            
            cursor.close()
            
            # Pagination info
            total_pages = (total + per_page - 1) // per_page
            
            return {
                'files': files,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_items': total,
                    'per_page': per_page,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
            
        except Exception as e:
            self.logger.error(f"Get all files error: {e}")
            return {'files': [], 'pagination': {}}
    
    def _get_system_storage_stats(self) -> Dict[str, Any]:
        """Sistem depolama istatistikleri"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Total system stats
            cursor.execute("""
                SELECT COUNT(*) as total_files, COALESCE(SUM(file_size), 0) as total_size
                FROM files
            """)
            totals = cursor.fetchone()
            
            # By user
            cursor.execute("""
                SELECT u.name, u.email, COUNT(f.id) as file_count, 
                       COALESCE(SUM(f.file_size), 0) as total_size
                FROM users u
                LEFT JOIN files f ON u.id = f.user_id
                GROUP BY u.id
                HAVING file_count > 0
                ORDER BY total_size DESC
                LIMIT 10
            """)
            by_user = cursor.fetchall()
            
            # By file type
            cursor.execute("""
                SELECT file_extension, COUNT(*) as count, SUM(file_size) as size
                FROM files
                GROUP BY file_extension
                ORDER BY size DESC
                LIMIT 10
            """)
            by_extension = cursor.fetchall()
            
            cursor.close()
            
            # Format sizes
            file_model = File()
            for user_stat in by_user:
                user_stat['formatted_size'] = file_model._format_file_size(user_stat['total_size'])
            
            for ext_stat in by_extension:
                ext_stat['formatted_size'] = file_model._format_file_size(ext_stat['size'])
            
            return {
                'total_files': totals['total_files'],
                'total_size': totals['total_size'],
                'formatted_total_size': file_model._format_file_size(totals['total_size']),
                'by_user': by_user,
                'by_extension': by_extension
            }
            
        except Exception as e:
            self.logger.error(f"Get system storage stats error: {e}")
            return {'total_files': 0, 'total_size': 0, 'by_user': [], 'by_extension': []}
    
    def _get_users_with_files(self) -> List[Dict[str, Any]]:
        """Dosyası olan kullanıcıları getir"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT DISTINCT u.id, u.name, u.email
                FROM users u
                JOIN files f ON u.id = f.user_id
                ORDER BY u.name
            """)
            
            users = cursor.fetchall()
            cursor.close()
            
            return users
            
        except Exception as e:
            self.logger.error(f"Get users with files error: {e}")
            return []