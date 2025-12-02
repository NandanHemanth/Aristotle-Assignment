"""
Quick test to verify the UI components load correctly
"""

import sys

def test_imports():
    """Test all imports work."""
    print("Testing imports...")
    try:
        import streamlit as st
        print("✅ streamlit")
        
        from tutoring_engine import TutoringEngine
        print("✅ tutoring_engine")
        
        from utils import process_uploaded_file, encode_image_to_base64
        print("✅ utils")
        
        from content_extractors import extract_content
        print("✅ content_extractors")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_session_state():
    """Test session state initialization."""
    print("\nTesting session state...")
    try:
        from tutoring_engine import TutoringEngine
        
        engine = TutoringEngine()
        print("✅ TutoringEngine initialized")
        
        sources = []
        messages = []
        problem_loaded = False
        
        print("✅ Session state variables created")
        return True
    except Exception as e:
        print(f"❌ Session state error: {e}")
        return False

def test_file_processing():
    """Test file processing functions."""
    print("\nTesting file processing...")
    try:
        from utils import extract_text_from_pdf, extract_text_from_docx
        print("✅ PDF extraction function available")
        print("✅ DOCX extraction function available")
        return True
    except Exception as e:
        print(f"❌ File processing error: {e}")
        return False

def test_content_extraction():
    """Test content extraction."""
    print("\nTesting content extraction...")
    try:
        from content_extractors import YouTubeExtractor, URLExtractor
        print("✅ YouTubeExtractor available")
        print("✅ URLExtractor available")
        return True
    except Exception as e:
        print(f"❌ Content extraction error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("UI COMPONENT TEST")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_session_state,
        test_file_processing,
        test_content_extraction,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    
    if all(results):
        print("✅ All tests passed!")
        print("\nYou can now run:")
        print("   streamlit run app_notebooklm_style.py")
        return 0
    else:
        print("❌ Some tests failed")
        print("\nPlease fix the errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
