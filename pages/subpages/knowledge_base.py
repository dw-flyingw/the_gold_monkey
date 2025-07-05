import streamlit as st
import asyncio
from pathlib import Path
from utils.actions import (
    query_rag_documents,
    rebuild_rag_database,
    list_rag_documents,
    add_rag_document,
)
from utils.shared import get_salty_personality_direct

def show_knowledge_base():
    st.subheader("📚 Knowledge Base")
    st.markdown("*🦜 Salty's treasure trove of tiki bar wisdom*")
    salty = get_salty_personality_direct()
    st.info(f"🦜 {salty['catchphrases'][3]} I've got a whole library of tiki bar knowledge, matey!")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔍 Search Knowledge")
        search_query = st.text_input("What would you like to know about The Gold Monkey?",
                                   placeholder="e.g., What is The Gold Monkey?")
        top_k = st.slider("Number of results", min_value=1, max_value=10, value=5)
        if st.button("🔍 Search", type="primary"):
            if search_query:
                with st.spinner("🦜 Searching through my knowledge..."):
                    result = asyncio.run(query_rag_documents(search_query, top_k))
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success(f"🦜 Found {result.get('count', 0)} relevant documents!")
                        if result.get('results'):
                            for i, (doc, metadata, distance) in enumerate(zip(
                                result['results'],
                                result.get('metadatas', []),
                                result.get('distances', [])
                            )):
                                with st.expander(f"Result {i+1} - {metadata.get('filename', 'Unknown')}"):
                                    st.write(f"**Source:** {metadata.get('filename', 'Unknown')}")
                                    st.write(f"**Similarity:** {1 - distance:.3f}" if distance else "N/A")
                                    st.write(f"**Content:**")
                                    st.write(doc)
                        else:
                            st.info("No relevant documents found. Try a different search term!")
            else:
                st.warning("Please enter a search query!")
        st.markdown("---")
        st.subheader("📄 Add New Document")
        new_content = st.text_area("Document content",
                                 placeholder="Enter the content of your document...",
                                 height=150)
        new_metadata = st.text_input("Document source (optional)",
                                   placeholder="e.g., tiki_bar_history.md")
        if st.button("📄 Add Document"):
            if new_content:
                with st.spinner("🦜 Adding document to my knowledge base..."):
                    metadata = {"filename": new_metadata} if new_metadata else {}
                    result = asyncio.run(add_rag_document(new_content, metadata))
                    if "error" in result:
                        st.error(f"🦜 Squawk! Error: {result['error']}")
                    else:
                        st.success("🦜 Document added successfully!")
                        st.info(f"Document ID: {result.get('id', 'Unknown')}")
            else:
                st.warning("Please enter document content!")
    with col2:
        st.subheader("🗂️ Database Management")
        if st.button("🔄 Rebuild Database"):
            with st.spinner("🦜 Rebuilding my knowledge base from markdown files..."):
                result = asyncio.run(rebuild_rag_database())
                if isinstance(result, str):
                    st.success(result)
                elif "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success("🦜 Knowledge base rebuilt successfully!")
                    st.info(f"Documents added: {result.get('documents_added', 0)}")
                    st.info(f"Files processed: {result.get('files_processed', 0)}")
        if st.button("📋 List Documents"):
            with st.spinner("🦜 Checking my document collection..."):
                result = asyncio.run(list_rag_documents())
                if "error" in result:
                    st.error(f"🦜 Squawk! Error: {result['error']}")
                else:
                    st.success(f"🦜 Found {result.get('count', 0)} documents!")
                    if result.get('documents'):
                        for i, (doc, metadata) in enumerate(zip(
                            result['documents'][:10],
                            result.get('metadatas', [])[:10]
                        )):
                            with st.expander(f"Document {i+1} - {metadata.get('filename', 'Unknown')}"):
                                st.write(f"**ID:** {result['ids'][i] if result.get('ids') else 'Unknown'}")
                                st.write(f"**Source:** {metadata.get('filename', 'Unknown')}")
                                st.write(f"**Content:** {doc[:200]}...")
                    if result.get('count', 0) > 10:
                        st.info(f"... and {result.get('count', 0) - 10} more documents")
        st.markdown("---")
        st.subheader("📊 Database Stats")
        try:
            import chromadb
            from chromadb.config import Settings
            client = chromadb.PersistentClient(
                path="./data/chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
            collection = client.get_or_create_collection("gold_monkey_docs")
            results = collection.get()
            total_docs = len(results["documents"]) if results["documents"] else 0
            source_counts = {}
            if results["metadatas"]:
                for metadata in results["metadatas"]:
                    source = metadata.get("filename", "Unknown")
                    source_counts[source] = source_counts.get(source, 0) + 1
            st.metric("Total Documents", total_docs)
            st.metric("Unique Sources", len(source_counts))
            if source_counts:
                st.write("**Documents by source:**")
                for source, count in source_counts.items():
                    st.write(f"• {source}: {count}")
        except Exception as e:
            st.warning(f"Could not load database stats: {e}")
        st.markdown("---")
        st.subheader("🦜 Salty's Tips")
        st.write("""
        **Knowledge Base Tips:**
        - 🔍 **Search** for specific information about The Gold Monkey
        - 📄 **Add documents** to expand my knowledge
        - 🔄 **Rebuild** to update from markdown files
        - 📋 **List** to see what I know about
        *Squawk! The more you teach me, the wiser I become!*
        """)
    st.markdown("---")
    st.subheader("📁 Available Markdown Files")
    rag_dir = Path(__file__).parent.parent / "rag"
    if rag_dir.exists():
        md_files = list(rag_dir.glob("*.md"))
        if md_files:
            st.write(f"Found {len(md_files)} markdown files in the `rag` folder:")
            for md_file in md_files:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"• **{md_file.name}**")
                with col_b:
                    try:
                        size = md_file.stat().st_size
                        st.write(f"({size} bytes)")
                    except:
                        st.write("(size unknown)")
        else:
            st.info("No markdown files found in the `rag` folder.")
            st.write("Add some `.md` files to the `rag` folder to build your knowledge base!")
    else:
        st.warning("`rag` folder not found. Create it to store your markdown files!")

if __name__ == "__main__":
    show_knowledge_base() 