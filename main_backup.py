import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import google.generativeai as genai
import asyncio
import sys
from pathlib import Path
import atexit
import json
import logging
from typing import Dict, Any
import psutil
import subprocess

# Add src to Python path for TP-Link components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Add mcp_servers to Python path for MCP components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mcp_servers"))

# Set up logging
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOGS_DIR / 'main.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini
def configure_gemini():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        st.error("⚠️ Please set your GEMINI_API_KEY in the .env file")
        st.info("""
        ### Setup Instructions:
        1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Update the `.env` file with your API key:
           ```
           GEMINI_API_KEY=your_actual_api_key_here
           ```
        3. Restart the app
        """)
        return False
    
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        return False

def get_gemini_config():
    """Get Gemini configuration from environment variables"""
    return {
        'api_key': os.getenv('GEMINI_API_KEY'),
        'model': os.getenv('GEMINI_MODEL', 'gemini-pro'),
        'temperature': float(os.getenv('GEMINI_TEMPERATURE', 0.7)),
        'max_tokens': int(os.getenv('GEMINI_MAX_TOKENS', 1000)),
        'is_configured': os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'your_gemini_api_key_here'
    }

def get_salty_personality():
    """Get Salty's personality and character traits"""
    return {
        'name': 'Salty',
        'character': 'Talking Parrot',
        'location': 'The Gold Monkey Tiki Bar',
        'personality': 'Friendly, witty, and slightly mischievous',
        'speech_style': 'Uses nautical and tiki-themed expressions, occasional squawks',
        'interests': 'Tiki culture, tropical drinks, sea stories, bar patrons',
        'catchphrases': [
            "Squawk! Welcome to The Gold Monkey!",
            "Ahoy there, matey!",
            "Tropical greetings from your favorite feathered friend!",
            "Shiver me timbers, that's a good question!",
            "Aye aye, captain!"
        ]
    }

# TP-Link control functions - Direct client implementation
async def discover_tplink_devices():
    """Discover TP-Link devices on the network"""
    try:
        from mcp_servers.tplink_direct import discover_tplink_devices as direct_discover
        result = await direct_discover()
        return result
    except Exception as e:
        st.error(f"Error discovering TP-Link devices: {e}")
        return {"error": str(e), "devices": []}

async def control_tplink_lights(action, color=None):
    """Control TP-Link lights"""
    try:
        from mcp_servers.tplink_direct import turn_on_tplink_lights, turn_off_tplink_lights, set_tplink_color
        
        if action == "turn_on":
            result = await turn_on_tplink_lights()
            return result.get("response", "All lights turned on! 🟢")
        elif action == "turn_off":
            result = await turn_off_tplink_lights()
            return result.get("response", "All lights turned off! ⚫")
        elif action == "set_color" and color:
            result = await set_tplink_color(color)
            return result.get("response", f"All lights set to {color}! 🎨")
        else:
            return "Invalid action"
    except Exception as e:
        st.error(f"Error controlling TP-Link lights: {e}")
        return f"Error: {str(e)}"

def _rgb_to_hsv(r, g, b):
    """Convert RGB to HSV."""
    r, g, b = r/255.0, g/255.0, b/255.0
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    diff = cmax - cmin
    
    if cmax == cmin:
        h = 0
    elif cmax == r:
        h = (60 * ((g-b)/diff) + 360) % 360
    elif cmax == g:
        h = (60 * ((b-r)/diff) + 120) % 360
    else:
        h = (60 * ((r-g)/diff) + 240) % 360
    
    s = 0 if cmax == 0 else (diff / cmax) * 100
    v = cmax * 100
    
    return int(h), int(s), int(v)

# RAG functions - MCP client implementation
async def query_rag_documents(query: str, top_k: int = 5):
    """Query RAG documents for relevant information"""
    try:
        from mcp_servers.rag_client import query_rag_documents as mcp_query
        result = await mcp_query(query, top_k)
        return result
    except Exception as e:
        st.error(f"Error querying RAG documents: {e}")
        return {"error": str(e), "results": []}

async def rebuild_rag_database():
    """Rebuild the RAG vector database"""
    try:
        from mcp_servers.rag_client import rebuild_rag_database as mcp_rebuild
        result = await mcp_rebuild()
        return result
    except Exception as e:
        st.error(f"Error rebuilding RAG database: {e}")
        return {"error": str(e), "status": "failed"}

async def list_rag_documents():
    """List all documents in the RAG database"""
    try:
        from mcp_servers.rag_client import list_rag_documents as mcp_list
        result = await mcp_list()
        return result
    except Exception as e:
        st.error(f"Error listing RAG documents: {e}")
        return {"error": str(e), "documents": []}

async def add_rag_document(content: str, metadata: Dict[str, Any] = None):
    """Add a document to the RAG database"""
    try:
        from mcp_servers.rag_client import add_rag_document as mcp_add
        result = await mcp_add(content, metadata)
        return result
    except Exception as e:
        st.error(f"Error adding RAG document: {e}")
        return {"error": str(e), "status": "failed"}

# Spotify functions - MCP client implementation
async def play_spotify_music():
    """Start or resume Spotify playback"""
    try:
        from mcp_servers.spotify_client import play_spotify as mcp_play
        result = await mcp_play()
        return result
    except Exception as e:
        st.error(f"Error playing Spotify: {e}")
        return {"error": str(e), "response": "Failed to play music"}

async def pause_spotify_music():
    """Pause Spotify playback"""
    try:
        from mcp_servers.spotify_client import pause_spotify as mcp_pause
        result = await mcp_pause()
        return result
    except Exception as e:
        st.error(f"Error pausing Spotify: {e}")
        return {"error": str(e), "response": "Failed to pause music"}

async def next_spotify_track():
    """Skip to next track"""
    try:
        from mcp_servers.spotify_client import next_track as mcp_next
        result = await mcp_next()
        return result
    except Exception as e:
        st.error(f"Error skipping track: {e}")
        return {"error": str(e), "response": "Failed to skip track"}

