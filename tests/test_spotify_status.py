#!/usr/bin/env python3
"""
Spotify Status Test Script
Quick diagnostic tool for Spotify integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.spotify_client import (
    get_playback_status,
    get_available_devices,
    play_spotify,
    play_playlist
)

async def test_spotify_status():
    """Test all Spotify functions"""
    print("🦜 Testing Spotify Integration...")
    print("=" * 50)
    
    # Test 1: Check available devices
    print("\n1. 📱 Checking available devices...")
    try:
        devices_result = await get_available_devices()
        if "error" in devices_result:
            print(f"❌ Error: {devices_result['error']}")
        else:
            print("✅ Devices retrieved successfully!")
            print(devices_result.get("response", "No response"))
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Check current playback status
    print("\n2. 📊 Checking current playback status...")
    try:
        status_result = await get_playback_status()
        if "error" in status_result:
            print(f"❌ Error: {status_result['error']}")
        else:
            print("✅ Status retrieved successfully!")
            print(status_result.get("response", "No response"))
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Try to start playback
    print("\n3. ▶️ Testing playback start...")
    try:
        play_result = await play_spotify()
        if "error" in play_result:
            print(f"❌ Error: {play_result['error']}")
        else:
            print("✅ Playback started successfully!")
            print(play_result.get("response", "No response"))
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: Try playlist playback
    print("\n4. 🏝️ Testing playlist playback...")
    try:
        playlist_id = "6tTFZeC3bHRtklZpmNDTM7"  # Tiki Dave's playlist
        playlist_result = await play_playlist(playlist_id)
        if "error" in playlist_result:
            print(f"❌ Error: {playlist_result['error']}")
        else:
            print("✅ Playlist started successfully!")
            print(playlist_result.get("response", "No response"))
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🦜 Spotify test completed!")
    print("\n💡 Troubleshooting tips:")
    print("- Check your computer's audio output")
    print("- Open Spotify Web Player to see if music is playing there")
    print("- Make sure your speakers/headphones are connected")
    print("- Check the volume level on your device")

if __name__ == "__main__":
    asyncio.run(test_spotify_status()) 