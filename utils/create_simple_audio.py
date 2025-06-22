#!/usr/bin/env python3
"""
Simple Audio Generator for Salty
Creates basic ambient sound files using only built-in libraries
"""

import wave
import struct
import math
import random
from pathlib import Path

def create_simple_wave(filename, frequency=440, duration=5, sample_rate=44100):
    """Create a simple sine wave audio file"""
    # Create audio directory if it doesn't exist
    audio_dir = Path(__file__).parent.parent / "audio"
    audio_dir.mkdir(exist_ok=True)
    
    # Generate sine wave
    num_samples = int(duration * sample_rate)
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        # Simple sine wave with fade in/out
        amplitude = 0.3
        if i < sample_rate:  # Fade in first second
            amplitude *= i / sample_rate
        if i > num_samples - sample_rate:  # Fade out last second
            amplitude *= (num_samples - i) / sample_rate
        
        sample = amplitude * math.sin(2 * math.pi * frequency * t)
        samples.append(int(sample * 32767))  # Convert to 16-bit integer
    
    # Write WAV file
    with wave.open(str(audio_dir / filename), 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Pack samples into bytes
        data = struct.pack('<%dh' % len(samples), *samples)
        wav_file.writeframes(data)
    
    print(f"Created {filename}")

def main():
    """Create simple ambient sound files"""
    print("🎵 Creating simple ambient sounds...")
    
    # Create ocean waves (low frequency)
    create_simple_wave("ocean_waves.wav", frequency=50, duration=10)
    
    # Create jungle birds (high frequency)
    create_simple_wave("jungle_birds.wav", frequency=800, duration=10)
    
    # Create tiki drums (medium frequency)
    create_simple_wave("tiki_drums.wav", frequency=200, duration=10)
    
    # Create ship bells (harmonic frequencies)
    create_simple_wave("ship_bells.wav", frequency=440, duration=10)
    
    print("✅ Simple ambient sounds created!")
    print("📁 Files saved to: audio/")

if __name__ == "__main__":
    main() 