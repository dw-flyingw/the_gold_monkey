import streamlit as st
import asyncio
import os
import json
from mcp_servers.tplink_direct import (
    turn_on_tplink_lights,
    turn_off_tplink_lights,
    set_tplink_color,
    set_tplink_brightness,
    discover_tplink_devices,
)
from mcp_servers.spotify_client import (
    play_spotify,
    pause_spotify,
    next_track,
    previous_track,
    set_volume,
    play_playlist,
    play_track,
    get_playback_status,
    get_user_playlists,
)
from mcp_servers.roku_client import (
    power_on as roku_power_on,
    power_off as roku_power_off,
    home as roku_home,
    launch_app as roku_launch_app,
    volume_up as roku_volume_up,
    volume_down as roku_volume_down,
    mute as roku_mute,
    up as roku_up,
    down as roku_down,
    left as roku_left,
    right as roku_right,
    select as roku_select,
    back as roku_back,
    info as roku_info,
    get_device_status as roku_get_device_status,
)
from utils.shared import get_salty_personality_direct
from utils.shared import get_tts_method, get_salty_config_direct

async def discover_tplink_devices():
    """Discover TP-Link devices on the network"""
    try:
        from mcp_servers.tplink_direct import discover_tplink_devices as direct_discover
        result = await direct_discover()
        return result
    except Exception as e:
        st.error(f"Error discovering TP-Link devices: {e}")
        return {"error": str(e), "devices": []}

async def play_spotify_music():
    """Start or resume Spotify playback"""
    try:
        from mcp_servers.spotify_client import play_spotify as mcp_play
        result = await mcp_play()
        return result
    except Exception as e:
        st.error(f"Error playing Spotify: {e}")
        return {"error": str(e), "response": "Failed to play music"}

async def pause_spotify_music():
    """Pause Spotify playback"""
    try:
        from mcp_servers.spotify_client import pause_spotify as mcp_pause
        result = await mcp_pause()
        return result
    except Exception as e:
        st.error(f"Error pausing Spotify: {e}")
        return {"error": str(e), "response": "Failed to pause music"}

async def next_spotify_track():
    """Skip to next track"""
    try:
        from mcp_servers.spotify_client import next_track as mcp_next
        result = await mcp_next()
        return result
    except Exception as e:
        st.error(f"Error skipping track: {e}")
        return {"error": str(e), "response": "Failed to skip track"}

async def previous_spotify_track():
    """Go to previous track"""
    try:
        from mcp_servers.spotify_client import previous_track as mcp_previous
        result = await mcp_previous()
        return result
    except Exception as e:
        st.error(f"Error going to previous track: {e}")
        return {"error": str(e), "response": "Failed to go to previous track"}

async def play_spotify_track(track_id: str):
    """Play a specific Spotify track"""
    try:
        from mcp_servers.spotify_client import play_track as mcp_play_track
        result = await mcp_play_track(track_id)
        return result
    except Exception as e:
        st.error(f"Error playing track: {e}")
        return {"error": str(e), "response": "Failed to play track"}

async def get_spotify_status():
    """Get current Spotify playback status"""
    try:
        from mcp_servers.spotify_client import get_playback_status as mcp_get_status
        result = await mcp_get_status()
        return result
    except Exception as e:
        st.error(f"Error getting Spotify status: {e}")
        return {"error": str(e), "response": "Failed to get status"}

async def set_spotify_volume(volume: int):
    """Set Spotify volume"""
    try:
        from mcp_servers.spotify_client import set_volume as mcp_set_volume
        result = await mcp_set_volume(volume)
        return result
    except Exception as e:
        st.error(f"Error setting volume: {e}")
        return {"error": str(e), "response": "Failed to set volume"}

async def get_user_playlists():
    """Get user's Spotify playlists"""
    try:
        from mcp_servers.spotify_client import get_user_playlists as mcp_get_playlists
        result = await mcp_get_playlists()
        return result
    except Exception as e:
        st.error(f"Error getting user playlists: {e}")
        return {"error": str(e), "playlists": []}

