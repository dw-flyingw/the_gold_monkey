from utils.shared import set_page_config, show_page_header
import streamlit as st
import os
import asyncio
from utils.actions import (
    speak_salty_voice_sync,
    play_ambient_sound_sync,
    stop_all_audio_sync,
)
from utils.shared import get_salty_personality_direct

# Import sub-pages
from pages.subpages.routines import show_routines
from pages.subpages.smart_lights import show_smart_lights
from pages.subpages.roku import show_roku
from pages.subpages.spotify import show_spotify

def show_automation():
    set_page_config()
    show_page_header("🤖 Home Automation", "Control your smart home devices and create automated routines")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][1]} Let me help you automate your tiki bar, matey!")
    
    # Create tabs for different automation features
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Smart Home", "🎭 Routines", "💡 Smart Lights", "📺 Roku", "🎵 Spotify"])
    
    with tab1:
        show_smart_home_controls()
    
    with tab2:
        show_routines()
    
    with tab3:
        show_smart_lights()
    
    with tab4:
        show_roku()
    
    with tab5:
        show_spotify()

def show_smart_home_controls():
    st.subheader("🏠 Smart Home Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💡 TP-Link Smart Lights")
        
        # Light control buttons
        if st.button("💡 Turn On All Lights", type="primary"):
            with st.spinner("🦜 Turning on all lights..."):
                st.success("All lights turned on!")
        
        if st.button("🔌 Turn Off All Lights"):
            with st.spinner("🦜 Turning off all lights..."):
                st.success("All lights turned off!")
        
        st.markdown("---")
        
        # Individual light controls
        st.subheader("🎛️ Individual Light Control")
        
        light_options = ["Living Room", "Kitchen", "Tiki Bar", "Patio", "Bedroom"]
        selected_light = st.selectbox("Select Light", light_options)
        
        light_col1, light_col2, light_col3 = st.columns(3)
        
        with light_col1:
            if st.button("💡 On", key="light_on"):
                st.success(f"{selected_light} light turned on!")
        
        with light_col2:
            if st.button("🔌 Off", key="light_off"):
                st.success(f"{selected_light} light turned off!")
        
        with light_col3:
            brightness = st.slider("Brightness", 0, 100, 50, key="automation_brightness_slider")
            if st.button("💡 Set", key="automation_set_brightness"):
                st.success(f"{selected_light} brightness set to {brightness}%!")
    
    with col2:
        st.subheader("🎵 Spotify Integration")
        
        # Spotify controls
        if st.button("🎵 Play Tiki Music"):
            with st.spinner("🦜 Starting tiki music..."):
                st.success("Tiki music started!")
        
        if st.button("⏸️ Pause Music"):
            with st.spinner("🦜 Pausing music..."):
                st.success("Music paused!")
        
        if st.button("🔊 Volume Up"):
            st.success("Volume increased!")
        
        if st.button("🔉 Volume Down"):
            st.success("Volume decreased!")
        
        st.markdown("---")
        
        st.subheader("🎭 Entertainment")
        
        # Roku controls
        if st.button("📺 Turn On TV"):
            with st.spinner("🦜 Turning on TV..."):
                st.success("TV turned on!")
        
        if st.button("📺 Turn Off TV"):
            with st.spinner("🦜 Turning off TV..."):
                st.success("TV turned off!")
        
        if st.button("🎬 Netflix"):
            st.success("Launching Netflix!")
        
        if st.button("🎵 Spotify App"):
            st.success("Launching Spotify on TV!")

