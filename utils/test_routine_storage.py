#!/usr/bin/env python3
"""
Test script for persistent routine storage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.routine_storage import RoutineStorage
from datetime import datetime

def test_routine_storage():
    """Test the routine storage functionality"""
    print("🧪 Testing Routine Storage...")
    
    # Create a test storage instance
    storage = RoutineStorage("test_routines")
    
    # Test 1: Save and load custom routines
    print("\n1. Testing custom routines...")
    
    test_routines = [
        {
            'name': 'Test Morning Routine',
            'description': 'A test morning routine',
            'steps': [
                {'type': 'Light Control', 'action': 'Turn On'},
                {'type': 'Voice Command', 'action': 'Good morning!'}
            ],
            'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_run': None
        },
        {
            'name': 'Test Evening Routine',
            'description': 'A test evening routine',
            'steps': [
                {'type': 'Light Control', 'action': 'Set Color: Orange'},
                {'type': 'Music Control', 'action': 'Play'}
            ],
            'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_run': None
        }
    ]
    
    # Save routines
    success = storage.save_custom_routines(test_routines)
    print(f"   Save routines: {'✅' if success else '❌'}")
    
    # Load routines
    loaded_routines = storage.load_custom_routines()
    print(f"   Load routines: {'✅' if len(loaded_routines) == 2 else '❌'}")
    print(f"   Loaded {len(loaded_routines)} routines")
    
    # Test 2: Save and load routine history
    print("\n2. Testing routine history...")
    
    test_history = [
        {
            'routine_name': 'Test Morning Routine',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'completed',
            'duration': 5.2,
            'notes': 'Test execution'
        },
        {
            'routine_name': 'Test Evening Routine',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'failed',
            'duration': 2.1,
            'notes': 'Test failure'
        }
    ]
    
    # Save history
    success = storage.save_routine_history(test_history)
    print(f"   Save history: {'✅' if success else '❌'}")
    
    # Load history
    loaded_history = storage.load_routine_history()
    print(f"   Load history: {'✅' if len(loaded_history) == 2 else '❌'}")
    print(f"   Loaded {len(loaded_history)} history entries")
    
    # Test 3: Individual routine operations
    print("\n3. Testing individual operations...")
    
    # Add a new routine
    new_routine = {
        'name': 'Test Party Routine',
        'description': 'A test party routine',
        'steps': [
            {'type': 'Light Control', 'action': 'Set Color: Purple'},
            {'type': 'Music Control', 'action': 'Play'}
        ],
        'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'last_run': None
    }
    
    success = storage.add_custom_routine(new_routine)
    print(f"   Add routine: {'✅' if success else '❌'}")
    
    # Update a routine
    if loaded_routines:
        updated_routine = loaded_routines[0].copy()
        updated_routine['last_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        success = storage.update_custom_routine(updated_routine['name'], updated_routine)
        print(f"   Update routine: {'✅' if success else '❌'}")
    
    # Test getting a specific routine
    if loaded_routines:
        routine_name = loaded_routines[0]['name']
        specific_routine = storage.get_custom_routine(routine_name)
        print(f"   Get specific routine: {'✅' if specific_routine else '❌'}")
    
    # Test routine existence check
    if loaded_routines:
        routine_name = loaded_routines[0]['name']
        exists = storage.routine_exists(routine_name)
        print(f"   Routine exists check: {'✅' if exists else '❌'}")
    
    # Add execution to history
    execution = {
        'routine_name': 'Test Party Routine',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': 'completed',
        'duration': 3.5,
        'notes': 'Test execution added'
    }
    success = storage.add_routine_execution(execution)
    print(f"   Add execution: {'✅' if success else '❌'}")
    
    # Test 4: Statistics
    print("\n4. Testing statistics...")
    
    stats = storage.get_routine_stats()
    print(f"   Total custom routines: {stats.get('total_custom_routines', 0)}")
    print(f"   Total executions: {stats.get('total_executions', 0)}")
    print(f"   Success rate: {stats.get('success_rate', 0)}%")
    print(f"   Most used routine: {stats.get('most_used_routine', 'None')}")
    print(f"   Total storage size: {stats.get('total_storage_size', 0)} bytes")
    print(f"   Routine files: {len(stats.get('routine_files', []))}")
    
    # Test 5: List routine files
    print("\n5. Testing file listing...")
    files = storage.list_routine_files()
    print(f"   Routine files: {len(files)}")
    for filename in files:
        print(f"     • {filename}")
    
    # Test 6: Backup and restore
    print("\n6. Testing backup and restore...")
    
    backup_file = storage.backup_routines("test_backup")
    print(f"   Create backup: {'✅' if backup_file else '❌'}")
    if backup_file:
        print(f"   Backup file: {backup_file}")
    
    # Test 7: Cleanup
    print("\n7. Cleaning up test files...")
    
    import shutil
    try:
        shutil.rmtree("test_routines")
        print("   Cleanup: ✅")
    except Exception as e:
        print(f"   Cleanup: ❌ ({e})")
    
    print("\n🎉 Routine storage test completed!")

if __name__ == "__main__":
    test_routine_storage() 