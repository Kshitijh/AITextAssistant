# Installation Guide

## 🚀 Complete Installation Instructions

### Prerequisites

Before you begin, ensure you have:

- **Python 3.9 or higher** installed
- **pip** package manager
- **4GB+ RAM** (for embedding model)
- **Internet connection** (for first-time model download)

### Step-by-Step Installation

#### 1. Verify Python Installation

Open a terminal/command prompt and run:

```bash
python --version
```

You should see: `Python 3.9.x` or higher

If not installed, download from: https://www.python.org/downloads/

---

#### 2. Navigate to Project Directory

```bash
cd d:\Workspace\AITextAssistant
```

---

#### 3. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

#### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected time:** 3-5 minutes (depending on internet speed)

**What gets installed:**
- sentence-transformers (~400MB)
- faiss-cpu (~20MB)
- PySide6 (~100MB)
- PyMuPDF, python-docx, and other utilities
- Total: ~600MB

**Common Issues:**

**Issue:** FAISS installation fails  
**Solution:** Use conda instead:
```bash
conda install -c conda-forge faiss-cpu
pip install -r requirements.txt --no-deps faiss-cpu
```

**Issue:** Torch installation is slow  
**Solution:** Normal - PyTorch is large (~800MB). Be patient.

---

#### 5. Verify Installation

Run the verification script:

```bash
python verify_installation.py
```

You should see all checks passing:
```
✓ PASS: Python Version
✓ PASS: Dependencies
✓ PASS: Project Structure
✓ PASS: Sample Data
```

---

#### 6. First Run

```bash
python app.py
```

**First run will:**
1. Download the embedding model (~80MB) - **one-time only**
2. Initialize logging
3. Open the application window

**Expected startup time:**
- First run: ~30 seconds (model download)
- Subsequent runs: ~5 seconds

---

### Post-Installation Setup

#### Load Sample Documents

1. Click **"📁 Load Documents"** in the toolbar
2. Navigate to the `data/` folder in the project directory
3. Click "Select Folder"
4. Wait ~30 seconds for indexing

You should see:
- Progress bar moving from 0% to 100%
- Status changing to "✅ Documents loaded"
- Log messages in the terminal

#### Test the Application

1. **Test Suggestions:**
   - Type: `"Python is used for"`
   - Wait 500ms
   - See suggestions appear in the right panel

2. **Test Generate Button:**
   - Type: `"ML is good"`
   - Select the text
   - Click the "✨ Generate" button
   - Choose "Refine Text"
   - See the text improve

---

## 🔧 Configuration

### Basic Configuration

Edit `config.yaml` to customize:

```yaml
# Adjust similarity threshold (lower = more suggestions)
retrieval:
  similarity_threshold: 0.3  # Try 0.2 for more suggestions

# Change typing delay
suggestion:
  debounce_ms: 500  # Milliseconds to wait after typing

# Disable online fallback
online_search:
  enabled: false  # Only use local documents
```

---

## 📊 System Requirements

### Minimum Requirements

- **CPU:** Dual-core 2.0 GHz
- **RAM:** 4GB
- **Disk:** 2GB free space
- **OS:** Windows 10, macOS 10.14, Ubuntu 20.04

### Recommended Requirements

- **CPU:** Quad-core 2.5 GHz or better
- **RAM:** 8GB
- **Disk:** 5GB free space (SSD preferred)
- **OS:** Windows 11, macOS 12+, Ubuntu 22.04

---

## 🐛 Troubleshooting

### Installation Issues

**Problem:** `pip install` fails with "No matching distribution found"

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

**Problem:** Import error when running app

**Solution:**
```bash
# Verify all packages installed
pip list | grep -E "(sentence|faiss|PySide6)"

# Reinstall if missing
pip install -r requirements.txt --force-reinstall
```

---

**Problem:** "ModuleNotFoundError: No module named 'config'"

**Solution:**
```bash
# Ensure you're in the project directory
cd d:\Workspace\AITextAssistant
python app.py
```

---

### Runtime Issues

**Problem:** No suggestions appear

**Solutions:**
1. Check if documents are loaded (status shows "✅")
2. Lower similarity threshold in config.yaml
3. Type at least 10 characters
4. Wait 500ms after typing
5. Check logs: `logs/app.log`

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
- Check logs if it takes >5 minutes

---

## 📝 Logs and Debugging

### Log Files

Logs are written to: `logs/app.log`

**View logs:**
```bash
# Windows
type logs\app.log

# macOS/Linux
cat logs/app.log

# Follow live logs
tail -f logs/app.log
```

### Log Levels

Change in `config.yaml`:
```yaml
logging:
  level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_embeddings.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 🔄 Updating

To update the application:

```bash
# Pull latest changes (if using git)
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Run verification
python verify_installation.py
```

---

## ❓ Getting Help

1. **Check logs:** `logs/app.log`
2. **Verify installation:** `python verify_installation.py`
3. **Read documentation:** `README.md`
4. **Test with samples:** Use files in `data/`

---

## ✅ Installation Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Verification script passed (`python verify_installation.py`)
- [ ] Application starts (`python app.py`)
- [ ] Sample documents loaded
- [ ] Suggestions working
- [ ] Generate button working

---

**Congratulations! You're all set up.** 🎉

For usage instructions, see [README.md](README.md)  
For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md)
