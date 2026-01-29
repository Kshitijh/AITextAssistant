"""
Installation Verification Script
Run this to verify your installation is correct.
"""

import sys
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ required")
        return False
    return True


def check_dependencies():
    """Check if all required packages are installed."""
    required = [
        'sentence_transformers',
        'faiss',
        'PySide6',
        'fitz',  # PyMuPDF
        'docx',
        'wikipedia',
        'yaml',
        'loguru',
        'numpy',
        'pytest'
    ]
    
    missing = []
    installed = []
    
    for package in required:
        try:
            __import__(package)
            installed.append(package)
        except ImportError:
            missing.append(package)
    
    print(f"\n✓ Installed packages: {len(installed)}/{len(required)}")
    for pkg in installed:
        print(f"  ✓ {pkg}")
    
    if missing:
        print(f"\n❌ Missing packages: {len(missing)}")
        for pkg in missing:
            print(f"  ❌ {pkg}")
        return False
    
    return True


def check_project_structure():
    """Check if all required directories and files exist."""
    required_dirs = [
        'config',
        'ingestion',
        'embeddings',
        'retrieval',
        'suggestion',
        'ui',
        'tests',
        'data',
        'logs',
        'models'
    ]
    
    required_files = [
        'app.py',
        'app_controller.py',
        'config.yaml',
        'requirements.txt',
        'README.md'
    ]
    
    root = Path(__file__).parent
    
    print("\nChecking project structure...")
    
    all_good = True
    
    # Check directories
    for dir_name in required_dirs:
        dir_path = root / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ (missing)")
            all_good = False
    
    # Check files
    for file_name in required_files:
        file_path = root / file_name
        if file_path.exists():
            print(f"  ✓ {file_name}")
        else:
            print(f"  ❌ {file_name} (missing)")
            all_good = False
    
    return all_good


def check_sample_data():
    """Check if sample data exists."""
    data_dir = Path(__file__).parent / 'data'
    
    if not data_dir.exists():
        print("\n❌ data/ directory not found")
        return False
    
    files = list(data_dir.glob('*.txt'))
    
    if len(files) > 0:
        print(f"\n✓ Found {len(files)} sample document(s):")
        for f in files:
            print(f"  ✓ {f.name}")
        return True
    else:
        print("\n⚠ No sample documents found in data/")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("AI Text Assistant - Installation Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Sample Data", check_sample_data)
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        result = check_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the application.")
        print("\nNext steps:")
        print("  1. Run: python app.py")
        print("  2. Click 'Load Documents'")
        print("  3. Select the 'data/' folder")
        print("  4. Start typing!")
    else:
        print("\n⚠ Some checks failed. Please fix the issues above.")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
