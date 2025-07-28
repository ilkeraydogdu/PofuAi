"""
Advanced API Gateway Service
Tüm API isteklerini yönlendiren, güvenlik ve performans kontrolü yapan servis
"""
import time
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
from core.Services.base_service import BaseService
from core.Services.cache_service import CacheService
from core.Services.logger import LoggerService

class APIGatewayService(BaseService):
    """İleri seviye API Gateway servisi"""
    
    def __init__(self):
        super().__init__()
        self.cache = CacheService()
        self.logger = LoggerService.get_logger()
        self.rate_limits = {}
        self.circuit_breakers = {}
        self.api_versions = ['v1', 'v2', 'v3']
        self.services = {}
        
    def register_service(self, name: str, config: Dict[str, Any]):
        """Microservice kaydet"""
        self.services[name] = {
            'name': name,
            'base_url': config.get('base_url'),
            'health_check': config.get('health_check', '/health'),
            'timeout': config.get('timeout', 30),
            'retry_count': config.get('retry_count', 3),
            'circuit_breaker': config.get('circuit_breaker', True),
            'rate_limit': config.get('rate_limit', 1000),  # per hour
            'auth_required': config.get('auth_required', True),
            'version': config.get('version', 'v1')
        }
        
    def route_request(self, request_path: str, method: str, headers: Dict, 
                     body: Any = None, query_params: Dict = None) -> Dict[str, Any]:
        """API isteğini yönlendir"""
        try:
            # 1. Request parsing
            parsed = self._parse_request(request_path, method, headers, body, query_params)
            
            # 2. Authentication & Authorization
            auth_result = self._authenticate_request(parsed)
            if not auth_result['success']:
                return self._error_response(401, 'Unauthorized', auth_result['message'])
            
            # 3. Rate limiting
            rate_check = self._check_rate_limit(parsed)
            if not rate_check['allowed']:
                return self._error_response(429, 'Too Many Requests', rate_check['message'])
            
            # 4. Service discovery
            service = self._discover_service(parsed['service_name'])
            if not service:
                return self._error_response(404, 'Service Not Found')
            
            # 5. Circuit breaker check
            if not self._check_circuit_breaker(service['name']):
                return self._error_response(503, 'Service Unavailable')
            
            # 6. Request transformation
            transformed_request = self._transform_request(parsed, service)
            
            # 7. Forward request to service
            response = self._forward_request(service, transformed_request)
            
            # 8. Response transformation
            final_response = self._transform_response(response, parsed)
            
            # 9. Caching
            self._cache_response(parsed, final_response)
            
            # 10. Metrics & Logging
            self._record_metrics(parsed, response, service)
            
            return final_response
            
        except Exception as e:
            self.logger.error(f"API Gateway error: {str(e)}")
            return self._error_response(500, 'Internal Server Error')
    
    def _parse_request(self, path: str, method: str, headers: Dict, 
                      body: Any, query_params: Dict) -> Dict[str, Any]:
        """İsteği parse et"""
        # Path analysis: /api/v2/users/123 -> service: users, version: v2, resource: 123
        path_parts = path.strip('/').split('/')
        
        if len(path_parts) < 3 or path_parts[0] != 'api':
            raise ValueError("Invalid API path format")
        
        version = path_parts[1] if path_parts[1] in self.api_versions else 'v1'
        service_name = path_parts[2]
        resource_path = '/'.join(path_parts[3:]) if len(path_parts) > 3 else ''
        
        return {
            'original_path': path,
            'method': method.upper(),
            'version': version,
            'service_name': service_name,
            'resource_path': resource_path,
            'headers': headers,
            'body': body,
            'query_params': query_params or {},
            'timestamp': datetime.now(),
            'request_id': self._generate_request_id()
        }
    
    def _authenticate_request(self, parsed_request: Dict) -> Dict[str, Any]:
        """İstek authentication"""
        service_name = parsed_request['service_name']
        service = self.services.get(service_name)
        
        if not service or not service.get('auth_required'):
            return {'success': True}
        
        # JWT token kontrolü
        auth_header = parsed_request['headers'].get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return {'success': False, 'message': 'Missing or invalid authorization header'}
        
        token = auth_header[7:]  # Remove 'Bearer '
        
        # Token validation (JWT decode)
        try:
            import jwt
            secret = self.get_config('app.jwt_secret', 'your-secret-key')
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            
            # Token blacklist kontrolü
            if self.cache.get(f'blacklist_{token}'):
                return {'success': False, 'message': 'Token is blacklisted'}
            
            parsed_request['user'] = payload
            return {'success': True}
            
        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'success': False, 'message': 'Invalid token'}
    
    def _check_rate_limit(self, parsed_request: Dict) -> Dict[str, Any]:
        """Rate limiting kontrolü"""
        service_name = parsed_request['service_name']
        user_id = parsed_request.get('user', {}).get('user_id', 'anonymous')
        
        # Rate limit key
        rate_key = f"rate_limit:{service_name}:{user_id}"
        current_time = datetime.now()
        window_start = current_time.replace(minute=0, second=0, microsecond=0)
        
        # Get current count
        current_count = self.cache.get(f"{rate_key}:{window_start.hour}") or 0
        
        # Service rate limit
        service = self.services.get(service_name, {})
        limit = service.get('rate_limit', 1000)
        
        if current_count >= limit:
            return {
                'allowed': False,
                'message': f'Rate limit exceeded. Limit: {limit} requests per hour'
            }
        
        # Increment counter
        self.cache.set(f"{rate_key}:{window_start.hour}", current_count + 1, 3600)
        
        return {
            'allowed': True,
            'remaining': limit - current_count - 1,
            'reset_time': window_start + timedelta(hours=1)
        }
    
    def _discover_service(self, service_name: str) -> Optional[Dict]:
        """Service discovery"""
        service = self.services.get(service_name)
        if not service:
            return None
        
        # Health check
        if not self._health_check(service):
            return None
        
        return service
    
    def _health_check(self, service: Dict) -> bool:
        """Service health check"""
        try:
            import requests
            health_url = f"{service['base_url']}{service['health_check']}"
            response = requests.get(health_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _check_circuit_breaker(self, service_name: str) -> bool:
        """Circuit breaker kontrolü"""
        circuit_key = f"circuit_breaker:{service_name}"
        circuit_state = self.cache.get(circuit_key)
        
        if not circuit_state:
            return True  # Circuit closed (healthy)
        
        if circuit_state['state'] == 'open':
            # Check if we should try again
            if datetime.now() > circuit_state['next_attempt']:
                # Half-open state
                self.cache.set(circuit_key, {
                    'state': 'half_open',
                    'failures': circuit_state['failures'],
                    'next_attempt': circuit_state['next_attempt']
                }, 300)
                return True
            return False
        
        return True  # Closed or half-open
    
    def _transform_request(self, parsed_request: Dict, service: Dict) -> Dict:
        """İsteği service formatına dönüştür"""
        return {
            'method': parsed_request['method'],
            'path': f"/{parsed_request['resource_path']}",
            'headers': {
                **parsed_request['headers'],
                'X-Request-ID': parsed_request['request_id'],
                'X-Service-Version': service['version'],
                'X-Gateway-Timestamp': parsed_request['timestamp'].isoformat()
            },
            'body': parsed_request['body'],
            'query_params': parsed_request['query_params']
        }
    
    def _forward_request(self, service: Dict, request: Dict) -> Dict:
        """İsteği service'e yönlendir"""
        try:
            import requests
            
            url = f"{service['base_url']}{request['path']}"
            
            response = requests.request(
                method=request['method'],
                url=url,
                headers=request['headers'],
                json=request['body'] if request['method'] in ['POST', 'PUT', 'PATCH'] else None,
                params=request['query_params'],
                timeout=service['timeout']
            )
            
            # Circuit breaker success
            self._record_circuit_breaker_success(service['name'])
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'response_time': response.elapsed.total_seconds()
            }
            
        except Exception as e:
            # Circuit breaker failure
            self._record_circuit_breaker_failure(service['name'])
            raise e
    
    def _record_circuit_breaker_success(self, service_name: str):
        """Circuit breaker başarı kaydı"""
        circuit_key = f"circuit_breaker:{service_name}"
        self.cache.delete(circuit_key)  # Reset circuit breaker
    
    def _record_circuit_breaker_failure(self, service_name: str):
        """Circuit breaker hata kaydı"""
        circuit_key = f"circuit_breaker:{service_name}"
        circuit_state = self.cache.get(circuit_key) or {'failures': 0, 'state': 'closed'}
        
        circuit_state['failures'] += 1
        
        # Open circuit after 5 failures
        if circuit_state['failures'] >= 5:
            circuit_state['state'] = 'open'
            circuit_state['next_attempt'] = datetime.now() + timedelta(minutes=5)
        
        self.cache.set(circuit_key, circuit_state, 3600)
    
    def _transform_response(self, response: Dict, parsed_request: Dict) -> Dict:
        """Response'u standardize et"""
        return {
            'status_code': response['status_code'],
            'data': response['body'],
            'meta': {
                'request_id': parsed_request['request_id'],
                'version': parsed_request['version'],
                'service': parsed_request['service_name'],
                'response_time': response.get('response_time', 0),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _cache_response(self, parsed_request: Dict, response: Dict):
        """Response'u cache'le"""
        if parsed_request['method'] == 'GET' and response['status_code'] == 200:
            cache_key = f"api_cache:{parsed_request['service_name']}:{parsed_request['resource_path']}"
            # Cache for 5 minutes
            self.cache.set(cache_key, response, 300)
    
    def _record_metrics(self, parsed_request: Dict, response: Dict, service: Dict):
        """Metrikleri kaydet"""
        metrics = {
            'timestamp': parsed_request['timestamp'].isoformat(),
            'request_id': parsed_request['request_id'],
            'service': parsed_request['service_name'],
            'method': parsed_request['method'],
            'path': parsed_request['resource_path'],
            'status_code': response['status_code'],
            'response_time': response.get('response_time', 0),
            'user_id': parsed_request.get('user', {}).get('user_id'),
            'version': parsed_request['version']
        }
        
        # Log to metrics service
        self.logger.info(f"API Gateway Metrics: {json.dumps(metrics)}")
        
        # Store in cache for analytics
        metrics_key = f"api_metrics:{datetime.now().strftime('%Y-%m-%d-%H')}"
        current_metrics = self.cache.get(metrics_key) or []
        current_metrics.append(metrics)
        self.cache.set(metrics_key, current_metrics, 7200)  # 2 hours
    
    def _generate_request_id(self) -> str:
        """Unique request ID oluştur"""
        import uuid
        return str(uuid.uuid4())
    
    def _error_response(self, status_code: int, error: str, message: str = None) -> Dict:
        """Hata response'u"""
        return {
            'status_code': status_code,
            'data': {
                'error': error,
                'message': message or error,
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def get_service_metrics(self, service_name: str = None, hours: int = 24) -> Dict:
        """Service metrikleri getir"""
        metrics = []
        
        for i in range(hours):
            hour_key = f"api_metrics:{(datetime.now() - timedelta(hours=i)).strftime('%Y-%m-%d-%H')}"
            hour_metrics = self.cache.get(hour_key) or []
            
            if service_name:
                hour_metrics = [m for m in hour_metrics if m['service'] == service_name]
            
            metrics.extend(hour_metrics)
        
        # Aggregate metrics
        total_requests = len(metrics)
        avg_response_time = sum(m['response_time'] for m in metrics) / total_requests if total_requests > 0 else 0
        error_rate = len([m for m in metrics if m['status_code'] >= 400]) / total_requests if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'avg_response_time': avg_response_time,
            'error_rate': error_rate,
            'top_endpoints': self._get_top_endpoints(metrics),
            'status_codes': self._get_status_code_distribution(metrics)
        }
    
    def _get_top_endpoints(self, metrics: List[Dict]) -> List[Dict]:
        """En çok kullanılan endpoint'ler"""
        endpoint_counts = {}
        for metric in metrics:
            endpoint = f"{metric['method']} {metric['path']}"
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
        
        return sorted([
            {'endpoint': endpoint, 'count': count}
            for endpoint, count in endpoint_counts.items()
        ], key=lambda x: x['count'], reverse=True)[:10]
    
    def _get_status_code_distribution(self, metrics: List[Dict]) -> Dict[str, int]:
        """Status code dağılımı"""
        status_counts = {}
        for metric in metrics:
            status = str(metric['status_code'])
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts

# Global API Gateway instance
_api_gateway = None

def get_api_gateway() -> APIGatewayService:
    """Global API Gateway instance'ını al"""
    global _api_gateway
    if _api_gateway is None:
        _api_gateway = APIGatewayService()
    return _api_gateway