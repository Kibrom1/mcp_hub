"""
Enhanced security implementation for MCP Hub Core
"""

import hashlib
import secrets
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import logging
from functools import wraps
import time
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "your-super-secret-key-change-in-production"  # Should be from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Rate limiting
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Security models
class User(BaseModel):
    id: str
    username: str
    email: str
    role: str = "user"
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

# Security utilities
class SecurityManager:
    """Enhanced security manager with proper authentication and authorization"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = REFRESH_TOKEN_EXPIRE_DAYS
        
        # In-memory storage for demo (use database in production)
        self.users = self._create_default_users()
        self.refresh_tokens = {}
        self.rate_limits = defaultdict(lambda: deque())
    
    def _create_default_users(self) -> Dict[str, User]:
        """Create default users for demo purposes"""
        users = {}
        
        # Admin user
        admin_password = self.hash_password("admin123")
        users["admin"] = User(
            id="admin-001",
            username="admin",
            email="admin@mcp-hub.com",
            role="admin",
            is_active=True,
            created_at=datetime.now()
        )
        users["admin"].password_hash = admin_password
        
        # Regular user
        user_password = self.hash_password("user123")
        users["user"] = User(
            id="user-001",
            username="user",
            email="user@mcp-hub.com",
            role="user",
            is_active=True,
            created_at=datetime.now()
        )
        users["user"].password_hash = user_password
        
        return users
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> TokenData:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            role: str = payload.get("role")
            
            if username is None or user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            return TokenData(username=username, user_id=user_id, role=role)
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.users.get(username)
        if not user or not user.is_active:
            return None
        
        if not hasattr(user, 'password_hash'):
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.now()
        
        return user
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limits"""
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW
        
        # Clean old requests
        while self.rate_limits[client_ip] and self.rate_limits[client_ip][0] < window_start:
            self.rate_limits[client_ip].popleft()
        
        # Check if within limits
        if len(self.rate_limits[client_ip]) >= RATE_LIMIT_REQUESTS:
            return False
        
        # Add current request
        self.rate_limits[client_ip].append(now)
        return True
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username)

# Global security manager
security_manager = SecurityManager()

# FastAPI security
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    token_data = security_manager.verify_token(token)
    
    user = security_manager.get_user_by_username(token_data.username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(required_role: str):
    """Decorator to require specific role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs or dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if current_user.role != required_role and current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Check permission (simplified for demo)
            if not has_permission(current_user, permission):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def has_permission(user: User, permission: str) -> bool:
    """Check if user has specific permission"""
    # Simplified permission system
    if user.role == "admin":
        return True
    
    # Define role-based permissions
    role_permissions = {
        "user": ["read_tools", "execute_tools", "read_resources"],
        "moderator": ["read_tools", "execute_tools", "read_resources", "manage_tools"],
        "admin": ["*"]  # All permissions
    }
    
    user_permissions = role_permissions.get(user.role, [])
    return permission in user_permissions or "*" in user_permissions

def rate_limit(max_requests: int = 100, window: int = 60):
    """Decorator for rate limiting"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get client IP from request
            request = kwargs.get('request')
            if not request:
                return await func(*args, **kwargs)
            
            client_ip = request.client.host
            
            if not security_manager.check_rate_limit(client_ip):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS"""
    import html
    return html.escape(text)

def validate_sql_query(query: str) -> bool:
    """Validate SQL query to prevent injection"""
    # Simple validation - in production, use proper SQL parsing
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
    query_upper = query.upper()
    
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False
    
    return True

def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)

def verify_csrf_token(token: str, session_token: str) -> bool:
    """Verify CSRF token"""
    return secrets.compare_digest(token, session_token)

# Security middleware
class SecurityMiddleware:
    """Security middleware for additional protection"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Add security headers
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    
                    # Security headers
                    security_headers = [
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"DENY"),
                        (b"x-xss-protection", b"1; mode=block"),
                        (b"strict-transport-security", b"max-age=31536000; includeSubDomains"),
                        (b"content-security-policy", b"default-src 'self'"),
                    ]
                    
                    headers.extend(security_headers)
                    message["headers"] = headers
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
