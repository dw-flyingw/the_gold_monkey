#!/usr/bin/env python3
"""
Direct Roku Client for Salty
Provides Roku TV control without MCP dependencies
"""

import asyncio
import json
import logging
import os
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
ROKU_BASE_URL = f"http://{ROKU_HOST}:8060" if ROKU_HOST else None

def roku_post(endpoint: str, data: Optional[dict] = None) -> bool:
    """Make a POST request to the Roku device"""
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
    """Make a GET request to the Roku device"""
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

class RokuClient:
    """Direct Roku client without MCP dependencies"""
    
    def __init__(self):
        """Initialize the Roku client"""
        self.base_url = ROKU_BASE_URL
    
    async def power_on(self) -> Dict[str, Any]:
        """Power on the Roku device"""
        try:
            if not roku_post("/keypress/PowerOn"):
                return {"error": "Failed to power on Roku or not configured"}
            return {"response": "🟢 Roku powered on!"}
        except Exception as e:
            logger.error(f"Error powering on Roku: {e}", exc_info=True)
            return {"error": f"Error powering on Roku: {str(e)}"}
    
    async def power_off(self) -> Dict[str, Any]:
        """Power off the Roku device"""
        try:
            if not roku_post("/keypress/PowerOff"):
                return {"error": "Failed to power off Roku or not configured"}
            return {"response": "⚫ Roku powered off!"}
        except Exception as e:
            logger.error(f"Error powering off Roku: {e}", exc_info=True)
            return {"error": f"Error powering off Roku: {str(e)}"}
    
    async def home(self) -> Dict[str, Any]:
        """Go to Roku home screen"""
        try:
            if not roku_post("/keypress/Home"):
                return {"error": "Failed to go home or Roku not configured"}
            return {"response": "🏠 Roku home screen activated!"}
        except Exception as e:
            logger.error(f"Error going home: {e}", exc_info=True)
            return {"error": f"Error going home: {str(e)}"}
    
    async def launch_app(self, app_name: str) -> Dict[str, Any]:
        """Launch an app by name on Roku"""
        try:
            if not self.base_url:
                return {"error": "Roku isn't configured"}
            
            # Get list of apps
            resp = roku_get("/query/apps")
            if not resp:
                return {"error": "Could not retrieve Roku apps"}
            
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
                return {"error": "Failed to increase volume or Roku not configured"}
            return {"response": "🔊 Volume up!"}
        except Exception as e:
            logger.error(f"Error increasing volume: {e}", exc_info=True)
            return {"error": f"Error increasing volume: {str(e)}"}
    
    async def volume_down(self) -> Dict[str, Any]:
        """Decrease Roku volume"""
        try:
            if not roku_post("/keypress/VolumeDown"):
                return {"error": "Failed to decrease volume or Roku not configured"}
            return {"response": "🔉 Volume down!"}
        except Exception as e:
            logger.error(f"Error decreasing volume: {e}", exc_info=True)
            return {"error": f"Error decreasing volume: {str(e)}"}
    
    async def mute(self) -> Dict[str, Any]:
        """Mute Roku volume"""
        try:
            if not roku_post("/keypress/VolumeMute"):
                return {"error": "Failed to mute or Roku not configured"}
            return {"response": "🔇 Roku muted!"}
        except Exception as e:
            logger.error(f"Error muting Roku: {e}", exc_info=True)
            return {"error": f"Error muting Roku: {str(e)}"}
    
    async def info(self) -> Dict[str, Any]:
        """Show Roku info banner"""
        try:
            if not roku_post("/keypress/Info"):
                return {"error": "Failed to show info or Roku not configured"}
            return {"response": "ℹ️ Roku info banner displayed!"}
        except Exception as e:
            logger.error(f"Error showing info: {e}", exc_info=True)
            return {"error": f"Error showing info: {str(e)}"}
    
    async def up(self) -> Dict[str, Any]:
        """Navigate up on Roku"""
        try:
            if not roku_post("/keypress/Up"):
                return {"error": "Failed to navigate up or Roku not configured"}
            return {"response": "⬆️ Navigated up!"}
        except Exception as e:
            logger.error(f"Error navigating up: {e}", exc_info=True)
            return {"error": f"Error navigating up: {str(e)}"}
    
    async def down(self) -> Dict[str, Any]:
        """Navigate down on Roku"""
        try:
            if not roku_post("/keypress/Down"):
                return {"error": "Failed to navigate down or Roku not configured"}
            return {"response": "⬇️ Navigated down!"}
        except Exception as e:
            logger.error(f"Error navigating down: {e}", exc_info=True)
            return {"error": f"Error navigating down: {str(e)}"}
    
    async def left(self) -> Dict[str, Any]:
        """Navigate left on Roku"""
        try:
            if not roku_post("/keypress/Left"):
                return {"error": "Failed to navigate left or Roku not configured"}
            return {"response": "⬅️ Navigated left!"}
        except Exception as e:
            logger.error(f"Error navigating left: {e}", exc_info=True)
            return {"error": f"Error navigating left: {str(e)}"}
    
    async def right(self) -> Dict[str, Any]:
        """Navigate right on Roku"""
        try:
            if not roku_post("/keypress/Right"):
                return {"error": "Failed to navigate right or Roku not configured"}
            return {"response": "➡️ Navigated right!"}
        except Exception as e:
            logger.error(f"Error navigating right: {e}", exc_info=True)
            return {"error": f"Error navigating right: {str(e)}"}
    
    async def select(self) -> Dict[str, Any]:
        """Select current item on Roku"""
        try:
            if not roku_post("/keypress/Select"):
                return {"error": "Failed to select or Roku not configured"}
            return {"response": "✅ Selected!"}
        except Exception as e:
            logger.error(f"Error selecting: {e}", exc_info=True)
            return {"error": f"Error selecting: {str(e)}"}
    
    async def back(self) -> Dict[str, Any]:
        """Go back on Roku"""
        try:
            if not roku_post("/keypress/Back"):
                return {"error": "Failed to go back or Roku not configured"}
            return {"response": "↩️ Went back!"}
        except Exception as e:
            logger.error(f"Error going back: {e}", exc_info=True)
            return {"error": f"Error going back: {str(e)}"}
    
    async def get_apps(self) -> Dict[str, Any]:
        """Get list of installed apps on Roku"""
        try:
            if not self.base_url:
                return {"error": "Roku isn't configured"}
            
            resp = roku_get("/query/apps")
            if not resp:
                return {"error": "Could not retrieve Roku apps"}
            
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)
            apps = []
            for app in root.findall('app'):
                apps.append({
                    'name': app.text,
                    'id': app.attrib.get('id', ''),
                    'type': app.attrib.get('type', '')
                })
            
            return {"response": f"Found {len(apps)} apps on Roku", "apps": apps}
        except Exception as e:
            logger.error(f"Error getting apps: {e}", exc_info=True)
            return {"error": f"Error getting apps: {str(e)}"}

