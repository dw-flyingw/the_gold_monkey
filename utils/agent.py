import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import google.generativeai as genai
from pathlib import Path
import traceback

# Import unified MCP client
from mcp_servers.unified_client import UnifiedMCPClient

# Import error handler
from utils.mcp_error_handler import MCPErrorHandler, handle_mcp_error, is_mcp_error

logger = logging.getLogger(__name__)

class GoalType(Enum):
    ENTERTAINMENT = "entertainment"
    AMBIANCE = "ambiance"
    INFORMATION = "information"
    AUTOMATION = "automation"
    SOCIAL = "social"

class ToolCategory(Enum):
    MEDIA = "media"
    LIGHTING = "lighting"
    INFORMATION = "information"
    VOICE = "voice"
    AUTOMATION = "automation"

@dataclass
class ToolUsage:
    tool_name: str
    category: ToolCategory
    success: bool
    timestamp: datetime
    execution_time: float
    user_feedback: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class Goal:
    id: str
    type: GoalType
    description: str
    priority: int  # 1-5, 5 being highest
    created_at: datetime
    completed_at: Optional[datetime] = None
    success: Optional[bool] = None
    tools_used: List[str] = None

@dataclass
class Memory:
    conversation_history: List[Dict]
    tool_usage_patterns: Dict[str, List[ToolUsage]]
    user_preferences: Dict[str, Any]
    successful_goals: List[Goal]
    failed_goals: List[Goal]

