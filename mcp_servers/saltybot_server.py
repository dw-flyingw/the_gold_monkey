#!/usr/bin/env python3
"""
SaltyBot MCP Server for Salty
Provides AI chatbot functionality via MCP protocol
"""

import asyncio
import logging
import os
import sys
import traceback
from typing import Any, Sequence, Dict, List
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
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
    ServerCapabilities,
    InitializeRequest,
    InitializeResult,
)

# Load environment variables
load_dotenv()

# Configure DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Also enable DEBUG for MCP and anyio modules
logging.getLogger('mcp').setLevel(logging.DEBUG)
logging.getLogger('anyio').setLevel(logging.DEBUG)

# Initialize the server
server = FastMCP("saltybot-server")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

def startup():
    """Initialize the server on startup"""
    logger.info("SaltyBot server starting up...")
    logger.info("SaltyBot server startup complete.")

# Call startup
startup()

def log_uncaught_exceptions(exctype, value, tb):
    logger.error("Uncaught exception:", exc_info=(exctype, value, tb))
    traceback.print_exception(exctype, value, tb)

sys.excepthook = log_uncaught_exceptions

@server.tool()
async def chat_with_salty(message: str, conversation_history: List[Dict] = None) -> str:
    """Chat with Salty using direct Gemini integration"""
    logger.info(f"=== chat_with_salty tool CALLED ===")
    logger.info(f"Message: {message}")
    logger.info(f"Conversation history: {conversation_history}")
    
    try:
        logger.info("Importing google.generativeai...")
        import google.generativeai as genai
        logger.info("Successfully imported google.generativeai")
        
        # Configure Gemini
        api_key = os.getenv('SALTY_GEMINI_API_KEY')
        model_name = os.getenv('SALTY_GEMINI_MODEL', 'gemini-2.0-flash')
        temperature = float(os.getenv('SALTY_GEMINI_TEMPERATURE', 0.7))
        max_tokens = int(os.getenv('SALTY_GEMINI_MAX_TOKENS', 1000))
        
        logger.info(f"API Key set: {bool(api_key and api_key != 'your_gemini_api_key_here')}")
        logger.info(f"Model: {model_name}")
        logger.info(f"Temperature: {temperature}")
        logger.info(f"Max tokens: {max_tokens}")
        
        if not api_key or api_key == 'your_gemini_api_key_here':
            logger.warning("No valid API key found")
            return "🦜 Squawk! My brain isn't configured properly, matey!"
        
        logger.info("Configuring Gemini...")
        genai.configure(api_key=api_key)
        logger.info("Gemini configured successfully")
        
        # Get Salty's personality
        logger.info("Getting Salty's personality...")
        personality = get_salty_personality()
        logger.info("Personality retrieved")
        
        # Build conversation context
        logger.info("Building conversation context...")
        messages = []
        
        # Add system message with personality
        system_prompt = f"""You are {personality['name']}, a {personality['character']} at {personality['location']}. 

Your personality: {personality['personality']}
Your speech style: {personality['speech_style']}
Your interests: {personality['interests']}

You should:
- Always respond in character as Salty
- Use nautical and tiki-themed expressions
- Be witty, friendly, and slightly mischievous
- Occasionally use squawks like "Squawk!" or "🦜"
- Reference your 150+ years of experience at the bar
- Keep responses conversational and engaging
- Use your catchphrases naturally: {', '.join(personality['catchphrases'])}

Remember: You're a beloved fixture at The Gold Monkey Tiki Bar, and you love chatting with patrons!"""
        
        messages.append({"role": "user", "parts": [system_prompt]})
        messages.append({"role": "model", "parts": ["Squawk! Aye aye, I understand my role perfectly, matey! I'm ready to chat with our patrons at The Gold Monkey!"]})
        
        # Add conversation history if provided
        if conversation_history:
            logger.info(f"Adding {len(conversation_history)} conversation history items...")
            for msg in conversation_history[-10:]:  # Keep last 10 messages
                if msg.get("role") == "user":
                    messages.append({"role": "user", "parts": [msg.get("content", "")]})
                elif msg.get("role") == "assistant":
                    messages.append({"role": "model", "parts": [msg.get("content", "")]})
        
        # Add current message
        messages.append({"role": "user", "parts": [message]})
        logger.info(f"Total messages prepared: {len(messages)}")
        
        # Generate response using environment variables
        logger.info("Creating Gemini model...")
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        logger.info("Gemini model created successfully")
        
        logger.info("Generating content...")
        response = model.generate_content(messages)
        response_text = response.text
        logger.info(f"Content generated successfully. Response length: {len(response_text)}")
        
        logger.info(f"Returning chat response: '{response_text}'")
        return response_text
        
    except Exception as e:
        logger.error(f"Error in chat_with_salty: {e}")
        logger.error(traceback.format_exc())
        return f"🦜 Squawk! Something went wrong with my brain, matey! Error: {str(e)}\nTraceback: {traceback.format_exc()}"

