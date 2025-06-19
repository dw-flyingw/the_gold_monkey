#!/usr/bin/env python3
"""
Stop all MCP servers for Salty
"""

import subprocess
import psutil
import os

def stop_mcp_servers():
    """Stop all MCP server processes"""
    print("🛑 Stopping all MCP servers...")
    
    # Look for Python processes running MCP servers
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python' and proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if any(server in cmdline for server in ['tplink_server.py', 'rag_server.py', 'spotify_server.py', 'roku_server.py', 'saltybot_server.py']):
                    print(f"Stopping process {proc.info['pid']} ({cmdline})")
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                        print(f"✅ Process {proc.info['pid']} stopped gracefully")
                    except psutil.TimeoutExpired:
                        proc.kill()
                        print(f"⚠️ Process {proc.info['pid']} force killed")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print("👋 All MCP servers stopped!")

if __name__ == "__main__":
    stop_mcp_servers() 