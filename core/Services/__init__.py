"""
Services Module
Merkezi servisler
"""

from .mail_service import get_mail_service
from .auth_page_service import AuthPageService
# from .UIService import UIService  # Flask dependency commented out
# from .ComponentService import ComponentService  # Flask dependency commented out
# from .PageService import PageService  # Flask dependency commented out
from .cache_service import CacheService
from .queue_service import QueueService
from .error_handler import ErrorHandler
from .logger import LoggerService as Logger
from .base_service import BaseService
from .notification_service import NotificationService

__all__ = [
    'get_mail_service',
    'AuthPageService',
    'UIService',
    'ComponentService',
    'PageService',
    'CacheService',
    'QueueService',
    'ErrorHandler',
    'Logger',
    'BaseService',
    'NotificationService'
] 