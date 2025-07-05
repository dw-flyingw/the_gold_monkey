#!/usr/bin/env python3
"""
Test voice server functionality
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path to import mcp_servers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp_servers.voice_server import VoiceServer

async def test_voice_server():
    """Test voice server"""
    try:
        print("Testing voice server...")
        
        # Create voice server
        voice_server = VoiceServer()
        print(f"TTS Method: {voice_server.tts_method}")
        tts_method = voice_server.tts_method.strip('"').strip("'")
        
        # Test generate_salty_voice
        if tts_method == 'gtts':
            print("Testing generate_salty_voice with gTTS...")
            try:
                result = await voice_server.generate_salty_voice("Hello, this is a test of the voice server")
                print(f"Result: {result}")
                
                if "error" in result:
                    print(f"Error: {result['error']}")
                elif "mp3_path" in result:
                    mp3_path = result["mp3_path"]
                    print(f"Generated file: {mp3_path}")
                    print(f"File exists: {os.path.exists(mp3_path)}")
                    if os.path.exists(mp3_path):
                        print(f"File size: {os.path.getsize(mp3_path)} bytes")
                        
                        # Clean up
                        try:
                            os.unlink(mp3_path)
                            print("Temporary file cleaned up")
                        except Exception as e:
                            print(f"Error cleaning up: {e}")
            except Exception as e:
                print(f"Error in generate_salty_voice: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"TTS method is {tts_method}, not testing gTTS")
        
    except Exception as e:
        print(f"Error in voice server test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_voice_server()) 