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
server = FastMCP("rag-server")

def get_disable_telemetry():
    val = os.getenv("CHROMA_DISABLE_TELEMETRY", "false")
    val = val.strip('\'\"").lower()
    return val == "true"

@server.tool()
async def query_documents(query: str, top_k: int = 5) -> str:
    """Search for relevant documents in the knowledge base"""
    try:
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=Settings(anonymized_telemetry=get_disable_telemetry())
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
            return f"No relevant documents found for query: '{query}'"
        
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
        
        return result_text.strip()
        
    except Exception as e:
        logger.error(f"Error querying documents: {e}")
        return f"Error querying documents: {str(e)}"

@server.tool()
async def rebuild_database() -> str:
    """Rebuild the RAG database from markdown files"""
    try:
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=Settings(anonymized_telemetry=get_disable_telemetry())
        )
        
        # Get collection
        collection = client.get_or_create_collection("gold_monkey_docs")
        
        # Clear existing documents
        collection.delete(where={})
        
        # Load embedding model
        embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        model = SentenceTransformer(embedding_model)
        
        # Process markdown files
        rag_dir = Path("./rag")
        if not rag_dir.exists():
            return "RAG directory not found. Create a 'rag' folder with markdown files."
        
        md_files = list(rag_dir.glob("*.md"))
        if not md_files:
            return "No markdown files found in the RAG directory."
        
        documents_added = 0
        files_processed = 0
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split content into chunks (simple approach)
                chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
                
                for i, chunk in enumerate(chunks):
                    if chunk.strip():
                        # Generate embedding
                        embedding = model.encode([chunk]).tolist()
                        
                        # Add to database
                        collection.add(
                            documents=[chunk],
                            embeddings=embedding,
                            metadatas=[{
                                "filename": md_file.name,
                                "chunk": i,
                                "source": "markdown"
                            }],
                            ids=[f"{md_file.stem}_{i}_{uuid.uuid4().hex[:8]}"]
                        )
                        documents_added += 1
                
                files_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
        
        return f"Database rebuilt successfully! Added {documents_added} documents from {files_processed} files."
        
    except Exception as e:
        logger.error(f"Error rebuilding database: {e}")
        return f"Error rebuilding database: {str(e)}"

@server.tool()
async def list_documents() -> str:
    """List all documents in the knowledge base"""
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=Settings(anonymized_telemetry=get_disable_telemetry())
        )
        
        # Get collection
        collection = client.get_or_create_collection("gold_monkey_docs")
        
        # Get all documents
        results = collection.get()
        
        if not results["documents"]:
            return "No documents found in the knowledge base."
        
        # Format results
        result_text = f"Found {len(results['documents'])} document(s) in the knowledge base:\n\n"
        
        for i, (doc, metadata) in enumerate(zip(
            results["documents"],
            results["metadatas"] if results["metadatas"] else []
        )):
            result_text += f"**Document {i+1}**\n"
            if metadata:
                result_text += f"Source: {metadata.get('filename', 'Unknown')}\n"
                if 'chunk' in metadata:
                    result_text += f"Chunk: {metadata['chunk']}\n"
            result_text += f"Content: {doc[:200]}...\n\n"
        
        return result_text.strip()
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return f"Error listing documents: {str(e)}"

@server.tool()
async def add_document(content: str, metadata: Dict[str, Any] = None) -> str:
    """Add a new document to the knowledge base"""
    try:
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=Settings(anonymized_telemetry=get_disable_telemetry())
        )
        
        # Get collection
        collection = client.get_or_create_collection("gold_monkey_docs")
        
        # Load embedding model
        embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        model = SentenceTransformer(embedding_model)
        
        # Generate embedding
        embedding = model.encode([content]).tolist()
        
        # Prepare metadata
        doc_metadata = metadata or {}
        doc_metadata["source"] = "manual_add"
        
        # Add to database
        doc_id = f"manual_{uuid.uuid4().hex}"
        collection.add(
            documents=[content],
            embeddings=embedding,
            metadatas=[doc_metadata],
            ids=[doc_id]
        )
        
        return f"Document added successfully with ID: {doc_id}"
        
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        return f"Error adding document: {str(e)}"

@server.tool()
async def get_database_stats() -> str:
    """Get statistics about the knowledge base"""
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=Settings(anonymized_telemetry=get_disable_telemetry())
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
        stats_text = f"Knowledge Base Statistics:\n\n"
        stats_text += f"Total Documents: {total_docs}\n"
        stats_text += f"Unique Sources: {len(source_counts)}\n\n"
        
        if source_counts:
            stats_text += "Documents by source:\n"
            for source, count in source_counts.items():
                stats_text += f"• {source}: {count}\n"
        
        return stats_text.strip()
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return f"Error getting database stats: {str(e)}"

if __name__ == "__main__":
    server.run() 