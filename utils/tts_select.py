#!/usr/bin/env python3
"""
TTS Selector for The Gold Monkey
Handles different text-to-speech methods
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)

class TTSSelector:
    """Text-to-speech selector with multiple backends"""
    
    def __init__(self):
        """Initialize TTS selector"""
        self.tts_method = os.getenv('TTS_METHOD', 'none').lower()
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.elevenlabs_voice_id = os.getenv('ELEVENLABS_VOICE_ID')
        
        logger.info(f"TTS Selector initialized with method: {self.tts_method}")
    
    async def text_to_speech(self, text: str, voice_id: Optional[str] = None) -> Dict[str, Any]:
        """Convert text to speech using the configured method"""
        if not text.strip():
            return {"error": "Empty text provided"}
        
        try:
            audio_data = None
            if self.tts_method == 'elevenlabs':
                audio_data = await self._elevenlabs_tts(text, voice_id)
            elif self.tts_method == 'pyttsx3':
                audio_data = await self._pyttsx3_tts(text)
            elif self.tts_method == 'gtts':
                audio_data = await self._gtts_tts(text)
            else:
                logger.warning(f"TTS method '{self.tts_method}' not supported")
                return {"error": f"TTS method '{self.tts_method}' not supported"}
            
            if audio_data:
                return {"audio_data": audio_data}
            else:
                return {"error": "Failed to generate audio"}
                
        except Exception as e:
            logger.error(f"Error in text_to_speech: {e}")
            return {"error": str(e)}
    
    async def _elevenlabs_tts(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """Use ElevenLabs for TTS"""
        try:
            import requests
            
            if not self.elevenlabs_api_key:
                logger.error("ElevenLabs API key not configured")
                return None
            
            voice_id = voice_id or self.elevenlabs_voice_id
            if not voice_id:
                logger.error("ElevenLabs voice ID not configured")
                return None
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                return None
                
        except ImportError:
            logger.error("requests library not available for ElevenLabs TTS")
            return None
        except Exception as e:
            logger.error(f"Error in ElevenLabs TTS: {e}")
            return None
    
    async def _pyttsx3_tts(self, text: str) -> Optional[bytes]:
        """Use pyttsx3 for TTS"""
        try:
            import pyttsx3
            import tempfile
            
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Initialize pyttsx3
            engine = pyttsx3.init()
            
            # Set properties
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            # Save to file
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            
            # Read the file and return bytes
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up
            os.unlink(temp_path)
            
            return audio_data
            
        except ImportError:
            logger.error("pyttsx3 library not available")
            return None
        except Exception as e:
            logger.error(f"Error in pyttsx3 TTS: {e}")
            return None
    
    async def _gtts_tts(self, text: str) -> Optional[bytes]:
        """Use gTTS for TTS"""
        try:
            from gtts import gTTS
            import tempfile
            
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_path)
            
            # Read the file and return bytes
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up
            os.unlink(temp_path)
            
            return audio_data
            
        except ImportError:
            logger.error("gTTS library not available")
            return None
        except Exception as e:
            logger.error(f"Error in gTTS: {e}")
            return None
    
    def get_available_methods(self) -> Dict[str, bool]:
        """Get available TTS methods and their status"""
        methods = {
            'elevenlabs': False,
            'pyttsx3': False,
            'gtts': False
        }
        
        # Check ElevenLabs
        try:
            import requests
            methods['elevenlabs'] = bool(self.elevenlabs_api_key)
        except ImportError:
            pass
        
        # Check pyttsx3
        try:
            import pyttsx3
            methods['pyttsx3'] = True
        except ImportError:
            pass
        
        # Check gTTS
        try:
            from gtts import gTTS
            methods['gtts'] = True
        except ImportError:
            pass
        
        return methods
    
    def get_current_method(self) -> str:
        """Get the currently configured TTS method"""
        return self.tts_method 