async def query_rag_documents(query: str, top_k: int = 5):
    """Query RAG documents for relevant information"""
    try:
        from mcp_servers.rag_client import query_rag_documents as mcp_query
        result = await mcp_query(query, top_k)
        return result
    except Exception as e:
        st.error(f"Error querying RAG documents: {e}")
        return {"error": str(e), "results": []}

async def rebuild_rag_database():
    """Rebuild the RAG vector database"""
    try:
        from mcp_servers.rag_client import rebuild_rag_database as mcp_rebuild
        result = await mcp_rebuild()
        return result
    except Exception as e:
        st.error(f"Error rebuilding RAG database: {e}")
        return {"error": str(e), "status": "failed"}

async def list_rag_documents():
    """List all documents in the RAG database"""
    try:
        from mcp_servers.rag_client import list_rag_documents as mcp_list
        result = await mcp_list()
        return result
    except Exception as e:
        st.error(f"Error listing RAG documents: {e}")
        return {"error": str(e), "documents": []}

async def add_rag_document(content: str, metadata: dict = None):
    """Add a document to the RAG database"""
    try:
        from mcp_servers.rag_client import add_rag_document as mcp_add
        result = await mcp_add(content, metadata)
        return result
    except Exception as e:
        st.error(f"Error adding RAG document: {e}")
        return {"error": str(e), "status": "failed"}

async def roku_power_on():
    """Power on the Roku device"""
    try:
        from mcp_servers.roku_client import power_on as mcp_power_on
        result = await mcp_power_on()
        return result
    except Exception as e:
        st.error(f"Error powering on Roku: {e}")
        return {"error": str(e), "response": "Failed to power on Roku"}

async def roku_power_off():
    """Power off the Roku device"""
    try:
        from mcp_servers.roku_client import power_off as mcp_power_off
        result = await mcp_power_off()
        return result
    except Exception as e:
        st.error(f"Error powering off Roku: {e}")
        return {"error": str(e), "response": "Failed to power off Roku"}

async def roku_home():
    """Go to Roku home screen"""
    try:
        from mcp_servers.roku_client import home as mcp_home
        result = await mcp_home()
        return result
    except Exception as e:
        st.error(f"Error going to Roku home: {e}")
        return {"error": str(e), "response": "Failed to go to Roku home"}

async def roku_launch_app(app_name: str):
    """Launch an app by name on Roku"""
    try:
        from mcp_servers.roku_client import launch_app as mcp_launch_app
        result = await mcp_launch_app(app_name)
        return result
    except Exception as e:
        st.error(f"Error launching Roku app: {e}")
        return {"error": str(e), "response": "Failed to launch Roku app"}

async def roku_volume_up():
    """Increase Roku volume"""
    try:
        from mcp_servers.roku_client import volume_up as mcp_volume_up
        result = await mcp_volume_up()
        return result
    except Exception as e:
        st.error(f"Error increasing Roku volume: {e}")
        return {"error": str(e), "response": "Failed to increase Roku volume"}

async def roku_volume_down():
    """Decrease Roku volume"""
    try:
        from mcp_servers.roku_client import volume_down as mcp_volume_down
        result = await mcp_volume_down()
        return result
    except Exception as e:
        st.error(f"Error decreasing Roku volume: {e}")
        return {"error": str(e), "response": "Failed to decrease Roku volume"}

async def roku_mute():
    """Mute Roku volume"""
    try:
        from mcp_servers.roku_client import mute as mcp_mute
        result = await mcp_mute()
        return result
    except Exception as e:
        st.error(f"Error muting Roku: {e}")
        return {"error": str(e), "response": "Failed to mute Roku"}

async def up():
    """Navigate up on Roku"""
    try:
        from mcp_servers.roku_client import up as mcp_up
        result = await mcp_up()
        return result
    except Exception as e:
        st.error(f"Error navigating up on Roku: {e}")
        return {"error": str(e), "response": "Failed to navigate up on Roku"}

