#!/usr/bin/env python3
"""
Test script for TP-Link caching system
"""

import asyncio
import time
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_servers.tplink_direct import (
    discover_tplink_devices,
    turn_on_tplink_lights,
    turn_off_tplink_lights,
    get_tplink_status
)

async def test_caching_system():
    """Test the TP-Link caching system"""
    print("🧪 Testing TP-Link Caching System")
    print("=" * 50)
    
    # Test 1: Initial discovery
    print("\n1. Testing initial device discovery...")
    start_time = time.time()
    result = await discover_tplink_devices()
    discovery_time = time.time() - start_time
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    else:
        print(f"✅ Found devices in {discovery_time:.2f}s")
        print(f"Response: {result.get('response', 'No response')[:100]}...")
    
    # Test 2: Fast subsequent discovery (should use cache)
    print("\n2. Testing cached discovery (should be fast)...")
    start_time = time.time()
    result2 = await discover_tplink_devices()
    cached_time = time.time() - start_time
    
    if "error" in result2:
        print(f"❌ Error: {result2['error']}")
    else:
        print(f"✅ Cached discovery: {cached_time:.2f}s")
        if discovery_time > 0:
            print(f"   Speed improvement: {discovery_time/cached_time:.1f}x faster")
    
    # Test 3: Device control (should use cache)
    print("\n3. Testing device control with cache...")
    start_time = time.time()
    result = await turn_on_tplink_lights()
    control_time = time.time() - start_time
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Device control: {result.get('response', 'Success')} in {control_time:.2f}s")
    
    # Test 4: Get status (should use cache)
    print("\n4. Testing status retrieval with cache...")
    start_time = time.time()
    result = await get_tplink_status()
    status_time = time.time() - start_time
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Status retrieval: {status_time:.2f}s")
        print(f"Response: {result.get('response', 'No response')[:100]}...")
    
    # Test 5: Turn off devices
    print("\n5. Testing device turn off...")
    start_time = time.time()
    result = await turn_off_tplink_lights()
    off_time = time.time() - start_time
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Device turn off: {result.get('response', 'Success')} in {off_time:.2f}s")
    
    print("\n" + "=" * 50)
    print("🎉 Caching system test completed!")
    print(f"📊 Performance Summary:")
    print(f"   - Initial discovery: {discovery_time:.2f}s")
    print(f"   - Cached discovery: {cached_time:.2f}s")
    if discovery_time > 0 and cached_time > 0:
        print(f"   - Speed improvement: {discovery_time/cached_time:.1f}x")
    print(f"   - Device control: {control_time:.2f}s")
    print(f"   - Status retrieval: {status_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_caching_system()) 