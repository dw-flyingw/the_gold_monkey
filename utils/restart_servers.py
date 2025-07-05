#!/usr/bin/env python3
"""
Restart all MCP servers for Salty
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
from utils.shared import SERVERS

def main():
    """Restart all servers"""
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        print("🔄 Restarting all servers for Salty...")
        subprocess.run(["python", "utils/stop_servers.py", "all"])
        subprocess.run(["python", "utils/start_servers.py", "all"])
        print("✅ All servers restarted.")
    elif len(sys.argv) > 1:
        server_to_restart = sys.argv[1]
        if server_to_restart in SERVERS:
            print(f"🔄 Restarting {server_to_restart} server...")
            subprocess.run(["python", "utils/stop_servers.py", server_to_restart])
            subprocess.run(["python", "utils/start_servers.py", server_to_restart])
            print(f"✅ {server_to_restart} server restarted.")
        else:
            print(f"❌ Unknown server: {server_to_restart}")
    else:
        print("Please specify a server to restart or 'all' to restart all servers.")

if __name__ == "__main__":
    main()