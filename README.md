# AI Text Assistant

<div align="center">

🤖 **A Local AI-Powered Writing Assistant**

*Smart autocomplete suggestions based on your documents - works completely offline!*

</div>

---

## 📋 Overview

AI Text Assistant is a powerful desktop application that provides intelligent writing suggestions based on your own documents. It works like GitHub Copilot but for any text editor - Notepad, Word, VS Code, and more!

### ✨ Key Features

- 📚 **Document-Based Learning**: Analyzes PDF, DOCX, and TXT files
- 🔍 **Semantic Search**: Uses embeddings and FAISS for intelligent context retrieval
- 🤖 **Local LLM**: Runs GPT4All models completely offline
- ⌨️ **Global Typing Detection**: Works across all applications
- 💡 **Smart Suggestions**: RAG-powered completions that understand your documents
- 🎨 **Modern UI**: Clean PyQt5 interface with dark mode
- 🔒 **Privacy First**: Everything runs locally - no data leaves your machine

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Text Assistant                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Document   │  │   Embedder   │  │    Vector    │     │
│  │    Loader    │─▶│ (Sentence-   │─▶│    Store     │     │
│  │  (PDF/DOCX)  │  │ Transformers)│  │   (FAISS)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                                      │            │
│         ▼                                      ▼            │
│  ┌──────────────────────────────────────────────────┐      │
│  │          Suggestion Engine (RAG + LLM)           │      │
│  │                   (GPT4All)                      │      │
│  └──────────────────────────────────────────────────┘      │
│         │                                      ▲            │
│         ▼                                      │            │
│  ┌──────────────┐                    ┌────────────────┐    │
│  │  Suggestion  │                    │   Keystroke    │    │
│  │   Overlay    │◀───────────────────│    Listener    │    │
│  │   (PyQt5)    │                    │   (pynput)     │    │
│  └──────────────┘                    └────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+** (recommended: Python 3.11)
- **Windows** (currently optimized for Windows)
- **4GB+ RAM** (8GB recommended for better performance)
- **2GB free disk space** (for models and index)

### Step 1: Clone or Download

```bash
cd d:\Workspace\AITextAssistant
```

### Step 2: Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: Installation may take 10-15 minutes as it downloads the embedding model and dependencies.

### Step 4: Download LLM Model

The application uses GPT4All. On first run, it will automatically download the model (~2GB). You can also manually download:

1. Visit: https://gpt4all.io/
2. Download a model (recommended: `orca-mini-3b-gguf2-q4_0.gguf` or `mistral-7b-openorca.Q4_0.gguf`)
3. Place in `d:\Workspace\AITextAssistant\models\`
4. Update model name in [config.yaml](config.yaml)

---

## 📖 Usage Guide

### 1️⃣ Add Your Documents

1. Place your documents (PDF, DOCX, TXT) in the `data` folder
2. You can organize them in subfolders if needed
3. Supported formats:
   - **PDF**: Research papers, ebooks, reports
   - **DOCX**: Word documents, templates
   - **TXT**: Plain text notes, code, documentation

### 2️⃣ Launch the Application

```powershell
python main.py
```

### 3️⃣ Build the Index

1. Click **"Build Index"** button
2. Wait for processing (depends on document count)
3. The app will:
   - Extract text from all documents
   - Split into chunks
   - Generate embeddings
   - Build FAISS vector database
   - Save for future use

### 4️⃣ Start the Assistant

1. Click **"Start Assistant"** button
2. The status will show: 🟢 **Running**
3. Open any text editor (Notepad, Word, VS Code, etc.)
4. Start typing...

### 5️⃣ Using Suggestions

- **Type naturally** - suggestions appear after punctuation
- **TAB** - Accept current suggestion
- **ESC** - Dismiss suggestions
- **↑/↓** - Navigate multiple suggestions (if available)

---

## ⚙️ Configuration

Edit [config.yaml](config.yaml) to customize:

### Document Processing
```yaml
documents:
  folder_path: "./data"
  chunk_size: 750          # Characters per chunk
  chunk_overlap: 100       # Overlap between chunks
```

### Embedding Model
```yaml
embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cpu"            # or "cuda" for GPU
```

### LLM Settings
```yaml
llm:
  backend: "gpt4all"
  model_name: "orca-mini-3b-gguf2-q4_0.gguf"
  temperature: 0.7         # Creativity (0.0-1.0)
  max_tokens: 100          # Max suggestion length
```

### Suggestion Behavior
```yaml
listener:
  trigger_threshold: 10    # Characters before triggering
  debounce_ms: 300        # Delay before suggestion

overlay:
  font_size: 12
  opacity: 0.95
  max_suggestions: 3
