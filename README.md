# Salty 🧂

A sophisticated home automation and entertainment system featuring Salty, the AI-powered talking parrot who manages The Gold Monkey Tiki Bar.

## Features

- 🏠 **Home Page**: Welcome screen with quick start guide
- 📊 **Data Explorer**: Upload and explore CSV files
- 📈 **Charts**: Multiple chart types and visualizations
- 🤖 **Chat with Salty**: AI-powered chatbot using Google Gemini
- 💡 **TPLink Control**: TP-Link smart bulb control with color presets
- 📚 **Knowledge Base**: RAG system with ChromaDB for document retrieval
- ℹ️ **About**: Information about the app
- 🤖 **AI Chatbot** - Salty powered by Google Gemini with personality
- 💡 **TPLink Control** - TP-Link smart bulb control with color presets
- 📚 **Knowledge Base** - RAG system with ChromaDB for document retrieval
- 📊 **Data exploration tools** - Upload and analyze CSV files
- 📈 **Multiple chart types** - Beautiful visualizations
- 🎨 **Beautiful and responsive design** - Modern Streamlit interface
- ⚡ **Fast and interactive** - Real-time control and responses

## Smart Home Integration

### TP-Link Smart Lighting (Direct Integration)
- **Full Color Control**: Red, orange, yellow, green, blue, purple presets
- **Custom Colors**: RGB color picker for any mood
- **Device Discovery**: Automatic detection of TP-Link smart bulbs
- **Quick Controls**: One-click on/off for all lights
- **Tiki Themes**: Pre-configured lighting for perfect atmosphere
- **Direct Integration**: Uses python-kasa library for direct device control

## Knowledge Base (RAG)

- **Document Retrieval** - Semantic search through markdown files
- **Vector Database** - ChromaDB with sentence transformers (stored in `data/chroma_db/`)
- **Markdown Processing** - Automatic parsing of .md files from the `rag` folder
- **Document Management** - Add, list, and rebuild knowledge base
- **Direct Integration** - Direct ChromaDB and sentence-transformers integration

## MCP Server Management

All servers are now managed through the MCP (Model Context Protocol) CLI using `uv`.

### Starting Servers

**Start all servers at once:**
```bash
python start_servers.py
```

**Start individual servers:**
```bash
# TP-Link Server
uv run mcp run python mcp_servers/tplink_server.py

# RAG Server
uv run mcp run python mcp_servers/rag_server.py

# Spotify Server
uv run mcp run python mcp_servers/spotify_server.py

# SaltyBot Server
uv run mcp run python mcp_servers/saltybot_server.py
```

### Stopping Servers

**Stop all servers:**
```bash
python stop_servers.py
```

**Or manually stop with Ctrl+C** in each terminal window.

### MCP Development

**Run with MCP Inspector (for debugging):**
```bash
uv run mcp dev python mcp_servers/tplink_server.py
```

**Check MCP version:**
```bash
uv run mcp version
```

### Server Status

The servers will show their status in the Streamlit app sidebar when running.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Salty
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```
   
   Required variables:
   - `SALTY_GEMINI_API_KEY` - Your Google Gemini API key
   - `EMBEDDING_MODEL` - Sentence transformer model (default: sentence-transformers/all-MiniLM-L6-v2)

4. **Add markdown files to the knowledge base:**
   Place `.md` files in the `rag/` folder. The system will automatically process them when you rebuild the database.

5. **Run the application:**
   ```bash
   streamlit run main.py
   ```

## Project Structure

```
Salty/
├── main.py                 # Main Streamlit application
├── pyproject.toml         # Project dependencies and configuration
├── .env                   # Environment variables
├── README.md              # This file
├── data/                  # Data storage
│   └── chroma_db/         # ChromaDB vector database
├── rag/                   # Knowledge base documents
│   ├── the_gold_monkey_backstory.md
│   ├── the_gold_monkey_trivia.md
│   └── Guests.md
├── logs/                  # Application logs
├── src/                   # Source code
│   └── utils/            # Utility scripts and tools
│       └── __init__.py
└── audio/                # Audio files (if any)
```

The app will open in your default browser at `http://localhost:8501`.

## Usage

- Use the sidebar to navigate between different pages
- Upload CSV files in the Data Explorer to analyze your data
- Explore various chart types in the Charts section
- Chat with Salty, the AI-powered parrot
- Control your TP-Link smart lights with color presets and custom colors
- Manage your knowledge base in the Knowledge Base page
- Check out the About page for more information

## Smart Lighting Features

The TP-Link integration includes:
- 💬 **Salty's Personality**: All lighting controls feature Salty's tiki-themed messages
- 🎨 **Color Presets**: Pre-configured colors for different tiki bar moods
- 🔍 **Device Discovery**: Automatic detection and listing of smart devices
- 🎛️ **Quick Controls**: Easy on/off and color change buttons
- 📊 **Status Monitoring**: Real-time device status and connection info
- 🎯 **Custom Colors**: Full RGB color picker for personalized lighting
- 🔧 **Direct Integration**: Uses python-kasa library for reliable device control

## Chatbot Features

The Gemini chatbot includes:
- 💬 Real-time chat interface with Salty's personality
- 🧠 Configurable model parameters (temperature, max tokens)
- 📝 Chat history persistence during session
- 🗑️ Clear chat history option
- ⚙️ Environment-based configuration

## Knowledge Base Features

The RAG system includes:
- 🔍 **Semantic Search**: Find relevant information using natural language
- 📄 **Document Management**: Add, list, and rebuild knowledge base
- 🎯 **Markdown Support**: Automatic processing of .md files
- 📊 **Vector Database**: ChromaDB with sentence transformer embeddings
- 🔄 **Easy Rebuilding**: One-click database rebuild from markdown files

## Development

To add more features:
1. Add new functions for different pages
2. Update the sidebar selectbox in `main()`
3. Add corresponding conditional logic

## Dependencies

The project uses the following key libraries:
- **Streamlit** - Modern web interface
- **Google Generative AI (Gemini)** - AI chatbot
- **ChromaDB** - Vector database for RAG
- **Sentence Transformers** - Text embeddings
- **Python Kasa** - TP-Link smart device control
- **Pandas & NumPy** - Data processing and analysis
- **Plotly** - Interactive charts and visualizations
