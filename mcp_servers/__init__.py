# MCP (Model Context Protocol) module for Salty
# Contains TP-Link smart device control, RAG knowledge base, and SaltyBot components

from .tplink_client import TPLinkMCPClient, discover_tplink_devices, turn_on_tplink_lights, turn_off_tplink_lights, set_tplink_color, get_tplink_status
from .rag_client import RAGMCPClient, query_rag_documents, rebuild_rag_database, list_rag_documents, add_rag_document, get_rag_stats
from .saltybot_client import SaltyBotMCPClient, chat_with_salty, get_salty_config, get_salty_personality, generate_tiki_story, recommend_drink

__all__ = [
    # TP-Link components
    'TPLinkMCPClient',
    'discover_tplink_devices',
    'turn_on_tplink_lights', 
    'turn_off_tplink_lights',
    'set_tplink_color',
    'get_tplink_status',
    
    # RAG components
    'RAGMCPClient',
    'query_rag_documents',
    'rebuild_rag_database',
    'list_rag_documents',
    'add_rag_document',
    'get_rag_stats',
    
    # SaltyBot components
    'SaltyBotMCPClient',
    'chat_with_salty',
    'get_salty_config',
    'get_salty_personality',
    'generate_tiki_story',
    'recommend_drink',
] 