```

---

## 📁 Project Structure

```
AITextAssistant/
├── main.py                     # Application entry point
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── config.py              # Configuration manager
│   ├── document_loader.py     # Document parsing (PDF/DOCX/TXT)
│   ├── embedder.py            # Sentence embeddings
│   ├── vector_store.py        # FAISS vector database
│   ├── suggestion_engine.py   # RAG + LLM generation
│   ├── keystroke_listener.py  # Global keyboard capture
│   ├── suggestion_overlay.py  # Floating suggestion window
│   └── ui.py                  # Main PyQt5 interface
│
├── data/                       # Place your documents here
│   └── .gitkeep
│
├── models/                     # LLM models and FAISS index
│   └── .gitkeep
│
└── logs/                       # Application logs
    └── .gitkeep
```

---

## 🔧 Troubleshooting

### Issue: "No suggestions appearing"

**Solutions:**
1. Check that index is built and loaded
2. Verify assistant is running (green status)
3. Ensure you have documents in `data` folder
4. Check logs in `logs/app.log`

### Issue: "Import errors"

**Solutions:**
```powershell
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue: "LLM model not found"

**Solutions:**
1. Let it auto-download on first run
2. Or manually download from https://gpt4all.io/
3. Place in `models/` folder
4. Update `config.yaml` with correct filename

### Issue: "High memory usage"

**Solutions:**
1. Use smaller LLM model (e.g., `orca-mini-3b`)
2. Reduce `chunk_size` in config
3. Limit number of documents
4. Close other applications

### Issue: "Slow suggestions"

**Solutions:**
1. Reduce `rag.top_k_results` in config
2. Use CPU-optimized model
3. Reduce `max_tokens` for faster generation
4. Consider upgrading hardware

---

## 🎯 Performance Tips

### For Best Performance:

1. **Use SSD** for faster index loading
2. **8GB+ RAM** for comfortable operation
3. **GPU** (optional): Set `device: "cuda"` in config
4. **Smaller models**: Trade quality for speed
5. **Limit documents**: Start with ~50-100 documents

### Optimization Settings:

```yaml
performance:
  use_gpu: false              # Enable if you have NVIDIA GPU
  num_threads: 4              # CPU cores to use
  cache_embeddings: true      # Faster repeated queries
```

---

## 🛠️ Advanced Features

### Custom LLM Models

You can use other GPT4All models:

1. Download from https://gpt4all.io/
2. Supported formats: `.gguf`, `.bin`
3. Update `config.yaml`:

```yaml
llm:
  model_name: "your-model-name.gguf"
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `TAB` | Accept suggestion |
| `ESC` | Dismiss suggestion |
| `↑` | Previous suggestion |
| `↓` | Next suggestion |

### Multiple Suggestions

The overlay shows up to 3 alternative suggestions. Navigate with arrow keys.

---

## 📊 System Requirements

### Minimum:
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Storage: 2 GB free
- OS: Windows 10

### Recommended:
- CPU: Quad-core 2.5 GHz+
- RAM: 8 GB+
- Storage: 5 GB free (SSD)
- OS: Windows 10/11
- GPU: NVIDIA (optional, for CUDA)

---

## 🐛 Known Limitations

1. **Windows Only**: Currently optimized for Windows (Linux/Mac support planned)
2. **LLM Speed**: Generation may take 1-3 seconds on CPU
3. **Text Insertion**: Suggestions are shown but not auto-inserted (requires additional permissions)
4. **Language**: Best performance with English documents
5. **Context Window**: Limited to last 200 characters

---

## 🔮 Future Enhancements

- [ ] Auto-insert accepted suggestions
- [ ] Multi-language support
- [ ] Llama.cpp backend option
- [ ] Cloud sync for index
- [ ] Chrome extension version
- [ ] Voice input support
- [ ] Advanced filtering options
- [ ] Export/import settings

---

## 📝 Logs & Debugging

Logs are stored in `logs/app.log`:

```powershell
# View latest logs
Get-Content .\logs\app.log -Tail 50

# Monitor logs in real-time
Get-Content .\logs\app.log -Wait
```

Log levels in [config.yaml](config.yaml):
- `DEBUG`: Verbose output
- `INFO`: Normal operation (default)
- `WARNING`: Issues that don't stop execution
- `ERROR`: Serious problems

---

## 🤝 Contributing

This is a complete working system. Feel free to:
- Report bugs
- Suggest features
- Submit improvements
- Share your experience

---

## 📄 License

This project is provided as-is for educational and personal use.

---

## 🙏 Acknowledgments

Built with:
- **sentence-transformers**: Semantic embeddings
- **FAISS**: Vector similarity search
- **GPT4All**: Local LLM inference
- **PyQt5**: Desktop UI framework
- **pynput**: Global keyboard monitoring
- **PyMuPDF**: PDF processing
- **python-docx**: Word document parsing

---

## 📞 Support

For issues, check:
1. This README
2. [config.yaml](config.yaml) documentation
3. Log files in `logs/`
4. Error messages in UI

---

<div align="center">

**Built with ❤️ for offline-first AI assistance**

*Happy Writing! ✍️*

</div>
