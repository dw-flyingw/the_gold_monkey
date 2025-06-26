#!/usr/bin/env python3
"""
Mute Audio Script
Temporarily mutes system audio to stop blips and buzzing.
"""

import subprocess
import time

def mute_audio():
    """Mute system audio."""
    print("🔇 Muting system audio...")
    
    try:
        # Mute system audio
        subprocess.run(['osascript', '-e', 'set volume output muted true'], check=True)
        print("✅ System audio muted")
        
    except Exception as e:
        print(f"❌ Could not mute audio: {e}")

def unmute_audio():
    """Unmute system audio."""
    print("🔊 Unmuting system audio...")
    
    try:
        # Unmute system audio
        subprocess.run(['osascript', '-e', 'set volume output muted false'], check=True)
        print("✅ System audio unmuted")
        
    except Exception as e:
        print(f"❌ Could not unmute audio: {e}")

def set_volume(level):
    """Set system volume to a specific level (0-100)."""
    print(f"🔊 Setting volume to {level}%...")
    
    try:
        # Set volume (0-100)
        subprocess.run(['osascript', '-e', f'set volume output volume {level}'], check=True)
        print(f"✅ Volume set to {level}%")
        
    except Exception as e:
        print(f"❌ Could not set volume: {e}")

def main():
    """Main function."""
    print("🔇 Audio Control Script")
    print("=" * 30)
    
    # Mute audio
    mute_audio()
    
    print("\n⏰ Audio will be muted for 10 seconds...")
    time.sleep(10)
    
    # Unmute audio
    unmute_audio()
    
    print("\n✅ Audio control complete!")

if __name__ == "__main__":
    main() 