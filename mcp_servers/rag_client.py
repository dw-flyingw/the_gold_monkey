#!/usr/bin/env python3
"""
RAG MCP Client for Salty
Communicates with RAG MCP server for knowledge base functionality
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

logger = logging.getLogger(__name__)

class RAGMCPClient:
    """Client for RAG MCP server"""
    
    def __init__(self, server_path: str = None):
        """Initialize the RAG MCP client"""
        self.server_path = server_path or os.getenv("RAG_SERVER_PATH", "mcp_servers/rag_server.py")
    
    async def _call_tool(self, tool_name: str, arguments: dict = None) -> Dict[str, Any]:
        """Call a tool on the RAG MCP server"""
        try:
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_path]
            )
            
            async with stdio_client(server_params) as session:
                # Call the tool
                result = await session.call_tool(tool_name, arguments or {})
                
                # Parse the result
                if result.content and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        try:
                            return json.loads(content.text)
                        except json.JSONDecodeError:
                            return {"response": content.text}
                    else:
                        return {"response": str(content)}
                else:
                    return {"error": "No response from server"}
                    
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def query_documents(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Query RAG documents"""
        return await self._call_tool("query_documents", {"query": query, "top_k": top_k})
    
    async def rebuild_database(self) -> Dict[str, Any]:
        """Rebuild the RAG database"""
        return await self._call_tool("rebuild_database")
    
    async def list_documents(self) -> Dict[str, Any]:
        """List all documents"""
        return await self._call_tool("list_documents")
    
    async def add_document(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a document to the database"""
        args = {"content": content}
        if metadata:
            args["metadata"] = metadata
        return await self._call_tool("add_document", args)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get RAG database statistics"""
        return await self._call_tool("get_database_stats")

# Convenience functions for direct use
async def query_rag_documents(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Query RAG documents"""
    client = RAGMCPClient()
    return await client.query_documents(query, top_k)

async def rebuild_rag_database() -> Dict[str, Any]:
    """Rebuild the RAG database"""
    client = RAGMCPClient()
    return await client.rebuild_database()

async def list_rag_documents() -> Dict[str, Any]:
    """List all documents"""
    client = RAGMCPClient()
    return await client.list_documents()

async def add_rag_document(content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Add a document to the database"""
    client = RAGMCPClient()
    return await client.add_document(content, metadata)

async def get_rag_stats() -> Dict[str, Any]:
    """Get RAG database statistics"""
    client = RAGMCPClient()
    return await client.get_stats()

async def get_tools() -> Dict[str, Any]:
    """Get a dictionary of all available tools"""
    return {
        "query_rag_documents": query_rag_documents,
        "rebuild_rag_database": rebuild_rag_database,
        "list_rag_documents": list_rag_documents,
        "add_rag_document": add_rag_document,
        "get_rag_stats": get_rag_stats,
    }

if __name__ == "__main__":
    # Test the client
    async def test():
        try:
            # Test getting stats
            stats = await get_rag_stats()
            print("RAG stats:", stats)
            
            # Test query
            result = await query_rag_documents("What is The Gold Monkey?", 3)
            print("Query result:", result)
            
        except Exception as e:
            print(f"Test error: {e}")
    
    asyncio.run(test()) 