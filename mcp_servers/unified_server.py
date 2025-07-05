#!/usr/bin/env python3
"""
Unified MCP Server for Salty
Exposes ALL tools through MCP protocol for true agentic architecture
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Sequence, Dict, List, Optional
from pathlib import Path
from datetime import datetime

# MCP imports
from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all clients
from mcp_servers.spotify_client import SpotifyClient
from mcp_servers.roku_client import RokuClient
from mcp_servers.tplink_direct import TPLinkDirectClient
from mcp_servers.rag_client import RAGMCPClient
from mcp_servers.saltybot_client import SaltyBotMCPClient
from mcp_servers.voice_client import VoiceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the server
server = FastMCP("unified-salty-server")

# Initialize all clients
spotify_client = SpotifyClient()
roku_client = RokuClient()
tplink_client = TPLinkDirectClient()
rag_client = RAGMCPClient()
saltybot_client = SaltyBotMCPClient()
voice_client = VoiceClient()

# ============================================================================
# SPOTIFY TOOLS
# ============================================================================

@server.tool()
async def spotify_play() -> str:
    """Start or resume Spotify playback"""
    try:
        result = await spotify_client.play_spotify()
        if result.get("error"):
            return f"🦜 Squawk! Error playing music: {result['error']}"
        return result.get("response", "🎵 Music is playing, matey!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def spotify_pause() -> str:
    """Pause Spotify playback"""
    try:
        result = await spotify_client.pause_spotify()
        if result.get("error"):
            return f"🦜 Squawk! Error pausing music: {result['error']}"
        return result.get("response", "🎵 Music paused, matey!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def spotify_next() -> str:
    """Skip to next track"""
    try:
        result = await spotify_client.next_track()
        if result.get("error"):
            return f"🦜 Squawk! Error skipping track: {result['error']}"
        return result.get("response", "🎵 Next track, matey!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def spotify_previous() -> str:
    """Go to previous track"""
    try:
        result = await spotify_client.previous_track()
        if result.get("error"):
            return f"🦜 Squawk! Error going to previous track: {result['error']}"
        return result.get("response", "🎵 Previous track, matey!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def spotify_set_volume(volume: int) -> str:
    """Set Spotify volume (0-100)"""
    try:
        result = await spotify_client.set_volume(volume)
        if result.get("error"):
            return f"🦜 Squawk! Error setting volume: {result['error']}"
        return result.get("response", f"🎵 Volume set to {volume}%, matey!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def spotify_play_playlist(playlist_id: str) -> str:
    """Play a specific Spotify playlist"""
    try:
        result = await spotify_client.play_playlist(playlist_id)
        if result.get("error"):
            return f"🦜 Squawk! Error playing playlist: {result['error']}"
        return result.get("response", "🎵 Playlist is playing, matey!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def spotify_get_status() -> str:
    """Get current Spotify playback status"""
    try:
        result = await spotify_client.get_playback_status()
        if result.get("error"):
            return f"🦜 Squawk! Error getting status: {result['error']}"
        return result.get("response", "🎵 Status retrieved, matey!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def spotify_get_playlists() -> str:
    """Get user's Spotify playlists"""
    try:
        result = await spotify_client.get_user_playlists()
        if result.get("error"):
            return f"🦜 Squawk! Error getting playlists: {result['error']}"
        return result.get("response", "🎵 Playlists retrieved, matey!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

# ============================================================================
# ROKU TOOLS
# ============================================================================

@server.tool()
async def roku_power_on() -> str:
    """Power on the Roku device"""
    try:
        result = await roku_client.power_on()
        if result.get("error"):
            return f"🦜 Squawk! Error powering on Roku: {result['error']}"
        return result.get("response", "🟢 Roku powered on!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def roku_power_off() -> str:
    """Power off the Roku device"""
    try:
        result = await roku_client.power_off()
        if result.get("error"):
            return f"🦜 Squawk! Error powering off Roku: {result['error']}"
        return result.get("response", "🔴 Roku powered off!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def roku_home() -> str:
    """Go to Roku home screen"""
    try:
        result = await roku_client.home()
        if result.get("error"):
            return f"🦜 Squawk! Error going home: {result['error']}"
        return result.get("response", "🏠 Roku home screen!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def roku_launch_app(app_name: str) -> str:
    """Launch a Roku app"""
    try:
        result = await roku_client.launch_app(app_name)
        if result.get("error"):
            return f"🦜 Squawk! Error launching app: {result['error']}"
        return result.get("response", f"📱 Launched {app_name}!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def roku_volume_up() -> str:
    """Increase Roku volume"""
    try:
        result = await roku_client.volume_up()
        if result.get("error"):
            return f"🦜 Squawk! Error increasing volume: {result['error']}"
        return result.get("response", "🔊 Volume up!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def roku_volume_down() -> str:
    """Decrease Roku volume"""
    try:
        result = await roku_client.volume_down()
        if result.get("error"):
            return f"🦜 Squawk! Error decreasing volume: {result['error']}"
        return result.get("response", "🔉 Volume down!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def roku_mute() -> str:
    """Mute/unmute Roku"""
    try:
        result = await roku_client.mute()
        if result.get("error"):
            return f"🦜 Squawk! Error muting: {result['error']}"
        return result.get("response", "🔇 Muted!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def roku_navigate(direction: str) -> str:
    """Navigate on Roku (up, down, left, right)"""
    try:
        result = await roku_client.navigate(direction)
        if result.get("error"):
            return f"🦜 Squawk! Error navigating: {result['error']}"
        return result.get("response", f"🎮 Navigated {direction}!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def roku_select() -> str:
    """Select on Roku"""
    try:
        result = await roku_client.select()
        if result.get("error"):
            return f"🦜 Squawk! Error selecting: {result['error']}"
        return result.get("response", "✅ Selected!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def roku_back() -> str:
    """Go back on Roku"""
    try:
        result = await roku_client.back()
        if result.get("error"):
            return f"🦜 Squawk! Error going back: {result['error']}"
        return result.get("response", "⬅️ Back!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def roku_get_status() -> str:
    """Get Roku device status"""
    try:
        result = await roku_client.get_device_status()
        if result.get("error"):
            return f"🦜 Squawk! Error getting status: {result['error']}"
        return result.get("response", "📺 Status retrieved!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

# ============================================================================
# TP-LINK TOOLS
# ============================================================================

@server.tool()
async def tplink_discover_devices() -> str:
    """Discover TP-Link devices on the network"""
    try:
        result = await tplink_client.discover_devices()
        if result.get("error"):
            return f"🦜 Squawk! Error discovering devices: {result['error']}"
        return result.get("response", "💡 Devices discovered!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def tplink_turn_on_lights() -> str:
    """Turn on all TP-Link lights"""
    try:
        result = await tplink_client.turn_on_lights()
        if result.get("error"):
            return f"🦜 Squawk! Error turning on lights: {result['error']}"
        return result.get("response", "💡 Lights turned on!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def tplink_turn_off_lights() -> str:
    """Turn off all TP-Link lights"""
    try:
        result = await tplink_client.turn_off_lights()
        if result.get("error"):
            return f"🦜 Squawk! Error turning off lights: {result['error']}"
        return result.get("response", "💡 Lights turned off!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def tplink_set_color(color: str) -> str:
    """Set TP-Link light color (e.g., 'red', 'blue', 'green')"""
    try:
        result = await tplink_client.set_color(color)
        if result.get("error"):
            return f"🦜 Squawk! Error setting color: {result['error']}"
        return result.get("response", f"🎨 Color set to {color}!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def tplink_set_brightness(brightness: int) -> str:
    """Set TP-Link light brightness (0-100)"""
    try:
        result = await tplink_client.set_brightness(brightness)
        if result.get("error"):
            return f"🦜 Squawk! Error setting brightness: {result['error']}"
        return result.get("response", f"💡 Brightness set to {brightness}%!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

# ============================================================================
# RAG TOOLS
# ============================================================================

@server.tool()
async def rag_query(query: str) -> str:
    """Query the RAG knowledge base"""
    try:
        result = await rag_client.query_documents(query)
        if result.get("error"):
            return f"🦜 Squawk! Error querying knowledge base: {result['error']}"
        return result.get("response", "📚 Knowledge retrieved!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def rag_add_document(content: str, metadata: str = "") -> str:
    """Add a document to the RAG knowledge base"""
    try:
        metadata_dict = json.loads(metadata) if metadata else {}
        result = await rag_client.add_document(content, metadata_dict)
        if result.get("error"):
            return f"🦜 Squawk! Error adding document: {result['error']}"
        return result.get("response", "📚 Document added!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def rag_list_documents() -> str:
    """List all documents in the RAG knowledge base"""
    try:
        result = await rag_client.list_documents()
        if result.get("error"):
            return f"🦜 Squawk! Error listing documents: {result['error']}"
        return result.get("response", "📚 Documents listed!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def rag_rebuild_database() -> str:
    """Rebuild the RAG database"""
    try:
        result = await rag_client.rebuild_database()
        if result.get("error"):
            return f"🦜 Squawk! Error rebuilding database: {result['error']}"
        return result.get("response", "📚 Database rebuilt!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

# ============================================================================
# VOICE TOOLS
# ============================================================================

@server.tool()
async def voice_speak_text(text: str) -> str:
    """Speak text using voice synthesis"""
    try:
        result = await voice_client.speak_text(text)
        if result.get("error"):
            return f"🦜 Squawk! Error speaking text: {result['error']}"
        return result.get("response", "🗣️ Text spoken!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def voice_play_ambient_sound(sound_name: str) -> str:
    """Play ambient sound"""
    try:
        result = await voice_client.play_ambient_sound(sound_name)
        if result.get("error"):
            return f"🦜 Squawk! Error playing ambient sound: {result['error']}"
        return result.get("response", f"🎵 Playing {sound_name}!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def voice_stop_all_audio() -> str:
    """Stop all audio playback"""
    try:
        result = await voice_client.stop_all_audio()
        if result.get("error"):
            return f"🦜 Squawk! Error stopping audio: {result['error']}"
        return result.get("response", "🔇 All audio stopped!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def voice_get_available_voices() -> str:
    """Get list of available voices"""
    try:
        result = await voice_client.get_available_voices()
        if result.get("error"):
            return f"🦜 Squawk! Error getting voices: {result['error']}"
        return result.get("response", "🗣️ Voices retrieved!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

# ============================================================================
# SALTYBOT TOOLS
# ============================================================================

@server.tool()
async def saltybot_chat(message: str) -> str:
    """Chat with Salty using the agentic core"""
    try:
        result = await saltybot_client.chat_with_salty(message)
        if result.get("error"):
            return f"🦜 Squawk! Error chatting: {result['error']}"
        return result.get("response", "🦜 Salty responded!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def saltybot_get_config() -> str:
    """Get Salty's current configuration"""
    try:
        result = await saltybot_client.get_salty_config()
        if result.get("error"):
            return f"🦜 Squawk! Error getting config: {result['error']}"
        return result.get("response", "⚙️ Config retrieved!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def saltybot_get_personality() -> str:
    """Get Salty's personality information"""
    try:
        result = await saltybot_client.get_salty_personality_info()
        if result.get("error"):
            return f"🦜 Squawk! Error getting personality: {result['error']}"
        return result.get("response", "🎭 Personality retrieved!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def saltybot_generate_story(theme: str = "tropical") -> str:
    """Generate a tiki-themed story"""
    try:
        result = await saltybot_client.generate_tiki_story(theme)
        if result.get("error"):
            return f"🦜 Squawk! Error generating story: {result['error']}"
        return result.get("response", "📖 Story generated!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def saltybot_recommend_drink(preferences: str = "classic") -> str:
    """Recommend a tropical drink"""
    try:
        result = await saltybot_client.recommend_drink(preferences)
        if result.get("error"):
            return f"🦜 Squawk! Error recommending drink: {result['error']}"
        return result.get("response", "🍹 Drink recommended!")
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

# ============================================================================
# SYSTEM TOOLS
# ============================================================================

@server.tool()
async def system_get_time() -> str:
    """Get current system time"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"🕐 Current time: {current_time}"
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def system_get_status() -> str:
    """Get system status and health"""
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = f"🖥️ System Status:\n"
        status += f"CPU: {cpu_percent}%\n"
        status += f"Memory: {memory.percent}%\n"
        status += f"Disk: {disk.percent}%\n"
        
        return status
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

@server.tool()
async def system_log_message(message: str, level: str = "info") -> str:
    """Log a message to the system log"""
    try:
        logger.log(
            getattr(logging, level.upper(), logging.INFO),
            f"User log: {message}"
        )
        return f"📝 Message logged: {message}"
    except Exception as e:
        return f"🦜 Squawk! Error: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    asyncio.run(stdio_server(server)) 