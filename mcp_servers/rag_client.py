#!/usr/bin/env python3
"""
RAG MCP Client for Salty
Communicates with RAG MCP server for knowledge base functionality
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

logger = logging.getLogger(__name__)

class RAGMCPClient:
    """Client for RAG MCP server"""
    
    def __init__(self, server_path: str = None):
        """Initialize the RAG MCP client"""
        self.server_path = server_path or "mcp_servers/rag_server.py"
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Connect to the RAG MCP server"""
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_path]
            )
            
            # Create client session
            self.session = ClientSession(server_params)
            await self.session.__aenter__()
            
            logger.info("Connected to RAG MCP server")
            
        except Exception as e:
            logger.error(f"Error connecting to RAG MCP server: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the RAG MCP server"""
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
                logger.info("Disconnected from RAG MCP server")
            except Exception as e:
                logger.error(f"Error disconnecting from RAG MCP server: {e}")
    
    async def query_documents(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Query RAG documents for relevant information"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the query_documents tool
            result = await self.session.call_tool("query_documents", {
                "query": query,
                "top_k": top_k
            })
            
            # Parse the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"response": content.text}
                else:
                    return {"response": str(content)}
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            return {"error": str(e)}
    
    async def rebuild_database(self) -> Dict[str, Any]:
        """Rebuild the RAG vector database"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the rebuild_database tool
            result = await self.session.call_tool("rebuild_database", {})
            
            # Parse the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"response": content.text}
                else:
                    return {"response": str(content)}
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Error rebuilding database: {e}")
            return {"error": str(e)}
    
    async def list_documents(self) -> Dict[str, Any]:
        """List all documents in the RAG database"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the list_documents tool
            result = await self.session.call_tool("list_documents", {})
            
            # Parse the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"response": content.text}
                else:
                    return {"response": str(content)}
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return {"error": str(e)}
    
    async def add_document(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a document to the RAG database"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the add_document tool
            args = {"content": content}
            if metadata:
                args["metadata"] = metadata
            
            result = await self.session.call_tool("add_document", args)
            
            # Parse the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"response": content.text}
                else:
                    return {"response": str(content)}
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return {"error": str(e)}
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            if not self.session:
                await self.connect()
            
            # Call the get_database_stats tool
            result = await self.session.call_tool("get_database_stats", {})
            
            # Parse the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"response": content.text}
                else:
                    return {"response": str(content)}
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}

# Convenience functions for direct use
async def query_rag_documents(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Query RAG documents"""
    async with RAGMCPClient() as client:
        return await client.query_documents(query, top_k)

async def rebuild_rag_database() -> Dict[str, Any]:
    """Rebuild RAG database"""
    async with RAGMCPClient() as client:
        return await client.rebuild_database()

async def list_rag_documents() -> Dict[str, Any]:
    """List RAG documents"""
    async with RAGMCPClient() as client:
        return await client.list_documents()

async def add_rag_document(content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Add document to RAG database"""
    async with RAGMCPClient() as client:
        return await client.add_document(content, metadata)

async def get_rag_stats() -> Dict[str, Any]:
    """Get RAG database stats"""
    async with RAGMCPClient() as client:
        return await client.get_database_stats()

if __name__ == "__main__":
    # Test the client
    async def test():
        try:
            # Test database stats
            stats = await get_rag_stats()
            print("Database stats:", stats)
            
            # Test query
            result = await query_rag_documents("What is The Gold Monkey?", 3)
            print("Query result:", result)
            
        except Exception as e:
            print(f"Test error: {e}")
    
    asyncio.run(test()) 