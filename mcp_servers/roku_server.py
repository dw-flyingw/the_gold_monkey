#!/usr/bin/env python3
"""
Roku MCP Server for Salty
Provides Roku TV control via MCP protocol using Roku's REST API
"""

import asyncio
import logging
import os
import socket
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

def discover_roku_ip():
    """Discover Roku IP address from hostname"""
    if not ROKU_HOST:
        logger.error("ROKU_HOST not set in environment")
        return None
    
    try:
        # Resolve hostname to IP address
        ip_address = socket.gethostbyname(ROKU_HOST)
        logger.info(f"Resolved {ROKU_HOST} to {ip_address}")
        return ip_address
    except socket.gaierror as e:
        logger.error(f"Failed to resolve hostname {ROKU_HOST}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error discovering Roku IP: {e}")
        return None

def get_roku_base_url():
    """Get Roku base URL with dynamic IP discovery"""
    roku_ip = discover_roku_ip()
    if roku_ip:
        port = os.getenv("ROKU_PORT", "8060")
        return f"http://{roku_ip}:{port}"
    return None

def roku_post(endpoint: str, data: Optional[dict] = None) -> bool:
    roku_base_url = get_roku_base_url()
    if not roku_base_url:
        logger.error("Could not determine Roku base URL")
        return False
    
    try:
        url = f"{roku_base_url}{endpoint}"
        logger.info(f"Making POST request to: {url}")
        response = requests.post(url, data=data, timeout=5)
        success = response.status_code == 200
        if not success:
            logger.warning(f"POST request failed with status {response.status_code}")
        return success
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to Roku: {e}")
        return False
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout connecting to Roku: {e}")
        return False
    except Exception as e:
        logger.error(f"HTTP POST to {endpoint} failed: {e}")
        return False

def roku_get(endpoint: str) -> Optional[requests.Response]:
    roku_base_url = get_roku_base_url()
    if not roku_base_url:
        logger.error("Could not determine Roku base URL")
        return None
    
    try:
        url = f"{roku_base_url}{endpoint}"
        logger.info(f"Making GET request to: {url}")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response
        else:
            logger.warning(f"GET request failed with status {response.status_code}")
            return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to Roku: {e}")
        return None
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout connecting to Roku: {e}")
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
        return "🦜 Squawk! Failed to power on Roku. Check if device is powered on and Developer Mode is enabled, matey!"
    return "🟢 Roku powered on!"

@server.tool()
async def power_off() -> str:
    """Power off the Roku device (if supported)"""
    if not roku_post("/keypress/PowerOff"):
        return "🦜 Squawk! Failed to power off Roku. Check if device is powered on and Developer Mode is enabled, matey!"
    return "⚫ Roku powered off!"

@server.tool()
async def home() -> str:
    """Go to Roku home screen"""
    if not roku_post("/keypress/Home"):
        return "🦜 Squawk! Failed to go home. Check if device is powered on and Developer Mode is enabled, matey!"
    return "🏠 Roku home screen activated!"

@server.tool()
async def launch_app(app_name: str) -> str:
    """Launch an app by name on Roku"""
    roku_base_url = get_roku_base_url()
    if not roku_base_url:
        return "🦜 Squawk! Roku isn't configured or can't be found, matey!"
    
    # Get list of apps
    resp = roku_get("/query/apps")
    if not resp:
        return "🦜 Squawk! Could not retrieve Roku apps! Check if Developer Mode is enabled."
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
        return "🦜 Squawk! Failed to increase volume. Check if device is powered on and Developer Mode is enabled, matey!"
    return "🔊 Volume up!"

@server.tool()
async def volume_down() -> str:
    """Decrease Roku volume"""
    if not roku_post("/keypress/VolumeDown"):
        return "🦜 Squawk! Failed to decrease volume. Check if device is powered on and Developer Mode is enabled, matey!"
    return "🔉 Volume down!"

@server.tool()
async def mute() -> str:
    """Mute Roku volume"""
    if not roku_post("/keypress/VolumeMute"):
        return "🦜 Squawk! Failed to mute. Check if device is powered on and Developer Mode is enabled, matey!"
    return "🔇 Roku muted!"

@server.tool()
async def info() -> str:
    """Get Roku device status and information"""
    try:
        # Get device info
        device_info = await get_device_info()
        
        # Get current app info
        app_info = await get_current_app()
        
        # Get active apps
        active_apps = await get_active_apps()
        
        # Combine all information
        status = f"{device_info}\n\n"
        status += f"{app_info}\n\n"
        status += f"{active_apps}"
        
        return status
    except Exception as e:
        logger.error(f"Error in info function: {e}")
        return f"🦜 Squawk! Error getting device info: {str(e)}"

@server.tool()
async def get_current_app() -> str:
    """Get information about the currently active app"""
    resp = roku_get("/query/active-app")
    if not resp:
        return "🦜 Squawk! Could not get current app info. Check if device is powered on and Developer Mode is enabled, matey!"
    
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.text)
        
        app_name = root.find('app')
        if app_name is not None and app_name.text:
            return f"📱 Current App: {app_name.text}"
        else:
            return "📱 Current App: Home Screen (no active app)"
    except Exception as e:
        logger.error(f"Error parsing current app: {e}")
        return f"🦜 Squawk! Error getting current app: {str(e)}"

