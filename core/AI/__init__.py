"""
PofuAi - Advanced AI System
============================

Gelişmiş yapay zeka sistemi modülleri
- Görsel tanıma ve kategorilendirme
- Kullanıcı bazlı içerik yönetimi
- Akıllı depolama sistemi
- Enterprise seviye AI özellikleri
"""

# Lazy loading için import'ları fonksiyon içinde yapacağız
def get_image_recognition_service():
    """ImageRecognitionService'i lazy loading ile yükle"""
    try:
        from .image_recognition import ImageRecognitionService
        return ImageRecognitionService
    except ImportError as e:
        print(f"ImageRecognitionService yüklenemedi: {e}")
        return None

def get_content_categorizer_service():
    """ContentCategorizerService'i lazy loading ile yükle"""
    try:
        from .content_categorizer import ContentCategorizerService
        return ContentCategorizerService
    except ImportError as e:
        print(f"ContentCategorizerService yüklenemedi: {e}")
        return None

def get_user_content_manager_service():
    """UserContentManagerService'i lazy loading ile yükle"""
    try:
        from .user_content_manager import UserContentManagerService
        return UserContentManagerService
    except ImportError as e:
        print(f"UserContentManagerService yüklenemedi: {e}")
        return None

def get_smart_storage_service():
    """SmartStorageService'i lazy loading ile yükle"""
    try:
        from .smart_storage import SmartStorageService
        return SmartStorageService
    except ImportError as e:
        print(f"SmartStorageService yüklenemedi: {e}")
        return None

def get_ai_core():
    """AICore'u lazy loading ile yükle"""
    try:
        from .ai_core import AICore
        return AICore
    except ImportError as e:
        print(f"AICore yüklenemedi: {e}")
        return None

# Backward compatibility için - Lazy loading, sadece istendiğinde yükle
# Startup sırasında AI servislerini yükleme, sadece çağrıldığında yükle
ImageRecognitionService = None
ContentCategorizerService = None
UserContentManagerService = None
SmartStorageService = None
AICore = None

__all__ = [
    'get_image_recognition_service',
    'get_content_categorizer_service', 
    'get_user_content_manager_service',
    'get_smart_storage_service',
    'get_ai_core',
    'ImageRecognitionService',
    'ContentCategorizerService', 
    'UserContentManagerService',
    'SmartStorageService',
    'AICore'
]

__version__ = '1.0.0'
__author__ = 'PofuAi Development Team'