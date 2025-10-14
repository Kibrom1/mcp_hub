"""
Caching system for MCP Hub Core with Redis and in-memory fallback
"""

import json
import time
import hashlib
from typing import Any, Optional, Dict, List, Union
from functools import wraps
import logging
from datetime import datetime, timedelta
import threading
from collections import OrderedDict

logger = logging.getLogger(__name__)

# Try to import Redis, fallback to in-memory cache
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")

class InMemoryCache:
    """Thread-safe in-memory cache with LRU eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = OrderedDict()
        self._lock = threading.RLock()
    
    def _is_expired(self, item: Dict[str, Any]) -> bool:
        """Check if cache item is expired"""
        if 'expires_at' not in item:
            return False
        return time.time() > item['expires_at']
    
    def _evict_expired(self):
        """Remove expired items"""
        current_time = time.time()
        expired_keys = []
        
        for key, item in self._cache.items():
            if 'expires_at' in item and current_time > item['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if self._cache:
            self._cache.popitem(last=False)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            self._evict_expired()
            
            if key not in self._cache:
                return None
            
            item = self._cache[key]
            
            if self._is_expired(item):
                del self._cache[key]
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return item['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        with self._lock:
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            
            # Remove if exists
            if key in self._cache:
                del self._cache[key]
            
            # Evict if at capacity
            while len(self._cache) >= self.max_size:
                self._evict_lru()
            
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time()
            }
            
            return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        with self._lock:
            self._cache.clear()
            return True
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get cache keys matching pattern"""
        with self._lock:
            if pattern == "*":
                return list(self._cache.keys())
            
            # Simple pattern matching
            import fnmatch
            return [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]
    
    def size(self) -> int:
        """Get cache size"""
        with self._lock:
            return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'default_ttl': self.default_ttl,
                'type': 'in_memory'
            }

class RedisCache:
    """Redis-based cache with connection pooling"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, 
                 password: Optional[str] = None, max_connections: int = 10):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        
        # Create connection pool
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            decode_responses=True
        )
        
        self.redis = redis.Redis(connection_pool=self.pool)
        
        # Test connection
        try:
            self.redis.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    def _serialize(self, value: Any) -> str:
        """Serialize value for storage"""
        return json.dumps(value, default=str)
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            return self._deserialize(value)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            serialized_value = self._serialize(value)
            if ttl:
                return self.redis.setex(key, ttl, serialized_value)
            else:
                return self.redis.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        try:
            return self.redis.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get cache keys matching pattern"""
        try:
            return self.redis.keys(pattern)
        except Exception as e:
            logger.error(f"Redis keys error: {e}")
            return []
    
    def size(self) -> int:
        """Get cache size"""
        try:
            return self.redis.dbsize()
        except Exception as e:
            logger.error(f"Redis size error: {e}")
            return 0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.redis.info()
            return {
                'size': self.size(),
                'type': 'redis',
                'host': self.host,
                'port': self.port,
                'db': self.db,
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'uptime': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {'type': 'redis', 'error': str(e)}

class CacheManager:
    """Unified cache manager with fallback support"""
    
    def __init__(self, cache_type: str = "auto", **kwargs):
        self.cache_type = cache_type
        self.cache = None
        
        if cache_type == "redis" and REDIS_AVAILABLE:
            try:
                self.cache = RedisCache(**kwargs)
                logger.info("Using Redis cache")
            except Exception as e:
                logger.warning(f"Redis cache failed, falling back to in-memory: {e}")
                self.cache = InMemoryCache()
        else:
            self.cache = InMemoryCache()
            logger.info("Using in-memory cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        return self.cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return self.cache.delete(key)
    
    def clear(self) -> bool:
        """Clear all cache"""
        return self.cache.clear()
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get cache keys matching pattern"""
        return self.cache.keys(pattern)
    
    def size(self) -> int:
        """Get cache size"""
        return self.cache.size()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.stats()

# Global cache manager
cache_manager = CacheManager()

# Cache decorators
def cache_result(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(func.__name__, args, kwargs, key_prefix)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        return wrapper
    return decorator

def cache_invalidate(pattern: str = "*"):
    """Decorator to invalidate cache after function execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Invalidate cache
            keys_to_delete = cache_manager.keys(pattern)
            for key in keys_to_delete:
                cache_manager.delete(key)
            
            logger.debug(f"Invalidated cache for pattern: {pattern}")
            return result
        return wrapper
    return decorator

def _generate_cache_key(func_name: str, args: tuple, kwargs: dict, prefix: str = "") -> str:
    """Generate cache key from function name and arguments"""
    # Create hash of arguments
    args_str = str(args) + str(sorted(kwargs.items()))
    args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
    
    # Combine with function name and prefix
    key_parts = [part for part in [prefix, func_name, args_hash] if part]
    return ":".join(key_parts)

# Cache utilities
class CacheUtils:
    """Utility functions for cache management"""
    
    @staticmethod
    def cache_tools_list(ttl: int = 600):
        """Cache tools list with TTL"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = "tools:list"
                cached = cache_manager.get(cache_key)
                if cached:
                    return cached
                
                result = await func(*args, **kwargs)
                cache_manager.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def cache_resources_list(ttl: int = 600):
        """Cache resources list with TTL"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = "resources:list"
                cached = cache_manager.get(cache_key)
                if cached:
                    return cached
                
                result = await func(*args, **kwargs)
                cache_manager.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def cache_llm_response(ttl: int = 3600):
        """Cache LLM responses with TTL"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Create cache key from messages
                messages = kwargs.get('messages', args[0] if args else [])
                messages_str = str(messages)
                messages_hash = hashlib.md5(messages_str.encode()).hexdigest()[:8]
                cache_key = f"llm:response:{messages_hash}"
                
                cached = cache_manager.get(cache_key)
                if cached:
                    return cached
                
                result = await func(*args, **kwargs)
                cache_manager.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def invalidate_tools_cache():
        """Invalidate tools-related cache"""
        patterns = ["tools:*", "resources:*"]
        for pattern in patterns:
            keys = cache_manager.keys(pattern)
            for key in keys:
                cache_manager.delete(key)
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return cache_manager.stats()
    
    @staticmethod
    def warm_cache():
        """Warm up cache with frequently accessed data"""
        # This would be called during application startup
        logger.info("Warming up cache...")
        # Implementation would depend on specific use cases
        pass