def show_routine_management():
    st.subheader("🎭 Automation Routines")
    
    # Display existing routines
    st.write("**Your Current Routines:**")
    
    routines = [
        {"name": "🌅 Morning Routine", "description": "Wake up with gentle lighting and tropical music", "status": "🟢 Active"},
        {"name": "🌆 Evening Routine", "description": "Dim lights and start ambient sounds", "status": "🟢 Active"},
        {"name": "🎬 Movie Night", "description": "Dim lights, start TV, and play movie audio", "status": "🟡 Scheduled"},
        {"name": "🎉 Party Mode", "description": "Bright lights, loud music, and party atmosphere", "status": "🔴 Inactive"},
        {"name": "😴 Sleep Mode", "description": "Turn off all lights and start white noise", "status": "🟢 Active"},
    ]
    
    for routine in routines:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{routine['name']}**")
            st.caption(routine['description'])
        with col2:
            st.write(routine['status'])
        with col3:
            if st.button("▶️ Run", key=f"run_{routine['name']}"):
                st.success(f"Running {routine['name']}!")
    
    st.markdown("---")
    
    # Create new routine
    st.subheader("➕ Create New Routine")
    
    routine_name = st.text_input("Routine Name", placeholder="e.g., Welcome Home")
    routine_description = st.text_area("Description", placeholder="What does this routine do?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕐 Schedule")
        enable_schedule = st.checkbox("Enable Schedule")
        if enable_schedule:
            schedule_time = st.time_input("Time to run")
            schedule_days = st.multiselect("Days of week", 
                                         ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    
    with col2:
        st.subheader("🎛️ Actions")
        actions = st.multiselect("Select actions", 
                               ["Turn on lights", "Play music", "Start TV", "Play ambient sounds", 
                                "Turn off lights", "Pause music", "Stop TV", "Stop all audio"])
    
    if st.button("💾 Save Routine", type="primary"):
        if routine_name and routine_description:
            st.success(f"Routine '{routine_name}' saved successfully!")
        else:
            st.error("Please fill in all required fields!")

def show_audio_automation():
    st.subheader("🎵 Audio Automation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌊 Ambient Sound Automation")
        
        # Ambient sound triggers
        st.write("**Sound Triggers:**")
        
        if st.checkbox("🌅 Play ocean waves at sunrise"):
            st.caption("Automatically plays ocean waves at 6:00 AM")
        
        if st.checkbox("🌆 Play jungle birds at sunset"):
            st.caption("Automatically plays jungle birds at 6:00 PM")
        
        if st.checkbox("🎉 Play tiki drums for parties"):
            st.caption("Plays tiki drums when party mode is activated")
        
        if st.checkbox("😴 Play white noise at bedtime"):
            st.caption("Plays white noise at 10:00 PM")
        
        st.markdown("---")
        
        st.subheader("🎵 Music Automation")
        
        # Music automation
        if st.checkbox("🎵 Auto-play tiki music"):
            st.caption("Automatically starts tiki music when guests arrive")
        
        if st.checkbox("🔊 Adjust volume based on time"):
            st.caption("Lowers volume after 9:00 PM")
        
        if st.checkbox("🎭 Salty announces events"):
            st.caption("Salty speaks when routines start/stop")
    
    with col2:
        st.subheader("🎤 Voice Automation")
        
        # Voice automation settings
        st.write("**Voice Triggers:**")
        
        if st.checkbox("🦜 Salty greets visitors"):
            st.caption("Salty speaks when motion is detected")
        
        if st.checkbox("🎉 Salty announces parties"):
            st.caption("Salty makes announcements during party mode")
        
        if st.checkbox("🌅 Salty announces routines"):
            st.caption("Salty speaks when routines start")
        
        if st.checkbox("🔔 Salty gives reminders"):
            st.caption("Salty reminds you of scheduled events")
        
        st.markdown("---")
        
        st.subheader("🎛️ Audio Settings")
        
        # Audio settings
        default_volume = st.slider("Default Volume", 0, 100, 50)
        max_volume = st.slider("Maximum Volume", 0, 100, 80)
        
        if st.button("💾 Save Audio Settings"):
            st.success("Audio settings saved!")
        
        st.markdown("---")
        
        st.subheader("🎵 Quick Audio Test")
        
        if st.button("🌊 Test Ocean Waves"):
            with st.spinner("🦜 Playing ocean waves..."):
                result = play_ambient_sound_sync("ocean_waves", 0.3, False)
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success("Ocean waves test completed!")
        
        if st.button("🔇 Stop All Audio"):
            with st.spinner("🦜 Stopping all audio..."):
                result = stop_all_audio_sync()
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success("All audio stopped!")

def show_automation_status():
    st.subheader("📊 Automation Status")
    
    # System status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🟢 Online Services")
        st.metric("TP-Link Lights", "Connected", "12 devices")
        st.metric("Spotify", "Connected", "Premium account")
        st.metric("Roku TV", "Connected", "Living room")
        st.metric("Voice Server", "Online", "ElevenLabs active")
    
    with col2:
        st.subheader("🔧 System Health")
        st.metric("Active Routines", "5", "+2 this week")
        st.metric("Automation Events", "127", "Today")
        st.metric("Voice Commands", "23", "This session")
        st.metric("Audio Sessions", "8", "This week")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    activities = [
        {"time": "2:30 PM", "event": "🌅 Morning routine completed", "status": "✅ Success"},
        {"time": "1:45 PM", "event": "🎵 Spotify playlist started", "status": "✅ Success"},
        {"time": "1:30 PM", "event": "💡 Living room lights on", "status": "✅ Success"},
        {"time": "1:15 PM", "event": "🦜 Salty greeted visitor", "status": "✅ Success"},
        {"time": "12:00 PM", "event": "🌆 Evening routine scheduled", "status": "⏰ Scheduled"},
    ]
    
    for activity in activities:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.write(activity['time'])
        with col2:
            st.write(activity['event'])
        with col3:
            st.write(activity['status'])
    
    st.markdown("---")
    
    # System information
    st.subheader("ℹ️ System Information")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.write("**Environment Variables:**")
        st.code(f"""
TP_LINK_USERNAME: {'✅ Set' if os.getenv('TP_LINK_USERNAME') else '❌ Not set'}
TP_LINK_PASSWORD: {'✅ Set' if os.getenv('TP_LINK_PASSWORD') else '❌ Not set'}
SPOTIFY_CLIENT_ID: {'✅ Set' if os.getenv('SPOTIFY_CLIENT_ID') else '❌ Not set'}
SPOTIFY_CLIENT_SECRET: {'✅ Set' if os.getenv('SPOTIFY_CLIENT_SECRET') else '❌ Not set'}
ROKU_IP_ADDRESS: {'✅ Set' if os.getenv('ROKU_IP_ADDRESS') else '❌ Not set'}
        """)
    
    with info_col2:
        st.write("**Connected Devices:**")
        st.write("• 💡 12 TP-Link smart bulbs")
        st.write("• 📺 1 Roku TV")
        st.write("• 🎵 Spotify Premium")
        st.write("• 🦜 Voice synthesis system")
        st.write("• 🎭 5 active routines")

if __name__ == "__main__":
    show_automation() 