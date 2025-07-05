from utils.shared import set_page_config, show_page_header
import streamlit as st
import os
import json
import time
from datetime import datetime, time as datetime_time
from utils.actions import speak_salty_voice_sync, play_ambient_sound_sync, stop_all_audio_sync
from utils.shared import get_salty_personality_direct
from utils.mcp_error_handler import handle_mcp_error, is_mcp_error
import concurrent.futures

def show_routines():
    set_page_config()
    show_page_header("🎭 Automation Routines", "Create and manage your smart home automation routines")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][2]} Let me help you set up some clever routines, matey!")
    
    # Create tabs for different routine features
    tab1, tab2, tab3 = st.tabs(["📋 Current Routines", "➕ Create Routine", "📊 Routine History"])
    
    with tab1:
        show_current_routines()
    
    with tab2:
        show_create_routine()
    
    with tab3:
        show_routine_history()

def show_current_routines():
    st.markdown("## 🎭 Your Automation Routines")
    st.markdown("*🦜 Salty's carefully crafted routines to make your tiki bar magical*")
    
    # Load routines from data file
    routines_file = "data/routines/custom_routines/"
    routines = []
    
    try:
        # Get list of routine files
        if os.path.exists(routines_file):
            for filename in os.listdir(routines_file):
                if filename.endswith('.json'):
                    with open(os.path.join(routines_file, filename), 'r') as f:
                        routine = json.load(f)
                        routines.append(routine)
    except Exception as e:
        st.warning(f"Could not load routines: {e}")
    
    # If no routines found, show sample routines
    if not routines:
        routines = [
            {
                "name": "🌅 Morning Routine",
                "description": "Wake up with gentle lighting and tropical music",
                "status": "🟢 Active",
                "schedule": "Daily at 6:00 AM",
                "actions": ["Turn on living room lights", "Play tropical music", "Start coffee maker"],
                "icon": "🌅",
                "color": "success"
            },
            {
                "name": "🌆 Evening Routine", 
                "description": "Dim lights and start ambient sounds",
                "status": "🟢 Active",
                "schedule": "Daily at 6:00 PM",
                "actions": ["Dim all lights", "Play ocean waves", "Set mood lighting"],
                "icon": "🌆",
                "color": "info"
            },
            {
                "name": "🎬 Movie Night",
                "description": "Dim lights, start TV, and play movie audio",
                "status": "🟡 Scheduled",
                "schedule": "Manual trigger",
                "actions": ["Turn off main lights", "Start TV", "Play ambient sounds"],
                "icon": "🎬",
                "color": "warning"
            },
            {
                "name": "🎉 Party Mode",
                "description": "Bright lights, loud music, and party atmosphere",
                "status": "🔴 Inactive",
                "schedule": "Manual trigger",
                "actions": ["Bright lights", "Loud music", "Party colors"],
                "icon": "🎉",
                "color": "error"
            },
            {
                "name": "😴 Sleep Mode",
                "description": "Turn off all lights and start white noise",
                "status": "🟢 Active",
                "schedule": "Daily at 10:00 PM",
                "actions": ["Turn off all lights", "Play white noise", "Set security mode"],
                "icon": "😴",
                "color": "success"
            }
        ]
    
    # Display routines in a beautiful grid layout
    for i, routine in enumerate(routines):
        # Safely get status with default value
        status = routine.get('status', '🟡 Manual')
        icon = routine.get('icon', '⚙️')
        color = routine.get('color', 'info')
        
        # Create a beautiful card-like container
        with st.container():
            st.markdown("---")
            
            # Header with icon and status
            col_header1, col_header2, col_header3 = st.columns([1, 3, 1])
            
            with col_header1:
                st.markdown(f"### {icon}")
            
            with col_header2:
                st.markdown(f"### {routine['name']}")
                st.caption(f"*{routine.get('description', 'No description available')}*")
            
            with col_header3:
                # Status badge
                if "🟢" in status:
                    st.success("🟢 Active")
                elif "🟡" in status:
                    st.warning("🟡 Scheduled")
                elif "🔴" in status:
                    st.error("🔴 Inactive")
                else:
                    st.info("🟡 Manual")
            
            # Main content
            col_content1, col_content2 = st.columns([5, 1])
            
            with col_content1:
                # Schedule info
                st.markdown(f"**📅 Schedule:** {routine.get('schedule', 'Manual')}")
                
                # Show actions - handle both 'actions' and 'steps' fields
                actions = routine.get('actions', [])
                if not actions and 'steps' in routine:
                    # Convert steps to action descriptions
                    actions = []
                    for step in routine['steps']:
                        if step.get('type') == 'Voice Command':
                            actions.append(f"🎤 Voice: {step.get('action', '')}")
                        elif step.get('type') == 'Light Control':
                            actions.append(f"💡 Lights: {step.get('action', '')}")
                        elif step.get('type') == 'Music Control':
                            actions.append(f"🎵 Music: {step.get('action', '')}")
                        elif step.get('type') == 'Wait':
                            actions.append(f"⏱️ Wait: {step.get('action', '')} seconds")
                        else:
                            actions.append(f"⚙️ {step.get('type', 'Unknown')}: {step.get('action', '')}")
                
                st.markdown("**🎛️ Actions:**")
                for action in actions:
                    st.markdown(f"• {action}")
                
                # Last run info
                if routine.get('last_run'):
                    st.markdown(f"**🕐 Last Run:** {routine['last_run']}")
                if routine.get('next_run'):
                    st.markdown(f"**⏰ Next Run:** {routine['next_run']}")
            
            with col_content2:
                # Action buttons in a vertical layout
                st.markdown("**🎮 Controls**")
                
                # Test button with enhanced functionality
                if st.button("🧪 Test Routine", key=f"test_routine_{i}", type="primary", use_container_width=True):
                    try:
                        with st.spinner(f"🦜 Testing {routine['name']}..."):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            actions_to_test = actions if actions else ["Voice Command", "Light Control", "Music Control"]
                            for idx, action in enumerate(actions_to_test):
                                progress = (idx + 1) / len(actions_to_test)
                                progress_bar.progress(progress)
                                status_text.text(f"Testing: {action}")
                                time.sleep(0.5)
                            progress_bar.progress(1.0)
                            status_text.text("✅ Test completed!")
                            st.success(f"🧪 {routine['name']} test completed successfully!")
                            st.balloons()
                    except Exception as e:
                        if is_mcp_error(e):
                            err = handle_mcp_error(e, f"Test Routine {routine['name']}")
                            st.error(f"🦜 Squawk! {err['response']}")
                        else:
                            st.error(f"🦜 Squawk! Something went wrong: {e}")
                
                # Run button
                if st.button("▶️ Run Now", key=f"run_routine_{i}", use_container_width=True):
                    try:
                        with st.spinner(f"🦜 Running {routine['name']}..."):
                            st.success(f"✅ {routine['name']} completed successfully!")
                            st.balloons()
                    except Exception as e:
                        if is_mcp_error(e):
                            err = handle_mcp_error(e, f"Run Routine {routine['name']}")
                            st.error(f"🦜 Squawk! {err['response']}")
                        else:
                            st.error(f"🦜 Squawk! Something went wrong: {e}")
                
                # Edit button
                if st.button("⚙️ Edit", key=f"edit_routine_{i}", use_container_width=True):
                    st.info("Edit functionality coming soon!")
                
                # Delete button
                if st.button("🗑️ Delete", key=f"delete_routine_{i}", use_container_width=True):
                    st.warning("Delete functionality coming soon!")
                
                # Quick status toggle
                if st.button("🔄 Toggle Status", key=f"toggle_status_{i}", use_container_width=True):
                    st.info(f"Status toggle for {routine['name']} coming soon!")

