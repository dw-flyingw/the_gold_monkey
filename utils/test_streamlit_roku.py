#!/usr/bin/env python3
"""
Test Roku integration as it would be called from Streamlit
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

async def test_streamlit_roku_integration():
    """Test Roku integration as it would be called from Streamlit"""
    print("🦜 Testing Roku integration as called from Streamlit")
    print("=" * 60)
    
    try:
        # Import the functions as they would be imported in main.py
        from mcp_servers.roku_client import info as roku_info
        
        print("✅ Successfully imported roku_client.info")
        
        # Test the function
        print("🔄 Testing info() function...")
        result = await roku_info()
        
        print(f"📊 Result: {result}")
        
        if "error" in result:
            print("❌ Function returned an error")
            return False
        else:
            print("✅ Function returned success")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_all_roku_functions():
    """Test all Roku functions"""
    print("\n🦜 Testing all Roku functions")
    print("=" * 40)
    
    try:
        from mcp_servers.roku_client import (
            power_on, power_off, home, volume_up, volume_down, 
            mute, info, up, down, left, right, select, back
        )
        
        functions = [
            ("Home", home),
            ("Info", info),
            ("Volume Up", volume_up),
            ("Volume Down", volume_down),
        ]
        
        results = {}
        
        for name, func in functions:
            print(f"🔄 Testing {name}...")
            try:
                result = await func()
                results[name] = result
                if "error" in result:
                    print(f"   ❌ {name}: {result['error']}")
                else:
                    print(f"   ✅ {name}: {result['response']}")
            except Exception as e:
                print(f"   ❌ {name}: Exception - {e}")
                results[name] = {"error": str(e)}
        
        # Summary
        print(f"\n📊 Summary:")
        success_count = sum(1 for r in results.values() if "response" in r)
        error_count = sum(1 for r in results.values() if "error" in r)
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Errors: {error_count}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error testing functions: {e}")
        return False

async def main():
    print("🦜 Salty's Streamlit Roku Integration Test")
    print("=" * 60)
    
    # Test basic integration
    if await test_streamlit_roku_integration():
        print("\n✅ Basic integration test passed!")
    else:
        print("\n❌ Basic integration test failed!")
        return
    
    # Test all functions
    if await test_all_roku_functions():
        print("\n✅ All function tests completed!")
    else:
        print("\n❌ Some function tests failed!")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 