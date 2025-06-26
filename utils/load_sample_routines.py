#!/usr/bin/env python3
"""
Load sample routines into persistent storage
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.routine_storage import get_routine_storage

def load_sample_routines():
    """Load sample routines from JSON file into persistent storage"""
    print("📦 Loading sample routines...")
    
    # Get the routine storage instance
    routine_storage = get_routine_storage()
    
    # Load sample routines from file
    sample_file = "routines/sample_routines.json"
    
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_routines = json.load(f)
        
        print(f"Found {len(sample_routines)} sample routines")
        
        # Add each sample routine to persistent storage
        for routine in sample_routines:
            success = routine_storage.add_custom_routine(routine)
            if success:
                print(f"✅ Loaded: {routine['name']}")
            else:
                print(f"❌ Failed to load: {routine['name']}")
        
        # Verify the routines were loaded
        loaded_routines = routine_storage.load_custom_routines()
        print(f"\n📊 Total routines in storage: {len(loaded_routines)}")
        
        print("\n🎉 Sample routines loaded successfully!")
        print("\nYou can now access these routines in The Gold Monkey app:")
        for routine in loaded_routines:
            print(f"  • {routine['name']} - {routine['description']}")
            
    except FileNotFoundError:
        print(f"❌ Sample routines file not found: {sample_file}")
    except Exception as e:
        print(f"❌ Error loading sample routines: {e}")

if __name__ == "__main__":
    load_sample_routines() 