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
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Connect to the SaltyBot MCP server"""
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_path]
            )
            
            # Create client session
            self.session = ClientSession(server_params)
            await self.session.__aenter__()
            
            logger.info("Connected to SaltyBot MCP server")
            
        except Exception as e:
            logger.error(f"Error connecting to SaltyBot MCP server: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the SaltyBot MCP server"""
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
                logger.info("Disconnected from SaltyBot MCP server")
            except Exception as e:
                logger.error(f"Error disconnecting from SaltyBot MCP server: {e}")
    
    async def chat_with_salty(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat with Salty, the talking parrot"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the chat_with_salty tool
            args = {"message": message}
            if conversation_history:
                args["conversation_history"] = conversation_history
            
            result = await self.session.call_tool("chat_with_salty", args)
            
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
            logger.error(f"Error chatting with Salty: {e}")
            return {"error": str(e)}
    
    async def get_salty_config(self) -> Dict[str, Any]:
        """Get Salty's current configuration"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the get_salty_config tool
            result = await self.session.call_tool("get_salty_config", {})
            
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
            logger.error(f"Error getting Salty config: {e}")
            return {"error": str(e)}
    
    async def get_salty_personality(self) -> Dict[str, Any]:
        """Get information about Salty's personality"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the get_salty_personality tool
            result = await self.session.call_tool("get_salty_personality", {})
            
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
            logger.error(f"Error getting Salty personality: {e}")
            return {"error": str(e)}
    
    async def generate_tiki_story(self, theme: str = "tropical") -> Dict[str, Any]:
        """Generate a tiki-themed story"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the generate_tiki_story tool
            result = await self.session.call_tool("generate_tiki_story", {"theme": theme})
            
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
            logger.error(f"Error generating tiki story: {e}")
            return {"error": str(e)}
    
    async def recommend_drink(self, preferences: str = "classic") -> Dict[str, Any]:
        """Recommend a tropical drink"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the recommend_drink tool
            result = await self.session.call_tool("recommend_drink", {"preferences": preferences})
            
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
            logger.error(f"Error recommending drink: {e}")
            return {"error": str(e)}

# Convenience functions for direct use
async def chat_with_salty(message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
    """Chat with Salty"""
    async with SaltyBotMCPClient() as client:
        return await client.chat_with_salty(message, conversation_history)

async def get_salty_config() -> Dict[str, Any]:
    """Get Salty's configuration"""
    async with SaltyBotMCPClient() as client:
        return await client.get_salty_config()

async def get_salty_personality() -> Dict[str, Any]:
    """Get Salty's personality"""
    async with SaltyBotMCPClient() as client:
        return await client.get_salty_personality()

async def generate_tiki_story(theme: str = "tropical") -> Dict[str, Any]:
    """Generate a tiki story"""
    async with SaltyBotMCPClient() as client:
        return await client.generate_tiki_story(theme)

async def recommend_drink(preferences: str = "classic") -> Dict[str, Any]:
    """Recommend a drink"""
    async with SaltyBotMCPClient() as client:
        return await client.recommend_drink(preferences)

if __name__ == "__main__":
    # Test the client
    async def test():
        try:
            # Test getting config
            config = await get_salty_config()
            print("Salty config:", config)
            
            # Test chat
            response = await chat_with_salty("Hello Salty! How are you today?")
            print("Chat response:", response)
            
        except Exception as e:
            print(f"Test error: {e}")
    
    asyncio.run(test()) 