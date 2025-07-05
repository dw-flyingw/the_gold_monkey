from utils.shared import set_page_config, show_page_header
import streamlit as st
import asyncio
import os
from utils.actions import (
    play_spotify_music,
    pause_spotify_music,
    next_spotify_track,
    previous_spotify_track,
    set_spotify_volume,
    play_spotify_playlist,
    play_spotify_track,
    get_spotify_status,
    get_user_playlists,
)
from utils.shared import get_salty_personality_direct
from utils.streamlit_async import safe_async_call

def show_spotify_control():
    set_page_config()
    show_page_header("🎵 Spotify Control", "Salty's music control panel for The Gold Monkey")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][2]} I can help you control the tiki bar music, matey!")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.subheader("🎛️ Playback Controls")
        
        # Basic controls
        if st.button("▶️ Play", key="play_spotify"):
            try:
                result = safe_async_call(play_spotify_music)
                if result.get("success"):
                    st.success("🎵 Music is playing!")
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        if st.button("⏸️ Pause", key="pause_spotify"):
            try:
                result = safe_async_call(pause_spotify_music)
                if result.get("success"):
                    st.success("⏸️ Music paused!")
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        if st.button("⏭️ Next", key="next_spotify"):
            try:
                result = safe_async_call(next_spotify_track)
                if result.get("success"):
                    st.success("⏭️ Next track!")
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        if st.button("⏮️ Previous", key="previous_spotify"):
            try:
                result = safe_async_call(previous_spotify_track)
                if result.get("success"):
                    st.success("⏮️ Previous track!")
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        st.markdown("---")
        
        st.subheader("🔊 Volume Control")
        
        # Volume slider
        volume = st.slider("Volume", 0, 100, 50, key="volume_slider")
        
        if st.button("Set Volume", key="set_volume"):
            try:
                result = safe_async_call(set_spotify_volume, volume)
                if result.get("success"):
                    st.success(f"🔊 Volume set to {volume}%!")
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        # Quick volume buttons
        col5, col6 = st.columns(2)
        
        with col5:
            if st.button("🔊 High Volume", key="high_volume"):
                try:
                    result = safe_async_call(set_spotify_volume, 75)
                    if result.get("success"):
                        st.success("🔊 Volume set to 75%!")
                    else:
                        st.error(f"❌ {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        with col6:
            if st.button("🔉 Low Volume", key="low_volume"):
                try:
                    result = safe_async_call(set_spotify_volume, 25)
                    if result.get("success"):
                        st.success("🔉 Volume set to 25%!")
                    else:
                        st.error(f"❌ {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    with col2:
        st.subheader("📻 Playlist Control")
        
        # Get playlist ID from environment
        tiki_playlist_id = os.getenv('SPOTIFY_TIKI_PLAYLIST_ID', '6tTFZeC3bHRtklZpmNDTM7')
        closing_song_id = os.getenv('SPOTIFY_CLOSING_SONG_ID', '0K2WjMLZYr09LKwurGRYRE')
        
        # Playlist buttons
        if st.button("🏝️ Play Tiki Playlist", help="Play the main tiki bar playlist", key="play_tiki_playlist"):
            try:
                result = safe_async_call(play_spotify_playlist, tiki_playlist_id)
                if result.get("success"):
                    st.success("🎵 Tiki Bar playlist is playing!")
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        if st.button("🧪 Test Playlist Access", help="Debug playlist access issues", key="test_playlist"):
            try:
                from mcp_servers.spotify_client import test_playlist_access
                result = safe_async_call(test_playlist_access, tiki_playlist_id)
                if result.get("success"):
                    st.success("✅ Playlist access working!")
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        if st.button("📋 Get My Playlists", help="Show all your Spotify playlists to find valid IDs", key="get_playlists"):
            try:
                result = safe_async_call(get_user_playlists)
                if result.get("success"):
                    playlists = result.get("playlists", [])
                    st.success(f"📋 Found {len(playlists)} playlists!")
                    for playlist in playlists[:5]:  # Show first 5
                        st.write(f"• {playlist['name']}")
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        if st.button("🌃 Play Closing Song", help="Play New York, New York (closing song)", key="play_closing"):
            try:
                result = safe_async_call(play_spotify_track, closing_song_id)
                if result.get("success"):
                    st.success("🎶 Closing song is playing!")
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        st.markdown("---")
        
        st.subheader("🔧 Playlist Troubleshooting")
        st.write(f"""
        **If you're getting 'Invalid context URI' errors:**
        
        1. **Check your playlist ID** - Use the "List My Playlists" button above
        2. **Make sure the playlist is public** - Private playlists may not work
        3. **Verify you own the playlist** - Or have permission to access it
        4. **Try a different playlist** - Some playlists may have restrictions
        
        **Current playlist ID:** `{tiki_playlist_id}`
        
        *🦜 Squawk! If the playlist ID looks wrong, update your .env file!*
        """)
        
        st.markdown("---")
        
        st.subheader("📊 Status")
        
        if st.button("🔍 Check Spotify Status", key="check_status"):
            try:
                result = safe_async_call(get_spotify_status)
                if result.get("success"):
                    status = result.get("status", {})
                    st.success("✅ Spotify is connected!")
                    st.json(status)
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        st.markdown("---")
        
        st.subheader("🦜 Salty's Music Tips")
        st.write("""
        **Music Tips from Salty:**
        - 🏝️ **Tiki Playlist**: Perfect for the tiki bar atmosphere
        - 🌃 **Closing Song**: Classic way to end the night
        - 🔊 **Volume**: Keep it at a good level for conversation
        - ⏭️ **Skip**: Don't be afraid to skip songs you don't like
        
        *Squawk! Good music makes for happy customers!*
        """)
    
    # Status section
    st.markdown("---")
    st.subheader("📊 Spotify Status")
    
    # Add some sample status info (in a real implementation, this would query actual status)
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.metric("Current Status", "🎵 Playing", "Tiki playlist active")
    
    with status_col2:
        st.metric("Volume", "50%", "Good for conversation")
    
    with status_col3:
        st.metric("Current Track", "Tiki Bar Vibes", "By Tiki Dave")

if __name__ == "__main__":
    show_spotify_control()
