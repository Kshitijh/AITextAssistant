"""
AI Model Trainer and Setup
Prepares the AI Text Assistant for intelligent text generation.
"""

from pathlib import Path
from loguru import logger
import sys

def setup_ai_model():
    """Interactive setup for AI text generation."""
    
    print("=" * 60)
    print("  AI Text Assistant - AI Model Setup")
    print("=" * 60)
    print()
    
    # Check if llama-cpp-python is installed
    try:
        import llama_cpp
        print("✅ llama-cpp-python is installed")
    except ImportError:
        print("❌ llama-cpp-python not found")
        print()
        print("Installing llama-cpp-python...")
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "llama-cpp-python"], 
                              capture_output=True)
        if result.returncode == 0:
            print("✅ Installation successful!")
        else:
            print("❌ Installation failed. Please run manually:")
            print("   pip install llama-cpp-python")
            return False
    
    print()
    
    # Check for model files
    models_dir = Path("./models")
    models_dir.mkdir(exist_ok=True)
    
    gguf_files = list(models_dir.glob("*.gguf"))
    
    if gguf_files:
        print(f"✅ Found {len(gguf_files)} model file(s):")
        for model in gguf_files:
            size_mb = model.stat().st_size / (1024 * 1024)
            print(f"   - {model.name} ({size_mb:.1f} MB)")
        print()
        print("Your AI is ready to generate text! 🤖")
    else:
        print("❌ No AI model found")
        print()
        print("📥 To enable AI text generation, download a model:")
        print()
        print("RECOMMENDED MODELS:")
        print()
        print("1. TinyLlama (~700MB) - Fast, good for quick responses")
        print("   https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF")
        print("   Download: TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf")
        print()
        print("2. Phi-3 Mini (~2GB) - RECOMMENDED - Best balance")
        print("   https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf")
        print("   Download: Phi-3-mini-4k-instruct-q4.gguf")
        print()
        print("3. Mistral 7B (~4GB) - Highest quality")
        print("   https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF")
        print("   Download: mistral-7b-instruct-v0.2.Q4_K_M.gguf")
        print()
        print(f"📁 Place the downloaded .gguf file in: {models_dir.absolute()}")
        print()
        print("Without a model, the system uses template-based suggestions")
        print("(still works well, just not AI-powered)")
    
    print()
    print("=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Add documents to the 'data' folder")
    print("2. Run: python app.py")
    print("3. Click 'Process Documents'")
    print("4. Start typing anywhere!")
    print()
    
    return True


def train_on_documents():
    """
    Train/index documents for the AI system.
    Note: We don't actually 'train' the LLM, but we build the RAG index.
    """
    
    print("=" * 60)
    print("  Processing Documents for AI")
    print("=" * 60)
    print()
    
    from ingestion.pdf_reader import PDFReader
    from ingestion.docx_reader import DOCXReader
    from ingestion.chunker import Chunker
    from embeddings.embedder import Embedder
    from embeddings.vector_store import VectorStore
    from retrieval.local_search import LocalSearch
    from config.settings import config
    
    try:
        # Initialize components
        pdf_reader = PDFReader()
        docx_reader = DOCXReader()
        chunker = Chunker()
        embedder = Embedder()
        
        # Check for documents
        data_folder = Path(config.data_folder)
        if not data_folder.exists():
            data_folder.mkdir(parents=True, exist_ok=True)
            print(f"❌ No documents found!")
            print(f"   Add documents to: {data_folder.absolute()}")
            return False
        
        # Find all documents
        pdf_files = list(data_folder.glob("**/*.pdf"))
        docx_files = list(data_folder.glob("**/*.docx"))
        txt_files = list(data_folder.glob("**/*.txt"))
        
        all_files = pdf_files + docx_files + txt_files
        
        if not all_files:
            print("❌ No documents found!")
            print(f"   Add PDF, DOCX, or TXT files to: {data_folder.absolute()}")
            return False
        
        print(f"📚 Found {len(all_files)} documents:")
        print(f"   - {len(pdf_files)} PDFs")
        print(f"   - {len(docx_files)} DOCX files")
        print(f"   - {len(txt_files)} TXT files")
        print()
        
        # Process documents
        all_chunks = []
        
        print("📖 Reading documents...")
        for pdf_file in pdf_files:
            try:
                text = pdf_reader.read(str(pdf_file))
                chunks = chunker.chunk_text(text, source=pdf_file.name)
                all_chunks.extend(chunks)
                print(f"   ✓ {pdf_file.name} ({len(chunks)} chunks)")
            except Exception as e:
                print(f"   ✗ {pdf_file.name} - Error: {e}")
        
        for docx_file in docx_files:
            try:
                text = docx_reader.read(str(docx_file))
                chunks = chunker.chunk_text(text, source=docx_file.name)
                all_chunks.extend(chunks)
                print(f"   ✓ {docx_file.name} ({len(chunks)} chunks)")
            except Exception as e:
                print(f"   ✗ {docx_file.name} - Error: {e}")
        
        for txt_file in txt_files:
            try:
                text = txt_file.read_text(encoding='utf-8')
                chunks = chunker.chunk_text(text, source=txt_file.name)
                all_chunks.extend(chunks)
                print(f"   ✓ {txt_file.name} ({len(chunks)} chunks)")
            except Exception as e:
                print(f"   ✗ {txt_file.name} - Error: {e}")
        
        if not all_chunks:
            print("❌ No content extracted from documents!")
            return False
        
        print()
        print(f"✅ Processed {len(all_chunks)} chunks total")
        print()
        
        # Generate embeddings
        print("🧠 Generating embeddings...")
        texts = [chunk['text'] for chunk in all_chunks]
        embedder.fit(texts)
        
        embeddings = embedder.embed_batch(texts)
        print(f"✅ Generated {len(embeddings)} embeddings")
        print()
        
        # Build search index
        print("🔍 Building search index...")
        vector_store = VectorStore()
        vector_store.add_documents(embeddings, all_chunks)
        
        # Save
        models_dir = Path(config.model_save_path).parent
        models_dir.mkdir(parents=True, exist_ok=True)
        
        embedder.save(str(models_dir / "embedder.joblib"))
        vector_store.save(str(models_dir / "vector_store.pkl"))
        
        print("✅ Index built and saved successfully!")
        print()
        print("=" * 60)
        print("  Your AI is now trained on your documents! 🎓")
        print("=" * 60)
        print()
        print("The system will now:")
        print("  • Understand your document content")
        print("  • Provide context-aware suggestions")
        print("  • Generate text based on your knowledge base")
        print()
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing documents: {e}")
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    print("🤖 AI Text Assistant - Training & Setup")
    print()
    
    # Setup AI model
    setup_ai_model()
    
    print()
    choice = input("Do you want to process documents now? (y/n): ").lower().strip()
    
    if choice == 'y':
        print()
        train_on_documents()
    else:
        print()
        print("You can process documents later by running:")
        print("  python app.py")
        print("  Then click 'Process Documents' button")
    
    print()
    print("✨ All done! Your AI writing assistant is ready!")
    print()
