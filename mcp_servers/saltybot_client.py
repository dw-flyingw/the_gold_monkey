#!/usr/bin/env python3
"""
SaltyBot MCP Client for Salty
Communicates with SaltyBot MCP server for AI chatbot functionality
"""

import asyncio
import json
import logging
import traceback
import sys
import os
from typing import Dict, Any, List
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Add the parent directory to the path to import utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.mcp_error_handler import handle_mcp_error, is_mcp_error

# Configure DEBUG logging for the client
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Also enable DEBUG for MCP client modules
logging.getLogger('mcp.client').setLevel(logging.DEBUG)

class SaltyBotMCPClient:
    """Client for SaltyBot MCP server"""
    
    def __init__(self, server_path: str = None):
        """Initialize the SaltyBot MCP client"""
        self.server_path = server_path or "mcp_servers/saltybot_server.py"
        logger.info(f"Initializing SaltyBotMCPClient with server path: {self.server_path}")
    
    async def _call_tool(self, tool_name: str, arguments: dict = None) -> Dict[str, Any]:
        """Call a tool on the SaltyBot MCP server"""
        logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
        try:
            logger.info(f"Launching subprocess: python mcp_servers/saltybot_server.py")
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_path]
            )
            async with stdio_client(server_params) as (read_stream, write_stream):
                logger.info("Connected to server, creating ClientSession...")
                async with ClientSession(read_stream, write_stream) as session:
                    logger.info("ClientSession created, waiting for initialization...")
                    # Add a small delay to ensure proper handshake
                    await asyncio.sleep(0.5)
                    logger.info("Initializing session...")
                    await session.initialize()
                    logger.info("Session initialized, calling tool...")
                    result = await session.call_tool(tool_name, arguments or {})
                    logger.info(f"Tool call completed, result: {result}")
                    # Parse the result
                    if result.content and len(result.content) > 0:
                        content = result.content[0]
                        if hasattr(content, 'text'):
                            response = {"response": content.text}
                            logger.info(f"Parsed response: {response}")
                            return response
                        else:
                            response = {"response": str(content)}
                            logger.info(f"Parsed response: {response}")
                            return response
                    else:
                        error = {"error": "No response from server"}
                        logger.warning(f"No content in result: {error}")
                        return error
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            logger.error(traceback.format_exc())
            if is_mcp_error(e):
                return handle_mcp_error(e, f"saltybot_client.{tool_name}")
            return {"error": str(e)}
    
    async def chat_with_salty(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat with Salty"""
        logger.info(f"chat_with_salty called with message: {message}")
        try:
            args = {"message": message}
            if conversation_history:
                args["conversation_history"] = conversation_history
            return await self._call_tool("chat_with_salty", args)
        except Exception as e:
            logging.error(f"Error in chat_with_salty: {e}\n{traceback.format_exc()}")
            if is_mcp_error(e):
                return handle_mcp_error(e, "saltybot_client.chat_with_salty")
            return {"error": str(e)}
    
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

async def get_tools() -> Dict[str, Any]:
    """Get a dictionary of all available tools"""
    return {
        "chat_with_salty": chat_with_salty,
        "get_salty_config": get_salty_config,
        "get_salty_personality": get_salty_personality,
        "generate_tiki_story": generate_tiki_story,
        "recommend_drink": recommend_drink,
    }

if __name__ == "__main__":
    # Test the client
    async def test():
        try:
            logger.info("Starting SaltyBot client test...")
            # Test getting config
            config = await get_salty_config()
            print("Salty config:", config)
            
            # Test chat
            response = await chat_with_salty("Hello Salty!")
            print("Chat response:", response)
            
        except Exception as e:
            print(f"Test error: {e}")
            logger.error(f"Test error: {e}")
            logger.error(traceback.format_exc())
    
    asyncio.run(test()) 