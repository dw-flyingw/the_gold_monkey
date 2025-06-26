#!/usr/bin/env python3
"""
Stop Audio Processes Script
Stops any lingering audio processes and clears audio contexts that might be causing buzzing noise.
"""

import os
import subprocess
import sys
import time

def stop_audio_processes():
    """Stop common audio processes"""
    audio_processes = ['pulseaudio', 'coreaudio', 'audio']
    
    for process in audio_processes:
        try:
            # Try to kill the process
            subprocess.run(['pkill', '-f', process], check=False)
            print(f"Attempted to stop {process}")
        except Exception as e:
            print(f"Error stopping {process}: {e}")

def clear_audio_devices():
    """Clear audio device states."""
    
    print("🎵 Clearing audio device states...")
    
    # On macOS, reset audio devices
    if sys.platform == "darwin":
        try:
            # Reset audio system
            subprocess.run(['sudo', 'killall', 'coreaudiod'], check=False)
            print("Reset macOS audio system")
            time.sleep(2)
            
            # Restart audio service
            subprocess.run(['sudo', 'launchctl', 'load', '/System/Library/LaunchDaemons/com.apple.audio.coreaudiod.plist'], check=False)
            print("Restarted macOS audio service")
            
        except Exception as e:
            print(f"Could not reset macOS audio: {e}")
    
    # On Linux, restart pulseaudio
    elif sys.platform.startswith("linux"):
        try:
            subprocess.run(['pulseaudio', '--kill'], check=False)
            time.sleep(1)
            subprocess.run(['pulseaudio', '--start'], check=False)
            print("Restarted PulseAudio")
        except Exception as e:
            print(f"Could not restart PulseAudio: {e}")

def create_audio_cleanup_html():
    """Create an HTML file that can be opened to clean up audio contexts."""
    
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Audio Cleanup</title>
</head>
<body>
    <h1>Audio Context Cleanup</h1>
    <p>This page will clean up any lingering audio contexts.</p>
    <button onclick="cleanupAudio()">Clean Up Audio</button>
    <div id="status"></div>
    
    <script>
        function cleanupAudio() {
            const status = document.getElementById('status');
            status.innerHTML = 'Cleaning up audio contexts...';
            
            // Close any existing audio contexts
            if (window.audioCtx) {
                try {
                    window.audioCtx.close();
                    console.log('Closed existing audio context');
                } catch (e) {
                    console.log('Audio context already closed');
                }
            }
            
            // Stop any oscillators
            if (window.oscillator) {
                try {
                    window.oscillator.stop();
                    window.oscillator.disconnect();
                    console.log('Stopped oscillator');
                } catch (e) {
                    console.log('Oscillator already stopped');
                }
            }
            
            // Clear any intervals
            for (let i = 1; i < 1000; i++) {
                window.clearInterval(i);
                window.clearTimeout(i);
            }
            
            status.innerHTML = 'Audio cleanup complete! You can close this tab now.';
            status.style.color = 'green';
        }
        
        // Auto-cleanup on page load
        window.addEventListener('load', function() {
            setTimeout(cleanupAudio, 1000);
        });
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {
            cleanupAudio();
        });
    </script>
</body>
</html>
"""
    
    with open('audio_cleanup.html', 'w') as f:
        f.write(html_content)
    
    print("📄 Created audio_cleanup.html - open this in your browser to clean up audio contexts")

def mute_system_volume():
    """Mute system volume on macOS"""
    try:
        # Set volume to 0 (mute)
        subprocess.run(['osascript', '-e', 'set volume output volume 0'], check=True)
        print("System volume muted")
    except Exception as e:
        print(f"Error muting system volume: {e}")

def main():
    """Main function to stop audio processes."""
    
    print("🔇 Audio Cleanup Script")
    print("=" * 40)
    
    # Stop audio processes
    stop_audio_processes()
    
    # Clear audio devices
    clear_audio_devices()
    
    # Create cleanup HTML
    create_audio_cleanup_html()
    
    # Mute system volume
    mute_system_volume()
    
    print("\n✅ Audio cleanup complete!")
    print("\n📋 Next steps:")
    print("1. Open audio_cleanup.html in your browser")
    print("2. Refresh any browser tabs with audio")
    print("3. Restart your Streamlit app")
    print("4. If buzzing persists, restart your computer")

if __name__ == "__main__":
    main() 