#!/usr/bin/env python3
"""
Migration script to convert from single-file routine storage to individual files
"""

import sys
import os
import json
import shutil
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.routine_storage import RoutineStorage

def migrate_routine_storage():
    """Migrate from single-file storage to individual file storage"""
    print("🔄 Migrating Routine Storage to Individual Files...")
    
    routines_dir = Path("routines")
    old_custom_routines_file = routines_dir / "custom_routines.json"
    
    # Check if old file exists
    if not old_custom_routines_file.exists():
        print("✅ No migration needed - individual file storage already in use")
        return
    
    # Create backup of old file
    backup_file = routines_dir / f"custom_routines_backup_{Path(__file__).stem}.json"
    shutil.copy2(old_custom_routines_file, backup_file)
    print(f"📦 Created backup: {backup_file}")
    
    # Load old routines
    try:
        with open(old_custom_routines_file, 'r', encoding='utf-8') as f:
            old_routines = json.load(f)
        print(f"📖 Loaded {len(old_routines)} routines from old storage")
    except Exception as e:
        print(f"❌ Error loading old routines: {e}")
        return
    
    # Get new storage instance
    routine_storage = RoutineStorage()
    
    # Migrate each routine to individual file
    migrated_count = 0
    for routine in old_routines:
        routine_name = routine.get('name', 'unnamed_routine')
        try:
            success = routine_storage.add_custom_routine(routine)
            if success:
                print(f"✅ Migrated: {routine_name}")
                migrated_count += 1
            else:
                print(f"❌ Failed to migrate: {routine_name}")
        except Exception as e:
            print(f"❌ Error migrating {routine_name}: {e}")
    
    # Verify migration
    new_routines = routine_storage.load_custom_routines()
    print(f"\n📊 Migration Results:")
    print(f"   Routines migrated: {migrated_count}/{len(old_routines)}")
    print(f"   Routines in new storage: {len(new_routines)}")
    
    if migrated_count == len(old_routines):
        # Remove old file
        try:
            old_custom_routines_file.unlink()
            print(f"🗑️ Removed old file: {old_custom_routines_file}")
        except Exception as e:
            print(f"⚠️ Warning: Could not remove old file: {e}")
        
        print("\n🎉 Migration completed successfully!")
        print(f"📁 New structure:")
        print(f"   {routine_storage.custom_routines_dir}/")
        for filename in routine_storage.list_routine_files():
            print(f"     • {filename}")
    else:
        print("\n⚠️ Migration incomplete - check for errors above")
        print("Old file preserved for manual review")

def verify_migration():
    """Verify that migration was successful"""
    print("\n🔍 Verifying Migration...")
    
    routine_storage = RoutineStorage()
    routines = routine_storage.load_custom_routines()
    
    print(f"📊 Verification Results:")
    print(f"   Routines loaded: {len(routines)}")
    
    for routine in routines:
        routine_name = routine.get('name', 'Unknown')
        filepath = routine_storage._get_routine_filepath(routine_name)
        exists = filepath.exists()
        print(f"   • {routine_name}: {'✅' if exists else '❌'} ({filepath.name})")
    
    # Check file structure
    custom_routines_dir = routine_storage.custom_routines_dir
    if custom_routines_dir.exists():
        files = list(custom_routines_dir.glob("*.json"))
        print(f"   Individual files: {len(files)}")
    else:
        print("   ❌ Custom routines directory not found")

if __name__ == "__main__":
    migrate_routine_storage()
    verify_migration() 