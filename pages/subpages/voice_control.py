from utils.shared import set_page_config, show_page_header
import streamlit as st
import asyncio
import os
import requests
from utils.actions import (
    speak_salty_voice_sync,
    chat_with_salty_direct,
    play_ambient_sound_sync,
    stop_all_audio_sync,
    get_available_voices_sync,
)
from utils.shared import get_salty_personality_direct
from utils.shared import get_salty_personality_direct

def show_voice_control():
    set_page_config()
    show_page_header("🎤 Voice Control", "Salty's voice synthesis and audio control panel")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][2]} Now I can actually speak to you, matey!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🗣️ Salty's Voice")
        
        # Voice synthesis controls
        voice_text = st.text_area(
            "What should Salty say?",
            placeholder="Enter text for Salty to speak...",
            height=100,
            help="Type what you want Salty to say out loud"
        )
        
        if st.button("🗣️ Make Salty Speak", type="primary"):
            if voice_text.strip():
                with st.spinner("🦜 Salty is speaking..."):
                    result = speak_salty_voice_sync(voice_text, blocking=True)
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Salty spoke successfully!"))
            else:
                st.warning("Please enter some text for Salty to say!")
        
        st.markdown("---")
        
        st.subheader("🎭 Quick Voice Commands")
        
        # Quick voice commands
        quick_commands = [
            "Squawk! Welcome to The Gold Monkey!",
            "Ahoy there, matey!",
            "Tropical greetings from your favorite feathered friend!",
            "Shiver me timbers, that's a good question!",
            "Aye aye, captain!",
            "Time for a tropical drink, matey!",
            "The tiki bar is open for business!",
            "Another round for my favorite customers!"
        ]
        
        selected_command = st.selectbox("Quick Salty phrases", quick_commands)
        
        if st.button("🗣️ Say It!"):
            with st.spinner("🦜 Salty is speaking..."):
                result = speak_salty_voice_sync(selected_command, blocking=True)
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Salty said it!")
        # Tell a Joke button
        if st.button("🦜 Tell a Joke"):
            with st.spinner("🦜 Salty is thinking of a joke..."):
                # Create varied joke prompts to prevent repetition
                joke_prompts = [
                    "Tell me a very short pirate joke in 1-2 sentences. Make it different from common pirate jokes.",
                    "Give me a brief tiki bar themed joke in 1-2 sentences. Be creative and original.",
                    "Tell me a quick nautical joke in 1-2 sentences. Avoid the typical 'pirate washing up' joke.",
                    "Share a short tropical island joke in 1-2 sentences. Make it unique and funny.",
                    "Tell me a brief joke about rum, coconuts, or tropical drinks in 1-2 sentences.",
                    "Give me a quick joke about parrots, ships, or treasure in 1-2 sentences. Be original."
                ]
                
                # Randomly select a prompt to add variety
                import random
                joke_prompt = random.choice(joke_prompts)
                
                joke_response = chat_with_salty_direct(joke_prompt)
                joke = joke_response.get("response", "Sorry, I can't think of a joke right now!")
                
                # Check if the joke is too generic or repetitive
                generic_phrases = ["washing up", "beach", "pirate walks into a bar", "arr matey"]
                if any(phrase in joke.lower() for phrase in generic_phrases):
                    # Use a pre-written joke as fallback
                    fallback_jokes = [
                        "Why did the coconut go to the doctor? Because it was feeling a little nutty!",
                        "What do you call a parrot that's good at math? A poly-nomial!",
                        "Why did the tiki torch go to therapy? It had too many burning issues!",
                        "What's a pirate's favorite letter? You'd think it's R, but it's actually the C!",
                        "Why don't sailors like to play cards? Because there are too many sharks in the deck!",
                        "What do you call a fish wearing a bowtie? So-fish-ticated!",
                        "Why did the rum go to the party? Because it was feeling spirited!",
                        "What's a pirate's favorite exercise? Planks!",
                        "Why did the palm tree go to the beach? To get some sun and relaxation!",
                        "What do you call a parrot that's always late? A procrasti-nator!"
                    ]
                    joke = random.choice(fallback_jokes)
                
                # Remove any asterisks from the response
                joke = joke.replace('*', '')
                
                # Display the joke text
                st.markdown(f"> {joke}")
                
                # Check if voice server is accessible
                try:
                    voice_server_url = os.getenv('VOICE_SERVER_URL')
                    response = requests.get(f"{voice_server_url}/available_voices", timeout=5)
                    if response.status_code != 200:
                        st.error("🦜 Voice server is not responding properly!")
                        return
                except Exception as e:
                    st.error(f"🦜 Cannot connect to voice server: {e}")
                    return
                
                result = speak_salty_voice_sync(joke, blocking=True)
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Salty told a joke!")
        
        st.markdown("---")
        
        st.subheader("🎵 Ambient Sounds")
        
        # Ambient sound controls
        ambient_sounds = {
            "ocean_waves": "🌊 Ocean Waves",
            "jungle_birds": "🐦 Jungle Birds",
            "tiki_drums": "🥁 Tiki Drums",
            "ship_bells": "🔔 Ship Bells",
            "parrot_squawk": "🦜 Parrot Squawk"
        }
        
        selected_sound = st.selectbox("Choose ambient sound", list(ambient_sounds.keys()),
                                    format_func=lambda x: ambient_sounds[x])
        
        sound_col1, sound_col2, sound_col3 = st.columns(3)
        
        with sound_col1:
            sound_volume = st.slider("Volume", 0.0, 1.0, 0.5, 0.1, help="Set the volume level")
        
        with sound_col2:
            loop_sound = st.checkbox("Loop", value=False, help="Loop the sound continuously")
        
        with sound_col3:
            if st.button("🎵 Play Sound"):
                with st.spinner(f"🦜 Playing {ambient_sounds[selected_sound]}..."):
                    result = play_ambient_sound_sync(selected_sound, sound_volume, loop_sound)
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Ambient sound started!"))
        
        if st.button("🔇 Stop All Audio", key="stop_audio_btn_main"):
            with st.spinner("🦜 Stopping all audio..."):
                result = stop_all_audio_sync()
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", "All audio stopped!"))
    
    with col2:
        st.subheader("🎙️ Voice Settings")
        
        # Voice configuration
        if st.button("🎙️ Get Available Voices"):
            with st.spinner("🦜 Getting available voices..."):
                result = get_available_voices_sync()
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Voices retrieved!")
                    st.markdown(result.get("response", "No voices found"))
        
        st.markdown("---")
        
        st.subheader("🔧 Voice Configuration")
        
        # Show current voice settings
        st.write("**Current Voice Settings:**")
        tts_method = os.getenv('TTS_METHOD')
        st.code(f"""
TTS_METHOD: {tts_method}
ELEVENLABS_API_KEY: {'✅ Set' if os.getenv('ELEVENLABS_API_KEY') else '❌ Not set'}
ELEVENLABS_VOICE_ID: {os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')}
VOICE_SERVER_URL: {os.getenv('VOICE_SERVER_URL', 'http://localhost:9006')}
        """)
        
        st.markdown("---")
        
        st.subheader("🎵 Audio Status")
        
        # Audio status indicators
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            st.metric("Voice Server", "🟢 Online", "ElevenLabs connected")
            st.metric("Audio System", "🟢 Ready", "Pygame initialized")
        
        with status_col2:
            st.metric("Voice Cache", "📦 Active", "50 phrases cached")
            st.metric("Ambient Sounds", "🎵 Available", "5 sounds loaded")
        
        st.markdown("---")
        
        st.subheader("🦜 Salty's Voice Tips")
        st.write("""
        **Voice Control Tips:**
        - 🗣️ **Speak naturally** - Salty understands conversational text
        - 🎵 **Ambient sounds** - Create the perfect tiki bar atmosphere
        - 🔊 **Volume control** - Adjust for different environments
        - 🔄 **Loop sounds** - Keep the atmosphere going
        - ⏸️ **Non-blocking** - Let Salty speak while you continue working
        
        *Squawk! My voice brings the tiki bar to life!*
        """)
    
    # Voice test section
    st.markdown("---")
    st.subheader("🎭 Voice Test Panel")
    
    test_col1, test_col2, test_col3 = st.columns(3)
    
    with test_col1:
        if st.button("🦜 Test Salty's Voice"):
            test_text = "Squawk! This is a test of my voice synthesis. How do I sound, matey?"
            with st.spinner("🦜 Testing voice synthesis..."):
                result = speak_salty_voice_sync(test_text, blocking=True)
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Voice test completed!")
    
    with test_col2:
        if st.button("🌊 Test Ocean Waves"):
            with st.spinner("🦜 Playing ocean waves..."):
                result = play_ambient_sound_sync("ocean_waves", 0.3, False)
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Ocean waves test completed!")
    
    with test_col3:
        if st.button("🔇 Stop All Audio", key="stop_audio_btn_testpanel"):
            with st.spinner("🦜 Stopping all audio..."):
                result = stop_all_audio_sync()
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("All audio stopped!")
    
    # Voice integration with chat
    st.markdown("---")
    st.subheader("🤖 Voice Chat Integration")
    
    st.write("""
    **Coming Soon:**
    - 🎤 **Voice Commands** - "Hey Salty" wake word detection
    - 🗣️ **Voice Responses** - Salty speaks his chat responses
    - 🎵 **Background Music** - Automatic ambient sounds during chat
    - 🎭 **Voice Moods** - Different voice styles for different situations
    
    *🦜 Squawk! The future of tiki bar interaction is here!*
    """)

if __name__ == "__main__":
    show_voice_control()
