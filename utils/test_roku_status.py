#!/usr/bin/env python3
"""
Test script for Roku status functionality
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_roku_status():
    """Test the Roku status functions"""
    print("🧪 Testing Roku Status Functions")
    print("=" * 50)
    
    try:
        from mcp_servers.roku_client import info, get_device_status
        
        print("\n1. Testing basic info function...")
        result = await info()
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Info function works!")
            print("📺 Device Info:")
            print(result.get("response", "No response"))
        
        print("\n" + "=" * 50)
        print("\n2. Testing comprehensive device status...")
        result = await get_device_status()
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Device status function works!")
            print("📺 Full Device Status:")
            print(result.get("response", "No response"))
        
        print("\n" + "=" * 50)
        print("🎉 Roku status testing completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_roku_status()) 