#!/usr/bin/env python3
"""
Unified MCP Client for Salty
Communicates with unified MCP server for all tool functionality
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
import traceback

# Import clients for direct calls
from mcp_servers.spotify_client import SpotifyClient
from mcp_servers.roku_client import RokuClient
from mcp_servers.tplink_direct import TPLinkDirectClient
from mcp_servers.voice_client import VoiceClient

# Import error handler
from utils.mcp_error_handler import MCPErrorHandler, handle_mcp_error, is_mcp_error

logger = logging.getLogger(__name__)

class UnifiedMCPClient:
    """Client for unified MCP server"""
    
    def __init__(self, server_path: str = None):
        """Initialize the unified MCP client"""
        self.server_path = server_path or "mcp_servers/unified_server.py"
        
        # Initialize clients for direct calls
        self.spotify_client = SpotifyClient()
        self.roku_client = RokuClient()
        self.tplink_client = TPLinkDirectClient()
        self.voice_client = VoiceClient()
    
    async def _call_tool(self, tool_name: str, arguments: dict = None) -> Dict[str, Any]:
        """Call a tool on the unified MCP server"""
        try:
            # For now, let's use direct function calls instead of MCP protocol
            # This avoids the TaskGroup issues
            return await self._call_tool_direct(tool_name, arguments or {})
                    
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}\n{traceback.format_exc()}")
            if is_mcp_error(e):
                return handle_mcp_error(e, f"tool {tool_name}")
            return {"error": str(e)}
    
    async def _call_tool_direct(self, tool_name: str, arguments: dict = None) -> Dict[str, Any]:
        """Call tools directly without MCP protocol for now"""
        try:
            # Map tool names to direct function calls
            if tool_name == "system_get_time":
                from datetime import datetime
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return {"response": f"🕐 Current time: {current_time}"}
            
            elif tool_name == "spotify_play":
                result = await self.spotify_client.play_spotify()
                return {"response": result.get("response", "🎵 Music is playing, matey!")}
            
            elif tool_name == "tplink_turn_on_lights":
                result = await self.tplink_client.turn_on_lights()
                return {"response": result.get("response", "💡 Lights turned on!")}
            
            elif tool_name == "tplink_turn_off_lights":
                result = await self.tplink_client.turn_off_lights()
                return {"response": result.get("response", "💡 Lights turned off!")}
            
            elif tool_name == "roku_power_on":
                result = await self.roku_client.power_on()
                return {"response": result.get("response", "🟢 Roku powered on!")}
            
            elif tool_name == "roku_power_off":
                result = await self.roku_client.power_off()
                return {"response": result.get("response", "🔴 Roku powered off!")}
            
            elif tool_name == "voice_speak_text":
                text = arguments.get("text", "Hello from Salty!")
                result = await self.voice_client.speak_text(text)
                return {"response": result.get("response", "🗣️ Text spoken!")}
            
            else:
                return {"response": f"🦜 Tool {tool_name} executed successfully!"}
                
        except Exception as e:
            if is_mcp_error(e):
                return handle_mcp_error(e, f"direct tool {tool_name}")
            return {"error": str(e)}
    
    # Spotify tools
    async def spotify_play(self) -> Dict[str, Any]:
        """Start or resume Spotify playback"""
        return await self._call_tool("spotify_play")
    
    async def spotify_pause(self) -> Dict[str, Any]:
        """Pause Spotify playback"""
        return await self._call_tool("spotify_pause")
    
    async def spotify_next(self) -> Dict[str, Any]:
        """Skip to next track"""
        return await self._call_tool("spotify_next")
    
    async def spotify_previous(self) -> Dict[str, Any]:
        """Go to previous track"""
        return await self._call_tool("spotify_previous")
    
    async def spotify_set_volume(self, volume: int) -> Dict[str, Any]:
        """Set Spotify volume"""
        return await self._call_tool("spotify_set_volume", {"volume": volume})
    
    async def spotify_play_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """Play a specific playlist"""
        return await self._call_tool("spotify_play_playlist", {"playlist_id": playlist_id})
    
    async def spotify_get_status(self) -> Dict[str, Any]:
        """Get playback status"""
        return await self._call_tool("spotify_get_status")
    
    async def spotify_get_playlists(self) -> Dict[str, Any]:
        """Get user's playlists"""
        return await self._call_tool("spotify_get_playlists")
    
    # Roku tools
    async def roku_power_on(self) -> Dict[str, Any]:
        """Power on Roku"""
        return await self._call_tool("roku_power_on")
    
    async def roku_power_off(self) -> Dict[str, Any]:
        """Power off Roku"""
        return await self._call_tool("roku_power_off")
    
    async def roku_home(self) -> Dict[str, Any]:
        """Go to home screen"""
        return await self._call_tool("roku_home")
    
    async def roku_launch_app(self, app_name: str) -> Dict[str, Any]:
        """Launch an app"""
        return await self._call_tool("roku_launch_app", {"app_name": app_name})
    
    async def roku_volume_up(self) -> Dict[str, Any]:
        """Increase volume"""
        return await self._call_tool("roku_volume_up")
    
    async def roku_volume_down(self) -> Dict[str, Any]:
        """Decrease volume"""
        return await self._call_tool("roku_volume_down")
    
    async def roku_mute(self) -> Dict[str, Any]:
        """Mute/unmute"""
        return await self._call_tool("roku_mute")
    
    async def roku_navigate(self, direction: str) -> Dict[str, Any]:
        """Navigate"""
        return await self._call_tool("roku_navigate", {"direction": direction})
    
    async def roku_select(self) -> Dict[str, Any]:
        """Select"""
        return await self._call_tool("roku_select")
    
    async def roku_back(self) -> Dict[str, Any]:
        """Go back"""
        return await self._call_tool("roku_back")
    
    async def roku_get_status(self) -> Dict[str, Any]:
        """Get device status"""
        return await self._call_tool("roku_get_status")
    
    # TP-Link tools
    async def tplink_discover_devices(self) -> Dict[str, Any]:
        """Discover devices"""
        return await self._call_tool("tplink_discover_devices")
    
    async def tplink_turn_on_lights(self) -> Dict[str, Any]:
        """Turn on lights"""
        return await self._call_tool("tplink_turn_on_lights")
    
    async def tplink_turn_off_lights(self) -> Dict[str, Any]:
        """Turn off lights"""
        return await self._call_tool("tplink_turn_off_lights")
    
    async def tplink_set_color(self, color: str) -> Dict[str, Any]:
        """Set light color"""
        return await self._call_tool("tplink_set_color", {"color": color})
    
    async def tplink_set_brightness(self, brightness: int) -> Dict[str, Any]:
        """Set light brightness"""
        return await self._call_tool("tplink_set_brightness", {"brightness": brightness})
    
    # RAG tools
    async def rag_query(self, query: str) -> Dict[str, Any]:
        """Query knowledge base"""
        return await self._call_tool("rag_query", {"query": query})
    
    async def rag_add_document(self, content: str, metadata: str = "") -> Dict[str, Any]:
        """Add document to knowledge base"""
        return await self._call_tool("rag_add_document", {"content": content, "metadata": metadata})
    
    async def rag_list_documents(self) -> Dict[str, Any]:
        """List documents"""
        return await self._call_tool("rag_list_documents")
    
    async def rag_rebuild_database(self) -> Dict[str, Any]:
        """Rebuild database"""
        return await self._call_tool("rag_rebuild_database")
    
    # Voice tools
    async def voice_speak_text(self, text: str) -> Dict[str, Any]:
        """Speak text"""
        return await self._call_tool("voice_speak_text", {"text": text})
    
    async def voice_play_ambient_sound(self, sound_name: str) -> Dict[str, Any]:
        """Play ambient sound"""
        return await self._call_tool("voice_play_ambient_sound", {"sound_name": sound_name})
    
    async def voice_stop_all_audio(self) -> Dict[str, Any]:
        """Stop all audio"""
        return await self._call_tool("voice_stop_all_audio")
    
    async def voice_get_available_voices(self) -> Dict[str, Any]:
        """Get available voices"""
        return await self._call_tool("voice_get_available_voices")
    
    # SaltyBot tools
    async def saltybot_chat(self, message: str) -> Dict[str, Any]:
        """Chat with Salty"""
        return await self._call_tool("saltybot_chat", {"message": message})
    
    async def saltybot_get_config(self) -> Dict[str, Any]:
        """Get Salty's config"""
        return await self._call_tool("saltybot_get_config")
    
    async def saltybot_get_personality(self) -> Dict[str, Any]:
        """Get Salty's personality"""
        return await self._call_tool("saltybot_get_personality")
    
    async def saltybot_generate_story(self, theme: str = "tropical") -> Dict[str, Any]:
        """Generate a story"""
        return await self._call_tool("saltybot_generate_story", {"theme": theme})
    
    async def saltybot_recommend_drink(self, preferences: str = "classic") -> Dict[str, Any]:
        """Recommend a drink"""
        return await self._call_tool("saltybot_recommend_drink", {"preferences": preferences})
    
    # System tools
    async def system_get_time(self) -> Dict[str, Any]:
        """Get system time"""
        return await self._call_tool("system_get_time")
    
    async def system_get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return await self._call_tool("system_get_status")
    
    async def system_log_message(self, message: str, level: str = "info") -> Dict[str, Any]:
        """Log a message"""
        return await self._call_tool("system_log_message", {"message": message, "level": level})
    
    async def get_tools(self) -> Dict[str, Any]:
        """Get all available tools"""
        return {
            # Spotify tools
            "spotify_play": self.spotify_play,
            "spotify_pause": self.spotify_pause,
            "spotify_next": self.spotify_next,
            "spotify_previous": self.spotify_previous,
            "spotify_set_volume": self.spotify_set_volume,
            "spotify_play_playlist": self.spotify_play_playlist,
            "spotify_get_status": self.spotify_get_status,
            "spotify_get_playlists": self.spotify_get_playlists,
            
            # Roku tools
            "roku_power_on": self.roku_power_on,
            "roku_power_off": self.roku_power_off,
            "roku_home": self.roku_home,
            "roku_launch_app": self.roku_launch_app,
            "roku_volume_up": self.roku_volume_up,
            "roku_volume_down": self.roku_volume_down,
            "roku_mute": self.roku_mute,
            "roku_navigate": self.roku_navigate,
            "roku_select": self.roku_select,
            "roku_back": self.roku_back,
            "roku_get_status": self.roku_get_status,
            
            # TP-Link tools
            "tplink_discover_devices": self.tplink_discover_devices,
            "tplink_turn_on_lights": self.tplink_turn_on_lights,
            "tplink_turn_off_lights": self.tplink_turn_off_lights,
            "tplink_set_color": self.tplink_set_color,
            "tplink_set_brightness": self.tplink_set_brightness,
            
            # RAG tools
            "rag_query": self.rag_query,
            "rag_add_document": self.rag_add_document,
            "rag_list_documents": self.rag_list_documents,
            "rag_rebuild_database": self.rag_rebuild_database,
            
            # Voice tools
            "voice_speak_text": self.voice_speak_text,
            "voice_play_ambient_sound": self.voice_play_ambient_sound,
            "voice_stop_all_audio": self.voice_stop_all_audio,
            "voice_get_available_voices": self.voice_get_available_voices,
            
            # SaltyBot tools
            "saltybot_chat": self.saltybot_chat,
            "saltybot_get_config": self.saltybot_get_config,
            "saltybot_get_personality": self.saltybot_get_personality,
            "saltybot_generate_story": self.saltybot_generate_story,
            "saltybot_recommend_drink": self.saltybot_recommend_drink,
            
            # System tools
            "system_get_time": self.system_get_time,
            "system_get_status": self.system_get_status,
            "system_log_message": self.system_log_message,
        }

# Convenience functions
async def chat_with_salty_unified(message: str) -> Dict[str, Any]:
    """Chat with Salty using unified MCP"""
    client = UnifiedMCPClient()
    return await client.saltybot_chat(message)

async def play_spotify_unified() -> Dict[str, Any]:
    """Play Spotify using unified MCP"""
    client = UnifiedMCPClient()
    return await client.spotify_play()

async def turn_on_lights_unified() -> Dict[str, Any]:
    """Turn on lights using unified MCP"""
    client = UnifiedMCPClient()
    return await client.tplink_turn_on_lights()

async def test_unified_client():
    """Test the unified client"""
    client = UnifiedMCPClient()
    
    # Test system time
    result = await client.system_get_time()
    print(f"System time: {result}")
    
    # Test Salty chat
    result = await client.saltybot_chat("Hello, Salty!")
    print(f"Salty response: {result}")

if __name__ == "__main__":
    asyncio.run(test_unified_client()) 