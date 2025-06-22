#!/usr/bin/env python3
"""
Debug Roku Connection
Comprehensive debugging script to test Roku connection and IP discovery
"""

import os
import socket
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_roku_connection():
    """Debug Roku connection step by step"""
    print("🦜 Salty's Roku Debug Tool")
    print("=" * 50)
    
    # Step 1: Check environment variables
    print("1️⃣ Checking environment variables...")
    roku_host = os.getenv('ROKU_HOST')
    if roku_host:
        print(f"   ✅ ROKU_HOST found: {roku_host}")
    else:
        print("   ❌ ROKU_HOST not found in .env file")
        return False
    
    # Step 2: DNS resolution
    print("\n2️⃣ Testing DNS resolution...")
    try:
        ip_address = socket.gethostbyname(roku_host)
        print(f"   ✅ DNS resolution successful: {roku_host} → {ip_address}")
    except socket.gaierror as e:
        print(f"   ❌ DNS resolution failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
    
    # Step 3: Network connectivity
    print("\n3️⃣ Testing network connectivity...")
    try:
        # Try ping (simulated with socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip_address, 8060))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Port 8060 is reachable on {ip_address}")
        else:
            print(f"   ❌ Port 8060 is not reachable on {ip_address}")
            print(f"   💡 Error code: {result}")
            return False
    except Exception as e:
        print(f"   ❌ Network test failed: {e}")
        return False
    
    # Step 4: HTTP connection test
    print("\n4️⃣ Testing HTTP connection...")
    roku_base_url = f"http://{ip_address}:8060"
    print(f"   🔗 Testing: {roku_base_url}")
    
    try:
        # Test device info endpoint
        response = requests.get(f"{roku_base_url}/query/device-info", timeout=5)
        print(f"   📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ HTTP connection successful!")
            
            # Parse and display device info
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                
                device_name = root.find('user-device-name')
                model_name = root.find('model-name')
                model_number = root.find('model-number')
                serial_number = root.find('serial-number')
                
                print("\n   📺 Device Information:")
                print(f"      • Name: {device_name.text if device_name is not None else 'Unknown'}")
                print(f"      • Model: {model_name.text if model_name is not None else 'Unknown'}")
                print(f"      • Model Number: {model_number.text if model_number is not None else 'Unknown'}")
                print(f"      • Serial: {serial_number.text if serial_number is not None else 'Unknown'}")
                print(f"      • IP Address: {ip_address}")
                
            except Exception as e:
                print(f"   ⚠️ Could not parse device info: {e}")
            
            return True
            
        elif response.status_code == 403:
            print("   ❌ 403 Forbidden - Developer Mode likely not enabled")
            print("   💡 Enable Developer Mode on your Roku device:")
            print("      Settings → System → Advanced system settings → Developer options")
            return False
            
        elif response.status_code == 404:
            print("   ❌ 404 Not Found - Roku API endpoint not available")
            print("   💡 This might not be a Roku device or it doesn't support the REST API")
            return False
            
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection error: {e}")
        print("   💡 Device might be powered off or not connected to network")
        return False
        
    except requests.exceptions.Timeout as e:
        print(f"   ❌ Timeout error: {e}")
        print("   💡 Device is not responding")
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_roku_commands():
    """Test basic Roku commands"""
    print("\n5️⃣ Testing Roku commands...")
    
    roku_host = os.getenv('ROKU_HOST')
    if not roku_host:
        return False
    
    try:
        ip_address = socket.gethostbyname(roku_host)
        roku_base_url = f"http://{ip_address}:8060"
        
        # Test a simple command
        response = requests.post(f"{roku_base_url}/keypress/Home", timeout=5)
        print(f"   📊 Home command status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Home command successful!")
            return True
        else:
            print(f"   ❌ Home command failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Command test failed: {e}")
        return False

def main():
    if debug_roku_connection():
        print("\n🎉 Roku connection is working!")
        
        # Test commands
        if test_roku_commands():
            print("🎉 Roku commands are working!")
            print("\n✅ Your Roku is fully configured and ready!")
            print("💡 You can now use the Roku Control panel in the Streamlit app")
        else:
            print("\n⚠️ Connection works but commands failed")
            print("💡 This might be a Developer Mode issue")
    else:
        print("\n❌ Roku connection failed!")
        print("\n🔧 Troubleshooting summary:")
        print("1. Check if Roku device is powered on")
        print("2. Ensure it's connected to the same network")
        print("3. Enable Developer Mode: Settings → System → Advanced → Developer options")
        print("4. Verify ROKU_HOST in .env file is correct")
        print("5. Try restarting the Roku device")

if __name__ == "__main__":
    main() 