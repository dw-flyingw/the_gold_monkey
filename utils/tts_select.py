import os
import logging
from dotenv import load_dotenv
from gtts import gTTS
import requests
import tempfile
from utils.env_utils import get_tts_method, get_elevenlabs_config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSSelector:
    def __init__(self):
        self.tts_method = get_tts_method()
        elevenlabs_config = get_elevenlabs_config()
        self.elevenlabs_api_key = elevenlabs_config['api_key']
        self.elevenlabs_voice_id = elevenlabs_config['voice_id']
        
    async def text_to_speech(self, text: str) -> str:
        """Convert text to speech using the configured TTS method."""
        if self.tts_method == 'none':
            raise Exception("Voice is disabled")
        elif self.tts_method == 'elevenlabs':
            return await self._elevenlabs_tts(text)
        else:
            return await self._gtts_tts(text)
    
    async def _gtts_tts(self, text: str) -> str:
        """Convert text to speech using Google Text-to-Speech."""
        try:
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_filename = fp.name
                tts.save(temp_filename)
            return temp_filename
        except Exception as e:
            logger.error(f"Error in gTTS conversion: {e}")
            raise
    
    async def _elevenlabs_tts(self, text: str) -> str:
        """Convert text to speech using ElevenLabs API."""
        if not self.elevenlabs_api_key or not self.elevenlabs_voice_id:
            logger.warning("ElevenLabs API key or voice ID not found, falling back to gTTS")
            return await self._gtts_tts(text)
            
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
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
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_filename = fp.name
                fp.write(response.content)
            return temp_filename
            
        except Exception as e:
            logger.error(f"Error in ElevenLabs TTS conversion: {e}")
            logger.info("Falling back to gTTS")
            return await self._gtts_tts(text) 