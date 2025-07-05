#!/usr/bin/env python3
"""
Dynamic Tool Discovery System
Discovers and registers tools at runtime for true agentic architecture
"""

import asyncio
import importlib
import inspect
import logging
import os
import sys
from typing import Dict, Any, List, Callable, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ToolMetadata:
    name: str
    description: str
    category: str
    parameters: Dict[str, Any]
    return_type: str
    discovered_at: datetime
    success_rate: float = 0.5
    usage_count: int = 0

class DynamicToolDiscovery:
    """Discovers and manages tools dynamically"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, ToolMetadata] = {}
        self.discovery_paths: List[Path] = []
        self.watchers: List[Callable] = []
    
    def add_discovery_path(self, path: Path):
        """Add a path to search for tools"""
        self.discovery_paths.append(path)
    
    def add_watcher(self, callback: Callable):
        """Add a callback to be called when tools are discovered"""
        self.watchers.append(callback)
    
    async def discover_tools(self) -> Dict[str, Callable]:
        """Discover all available tools"""
        discovered_tools = {}
        
        for path in self.discovery_paths:
            tools = await self._discover_tools_in_path(path)
            discovered_tools.update(tools)
        
        # Update tools and notify watchers
        self.tools.update(discovered_tools)
        for watcher in self.watchers:
            try:
                watcher(discovered_tools)
            except Exception as e:
                logger.error(f"Error in tool discovery watcher: {e}")
        
        return discovered_tools
    
    async def _discover_tools_in_path(self, path: Path) -> Dict[str, Callable]:
        """Discover tools in a specific path"""
        tools = {}
        
        if not path.exists():
            return tools
        
        # Look for Python files
        for py_file in path.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            try:
                # Import the module
                module_name = str(py_file.relative_to(path.parent)).replace("/", ".").replace(".py", "")
                module = importlib.import_module(module_name)
                
                # Look for functions with tool decorators or specific patterns
                for name, obj in inspect.getmembers(module):
                    if self._is_tool_function(obj):
                        tool_name = f"{module_name}.{name}"
                        tools[tool_name] = obj
                        
                        # Create metadata
                        metadata = self._create_tool_metadata(obj, tool_name)
                        self.tool_metadata[tool_name] = metadata
                        
                        logger.info(f"Discovered tool: {tool_name}")
                
            except Exception as e:
                logger.error(f"Error discovering tools in {py_file}: {e}")
        
        return tools
    
    def _is_tool_function(self, obj) -> bool:
        """Check if an object is a tool function"""
        if not callable(obj):
            return False
        
        # Check for common tool patterns
        name = getattr(obj, "__name__", "")
        if name.startswith("_"):
            return False
        
        # Check if it's an async function
        if not asyncio.iscoroutinefunction(obj):
            return False
        
        # Check for tool decorators or specific naming patterns
        if hasattr(obj, "__tool__"):
            return True
        
        # Check for common tool naming patterns
        tool_patterns = [
            "play_", "pause_", "stop_", "start_", "turn_on_", "turn_off_",
            "set_", "get_", "query_", "search_", "speak_", "voice_",
            "light_", "music_", "tv_", "roku_", "spotify_", "tplink_"
        ]
        
        return any(pattern in name.lower() for pattern in tool_patterns)
    
    def _create_tool_metadata(self, func: Callable, tool_name: str) -> ToolMetadata:
        """Create metadata for a tool function"""
        sig = inspect.signature(func)
        parameters = {}
        
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            
            param_info = {
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                "default": param.default if param.default != inspect.Parameter.empty else None,
                "required": param.default == inspect.Parameter.empty
            }
            parameters[name] = param_info
        
        return ToolMetadata(
            name=tool_name,
            description=func.__doc__ or f"Tool {tool_name}",
            category=self._categorize_tool(tool_name),
            parameters=parameters,
            return_type=str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "Any",
            discovered_at=datetime.now()
        )
    
    def _categorize_tool(self, tool_name: str) -> str:
        """Categorize a tool based on its name"""
        tool_name_lower = tool_name.lower()
        
        if any(word in tool_name_lower for word in ["spotify", "music", "play", "track"]):
            return "media"
        elif any(word in tool_name_lower for word in ["light", "tplink", "bulb"]):
            return "lighting"
        elif any(word in tool_name_lower for word in ["rag", "query", "search"]):
            return "information"
        elif any(word in tool_name_lower for word in ["voice", "speak", "tts"]):
            return "voice"
        elif any(word in tool_name_lower for word in ["roku", "tv", "app"]):
            return "entertainment"
        else:
            return "automation"
    
    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool"""
        return self.tool_metadata.get(tool_name)
    
    def get_tools_by_category(self, category: str) -> Dict[str, Callable]:
        """Get tools by category"""
        return {
            name: tool for name, tool in self.tools.items()
            if self.tool_metadata.get(name, ToolMetadata("", "", "", {}, "", datetime.now())).category == category
        }
    
    def update_tool_usage(self, tool_name: str, success: bool):
        """Update tool usage statistics"""
        if tool_name in self.tool_metadata:
            metadata = self.tool_metadata[tool_name]
            metadata.usage_count += 1
            
            # Update success rate
            if metadata.usage_count == 1:
                metadata.success_rate = 1.0 if success else 0.0
            else:
                # Simple moving average
                current_success = 1.0 if success else 0.0
                metadata.success_rate = (metadata.success_rate * (metadata.usage_count - 1) + current_success) / metadata.usage_count
    
    def get_best_tools_for_task(self, task_description: str, category: str = None) -> List[str]:
        """Get the best tools for a specific task"""
        candidates = []
        
        for tool_name, metadata in self.tool_metadata.items():
            if category and metadata.category != category:
                continue
            
            # Simple scoring based on success rate and usage
            score = metadata.success_rate * (1 + metadata.usage_count * 0.1)
            candidates.append((tool_name, score))
        
        # Sort by score and return top tools
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [tool_name for tool_name, score in candidates[:5]]
    
    async def monitor_for_changes(self):
        """Monitor for changes in tool files and rediscover"""
        while True:
            try:
                # Check for file modifications
                for path in self.discovery_paths:
                    if self._has_changes(path):
                        logger.info(f"Changes detected in {path}, rediscovering tools...")
                        await self.discover_tools()
                        break
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in tool monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def _has_changes(self, path: Path) -> bool:
        """Check if there are changes in the path"""
        # Simple implementation - could be enhanced with file watching
        return False  # Placeholder

