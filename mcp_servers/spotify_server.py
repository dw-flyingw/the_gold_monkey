#!/usr/bin/env python3
"""
Spotify MCP Server for Salty
Provides Spotify playback control via MCP protocol
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pathlib import Path

# MCP imports
from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool
)

# Load environment variables
load_dotenv()

# Ensure logs directory exists
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / 'spotify_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Spotify configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_SCOPE = os.getenv('SPOTIFY_SCOPE', 'user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative')

# Initialize Spotify client
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    ))
    logger.info("Spotify client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Spotify client: {e}", exc_info=True)
    sp = None

# Create MCP server
server = FastMCP("spotify")

@server.tool()
async def play_spotify() -> str:
    """Start or resume Spotify playback"""
    try:
        if not sp:
            return "🦜 Squawk! Spotify isn't configured, matey!"
        
        sp.start_playback()
        return "🎵 Squawk! Music is playing, matey!"
    except Exception as e:
        logger.error(f"Error playing Spotify: {e}", exc_info=True)
        return f"🦜 Squawk! Error playing music: {str(e)}"

@server.tool()
async def pause_spotify() -> str:
    """Pause Spotify playback"""
    try:
        if not sp:
            return "🦜 Squawk! Spotify isn't configured, matey!"
        
        sp.pause_playback()
        return "🎵 Squawk! Music paused, matey!"
    except Exception as e:
        logger.error(f"Error pausing Spotify: {e}", exc_info=True)
        return f"🦜 Squawk! Error pausing music: {str(e)}"

@server.tool()
async def next_track() -> str:
    """Skip to next track"""
    try:
        if not sp:
            return "🦜 Squawk! Spotify isn't configured, matey!"
        
        sp.next_track()
        return "🎵 Squawk! Next track, matey!"
    except Exception as e:
        logger.error(f"Error skipping track: {e}", exc_info=True)
        return f"🦜 Squawk! Error skipping track: {str(e)}"

@server.tool()
async def previous_track() -> str:
    """Go to previous track"""
    try:
        if not sp:
            return "🦜 Squawk! Spotify isn't configured, matey!"
        
        sp.previous_track()
        return "🎵 Squawk! Previous track, matey!"
    except Exception as e:
        logger.error(f"Error going to previous track: {e}", exc_info=True)
        return f"🦜 Squawk! Error going to previous track: {str(e)}"

@server.tool()
async def set_volume(volume: int) -> str:
    """Set playback volume (0-100)"""
    try:
        if not sp:
            return "🦜 Squawk! Spotify isn't configured, matey!"
        
        # Ensure volume is within valid range
        volume = max(0, min(100, volume))
        sp.volume(volume)
        return f"🔊 Squawk! Volume set to {volume}%, matey!"
    except Exception as e:
        logger.error(f"Error setting volume: {e}", exc_info=True)
        return f"🦜 Squawk! Error setting volume: {str(e)}"

@server.tool()
async def play_playlist(playlist_id: str) -> str:
    """Play a specific Spotify playlist"""
    try:
        if not sp:
            return "🦜 Squawk! Spotify isn't configured, matey!"
        
        if not playlist_id:
            return "🦜 Squawk! Playlist ID is required, matey!"
        
        sp.start_playback(context_uri=f"spotify:playlist:{playlist_id}")
        return f"🎵 Squawk! Playing playlist {playlist_id}, matey!"
    except Exception as e:
        logger.error(f"Error playing playlist: {e}", exc_info=True)
        return f"🦜 Squawk! Error playing playlist: {str(e)}"

@server.tool()
async def play_track(track_id: str) -> str:
    """Play a specific Spotify track"""
    try:
        if not sp:
            return "🦜 Squawk! Spotify isn't configured, matey!"
        
        if not track_id:
            return "🦜 Squawk! Track ID is required, matey!"
        
        sp.start_playback(uris=[f"spotify:track:{track_id}"])
        return f"🎵 Squawk! Playing track {track_id}, matey!"
    except Exception as e:
        logger.error(f"Error playing track: {e}", exc_info=True)
        return f"🦜 Squawk! Error playing track: {str(e)}"

@server.tool()
async def get_playback_status() -> str:
    """Get current playback status and track information"""
    try:
        if not sp:
            return "🦜 Squawk! Spotify isn't configured, matey!"
        
        current = sp.current_playback()
        
        if not current:
            return "🎵 Squawk! Nothing is currently playing, matey!"
        
        # Extract track information
        track = current.get('item', {})
        track_name = track.get('name', 'Unknown Track')
        artists = [artist['name'] for artist in track.get('artists', [])]
        artist_names = ', '.join(artists) if artists else 'Unknown Artist'
        album = track.get('album', {}).get('name', 'Unknown Album')
        
        # Extract playback information
        is_playing = current.get('is_playing', False)
        progress_ms = current.get('progress_ms', 0)
        duration_ms = track.get('duration_ms', 0)
        
        # Calculate progress percentage
        progress_pct = (progress_ms / duration_ms * 100) if duration_ms > 0 else 0
        
        # Format status
        status_text = f"🎵 **Current Playback Status**\n\n"
        status_text += f"**Track:** {track_name}\n"
        status_text += f"**Artist:** {artist_names}\n"
        status_text += f"**Album:** {album}\n"
        status_text += f"**Status:** {'🟢 Playing' if is_playing else '⏸️ Paused'}\n"
        status_text += f"**Progress:** {progress_pct:.1f}% ({progress_ms//1000}s / {duration_ms//1000}s)\n"
        
        return status_text
        
    except Exception as e:
        logger.error(f"Error getting playback status: {e}", exc_info=True)
        return f"🦜 Squawk! Error getting playback status: {str(e)}"

@server.tool()
async def get_playlist_info(playlist_id: str) -> str:
    """Get information about a Spotify playlist"""
    try:
        if not sp:
            return "🦜 Squawk! Spotify isn't configured, matey!"
        
        if not playlist_id:
            return "🦜 Squawk! Playlist ID is required, matey!"
        
        playlist = sp.playlist(playlist_id)
        
        if not playlist:
            return f"🦜 Squawk! Playlist {playlist_id} not found, matey!"
        
        # Extract playlist information
        name = playlist.get('name', 'Unknown Playlist')
        description = playlist.get('description', 'No description')
        owner = playlist.get('owner', {}).get('display_name', 'Unknown Owner')
        tracks_total = playlist.get('tracks', {}).get('total', 0)
        public = playlist.get('public', False)
        
        # Format playlist info
        info_text = f"📋 **Playlist Information**\n\n"
        info_text += f"**Name:** {name}\n"
        info_text += f"**Owner:** {owner}\n"
        info_text += f"**Tracks:** {tracks_total}\n"
        info_text += f"**Public:** {'Yes' if public else 'No'}\n"
        info_text += f"**Description:** {description}\n"
        
        return info_text
        
    except Exception as e:
        logger.error(f"Error getting playlist info: {e}", exc_info=True)
        return f"🦜 Squawk! Error getting playlist info: {str(e)}"

if __name__ == "__main__":
    server.run() 