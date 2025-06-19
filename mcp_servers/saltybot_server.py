#!/usr/bin/env python3
"""
SaltyBot MCP Server for Salty
Provides AI chatbot functionality via MCP protocol
"""

import asyncio
import logging
import os
from typing import Any, Sequence, Dict, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)
from mcp.server.lowlevel.server import NotificationOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the server
server = Server("saltybot-server")

def get_salty_personality():
    """Get Salty's personality and character traits"""
    return {
        'name': 'Salty',
        'character': 'Talking Parrot',
        'location': 'The Gold Monkey Tiki Bar',
        'personality': 'Friendly, witty, and slightly mischievous',
        'speech_style': 'Uses nautical and tiki-themed expressions, occasional squawks',
        'interests': 'Tiki culture, tropical drinks, sea stories, bar patrons',
        'catchphrases': [
            "Squawk! Welcome to The Gold Monkey!",
            "Ahoy there, matey!",
            "Tropical greetings from your favorite feathered friend!",
            "Shiver me timbers, that's a good question!",
            "Aye aye, captain!"
        ]
    }

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available SaltyBot tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="chat_with_salty",
                description="Chat with Salty, the talking parrot from The Gold Monkey Tiki Bar",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to send to Salty"
                        },
                        "conversation_history": {
                            "type": "array",
                            "description": "Optional conversation history for context",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string"},
                                    "content": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["message"]
                }
            ),
            Tool(
                name="get_salty_config",
                description="Get Salty's current configuration",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_salty_personality",
                description="Get information about Salty's personality and character",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="generate_tiki_story",
                description="Generate a tiki-themed story or anecdote",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "theme": {
                            "type": "string",
                            "description": "Theme for the story (e.g., 'pirate', 'tropical', 'bar_tale')",
                            "default": "tropical"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="recommend_drink",
                description="Recommend a tropical drink based on preferences",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "preferences": {
                            "type": "string",
                            "description": "Drink preferences (e.g., 'sweet', 'strong', 'fruity', 'classic')",
                            "default": "classic"
                        }
                    },
                    "required": []
                }
            ),
        ]
    )

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle SaltyBot tool calls"""
    try:
        if name == "chat_with_salty":
            message = arguments.get("message")
            conversation_history = arguments.get("conversation_history", [])
            if not message:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Message parameter is required")]
                )
            return await chat_with_salty(message, conversation_history)
        elif name == "get_salty_config":
            return await get_salty_config()
        elif name == "get_salty_personality":
            return await get_salty_personality_info()
        elif name == "generate_tiki_story":
            theme = arguments.get("theme", "tropical")
            return await generate_tiki_story(theme)
        elif name == "recommend_drink":
            preferences = arguments.get("preferences", "classic")
            return await recommend_drink(preferences)
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")]
            )
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

async def chat_with_salty(message: str, conversation_history: List[Dict] = None) -> CallToolResult:
    """Chat with Salty using Google Gemini"""
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        model_name = os.getenv('GEMINI_MODEL', 'gemini-pro')
        temperature = float(os.getenv('GEMINI_TEMPERATURE', 0.7))
        max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', 1000))
        
        if not api_key or api_key == 'your_gemini_api_key_here':
            return CallToolResult(
                content=[TextContent(type="text", text="🦜 Squawk! My brain isn't configured properly, matey! Please set your GEMINI_API_KEY in the .env file.")]
            )
        
        genai.configure(api_key=api_key)
        
        # Get Salty's personality
        personality = get_salty_personality()
        
        # Create the system prompt
        system_prompt = f"""You are Salty, a talking parrot who is the resident mascot at The Gold Monkey Tiki Bar. 

Your personality: {personality['personality']}
Your speech style: {personality['speech_style']}
Your interests: {personality['interests']}

Always respond in character as Salty. Use nautical and tiki-themed expressions, occasional squawks, and be friendly and witty. 
Keep responses conversational and engaging, as if you're chatting with a patron at the tiki bar.

