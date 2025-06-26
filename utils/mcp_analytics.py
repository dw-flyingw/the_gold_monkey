#!/usr/bin/env python3
"""
MCP Server Analytics for The Gold Monkey
Tracks and analyzes MCP server usage patterns
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class MCPAnalytics:
    """Analytics tracker for MCP servers"""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.servers = {
            "tplink": "tplink_server.log",
            "spotify": "spotify_server.log", 
            "roku": "roku_server.log",
            "rag": "rag_server.log",
            "voice": "voice_server.log",
            "saltybot": "saltybot_server.log"
        }
        
        # Initialize analytics data structure
        self.analytics_data = {
            "server_usage": {},
            "tool_calls": {},
            "errors": {},
            "performance": {},
            "daily_stats": {},
            "hourly_stats": {}
        }
    
    def parse_log_file(self, log_file: Path) -> List[Dict[str, Any]]:
        """Parse a log file and extract structured data"""
        entries = []
        
        if not log_file.exists():
            return entries
        
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    entry = self._parse_log_line(line.strip())
                    if entry:
                        entries.append(entry)
        except Exception as e:
            logger.error(f"Error parsing log file {log_file}: {e}")
        
        return entries
    
    def _parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single log line"""
        if not line:
            return None
        
        # Common log patterns
        patterns = [
            # Standard timestamp format: 2024-01-01 12:00:00,000 - INFO - message
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3} - (\w+) - (.+)',
            # Alternative format: 2024-01-01 12:00:00 - INFO - message
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.+)',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                timestamp_str, level, message = match.groups()
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    return {
                        'timestamp': timestamp,
                        'level': level,
                        'message': message,
                        'raw_line': line
                    }
                except ValueError:
                    continue
        
        return None
    
    def extract_tool_calls(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract tool call information from log entries"""
        tool_calls = []
        
        for entry in entries:
            message = entry.get('message', '')
            
            # Look for tool call patterns
            tool_patterns = [
                r'Calling tool: (\w+)',
                r'Tool call: (\w+)',
                r'Executing tool: (\w+)',
                r'handle_call_tool.*name: (\w+)'
            ]
            
            for pattern in tool_patterns:
                match = re.search(pattern, message)
                if match:
                    tool_name = match.group(1)
                    tool_calls.append({
                        'timestamp': entry['timestamp'],
                        'tool_name': tool_name,
                        'level': entry['level'],
                        'message': message
                    })
                    break
        
        return tool_calls
    
    def extract_errors(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract error information from log entries"""
        errors = []
        
        for entry in entries:
            if entry.get('level') in ['ERROR', 'CRITICAL']:
                errors.append({
                    'timestamp': entry['timestamp'],
                    'level': entry['level'],
                    'message': entry['message'],
                    'raw_line': entry['raw_line']
                })
        
        return errors
    
    def analyze_server_performance(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze server performance metrics"""
        if not entries:
            return {}
        
        # Calculate basic metrics
        total_entries = len(entries)
        error_count = len([e for e in entries if e.get('level') in ['ERROR', 'CRITICAL']])
        warning_count = len([e for e in entries if e.get('level') == 'WARNING'])
        
        # Calculate uptime (entries per hour)
        if len(entries) > 1:
            time_span = entries[-1]['timestamp'] - entries[0]['timestamp']
            hours_span = time_span.total_seconds() / 3600
            entries_per_hour = total_entries / hours_span if hours_span > 0 else 0
        else:
            entries_per_hour = 0
        
        return {
            'total_entries': total_entries,
            'error_count': error_count,
            'warning_count': warning_count,
            'error_rate': (error_count / total_entries * 100) if total_entries > 0 else 0,
            'entries_per_hour': entries_per_hour,
            'first_entry': entries[0]['timestamp'] if entries else None,
            'last_entry': entries[-1]['timestamp'] if entries else None
        }
    
    def generate_daily_stats(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate daily statistics"""
        if not entries:
            return {}
        
        daily_stats = {}
        
        for entry in entries:
            date_str = entry['timestamp'].strftime('%Y-%m-%d')
            if date_str not in daily_stats:
                daily_stats[date_str] = {
                    'total_entries': 0,
                    'errors': 0,
                    'warnings': 0,
                    'info': 0,
                    'tool_calls': 0
                }
            
            daily_stats[date_str]['total_entries'] += 1
            
            if entry['level'] == 'ERROR':
                daily_stats[date_str]['errors'] += 1
            elif entry['level'] == 'WARNING':
                daily_stats[date_str]['warnings'] += 1
            elif entry['level'] == 'INFO':
                daily_stats[date_str]['info'] += 1
            
            # Count tool calls
            if 'Calling tool:' in entry['message'] or 'Tool call:' in entry['message']:
                daily_stats[date_str]['tool_calls'] += 1
        
        return daily_stats
    
    def generate_hourly_stats(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate hourly statistics"""
        if not entries:
            return {}
        
        hourly_stats = {}
        
        for entry in entries:
            hour_str = entry['timestamp'].strftime('%Y-%m-%d %H:00')
            if hour_str not in hourly_stats:
                hourly_stats[hour_str] = {
                    'total_entries': 0,
                    'errors': 0,
                    'tool_calls': 0
                }
            
            hourly_stats[hour_str]['total_entries'] += 1
            
            if entry['level'] == 'ERROR':
                hourly_stats[hour_str]['errors'] += 1
            
            if 'Calling tool:' in entry['message'] or 'Tool call:' in entry['message']:
                hourly_stats[hour_str]['tool_calls'] += 1
        
        return hourly_stats
    
    def get_server_status(self) -> Dict[str, str]:
        """Get current status of all MCP servers"""
        status = {}
        
        for server_name, log_file in self.servers.items():
            log_path = self.logs_dir / log_file
            
            if not log_path.exists():
                status[server_name] = "🔴 Offline"
                continue
            
            # Check if log file has been updated recently (within last 5 minutes)
            try:
                mtime = datetime.fromtimestamp(log_path.stat().st_mtime)
                time_diff = datetime.now() - mtime
                
                if time_diff < timedelta(minutes=5):
                    status[server_name] = "🟢 Online"
                elif time_diff < timedelta(hours=1):
                    status[server_name] = "🟡 Idle"
                else:
                    status[server_name] = "🔴 Offline"
            except Exception:
                status[server_name] = "🔴 Unknown"
        
        return status
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        summary = {
            'server_status': self.get_server_status(),
            'total_tool_calls': 0,
            'total_errors': 0,
            'most_active_server': None,
            'most_used_tool': None,
            'recent_activity': {}
        }
        
        all_tool_calls = []
        all_errors = []
        server_activity = {}
        
        # Analyze each server
        for server_name, log_file in self.servers.items():
            log_path = self.logs_dir / log_file
            entries = self.parse_log_file(log_path)
            
            if entries:
                # Extract tool calls and errors
                tool_calls = self.extract_tool_calls(entries)
                errors = self.extract_errors(entries)
                
                all_tool_calls.extend(tool_calls)
                all_errors.extend(errors)
                server_activity[server_name] = len(tool_calls)
                
                # Get recent activity (last 24 hours)
                recent_entries = [
                    e for e in entries 
                    if e['timestamp'] > datetime.now() - timedelta(hours=24)
                ]
                summary['recent_activity'][server_name] = len(recent_entries)
        
        # Calculate summary statistics
        summary['total_tool_calls'] = len(all_tool_calls)
        summary['total_errors'] = len(all_errors)
        
        if server_activity:
            summary['most_active_server'] = max(server_activity, key=server_activity.get)
        
        # Find most used tool
        tool_counts = {}
        for call in all_tool_calls:
            tool_name = call['tool_name']
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        
        if tool_counts:
            summary['most_used_tool'] = max(tool_counts, key=tool_counts.get)
        
        return summary
    
    def get_tool_usage_data(self) -> pd.DataFrame:
        """Get tool usage data as a DataFrame"""
        all_tool_calls = []
        
        for server_name, log_file in self.servers.items():
            log_path = self.logs_dir / log_file
            entries = self.parse_log_file(log_path)
            tool_calls = self.extract_tool_calls(entries)
            
            for call in tool_calls:
                all_tool_calls.append({
                    'server': server_name,
                    'tool': call['tool_name'],
                    'timestamp': call['timestamp'],
                    'date': call['timestamp'].date(),
                    'hour': call['timestamp'].hour
                })
        
        if all_tool_calls:
            return pd.DataFrame(all_tool_calls)
        else:
            return pd.DataFrame(columns=['server', 'tool', 'timestamp', 'date', 'hour'])
    
    def get_error_trends(self) -> pd.DataFrame:
        """Get error trends data as a DataFrame"""
        all_errors = []
        
        for server_name, log_file in self.servers.items():
            log_path = self.logs_dir / log_file
            entries = self.parse_log_file(log_path)
            errors = self.extract_errors(entries)
            
            for error in errors:
                all_errors.append({
                    'server': server_name,
                    'timestamp': error['timestamp'],
                    'date': error['timestamp'].date(),
                    'level': error['level'],
                    'message': error['message'][:100] + '...' if len(error['message']) > 100 else error['message']
                })
        
        if all_errors:
            return pd.DataFrame(all_errors)
        else:
            return pd.DataFrame(columns=['server', 'timestamp', 'date', 'level', 'message'])
    
    def get_server_performance_data(self) -> Dict[str, Dict[str, Any]]:
        """Get performance data for all servers"""
        performance_data = {}
        
        for server_name, log_file in self.servers.items():
            log_path = self.logs_dir / log_file
            entries = self.parse_log_file(log_path)
            
            if entries:
                performance_data[server_name] = self.analyze_server_performance(entries)
                performance_data[server_name]['daily_stats'] = self.generate_daily_stats(entries)
                performance_data[server_name]['hourly_stats'] = self.generate_hourly_stats(entries)
        
        return performance_data

# Global analytics instance
mcp_analytics = MCPAnalytics()

def get_mcp_analytics() -> MCPAnalytics:
    """Get the global MCP analytics instance"""
    return mcp_analytics 