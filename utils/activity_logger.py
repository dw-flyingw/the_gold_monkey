import json
import os
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, Any, List
import logging

class ActivityLogger:
    """Logs user activities for metrics tracking"""
    
    def __init__(self):
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        self.activity_file = self.logs_dir / "activity_log.json"
        self._load_activities()
    
    def _load_activities(self):
        """Load existing activities from file"""
        if self.activity_file.exists():
            try:
                with open(self.activity_file, 'r') as f:
                    self.activities = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.activities = []
        else:
            self.activities = []
    
    def _save_activities(self):
        """Save activities to file"""
        with open(self.activity_file, 'w') as f:
            json.dump(self.activities, f, indent=2, default=str)
    
    def log_activity(self, activity_type: str, details: Dict[str, Any] = None):
        """Log a user activity"""
        activity = {
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "type": activity_type,
            "details": details or {}
        }
        
        self.activities.append(activity)
        self._save_activities()
        
        # Also log to standard logging
        logging.info(f"Activity logged: {activity_type} - {details}")
    
    def get_today_activities(self) -> List[Dict]:
        """Get all activities for today"""
        today = date.today().isoformat()
        return [activity for activity in self.activities 
                if activity.get('date') == today]
    
    def get_activities_by_type(self, activity_type: str, days: int = 1) -> List[Dict]:
        """Get activities of a specific type for the last N days"""
        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        return [activity for activity in self.activities 
                if activity.get('type') == activity_type 
                and activity.get('date') >= cutoff_date]
    
    def get_hourly_stats(self, activity_type: str, target_date: str = None) -> Dict[int, int]:
        """Get hourly statistics for a specific activity type"""
        if target_date is None:
            target_date = date.today().isoformat()
        
        hourly_stats = {hour: 0 for hour in range(24)}
        
        for activity in self.activities:
            if (activity.get('type') == activity_type and 
                activity.get('date') == target_date):
                try:
                    timestamp = datetime.fromisoformat(activity['timestamp'])
                    hour = timestamp.hour
                    hourly_stats[hour] += 1
                except (ValueError, KeyError):
                    continue
        
        return hourly_stats
    
    def get_daily_summary(self, target_date: str = None) -> Dict[str, int]:
        """Get daily summary of all activity types"""
        if target_date is None:
            target_date = date.today().isoformat()
        
        summary = {}
        for activity in self.activities:
            if activity.get('date') == target_date:
                activity_type = activity.get('type', 'unknown')
                summary[activity_type] = summary.get(activity_type, 0) + 1
        
        return summary
    
    def get_popular_actions(self, days: int = 7) -> Dict[str, int]:
        """Get most popular actions over the last N days"""
        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        action_counts = {}
        for activity in self.activities:
            if activity.get('date') >= cutoff_date:
                activity_type = activity.get('type', 'unknown')
                action_counts[activity_type] = action_counts.get(activity_type, 0) + 1
        
        return dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True))

# Global activity logger instance
activity_logger = ActivityLogger()

def log_chat_message(user_message: str = None):
    """Log a chat interaction with Salty"""
    activity_logger.log_activity("chat_message", {
        "message_length": len(user_message) if user_message else 0,
        "has_message": bool(user_message)
    })

def log_light_change(device: str, action: str, brightness: int = None):
    """Log a smart light control action"""
    activity_logger.log_activity("light_change", {
        "device": device,
        "action": action,
        "brightness": brightness
    })

def log_music_play(track: str = None, playlist: str = None, action: str = "play"):
    """Log a music playback action"""
    activity_logger.log_activity("music_play", {
        "track": track,
        "playlist": playlist,
        "action": action
    })

def log_voice_command(command: str):
    """Log a voice command"""
    activity_logger.log_activity("voice_command", {
        "command": command,
        "command_length": len(command)
    })

def log_system_error(error_type: str, error_message: str):
    """Log a system error"""
    activity_logger.log_activity("system_error", {
        "error_type": error_type,
        "error_message": error_message
    })

def log_routine_execution(routine_name: str, status: str):
    """Log a routine execution"""
    activity_logger.log_activity("routine_execution", {
        "routine_name": routine_name,
        "status": status
    })

def log_roku_action(action: str, app: str = None):
    """Log a Roku control action"""
    activity_logger.log_activity("roku_action", {
        "action": action,
        "app": app
    }) 