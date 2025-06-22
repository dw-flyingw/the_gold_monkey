#!/usr/bin/env python3
"""
Ambient Sound Generator for Salty
Creates ambient tiki bar sounds using audio synthesis
"""

import numpy as np
import soundfile as sf
from pathlib import Path
import os

def create_ocean_waves(duration=30, sample_rate=44100):
    """Create ocean wave sounds"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Multiple wave frequencies
    wave1 = 0.3 * np.sin(2 * np.pi * 0.1 * t)  # Slow waves
    wave2 = 0.2 * np.sin(2 * np.pi * 0.3 * t)  # Medium waves
    wave3 = 0.1 * np.sin(2 * np.pi * 0.7 * t)  # Fast waves
    
    # Add some randomness
    noise = 0.05 * np.random.randn(len(t))
    
    # Combine waves
    ocean = wave1 + wave2 + wave3 + noise
    
    # Fade in/out
    fade_samples = int(0.5 * sample_rate)
    ocean[:fade_samples] *= np.linspace(0, 1, fade_samples)
    ocean[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    return ocean

def create_jungle_birds(duration=30, sample_rate=44100):
    """Create jungle bird sounds"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Bird chirps at different frequencies
    bird_sounds = []
    
    # Create several bird chirps
    for i in range(10):
        start_time = np.random.uniform(0, duration - 2)
        chirp_duration = np.random.uniform(0.5, 2.0)
        frequency = np.random.uniform(800, 2000)
        
        chirp_t = np.linspace(0, chirp_duration, int(sample_rate * chirp_duration))
        chirp = 0.2 * np.sin(2 * np.pi * frequency * chirp_t)
        
        # Add some variation
        chirp *= np.exp(-chirp_t / chirp_duration)
        
        # Place in timeline
        start_sample = int(start_time * sample_rate)
        end_sample = start_sample + len(chirp)
        
        if end_sample <= len(t):
            bird_sounds.append((start_sample, end_sample, chirp))
    
    # Combine all bird sounds
    jungle = np.zeros(len(t))
    for start, end, chirp in bird_sounds:
        jungle[start:end] += chirp
    
    # Add some background noise
    background = 0.02 * np.random.randn(len(t))
    jungle += background
    
    return jungle

def create_tiki_drums(duration=30, sample_rate=44100):
    """Create tiki drum sounds"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Drum pattern
    drums = np.zeros(len(t))
    
    # Bass drum pattern
    bass_pattern = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]  # Every 0.5 seconds
    for beat_time in bass_pattern:
        if beat_time < duration:
            beat_sample = int(beat_time * sample_rate)
            # Bass drum sound
            drum_sound = 0.4 * np.exp(-np.linspace(0, 0.1, int(0.1 * sample_rate)))
            end_sample = min(beat_sample + len(drum_sound), len(drums))
            drums[beat_sample:end_sample] += drum_sound[:end_sample - beat_sample]
    
    # High hat pattern
    hat_pattern = [0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75]  # Off-beats
    for beat_time in hat_pattern:
        if beat_time < duration:
            beat_sample = int(beat_time * sample_rate)
            # High hat sound
            hat_sound = 0.2 * np.exp(-np.linspace(0, 0.05, int(0.05 * sample_rate)))
            end_sample = min(beat_sample + len(hat_sound), len(drums))
            drums[beat_sample:end_sample] += hat_sound[:end_sample - beat_sample]
    
    return drums

def create_ship_bells(duration=30, sample_rate=44100):
    """Create ship bell sounds"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    bells = np.zeros(len(t))
    
    # Bell pattern (like a ship's bell)
    bell_times = [0, 5, 10, 15, 20, 25]  # Every 5 seconds
    
    for bell_time in bell_times:
        if bell_time < duration:
            bell_sample = int(bell_time * sample_rate)
            
            # Bell sound (harmonic)
            bell_duration = 3.0
            bell_t = np.linspace(0, bell_duration, int(sample_rate * bell_duration))
            
            # Multiple harmonics for bell sound
            bell = (0.3 * np.sin(2 * np.pi * 440 * bell_t) +  # A4
                   0.2 * np.sin(2 * np.pi * 880 * bell_t) +  # A5
                   0.1 * np.sin(2 * np.pi * 1320 * bell_t))  # E6
            
            # Bell envelope
            bell *= np.exp(-bell_t / bell_duration)
            
            end_sample = min(bell_sample + len(bell), len(bells))
            bells[bell_sample:end_sample] += bell[:end_sample - bell_sample]
    
    return bells

def create_parrot_squawk(duration=30, sample_rate=44100):
    """Create parrot squawk sounds"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    squawks = np.zeros(len(t))
    
    # Squawk pattern
    squawk_times = [2, 8, 15, 22, 28]  # Random squawks
    
    for squawk_time in squawk_times:
        if squawk_time < duration:
            squawk_sample = int(squawk_time * sample_rate)
            
            # Squawk sound
            squawk_duration = 1.0
            squawk_t = np.linspace(0, squawk_duration, int(sample_rate * squawk_duration))
            
            # Parrot squawk (high frequency, noisy)
            frequency = np.random.uniform(800, 1500)
            squawk = 0.3 * np.sin(2 * np.pi * frequency * squawk_t)
            
            # Add noise for authenticity
            noise = 0.1 * np.random.randn(len(squawk_t))
            squawk += noise
            
            # Squawk envelope
            squawk *= np.exp(-squawk_t / squawk_duration)
            
            end_sample = min(squawk_sample + len(squawk), len(squawks))
            squawks[squawk_sample:end_sample] += squawk[:end_sample - squawk_sample]
    
    return squawks

def main():
    """Generate all ambient sounds"""
    # Create audio directory if it doesn't exist
    audio_dir = Path(__file__).parent.parent / "audio"
    audio_dir.mkdir(exist_ok=True)
    
    sample_rate = 44100
    duration = 30  # 30 seconds
    
    print("🎵 Generating ambient tiki bar sounds...")
    
    # Generate ocean waves
    print("🌊 Creating ocean waves...")
    ocean = create_ocean_waves(duration, sample_rate)
    sf.write(audio_dir / "ocean_waves.wav", ocean, sample_rate)
    
    # Generate jungle birds
    print("🐦 Creating jungle birds...")
    birds = create_jungle_birds(duration, sample_rate)
    sf.write(audio_dir / "jungle_birds.wav", birds, sample_rate)
    
    # Generate tiki drums
    print("🥁 Creating tiki drums...")
    drums = create_tiki_drums(duration, sample_rate)
    sf.write(audio_dir / "tiki_drums.wav", drums, sample_rate)
    
    # Generate ship bells
    print("🔔 Creating ship bells...")
    bells = create_ship_bells(duration, sample_rate)
    sf.write(audio_dir / "ship_bells.wav", bells, sample_rate)
    
    # Generate parrot squawks
    print("🦜 Creating parrot squawks...")
    squawks = create_parrot_squawk(duration, sample_rate)
    sf.write(audio_dir / "parrot_squawk.wav", squawks, sample_rate)
    
    print("✅ All ambient sounds generated successfully!")
    print(f"📁 Files saved to: {audio_dir}")
    
    # List generated files
    for file in audio_dir.glob("*.wav"):
        size = file.stat().st_size / 1024  # KB
        print(f"  • {file.name} ({size:.1f} KB)")

if __name__ == "__main__":
    main() 