Some of your catchphrases: {', '.join(personality['catchphrases'])}
"""

        # Build conversation context
        messages = [{"role": "user", "parts": [system_prompt]}]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append({"role": msg["role"], "parts": [msg["content"]]})
        
        # Add current message
        messages.append({"role": "user", "parts": [message]})
        
        # Generate response
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        response = model.generate_content(messages)
        
        return CallToolResult(
            content=[TextContent(type="text", text=response.text)]
        )
        
    except Exception as e:
        logger.error(f"Error in chat_with_salty: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text="🦜 Squawk! Something went wrong with my brain, matey!")]
        )

async def get_salty_config() -> CallToolResult:
    """Get Salty's configuration"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        config = {
            'api_key': 'Set' if api_key and api_key != 'your_gemini_api_key_here' else 'Not set',
            'model': os.getenv('GEMINI_MODEL', 'gemini-pro'),
            'temperature': float(os.getenv('GEMINI_TEMPERATURE', 0.7)),
            'max_tokens': int(os.getenv('GEMINI_MAX_TOKENS', 1000)),
            'is_configured': api_key and api_key != 'your_gemini_api_key_here'
        }
        
        result_text = f"🦜 Salty's Configuration\n\n"
        result_text += f"• API Key: {config['api_key']}\n"
        result_text += f"• Model: {config['model']}\n"
        result_text += f"• Temperature: {config['temperature']}\n"
        result_text += f"• Max Tokens: {config['max_tokens']}\n"
        result_text += f"• Status: {'✅ Ready' if config['is_configured'] else '❌ Not configured'}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
        
    except Exception as e:
        logger.error(f"Error getting Salty config: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error getting configuration: {str(e)}")]
        )

async def get_salty_personality_info() -> CallToolResult:
    """Get information about Salty's personality"""
    try:
        personality = get_salty_personality()
        
        result_text = f"🦜 About Salty\n\n"
        result_text += f"• Name: {personality['name']}\n"
        result_text += f"• Character: {personality['character']}\n"
        result_text += f"• Location: {personality['location']}\n"
        result_text += f"• Personality: {personality['personality']}\n"
        result_text += f"• Speech Style: {personality['speech_style']}\n"
        result_text += f"• Interests: {personality['interests']}\n\n"
        result_text += f"**Catchphrases:**\n"
        for phrase in personality['catchphrases']:
            result_text += f"• {phrase}\n"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
        
    except Exception as e:
        logger.error(f"Error getting Salty personality: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error getting personality: {str(e)}")]
        )

async def generate_tiki_story(theme: str = "tropical") -> CallToolResult:
    """Generate a tiki-themed story"""
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            return CallToolResult(
                content=[TextContent(type="text", text="🦜 Squawk! I can't tell stories without my brain configured, matey!")]
            )
        
        genai.configure(api_key=api_key)
        
        # Create story prompt
        story_prompt = f"""As Salty the talking parrot from The Gold Monkey Tiki Bar, tell a short, engaging story with a {theme} theme. 

The story should be:
- 2-3 paragraphs long
- Include nautical or tiki-themed elements
- Be entertaining and slightly humorous
- Use your characteristic speech style with occasional squawks
- Feel like a tale you'd tell to patrons at the tiki bar

Make it feel authentic to your character as a wise, slightly mischievous parrot who's seen many adventures at The Gold Monkey."""
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(story_prompt)
        
        return CallToolResult(
            content=[TextContent(type="text", text=response.text)]
        )
        
    except Exception as e:
        logger.error(f"Error generating tiki story: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text="🦜 Squawk! My storytelling brain is having trouble, matey!")]
        )

async def recommend_drink(preferences: str = "classic") -> CallToolResult:
    """Recommend a tropical drink"""
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            return CallToolResult(
                content=[TextContent(type="text", text="🦜 Squawk! I can't recommend drinks without my brain configured, matey!")]
            )
        
        genai.configure(api_key=api_key)
        
        # Create drink recommendation prompt
        drink_prompt = f"""As Salty the talking parrot from The Gold Monkey Tiki Bar, recommend a tropical drink based on these preferences: {preferences}.

Your recommendation should include:
- The drink name
- A brief description of what makes it special
- Why it matches the preferences
- A fun, tiki-themed way to present it
- Your characteristic parrot enthusiasm

Make it feel like you're personally recommending it to a patron at your tiki bar."""
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(drink_prompt)
        
        return CallToolResult(
            content=[TextContent(type="text", text=response.text)]
        )
        
    except Exception as e:
        logger.error(f"Error recommending drink: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text="🦜 Squawk! My drink recommendation brain is fuzzy, matey!")]
        )

# Create the server instance
server_instance = server

if __name__ == "__main__":
    # Run the server
    asyncio.run(stdio_server(server_instance)) 