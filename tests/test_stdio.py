#!/usr/bin/env python3
"""
Test script to understand MCP stdio_server usage
"""

import asyncio
from mcp.server.stdio import stdio_server

async def test_stdio():
    print("Testing stdio_server...")
    try:
        async with stdio_server() as server:
            print("Server started successfully")
            await asyncio.sleep(1)
            print("Server stopped")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_stdio()) 