@server.tool()
async def ping() -> str:
    """Simple ping tool for testing"""
    logger.info("=== ping tool CALLED ===")
    return "pong"

@server.tool()
async def get_salty_config() -> str:
    """Get Salty's current configuration"""
    logger.info("=== get_salty_config tool CALLED ===")
    try:
        api_key = os.getenv('SALTY_GEMINI_API_KEY')
        config = {
            'api_key': 'Set' if api_key and api_key != 'your_gemini_api_key_here' else 'Not set',
            'model': os.getenv('SALTY_GEMINI_MODEL', 'gemini-2.0-flash'),
            'temperature': float(os.getenv('SALTY_GEMINI_TEMPERATURE', 0.7)),
            'max_tokens': int(os.getenv('SALTY_GEMINI_MAX_TOKENS', 1000))
        }
        
        config_text = "🦜 **Salty's Configuration**\n\n"
        config_text += f"**API Key:** {config['api_key']}\n"
        config_text += f"**Model:** {config['model']}\n"
        config_text += f"**Temperature:** {config['temperature']}\n"
        config_text += f"**Max Tokens:** {config['max_tokens']}\n"
        
        logger.info("Configuration retrieved successfully")
        return config_text
        
    except Exception as e:
        logger.error(f"Error getting Salty config: {e}")
        logger.error(traceback.format_exc())
        return f"🦜 Squawk! Error getting configuration: {str(e)}"

@server.tool()
async def get_salty_personality_info() -> str:
    """Get information about Salty's personality and character"""
    logger.info("=== get_salty_personality_info tool CALLED ===")
    try:
        personality = get_salty_personality()
        
        personality_text = f"🦜 **About Salty**\n\n"
        personality_text += f"**Name:** {personality['name']}\n"
        personality_text += f"**Character:** {personality['character']}\n"
        personality_text += f"**Location:** {personality['location']}\n"
        personality_text += f"**Personality:** {personality['personality']}\n"
        personality_text += f"**Speech Style:** {personality['speech_style']}\n"
        personality_text += f"**Interests:** {personality['interests']}\n\n"
        personality_text += f"**Catchphrases:**\n"
        for phrase in personality['catchphrases']:
            personality_text += f"• {phrase}\n"
        
        logger.info("Personality info retrieved successfully")
        return personality_text
        
    except Exception as e:
        logger.error(f"Error getting Salty personality: {e}")
        logger.error(traceback.format_exc())
        return f"🦜 Squawk! Error getting personality info: {str(e)}"

@server.tool()
async def generate_tiki_story(theme: str = "tropical") -> str:
    """Generate a tiki-themed story or anecdote"""
    logger.info(f"=== generate_tiki_story tool CALLED with theme: {theme} ===")
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        api_key = os.getenv('SALTY_GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            return "🦜 Squawk! My brain isn't configured properly, matey!"
        
        genai.configure(api_key=api_key)
        
        # Create story prompt
        story_prompt = f"""As Salty, the immortal parrot proprietor of The Gold Monkey Tiki Bar, tell a short, entertaining story with a {theme} theme. 

Make it engaging, slightly mischievous, and include:
- Nautical or tiki-themed elements
- Your signature wit and sarcasm
- References to your 150+ years of experience
- A moral or lesson (optional but fun)

Keep it under 200 words and make it feel like you're telling it to a patron at the bar."""

        model = genai.GenerativeModel(os.getenv('SALTY_GEMINI_MODEL', 'gemini-2.0-flash'))
        response = model.generate_content(story_prompt)
        
        logger.info("Story generated successfully")
        return response.text
        
    except Exception as e:
        logger.error(f"Error generating tiki story: {e}")
        logger.error(traceback.format_exc())
        return f"🦜 Squawk! Error generating story: {str(e)}"

@server.tool()
async def recommend_drink(preferences: str = "classic") -> str:
    """Recommend a tropical drink based on preferences"""
    logger.info(f"=== recommend_drink tool CALLED with preferences: {preferences} ===")
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        api_key = os.getenv('SALTY_GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            return "🦜 Squawk! My brain isn't configured properly, matey!"
        
        genai.configure(api_key=api_key)
        
        # Create drink recommendation prompt
        drink_prompt = f"""As Salty, the immortal parrot proprietor of The Gold Monkey Tiki Bar, recommend a tropical drink for someone who prefers {preferences} drinks.

Include:
- The drink name and basic ingredients
- Why it's perfect for their taste
- A witty comment about the drink
- Any supernatural effects (since this is The Gold Monkey)

Keep it under 150 words and make it feel like you're personally recommending it to a patron."""

        model = genai.GenerativeModel(os.getenv('SALTY_GEMINI_MODEL', 'gemini-2.0-flash'))
        response = model.generate_content(drink_prompt)
        
        logger.info("Drink recommendation generated successfully")
        return response.text
        
    except Exception as e:
        logger.error(f"Error recommending drink: {e}")
        logger.error(traceback.format_exc())
        return f"🦜 Squawk! Error recommending drink: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting SaltyBot server...")
    server.run() 