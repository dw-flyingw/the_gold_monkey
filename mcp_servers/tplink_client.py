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
    
    async def _call_tool(self, tool_name: str, arguments: dict = None) -> Dict[str, Any]:
        """Call a tool on the TP-Link MCP server"""
        try:
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_path]
            )
            
            async with stdio_client(server_params) as session:
                # Call the tool
                result = await session.call_tool(tool_name, arguments or {})
                
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
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def discover_devices(self) -> Dict[str, Any]:
        """Discover TP-Link devices on the network"""
        return await self._call_tool("discover_tplink_devices")
    
    async def turn_on_all(self) -> Dict[str, Any]:
        """Turn on all TP-Link lights"""
        return await self._call_tool("turn_on_lights")
    
    async def turn_off_all(self) -> Dict[str, Any]:
        """Turn off all TP-Link lights"""
        return await self._call_tool("turn_off_lights")
    
    async def set_color_all(self, color: str) -> Dict[str, Any]:
        """Set color for all TP-Link lights"""
        return await self._call_tool("set_light_color", {"color": color})
    
    async def get_light_status(self) -> Dict[str, Any]:
        """Get status of all TP-Link lights"""
        return await self._call_tool("get_light_status")

# Convenience functions for direct use
async def discover_tplink_devices() -> Dict[str, Any]:
    """Discover TP-Link devices"""
    client = TPLinkMCPClient()
    return await client.discover_devices()

async def turn_on_tplink_lights() -> Dict[str, Any]:
    """Turn on all TP-Link lights"""
    client = TPLinkMCPClient()
    return await client.turn_on_all()

async def turn_off_tplink_lights() -> Dict[str, Any]:
    """Turn off all TP-Link lights"""
    client = TPLinkMCPClient()
    return await client.turn_off_all()

async def set_tplink_color(color: str) -> Dict[str, Any]:
    """Set color for all TP-Link lights"""
    client = TPLinkMCPClient()
    return await client.set_color_all(color)

async def get_tplink_status() -> Dict[str, Any]:
    """Get status of all TP-Link lights"""
    client = TPLinkMCPClient()
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