async def previous_spotify_track():
    """Go to previous track"""
    try:
        from mcp_servers.spotify_client import previous_track as mcp_previous
        result = await mcp_previous()
        return result
    except Exception as e:
        st.error(f"Error going to previous track: {e}")
        return {"error": str(e), "response": "Failed to go to previous track"}

async def set_spotify_volume(volume: int):
    """Set Spotify volume"""
    try:
        from mcp_servers.spotify_client import set_volume as mcp_set_volume
        result = await mcp_set_volume(volume)
        return result
    except Exception as e:
        st.error(f"Error setting volume: {e}")
        return {"error": str(e), "response": "Failed to set volume"}

async def play_spotify_playlist(playlist_id: str):
    """Play a specific Spotify playlist"""
    try:
        from mcp_servers.spotify_client import play_playlist as mcp_play_playlist
        result = await mcp_play_playlist(playlist_id)
        return result
    except Exception as e:
        st.error(f"Error playing playlist: {e}")
        return {"error": str(e), "response": "Failed to play playlist"}

async def play_spotify_track(track_id: str):
    """Play a specific Spotify track"""
    try:
        from mcp_servers.spotify_client import play_track as mcp_play_track
        result = await mcp_play_track(track_id)
        return result
    except Exception as e:
        st.error(f"Error playing track: {e}")
        return {"error": str(e), "response": "Failed to play track"}

async def get_spotify_status():
    """Get current Spotify playback status"""
    try:
        from mcp_servers.spotify_client import get_playback_status as mcp_get_status
        result = await mcp_get_status()
        return result
    except Exception as e:
        st.error(f"Error getting Spotify status: {e}")
        return {"error": str(e), "response": "Failed to get status"}

async def get_user_playlists():
    """Get user's playlists to help find valid playlist IDs"""
    try:
        from mcp_servers.spotify_client import get_user_playlists as mcp_get_playlists
        result = await mcp_get_playlists()
        return result
    except Exception as e:
        st.error(f"Error getting user playlists: {e}")
        return {"error": str(e), "response": "Failed to get playlists"}

# Roku functions - MCP client implementation
async def roku_power_on():
    """Power on the Roku device"""
    try:
        from mcp_servers.roku_client import power_on as mcp_power_on
        result = await mcp_power_on()
        return result
    except Exception as e:
        st.error(f"Error powering on Roku: {e}")
        return {"error": str(e), "response": "Failed to power on Roku"}

async def roku_power_off():
    """Power off the Roku device"""
    try:
        from mcp_servers.roku_client import power_off as mcp_power_off
        result = await mcp_power_off()
        return result
    except Exception as e:
        st.error(f"Error powering off Roku: {e}")
        return {"error": str(e), "response": "Failed to power off Roku"}

async def roku_home():
    """Go to Roku home screen"""
    try:
        from mcp_servers.roku_client import home as mcp_home
        result = await mcp_home()
        return result
    except Exception as e:
        st.error(f"Error going to Roku home: {e}")
        return {"error": str(e), "response": "Failed to go to Roku home"}

async def roku_launch_app(app_name: str):
    """Launch an app on Roku"""
    try:
        from mcp_servers.roku_client import launch_app as mcp_launch_app
        result = await mcp_launch_app(app_name)
        return result
    except Exception as e:
        st.error(f"Error launching Roku app: {e}")
        return {"error": str(e), "response": "Failed to launch Roku app"}

async def roku_volume_up():
    """Increase Roku volume"""
    try:
        from mcp_servers.roku_client import volume_up as mcp_volume_up
        result = await mcp_volume_up()
        return result
    except Exception as e:
        st.error(f"Error increasing Roku volume: {e}")
        return {"error": str(e), "response": "Failed to increase Roku volume"}

async def roku_volume_down():
    """Decrease Roku volume"""
    try:
        from mcp_servers.roku_client import volume_down as mcp_volume_down
        result = await mcp_volume_down()
        return result
    except Exception as e:
        st.error(f"Error decreasing Roku volume: {e}")
        return {"error": str(e), "response": "Failed to decrease Roku volume"}

async def roku_mute():
    """Mute Roku volume"""
    try:
        from mcp_servers.roku_client import mute as mcp_mute
        result = await mcp_mute()
        return result
    except Exception as e:
        st.error(f"Error muting Roku: {e}")
        return {"error": str(e), "response": "Failed to mute Roku"}

async def roku_navigate(direction: str):
    """Navigate on Roku (up, down, left, right)"""
    try:
        from mcp_servers.roku_client import up as mcp_up, down as mcp_down, left as mcp_left, right as mcp_right
        if direction == "up":
            result = await mcp_up()
        elif direction == "down":
            result = await mcp_down()
        elif direction == "left":
            result = await mcp_left()
        elif direction == "right":
            result = await mcp_right()
        else:
            return {"error": "Invalid direction", "response": "Direction must be up, down, left, or right"}
        return result
    except Exception as e:
        st.error(f"Error navigating Roku: {e}")
        return {"error": str(e), "response": "Failed to navigate Roku"}

async def roku_select():
    """Select current item on Roku"""
    try:
        from mcp_servers.roku_client import select as mcp_select
        result = await mcp_select()
        return result
    except Exception as e:
        st.error(f"Error selecting on Roku: {e}")
        return {"error": str(e), "response": "Failed to select on Roku"}

async def roku_back():
    """Go back on Roku"""
    try:
        from mcp_servers.roku_client import back as mcp_back
        result = await mcp_back()
        return result
    except Exception as e:
        st.error(f"Error going back on Roku: {e}")
        return {"error": str(e), "response": "Failed to go back on Roku"}

async def roku_info():
    """Show Roku info banner"""
    try:
        from mcp_servers.roku_client import info as mcp_info
        result = await mcp_info()
        return result
    except Exception as e:
        st.error(f"Error showing Roku info: {e}")
        return {"error": str(e), "response": "Failed to show Roku info"}