class ToolRegistry:
    """Registry for managing tool discovery and registration"""
    
    def __init__(self):
        self.discovery = DynamicToolDiscovery()
        self.registered_tools: Dict[str, Callable] = {}
    
    def register_tool(self, name: str, func: Callable):
        """Register a tool manually"""
        self.registered_tools[name] = func
    
    async def discover_and_register(self):
        """Discover and register all tools"""
        discovered_tools = await self.discovery.discover_tools()
        self.registered_tools.update(discovered_tools)
        return self.registered_tools
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a specific tool"""
        return self.registered_tools.get(name)
    
    def get_tools_by_category(self, category: str) -> Dict[str, Callable]:
        """Get tools by category"""
        return self.discovery.get_tools_by_category(category)
    
    def get_best_tools_for_task(self, task_description: str, category: str = None) -> List[str]:
        """Get the best tools for a task"""
        return self.discovery.get_best_tools_for_task(task_description, category)

# Global tool registry instance
tool_registry = ToolRegistry()

# Add default discovery paths
tool_registry.discovery.add_discovery_path(Path("mcp_servers"))
tool_registry.discovery.add_discovery_path(Path("utils"))

async def discover_all_tools():
    """Discover all available tools"""
    return await tool_registry.discover_and_register()

def register_tool(name: str, func: Callable):
    """Register a tool"""
    tool_registry.register_tool(name, func)

def get_tool(name: str) -> Optional[Callable]:
    """Get a specific tool"""
    return tool_registry.get_tool(name)

def get_tools_by_category(category: str) -> Dict[str, Callable]:
    """Get tools by category"""
    return tool_registry.get_tools_by_category(category)

async def main():
    """Test the dynamic tool discovery"""
    print("🔍 Discovering tools...")
    tools = await discover_all_tools()
    
    print(f"✅ Discovered {len(tools)} tools:")
    for name in tools:
        print(f"  • {name}")
    
    # Test categorization
    categories = ["media", "lighting", "information", "voice", "entertainment", "automation"]
    for category in categories:
        category_tools = get_tools_by_category(category)
        if category_tools:
            print(f"\n📂 {category.title()} tools:")
            for name in category_tools:
                print(f"  • {name}")

if __name__ == "__main__":
    asyncio.run(main()) 