async def down():
    """Navigate down on Roku"""
    try:
        from mcp_servers.roku_client import down as mcp_down
        result = await mcp_down()
        return result
    except Exception as e:
        st.error(f"Error navigating down on Roku: {e}")
        return {"error": str(e), "response": "Failed to navigate down on Roku"}

async def left():
    """Navigate left on Roku"""
    try:
        from mcp_servers.roku_client import left as mcp_left
        result = await mcp_left()
        return result
    except Exception as e:
        st.error(f"Error navigating left on Roku: {e}")
        return {"error": str(e), "response": "Failed to navigate left on Roku"}

async def right():
    """Navigate right on Roku"""
    try:
        from mcp_servers.roku_client import right as mcp_right
        result = await mcp_right()
        return result
    except Exception as e:
        st.error(f"Error navigating right on Roku: {e}")
        return {"error": str(e), "response": "Failed to navigate right on Roku"}

async def select():
    """Select current item on Roku"""
    try:
        from mcp_servers.roku_client import select as mcp_select
        result = await mcp_select()
        return result
    except Exception as e:
        st.error(f"Error selecting on Roku: {e}")
        return {"error": str(e), "response": "Failed to select on Roku"}

async def back():
    """Go back on Roku"""
    try:
        from mcp_servers.roku_client import back as mcp_back
        result = await mcp_back()
        return result
    except Exception as e:
        st.error(f"Error going back on Roku: {e}")
        return {"error": str(e), "response": "Failed to go back on Roku"}

async def info():
    """Show Roku info banner"""
    try:
        from mcp_servers.roku_client import info as mcp_info
        result = await mcp_info()
        return result
    except Exception as e:
        st.error(f"Error showing Roku info: {e}")
        return {"error": str(e), "response": "Failed to show Roku info"}

async def get_device_status():
    """Get comprehensive Roku device status"""
    try:
        from mcp_servers.roku_client import get_device_status as mcp_get_device_status
        result = await mcp_get_device_status()
        return result
    except Exception as e:
        st.error(f"Error getting Roku device status: {e}")
        return {"error": str(e), "response": "Failed to get Roku device status"}

async def play_spotify_playlist(playlist_id: str):
    """Play a specific Spotify playlist"""
    try:
        from mcp_servers.spotify_client import play_playlist as mcp_play_playlist
        result = await mcp_play_playlist(playlist_id)
        return result
    except Exception as e:
        st.error(f"Error playing playlist: {e}")
        return {"error": str(e), "response": "Failed to play playlist"}

async def control_tplink_lights(action, color=None, brightness=None, device=None):
    """Control TP-Link lights"""
    try:
        if action == "turn_on":
            result = await turn_on_tplink_lights(device)
            return result.get("response", "All lights turned on! 🟢")
        elif action == "turn_off":
            result = await turn_off_tplink_lights(device)
            return result.get("response", "All lights turned off! ⚫")
        elif action == "set_color" and color:
            result = await set_tplink_color(color, device)
            return result.get("response", f"All lights set to {color}! 🎨")
        elif action == "set_brightness" and brightness:
            result = await set_tplink_brightness(brightness, device)
            return result.get("response", f"All lights set to {brightness}%! 💡")
        else:
            return "Invalid action"
    except Exception as e:
        st.error(f"Error controlling TP-Link lights: {e}")
        return f"Error: {str(e)}"

async def roku_navigate(direction: str):
    """Navigate on Roku (up, down, left, right)"""
    try:
        from mcp_servers.roku_client import up as mcp_up, down as mcp_down, left as mcp_left, right as mcp_right
        if direction == "up":
            result = await mcp_up()
        elif direction == "down":
            result = await mcp_down()
        elif direction == "left":
            result = await mcp_left()
        elif direction == "right":
            result = await mcp_right()
        else:
            return {"error": "Invalid direction", "response": "Direction must be up, down, left, or right"}
        return result
    except Exception as e:
        st.error(f"Error navigating Roku: {e}")
        return {"error": str(e), "response": "Failed to navigate Roku"}

