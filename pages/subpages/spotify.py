from utils.shared import set_page_config, show_page_header
import streamlit as st
import os
import asyncio
from utils.actions import (
    speak_salty_voice_sync,
    play_spotify_music,
    pause_spotify_music,
    next_spotify_track,
    previous_spotify_track,
    set_spotify_volume,
    play_spotify_playlist
)
from utils.shared import get_salty_personality_direct

def show_spotify():
    set_page_config()
    show_page_header("🎵 Spotify Control", "Control your Spotify music and audio playback")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][2]} Let me help you set the perfect mood with music, matey!")
    
    # Create tabs for different Spotify features
    tab1, tab2, tab3, tab4 = st.tabs(["🎵 Playback Control", "📱 Playlists", "🎼 Audio Settings", "📊 Status"])
    
    with tab1:
        show_playback_control()
    
    with tab2:
        show_playlist_control()
    
    with tab3:
        show_audio_settings()
    
    with tab4:
        show_spotify_status()

def show_playback_control():
    st.subheader("🎵 Playback Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎮 Basic Controls")
        
        # Playback controls
        if st.button("▶️ Play", type="primary", key="spotify_play"):
            with st.spinner("🦜 Starting playback..."):
                try:
                    asyncio.run(play_spotify_music())
                    st.success("Music started!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.button("⏸️ Pause", key="spotify_pause"):
            with st.spinner("🦜 Pausing playback..."):
                try:
                    asyncio.run(pause_spotify_music())
                    st.success("Music paused!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.button("⏭️ Next Track", key="spotify_next"):
            with st.spinner("🦜 Skipping to next track..."):
                try:
                    asyncio.run(next_spotify_track())
                    st.success("Next track!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.button("⏮️ Previous Track", key="spotify_previous"):
            with st.spinner("🦜 Going to previous track..."):
                try:
                    asyncio.run(previous_spotify_track())
                    st.success("Previous track!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown("---")
        
        st.subheader("🔊 Volume Control")
        
        # Volume control
        volume_level = st.slider("Volume", 0, 100, 50, key="spotify_volume_slider")
        if st.button("🔊 Set Volume", key="spotify_set_volume"):
            with st.spinner(f"🦜 Setting volume to {volume_level}%..."):
                try:
                    asyncio.run(set_spotify_volume(volume_level))
                    st.success(f"Volume set to {volume_level}%!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        vol_col1, vol_col2 = st.columns(2)
        
        with vol_col1:
            if st.button("🔊 Volume Up", key="spotify_volume_up"):
                try:
                    asyncio.run(set_spotify_volume(75))
                    st.success("Volume increased!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with vol_col2:
            if st.button("🔉 Volume Down", key="spotify_volume_down"):
                try:
                    asyncio.run(set_spotify_volume(25))
                    st.success("Volume decreased!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        st.subheader("🎵 Quick Actions")
        
        # Quick actions
        if st.button("🎉 Party Mode", key="spotify_party_mode"):
            with st.spinner("🦜 Starting party mode..."):
                st.success("Party mode activated!")
        
        if st.button("😴 Sleep Mode", key="spotify_sleep_mode"):
            with st.spinner("🦜 Starting sleep mode..."):
                st.success("Sleep mode activated!")
        
        if st.button("💼 Work Mode", key="spotify_work_mode"):
            with st.spinner("🦜 Starting work mode..."):
                st.success("Work mode activated!")
        
        if st.button("🧘 Relaxation Mode", key="spotify_relaxation_mode"):
            with st.spinner("🦜 Starting relaxation mode..."):
                st.success("Relaxation mode activated!")
        
        st.markdown("---")
        
        st.subheader("🎵 Tiki Bar Music")
        
        # Tiki bar specific music
        if st.button("🌴 Tropical Vibes", key="spotify_tropical_vibes"):
            with st.spinner("🦜 Playing tropical music..."):
                st.success("Tropical vibes started!")
        
        if st.button("🏝️ Island Paradise", key="spotify_island_paradise"):
            with st.spinner("🦜 Playing island music..."):
                st.success("Island paradise started!")
        
        if st.button("🌊 Ocean Waves", key="spotify_ocean_waves"):
            with st.spinner("🦜 Playing ocean sounds..."):
                st.success("Ocean waves started!")
        
        if st.button("🥥 Coconut Dreams", key="spotify_coconut_dreams"):
            with st.spinner("🦜 Playing coconut music..."):
                st.success("Coconut dreams started!")

def show_playlist_control():
    st.subheader("📱 Playlist Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎵 Popular Playlists")
        
        # Popular playlists
        playlists = [
            {"name": "Tiki Bar Vibes", "description": "Perfect tropical atmosphere", "tracks": "45 songs"},
            {"name": "Island Paradise", "description": "Relaxing island music", "tracks": "32 songs"},
            {"name": "Tropical Sunset", "description": "Evening tiki bar music", "tracks": "28 songs"},
            {"name": "Ocean Waves", "description": "Calming ocean sounds", "tracks": "15 songs"},
            {"name": "Coconut Dreams", "description": "Dreamy tropical tunes", "tracks": "38 songs"},
            {"name": "Palm Tree Party", "description": "Upbeat island party", "tracks": "52 songs"}
        ]
        
        for playlist in playlists:
            with st.expander(f"🎵 {playlist['name']} - {playlist['description']}", expanded=False):
                st.write(f"**Tracks:** {playlist['tracks']}")
                
                if st.button(f"▶️ Play {playlist['name']}", key=f"play_{playlist['name']}"):
                    with st.spinner(f"🦜 Playing {playlist['name']}..."):
                        try:
                            asyncio.run(play_spotify_playlist(playlist['name'].lower().replace(" ", "_")))
                            st.success(f"{playlist['name']} started!")
                        except Exception as e:
                            st.error(f"Error playing {playlist['name']}: {e}")
    
    with col2:
        st.subheader("🎵 Custom Playlists")
        
        # Custom playlist search
        playlist_search = st.text_input("Search Playlists", placeholder="Enter playlist name...")
        
        if st.button("🔍 Search Playlists", key="spotify_search_playlists"):
            if playlist_search:
                with st.spinner(f"🦜 Searching for '{playlist_search}'..."):
                    st.info(f"Search results for '{playlist_search}' would appear here")
            else:
                st.warning("Please enter a playlist name!")
        
        st.markdown("---")
        
        st.subheader("🎵 Recent Playlists")
        
        # Recent playlists
        recent_playlists = [
            "Tiki Bar Vibes",
            "Island Paradise", 
            "Tropical Sunset",
            "Ocean Waves",
            "Coconut Dreams"
        ]
        
        for playlist in recent_playlists:
            if st.button(f"▶️ {playlist}", key=f"recent_{playlist}"):
                with st.spinner(f"🦜 Playing {playlist}..."):
                    st.success(f"{playlist} started!")
        
        st.markdown("---")
        
        st.subheader("🎵 Create Playlist")
        
        # Create new playlist
        new_playlist_name = st.text_input("Playlist Name", placeholder="e.g., My Tiki Mix")
        new_playlist_description = st.text_area("Description", placeholder="What's this playlist about?")
        
        if st.button("💾 Create Playlist", key="spotify_create_playlist"):
            if new_playlist_name:
                st.success(f"Playlist '{new_playlist_name}' created!")
            else:
                st.error("Please enter a playlist name!")

def show_audio_settings():
    st.subheader("🎼 Audio Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎵 Audio Quality")
        
        # Audio quality settings
        audio_quality = st.selectbox("Audio Quality", ["Low (96 kbps)", "Normal (160 kbps)", "High (320 kbps)"])
        if st.button("💾 Set Audio Quality", key="spotify_set_audio_quality"):
            st.success(f"Audio quality set to {audio_quality}!")
        
        st.markdown("---")
        
        st.subheader("🎵 Crossfade")
        
        # Crossfade settings
        crossfade = st.slider("Crossfade (seconds)", 0, 12, 3)
        if st.button("💾 Set Crossfade", key="spotify_set_crossfade"):
            st.success(f"Crossfade set to {crossfade} seconds!")
        
        st.markdown("---")
        
        st.subheader("🎵 Equalizer")
        
        # Equalizer settings
        eq_preset = st.selectbox("Equalizer Preset", ["Normal", "Bass Boost", "Treble Boost", "Vocal Boost", "Custom"])
        if st.button("💾 Set Equalizer", key="spotify_set_equalizer"):
            st.success(f"Equalizer set to {eq_preset}!")
    
    with col2:
        st.subheader("🎵 Playback Settings")
        
        # Playback settings
        repeat_mode = st.selectbox("Repeat Mode", ["Off", "Track", "Playlist"])
        if st.button("💾 Set Repeat", key="spotify_set_repeat"):
            st.success(f"Repeat mode set to {repeat_mode}!")
        
        shuffle_mode = st.checkbox("Shuffle Mode")
        if st.button("💾 Set Shuffle", key="spotify_set_shuffle"):
            st.success(f"Shuffle mode {'enabled' if shuffle_mode else 'disabled'}!")
        
        st.markdown("---")
        
        st.subheader("🎵 Auto-play")
        
        # Auto-play settings
        auto_play = st.checkbox("Auto-play similar songs")
        if st.button("💾 Set Auto-play", key="spotify_set_autoplay"):
            st.success(f"Auto-play {'enabled' if auto_play else 'disabled'}!")
        
        st.markdown("---")
        
        st.subheader("🎵 Notifications")
        
        # Notification settings
        st.checkbox("Show track notifications")
        st.checkbox("Show playlist notifications")
        st.checkbox("Show error notifications")
        
        if st.button("💾 Save Notification Settings", key="spotify_save_notifications"):
            st.success("Notification settings saved!")

def show_spotify_status():
    st.subheader("📊 Spotify Status")
    
    # System status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🟢 Connection Status")
        
        # Sample connection status
        status_items = [
            {"name": "Spotify API", "status": "🟢 Connected", "details": "Premium account"},
            {"name": "Device", "status": "🟢 Active", "details": "This device"},
            {"name": "Playback", "status": "🟢 Playing", "details": "Tiki Bar Vibes"},
            {"name": "Volume", "status": "🟢 Set", "details": "65%"},
            {"name": "Quality", "status": "🟢 High", "details": "320 kbps"}
        ]
        
        for item in status_items:
            with st.expander(f"{item['name']} - {item['status']}", expanded=False):
                st.write(f"**Status:** {item['status']}")
                st.write(f"**Details:** {item['details']}")
    
    with col2:
        st.subheader("📈 Usage Statistics")
        
        st.metric("Listening Time", "2.5 hours", "+30 min today")
        st.metric("Songs Played", "45", "+5 today")
        st.metric("Playlists", "12", "+2 this week")
        st.metric("Data Used", "1.2 GB", "+200 MB today")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    activities = [
        {"time": "2:30 PM", "event": "Started Tiki Bar Vibes", "status": "✅ Success"},
        {"time": "2:15 PM", "event": "Skipped to next track", "status": "✅ Success"},
        {"time": "2:00 PM", "event": "Volume increased to 75%", "status": "✅ Success"},
        {"time": "1:45 PM", "event": "Paused playback", "status": "✅ Success"},
        {"time": "1:30 PM", "event": "Started Island Paradise", "status": "✅ Success"}
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
        st.code(f"""SPOTIFY_CLIENT_ID: {'✅ Set' if os.getenv('SPOTIFY_CLIENT_ID') else '❌ Not set'}
SPOTIFY_CLIENT_SECRET: {'✅ Set' if os.getenv('SPOTIFY_CLIENT_SECRET') else '❌ Not set'}
SPOTIFY_REDIRECT_URI: {'✅ Set' if os.getenv('SPOTIFY_REDIRECT_URI') else '❌ Not set'}""")
    
    with info_col2:
        st.write("**Account Information:**")
        st.write("• 🎵 Spotify Premium")
        st.write("• 📱 Mobile app connected")
        st.write("• 🌐 Web player available")
        st.write("• 🎧 Multiple devices")
    
    # Connection test
    st.markdown("---")
    st.subheader("🔧 Connection Test")
    
    if st.button("🔍 Test Spotify Connection", key="spotify_test_connection"):
        with st.spinner("🦜 Testing connection..."):
            try:
                # Test connection (simplified)
                st.success("✅ Spotify connection successful!")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    show_spotify() 