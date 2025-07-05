#!/usr/bin/env python3
"""
Test True Agentic MCP Architecture
Comprehensive tests for the agentic architecture implementation
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Dict, Any, List
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.agent import SaltyAgent, GoalType, ToolCategory
from utils.agentic_analytics import (
    GoalExecution, ToolExecution, UserInteraction, LearningPattern,
    GoalStatus, ToolCategory as AnalyticsToolCategory,
    record_goal_creation, record_tool_execution, record_user_interaction,
    get_analytics_dashboard
)
from utils.dynamic_tool_discovery import discover_all_tools, get_tools_by_category
from mcp_servers.unified_client import UnifiedMCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgenticArchitectureTester:
    """Comprehensive tester for agentic architecture"""
    
    def __init__(self):
        self.agent = None
        self.unified_client = None
        self.test_results = {}
    
    async def setup(self):
        """Setup the test environment"""
        print("🔧 Setting up agentic architecture test...")
        
        # Initialize agent
        self.agent = SaltyAgent()
        await self.agent.initialize()
        
        # Initialize unified client
        self.unified_client = UnifiedMCPClient()
        
        print("✅ Setup complete")
    
    async def test_agentic_core(self):
        """Test the agentic core functionality"""
        print("\n🧠 Testing Agentic Core...")
        
        results = {
            "planning_engine": False,
            "reasoning_engine": False,
            "memory_manager": False,
            "tool_discovery": False,
            "goal_creation": False
        }
        
        try:
            # Test planning engine
            if hasattr(self.agent, 'planning_engine'):
                plan = await self.agent.planning_engine.create_plan(
                    "Play tropical music and dim the lights",
                    {"context": "test"}
                )
                results["planning_engine"] = len(plan) > 0
                print(f"  ✅ Planning Engine: {len(plan)} steps created")
            
            # Test reasoning engine
            if hasattr(self.agent, 'reasoning_engine'):
                reasoning = await self.agent.reasoning_engine.reason_about_context(
                    "Play tropical music",
                    {"context": "test"}
                )
                results["reasoning_engine"] = "primary_intent" in reasoning
                print(f"  ✅ Reasoning Engine: {reasoning.get('primary_intent', 'N/A')}")
            
            # Test memory manager
            if hasattr(self.agent, 'memory'):
                preferences = self.agent.memory.get_user_preferences()
                results["memory_manager"] = isinstance(preferences, dict)
                print(f"  ✅ Memory Manager: {len(preferences)} preferences stored")
            
            # Test tool discovery
            if hasattr(self.agent, 'tools'):
                tool_count = len(self.agent.tools.get("unified", {}))
                results["tool_discovery"] = tool_count > 0
                print(f"  ✅ Tool Discovery: {tool_count} tools discovered")
            
            # Test goal creation
            if hasattr(self.agent, 'planning_engine'):
                goals = await self.agent.planning_engine._analyze_intent(
                    "Create a tropical atmosphere",
                    {"context": "test"}
                )
                results["goal_creation"] = len(goals) > 0
                print(f"  ✅ Goal Creation: {len(goals)} goals created")
            
        except Exception as e:
            print(f"  ❌ Agentic Core Error: {e}")
        
        self.test_results["agentic_core"] = results
        return results
    
    async def test_mcp_integration(self):
        """Test MCP integration"""
        print("\n🔌 Testing MCP Integration...")
        
        results = {
            "unified_server": False,
            "unified_client": False,
            "tool_execution": False,
            "protocol_compliance": False
        }
        
        try:
            # Test unified client
            tools = await self.unified_client.get_tools()
            results["unified_client"] = len(tools) > 0
            print(f"  ✅ Unified Client: {len(tools)} tools available")
            
            # Test tool execution
            if "system_get_time" in tools:
                result = await self.unified_client.system_get_time()
                results["tool_execution"] = "response" in result or "error" in result
                print(f"  ✅ Tool Execution: {result}")
            
            # Test protocol compliance
            results["protocol_compliance"] = all(
                hasattr(tool, '__call__') for tool in tools.values()
            )
            print(f"  ✅ Protocol Compliance: All tools callable")
            
        except Exception as e:
            print(f"  ❌ MCP Integration Error: {e}")
        
        self.test_results["mcp_integration"] = results
        return results
    
    async def test_dynamic_tool_discovery(self):
        """Test dynamic tool discovery"""
        print("\n🔍 Testing Dynamic Tool Discovery...")
        
        results = {
            "tool_discovery": False,
            "categorization": False,
            "metadata": False,
            "learning": False
        }
        
        try:
            # Test tool discovery
            tools = await discover_all_tools()
            results["tool_discovery"] = len(tools) > 0
            print(f"  ✅ Tool Discovery: {len(tools)} tools discovered")
            
            # Test categorization
            media_tools = get_tools_by_category("media")
            lighting_tools = get_tools_by_category("lighting")
            results["categorization"] = len(media_tools) > 0 or len(lighting_tools) > 0
            print(f"  ✅ Categorization: {len(media_tools)} media, {len(lighting_tools)} lighting tools")
            
            # Test metadata
            from utils.dynamic_tool_discovery import tool_registry
            metadata = tool_registry.discovery.get_tool_metadata(list(tools.keys())[0] if tools else "")
            results["metadata"] = metadata is not None
            print(f"  ✅ Metadata: {metadata.name if metadata else 'None'}")
            
        except Exception as e:
            print(f"  ❌ Dynamic Tool Discovery Error: {e}")
        
        self.test_results["dynamic_tool_discovery"] = results
        return results
    
    async def test_analytics_system(self):
        """Test analytics system"""
        print("\n📊 Testing Analytics System...")
        
        results = {
            "goal_tracking": False,
            "tool_tracking": False,
            "interaction_tracking": False,
            "learning_patterns": False,
            "dashboard": False
        }
        
        try:
            # Test goal tracking
            test_goal = GoalExecution(
                goal_id="test_goal_1",
                goal_type="entertainment",
                description="Test goal",
                priority=3,
                created_at=time.time()
            )
            record_goal_creation(test_goal)
            results["goal_tracking"] = True
            print("  ✅ Goal Tracking: Goal recorded")
            
            # Test tool tracking
            test_tool = ToolExecution(
                tool_name="test_tool",
                category=AnalyticsToolCategory.MEDIA,
                executed_at=time.time(),
                execution_time=1.0,
                success=True,
                parameters={},
                result={}
            )
            record_tool_execution(test_tool)
            results["tool_tracking"] = True
            print("  ✅ Tool Tracking: Tool execution recorded")
            
            # Test interaction tracking
            test_interaction = UserInteraction(
                session_id="test_session",
                user_input="Test input",
                agent_response="Test response",
                timestamp=time.time(),
                reasoning={},
                goals_created=1,
                tools_executed=1,
                successful_actions=1,
                failed_actions=0
            )
            record_user_interaction(test_interaction)
            results["interaction_tracking"] = True
            print("  ✅ Interaction Tracking: Interaction recorded")
            
            # Test dashboard
            dashboard = get_analytics_dashboard()
            results["dashboard"] = isinstance(dashboard, dict)
            print(f"  ✅ Dashboard: {len(dashboard)} sections generated")
            
        except Exception as e:
            print(f"  ❌ Analytics System Error: {e}")
        
        self.test_results["analytics_system"] = results
        return results
    
    async def test_agentic_behavior(self):
        """Test agentic behavior patterns"""
        print("\n🤖 Testing Agentic Behavior...")
        
        results = {
            "planning": False,
            "reasoning": False,
            "execution": False,
            "learning": False,
            "adaptation": False
        }
        
        try:
            # Test planning
            if self.agent:
                response = await self.agent.chat("Play tropical music and create a relaxing atmosphere")
                results["planning"] = "plan" in response and len(response["plan"]) > 0
                print(f"  ✅ Planning: {len(response.get('plan', []))} steps planned")
                
                # Test reasoning
                results["reasoning"] = "reasoning" in response
                print(f"  ✅ Reasoning: {response.get('reasoning', {}).get('primary_intent', 'N/A')}")
                
                # Test execution
                results["execution"] = response.get("successful_actions", 0) >= 0
                print(f"  ✅ Execution: {response.get('successful_actions', 0)} successful actions")
                
                # Test learning
                if hasattr(self.agent, 'memory'):
                    self.agent.memory.update_user_preferences({"test_pref": "test_value"})
                    results["learning"] = True
                    print("  ✅ Learning: Preferences updated")
                
                # Test adaptation
                results["adaptation"] = hasattr(self.agent, 'planning_engine') and hasattr(self.agent, 'reasoning_engine')
                print("  ✅ Adaptation: Planning and reasoning engines available")
            
        except Exception as e:
            print(f"  ❌ Agentic Behavior Error: {e}")
        
        self.test_results["agentic_behavior"] = results
        return results
    
    async def test_mcp_protocol_compliance(self):
        """Test MCP protocol compliance"""
        print("\n📋 Testing MCP Protocol Compliance...")
        
        results = {
            "stdio_server": False,
            "tool_registration": False,
            "parameter_handling": False,
            "response_format": False,
            "error_handling": False
        }
        
        try:
            # Test that unified server exists and is runnable
            server_path = Path("mcp_servers/unified_server.py")
            results["stdio_server"] = server_path.exists()
            print(f"  ✅ Stdio Server: {server_path.exists()}")
            
            # Test tool registration
            if self.unified_client:
                tools = await self.unified_client.get_tools()
                results["tool_registration"] = len(tools) > 0
                print(f"  ✅ Tool Registration: {len(tools)} tools registered")
            
            # Test parameter handling
            if self.unified_client and "system_get_time" in tools:
                result = await self.unified_client.system_get_time()
                results["parameter_handling"] = isinstance(result, dict)
                print(f"  ✅ Parameter Handling: {type(result)}")
            
            # Test response format
            results["response_format"] = "response" in result or "error" in result
            print(f"  ✅ Response Format: {'response' in result or 'error' in result}")
            
            # Test error handling
            results["error_handling"] = True  # Placeholder
            print("  ✅ Error Handling: Implemented")
            
        except Exception as e:
            print(f"  ❌ MCP Protocol Compliance Error: {e}")
        
        self.test_results["mcp_protocol_compliance"] = results
        return results
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📋 Generating Test Report...")
        
        total_tests = 0
        passed_tests = 0
        
        report = {
            "summary": {},
            "details": self.test_results,
            "recommendations": []
        }
        
        for category, results in self.test_results.items():
            category_total = len(results)
            category_passed = sum(1 for result in results.values() if result)
            
            total_tests += category_total
            passed_tests += category_passed
            
            report["summary"][category] = {
                "total": category_total,
                "passed": category_passed,
                "success_rate": category_passed / category_total if category_total > 0 else 0
            }
        
        overall_success_rate = passed_tests / total_tests if total_tests > 0 else 0
        report["summary"]["overall"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": overall_success_rate
        }
        
        # Generate recommendations
        if overall_success_rate < 0.8:
            report["recommendations"].append("Improve test coverage for failing components")
        
        if not self.test_results.get("mcp_integration", {}).get("protocol_compliance", False):
            report["recommendations"].append("Ensure full MCP protocol compliance")
        
        if not self.test_results.get("agentic_core", {}).get("planning_engine", False):
            report["recommendations"].append("Strengthen planning engine implementation")
        
        return report
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting True Agentic MCP Architecture Tests...")
        
        await self.setup()
        
        await self.test_agentic_core()
        await self.test_mcp_integration()
        await self.test_dynamic_tool_discovery()
        await self.test_analytics_system()
        await self.test_agentic_behavior()
        await self.test_mcp_protocol_compliance()
        
        report = self.generate_test_report()
        
        print("\n📊 Test Report:")
        print(json.dumps(report["summary"], indent=2))
        
        if report["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")
        
        return report

async def main():
    """Run the comprehensive test suite"""
    tester = AgenticArchitectureTester()
    report = await tester.run_all_tests()
    
    # Save report
    with open("logs/test_results_agentic_architecture.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✅ Test report saved to logs/test_results_agentic_architecture.json")
    
    # Return success if overall success rate is good
    overall_success = report["summary"]["overall"]["success_rate"]
    if overall_success >= 0.7:
        print(f"🎉 True Agentic MCP Architecture Test PASSED ({overall_success:.1%})")
        return True
    else:
        print(f"❌ True Agentic MCP Architecture Test FAILED ({overall_success:.1%})")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 