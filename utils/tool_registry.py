import asyncio
import importlib
from typing import Dict, Any, Callable
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    The ToolRegistry discovers and manages tools from all available MCP servers.
    """

    def __init__(self):
        """
        Initializes the ToolRegistry.
        """
        self.tools: Dict[str, Callable] = {}

    async def discover_tools(self):
        """
        Discovers and registers tools from all available MCP servers.
        Only imports direct client modules that don't require MCP dependencies.
        """
        # Only include direct client modules that don't require MCP
        direct_clients = [
            "spotify_client",
            "tplink_direct", 
            "voice_client",
        ]
        
        # MCP-dependent clients (these require MCP servers to be running)
        mcp_clients = [
            "roku_client",
            "rag_client", 
            "saltybot_client",
        ]

        # Get the mcp_servers directory path
        mcp_servers_dir = Path(__file__).parent.parent / "mcp_servers"
        
        # First, try direct clients
        for client_module_name in direct_clients:
            try:
                logger.info(f"Discovering tools from direct client: {client_module_name}")
                
                # Import the module directly from the file path
                module_path = mcp_servers_dir / f"{client_module_name}.py"
                if not module_path.exists():
                    logger.warning(f"Module file not found: {module_path}")
                    continue
                
                # Add the mcp_servers directory to sys.path temporarily
                original_path = sys.path.copy()
                sys.path.insert(0, str(mcp_servers_dir))
                
                try:
                    client_module = importlib.import_module(client_module_name)
                    
                    # Check if the module has a get_tools function
                    if hasattr(client_module, "get_tools"):
                        get_tools_func = client_module.get_tools
                        
                        # Check if it's an async function
                        if asyncio.iscoroutinefunction(get_tools_func):
                            new_tools = await get_tools_func()
                        else:
                            new_tools = get_tools_func()
                        
                        if new_tools and isinstance(new_tools, dict):
                            # Add module prefix to tool names to avoid conflicts
                            module_prefix = client_module_name
                            for tool_name, tool_func in new_tools.items():
                                prefixed_name = f"{module_prefix}.{tool_name}"
                                self.tools[prefixed_name] = tool_func
                            
                            logger.info(f"Discovered {len(new_tools)} tools from {client_module_name}")
                        else:
                            logger.warning(f"No tools returned from {client_module_name}")
                    else:
                        logger.warning(f"No get_tools function found in {client_module_name}")
                        
                finally:
                    # Restore original sys.path
                    sys.path = original_path
                    
            except ImportError as e:
                logger.error(f"Could not import {client_module_name}: {e}")
            except Exception as e:
                logger.error(f"Error discovering tools from {client_module_name}: {e}")

        # Then try MCP clients (these might fail if MCP is not available)
        for client_module_name in mcp_clients:
            try:
                logger.info(f"Attempting to discover tools from MCP client: {client_module_name}")
                
                # Import the module directly from the file path
                module_path = mcp_servers_dir / f"{client_module_name}.py"
                if not module_path.exists():
                    logger.warning(f"Module file not found: {module_path}")
                    continue
                
                # Add the mcp_servers directory to sys.path temporarily
                original_path = sys.path.copy()
                sys.path.insert(0, str(mcp_servers_dir))
                
                try:
                    client_module = importlib.import_module(client_module_name)
                    
                    # Check if the module has a get_tools function
                    if hasattr(client_module, "get_tools"):
                        get_tools_func = client_module.get_tools
                        
                        # Check if it's an async function
                        if asyncio.iscoroutinefunction(get_tools_func):
                            new_tools = await get_tools_func()
                        else:
                            new_tools = get_tools_func()
                        
                        if new_tools and isinstance(new_tools, dict):
                            # Add module prefix to tool names to avoid conflicts
                            module_prefix = client_module_name
                            for tool_name, tool_func in new_tools.items():
                                prefixed_name = f"{module_prefix}.{tool_name}"
                                self.tools[prefixed_name] = tool_func
                            
                            logger.info(f"Discovered {len(new_tools)} tools from {client_module_name}")
                        else:
                            logger.warning(f"No tools returned from {client_module_name}")
                    else:
                        logger.warning(f"No get_tools function found in {client_module_name}")
                        
                finally:
                    # Restore original sys.path
                    sys.path = original_path
                    
            except ImportError as e:
                logger.warning(f"Could not import MCP client {client_module_name}: {e}")
                logger.info(f"This is expected if MCP is not installed or servers are not running")
            except Exception as e:
                logger.error(f"Error discovering tools from {client_module_name}: {e}")

    def get_tools(self) -> Dict[str, Callable]:
        """
        Returns the dictionary of available tools.
        """
        return self.tools

    def get_tools_by_module(self, module_name: str) -> Dict[str, Callable]:
        """
        Returns tools from a specific module.
        """
        prefix = f"{module_name}."
        return {k: v for k, v in self.tools.items() if k.startswith(prefix)}

    def get_tool(self, tool_name: str) -> Callable:
        """
        Returns a specific tool by name.
        """
        return self.tools.get(tool_name)

async def main():
    """
    Main function to test the ToolRegistry.
    """
    registry = ToolRegistry()
    await registry.discover_tools()
    tools = registry.get_tools()
    print("Discovered tools:")
    for tool_name in tools:
        print(f"- {tool_name}")

if __name__ == "__main__":
    asyncio.run(main())