# Global client instance
roku_client = RokuClient()

# Convenience functions for direct use
async def power_on() -> Dict[str, Any]:
    """Power on the Roku device"""
    return await roku_client.power_on()

async def power_off() -> Dict[str, Any]:
    """Power off the Roku device"""
    return await roku_client.power_off()

async def home() -> Dict[str, Any]:
    """Go to Roku home screen"""
    return await roku_client.home()

async def launch_app(app_name: str) -> Dict[str, Any]:
    """Launch an app by name on Roku"""
    return await roku_client.launch_app(app_name)

async def volume_up() -> Dict[str, Any]:
    """Increase Roku volume"""
    return await roku_client.volume_up()

async def volume_down() -> Dict[str, Any]:
    """Decrease Roku volume"""
    return await roku_client.volume_down()

async def mute() -> Dict[str, Any]:
    """Mute Roku volume"""
    return await roku_client.mute()

async def info() -> Dict[str, Any]:
    """Show Roku info banner"""
    return await roku_client.info()

async def up() -> Dict[str, Any]:
    """Navigate up on Roku"""
    return await roku_client.up()

async def down() -> Dict[str, Any]:
    """Navigate down on Roku"""
    return await roku_client.down()

async def left() -> Dict[str, Any]:
    """Navigate left on Roku"""
    return await roku_client.left()

async def right() -> Dict[str, Any]:
    """Navigate right on Roku"""
    return await roku_client.right()

async def select() -> Dict[str, Any]:
    """Select current item on Roku"""
    return await roku_client.select()

async def back() -> Dict[str, Any]:
    """Go back on Roku"""
    return await roku_client.back()

async def get_apps() -> Dict[str, Any]:
    """Get list of installed apps on Roku"""
    return await roku_client.get_apps() 