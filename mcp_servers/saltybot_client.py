#!/usr/bin/env python3
"""
SaltyBot MCP Client for Salty
Communicates with SaltyBot MCP server for AI chatbot functionality
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

logger = logging.getLogger(__name__)

class SaltyBotMCPClient:
    """Client for SaltyBot MCP server"""
    
    def __init__(self, server_path: str = None):
        """Initialize the SaltyBot MCP client"""
        self.server_path = server_path or "mcp_servers/saltybot_server.py"
    
    async def _call_tool(self, tool_name: str, arguments: dict = None) -> Dict[str, Any]:
        """Call a tool on the SaltyBot MCP server"""
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
    
    async def chat_with_salty(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat with Salty"""
        args = {"message": message}
        if conversation_history:
            args["conversation_history"] = conversation_history
        return await self._call_tool("chat_with_salty", args)
    
    async def get_config(self) -> Dict[str, Any]:
        """Get Salty's configuration"""
        return await self._call_tool("get_salty_config")
    
    async def get_personality(self) -> Dict[str, Any]:
        """Get Salty's personality information"""
        return await self._call_tool("get_salty_personality")
    
    async def generate_story(self, theme: str = "tropical") -> Dict[str, Any]:
        """Generate a tiki-themed story"""
        return await self._call_tool("generate_tiki_story", {"theme": theme})
    
    async def recommend_drink(self, preferences: str = "classic") -> Dict[str, Any]:
        """Recommend a tropical drink"""
        return await self._call_tool("recommend_drink", {"preferences": preferences})

# Convenience functions for direct use
async def chat_with_salty(message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
    """Chat with Salty"""
    client = SaltyBotMCPClient()
    return await client.chat_with_salty(message, conversation_history)

async def get_salty_config() -> Dict[str, Any]:
    """Get Salty's configuration"""
    client = SaltyBotMCPClient()
    return await client.get_config()

async def get_salty_personality() -> Dict[str, Any]:
    """Get Salty's personality information"""
    client = SaltyBotMCPClient()
    return await client.get_personality()

async def generate_tiki_story(theme: str = "tropical") -> Dict[str, Any]:
    """Generate a tiki-themed story"""
    client = SaltyBotMCPClient()
    return await client.generate_story(theme)

async def recommend_drink(preferences: str = "classic") -> Dict[str, Any]:
    """Recommend a tropical drink"""
    client = SaltyBotMCPClient()
    return await client.recommend_drink(preferences)

if __name__ == "__main__":
    # Test the client
    async def test():
        try:
            # Test getting config
            config = await get_salty_config()
            print("Salty config:", config)
            
            # Test chat
            response = await chat_with_salty("Hello Salty!")
            print("Chat response:", response)
            
        except Exception as e:
            print(f"Test error: {e}")
    
    asyncio.run(test()) 