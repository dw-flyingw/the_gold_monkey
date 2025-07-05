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
        self._device_cache = {}
        self._cache_timestamp = 0
        self._cache_duration = 30  # Cache devices for 30 seconds
    
    async def _get_cached_devices(self, force_refresh: bool = False) -> list:
        """Get devices from cache or discover them if cache is stale"""
        import time
        
        current_time = time.time()
        
        # Check if cache is valid
        if (not force_refresh and 
            self._device_cache and 
            current_time - self._cache_timestamp < self._cache_duration):
            logger.info("Using cached devices")
            return list(self._device_cache.values())
        
        # Discover devices
        logger.info("Discovering devices (cache miss or forced refresh)")
        devices = await kasa.Discover.discover()
        self._device_cache = devices
        self._cache_timestamp = current_time
        
        return list(devices.values())
    
    def _is_light_device(self, device) -> bool:
        """Check if device is a light that supports color/brightness control"""
        try:
            # Check if device has light-specific attributes
            has_brightness = hasattr(device, 'brightness')
            has_color = hasattr(device, 'set_hsv') or hasattr(device, '_set_hsv')
            has_color_temp = hasattr(device, 'set_color_temp')
            
            # Device is a light if it has brightness control or color capabilities
            return has_brightness or has_color or has_color_temp
        except Exception:
            return False
    
    def _get_light_devices(self, device_list: list) -> list:
        """Filter device list to only include light devices"""
        light_devices = []
        for device in device_list:
            if self._is_light_device(device):
                light_devices.append(device)
            else:
                logger.debug(f"Skipping non-light device: {device.alias} ({type(device).__name__})")
        return light_devices
    
    async def discover_devices(self) -> Dict[str, Any]:
        """Discover TP-Link devices on the network"""
        try:
            logger.info("Discovering TP-Link devices...")
            device_list = await self._get_cached_devices()
            
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
    
    async def turn_on_lights(self, device_alias: str = None) -> Dict[str, Any]:
        """Turn on all TP-Link smart lights"""
        try:
            logger.info("Turning on all TP-Link lights...")
            device_list = await self._get_cached_devices()
            
            if not device_list:
                return {"error": "No TP-Link devices found on the network"}
            
            # Filter to only light devices
            light_devices = self._get_light_devices(device_list)
            
            if not light_devices:
                return {"error": "No TP-Link light devices found on the network"}

            if device_alias and device_alias != "All Devices":
                light_devices = [d for d in light_devices if d.alias == device_alias]

            # Turn on all lights
            turned_on = 0
            errors = []
            for device in light_devices:
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
                return {"response": f"🟢 Turned on {turned_on} out of {len(light_devices)} light devices", "warnings": errors}
            else:
                return {"response": f"🟢 Turned on {turned_on} out of {len(light_devices)} light devices"}
            
        except Exception as e:
            logger.error(f"Error turning on lights: {e}", exc_info=True)
            return {"error": f"Error turning on lights: {str(e)}"}
    
    async def turn_off_lights(self, device_alias: str = None) -> Dict[str, Any]:
        """Turn off all TP-Link smart lights"""
        try:
            logger.info("Turning off all TP-Link lights...")
            device_list = await self._get_cached_devices()
            
            if not device_list:
                return {"error": "No TP-Link devices found on the network"}
            
            # Filter to only light devices
            light_devices = self._get_light_devices(device_list)
            
            if not light_devices:
                return {"error": "No TP-Link light devices found on the network"}

            if device_alias and device_alias != "All Devices":
                light_devices = [d for d in light_devices if d.alias == device_alias]

            # Turn off all lights
            turned_off = 0
            errors = []
            for device in light_devices:
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
                return {"response": f"⚫ Turned off {turned_off} out of {len(light_devices)} light devices", "warnings": errors}
            else:
                return {"response": f"⚫ Turned off {turned_off} out of {len(light_devices)} light devices"}
            
        except Exception as e:
            logger.error(f"Error turning off lights: {e}", exc_info=True)
            return {"error": f"Error turning off lights: {str(e)}"}
    
    async def set_light_color(self, color: str, device_alias: str = None) -> Dict[str, Any]:
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
            
            # Get devices from cache
            device_list = await self._get_cached_devices()
            
            if not device_list:
                return {"error": "No TP-Link devices found on the network"}
            
            # Filter to only light devices
            light_devices = self._get_light_devices(device_list)
            
            if not light_devices:
                return {"error": "No TP-Link light devices found on the network"}

            if device_alias and device_alias != "All Devices":
                light_devices = [d for d in light_devices if d.alias == device_alias]

            # Set color for all light devices
            updated = 0
            errors = []
            for device in light_devices:
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
                return {"response": f"🎨 Set color to {color} for {updated} out of {len(light_devices)} light devices", "warnings": errors}
            else:
                return {"response": f"🎨 Set color to {color} for {updated} out of {len(light_devices)} light devices"}
            
        except Exception as e:
            logger.error(f"Error setting light color: {e}", exc_info=True)
            return {"error": f"Error setting light color: {str(e)}"}
    
    async def set_light_brightness(self, brightness: int, device_alias: str = None) -> Dict[str, Any]:
        """Set brightness for TP-Link smart lights"""
        try:
            logger.info(f"Setting light brightness to: {brightness}%")
            
            device_list = await self._get_cached_devices()
            
            if not device_list:
                return {"error": "No TP-Link devices found on the network"}
            
            light_devices = self._get_light_devices(device_list)
            
            if not light_devices:
                return {"error": "No TP-Link light devices found on the network"}

            if device_alias and device_alias != "All Devices":
                light_devices = [d for d in light_devices if d.alias == device_alias]

            updated = 0
            errors = []
            for device in light_devices:
                try:
                    if hasattr(device, 'set_brightness'):
                        await device.set_brightness(brightness)
                        updated += 1
                        logger.info(f"Set brightness for {device.alias} to {brightness}%")
                    else:
                        logger.warning(f"Device {device.alias} does not support brightness control")
                except Exception as e:
                    error_msg = f"Error setting brightness for {device.alias}: {e}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
            
            if errors:
                return {"response": f"💡 Set brightness to {brightness}% for {updated} out of {len(light_devices)} light devices", "warnings": errors}
            else:
                return {"response": f"💡 Set brightness to {brightness}% for {updated} out of {len(light_devices)} light devices"}
            
        except Exception as e:
            logger.error(f"Error setting light brightness: {e}", exc_info=True)
            return {"error": f"Error setting light brightness: {str(e)}"}
    
    async def get_light_status(self) -> Dict[str, Any]:
        """Get status of all TP-Link smart lights"""
        try:
            logger.info("Getting TP-Link light status...")
            device_list = await self._get_cached_devices()
            
            if not device_list:
                return {"error": "No TP-Link devices found on the network"}
            
            # Filter to only light devices
            light_devices = self._get_light_devices(device_list)
            
            if not light_devices:
                return {"error": "No TP-Link light devices found on the network"}
            
            # Get status for all light devices
            status_info = []
            for device in light_devices:
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
            
            result_text = f"Status of {len(light_devices)} TP-Link light device(s):\n\n"
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
    
    async def get_all_device_status(self) -> Dict[str, Any]:
        """Get status of all TP-Link devices (including non-lights)"""
        try:
            logger.info("Getting all TP-Link device status...")
            device_list = await self._get_cached_devices()
            
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
                        "type": type(device).__name__,
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
                        "type": type(device).__name__,
                        "error": str(e)
                    })
            
            result_text = f"Status of {len(device_list)} TP-Link device(s):\n\n"
            for status in status_info:
                result_text += f"• {status['alias']} ({status['type']}) at {status['ip']}\n"
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
            logger.error(f"Error getting device status: {e}", exc_info=True)
            return {"error": f"Error getting device status: {str(e)}"}

