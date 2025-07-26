"""
Email Box Module
E-posta kutusu ve bildirim işlevleri
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Callable

class EmailBox:
    """
    E-posta kutusu yöneticisi
    Gelen ve giden e-postaları takip etme ve yönetme
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        E-posta kutusu başlat
        
        Args:
            config: Konfigürasyon ayarları
        """
        self.config = config or {}
        
        # Temel dizinleri belirle
        self.base_dir = self.config.get('base_dir') or os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        self.storage_dir = os.path.join(self.base_dir, self.config.get('storage_dir', 'storage'))
        self.emails_dir = os.path.join(self.storage_dir, self.config.get('emails_dir', 'emails'))
        
        # Dosya adı formatları
        self.inbox_file = self.config.get('inbox_file', 'inbox.json')
        self.outbox_file = self.config.get('outbox_file', 'outbox.json')
        
        # Dizinleri oluştur
        os.makedirs(self.emails_dir, exist_ok=True)
        
        # Callback fonksiyonları
        self.callbacks = {
            'on_new_email': None,
            'on_email_read': None,
            'on_email_deleted': None
        }
    
    def register_callback(self, event: str, callback: Callable):
        """
        Olay için callback fonksiyonu kaydet
        
        Args:
            event: Olay adı ('on_new_email', 'on_email_read', 'on_email_deleted')
            callback: Callback fonksiyonu
        """
        if event in self.callbacks:
            self.callbacks[event] = callback
    
    def add_to_inbox(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gelen kutusuna e-posta ekle
        
        Args:
            email_data: E-posta verileri (subject, from, to, body, attachments, meta)
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # E-posta verilerini doğrula
            if not self._validate_email(email_data, is_incoming=True):
                return {
                    'status': 'error',
                    'message': 'Geçersiz e-posta verileri'
                }
            
            # E-posta ID'si ve zaman damgası ekle
            email_data['id'] = self._generate_id()
            email_data['timestamp'] = datetime.now().isoformat()
            email_data['read'] = False
            
            # Gelen kutusunu yükle
            inbox = self._load_inbox()
            
            # E-postayı ekle
            inbox.append(email_data)
            
            # Gelen kutusunu kaydet
            self._save_inbox(inbox)
            
            # Callback çağır
            if self.callbacks['on_new_email']:
                self.callbacks['on_new_email'](email_data)
            
            return {
                'status': 'success',
                'message': 'E-posta gelen kutusuna eklendi',
                'email_id': email_data['id']
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'E-posta eklenirken hata oluştu: {str(e)}'
            }
    
    def add_to_outbox(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Giden kutusuna e-posta ekle
        
        Args:
            email_data: E-posta verileri (subject, from, to, body, attachments, meta)
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # E-posta verilerini doğrula
            if not self._validate_email(email_data, is_incoming=False):
                return {
                    'status': 'error',
                    'message': 'Geçersiz e-posta verileri'
                }
            
            # E-posta ID'si ve zaman damgası ekle
            email_data['id'] = self._generate_id()
            email_data['timestamp'] = datetime.now().isoformat()
            email_data['status'] = email_data.get('status', 'pending')
            
            # Giden kutusunu yükle
            outbox = self._load_outbox()
            
            # E-postayı ekle
            outbox.append(email_data)
            
            # Giden kutusunu kaydet
            self._save_outbox(outbox)
            
            return {
                'status': 'success',
                'message': 'E-posta giden kutusuna eklendi',
                'email_id': email_data['id']
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'E-posta eklenirken hata oluştu: {str(e)}'
            }
    
    def get_inbox(self, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Gelen kutusundaki e-postaları al
        
        Args:
            filters: Filtreler (read, from, to, subject)
            page: Sayfa numarası
            per_page: Sayfa başına öğe sayısı
            
        Returns:
            Dict: Gelen kutusu e-postaları ve meta veriler
        """
        try:
            # Gelen kutusunu yükle
            inbox = self._load_inbox()
            
            # Filtreleme yap
            if filters:
                filtered_inbox = []
                for email in inbox:
                    match = True
                    for key, value in filters.items():
                        if key in email and email[key] != value:
                            match = False
                            break
                    if match:
                        filtered_inbox.append(email)
                inbox = filtered_inbox
            
            # Sıralama (en yeni en üstte)
            inbox.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Sayfalama
            total = len(inbox)
            total_pages = (total + per_page - 1) // per_page
            start = (page - 1) * per_page
            end = min(start + per_page, total)
            
            return {
                'status': 'success',
                'data': inbox[start:end],
                'meta': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Gelen kutusu yüklenirken hata oluştu: {str(e)}'
            }
    
    def get_outbox(self, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Giden kutusundaki e-postaları al
        
        Args:
            filters: Filtreler (status, from, to, subject)
            page: Sayfa numarası
            per_page: Sayfa başına öğe sayısı
            
        Returns:
            Dict: Giden kutusu e-postaları ve meta veriler
        """
        try:
            # Giden kutusunu yükle
            outbox = self._load_outbox()
            
            # Filtreleme yap
            if filters:
                filtered_outbox = []
                for email in outbox:
                    match = True
                    for key, value in filters.items():
                        if key in email and email[key] != value:
                            match = False
                            break
                    if match:
                        filtered_outbox.append(email)
                outbox = filtered_outbox
            
            # Sıralama (en yeni en üstte)
            outbox.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Sayfalama
            total = len(outbox)
            total_pages = (total + per_page - 1) // per_page
            start = (page - 1) * per_page
            end = min(start + per_page, total)
            
            return {
                'status': 'success',
                'data': outbox[start:end],
                'meta': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Giden kutusu yüklenirken hata oluştu: {str(e)}'
            }
    
    def get_email(self, email_id: str, mark_as_read: bool = False) -> Dict[str, Any]:
        """
        Belirtilen ID'ye sahip e-postayı al
        
        Args:
            email_id: E-posta ID'si
            mark_as_read: Okundu olarak işaretlensin mi
            
        Returns:
            Dict: E-posta verileri veya hata
        """
        try:
            # Önce gelen kutusunda ara
            inbox = self._load_inbox()
            for email in inbox:
                if email.get('id') == email_id:
                    if mark_as_read and not email.get('read'):
                        email['read'] = True
                        self._save_inbox(inbox)
                        
                        # Callback çağır
                        if self.callbacks['on_email_read']:
                            self.callbacks['on_email_read'](email)
                    
                    return {
                        'status': 'success',
                        'data': email,
                        'source': 'inbox'
                    }
            
            # Giden kutusunda ara
            outbox = self._load_outbox()
            for email in outbox:
                if email.get('id') == email_id:
                    return {
                        'status': 'success',
                        'data': email,
                        'source': 'outbox'
                    }
            
            # Bulunamadı
            return {
                'status': 'error',
                'message': 'E-posta bulunamadı'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'E-posta alınırken hata oluştu: {str(e)}'
            }
    
    def mark_as_read(self, email_id: str) -> Dict[str, Any]:
        """
        E-postayı okundu olarak işaretle
        
        Args:
            email_id: E-posta ID'si
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Gelen kutusunu yükle
            inbox = self._load_inbox()
            
            # E-postayı bul ve güncelle
            for email in inbox:
                if email.get('id') == email_id:
                    if not email.get('read'):
                        email['read'] = True
                        self._save_inbox(inbox)
                        
                        # Callback çağır
                        if self.callbacks['on_email_read']:
                            self.callbacks['on_email_read'](email)
                        
                        return {
                            'status': 'success',
                            'message': 'E-posta okundu olarak işaretlendi'
                        }
                    else:
                        return {
                            'status': 'info',
                            'message': 'E-posta zaten okundu olarak işaretlenmiş'
                        }
            
            # E-posta bulunamadı
            return {
                'status': 'error',
                'message': 'E-posta bulunamadı'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'E-posta işaretlenirken hata oluştu: {str(e)}'
            }
    
    def delete_email(self, email_id: str, source: str = None) -> Dict[str, Any]:
        """
        E-postayı sil
        
        Args:
            email_id: E-posta ID'si
            source: Kaynak ('inbox' veya 'outbox'), belirtilmezse her ikisinde de aranır
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            deleted = False
            deleted_email = None
            
            # Gelen kutusundan sil
            if source is None or source == 'inbox':
                inbox = self._load_inbox()
                for i, email in enumerate(inbox):
                    if email.get('id') == email_id:
                        deleted_email = email
                        del inbox[i]
                        self._save_inbox(inbox)
                        deleted = True
                        
                        # Callback çağır
                        if self.callbacks['on_email_deleted']:
                            self.callbacks['on_email_deleted'](deleted_email, 'inbox')
                        
                        break
            
            # Giden kutusundan sil
            if (source is None or source == 'outbox') and not deleted:
                outbox = self._load_outbox()
                for i, email in enumerate(outbox):
                    if email.get('id') == email_id:
                        deleted_email = email
                        del outbox[i]
                        self._save_outbox(outbox)
                        deleted = True
                        
                        # Callback çağır
                        if self.callbacks['on_email_deleted']:
                            self.callbacks['on_email_deleted'](deleted_email, 'outbox')
                        
                        break
            
            if deleted:
                return {
                    'status': 'success',
                    'message': 'E-posta silindi'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'E-posta bulunamadı'
                }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'E-posta silinirken hata oluştu: {str(e)}'
            }
    
    def update_outbox_status(self, email_id: str, status: str) -> Dict[str, Any]:
        """
        Giden kutusundaki e-postanın durumunu güncelle
        
        Args:
            email_id: E-posta ID'si
            status: Yeni durum ('pending', 'sent', 'failed')
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Giden kutusunu yükle
            outbox = self._load_outbox()
            
            # E-postayı bul ve güncelle
            for email in outbox:
                if email.get('id') == email_id:
                    email['status'] = status
                    if status == 'sent':
                        email['sent_at'] = datetime.now().isoformat()
                    self._save_outbox(outbox)
                    return {
                        'status': 'success',
                        'message': f'E-posta durumu güncellendi: {status}'
                    }
            
            # E-posta bulunamadı
            return {
                'status': 'error',
                'message': 'E-posta bulunamadı'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'E-posta durumu güncellenirken hata oluştu: {str(e)}'
            }
    
    def clear_inbox(self) -> Dict[str, Any]:
        """
        Gelen kutusunu temizle
        
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Boş gelen kutusu kaydet
            self._save_inbox([])
            return {
                'status': 'success',
                'message': 'Gelen kutusu temizlendi'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Gelen kutusu temizlenirken hata oluştu: {str(e)}'
            }
    
    def clear_outbox(self) -> Dict[str, Any]:
        """
        Giden kutusunu temizle
        
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Boş giden kutusu kaydet
            self._save_outbox([])
            return {
                'status': 'success',
                'message': 'Giden kutusu temizlendi'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Giden kutusu temizlenirken hata oluştu: {str(e)}'
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        E-posta istatistiklerini al
        
        Returns:
            Dict: İstatistikler
        """
        try:
            inbox = self._load_inbox()
            outbox = self._load_outbox()
            
            # İstatistikleri hesapla
            unread_count = sum(1 for email in inbox if not email.get('read', False))
            inbox_count = len(inbox)
            outbox_count = len(outbox)
            pending_count = sum(1 for email in outbox if email.get('status') == 'pending')
            sent_count = sum(1 for email in outbox if email.get('status') == 'sent')
            failed_count = sum(1 for email in outbox if email.get('status') == 'failed')
            
            return {
                'status': 'success',
                'data': {
                    'inbox': {
                        'total': inbox_count,
                        'unread': unread_count,
                        'read': inbox_count - unread_count
                    },
                    'outbox': {
                        'total': outbox_count,
                        'pending': pending_count,
                        'sent': sent_count,
                        'failed': failed_count
                    }
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'İstatistikler alınırken hata oluştu: {str(e)}'
            }
    
    def _load_inbox(self) -> List[Dict[str, Any]]:
        """
        Gelen kutusunu yükle
        
        Returns:
            List: E-posta listesi
        """
        inbox_path = os.path.join(self.emails_dir, self.inbox_file)
        if not os.path.exists(inbox_path):
            return []
        
        try:
            with open(inbox_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_inbox(self, inbox: List[Dict[str, Any]]):
        """
        Gelen kutusunu kaydet
        
        Args:
            inbox: E-posta listesi
        """
        inbox_path = os.path.join(self.emails_dir, self.inbox_file)
        with open(inbox_path, 'w', encoding='utf-8') as f:
            json.dump(inbox, f, ensure_ascii=False, indent=2)
    
    def _load_outbox(self) -> List[Dict[str, Any]]:
        """
        Giden kutusunu yükle
        
        Returns:
            List: E-posta listesi
        """
        outbox_path = os.path.join(self.emails_dir, self.outbox_file)
        if not os.path.exists(outbox_path):
            return []
        
        try:
            with open(outbox_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_outbox(self, outbox: List[Dict[str, Any]]):
        """
        Giden kutusunu kaydet
        
        Args:
            outbox: E-posta listesi
        """
        outbox_path = os.path.join(self.emails_dir, self.outbox_file)
        with open(outbox_path, 'w', encoding='utf-8') as f:
            json.dump(outbox, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self) -> str:
        """
        Benzersiz ID oluştur
        
        Returns:
            str: Benzersiz ID
        """
        import uuid
        return str(uuid.uuid4())
    
    def _validate_email(self, email_data: Dict[str, Any], is_incoming: bool = False) -> bool:
        """
        E-posta verilerini doğrula
        
        Args:
            email_data: E-posta verileri
            is_incoming: Gelen e-posta mı
            
        Returns:
            bool: Geçerli mi
        """
        required_fields = ['subject', 'body']
        
        if is_incoming:
            required_fields.append('from')
            required_fields.append('to')
        else:
            required_fields.append('to')
        
        # Gerekli alanları kontrol et
        for field in required_fields:
            if field not in email_data:
                return False
        
        return True


# Global email box instance
_email_box = None

def get_email_box(config: Dict[str, Any] = None) -> EmailBox:
    """
    EmailBox singleton instance'ını al
    
    Args:
        config: Konfigürasyon ayarları
        
    Returns:
        EmailBox: Email box instance
    """
    global _email_box
    if _email_box is None:
        _email_box = EmailBox(config)
    elif config:
        # Konfigürasyon değişti, yeni instance oluştur
        _email_box = EmailBox(config)
    return _email_box 