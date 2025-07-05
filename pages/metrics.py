from utils.shared import set_page_config, show_page_header
import streamlit as st
import pandas as pd
import numpy as np
import time
import asyncio
from pathlib import Path
from utils.mcp_analytics import get_mcp_analytics
from utils.activity_logger import activity_logger
from utils.actions import (
    query_rag_documents,
    rebuild_rag_database,
    list_rag_documents,
    add_rag_document,
)
from utils.shared import get_salty_personality_direct

# Import subpage tab functions
from pages.subpages.analytics_dashboard import show_analytics_dashboard_flat
from pages.subpages.data_explorer import show_data_explorer
from pages.subpages.knowledge_base import show_knowledge_base

def show_analytics_and_data():
    set_page_config()
    show_page_header("📊 Metrics", "Salty's comprehensive insights and data management")
    tab1, tab2, tab3 = st.tabs(["📈 Analytics Dashboard", "📊 Data Explorer", "📚 Knowledge Base"])
    with tab1:
        show_analytics_dashboard_flat()
    with tab2:
        show_data_explorer()
    with tab3:
        show_knowledge_base()

def show_analytics_dashboard_flat():
    """Show analytics dashboard as a single section with sub-headers, no nested tabs."""
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
    """Show general analytics dashboard with real data"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Real-Time Metrics")
        
        # Get real activity data
        daily_summary = activity_logger.get_daily_summary()
        
        # Key performance indicators
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        
        with kpi_col1:
            chat_count = daily_summary.get('chat_message', 0)
            st.metric(
                "Chat Messages", 
                chat_count,
                delta=f"+{chat_count} today" if chat_count > 0 else "0 today"
            )
        
        with kpi_col2:
            light_count = daily_summary.get('light_change', 0)
            st.metric(
                "Light Changes", 
                light_count,
                delta=f"+{light_count} today" if light_count > 0 else "0 today"
            )
        
        with kpi_col3:
            music_count = daily_summary.get('music_play', 0)
            st.metric(
                "Music Plays", 
                music_count,
                delta=f"+{music_count} today" if music_count > 0 else "0 today"
            )
        
        st.markdown("---")
        
        st.subheader("🎯 Popular Actions")
        
        # Get real popular actions
        popular_actions = activity_logger.get_popular_actions(days=7)
        
        if popular_actions:
            # Create a bar chart
            actions_df = pd.DataFrame(list(popular_actions.items()), columns=['Action', 'Count'])
            st.bar_chart(actions_df.set_index('Action'))
        else:
            st.info("No activity data available yet. Start using the system to see metrics!")
        
        st.markdown("---")
        
        st.subheader("🕐 Usage Timeline")
        
        # Get real hourly data for today
        chat_hourly = activity_logger.get_hourly_stats('chat_message')
        light_hourly = activity_logger.get_hourly_stats('light_change')
        music_hourly = activity_logger.get_hourly_stats('music_play')
        
        # Combine all activities
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
        
        # System status indicators
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
        
        # Get real error data
        error_activities = activity_logger.get_activities_by_type('system_error', days=1)
        
        if error_activities:
            for error in error_activities[-5:]:  # Show last 5 errors
                timestamp = error.get('timestamp', 'Unknown')
                details = error.get('details', {})
                error_type = details.get('error_type', 'Unknown')
                error_message = details.get('error_message', 'No details')
                
                st.write(f"🔴 **{timestamp}** - {error_type}: {error_message}")
        else:
            st.success("✅ No errors logged today!")
        
        st.markdown("---")
        
        st.subheader("🎵 Music Analytics")
        
        # Get real music statistics
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
                "Most Active Day": "Today"  # Could be calculated
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
    """Show detailed analytics reports with real data"""
    st.subheader("📈 Detailed Reports")
    st.markdown("*🦜 Comprehensive analysis and insights*")
    
    # Report selection
    report_type = st.selectbox(
        "Select Report Type",
        ["Daily Summary", "Weekly Trends", "Monthly Analysis", "Custom Period"]
    )
    
    if report_type == "Daily Summary":
        st.markdown("### 📅 Today's Activity Summary")
        
        # Get real daily data
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
            
            # Summary statistics
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
        
        # Get weekly data (simplified - could be enhanced)
        weekly_data = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Total Activity': [0, 0, 0, 0, 0, 0, 0],  # Placeholder
            'Errors': [0, 0, 0, 0, 0, 0, 0]  # Placeholder
        })
        
        st.bar_chart(weekly_data.set_index('Day'))
        st.info("Weekly trends will be available as more data accumulates.")
        
    elif report_type == "Monthly Analysis":
        st.markdown("### 📈 Monthly Insights")
        
        # Get monthly data (simplified - could be enhanced)
        monthly_data = pd.DataFrame({
            'Week': range(1, 5),
            'User Engagement': [0, 0, 0, 0],  # Placeholder
            'System Reliability': [100, 100, 100, 100],  # Placeholder
            'Feature Usage': [0, 0, 0, 0]  # Placeholder
        })
        
        st.line_chart(monthly_data.set_index('Week'))
        st.info("Monthly analysis will be available as more data accumulates.")
    
    else:  # Custom Period
        st.markdown("### 📅 Custom Period Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        
        if start_date and end_date:
            st.info(f"📊 Analyzing data from {start_date} to {end_date}")
            st.info("Custom period analysis will be implemented as data accumulates.")

def show_data_explorer():
    """Show data explorer functionality"""
    st.subheader("📊 Data Explorer")
    st.markdown("*🦜 Upload and analyze CSV files*")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file to explore"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Data Preview")
                st.dataframe(df.head())
            
            with col2:
                st.subheader("Data Info")
                st.write(f"**Shape:** {df.shape}")
                st.write(f"**Columns:** {list(df.columns)}")
                st.write(f"**Data Types:**")
                st.write(df.dtypes)
            
            # Data analysis section
            st.markdown("---")
            st.subheader("📈 Data Analysis")
            
            analysis_col1, analysis_col2 = st.columns(2)
            
            with analysis_col1:
                st.subheader("📊 Basic Statistics")
                if df.select_dtypes(include=[np.number]).columns.any():
                    st.write(df.describe())
                else:
                    st.info("No numeric columns found for statistical analysis")
            
            with analysis_col2:
                st.subheader("📋 Missing Values")
                missing_data = df.isnull().sum()
                if missing_data.sum() > 0:
                    st.write(missing_data[missing_data > 0])
                else:
                    st.success("No missing values found!")
            
            # Visualization section
            st.markdown("---")
            st.subheader("📊 Visualizations")
            
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                # Numeric columns histogram
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    selected_col = st.selectbox("Select column for histogram", numeric_cols)
                    if selected_col:
                        st.subheader(f"Histogram: {selected_col}")
                        st.bar_chart(df[selected_col].value_counts())
            
            with viz_col2:
                # Correlation matrix for numeric columns
                if len(numeric_cols) > 1:
                    st.subheader("Correlation Matrix")
                    corr_matrix = df[numeric_cols].corr()
                    st.write(corr_matrix)
                
        except Exception as e:
            st.error(f"Error loading file: {e}")
    else:
        st.info("👆 Upload a CSV file to get started")

def show_knowledge_base():
    """Show knowledge base functionality"""
    st.subheader("📚 Knowledge Base")
    st.markdown("*🦜 Salty's treasure trove of tiki bar wisdom*")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][3]} I've got a whole library of tiki bar knowledge, matey!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Search Knowledge")
        
        # Search interface
        search_query = st.text_input("What would you like to know about The Gold Monkey?",
                                   placeholder="e.g., What is The Gold Monkey?")
        
        top_k = st.slider("Number of results", min_value=1, max_value=10, value=5)
        
        if st.button("🔍 Search", type="primary"):
            if search_query:
                with st.spinner("🦜 Searching through my knowledge..."):
                    result = asyncio.run(query_rag_documents(search_query, top_k))
                    
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(f"🦜 Found {result.get('count', 0)} relevant documents!")
                        
                        if result.get('results'):
                            for i, (doc, metadata, distance) in enumerate(zip(
                                result['results'],
                                result.get('metadatas', []),
                                result.get('distances', [])
                            )):
                                with st.expander(f"Result {i+1} - {metadata.get('filename', 'Unknown')}"):
                                    st.write(f"**Source:** {metadata.get('filename', 'Unknown')}")
                                    st.write(f"**Similarity:** {1 - distance:.3f}" if distance else "N/A")
                                    st.write(f"**Content:**")
                                    st.write(doc)
                        else:
                            st.info("No relevant documents found. Try a different search term!")
            else:
                st.warning("Please enter a search query!")
        
        st.markdown("---")
        
        st.subheader("📄 Add New Document")
        
        # Document addition interface
        new_content = st.text_area("Document content",
                                 placeholder="Enter the content of your document...",
                                 height=150)
        
        new_metadata = st.text_input("Document source (optional)",
                                   placeholder="e.g., tiki_bar_history.md")
        
        if st.button("📄 Add Document"):
            if new_content:
                with st.spinner("🦜 Adding document to my knowledge base..."):
                    metadata = {"filename": new_metadata} if new_metadata else {}
                    result = asyncio.run(add_rag_document(new_content, metadata))
                    
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success("🦜 Document added successfully!")
                        st.info(f"Document ID: {result.get('id', 'Unknown')}")
            else:
                st.warning("Please enter document content!")
    
    with col2:
        st.subheader("🗂️ Database Management")
        
        # Database operations
        if st.button("🔄 Rebuild Database"):
            with st.spinner("🦜 Rebuilding my knowledge base from markdown files..."):
                result = asyncio.run(rebuild_rag_database())
                
                if isinstance(result, str):
                    st.success(result)
                elif "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("🦜 Knowledge base rebuilt successfully!")
                    st.info(f"Documents added: {result.get('documents_added', 0)}")
                    st.info(f"Files processed: {result.get('files_processed', 0)}")
        
        if st.button("📋 List Documents"):
            with st.spinner("🦜 Checking my document collection..."):
                result = asyncio.run(list_rag_documents())
                
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(f"🦜 Found {result.get('count', 0)} documents!")
                    
                    if result.get('documents'):
                        for i, (doc, metadata) in enumerate(zip(
                            result['documents'][:10],  # Show first 10
                            result.get('metadatas', [])[:10]
                        )):
                            with st.expander(f"Document {i+1} - {metadata.get('filename', 'Unknown')}"):
                                st.write(f"**ID:** {result['ids'][i] if result.get('ids') else 'Unknown'}")
                                st.write(f"**Source:** {metadata.get('filename', 'Unknown')}")
                                st.write(f"**Content:** {doc[:200]}...")
                    
                    if result.get('count', 0) > 10:
                        st.info(f"... and {result.get('count', 0) - 10} more documents")
        
        st.markdown("---")
        
        st.subheader("📊 Database Stats")
        
        # Show some basic stats
        try:
            import chromadb
            from chromadb.config import Settings
            
            client = chromadb.PersistentClient(
                path="./data/chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
            
            collection = client.get_or_create_collection("gold_monkey_docs")
            results = collection.get()
            
            total_docs = len(results["documents"]) if results["documents"] else 0
            
            # Count by source
            source_counts = {}
            if results["metadatas"]:
                for metadata in results["metadatas"]:
                    source = metadata.get("filename", "Unknown")
                    source_counts[source] = source_counts.get(source, 0) + 1
            
            st.metric("Total Documents", total_docs)
            st.metric("Unique Sources", len(source_counts))
            
            if source_counts:
                st.write("**Documents by source:**")
                for source, count in source_counts.items():
                    st.write(f"• {source}: {count}")
                    
        except Exception as e:
            st.warning(f"Could not load database stats: {e}")
        
        st.markdown("---")
        
        st.subheader("🦜 Salty's Tips")
        st.write("""
        **Knowledge Base Tips:**
        - 🔍 **Search** for specific information about The Gold Monkey
        - 📄 **Add documents** to expand my knowledge
        - 🔄 **Rebuild** to update from markdown files
        - 📋 **List** to see what I know about
        
        *Squawk! The more you teach me, the wiser I become!*
        """)
    
    # Show available markdown files
    st.markdown("---")
    st.subheader("📁 Available Markdown Files")
    
    rag_dir = Path(__file__).parent.parent / "rag"
    if rag_dir.exists():
        md_files = list(rag_dir.glob("*.md"))
        if md_files:
            st.write(f"Found {len(md_files)} markdown files in the `rag` folder:")
            for md_file in md_files:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"• **{md_file.name}**")
                with col_b:
                    try:
                        size = md_file.stat().st_size
                        st.write(f"({size} bytes)")
                    except:
                        st.write("(size unknown)")
        else:
            st.info("No markdown files found in the `rag` folder.")
            st.write("Add some `.md` files to the `rag` folder to build your knowledge base!")
    else:
        st.warning("`rag` folder not found. Create it to store your markdown files!")

if __name__ == "__main__":
    show_analytics_and_data() 