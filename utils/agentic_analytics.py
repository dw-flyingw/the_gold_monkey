#!/usr/bin/env python3
"""
Agentic Analytics System
Tracks agentic behavior, tool usage, and learning patterns
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

class GoalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ToolCategory(Enum):
    MEDIA = "media"
    LIGHTING = "lighting"
    INFORMATION = "information"
    VOICE = "voice"
    AUTOMATION = "automation"
    ENTERTAINMENT = "entertainment"

@dataclass
class GoalExecution:
    goal_id: str
    goal_type: str
    description: str
    priority: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: GoalStatus = GoalStatus.PENDING
    tools_used: List[str] = None
    success_rate: float = 0.0
    execution_time: float = 0.0
    reasoning: Dict[str, Any] = None
    user_feedback: Optional[str] = None

@dataclass
class ToolExecution:
    tool_name: str
    category: ToolCategory
    executed_at: datetime
    execution_time: float
    success: bool
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    error_message: Optional[str] = None
    goal_id: Optional[str] = None

@dataclass
class UserInteraction:
    session_id: str
    user_input: str
    agent_response: str
    timestamp: datetime
    reasoning: Dict[str, Any]
    goals_created: int
    tools_executed: int
    successful_actions: int
    failed_actions: int
    user_satisfaction: Optional[float] = None

@dataclass
class LearningPattern:
    pattern_id: str
    pattern_type: str
    description: str
    discovered_at: datetime
    confidence: float
    usage_count: int
    success_rate: float
    tools_involved: List[str]
    user_preferences: Dict[str, Any]

class AgenticAnalytics:
    """Comprehensive analytics for agentic behavior"""
    
    def __init__(self, data_dir: str = "data/agentic_analytics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data storage
        self.goals: List[GoalExecution] = []
        self.tool_executions: List[ToolExecution] = []
        self.user_interactions: List[UserInteraction] = []
        self.learning_patterns: List[LearningPattern] = []
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load existing analytics data"""
        try:
            # Load goals
            goals_file = self.data_dir / "goals.json"
            if goals_file.exists():
                with open(goals_file, 'r') as f:
                    goals_data = json.load(f)
                    self.goals = [GoalExecution(**g) for g in goals_data]
            
            # Load tool executions
            tools_file = self.data_dir / "tool_executions.json"
            if tools_file.exists():
                with open(tools_file, 'r') as f:
                    tools_data = json.load(f)
                    self.tool_executions = [ToolExecution(**t) for t in tools_data]
            
            # Load user interactions
            interactions_file = self.data_dir / "user_interactions.json"
            if interactions_file.exists():
                with open(interactions_file, 'r') as f:
                    interactions_data = json.load(f)
                    self.user_interactions = [UserInteraction(**i) for i in interactions_data]
            
            # Load learning patterns
            patterns_file = self.data_dir / "learning_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns_data = json.load(f)
                    self.learning_patterns = [LearningPattern(**p) for p in patterns_data]
                    
        except Exception as e:
            logger.error(f"Error loading analytics data: {e}")
    
    def _save_data(self):
        """Save analytics data"""
        try:
            # Save goals
            with open(self.data_dir / "goals.json", 'w') as f:
                json.dump([asdict(g) for g in self.goals], f, indent=2, default=str)
            
            # Save tool executions
            with open(self.data_dir / "tool_executions.json", 'w') as f:
                json.dump([asdict(t) for t in self.tool_executions], f, indent=2, default=str)
            
            # Save user interactions
            with open(self.data_dir / "user_interactions.json", 'w') as f:
                json.dump([asdict(i) for i in self.user_interactions], f, indent=2, default=str)
            
            # Save learning patterns
            with open(self.data_dir / "learning_patterns.json", 'w') as f:
                json.dump([asdict(p) for p in self.learning_patterns], f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")
    
    def record_goal_creation(self, goal: GoalExecution):
        """Record a new goal"""
        self.goals.append(goal)
        self._save_data()
    
    def record_goal_completion(self, goal_id: str, status: GoalStatus, execution_time: float = 0.0):
        """Record goal completion"""
        for goal in self.goals:
            if goal.goal_id == goal_id:
                goal.status = status
                goal.completed_at = datetime.now()
                goal.execution_time = execution_time
                break
        self._save_data()
    
    def record_tool_execution(self, execution: ToolExecution):
        """Record a tool execution"""
        self.tool_executions.append(execution)
        self._save_data()
    
    def record_user_interaction(self, interaction: UserInteraction):
        """Record a user interaction"""
        self.user_interactions.append(interaction)
        self._save_data()
    
    def record_learning_pattern(self, pattern: LearningPattern):
        """Record a discovered learning pattern"""
        self.learning_patterns.append(pattern)
        self._save_data()
    
    def get_goal_statistics(self, time_period: str = "all") -> Dict[str, Any]:
        """Get goal execution statistics"""
        if time_period == "all":
            goals = self.goals
        else:
            cutoff = datetime.now() - timedelta(days=int(time_period))
            goals = [g for g in self.goals if g.created_at >= cutoff]
        
        if not goals:
            return {}
        
        total_goals = len(goals)
        completed_goals = len([g for g in goals if g.status == GoalStatus.COMPLETED])
        failed_goals = len([g for g in goals if g.status == GoalStatus.FAILED])
        
        avg_execution_time = sum(g.execution_time for g in goals if g.execution_time > 0) / len([g for g in goals if g.execution_time > 0]) if any(g.execution_time > 0 for g in goals) else 0
        
        return {
            "total_goals": total_goals,
            "completed_goals": completed_goals,
            "failed_goals": failed_goals,
            "success_rate": completed_goals / total_goals if total_goals > 0 else 0,
            "avg_execution_time": avg_execution_time,
            "goals_by_type": self._count_by_type(goals, lambda g: g.goal_type),
            "goals_by_priority": self._count_by_type(goals, lambda g: str(g.priority))
        }
    
    def get_tool_statistics(self, time_period: str = "all") -> Dict[str, Any]:
        """Get tool execution statistics"""
        if time_period == "all":
            executions = self.tool_executions
        else:
            cutoff = datetime.now() - timedelta(days=int(time_period))
            executions = [e for e in self.tool_executions if e.executed_at >= cutoff]
        
        if not executions:
            return {}
        
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.success])
        
        avg_execution_time = sum(e.execution_time for e in executions) / total_executions
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "avg_execution_time": avg_execution_time,
            "tools_by_category": self._count_by_type(executions, lambda e: e.category.value),
            "most_used_tools": self._get_most_used(executions, lambda e: e.tool_name, 10),
            "most_successful_tools": self._get_most_successful_tools(executions, 10)
        }
    
    def get_user_interaction_statistics(self, time_period: str = "all") -> Dict[str, Any]:
        """Get user interaction statistics"""
        if time_period == "all":
            interactions = self.user_interactions
        else:
            cutoff = datetime.now() - timedelta(days=int(time_period))
            interactions = [i for i in self.user_interactions if i.timestamp >= cutoff]
        
        if not interactions:
            return {}
        
        total_interactions = len(interactions)
        avg_satisfaction = sum(i.user_satisfaction for i in interactions if i.user_satisfaction is not None) / len([i for i in interactions if i.user_satisfaction is not None]) if any(i.user_satisfaction is not None for i in interactions) else 0
        
        return {
            "total_interactions": total_interactions,
            "avg_satisfaction": avg_satisfaction,
            "avg_goals_per_interaction": sum(i.goals_created for i in interactions) / total_interactions if total_interactions > 0 else 0,
            "avg_tools_per_interaction": sum(i.tools_executed for i in interactions) / total_interactions if total_interactions > 0 else 0,
            "successful_actions_rate": sum(i.successful_actions for i in interactions) / sum(i.tools_executed for i in interactions) if sum(i.tools_executed for i in interactions) > 0 else 0
        }
    
    def get_learning_patterns(self) -> List[Dict[str, Any]]:
        """Get discovered learning patterns"""
        return [
            {
                "pattern_id": p.pattern_id,
                "pattern_type": p.pattern_type,
                "description": p.description,
                "confidence": p.confidence,
                "usage_count": p.usage_count,
                "success_rate": p.success_rate,
                "tools_involved": p.tools_involved
            }
            for p in sorted(self.learning_patterns, key=lambda x: x.confidence, reverse=True)
        ]
    
    def _count_by_type(self, items: List, key_func) -> Dict[str, int]:
        """Count items by a key function"""
        counts = {}
        for item in items:
            key = key_func(item)
            counts[key] = counts.get(key, 0) + 1
        return counts
    
    def _get_most_used(self, items: List, key_func, limit: int = 10) -> List[tuple]:
        """Get most used items"""
        counts = {}
        for item in items:
            key = key_func(item)
            counts[key] = counts.get(key, 0) + 1
        
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def _get_most_successful_tools(self, executions: List[ToolExecution], limit: int = 10) -> List[Dict[str, Any]]:
        """Get most successful tools"""
        tool_stats = {}
        
        for execution in executions:
            tool_name = execution.tool_name
            if tool_name not in tool_stats:
                tool_stats[tool_name] = {"total": 0, "successful": 0, "avg_time": 0}
            
            tool_stats[tool_name]["total"] += 1
            if execution.success:
                tool_stats[tool_name]["successful"] += 1
        
        # Calculate success rates
        for tool_name, stats in tool_stats.items():
            stats["success_rate"] = stats["successful"] / stats["total"] if stats["total"] > 0 else 0
        
        # Sort by success rate
        sorted_tools = sorted(tool_stats.items(), key=lambda x: x[1]["success_rate"], reverse=True)
        
        return [
            {
                "tool_name": tool_name,
                "success_rate": stats["success_rate"],
                "total_executions": stats["total"],
                "successful_executions": stats["successful"]
            }
            for tool_name, stats in sorted_tools[:limit]
        ]
    
    def generate_analytics_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive analytics dashboard"""
        return {
            "goals": self.get_goal_statistics(),
            "tools": self.get_tool_statistics(),
            "interactions": self.get_user_interaction_statistics(),
            "learning_patterns": self.get_learning_patterns(),
            "recent_activity": self._get_recent_activity(),
            "performance_metrics": self._get_performance_metrics()
        }
    
    def _get_recent_activity(self) -> Dict[str, Any]:
        """Get recent activity summary"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        recent_goals = [g for g in self.goals if g.created_at >= last_24h]
        recent_tools = [t for t in self.tool_executions if t.executed_at >= last_24h]
        recent_interactions = [i for i in self.user_interactions if i.timestamp >= last_24h]
        
        return {
            "goals_created_24h": len(recent_goals),
            "tools_executed_24h": len(recent_tools),
            "interactions_24h": len(recent_interactions),
            "recent_goals": [
                {
                    "goal_id": g.goal_id,
                    "description": g.description,
                    "status": g.status.value,
                    "created_at": g.created_at.isoformat()
                }
                for g in sorted(recent_goals, key=lambda x: x.created_at, reverse=True)[:5]
            ],
            "recent_tools": [
                {
                    "tool_name": t.tool_name,
                    "success": t.success,
                    "execution_time": t.execution_time,
                    "executed_at": t.executed_at.isoformat()
                }
                for t in sorted(recent_tools, key=lambda x: x.executed_at, reverse=True)[:10]
            ]
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        # Calculate agentic efficiency
        total_goals = len(self.goals)
        successful_goals = len([g for g in self.goals if g.status == GoalStatus.COMPLETED])
        
        total_tools = len(self.tool_executions)
        successful_tools = len([t for t in self.tool_executions if t.success])
        
        avg_goals_per_interaction = sum(i.goals_created for i in self.user_interactions) / len(self.user_interactions) if self.user_interactions else 0
        
        return {
            "goal_success_rate": successful_goals / total_goals if total_goals > 0 else 0,
            "tool_success_rate": successful_tools / total_tools if total_tools > 0 else 0,
            "avg_goals_per_interaction": avg_goals_per_interaction,
            "total_learning_patterns": len(self.learning_patterns),
            "avg_pattern_confidence": sum(p.confidence for p in self.learning_patterns) / len(self.learning_patterns) if self.learning_patterns else 0
        }

# Global analytics instance
analytics = AgenticAnalytics()

def record_goal_creation(goal: GoalExecution):
    """Record a new goal"""
    analytics.record_goal_creation(goal)

def record_goal_completion(goal_id: str, status: GoalStatus, execution_time: float = 0.0):
    """Record goal completion"""
    analytics.record_goal_completion(goal_id, status, execution_time)

def record_tool_execution(execution: ToolExecution):
    """Record a tool execution"""
    analytics.record_tool_execution(execution)

def record_user_interaction(interaction: UserInteraction):
    """Record a user interaction"""
    analytics.record_user_interaction(interaction)

def record_learning_pattern(pattern: LearningPattern):
    """Record a learning pattern"""
    analytics.record_learning_pattern(pattern)

def get_analytics_dashboard() -> Dict[str, Any]:
    """Get analytics dashboard"""
    return analytics.generate_analytics_dashboard()

async def main():
    """Test the analytics system"""
    print("📊 Testing Agentic Analytics System...")
    
    # Create some test data
    test_goal = GoalExecution(
        goal_id="test_goal_1",
        goal_type="entertainment",
        description="Play tropical music",
        priority=3,
        created_at=datetime.now()
    )
    
    test_tool = ToolExecution(
        tool_name="spotify_play",
        category=ToolCategory.MEDIA,
        executed_at=datetime.now(),
        execution_time=1.5,
        success=True,
        parameters={"volume": 50},
        result={"status": "playing"}
    )
    
    test_interaction = UserInteraction(
        session_id="test_session_1",
        user_input="Play some tropical music",
        agent_response="🦜 Aye aye, matey! Playing tropical tunes for you!",
        timestamp=datetime.now(),
        reasoning={"primary_intent": "entertainment", "confidence": 0.9},
        goals_created=1,
        tools_executed=1,
        successful_actions=1,
        failed_actions=0
    )
    
    # Record test data
    record_goal_creation(test_goal)
    record_tool_execution(test_tool)
    record_user_interaction(test_interaction)
    
    # Generate dashboard
    dashboard = get_analytics_dashboard()
    print("📈 Analytics Dashboard:")
    print(json.dumps(dashboard, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main()) 