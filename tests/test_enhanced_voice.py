#!/usr/bin/env python3
"""
Test script for the enhanced voice server with parrot effects
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_servers.voice_server import voice_server

async def test_enhanced_voice():
    """Test the enhanced voice server with parrot effects"""
    print("🧪 Testing Enhanced Voice Server with Parrot Effects")
    print("=" * 60)
    
    # Test 1: Basic text without effects
    print("\n1. Testing basic text without effects...")
    result = await voice_server.speak_text("Hello, welcome to The Gold Monkey!", blocking=False)
    print(f"Result: {result}")
    
    # Test 2: Text with squawk
    print("\n2. Testing text with squawk...")
    result = await voice_server.speak_text("Squawk! Hello there, matey!", blocking=False)
    print(f"Result: {result}")
    
    # Test 3: Text with screech
    print("\n3. Testing text with screech...")
    result = await voice_server.speak_text("Screech! This is exciting!", blocking=False)
    print(f"Result: {result}")
    
    # Test 4: Text with both squawk and screech
    print("\n4. Testing text with both squawk and screech...")
    result = await voice_server.speak_text("Squawk! Welcome to the tiki bar! Screech! It's party time!", blocking=False)
    print(f"Result: {result}")
    
    # Test 5: Joke with timing
    print("\n5. Testing joke with timing...")
    result = await voice_server.speak_text("Why did the parrot go to the doctor? Because it was feeling a bit under the weather!", blocking=False)
    print(f"Result: {result}")
    
    # Test 6: Ambient sound
    print("\n6. Testing ambient sound...")
    result = await voice_server.play_ambient_sound("ocean_waves", volume=0.3, loop=False)
    print(f"Result: {result}")
    
    # Test 7: Stop all audio
    print("\n7. Testing stop all audio...")
    result = await voice_server.stop_all_audio()
    print(f"Result: {result}")
    
    print("\n✅ Enhanced voice server test completed!")
    print("Note: Audio playback tests were run in non-blocking mode for faster testing.")

if __name__ == "__main__":
    asyncio.run(test_enhanced_voice()) 