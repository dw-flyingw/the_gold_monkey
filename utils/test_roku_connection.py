#!/usr/bin/env python3
"""
Test Roku Connection
Simple script to test if the Roku device is reachable and responding
"""

import os
import requests
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_roku_connection():
    """Test the Roku connection"""
    roku_host = os.getenv('ROKU_HOST')
    
    if not roku_host:
        print("❌ ROKU_HOST not set in .env file")
        return False
    
    print(f"🔍 Testing connection to Roku at: {roku_host}")
    
    # Test 1: DNS resolution
    try:
        ip_address = socket.gethostbyname(roku_host)
        print(f"✅ DNS resolution successful: {roku_host} -> {ip_address}")
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False
    
    # Test 2: HTTP connection
    roku_base_url = f"http://{roku_host}:8060"
    print(f"🔗 Testing HTTP connection to: {roku_base_url}")
    
    try:
        # Test basic connectivity
        response = requests.get(f"{roku_base_url}/query/device-info", timeout=5)
        if response.status_code == 200:
            print("✅ HTTP connection successful!")
            
            # Parse device info
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                device_name = root.find('user-device-name')
                model_name = root.find('model-name')
                model_number = root.find('model-number')
                
                print(f"📺 Device Name: {device_name.text if device_name is not None else 'Unknown'}")
                print(f"📺 Model: {model_name.text if model_name is not None else 'Unknown'}")
                print(f"📺 Model Number: {model_number.text if model_number is not None else 'Unknown'}")
                
            except Exception as e:
                print(f"⚠️ Could not parse device info: {e}")
            
            return True
        else:
            print(f"❌ HTTP request failed with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - Roku device not reachable")
        print("💡 Make sure:")
        print("   - Roku device is powered on")
        print("   - Roku device is connected to the same network")
        print("   - ROKU_HOST is correct in .env file")
        return False
    except requests.exceptions.Timeout:
        print("❌ Connection timeout - Roku device not responding")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_roku_apps():
    """Test getting list of apps"""
    roku_host = os.getenv('ROKU_HOST')
    if not roku_host:
        return False
    
    roku_base_url = f"http://{roku_host}:8060"
    
    try:
        response = requests.get(f"{roku_base_url}/query/apps", timeout=5)
        if response.status_code == 200:
            print("✅ Apps query successful!")
            
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                apps = root.findall('app')
                
                print(f"📱 Found {len(apps)} apps:")
                for app in apps[:10]:  # Show first 10 apps
                    print(f"   • {app.text}")
                
                if len(apps) > 10:
                    print(f"   ... and {len(apps) - 10} more")
                    
            except Exception as e:
                print(f"⚠️ Could not parse apps: {e}")
            
            return True
        else:
            print(f"❌ Apps query failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Apps query error: {e}")
        return False

def main():
    print("🦜 Salty's Roku Connection Tester")
    print("=" * 40)
    
    # Test basic connection
    if test_roku_connection():
        print("\n🎉 Roku connection successful!")
        
        # Test apps
        print("\n📱 Testing apps query...")
        test_roku_apps()
        
        print("\n✅ Your Roku is ready to be controlled by Salty!")
        print("💡 You can now use the Roku Control panel in the Streamlit app")
        
    else:
        print("\n❌ Roku connection failed!")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure your Roku device is powered on")
        print("2. Ensure it's connected to the same network as this computer")
        print("3. Check that ROKU_HOST in .env file is correct")
        print("4. Try using the IP address instead of hostname")
        print("5. Make sure Roku's developer mode is enabled (if needed)")

if __name__ == "__main__":
    main() 