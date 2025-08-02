"""
Review Model
Değerlendirme ve rating sistemi modeli
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.Database.base_model import BaseModel
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

class Review(BaseModel):
    """Değerlendirme modeli"""
    
    table_name = 'reviews'
    
    def __init__(self):
        super().__init__()
        self.fillable = [
            'user_id', 'product_id', 'order_id', 'rating', 'title', 'comment',
            'pros', 'cons', 'is_verified', 'is_approved', 'helpful_count',
            'not_helpful_count', 'images', 'response_text', 'response_date'
        ]
        
        self.validation_rules = {
            'user_id': 'required|integer',
            'product_id': 'required|integer',
            'rating': 'required|integer|min:1|max:5',
            'title': 'required|string|max:255',
            'comment': 'required|string|min:10',
            'pros': 'string',
            'cons': 'string'
        }
    
    def create_review(self, data: Dict[str, Any]) -> int:
        """Yeni değerlendirme oluştur"""
        try:
            # Değerlendirme verisi hazırla
            review_data = {
                'user_id': data['user_id'],
                'product_id': data['product_id'],
                'order_id': data.get('order_id'),
                'rating': int(data['rating']),
                'title': data['title'],
                'comment': data['comment'],
                'pros': data.get('pros', ''),
                'cons': data.get('cons', ''),
                'is_verified': self._is_verified_purchase(data['user_id'], data['product_id']),
                'is_approved': False,  # Admin onayı gerekli
                'helpful_count': 0,
                'not_helpful_count': 0,
                'images': json.dumps(data.get('images', [])) if data.get('images') else None,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Validasyon
            if not self.validate(review_data):
                return 0
            
            # Duplicate kontrolü
            if self._check_duplicate_review(data['user_id'], data['product_id']):
                return 0
            
            # Veritabanına kaydet
            cursor = self.db.cursor()
            
            columns = ', '.join([k for k, v in review_data.items() if v is not None])
            placeholders = ', '.join(['%s'] * len([v for v in review_data.values() if v is not None]))
            values = [v for v in review_data.values() if v is not None]
            
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            
            cursor.execute(query, values)
            review_id = cursor.lastrowid
            
            self.db.commit()
            cursor.close()
            
            # Ürün rating ortalamasını güncelle
            self._update_product_rating(data['product_id'])
            
            return review_id
            
        except Exception as e:
            self.logger.error(f"Create review error: {e}")
            return 0
    
    def get_product_reviews(self, product_id: int, limit: int = 20, page: int = 1,
                           sort_by: str = 'newest') -> Dict[str, Any]:
        """Ürün değerlendirmelerini getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            offset = (page - 1) * limit
            
            # Sort options
            sort_options = {
                'newest': 'r.created_at DESC',
                'oldest': 'r.created_at ASC',
                'highest_rating': 'r.rating DESC',
                'lowest_rating': 'r.rating ASC',
                'most_helpful': 'r.helpful_count DESC'
            }
            
            order_by = sort_options.get(sort_by, 'r.created_at DESC')
            
            # Base query
            base_query = f"""
                FROM {self.table_name} r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.product_id = %s AND r.is_approved = TRUE
            """
            params = [product_id]
            
            # Count query
            count_query = f"SELECT COUNT(*) as total {base_query}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # Main query
            query = f"""
                SELECT r.*, u.name as user_name, u.email as user_email
                {base_query}
                ORDER BY {order_by}
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            reviews = cursor.fetchall()
            
            # Process reviews
            for review in reviews:
                if review['images']:
                    review['images'] = json.loads(review['images'])
                else:
                    review['images'] = []
                
                # Mask email for privacy
                if review['user_email']:
                    email_parts = review['user_email'].split('@')
                    if len(email_parts) == 2:
                        masked_email = f"{email_parts[0][:2]}***@{email_parts[1]}"
                        review['user_email'] = masked_email
            
            cursor.close()
            
            # Pagination info
            total_pages = (total + limit - 1) // limit
            
            return {
                'reviews': reviews,
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
            self.logger.error(f"Get product reviews error: {e}")
            return {'reviews': [], 'pagination': {}}
    
    def get_user_reviews(self, user_id: int, limit: int = 20, page: int = 1) -> Dict[str, Any]:
        """Kullanıcının değerlendirmelerini getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            offset = (page - 1) * limit
            
            # Base query
            base_query = f"""
                FROM {self.table_name} r
                LEFT JOIN products p ON r.product_id = p.id
                WHERE r.user_id = %s
            """
            params = [user_id]
            
            # Count query
            count_query = f"SELECT COUNT(*) as total {base_query}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # Main query
            query = f"""
                SELECT r.*, p.name as product_name, p.image_url as product_image
                {base_query}
                ORDER BY r.created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            reviews = cursor.fetchall()
            
            # Process reviews
            for review in reviews:
                if review['images']:
                    review['images'] = json.loads(review['images'])
                else:
                    review['images'] = []
            
            cursor.close()
            
            # Pagination info
            total_pages = (total + limit - 1) // limit
            
            return {
                'reviews': reviews,
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
            self.logger.error(f"Get user reviews error: {e}")
            return {'reviews': [], 'pagination': {}}
    
    def get_review_by_id(self, review_id: int) -> Optional[Dict[str, Any]]:
        """ID ile değerlendirme getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            query = f"""
                SELECT r.*, u.name as user_name, p.name as product_name
                FROM {self.table_name} r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN products p ON r.product_id = p.id
                WHERE r.id = %s
            """
            
            cursor.execute(query, [review_id])
            review = cursor.fetchone()
            
            if review and review['images']:
                review['images'] = json.loads(review['images'])
            elif review:
                review['images'] = []
            
            cursor.close()
            return review
            
        except Exception as e:
            self.logger.error(f"Get review by ID error: {e}")
            return None
    
    def mark_helpful(self, review_id: int, user_id: int, is_helpful: bool) -> bool:
        """Değerlendirmeyi yararlı/yararsız olarak işaretle"""
        try:
            # Önce kullanıcının daha önce işaretleyip işaretlemediğini kontrol et
            cursor = self.db.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT is_helpful FROM review_helpfulness 
                WHERE review_id = %s AND user_id = %s
            """, [review_id, user_id])
            
            existing = cursor.fetchone()
            
            if existing:
                # Mevcut işaretlemeyi güncelle
                if existing['is_helpful'] != is_helpful:
                    # Eski işaretlemeyi kaldır
                    old_column = 'helpful_count' if existing['is_helpful'] else 'not_helpful_count'
                    new_column = 'helpful_count' if is_helpful else 'not_helpful_count'
                    
                    cursor.execute(f"""
                        UPDATE {self.table_name} 
                        SET {old_column} = {old_column} - 1, 
                            {new_column} = {new_column} + 1,
                            updated_at = %s
                        WHERE id = %s
                    """, [datetime.now(), review_id])
                    
                    # Helpfulness tablosunu güncelle
                    cursor.execute("""
                        UPDATE review_helpfulness 
                        SET is_helpful = %s, updated_at = %s
                        WHERE review_id = %s AND user_id = %s
                    """, [is_helpful, datetime.now(), review_id, user_id])
                
            else:
                # Yeni işaretleme ekle
                column = 'helpful_count' if is_helpful else 'not_helpful_count'
                
                cursor.execute(f"""
                    UPDATE {self.table_name} 
                    SET {column} = {column} + 1, updated_at = %s
                    WHERE id = %s
                """, [datetime.now(), review_id])
                
                # Helpfulness tablosuna ekle
                cursor.execute("""
                    INSERT INTO review_helpfulness (review_id, user_id, is_helpful, created_at)
                    VALUES (%s, %s, %s, %s)
                """, [review_id, user_id, is_helpful, datetime.now()])
            
            self.db.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Mark helpful error: {e}")
            return False
    
    def approve_review(self, review_id: int, admin_id: int) -> bool:
        """Değerlendirmeyi onayla"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute(f"""
                UPDATE {self.table_name} 
                SET is_approved = TRUE, approved_by = %s, approved_at = %s, updated_at = %s
                WHERE id = %s
            """, [admin_id, datetime.now(), datetime.now(), review_id])
            
            success = cursor.rowcount > 0
            self.db.commit()
            cursor.close()
            
            if success:
                # Ürün rating ortalamasını güncelle
                review = self.get_review_by_id(review_id)
                if review:
                    self._update_product_rating(review['product_id'])
            
            return success
            
        except Exception as e:
            self.logger.error(f"Approve review error: {e}")
            return False
    
    def add_vendor_response(self, review_id: int, response_text: str, vendor_id: int) -> bool:
        """Satıcı yanıtı ekle"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute(f"""
                UPDATE {self.table_name} 
                SET response_text = %s, response_date = %s, response_by = %s, updated_at = %s
                WHERE id = %s
            """, [response_text, datetime.now(), vendor_id, datetime.now(), review_id])
            
            success = cursor.rowcount > 0
            self.db.commit()
            cursor.close()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Add vendor response error: {e}")
            return False
    
    def get_product_rating_summary(self, product_id: int) -> Dict[str, Any]:
        """Ürün rating özetini getir"""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            # Genel istatistikler
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_reviews,
                    AVG(rating) as average_rating,
                    COUNT(CASE WHEN rating = 5 THEN 1 END) as five_star,
                    COUNT(CASE WHEN rating = 4 THEN 1 END) as four_star,
                    COUNT(CASE WHEN rating = 3 THEN 1 END) as three_star,
                    COUNT(CASE WHEN rating = 2 THEN 1 END) as two_star,
                    COUNT(CASE WHEN rating = 1 THEN 1 END) as one_star,
                    COUNT(CASE WHEN is_verified = TRUE THEN 1 END) as verified_reviews
                FROM {self.table_name}
                WHERE product_id = %s AND is_approved = TRUE
            """, [product_id])
            
            summary = cursor.fetchone()
            cursor.close()
            
            if summary and summary['total_reviews'] > 0:
                # Yüzde hesaplamaları
                total = summary['total_reviews']
                summary['five_star_percent'] = round((summary['five_star'] / total) * 100, 1)
                summary['four_star_percent'] = round((summary['four_star'] / total) * 100, 1)
                summary['three_star_percent'] = round((summary['three_star'] / total) * 100, 1)
                summary['two_star_percent'] = round((summary['two_star'] / total) * 100, 1)
                summary['one_star_percent'] = round((summary['one_star'] / total) * 100, 1)
                summary['average_rating'] = round(summary['average_rating'], 1)
            else:
                summary = {
                    'total_reviews': 0,
                    'average_rating': 0,
                    'five_star': 0, 'four_star': 0, 'three_star': 0, 'two_star': 0, 'one_star': 0,
                    'five_star_percent': 0, 'four_star_percent': 0, 'three_star_percent': 0,
                    'two_star_percent': 0, 'one_star_percent': 0,
                    'verified_reviews': 0
                }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Get product rating summary error: {e}")
            return {'total_reviews': 0, 'average_rating': 0}
    
    def delete_review(self, review_id: int, user_id: int) -> bool:
        """Değerlendirme silme"""
        try:
            cursor = self.db.cursor()
            
            # Önce review'ı getir (product_id için)
            cursor.execute(f"SELECT product_id FROM {self.table_name} WHERE id = %s AND user_id = %s", 
                         [review_id, user_id])
            review = cursor.fetchone()
            
            if not review:
                return False
            
            product_id = review[0]
            
            # Review'ı sil
            cursor.execute(f"DELETE FROM {self.table_name} WHERE id = %s AND user_id = %s", 
                         [review_id, user_id])
            
            success = cursor.rowcount > 0
            self.db.commit()
            cursor.close()
            
            if success:
                # Ürün rating ortalamasını güncelle
                self._update_product_rating(product_id)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Delete review error: {e}")
            return False
    
    # Helper Methods
    def _is_verified_purchase(self, user_id: int, product_id: int) -> bool:
        """Doğrulanmış satın alma kontrolü"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                WHERE o.user_id = %s AND oi.product_id = %s AND o.status = 'completed'
            """, [user_id, product_id])
            
            count = cursor.fetchone()[0]
            cursor.close()
            
            return count > 0
            
        except Exception as e:
            self.logger.error(f"Verify purchase error: {e}")
            return False
    
    def _check_duplicate_review(self, user_id: int, product_id: int) -> bool:
        """Duplicate değerlendirme kontrolü"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute(f"""
                SELECT COUNT(*) FROM {self.table_name} 
                WHERE user_id = %s AND product_id = %s
            """, [user_id, product_id])
            
            count = cursor.fetchone()[0]
            cursor.close()
            
            return count > 0
            
        except Exception as e:
            self.logger.error(f"Check duplicate review error: {e}")
            return False
    
    def _update_product_rating(self, product_id: int):
        """Ürün rating ortalamasını güncelle"""
        try:
            cursor = self.db.cursor()
            
            # Ortalama rating hesapla
            cursor.execute(f"""
                SELECT AVG(rating) as avg_rating, COUNT(*) as review_count
                FROM {self.table_name}
                WHERE product_id = %s AND is_approved = TRUE
            """, [product_id])
            
            result = cursor.fetchone()
            avg_rating = result[0] if result[0] else 0
            review_count = result[1]
            
            # Products tablosunu güncelle
            cursor.execute("""
                UPDATE products 
                SET average_rating = %s, review_count = %s, updated_at = %s
                WHERE id = %s
            """, [round(avg_rating, 1), review_count, datetime.now(), product_id])
            
            self.db.commit()
            cursor.close()
            
        except Exception as e:
            self.logger.error(f"Update product rating error: {e}")

# Review status constants
REVIEW_STATUS = {
    'pending': 'Onay Bekliyor',
    'approved': 'Onaylandı',
    'rejected': 'Reddedildi'
}

# Rating labels
RATING_LABELS = {
    1: 'Çok Kötü',
    2: 'Kötü',
    3: 'Orta',
    4: 'İyi',
    5: 'Mükemmel'
} 