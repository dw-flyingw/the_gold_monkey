#!/usr/bin/env python3
"""
Test script for MCP servers
Tests the functionality of all MCP servers used by Salty
"""

import asyncio
import sys
import os

# Add mcp_servers to Python path (from utils folder, need to go up one level)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp_servers"))

def test_saltybot_server():
    """Test the SaltyBot MCP server"""
    print("🦜 Testing SaltyBot MCP server...")
    
    try:
        from saltybot_client import chat_with_salty, get_salty_config
        print("✅ SaltyBot MCP client imported successfully")
        
        # Test configuration
        config = get_salty_config()
        print(f"✅ SaltyBot config: {config}")
        
        return True
    except Exception as e:
        print(f"❌ SaltyBot MCP server test failed: {e}")
        return False

def test_rag_server():
    """Test the RAG MCP server"""
    print("📚 Testing RAG MCP server...")
    
    try:
        from rag_client import get_rag_stats, query_rag_documents
        print("✅ RAG MCP client imported successfully")
        
        # Test basic functionality
        stats = get_rag_stats()
        print(f"✅ RAG stats: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ RAG MCP server test failed: {e}")
        return False

def test_tplink_server():
    """Test the TP-Link MCP server"""
    print("💡 Testing TP-Link MCP server...")
    
    try:
        from tplink_client import discover_tplink_devices, get_tplink_status
        print("✅ TP-Link MCP client imported successfully")
        
        # Test basic functionality
        status = get_tplink_status()
        print(f"✅ TP-Link status: {status}")
        
        return True
    except Exception as e:
        print(f"❌ TP-Link MCP server test failed: {e}")
        return False

async def main():
    """Run all MCP server tests"""
    print("🧪 Testing MCP servers...\n")
    
    # Test each server
    saltybot_ok = test_saltybot_server()
    print()
    
    rag_ok = test_rag_server()
    print()
    
    tplink_ok = test_tplink_server()
    print()
    
    # Summary
    print("📊 Test Results:")
    print(f"🦜 SaltyBot: {'✅ PASS' if saltybot_ok else '❌ FAIL'}")
    print(f"📚 RAG: {'✅ PASS' if rag_ok else '❌ FAIL'}")
    print(f"💡 TP-Link: {'✅ PASS' if tplink_ok else '❌ FAIL'}")
    print()
    
    if all([saltybot_ok, rag_ok, tplink_ok]):
        print("🎉 All MCP servers are working correctly!")
    else:
        print("⚠️ Some MCP servers have issues. Check the logs above.")

if __name__ == "__main__":
    asyncio.run(main()) 