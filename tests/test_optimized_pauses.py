#!/usr/bin/env python3
"""
Test script for optimized pause timing in voice synthesis
Demonstrates the improved natural speech patterns
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_servers.voice_server import VoiceServer

async def test_optimized_pauses():
    """Test the optimized pause timing for natural speech"""
    print("🎤 Testing Optimized Pause Timing for Natural Speech")
    print("=" * 60)
    
    # Create a voice server instance for testing
    voice_server = VoiceServer()
    
    # Test cases with different sentence types
    test_texts = [
        # Regular sentences with periods
        "Welcome to The Gold Monkey. This is your favorite tiki bar. I'm Salty, your host.",
        
        # Questions and exclamations
        "How are you doing today? I'm excited to see you! What would you like to drink?",
        
        # Mixed sentence types
        "Ahoy there, matey! Welcome to our tropical paradise. Are you ready for some fun? The drinks are flowing and the music is playing!",
        
        # Joke with optimized timing
        "Why did the parrot go to the doctor? Because it was feeling a bit under the weather!",
        
        # Conversational flow
        "The weather is perfect today. I can see the palm trees swaying. Would you like to sit outside? The ocean breeze is wonderful!",
        
        # Multiple questions
        "What's your name? Where are you from? How long are you staying? I hope you enjoy your visit!"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Testing: {text}")
        print("-" * 40)
        
        # Process the text to show the timing breakdown
        parts = await voice_server.process_text_with_squawks(text)
        
        total_duration = 0
        for part in parts:
            if part['type'] == 'text':
                print(f"   Speak: '{part['content']}'")
            elif part['type'] == 'pause':
                print(f"   Pause: {part['duration']:.2f}s")
                total_duration += part['duration']
            elif part['type'] in ['squawk', 'screech']:
                print(f"   Sound: {part['type']}")
        
        print(f"   Total pause time: {total_duration:.2f}s")
        
        # Actually speak the text (optional - uncomment to hear it)
        # result = await voice_server.speak_text(text, blocking=False)
        # print(f"   Result: {result}")
        
        # Small pause between tests
        await asyncio.sleep(1)

def show_pause_optimization_summary():
    """Show a summary of the pause optimization changes"""
    print("\n📊 Pause Optimization Summary")
    print("=" * 40)
    print("Previous vs Optimized Pause Durations:")
    print()
    print("Regular sentences (ending with .):")
    print("  Before: 0.5s → After: 0.25s (50% reduction)")
    print()
    print("Exclamations (ending with !):")
    print("  Before: 0.8s → After: 0.3s (62.5% reduction)")
    print()
    print("Questions (ending with ?):")
    print("  Before: 0.8s → After: 0.4s (50% reduction)")
    print()
    print("Joke dramatic pauses:")
    print("  Before: 2.0s → After: 1.2s (40% reduction)")
    print()
    print("Base audio delay:")
    print("  Before: 0.2s → After: 0.15s (25% reduction)")
    print()
    print("Benefits:")
    print("✅ More natural conversational flow")
    print("✅ Better engagement and responsiveness")
    print("✅ Maintains appropriate pauses for questions")
    print("✅ Preserves comedic timing for jokes")
    print("✅ Reduces overall speech duration")
    print("✅ Improves listener experience")

if __name__ == "__main__":
    show_pause_optimization_summary()
    asyncio.run(test_optimized_pauses()) 