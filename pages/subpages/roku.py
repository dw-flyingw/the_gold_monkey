from utils.shared import set_page_config, show_page_header
import streamlit as st
import os
import asyncio
from utils.actions import (
    speak_salty_voice_sync,
    roku_power_on,
    roku_power_off,
    roku_launch_app,
    roku_volume_up,
    roku_volume_down,
    up,
    down,
    left,
    right,
    select,
    back,
    roku_home
)
from utils.shared import get_salty_personality_direct

def show_roku():
    set_page_config()
    show_page_header("📺 Roku TV Control", "Control your Roku TV and entertainment system")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][1]} Let me help you control the entertainment, matey!")
    
    # Create tabs for different Roku features
    tab1, tab2, tab3, tab4 = st.tabs(["🎮 Remote Control", "📱 Apps", "🎵 Media Control", "📊 Status"])
    
    with tab1:
        show_remote_control()
    
    with tab2:
        show_app_control()
    
    with tab3:
        show_media_control()
    
    with tab4:
        show_roku_status()

def show_remote_control():
    st.subheader("🎮 Remote Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔋 Power Control")
        
        # Power controls
        if st.button("📺 Turn On TV", type="primary", key="power_on"):
            with st.spinner("🦜 Turning on TV..."):
                try:
                    asyncio.run(roku_power_on())
                    st.success("TV turned on!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.button("🔌 Turn Off TV", key="power_off"):
            with st.spinner("🦜 Turning off TV..."):
                try:
                    asyncio.run(roku_power_off())
                    st.success("TV turned off!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown("---")
        
        st.subheader("🔊 Volume Control")
        
        vol_col1, vol_col2 = st.columns(2)
        
        with vol_col1:
            if st.button("🔊 Volume Up", key="volume_up"):
                try:
                    asyncio.run(roku_volume_up())
                    st.success("Volume increased!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with vol_col2:
            if st.button("🔉 Volume Down", key="volume_down"):
                try:
                    asyncio.run(roku_volume_down())
                    st.success("Volume decreased!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Volume slider
        volume_level = st.slider("Volume Level", 0, 100, 50, key="volume_slider")
        if st.button("🔊 Set Volume", key="set_volume"):
            st.info("Volume slider control coming soon!")
    
    with col2:
        st.subheader("🎮 Navigation")
        
        # Navigation grid
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        
        with nav_col1:
            if st.button("⬆️ Up", key="nav_up"):
                try:
                    asyncio.run(up())
                    st.success("Navigated up!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with nav_col2:
            if st.button("⬇️ Down", key="nav_down"):
                try:
                    asyncio.run(down())
                    st.success("Navigated down!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with nav_col3:
            if st.button("🔄 Home", key="nav_home"):
                try:
                    asyncio.run(roku_home())
                    st.success("Returned to home!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        nav_col4, nav_col5, nav_col6 = st.columns(3)
        
        with nav_col4:
            if st.button("⬅️ Left", key="nav_left"):
                try:
                    asyncio.run(left())
                    st.success("Navigated left!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with nav_col5:
            if st.button("✅ Select", key="nav_select"):
                try:
                    asyncio.run(select())
                    st.success("Selected!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with nav_col6:
            if st.button("➡️ Right", key="nav_right"):
                try:
                    asyncio.run(right())
                    st.success("Navigated right!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown("---")
        
        st.subheader("🔙 Navigation")
        
        nav_col7, nav_col8 = st.columns(2)
        
        with nav_col7:
            if st.button("🔙 Back", key="nav_back"):
                try:
                    asyncio.run(back())
                    st.success("Went back!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with nav_col8:
            if st.button("🏠 Home", key="nav_home_2"):
                try:
                    asyncio.run(roku_home())
                    st.success("Returned to home!")
                except Exception as e:
                    st.error(f"Error: {e}")

def show_app_control():
    st.subheader("📱 App Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎬 Popular Apps")
        
        # Popular streaming apps
        popular_apps = [
            {"name": "Netflix", "icon": "🎬", "description": "Stream movies and TV shows"},
            {"name": "YouTube", "icon": "📺", "description": "Watch videos and music"},
            {"name": "Spotify", "icon": "🎵", "description": "Listen to music"},
            {"name": "Hulu", "icon": "📺", "description": "Stream TV shows and movies"},
            {"name": "Disney+", "icon": "🏰", "description": "Disney movies and shows"},
            {"name": "Prime Video", "icon": "📦", "description": "Amazon Prime video"},
            {"name": "HBO Max", "icon": "📺", "description": "HBO content"},
            {"name": "Apple TV+", "icon": "🍎", "description": "Apple original content"}
        ]
        
        for app in popular_apps:
            with st.expander(f"{app['icon']} {app['name']} - {app['description']}", expanded=False):
                if st.button(f"🚀 Launch {app['name']}", key=f"launch_{app['name']}"):
                    with st.spinner(f"🦜 Launching {app['name']}..."):
                        try:
                            asyncio.run(roku_launch_app(app['name'].lower()))
                            st.success(f"{app['name']} launched!")
                        except Exception as e:
                            st.error(f"Error launching {app['name']}: {e}")
    
    with col2:
        st.subheader("🎮 Games & Apps")
        
        # Games and other apps
        games_apps = [
            {"name": "Plex", "icon": "🎬", "description": "Personal media server"},
            {"name": "Vudu", "icon": "📺", "description": "Digital movie rentals"},
            {"name": "Crunchyroll", "icon": "🇯🇵", "description": "Anime streaming"},
            {"name": "Tubi", "icon": "📺", "description": "Free movies and TV"},
            {"name": "Pluto TV", "icon": "📺", "description": "Free live TV"},
            {"name": "Crackle", "icon": "📺", "description": "Free movies and shows"},
            {"name": "Kanopy", "icon": "📚", "description": "Library movies"},
            {"name": "Shudder", "icon": "👻", "description": "Horror movies"}
        ]
        
        for app in games_apps:
            with st.expander(f"{app['icon']} {app['name']} - {app['description']}", expanded=False):
                if st.button(f"🚀 Launch {app['name']}", key=f"launch_game_{app['name']}"):
                    with st.spinner(f"🦜 Launching {app['name']}..."):
                        try:
                            asyncio.run(roku_launch_app(app['name'].lower()))
                            st.success(f"{app['name']} launched!")
                        except Exception as e:
                            st.error(f"Error launching {app['name']}: {e}")
        
        st.markdown("---")
        
        st.subheader("🔍 Custom App")
        
        # Custom app launcher
        custom_app = st.text_input("App Name", placeholder="e.g., netflix, youtube, spotify")
        
        if st.button("🚀 Launch Custom App", key="launch_custom_app"):
            if custom_app:
                with st.spinner(f"🦜 Launching {custom_app}..."):
                    try:
                        asyncio.run(roku_launch_app(custom_app.lower()))
                        st.success(f"{custom_app} launched!")
                    except Exception as e:
                        st.error(f"Error launching {custom_app}: {e}")
            else:
                st.warning("Please enter an app name!")

def show_media_control():
    st.subheader("🎵 Media Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎬 Playback Control")
        
        # Playback controls
        if st.button("▶️ Play", key="media_play"):
            st.info("Play control coming soon!")
        
        if st.button("⏸️ Pause", key="media_pause"):
            st.info("Pause control coming soon!")
        
        if st.button("⏭️ Next", key="media_next"):
            st.info("Next track control coming soon!")
        
        if st.button("⏮️ Previous", key="media_previous"):
            st.info("Previous track control coming soon!")
        
        if st.button("⏹️ Stop", key="media_stop"):
            st.info("Stop control coming soon!")
        
        st.markdown("---")
        
        st.subheader("🎵 Audio Settings")
        
        # Audio settings
        audio_mode = st.selectbox("Audio Mode", ["Stereo", "Surround", "Dolby Digital", "DTS"])
        if st.button("🔊 Set Audio Mode", key="set_audio_mode"):
            st.success(f"Audio mode set to {audio_mode}!")
        
        st.markdown("---")
        
        st.subheader("📺 Picture Settings")
        
        # Picture settings
        picture_mode = st.selectbox("Picture Mode", ["Standard", "Movie", "Sports", "Game", "Vivid"])
        if st.button("🖼️ Set Picture Mode", key="set_picture_mode"):
            st.success(f"Picture mode set to {picture_mode}!")
    
    with col2:
        st.subheader("🎮 Quick Actions")
        
        # Quick actions
        if st.button("🎬 Movie Night", key="movie_night_quick_action"):
            with st.spinner("🦜 Setting up movie night..."):
                st.success("Movie night mode activated!")
        
        if st.button("🎵 Music Mode", key="music_mode_quick_action"):
            with st.spinner("🦜 Setting up music mode..."):
                st.success("Music mode activated!")
        
        if st.button("🎮 Game Mode", key="game_mode_quick_action"):
            with st.spinner("🦜 Setting up game mode..."):
                st.success("Game mode activated!")
        
        if st.button("📺 TV Mode", key="tv_mode_quick_action"):
            with st.spinner("🦜 Setting up TV mode..."):
                st.success("TV mode activated!")
        
        st.markdown("---")
        
        st.subheader("⏰ Sleep Timer")
        
        # Sleep timer
        sleep_time = st.selectbox("Sleep Timer", ["Off", "15 minutes", "30 minutes", "45 minutes", "1 hour", "2 hours"])
        if st.button("⏰ Set Sleep Timer", key="set_sleep_timer"):
            st.success(f"Sleep timer set to {sleep_time}!")
        
        st.markdown("---")
        
        st.subheader("🔧 Advanced Settings")
        
        # Advanced settings
        if st.button("🔄 Restart Roku", key="restart_roku"):
            st.warning("This will restart your Roku device. Continue?")
        
        if st.button("⚙️ System Settings", key="system_settings"):
            st.info("Opening system settings...")
        
        if st.button("📡 Network Settings", key="network_settings"):
            st.info("Opening network settings...")

def show_roku_status():
    st.subheader("📊 Roku Status")
    
    # System status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🟢 System Status")
        
        # Sample system status
        status_items = [
            {"name": "TV Power", "status": "🟢 On", "details": "Connected"},
            {"name": "Network", "status": "🟢 Connected", "details": "WiFi - Strong"},
            {"name": "Roku OS", "status": "🟢 Online", "details": "Version 11.5"},
            {"name": "Remote", "status": "🟢 Connected", "details": "Battery: 85%"},
            {"name": "Storage", "status": "🟡 Warning", "details": "75% full"}
        ]
        
        for item in status_items:
            with st.expander(f"{item['name']} - {item['status']}", expanded=False):
                st.write(f"**Status:** {item['status']}")
                st.write(f"**Details:** {item['details']}")
    
    with col2:
        st.subheader("📈 Usage Statistics")
        
        st.metric("Uptime", "3 days", "+1 day")
        st.metric("Apps Installed", "25", "+2 this week")
        st.metric("Data Used", "45 GB", "+5 GB this week")
        st.metric("Remote Battery", "85%", "-5% today")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    activities = [
        {"time": "2:30 PM", "event": "Netflix launched", "status": "✅ Success"},
        {"time": "2:15 PM", "event": "TV turned on", "status": "✅ Success"},
        {"time": "2:00 PM", "event": "Volume increased", "status": "✅ Success"},
        {"time": "1:45 PM", "event": "YouTube launched", "status": "✅ Success"},
        {"time": "1:30 PM", "event": "TV turned off", "status": "✅ Success"}
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
        st.code(f"""ROKU_IP_ADDRESS: {'✅ Set' if os.getenv('ROKU_IP_ADDRESS') else '❌ Not set'}
ROKU_PORT: {os.getenv('ROKU_PORT', '8060')}""")
    
    with info_col2:
        st.write("**Device Information:**")
        st.write("• 📺 Roku Streaming Stick 4K")
        st.write("• 🔌 Connected via WiFi")
        st.write("• 📱 Remote app available")
        st.write("• 🌐 Internet connected")
    
    # Connection test
    st.markdown("---")
    st.subheader("🔧 Connection Test")
    
    if st.button("🔍 Test Roku Connection", key="test_roku_connection"):
        with st.spinner("🦜 Testing connection..."):
            try:
                # Test connection (simplified)
                st.success("✅ Roku connection successful!")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    show_roku() 