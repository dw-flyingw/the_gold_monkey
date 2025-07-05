#!/usr/bin/env python3
"""
Test persistent routines integration with main app
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.routine_storage import get_routine_storage

def test_persistent_routines():
    """Test that persistent routines work with the main app"""
    print("🧪 Testing Persistent Routines Integration...")
    
    # Get the routine storage instance
    routine_storage = get_routine_storage()
    
    # Test 1: Load custom routines
    print("\n1. Loading custom routines...")
    routines = routine_storage.load_custom_routines()
    print(f"   Loaded {len(routines)} custom routines")
    
    for routine in routines:
        print(f"   • {routine['name']} - {routine['description']}")
        print(f"     Steps: {len(routine['steps'])}")
        print(f"     Created: {routine['created']}")
        print(f"     Last Run: {routine.get('last_run', 'Never')}")
    
    # Test 2: Load routine history
    print("\n2. Loading routine history...")
    history = routine_storage.load_routine_history()
    print(f"   Loaded {len(history)} history entries")
    
    # Test 3: Get statistics
    print("\n3. Getting routine statistics...")
    stats = routine_storage.get_routine_stats()
    print(f"   Total custom routines: {stats.get('total_custom_routines', 0)}")
    print(f"   Total executions: {stats.get('total_executions', 0)}")
    print(f"   Success rate: {stats.get('success_rate', 0)}%")
    print(f"   Most used routine: {stats.get('most_used_routine', 'None')}")
    
    # Test 4: Simulate routine execution
    print("\n4. Simulating routine execution...")
    if routines:
        test_routine = routines[0]
        print(f"   Testing routine: {test_routine['name']}")
        
        # Simulate execution
        execution = {
            'routine_name': test_routine['name'],
            'timestamp': '2024-01-15 21:00:00',
            'status': 'completed',
            'duration': 4.5,
            'notes': 'Test execution from integration test'
        }
        
        success = routine_storage.add_routine_execution(execution)
        print(f"   Execution logged: {'✅' if success else '❌'}")
        
        # Update last run time
        test_routine['last_run'] = '2024-01-15 21:00:00'
        success = routine_storage.update_custom_routine(test_routine['name'], test_routine)
        print(f"   Last run updated: {'✅' if success else '❌'}")
    
    # Test 5: Create a backup
    print("\n5. Creating backup...")
    backup_file = routine_storage.backup_routines("integration_test")
    print(f"   Backup created: {'✅' if backup_file else '❌'}")
    if backup_file:
        print(f"   Backup file: {backup_file}")
    
    print("\n🎉 Persistent routines integration test completed!")
    print("\nThe routines are now ready to use in The Gold Monkey app:")
    print("1. Go to the Routines section")
    print("2. Check the Custom Routines tab to see your saved routines")
    print("3. Use the Storage & Backup tab to manage backups")
    print("4. View execution history in the Routine History tab")

if __name__ == "__main__":
    test_persistent_routines() 