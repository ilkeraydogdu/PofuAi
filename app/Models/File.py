"""
File Model
Dosya yönetim sistemi modeli
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.Database.base_model import BaseModel
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import hashlib
import mimetypes
from pathlib import Path

class File(BaseModel):
    """Dosya modeli"""
    
    table_name = 'files'
    
    def __init__(self):
        super().__init__()
        self.fillable = [
            'user_id', 'filename', 'original_filename', 'file_path', 'file_size',
            'mime_type', 'file_extension', 'file_hash', 'storage_type', 'is_public',
            'download_count', 'metadata', 'expires_at', 'folder_id'
        ]
        
        self.validation_rules = {
            'user_id': 'required|integer',
            'filename': 'required|string|max:255',
            'original_filename': 'required|string|max:255',
            'file_path': 'required|string|max:500',
            'file_size': 'required|integer',
            'mime_type': 'required|string|max:100',
            'storage_type': 'string|in:local,s3,azure,gcp',
            'is_public': 'boolean'
        }
        
        # Allowed file types
        self.allowed_types = {
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp'],
            'document': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf'],
            'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'],
            'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma'],
            'archive': ['zip', 'rar', '7z', 'tar', 'gz'],
            'other': []
        }
        
        # Max file sizes (in bytes)
        self.max_sizes = {
            'image': 10 * 1024 * 1024,      # 10MB
            'document': 50 * 1024 * 1024,   # 50MB
            'video': 500 * 1024 * 1024,     # 500MB
            'audio': 100 * 1024 * 1024,     # 100MB
            'archive': 100 * 1024 * 1024,   # 100MB
            'other': 10 * 1024 * 1024       # 10MB
        }
    
    def upload_file(self, file_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Dosya yükleme"""
        try:
            # File validation
            validation_result = self._validate_file(file_data)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Generate unique filename
            file_extension = self._get_file_extension(file_data['original_filename'])
            unique_filename = self._generate_unique_filename(file_extension)
            
            # Determine file category
            file_category = self._get_file_category(file_extension)
            
            # Create upload directory
            upload_path = self._create_upload_directory(user_id, file_category)
            file_path = os.path.join(upload_path, unique_filename)
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_data.get('content', b''))
            
            # Check for duplicates
            existing_file = self._check_duplicate(file_hash, user_id)
            if existing_file:
                return {
                    'success': True,
                    'file_id': existing_file['id'],
                    'message': 'File already exists',
                    'duplicate': True
                }
            
            # Save file to storage
            storage_result = self._save_to_storage(file_data, file_path)
            if not storage_result['success']:
                return {'success': False, 'error': storage_result['error']}
            
            # Save file record to database
            file_record = {
                'user_id': user_id,
                'filename': unique_filename,
                'original_filename': file_data['original_filename'],
                'file_path': file_path,
                'file_size': file_data['size'],
                'mime_type': file_data.get('mime_type', mimetypes.guess_type(file_data['original_filename'])[0]),
                'file_extension': file_extension,
                'file_hash': file_hash,
                'storage_type': 'local',  # Default to local storage
                'is_public': file_data.get('is_public', False),
                'download_count': 0,
                'metadata': json.dumps(self._extract_metadata(file_data)),
                'folder_id': file_data.get('folder_id'),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Insert to database
            file_id = self._insert_file_record(file_record)
            
            if file_id:
                return {
                    'success': True,
                    'file_id': file_id,
                    'filename': unique_filename,
                    'file_path': file_path,
                    'file_url': self._generate_file_url(file_id, unique_filename)
                }
            else:
                # Clean up uploaded file if database insert fails
                self._cleanup_file(file_path)
                return {'success': False, 'error': 'Failed to save file record'}
                
        except Exception as e:
            self.logger.error(f"File upload error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_files(self, user_id: int, folder_id: Optional[int] = None, 
                      file_type: str = 'all', limit: int = 50, page: int = 1) -> Dict[str, Any]:
        """Kullanıcının dosyalarını getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            offset = (page - 1) * limit
            
            # Base query
            base_query = f"""
                FROM {self.table_name} f
                LEFT JOIN file_folders ff ON f.folder_id = ff.id
                WHERE f.user_id = %s
            """
            params = [user_id]
            
            # Folder filter
            if folder_id is not None:
                base_query += " AND f.folder_id = %s"
                params.append(folder_id)
            
            # File type filter
            if file_type != 'all':
                extensions = self.allowed_types.get(file_type, [])
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
                SELECT f.*, ff.name as folder_name
                {base_query}
                ORDER BY f.created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            files = cursor.fetchall()
            
            # Process files
            for file in files:
                file['file_url'] = self._generate_file_url(file['id'], file['filename'])
                file['file_category'] = self._get_file_category(file['file_extension'])
                file['formatted_size'] = self._format_file_size(file['file_size'])
                if file['metadata']:
                    file['metadata'] = json.loads(file['metadata'])
            
            cursor.close()
            
            # Pagination info
            total_pages = (total + limit - 1) // limit
            
            return {
                'files': files,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_items': total,
                    'per_page': limit,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
            
        except Exception as e:
            self.logger.error(f"Get user files error: {e}")
            return {'files': [], 'pagination': {}}
    
    def get_file_by_id(self, file_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """ID ile dosya getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            query = f"""
                SELECT f.*, ff.name as folder_name, u.name as owner_name
                FROM {self.table_name} f
                LEFT JOIN file_folders ff ON f.folder_id = ff.id
                LEFT JOIN users u ON f.user_id = u.id
                WHERE f.id = %s
            """
            params = [file_id]
            
            # User access control
            if user_id is not None:
                query += " AND (f.user_id = %s OR f.is_public = TRUE)"
                params.append(user_id)
            
            cursor.execute(query, params)
            file = cursor.fetchone()
            
            if file:
                file['file_url'] = self._generate_file_url(file['id'], file['filename'])
                file['file_category'] = self._get_file_category(file['file_extension'])
                file['formatted_size'] = self._format_file_size(file['file_size'])
                if file['metadata']:
                    file['metadata'] = json.loads(file['metadata'])
            
            cursor.close()
            return file
            
        except Exception as e:
            self.logger.error(f"Get file by ID error: {e}")
            return None
    
    def delete_file(self, file_id: int, user_id: int) -> bool:
        """Dosya silme"""
        try:
            # Get file info
            file_info = self.get_file_by_id(file_id, user_id)
            if not file_info or file_info['user_id'] != user_id:
                return False
            
            # Delete from storage
            self._cleanup_file(file_info['file_path'])
            
            # Delete from database
            cursor = self.db.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE id = %s AND user_id = %s", 
                         [file_id, user_id])
            
            success = cursor.rowcount > 0
            self.db.commit()
            cursor.close()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Delete file error: {e}")
            return False
    
    def increment_download_count(self, file_id: int) -> bool:
        """İndirme sayısını artır"""
        try:
            cursor = self.db.cursor()
            cursor.execute(f"""
                UPDATE {self.table_name} 
                SET download_count = download_count + 1, updated_at = %s
                WHERE id = %s
            """, [datetime.now(), file_id])
            
            success = cursor.rowcount > 0
            self.db.commit()
            cursor.close()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Increment download count error: {e}")
            return False
    
    def get_storage_stats(self, user_id: int) -> Dict[str, Any]:
        """Depolama istatistikleri"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            # Total files and size
            cursor.execute(f"""
                SELECT COUNT(*) as total_files, COALESCE(SUM(file_size), 0) as total_size
                FROM {self.table_name} WHERE user_id = %s
            """, [user_id])
            totals = cursor.fetchone()
            
            # By file type
            cursor.execute(f"""
                SELECT file_extension, COUNT(*) as count, SUM(file_size) as size
                FROM {self.table_name} WHERE user_id = %s
                GROUP BY file_extension
                ORDER BY size DESC
            """, [user_id])
            by_extension = cursor.fetchall()
            
            # By category
            stats_by_category = {}
            for ext_stat in by_extension:
                category = self._get_file_category(ext_stat['file_extension'])
                if category not in stats_by_category:
                    stats_by_category[category] = {'count': 0, 'size': 0}
                stats_by_category[category]['count'] += ext_stat['count']
                stats_by_category[category]['size'] += ext_stat['size']
            
            cursor.close()
            
            return {
                'total_files': totals['total_files'],
                'total_size': totals['total_size'],
                'formatted_total_size': self._format_file_size(totals['total_size']),
                'by_extension': by_extension,
                'by_category': stats_by_category
            }
            
        except Exception as e:
            self.logger.error(f"Get storage stats error: {e}")
            return {'total_files': 0, 'total_size': 0, 'by_extension': [], 'by_category': {}}
    
    # Helper Methods
    def _validate_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dosya validasyonu"""
        try:
            # Check required fields
            required_fields = ['original_filename', 'size']
            for field in required_fields:
                if field not in file_data:
                    return {'valid': False, 'error': f'Missing required field: {field}'}
            
            # Get file extension
            file_extension = self._get_file_extension(file_data['original_filename']).lower()
            
            # Check allowed extensions
            allowed_extensions = []
            for category, extensions in self.allowed_types.items():
                allowed_extensions.extend(extensions)
            
            if file_extension not in allowed_extensions:
                return {'valid': False, 'error': f'File type not allowed: {file_extension}'}
            
            # Check file size
            file_category = self._get_file_category(file_extension)
            max_size = self.max_sizes.get(file_category, self.max_sizes['other'])
            
            if file_data['size'] > max_size:
                return {'valid': False, 'error': f'File too large. Max size: {self._format_file_size(max_size)}'}
            
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def _get_file_extension(self, filename: str) -> str:
        """Dosya uzantısını al"""
        return Path(filename).suffix[1:].lower() if '.' in filename else ''
    
    def _get_file_category(self, extension: str) -> str:
        """Dosya kategorisini belirle"""
        for category, extensions in self.allowed_types.items():
            if extension.lower() in extensions:
                return category
        return 'other'
    
    def _generate_unique_filename(self, extension: str) -> str:
        """Benzersiz dosya adı oluştur"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_hash = hashlib.md5(f"{timestamp}_{os.urandom(8)}".encode()).hexdigest()[:8]
        return f"{timestamp}_{random_hash}.{extension}"
    
    def _calculate_file_hash(self, content: bytes) -> str:
        """Dosya hash'i hesapla"""
        return hashlib.sha256(content).hexdigest()
    
    def _create_upload_directory(self, user_id: int, category: str) -> str:
        """Upload dizini oluştur"""
        base_path = os.path.join('uploads', str(user_id), category)
        os.makedirs(base_path, exist_ok=True)
        return base_path
    
    def _save_to_storage(self, file_data: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Dosyayı storage'a kaydet"""
        try:
            # For now, simulate file saving
            # In real implementation, this would save the actual file
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _cleanup_file(self, file_path: str):
        """Dosyayı temizle"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            self.logger.error(f"File cleanup error: {e}")
    
    def _check_duplicate(self, file_hash: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Duplicate dosya kontrolü"""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute(f"""
                SELECT id, filename FROM {self.table_name} 
                WHERE file_hash = %s AND user_id = %s
            """, [file_hash, user_id])
            
            result = cursor.fetchone()
            cursor.close()
            return result
            
        except Exception as e:
            self.logger.error(f"Check duplicate error: {e}")
            return None
    
    def _insert_file_record(self, file_record: Dict[str, Any]) -> int:
        """Dosya kaydını veritabanına ekle"""
        try:
            cursor = self.db.cursor()
            
            columns = ', '.join(file_record.keys())
            placeholders = ', '.join(['%s'] * len(file_record))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            
            cursor.execute(query, list(file_record.values()))
            file_id = cursor.lastrowid
            
            self.db.commit()
            cursor.close()
            
            return file_id
            
        except Exception as e:
            self.logger.error(f"Insert file record error: {e}")
            return 0
    
    def _generate_file_url(self, file_id: int, filename: str) -> str:
        """Dosya URL'si oluştur"""
        return f"/files/{file_id}/{filename}"
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Dosya boyutunu formatla"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _extract_metadata(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dosya metadata'sını çıkar"""
        metadata = {
            'upload_date': datetime.now().isoformat(),
            'original_name': file_data['original_filename']
        }
        
        # Add specific metadata based on file type
        file_extension = self._get_file_extension(file_data['original_filename'])
        file_category = self._get_file_category(file_extension)
        
        if file_category == 'image':
            # For images, you could extract EXIF data, dimensions, etc.
            metadata.update({
                'type': 'image',
                'format': file_extension.upper()
            })
        elif file_category == 'document':
            metadata.update({
                'type': 'document',
                'format': file_extension.upper()
            })
        
        return metadata