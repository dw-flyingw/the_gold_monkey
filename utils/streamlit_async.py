#!/usr/bin/env python3
"""
Streamlit Async Utilities
Handles async operations in Streamlit without event loop conflicts
"""

import asyncio
import concurrent.futures
import logging
from typing import Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)

def run_async_in_thread(async_func: Callable, *args, **kwargs) -> Any:
    """
    Run an async function in a separate thread to avoid Streamlit event loop conflicts.
    
    Args:
        async_func: The async function to run
        *args, **kwargs: Arguments to pass to the async function
        
    Returns:
        The result of the async function
        
    Raises:
        Exception: If the async function raises an exception
    """
    def run_in_new_loop():
        """Create a new event loop in the thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(async_func(*args, **kwargs))
        finally:
            loop.close()
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_new_loop)
            return future.result(timeout=30)  # 30 second timeout
    except concurrent.futures.TimeoutError:
        raise Exception("Async operation timed out")
    except Exception as e:
        logger.error(f"Error in async operation: {e}")
        raise

def streamlit_async(async_func: Callable) -> Callable:
    """
    Decorator to make async functions safe for use in Streamlit.
    
    Usage:
        @streamlit_async
        async def my_async_function():
            return "result"
            
        # In Streamlit:
        result = my_async_function()  # No asyncio.run() needed
    """
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        return run_async_in_thread(async_func, *args, **kwargs)
    return wrapper

# Convenience functions for common operations
def safe_async_call(async_func: Callable, *args, **kwargs) -> Any:
    """Safely call an async function from Streamlit"""
    return run_async_in_thread(async_func, *args, **kwargs) 