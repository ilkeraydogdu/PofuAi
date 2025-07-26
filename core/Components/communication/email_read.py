"""
Email Read Component
E-posta okuma bileşeni
"""
from typing import Dict, Any, List, Optional

class EmailReadComponent:
    """E-posta okuma bileşeni"""
    
    def __init__(self):
        """E-posta okuma bileşenini başlat"""
        pass
    
    def render(self, props: Dict[str, Any] = None) -> str:
        """E-posta okuma bileşenini render et"""
        props = props or {}
        
        # Varsayılan değerler
        email = props.get('email', {})
        show_reply = props.get('show_reply', True)
        show_actions = props.get('show_actions', True)
        
        # E-posta detayları
        sender = email.get('sender', {})
        recipients = email.get('recipients', [])
        attachments = email.get('attachments', [])
        
        # Alıcıları formatlama
        recipients_html = ""
        for recipient in recipients:
            recipients_html += f"""
            <span class="badge bg-light text-dark me-1 mb-1">{recipient.get('name', '')} &lt;{recipient.get('email', '')}&gt;</span>
            """
        
        # Ekleri formatlama
        attachments_html = ""
        if attachments:
            attachments_html = """
            <div class="email-attachments mt-4 p-3 border rounded">
                <h6 class="mb-3"><i class="bi bi-paperclip me-2"></i>Ekler</h6>
                <div class="d-flex flex-wrap">
            """
            
            for attachment in attachments:
                file_type = attachment.get('type', 'file')
                icon = 'bi-file-earmark'
                
                if 'image' in file_type:
                    icon = 'bi-file-earmark-image'
                elif 'pdf' in file_type:
                    icon = 'bi-file-earmark-pdf'
                elif 'word' in file_type or 'doc' in file_type:
                    icon = 'bi-file-earmark-word'
                elif 'excel' in file_type or 'sheet' in file_type:
                    icon = 'bi-file-earmark-excel'
                elif 'zip' in file_type or 'archive' in file_type:
                    icon = 'bi-file-earmark-zip'
                
                attachments_html += f"""
                <div class="attachment-item me-3 mb-3">
                    <div class="card" style="width: 120px;">
                        <div class="card-body p-2 text-center">
                            <i class="bi {icon} fs-3 mb-2"></i>
                            <p class="mb-1 text-truncate">{attachment.get('name', 'Dosya')}</p>
                            <small class="text-muted">{attachment.get('size', '')}</small>
                            <div class="mt-2">
                                <a href="#" class="btn btn-sm btn-outline-primary">İndir</a>
                            </div>
                        </div>
                    </div>
                </div>
                """
            
            attachments_html += """
                </div>
            </div>
            """
        
        # E-posta okuma
        html = f"""
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">{email.get('subject', 'Konu yok')}</h5>
                {self._render_actions() if show_actions else ''}
            </div>
            <div class="card-body">
                <div class="email-header mb-4">
                    <div class="d-flex align-items-center mb-3">
                        <div class="email-sender-avatar me-3">
                            <img src="{sender.get('avatar', '/static/assets/images/avatars/01.png')}" class="rounded-circle" width="48" alt="Sender">
                        </div>
                        <div class="email-sender-info">
                            <h6 class="mb-1">{sender.get('name', 'Gönderen')}</h6>
                            <p class="mb-0 text-muted">{sender.get('email', '')}</p>
                        </div>
                        <div class="email-time ms-auto text-muted">
                            {email.get('date', '')}
                        </div>
                    </div>
                    
                    <div class="email-recipients mb-3">
                        <p class="mb-1"><strong>Kime:</strong></p>
                        <div class="d-flex flex-wrap">
                            {recipients_html if recipients else '<span class="text-muted">Alıcı yok</span>'}
                        </div>
                    </div>
                </div>
                
                <div class="email-content">
                    {email.get('content', '')}
                </div>
                
                {attachments_html}
                
                {self._render_reply() if show_reply else ''}
            </div>
        </div>
        """
        
        return html
    
    def _render_actions(self) -> str:
        """Aksiyon butonlarını render et"""
        return """
        <div class="email-actions">
            <div class="btn-group">
                <button class="btn btn-sm btn-outline-secondary">
                    <i class="bi bi-reply"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary">
                    <i class="bi bi-reply-all"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary">
                    <i class="bi bi-forward"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary">
                    <i class="bi bi-trash"></i>
                </button>
                <button class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                    <i class="bi bi-three-dots"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li><a class="dropdown-item" href="#"><i class="bi bi-printer me-2"></i>Yazdır</a></li>
                    <li><a class="dropdown-item" href="#"><i class="bi bi-archive me-2"></i>Arşivle</a></li>
                    <li><a class="dropdown-item" href="#"><i class="bi bi-star me-2"></i>Yıldızla</a></li>
                    <li><a class="dropdown-item" href="#"><i class="bi bi-flag me-2"></i>İşaretle</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" href="#"><i class="bi bi-exclamation-triangle me-2"></i>Spam Olarak İşaretle</a></li>
                </ul>
            </div>
        </div>
        """
    
    def _render_reply(self) -> str:
        """Yanıt formunu render et"""
        return """
        <div class="email-reply mt-4">
            <h6 class="mb-3">Yanıtla</h6>
            <div class="card">
                <div class="card-body p-3">
                    <div class="mb-3">
                        <textarea class="form-control" rows="5" placeholder="Yanıtınızı buraya yazın..."></textarea>
                    </div>
                    <div class="d-flex justify-content-between">
                        <div class="email-attachments-buttons">
                            <button class="btn btn-sm btn-outline-secondary me-2">
                                <i class="bi bi-paperclip"></i> Dosya Ekle
                            </button>
                            <button class="btn btn-sm btn-outline-secondary">
                                <i class="bi bi-emoji-smile"></i>
                            </button>
                        </div>
                        <div class="email-send-buttons">
                            <button class="btn btn-sm btn-outline-secondary me-2">Taslak Kaydet</button>
                            <button class="btn btn-sm btn-primary">Gönder</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

# Singleton instance
_email_read_component = None

def get_email_read_component() -> EmailReadComponent:
    """Email read component singleton instance'ını al"""
    global _email_read_component
    if _email_read_component is None:
        _email_read_component = EmailReadComponent()
    return _email_read_component 