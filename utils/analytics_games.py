#!/usr/bin/env python3
"""
Analytics Dashboard and Tiki Bar Games for Salty
Additional features for the Streamlit interface
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

def show_analytics_dashboard():
    st.header("📊 Analytics Dashboard")
    st.markdown("*🦜 Salty's insights into your tiki bar operations*")
    
    # Initialize session state for analytics
    if "analytics_data" not in st.session_state:
        st.session_state.analytics_data = {
            "chat_messages": 0,
            "light_changes": 0,
            "music_plays": 0,
            "voice_commands": 0,
            "system_errors": 0,
            "session_start": pd.Timestamp.now(),
            "popular_actions": {},
            "daily_stats": {}
        }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Real-Time Metrics")
        
        # Key performance indicators
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        
        with kpi_col1:
            st.metric(
                "Chat Messages", 
                st.session_state.analytics_data["chat_messages"],
                delta="+5 today"
            )
        
        with kpi_col2:
            st.metric(
                "Light Changes", 
                st.session_state.analytics_data["light_changes"],
                delta="+12 today"
            )
        
        with kpi_col3:
            st.metric(
                "Music Plays", 
                st.session_state.analytics_data["music_plays"],
                delta="+8 today"
            )
        
        st.markdown("---")
        
        st.subheader("🎯 Popular Actions")
        
        # Popular actions chart
        popular_actions = {
            "Play Music": 45,
            "Change Lights": 32,
            "Chat with Salty": 28,
            "Voice Commands": 15,
            "System Status": 12
        }
        
        # Create a bar chart
        actions_df = pd.DataFrame(list(popular_actions.items()), columns=['Action', 'Count'])
        st.bar_chart(actions_df.set_index('Action'))
        
        st.markdown("---")
        
        st.subheader("🕐 Usage Timeline")
        
        # Generate sample timeline data
        timeline_data = pd.DataFrame({
            'Time': pd.date_range(start='2024-01-01', periods=24, freq='h'),
            'Activity': np.random.randint(0, 10, 24)
        })
        
        st.line_chart(timeline_data.set_index('Time'))
    
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
        
        # Error log
        errors = [
            {"time": "2024-01-01 14:30", "error": "Spotify connection timeout", "severity": "Low"},
            {"time": "2024-01-01 12:15", "error": "Light bulb not responding", "severity": "Medium"},
            {"time": "2024-01-01 10:45", "error": "Voice synthesis failed", "severity": "Low"}
        ]
        
        for error in errors:
            severity_color = "🔴" if error["severity"] == "High" else "🟡" if error["severity"] == "Medium" else "🟢"
            st.write(f"{severity_color} **{error['time']}** - {error['error']} ({error['severity']})")
        
        st.markdown("---")
        
        st.subheader("🎵 Music Analytics")
        
        # Music statistics
        music_stats = {
            "Total Tracks Played": 156,
            "Most Played Genre": "Tropical",
            "Average Session Length": "2.5 hours",
            "Favorite Playlist": "Tiki Dave's"
        }
        
        for stat, value in music_stats.items():
            st.write(f"**{stat}:** {value}")
    
    # Detailed analytics section
    st.markdown("---")
    st.subheader("📋 Detailed Reports")
    
    report_col1, report_col2 = st.columns(2)
    
    with report_col1:
        st.subheader("🎭 User Engagement")
        
        # Engagement metrics
        engagement_data = pd.DataFrame({
            'Metric': ['Chat Messages', 'Voice Commands', 'Light Changes', 'Music Controls'],
            'Count': [28, 15, 32, 45],
            'Percentage': [20, 11, 23, 33]
        })
        
        st.dataframe(engagement_data, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("🌡️ Environmental Data")
        
        # Environmental metrics (simulated)
        env_data = pd.DataFrame({
            'Time': pd.date_range(start='2024-01-01', periods=12, freq='2h'),
            'Temperature': np.random.uniform(72, 78, 12),
            'Humidity': np.random.uniform(45, 55, 12)
        })
        
        st.line_chart(env_data.set_index('Time'))
    
    with report_col2:
        st.subheader("⚡ Energy Usage")
        
        # Energy consumption (simulated)
        energy_data = pd.DataFrame({
            'Device': ['Smart Lights', 'Audio System', 'Roku', 'Voice System'],
            'Power (W)': [45, 120, 15, 25],
            'Daily Usage (hrs)': [8, 6, 4, 2]
        })
        
        st.dataframe(energy_data, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("🎯 Performance Metrics")
        
        # Performance indicators
        perf_metrics = {
            "System Uptime": "99.8%",
            "Average Response Time": "0.3s",
            "API Success Rate": "98.5%",
            "User Satisfaction": "4.8/5"
        }
        
        for metric, value in perf_metrics.items():
            st.write(f"**{metric}:** {value}")
    
    # Export and settings
    st.markdown("---")
    st.subheader("📤 Export & Settings")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("📊 Export Analytics Report"):
            st.success("📊 Analytics report exported successfully!")
            st.info("Report saved as 'tiki_bar_analytics_2024.csv'")
        
        if st.button("🔄 Refresh Data"):
            st.success("🔄 Data refreshed!")
            st.rerun()
    
    with export_col2:
        st.subheader("⚙️ Analytics Settings")
        
        auto_refresh = st.checkbox("Auto-refresh every 5 minutes", value=True)
        track_usage = st.checkbox("Track user interactions", value=True)
        export_automatically = st.checkbox("Export reports daily", value=False)
        
        if st.button("💾 Save Settings"):
            st.success("💾 Settings saved!")

def show_tiki_bar_games():
    st.header("🎮 Tiki Bar Games")
    st.markdown("*🦜 Salty's collection of tropical entertainment*")
    
    # Initialize session state for games
    if "game_scores" not in st.session_state:
        st.session_state.game_scores = {
            "trivia": 0,
            "drink_quiz": 0,
            "tiki_bingo": 0
        }
    
    if "current_game" not in st.session_state:
        st.session_state.current_game = None
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎲 Available Games")
        
        # Game selection
        games = {
            "trivia": "🏴‍☠️ Pirate Trivia",
            "drink_quiz": "🍹 Tiki Drink Quiz", 
            "tiki_bingo": "🎯 Tiki Bar Bingo",
            "story_mode": "📖 Salty's Story Mode"
        }
        
        selected_game = st.selectbox("Choose a game", list(games.keys()), format_func=lambda x: games[x])
        
        if st.button("🎮 Start Game", type="primary"):
            st.session_state.current_game = selected_game
            st.success(f"🎮 Starting {games[selected_game]}!")
            st.rerun()
        
        st.markdown("---")
        
        st.subheader("🏆 Leaderboard")
        
        # Display scores
        for game, score in st.session_state.game_scores.items():
            game_name = games.get(game, game.title())
            st.write(f"**{game_name}:** {score} points")
        
        if st.button("🔄 Reset Scores"):
            st.session_state.game_scores = {game: 0 for game in st.session_state.game_scores}
            st.success("🔄 Scores reset!")
            st.rerun()
    
    with col2:
        st.subheader("🎯 Current Game")
        
        if st.session_state.current_game == "trivia":
            show_pirate_trivia()
        elif st.session_state.current_game == "drink_quiz":
            show_drink_quiz()
        elif st.session_state.current_game == "tiki_bingo":
            show_tiki_bingo()
        elif st.session_state.current_game == "story_mode":
            show_story_mode()
        else:
            st.info("🎮 Select a game to start playing!")
    
    # Game instructions
    st.markdown("---")
    st.subheader("📖 Game Instructions")
    
    instructions_col1, instructions_col2 = st.columns(2)
    
    with instructions_col1:
        st.write("""
        **🏴‍☠️ Pirate Trivia:**
        - Answer questions about pirates, tiki culture, and sea lore
        - Earn points for correct answers
        - Learn fascinating facts from Salty's 150+ years of experience
        
        **🍹 Tiki Drink Quiz:**
        - Test your knowledge of tropical cocktails
        - Learn about drink ingredients and history
        - Perfect for aspiring tiki bartenders
        """)
    
    with instructions_col2:
        st.write("""
        **🎯 Tiki Bar Bingo:**
        - Mark off tiki bar items as you spot them
        - First to complete a row wins
        - Great for parties and gatherings
        
        **📖 Story Mode:**
        - Listen to Salty's tales from the high seas
        - Interactive storytelling with choices
        - Unlock new stories as you progress
        """)

def show_pirate_trivia():
    st.subheader("🏴‍☠️ Pirate Trivia")
    
    # Trivia questions
    trivia_questions = [
        {
            "question": "What was the most feared pirate flag called?",
            "options": ["Jolly Roger", "Black Flag", "Skull & Crossbones", "Death's Head"],
            "correct": 0,
            "explanation": "The Jolly Roger was the traditional pirate flag featuring a skull and crossbones on a black background."
        },
        {
            "question": "What year was I cursed by the Gold Monkey idol?",
            "options": ["1847", "1850", "1845", "1852"],
            "correct": 0,
            "explanation": "I was cursed in 1847 when I foolishly tried to steal the Gold Monkey treasure!"
        },
        {
            "question": "What's the main ingredient in a Mai Tai?",
            "options": ["Rum", "Vodka", "Gin", "Tequila"],
            "correct": 0,
            "explanation": "Rum is the base spirit in a Mai Tai, typically a blend of aged rums."
        },
        {
            "question": "What does 'tiki' mean in Polynesian culture?",
            "options": ["God", "Spirit", "Carved figure", "Sacred place"],
            "correct": 2,
            "explanation": "Tiki refers to carved figures representing ancestors or deities in Polynesian culture."
        }
    ]
    
    if "trivia_question" not in st.session_state:
        st.session_state.trivia_question = 0
        st.session_state.trivia_score = 0
    
    if st.session_state.trivia_question < len(trivia_questions):
        current_q = trivia_questions[st.session_state.trivia_question]
        
        st.write(f"**Question {st.session_state.trivia_question + 1}:** {current_q['question']}")
        
        selected_answer = st.radio("Choose your answer:", current_q['options'])
        
        if st.button("⏭️ Submit Answer"):
            if selected_answer == current_q['options'][current_q['correct']]:
                st.success("✅ Correct! Well done, matey!")
                st.session_state.trivia_score += 10
                st.session_state.game_scores["trivia"] = st.session_state.trivia_score
            else:
                st.error(f"❌ Wrong! The correct answer was: {current_q['options'][current_q['correct']]}")
            
            st.info(f"💡 {current_q['explanation']}")
            
            st.session_state.trivia_question += 1
            
            if st.session_state.trivia_question < len(trivia_questions):
                if st.button("⏭️ Next Question"):
                    st.rerun()
            else:
                st.balloons()
                st.success(f"🎉 Trivia complete! Final score: {st.session_state.trivia_score} points!")
                
                if st.button("🔄 Play Again"):
                    st.session_state.trivia_question = 0
                    st.session_state.trivia_score = 0
                    st.rerun()
    else:
        st.success(f"🎉 Trivia complete! Final score: {st.session_state.trivia_score} points!")
        
        if st.button("🔄 Play Again"):
            st.session_state.trivia_question = 0
            st.session_state.trivia_score = 0
            st.rerun()

def show_drink_quiz():
    st.subheader("🍹 Tiki Drink Quiz")
    
    # Drink quiz questions
    drink_questions = [
        {
            "question": "What type of rum is traditionally used in a Zombie cocktail?",
            "options": ["White rum only", "Aged rum only", "Multiple types of rum", "Spiced rum only"],
            "correct": 2,
            "explanation": "The Zombie typically uses multiple types of rum including light, dark, and overproof rums."
        },
        {
            "question": "What fruit is essential for a Pina Colada?",
            "options": ["Pineapple", "Coconut", "Both pineapple and coconut", "Mango"],
            "correct": 2,
            "explanation": "Both pineapple and coconut are essential - that's what makes it a Pina Colada!"
        },
        {
            "question": "What's the main spirit in a Blue Hawaii?",
            "options": ["Vodka", "Rum", "Gin", "Tequila"],
            "correct": 0,
            "explanation": "The Blue Hawaii uses vodka as its base spirit, giving it a clean, crisp taste."
        },
        {
            "question": "What garnish is traditional for a Mai Tai?",
            "options": ["Lime wheel", "Mint sprig", "Orchid flower", "All of the above"],
            "correct": 3,
            "explanation": "A traditional Mai Tai is garnished with a lime wheel, mint sprig, and an orchid flower."
        }
    ]
    
    if "drink_question" not in st.session_state:
        st.session_state.drink_question = 0
        st.session_state.drink_score = 0
    
    if st.session_state.drink_question < len(drink_questions):
        current_q = drink_questions[st.session_state.drink_question]
        
        st.write(f"**Question {st.session_state.drink_question + 1}:** {current_q['question']}")
        
        selected_answer = st.radio("Choose your answer:", current_q['options'])
        
        if st.button("⏭️ Submit Answer"):
            if selected_answer == current_q['options'][current_q['correct']]:
                st.success("✅ Correct! You know your tiki drinks!")
                st.session_state.drink_score += 10
                st.session_state.game_scores["drink_quiz"] = st.session_state.drink_score
            else:
                st.error(f"❌ Wrong! The correct answer was: {current_q['options'][current_q['correct']]}")
            
            st.info(f"💡 {current_q['explanation']}")
            
            st.session_state.drink_question += 1
            
            if st.session_state.drink_question < len(drink_questions):
                if st.button("⏭️ Next Question"):
                    st.rerun()
            else:
                st.balloons()
                st.success(f"🎉 Drink quiz complete! Final score: {st.session_state.drink_score} points!")
                
                if st.button("🔄 Play Again"):
                    st.session_state.drink_question = 0
                    st.session_state.drink_score = 0
                    st.rerun()
    else:
        st.success(f"🎉 Drink quiz complete! Final score: {st.session_state.drink_score} points!")
        
        if st.button("🔄 Play Again"):
            st.session_state.drink_question = 0
            st.session_state.drink_score = 0
            st.rerun()

def show_tiki_bingo():
    st.subheader("🎯 Tiki Bar Bingo")
    
    # Tiki bar bingo board
    bingo_items = [
        "Tiki Mask", "Bamboo", "Coconut", "Palm Tree", "Tiki Torch",
        "Mai Tai", "Pina Colada", "Zombie", "Blue Hawaii", "Rum",
        "Parrot", "Ship Wheel", "Anchor", "Treasure Chest", "Gold Coin",
        "Tropical Flower", "Lei", "Hula Skirt", "Ukulele", "Tiki Statue",
        "Ocean View", "Sunset", "Palm Fronds", "Tiki Bar", "Tropical Music"
    ]
    
    if "bingo_board" not in st.session_state:
        st.session_state.bingo_board = {item: False for item in bingo_items}
    
    # Create 5x5 bingo board
    board_items = np.random.choice(bingo_items, 25, replace=False).reshape(5, 5)
    
    st.write("**Mark off items you see in your tiki bar environment:**")
    
    # Display bingo board
    for i in range(5):
        cols = st.columns(5)
        for j in range(5):
            item = board_items[i][j]
            is_marked = st.session_state.bingo_board.get(item, False)
            
            with cols[j]:
                if st.checkbox(item, value=is_marked, key=f"bingo_{i}_{j}"):
                    st.session_state.bingo_board[item] = True
                else:
                    st.session_state.bingo_board[item] = False
    
    # Check for bingo
    marked_count = sum(st.session_state.bingo_board.values())
    st.write(f"**Items found: {marked_count}/25**")
    
    if marked_count >= 5:
        st.success("🎉 You're making progress! Keep looking for more tiki items!")
    
    if st.button("🔄 New Board"):
        st.session_state.bingo_board = {item: False for item in bingo_items}
        st.rerun()

def show_story_mode():
    st.subheader("📖 Salty's Story Mode")
    
    st.write("""
    **Welcome to Story Mode, matey!**
    
    I've got centuries of tales to tell from my time as Captain "Blackheart" McGillicuddy. 
    Choose your adventure and I'll spin you a yarn that'll make your hair stand on end!
    """)
    
    story_options = [
        "🏴‍☠️ The Curse of the Gold Monkey",
        "🌊 The Battle of the Seven Seas", 
        "🏝️ The Lost Island of Tiki",
        "💎 The Treasure of Captain Kidd"
    ]
    
    selected_story = st.selectbox("Choose your story:", story_options)
    
    if st.button("📖 Begin Story"):
        st.success("📖 Let the tale begin...")
        
        if "The Curse of the Gold Monkey" in selected_story:
            st.write("""
            **The Curse of the Gold Monkey**
            
            It was the year 1847, and I was the most feared pirate in the Caribbean. 
            Captain "Blackheart" McGillicuddy, they called me. I had a crew of 50 men 
            and a ship that could outrun any navy vessel.
            
            But my downfall came when I heard tales of the Gold Monkey idol - a 
            mystical artifact said to grant immortality to whoever possessed it. 
            Foolish as I was, I set sail for the island where it was said to be hidden...
            
            *To be continued...*
            """)
        
        elif "The Battle of the Seven Seas" in selected_story:
            st.write("""
            **The Battle of the Seven Seas**
            
            The year was 1846, and the seven pirate lords had gathered for the 
            greatest naval battle ever seen. Each captain commanded a fleet of 
            ships, and the prize was control of all the Caribbean trade routes...
            
            *To be continued...*
            """)
        
        elif "The Lost Island of Tiki" in selected_story:
            st.write("""
            **The Lost Island of Tiki**
            
            Deep in the South Pacific, there existed an island where the ancient 
            tiki gods still walked among men. The island was said to be protected 
            by powerful magic, and only those pure of heart could find it...
            
            *To be continued...*
            """)
        
        elif "The Treasure of Captain Kidd" in selected_story:
            st.write("""
            **The Treasure of Captain Kidd**
            
            Captain William Kidd was said to have buried the greatest treasure 
            ever amassed by a pirate. His map was divided into seven pieces, 
            each hidden in a different location around the world...
            
            *To be continued...*
            """)
        
        st.info("🦜 Squawk! These are just the beginnings of my tales. Each story has multiple paths and endings based on your choices!") 