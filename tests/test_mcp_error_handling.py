#!/usr/bin/env python3
"""
Test MCP Error Handling
"""

import asyncio
import pytest
import logging
from unittest.mock import Mock, patch

# Import error handler
from utils.mcp_error_handler import (
    MCPErrorHandler, 
    handle_mcp_error, 
    is_mcp_error,
    safe_mcp_execution
)

# Import unified client
from mcp_servers.unified_client import UnifiedMCPClient

logger = logging.getLogger(__name__)

class TestMCPErrorHandling:
    """Test MCP error handling functionality"""
    
    def test_is_mcp_error(self):
        """Test MCP error detection"""
        # Test TaskGroup error
        taskgroup_error = Exception("unhandled errors in a TaskGroup (1 sub-exception)")
        assert is_mcp_error(taskgroup_error) == True
        
        # Test regular error
        regular_error = Exception("Something else went wrong")
        assert is_mcp_error(regular_error) == False
        
        # Test MCP error
        mcp_error = Exception("MCP communication failed")
        assert is_mcp_error(mcp_error) == True
    
    def test_handle_mcp_error(self):
        """Test MCP error handling"""
        taskgroup_error = Exception("unhandled errors in a TaskGroup (1 sub-exception)")
        result = handle_mcp_error(taskgroup_error, "test context")
        
        assert result["error"] == "MCP communication error"
        assert result["fallback"] == True
        assert "🦜 Squawk!" in result["response"]
    
    def test_create_fallback_response(self):
        """Test fallback response creation"""
        fallback = MCPErrorHandler.create_fallback_response("system_get_time")
        assert fallback["response"] == "🕐 System time unavailable"
        
        fallback = MCPErrorHandler.create_fallback_response("spotify_play")
        assert fallback["response"] == "🎵 Spotify control unavailable"
        
        fallback = MCPErrorHandler.create_fallback_response("unknown_tool")
        assert "🦜 Tool unknown_tool unavailable" in fallback["response"]
    
    @pytest.mark.asyncio
    async def test_safe_mcp_execution(self):
        """Test safe MCP execution with error handling"""
        # Test successful execution
        def successful_func():
            return {"response": "Success!"}
        
        result = safe_mcp_execution("test_func", successful_func)
        assert result["response"] == "Success!"
        
        # Test TaskGroup error
        def failing_func():
            raise Exception("unhandled errors in a TaskGroup (1 sub-exception)")
        
        result = safe_mcp_execution("test_func", failing_func)
        assert result["error"] == "MCP communication error"
        assert result["fallback"] == True
    
    @pytest.mark.asyncio
    async def test_unified_client_error_handling(self):
        """Test unified client error handling"""
        client = UnifiedMCPClient()
        
        # Test successful call
        result = await client.call_tool("system_get_time")
        assert "response" in result
        assert "🕐 Current time:" in result["response"]
        
        # Test with invalid tool (should handle gracefully)
        result = await client.call_tool("invalid_tool")
        assert "response" in result
        assert "🦜 Tool invalid_tool executed successfully!" in result["response"]

class TestMCPErrorHandlerClass:
    """Test MCPErrorHandler class methods"""
    
    @pytest.mark.asyncio
    async def test_safe_mcp_call_decorator(self):
        """Test the safe_mcp_call decorator"""
        
        @MCPErrorHandler.safe_mcp_call
        async def test_function():
            raise Exception("unhandled errors in a TaskGroup (1 sub-exception)")
        
        result = await test_function()
        assert result["error"] == "MCP communication error"
        assert result["fallback"] == True
    
    @pytest.mark.asyncio
    async def test_retry_mcp_call(self):
        """Test retry functionality"""
        call_count = 0
        
        async def failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("unhandled errors in a TaskGroup (1 sub-exception)")
        
        result = await MCPErrorHandler.retry_mcp_call(failing_function, max_retries=3)
        assert result["error"] == "MCP communication failed after retries"
        assert result["fallback"] == True
        assert call_count == 3  # Should have tried 3 times

def test_error_handler_integration():
    """Test integration with real error scenarios"""
    
    # Simulate a TaskGroup error
    error = Exception("unhandled errors in a TaskGroup (1 sub-exception)")
    
    # Test error detection
    assert is_mcp_error(error) == True
    
    # Test error handling
    result = handle_mcp_error(error, "integration test")
    assert result["fallback"] == True
    assert "🦜 Squawk!" in result["response"]

if __name__ == "__main__":
    # Run basic tests
    print("Testing MCP error handling...")
    
    # Test error detection
    error = Exception("unhandled errors in a TaskGroup (1 sub-exception)")
    assert is_mcp_error(error) == True
    print("✅ Error detection works")
    
    # Test error handling
    result = handle_mcp_error(error, "test")
    assert result["fallback"] == True
    print("✅ Error handling works")
    
    # Test fallback responses
    fallback = MCPErrorHandler.create_fallback_response("system_get_time")
    assert "🕐 System time unavailable" in fallback["response"]
    print("✅ Fallback responses work")
    
    print("🎉 All MCP error handling tests passed!") 