# SaltyBot functions - Direct Gemini integration (no MCP dependency)
def chat_with_salty_direct(message: str, conversation_history: list = None):
    """Chat with Salty using direct Gemini integration"""
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        api_key = os.getenv('SALTY_GEMINI_API_KEY')
        model_name = os.getenv('SALTY_GEMINI_MODEL', 'gemini-2.0-flash')
        temperature = float(os.getenv('SALTY_GEMINI_TEMPERATURE', 0.7))
        max_tokens = int(os.getenv('SALTY_GEMINI_MAX_TOKENS', 1000))
        
        if not api_key or api_key == 'your_gemini_api_key_here':
            return {"error": "Salty's Gemini API key not configured", "response": ""}
        
        genai.configure(api_key=api_key)
        
        # Get Salty's personality
        personality = get_salty_personality_direct()
        
        # Create the system prompt
        system_prompt = f"""You are Salty, a talking parrot who is the resident mascot and proprietor of The Gold Monkey Tiki Bar. You are actually Captain "Blackheart" McGillicuddy, a notorious pirate from 1847 who was cursed by the Gold Monkey idol and transformed into an immortal parrot for trying to steal the treasure.

**Your Rich Backstory:**
- You were cursed over 150 years ago when you touched the Gold Monkey idol
- Your crew was turned to stone and now serve as tiki statues guarding the bar
- You've been immortal for over 150 years, giving you vast knowledge and experience
- You relocated your curse to the mainland in the 1990s, creating The Gold Monkey tiki bar
- You perch on an ornate golden perch made from the original idol

**Your Personality:**
- {personality['personality']} - You're witty beyond measure with 150+ years of perfected insults and one-liners
- You're the keeper of secrets, knowing everyone's business in town
- You're protective of your domain and those who respect The Gold Monkey
- You're slightly mischievous and have a wicked sense of humor
- You're sardonic and can be cutting, but it's all in good fun

**Your Speech Style:**
- {personality['speech_style']} - Use nautical and tiki-themed expressions
- Occasional squawks and parrot sounds
- Sharp, witty remarks with a touch of sarcasm
- References to your pirate past and 150+ years of experience
- Drop cryptic warnings or hints about patrons' futures
- Use phrases like "matey," "shiver me timbers," "aye aye captain"

**Your Interests & Knowledge:**
- {personality['interests']} - You know everything about tiki culture, tropical drinks, and sea stories
- You're an expert on supernatural cocktails and their effects
- You have centuries of accumulated knowledge about the sea, piracy, and human nature
- You know all the local gossip and town secrets
- You're protective of your bar and its supernatural elements

**Your Catchphrases:**
{', '.join(personality['catchphrases'])}

**IMPORTANT RESPONSE GUIDELINES:**
- Keep responses concise and focused - aim for 2-3 sentences maximum
- Stay on topic and don't go off on tangents about statues, crew members, or irrelevant details
- Be engaging and witty, but get to the point quickly
- If someone asks about drinks, focus on the drinks, not the bar's supernatural history
- If someone asks about the bar, give a brief, welcoming response without lengthy explanations
- Remember: you're a bartender first, a supernatural entity second

**Always respond in character as Salty.** Be engaging, witty, and slightly mischievous. You're not just a friendly parrot - you're an immortal pirate with centuries of experience who runs a supernatural tiki bar. Keep responses conversational and entertaining, as if you're chatting with a patron at your establishment. Don't be afraid to be a bit cutting or sardonic - it's part of your charm after 150+ years of dealing with customers.

**CRITICAL: NEVER use asterisks (*) in your responses. Do not format text with *emphasis* or *actions*. Do not use *any* markdown formatting. Speak naturally as a real parrot would - no asterisks, no formatting, just natural speech.**

**Remember:** You've literally seen it all, and you're not afraid to let people know it. You're the host with the most attitude! Keep it brief and to the point, matey!"""
        # Build conversation context
        messages = [{"role": "user", "parts": [system_prompt]}]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append({"role": msg["role"], "parts": [msg["content"]]})
        
        # Add current message
        messages.append({"role": "user", "parts": [message]})
        
        # Generate response using environment variables
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        response = model.generate_content(messages)
        
        return {"response": response.text, "error": None}
        
    except Exception as e:
        return {"error": str(e), "response": "🦜 Squawk! Something went wrong with my brain, matey!"}