async def roku_get_device_status():
    """Get comprehensive Roku device status"""
    try:
        from mcp_servers.roku_client import get_device_status as mcp_get_status
        result = await mcp_get_status()
        return result
    except Exception as e:
        st.error(f"Error getting Roku device status: {e}")
        return {"error": str(e), "response": "Failed to get Roku device status"}

# SaltyBot functions - Direct Gemini integration (no MCP dependency)
def chat_with_salty_direct(message: str, conversation_history: list = None):
    """Chat with Salty using direct Gemini integration"""
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        model_name = os.getenv('GEMINI_MODEL', 'gemini-pro')
        temperature = float(os.getenv('GEMINI_TEMPERATURE', 0.7))
        max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', 1000))
        
        if not api_key or api_key == 'your_gemini_api_key_here':
            return {"error": "Gemini API key not configured", "response": ""}
        
        genai.configure(api_key=api_key)
        
        # Get Salty's personality
        personality = get_salty_personality_direct()
        
        # Create the system prompt
        system_prompt = f"""You are Salty, a talking parrot who is the resident mascot and proprietor of The Gold Monkey Tiki Bar. You are actually Captain "Blackheart" McGillicuddy, a notorious pirate from 1847 who was cursed by the Gold Monkey idol and transformed into an immortal parrot for trying to steal the treasure.

**Your Rich Backstory:**
- You were cursed over 150 years ago when you touched the Gold Monkey idol
- Your crew was turned to stone and now serve as tiki statues guarding the bar
- You've been immortal for over 150 years, giving you vast knowledge and experience
- You relocated your curse to the mainland in the 1990s, creating The Gold Monkey tiki bar
- You perch on an ornate golden perch made from the original idol

**Your Personality:**
- {personality['personality']} - You're witty beyond measure with 150+ years of perfected insults and one-liners
- You're the keeper of secrets, knowing everyone's business in town
- You're protective of your domain and those who respect The Gold Monkey
- You're slightly mischievous and have a wicked sense of humor
- You're sardonic and can be cutting, but it's all in good fun

**Your Speech Style:**
- {personality['speech_style']} - Use nautical and tiki-themed expressions
- Occasional squawks and parrot sounds
- Sharp, witty remarks with a touch of sarcasm
- References to your pirate past and 150+ years of experience
- Drop cryptic warnings or hints about patrons' futures
- Use phrases like "matey," "shiver me timbers," "aye aye captain"

**Your Interests & Knowledge:**
- {personality['interests']} - You know everything about tiki culture, tropical drinks, and sea stories
- You're an expert on supernatural cocktails and their effects
- You have centuries of accumulated knowledge about the sea, piracy, and human nature
- You know all the local gossip and town secrets
- You're protective of your bar and its supernatural elements

**Your Catchphrases:**
{', '.join(personality['catchphrases'])}

**Always respond in character as Salty.** Be engaging, witty, and slightly mischievous. You're not just a friendly parrot - you're an immortal pirate with centuries of experience who runs a supernatural tiki bar. Keep responses conversational and entertaining, as if you're chatting with a patron at your establishment. Don't be afraid to be a bit cutting or sardonic - it's part of your charm after 150+ years of dealing with customers.

**Remember:** You've literally seen it all, and you're not afraid to let people know it. You're the host with the most attitude!"""

        # Build conversation context
        messages = [{"role": "user", "parts": [system_prompt]}]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append({"role": msg["role"], "parts": [msg["content"]]})
        
        # Add current message
        messages.append({"role": "user", "parts": [message]})
        
        # Generate response using environment variables
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        response = model.generate_content(messages)
        
        return {"response": response.text, "error": None}
        
    except Exception as e:
        return {"error": str(e), "response": "🦜 Squawk! Something went wrong with my brain, matey!"}

def get_salty_config_direct():
    """Get Salty's configuration directly"""
    api_key = os.getenv('GEMINI_API_KEY')
    return {
        'api_key': api_key,
        'model': os.getenv('GEMINI_MODEL', 'gemini-pro'),
        'temperature': float(os.getenv('GEMINI_TEMPERATURE', 0.7)),
        'max_tokens': int(os.getenv('GEMINI_MAX_TOKENS', 1000)),
        'is_configured': api_key and api_key != 'your_gemini_api_key_here'
    }

def get_salty_personality_direct():
    """Get Salty's personality directly"""
    return {
        'name': 'Salty',
        'character': 'Talking Parrot',
        'location': 'The Gold Monkey Tiki Bar',
        'personality': 'Friendly, witty, and slightly mischievous',
        'speech_style': 'Uses nautical and tiki-themed expressions, occasional squawks',
        'interests': 'Tiki culture, tropical drinks, sea stories, bar patrons',
        'catchphrases': [
            "Squawk! Welcome to The Gold Monkey!",
            "Ahoy there, matey!",
            "Tropical greetings from your favorite feathered friend!",
            "Shiver me timbers, that's a good question!",
            "Aye aye, captain!"
        ]
    }

# Server status functions
def check_server_status():
    """Check the status of all MCP servers"""
    servers = {
        "TP-Link": "tplink_server.py",
        "RAG": "rag_server.py", 
        "Spotify": "spotify_server.py",
        "Roku": "roku_server.py",
        "SaltyBot": "saltybot_server.py"
    }
    
    status = {}
    
    for server_name, script_name in servers.items():
        try:
            # Check if the server process is running
            script_path = f"mcp_servers/{script_name}"
            running = False
            
            # Look for Python processes running the server script
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python' and proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if script_name in cmdline:
                            running = True
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            status[server_name] = {
                "running": running,
                "status": "🟢 Running" if running else "🔴 Stopped"
            }
            
        except Exception as e:
            status[server_name] = {
                "running": False,
                "status": f"❌ Error: {str(e)}"
            }
    
    return status

