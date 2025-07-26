"""
Logger Service
Uygulama loglama hizmetleri
"""
import os
import logging
from logging.handlers import RotatingFileHandler
import sys
import traceback
from datetime import datetime

class LoggerService:
    """
    Logger servisi
    Uygulama genelinde log kaydı tutma işlemlerini yönetir
    """
    
    _logger = None
    
    @staticmethod
    def init(log_level=None):
        """
        Logger'ı başlat
        
        Args:
            log_level: Log seviyesi
        """
        if LoggerService._logger is not None:
            return LoggerService._logger
        
        # Konfigürasyondan log seviyesini al
        try:
            from core.Config.config import get_config
            config = get_config()
            
            # Log seviyesini belirle
            level_map = {
                'debug': logging.DEBUG,
                'info': logging.INFO,
                'warning': logging.WARNING,
                'error': logging.ERROR,
                'critical': logging.CRITICAL
            }
            
            # Parametre olarak verilen log seviyesi yoksa config'den al
            if log_level is None:
                log_level_str = config.get('logging.level', 'debug').lower()
                log_level = level_map.get(log_level_str, logging.DEBUG)
            
            # Log dizinini config'den al
            log_dir = config.get('logging.path')
            
            if not log_dir:
                # Varsayılan log dizini
                app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                log_dir = os.path.join(app_root, 'storage', 'logs')
                
        except Exception as e:
            # Varsayılan değerlerle devam et
            log_level = logging.DEBUG
            app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_dir = os.path.join(app_root, 'storage', 'logs')
            print(f"Log konfigürasyonu yüklenemedi: {e}")
            
        # Dizini oluştur
        os.makedirs(log_dir, exist_ok=True)
        
        # Tarih bazlı log dosya adı
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f'app_{today}.log')
        
        # Logger'ı oluştur
        logger = logging.getLogger('pofu_ai')
        
        # Önceden handler'lar eklenmiş olabilir, temizle
        if logger.hasHandlers():
            logger.handlers.clear()
            
        logger.setLevel(log_level)
        
        # Konsol handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter('%(levelname)s [%(asctime)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(console_formatter)
        
        # Dosya handler
        file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)  # 10MB, 5 yedek
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter('%(levelname)s [%(asctime)s] [%(module)s.%(funcName)s:%(lineno)d]: %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Handler'ları ekle
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        # Her zaman log yazdığından emin ol
        logger.propagate = False
        
        # Başlatma mesajı yaz
        logger.info(f"Logger başlatıldı - Seviye: {logging.getLevelName(log_level)}, Dosya: {log_file}")
        
        # Global logger'ı ayarla
        LoggerService._logger = logger
        
        return logger
    
    @staticmethod
    def get_logger():
        """
        Global logger'ı döndür, yoksa oluştur
        
        Returns:
            logging.Logger: Logger nesnesi
        """
        if LoggerService._logger is None:
            return LoggerService.init()
        return LoggerService._logger
    
    @staticmethod
    def log_exception(exception, level=logging.ERROR, include_traceback=True):
        """
        Exception'ı logla
        
        Args:
            exception (Exception): Log'lanacak hata
            level: Log seviyesi
            include_traceback (bool): Traceback eklensin mi
        """
        logger = LoggerService.get_logger()
        
        # Hata mesajı
        error_message = str(exception)
        
        # Traceback bilgilerini ekle
        if include_traceback:
            tb = traceback.format_exc()
            error_message = f"{error_message}\n{tb}"
        
        logger.log(level, error_message)
    
    @staticmethod
    def log_request(request, response=None):
        """
        HTTP isteğini logla
        
        Args:
            request: HTTP isteği
            response: HTTP yanıtı (isteğe bağlı)
        """
        logger = LoggerService.get_logger()
        
        if request is None:
            return
            
        # İstek detayları
        method = getattr(request, 'method', 'UNKNOWN')
        path = getattr(request, 'path', '/')
        remote_addr = getattr(request, 'remote_addr', '0.0.0.0')
        user_agent = request.headers.get('User-Agent', '-') if hasattr(request, 'headers') else '-'
        
        # Yanıt durumu
        status_code = getattr(response, 'status_code', '-') if response else '-'
        
        log_message = f"{remote_addr} {method} {path} {status_code} \"{user_agent}\""
        logger.info(log_message)
    
    @staticmethod
    def log_database_query(query, params=None, duration=None):
        """
        Veritabanı sorgusunu logla
        
        Args:
            query (str): SQL sorgusu
            params: Sorgu parametreleri
            duration: Sorgu süresi (saniye)
        """
        logger = LoggerService.get_logger()
        
        log_message = f"QUERY: {query}"
        
        if params:
            log_message += f" PARAMS: {params}"
        
        if duration is not None:
            log_message += f" DURATION: {duration:.4f}s"
        
        logger.debug(log_message)
    
    @staticmethod
    def log_api_request(endpoint, method, request_data=None, response_data=None, status_code=None, duration=None):
        """
        API isteğini logla
        
        Args:
            endpoint (str): API endpoint
            method (str): HTTP metodu
            request_data: İstek verileri
            response_data: Yanıt verileri
            status_code: HTTP durum kodu
            duration: İstek süresi (saniye)
        """
        logger = LoggerService.get_logger()
        
        log_message = f"API {method} {endpoint}"
        
        if status_code is not None:
            log_message += f" {status_code}"
        
        if duration is not None:
            log_message += f" {duration:.4f}s"
        
        logger.info(log_message)
        
        # Detaylı debug log
        if request_data:
            logger.debug(f"API Request Data: {request_data}")
        
        if response_data:
            logger.debug(f"API Response Data: {response_data}")

# Logger'ı başlat
logger = LoggerService.init() 