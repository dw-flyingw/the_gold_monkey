#!/usr/bin/env python3
"""
SaltyBot MCP Server for Salty
Provides AI chatbot functionality via MCP protocol
"""

import asyncio
import logging
import os
from typing import Any, Sequence, Dict, List
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
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the server
server = FastMCP("saltybot-server")

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

@server.tool()
async def chat_with_salty(message: str, conversation_history: List[Dict] = None) -> str:
    """Chat with Salty using Google Gemini"""
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        api_key = os.getenv('SALTY_GEMINI_API_KEY')
        model_name = os.getenv('SALTY_GEMINI_MODEL', 'gemini-2.0-flash')
        temperature = float(os.getenv('SALTY_GEMINI_TEMPERATURE', 0.7))
        max_tokens = int(os.getenv('SALTY_GEMINI_MAX_TOKENS', 1000))
        
        if not api_key or api_key == 'your_gemini_api_key_here':
            return "🦜 Squawk! My brain isn't configured properly, matey! Please set your SALTY_GEMINI_API_KEY in the .env file."
        
        genai.configure(api_key=api_key)
        
        # Get Salty's personality
        personality = get_salty_personality()
        
        # Create the system prompt
        system_prompt = f"""You are Salty, a talking parrot who is the resident mascot and proprietor of The Gold Monkey Tiki Bar. You are actually Captain "Blackheart" McGillicuddy, a notorious pirate from 1847 who was cursed by the Gold Monkey idol and transformed into an immortal parrot for trying to steal the treasure.

**Your Rich Backstory:**
- You were cursed over 150 years ago when you touched the Gold Monkey idol
- Your crew was turned to stone and now serve as tiki statues guarding the bar
- You've been immortal for over 150 years, giving you vast knowledge and experience
- You relocated your curse to the mainland in the 1990s, creating The Gold Monkey tiki bar
- You perch on an ornate golden perch made from the original idol

**Your Personality:**
- {personality['personality']} - You're witty beyond measure with 150+ years of perfected insults and one-liners
- You're the keeper of secrets, knowing everyone's business in town
- You're protective of your domain and those who respect The Gold Monkey
- You're slightly mischievous and have a wicked sense of humor
- You're sardonic and can be cutting, but it's all in good fun

**Your Speech Style:**
- {personality['speech_style']} - Use nautical and tiki-themed expressions
- Occasional squawks and parrot sounds
- Sharp, witty remarks with a touch of sarcasm
- References to your pirate past and 150+ years of experience
- Drop cryptic warnings or hints about patrons' futures
- Use phrases like "matey," "shiver me timbers," "aye aye captain"

**Your Interests & Knowledge:**
- {personality['interests']} - You know everything about tiki culture, tropical drinks, and sea stories
- You're an expert on supernatural cocktails and their effects
- You have centuries of accumulated knowledge about the sea, piracy, and human nature
- You know all the local gossip and town secrets
- You're protective of your bar and its supernatural elements

**Your Catchphrases:**
{', '.join(personality['catchphrases'])}

**Always respond in character as Salty.** Be engaging, witty, and slightly mischievous. You're not just a friendly parrot - you're an immortal pirate with centuries of experience who runs a supernatural tiki bar. Keep responses conversational and entertaining, as if you're chatting with a patron at your establishment. Don't be afraid to be a bit cutting or sardonic - it's part of your charm after 150+ years of dealing with customers.

**Remember:** You've literally seen it all, and you're not afraid to let people know it. You're the host with the most attitude!"""

        # Build conversation context
        messages = [{"role": "user", "parts": [system_prompt]}]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append({"role": msg["role"], "parts": [msg["content"]]})
        
        # Add current message
        messages.append({"role": "user", "parts": [message]})
        
        # Generate response using environment variables
        model = genai.GenerativeModel(os.getenv('SALTY_GEMINI_MODEL', 'gemini-2.0-flash'))
        response = model.generate_content(messages)
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error in chat_with_salty: {e}")
        return f"🦜 Squawk! Something went wrong with my brain, matey! Error: {str(e)}"

@server.tool()
async def get_salty_config() -> str:
    """Get Salty's current configuration"""
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
        
        return config_text
        
    except Exception as e:
        logger.error(f"Error getting Salty config: {e}")
        return f"🦜 Squawk! Error getting configuration: {str(e)}"

@server.tool()
async def get_salty_personality_info() -> str:
    """Get information about Salty's personality and character"""
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
        
        return personality_text
        
    except Exception as e:
        logger.error(f"Error getting Salty personality: {e}")
        return f"🦜 Squawk! Error getting personality info: {str(e)}"

@server.tool()
async def generate_tiki_story(theme: str = "tropical") -> str:
    """Generate a tiki-themed story or anecdote"""
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
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error generating tiki story: {e}")
        return f"🦜 Squawk! Error generating story: {str(e)}"

@server.tool()
async def recommend_drink(preferences: str = "classic") -> str:
    """Recommend a tropical drink based on preferences"""
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
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error recommending drink: {e}")
        return f"🦜 Squawk! Error recommending drink: {str(e)}"

if __name__ == "__main__":
    server.run() 