from utils.shared import set_page_config, show_page_header
import streamlit as st
import asyncio
from utils.actions import (
    roku_power_on,
    roku_power_off,
    roku_home,
    roku_volume_up,
    roku_volume_down,
    roku_mute,
    roku_launch_app,
    roku_up,
    roku_down,
    roku_left,
    roku_right,
    roku_select,
    roku_back,
    roku_info,
    roku_get_device_status,
)
from utils.shared import get_salty_personality_direct
from utils.shared import get_salty_personality_direct

def show_roku_control():
    set_page_config()
    show_page_header("📺 Roku Control", "Salty's entertainment control panel for The Gold Monkey")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][2]} I can help you control the tiki bar entertainment, matey!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔌 Power Controls")
        
        # Power controls
        if st.button("🟢 Power On", type="primary"):
            with st.spinner("🦜 Squawk! Powering on the Roku..."):
                result = asyncio.run(roku_power_on())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", "Roku powered on!"))
        
        if st.button("⚫ Power Off"):
            with st.spinner("🦜 Powering off the Roku..."):
                result = asyncio.run(roku_power_off())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", "Roku powered off!"))
        
        if st.button("🏠 Home"):
            with st.spinner("🦜 Going to Roku home..."):
                result = asyncio.run(roku_home())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", "Roku home screen!"))
        
        st.markdown("---")
        
        st.subheader("🔊 Volume Controls")
        
        # Volume controls
        vol_col1, vol_col2, vol_col3 = st.columns(3)
        
        with vol_col1:
            if st.button("🔊 Volume Up"):
                with st.spinner("🦜 Increasing volume..."):
                    result = asyncio.run(roku_volume_up())
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Volume up!"))
        
        with vol_col2:
            if st.button("🔉 Volume Down"):
                with st.spinner("🦜 Decreasing volume..."):
                    result = asyncio.run(roku_volume_down())
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Volume down!"))
        
        with vol_col3:
            if st.button("🔇 Mute"):
                with st.spinner("🦜 Muting..."):
                    result = asyncio.run(roku_mute())
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Roku muted!"))
        
        st.markdown("---")
        
        st.subheader("📱 App Control")
        
        # App launching
        app_name = st.text_input("App name to launch", placeholder="e.g., Netflix, YouTube, Hulu")
        
        if st.button("🚀 Launch App"):
            if app_name:
                with st.spinner(f"🦜 Launching {app_name}..."):
                    result = asyncio.run(roku_launch_app(app_name))
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", f"{app_name} launched!"))
            else:
                st.warning("Please enter an app name!")
    
    with col2:
        st.subheader("🎮 Navigation")
        
        # Navigation controls
        nav_col1, nav_col2, nav_col3 = st.columns(3)
        
        with nav_col1:
            if st.button("⬆️ Up"):
                with st.spinner("🦜 Navigating up..."):
                    result = asyncio.run(roku_navigate("up"))
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Navigated up!"))
        
        with nav_col2:
            if st.button("⬇️ Down"):
                with st.spinner("🦜 Navigating down..."):
                    result = asyncio.run(roku_navigate("down"))
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Navigated down!"))
        
        with nav_col3:
            if st.button("✅ Select"):
                with st.spinner("🦜 Selecting..."):
                    result = asyncio.run(roku_select())
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Selected!"))
        
        nav_col4, nav_col5, nav_col6 = st.columns(3)
        
        with nav_col4:
            if st.button("⬅️ Left"):
                with st.spinner("🦜 Navigating left..."):
                    result = asyncio.run(roku_navigate("left"))
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Navigated left!"))
        
        with nav_col5:
            if st.button("➡️ Right"):
                with st.spinner("🦜 Navigating right..."):
                    result = asyncio.run(roku_navigate("right"))
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Navigated right!"))
        
        with nav_col6:
            if st.button("↩️ Back"):
                with st.spinner("🦜 Going back..."):
                    result = asyncio.run(roku_back())
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Went back!"))
        
        st.markdown("---")
        
        st.subheader("ℹ️ Info & Status")
        
        if st.button("ℹ️ Show Info"):
            with st.spinner("🦜 Getting Roku device status..."):
                result = asyncio.run(roku_info())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    # Display the status information in a formatted way
                    status_text = result.get("response", "No status information available")
                    
                    # Create a nice formatted display
                    st.success("🦜 Roku status retrieved successfully!")
                    
                    # Display the status in a code block for better formatting
                    st.markdown("### 📺 Device Status")
                    st.code(status_text, language="text")
                    
                    # Also display in a more readable format
                    st.markdown("### 📊 Status Summary")
                    
                    # Parse the status text to extract key information
                    lines = status_text.split('\n')
                    device_name = "Unknown"
                    current_app = "Unknown"
                    ip_address = "Unknown"
                    
                    for line in lines:
                        if "Name:" in line:
                            device_name = line.split("Name:")[1].strip()
                        elif "Current App:" in line:
                            current_app = line.split("Current App:")[1].strip()
                        elif "IP:" in line:
                            ip_address = line.split("IP:")[1].strip()
                    
                    # Display key metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Device Name", device_name)
                    with col2:
                        st.metric("Current App", current_app)
                    with col3:
                        st.metric("IP Address", ip_address)
        
        # Add a separate button for comprehensive status
        if st.button("📊 Get Full Status"):
            with st.spinner("🦜 Getting comprehensive Roku status..."):
                result = asyncio.run(roku_get_device_status())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("🦜 Full status retrieved!")
                    
                    # Display in an expander for better organization
                    with st.expander("📺 Complete Roku Status", expanded=True):
                        st.markdown(result.get("response", "No status available"))
        
        st.markdown("---")
        
        st.subheader("🦜 Salty's Roku Tips")
        st.write("""
        **Roku Tips from Salty:**
        - 🏠 **Home**: Always a safe place to start
        - 🎮 **Navigation**: Use the arrow keys to move around
        - ✅ **Select**: Choose what you want to watch
        - ↩️ **Back**: Go back to the previous screen
        - 🔊 **Volume**: Keep it at a good level for the tiki bar
        - ℹ️ **Info**: Get detailed device status and information
        
        *Squawk! Good entertainment makes for happy customers!*
        """)
    
    # Status section
    st.markdown("---")
    st.subheader("📊 Roku Status")
    
    # Add some sample status info (in a real implementation, this would query actual status)
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.metric("Device Status", "🟢 Online", "Connected to network")
    
    with status_col2:
        st.metric("Current App", "Home Screen", "Ready for selection")
    
    with status_col3:
        st.metric("Volume Level", "50%", "Good for tiki bar")

if __name__ == "__main__":
    show_roku_control()
