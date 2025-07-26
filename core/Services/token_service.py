"""
Token Service
Geçici şifre ve token yönetimi için merkezi servis
"""
import os
import json
import hashlib
import secrets
import string
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import random

from core.Services.base_service import BaseService
from core.Database.connection import get_db_connection

class TokenService(BaseService):
    """Token ve geçici şifre yönetimi için merkezi servis"""
    
    def __init__(self):
        super().__init__()
        self.db = get_db_connection()
        self.token_expiry = self.get_config('auth.token_expiry', 3600)  # Varsayılan 1 saat (saniye)
        self.password_expiry = self.get_config('auth.password_expiry', 86400)  # Varsayılan 24 saat (saniye)
        
        # Şifre oluşturma için kelime listeleri
        self.adjectives = [
            'Mavi', 'Kirmizi', 'Yesil', 'Sari', 'Mor', 'Turuncu', 'Beyaz', 'Siyah', 'Gumus', 'Altin',
            'Parlak', 'Koyu', 'Acik', 'Sicak', 'Soguk', 'Buyuk', 'Kucuk', 'Genis', 'Dar', 'Uzun'
        ]
        self.nouns = [
            'Kalem', 'Defter', 'Kitap', 'Masa', 'Sandalye', 'Lamba', 'Bilgisayar', 'Telefon', 'Saat', 'Anahtar',
            'Kapi', 'Pencere', 'Duvar', 'Tavan', 'Zemin', 'Bardak', 'Tabak', 'Catal', 'Bicak', 'Kasik'
        ]
        
        # Token tablosunu oluştur
        self._create_token_table()
    
    def _create_token_table(self):
        """Token tablosunu oluştur (MySQL uyumlu)"""
        try:
            # Token tablosu var mı kontrol et (MySQL)
            table_check = self.db.execute_query("SHOW TABLES LIKE 'tokens';")

            if not table_check:
                # Tablo yoksa oluştur (MySQL uyumlu)
                self.db.execute_query('''
                CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,
                    data TEXT,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                ''')

                # İndeks oluştur (MySQL'de IF NOT EXISTS yok, hata olursa göz ardı et)
                try:
                    self.db.execute_query('CREATE INDEX idx_tokens_token ON tokens (token);')
                except Exception:
                    pass
                try:
                    self.db.execute_query('CREATE INDEX idx_tokens_user_id ON tokens (user_id);')
                except Exception:
                    pass

                self.log('Token tablosu oluşturuldu', 'info')
        except Exception as e:
            self.log(f'Token tablosu oluşturma hatası: {str(e)}', 'error')
    
    def generate_token(self, user_id: int, token_type: str = 'reset_password', data: Dict[str, Any] = None, expiry: int = None) -> Optional[str]:
        """
        Güvenli token oluştur ve veritabanına kaydet
        
        Args:
            user_id: Kullanıcı ID'si
            token_type: Token tipi (reset_password, email_verification, vb.)
            data: Token ile ilişkili ek veri
            expiry: Geçerlilik süresi (saniye), None ise varsayılan değer kullanılır
            
        Returns:
            str: Oluşturulan token, hata durumunda None
        """
        try:
            # Önceki aynı tipte token'ları temizle
            self._clean_user_tokens(user_id, token_type)
            
            # Benzersiz token oluştur
            token = secrets.token_urlsafe(32)
            
            # Son kullanma tarihi hesapla
            if expiry is None:
                expiry = self.token_expiry
                
            expires_at = datetime.now() + timedelta(seconds=expiry)
            
            # Veriyi JSON'a çevir
            data_json = json.dumps(data) if data else None
            
            # Token'ı veritabanına kaydet
            query = '''
            INSERT INTO tokens (user_id, token, type, data, expires_at)
            VALUES (?, ?, ?, ?, ?)
            '''
            
            self.db.execute_query(
                query, 
                (user_id, token, token_type, data_json, expires_at.isoformat())
            )
            
            return token
            
        except Exception as e:
            self.log(f'Token oluşturma hatası: {str(e)}', 'error')
            return None
    
    def verify_token(self, token: str, token_type: str = 'reset_password') -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Token'ı doğrula
        
        Args:
            token: Doğrulanacak token
            token_type: Token tipi
            
        Returns:
            Tuple[bool, Optional[Dict]]: (Geçerli mi, Token verisi)
        """
        try:
            # Süresi dolmuş token'ları temizle
            self._clean_expired_tokens()
            
            # Token'ı kontrol et
            query = '''
            SELECT id, user_id, data, expires_at
            FROM tokens
            WHERE token = ? AND type = ?
            '''
            
            result = self.db.execute_query(query, (token, token_type))
            
            if not result:
                return False, None
            
            token_data = result[0]
            
            # Son kullanma tarihini kontrol et
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            
            if datetime.now() > expires_at:
                return False, None
            
            # Token verisini hazırla
            data = {
                'token_id': token_data['id'],
                'user_id': token_data['user_id']
            }
            
            # Ek veri varsa ekle
            if token_data['data']:
                try:
                    extra_data = json.loads(token_data['data'])
                    if isinstance(extra_data, dict):
                        data.update(extra_data)
                except:
                    pass
            
            return True, data
            
        except Exception as e:
            self.log(f'Token doğrulama hatası: {str(e)}', 'error')
            return False, None
    
    def invalidate_token(self, token: str) -> bool:
        """
        Token'ı geçersiz kıl (veritabanından sil)
        
        Args:
            token: Geçersiz kılınacak token
            
        Returns:
            bool: Başarılı mı
        """
        try:
            query = 'DELETE FROM tokens WHERE token = ?'
            self.db.execute_query(query, (token,))
            return True
        except Exception as e:
            self.log(f'Token geçersiz kılma hatası: {str(e)}', 'error')
            return False
    
    def generate_memorable_password(self, length: int = 8) -> str:
        """
        Anlamlı ve hatırlanabilir geçici şifre oluştur
        
        Args:
            length: Şifre uzunluğu
            
        Returns:
            str: Oluşturulan şifre
        """
        # Rastgele bir sıfat ve isim seç
        adjective = random.choice(self.adjectives)
        noun = random.choice(self.nouns)
        
        # 2 rastgele sayı ekle (10-99 arası)
        numbers = str(random.randint(10, 99))
        
        # Şifre oluştur
        password = adjective + noun + numbers
        
        # Şifrenin uzunluğunu kontrol et ve gerekirse kırp
        if len(password) > length:
            password = password[:length]
        
        # En az bir büyük harf, bir küçük harf ve bir sayı içerdiğinden emin ol
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        # Eğer eksik karakter türü varsa ekle
        if not has_upper:
            # Rastgele bir pozisyona büyük harf ekle
            pos = random.randint(0, len(password)-1)
            password = password[:pos] + random.choice(string.ascii_uppercase) + password[pos+1:]
        
        if not has_lower:
            # Rastgele bir pozisyona küçük harf ekle
            pos = random.randint(0, len(password)-1)
            password = password[:pos] + random.choice(string.ascii_lowercase) + password[pos+1:]
        
        if not has_digit:
            # Rastgele bir pozisyona sayı ekle
            pos = random.randint(0, len(password)-1)
            password = password[:pos] + random.choice(string.digits) + password[pos+1:]
        
        return password
    
    def store_temporary_password(self, user_id: int, password: str, expiry: int = None) -> Optional[str]:
        """
        Geçici şifre oluştur ve sakla
        
        Args:
            user_id: Kullanıcı ID'si
            password: Şifre (hash'lenmemiş)
            expiry: Geçerlilik süresi (saniye), None ise varsayılan değer kullanılır
            
        Returns:
            str: Oluşturulan token, hata durumunda None
        """
        if expiry is None:
            expiry = self.password_expiry
        
        # Şifreyi hash'le
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Token verisi
        data = {
            'password_hash': password_hash,
            'password_plain': password  # Güvenli olmayan bir yöntem, sadece geçici şifreler için
        }
        
        # Token oluştur
        return self.generate_token(user_id, 'temporary_password', data, expiry)
    
    def verify_temporary_password(self, token: str, password: str) -> Tuple[bool, Optional[int]]:
        """
        Geçici şifreyi doğrula
        
        Args:
            token: Doğrulama token'ı
            password: Kontrol edilecek şifre
            
        Returns:
            Tuple[bool, Optional[int]]: (Geçerli mi, Kullanıcı ID)
        """
        # Token'ı doğrula
        valid, token_data = self.verify_token(token, 'temporary_password')
        
        if not valid or not token_data:
            return False, None
        
        # Şifreyi kontrol et
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if token_data.get('password_hash') == password_hash:
            return True, token_data.get('user_id')
        
        return False, None
    
    def _clean_expired_tokens(self):
        """Süresi dolmuş token'ları temizle"""
        try:
            query = 'DELETE FROM tokens WHERE expires_at < ?'
            self.db.execute_query(query, (datetime.now().isoformat(),))
        except Exception as e:
            self.log(f'Token temizleme hatası: {str(e)}', 'error')
    
    def _clean_user_tokens(self, user_id: int, token_type: str):
        """Kullanıcının belirli tipteki token'larını temizle"""
        try:
            query = 'DELETE FROM tokens WHERE user_id = ? AND type = ?'
            self.db.execute_query(query, (user_id, token_type))
        except Exception as e:
            self.log(f'Kullanıcı token temizleme hatası: {str(e)}', 'error')

# Global token service instance
_token_service = None

def get_token_service() -> TokenService:
    """Global token service instance'ını al"""
    global _token_service
    if _token_service is None:
        _token_service = TokenService()
    return _token_service 