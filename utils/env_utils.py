#!/usr/bin/env python3
"""
Minimal environment variable helpers for Salty

This module provides a simple, consistent way to access key environment variables
used throughout the Salty project. It expects variables to be set in a .env file
or in the system environment. All helpers provide sensible defaults.

Environment variables used:
- TTS_METHOD: Which text-to-speech engine to use (e.g., 'gtts', 'elevenlabs', 'none')
- VOICE_SERVER_URL: URL for the voice server (default: http://localhost:9006)
- ELEVENLABS_API_KEY: API key for ElevenLabs voice synthesis
- ELEVENLABS_VOICE_ID: Voice ID for ElevenLabs (default: pNInz6obpgDQGcFmaJgB)

Usage example:
    from utils.env_utils import get_tts_method, get_voice_server_url, get_elevenlabs_config
    tts_method = get_tts_method()  # e.g., 'elevenlabs'
    voice_url = get_voice_server_url()  # e.g., 'http://localhost:9006'
    elevenlabs = get_elevenlabs_config()  # dict with 'api_key' and 'voice_id'
"""
import os

def get_tts_method() -> str:
    """Get TTS method from environment"""
    return os.getenv('TTS_METHOD', 'gtts').lower()

def get_voice_server_url() -> str:
    """Get voice server URL from environment"""
    return os.getenv('VOICE_SERVER_URL', 'http://localhost:9006')

def get_elevenlabs_config() -> dict:
    """Get ElevenLabs configuration from environment"""
    return {
        'api_key': os.getenv('ELEVENLABS_API_KEY'),
        'voice_id': os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')
    } 