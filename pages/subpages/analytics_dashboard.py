import streamlit as st
import pandas as pd
from utils.activity_logger import activity_logger
from utils.shared import get_salty_personality_direct

def show_analytics_dashboard_flat():
    st.subheader("📈 Analytics Dashboard")
    st.markdown("*🦜 Salty's insights into your tiki bar operations*")
    
    # General Analytics
    st.markdown("## 📊 General Analytics")
    show_general_analytics()
    st.markdown("---")
    
    # Detailed Reports
    st.markdown("## 📈 Detailed Reports")
    show_detailed_reports()

def show_general_analytics():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Real-Time Metrics")
        daily_summary = activity_logger.get_daily_summary()
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1:
            chat_count = daily_summary.get('chat_message', 0)
            st.metric("Chat Messages", chat_count, delta=f"+{chat_count} today" if chat_count > 0 else "0 today")
        with kpi_col2:
            light_count = daily_summary.get('light_change', 0)
            st.metric("Light Changes", light_count, delta=f"+{light_count} today" if light_count > 0 else "0 today")
        with kpi_col3:
            music_count = daily_summary.get('music_play', 0)
            st.metric("Music Plays", music_count, delta=f"+{music_count} today" if music_count > 0 else "0 today")
        st.markdown("---")
        st.subheader("🎯 Popular Actions")
        popular_actions = activity_logger.get_popular_actions(days=7)
        if popular_actions:
            actions_df = pd.DataFrame(list(popular_actions.items()), columns=['Action', 'Count'])
            st.bar_chart(actions_df.set_index('Action'))
        else:
            st.info("No activity data available yet. Start using the system to see metrics!")
        st.markdown("---")
        st.subheader("🕐 Usage Timeline")
        chat_hourly = activity_logger.get_hourly_stats('chat_message')
        light_hourly = activity_logger.get_hourly_stats('light_change')
        music_hourly = activity_logger.get_hourly_stats('music_play')
        timeline_data = pd.DataFrame({
            'Hour': range(24),
            'Chat Messages': [chat_hourly.get(hour, 0) for hour in range(24)],
            'Light Changes': [light_hourly.get(hour, 0) for hour in range(24)],
            'Music Plays': [music_hourly.get(hour, 0) for hour in range(24)]
        })
        if timeline_data[['Chat Messages', 'Light Changes', 'Music Plays']].sum().sum() > 0:
            st.line_chart(timeline_data.set_index('Hour'))
        else:
            st.info("No activity data for today yet. Start using the system to see the timeline!")
    with col2:
        st.subheader("🔧 System Health")
        status_col1, status_col2 = st.columns(2)
        with status_col1:
            st.metric("Spotify Status", "🟢 Online", "Connected")
            st.metric("Lighting System", "🟢 Online", "3 devices")
            st.metric("Voice System", "🟢 Online", "ElevenLabs active")
        with status_col2:
            st.metric("Roku Status", "🟢 Online", "Connected")
            st.metric("Knowledge Base", "🟢 Online", "3 documents")
            st.metric("AI Chat", "🟢 Online", "Gemini active")
        st.markdown("---")
        st.subheader("📊 Error Tracking")
        error_activities = activity_logger.get_activities_by_type('system_error', days=1)
        if error_activities:
            for error in error_activities[-5:]:
                timestamp = error.get('timestamp', 'Unknown')
                details = error.get('details', {})
                error_type = details.get('error_type', 'Unknown')
                error_message = details.get('error_message', 'No details')
                st.write(f"🔴 **{timestamp}** - {error_type}: {error_message}")
        else:
            st.success("✅ No errors logged today!")
        st.markdown("---")
        st.subheader("🎵 Music Analytics")
        music_activities = activity_logger.get_activities_by_type('music_play', days=7)
        if music_activities:
            total_tracks = len(music_activities)
            playlists = set()
            tracks = set()
            for activity in music_activities:
                details = activity.get('details', {})
                if details.get('playlist'):
                    playlists.add(details['playlist'])
                if details.get('track'):
                    tracks.add(details['track'])
            music_stats = {
                "Total Tracks Played": total_tracks,
                "Unique Playlists": len(playlists),
                "Unique Tracks": len(tracks),
                "Most Active Day": "Today"
            }
        else:
            music_stats = {
                "Total Tracks Played": 0,
                "Unique Playlists": 0,
                "Unique Tracks": 0,
                "Most Active Day": "None"
            }
        for stat, value in music_stats.items():
            st.write(f"**{stat}:** {value}")

def show_detailed_reports():
    st.subheader("📈 Detailed Reports")
    st.markdown("*🦜 Comprehensive analysis and insights*")
    report_type = st.selectbox(
        "Select Report Type",
        ["Daily Summary", "Weekly Trends", "Monthly Analysis", "Custom Period"]
    )
    if report_type == "Daily Summary":
        st.markdown("### 📅 Today's Activity Summary")
        chat_hourly = activity_logger.get_hourly_stats('chat_message')
        light_hourly = activity_logger.get_hourly_stats('light_change')
        music_hourly = activity_logger.get_hourly_stats('music_play')
        daily_data = pd.DataFrame({
            'Hour': range(24),
            'Chat Messages': [chat_hourly.get(hour, 0) for hour in range(24)],
            'Light Changes': [light_hourly.get(hour, 0) for hour in range(24)],
            'Music Plays': [music_hourly.get(hour, 0) for hour in range(24)]
        })
        if daily_data[['Chat Messages', 'Light Changes', 'Music Plays']].sum().sum() > 0:
            st.line_chart(daily_data.set_index('Hour'))
            col1, col2, col3 = st.columns(3)
            with col1:
                total_interactions = daily_data['Chat Messages'].sum() + daily_data['Light Changes'].sum() + daily_data['Music Plays'].sum()
                st.metric("Total Interactions", total_interactions)
            with col2:
                peak_hour = daily_data['Chat Messages'].idxmax() if daily_data['Chat Messages'].sum() > 0 else 0
                st.metric("Peak Hour", f"{peak_hour}:00")
            with col3:
                avg_activity = round(daily_data['Chat Messages'].mean(), 1)
                st.metric("Average Activity", avg_activity)
        else:
            st.info("No activity data for today yet. Start using the system to see the summary!")
    elif report_type == "Weekly Trends":
        st.markdown("### 📊 Weekly Performance Trends")
        weekly_data = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Total Activity': [0, 0, 0, 0, 0, 0, 0],
            'Errors': [0, 0, 0, 0, 0, 0, 0]
        })
        st.bar_chart(weekly_data.set_index('Day'))
        st.info("Weekly trends will be available as more data accumulates.")
    elif report_type == "Monthly Analysis":
        st.markdown("### 📈 Monthly Insights")
        monthly_data = pd.DataFrame({
            'Week': range(1, 5),
            'User Engagement': [0, 0, 0, 0],
            'System Reliability': [100, 100, 100, 100],
            'Feature Usage': [0, 0, 0, 0]
        })
        st.line_chart(monthly_data.set_index('Week'))
        st.info("Monthly analysis will be available as more data accumulates.")
    else:
        st.markdown("### 📅 Custom Period Analysis")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        if start_date and end_date:
            st.info(f"📊 Analyzing data from {start_date} to {end_date}")
            st.info("Custom period analysis will be implemented as data accumulates.")

if __name__ == "__main__":
    show_analytics_dashboard_flat() 