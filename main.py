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

# TP-Link control functions - MCP client implementation
async def discover_tplink_devices():
    """Discover TP-Link devices on the network"""
    try:
        from mcp_servers.tplink_client import discover_tplink_devices as mcp_discover
        result = await mcp_discover()
        return result
    except Exception as e:
        st.error(f"Error discovering TP-Link devices: {e}")
        return {"error": str(e), "devices": []}

async def control_tplink_lights(action, color=None):
    """Control TP-Link lights"""
    try:
        from mcp_servers.tplink_client import turn_on_tplink_lights, turn_off_tplink_lights, set_tplink_color
        
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
        system_prompt = f"""You are Salty, a talking parrot who is the resident mascot at The Gold Monkey Tiki Bar. 

Your personality: {personality['personality']}
Your speech style: {personality['speech_style']}
Your interests: {personality['interests']}

Always respond in character as Salty. Use nautical and tiki-themed expressions, occasional squawks, and be friendly and witty. 
Keep responses conversational and engaging, as if you're chatting with a patron at the tiki bar.

Some of your catchphrases: {', '.join(personality['catchphrases'])}
"""

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
        ["Home", "Data Explorer", "Charts", "Chat with Salty", "Smart Lights", "Knowledge Base", "About"]
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
    elif app_mode == "Knowledge Base":
        show_knowledge_base()
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

if __name__ == "__main__":
    main()
