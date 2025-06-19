# MCP (Model Context Protocol) module for Salty
# Contains TP-Link smart device control, RAG knowledge base, and SaltyBot components

from .tplink_client import TPLinkMCPClient, discover_tplink_devices, turn_on_tplink_lights, turn_off_tplink_lights, set_tplink_color
from .rag_client import RAGMCPClient, query_rag_documents, rebuild_rag_database, list_rag_documents, add_rag_document
from .spotify_client import SpotifyClient, play_spotify, pause_spotify, next_track, previous_track, set_volume, play_playlist, play_track, get_playback_status, get_playlist_info
from .roku_client import RokuClient, power_on, power_off, home, launch_app, volume_up, volume_down, mute, info, up, down, left, right, select, back, get_apps
from .saltybot_client import SaltyBotMCPClient, chat_with_salty

__all__ = [
    # TP-Link components
    'TPLinkMCPClient',
    'discover_tplink_devices',
    'turn_on_tplink_lights', 
    'turn_off_tplink_lights',
    'set_tplink_color',
    
    # RAG components
    'RAGMCPClient',
    'query_rag_documents',
    'rebuild_rag_database',
    'list_rag_documents',
    'add_rag_document',
    
    # Spotify components
    'SpotifyClient',
    'play_spotify',
    'pause_spotify',
    'next_track',
    'previous_track',
    'set_volume',
    'play_playlist',
    'play_track',
    'get_playback_status',
    'get_playlist_info',
    
    # Roku components
    'RokuClient',
    'power_on',
    'power_off',
    'home',
    'launch_app',
    'volume_up',
    'volume_down',
    'mute',
    'info',
    'up',
    'down',
    'left',
    'right',
    'select',
    'back',
    'get_apps',
    
    # SaltyBot components
    'SaltyBotMCPClient',
    'chat_with_salty',
] 