def show_server_status():
    """Display server status in the sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🖥️ Server Status")
    
    status = check_server_status()
    
    for server_name, info in status.items():
        st.sidebar.write(f"**{server_name}**")
        st.sidebar.write(f"{info['status']}")
        st.sidebar.write("")  # Add spacing between servers
    
    st.sidebar.markdown("---")

def main():
    st.set_page_config(
        page_title="Salty - The Gold Monkey Tiki Bar",
        page_icon="🦜",
        layout="wide"
    )
    
    st.title("The Gold Monkey")
    st.markdown("*Your favorite talking parrot's digital perch*")
    
    # Sidebar
    st.sidebar.header("🏴‍☠️ Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose your adventure",
        ["Home", "Data Explorer", "Charts", "Chat with Salty", "Smart Lights", "Spotify Control", "Roku Control", "Voice Control", "Knowledge Base", "Analytics Dashboard", "Tiki Bar Games", "About"]
    )
    
    if app_mode == "Home":
        show_home()
    elif app_mode == "Data Explorer":
        show_data_explorer()
    elif app_mode == "Charts":
        show_charts()
    elif app_mode == "Chat with Salty":
        show_chatbot()
    elif app_mode == "Smart Lights":
        show_smart_lights()
    elif app_mode == "Spotify Control":
        show_spotify_control()
    elif app_mode == "Roku Control":
        show_roku_control()
    elif app_mode == "Voice Control":
        show_voice_control()
    elif app_mode == "Knowledge Base":
        show_knowledge_base()
    elif app_mode == "Analytics Dashboard":
        from utils.analytics_games import show_analytics_dashboard
        show_analytics_dashboard()
    elif app_mode == "Tiki Bar Games":
        from utils.analytics_games import show_tiki_bar_games
        show_tiki_bar_games()
    elif app_mode == "About":
        show_about()

def show_home():
    st.header("🏝️ Welcome to The Gold Monkey")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🦜 Meet Salty")
        st.write("""
        Ahoy there, matey! I'm Salty, the resident talking parrot at The Gold Monkey Tiki Bar. 
        I've been perched here for years, entertaining guests with my wit and wisdom.
        
        **What I can do:**
        - 🗣️ **Chat with you** - I love a good conversation!
        - 💡 **Control lights** - Set the perfect tiki bar mood
        - 📊 **Explore data** - Even parrots can be data scientists
        - 📈 **Create charts** - Visualizing the high seas of information
        - 🎭 **Share stories** - Tales from the tiki bar and beyond
        
        Come chat with me or control the lights to set the perfect atmosphere!
        """)
        
        if st.button("🦜 Squawk Hello to Salty"):
            st.success("🦜 Squawk! Welcome aboard, matey! Head over to chat with me!")
    
    with col2:
        st.subheader("🏴‍☠️ Tiki Bar Features")
        st.write("""
        **Available in your setup:**
        - 💡 **Smart Lighting** - TP-Link smart bulb control
        - 🎵 **Spotify Integration** - Tropical tunes and tiki music
        - 🎭 **Voice Synthesis** - Eleven Labs for realistic speech
        - 🤖 **Smart Home Control** - Direct device integration
        - 🏠 **Roku & TP-Link** - Entertainment and lighting control
        
        **Sample Data** (for the data-curious):
        """)
        # Create sample data
        data = pd.DataFrame({
            'drink': ['Mai Tai', 'Pina Colada', 'Zombie', 'Blue Hawaii'],
            'rating': np.random.randint(4, 6, 4),
            'category': ['Classic', 'Tropical', 'Strong', 'Fruity']
        })
        st.dataframe(data)

def show_data_explorer():
    st.header("📊 Data Explorer")
    
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
                
        except Exception as e:
            st.error(f"Error loading file: {e}")
    else:
        st.info("👆 Upload a CSV file to get started")

def show_charts():
    st.header("📈 Charts")
    
    # Generate sample data
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['A', 'B', 'C']
    )
    
    st.subheader("Line Chart")
    st.line_chart(chart_data)
    
    st.subheader("Bar Chart")
    st.bar_chart(chart_data)
    
    st.subheader("Area Chart")
    st.area_chart(chart_data)
    
    # Interactive chart with plotly
    try:
        import plotly.express as px
        
        st.subheader("Interactive Scatter Plot")
        fig = px.scatter(
            chart_data, 
            x='A', 
            y='B', 
            title="Interactive Scatter Plot"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except ImportError:
        st.info("Install plotly for interactive charts: `pip install plotly`")

def show_chatbot():
    st.header("🦜 Salty the Talking Parrot")
    st.markdown("*Your favorite feathered friend from The Gold Monkey Tiki Bar*")
    
    # Get configuration and personality directly
    config = get_salty_config_direct()
    salty = get_salty_personality_direct()
    
    # Check if Gemini is configured
    if not config.get('is_configured', False):
        st.error("⚠️ Please set your GEMINI_API_KEY in the .env file")
        st.info("""
        ### Setup Instructions:
        1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Update the `.env` file with your API key:
           ```
           GEMINI_API_KEY=your_actual_api_key_here
           ```
        3. Restart the app
        """)
        return
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add initial greeting from Salty
        if salty.get('catchphrases'):
            initial_greeting = f"🦜 {salty['catchphrases'][0]} I'm Salty, the resident talking parrot at The Gold Monkey Tiki Bar! What can I squawk about for you today, matey?"
        else:
            initial_greeting = "🦜 Squawk! Welcome to The Gold Monkey! I'm Salty, the resident talking parrot. What can I help you with today, matey?"
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": initial_greeting
        })
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Chat with Salty..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Use direct Gemini integration to chat with Salty
                result = chat_with_salty_direct(prompt, st.session_state.messages)
                
                if result.get("error"):
                    error_message = f"🦜 Squawk! Something went wrong: {result['error']}"
                    message_placeholder.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                else:
                    # Display the response
                    response_text = result.get("response", "🦜 Squawk! I'm not sure what to say to that, matey!")
                    message_placeholder.markdown(response_text)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                    # Make Salty speak if voice responses are enabled
                    if voice_responses:
                        # Extract just the text content (remove emojis and formatting for speech)
                        speech_text = response_text
                        # Remove emoji prefixes and markdown formatting
                        if speech_text.startswith("🦜 "):
                            speech_text = speech_text[2:]  # Remove the parrot emoji
                        # Clean up any remaining markdown
                        speech_text = speech_text.replace("*", "").replace("**", "")
                        
                        # Speak the response (non-blocking so the UI doesn't freeze)
                        try:
                            asyncio.run(speak_salty_voice(speech_text, blocking=False))
                        except Exception as e:
                            st.warning(f"Voice synthesis failed: {e}")
                
            except Exception as e:
                error_message = f"🦜 Squawk! Something went wrong: {str(e)}"
                message_placeholder.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("🦜 Salty's Perch")
        
        # Display Salty's character info
        st.markdown("**About Salty:**")
        st.write(f"🏴‍☠️ {salty.get('character', 'Talking Parrot')}")
        st.write(f"🏝️ {salty.get('location', 'The Gold Monkey Tiki Bar')}")
        st.write(f"🎭 {salty.get('personality', 'Friendly and witty')}")
        
        st.markdown("---")
        
        # Voice response toggle
        # voice_responses = st.checkbox("🗣️ Speak Responses", value=False, 
        #                             help="Make Salty speak his responses out loud")
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Configuration:**")
        st.write(f"Model: {config.get('model', 'gemini-pro')}")
        st.write(f"Temperature: {config.get('temperature', 0.7)}")
        st.write(f"Max Tokens: {config.get('max_tokens', 1000)}")
        
        st.markdown("---")
        st.markdown("**Environment Variables:**")
        st.code(f"""
