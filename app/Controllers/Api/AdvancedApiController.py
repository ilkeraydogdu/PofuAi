"""
Advanced API Controller
İleri seviye API endpoint'leri - CQRS, Event Sourcing, WebSocket, Microservices
"""
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from flask import request, jsonify
from app.Controllers.BaseController import BaseController
from core.Services.advanced_api_orchestrator import (
    AdvancedAPIOrchestrator, Command, Query, APIEvent, EventType
)
from core.Services.realtime_websocket_service import RealtimeWebSocketService
from core.Services.error_handler import error_handler

class AdvancedApiController(BaseController):
    """İleri seviye API controller"""
    
    def __init__(self):
        super().__init__()
        self.orchestrator = AdvancedAPIOrchestrator()
        self.websocket_service = RealtimeWebSocketService()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Handler'ları setup et"""
        # Command handlers
        self.orchestrator.register_command_handler('create_user', self._handle_create_user_command)
        self.orchestrator.register_command_handler('update_user', self._handle_update_user_command)
        self.orchestrator.register_command_handler('delete_user', self._handle_delete_user_command)
        
        # Query handlers
        self.orchestrator.register_query_handler('get_users', self._handle_get_users_query)
        self.orchestrator.register_query_handler('get_user_analytics', self._handle_user_analytics_query)
        
        # Event handlers
        self.orchestrator.register_event_handler('domain_event', self._handle_domain_event)
        
        # WebSocket handlers
        self.websocket_service.register_message_handler('message', self._handle_websocket_message)
    
    # CQRS Endpoints
    async def execute_command(self):
        """Command çalıştır (Write operations)"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
            
            # Get command data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'type': 'required|string',
                'aggregate_id': 'required|string',
                'payload': 'required|dict'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
            
            # Create command
            command = Command(
                id=str(uuid.uuid4()),
                type=data['type'],
                aggregate_id=data['aggregate_id'],
                payload=data['payload'],
                metadata={
                    'user_id': user.id,
                    'ip_address': self.get_client_ip(),
                    'user_agent': request.headers.get('User-Agent', ''),
                    'timestamp': datetime.now().isoformat()
                },
                timestamp=datetime.now(),
                expected_version=data.get('expected_version')
            )
            
            # Execute command
            result = await self.orchestrator.execute_command(command)
            
            # Send real-time update if successful
            if result['success']:
                await self._send_real_time_update(command.type, result)
            
            return self.json_response(result)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    async def execute_query(self):
        """Query çalıştır (Read operations)"""
        try:
            # Auth check (optional for some queries)
            user = self.get_current_user()
            
            # Get query data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'type': 'required|string',
                'filters': 'dict',
                'pagination': 'dict',
                'projections': 'array'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
            
            # Create query
            query = Query(
                id=str(uuid.uuid4()),
                type=data['type'],
                filters=data.get('filters', {}),
                pagination=data.get('pagination', {'page': 1, 'limit': 10}),
                projections=data.get('projections', []),
                timestamp=datetime.now()
            )
            
            # Add user context to filters if authenticated
            if user:
                query.filters['_user_id'] = user.id
                query.filters['_user_role'] = user.role
            
            # Execute query
            result = await self.orchestrator.execute_query(query)
            
            return self.json_response(result)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # Microservices Orchestration
    async def orchestrate_workflow(self):
        """Microservices workflow orchestrate et"""
        try:
            # Admin check
            user = self.require_role('admin')
            if isinstance(user, dict):
                return user
            
            # Get workflow data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'workflow_id': 'required|string',
                'steps': 'required|array'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
            
            # Execute workflow
            result = await self.orchestrator.orchestrate_microservices(
                data['workflow_id'],
                data['steps']
            )
            
            return self.json_response(result)
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    async def start_saga(self):
        """Saga pattern başlat"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
            
            # Get saga data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'saga_type': 'required|string',
                'initial_data': 'required|dict'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
            
            # Start saga
            saga_id = await self.orchestrator.start_saga(
                data['saga_type'],
                data['initial_data']
            )
            
            return self.json_response({
                'success': True,
                'saga_id': saga_id,
                'message': 'Saga started successfully'
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # WebSocket API Endpoints
    async def websocket_connect(self):
        """WebSocket bağlantısı başlat"""
        try:
            # Get connection data
            data = self.get_all_input()
            user = self.get_current_user()
            
            connection_id = data.get('connection_id', str(uuid.uuid4()))
            
            # Create connection
            connection = await self.websocket_service.connect(
                connection_id=connection_id,
                user_id=user.id if user else None,
                metadata={
                    'ip_address': self.get_client_ip(),
                    'user_agent': request.headers.get('User-Agent', ''),
                    'is_admin': user.is_admin if user else False
                }
            )
            
            return self.json_response({
                'success': True,
                'connection_id': connection.id,
                'status': connection.status.value
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    async def websocket_subscribe(self):
        """WebSocket channel'a abone ol"""
        try:
            # Get subscription data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'connection_id': 'required|string',
                'channel': 'required|string'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
            
            # Subscribe
            success = await self.websocket_service.subscribe(
                data['connection_id'],
                data['channel']
            )
            
            return self.json_response({
                'success': success,
                'message': 'Subscribed successfully' if success else 'Subscription failed'
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    async def websocket_send_message(self):
        """WebSocket mesaj gönder"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
            
            # Get message data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'channel': 'required|string',
                'message': 'required|dict'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
            
            # Send message
            sent_count = await self.websocket_service.send_message(
                data['channel'],
                data['message'],
                user.id
            )
            
            return self.json_response({
                'success': True,
                'sent_count': sent_count,
                'message': f'Message sent to {sent_count} connections'
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    async def websocket_broadcast(self):
        """WebSocket broadcast"""
        try:
            # Admin check
            user = self.require_role('admin')
            if isinstance(user, dict):
                return user
            
            # Get broadcast data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'message': 'required|dict'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
            
            # Broadcast
            sent_count = await self.websocket_service.broadcast(
                data['message'],
                set(data.get('exclude_connections', []))
            )
            
            return self.json_response({
                'success': True,
                'sent_count': sent_count,
                'message': f'Broadcast sent to {sent_count} connections'
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # Real-time Notifications
    async def send_notification(self):
        """Real-time bildirim gönder"""
        try:
            # Auth check
            user = self.require_auth()
            if isinstance(user, dict):
                return user
            
            # Get notification data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'title': 'required|string',
                'message': 'required|string',
                'recipients': 'array',
                'channel': 'string'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
            
            # Send notification
            sent_count = await self.websocket_service.send_real_time_notification({
                'title': data['title'],
                'message': data['message'],
                'data': data.get('data', {}),
                'recipients': data.get('recipients', []),
                'channel': data.get('channel'),
                'priority': data.get('priority', 'normal')
            })
            
            return self.json_response({
                'success': True,
                'sent_count': sent_count,
                'message': f'Notification sent to {sent_count} recipients'
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # API Analytics & Monitoring
    def get_api_metrics(self):
        """API metrikleri al"""
        try:
            # Admin check
            user = self.require_role('admin')
            if isinstance(user, dict):
                return user
            
            # Get orchestrator metrics
            orchestrator_metrics = self.orchestrator.get_performance_metrics()
            
            # Get WebSocket metrics
            websocket_metrics = self.websocket_service.get_connection_stats()
            
            return self.json_response({
                'success': True,
                'data': {
                    'orchestrator': orchestrator_metrics,
                    'websocket': websocket_metrics,
                    'timestamp': datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def get_event_store(self):
        """Event store verilerini al"""
        try:
            # Admin check
            user = self.require_role('admin')
            if isinstance(user, dict):
                return user
            
            # Get pagination parameters
            page = int(self.get_input('page', 1))
            limit = int(self.get_input('limit', 50))
            event_type = self.get_input('event_type')
            aggregate_id = self.get_input('aggregate_id')
            
            # Get events from store
            events = self.orchestrator.event_store
            
            # Filter events
            if event_type:
                events = [e for e in events if e.get('type') == event_type]
            
            if aggregate_id:
                events = [e for e in events if e.get('aggregate_id') == aggregate_id]
            
            # Pagination
            start = (page - 1) * limit
            end = start + limit
            paginated_events = events[start:end]
            
            return self.json_response({
                'success': True,
                'data': paginated_events,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': len(events),
                    'pages': (len(events) + limit - 1) // limit
                }
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # API Versioning
    def register_api_version(self):
        """API version kaydet"""
        try:
            # Admin check
            user = self.require_role('admin')
            if isinstance(user, dict):
                return user
            
            # Get version data
            data = self.get_all_input()
            
            # Validation
            rules = {
                'version': 'required|string',
                'schema': 'required|dict'
            }
            
            if not self.validator.validate(data, rules):
                return self.error_response('Validation failed', 422, self.validator.get_errors())
            
            # Register version
            self.orchestrator.register_api_version(data['version'], data['schema'])
            
            return self.json_response({
                'success': True,
                'message': f'API version {data["version"]} registered successfully'
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    def check_api_compatibility(self):
        """API version uyumluluğu kontrol et"""
        try:
            # Get version parameters
            from_version = self.get_input('from_version')
            to_version = self.get_input('to_version')
            
            if not from_version or not to_version:
                return self.error_response('from_version and to_version required', 400)
            
            # Check compatibility
            compatibility = self.orchestrator.validate_api_compatibility(from_version, to_version)
            
            return self.json_response({
                'success': True,
                'data': compatibility
            })
            
        except Exception as e:
            return error_handler.handle_error(e, self.request)
    
    # Command Handlers (CQRS)
    async def _handle_create_user_command(self, command: Command) -> List[APIEvent]:
        """Create user command handler"""
        from app.Models.User import User
        
        # Create user
        user_data = command.payload
        user = User.create_user(user_data)
        
        if not user:
            raise Exception("User creation failed")
        
        # Create domain event
        event = APIEvent(
            id=str(uuid.uuid4()),
            type=EventType.DOMAIN_EVENT,
            aggregate_id=command.aggregate_id,
            aggregate_type='User',
            event_data={
                'event_type': 'UserCreated',
                'user_id': user.id,
                'user_data': user.to_dict()
            },
            metadata=command.metadata,
            timestamp=datetime.now(),
            version=1,
            correlation_id=command.id
        )
        
        return [event]
    
    async def _handle_update_user_command(self, command: Command) -> List[APIEvent]:
        """Update user command handler"""
        from app.Models.User import User
        
        # Update user
        user = User.find(command.aggregate_id)
        if not user:
            raise Exception("User not found")
        
        old_data = user.to_dict()
        user.update(command.payload)
        
        # Create domain event
        event = APIEvent(
            id=str(uuid.uuid4()),
            type=EventType.DOMAIN_EVENT,
            aggregate_id=command.aggregate_id,
            aggregate_type='User',
            event_data={
                'event_type': 'UserUpdated',
                'user_id': user.id,
                'old_data': old_data,
                'new_data': user.to_dict(),
                'changes': command.payload
            },
            metadata=command.metadata,
            timestamp=datetime.now(),
            version=user.version + 1,
            correlation_id=command.id
        )
        
        return [event]
    
    async def _handle_delete_user_command(self, command: Command) -> List[APIEvent]:
        """Delete user command handler"""
        from app.Models.User import User
        
        # Delete user
        user = User.find(command.aggregate_id)
        if not user:
            raise Exception("User not found")
        
        user_data = user.to_dict()
        user.delete()
        
        # Create domain event
        event = APIEvent(
            id=str(uuid.uuid4()),
            type=EventType.DOMAIN_EVENT,
            aggregate_id=command.aggregate_id,
            aggregate_type='User',
            event_data={
                'event_type': 'UserDeleted',
                'user_id': user.id,
                'user_data': user_data
            },
            metadata=command.metadata,
            timestamp=datetime.now(),
            version=user.version + 1,
            correlation_id=command.id
        )
        
        return [event]
    
    # Query Handlers (CQRS)
    async def _handle_get_users_query(self, query: Query) -> Dict[str, Any]:
        """Get users query handler"""
        from app.Models.User import User
        
        # Build query
        user_query = User.query()
        
        # Apply filters
        filters = query.filters
        if 'name' in filters:
            user_query = user_query.where_like('name', f"%{filters['name']}%")
        
        if 'role' in filters:
            user_query = user_query.where({'role': filters['role']})
        
        if 'status' in filters:
            user_query = user_query.where({'status': filters['status']})
        
        # Apply pagination
        page = query.pagination.get('page', 1)
        limit = query.pagination.get('limit', 10)
        
        result = user_query.paginate(page, limit)
        
        # Apply projections
        if query.projections:
            data = []
            for user in result['data']:
                user_dict = user.to_dict()
                projected = {field: user_dict.get(field) for field in query.projections}
                data.append(projected)
            result['data'] = data
        else:
            result['data'] = [user.to_dict() for user in result['data']]
        
        return result
    
    async def _handle_user_analytics_query(self, query: Query) -> Dict[str, Any]:
        """User analytics query handler"""
        from app.Models.User import User
        
        # Get user analytics
        filters = query.filters
        user_id = filters.get('user_id')
        
        if user_id:
            user = User.find(user_id)
            if not user:
                raise Exception("User not found")
            
            # Get user-specific analytics
            analytics = {
                'user_id': user.id,
                'profile': user.to_dict(),
                'activity_stats': {
                    'login_count': user.login_count,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'created_at': user.created_at.isoformat()
                }
            }
        else:
            # Get general user analytics
            total_users = User.count()
            active_users = User.where({'status': 'active'}).count()
            
            analytics = {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'user_roles': User.get_role_distribution(),
                'recent_registrations': User.get_recent_registrations(30)
            }
        
        return analytics
    
    # Event Handlers
    async def _handle_domain_event(self, event: APIEvent):
        """Domain event handler"""
        # Send real-time update
        await self.websocket_service.send_live_update(
            event.aggregate_type.lower(),
            event.aggregate_id,
            event.event_data.get('event_type', 'updated'),
            event.event_data
        )
    
    # WebSocket Message Handler
    async def _handle_websocket_message(self, message, connection):
        """WebSocket mesaj handler"""
        # Process incoming WebSocket message
        self.logger.info(f"WebSocket message from {connection.id}: {message.data}")
        
        # Echo message back to sender
        await self.websocket_service.send_to_user(
            connection.user_id,
            {'type': 'echo', 'original': message.data}
        )
    
    # Helper Methods
    async def _send_real_time_update(self, command_type: str, result: Dict[str, Any]):
        """Real-time güncelleme gönder"""
        try:
            # Determine update type
            update_type = 'created' if 'create' in command_type else 'updated'
            
            # Send to relevant channels
            await self.websocket_service.send_live_update(
                'api_command',
                result.get('command_id', ''),
                update_type,
                {
                    'command_type': command_type,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Real-time update failed: {str(e)}")
    
    def get_current_user(self):
        """Mevcut kullanıcıyı al (optional)"""
        try:
            return self.require_auth()
        except:
            return None