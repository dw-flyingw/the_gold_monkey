#!/usr/bin/env python3
"""
Find Roku devices on the network
"""

import socket
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor

def scan_ip(ip):
    """Scan a single IP for Roku device"""
    try:
        # Try to connect to Roku's control port
        url = f"http://{ip}:8060/query/device-info"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return ip, True
    except:
        pass
    return ip, False

def find_roku_devices():
    """Find Roku devices on the local network"""
    print("🦜 Salty's Roku Device Finder")
    print("=" * 40)
    
    # Get local IP to determine network range
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Extract network prefix (e.g., 192.168.1 from 192.168.1.100)
        network_prefix = '.'.join(local_ip.split('.')[:-1])
        print(f"🔍 Scanning network: {network_prefix}.0/24")
        
    except Exception as e:
        print(f"❌ Could not determine local IP: {e}")
        return
    
    # Scan common network ranges
    potential_networks = [
        f"{network_prefix}.0/24",  # Same network as this computer
        "192.168.1.0/24",          # Common home network
        "192.168.0.0/24",          # Common home network
        "10.0.0.0/24",             # Common home network
    ]
    
    found_devices = []
    
    for network in potential_networks:
        print(f"\n🔍 Scanning {network}...")
        
        # Generate IP range
        base_ip = network.split('/')[0]
        base_parts = base_ip.split('.')
        
        # Scan IPs in parallel
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i in range(1, 255):
                ip = f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{i}"
                futures.append(executor.submit(scan_ip, ip))
            
            # Check results
            for future in futures:
                ip, is_roku = future.result()
                if is_roku:
                    found_devices.append(ip)
                    print(f"✅ Found Roku device at: {ip}")
    
    if found_devices:
        print(f"\n🎉 Found {len(found_devices)} Roku device(s)!")
        print("\n📝 Update your .env file with one of these IPs:")
        for ip in found_devices:
            print(f"   ROKU_HOST=\"{ip}\"")
        
        print("\n💡 Try the first one first, then restart your Streamlit app!")
    else:
        print("\n❌ No Roku devices found!")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure your Roku device is powered on")
        print("2. Ensure it's connected to the same network as this computer")
        print("3. Try enabling Developer Mode on your Roku device")
        print("4. Check if your Roku device supports the REST API")

if __name__ == "__main__":
    find_roku_devices() 