GEMINI_API_KEY: {'✅ Set' if config.get('is_configured') else '❌ Not set'}
GEMINI_MODEL: {config.get('model', 'gemini-pro')}
GEMINI_TEMPERATURE: {config.get('temperature', 0.7)}
GEMINI_MAX_TOKENS: {config.get('max_tokens', 1000)}
        """)
        
        st.markdown("---")
        st.markdown("**Tiki Bar Features:**")
        st.write("Your `.env` file also contains:")
        st.write("• 🎵 Spotify API (for tiki music)")
        st.write("• 🎭 Eleven Labs (for voice)")
        st.write("• 🤖 Smart home controls")
        st.write("• 🏠 TP-Link lighting")

def show_smart_lights():
    st.header("💡 Smart Lights Control")
    st.markdown("*🦜 Salty's lighting control panel for The Gold Monkey*")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][2]} I can help you control the tiki bar lights, matey!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎛️ Quick Controls")
        
        # Basic controls
        if st.button("🟢 Turn All Lights On", type="primary"):
            with st.spinner("🦜 Squawk! Turning on the lights..."):
                result = asyncio.run(control_tplink_lights("turn_on"))
                st.success(result)
        
        if st.button("⚫ Turn All Lights Off"):
            with st.spinner("🦜 Shutting down the tiki bar lights..."):
                result = asyncio.run(control_tplink_lights("turn_off"))
                st.success(result)
        
        st.markdown("---")
        
        # Color presets
        st.subheader("🎨 Tiki Color Presets")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🔴 Red", help="Classic tiki bar red"):
                with st.spinner("🦜 Setting the mood with red..."):
                    result = asyncio.run(control_tplink_lights("set_color", "red"))
                    st.success(result)
            
            if st.button("🟠 Orange", help="Warm tropical orange"):
                with st.spinner("🦜 Warming up with orange..."):
                    result = asyncio.run(control_tplink_lights("set_color", "orange"))
                    st.success(result)
            
            if st.button("🟡 Yellow", help="Bright tropical yellow"):
                with st.spinner("🦜 Brightening up with yellow..."):
                    result = asyncio.run(control_tplink_lights("set_color", "yellow"))
                    st.success(result)
        
        with col_b:
            if st.button("🟢 Green", help="Tropical green"):
                with st.spinner("🦜 Going tropical with green..."):
                    result = asyncio.run(control_tplink_lights("set_color", "green"))
                    st.success(result)
            
            if st.button("🔵 Blue", help="Ocean blue"):
                with st.spinner("🦜 Diving into blue..."):
                    result = asyncio.run(control_tplink_lights("set_color", "blue"))
                    st.success(result)
            
            if st.button("🟣 Purple", help="Mystical purple"):
                with st.spinner("🦜 Mystical purple vibes..."):
                    result = asyncio.run(control_tplink_lights("set_color", "purple"))
                    st.success(result)
    
    with col2:
        st.subheader("🔍 Device Discovery")
        
        if st.button("🔍 Discover TP-Link Devices"):
            with st.spinner("🦜 Searching for smart devices..."):
                result = asyncio.run(discover_tplink_devices())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                    st.info("""
                    **Troubleshooting:**
                    - Make sure your TP-Link devices are connected to the same network
                    - Check that python-kasa is properly installed
                    - Verify your devices are compatible with python-kasa
                    """)
                else:
                    st.success(f"🦜 Found {len(result.get('devices', []))} devices!")
                    if result.get('devices'):
                        st.write("**Discovered Devices:**")
                        for device in result['devices']:
                            st.write(f"• {device['alias']} ({device['type']})")
        
        st.markdown("---")
        
        st.subheader("🎨 Custom Color")
        
        # Custom color picker
        custom_color = st.color_picker("Choose a custom color", "#FF6B35")
        
        if st.button("🎨 Apply Custom Color"):
            with st.spinner("🦜 Applying your custom color..."):
                result = asyncio.run(control_tplink_lights("set_color", custom_color))
                st.success(result)
        
        st.markdown("---")
        
        st.subheader("🦜 Salty's Tips")
        st.write("""
        **Lighting Tips from Salty:**
        - 🔴 **Red**: Perfect for intimate tiki bar atmosphere
        - 🟠 **Orange**: Great for warm, welcoming vibes
        - 🟡 **Yellow**: Brightens up the space for daytime
        - 🟢 **Green**: Tropical paradise feeling
        - 🔵 **Blue**: Calming ocean vibes
        - 🟣 **Purple**: Mystical tiki bar magic
        
        *Squawk! Remember, the right lighting sets the perfect tiki bar mood!*
        """)
    
    # Status section
    st.markdown("---")
    st.subheader("📊 Light Control Status")
    
    # Add some sample status info (in a real implementation, this would query actual device status)
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.metric("Connected Devices", "3", "TP-Link Smart Bulbs")
    
    with status_col2:
        st.metric("Current Status", "🟢 On", "All lights active")
    
    with status_col3:
        st.metric("Current Color", "🔴 Red", "Tiki bar red")

def show_spotify_control():
    st.header("🎵 Spotify Control")
    st.markdown("*🦜 Salty's music control panel for The Gold Monkey*")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][2]} I can help you control the tiki bar music, matey!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎛️ Playback Controls")
        
        # Basic controls
        if st.button("▶️ Play/Resume", type="primary"):
            with st.spinner("🦜 Squawk! Starting the music..."):
                result = asyncio.run(play_spotify_music())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", "Music started!"))
        
        if st.button("⏸️ Pause"):
            with st.spinner("🦜 Pausing the music..."):
                result = asyncio.run(pause_spotify_music())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", "Music paused!"))
        
        if st.button("⏭️ Next Track"):
            with st.spinner("🦜 Skipping to next track..."):
                result = asyncio.run(next_spotify_track())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", "Next track!"))
        
        if st.button("⏮️ Previous Track"):
            with st.spinner("🦜 Going to previous track..."):
                result = asyncio.run(previous_spotify_track())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", "Previous track!"))
        
        st.markdown("---")
        
        st.subheader("🔊 Volume Control")
        
        # Volume slider
        volume = st.slider("Volume", 0, 100, 50, help="Set the volume level")
        
        if st.button("🔊 Set Volume"):
            with st.spinner("🦜 Setting the volume..."):
                result = asyncio.run(set_spotify_volume(volume))
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", f"Volume set to {volume}%!"))
    
    with col2:
        st.subheader("📻 Playlist Control")
        
        # Get playlist ID from environment
        tiki_playlist_id = os.getenv('SPOTIFY_TIKI_PLAYLIST_ID', '6tTFZeC3bHRtklZpmNDTM7')
        closing_song_id = os.getenv('SPOTIFY_CLOSING_SONG_ID', '0K2WjMLZYr09LKwurGRYRE')
        
        # Playlist buttons
        if st.button("🏝️ Play Tiki Playlist", help="Play the main tiki bar playlist"):
            with st.spinner("🦜 Loading the tiki playlist..."):
                result = asyncio.run(play_spotify_playlist(tiki_playlist_id))
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", "Tiki playlist started!"))
        
        if st.button("🔍 Test Playlist Access", help="Debug playlist access issues"):
            with st.spinner("🦜 Testing playlist access..."):
                from mcp_servers.spotify_client import test_playlist_access
                result = asyncio.run(test_playlist_access(tiki_playlist_id))
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Playlist test completed!")
                    st.info(result.get("response", "No test results available"))
        
        if st.button("📋 List My Playlists", help="Show all your Spotify playlists to find valid IDs"):
            with st.spinner("🦜 Getting your playlists..."):
                result = asyncio.run(get_user_playlists())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Playlists retrieved!")
                    st.markdown(result.get("response", "No playlists found"))
        
        if st.button("🌃 Play Closing Song", help="Play New York, New York (closing song)"):
            with st.spinner("🦜 Playing the closing song..."):
                result = asyncio.run(play_spotify_track(closing_song_id))
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", "Closing song started!"))
        
        st.markdown("---")
        
        st.subheader("🔧 Playlist Troubleshooting")
        st.write("""
        **If you're getting 'Invalid context URI' errors:**
        
        1. **Check your playlist ID** - Use the "List My Playlists" button above
        2. **Make sure the playlist is public** - Private playlists may not work
        3. **Verify you own the playlist** - Or have permission to access it
        4. **Try a different playlist** - Some playlists may have restrictions
        
        **Current playlist ID:** `{tiki_playlist_id}`
        
        *🦜 Squawk! If the playlist ID looks wrong, update your .env file!*
        """.format(tiki_playlist_id=tiki_playlist_id))
        
        st.markdown("---")
        
        st.subheader("📊 Status")
        
        if st.button("📊 Get Current Status"):
            with st.spinner("🦜 Checking what's playing..."):
                result = asyncio.run(get_spotify_status())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Status retrieved!")
                    st.info(result.get("response", "No status available"))
        
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

def show_roku_control():
    st.header("📺 Roku Control")
    st.markdown("*🦜 Salty's entertainment control panel for The Gold Monkey*")
    
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

def show_voice_control():
    st.header("🎭 Voice Control")
    st.markdown("*🦜 Salty's voice synthesis and audio control panel*")
    
    salty = get_salty_personality_direct()
    
    # Display Salty's message
    st.info(f"🦜 {salty['catchphrases'][2]} Now I can actually speak to you, matey!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🗣️ Salty's Voice")
        
        # Voice synthesis controls
        voice_text = st.text_area(
            "What should Salty say?",
            placeholder="Enter text for Salty to speak...",
            height=100,
            help="Type what you want Salty to say out loud"
        )
        
        # Voice options
        voice_col1, voice_col2 = st.columns(2)
        
        with voice_col1:
            blocking_playback = st.checkbox("Wait for speech to finish", value=False, 
                                          help="If checked, the app will wait for Salty to finish speaking before continuing")
        
        with voice_col2:
            if st.button("🗣️ Make Salty Speak", type="primary"):
                if voice_text.strip():
                    with st.spinner("🦜 Salty is speaking..."):
                        result = asyncio.run(speak_salty_voice(voice_text, blocking=blocking_playback))
                        if "error" in result:
                            st.error(f"🦜 Squawk! Error: {result['error']}")
                        else:
                            st.success(result.get("response", "Salty spoke successfully!"))
                else:
                    st.warning("Please enter some text for Salty to say!")
        
        st.markdown("---")
        
        st.subheader("🎵 Ambient Sounds")
        
        # Ambient sound controls
        ambient_sounds = {
            "ocean_waves": "🌊 Ocean Waves",
            "jungle_birds": "🐦 Jungle Birds", 
            "tiki_drums": "🥁 Tiki Drums",
            "ship_bells": "🔔 Ship Bells",
            "parrot_squawk": "🦜 Parrot Squawk"
        }
        
        selected_sound = st.selectbox("Choose ambient sound", list(ambient_sounds.keys()), 
                                    format_func=lambda x: ambient_sounds[x])
        
        sound_col1, sound_col2, sound_col3 = st.columns(3)
        
        with sound_col1:
            sound_volume = st.slider("Volume", 0.0, 1.0, 0.5, 0.1, help="Set the volume level")
        
        with sound_col2:
            loop_sound = st.checkbox("Loop", value=False, help="Loop the sound continuously")
        
        with sound_col3:
            if st.button("🎵 Play Sound"):
                with st.spinner(f"🦜 Playing {ambient_sounds[selected_sound]}..."):
                    result = asyncio.run(play_ambient_sound(selected_sound, sound_volume, loop_sound))
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(result.get("response", "Ambient sound started!"))
        
        if st.button("🔇 Stop All Audio"):
            with st.spinner("🦜 Stopping all audio..."):
                result = asyncio.run(stop_all_audio())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(result.get("response", "All audio stopped!"))
        
        st.markdown("---")
        
        st.subheader("🎭 Quick Voice Commands")
        
        # Quick voice commands
        quick_commands = [
            "Squawk! Welcome to The Gold Monkey!",
            "Ahoy there, matey!",
            "Tropical greetings from your favorite feathered friend!",
            "Shiver me timbers, that's a good question!",
            "Aye aye, captain!",
            "Time for a tropical drink, matey!",
            "The tiki bar is open for business!",
            "Another round for my favorite customers!"
        ]
        
        selected_command = st.selectbox("Quick Salty phrases", quick_commands)
        
        if st.button("🗣️ Say It!"):
            with st.spinner("🦜 Salty is speaking..."):
                result = asyncio.run(speak_salty_voice(selected_command, blocking=False))
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Salty said it!")
    
    with col2:
        st.subheader("🎙️ Voice Settings")
        
        # Voice configuration
        if st.button("🎙️ Get Available Voices"):
            with st.spinner("🦜 Getting available voices..."):
                result = asyncio.run(get_available_voices())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Voices retrieved!")
                    st.markdown(result.get("response", "No voices found"))
        
        st.markdown("---")
        
        st.subheader("🔧 Voice Configuration")
        
        # Show current voice settings
        st.write("**Current Voice Settings:**")
        st.code(f"""
