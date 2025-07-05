#!/usr/bin/env python3
"""
Start all MCP servers for Salty
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
from pathlib import Path
from dotenv import load_dotenv
from utils.shared import SERVERS
import multiprocessing

load_dotenv()

def run_server(server_name, server_info):
    """Start a single server"""
    pid_file = Path(f".pids/{server_name}.pid")
    if pid_file.exists():
        print(f"ℹ️ {server_name} server is already running.")
        return

    try:
        print(f"Starting {server_name} server...")
        env = os.environ.copy()
        script_path = server_info["path"]
        server_type = server_info["type"]

        if server_type == "mcp":
            command = ["uv", "run", "mcp", "run", script_path]
        else:
            command = ["python3", script_path]

        process = subprocess.Popen(
            command,
            env=env,
            start_new_session=True,
        )
        
        with open(pid_file, "w") as f:
            f.write(str(process.pid))
        
        print(f"✅ {server_name} server started (PID: {process.pid})")
    except Exception as e:
        print(f"❌ Error starting {server_name}: {e}")

def main():
    """Start all servers"""
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        print("🚀 Starting all servers for Salty...")
        processes = []
        for server_name, server_info in SERVERS.items():
            p = multiprocessing.Process(target=run_server, args=(server_name, server_info))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        print("🎉 All servers have been started.")
    elif len(sys.argv) > 1:
        server_to_start = sys.argv[1]
        if server_to_start in SERVERS:
            run_server(server_to_start, SERVERS[server_to_start])
        else:
            print(f"❌ Unknown server: {server_to_start}")
    else:
        print("Please specify a server to start or 'all' to start all servers.")

if __name__ == "__main__":
    main()
