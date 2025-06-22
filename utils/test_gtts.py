#!/usr/bin/env python3
"""
Test gTTS functionality
"""

from gtts import gTTS
import tempfile
import os
import pygame
import time

def test_gtts():
    """Test gTTS text-to-speech"""
    try:
        print("Testing gTTS...")
        
        # Create gTTS object
        tts = gTTS(text='Hello, this is a test of Google Text to Speech', lang='en')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_filename = fp.name
            tts.save(temp_filename)
        
        print(f"Created audio file: {temp_filename}")
        print(f"File exists: {os.path.exists(temp_filename)}")
        print(f"File size: {os.path.getsize(temp_filename)} bytes")
        
        # Try to play it with pygame
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            print("Playing audio...")
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            print("Audio playback completed")
            
        except Exception as e:
            print(f"Error playing audio: {e}")
        
        # Clean up
        try:
            os.unlink(temp_filename)
            print("Temporary file cleaned up")
        except Exception as e:
            print(f"Error cleaning up: {e}")
            
    except Exception as e:
        print(f"Error in gTTS test: {e}")

if __name__ == "__main__":
    test_gtts() 