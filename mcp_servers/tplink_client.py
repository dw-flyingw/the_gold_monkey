#!/usr/bin/env python3
"""
TP-Link MCP Client for Salty
Communicates with TP-Link MCP server for smart lighting control
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

logger = logging.getLogger(__name__)

class TPLinkMCPClient:
    """Client for TP-Link MCP server"""
    
    def __init__(self, server_path: str = None):
        """Initialize the TP-Link MCP client"""
        self.server_path = server_path or "mcp_servers/tplink_server.py"
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Connect to the TP-Link MCP server"""
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_path]
            )
            
            # Create client session
            self.session = ClientSession(server_params)
            await self.session.__aenter__()
            
            logger.info("Connected to TP-Link MCP server")
            
        except Exception as e:
            logger.error(f"Error connecting to TP-Link MCP server: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the TP-Link MCP server"""
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
                logger.info("Disconnected from TP-Link MCP server")
            except Exception as e:
                logger.error(f"Error disconnecting from TP-Link MCP server: {e}")
    
    async def discover_devices(self) -> Dict[str, Any]:
        """Discover TP-Link devices on the network"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the discover_tplink_devices tool
            result = await self.session.call_tool("discover_tplink_devices", {})
            
            # Parse the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"response": content.text}
                else:
                    return {"response": str(content)}
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
            return {"error": str(e)}
    
    async def turn_on_all(self) -> Dict[str, Any]:
        """Turn on all TP-Link lights"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the turn_on_lights tool
            result = await self.session.call_tool("turn_on_lights", {})
            
            # Parse the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"response": content.text}
                else:
                    return {"response": str(content)}
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Error turning on lights: {e}")
            return {"error": str(e)}
    
    async def turn_off_all(self) -> Dict[str, Any]:
        """Turn off all TP-Link lights"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the turn_off_lights tool
            result = await self.session.call_tool("turn_off_lights", {})
            
            # Parse the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"response": content.text}
                else:
                    return {"response": str(content)}
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Error turning off lights: {e}")
            return {"error": str(e)}
    
    async def set_color_all(self, color: str) -> Dict[str, Any]:
        """Set color for all TP-Link lights"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the set_light_color tool
            result = await self.session.call_tool("set_light_color", {"color": color})
            
            # Parse the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"response": content.text}
                else:
                    return {"response": str(content)}
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Error setting light color: {e}")
            return {"error": str(e)}
    
    async def get_light_status(self) -> Dict[str, Any]:
        """Get status of all TP-Link lights"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the get_light_status tool
            result = await self.session.call_tool("get_light_status", {})
            
            # Parse the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"response": content.text}
                else:
                    return {"response": str(content)}
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Error getting light status: {e}")
            return {"error": str(e)}

# Convenience functions for direct use
async def discover_tplink_devices() -> Dict[str, Any]:
    """Discover TP-Link devices"""
    async with TPLinkMCPClient() as client:
        return await client.discover_devices()

async def turn_on_tplink_lights() -> Dict[str, Any]:
    """Turn on all TP-Link lights"""
    async with TPLinkMCPClient() as client:
        return await client.turn_on_all()

async def turn_off_tplink_lights() -> Dict[str, Any]:
    """Turn off all TP-Link lights"""
    async with TPLinkMCPClient() as client:
        return await client.turn_off_all()

async def set_tplink_color(color: str) -> Dict[str, Any]:
    """Set color for all TP-Link lights"""
    async with TPLinkMCPClient() as client:
        return await client.set_color_all(color)

async def get_tplink_status() -> Dict[str, Any]:
    """Get status of all TP-Link lights"""
    async with TPLinkMCPClient() as client:
        return await client.get_light_status()

if __name__ == "__main__":
    # Test the client
    async def test():
        try:
            # Test device discovery
            result = await discover_tplink_devices()
            print("Device discovery result:", result)
            
            # Test getting status
            status = await get_tplink_status()
            print("Light status:", status)
            
        except Exception as e:
            print(f"Test error: {e}")
    
    asyncio.run(test()) 