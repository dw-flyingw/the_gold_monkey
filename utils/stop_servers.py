#!/usr/bin/env python3
"""
Stop all servers for Salty
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
import psutil
from pathlib import Path
from utils.shared import SERVERS

def stop_server(server_name):
    """Stop a single server"""
    pid_file = Path(f".pids/{server_name}.pid")
    if not pid_file.exists():
        print(f"ℹ️ {server_name} server is not running.")
        return

    try:
        pid = int(pid_file.read_text())
        if psutil.pid_exists(pid):
            print(f"Stopping {server_name} server (PID: {pid})...")
            proc = psutil.Process(pid)
            proc.terminate()
            try:
                proc.wait(timeout=5)
                print(f"✅ {server_name} server stopped gracefully.")
            except psutil.TimeoutExpired:
                proc.kill()
                print(f"⚠️ {server_name} server force-killed.")
        else:
            print(f"ℹ️ Stale PID file for {server_name}. Cleaning up.")
        
        pid_file.unlink()
    except (ValueError, FileNotFoundError) as e:
        print(f"❌ Error stopping {server_name}: {e}")

def main():
    """Stop all servers"""
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        print("🛑 Stopping all servers for Salty...")
        for server_name in SERVERS:
            stop_server(server_name)
        print("👋 All servers have been stopped.")
    elif len(sys.argv) > 1:
        server_to_stop = sys.argv[1]
        if server_to_stop in SERVERS:
            stop_server(server_to_stop)
        else:
            print(f"❌ Unknown server: {server_to_stop}")
    else:
        print("Please specify a server to stop or 'all' to stop all servers.")

if __name__ == "__main__":
    main()