@server.tool()
async def get_active_apps() -> str:
    """Get list of installed apps"""
    resp = roku_get("/query/apps")
    if not resp:
        return "🦜 Squawk! Could not get apps list. Check if device is powered on and Developer Mode is enabled, matey!"
    
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.text)
        
        apps = root.findall('app')
        if apps:
            app_list = []
            for app in apps[:10]:  # Show first 10 apps
                app_list.append(f"• {app.text}")
            
            result = f"📱 Installed Apps (showing first 10):\n" + "\n".join(app_list)
            if len(apps) > 10:
                result += f"\n... and {len(apps) - 10} more apps"
            return result
        else:
            return "📱 No apps found"
    except Exception as e:
        logger.error(f"Error parsing apps: {e}")
        return f"🦜 Squawk! Error getting apps: {str(e)}"

@server.tool()
async def get_device_status() -> str:
    """Get comprehensive Roku device status"""
    try:
        # Get device info
        device_info = await get_device_info()
        
        # Get current app
        current_app = await get_current_app()
        
        # Get network info
        network_info = await get_network_info()
        
        # Combine all status information
        status = f"📺 ROKU DEVICE STATUS\n"
        status += f"{'='*50}\n\n"
        status += f"{device_info}\n\n"
        status += f"{current_app}\n\n"
        status += f"{network_info}"
        
        return status
    except Exception as e:
        logger.error(f"Error in get_device_status function: {e}")
        return f"🦜 Squawk! Error getting device status: {str(e)}"

@server.tool()
async def get_network_info() -> str:
    """Get Roku network information"""
    resp = roku_get("/query/network")
    if not resp:
        return "🌐 Network: Could not retrieve network info"
    
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.text)
        
        network_info = "🌐 Network Information:\n"
        
        # Get various network details
        elements = {
            'ip': 'IP Address',
            'gateway': 'Gateway',
            'dns': 'DNS',
            'mac': 'MAC Address',
            'ssid': 'WiFi Network'
        }
        
        for element_name, display_name in elements.items():
            element = root.find(element_name)
            if element is not None and element.text:
                network_info += f"• {display_name}: {element.text}\n"
        
        return network_info
    except Exception as e:
        logger.error(f"Error parsing network info: {e}")
        return f"🌐 Network: Error retrieving network info - {str(e)}"

@server.tool()
async def up() -> str:
    """Navigate up on Roku"""
    if not roku_post("/keypress/Up"):
        return "🦜 Squawk! Failed to navigate up. Check if device is powered on and Developer Mode is enabled, matey!"
    return "⬆️ Navigated up!"

@server.tool()
async def down() -> str:
    """Navigate down on Roku"""
    if not roku_post("/keypress/Down"):
        return "🦜 Squawk! Failed to navigate down. Check if device is powered on and Developer Mode is enabled, matey!"
    return "⬇️ Navigated down!"

@server.tool()
async def left() -> str:
    """Navigate left on Roku"""
    if not roku_post("/keypress/Left"):
        return "🦜 Squawk! Failed to navigate left. Check if device is powered on and Developer Mode is enabled, matey!"
    return "⬅️ Navigated left!"

@server.tool()
async def right() -> str:
    """Navigate right on Roku"""
    if not roku_post("/keypress/Right"):
        return "🦜 Squawk! Failed to navigate right. Check if device is powered on and Developer Mode is enabled, matey!"
    return "➡️ Navigated right!"

@server.tool()
async def select() -> str:
    """Select current item on Roku"""
    if not roku_post("/keypress/Select"):
        return "🦜 Squawk! Failed to select. Check if device is powered on and Developer Mode is enabled, matey!"
    return "✅ Selected!"

@server.tool()
async def back() -> str:
    """Go back on Roku"""
    if not roku_post("/keypress/Back"):
        return "🦜 Squawk! Failed to go back. Check if device is powered on and Developer Mode is enabled, matey!"
    return "↩️ Went back!"

@server.tool()
async def get_device_info() -> str:
    """Get Roku device information"""
    resp = roku_get("/query/device-info")
    if not resp:
        return "🦜 Squawk! Could not get device info. Check if device is powered on and Developer Mode is enabled, matey!"
    
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.text)
        
        device_name = root.find('user-device-name')
        model_name = root.find('model-name')
        model_number = root.find('model-number')
        serial_number = root.find('serial-number')
        
        info = f"📺 Device Info:\n"
        info += f"• Name: {device_name.text if device_name is not None else 'Unknown'}\n"
        info += f"• Model: {model_name.text if model_name is not None else 'Unknown'}\n"
        info += f"• Model Number: {model_number.text if model_number is not None else 'Unknown'}\n"
        info += f"• Serial: {serial_number.text if serial_number is not None else 'Unknown'}\n"
        info += f"• IP: {discover_roku_ip() or 'Unknown'}"
        
        return info
    except Exception as e:
        logger.error(f"Error parsing device info: {e}")
        return f"🦜 Squawk! Error parsing device info: {str(e)}"

if __name__ == "__main__":
    stdio_server(server) 