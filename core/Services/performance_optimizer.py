"""
Performance Optimization Service
Site yüklenme hızı ve performans optimizasyonu
"""
import os
import gzip
import zlib
import time
import json
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from flask import request, current_app, make_response, g
from core.Services.base_service import BaseService
from core.Services.logger import LoggerService
from core.Services.cache_service import CacheService
from core.Database.connection import get_connection
from dataclasses import dataclass
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc

class OptimizationType(Enum):
    MINIFY_CSS = "minify_css"
    MINIFY_JS = "minify_js"
    COMPRESS_IMAGES = "compress_images"
    GZIP_CONTENT = "gzip_content"
    CACHE_STATIC = "cache_static"
    DATABASE_QUERY = "database_query"
    MEMORY_USAGE = "memory_usage"

@dataclass
class PerformanceMetric:
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    category: str

@dataclass
class OptimizationResult:
    type: OptimizationType
    original_size: int
    optimized_size: int
    savings_bytes: int
    savings_percent: float
    processing_time: float

class PerformanceOptimizer(BaseService):
    """Site performans optimizasyonu"""
    
    def __init__(self):
        super().__init__()
        self.logger = LoggerService.get_logger()
        self.cache = CacheService()
        self.connection = get_connection()
        
        # Performance thresholds
        self.thresholds = {
            'page_load_time': 3.0,  # seconds
            'database_query_time': 0.1,  # seconds
            'memory_usage': 80,  # percent
            'cpu_usage': 70,  # percent
            'cache_hit_ratio': 0.8  # 80%
        }
        
        # Optimization settings
        self.optimization_settings = {
            'enable_gzip': True,
            'enable_minification': True,
            'enable_image_compression': True,
            'enable_static_caching': True,
            'cache_duration': 86400,  # 24 hours
            'max_file_size_for_minification': 1024 * 1024,  # 1MB
        }
        
        # Thread pool for async optimizations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def optimize_response(self, response, endpoint: str = None) -> Any:
        """Response optimizasyonu"""
        try:
            start_time = time.time()
            
            # Response type kontrolü
            content_type = response.headers.get('Content-Type', '')
            
            # Static file optimizations
            if self._is_static_file(endpoint):
                response = self._optimize_static_file(response, endpoint)
            
            # HTML optimization
            elif 'text/html' in content_type:
                response = self._optimize_html_response(response)
            
            # CSS optimization
            elif 'text/css' in content_type:
                response = self._optimize_css_response(response)
            
            # JavaScript optimization
            elif 'application/javascript' in content_type or 'text/javascript' in content_type:
                response = self._optimize_js_response(response)
            
            # JSON optimization
            elif 'application/json' in content_type:
                response = self._optimize_json_response(response)
            
            # Gzip compression
            if self.optimization_settings['enable_gzip']:
                response = self._apply_gzip_compression(response)
            
            # Cache headers
            if self.optimization_settings['enable_static_caching']:
                response = self._set_cache_headers(response, endpoint)
            
            # Security headers
            response = self._set_security_headers(response)
            
            # Performance metrics
            processing_time = time.time() - start_time
            self._record_performance_metric('response_optimization_time', processing_time, 'seconds', 'optimization')
            
            return response
            
        except Exception as e:
            self.logger.error(f"Response optimization error: {str(e)}")
            return response
    
    def _optimize_html_response(self, response) -> Any:
        """HTML response optimizasyonu"""
        try:
            if not hasattr(response, 'data'):
                return response
            
            html_content = response.get_data(as_text=True)
            
            # HTML minification
            if self.optimization_settings['enable_minification']:
                html_content = self._minify_html(html_content)
            
            # Critical CSS inline
            html_content = self._inline_critical_css(html_content)
            
            # Lazy loading attributes
            html_content = self._add_lazy_loading(html_content)
            
            # Preload hints
            html_content = self._add_preload_hints(html_content)
            
            response.set_data(html_content)
            
            return response
            
        except Exception as e:
            self.logger.error(f"HTML optimization error: {str(e)}")
            return response
    
    def _minify_html(self, html: str) -> str:
        """HTML minification"""
        try:
            import re
            
            # Remove comments
            html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
            
            # Remove extra whitespace
            html = re.sub(r'\s+', ' ', html)
            
            # Remove whitespace around tags
            html = re.sub(r'>\s+<', '><', html)
            
            return html.strip()
            
        except Exception as e:
            self.logger.error(f"HTML minification error: {str(e)}")
            return html
    
    def _optimize_css_response(self, response) -> Any:
        """CSS response optimizasyonu"""
        try:
            css_content = response.get_data(as_text=True)
            
            # CSS minification
            if self.optimization_settings['enable_minification']:
                css_content = self._minify_css(css_content)
            
            response.set_data(css_content)
            
            return response
            
        except Exception as e:
            self.logger.error(f"CSS optimization error: {str(e)}")
            return response
    
    def _minify_css(self, css: str) -> str:
        """CSS minification"""
        try:
            import re
            
            # Remove comments
            css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
            
            # Remove extra whitespace
            css = re.sub(r'\s+', ' ', css)
            
            # Remove whitespace around specific characters
            css = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css)
            
            # Remove trailing semicolons
            css = re.sub(r';}', '}', css)
            
            return css.strip()
            
        except Exception as e:
            self.logger.error(f"CSS minification error: {str(e)}")
            return css
    
    def _optimize_js_response(self, response) -> Any:
        """JavaScript response optimizasyonu"""
        try:
            js_content = response.get_data(as_text=True)
            
            # JS minification
            if self.optimization_settings['enable_minification']:
                js_content = self._minify_js(js_content)
            
            response.set_data(js_content)
            
            return response
            
        except Exception as e:
            self.logger.error(f"JS optimization error: {str(e)}")
            return response
    
    def _minify_js(self, js: str) -> str:
        """JavaScript minification (basic)"""
        try:
            import re
            
            # Remove single line comments (but preserve URLs)
            js = re.sub(r'(?<!:)//(?![^\r\n]*["\']).*$', '', js, flags=re.MULTILINE)
            
            # Remove multi-line comments
            js = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL)
            
            # Remove extra whitespace
            js = re.sub(r'\s+', ' ', js)
            
            # Remove whitespace around operators and punctuation
            js = re.sub(r'\s*([{}();,=+\-*/<>!&|])\s*', r'\1', js)
            
            return js.strip()
            
        except Exception as e:
            self.logger.error(f"JS minification error: {str(e)}")
            return js
    
    def _apply_gzip_compression(self, response) -> Any:
        """Gzip compression uygula"""
        try:
            # Gzip için uygun content type kontrolü
            content_type = response.headers.get('Content-Type', '')
            compressible_types = [
                'text/html', 'text/css', 'text/javascript',
                'application/javascript', 'application/json',
                'text/xml', 'application/xml', 'text/plain'
            ]
            
            if not any(ct in content_type for ct in compressible_types):
                return response
            
            # Client gzip desteği kontrolü
            if request and 'gzip' not in request.headers.get('Accept-Encoding', ''):
                return response
            
            # Content boyutu kontrolü (çok küçük dosyalar için gzip gereksiz)
            content = response.get_data()
            if len(content) < 1024:  # 1KB'dan küçük
                return response
            
            # Gzip compression
            compressed_content = gzip.compress(content)
            
            # Compression oranı kontrolü
            compression_ratio = len(compressed_content) / len(content)
            if compression_ratio > 0.9:  # %10'dan az sıkıştırma
                return response
            
            response.set_data(compressed_content)
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = str(len(compressed_content))
            response.headers['Vary'] = 'Accept-Encoding'
            
            # Metrics
            savings = len(content) - len(compressed_content)
            self._record_performance_metric('gzip_savings_bytes', savings, 'bytes', 'compression')
            
            return response
            
        except Exception as e:
            self.logger.error(f"Gzip compression error: {str(e)}")
            return response
    
    def _set_cache_headers(self, response, endpoint: str = None) -> Any:
        """Cache header'ları ayarla"""
        try:
            # Static file cache duration
            if self._is_static_file(endpoint):
                cache_duration = self.optimization_settings['cache_duration']
                response.headers['Cache-Control'] = f'public, max-age={cache_duration}'
                
                # ETag for cache validation
                content = response.get_data()
                etag = hashlib.md5(content).hexdigest()
                response.headers['ETag'] = f'"{etag}"'
                
                # Last-Modified
                response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            # Dynamic content cache
            else:
                response.headers['Cache-Control'] = 'no-cache, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
            
            return response
            
        except Exception as e:
            self.logger.error(f"Cache headers error: {str(e)}")
            return response
    
    def _set_security_headers(self, response) -> Any:
        """Güvenlik header'ları ayarla"""
        try:
            # Security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # HTTPS only headers
            if request and request.is_secure:
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            return response
            
        except Exception as e:
            self.logger.error(f"Security headers error: {str(e)}")
            return response
    
    def optimize_database_queries(self) -> Dict[str, Any]:
        """Database query optimizasyonu"""
        try:
            optimization_results = {
                'slow_queries': [],
                'index_suggestions': [],
                'query_optimizations': [],
                'total_improvements': 0
            }
            
            # Slow query detection
            slow_queries = self._detect_slow_queries()
            optimization_results['slow_queries'] = slow_queries
            
            # Index analysis
            index_suggestions = self._analyze_indexes()
            optimization_results['index_suggestions'] = index_suggestions
            
            # Query optimization suggestions
            query_optimizations = self._suggest_query_optimizations()
            optimization_results['query_optimizations'] = query_optimizations
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Database optimization error: {str(e)}")
            return {'error': str(e)}
    
    def _detect_slow_queries(self) -> List[Dict[str, Any]]:
        """Yavaş sorguları tespit et"""
        try:
            slow_queries = []
            
            # MySQL slow query log analizi
            query = """
            SELECT 
                sql_text,
                avg_timer_wait/1000000000 as avg_time_seconds,
                count_star as execution_count,
                sum_timer_wait/1000000000 as total_time_seconds
            FROM performance_schema.events_statements_summary_by_digest 
            WHERE avg_timer_wait/1000000000 > %s
            ORDER BY avg_timer_wait DESC 
            LIMIT 10
            """
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, [self.thresholds['database_query_time']])
            results = cursor.fetchall()
            
            for result in results:
                slow_queries.append({
                    'query': result['sql_text'][:200] + '...' if len(result['sql_text']) > 200 else result['sql_text'],
                    'avg_time': result['avg_time_seconds'],
                    'execution_count': result['execution_count'],
                    'total_time': result['total_time_seconds']
                })
            
            return slow_queries
            
        except Exception as e:
            self.logger.error(f"Slow query detection error: {str(e)}")
            return []
    
    def monitor_system_performance(self) -> Dict[str, Any]:
        """Sistem performansını izle"""
        try:
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'used': psutil.virtual_memory().used,
                    'percent': psutil.virtual_memory().percent,
                    'available': psutil.virtual_memory().available
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'percent': psutil.disk_usage('/').percent,
                    'free': psutil.disk_usage('/').free
                },
                'network': dict(psutil.net_io_counters()._asdict()),
                'processes': len(psutil.pids()),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
            
            # Performance alerts
            alerts = []
            
            if performance_data['cpu_usage'] > self.thresholds['cpu_usage']:
                alerts.append(f"High CPU usage: {performance_data['cpu_usage']:.1f}%")
            
            if performance_data['memory']['percent'] > self.thresholds['memory_usage']:
                alerts.append(f"High memory usage: {performance_data['memory']['percent']:.1f}%")
            
            if performance_data['disk']['percent'] > 90:
                alerts.append(f"Low disk space: {performance_data['disk']['percent']:.1f}% used")
            
            performance_data['alerts'] = alerts
            
            # Cache performance data
            self.cache.set('system_performance', performance_data, 300)  # 5 minutes
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"System performance monitoring error: {str(e)}")
            return {'error': str(e)}
    
    def optimize_images_async(self, image_paths: List[str]) -> None:
        """Asenkron image optimization"""
        try:
            for image_path in image_paths:
                self.executor.submit(self._optimize_single_image, image_path)
        except Exception as e:
            self.logger.error(f"Async image optimization error: {str(e)}")
    
    def _optimize_single_image(self, image_path: str) -> OptimizationResult:
        """Tek image optimizasyonu"""
        try:
            from PIL import Image
            import os
            
            if not os.path.exists(image_path):
                return None
            
            original_size = os.path.getsize(image_path)
            start_time = time.time()
            
            # Image optimization
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large
                max_dimension = 1920
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Save with optimization
                img.save(image_path, optimize=True, quality=85)
            
            optimized_size = os.path.getsize(image_path)
            processing_time = time.time() - start_time
            
            savings_bytes = original_size - optimized_size
            savings_percent = (savings_bytes / original_size) * 100 if original_size > 0 else 0
            
            result = OptimizationResult(
                type=OptimizationType.COMPRESS_IMAGES,
                original_size=original_size,
                optimized_size=optimized_size,
                savings_bytes=savings_bytes,
                savings_percent=savings_percent,
                processing_time=processing_time
            )
            
            self.logger.info(f"Image optimized: {image_path}, saved {savings_bytes} bytes ({savings_percent:.1f}%)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Single image optimization error: {str(e)}")
            return None
    
    def cleanup_memory(self) -> Dict[str, Any]:
        """Memory cleanup"""
        try:
            # Get memory usage before cleanup
            memory_before = psutil.virtual_memory().percent
            
            # Force garbage collection
            collected = gc.collect()
            
            # Clear expired cache entries
            cache_cleared = self.cache.clear_expired()
            
            # Get memory usage after cleanup
            memory_after = psutil.virtual_memory().percent
            
            result = {
                'memory_before': memory_before,
                'memory_after': memory_after,
                'memory_freed': memory_before - memory_after,
                'gc_collected': collected,
                'cache_entries_cleared': cache_cleared,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Memory cleanup completed: {result}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Memory cleanup error: {str(e)}")
            return {'error': str(e)}
    
    def get_performance_report(self, days: int = 7) -> Dict[str, Any]:
        """Performans raporu"""
        try:
            report = {
                'period': f'Last {days} days',
                'generated_at': datetime.now().isoformat(),
                'system_performance': self.monitor_system_performance(),
                'optimization_results': self._get_optimization_history(days),
                'recommendations': self._generate_performance_recommendations(),
                'metrics': self._get_performance_metrics(days)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Performance report error: {str(e)}")
            return {'error': str(e)}
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Performans önerileri oluştur"""
        recommendations = []
        
        try:
            # System performance check
            system_perf = self.monitor_system_performance()
            
            if system_perf.get('cpu_usage', 0) > 70:
                recommendations.append("CPU usage is high. Consider optimizing slow queries or adding more processing power.")
            
            if system_perf.get('memory', {}).get('percent', 0) > 80:
                recommendations.append("Memory usage is high. Consider implementing memory caching or increasing RAM.")
            
            # Database recommendations
            slow_queries = self._detect_slow_queries()
            if slow_queries:
                recommendations.append(f"Found {len(slow_queries)} slow queries. Consider adding indexes or optimizing queries.")
            
            # Cache recommendations
            cache_stats = self.cache.get_stats()
            if cache_stats.get('hit_ratio', 1) < 0.8:
                recommendations.append("Cache hit ratio is low. Consider increasing cache duration or adding more cache layers.")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Performance recommendations error: {str(e)}")
            return ["Unable to generate recommendations due to error"]
    
    def _record_performance_metric(self, metric_name: str, value: float, unit: str, category: str):
        """Performans metriği kaydet"""
        try:
            metric = PerformanceMetric(
                metric_name=metric_name,
                value=value,
                unit=unit,
                timestamp=datetime.now(),
                category=category
            )
            
            # Cache'e kaydet
            cache_key = f"performance_metric_{metric_name}_{int(time.time())}"
            self.cache.set(cache_key, metric.__dict__, 86400)  # 24 hours
            
        except Exception as e:
            self.logger.error(f"Performance metric recording error: {str(e)}")
    
    def _is_static_file(self, endpoint: str) -> bool:
        """Static file kontrolü"""
        if not endpoint:
            return False
        
        static_extensions = ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.svg']
        return any(endpoint.endswith(ext) for ext in static_extensions)
    
    def _inline_critical_css(self, html: str) -> str:
        """Critical CSS'i inline yap"""
        # Bu fonksiyon critical CSS detection ve inlining yapacak
        # Şimdilik placeholder
        return html
    
    def _add_lazy_loading(self, html: str) -> str:
        """Lazy loading attribute'ları ekle"""
        import re
        
        # img taglarına loading="lazy" ekle
        html = re.sub(r'<img(?![^>]*loading=)', '<img loading="lazy"', html)
        
        return html
    
    def _add_preload_hints(self, html: str) -> str:
        """Preload hint'leri ekle"""
        # Critical resources için preload hints ekle
        # Şimdilik placeholder
        return html