"""
Debounce and throttle utilities for performance optimization
"""
import time
from functools import wraps

def debounce(wait_seconds):
    """
    Decorator that will postpone a function's execution until after 
    wait_seconds have elapsed since the last time it was invoked.
    """
    def decorator(func):
        last_call = [0]
        timeout = [None]
        
        @wraps(func)
        def debounced(*args, **kwargs):
            def call_function():
                last_call[0] = time.time()
                return func(*args, **kwargs)
            
            current_time = time.time()
            
            if timeout[0]:
                timeout[0] = None
            
            if current_time - last_call[0] > wait_seconds:
                return call_function()
            else:
                timeout[0] = call_function
                
        return debounced
    return decorator

def throttle(wait_seconds):
    """
    Decorator that prevents a function from being called more than
    once every wait_seconds.
    """
    def decorator(func):
        last_call = [0]
        
        @wraps(func)
        def throttled(*args, **kwargs):
            current_time = time.time()
            
            if current_time - last_call[0] >= wait_seconds:
                last_call[0] = current_time
                return func(*args, **kwargs)
        
        return throttled
    return decorator
