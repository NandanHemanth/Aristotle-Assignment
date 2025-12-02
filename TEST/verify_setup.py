"""
Quick verification script to check if all dependencies are installed
and the app is ready to run.
"""

import sys

def check_imports():
    """Check if all required packages are installed."""
    required_packages = {
        'streamlit': 'streamlit',
        'PIL': 'pillow',
        'PyPDF2': 'PyPDF2',
        'docx': 'python-docx',
        'requests': 'requests',
        'youtube_transcript_api': 'youtube-transcript-api',
        'bs4': 'beautifulsoup4',
        'dotenv': 'python-dotenv',
    }
    
    missing = []
    installed = []
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            installed.append(f"✅ {package}")
        except ImportError:
            missing.append(f"❌ {package}")
    
    print("=" * 50)
    print("DEPENDENCY CHECK")
    print("=" * 50)
    
    for pkg in installed:
        print(pkg)
    
    if missing:
        print("\nMissing packages:")
        for pkg in missing:
            print(pkg)
        print("\nRun: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True

def check_env():
    """Check if .env file exists and has API key."""
    import os
    from pathlib import Path
    
    print("\n" + "=" * 50)
    print("ENVIRONMENT CHECK")
    print("=" * 50)
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        print("   Then add your OPENROUTER_API_KEY")
        return False
    
    print("✅ .env file exists")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("❌ OPENROUTER_API_KEY not set in .env")
        print("   Edit .env and add your API key")
        return False
    
    print("✅ OPENROUTER_API_KEY is set")
    return True

def check_files():
    """Check if all required files exist."""
    from pathlib import Path
    
    print("\n" + "=" * 50)
    print("FILE CHECK")
    print("=" * 50)
    
    required_files = [
        'app.py',
        'tutoring_engine.py',
        'content_extractors.py',
        'openrouter_client.py',
        'config.py',
        'utils.py',
        'requirements.txt',
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            all_exist = False
    
    return all_exist

def main():
    """Run all checks."""
    print("\n🎓 ARISTOTLE AI TUTOR - SETUP VERIFICATION\n")
    
    deps_ok = check_imports()
    env_ok = check_env()
    files_ok = check_files()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if deps_ok and env_ok and files_ok:
        print("✅ Everything is ready!")
        print("\nTo start the app, run:")
        print("   streamlit run app.py")
        return 0
    else:
        print("❌ Some issues need to be fixed")
        print("\nPlease address the issues above and run this script again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
