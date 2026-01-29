# AI Text Assistant

## 🎯 Project Purpose

AI Text Assistant is a **local-first intelligent writing assistant** similar to GitHub Copilot, but trained exclusively on your personal documents. It provides real-time text suggestions and content generation based on semantic understanding of your document library, with online search as a secondary fallback.

## ✨ Key Features

- 📚 **Document Ingestion**: Automatically index PDF, DOCX, and TXT files
- 🧠 **Semantic Search**: Uses sentence-transformers for high-quality embeddings
- ⚡ **Real-time Suggestions**: Copilot-style autocomplete as you type
- ✍️ **Text Refinement**: Select text and refine, expand, or get alternatives
- 🎯 **Local-First Architecture**: Prioritizes your documents over online sources
- 🌐 **Smart Fallback**: Only uses Wikipedia when local data is insufficient
- 🖥️ **Desktop UI**: Clean PySide6-based interface

---

## 🏗️ Architecture

### High-Level Architecture Diagram

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

### Module Breakdown

#### 1. **Ingestion Layer** (`ingestion/`)
- **PDF Reader**: Extracts text from PDF files using PyMuPDF
- **DOCX Reader**: Extracts text from Word documents using python-docx
- **Text Chunker**: Intelligently splits text into semantic chunks with overlap

#### 2. **Embeddings Layer** (`embeddings/`)
- **Embedder**: Generates 384-dimensional embeddings using `all-MiniLM-L6-v2`
- **Vector Store**: FAISS-based index for fast similarity search (<200ms)

#### 3. **Retrieval Layer** (`retrieval/`)
- **Local Search**: Searches indexed documents by semantic similarity
- **Online Search**: Wikipedia fallback when local similarity < threshold
- **Ranker**: Prioritizes results (local always first)

#### 4. **Suggestion Layer** (`suggestion/`)
- **Autocomplete**: Generates real-time text suggestions
- **Text Replacer**: Refines, expands, or finds alternatives for selected text

#### 5. **UI Layer** (`ui/`)
- **Editor**: Enhanced QTextEdit with debounced change detection
- **Generate Button**: Floating button for text operations
- **Main Window**: Application shell with all controls

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9 or higher
- 4GB+ RAM (for embedding model)
- Windows, macOS, or Linux

### Installation

1. **Clone or download the project**:
   ```bash
   cd AITextAssistant
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify configuration**:
   Edit `config.yaml` to adjust settings (optional).

### Running the Application

```bash
python app.py
```

---

## 📖 How to Use

### 1. Load Documents

1. Click **"📁 Load Documents"** button
2. Select a folder containing PDF, DOCX, or TXT files
3. Wait for indexing to complete (progress bar shows status)

### 2. Get Real-Time Suggestions

1. Start typing in the editor
2. Suggestions appear in the right panel after ~500ms
3. Suggestions are based on semantic similarity to your documents

### 3. Refine Selected Text

1. Select text in the editor
2. Click the **"✨ Generate"** button that appears
3. Choose an action:
   - **✍️ Refine Text**: Improve clarity/quality
   - **📝 Expand Text**: Add more detail
   - **🔄 Get Alternatives**: See alternative phrasings

### 4. Toggle Suggestions

- Click **"💡 Suggestions: ON/OFF"** to enable/disable real-time suggestions

---

## ⚙️ How Prioritization Works (Local vs Online)

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

### Configuration

Edit `config.yaml` to adjust:

```yaml
retrieval:
  similarity_threshold: 0.3  # Lower = more lenient (0.0-1.0)
  top_k_results: 5           # Number of results to return

online_search:
  enabled: true              # Set to false to disable online fallback
```

### Logging

All searches are logged with:
- Similarity score
- Source (local file name or "wikipedia")
- Timestamp

Check `logs/app.log` for details.

---

## 📁 Project Structure

```
AITextAssistant/
├── app.py                      # Main entry point
├── app_controller.py           # Application orchestrator
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
│
├── config/                     # Configuration management
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
│   ├── embedder.py             # Sentence transformer wrapper
│   └── vector_store.py         # FAISS index manager
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
│   └── main_window.py          # Main application window
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
│   └── app.log
│
└── models/                     # Saved models & indices
    ├── faiss_index.index       # FAISS vector index
    ├── faiss_index.docs        # Document metadata
    └── online_cache.pkl        # Cached online searches
