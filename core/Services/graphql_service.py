"""
Advanced GraphQL Service
Modern, flexible API sorguları için GraphQL implementasyonu
"""
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from core.Services.base_service import BaseService
from core.Services.cache_service import CacheService

class GraphQLService(BaseService):
    """İleri seviye GraphQL servisi"""
    
    def __init__(self):
        super().__init__()
        self.cache = CacheService()
        self.schema = {}
        self.resolvers = {}
        self.middlewares = []
        self.subscriptions = {}
        
    def define_schema(self, schema_definition: str):
        """GraphQL schema tanımla"""
        self.schema = self._parse_schema(schema_definition)
    
    def add_resolver(self, type_name: str, field_name: str, resolver_func):
        """Resolver fonksiyonu ekle"""
        if type_name not in self.resolvers:
            self.resolvers[type_name] = {}
        self.resolvers[type_name][field_name] = resolver_func
    
    def add_middleware(self, middleware_func):
        """Middleware ekle"""
        self.middlewares.append(middleware_func)
    
    def execute_query(self, query: str, variables: Dict = None, 
                     context: Dict = None) -> Dict[str, Any]:
        """GraphQL sorgusu çalıştır"""
        try:
            # Parse query
            parsed_query = self._parse_query(query)
            
            # Apply middlewares
            for middleware in self.middlewares:
                result = middleware(parsed_query, variables, context)
                if result and 'error' in result:
                    return result
            
            # Execute query
            if parsed_query['operation_type'] == 'query':
                return self._execute_query(parsed_query, variables, context)
            elif parsed_query['operation_type'] == 'mutation':
                return self._execute_mutation(parsed_query, variables, context)
            elif parsed_query['operation_type'] == 'subscription':
                return self._execute_subscription(parsed_query, variables, context)
            else:
                return {'error': 'Unknown operation type'}
                
        except Exception as e:
            self.logger.error(f"GraphQL execution error: {str(e)}")
            return {
                'error': 'GraphQL execution failed',
                'message': str(e)
            }
    
    def _parse_schema(self, schema_definition: str) -> Dict:
        """Schema'yı parse et"""
        # Basit schema parser (gerçek uygulamada graphql-core kullanılabilir)
        schema = {
            'types': {},
            'queries': {},
            'mutations': {},
            'subscriptions': {}
        }
        
        lines = schema_definition.strip().split('\n')
        current_type = None
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if line.startswith('type '):
                current_type = line.split()[1].rstrip('{')
                schema['types'][current_type] = {'fields': {}}
                current_section = 'type'
            elif line.startswith('type Query'):
                current_section = 'queries'
            elif line.startswith('type Mutation'):
                current_section = 'mutations'
            elif line.startswith('type Subscription'):
                current_section = 'subscriptions'
            elif ':' in line and current_section:
                field_def = line.rstrip(',')
                field_name = field_def.split(':')[0].strip()
                field_type = field_def.split(':')[1].strip()
                
                if current_section == 'type' and current_type:
                    schema['types'][current_type]['fields'][field_name] = field_type
                else:
                    schema[current_section][field_name] = field_type
        
        return schema
    
    def _parse_query(self, query: str) -> Dict:
        """GraphQL sorgusunu parse et"""
        query = query.strip()
        
        # Operation type belirleme
        operation_type = 'query'  # default
        if query.startswith('mutation'):
            operation_type = 'mutation'
        elif query.startswith('subscription'):
            operation_type = 'subscription'
        
        # Basit field extraction
        fields = self._extract_fields(query)
        
        return {
            'operation_type': operation_type,
            'fields': fields,
            'raw_query': query
        }
    
    def _extract_fields(self, query: str) -> List[Dict]:
        """Query'den field'ları çıkar"""
        # Basit field extraction
        # Gerçek uygulamada daha sophisticated parser kullanılmalı
        fields = []
        
        # { } içindeki field'ları bul
        start = query.find('{')
        end = query.rfind('}')
        
        if start != -1 and end != -1:
            field_section = query[start+1:end].strip()
            field_lines = [line.strip() for line in field_section.split('\n') if line.strip()]
            
            for line in field_lines:
                if line and not line.startswith('#'):
                    field_name = line.split('(')[0].strip()  # Remove arguments for now
                    fields.append({
                        'name': field_name,
                        'arguments': {},  # TODO: Parse arguments
                        'sub_fields': []  # TODO: Parse nested fields
                    })
        
        return fields
    
    def _execute_query(self, parsed_query: Dict, variables: Dict, context: Dict) -> Dict:
        """Query'yi execute et"""
        data = {}
        errors = []
        
        for field in parsed_query['fields']:
            field_name = field['name']
            
            try:
                # Cache kontrolü
                cache_key = f"graphql_query:{field_name}:{hash(str(variables))}"
                cached_result = self.cache.get(cache_key)
                
                if cached_result:
                    data[field_name] = cached_result
                    continue
                
                # Resolver'ı bul ve çalıştır
                resolver = self._find_resolver('Query', field_name)
                if resolver:
                    result = resolver(field, variables, context)
                    data[field_name] = result
                    
                    # Cache'le (5 dakika)
                    self.cache.set(cache_key, result, 300)
                else:
                    errors.append(f"No resolver found for field: {field_name}")
                    
            except Exception as e:
                errors.append(f"Error resolving field {field_name}: {str(e)}")
        
        response = {'data': data}
        if errors:
            response['errors'] = errors
        
        return response
    
    def _execute_mutation(self, parsed_query: Dict, variables: Dict, context: Dict) -> Dict:
        """Mutation'ı execute et"""
        data = {}
        errors = []
        
        for field in parsed_query['fields']:
            field_name = field['name']
            
            try:
                # Resolver'ı bul ve çalıştır
                resolver = self._find_resolver('Mutation', field_name)
                if resolver:
                    result = resolver(field, variables, context)
                    data[field_name] = result
                    
                    # Mutation sonrası cache'leri temizle
                    self._invalidate_related_cache(field_name)
                else:
                    errors.append(f"No resolver found for mutation: {field_name}")
                    
            except Exception as e:
                errors.append(f"Error executing mutation {field_name}: {str(e)}")
        
        response = {'data': data}
        if errors:
            response['errors'] = errors
        
        return response
    
    def _execute_subscription(self, parsed_query: Dict, variables: Dict, context: Dict) -> Dict:
        """Subscription'ı execute et"""
        # Subscription implementation (WebSocket ile kullanılır)
        subscription_id = f"sub_{datetime.now().timestamp()}"
        
        for field in parsed_query['fields']:
            field_name = field['name']
            
            # Subscription'ı kaydet
            self.subscriptions[subscription_id] = {
                'field': field_name,
                'variables': variables,
                'context': context,
                'created_at': datetime.now()
            }
        
        return {
            'data': {
                'subscription_id': subscription_id,
                'status': 'subscribed'
            }
        }
    
    def _find_resolver(self, type_name: str, field_name: str):
        """Resolver fonksiyonunu bul"""
        return self.resolvers.get(type_name, {}).get(field_name)
    
    def _invalidate_related_cache(self, mutation_name: str):
        """Mutation sonrası ilgili cache'leri temizle"""
        # Mutation'a göre cache invalidation stratejisi
        cache_patterns = {
            'createUser': ['graphql_query:users*', 'graphql_query:user*'],
            'updateUser': ['graphql_query:users*', 'graphql_query:user*'],
            'deleteUser': ['graphql_query:users*', 'graphql_query:user*'],
            'createPost': ['graphql_query:posts*', 'graphql_query:post*'],
            'updatePost': ['graphql_query:posts*', 'graphql_query:post*'],
            'deletePost': ['graphql_query:posts*', 'graphql_query:post*']
        }
        
        patterns = cache_patterns.get(mutation_name, [])
        for pattern in patterns:
            # Pattern'e göre cache'leri temizle
            # Bu basit implementasyon, gerçek uygulamada daha sophisticated olmalı
            pass
    
    def create_default_schema(self):
        """Varsayılan schema oluştur"""
        schema_definition = """
        type User {
            id: ID!
            name: String!
            email: String!
            posts: [Post!]!
            createdAt: String!
        }
        
        type Post {
            id: ID!
            title: String!
            content: String!
            author: User!
            comments: [Comment!]!
            createdAt: String!
        }
        
        type Comment {
            id: ID!
            content: String!
            author: User!
            post: Post!
            createdAt: String!
        }
        
        type Query {
            users(limit: Int, offset: Int): [User!]!
            user(id: ID!): User
            posts(limit: Int, offset: Int): [Post!]!
            post(id: ID!): Post
            searchPosts(query: String!): [Post!]!
        }
        
        type Mutation {
            createUser(input: CreateUserInput!): User!
            updateUser(id: ID!, input: UpdateUserInput!): User!
            deleteUser(id: ID!): Boolean!
            createPost(input: CreatePostInput!): Post!
            updatePost(id: ID!, input: UpdatePostInput!): Post!
            deletePost(id: ID!): Boolean!
        }
        
        type Subscription {
            postAdded: Post!
            commentAdded(postId: ID!): Comment!
            userOnline: User!
        }
        
        input CreateUserInput {
            name: String!
            email: String!
            password: String!
        }
        
        input UpdateUserInput {
            name: String
            email: String
        }
        
        input CreatePostInput {
            title: String!
            content: String!
        }
        
        input UpdatePostInput {
            title: String
            content: String
        }
        """
        
        self.define_schema(schema_definition)
    
    def add_default_resolvers(self):
        """Varsayılan resolver'ları ekle"""
        from app.Models.User import User
        from app.Models.Post import Post
        from app.Models.Comment import Comment
        
        # Query resolvers
        self.add_resolver('Query', 'users', self._resolve_users)
        self.add_resolver('Query', 'user', self._resolve_user)
        self.add_resolver('Query', 'posts', self._resolve_posts)
        self.add_resolver('Query', 'post', self._resolve_post)
        self.add_resolver('Query', 'searchPosts', self._resolve_search_posts)
        
        # Mutation resolvers
        self.add_resolver('Mutation', 'createUser', self._resolve_create_user)
        self.add_resolver('Mutation', 'updateUser', self._resolve_update_user)
        self.add_resolver('Mutation', 'deleteUser', self._resolve_delete_user)
        self.add_resolver('Mutation', 'createPost', self._resolve_create_post)
        self.add_resolver('Mutation', 'updatePost', self._resolve_update_post)
        self.add_resolver('Mutation', 'deletePost', self._resolve_delete_post)
        
        # Type resolvers
        self.add_resolver('User', 'posts', self._resolve_user_posts)
        self.add_resolver('Post', 'author', self._resolve_post_author)
        self.add_resolver('Post', 'comments', self._resolve_post_comments)
    
    def _resolve_users(self, field, variables, context):
        """Users query resolver"""
        from app.Models.User import User
        
        limit = variables.get('limit', 10)
        offset = variables.get('offset', 0)
        
        users = User.query().limit(limit).offset(offset).get()
        return [user.to_dict() for user in users]
    
    def _resolve_user(self, field, variables, context):
        """User query resolver"""
        from app.Models.User import User
        
        user_id = variables.get('id')
        if not user_id:
            raise ValueError("User ID is required")
        
        user = User.find(user_id)
        return user.to_dict() if user else None
    
    def _resolve_posts(self, field, variables, context):
        """Posts query resolver"""
        from app.Models.Post import Post
        
        limit = variables.get('limit', 10)
        offset = variables.get('offset', 0)
        
        posts = Post.query().where({'status': 'published'}).limit(limit).offset(offset).get()
        return [post.to_dict() for post in posts]
    
    def _resolve_post(self, field, variables, context):
        """Post query resolver"""
        from app.Models.Post import Post
        
        post_id = variables.get('id')
        if not post_id:
            raise ValueError("Post ID is required")
        
        post = Post.find(post_id)
        return post.to_dict() if post else None
    
    def _resolve_search_posts(self, field, variables, context):
        """Search posts resolver"""
        from app.Models.Post import Post
        
        query = variables.get('query')
        if not query:
            return []
        
        posts = Post.query().where_like('title', f'%{query}%').get()
        return [post.to_dict() for post in posts]
    
    def _resolve_create_user(self, field, variables, context):
        """Create user mutation resolver"""
        from app.Models.User import User
        
        input_data = variables.get('input', {})
        user = User.create_user(input_data)
        
        if not user:
            raise ValueError("Failed to create user")
        
        return user.to_dict()
    
    def _resolve_update_user(self, field, variables, context):
        """Update user mutation resolver"""
        from app.Models.User import User
        
        user_id = variables.get('id')
        input_data = variables.get('input', {})
        
        user = User.find(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.update(input_data):
            return user.to_dict()
        else:
            raise ValueError("Failed to update user")
    
    def _resolve_delete_user(self, field, variables, context):
        """Delete user mutation resolver"""
        from app.Models.User import User
        
        user_id = variables.get('id')
        user = User.find(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        return user.delete()
    
    def _resolve_create_post(self, field, variables, context):
        """Create post mutation resolver"""
        from app.Models.Post import Post
        
        input_data = variables.get('input', {})
        
        # Context'ten user bilgisi al
        user = context.get('user')
        if not user:
            raise ValueError("Authentication required")
        
        input_data['user_id'] = user.get('user_id')
        post = Post.create_post(input_data)
        
        if not post:
            raise ValueError("Failed to create post")
        
        return post.to_dict()
    
    def _resolve_update_post(self, field, variables, context):
        """Update post mutation resolver"""
        from app.Models.Post import Post
        
        post_id = variables.get('id')
        input_data = variables.get('input', {})
        
        post = Post.find(post_id)
        if not post:
            raise ValueError("Post not found")
        
        # Authorization check
        user = context.get('user')
        if not user or (post.user_id != user.get('user_id') and user.get('role') != 'admin'):
            raise ValueError("Unauthorized")
        
        if post.update(input_data):
            return post.to_dict()
        else:
            raise ValueError("Failed to update post")
    
    def _resolve_delete_post(self, field, variables, context):
        """Delete post mutation resolver"""
        from app.Models.Post import Post
        
        post_id = variables.get('id')
        post = Post.find(post_id)
        
        if not post:
            raise ValueError("Post not found")
        
        # Authorization check
        user = context.get('user')
        if not user or (post.user_id != user.get('user_id') and user.get('role') != 'admin'):
            raise ValueError("Unauthorized")
        
        return post.delete()
    
    def _resolve_user_posts(self, field, variables, context):
        """User posts resolver"""
        from app.Models.Post import Post
        
        user_data = field.get('parent')  # Parent User object
        if not user_data:
            return []
        
        posts = Post.query().where({'user_id': user_data['id']}).get()
        return [post.to_dict() for post in posts]
    
    def _resolve_post_author(self, field, variables, context):
        """Post author resolver"""
        from app.Models.User import User
        
        post_data = field.get('parent')  # Parent Post object
        if not post_data:
            return None
        
        user = User.find(post_data['user_id'])
        return user.to_dict() if user else None
    
    def _resolve_post_comments(self, field, variables, context):
        """Post comments resolver"""
        from app.Models.Comment import Comment
        
        post_data = field.get('parent')  # Parent Post object
        if not post_data:
            return []
        
        comments = Comment.query().where({'post_id': post_data['id']}).get()
        return [comment.to_dict() for comment in comments]
    
    def introspect_schema(self) -> Dict:
        """Schema introspection (GraphQL tools için)"""
        return {
            'schema': self.schema,
            'types': list(self.schema.get('types', {}).keys()),
            'queries': list(self.schema.get('queries', {}).keys()),
            'mutations': list(self.schema.get('mutations', {}).keys()),
            'subscriptions': list(self.schema.get('subscriptions', {}).keys())
        }

# Global GraphQL service instance
_graphql_service = None

def get_graphql_service() -> GraphQLService:
    """Global GraphQL service instance'ını al"""
    global _graphql_service
    if _graphql_service is None:
        _graphql_service = GraphQLService()
        _graphql_service.create_default_schema()
        _graphql_service.add_default_resolvers()
    return _graphql_service