ELEVENLABS_API_KEY: {'✅ Set' if os.getenv('ELEVENLABS_API_KEY') else '❌ Not set'}
ELEVENLABS_VOICE_ID: {os.getenv('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')}
VOICE_SERVER_URL: {os.getenv('VOICE_SERVER_URL', 'http://localhost:8001')}
        """)
        
        st.markdown("---")
        
        st.subheader("🎵 Audio Status")
        
        # Audio status indicators
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            st.metric("Voice Server", "🟢 Online", "ElevenLabs connected")
            st.metric("Audio System", "🟢 Ready", "Pygame initialized")
        
        with status_col2:
            st.metric("Voice Cache", "📦 Active", "50 phrases cached")
            st.metric("Ambient Sounds", "🎵 Available", "5 sounds loaded")
        
        st.markdown("---")
        
        st.subheader("🦜 Salty's Voice Tips")
        st.write("""
        **Voice Control Tips:**
        - 🗣️ **Speak naturally** - Salty understands conversational text
        - 🎵 **Ambient sounds** - Create the perfect tiki bar atmosphere
        - 🔊 **Volume control** - Adjust for different environments
        - 🔄 **Loop sounds** - Keep the atmosphere going
        - ⏸️ **Non-blocking** - Let Salty speak while you continue working
        
        *Squawk! My voice brings the tiki bar to life!*
        """)
    
    # Voice test section
    st.markdown("---")
    st.subheader("🎭 Voice Test Panel")
    
    test_col1, test_col2, test_col3 = st.columns(3)
    
    with test_col1:
        if st.button("🦜 Test Salty's Voice"):
            test_text = "Squawk! This is a test of my voice synthesis. How do I sound, matey?"
            with st.spinner("🦜 Testing voice synthesis..."):
                result = asyncio.run(speak_salty_voice(test_text, blocking=False))
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Voice test completed!")
    
    with test_col2:
        if st.button("🌊 Test Ocean Waves"):
            with st.spinner("🦜 Playing ocean waves..."):
                result = asyncio.run(play_ambient_sound("ocean_waves", 0.3, False))
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("Ocean waves test completed!")
    
    with test_col3:
        if st.button("🔇 Stop All Audio"):
            with st.spinner("🦜 Stopping all audio..."):
                result = asyncio.run(stop_all_audio())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("All audio stopped!")
    
    # Voice integration with chat
    st.markdown("---")
    st.subheader("🤖 Voice Chat Integration")
    
    st.write("""
    **Coming Soon:**
    - 🎤 **Voice Commands** - "Hey Salty" wake word detection
    - 🗣️ **Voice Responses** - Salty speaks his chat responses
    - 🎵 **Background Music** - Automatic ambient sounds during chat
    - 🎭 **Voice Moods** - Different voice styles for different situations
    
    *🦜 Squawk! The future of tiki bar interaction is here!*
    """)

def show_knowledge_base():
    st.header("📚 Knowledge Base")
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
                
                if "error" in result:
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
    
    rag_dir = Path(__file__).parent / "rag"
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

def show_about():
    st.header("ℹ️ About")
    
    st.write("""
    ## The Gold Monkey
    
    This is a sophisticated home automation and entertainment system featuring Salty, 
    the AI-powered talking parrot who manages The Gold Monkey Tiki Bar.
    
    ### Features
    - 🤖 **AI Chatbot** - Salty powered by Google Gemini with personality
    - 💡 **Smart Lighting** - TP-Link smart bulb control with color presets
    - 📚 **Knowledge Base** - RAG system with ChromaDB for document retrieval
    - 📊 **Data exploration tools** - Upload and analyze CSV files
    - 📈 **Multiple chart types** - Beautiful visualizations
    - 🎨 **Beautiful and responsive design** - Modern Streamlit interface
    - ⚡ **Fast and interactive** - Real-time control and responses
    
    ### Smart Home Integration
    - **TP-Link Smart Bulbs** - Full color control and automation
    - **Device Discovery** - Automatic detection of smart devices
    - **Color Presets** - Pre-configured tiki bar lighting themes
    - **Custom Colors** - Full RGB color picker for custom moods
    
    ### Knowledge Base (RAG)
    - **Document Retrieval** - Semantic search through markdown files
    - **Vector Database** - ChromaDB with sentence transformer embeddings (stored in `data/chroma_db/`)
    - **Markdown Support** - Automatic processing of .md files
    - **Document Management** - Add, list, and rebuild knowledge base
    - **Direct Integration** - Direct ChromaDB and sentence-transformers integration
    
    ### Built with
    - Streamlit - Modern web interface
    - Google Generative AI (Gemini) - AI chatbot
    - ChromaDB - Vector database for RAG
    - Sentence Transformers - Text embeddings
    - Python Kasa - TP-Link smart device control
    - FastAPI - REST API for device communication
    - Pandas & NumPy - Data processing and analysis
    - SaltyBot - Dedicated chatbot server with personality
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🦜 Salty's Role")
        st.write("""
        Salty is more than just a chatbot - he's the heart of The Gold Monkey!
        
        - **Personality**: Witty, knowledgeable parrot with tiki bar wisdom
        - **Capabilities**: Controls lights, remembers conversations, provides entertainment
        - **Speech Style**: Nautical expressions, occasional squawks, tropical charm
        - **Knowledge**: Tiki culture, tropical drinks, sea stories, and more
        - **RAG Integration**: Can search through knowledge base for accurate information
        """)
    
    with col2:
        st.subheader("💡 Smart Lighting")
        st.write("""
        The lighting system creates the perfect tiki bar atmosphere:
        
        - **Quick Controls**: One-click on/off for all lights
        - **Color Presets**: Red, orange, yellow, green, blue, purple
        - **Custom Colors**: Full RGB control for any mood
        - **Device Management**: Automatic discovery and status monitoring
        - **Tiki Themes**: Pre-configured lighting for different occasions
        """)
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📚 Knowledge Base")
        st.write("""
        The RAG system provides intelligent document retrieval:
        
        - **Semantic Search**: Find relevant information using natural language
        - **Vector Database**: ChromaDB with sentence transformer embeddings (stored in `data/chroma_db/`)
        - **Markdown Support**: Automatic processing of .md files
        - **Document Management**: Add, list, and rebuild knowledge base
        - **Direct Integration**: Direct ChromaDB and sentence-transformers integration
        """)
    
    with col4:
        st.subheader("🔧 System Architecture")
        st.write("""
        **Built with modern, scalable architecture:**
        
        - **Direct Integration**: TP-Link and RAG components using direct library integration
        - **Async Operations**: Non-blocking I/O for better performance
        - **Error Handling**: Robust error handling and logging
        - **Modular Design**: Easy to extend with new features
        - **Environment Config**: Flexible configuration via .env files
        - **Dedicated Chatbot**: SaltyBot server for personality-driven conversations
        """)
    
    st.markdown("---")
    st.caption("Made with ❤️ using Streamlit and powered by Salty the Talking Parrot")

