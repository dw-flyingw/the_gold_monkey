from utils.shared import set_page_config, show_page_header
import streamlit as st
import os
import asyncio
import concurrent.futures
from mcp_servers.saltybot_client import chat_with_salty
from utils.shared import get_salty_personality_direct
from utils.shared import get_tts_method, get_salty_config_direct
from utils.actions import speak_salty_voice_sync
from utils.mcp_error_handler import handle_mcp_error, is_mcp_error
from utils.streamlit_async import safe_async_call

# Import the voice control functionality
from pages.subpages.voice_control import show_voice_control

def show_chatbot():
    set_page_config()
    show_page_header("🦜 Salty the Talking Parrot", "Your favorite feathered friend from The Gold Monkey Tiki Bar")
    
    # Create tabs for navigation
    tab1, tab2 = st.tabs(["💬 Chat with Salty", "🎤 Voice Control"])
    
    with tab1:
        show_chat_interface()
    
    with tab2:
        show_voice_control()

def show_chat_interface():
    # Get configuration and personality directly
    config = get_salty_config_direct()
    salty = get_salty_personality_direct()
    
    # Check if Gemini is configured
    if not config.get('is_configured', False):
        st.error("⚠️ Please set your SALTY_GEMINI_API_KEY in the .env file")
        st.info("""
        ### Setup Instructions:
        1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Update the `.env` file with your API key:
           ```
           SALTY_GEMINI_API_KEY=your_actual_api_key_here
           ```
        3. Restart the app
        """)
        return
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add initial greeting from Salty
        if salty.get('catchphrases'):
            initial_greeting = f"🦜 {salty['catchphrases'][0]} I'm Salty, the resident talking parrot at The Gold Monkey Tiki Bar! What can I squawk about for you today, matey?"
        else:
            initial_greeting = "🦜 Squawk! Welcome to The Gold Monkey! I'm Salty, the resident talking parrot. What can I help you with today, matey?"
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": initial_greeting
        })
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Chat with Salty..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Use safe async call for Streamlit
                result = safe_async_call(chat_with_salty, prompt, st.session_state.messages)
                
                if result.get("fallback"):
                    # Show a friendly fallback message
                    fallback_msg = result.get("response", "🦜 Squawk! MCP communication issue, fallback mode engaged!")
                    message_placeholder.error(fallback_msg)
                    st.session_state.messages.append({"role": "assistant", "content": fallback_msg})
                elif result.get("error"):
                    error_message = f"🦜 Squawk! Something went wrong: {result['error']}"
                    message_placeholder.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                else:
                    # Display the response
                    response_text = result.get("response", "🦜 Squawk! I'm not sure what to say to that, matey!")
                    message_placeholder.markdown(response_text)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                    # Check if voice is enabled (both toggle and environment variable)
                    voice_enabled = st.session_state.get('voice_enabled', True)
                    tts_method = get_tts_method()
                    
                    if voice_enabled and tts_method != 'none':
                        # Extract just the text content (remove emojis and formatting for speech)
                        speech_text = response_text
                        # Remove emoji prefixes and markdown formatting
                        if speech_text.startswith("🦜 "):
                            speech_text = speech_text[2:]  # Remove the parrot emoji
                        # Clean up any remaining markdown
                        speech_text = speech_text.replace("*", "").replace("**", "")
                        
                        # Speak the response (blocking so the UI waits for speech to complete)
                        try:
                            speak_salty_voice_sync(speech_text, blocking=True)
                        except Exception as e:
                            st.warning(f"Voice synthesis failed: {e}")
                    elif not voice_enabled:
                        # Voice is disabled by user toggle
                        pass
                    else:
                        # Voice is disabled by environment variable
                        pass
            except Exception as e:
                if is_mcp_error(e):
                    err = handle_mcp_error(e, "chat_with_salty Streamlit page")
                    fallback_msg = err.get("response", f"🦜 Squawk! MCP communication issue: {e}")
                    message_placeholder.error(fallback_msg)
                    st.session_state.messages.append({"role": "assistant", "content": fallback_msg})
                else:
                    error_message = f"🦜 Squawk! Something went wrong: {str(e)}"
                    message_placeholder.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("🦜 Salty's Perch")
        
        # Display Salty's character info
        st.markdown("**About Salty:**")
        st.write(f"🏴‍☠️ {salty.get('character', 'Talking Parrot')}")
        st.write(f"🏝️ {salty.get('location', 'The Gold Monkey Tiki Bar')}")
        st.write(f"🎭 {salty.get('personality', 'Friendly and witty')}")
        
        st.markdown("---")
        
        # Voice control settings
        st.subheader("🗣️ Voice Settings")
        
        # Voice toggle - store in session state
        if "voice_enabled" not in st.session_state:
            st.session_state.voice_enabled = True  # Default to enabled
        
        voice_toggle = st.toggle(
            "🎤 Enable Voice", 
            value=st.session_state.voice_enabled,
            help="Turn Salty's voice on or off"
        )
        
        # Update session state when toggle changes
        if voice_toggle != st.session_state.voice_enabled:
            st.session_state.voice_enabled = voice_toggle
            if voice_toggle:
                st.success("🎤 Voice enabled! Salty will speak his responses.")
            else:
                st.info("🔇 Voice disabled. Salty will respond silently.")
        
        # Get TTS method from environment variable
        tts_method = get_tts_method()
        
        # Display current TTS method
        if tts_method == 'none':
            st.info("ℹ️ Voice is disabled - Salty will not speak")
        elif tts_method == 'gtts':
            st.info("ℹ️ Using Google Text-to-Speech (free, no API key required)")
        elif tts_method == 'elevenlabs':
            if not os.getenv('ELEVENLABS_API_KEY'):
                st.warning("⚠️ ElevenLabs API key not found in .env file")
            else:
                st.success("✅ ElevenLabs API key configured")
        else:
            st.warning(f"⚠️ Unknown TTS method: {tts_method}")
        
        st.markdown("---")
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Configuration:**")
        st.write(f"Model: {config.get('model', 'gemini-2.0-flash')}")
        st.write(f"Temperature: {config.get('temperature', 0.7)}")
        st.write(f"Max Tokens: {config.get('max_tokens', 1000)}")
        
        st.markdown("---")
        st.markdown("**Environment Variables:**")
        st.code(f"""
SALTY_GEMINI_API_KEY: {'✅ Set' if config.get('is_configured') else '❌ Not set'}
SALTY_GEMINI_MODEL: {config.get('model', 'gemini-2.0-flash')}
SALTY_GEMINI_TEMPERATURE: {config.get('temperature', 0.7)}
SALTY_GEMINI_MAX_TOKENS: {config.get('max_tokens', 1000)}
TTS_METHOD: {tts_method}
        """)
        
        st.markdown("---")
        st.markdown("**Tiki Bar Features:**")
        st.write("Your `.env` file also contains:")
        st.write("• 🎵 Spotify API (for tiki music)")
        st.write("• 🎭 Eleven Labs (for voice)")
        st.write("• 🤖 Smart home controls")
        st.write("• 🏠 TP-Link lighting")

if __name__ == "__main__":
    show_chatbot()
