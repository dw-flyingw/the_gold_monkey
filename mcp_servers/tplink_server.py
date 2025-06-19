#!/usr/bin/env python3
"""
TP-Link MCP Server for Salty
Provides smart lighting control via MCP protocol
"""

import asyncio
import logging
from typing import Any, Sequence
from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the server
server = FastMCP("tplink-server")

@server.tool()
async def discover_tplink_devices() -> str:
    """Discover TP-Link smart devices on the network"""
    try:
        import kasa
        
        # Discover devices
        devices = await kasa.Discover.discover()
        device_list = list(devices.values())
        
        if not device_list:
            return "No TP-Link devices found on the network"
        
        # Format device information
        device_info = []
        for device in device_list:
            try:
                await device.update()
                device_info.append({
                    "alias": device.alias,
                    "type": type(device).__name__,
                    "ip": device.host,
                    "is_on": device.is_on if hasattr(device, 'is_on') else None,
                    "brightness": device.brightness if hasattr(device, 'brightness') else None
                })
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
        
        return result_text.strip()
        
    except Exception as e:
        logger.error(f"Error discovering devices: {e}")
        return f"Error discovering TP-Link devices: {str(e)}"

@server.tool()
async def turn_on_lights() -> str:
    """Turn on all TP-Link smart lights"""
    try:
        import kasa
        
        # Discover devices
        devices = await kasa.Discover.discover()
        device_list = list(devices.values())
        
        if not device_list:
            return "No TP-Link devices found on the network"
        
        # Turn on all lights
        turned_on = 0
        for device in device_list:
            try:
                if hasattr(device, 'turn_on'):
                    await device.turn_on()
                    turned_on += 1
            except Exception as e:
                logger.warning(f"Error turning on device {device.host}: {e}")
        
        return f"🟢 Turned on {turned_on} out of {len(device_list)} devices"
        
    except Exception as e:
        logger.error(f"Error turning on lights: {e}")
        return f"Error turning on lights: {str(e)}"

@server.tool()
async def turn_off_lights() -> str:
    """Turn off all TP-Link smart lights"""
    try:
        import kasa
        
        # Discover devices
        devices = await kasa.Discover.discover()
        device_list = list(devices.values())
        
        if not device_list:
            return "No TP-Link devices found on the network"
        
        # Turn off all lights
        turned_off = 0
        for device in device_list:
            try:
                if hasattr(device, 'turn_off'):
                    await device.turn_off()
                    turned_off += 1
            except Exception as e:
                logger.warning(f"Error turning off device {device.host}: {e}")
        
        return f"⚫ Turned off {turned_off} out of {len(device_list)} devices"
        
    except Exception as e:
        logger.error(f"Error turning off lights: {e}")
        return f"Error turning off lights: {str(e)}"

@server.tool()
async def set_light_color(color: str) -> str:
    """Set color for all TP-Link smart lights"""
    try:
        import kasa
        
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
                return "Error: Invalid hex color format"
        else:
            rgb = color_map.get(color.lower(), (255, 255, 255))
        
        # Discover devices
        devices = await kasa.Discover.discover()
        device_list = list(devices.values())
        
        if not device_list:
            return "No TP-Link devices found on the network"
        
        # Set color for all devices
        updated = 0
        for device in device_list:
            try:
                if hasattr(device, 'set_hsv'):
                    # Convert RGB to HSV
                    h, s, v = _rgb_to_hsv(*rgb)
                    await device.set_hsv(h, s, v)
                    updated += 1
                elif hasattr(device, 'set_color_temp'):
                    # Fallback to color temperature
                    await device.set_color_temp(2700)
                    updated += 1
            except Exception as e:
                logger.warning(f"Error setting color for device {device.host}: {e}")
        
        return f"🎨 Set color to {color} for {updated} out of {len(device_list)} devices"
        
    except Exception as e:
        logger.error(f"Error setting light color: {e}")
        return f"Error setting light color: {str(e)}"

@server.tool()
async def get_light_status() -> str:
    """Get status of all TP-Link smart lights"""
    try:
        import kasa
        
        # Discover devices
        devices = await kasa.Discover.discover()
        device_list = list(devices.values())
        
        if not device_list:
            return "No TP-Link devices found on the network"
        
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
        
        return result_text.strip()
        
    except Exception as e:
        logger.error(f"Error getting light status: {e}")
        return f"Error getting light status: {str(e)}"

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

if __name__ == "__main__":
    server.run() 