class PlanningEngine:
    """Handles goal planning and tool selection"""
    
    def __init__(self, agent):
        self.agent = agent
    
    async def create_plan(self, user_input: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a plan to achieve the user's goal"""
        
        # Analyze user intent and create goals
        goals = await self._analyze_intent(user_input, context)
        
        # For each goal, create a plan
        plans = []
        for goal in goals:
            plan = await self._plan_for_goal(goal, context)
            plans.extend(plan)
        
        return plans
    
    async def _analyze_intent(self, user_input: str, context: Dict[str, Any]) -> List[Goal]:
        """Analyze user input to determine goals"""
        
        # Use LLM to analyze intent
        analysis_prompt = f"""
        Analyze this user input and determine what goals they want to achieve:
        
        User Input: "{user_input}"
        Context: {json.dumps(context, indent=2)}
        
        Available goal types:
        - ENTERTAINMENT: Music, TV, games, fun activities
        - AMBIANCE: Lighting, mood setting, atmosphere
        - INFORMATION: Knowledge queries, data lookup
        - AUTOMATION: Smart home control, routines
        - SOCIAL: Conversation, interaction, engagement
        
        Return a JSON array of goals with this structure:
        {{
            "type": "goal_type",
            "description": "what the user wants to achieve",
            "priority": 1-5
        }}
        """
        
        try:
            response = await self.agent._call_llm(analysis_prompt)
            goals_data = json.loads(response)
            
            goals = []
            for i, goal_data in enumerate(goals_data):
                goal = Goal(
                    id=f"goal_{int(time.time())}_{i}",
                    type=GoalType(goal_data["type"]),
                    description=goal_data["description"],
                    priority=goal_data["priority"],
                    created_at=datetime.now()
                )
                goals.append(goal)
            
            return goals
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            # Fallback: create a basic goal
            return [Goal(
                id=f"goal_{int(time.time())}",
                type=GoalType.SOCIAL,
                description="Engage in conversation with user",
                priority=3,
                created_at=datetime.now()
            )]
    
    async def _plan_for_goal(self, goal: Goal, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a plan to achieve a specific goal"""
        
        # Get available tools for this goal type
        available_tools = self._get_tools_for_goal(goal.type)
        
        # Use LLM to create a plan
        planning_prompt = f"""
        Create a plan to achieve this goal:
        
        Goal: {goal.description}
        Goal Type: {goal.type.value}
        Priority: {goal.priority}
        
        Available tools: {list(available_tools.keys())}
        
        Create a step-by-step plan. Return JSON array:
        [
            {{
                "step": 1,
                "action": "tool_name",
                "parameters": {{"param": "value"}},
                "reasoning": "why this step is needed"
            }}
        ]
        """
        
        try:
            response = await self.agent._call_llm(planning_prompt)
            plan_steps = json.loads(response)
            return plan_steps
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return []

    def _get_tools_for_goal(self, goal_type: GoalType) -> Dict[str, Any]:
        """Get tools appropriate for a goal type"""
        unified_tools = self.agent.tools.get("unified", {})
        tools = {}
        
        if goal_type == GoalType.ENTERTAINMENT:
            # Spotify and Roku tools
            for name, tool in unified_tools.items():
                if name.startswith(("spotify_", "roku_")):
                    tools[name] = tool
        elif goal_type == GoalType.AMBIANCE:
            # TP-Link and Spotify tools
            for name, tool in unified_tools.items():
                if name.startswith(("tplink_", "spotify_")):
                    tools[name] = tool
        elif goal_type == GoalType.INFORMATION:
            # RAG tools
            for name, tool in unified_tools.items():
                if name.startswith("rag_"):
                    tools[name] = tool
        elif goal_type == GoalType.AUTOMATION:
            # TP-Link and Roku tools
            for name, tool in unified_tools.items():
                if name.startswith(("tplink_", "roku_")):
                    tools[name] = tool
        elif goal_type == GoalType.SOCIAL:
            # Voice and SaltyBot tools
            for name, tool in unified_tools.items():
                if name.startswith(("voice_", "saltybot_")):
                    tools[name] = tool
        
        return tools

class MemoryManager:
    """Manages agent memory and learning"""
    
    def __init__(self, memory_file: str = "data/agent_memory.json"):
        self.memory_file = Path(memory_file)
        self.memory_file.parent.mkdir(exist_ok=True)
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Memory:
        """Load memory from file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    return Memory(
                        conversation_history=data.get("conversation_history", []),
                        tool_usage_patterns=data.get("tool_usage_patterns", {}),
                        user_preferences=data.get("user_preferences", {}),
                        successful_goals=[Goal(**g) for g in data.get("successful_goals", [])],
                        failed_goals=[Goal(**g) for g in data.get("failed_goals", [])]
                    )
            except Exception as e:
                logger.error(f"Error loading memory: {e}")
        
        return Memory(
            conversation_history=[],
            tool_usage_patterns={},
            user_preferences={},
            successful_goals=[],
            failed_goals=[]
        )
    
    def save_memory(self):
        """Save memory to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump({
                    "conversation_history": self.memory.conversation_history,
                    "tool_usage_patterns": {k: [asdict(u) for u in v] for k, v in self.memory.tool_usage_patterns.items()},
                    "user_preferences": self.memory.user_preferences,
                    "successful_goals": [asdict(g) for g in self.memory.successful_goals],
                    "failed_goals": [asdict(g) for g in self.memory.failed_goals]
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def add_tool_usage(self, tool_name: str, usage: ToolUsage):
        """Record tool usage for learning"""
        if tool_name not in self.memory.tool_usage_patterns:
            self.memory.tool_usage_patterns[tool_name] = []
        
        self.memory.tool_usage_patterns[tool_name].append(usage)
        
        # Keep only last 100 usages per tool
        if len(self.memory.tool_usage_patterns[tool_name]) > 100:
            self.memory.tool_usage_patterns[tool_name] = self.memory.tool_usage_patterns[tool_name][-100:]
        
        self.save_memory()
    
    def get_tool_success_rate(self, tool_name: str) -> float:
        """Get success rate for a tool"""
        if tool_name not in self.memory.tool_usage_patterns:
            return 0.5  # Default to 50% if no data
        
        usages = self.memory.tool_usage_patterns[tool_name]
        if not usages:
            return 0.5
        
        successful = sum(1 for u in usages if u.success)
        return successful / len(usages)
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get learned user preferences"""
        return self.memory.user_preferences
    
    def update_user_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences based on interactions"""
        self.memory.user_preferences.update(preferences)
        self.save_memory()
    
    def add_goal_result(self, goal: Goal, success: bool):
        """Record goal completion"""
        if success:
            self.memory.successful_goals.append(goal)
        else:
            self.memory.failed_goals.append(goal)
        
        # Keep only last 50 goals
        if len(self.memory.successful_goals) > 50:
            self.memory.successful_goals = self.memory.successful_goals[-50:]
        if len(self.memory.failed_goals) > 50:
            self.memory.failed_goals = self.memory.failed_goals[-50:]
        
        self.save_memory()

class ReasoningEngine:
    """Handles reasoning and decision making"""
    
    def __init__(self, agent):
        self.agent = agent
    
    async def reason_about_context(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Reason about the current context and user needs"""
        
        reasoning_prompt = f"""
        Analyze this situation and provide reasoning:
        
        User Input: "{user_input}"
        Context: {json.dumps(context, indent=2)}
        User Preferences: {json.dumps(self.agent.memory.get_user_preferences(), indent=2)}
        
        Consider:
        1. What does the user really want?
        2. What tools would be most effective?
        3. What patterns from past interactions apply?
        4. What might go wrong and how to handle it?
        
        Return JSON with reasoning:
        {{
            "primary_intent": "what user wants",
            "secondary_intents": ["other things they might want"],
            "recommended_tools": ["tool1", "tool2"],
            "potential_issues": ["issue1", "issue2"],
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = await self.agent._call_llm(reasoning_prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in reasoning: {e}")
            return {
                "primary_intent": "conversation",
                "secondary_intents": [],
                "recommended_tools": [],
                "potential_issues": [],
                "confidence": 0.5
            }

class SaltyAgent:
    """
    True agentic chatbot with planning, reasoning, memory, and learning capabilities.
    """

    def __init__(self):
        """Initialize the agentic agent"""
        self.memory = MemoryManager()
        self.planning_engine = PlanningEngine(self)
        self.reasoning_engine = ReasoningEngine(self)
        self.tools = {}
        self.model = None
        
        # Configure Gemini
        api_key = os.getenv("SALTY_GEMINI_API_KEY")
        model_name = os.getenv("SALTY_GEMINI_MODEL", "gemini-2.0-flash")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            logger.warning("No Salty Gemini API key found")

    async def initialize(self):
        """Initialize the agent by discovering all tools"""
        logger.info("Initializing SaltyAgent...")
        await self._discover_all_tools()
        await self._load_tool_usage_patterns()
        logger.info("SaltyAgent initialized.")

    async def _discover_all_tools(self):
        """Discover all available tools from unified MCP server"""
        
        logger.info(f"Discovering tools from unified MCP server...")
        # Initialize unified MCP client
        self.unified_client = UnifiedMCPClient()
        
        try:
            # Get all tools from unified client
            tools = await self.unified_client.get_tools()
            self.tools = {"unified": tools}
            logger.info(f"Discovered {len(tools)} tools from unified MCP server")
        except Exception as e:
            logger.error(f"Error discovering tools from unified MCP server: {e}")
            self.tools = {"unified": {}}

    async def _load_tool_usage_patterns(self):
        """Load and analyze tool usage patterns"""
        # This will be used by the reasoning engine
        pass

    async def chat(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Agentic chat with planning, reasoning, and learning
        """
        
        logger.info(f"Starting agentic chat with message: '{message}'")
        # Step 1: Reason about the context
        context = {
            "conversation_history": conversation_history or [],
            "current_time": datetime.now().isoformat(),
            "user_preferences": self.memory.get_user_preferences()
        }
        
        logger.info("Reasoning about context...")
        reasoning_result = await self.reasoning_engine.reason_about_context(message, context)
        logger.info(f"Reasoning result: {reasoning_result}")
        
        # Step 2: Create a plan
        logger.info("Creating a plan...")
        plan = await self.planning_engine.create_plan(message, context)
        logger.info(f"Plan created: {plan}")
        
        # Step 3: Execute the plan
        logger.info("Executing plan...")
        results = []
        for step in plan:
            try:
                result = await self._execute_plan_step(step, reasoning_result)
                results.append(result)
                
                # Record tool usage for learning
                if "tool_name" in step:
                    usage = ToolUsage(
                        tool_name=step["tool_name"],
                        category=self._categorize_tool(step["tool_name"]),
                        success=result.get("success", False),
                        timestamp=datetime.now(),
                        execution_time=result.get("execution_time", 0),
                        error_message=result.get("error")
                    )
                    self.memory.add_tool_usage(step["tool_name"], usage)
                
            except Exception as e:
                logger.error(f"Error executing plan step: {e}")
                results.append({"error": str(e), "success": False})
        
        logger.info(f"Plan execution results: {results}")
        
        # Step 4: Generate response
        logger.info("Generating response...")
        response = await self._generate_response(message, plan, results, reasoning_result)
        logger.info(f"Generated response: {response}")
        
        # Step 5: Update memory
        logger.info("Updating conversation memory...")
        self._update_conversation_memory(message, response)
        logger.info("Agentic chat finished.")
        
        return response

    async def _execute_plan_step(self, step: Dict[str, Any], reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single plan step"""
        logger.info(f"Executing plan step: {step}")
        start_time = time.time()
        
        try:
            tool_name = step["action"]
            parameters = step.get("parameters", {})
            
            # Find the tool in unified tools
            logger.info(f"Looking for tool: {tool_name}")
            tool_func = self.tools.get("unified", {}).get(tool_name)
            
            if tool_func:
                # Execute the tool
                logger.info(f"Executing tool '{tool_name}' with parameters: {parameters}")
                result = await tool_func(**parameters)
                execution_time = time.time() - start_time
                logger.info(f"Tool '{tool_name}' executed successfully in {execution_time:.2f}s. Result: {result}")
                
                return {
                    "success": True,
                    "result": result,
                    "execution_time": execution_time,
                    "tool_name": tool_name
                }
            else:
                logger.error(f"Tool '{tool_name}' not found.")
                return {
                    "success": False,
                    "error": f"Tool {tool_name} not found",
                    "execution_time": time.time() - start_time
                }
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing plan step {step.get('action', 'unknown')}: {e}\n{traceback.format_exc()}")
            if is_mcp_error(e):
                error_response = handle_mcp_error(e, f"plan step {tool_name}")
                return {
                    "success": False,
                    "error": error_response.get("error", str(e)),
                    "fallback": error_response.get("fallback", False),
                    "execution_time": execution_time,
                    "tool_name": tool_name
                }
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }

    def _categorize_tool(self, tool_name: str) -> ToolCategory:
        """Categorize a tool based on its name"""
        tool_name_lower = tool_name.lower()
        
        if any(word in tool_name_lower for word in ["spotify", "music", "play", "track"]):
            return ToolCategory.MEDIA
        elif any(word in tool_name_lower for word in ["light", "tplink", "bulb"]):
            return ToolCategory.LIGHTING
        elif any(word in tool_name_lower for word in ["rag", "query", "search"]):
            return ToolCategory.INFORMATION
        elif any(word in tool_name_lower for word in ["voice", "speak", "tts"]):
            return ToolCategory.VOICE
        else:
            return ToolCategory.AUTOMATION

    async def _generate_response(self, message: str, plan: List[Dict], results: List[Dict], reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response based on plan execution results"""
        
        logger.info("Generating response...")
        # Create a summary of what was accomplished
        successful_actions = [r for r in results if r.get("success")]
        failed_actions = [r for r in results if not r.get("success")]
        
        response_prompt = f"""
        You are Salty, the immortal parrot proprietor of The Gold Monkey Tiki Bar. 
        Generate a response to the user based on what you accomplished.
        
        User Message: "{message}"
        Your Reasoning: {reasoning.get("primary_intent", "conversation")}
        
        Actions Taken:
        {json.dumps(successful_actions, indent=2)}
        
        Failed Actions:
        {json.dumps(failed_actions, indent=2)}
        
        Respond as Salty, explaining what you did and why. Be witty and engaging.
        Keep it conversational and in character.
        """
        
        try:
            logger.info("Calling LLM to generate response...")
            response = await self._call_llm(response_prompt)
            logger.info(f"LLM response: {response}")
            return {
                "response": response,
                "reasoning": reasoning,
                "plan": plan,
                "results": results,
                "successful_actions": len(successful_actions),
                "failed_actions": len(failed_actions)
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "🦜 Squawk! Something went wrong with my thinking, matey!",
                "error": str(e)
            }

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM with a prompt"""
        if not self.model:
            return "🦜 Squawk! My brain isn't configured properly, matey!"
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return "🦜 Squawk! My brain is having trouble thinking, matey!"

    def _update_conversation_memory(self, message: str, response: Dict[str, Any]):
        """Update conversation memory"""
        self.memory.memory.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        self.memory.memory.conversation_history.append({
            "role": "assistant",
            "content": response.get("response", ""),
            "timestamp": datetime.now().isoformat(),
            "reasoning": response.get("reasoning"),
            "actions_taken": response.get("successful_actions", 0)
        })
        
        # Keep only last 100 messages
        if len(self.memory.memory.conversation_history) > 100:
            self.memory.memory.conversation_history = self.memory.memory.conversation_history[-100:]
        
        self.memory.save_memory()

    async def learn_from_interaction(self, user_feedback: str, success: bool):
        """Learn from user feedback"""
        # Update user preferences based on feedback
        preferences = self.memory.get_user_preferences()
        
        # Simple learning: if successful, increase confidence in used tools
        if success:
            # This could be more sophisticated
            pass
        
        self.memory.update_user_preferences(preferences)


