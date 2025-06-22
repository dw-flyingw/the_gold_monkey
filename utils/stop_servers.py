#!/usr/bin/env python3
"""
Stop all servers for Salty
"""

import subprocess
import psutil
import os

def stop_servers():
    """Stop all server processes"""
    print("🛑 Stopping all servers for Salty...")
    
    # Define server names for better feedback
    server_names = {
        'tplink_server.py': 'TP-Link',
        'rag_server.py': 'RAG', 
        'spotify_server.py': 'Spotify',
        'roku_server.py': 'Roku',
        'saltybot_server.py': 'SaltyBot',
        'voice_server.py': 'Voice'
    }
    
    stopped_count = 0
    
    # Look for Python processes running servers
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python' and proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                for server_file, server_name in server_names.items():
                    if server_file in cmdline:
                        print(f"Stopping {server_name} server (PID: {proc.info['pid']})")
                        proc.terminate()
                        try:
                            proc.wait(timeout=5)
                            print(f"✅ {server_name} server stopped gracefully")
                            stopped_count += 1
                        except psutil.TimeoutExpired:
                            proc.kill()
                            print(f"⚠️ {server_name} server force killed")
                            stopped_count += 1
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if stopped_count == 0:
        print("ℹ️ No running servers found")
    else:
        print(f"👋 Stopped {stopped_count} servers!")

if __name__ == "__main__":
    stop_servers() 