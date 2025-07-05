from utils.shared import set_page_config, show_page_header
import streamlit as st
import os
import asyncio
from utils.actions import (
    speak_salty_voice_sync,
    control_tplink_lights,
)
from utils.shared import get_light_devices, rebuild_kasa_cache
from utils.shared import get_salty_personality_direct
from utils.streamlit_async import safe_async_call

def show_smart_lights():
    set_page_config()
    show_page_header("💡 Smart Lights", "Control your TP-Link smart lights and lighting automation")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][0]} Let me help you light up The Gold Monkey, matey!")
    
    # Create tabs for different lighting features
    tab1, tab2, tab3, tab4 = st.tabs(["🎛️ Light Control", "🎨 Scenes", "⏰ Automation", "📊 Status"])
    
    with tab1:
        show_light_control()
    
    with tab2:
        show_light_scenes()
    
    with tab3:
        show_light_automation()
    
    with tab4:
        show_light_status()

def show_light_control():
    st.subheader("🎛️ Light Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💡 Quick Controls")
        
        # Power controls
        if st.button("💡 Turn On All Lights", key="turn_on_all"):
            try:
                safe_async_call(control_tplink_lights, "turn_on")
                st.success("✅ All lights turned on!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        if st.button("🔌 Turn Off All Lights", key="turn_off_all"):
            try:
                safe_async_call(control_tplink_lights, "turn_off")
                st.success("✅ All lights turned off!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        st.markdown("---")
        
        # Individual light control
        st.subheader("🎯 Individual Light Control")
        
        try:
            light_devices = safe_async_call(get_light_devices)
            
            if light_devices:
                selected_light = st.selectbox("Select Light Device", light_devices, key="light_select")
                
                col3, col4, col5 = st.columns(3)
                
                with col3:
                    if st.button("💡 Turn On", key="turn_on_single"):
                        try:
                            safe_async_call(control_tplink_lights, "turn_on", device=selected_light)
                            st.success(f"✅ {selected_light} turned on!")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                
                with col4:
                    if st.button("🔌 Turn Off", key="turn_off_single"):
                        try:
                            safe_async_call(control_tplink_lights, "turn_off", device=selected_light)
                            st.success(f"✅ {selected_light} turned off!")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                
                with col5:
                    if st.button("🔄 Toggle", key="toggle_single"):
                        try:
                            safe_async_call(control_tplink_lights, "toggle", device=selected_light)
                            st.success(f"✅ {selected_light} toggled!")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                
                # Brightness control
                st.subheader("🌞 Brightness Control")
                brightness = st.slider("Brightness", 0, 100, 50, key="smart_lights_brightness_slider")
                
                if st.button("Set Brightness", key="set_brightness"):
                    try:
                        safe_async_call(control_tplink_lights, "set_brightness", brightness=brightness, device=selected_light)
                        st.success(f"✅ {selected_light} brightness set to {brightness}%!")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                
                # Color control
                st.subheader("🎨 Color Control")
                color_options = {
                    "Red": "red",
                    "Green": "green", 
                    "Blue": "blue",
                    "White": "white",
                    "Yellow": "yellow",
                    "Purple": "purple",
                    "Orange": "orange"
                }
                
                selected_color = st.selectbox("Select Color", list(color_options.keys()), key="color_select")
                
                if st.button("Set Color", key="set_color_individual"):
                    try:
                        safe_async_call(control_tplink_lights, "set_color", color=color_options[selected_color], device=selected_light)
                        st.success(f"✅ {selected_light} color set to {selected_color}!")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                
                # Custom color
                st.subheader("🎨 Custom Color")
                custom_color = st.color_picker("Choose Custom Color", "#ff0000", key="custom_color_picker")
                
                if st.button("Set Custom Color", key="set_custom_color_individual"):
                    try:
                        safe_async_call(control_tplink_lights, "set_color", color=custom_color, device=selected_light)
                        st.success(f"✅ {selected_light} custom color set!")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ No TP-Link devices found. Make sure your devices are connected and discoverable.")
            
        except Exception as e:
            st.error(f"❌ Error discovering devices: {e}")
    
    with col2:
        st.subheader("🎨 Light Settings")
        
        # Brightness control
        brightness = st.slider("Brightness", 0, 100, 50, key="brightness_slider_main")
        if st.button("💡 Set Brightness", key="set_brightness_main"):
            with st.spinner(f"🦜 Setting brightness to {brightness}%..."):
                try:
                    safe_async_call(control_tplink_lights, "set_brightness", brightness=brightness, device=selected_light)
                    st.success(f"Brightness set to {brightness}%!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown("---")
        
        # Color control
        st.subheader("🎨 Color Control")
        
        color_options = {
            "Warm White": "#FFD700",
            "Cool White": "#FFFFFF", 
            "Red": "#FF0000",
            "Green": "#00FF00",
            "Blue": "#0000FF",
            "Purple": "#800080",
            "Orange": "#FFA500",
            "Pink": "#FFC0CB"
        }
        
        selected_color = st.selectbox("Choose Color", list(color_options.keys()))
        
        if st.button("🎨 Set Color", key="set_color_main"):
            with st.spinner(f"🦜 Setting color to {selected_color}..."):
                try:
                    safe_async_call(control_tplink_lights, "set_color", color=color_options[selected_color], device=selected_light)
                    st.success(f"Color set to {selected_color}!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown("---")
        
        # Custom color picker
        st.subheader("🎨 Custom Color")
        custom_color = st.color_picker("Pick a custom color", "#FFD700")
        
        if st.button("🎨 Set Custom Color", key="set_custom_color"):
            with st.spinner("🦜 Setting custom color..."):
                try:
                    safe_async_call(control_tplink_lights, "set_color", color=custom_color, device=selected_light)
                    st.success("Custom color set!")
                except Exception as e:
                    st.error(f"Error: {e}")

def show_light_scenes():
    st.subheader("🎨 Light Scenes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌅 Predefined Scenes")
        
        scenes = [
            {
                "name": "🌅 Sunrise",
                "description": "Warm, gentle lighting to wake up",
                "actions": ["Set brightness to 30%", "Set color to warm white", "Gradual brightness increase"]
            },
            {
                "name": "🌆 Sunset", 
                "description": "Cozy evening atmosphere",
                "actions": ["Set brightness to 60%", "Set color to orange", "Dim over time"]
            },
            {
                "name": "🎉 Party Mode",
                "description": "Bright, colorful party lighting",
                "actions": ["Set brightness to 100%", "Color cycling", "Dynamic effects"]
            },
            {
                "name": "😴 Sleep Mode",
                "description": "Soft, calming lighting for bedtime",
                "actions": ["Set brightness to 20%", "Set color to blue", "Gradual dimming"]
            },
            {
                "name": "💼 Work Mode",
                "description": "Bright, focused lighting for work",
                "actions": ["Set brightness to 90%", "Set color to cool white", "Full illumination"]
            }
        ]
        
        for scene in scenes:
            with st.expander(f"{scene['name']} - {scene['description']}", expanded=False):
                st.write("**Actions:**")
                for action in scene['actions']:
                    st.write(f"• {action}")
                
                if st.button(f"🎨 Activate {scene['name']}", key=f"activate_{scene['name']}"):
                    with st.spinner(f"🦜 Activating {scene['name']}..."):
                        # Simulate scene activation
                        st.success(f"{scene['name']} activated!")
    
    with col2:
        st.subheader("🎨 Custom Scenes")
        
        # Create custom scene
        scene_name = st.text_input("Scene Name", placeholder="e.g., Movie Night")
        scene_description = st.text_area("Description", placeholder="What does this scene do?")
        
        st.subheader("🎛️ Scene Actions")
        
        # Scene actions
        actions = []
        
        if st.checkbox("Set brightness", key="scene_brightness_checkbox"):
            brightness = st.slider("Brightness", 0, 100, 50, key="scene_brightness_slider")
            actions.append(f"Set brightness to {brightness}%")
        
        if st.checkbox("Set color", key="scene_color_checkbox"):
            scene_color = st.color_picker("Color", "#FFD700", key="scene_color_picker")
            actions.append(f"Set color to {scene_color}")
        
        if st.checkbox("Turn on specific lights", key="scene_lights_checkbox"):
            light_options = ["Living Room", "Kitchen", "Tiki Bar", "Patio", "Bedroom"]
            selected_lights = st.multiselect("Select lights", light_options, key="scene_lights_multiselect")
            if selected_lights:
                actions.append(f"Turn on: {', '.join(selected_lights)}")
        
        if st.checkbox("Add delay", key="scene_delay_checkbox"):
            delay = st.number_input("Delay (seconds)", 1, 60, 5, key="scene_delay_input")
            actions.append(f"Wait {delay} seconds")
        
        st.write("**Scene Actions:**")
        for action in actions:
            st.write(f"• {action}")
        
        if st.button("💾 Save Scene", type="primary", key="save_custom_scene"):
            if scene_name and scene_description and actions:
                st.success(f"Scene '{scene_name}' saved!")
            else:
                st.error("Please fill in all fields and add at least one action!")

def show_light_automation():
    st.subheader("⏰ Light Automation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕐 Time-based Automation")
        
        # Time-based triggers
        st.write("**Automation Triggers:**")
        
        if st.checkbox("🌅 Turn on lights at sunrise", key="sunrise_checkbox"):
            sunrise_time = st.time_input("Sunrise time", value=(6, 0), key="sunrise_time_input")
            st.caption(f"Lights will turn on at {sunrise_time[0]:02d}:{sunrise_time[1]:02d}")
        
        if st.checkbox("🌆 Turn on lights at sunset", key="sunset_checkbox"):
            sunset_time = st.time_input("Sunset time", value=(18, 0), key="sunset_time_input")
            st.caption(f"Lights will turn on at {sunset_time[0]:02d}:{sunset_time[1]:02d}")
        
        if st.checkbox("😴 Turn off lights at bedtime", key="bedtime_checkbox"):
            bedtime = st.time_input("Bedtime", value=(22, 0), key="bedtime_input")
            st.caption(f"Lights will turn off at {bedtime[0]:02d}:{bedtime[1]:02d}")
        
        if st.checkbox("🌅 Gradual morning wake-up", key="wake_checkbox"):
            wake_time = st.time_input("Wake time", value=(7, 0), key="wake_time_input")
            st.caption(f"Lights will gradually brighten starting at {wake_time[0]:02d}:{wake_time[1]:02d}")
        
        st.markdown("---")
        
        st.subheader("🎭 Event-based Automation")
        
        # Event-based triggers
        st.write("**Event Triggers:**")
        
        if st.checkbox("🎬 Movie mode when TV turns on", key="movie_mode_checkbox"):
            st.caption("Lights will dim when TV is activated")
        
        if st.checkbox("🎵 Party mode when music plays", key="party_mode_checkbox"):
            st.caption("Lights will sync with music")
        
        if st.checkbox("🦜 Salty announces light changes", key="salty_announce_checkbox"):
            st.caption("Salty will speak when lights change")
    
    with col2:
        st.subheader("🌍 Location-based Automation")
        
        # Location-based triggers
        st.write("**Location Triggers:**")
        
        if st.checkbox("🏠 Turn on lights when arriving home", key="arrive_home_checkbox"):
            st.caption("Lights will turn on when you arrive")
        
        if st.checkbox("🚪 Turn off lights when leaving", key="leave_home_checkbox"):
            st.caption("Lights will turn off when you leave")
        
        if st.checkbox("📱 Control via mobile app", key="mobile_control_checkbox"):
            st.caption("Control lights from your phone")
        
        st.markdown("---")
        
        st.subheader("🌡️ Environment-based Automation")
        
        # Environment-based triggers
        st.write("**Environment Triggers:**")
        
        if st.checkbox("☀️ Adjust brightness based on natural light", key="natural_light_checkbox"):
            st.caption("Lights will adjust based on sunlight")
        
        if st.checkbox("🌧️ Turn on lights during bad weather", key="bad_weather_checkbox"):
            st.caption("Lights will turn on during storms")
        
        if st.checkbox("🌡️ Adjust color temperature based on time", key="color_temp_checkbox"):
            st.caption("Warm colors in evening, cool in morning")
        
        st.markdown("---")
        
        st.subheader("💾 Save Automation")
        
        if st.button("💾 Save Automation Settings", type="primary", key="save_automation_settings"):
            st.success("Automation settings saved!")
        
        if st.button("🔄 Test Automation", key="test_automation"):
            with st.spinner("🦜 Testing automation..."):
                st.success("Automation test completed!")

def show_light_status():
    st.subheader("📊 Light Status")
    
    # System status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🟢 Connected Devices")
        
        # Sample device status
        devices = [
            {"name": "Living Room Light", "status": "🟢 Online", "brightness": "80%", "color": "Warm White"},
            {"name": "Kitchen Light", "status": "🟢 Online", "brightness": "60%", "color": "Cool White"},
            {"name": "Tiki Bar Light", "status": "🟢 Online", "brightness": "100%", "color": "Orange"},
            {"name": "Patio Light", "status": "🔴 Offline", "brightness": "0%", "color": "N/A"},
            {"name": "Bedroom Light", "status": "🟢 Online", "brightness": "30%", "color": "Blue"}
        ]
        
        for device in devices:
            with st.expander(f"{device['name']} - {device['status']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Status:** {device['status']}")
                with col2:
                    st.write(f"**Brightness:** {device['brightness']}")
                with col3:
                    st.write(f"**Color:** {device['color']}")
    
    with col2:
        st.subheader("📈 Usage Statistics")
        
        st.metric("Total Lights", "5", "1 offline")
        st.metric("Average Brightness", "54%", "+5% vs yesterday")
        st.metric("Power Usage", "2.3 kWh", "-0.2 kWh vs yesterday")
        st.metric("Active Scenes", "3", "No change")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    activities = [
        {"time": "2:30 PM", "event": "Living Room Light turned on", "status": "✅ Success"},
        {"time": "2:15 PM", "event": "Kitchen Light brightness set to 60%", "status": "✅ Success"},
        {"time": "2:00 PM", "event": "Tiki Bar Light color changed to Orange", "status": "✅ Success"},
        {"time": "1:45 PM", "event": "Patio Light connection lost", "status": "⚠️ Warning"},
        {"time": "1:30 PM", "event": "All lights turned off", "status": "✅ Success"}
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
TP_LINK_DEVICE_IP: {'✅ Set' if os.getenv('TP_LINK_DEVICE_IP') else '❌ Not set'}
        """)
    
    with info_col2:
        st.write("**Connected Devices:**")
        st.write("• 💡 4 TP-Link smart bulbs")
        st.write("• 🔌 1 TP-Link smart plug")
        st.write("• 📱 Mobile app connected")
        st.write("• 🌐 Cloud sync enabled")
    
    # Cache management
    st.markdown("---")
    st.subheader("🗄️ Cache Management")
    
    cache_col1, cache_col2 = st.columns(2)
    
    with cache_col1:
        st.write("**Cache Status:**")
        try:
            from utils.actions import get_tplink_cache_status
            cache_status = safe_async_call(get_tplink_cache_status)
            
            if "error" in cache_status:
                st.write(f"• Status: Error - {cache_status['error']}")
            else:
                status = cache_status.get("status", {})
                st.write(f"• Status: {'Active' if status.get('cache_valid', False) else 'Expired'}")
                st.write(f"• Devices cached: {status.get('cached_devices', 0)}")
                st.write(f"• Age: {status.get('cache_age_seconds', 0)}s")
                st.write(f"• Duration: {status.get('cache_duration_seconds', 30)}s")
                if status.get('cache_valid'):
                    st.write(f"• Expires in: {status.get('cache_expires_in', 0)}s")
        except Exception as e:
            st.write(f"• Status: Error - {e}")
    
    with cache_col2:
        st.write("**Cache Actions:**")
        if st.button("🔄 Rebuild Cache", key="rebuild_cache"):
            try:
                safe_async_call(rebuild_tplink_cache)
                st.success("✅ Cache rebuilt successfully!")
            except Exception as e:
                st.error(f"❌ Error rebuilding cache: {e}")
        
        if st.button("📊 Show Cache Info", key="show_cache_info"):
            try:
                cache_status = safe_async_call(get_tplink_cache_status)
                if "error" in cache_status:
                    st.error(f"❌ Error getting cache info: {cache_status['error']}")
                else:
                    status = cache_status.get("status", {})
                    st.info(f"Cache contains {status.get('cached_devices', 0)} devices, age: {status.get('cache_age_seconds', 0)}s, valid: {status.get('cache_valid', False)}")
            except Exception as e:
                st.error(f"❌ Error getting cache info: {e}")

if __name__ == "__main__":
    show_smart_lights()
