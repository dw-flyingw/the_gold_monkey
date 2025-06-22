#!/usr/bin/env python3
"""
Salty Voice Server
"""

import asyncio
import base64
import logging
import os
import queue
import re
import sys
import tempfile
import threading
import time
from typing import Any, Dict, List, Optional
from collections import OrderedDict

import requests
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from pydub import AudioSegment
from pydub.playback import play
import pygame
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.env_utils import get_env_vars
from utils.tts_select import TTSSelector

# --- Configuration ---
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / "voice_server.log")
    ]
)
logger = logging.getLogger(__name__)

AUDIO_DELAY = 0.2  # Base delay for audio effects

# --- FastAPI App ---
app = FastAPI()

# --- Voice Server Class ---
class VoiceServer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VoiceServer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized') and self.initialized:
            return
        
        logger.info("Initializing Voice Server...")
        self.initialized = False
        self.loop = asyncio.get_event_loop()

        # Load environment variables
        env_vars = get_env_vars()
        self.api_key = env_vars.get("ELEVENLABS_API_KEY")
        self.voice_id = env_vars.get("ELEVENLABS_VOICE_ID")
        self.tts_method = env_vars.get("TTS_METHOD", "elevenlabs")
        
        # Audio components
        self.tts_selector = TTSSelector(api_key=self.api_key, voice_id=self.voice_id)
        self.audio_cache = OrderedDict()
        self.cache_size = 50
        self.audio_queue = queue.Queue()
        self.audio_lock = threading.Lock()
        self.shutdown_event = threading.Event()
        self.mixer_initialized = False
        
        self.initialize_audio()
        self.initialize_parrot_effects()
        self.start_audio_thread()
        self.initialized = True
        logger.info("Voice Server Initialized.")

    def initialize_audio(self):
        """Initialize the audio mixer."""
        try:
            pygame.mixer.init()
            self.mixer = pygame.mixer
            self.mixer_initialized = True
            logger.info("Pygame mixer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}", exc_info=True)
            self.mixer_initialized = False

    def initialize_parrot_effects(self):
        """Load parrot sound effects."""
        self.squawk_sound = self._load_sound("../audio/squawk.wav")
        self.screech_sound = self._load_sound("../audio/screeech.wav")

    def _load_sound(self, file_path: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound file."""
        if not self.mixer_initialized:
            return None
        try:
            path = Path(__file__).parent / file_path
            if not path.exists():
                logger.error(f"Sound file not found: {path}")
                return None
            sound = self.mixer.Sound(str(path))
            logger.info(f"Loaded sound: {file_path}")
            return sound
        except Exception as e:
            logger.error(f"Failed to load sound {file_path}: {e}", exc_info=True)
            return None
            
    def start_audio_thread(self):
        """Start the background thread for processing the audio queue."""
        self.audio_thread = threading.Thread(target=self.process_audio_queue, daemon=True)
        self.audio_thread.start()
        logger.info("Audio processing thread started.")

    def process_audio_queue(self):
        """Continuously process audio queue in a separate thread"""
        while not self.shutdown_event.is_set():
            try:
                item = self.audio_queue.get(timeout=1)
                audio_type, data, completion_event = item
                try:
                    with self.audio_lock:
                        if audio_type == 'file':
                            self._play_audio_file(data)
                        elif audio_type == 'mp3':
                            self._play_audio_data(data)
                        elif audio_type == 'squawk':
                            self._play_squawk()
                        elif audio_type == 'screech':
                            self._play_screech()
                finally:
                    # Signal that this audio part is done processing
                    if completion_event:
                        self.loop.call_soon_threadsafe(completion_event.set)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing audio queue: {e}", exc_info=True)
                if 'item' in locals() and item[2]:
                    self.loop.call_soon_threadsafe(item[2].set)

    def _play_audio_file(self, file_name: str):
        """Play an audio file."""
        if not self.mixer_initialized:
            return
        try:
            self.mixer.music.load(file_name)
            self.mixer.music.play()
            while self.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Failed to play audio file {file_name}: {e}", exc_info=True)

    def _play_audio_data(self, audio_data: bytes):
        """Play audio from bytes using a temporary file for pygame compatibility."""
        if not self.mixer_initialized:
            return
        try:
            with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmpfile:
                tmpfile.write(audio_data)
                tmpfile.flush()
                self.mixer.music.load(tmpfile.name)
                self.mixer.music.play()
                while self.mixer.music.get_busy():
                    time.sleep(0.1)
        except Exception as e:
            logger.error(f"Failed to play audio data: {e}", exc_info=True)
            
    def _play_squawk(self):
        """Play squawk sound effect"""
        if self.squawk_sound:
            try:
                self.squawk_sound.play()
                while self.mixer.get_busy():
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Failed to play squawk sound: {e}", exc_info=True)

    def _play_screech(self):
        """Play screech sound effect"""
        if self.screech_sound:
            try:
                self.screech_sound.play()
                while self.mixer.get_busy():
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Failed to play screech sound: {e}", exc_info=True)

    async def process_text_with_squawks(self, text: str) -> List[Dict[str, Any]]:
        """Process text to identify and handle squawk, screech, joke patterns, and sentence pauses."""
        parts = []
        
        # First, split text into sentences while preserving special patterns
        pattern = re.compile(
            r'(\b(?:why\s+(?:did|does|do|is|are|was|were).*?\?|what\s+(?:do\s+you\s+call|is|are|was|were).*?\?|how\s+(?:do\s+you|many|much|long|far|often).*?\?|knock\sknock.*?))|'  # Jokes
            r'(\bsqu+a+w+k+\b)|'  # Squawk
            r'(\bscree+e+c+h+\b)',  # Screech
            re.IGNORECASE
        )
        
        last_end = 0
        for match in pattern.finditer(text):
            start, end = match.span()
            if start > last_end:
                # Process the text before the special pattern
                text_before = text[last_end:start].strip()
                if text_before:
                    parts.extend(self._split_into_sentences(text_before))
            
            joke, squawk, screech = match.groups()
            
            if joke:
                if '?' in joke:
                    setup, punchline = joke.split('?', 1)
                    parts.append({'type': 'text', 'content': setup + '?'})
                    parts.append({'type': 'pause', 'duration': 2.0})  # Dramatic pause for jokes
                    parts.append({'type': 'text', 'content': punchline.strip()})
                else:
                    parts.append({'type': 'text', 'content': joke})
            elif squawk:
                parts.append({'type': 'squawk'})
                parts.append({'type': 'pause', 'duration': AUDIO_DELAY})
            elif screech:
                parts.append({'type': 'screech'})
                parts.append({'type': 'pause', 'duration': AUDIO_DELAY})
            last_end = end
            
        # Process any remaining text after the last special pattern
        if last_end < len(text):
            remaining_text = text[last_end:].strip()
            if remaining_text:
                parts.extend(self._split_into_sentences(remaining_text))
            
        return [p for p in parts if p.get('type') != 'text' or p.get('content')]

    def _split_into_sentences(self, text: str) -> List[Dict[str, Any]]:
        """Split text into sentences and add pauses between them."""
        parts = []
        
        # Split on sentence boundaries (., !, ?) but preserve the punctuation
        sentence_pattern = re.compile(r'([^.!?]+[.!?]+)')
        sentences = sentence_pattern.findall(text)
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if sentence:
                parts.append({'type': 'text', 'content': sentence})
                
                # Add pause after each sentence except the last one
                if i < len(sentences) - 1:
                    # Longer pause for sentences ending with ! or ?
                    if sentence.endswith(('!', '?')):
                        parts.append({'type': 'pause', 'duration': 0.8})
                    else:
                        parts.append({'type': 'pause', 'duration': 0.5})
        
        # If no sentence boundaries found, treat the whole text as one sentence
        if not sentences and text.strip():
            parts.append({'type': 'text', 'content': text.strip()})
            
        return parts

    async def generate_salty_voice(self, text: str, voice_id: str = None) -> Dict[str, Any]:
        """Generate Salty's voice using ElevenLabs."""
        if not self.api_key:
            return {"error": "ElevenLabs API key not configured"}
        
        voice_to_use = voice_id or self.voice_id
        cache_key = f"{voice_to_use}_{hash(text)}"
        if cache_key in self.audio_cache:
            logger.info("Using cached audio")
            return {"audio_data": self.audio_cache[cache_key]}
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_to_use}"
        headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": self.api_key}
        data = {
            "text": text, "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.7, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True}
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            audio_bytes = response.content
            if len(self.audio_cache) >= self.cache_size:
                self.audio_cache.popitem(last=False)
            self.audio_cache[cache_key] = audio_bytes
            return {"audio_data": audio_bytes}
        except requests.exceptions.RequestException as e:
            logger.error(f"ElevenLabs API request failed: {e}")
            return {"error": str(e)}

    async def speak_text(self, text: str, voice_id: str = None, blocking: bool = True) -> Dict[str, Any]:
        """Generate and play Salty's voice for text with effects."""
        if self.tts_method == 'none':
            return {"response": "Voice is disabled"}

        parts = await self.process_text_with_squawks(text)
        
        for part in parts:
            completion_event = asyncio.Event()

            if part['type'] == 'pause':
                await asyncio.sleep(part['duration'])
                continue
            elif part['type'] in ['squawk', 'screech']:
                self.audio_queue.put((part['type'], None, completion_event))
            elif part['type'] == 'text':
                content = part['content']
                if self.tts_method == 'gtts':
                    voice_result = await self.tts_selector.text_to_speech(content)
                    if "mp3_path" in voice_result:
                        self.audio_queue.put(('file', voice_result["mp3_path"], completion_event))
                    else:
                        logger.error(f"gTTS failed: {voice_result.get('error')}")
                        completion_event.set()
                else:
                    voice_result = await self.generate_salty_voice(content, voice_id)
                    if "audio_data" in voice_result:
                        self.audio_queue.put(('mp3', voice_result["audio_data"], completion_event))
                    else:
                        logger.error(f"ElevenLabs failed: {voice_result.get('error')}")
                        completion_event.set()
            if blocking:
                await completion_event.wait()
        return {"response": "Text spoken successfully"}

    async def play_ambient_sound(self, sound_name: str, volume: float, loop: bool) -> Dict[str, Any]:
        # This is a stub. Implement logic to play ambient sounds.
        logger.info(f"STUB: play_ambient_sound({sound_name}, {volume}, {loop})")
        return {"status": "ambient sound playing (stub)"}

    async def stop_all_audio(self) -> Dict[str, Any]:
        # This is a stub. Implement logic to stop all audio.
        logger.info("STUB: stop_all_audio()")
        if self.mixer_initialized:
            self.mixer.music.stop()
            # You might need more logic to stop channel sounds too
        return {"status": "all audio stopped (stub)"}

    async def get_available_voices(self) -> Dict[str, Any]:
        # This is a stub. Implement logic to get voices from ElevenLabs.
        logger.info("STUB: get_available_voices()")
        return {"voices": ["voice1 (stub)", "voice2 (stub)"]}

    async def get_audio_history(self) -> Dict[str, Any]:
        # This is a stub. Implement logic to get audio history.
        logger.info("STUB: get_audio_history()")
        return {"history": ["history_item_1 (stub)"]}
    
    def shutdown(self):
        logger.info("Shutting down Voice Server.")
        self.shutdown_event.set()
        if self.audio_thread.is_alive():
            self.audio_thread.join()
        if self.mixer_initialized:
            pygame.quit()

# --- FastAPI Endpoints ---
@app.on_event("startup")
async def startup_event():
    app.state.voice_server = VoiceServer()

@app.on_event("shutdown")
async def shutdown_event():
    app.state.voice_server.shutdown()

@app.post("/speak_text")
async def speak_text_endpoint(request: Request):
    data = await request.json()
    text = data.get("text")
    voice_id = data.get("voice_id")
    blocking = data.get("blocking", True)
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    return await app.state.voice_server.speak_text(text, voice_id, blocking)

@app.post("/play_ambient_sound")
async def play_ambient_sound_endpoint(request: Request):
    data = await request.json()
    return await app.state.voice_server.play_ambient_sound(
        data.get("sound_name"), data.get("volume", 0.5), data.get("loop", False)
    )

@app.post("/stop_all_audio")
async def stop_all_audio_endpoint():
    return await app.state.voice_server.stop_all_audio()

@app.get("/available_voices")
async def get_available_voices_endpoint():
    return await app.state.voice_server.get_available_voices()

@app.get("/audio_history")
async def get_audio_history_endpoint():
    return await app.state.voice_server.get_audio_history()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 