#!/usr/bin/env python3
"""
RAG MCP Server for Salty
Provides knowledge base functionality via MCP protocol
"""

import asyncio
import logging
import os
import uuid
from pathlib import Path
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
server = Server("rag-server")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available RAG tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="query_documents",
                description="Search for relevant documents in the knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query to find relevant documents"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="rebuild_database",
                description="Rebuild the RAG database from markdown files",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="list_documents",
                description="List all documents in the knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="add_document",
                description="Add a new document to the knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Document content to add"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Optional metadata for the document"
                        }
                    },
                    "required": ["content"]
                }
            ),
            Tool(
                name="get_database_stats",
                description="Get statistics about the knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
        ]
    )

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle RAG tool calls"""
    try:
        if name == "query_documents":
            query = arguments.get("query")
            top_k = arguments.get("top_k", 5)
            if not query:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Query parameter is required")]
                )
            return await query_documents(query, top_k)
        elif name == "rebuild_database":
            return await rebuild_database()
        elif name == "list_documents":
            return await list_documents()
        elif name == "add_document":
            content = arguments.get("content")
            metadata = arguments.get("metadata", {})
            if not content:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Content parameter is required")]
                )
            return await add_document(content, metadata)
        elif name == "get_database_stats":
            return await get_database_stats()
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")]
            )
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

async def query_documents(query: str, top_k: int = 5) -> CallToolResult:
    """Query RAG documents for relevant information"""
    try:
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        collection = client.get_or_create_collection("gold_monkey_docs")
        
        # Load embedding model
        embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        model = SentenceTransformer(embedding_model)
        
        # Generate embeddings for query
        query_embedding = model.encode([query]).tolist()
        
        # Search
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        if not results["documents"] or not results["documents"][0]:
            return CallToolResult(
                content=[TextContent(type="text", text=f"No relevant documents found for query: '{query}'")]
            )
        
        # Format results
        result_text = f"Found {len(results['documents'][0])} relevant document(s) for query: '{query}'\n\n"
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0] if results["metadatas"] else [],
            results["distances"][0] if results["distances"] else []
        )):
            result_text += f"**Result {i+1}**\n"
            if metadata:
                result_text += f"Source: {metadata.get('filename', 'Unknown')}\n"
            if distance is not None:
                similarity = 1 - distance
                result_text += f"Similarity: {similarity:.3f}\n"
            result_text += f"Content: {doc[:500]}...\n\n"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text.strip())]
        )
        
    except Exception as e:
        logger.error(f"Error querying documents: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error querying documents: {str(e)}")]
        )

async def rebuild_database() -> CallToolResult:
    """Rebuild the RAG vector database"""
    try:
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer
        import markdown
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        collection = client.get_or_create_collection("gold_monkey_docs")
        
        # Clear existing documents
        collection.delete(where={})
        
        # Load embedding model
        embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        model = SentenceTransformer(embedding_model)
        
        # Process markdown files
        rag_dir = Path(__file__).parent.parent.parent / "rag"
        documents = []
        metadatas = []
        ids = []
        
        if not rag_dir.exists():
            return CallToolResult(
                content=[TextContent(type="text", text="RAG directory not found. Create a 'rag' folder with markdown files.")]
            )
        
        files_processed = 0
        for md_file in rag_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Convert markdown to text
                md = markdown.Markdown()
                text_content = md.convert(content)
                
                # Split into chunks (simple paragraph splitting)
                chunks = [chunk.strip() for chunk in text_content.split('\n\n') if chunk.strip()]
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"{md_file.stem}_{i}"
                    documents.append(chunk)
                    metadatas.append({
                        "source": str(md_file),
                        "filename": md_file.name,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    })
                    ids.append(doc_id)
                
                files_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
        
        # Add documents to collection
        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            result_text = f"✅ Database rebuilt successfully!\n\n"
            result_text += f"• Documents added: {len(documents)}\n"
            result_text += f"• Files processed: {files_processed}\n"
            result_text += f"• Collection: gold_monkey_docs\n"
            result_text += f"• Database location: ./data/chroma_db"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text="No documents found to add. Add some .md files to the 'rag' folder.")]
            )
            
    except Exception as e:
        logger.error(f"Error rebuilding database: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error rebuilding database: {str(e)}")]
        )

async def list_documents() -> CallToolResult:
    """List all documents in the RAG database"""
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        collection = client.get_or_create_collection("gold_monkey_docs")
        
        # Get all documents
        results = collection.get()
        
        if not results["documents"]:
            return CallToolResult(
                content=[TextContent(type="text", text="No documents found in the knowledge base. Try rebuilding the database.")]
            )
        
        # Format results
        result_text = f"Found {len(results['documents'])} document(s) in the knowledge base:\n\n"
        
        for i, (doc, metadata) in enumerate(zip(
            results["documents"],
            results["metadatas"] if results["metadatas"] else []
        )):
            result_text += f"**Document {i+1}**\n"
            if metadata:
                result_text += f"Source: {metadata.get('filename', 'Unknown')}\n"
                if 'chunk_index' in metadata:
                    result_text += f"Chunk: {metadata['chunk_index'] + 1}/{metadata.get('total_chunks', 1)}\n"
            result_text += f"Content: {doc[:200]}...\n\n"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text.strip())]
        )
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error listing documents: {str(e)}")]
        )

async def add_document(content: str, metadata: Dict[str, Any] = None) -> CallToolResult:
    """Add a document to the RAG database"""
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        collection = client.get_or_create_collection("gold_monkey_docs")
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Add document
        collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )
        
        result_text = f"✅ Document added successfully!\n\n"
        result_text += f"• Document ID: {doc_id}\n"
        result_text += f"• Content length: {len(content)} characters\n"
        if metadata:
            result_text += f"• Metadata: {metadata}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
        
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error adding document: {str(e)}")]
        )

async def get_database_stats() -> CallToolResult:
    """Get statistics about the knowledge base"""
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        collection = client.get_or_create_collection("gold_monkey_docs")
        
        # Get all documents
        results = collection.get()
        
        total_docs = len(results["documents"]) if results["documents"] else 0
        
        # Count by source
        source_counts = {}
        if results["metadatas"]:
            for metadata in results["metadatas"]:
                source = metadata.get("filename", "Unknown")
                source_counts[source] = source_counts.get(source, 0) + 1
        
        # Format stats
        result_text = f"📊 Knowledge Base Statistics\n\n"
        result_text += f"• Total Documents: {total_docs}\n"
        result_text += f"• Unique Sources: {len(source_counts)}\n"
        result_text += f"• Collection: gold_monkey_docs\n"
        result_text += f"• Database: ./data/chroma_db\n\n"
        
        if source_counts:
            result_text += f"**Documents by source:**\n"
            for source, count in source_counts.items():
                result_text += f"• {source}: {count} documents\n"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error getting database stats: {str(e)}")]
        )

# Create the server instance
server_instance = server

if __name__ == "__main__":
    # Run the server
    asyncio.run(stdio_server(server_instance)) 