```

---

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Test Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

### Manual Testing

1. Load the sample documents from `data/`
2. Type "Python programming" → Should suggest Python-related content
3. Type "machine learning" → Should suggest ML-related content
4. Select text and use Generate button

---

## 🔧 Configuration Reference

### `config.yaml` Sections

#### Documents
```yaml
documents:
  folder_path: "./data"              # Where to scan for documents
  supported_formats: [pdf, docx, txt]
  chunk_size: 512                     # Characters per chunk
  chunk_overlap: 50                   # Overlap between chunks
```

#### Embedding Model
```yaml
embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cpu"                       # Use "cuda" for GPU
  batch_size: 32
```

#### Vector Store
```yaml
vector_store:
  index_path: "./models/faiss_index"
  dimension: 384                      # Must match model
  metric: "cosine"
```

#### Retrieval
```yaml
retrieval:
  top_k_results: 5                    # Results to return
  similarity_threshold: 0.3           # Minimum similarity (0.0-1.0)
  max_context_length: 1500            # Max chars in context
```

#### Suggestion Engine
```yaml
suggestion:
  context_window_size: 100            # Last N chars to analyze
  trigger_threshold: 3                # Min chars to trigger
  debounce_ms: 500                    # Wait time after typing
```

#### Online Search
```yaml
online_search:
  enabled: true
  cache_enabled: true                 # Cache Wikipedia results
  cache_path: "./models/online_cache.pkl"
  max_results: 3
```

---

## 🐛 Troubleshooting

### Issue: Model download fails

**Solution**: Check internet connection. The model (~80MB) downloads on first run.

```bash
# Manually download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Issue: FAISS installation fails

**Solution**: Install via conda:

```bash
conda install -c conda-forge faiss-cpu
```

### Issue: UI doesn't respond

**Solution**: Check logs at `logs/app.log`. Ensure PySide6 is installed correctly.

### Issue: No suggestions appear

**Solution**: 
1. Verify documents are loaded (status shows "✅ Documents loaded")
2. Check similarity threshold in `config.yaml` (try lowering to 0.2)
3. Ensure you've typed enough context (>10 characters)

---

## 🚀 Future Improvements

### Short-term Enhancements
- [ ] Add support for more file formats (Markdown, HTML, RTF)
- [ ] Implement keyboard shortcuts for accepting suggestions
- [ ] Add dark mode UI theme
- [ ] Export/import index for faster startup

### Medium-term Features
- [ ] Fine-tune local LLM for better text generation
- [ ] Multi-workspace support (project-specific knowledge)
- [ ] Browser extension for web-based editors
- [ ] Collaborative knowledge sharing

### Long-term Vision
- [ ] VS Code extension integration
- [ ] Real-time collaborative editing
- [ ] Custom domain-specific models
- [ ] Cloud sync for enterprise deployment

---

## 📄 License

This project is provided as-is for educational and personal use.

---

## 🙏 Acknowledgments

### Technologies Used

- **sentence-transformers**: Embedding generation
- **FAISS**: Fast similarity search
- **PySide6**: Modern Qt bindings
- **PyMuPDF**: PDF processing
- **python-docx**: Word document handling
- **Wikipedia API**: Online fallback

---

## 📞 Support

For issues or questions:

1. Check `logs/app.log` for error details
2. Review configuration in `config.yaml`
3. Ensure all dependencies are installed
4. Test with sample documents first

---

**Built with ❤️ for local-first AI assistance**

---

## Quick Start Guide

### First-Time Setup (5 minutes)

1. **Install**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run**:
   ```bash
   python app.py
   ```

3. **Load Samples**:
   - Click "📁 Load Documents"
   - Select the `data/` folder
   - Wait ~30 seconds for indexing

4. **Try It**:
   - Type: "Python is used for"
   - See suggestions appear!
   - Select text → Click "✨ Generate"

**That's it! You're ready to go.** 🎉
