# AI Text Assistant

> **A Local-First Intelligent Writing Assistant** - Get smart autocomplete suggestions based on your own documents, works completely offline!

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start-5-minutes)
- [Installation Guide](#-installation-guide)
- [How to Use](#-how-to-use)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Future Enhancements](#-future-enhancements)
- [Technical Details](#-technical-details)
- [License](#-license)

---

## 🎯 Overview

AI Text Assistant is a **local-first intelligent writing assistant** similar to GitHub Copilot, but trained exclusively on your personal documents. It provides real-time text suggestions and content generation based on semantic understanding of your document library, with online search as a secondary fallback.

### What Makes It Special?

- 🔒 **Privacy-Focused**: All processing happens locally on your machine
- 📚 **Your Documents**: Learn from YOUR content, not generic data
- ⚡ **Fast**: Sub-200ms similarity search using FAISS
- 🎯 **Smart Priority**: Local documents always take precedence over online sources
- 🖥️ **Easy to Use**: Simple desktop interface, no command-line needed

---

## ✨ Features

### Core Capabilities

- 📚 **Document Ingestion**: Automatically index PDF, DOCX, and TXT files
- 🧠 **Semantic Search**: Uses sentence-transformers for high-quality embeddings
- ⚡ **Real-time Suggestions**: Copilot-style autocomplete as you type (shows 5 suggestions with 2-3 sentences each)
- ✍️ **Text Refinement**: Select text and refine, expand, or get alternatives
- 🎯 **Local-First Architecture**: Prioritizes your documents over online sources
- 🌐 **Smart Fallback**: Only uses Wikipedia when local data is insufficient
- 🖥️ **Desktop UI**: Clean PySide6-based interface with progress tracking

### Advanced Features

- **Semantic Chunking**: Intelligently splits documents at sentence/paragraph boundaries
- **Source Attribution**: Each suggestion shows which document it came from
- **Cached Results**: Minimizes API calls to online sources
- **Debounced Input**: Efficient processing without overwhelming the system
- **Background Indexing**: Non-blocking UI during document processing
- **Comprehensive Logging**: Track all searches with similarity scores

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Navigate to project directory
cd AITextAssistant

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

**First-time setup takes 3-5 minutes** (downloads ~600MB of packages including the embedding model)

### 2. Verify Installation

```bash
python verify_installation.py
```

You should see all checks passing ✅

### 3. Run the Application

```bash
python app.py
```

### 4. Load Sample Documents

1. Click **"📁 Load Documents"** button
2. Select the `data/` folder (contains sample files)
3. Wait ~30 seconds for indexing
4. Status shows "✅ Documents loaded"

### 5. Try It Out!

**Test Suggestions:**
- Type: `"Python is used for"`
- Wait 500ms
- See 5 detailed suggestions appear in the right panel!

**Test Generate Button:**
- Type: `"ML is good"`
- Select the text
- Click **"✨ Generate"** button that appears
- Choose **"Refine Text"**
- Watch it transform!

**🎉 That's it! You're ready to go.**

---

## 📦 Installation Guide

### Prerequisites

- **Python 3.9 or higher**
- **pip** package manager
- **4GB+ RAM** (for embedding model)
- **Internet connection** (for first-time model download)
- **2GB+ free disk space**

### Detailed Installation Steps

#### 1. Verify Python Version

```bash
python --version
```

Should show: `Python 3.9.x` or higher

If not installed, download from: https://www.python.org/downloads/

#### 2. Clone or Download Project

```bash
# If using git
git clone <repository-url>
cd AITextAssistant

# Or download and extract ZIP, then navigate to folder
cd AITextAssistant
```

#### 3. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your prompt.

#### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**What gets installed:**
- `sentence-transformers` - Embedding model (~400MB)
- `faiss-cpu` - Fast similarity search
- `PySide6` - Desktop UI framework
- `PyMuPDF` - PDF processing
- `python-docx` - Word document handling
- `wikipedia` - Online fallback
- Other utilities

**Total download:** ~600MB  
**Installation time:** 3-5 minutes

#### 5. Verify Installation

```bash
python verify_installation.py
```

**Expected output:**
```
✓ PASS: Python Version
✓ PASS: Dependencies
✓ PASS: Project Structure
✓ PASS: Sample Data

🎉 All checks passed! You're ready to run the application.
```

#### Common Installation Issues

**Issue: FAISS installation fails**

Solution (use conda):
```bash
conda install -c conda-forge faiss-cpu
pip install -r requirements.txt
```

**Issue: "No module named 'sentence_transformers'"**

Solution:
```bash
pip install sentence-transformers --no-cache-dir
```

**Issue: Torch installation is slow**

Solution: This is normal, PyTorch is large (~800MB). Be patient or use a faster internet connection.

---

## 📖 How to Use

### Loading Documents

1. **Prepare Your Documents**
   - Supported formats: PDF, DOCX, TXT
   - Place them in any folder
   - No size limit, but start with 10-50 documents

2. **Load into Application**
   - Click **"📁 Load Documents"**
   - Select your folder
   - Wait for indexing (progress bar shows status)
   - Larger document sets take longer (1-2 min per 100 pages)

3. **Verification**
   - Status shows "✅ Documents loaded"
   - Number of chunks displayed in logs
   - Index saved to `models/` folder

### Getting Real-Time Suggestions

1. **Start Typing** in the editor
2. **Wait 500ms** (debounce delay)
3. **See 5 Suggestions** appear in right panel
   - Each shows 2-3 sentences
   - Includes source file name
   - Based on semantic similarity

4. **Suggestion Format:**
   ```
   ━━━ Suggestion 1 ━━━
   [From: sample_python.txt]
   Python is a high-level, interpreted programming language known for 
   its simplicity and readability. It was created by Guido van Rossum 
   and first released in 1991. Python is widely used in web development.
   ```

### Using the Generate Button

1. **Select Text** in the editor
2. **Click "✨ Generate"** button that appears
3. **Choose Action:**
   - **✍️ Refine Text**: Improve clarity and quality
   - **📝 Expand Text**: Add more detail from similar content
   - **🔄 Get Alternatives**: See different phrasings

4. **Review & Accept** - Text is automatically replaced

### Toggle Suggestions

Click **"💡 Suggestions: ON/OFF"** to enable/disable real-time suggestions.

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer (PySide6)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Editor    │  │Generate Btn  │  │  Main Window     │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Application Controller                          │
│  (Orchestrates all components)                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌──────────────┐  ┌─────────────────┐
│  Ingestion    │  │  Embeddings  │  │   Retrieval     │
│  ┌─────────┐  │  │  ┌────────┐  │  │  ┌───────────┐  │
│  │PDF Read │  │  │  │Embedder│  │  │  │Local Src  │  │
│  │DOCX Read│  │  │  │Vector  │  │  │  │Online Src │  │
│  │Chunker  │  │  │  │Store   │  │  │  │Ranker     │  │
│  └─────────┘  │  │  └────────┘  │  │  └───────────┘  │
└───────────────┘  └──────────────┘  └─────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Suggestion    │
                  │  ┌───────────┐  │
                  │  │Autocomplete│ │
                  │  │Text Replacer│ │
                  │  └───────────┘  │
                  └─────────────────┘
```

### Component Details

#### 1. Ingestion Layer (`ingestion/`)
- **PDF Reader** (`pdf_reader.py`): Extracts text from PDFs using PyMuPDF
- **DOCX Reader** (`docx_reader.py`): Extracts text from Word documents
- **Text Chunker** (`chunker.py`): Intelligently splits text at sentence/paragraph boundaries

**How it works:**
- Scans folder for supported formats
- Extracts clean text from each document
- Splits into ~512-character chunks with 50-char overlap
- Preserves metadata (filename, chunk index)

#### 2. Embeddings Layer (`embeddings/`)
- **Embedder** (`embedder.py`): Generates 384-dim vectors using `all-MiniLM-L6-v2`
- **Vector Store** (`vector_store.py`): FAISS IndexFlatIP for cosine similarity

**How it works:**
- Converts each chunk to a semantic embedding
- Normalizes vectors for cosine similarity
- Stores in FAISS index with metadata
- Saves to disk for fast reload

#### 3. Retrieval Layer (`retrieval/`)
- **Local Search** (`local_search.py`): Queries indexed documents
- **Online Search** (`online_search.py`): Wikipedia fallback
- **Ranker** (`ranker.py`): Prioritizes results (local always first)

**Priority Logic:**
```
User types text
    ↓
Search local documents (similarity threshold: 0.3)
    ↓
    ├─ Found results? → Use local only
    └─ No results? → Search Wikipedia → Combine (local first)
```

#### 4. Suggestion Layer (`suggestion/`)
- **Autocomplete** (`autocomplete.py`): Real-time suggestions
- **Text Replacer** (`text_replacer.py`): Refine/expand/alternatives

**Features:**
- Context window: 100 characters
- Debounce: 500ms
- Suggestions: 5 items, 2-3 sentences each
- Source attribution included

#### 5. UI Layer (`ui/`)
- **Editor** (`editor.py`): Enhanced QTextEdit with signals
- **Generate Button** (`generate_button.py`): Floating context menu
- **Main Window** (`main_window.py`): Application shell

**Key Features:**
- Debounced text change detection
- Background threading for indexing
- Progress feedback
- Responsive interface

---

## ⚙️ Configuration

### Configuration File: `config.yaml`

```yaml
# Document Processing
documents:
  folder_path: "./data"              # Default document folder
  supported_formats:                 # File types to index
    - pdf
    - docx
    - txt
  chunk_size: 512                    # Characters per chunk
  chunk_overlap: 50                  # Overlap between chunks

# Embedding Model
embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cpu"                      # Use "cuda" for GPU
  batch_size: 32                     # Batch size for encoding

# Vector Store
vector_store:
  index_path: "./models/faiss_index"
  dimension: 384                     # Must match model
  metric: "cosine"

# Retrieval Settings
retrieval:
  top_k_results: 5                   # Number of results to return
  similarity_threshold: 0.3          # Minimum similarity (0.0-1.0)
  max_context_length: 1500           # Max chars in context

# Suggestion Engine
suggestion:
  context_window_size: 100           # Last N chars to analyze
  trigger_threshold: 3               # Min chars to trigger
  debounce_ms: 500                   # Wait time after typing

# Online Search (Fallback)
online_search:
  enabled: true                      # Enable Wikipedia fallback
  cache_enabled: true                # Cache results
  cache_path: "./models/online_cache.pkl"
  max_results: 3                     # Max online results

# Logging
logging:
  level: "INFO"                      # DEBUG, INFO, WARNING, ERROR
  file_path: "./logs/app.log"
```

### Key Parameters to Adjust

**Get More Suggestions:**
```yaml
retrieval:
  similarity_threshold: 0.2          # Lower = more lenient (default: 0.3)
  top_k_results: 10                  # More results (default: 5)
```

**Faster Response:**
```yaml
suggestion:
  debounce_ms: 300                   # Faster trigger (default: 500)
```

**Disable Online Fallback:**
```yaml
online_search:
  enabled: false                     # Only use local documents
```

**Better Performance (GPU):**
```yaml
embedding:
  device: "cuda"                     # Requires CUDA-capable GPU
```

---

## 📁 Project Structure

```
AITextAssistant/
├── app.py                      # Main entry point
├── app_controller.py           # Central orchestrator
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
├── verify_installation.py      # Installation checker
│
├── config/                     # Configuration module
│   ├── __init__.py
│   └── settings.py             # Settings class
│
├── ingestion/                  # Document processing
│   ├── __init__.py
│   ├── pdf_reader.py           # PDF extraction
│   ├── docx_reader.py          # Word extraction
│   └── chunker.py              # Text chunking
│
├── embeddings/                 # Embedding generation
│   ├── __init__.py
│   ├── embedder.py             # Transformer wrapper
│   └── vector_store.py         # FAISS manager
│
├── retrieval/                  # Search & retrieval
│   ├── __init__.py
│   ├── local_search.py         # Local document search
│   ├── online_search.py        # Wikipedia fallback
│   └── ranker.py               # Result prioritization
│
├── suggestion/                 # Suggestion engine
│   ├── __init__.py
│   ├── autocomplete.py         # Real-time suggestions
│   └── text_replacer.py        # Text refinement
│
├── ui/                         # User interface
│   ├── __init__.py
│   ├── editor.py               # Text editor widget
│   ├── generate_button.py      # Floating button
│   └── main_window.py          # Main window
│
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── test_ingestion.py
│   ├── test_embeddings.py
│   └── test_retrieval.py
│
├── data/                       # Sample documents
│   ├── sample_python.txt
│   └── sample_ml.txt
│
├── logs/                       # Application logs
│   └── app.log                 # (generated at runtime)
│
└── models/                     # Saved models & indices
    ├── faiss_index.index       # (generated)
    ├── faiss_index.docs        # (generated)
    └── online_cache.pkl        # (generated)
```

---

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_embeddings.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Manual Testing Checklist

- [ ] Load sample documents from `data/` folder
- [ ] Type "Python programming" → Verify suggestions appear
- [ ] Type "machine learning" → Verify ML-related suggestions
- [ ] Select text → Click Generate → Test all 3 options
- [ ] Toggle suggestions ON/OFF
- [ ] Check logs at `logs/app.log`

---

## 🐛 Troubleshooting

### Installation Issues

**Problem:** `pip install` fails with "No matching distribution found"

**Solution:**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

**Problem:** FAISS installation fails on Windows

**Solution:**
```bash
# Use conda instead
conda install -c conda-forge faiss-cpu
pip install -r requirements.txt
```

---

**Problem:** "ModuleNotFoundError: No module named 'config'"

**Solution:**
```bash
# Ensure you're in the project directory
cd AITextAssistant
python app.py
```

---

### Runtime Issues

**Problem:** No suggestions appear

**Solutions:**
1. Verify documents are loaded: Status shows "✅ Documents loaded"
2. Lower similarity threshold in `config.yaml` to 0.2
3. Type at least 10 characters
4. Wait 500ms after typing
5. Check `logs/app.log` for errors

---

**Problem:** "Model download fails"

**Solution:**
```bash
# Manually download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

---

**Problem:** UI freezes during indexing

**Solution:**
- This is normal for large document sets
- Progress bar should still update
- Wait for completion
- Check logs if it takes >5 minutes for 100 pages

---

**Problem:** Suggestions are not relevant

**Solutions:**
1. Add more documents to your library
2. Lower `similarity_threshold` in config.yaml
3. Ensure documents are related to your writing topic
4. Check that documents indexed properly (see logs)

---

### Performance Issues

**Problem:** Slow search (<200ms goal)

**Solutions:**
1. Reduce `top_k_results` in config.yaml
2. Use GPU if available (`device: "cuda"`)
3. Reduce number of indexed documents
4. Check system has enough RAM

---

**Problem:** High memory usage

**Solutions:**
1. Reduce `batch_size` in config.yaml
2. Index fewer documents at once
3. Restart application to free memory
4. Close other applications

---

## 🚀 Future Enhancements

### Planned Features

#### Short-term
- [ ] Support for Markdown, HTML, RTF files
- [ ] Keyboard shortcuts (Tab to accept suggestion)
- [ ] Dark mode UI theme
- [ ] Export/import index for faster startup
- [ ] Batch document upload via drag-and-drop

#### Medium-term
- [ ] Fine-tune local LLM for better generation
- [ ] Multi-workspace support (project-specific knowledge)
- [ ] Browser extension for web-based editors
- [ ] Syntax highlighting in editor
- [ ] Search history and favorites

#### Long-term
- [ ] VS Code extension integration
- [ ] Real-time collaborative editing
- [ ] Custom domain-specific models
- [ ] Cloud sync for enterprise deployment
- [ ] Mobile app for on-the-go access

---

## 🔧 Technical Details

### Technologies Used

**Core AI/ML:**
- `sentence-transformers` - Embedding generation (all-MiniLM-L6-v2)
- `FAISS` - Fast similarity search (IndexFlatIP)
- `numpy` - Numerical operations

**Document Processing:**
- `PyMuPDF` (fitz) - PDF parsing
- `python-docx` - Word document handling

**UI Framework:**
- `PySide6` - Qt6 bindings for Python
- Signal/Slot pattern for event handling

**Online Integration:**
- `wikipedia` API - Fallback search
- `requests` + `BeautifulSoup4` - Web scraping (future)

**Utilities:**
- `loguru` - Advanced logging
- `PyYAML` - Configuration management
- `pytest` - Testing framework

### Performance Characteristics

- **Search Speed**: ~150ms average (goal: <200ms)
- **Indexing Speed**: ~2-3 pages/second
- **Memory Usage**: ~1-2GB (with model loaded)
- **Disk Usage**: ~500MB (dependencies) + ~100MB per 1000 documents

### System Requirements

**Minimum:**
- CPU: Dual-core 2.0 GHz
- RAM: 4GB
- Disk: 2GB free space
- OS: Windows 10, macOS 10.14, Ubuntu 20.04

**Recommended:**
- CPU: Quad-core 2.5 GHz+
- RAM: 8GB
- Disk: 5GB free space (SSD preferred)
- OS: Windows 11, macOS 12+, Ubuntu 22.04

---

## 📝 How It Works: Local vs Online Priority

### The Priority Logic

```
┌─────────────────────────────────────────────┐
│  1. User types text                         │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  2. Search LOCAL documents                  │
│     - Calculate similarity scores           │
│     - Filter by threshold (default: 0.3)    │
└────────────────┬────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐   ┌──────────────────────────┐
│ Found >= 1   │   │ Found 0 results          │
│ local result │   │ OR score < threshold     │
└──────┬───────┘   └──────┬───────────────────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────────────────┐
│ USE LOCAL    │   │ 3. Search ONLINE         │
│ ONLY         │   │    (Wikipedia)           │
└──────────────┘   └──────┬───────────────────┘
                          │
                          ▼
                   ┌──────────────────────────┐
                   │ 4. Combine results:      │
                   │    LOCAL first           │
                   │    ONLINE second         │
                   └──────────────────────────┘
```

**Why This Matters:**
- Your documents are ALWAYS prioritized
- Online search only when absolutely needed
- No data leakage - your content stays private
- Faster responses (local search is instant)

---

## 📄 License

This project is provided as-is for educational and personal use.

**MIT License** - Feel free to modify and extend for your needs.

---

## 🙏 Acknowledgments

This project was built using:

- **sentence-transformers** by UKPLab - Excellent embedding models
- **FAISS** by Meta AI - Lightning-fast similarity search
- **PySide6** by Qt - Modern, powerful UI framework
- **PyMuPDF** - Robust PDF processing
- **python-docx** - Reliable Word document handling
- **Wikipedia API** - Rich knowledge base for fallback

---

## 📞 Support & Contributing

### Getting Help

1. Check this README thoroughly
2. Review `logs/app.log` for error details
3. Run `python verify_installation.py`
4. Test with sample documents first

### Logs and Debugging

**Log Location:** `logs/app.log`

**View logs:**
```bash
# Windows
type logs\app.log

# macOS/Linux
cat logs/app.log

# Follow live
tail -f logs/app.log
```

**Enable debug logging:**
```yaml
# config.yaml
logging:
  level: "DEBUG"
```

---

## 🎓 Learn More

### Understanding RAG (Retrieval-Augmented Generation)

This application implements a **local-first RAG system**:

1. **Retrieval**: Find relevant chunks from your documents
2. **Augmentation**: Enrich context with similar content
3. **Generation**: Produce suggestions based on retrieved context

**Benefits:**
- More accurate than generic models
- Personalized to your writing style
- Based on verified information (your docs)
- Explainable (shows source documents)

### Key Concepts

**Embeddings:** Dense vector representations of text that capture semantic meaning.

**Similarity Search:** Finding documents with similar meaning (not just keywords).

**Chunking:** Breaking documents into smaller pieces for better retrieval granularity.

**Local-First:** Processing and storage on your device, not in the cloud.

---

## 🚦 Project Status

- ✅ **Core Features**: Complete and tested
- ✅ **Documentation**: Comprehensive
- ✅ **Performance**: Meets goals (<200ms search)
- ✅ **Production Ready**: Error handling, logging, tests
- 🔄 **Active Development**: Future enhancements planned

**Version:** 1.0.0  
**Last Updated:** January 2025

---

**Built with ❤️ for developers who value local-first AI**

**Ready to use. Ready to extend. Ready to learn from.**

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  Quick Commands                                 │
├─────────────────────────────────────────────────┤
│  Install:    pip install -r requirements.txt    │
│  Verify:     python verify_installation.py      │
│  Run:        python app.py                      │
│  Test:       pytest tests/ -v                   │
│  Logs:       cat logs/app.log                   │
├─────────────────────────────────────────────────┤
│  UI Controls                                    │
├─────────────────────────────────────────────────┤
│  📁 Load Documents  → Index your files          │
│  💡 Toggle Suggestions → ON/OFF                 │
│  ✨ Generate → Refine/Expand/Alternatives       │
├─────────────────────────────────────────────────┤
│  Key Files                                      │
├─────────────────────────────────────────────────┤
│  config.yaml        → All settings              │
│  logs/app.log       → Application logs          │
│  data/              → Your documents            │
│  models/            → Saved indices             │
└─────────────────────────────────────────────────┘
```

---

**🎉 Happy Writing with AI Text Assistant!**
