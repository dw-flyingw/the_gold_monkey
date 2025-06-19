#!/usr/bin/env python3
"""
TP-Link MCP Server for Salty
Provides smart lighting control via MCP protocol
"""

import asyncio
import logging
from typing import Any, Sequence
from mcp.server import Server
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
from mcp.server.lowlevel.server import NotificationOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the server
server = Server("tplink-server")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available TP-Link tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="discover_tplink_devices",
                description="Discover TP-Link smart devices on the network",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="turn_on_lights",
                description="Turn on all TP-Link smart lights",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="turn_off_lights",
                description="Turn off all TP-Link smart lights",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="set_light_color",
                description="Set color for all TP-Link smart lights",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "color": {
                            "type": "string",
                            "description": "Color name (red, orange, yellow, green, blue, purple, pink, white, warm_white, cool_white) or hex color code",
                            "enum": ["red", "orange", "yellow", "green", "blue", "purple", "pink", "white", "warm_white", "cool_white"]
                        }
                    },
                    "required": ["color"]
                }
            ),
            Tool(
                name="get_light_status",
                description="Get status of all TP-Link smart lights",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
        ]
    )

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle TP-Link tool calls"""
    try:
        if name == "discover_tplink_devices":
            return await discover_tplink_devices()
        elif name == "turn_on_lights":
            return await turn_on_lights()
        elif name == "turn_off_lights":
            return await turn_off_lights()
        elif name == "set_light_color":
            color = arguments.get("color")
            if not color:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Color parameter is required")]
                )
            return await set_light_color(color)
        elif name == "get_light_status":
            return await get_light_status()
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")]
            )
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

async def discover_tplink_devices() -> CallToolResult:
    """Discover TP-Link devices on the network"""
    try:
        import kasa
        
        # Discover devices
        devices = await kasa.Discover.discover()
        device_list = list(devices.values())
        
        if not device_list:
            return CallToolResult(
                content=[TextContent(type="text", text="No TP-Link devices found on the network")]
            )
        
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
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text.strip())]
        )
        
    except Exception as e:
        logger.error(f"Error discovering devices: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error discovering TP-Link devices: {str(e)}")]
        )

async def turn_on_lights() -> CallToolResult:
    """Turn on all TP-Link smart lights"""
    try:
        import kasa
        
        # Discover devices
        devices = await kasa.Discover.discover()
        device_list = list(devices.values())
        
        if not device_list:
            return CallToolResult(
                content=[TextContent(type="text", text="No TP-Link devices found on the network")]
            )
        
        # Turn on all lights
        turned_on = 0
        for device in device_list:
            try:
                if hasattr(device, 'turn_on'):
                    await device.turn_on()
                    turned_on += 1
            except Exception as e:
                logger.warning(f"Error turning on device {device.host}: {e}")
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"🟢 Turned on {turned_on} out of {len(device_list)} devices")]
        )
        
    except Exception as e:
        logger.error(f"Error turning on lights: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error turning on lights: {str(e)}")]
        )

async def turn_off_lights() -> CallToolResult:
    """Turn off all TP-Link smart lights"""
    try:
        import kasa
        
        # Discover devices
        devices = await kasa.Discover.discover()
        device_list = list(devices.values())
        
        if not device_list:
            return CallToolResult(
                content=[TextContent(type="text", text="No TP-Link devices found on the network")]
            )
        
        # Turn off all lights
        turned_off = 0
        for device in device_list:
            try:
                if hasattr(device, 'turn_off'):
                    await device.turn_off()
                    turned_off += 1
            except Exception as e:
                logger.warning(f"Error turning off device {device.host}: {e}")
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"⚫ Turned off {turned_off} out of {len(device_list)} devices")]
        )
        
    except Exception as e:
        logger.error(f"Error turning off lights: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error turning off lights: {str(e)}")]
        )

async def set_light_color(color: str) -> CallToolResult:
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
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Invalid hex color format")]
                )
        else:
            rgb = color_map.get(color.lower(), (255, 255, 255))
        
        # Discover devices
        devices = await kasa.Discover.discover()
        device_list = list(devices.values())
        
        if not device_list:
            return CallToolResult(
                content=[TextContent(type="text", text="No TP-Link devices found on the network")]
            )
        
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
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"🎨 Set color to {color} for {updated} out of {len(device_list)} devices")]
        )
        
    except Exception as e:
        logger.error(f"Error setting light color: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error setting light color: {str(e)}")]
        )

async def get_light_status() -> CallToolResult:
    """Get status of all TP-Link smart lights"""
    try:
        import kasa
        
        # Discover devices
        devices = await kasa.Discover.discover()
        device_list = list(devices.values())
        
        if not device_list:
            return CallToolResult(
                content=[TextContent(type="text", text="No TP-Link devices found on the network")]
            )
        
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
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text.strip())]
        )
        
    except Exception as e:
        logger.error(f"Error getting light status: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error getting light status: {str(e)}")]
        )

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

# Create the server instance
server_instance = server

if __name__ == "__main__":
    # Run the server
    asyncio.run(stdio_server(server_instance)) 