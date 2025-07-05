#!/usr/bin/env python3
"""
Voice Client for Salty
Provides client interface for voice synthesis server
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any
from pathlib import Path
import httpx

# Add the parent directory to the path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Ensure logs directory exists
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / 'voice_client.log')
    ]
)
logger = logging.getLogger(__name__)

# Voice server configuration using environment variables
VOICE_SERVER_URL = os.getenv('VOICE_SERVER_URL', 'http://localhost:9006')

class VoiceClient:
    """Voice client for voice synthesis"""
    
    def __init__(self):
        """Initialize the voice client"""
        self.server_url = VOICE_SERVER_URL
        self.client = httpx.AsyncClient(
            base_url=self.server_url,
            timeout=60.0  # Longer timeout for voice generation
        )
        logger.info(f"Voice client initialized with server URL: {self.server_url}")
    
    async def _make_request(self, method: str, endpoint: str, json_data: Dict = None) -> Dict[str, Any]:
        """Make HTTP request using the shared client"""
        try:
            if method.upper() == "GET":
                response = await self.client.get(endpoint)
            else:
                response = await self.client.post(endpoint, json=json_data)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            logger.error(f"Error making request to {endpoint}: {e}", exc_info=True)
            return {"error": f"Request failed: {str(e)}"}
    
    async def close(self):
        """Close the httpx client"""
        await self.client.aclose()

    async def generate_salty_voice(self, text: str, voice_id: str = None) -> Dict[str, Any]:
        """Generate Salty's voice for given text"""
        return await self._make_request("POST", "/generate_voice", {
            "text": text,
            "voice_id": voice_id
        })
    
    async def speak_text(self, text: str, voice_id: str = None, blocking: bool = True) -> Dict[str, Any]:
        """Generate and play Salty's voice for text"""
        return await self._make_request("POST", "/speak_text", {
            "text": text,
            "voice_id": voice_id,
            "blocking": blocking
        })
    
    async def play_ambient_sound(self, sound_name: str, volume: float = 0.5, loop: bool = False) -> Dict[str, Any]:
        """Play ambient sound"""
        return await self._make_request("POST", "/play_ambient_sound", {
            "sound_name": sound_name,
            "volume": volume,
            "loop": loop
        })
    
    async def stop_all_audio(self) -> Dict[str, Any]:
        """Stop all audio playback"""
        return await self._make_request("POST", "/stop_all_audio")
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Get available ElevenLabs voices"""
        return await self._make_request("GET", "/available_voices")
    
    async def get_audio_history(self) -> Dict[str, Any]:
        """Get audio generation history"""
        return await self._make_request("GET", "/audio_history")

# Global client instance
voice_client = VoiceClient()

# Convenience functions for direct use
async def generate_salty_voice(text: str, voice_id: str = None) -> Dict[str, Any]:
    """Generate Salty's voice for given text"""
    return await voice_client.generate_salty_voice(text, voice_id)

async def speak_text(text: str, voice_id: str = None, blocking: bool = True) -> Dict[str, Any]:
    """Generate and play Salty's voice for text"""
    return await voice_client.speak_text(text, voice_id, blocking)

async def play_ambient_sound(sound_name: str, volume: float = 0.5, loop: bool = False) -> Dict[str, Any]:
    """Play ambient sound"""
    return await voice_client.play_ambient_sound(sound_name, volume, loop)

async def stop_all_audio() -> Dict[str, Any]:
    """Stop all audio playback"""
    return await voice_client.stop_all_audio()

async def get_available_voices() -> Dict[str, Any]:
    """Get available ElevenLabs voices"""
    return await voice_client.get_available_voices()

async def get_audio_history() -> Dict[str, Any]:
    """Get audio generation history"""
    return await voice_client.get_audio_history()

async def get_tools() -> Dict[str, Any]:
    """Get a dictionary of all available tools"""
    return {
        "generate_salty_voice": generate_salty_voice,
        "speak_text": speak_text,
        "play_ambient_sound": play_ambient_sound,
        "stop_all_audio": stop_all_audio,
        "get_available_voices": get_available_voices,
        "get_audio_history": get_audio_history,
    }