# Global client instance for caching
_global_client = None

def _get_client():
    """Get or create the global TP-Link client instance"""
    global _global_client
    if _global_client is None:
        _global_client = TPLinkDirectClient()
    return _global_client

# Convenience functions for direct use
async def discover_tplink_devices() -> Dict[str, Any]:
    """Discover TP-Link devices on the network"""
    client = _get_client()
    return await client.discover_devices()

async def turn_on_tplink_lights(device=None) -> Dict[str, Any]:
    """Turn on all TP-Link lights"""
    client = _get_client()
    return await client.turn_on_lights(device)

async def turn_off_tplink_lights(device=None) -> Dict[str, Any]:
    """Turn off all TP-Link lights"""
    client = _get_client()
    return await client.turn_off_lights(device)

async def set_tplink_color(color: str, device=None) -> Dict[str, Any]:
    """Set color for all TP-Link lights"""
    client = _get_client()
    return await client.set_light_color(color, device)

async def set_tplink_brightness(brightness: int, device=None) -> Dict[str, Any]:
    """Set brightness for all TP-Link lights"""
    client = _get_client()
    return await client.set_light_brightness(brightness, device)

async def get_tplink_status() -> Dict[str, Any]:
    """Get status of all TP-Link lights"""
    client = _get_client()
    return await client.get_light_status()

async def get_all_tplink_status() -> Dict[str, Any]:
    """Get status of all TP-Link devices (including non-lights)"""
    client = _get_client()
    return await client.get_all_device_status()

async def get_tools() -> Dict[str, Any]:
    """Get a dictionary of all available tools"""
    return {
        "discover_tplink_devices": discover_tplink_devices,
        "turn_on_tplink_lights": turn_on_tplink_lights,
        "turn_off_tplink_lights": turn_off_tplink_lights,
        "set_tplink_color": set_tplink_color,
        "set_tplink_brightness": set_tplink_brightness,
        "get_tplink_status": get_tplink_status,
        "get_all_tplink_status": get_all_tplink_status,
    }

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