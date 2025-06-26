#!/usr/bin/env python3
"""
Routine Storage Utility for The Gold Monkey
Handles persistent storage of custom routines and execution history
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import re

logger = logging.getLogger(__name__)

class RoutineStorage:
    """Handles persistent storage of routines and execution history"""
    
    def __init__(self, routines_dir: str = "routines"):
        self.routines_dir = Path(routines_dir)
        self.routines_dir.mkdir(exist_ok=True)
        
        # Directory structure
        self.custom_routines_dir = self.routines_dir / "custom_routines"
        self.custom_routines_dir.mkdir(exist_ok=True)
        
        # File paths
        self.routine_history_file = self.routines_dir / "routine_history.json"
        
        logger.info(f"Routine storage initialized at: {self.routines_dir}")
    
    def _sanitize_filename(self, name: str) -> str:
        """Convert routine name to safe filename"""
        # Remove special characters and replace spaces with underscores
        safe_name = re.sub(r'[^\w\s-]', '', name)
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        return safe_name.lower()
    
    def _get_routine_filename(self, routine_name: str) -> str:
        """Get filename for a routine"""
        safe_name = self._sanitize_filename(routine_name)
        return f"{safe_name}.json"
    
    def _get_routine_filepath(self, routine_name: str) -> Path:
        """Get full filepath for a routine"""
        filename = self._get_routine_filename(routine_name)
        return self.custom_routines_dir / filename
    
    def save_custom_routines(self, routines: List[Dict[str, Any]]) -> bool:
        """Save custom routines to individual files"""
        try:
            # Clear existing routines
            for file in self.custom_routines_dir.glob("*.json"):
                file.unlink()
            
            # Save each routine to its own file
            for routine in routines:
                routine_name = routine.get('name', 'unnamed_routine')
                filepath = self._get_routine_filepath(routine_name)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(routine, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(routines)} custom routines to individual files")
            return True
        except Exception as e:
            logger.error(f"Error saving custom routines: {e}")
            return False
    
    def load_custom_routines(self) -> List[Dict[str, Any]]:
        """Load custom routines from individual files"""
        try:
            routines = []
            for filepath in self.custom_routines_dir.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        routine = json.load(f)
                    routines.append(routine)
                except Exception as e:
                    logger.error(f"Error loading routine from {filepath}: {e}")
                    continue
            
            # Sort by creation time
            routines.sort(key=lambda x: x.get('created', ''))
            
            logger.info(f"Loaded {len(routines)} custom routines from individual files")
            return routines
        except Exception as e:
            logger.error(f"Error loading custom routines: {e}")
            return []
    
    def save_routine_history(self, history: List[Dict[str, Any]]) -> bool:
        """Save routine execution history to JSON file"""
        try:
            # Keep only the last 100 entries to prevent file from growing too large
            if len(history) > 100:
                history = history[-100:]
            
            with open(self.routine_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(history)} routine history entries")
            return True
        except Exception as e:
            logger.error(f"Error saving routine history: {e}")
            return False
    
    def load_routine_history(self) -> List[Dict[str, Any]]:
        """Load routine execution history from JSON file"""
        try:
            if self.routine_history_file.exists():
                with open(self.routine_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                logger.info(f"Loaded {len(history)} routine history entries")
                return history
            else:
                logger.info("No routine history file found, starting with empty list")
                return []
        except Exception as e:
            logger.error(f"Error loading routine history: {e}")
            return []
    
    def add_custom_routine(self, routine: Dict[str, Any]) -> bool:
        """Add a single custom routine and save to file"""
        try:
            routine_name = routine.get('name', 'unnamed_routine')
            filepath = self._get_routine_filepath(routine_name)
            
            # Check if routine with same name already exists
            if filepath.exists():
                logger.warning(f"Routine '{routine_name}' already exists, overwriting")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(routine, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Added custom routine: {routine_name}")
            return True
        except Exception as e:
            logger.error(f"Error adding custom routine: {e}")
            return False
    
    def update_custom_routine(self, routine_name: str, routine: Dict[str, Any]) -> bool:
        """Update a custom routine by name"""
        try:
            filepath = self._get_routine_filepath(routine_name)
            if filepath.exists():
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(routine, f, indent=2, ensure_ascii=False)
                logger.info(f"Updated custom routine: {routine_name}")
                return True
            else:
                logger.error(f"Routine not found: {routine_name}")
                return False
        except Exception as e:
            logger.error(f"Error updating custom routine: {e}")
            return False
    
    def delete_custom_routine(self, routine_name: str) -> bool:
        """Delete a custom routine by name"""
        try:
            filepath = self._get_routine_filepath(routine_name)
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted routine: {routine_name}")
                return True
            else:
                logger.error(f"Routine not found: {routine_name}")
                return False
        except Exception as e:
            logger.error(f"Error deleting custom routine: {e}")
            return False
    
    def get_custom_routine(self, routine_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific custom routine by name"""
        try:
            filepath = self._get_routine_filepath(routine_name)
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    routine = json.load(f)
                return routine
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting custom routine: {e}")
            return None
    
    def routine_exists(self, routine_name: str) -> bool:
        """Check if a routine exists"""
        filepath = self._get_routine_filepath(routine_name)
        return filepath.exists()
    
    def add_routine_execution(self, execution: Dict[str, Any]) -> bool:
        """Add a routine execution to history and save to file"""
        try:
            history = self.load_routine_history()
            history.append(execution)
            return self.save_routine_history(history)
        except Exception as e:
            logger.error(f"Error adding routine execution: {e}")
            return False
    
    def get_routine_stats(self) -> Dict[str, Any]:
        """Get statistics about stored routines"""
        try:
            routines = self.load_custom_routines()
            history = self.load_routine_history()
            
            # Calculate stats
            total_routines = len(routines)
            total_executions = len(history)
            
            # Most used routines
            routine_usage = {}
            for execution in history:
                routine_name = execution.get('routine_name', 'Unknown')
                routine_usage[routine_name] = routine_usage.get(routine_name, 0) + 1
            
            most_used = max(routine_usage.items(), key=lambda x: x[1]) if routine_usage else None
            
            # Success rate
            successful_executions = sum(1 for e in history if e.get('status') == 'completed')
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            
            # File sizes
            total_size = sum(f.stat().st_size for f in self.custom_routines_dir.glob("*.json"))
            
            return {
                'total_custom_routines': total_routines,
                'total_executions': total_executions,
                'success_rate': round(success_rate, 1),
                'most_used_routine': most_used[0] if most_used else None,
                'most_used_count': most_used[1] if most_used else 0,
                'recent_executions': history[-10:] if history else [],
                'total_storage_size': total_size,
                'routine_files': [f.name for f in self.custom_routines_dir.glob("*.json")]
            }
        except Exception as e:
            logger.error(f"Error getting routine stats: {e}")
            return {}
    
    def backup_routines(self, backup_name: str = None) -> str:
        """Create a backup of all routine data"""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_dir = self.routines_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Collect all routine files
            routine_files = {}
            for filepath in self.custom_routines_dir.glob("*.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    routine_files[filepath.name] = json.load(f)
            
            backup_data = {
                'custom_routines': routine_files,
                'routine_history': self.load_routine_history(),
                'backup_timestamp': datetime.now().isoformat(),
                'backup_name': backup_name
            }
            
            backup_file = backup_dir / f"{backup_name}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created routine backup: {backup_file}")
            return str(backup_file)
        except Exception as e:
            logger.error(f"Error creating routine backup: {e}")
            return ""
    
    def restore_routines(self, backup_file: str) -> bool:
        """Restore routines from a backup file"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Clear existing routines
            for file in self.custom_routines_dir.glob("*.json"):
                file.unlink()
            
            # Restore custom routines
            if 'custom_routines' in backup_data:
                for filename, routine_data in backup_data['custom_routines'].items():
                    filepath = self.custom_routines_dir / filename
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(routine_data, f, indent=2, ensure_ascii=False)
            
            # Restore routine history
            if 'routine_history' in backup_data:
                self.save_routine_history(backup_data['routine_history'])
            
            logger.info(f"Restored routines from backup: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Error restoring routines: {e}")
            return False
    
    def list_routine_files(self) -> List[str]:
        """List all routine files"""
        return [f.name for f in self.custom_routines_dir.glob("*.json")]

# Global routine storage instance
routine_storage = RoutineStorage()

def get_routine_storage() -> RoutineStorage:
    """Get the global routine storage instance"""
    return routine_storage 