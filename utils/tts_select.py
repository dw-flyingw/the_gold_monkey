import os
import logging
from dotenv import load_dotenv
from gtts import gTTS
import requests
import tempfile

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSSelector:
    def __init__(self):
        self.tts_method = os.getenv('TTS_METHOD')
        if not self.tts_method:
            raise Exception("TTS_METHOD environment variable is not set")
        self.tts_method = self.tts_method.strip('"').strip("'").lower()
        
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.elevenlabs_voice_id = os.getenv('ELEVENLABS_VOICE_ID')
        
    async def text_to_speech(self, text: str, voice_id: str = None) -> str:
        """Convert text to speech using the configured TTS method."""
        if self.tts_method == 'none':
            raise Exception("Voice is disabled")
        elif self.tts_method == 'elevenlabs':
            return await self._elevenlabs_tts(text, voice_id)
        else:
            return await self._gtts_tts(text)
    
    async def _gtts_tts(self, text: str) -> dict:
        """Convert text to speech using Google Text-to-Speech and return audio bytes."""
        try:
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_filename = fp.name
                tts.save(temp_filename)
            # Read the audio file as bytes
            with open(temp_filename, 'rb') as f:
                audio_bytes = f.read()
            # Optionally clean up the temp file
            try:
                os.unlink(temp_filename)
            except Exception:
                pass
            return {"audio_data": audio_bytes}
        except Exception as e:
            logger.error(f"Error in gTTS conversion: {e}")
            raise
    
    async def _elevenlabs_tts(self, text: str, voice_id: str = None) -> dict:
        """Convert text to speech using ElevenLabs API."""
        selected_voice_id = voice_id or self.elevenlabs_voice_id
        if not self.elevenlabs_api_key or not selected_voice_id:
            raise Exception("ElevenLabs API key or voice ID not configured")
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{selected_voice_id}"
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
            # Read the audio file as bytes
            with open(temp_filename, 'rb') as f:
                audio_bytes = f.read()
            try:
                os.unlink(temp_filename)
            except Exception:
                pass
            return {"audio_data": audio_bytes}
        except Exception as e:
            logger.error(f"Error in ElevenLabs TTS conversion: {e}")
            raise 