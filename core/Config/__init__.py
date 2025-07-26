"""
PofuAi Config Module
Merkezi konfigürasyon yönetimi
"""

from .config import (
    Config,
    get_config,
)

# Çevre değişkenlerini almak için yardımcı fonksiyon
def get_env(key, default=None):
    """
    Çevre değişkenini al
    
    Args:
        key (str): Çevre değişkeni adı
        default (Any, optional): Varsayılan değer
        
    Returns:
        Any: Çevre değişkeni değeri veya varsayılan değer
    """
    import os
    return os.environ.get(key, default)

__all__ = [
    'Config',
    'get_config',
    'get_env',
]

# Versiyon bilgisi
__version__ = "2.0.0"
__author__ = "PofuAi Team"
__description__ = "Merkezi konfigürasyon yönetimi" 