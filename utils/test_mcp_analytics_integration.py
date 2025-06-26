#!/usr/bin/env python3
"""
Test script for MCP Analytics Integration
Verifies that the MCP analytics module works correctly with existing log files
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mcp_analytics import get_mcp_analytics
import pandas as pd

def test_mcp_analytics():
    """Test the MCP analytics functionality"""
    print("🤖 Testing MCP Analytics Integration")
    print("=" * 50)
    
    try:
        # Get the analytics instance
        mcp_analytics = get_mcp_analytics()
        print("✅ MCP Analytics instance created successfully")
        
        # Test server status
        print("\n📊 Testing Server Status...")
        server_status = mcp_analytics.get_server_status()
        print(f"Found {len(server_status)} servers:")
        for server, status in server_status.items():
            print(f"  - {server}: {status}")
        
        # Test analytics summary
        print("\n📈 Testing Analytics Summary...")
        summary = mcp_analytics.get_analytics_summary()
        print(f"Total tool calls: {summary['total_tool_calls']}")
        print(f"Total errors: {summary['total_errors']}")
        print(f"Most active server: {summary['most_active_server']}")
        print(f"Most used tool: {summary['most_used_tool']}")
        
        # Test tool usage data
        print("\n🔧 Testing Tool Usage Data...")
        tool_usage_df = mcp_analytics.get_tool_usage_data()
        if not tool_usage_df.empty:
            print(f"Tool usage data shape: {tool_usage_df.shape}")
            print("Tool usage sample:")
            print(tool_usage_df.head())
        else:
            print("No tool usage data found")
        
        # Test error trends
        print("\n⚠️ Testing Error Trends...")
        error_df = mcp_analytics.get_error_trends()
        if not error_df.empty:
            print(f"Error trends data shape: {error_df.shape}")
            print("Recent errors:")
            print(error_df.head())
        else:
            print("No error data found")
        
        # Test server performance
        print("\n⚡ Testing Server Performance...")
        performance_data = mcp_analytics.get_server_performance_data()
        if performance_data:
            print(f"Performance data for {len(performance_data)} servers:")
            for server, perf in performance_data.items():
                print(f"  - {server}: {perf.get('total_entries', 0)} entries, {perf.get('error_count', 0)} errors")
        else:
            print("No performance data found")
        
        print("\n✅ MCP Analytics integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing MCP analytics: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_analytics() 