"""
Advanced API Routes
İleri seviye API endpoint'leri için routing
"""
from flask import Blueprint

def register_advanced_api_routes(app):
    """
    İleri seviye API route'larını kaydet
    
    Args:
        app (Flask): Flask uygulaması
    """
    
    # Advanced API Controller
    from app.Controllers.Api.AdvancedApiController import AdvancedApiController
    advanced_api_controller = AdvancedApiController()
    
    # Advanced API Blueprint
    advanced_api_blueprint = Blueprint('advanced_api', __name__, url_prefix='/api/v2')
    
    # CQRS Endpoints
    advanced_api_blueprint.add_url_rule(
        '/cqrs/command', 
        'execute_command', 
        advanced_api_controller.execute_command, 
        methods=['POST']
    )
    
    advanced_api_blueprint.add_url_rule(
        '/cqrs/query', 
        'execute_query', 
        advanced_api_controller.execute_query, 
        methods=['POST']
    )
    
    # Microservices Orchestration
    advanced_api_blueprint.add_url_rule(
        '/orchestration/workflow', 
        'orchestrate_workflow', 
        advanced_api_controller.orchestrate_workflow, 
        methods=['POST']
    )
    
    advanced_api_blueprint.add_url_rule(
        '/orchestration/saga', 
        'start_saga', 
        advanced_api_controller.start_saga, 
        methods=['POST']
    )
    
    # WebSocket API Endpoints
    advanced_api_blueprint.add_url_rule(
        '/websocket/connect', 
        'websocket_connect', 
        advanced_api_controller.websocket_connect, 
        methods=['POST']
    )
    
    advanced_api_blueprint.add_url_rule(
        '/websocket/subscribe', 
        'websocket_subscribe', 
        advanced_api_controller.websocket_subscribe, 
        methods=['POST']
    )
    
    advanced_api_blueprint.add_url_rule(
        '/websocket/send', 
        'websocket_send_message', 
        advanced_api_controller.websocket_send_message, 
        methods=['POST']
    )
    
    advanced_api_blueprint.add_url_rule(
        '/websocket/broadcast', 
        'websocket_broadcast', 
        advanced_api_controller.websocket_broadcast, 
        methods=['POST']
    )
    
    # Real-time Notifications
    advanced_api_blueprint.add_url_rule(
        '/notifications/send', 
        'send_notification', 
        advanced_api_controller.send_notification, 
        methods=['POST']
    )
    
    # API Analytics & Monitoring
    advanced_api_blueprint.add_url_rule(
        '/metrics', 
        'get_api_metrics', 
        advanced_api_controller.get_api_metrics, 
        methods=['GET']
    )
    
    advanced_api_blueprint.add_url_rule(
        '/events', 
        'get_event_store', 
        advanced_api_controller.get_event_store, 
        methods=['GET']
    )
    
    # API Versioning
    advanced_api_blueprint.add_url_rule(
        '/versioning/register', 
        'register_api_version', 
        advanced_api_controller.register_api_version, 
        methods=['POST']
    )
    
    advanced_api_blueprint.add_url_rule(
        '/versioning/compatibility', 
        'check_api_compatibility', 
        advanced_api_controller.check_api_compatibility, 
        methods=['GET']
    )
    
    # GraphQL Endpoint
    from core.Services.graphql_service import GraphQLService
    graphql_service = GraphQLService()
    
    def graphql_endpoint():
        """GraphQL endpoint"""
        from flask import request, jsonify
        
        try:
            if request.method == 'POST':
                data = request.get_json()
                query = data.get('query')
                variables = data.get('variables', {})
                
                result = graphql_service.execute_query(query, variables)
                return jsonify(result)
            else:
                # GraphQL Playground for GET requests
                return """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>GraphQL Playground</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; }
                        .container { max-width: 800px; margin: 0 auto; }
                        textarea { width: 100%; height: 200px; margin: 10px 0; }
                        button { padding: 10px 20px; background: #007cba; color: white; border: none; cursor: pointer; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>GraphQL Playground</h1>
                        <p>Test your GraphQL queries here:</p>
                        
                        <h3>Query:</h3>
                        <textarea id="query" placeholder="Enter your GraphQL query here...">
query {
  users {
    id
    name
    email
  }
}
                        </textarea>
                        
                        <h3>Variables (JSON):</h3>
                        <textarea id="variables" placeholder="Enter variables as JSON...">{}</textarea>
                        
                        <button onclick="executeQuery()">Execute Query</button>
                        
                        <h3>Result:</h3>
                        <pre id="result"></pre>
                    </div>
                    
                    <script>
                        function executeQuery() {
                            const query = document.getElementById('query').value;
                            const variables = JSON.parse(document.getElementById('variables').value || '{}');
                            
                            fetch('/api/v2/graphql', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({ query, variables })
                            })
                            .then(response => response.json())
                            .then(data => {
                                document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                            })
                            .catch(error => {
                                document.getElementById('result').textContent = 'Error: ' + error.message;
                            });
                        }
                    </script>
                </body>
                </html>
                """
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    advanced_api_blueprint.add_url_rule(
        '/graphql', 
        'graphql', 
        graphql_endpoint, 
        methods=['GET', 'POST']
    )
    
    # API Gateway Endpoint
    from core.Services.api_gateway_service import APIGatewayService
    api_gateway = APIGatewayService()
    
    def gateway_endpoint(path):
        """API Gateway endpoint"""
        from flask import request, jsonify
        
        try:
            # Route request through gateway
            result = api_gateway.route_request(
                request_path=f"/{path}",
                method=request.method,
                headers=dict(request.headers),
                body=request.get_json() if request.is_json else None,
                query_params=dict(request.args)
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    advanced_api_blueprint.add_url_rule(
        '/gateway/<path:path>', 
        'gateway', 
        gateway_endpoint, 
        methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    )
    
    # API Documentation Endpoint
    def api_documentation():
        """API dokümantasyonu"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>PofuAi Advanced API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                .container { max-width: 1200px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { display: inline-block; padding: 3px 8px; border-radius: 3px; color: white; font-weight: bold; }
                .post { background: #28a745; }
                .get { background: #007bff; }
                .put { background: #ffc107; color: black; }
                .delete { background: #dc3545; }
                pre { background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }
                .section { margin: 30px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 PofuAi Advanced API Documentation</h1>
                <p>Bu dokümantasyon, PofuAi projesinin ileri seviye API endpoint'lerini açıklar.</p>
                
                <div class="section">
                    <h2>🏗️ CQRS (Command Query Responsibility Segregation)</h2>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/api/v2/cqrs/command</strong>
                        <p>Command çalıştır (Write operations)</p>
                        <pre>{
  "type": "create_user",
  "aggregate_id": "user-123",
  "payload": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}</pre>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/api/v2/cqrs/query</strong>
                        <p>Query çalıştır (Read operations)</p>
                        <pre>{
  "type": "get_users",
  "filters": {
    "role": "admin"
  },
  "pagination": {
    "page": 1,
    "limit": 10
  },
  "projections": ["id", "name", "email"]
}</pre>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🔗 Microservices Orchestration</h2>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/api/v2/orchestration/workflow</strong>
                        <p>Microservices workflow orchestrate et</p>
                        <pre>{
  "workflow_id": "user-registration-flow",
  "steps": [
    {
      "id": "validate-email",
      "service": "validation-service",
      "action": "validate_email",
      "payload": {"email": "user@example.com"}
    },
    {
      "id": "create-user",
      "service": "user-service", 
      "action": "create_user",
      "payload": {"name": "John", "email": "user@example.com"}
    }
  ]
}</pre>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/api/v2/orchestration/saga</strong>
                        <p>Saga pattern başlat</p>
                        <pre>{
  "saga_type": "user_registration_saga",
  "initial_data": {
    "user_id": "123",
    "email": "user@example.com"
  }
}</pre>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🔌 WebSocket API</h2>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/api/v2/websocket/connect</strong>
                        <p>WebSocket bağlantısı başlat</p>
                        <pre>{
  "connection_id": "conn-123"
}</pre>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/api/v2/websocket/subscribe</strong>
                        <p>Channel'a abone ol</p>
                        <pre>{
  "connection_id": "conn-123",
  "channel": "public:notifications"
}</pre>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/api/v2/websocket/send</strong>
                        <p>WebSocket mesaj gönder</p>
                        <pre>{
  "channel": "public:chat",
  "message": {
    "text": "Hello World!",
    "type": "chat"
  }
}</pre>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📊 GraphQL API</h2>
                    
                    <div class="endpoint">
                        <span class="method get">GET</span> <strong>/api/v2/graphql</strong>
                        <p>GraphQL Playground</p>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/api/v2/graphql</strong>
                        <p>GraphQL Query çalıştır</p>
                        <pre>{
  "query": "query { users { id name email } }",
  "variables": {}
}</pre>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📈 Monitoring & Analytics</h2>
                    
                    <div class="endpoint">
                        <span class="method get">GET</span> <strong>/api/v2/metrics</strong>
                        <p>API metrikleri al</p>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method get">GET</span> <strong>/api/v2/events</strong>
                        <p>Event store verilerini al</p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🌐 API Gateway</h2>
                    
                    <div class="endpoint">
                        <span class="method get post put delete">ALL</span> <strong>/api/v2/gateway/*</strong>
                        <p>API Gateway üzerinden tüm istekleri yönlendir</p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🔔 Real-time Notifications</h2>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span> <strong>/api/v2/notifications/send</strong>
                        <p>Real-time bildirim gönder</p>
                        <pre>{
  "title": "New Message",
  "message": "You have a new message",
  "recipients": ["user-123", "user-456"],
  "channel": "notifications:general",
  "priority": "high"
}</pre>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 Authentication</h2>
                    <p>Tüm API endpoint'leri JWT token tabanlı authentication gerektirir.</p>
                    <p>Header'da <code>Authorization: Bearer YOUR_JWT_TOKEN</code> göndermeniz gerekir.</p>
                </div>
                
                <div class="section">
                    <h2>🛠️ Error Handling</h2>
                    <p>Tüm hatalar standart JSON formatında döner:</p>
                    <pre>{
  "success": false,
  "error": "Error message",
  "code": 400,
  "timestamp": "2025-01-28T12:00:00Z"
}</pre>
                </div>
            </div>
        </body>
        </html>
        """
    
    advanced_api_blueprint.add_url_rule(
        '/docs', 
        'api_documentation', 
        api_documentation, 
        methods=['GET']
    )
    
    # Register blueprint
    app.register_blueprint(advanced_api_blueprint)
    
    return advanced_api_blueprint