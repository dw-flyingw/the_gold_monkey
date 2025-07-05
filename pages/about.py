import streamlit as st

from utils.shared import set_page_config, show_page_header

def show_about():
    set_page_config()
    show_page_header("ℹ️ About", "The Gold Monkey Tiki Bar")
    
    st.write("""
    ## The Gold Monkey
    
    This is a sophisticated home automation and entertainment system featuring Salty
    the AI-powered talking parrot who manages The Gold Monkey Tiki Bar.
    
    ### Features
    - 🤖 **AI Chatbot** - Salty powered by Google Gemini with personality
    - 💡 **Smart Lighting** - TP-Link smart bulb control with color presets
    - 📚 **Knowledge Base** - RAG system with ChromaDB for document retrieval
    - 📊 **Data exploration tools** - Upload and analyze CSV files
    - 📈 **Multiple chart types** - Beautiful visualizations
    - 🎨 **Beautiful and responsive design** - Modern Streamlit interface
    - ⚡ **Fast and interactive** - Real-time control and responses
    
    ### Smart Home Integration
    - **TP-Link Smart Bulbs** - Full color control and automation
    - **Device Discovery** - Automatic detection of smart devices
    - **Color Presets** - Pre-configured tiki bar lighting themes
    - **Custom Colors** - Full RGB color picker for custom moods
    
    ### Knowledge Base (RAG)
    - **Document Retrieval** - Semantic search through markdown files
    - **Vector Database** - ChromaDB with sentence transformer embeddings (stored in `data/chroma_db/`)
    - **Markdown Support** - Automatic processing of .md files
    - **Document Management** - Add, list, and rebuild knowledge base
    - **Direct Integration** - Direct ChromaDB and sentence-transformers integration
    
    ### Built with
    - Streamlit - Modern web interface
    - Google Generative AI (Gemini) - AI chatbot
    - ChromaDB - Vector database for RAG
    - Sentence Transformers - Text embeddings
    - Python Kasa - TP-Link smart device control
    - FastAPI - REST API for device communication
    - Pandas & NumPy - Data processing and analysis
    - SaltyBot - Dedicated chatbot server with personality
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🦜 Salty's Role")
        st.write("""
        Salty is more than just a chatbot - he's the heart of The Gold Monkey!
        
        - **Personality**: Witty, knowledgeable parrot with tiki bar wisdom
        - **Capabilities**: Controls lights, remembers conversations, provides entertainment
        - **Speech Style**: Nautical expressions, occasional squawks, tropical charm
        - **Knowledge**: Tiki culture, tropical drinks, sea stories, and more
        - **RAG Integration**: Can search through knowledge base for accurate information
        """)
    
    with col2:
        st.subheader("💡 Smart Lighting")
        st.write("""
        The lighting system creates the perfect tiki bar atmosphere:
        
        - **Quick Controls**: One-click on/off for all lights
        - **Color Presets**: Red, orange, yellow, green, blue, purple
        - **Custom Colors**: Full RGB control for any mood
        - **Device Management**: Automatic discovery and status monitoring
        - **Tiki Themes**: Pre-configured lighting for different occasions
        """)
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📚 Knowledge Base")
        st.write("""
        The RAG system provides intelligent document retrieval:
        
        - **Semantic Search**: Find relevant information using natural language
        - **Vector Database**: ChromaDB with sentence transformer embeddings (stored in `data/chroma_db/`)
        - **Markdown Support**: Automatic processing of .md files
        - **Document Management**: Add, list, and rebuild knowledge base
        - **Direct Integration**: Direct ChromaDB and sentence-transformers integration
        """)
    
    with col4:
        st.subheader("🔧 System Architecture")
        st.write("""
        **Built with modern, scalable architecture:**
        
        - **Direct Integration**: TP-Link and RAG components using direct library integration
        - **Async Operations**: Non-blocking I/O for better performance
        - **Error Handling**: Robust error handling and logging
        - **Modular Design**: Easy to extend with new features
        - **Environment Config**: Flexible configuration via .env files
        - **Dedicated Chatbot**: SaltyBot server for personality-driven conversations
        """)
    
    st.markdown("---")
    st.caption("Made with ❤️ using Streamlit and powered by Salty the Talking Parrot")

if __name__ == "__main__":
    show_about()
