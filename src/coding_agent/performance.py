"""
Caching and performance utilities for Codeius AI Coding Agent.
Implements caching for API calls and other expensive operations.
"""
import hashlib
import json
import time
from typing import Any, Optional, Dict
from functools import wraps
from datetime import datetime, timedelta
from coding_agent.config import config_manager
from coding_agent.logger import agent_logger


class SimpleCache:
    """Simple in-memory cache with TTL (Time To Live)."""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if cached entry is expired."""
        return datetime.now() < timestamp + timedelta(seconds=self.ttl_seconds)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry['expires_at']:
                return entry['value']
            else:
                # Clean up expired entry
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        expires_at = datetime.now() + timedelta(seconds=self.ttl_seconds)
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at
        }
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
    
    def remove(self, key: str) -> None:
        """Remove specific entry from cache."""
        if key in self.cache:
            del self.cache[key]


# Global cache instance
api_cache = SimpleCache(ttl_seconds=config_manager.get_agent_config().mcp_server_timeout)


def generate_cache_key(*args, **kwargs) -> str:
    """Generate a unique cache key from function args and kwargs."""
    # Create a unique key from the function arguments
    key_str = f"{args}_{sorted(kwargs.items())}"
    # Hash the string to get a consistent, fixed-length key
    return hashlib.md5(key_str.encode()).hexdigest()


def cached_api_call(ttl_seconds: int = 300):
    """Decorator for caching API calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"api_{func.__name__}_{generate_cache_key(*args, **kwargs)}"
            
            # Try to get from cache first
            cached_result = api_cache.get(cache_key)
            if cached_result is not None:
                agent_logger.api_logger.debug(f"Cache HIT for {cache_key}")
                return cached_result
            
            # Execute the function and cache the result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Only cache if call took more than a threshold (to avoid caching quick calls that don't benefit)
            if execution_time > 0.1:  # Only cache if call took more than 100ms
                api_cache.set(cache_key, result)
                agent_logger.api_logger.debug(f"Cache SET for {cache_key}")
            else:
                agent_logger.api_logger.debug(f"Cache SKIP (too fast) for {cache_key}")
            
            return result
        return wrapper
    return decorator


def rate_limit(max_calls: int, time_window: int):
    """Decorator to implement rate limiting."""
    def decorator(func):
        calls = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal calls
            now = time.time()
            
            # Remove calls that are outside the time window
            calls = [call_time for call_time in calls if now - call_time < time_window]
            
            if len(calls) >= max_calls:
                agent_logger.app_logger.warning(f"Rate limit exceeded for {func.__name__}")
                raise Exception(f"Rate limit exceeded: {max_calls} calls per {time_window} seconds")
            
            # Add current call
            calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics = {}
    
    def record_operation(self, operation_name: str, duration: float, success: bool = True):
        """Record an operation's performance."""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                'count': 0,
                'total_duration': 0.0,
                'success_count': 0,
                'failure_count': 0,
                'avg_duration': 0.0
            }
        
        metrics = self.metrics[operation_name]
        metrics['count'] += 1
        metrics['total_duration'] += duration
        
        if success:
            metrics['success_count'] += 1
        else:
            metrics['failure_count'] += 1
            
        metrics['avg_duration'] = metrics['total_duration'] / metrics['count']
        
        # Log slow operations
        if duration > 1.0:  # More than 1 second
            agent_logger.app_logger.warning(f"Slow operation: {operation_name} took {duration:.2f}s")
    
    def get_metrics(self, operation_name: str) -> Dict[str, Any]:
        """Get metrics for a specific operation."""
        return self.metrics.get(operation_name, {})


# Global performance monitor
perf_monitor = PerformanceMonitor()