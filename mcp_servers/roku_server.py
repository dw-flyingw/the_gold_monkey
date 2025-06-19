#!/usr/bin/env python3
"""
Roku MCP Server for Salty
Provides Roku TV control via MCP protocol using Roku's REST API
"""

import asyncio
import logging
import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path
import requests

# MCP imports
from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool
)

# Load environment variables
load_dotenv()

# Ensure logs directory exists
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / 'roku_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Roku configuration
ROKU_HOST = os.getenv('ROKU_HOST')
ROKU_MCP_URL = os.getenv('ROKU_MCP_URL')
ROKU_BASE_URL = f"http://{ROKU_HOST}:8060" if ROKU_HOST else None

def roku_post(endpoint: str, data: Optional[dict] = None) -> bool:
    if not ROKU_BASE_URL:
        return False
    try:
        url = f"{ROKU_BASE_URL}{endpoint}"
        response = requests.post(url, data=data, timeout=2)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"HTTP POST to {endpoint} failed: {e}")
        return False

def roku_get(endpoint: str) -> Optional[requests.Response]:
    if not ROKU_BASE_URL:
        return None
    try:
        url = f"{ROKU_BASE_URL}{endpoint}"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return response
        return None
    except Exception as e:
        logger.error(f"HTTP GET to {endpoint} failed: {e}")
        return None

# Create MCP server
server = FastMCP("roku")

@server.tool()
async def power_on() -> str:
    """Power on the Roku device (if supported)"""
    if not roku_post("/keypress/PowerOn"):
        return "🦜 Squawk! Failed to power on Roku or not configured, matey!"
    return "🟢 Roku powered on!"

@server.tool()
async def power_off() -> str:
    """Power off the Roku device (if supported)"""
    if not roku_post("/keypress/PowerOff"):
        return "🦜 Squawk! Failed to power off Roku or not configured, matey!"
    return "⚫ Roku powered off!"

@server.tool()
async def home() -> str:
    """Go to Roku home screen"""
    if not roku_post("/keypress/Home"):
        return "🦜 Squawk! Failed to go home or Roku not configured, matey!"
    return "🏠 Roku home screen activated!"

@server.tool()
async def launch_app(app_name: str) -> str:
    """Launch an app by name on Roku"""
    if not ROKU_BASE_URL:
        return "🦜 Squawk! Roku isn't configured, matey!"
    # Get list of apps
    resp = roku_get("/query/apps")
    if not resp:
        return "🦜 Squawk! Could not retrieve Roku apps!"
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.text)
        app = next((a for a in root.findall('app') if app_name.lower() in a.text.lower()), None)
        if not app:
            return f"🦜 Squawk! App '{app_name}' not found on Roku!"
        app_id = app.attrib['id']
        if not roku_post(f"/launch/{app_id}"):
            return f"🦜 Squawk! Failed to launch '{app_name}', matey!"
        return f"🚀 Launched '{app.text}' on Roku!"
    except Exception as e:
        logger.error(f"Error parsing Roku apps XML: {e}")
        return f"🦜 Squawk! Error launching app: {str(e)}"

@server.tool()
async def volume_up() -> str:
    """Increase Roku volume"""
    if not roku_post("/keypress/VolumeUp"):
        return "🦜 Squawk! Failed to increase volume or Roku not configured, matey!"
    return "🔊 Volume up!"

@server.tool()
async def volume_down() -> str:
    """Decrease Roku volume"""
    if not roku_post("/keypress/VolumeDown"):
        return "🦜 Squawk! Failed to decrease volume or Roku not configured, matey!"
    return "🔉 Volume down!"

@server.tool()
async def mute() -> str:
    """Mute Roku volume"""
    if not roku_post("/keypress/VolumeMute"):
        return "🦜 Squawk! Failed to mute or Roku not configured, matey!"
    return "🔇 Roku muted!"

@server.tool()
async def info() -> str:
    """Show Roku info banner"""
    if not roku_post("/keypress/Info"):
        return "🦜 Squawk! Failed to show info or Roku not configured, matey!"
    return "ℹ️ Roku info banner displayed!"

@server.tool()
async def up() -> str:
    """Navigate up on Roku"""
    if not roku_post("/keypress/Up"):
        return "🦜 Squawk! Failed to navigate up or Roku not configured, matey!"
    return "⬆️ Navigated up!"

@server.tool()
async def down() -> str:
    """Navigate down on Roku"""
    if not roku_post("/keypress/Down"):
        return "🦜 Squawk! Failed to navigate down or Roku not configured, matey!"
    return "⬇️ Navigated down!"

@server.tool()
async def left() -> str:
    """Navigate left on Roku"""
    if not roku_post("/keypress/Left"):
        return "🦜 Squawk! Failed to navigate left or Roku not configured, matey!"
    return "⬅️ Navigated left!"

@server.tool()
async def right() -> str:
    """Navigate right on Roku"""
    if not roku_post("/keypress/Right"):
        return "🦜 Squawk! Failed to navigate right or Roku not configured, matey!"
    return "➡️ Navigated right!"

@server.tool()
async def select() -> str:
    """Select current item on Roku"""
    if not roku_post("/keypress/Select"):
        return "🦜 Squawk! Failed to select or Roku not configured, matey!"
    return "✅ Selected!"

@server.tool()
async def back() -> str:
    """Go back on Roku"""
    if not roku_post("/keypress/Back"):
        return "🦜 Squawk! Failed to go back or Roku not configured, matey!"
    return "↩️ Went back!"

if __name__ == "__main__":
    stdio_server(server) 