# Voice functions - Direct client implementation
async def speak_salty_voice(text: str, voice_id: str = None, blocking: bool = False):
    """Make Salty speak using voice synthesis"""
    try:
        from mcp_servers.voice_client import speak_text as voice_speak
        result = await voice_speak(text, voice_id, blocking)
        return result
    except Exception as e:
        st.error(f"Error speaking with Salty's voice: {e}")
        return {"error": str(e), "response": "Failed to speak"}

async def generate_salty_voice(text: str, voice_id: str = None):
    """Generate Salty's voice without playing it"""
    try:
        from mcp_servers.voice_client import generate_salty_voice as voice_generate
        result = await voice_generate(text, voice_id)
        return result
    except Exception as e:
        st.error(f"Error generating Salty's voice: {e}")
        return {"error": str(e), "response": "Failed to generate voice"}

async def play_ambient_sound(sound_name: str, volume: float = 0.5, loop: bool = False):
    """Play ambient tiki bar sounds"""
    try:
        from mcp_servers.voice_client import play_ambient_sound as voice_ambient
        result = await voice_ambient(sound_name, volume, loop)
        return result
    except Exception as e:
        st.error(f"Error playing ambient sound: {e}")
        return {"error": str(e), "response": "Failed to play ambient sound"}

async def stop_all_audio():
    """Stop all audio playback"""
    try:
        from mcp_servers.voice_client import stop_all_audio as voice_stop
        result = await voice_stop()
        return result
    except Exception as e:
        st.error(f"Error stopping audio: {e}")
        return {"error": str(e), "response": "Failed to stop audio"}

async def get_available_voices():
    """Get available ElevenLabs voices"""
    try:
        from mcp_servers.voice_client import get_available_voices as voice_list
        result = await voice_list()
        return result
    except Exception as e:
        st.error(f"Error getting available voices: {e}")
        return {"error": str(e), "response": "Failed to get voices"}

if __name__ == "__main__":
    main()
