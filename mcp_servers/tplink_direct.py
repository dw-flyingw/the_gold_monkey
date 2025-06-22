#!/usr/bin/env python3
"""
Direct TP-Link Client for Salty
Provides TP-Link smart lighting control without MCP dependencies
"""

import asyncio
import logging
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import kasa
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
        logging.FileHandler(LOGS_DIR / 'tplink_direct.log')
    ]
)
logger = logging.getLogger(__name__)

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

class TPLinkDirectClient:
    """Direct TP-Link client without MCP dependencies"""
    
    def __init__(self):
        """Initialize the TP-Link client"""
        pass
    
    async def discover_devices(self) -> Dict[str, Any]:
        """Discover TP-Link devices on the network"""
        try:
            logger.info("Discovering TP-Link devices...")
            devices = await kasa.Discover.discover()
            device_list = list(devices.values())
            
            if not device_list:
                return {"error": "No TP-Link devices found on the network"}
            
            # Format device information
            device_info = []
            for device in device_list:
                try:
                    await device.update()
                    info = {
                        "alias": device.alias,
                        "type": type(device).__name__,
                        "ip": device.host,
                        "is_on": device.is_on if hasattr(device, 'is_on') else None,
                        "brightness": device.brightness if hasattr(device, 'brightness') else None
                    }
                    device_info.append(info)
                except Exception as e:
                    logger.warning(f"Error getting info for device {device.host}: {e}")
                    device_info.append({
                        "alias": device.alias,
                        "type": type(device).__name__,
                        "ip": device.host,
                        "error": str(e)
                    })
            
            result_text = f"Found {len(device_list)} TP-Link device(s):\n\n"
            for info in device_info:
                result_text += f"• {info['alias']} ({info['type']}) at {info['ip']}\n"
                if 'is_on' in info and info['is_on'] is not None:
                    result_text += f"  Status: {'🟢 On' if info['is_on'] else '⚫ Off'}\n"
                if 'brightness' in info and info['brightness'] is not None:
                    result_text += f"  Brightness: {info['brightness']}%\n"
                if 'error' in info:
                    result_text += f"  Error: {info['error']}\n"
                result_text += "\n"
            
            return {"response": result_text.strip(), "devices": device_info}
            
        except Exception as e:
            logger.error(f"Error discovering devices: {e}", exc_info=True)
            return {"error": f"Error discovering TP-Link devices: {str(e)}"}
    
    async def turn_on_lights(self) -> Dict[str, Any]:
        """Turn on all TP-Link smart lights"""
        try:
            logger.info("Turning on all TP-Link lights...")
            devices = await kasa.Discover.discover()
            device_list = list(devices.values())
            
            if not device_list:
                return {"error": "No TP-Link devices found on the network"}
            
            # Turn on all lights
            turned_on = 0
            errors = []
            for device in device_list:
                try:
                    if hasattr(device, 'turn_on'):
                        await device.turn_on()
                        turned_on += 1
                        logger.info(f"Turned on {device.alias}")
                    else:
                        logger.warning(f"Device {device.alias} does not support turn_on")
                except Exception as e:
                    error_msg = f"Error turning on {device.alias}: {e}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
            
            if errors:
                return {"response": f"🟢 Turned on {turned_on} out of {len(device_list)} devices", "warnings": errors}
            else:
                return {"response": f"🟢 Turned on {turned_on} out of {len(device_list)} devices"}
            
        except Exception as e:
            logger.error(f"Error turning on lights: {e}", exc_info=True)
            return {"error": f"Error turning on lights: {str(e)}"}
    
    async def turn_off_lights(self) -> Dict[str, Any]:
        """Turn off all TP-Link smart lights"""
        try:
            logger.info("Turning off all TP-Link lights...")
            devices = await kasa.Discover.discover()
            device_list = list(devices.values())
            
            if not device_list:
                return {"error": "No TP-Link devices found on the network"}
            
            # Turn off all lights
            turned_off = 0
            errors = []
            for device in device_list:
                try:
                    if hasattr(device, 'turn_off'):
                        await device.turn_off()
                        turned_off += 1
                        logger.info(f"Turned off {device.alias}")
                    else:
                        logger.warning(f"Device {device.alias} does not support turn_off")
                except Exception as e:
                    error_msg = f"Error turning off {device.alias}: {e}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
            
            if errors:
                return {"response": f"⚫ Turned off {turned_off} out of {len(device_list)} devices", "warnings": errors}
            else:
                return {"response": f"⚫ Turned off {turned_off} out of {len(device_list)} devices"}
            
        except Exception as e:
            logger.error(f"Error turning off lights: {e}", exc_info=True)
            return {"error": f"Error turning off lights: {str(e)}"}
    
    async def set_light_color(self, color: str) -> Dict[str, Any]:
        """Set color for all TP-Link smart lights"""
        try:
            logger.info(f"Setting light color to: {color}")
            
            # Color mapping
            color_map = {
                "red": (255, 0, 0),
                "orange": (255, 165, 0),
                "yellow": (255, 255, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),
                "purple": (128, 0, 128),
                "pink": (255, 192, 203),
                "white": (255, 255, 255),
                "warm_white": (255, 244, 229),
                "cool_white": (255, 255, 255)
            }
            
            # Handle hex colors
            if color.startswith('#'):
                try:
                    color = color.lstrip('#')
                    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                except:
                    return {"error": "Error: Invalid hex color format"}
            else:
                rgb = color_map.get(color.lower(), (255, 255, 255))
            
            logger.info(f"RGB values: {rgb}")
            
            # Discover devices
            devices = await kasa.Discover.discover()
            device_list = list(devices.values())
            
            if not device_list:
                return {"error": "No TP-Link devices found on the network"}
            
            # Set color for all devices
            updated = 0
            errors = []
            for device in device_list:
                try:
                    if hasattr(device, '_set_hsv'):
                        # Convert RGB to HSV
                        h, s, v = _rgb_to_hsv(*rgb)
                        logger.info(f"Setting HSV for {device.alias}: h={h}, s={s}, v={v}")
                        await device._set_hsv(h, s, v)
                        updated += 1
                        logger.info(f"Set color for {device.alias}")
                    elif hasattr(device, 'set_hsv'):
                        # Alternative method name
                        h, s, v = _rgb_to_hsv(*rgb)
                        logger.info(f"Setting HSV for {device.alias}: h={h}, s={s}, v={v}")
                        await device.set_hsv(h, s, v)
                        updated += 1
                        logger.info(f"Set color for {device.alias}")
                    elif hasattr(device, 'set_color_temp'):
                        # Fallback to color temperature
                        logger.info(f"Setting color temp for {device.alias}")
                        await device.set_color_temp(2700)
                        updated += 1
                        logger.info(f"Set color temp for {device.alias}")
                    else:
                        logger.warning(f"Device {device.alias} does not support color")
                except Exception as e:
                    error_msg = f"Error setting color for {device.alias}: {e}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
            
            if errors:
                return {"response": f"🎨 Set color to {color} for {updated} out of {len(device_list)} devices", "warnings": errors}
            else:
                return {"response": f"🎨 Set color to {color} for {updated} out of {len(device_list)} devices"}
            
        except Exception as e:
            logger.error(f"Error setting light color: {e}", exc_info=True)
            return {"error": f"Error setting light color: {str(e)}"}
    
    async def get_light_status(self) -> Dict[str, Any]:
        """Get status of all TP-Link smart lights"""
        try:
            logger.info("Getting TP-Link light status...")
            devices = await kasa.Discover.discover()
            device_list = list(devices.values())
            
            if not device_list:
                return {"error": "No TP-Link devices found on the network"}
            
            # Get status for all devices
            status_info = []
            for device in device_list:
                try:
                    await device.update()
                    status = {
                        "alias": device.alias,
                        "ip": device.host,
                        "is_on": device.is_on if hasattr(device, 'is_on') else None,
                        "brightness": device.brightness if hasattr(device, 'brightness') else None,
                        "color_temp": device.color_temp if hasattr(device, 'color_temp') else None
                    }
                    status_info.append(status)
                except Exception as e:
                    logger.warning(f"Error getting status for device {device.host}: {e}")
                    status_info.append({
                        "alias": device.alias,
                        "ip": device.host,
                        "error": str(e)
                    })
            
            result_text = f"Status of {len(device_list)} TP-Link device(s):\n\n"
            for status in status_info:
                result_text += f"• {status['alias']} ({status['ip']})\n"
                if 'is_on' in status and status['is_on'] is not None:
                    result_text += f"  Status: {'🟢 On' if status['is_on'] else '⚫ Off'}\n"
                if 'brightness' in status and status['brightness'] is not None:
                    result_text += f"  Brightness: {status['brightness']}%\n"
                if 'color_temp' in status and status['color_temp'] is not None:
                    result_text += f"  Color Temp: {status['color_temp']}K\n"
                if 'error' in status:
                    result_text += f"  Error: {status['error']}\n"
                result_text += "\n"
            
            return {"response": result_text.strip(), "devices": status_info}
            
        except Exception as e:
            logger.error(f"Error getting light status: {e}", exc_info=True)
            return {"error": f"Error getting light status: {str(e)}"}

# Convenience functions for direct use
async def discover_tplink_devices() -> Dict[str, Any]:
    """Discover TP-Link devices on the network"""
    client = TPLinkDirectClient()
    return await client.discover_devices()

async def turn_on_tplink_lights() -> Dict[str, Any]:
    """Turn on all TP-Link lights"""
    client = TPLinkDirectClient()
    return await client.turn_on_lights()

async def turn_off_tplink_lights() -> Dict[str, Any]:
    """Turn off all TP-Link lights"""
    client = TPLinkDirectClient()
    return await client.turn_off_lights()

async def set_tplink_color(color: str) -> Dict[str, Any]:
    """Set color for all TP-Link lights"""
    client = TPLinkDirectClient()
    return await client.set_light_color(color)

async def get_tplink_status() -> Dict[str, Any]:
    """Get status of all TP-Link lights"""
    client = TPLinkDirectClient()
    return await client.get_light_status()

if __name__ == "__main__":
    # Test the client
    async def test():
        try:
            # Test device discovery
            result = await discover_tplink_devices()
            print("Device discovery result:", result)
            
            # Test getting status
            status = await get_tplink_status()
            print("Light status:", status)
            
        except Exception as e:
            print(f"Test error: {e}")
    
    asyncio.run(test()) 