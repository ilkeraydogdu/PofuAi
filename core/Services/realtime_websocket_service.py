"""
Real-time WebSocket API Service
WebSocket bağlantıları, pub/sub messaging, real-time bildirimler
"""
import json
import asyncio
import uuid
import weakref
from typing import Dict, Any, List, Optional, Set, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from core.Services.base_service import BaseService
from core.Services.cache_service import CacheService
from core.Services.logger import LoggerService

class MessageType(Enum):
    """WebSocket mesaj tipleri"""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    MESSAGE = "message"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"
    ERROR = "error"

class ConnectionStatus(Enum):
    """Bağlantı durumları"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"

@dataclass
class WebSocketMessage:
    """WebSocket mesaj modeli"""
    id: str
    type: MessageType
    channel: Optional[str]
    data: Dict[str, Any]
    sender_id: Optional[str]
    timestamp: datetime
    correlation_id: Optional[str] = None

@dataclass
class Connection:
    """WebSocket bağlantı modeli"""
    id: str
    user_id: Optional[str]
    session_id: str
    status: ConnectionStatus
    channels: Set[str]
    metadata: Dict[str, Any]
    connected_at: datetime
    last_heartbeat: datetime
    ip_address: str
    user_agent: str

class RealtimeWebSocketService(BaseService):
    """Real-time WebSocket API servisi"""
    
    def __init__(self):
        super().__init__()
        self.cache = CacheService()
        self.logger = LoggerService.get_logger()
        
        # Connection management
        self.connections: Dict[str, Connection] = {}
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        self.channel_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        
        # Message handling
        self.message_handlers: Dict[MessageType, List[Callable]] = defaultdict(list)
        self.channel_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = defaultdict(list)
        self.max_messages_per_minute = 60
        
        # Background tasks
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.cleanup_task = None
        
        # Metrics
        self.metrics = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'channels_active': 0
        }
        
        self._start_background_tasks()
    
    # Connection Management
    async def connect(self, connection_id: str, user_id: Optional[str] = None,
                     session_id: str = None, metadata: Dict[str, Any] = None) -> Connection:
        """WebSocket bağlantısı oluştur"""
        try:
            connection = Connection(
                id=connection_id,
                user_id=user_id,
                session_id=session_id or str(uuid.uuid4()),
                status=ConnectionStatus.CONNECTING,
                channels=set(),
                metadata=metadata or {},
                connected_at=datetime.now(),
                last_heartbeat=datetime.now(),
                ip_address=metadata.get('ip_address', 'unknown'),
                user_agent=metadata.get('user_agent', 'unknown')
            )
            
            self.connections[connection_id] = connection
            
            if user_id:
                self.user_connections[user_id].add(connection_id)
            
            connection.status = ConnectionStatus.CONNECTED
            self.metrics['total_connections'] += 1
            self.metrics['active_connections'] += 1
            
            # Log connection
            self.logger.info(f"WebSocket connected: {connection_id} (User: {user_id})")
            
            # Send welcome message
            await self._send_to_connection(connection_id, WebSocketMessage(
                id=str(uuid.uuid4()),
                type=MessageType.CONNECT,
                channel=None,
                data={'status': 'connected', 'connection_id': connection_id},
                sender_id='system',
                timestamp=datetime.now()
            ))
            
            return connection
            
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            raise
    
    async def disconnect(self, connection_id: str, reason: str = "normal"):
        """WebSocket bağlantısını kapat"""
        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return
            
            connection.status = ConnectionStatus.DISCONNECTING
            
            # Unsubscribe from all channels
            for channel in list(connection.channels):
                await self.unsubscribe(connection_id, channel)
            
            # Remove from user connections
            if connection.user_id:
                self.user_connections[connection.user_id].discard(connection_id)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]
            
            # Remove connection
            del self.connections[connection_id]
            self.metrics['active_connections'] -= 1
            
            self.logger.info(f"WebSocket disconnected: {connection_id} (Reason: {reason})")
            
        except Exception as e:
            self.logger.error(f"Disconnect error: {str(e)}")
    
    # Channel Management
    async def subscribe(self, connection_id: str, channel: str) -> bool:
        """Channel'a abone ol"""
        try:
            connection = self.connections.get(connection_id)
            if not connection or connection.status != ConnectionStatus.CONNECTED:
                return False
            
            # Channel validation
            if not self._validate_channel(channel, connection):
                await self._send_error(connection_id, f"Access denied to channel: {channel}")
                return False
            
            # Add subscription
            connection.channels.add(channel)
            self.channel_subscriptions[channel].add(connection_id)
            
            # Update metrics
            self.metrics['channels_active'] = len(self.channel_subscriptions)
            
            # Send confirmation
            await self._send_to_connection(connection_id, WebSocketMessage(
                id=str(uuid.uuid4()),
                type=MessageType.SUBSCRIBE,
                channel=channel,
                data={'status': 'subscribed', 'channel': channel},
                sender_id='system',
                timestamp=datetime.now()
            ))
            
            self.logger.info(f"Subscribed to channel: {connection_id} -> {channel}")
            return True
            
        except Exception as e:
            self.logger.error(f"Subscribe error: {str(e)}")
            return False
    
    async def unsubscribe(self, connection_id: str, channel: str) -> bool:
        """Channel'dan çık"""
        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return False
            
            # Remove subscription
            connection.channels.discard(channel)
            self.channel_subscriptions[channel].discard(connection_id)
            
            # Clean empty channels
            if not self.channel_subscriptions[channel]:
                del self.channel_subscriptions[channel]
            
            # Update metrics
            self.metrics['channels_active'] = len(self.channel_subscriptions)
            
            # Send confirmation
            await self._send_to_connection(connection_id, WebSocketMessage(
                id=str(uuid.uuid4()),
                type=MessageType.UNSUBSCRIBE,
                channel=channel,
                data={'status': 'unsubscribed', 'channel': channel},
                sender_id='system',
                timestamp=datetime.now()
            ))
            
            self.logger.info(f"Unsubscribed from channel: {connection_id} -> {channel}")
            return True
            
        except Exception as e:
            self.logger.error(f"Unsubscribe error: {str(e)}")
            return False
    
    # Message Handling
    async def send_message(self, channel: str, data: Dict[str, Any], 
                          sender_id: str = None) -> int:
        """Channel'a mesaj gönder"""
        try:
            message = WebSocketMessage(
                id=str(uuid.uuid4()),
                type=MessageType.MESSAGE,
                channel=channel,
                data=data,
                sender_id=sender_id,
                timestamp=datetime.now()
            )
            
            # Get subscribers
            subscribers = self.channel_subscriptions.get(channel, set())
            sent_count = 0
            
            # Send to all subscribers
            for connection_id in subscribers:
                if await self._send_to_connection(connection_id, message):
                    sent_count += 1
            
            self.metrics['messages_sent'] += sent_count
            
            # Execute channel handlers
            await self._execute_channel_handlers(channel, message)
            
            return sent_count
            
        except Exception as e:
            self.logger.error(f"Send message error: {str(e)}")
            return 0
    
    async def send_to_user(self, user_id: str, data: Dict[str, Any], 
                          message_type: MessageType = MessageType.NOTIFICATION) -> int:
        """Kullanıcıya mesaj gönder"""
        try:
            message = WebSocketMessage(
                id=str(uuid.uuid4()),
                type=message_type,
                channel=None,
                data=data,
                sender_id='system',
                timestamp=datetime.now()
            )
            
            # Get user connections
            user_connection_ids = self.user_connections.get(user_id, set())
            sent_count = 0
            
            # Send to all user connections
            for connection_id in user_connection_ids:
                if await self._send_to_connection(connection_id, message):
                    sent_count += 1
            
            self.metrics['messages_sent'] += sent_count
            return sent_count
            
        except Exception as e:
            self.logger.error(f"Send to user error: {str(e)}")
            return 0
    
    async def broadcast(self, data: Dict[str, Any], exclude_connections: Set[str] = None) -> int:
        """Tüm bağlantılara broadcast yap"""
        try:
            message = WebSocketMessage(
                id=str(uuid.uuid4()),
                type=MessageType.BROADCAST,
                channel=None,
                data=data,
                sender_id='system',
                timestamp=datetime.now()
            )
            
            exclude_connections = exclude_connections or set()
            sent_count = 0
            
            # Send to all connections
            for connection_id in self.connections:
                if connection_id not in exclude_connections:
                    if await self._send_to_connection(connection_id, message):
                        sent_count += 1
            
            self.metrics['messages_sent'] += sent_count
            return sent_count
            
        except Exception as e:
            self.logger.error(f"Broadcast error: {str(e)}")
            return 0
    
    # Message Handlers
    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """Mesaj handler kaydet"""
        self.message_handlers[message_type].append(handler)
    
    def register_channel_handler(self, channel: str, handler: Callable):
        """Channel handler kaydet"""
        self.channel_handlers[channel].append(handler)
    
    async def handle_incoming_message(self, connection_id: str, raw_message: str):
        """Gelen mesajı işle"""
        try:
            connection = self.connections.get(connection_id)
            if not connection or connection.status != ConnectionStatus.CONNECTED:
                return
            
            # Rate limiting check
            if not self._check_rate_limit(connection_id):
                await self._send_error(connection_id, "Rate limit exceeded")
                return
            
            # Parse message
            try:
                message_data = json.loads(raw_message)
            except json.JSONDecodeError:
                await self._send_error(connection_id, "Invalid JSON format")
                return
            
            # Create message object
            message = WebSocketMessage(
                id=message_data.get('id', str(uuid.uuid4())),
                type=MessageType(message_data.get('type', 'message')),
                channel=message_data.get('channel'),
                data=message_data.get('data', {}),
                sender_id=connection.user_id,
                timestamp=datetime.now(),
                correlation_id=message_data.get('correlation_id')
            )
            
            self.metrics['messages_received'] += 1
            
            # Update heartbeat
            connection.last_heartbeat = datetime.now()
            
            # Execute message handlers
            await self._execute_message_handlers(message, connection)
            
        except Exception as e:
            self.logger.error(f"Handle incoming message error: {str(e)}")
            await self._send_error(connection_id, "Message processing failed")
    
    # Real-time Features
    async def send_real_time_notification(self, notification_data: Dict[str, Any]):
        """Real-time bildirim gönder"""
        try:
            # Determine recipients
            recipients = notification_data.get('recipients', [])
            channel = notification_data.get('channel')
            
            notification = {
                'id': str(uuid.uuid4()),
                'type': 'notification',
                'title': notification_data.get('title'),
                'message': notification_data.get('message'),
                'data': notification_data.get('data', {}),
                'timestamp': datetime.now().isoformat(),
                'priority': notification_data.get('priority', 'normal')
            }
            
            sent_count = 0
            
            # Send to specific users
            if recipients:
                for user_id in recipients:
                    sent_count += await self.send_to_user(user_id, notification)
            
            # Send to channel
            if channel:
                sent_count += await self.send_message(channel, notification, 'system')
            
            return sent_count
            
        except Exception as e:
            self.logger.error(f"Real-time notification error: {str(e)}")
            return 0
    
    async def send_live_update(self, entity_type: str, entity_id: str, 
                              action: str, data: Dict[str, Any]):
        """Canlı güncelleme gönder"""
        try:
            update_data = {
                'type': 'live_update',
                'entity_type': entity_type,
                'entity_id': entity_id,
                'action': action,  # create, update, delete
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send to relevant channels
            channels = [
                f"{entity_type}:all",
                f"{entity_type}:{entity_id}",
                f"updates:all"
            ]
            
            sent_count = 0
            for channel in channels:
                sent_count += await self.send_message(channel, update_data, 'system')
            
            return sent_count
            
        except Exception as e:
            self.logger.error(f"Live update error: {str(e)}")
            return 0
    
    # Helper Methods
    async def _send_to_connection(self, connection_id: str, message: WebSocketMessage) -> bool:
        """Bağlantıya mesaj gönder"""
        try:
            connection = self.connections.get(connection_id)
            if not connection or connection.status != ConnectionStatus.CONNECTED:
                return False
            
            # Convert message to JSON
            message_json = json.dumps({
                'id': message.id,
                'type': message.type.value,
                'channel': message.channel,
                'data': message.data,
                'sender_id': message.sender_id,
                'timestamp': message.timestamp.isoformat(),
                'correlation_id': message.correlation_id
            })
            
            # In real implementation, this would send via WebSocket
            # For now, we'll log it
            self.logger.debug(f"Sending to {connection_id}: {message_json}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Send to connection error: {str(e)}")
            return False
    
    async def _send_error(self, connection_id: str, error_message: str):
        """Hata mesajı gönder"""
        error_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type=MessageType.ERROR,
            channel=None,
            data={'error': error_message},
            sender_id='system',
            timestamp=datetime.now()
        )
        await self._send_to_connection(connection_id, error_msg)
    
    def _validate_channel(self, channel: str, connection: Connection) -> bool:
        """Channel erişim kontrolü"""
        # Public channels
        if channel.startswith('public:'):
            return True
        
        # User-specific channels
        if channel.startswith('user:'):
            user_id = channel.split(':', 1)[1]
            return connection.user_id == user_id
        
        # Admin channels
        if channel.startswith('admin:'):
            return connection.metadata.get('is_admin', False)
        
        # Private channels - require specific permission
        if channel.startswith('private:'):
            return self._check_private_channel_access(channel, connection)
        
        return False
    
    def _check_private_channel_access(self, channel: str, connection: Connection) -> bool:
        """Private channel erişim kontrolü"""
        # Implementation for private channel access control
        return False
    
    def _check_rate_limit(self, connection_id: str) -> bool:
        """Rate limiting kontrolü"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old entries
        self.rate_limits[connection_id] = [
            timestamp for timestamp in self.rate_limits[connection_id]
            if timestamp > minute_ago
        ]
        
        # Check limit
        if len(self.rate_limits[connection_id]) >= self.max_messages_per_minute:
            return False
        
        # Add current request
        self.rate_limits[connection_id].append(now)
        return True
    
    async def _execute_message_handlers(self, message: WebSocketMessage, connection: Connection):
        """Mesaj handler'larını çalıştır"""
        handlers = self.message_handlers.get(message.type, [])
        
        for handler in handlers:
            try:
                await self._execute_async(handler, message, connection)
            except Exception as e:
                self.logger.error(f"Message handler error: {str(e)}")
    
    async def _execute_channel_handlers(self, channel: str, message: WebSocketMessage):
        """Channel handler'larını çalıştır"""
        handlers = self.channel_handlers.get(channel, [])
        
        for handler in handlers:
            try:
                await self._execute_async(handler, channel, message)
            except Exception as e:
                self.logger.error(f"Channel handler error: {str(e)}")
    
    async def _execute_async(self, func: Callable, *args) -> Any:
        """Async function execute et"""
        if asyncio.iscoroutinefunction(func):
            return await func(*args)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self.executor, func, *args)
    
    # Background Tasks
    def _start_background_tasks(self):
        """Background task'ları başlat"""
        # Background tasks will be started when needed in async context
        self.cleanup_task = None
    
    async def _cleanup_connections(self):
        """Ölü bağlantıları temizle"""
        while True:
            try:
                await asyncio.sleep(30)  # Her 30 saniyede bir kontrol et
                
                now = datetime.now()
                timeout = timedelta(minutes=5)  # 5 dakika timeout
                
                dead_connections = []
                
                for connection_id, connection in self.connections.items():
                    if now - connection.last_heartbeat > timeout:
                        dead_connections.append(connection_id)
                
                # Remove dead connections
                for connection_id in dead_connections:
                    await self.disconnect(connection_id, "timeout")
                
                if dead_connections:
                    self.logger.info(f"Cleaned up {len(dead_connections)} dead connections")
                
            except Exception as e:
                self.logger.error(f"Cleanup task error: {str(e)}")
    
    # Statistics & Monitoring
    def get_connection_stats(self) -> Dict[str, Any]:
        """Bağlantı istatistikleri"""
        return {
            'total_connections': self.metrics['total_connections'],
            'active_connections': self.metrics['active_connections'],
            'messages_sent': self.metrics['messages_sent'],
            'messages_received': self.metrics['messages_received'],
            'active_channels': self.metrics['channels_active'],
            'users_online': len(self.user_connections),
            'channels': list(self.channel_subscriptions.keys()),
            'connection_details': [
                {
                    'id': conn.id,
                    'user_id': conn.user_id,
                    'status': conn.status.value,
                    'channels': list(conn.channels),
                    'connected_at': conn.connected_at.isoformat(),
                    'last_heartbeat': conn.last_heartbeat.isoformat()
                }
                for conn in self.connections.values()
            ]
        }
    
    def get_channel_stats(self, channel: str) -> Dict[str, Any]:
        """Channel istatistikleri"""
        subscribers = self.channel_subscriptions.get(channel, set())
        
        return {
            'channel': channel,
            'subscriber_count': len(subscribers),
            'subscribers': list(subscribers),
            'active': len(subscribers) > 0
        }
    
    # Cleanup
    async def shutdown(self):
        """Servisi kapat"""
        try:
            # Cancel cleanup task
            if self.cleanup_task:
                self.cleanup_task.cancel()
            
            # Disconnect all connections
            for connection_id in list(self.connections.keys()):
                await self.disconnect(connection_id, "shutdown")
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            self.logger.info("WebSocket service shut down")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {str(e)}")