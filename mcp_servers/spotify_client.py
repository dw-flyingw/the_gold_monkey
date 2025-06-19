#!/usr/bin/env python3
"""
Direct Spotify Client for Salty
Provides Spotify playback control without MCP dependencies
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
        logging.FileHandler(LOGS_DIR / 'spotify_client.log')
    ]
)
logger = logging.getLogger(__name__)

# Spotify configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_SCOPE = os.getenv('SPOTIFY_SCOPE', 'user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative')
SPOTIFY_DEFAULT_SPEAKER = os.getenv('SPOTIFY_SPEAKER', 'Tiki Lounge')
SPOTIFY_DEFAULT_VOLUME = os.getenv('SPOTIFY_VOLUME', '50%').replace('%', '')

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

class SpotifyClient:
    """Direct Spotify client without MCP dependencies"""
    
    def __init__(self):
        """Initialize the Spotify client"""
        self.sp = sp
    
    async def _find_and_transfer_to_default_speaker(self) -> bool:
        """Find the default speaker and transfer playback to it"""
        try:
            if not self.sp:
                return False
            
            # Get all available devices
            devices = self.sp.devices()
            if not devices['devices']:
                logger.warning("No Spotify devices found")
                return False
            
            # Look for the default speaker
            default_device = None
            for device in devices['devices']:
                if SPOTIFY_DEFAULT_SPEAKER.lower() in device['name'].lower():
                    default_device = device
                    break
            
            if not default_device:
                logger.warning(f"Default speaker '{SPOTIFY_DEFAULT_SPEAKER}' not found. Available devices: {[d['name'] for d in devices['devices']]}")
                # Use the first available device as fallback
                default_device = devices['devices'][0]
                logger.info(f"Using fallback device: {default_device['name']}")
            
            # Transfer playback to the default device
            self.sp.transfer_playback(device_id=default_device['id'], force_play=False)
            logger.info(f"Transferred playback to: {default_device['name']}")
            
            # Wait a moment for the transfer to complete
            await asyncio.sleep(2)
            
            # Verify the device is now active
            devices_after = self.sp.devices()
            for device in devices_after['devices']:
                if device['id'] == default_device['id'] and device.get('is_active', False):
                    logger.info(f"Device {default_device['name']} is now active")
                    return True
            
            logger.warning(f"Device {default_device['name']} transfer completed but not yet active")
            return True  # Return True anyway, the device might become active shortly
            
        except Exception as e:
            logger.error(f"Error transferring to default speaker: {e}", exc_info=True)
            return False

    async def play_spotify(self) -> Dict[str, Any]:
        """Start or resume Spotify playback"""
        try:
            if not self.sp:
                return {"error": "Spotify client not initialized"}
            
            # Check for active devices
            devices = self.sp.devices()
            if not devices['devices']:
                return {"error": "No Spotify devices found. Please open Spotify on a device."}
            
            # Try to start playback
            try:
                self.sp.start_playback()
                return {"response": "🎵 Squawk! Music is playing, matey!"}
            except Exception as e:
                if "NO_ACTIVE_DEVICE" in str(e):
                    # No active device, try to transfer to default speaker
                    logger.info("No active device found, transferring to default speaker...")
                    if await self._find_and_transfer_to_default_speaker():
                        # Wait a bit more for the device to become fully active
                        await asyncio.sleep(3)
                        
                        # Try starting playback again with retries
                        for attempt in range(3):
                            try:
                                self.sp.start_playback()
                                return {"response": f"🎵 Squawk! Music is playing on {SPOTIFY_DEFAULT_SPEAKER}, matey!"}
                            except Exception as e2:
                                if "NO_ACTIVE_DEVICE" in str(e2) and attempt < 2:
                                    logger.info(f"Retry {attempt + 1}/3: Device not ready yet, waiting...")
                                    await asyncio.sleep(2)
                                else:
                                    return {"error": f"Error starting playback after device transfer: {str(e2)}"}
                    else:
                        return {"error": f"No active device found and couldn't transfer to {SPOTIFY_DEFAULT_SPEAKER}. Please open Spotify on a device."}
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Error playing Spotify: {e}", exc_info=True)
            return {"error": f"Error playing music: {str(e)}"}
    
    async def pause_spotify(self) -> Dict[str, Any]:
        """Pause Spotify playback"""
        try:
            if not self.sp:
                return {"error": "Spotify client not initialized"}
            
            self.sp.pause_playback()
            return {"response": "🎵 Squawk! Music paused, matey!"}
        except Exception as e:
            logger.error(f"Error pausing Spotify: {e}", exc_info=True)
            return {"error": f"Error pausing music: {str(e)}"}
    
    async def next_track(self) -> Dict[str, Any]:
        """Skip to next track"""
        try:
            if not self.sp:
                return {"error": "Spotify client not initialized"}
            
            self.sp.next_track()
            return {"response": "🎵 Squawk! Next track, matey!"}
        except Exception as e:
            logger.error(f"Error skipping track: {e}", exc_info=True)
            return {"error": f"Error skipping track: {str(e)}"}
    
    async def previous_track(self) -> Dict[str, Any]:
        """Go to previous track"""
        try:
            if not self.sp:
                return {"error": "Spotify client not initialized"}
            
            self.sp.previous_track()
            return {"response": "🎵 Squawk! Previous track, matey!"}
        except Exception as e:
            logger.error(f"Error going to previous track: {e}", exc_info=True)
            return {"error": f"Error going to previous track: {str(e)}"}
    
    async def set_volume(self, volume: int) -> Dict[str, Any]:
        """Set playback volume"""
        try:
            if not self.sp:
                return {"error": "Spotify client not initialized"}
            
            # Ensure volume is between 0 and 100
            volume = max(0, min(100, volume))
            self.sp.volume(volume)
            return {"response": f"🎵 Squawk! Volume set to {volume}%, matey!"}
        except Exception as e:
            logger.error(f"Error setting volume: {e}", exc_info=True)
            return {"error": f"Error setting volume: {str(e)}"}
    
    async def play_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """Play a specific playlist"""
        try:
            if not self.sp:
                return {"error": "Spotify client not initialized"}
            
            if not playlist_id:
                return {"error": "Playlist ID is required"}
            
            self.sp.start_playback(context_uri=f"spotify:playlist:{playlist_id}")
            return {"response": f"🎵 Squawk! Playing playlist {playlist_id}, matey!"}
        except Exception as e:
            logger.error(f"Error playing playlist: {e}", exc_info=True)
            return {"error": f"Error playing playlist: {str(e)}"}
    
    async def play_track(self, track_id: str) -> Dict[str, Any]:
        """Play a specific track"""
        try:
            if not self.sp:
                return {"error": "Spotify client not initialized"}
            
            if not track_id:
                return {"error": "Track ID is required"}
            
            self.sp.start_playback(uris=[f"spotify:track:{track_id}"])
            return {"response": f"🎵 Squawk! Playing track {track_id}, matey!"}
        except Exception as e:
            logger.error(f"Error playing track: {e}", exc_info=True)
            return {"error": f"Error playing track: {str(e)}"}
    
    async def get_playback_status(self) -> Dict[str, Any]:
        """Get current playback status"""
        try:
            if not self.sp:
                return {"error": "Spotify client not initialized"}
            
            current = self.sp.current_playback()
            if current:
                track = current.get('item', {})
                track_name = track.get('name', 'Unknown')
                artist = track.get('artists', [{}])[0].get('name', 'Unknown')
                is_playing = current.get('is_playing', False)
                
                status_text = f"🎵 Currently playing: {track_name} by {artist}"
                status_text += f"\n🦜 Status: {'Playing' if is_playing else 'Paused'}"
                
                return {"response": status_text}
            else:
                return {"response": "🎵 Squawk! Nothing playing right now, matey!"}
        except Exception as e:
            logger.error(f"Error getting playback status: {e}", exc_info=True)
            return {"error": f"Error getting playback status: {str(e)}"}
    
    async def get_playlist_info(self, playlist_id: str) -> Dict[str, Any]:
        """Get playlist information"""
        try:
            if not self.sp:
                return {"error": "Spotify client not initialized"}
            
            if not playlist_id:
                return {"error": "Playlist ID is required"}
            
            playlist = self.sp.playlist(playlist_id)
            name = playlist.get('name', 'Unknown')
            tracks = playlist.get('tracks', {}).get('total', 0)
            
            info_text = f"🎵 Playlist: {name}"
            info_text += f"\n🦜 Tracks: {tracks}"
            
            return {"response": info_text}
        except Exception as e:
            logger.error(f"Error getting playlist info: {e}", exc_info=True)
            return {"error": f"Error getting playlist info: {str(e)}"}

    async def get_available_devices(self) -> Dict[str, Any]:
        """Get list of available Spotify devices"""
        try:
            if not self.sp:
                return {"error": "Spotify client not initialized"}
            
            devices = self.sp.devices()
            if not devices['devices']:
                return {"response": "No Spotify devices found. Please open Spotify on a device."}
            
            device_list = []
            for device in devices['devices']:
                device_info = {
                    'name': device['name'],
                    'type': device['type'],
                    'id': device['id'],
                    'is_active': device.get('is_active', False),
                    'is_private_session': device.get('is_private_session', False),
                    'is_restricted': device.get('is_restricted', False)
                }
                device_list.append(device_info)
            
            result_text = f"Available Spotify devices ({len(device_list)}):\n\n"
            for i, device in enumerate(device_list, 1):
                result_text += f"{i}. **{device['name']}** ({device['type']})\n"
                result_text += f"   ID: {device['id']}\n"
                result_text += f"   Active: {'✅ Yes' if device['is_active'] else '❌ No'}\n"
                if device['is_private_session']:
                    result_text += f"   Private Session: ✅ Yes\n"
                if device['is_restricted']:
                    result_text += f"   Restricted: ✅ Yes\n"
                result_text += "\n"
            
            return {"response": result_text.strip()}
            
        except Exception as e:
            logger.error(f"Error getting available devices: {e}", exc_info=True)
            return {"error": f"Error getting available devices: {str(e)}"}

# Global client instance
spotify_client = SpotifyClient()

# Convenience functions for direct use
async def play_spotify() -> Dict[str, Any]:
    """Start or resume Spotify playback"""
    return await spotify_client.play_spotify()

async def pause_spotify() -> Dict[str, Any]:
    """Pause Spotify playback"""
    return await spotify_client.pause_spotify()

async def next_track() -> Dict[str, Any]:
    """Skip to next track"""
    return await spotify_client.next_track()

async def previous_track() -> Dict[str, Any]:
    """Go to previous track"""
    return await spotify_client.previous_track()

async def set_volume(volume: int) -> Dict[str, Any]:
    """Set playback volume"""
    return await spotify_client.set_volume(volume)

async def play_playlist(playlist_id: str) -> Dict[str, Any]:
    """Play a specific playlist"""
    return await spotify_client.play_playlist(playlist_id)

async def play_track(track_id: str) -> Dict[str, Any]:
    """Play a specific track"""
    return await spotify_client.play_track(track_id)

async def get_playback_status() -> Dict[str, Any]:
    """Get current playback status"""
    return await spotify_client.get_playback_status()

async def get_playlist_info(playlist_id: str) -> Dict[str, Any]:
    """Get playlist information"""
    return await spotify_client.get_playlist_info(playlist_id)

async def get_available_devices() -> Dict[str, Any]:
    """Get list of available Spotify devices"""
    return await spotify_client.get_available_devices()

# Test function
async def test():
    """Test the Spotify client"""
    try:
        # Test playback status
        status = await get_playback_status()
        print(f"Playback status: {status}")
        
        # Test volume
        volume_result = await set_volume(50)
        print(f"Volume result: {volume_result}")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test()) 