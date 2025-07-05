#!/usr/bin/env python3
"""
Test TTSSelector functionality
"""

import asyncio
import os
from utils.tts_select import TTSSelector
import tempfile

async def test_tts_selector():
    """Test TTSSelector"""
    try:
        print("Testing TTSSelector...")
        
        # Create TTSSelector
        tts_selector = TTSSelector()
        print(f"TTS Method: {tts_selector.tts_method}")
        tts_method = tts_selector.tts_method.strip('"').strip("'")
        
        # Test gTTS
        if tts_method == 'gtts':
            print("Testing gTTS...")
            result = await tts_selector.text_to_speech("Hello, this is a test of TTSSelector")
            # result is a dict with 'audio_data'
            audio_bytes = result["audio_data"]
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_filename = fp.name
                fp.write(audio_bytes)
            print(f"Generated file: {temp_filename}")
            print(f"File exists: {os.path.exists(temp_filename)}")
            print(f"File size: {os.path.getsize(temp_filename)} bytes")
            # Clean up
            try:
                os.unlink(temp_filename)
                print("Temporary file cleaned up")
            except Exception as e:
                print(f"Error cleaning up: {e}")
        elif tts_method == 'elevenlabs':
            print("Testing ElevenLabs...")
            mp3_path = await tts_selector.text_to_speech("Hello, this is a test of TTSSelector with ElevenLabs")
            print(f"Generated file: {mp3_path}")
            print(f"File exists: {os.path.exists(mp3_path)}")
            print(f"File size: {os.path.getsize(mp3_path)} bytes")
            # Clean up
            try:
                os.unlink(mp3_path)
                print("Temporary file cleaned up")
            except Exception as e:
                print(f"Error cleaning up: {e}")
        
    except Exception as e:
        print(f"Error in TTSSelector test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tts_selector()) 