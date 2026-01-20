# Quick Start Guide - AI Text Assistant

## 🚀 Quick Setup (5 Minutes)

### 1. Install Python Dependencies

```powershell
# Navigate to project folder
cd d:\Workspace\AITextAssistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Add Sample Documents

```powershell
# Create some sample text files for testing
New-Item -Path ".\data\sample1.txt" -ItemType File
Set-Content -Path ".\data\sample1.txt" -Value "AI and machine learning are transforming the world. Deep learning models can process vast amounts of data. Natural language processing enables computers to understand human language."

New-Item -Path ".\data\sample2.txt" -ItemType File
Set-Content -Path ".\data\sample2.txt" -Value "Python is a versatile programming language. It is widely used for data science, web development, and automation. Python's syntax is clean and readable."
```

Or simply copy your own PDF, DOCX, or TXT files to the `data` folder.

### 3. Run the Application

```powershell
python main.py
```

### 4. First-Time Setup in UI

1. **Build Index**:
   - Click "Build Index" button
   - Wait for processing (1-2 minutes for small datasets)
   - You'll see: "Index built successfully"

2. **Start Assistant**:
   - Click "Start Assistant" button
   - Status changes to 🟢 Running
   - LLM model downloads automatically (first time only, ~2GB)

3. **Test It**:
   - Open Notepad or any text editor
   - Start typing: "Python is a programming"
   - Wait for suggestion overlay
   - Press TAB to accept

## ⚡ Common Commands

```powershell
# Start the app
python main.py

# View logs
Get-Content .\logs\app.log -Tail 20

# Check Python version
python --version

# List installed packages
pip list

# Update dependencies
pip install -r requirements.txt --upgrade
```

## 🎯 Testing the Assistant

### Test Text to Type:

Try typing these in Notepad to see suggestions:

1. "Machine learning is"
2. "Python programming"
3. "Natural language"
4. "Data science requires"

The assistant will suggest completions based on your documents!

## 🐛 Quick Fixes

### Problem: Virtual environment not activating
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

### Problem: Module not found errors
```powershell
pip install -r requirements.txt --force-reinstall
```

### Problem: No suggestions appearing
1. Check that index is built (shows chunk count)
2. Ensure assistant is running (green status)
3. Type more than 10 characters
4. End sentence with space or punctuation

## 📊 First Run Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Documents in `data` folder
- [ ] Application launched
- [ ] Index built successfully
- [ ] Assistant started
- [ ] Test in Notepad works

## 🎓 Next Steps

1. Read full [README.md](README.md)
2. Customize [config.yaml](config.yaml)
3. Add your own documents
4. Experiment with settings
5. Review logs for insights

---

**Need Help?** Check [README.md](README.md) for detailed documentation.
