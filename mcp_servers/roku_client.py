#!/usr/bin/env python3
"""
Direct Roku Client for Salty
Provides Roku TV control without MCP dependencies
"""

import asyncio
import json
import logging
import os
import socket
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import requests
from pathlib import Path

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
        logging.FileHandler(LOGS_DIR / 'roku_client.log')
    ]
)
logger = logging.getLogger(__name__)

# Roku configuration
ROKU_HOST = os.getenv('ROKU_HOST')

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
        return f"http://{roku_ip}:8060"
    return None

def roku_post(endpoint: str, data: Optional[dict] = None) -> bool:
    """Make a POST request to the Roku device"""
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
    """Make a GET request to the Roku device"""
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

class RokuClient:
    """Direct Roku client without MCP dependencies"""
    
    def __init__(self):
        """Initialize the Roku client"""
        self.base_url = get_roku_base_url()
    
    async def power_on(self) -> Dict[str, Any]:
        """Power on the Roku device"""
        try:
            if not roku_post("/keypress/PowerOn"):
                return {"error": "Failed to power on Roku. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "🟢 Roku powered on!"}
        except Exception as e:
            logger.error(f"Error powering on Roku: {e}", exc_info=True)
            return {"error": f"Error powering on Roku: {str(e)}"}
    
    async def power_off(self) -> Dict[str, Any]:
        """Power off the Roku device"""
        try:
            if not roku_post("/keypress/PowerOff"):
                return {"error": "Failed to power off Roku. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "⚫ Roku powered off!"}
        except Exception as e:
            logger.error(f"Error powering off Roku: {e}", exc_info=True)
            return {"error": f"Error powering off Roku: {str(e)}"}
    
    async def home(self) -> Dict[str, Any]:
        """Go to Roku home screen"""
        try:
            if not roku_post("/keypress/Home"):
                return {"error": "Failed to go home. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "🏠 Roku home screen activated!"}
        except Exception as e:
            logger.error(f"Error going home: {e}", exc_info=True)
            return {"error": f"Error going home: {str(e)}"}
    
    async def launch_app(self, app_name: str) -> Dict[str, Any]:
        """Launch an app by name on Roku"""
        try:
            if not self.base_url:
                return {"error": "Roku isn't configured or can't be found"}
            
            # Get list of apps
            resp = roku_get("/query/apps")
            if not resp:
                return {"error": "Could not retrieve Roku apps! Check if Developer Mode is enabled."}
            
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)
            app = next((a for a in root.findall('app') if app_name.lower() in a.text.lower()), None)
            if not app:
                return {"error": f"App '{app_name}' not found on Roku"}
            
            app_id = app.attrib['id']
            if not roku_post(f"/launch/{app_id}"):
                return {"error": f"Failed to launch '{app_name}'"}
            
            return {"response": f"🚀 Launched '{app.text}' on Roku!"}
        except Exception as e:
            logger.error(f"Error launching app: {e}", exc_info=True)
            return {"error": f"Error launching app: {str(e)}"}
    
    async def volume_up(self) -> Dict[str, Any]:
        """Increase Roku volume"""
        try:
            if not roku_post("/keypress/VolumeUp"):
                return {"error": "Failed to increase volume. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "🔊 Volume up!"}
        except Exception as e:
            logger.error(f"Error increasing volume: {e}", exc_info=True)
            return {"error": f"Error increasing volume: {str(e)}"}
    
    async def volume_down(self) -> Dict[str, Any]:
        """Decrease Roku volume"""
        try:
            if not roku_post("/keypress/VolumeDown"):
                return {"error": "Failed to decrease volume. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "🔉 Volume down!"}
        except Exception as e:
            logger.error(f"Error decreasing volume: {e}", exc_info=True)
            return {"error": f"Error decreasing volume: {str(e)}"}
    
    async def mute(self) -> Dict[str, Any]:
        """Mute Roku volume"""
        try:
            if not roku_post("/keypress/VolumeMute"):
                return {"error": "Failed to mute. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "🔇 Roku muted!"}
        except Exception as e:
            logger.error(f"Error muting Roku: {e}", exc_info=True)
            return {"error": f"Error muting Roku: {str(e)}"}
    
    async def info(self) -> Dict[str, Any]:
        """Get Roku device status and information"""
        try:
            # Get device info
            device_info = await self.get_device_info()
            
            # Get current app info
            app_info = await self.get_current_app()
            
            # Get active apps
            active_apps = await self.get_active_apps()
            
            # Combine all information
            status = f"{device_info}\n\n"
            status += f"{app_info}\n\n"
            status += f"{active_apps}"
            
            return {"response": status}
        except Exception as e:
            logger.error(f"Error getting Roku info: {e}", exc_info=True)
            return {"error": f"Error getting Roku info: {str(e)}"}
    
    async def get_device_info(self) -> str:
        """Get Roku device information"""
        try:
            resp = roku_get("/query/device-info")
            if not resp:
                return "🦜 Squawk! Could not get device info. Check if device is powered on and Developer Mode is enabled, matey!"
            
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
    
    async def get_current_app(self) -> str:
        """Get information about the currently active app"""
        try:
            resp = roku_get("/query/active-app")
            if not resp:
                return "🦜 Squawk! Could not get current app info. Check if device is powered on and Developer Mode is enabled, matey!"
            
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
    
    async def get_active_apps(self) -> str:
        """Get list of installed apps"""
        try:
            resp = roku_get("/query/apps")
            if not resp:
                return "🦜 Squawk! Could not get apps list. Check if device is powered on and Developer Mode is enabled, matey!"
            
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
    
    async def get_device_status(self) -> Dict[str, Any]:
        """Get comprehensive Roku device status"""
        try:
            # Get device info
            device_info = await self.get_device_info()
            
            # Get current app
            current_app = await self.get_current_app()
            
            # Get network info
            network_info = await self.get_network_info()
            
            # Combine all status information
            status = f"📺 ROKU DEVICE STATUS\n"
            status += f"{'='*50}\n\n"
            status += f"{device_info}\n\n"
            status += f"{current_app}\n\n"
            status += f"{network_info}"
            
            return {"response": status}
        except Exception as e:
            logger.error(f"Error getting device status: {e}", exc_info=True)
            return {"error": f"Error getting device status: {str(e)}"}
    
    async def get_network_info(self) -> str:
        """Get Roku network information"""
        try:
            resp = roku_get("/query/network")
            if not resp:
                return "🌐 Network: Could not retrieve network info"
            
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
    
    async def up(self) -> Dict[str, Any]:
        """Navigate up on Roku"""
        try:
            if not roku_post("/keypress/Up"):
                return {"error": "Failed to navigate up. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "⬆️ Navigated up!"}
        except Exception as e:
            logger.error(f"Error navigating up: {e}", exc_info=True)
            return {"error": f"Error navigating up: {str(e)}"}
    
    async def down(self) -> Dict[str, Any]:
        """Navigate down on Roku"""
        try:
            if not roku_post("/keypress/Down"):
                return {"error": "Failed to navigate down. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "⬇️ Navigated down!"}
        except Exception as e:
            logger.error(f"Error navigating down: {e}", exc_info=True)
            return {"error": f"Error navigating down: {str(e)}"}
    
    async def left(self) -> Dict[str, Any]:
        """Navigate left on Roku"""
        try:
            if not roku_post("/keypress/Left"):
                return {"error": "Failed to navigate left. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "⬅️ Navigated left!"}
        except Exception as e:
            logger.error(f"Error navigating left: {e}", exc_info=True)
            return {"error": f"Error navigating left: {str(e)}"}
    
    async def right(self) -> Dict[str, Any]:
        """Navigate right on Roku"""
        try:
            if not roku_post("/keypress/Right"):
                return {"error": "Failed to navigate right. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "➡️ Navigated right!"}
        except Exception as e:
            logger.error(f"Error navigating right: {e}", exc_info=True)
            return {"error": f"Error navigating right: {str(e)}"}
    
    async def select(self) -> Dict[str, Any]:
        """Select current item on Roku"""
        try:
            if not roku_post("/keypress/Select"):
                return {"error": "Failed to select. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "✅ Selected!"}
        except Exception as e:
            logger.error(f"Error selecting: {e}", exc_info=True)
            return {"error": f"Error selecting: {str(e)}"}
    
    async def back(self) -> Dict[str, Any]:
        """Go back on Roku"""
        try:
            if not roku_post("/keypress/Back"):
                return {"error": "Failed to go back. Check if device is powered on and Developer Mode is enabled"}
            return {"response": "↩️ Went back!"}
        except Exception as e:
            logger.error(f"Error going back: {e}", exc_info=True)
            return {"error": f"Error going back: {str(e)}"}
    
    async def get_apps(self) -> Dict[str, Any]:
        """Get list of installed apps"""
        try:
            resp = roku_get("/query/apps")
            if not resp:
                return {"error": "Could not retrieve Roku apps! Check if Developer Mode is enabled."}
            
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)
            apps = []
            
            for app in root.findall('app'):
                apps.append({
                    'name': app.text,
                    'id': app.attrib.get('id', 'Unknown')
                })
            
            return {"response": f"Found {len(apps)} apps", "apps": apps}
        except Exception as e:
            logger.error(f"Error getting apps: {e}", exc_info=True)
            return {"error": f"Error getting apps: {str(e)}"}

# Convenience functions for direct use
async def power_on() -> Dict[str, Any]:
    """Power on the Roku device"""
    client = RokuClient()
    return await client.power_on()

async def power_off() -> Dict[str, Any]:
    """Power off the Roku device"""
    client = RokuClient()
    return await client.power_off()

async def home() -> Dict[str, Any]:
    """Go to Roku home screen"""
    client = RokuClient()
    return await client.home()

async def launch_app(app_name: str) -> Dict[str, Any]:
    """Launch an app by name on Roku"""
    client = RokuClient()
    return await client.launch_app(app_name)

async def volume_up() -> Dict[str, Any]:
    """Increase Roku volume"""
    client = RokuClient()
    return await client.volume_up()

async def volume_down() -> Dict[str, Any]:
    """Decrease Roku volume"""
    client = RokuClient()
    return await client.volume_down()

async def mute() -> Dict[str, Any]:
    """Mute Roku volume"""
    client = RokuClient()
    return await client.mute()

async def info() -> Dict[str, Any]:
    """Show Roku info banner"""
    client = RokuClient()
    return await client.info()

async def up() -> Dict[str, Any]:
    """Navigate up on Roku"""
    client = RokuClient()
    return await client.up()

async def down() -> Dict[str, Any]:
    """Navigate down on Roku"""
    client = RokuClient()
    return await client.down()

async def left() -> Dict[str, Any]:
    """Navigate left on Roku"""
    client = RokuClient()
    return await client.left()

async def right() -> Dict[str, Any]:
    """Navigate right on Roku"""
    client = RokuClient()
    return await client.right()

async def select() -> Dict[str, Any]:
    """Select current item on Roku"""
    client = RokuClient()
    return await client.select()

async def back() -> Dict[str, Any]:
    """Go back on Roku"""
    client = RokuClient()
    return await client.back()

async def get_apps() -> Dict[str, Any]:
    """Get list of installed apps"""
    client = RokuClient()
    return await client.get_apps()

async def get_device_status() -> Dict[str, Any]:
    """Get comprehensive Roku device status"""
    client = RokuClient()
    return await client.get_device_status() 