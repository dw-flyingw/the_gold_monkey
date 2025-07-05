import os
import asyncio
import streamlit as st
import psutil
from pathlib import Path
import sys

# Import tplink_direct directly to avoid MCP import issues
try:
    # Add mcp_servers to path temporarily
    mcp_servers_dir = Path(__file__).parent.parent / "mcp_servers"
    sys.path.insert(0, str(mcp_servers_dir))
    from tplink_direct import TPLinkDirectClient
    sys.path.pop(0)  # Remove from path
except ImportError:
    # Fallback if tplink_direct is not available
    TPLinkDirectClient = None

SERVERS = {
    "TP-Link": {"path": "mcp_servers/tplink_server.py", "type": "mcp"},
    "RAG": {"path": "mcp_servers/rag_server.py", "type": "mcp"},
    "Spotify": {"path": "mcp_servers/spotify_server.py", "type": "mcp"},
    "Roku": {"path": "mcp_servers/roku_server.py", "type": "mcp"},
    "SaltyBot": {"path": "mcp_servers/saltybot_server.py", "type": "mcp"},
    "Voice": {"path": "mcp_servers/voice_server.py", "type": "standalone"}
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

def set_page_config():
    """Sets the default page configuration for all Streamlit pages"""
    st.set_page_config(
        page_title="The Gold Monkey",
        page_icon="images/gold_monkey.svg",
        layout="wide",
    )

def show_page_header(title, subtitle):
    """Displays the page header with a title and subtitle."""
    st.header(title)
    st.markdown(f"*🦜 {subtitle}*")

def get_tts_method():
    """Get the configured TTS method from environment variables"""
    return os.getenv('TTS_METHOD', 'none').lower()

async def get_light_devices():
    """Get a list of all available light devices."""
    if TPLinkDirectClient is None:
        return []
    try:
        client = TPLinkDirectClient()
        devices = await client._get_cached_devices()
        light_devices = client._get_light_devices(devices)
        return [d.alias for d in light_devices]
    except Exception:
        return []

async def rebuild_kasa_cache():
    """Force a rebuild of the Kasa device cache."""
    if TPLinkDirectClient is None:
        return
    try:
        client = TPLinkDirectClient()
        await client._get_cached_devices(force_refresh=True)
    except Exception:
        pass

def get_salty_config_direct():
    """Get Salty's configuration directly"""
    api_key = os.getenv('SALTY_GEMINI_API_KEY')
    return {
        'api_key': api_key,
        'model': os.getenv('SALTY_GEMINI_MODEL', 'gemini-2.0-flash'),
        'temperature': float(os.getenv('SALTY_GEMINI_TEMPERATURE', 0.7)),
        'max_tokens': int(os.getenv('SALTY_GEMINI_MAX_TOKENS', 1000)),
        'is_configured': api_key and api_key != 'your_gemini_api_key_here'
    }

def check_server_status():
    """Check the status of all MCP servers"""
    status = {}
    for server_name in SERVERS:
        pid_file = Path(f".pids/{server_name}.pid")
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text())
                if psutil.pid_exists(pid):
                    status[server_name] = {"running": True, "status": "🟢 Running"}
                else:
                    status[server_name] = {"running": False, "status": "🔴 Stopped"}
                    pid_file.unlink() # Clean up stale PID file
            except (ValueError, FileNotFoundError):
                status[server_name] = {"running": False, "status": "🔴 Stopped"}
        else:
            status[server_name] = {"running": False, "status": "🔴 Stopped"}
    return status