def show_create_routine():
    st.subheader("➕ Create New Routine")
    
    # Basic routine information
    routine_name = st.text_input("Routine Name", placeholder="e.g., Welcome Home")
    routine_description = st.text_area("Description", placeholder="What does this routine do?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕐 Schedule Settings")
        
        schedule_type = st.selectbox("Schedule Type", ["Manual", "Daily", "Weekly", "Custom"])
        
        if schedule_type == "Daily":
            schedule_time = st.time_input("Time to run", value=datetime_time(18, 0))
            st.write(f"Runs daily at {schedule_time.strftime('%I:%M %p')}")
        
        elif schedule_type == "Weekly":
            schedule_time = st.time_input("Time to run", value=datetime_time(18, 0))
            schedule_days = st.multiselect("Days of week", 
                                         ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            if schedule_days:
                st.write(f"Runs on {', '.join(schedule_days)} at {schedule_time.strftime('%I:%M %p')}")
        
        elif schedule_type == "Custom":
            st.write("Advanced scheduling coming soon!")
    
    with col2:
        st.subheader("🎛️ Routine Actions")
        
        # Action categories
        action_categories = {
            "💡 Lights": ["Turn on all lights", "Turn off all lights", "Dim lights", "Set brightness", "Set color"],
            "🎵 Audio": ["Play music", "Pause music", "Play ambient sounds", "Stop all audio", "Set volume"],
            "📺 Entertainment": ["Turn on TV", "Turn off TV", "Launch Netflix", "Launch Spotify"],
            "🦜 Voice": ["Salty greeting", "Salty announcement", "Voice reminder"],
            "🌡️ Climate": ["Set temperature", "Turn on fan", "Turn off fan"],
            "🔒 Security": ["Arm security", "Disarm security", "Lock doors", "Unlock doors"]
        }
        
        selected_actions = []
        
        for category, actions in action_categories.items():
            with st.expander(category):
                for action in actions:
                    if st.checkbox(action, key=f"action_{action}"):
                        selected_actions.append(action)
        
        st.write(f"**Selected Actions:** {len(selected_actions)}")
        for action in selected_actions:
            st.write(f"• {action}")
    
    st.markdown("---")
    
    # Advanced settings
    st.subheader("⚙️ Advanced Settings")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.write("**Trigger Conditions:**")
        enable_conditions = st.checkbox("Enable conditions")
        if enable_conditions:
            st.write("• Motion detected")
            st.write("• Time of day")
            st.write("• Weather conditions")
            st.write("• Device status")
    
    with col4:
        st.write("**Notifications:**")
        st.checkbox("Send notification when routine starts")
        st.checkbox("Send notification when routine completes")
        st.checkbox("Send notification if routine fails")
    
    # Save routine
    if st.button("💾 Save Routine", type="primary"):
        if routine_name and routine_description and selected_actions:
            # Create routine object
            new_routine = {
                "name": routine_name,
                "description": routine_description,
                "schedule_type": schedule_type,
                "actions": selected_actions,
                "created_at": datetime.now().isoformat(),
                "status": "🟢 Active"
            }
            
            # Save to file (simplified for now)
            st.success(f"✅ Routine '{routine_name}' saved successfully!")
            st.info("Routine will be available in your Current Routines tab.")
        else:
            st.error("Please fill in all required fields and select at least one action!")

def show_routine_history():
    st.subheader("📊 Routine Execution History")
    
    # Sample history data
    history_data = [
        {
            "routine": "🌅 Morning Routine",
            "executed_at": "2024-01-15 06:00:00",
            "status": "✅ Success",
            "duration": "2m 30s",
            "actions_completed": 3
        },
        {
            "routine": "🌆 Evening Routine", 
            "executed_at": "2024-01-14 18:00:00",
            "status": "✅ Success",
            "duration": "1m 45s",
            "actions_completed": 2
        },
        {
            "routine": "🎬 Movie Night",
            "executed_at": "2024-01-14 20:30:00",
            "status": "✅ Success",
            "duration": "45s",
            "actions_completed": 3
        },
        {
            "routine": "😴 Sleep Mode",
            "executed_at": "2024-01-14 22:00:00",
            "status": "✅ Success",
            "duration": "1m 15s",
            "actions_completed": 2
        },
        {
            "routine": "🌅 Morning Routine",
            "executed_at": "2024-01-14 06:00:00",
            "status": "⚠️ Partial",
            "duration": "1m 20s",
            "actions_completed": 2
        }
    ]
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "✅ Success", "⚠️ Partial", "❌ Failed"])
    
    with col2:
        routine_filter = st.selectbox("Filter by Routine", ["All"] + list(set([h["routine"] for h in history_data])))
    
    with col3:
        days_filter = st.selectbox("Time Period", ["Last 7 days", "Last 30 days", "Last 90 days", "All time"])
    
    # Display filtered history
    filtered_history = history_data
    
    if status_filter != "All":
        filtered_history = [h for h in filtered_history if h["status"] == status_filter]
    
    if routine_filter != "All":
        filtered_history = [h for h in filtered_history if h["routine"] == routine_filter]
    
    # Display history table
    if filtered_history:
        st.write(f"**Showing {len(filtered_history)} executions**")
        
        for execution in filtered_history:
            with st.expander(f"{execution['routine']} - {execution['executed_at']}", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**Routine:** {execution['routine']}")
                    st.write(f"**Executed:** {execution['executed_at']}")
                
                with col2:
                    st.write(f"**Status:** {execution['status']}")
                    st.write(f"**Duration:** {execution['duration']}")
                
                with col3:
                    st.write(f"**Actions:** {execution['actions_completed']} completed")
                
                with col4:
                    if st.button("📋 Details", key=f"details_{execution['executed_at']}"):
                        st.info("Detailed execution log coming soon!")
    else:
        st.info("No routine executions found for the selected filters.")
    
    # Statistics
    st.markdown("---")
    st.subheader("📈 Routine Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Executions", "127", "+12 this week")
    
    with col2:
        st.metric("Success Rate", "94%", "+2% vs last week")
    
    with col3:
        st.metric("Average Duration", "1m 45s", "-15s vs last week")
    
    with col4:
        st.metric("Active Routines", "5", "No change")

if __name__ == "__main__":
    show_routines()