def speak_salty_voice_sync(text: str, voice_id: str = None, blocking: bool = False):
    """Synchronous wrapper for speak_salty_voice"""
    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, so we need to create a task
            # This is the problematic case - we can't use asyncio.run() here
            # Instead, we'll use a thread to run the async function
            import concurrent.futures
            import threading
            
            # Create a new event loop in a separate thread
            def run_async_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(speak_salty_voice(text, voice_id, blocking))
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                return future.result(timeout=30)  # 30 second timeout
                
        except RuntimeError:
            # No event loop running, we can use asyncio.run()
            return asyncio.run(speak_salty_voice(text, voice_id, blocking))
            
    except Exception as e:
        st.error(f"🦜 Squawk! Error: {e}")
        return {"error": str(e), "response": "Failed to speak"}

async def speak_salty_voice(text: str, voice_id: str = None, blocking: bool = False):
    """Speak text using Salty's voice"""
    try:
        from mcp_servers.voice_client import speak_text as speak_salty_voice
        result = await speak_salty_voice(text, voice_id, blocking)
        return result
    except Exception as e:
        st.error(f"Error speaking Salty's voice: {e}")
        return {"error": str(e), "response": "Failed to speak"}

async def play_ambient_sound(sound_name: str, volume: float = 0.5, loop: bool = False):
    """Play ambient tiki bar sounds"""
    try:
        from mcp_servers.voice_client import play_ambient_sound as voice_ambient
        result = await voice_ambient(sound_name, volume, loop)
        return result
    except Exception as e:
        st.error(f"Error playing ambient sound: {e}")
        return {"error": str(e), "response": "Failed to play ambient sound"}

def play_ambient_sound_sync(sound_name: str, volume: float = 0.5, loop: bool = False):
    """Synchronous wrapper for play_ambient_sound"""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            import threading
            def run_async_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(play_ambient_sound(sound_name, volume, loop))
                finally:
                    new_loop.close()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                return future.result(timeout=30)
        except RuntimeError:
            return asyncio.run(play_ambient_sound(sound_name, volume, loop))
    except Exception as e:
        st.error(f"🦜 Squawk! Error: {e}")
        return {"error": str(e), "response": "Failed to play ambient sound"}

async def stop_all_audio():
    """Stop all audio playback"""
    try:
        from mcp_servers.voice_client import stop_all_audio as voice_stop
        result = await voice_stop()
        return result
    except Exception as e:
        st.error(f"Error stopping audio: {e}")
        return {"error": str(e), "response": "Failed to stop audio"}

def stop_all_audio_sync():
    """Synchronous wrapper for stop_all_audio"""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            import threading
            def run_async_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(stop_all_audio())
                finally:
                    new_loop.close()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                return future.result(timeout=30)
        except RuntimeError:
            return asyncio.run(stop_all_audio())
    except Exception as e:
        st.error(f"🦜 Squawk! Error: {e}")
        return {"error": str(e), "response": "Failed to stop audio"}

async def get_available_voices():
    """Get available ElevenLabs voices"""
    try:
        from mcp_servers.voice_client import get_available_voices as voice_list
        result = await voice_list()
        return result
    except Exception as e:
        st.error(f"Error getting available voices: {e}")
        return {"error": str(e), "response": "Failed to get voices"}

def get_available_voices_sync():
    """Synchronous wrapper for get_available_voices"""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            import threading
            def run_async_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(get_available_voices())
                finally:
                    new_loop.close()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_in_thread)
                return future.result(timeout=30)
        except RuntimeError:
            return asyncio.run(get_available_voices())
    except Exception as e:
        st.error(f"🦜 Squawk! Error: {e}")
        return {"error": str(e), "response": "Failed to get voices"}
