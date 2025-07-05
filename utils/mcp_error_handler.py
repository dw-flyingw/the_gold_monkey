#!/usr/bin/env python3
"""
MCP Error Handler
Handles TaskGroup and other MCP communication errors gracefully
"""

import asyncio
import logging
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class MCPErrorHandler:
    """Handles MCP communication errors gracefully"""
    
    @staticmethod
    def safe_mcp_call(func: Callable) -> Callable:
        """Decorator to safely handle MCP calls"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                if "TaskGroup" in error_msg or "unhandled errors" in error_msg:
                    logger.warning(f"MCP TaskGroup error in {func.__name__}: {error_msg}")
                    return {"error": "MCP communication error", "fallback": True}
                else:
                    logger.error(f"Error in {func.__name__}: {error_msg}")
                    return {"error": error_msg}
        return wrapper
    
    @staticmethod
    async def retry_mcp_call(func: Callable, max_retries: int = 3, delay: float = 1.0) -> Any:
        """Retry MCP calls with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                error_msg = str(e)
                if "TaskGroup" in error_msg or "unhandled errors" in error_msg:
                    logger.warning(f"MCP TaskGroup error (attempt {attempt + 1}/{max_retries}): {error_msg}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))
                        continue
                    else:
                        return {"error": "MCP communication failed after retries", "fallback": True}
                else:
                    logger.error(f"Error in MCP call: {error_msg}")
                    return {"error": error_msg}
        
        return {"error": "Max retries exceeded"}
    
    @staticmethod
    def create_fallback_response(original_call: str, fallback_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a fallback response when MCP fails"""
        fallback_data = fallback_data or {}
        
        fallbacks = {
            "system_get_time": {"response": "🕐 System time unavailable"},
            "spotify_play": {"response": "🎵 Spotify control unavailable"},
            "tplink_turn_on_lights": {"response": "💡 Light control unavailable"},
            "roku_power_on": {"response": "🟢 Roku control unavailable"},
            "voice_speak_text": {"response": "🗣️ Voice control unavailable"},
        }
        
        return fallbacks.get(original_call, {"response": f"🦜 Tool {original_call} unavailable"})

def safe_mcp_execution(func_name: str, func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Safely execute MCP functions with error handling"""
    try:
        # Try the original function
        result = asyncio.run(func(*args, **kwargs))
        return result
    except Exception as e:
        error_msg = str(e)
        if "TaskGroup" in error_msg or "unhandled errors" in error_msg:
            logger.warning(f"MCP TaskGroup error in {func_name}: {error_msg}")
            # Return fallback response
            fallback = MCPErrorHandler.create_fallback_response(func_name)
            fallback["error"] = "MCP communication error"
            fallback["fallback"] = True
            return fallback
        else:
            logger.error(f"Error in {func_name}: {error_msg}")
            return {"error": error_msg}

# Convenience functions
def handle_mcp_error(error: Exception, context: str = "MCP call") -> Dict[str, Any]:
    """Handle MCP errors and return appropriate response"""
    error_msg = str(error)
    
    if "TaskGroup" in error_msg or "unhandled errors" in error_msg:
        logger.warning(f"MCP TaskGroup error in {context}: {error_msg}")
        return {
            "error": "MCP communication error",
            "fallback": True,
            "response": "🦜 Squawk! MCP communication issue, using fallback mode!"
        }
    else:
        logger.error(f"Error in {context}: {error_msg}")
        return {"error": error_msg}

def is_mcp_error(error: Exception) -> bool:
    """Check if an error is MCP-related"""
    error_msg = str(error)
    return "TaskGroup" in error_msg or "unhandled errors" in error_msg or "MCP" in error_msg 