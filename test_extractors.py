"""
Test content extractors
"""

from content_extractors import YouTubeExtractor, URLExtractor, extract_content

def test_youtube():
    """Test YouTube extraction."""
    print("=" * 50)
    print("Testing YouTube Extraction")
    print("=" * 50)
    
    # Test with a known educational video
    test_urls = [
        "https://www.youtube.com/watch?v=kCc8FmEb1nY",  # CrashCourse
        "https://www.youtube.com/watch?v=7SzdsSTlN4k-1s",  # Your URL
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        content, metadata = YouTubeExtractor.extract_from_url(url)
        
        if metadata.get("error"):
            print(f"❌ Error: {content}")
        else:
            print(f"✅ Success!")
            print(f"   Words: {metadata.get('word_count', 0)}")
            print(f"   Duration: {metadata.get('duration_seconds', 0) / 60:.1f} min")
            print(f"   Preview: {content[:100]}...")

def test_url():
    """Test URL extraction."""
    print("\n" + "=" * 50)
    print("Testing URL Extraction")
    print("=" * 50)
    
    test_urls = [
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "https://www.example.com",
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        content, metadata = URLExtractor.extract_from_url(url)
        
        if metadata.get("error"):
            print(f"❌ Error: {content}")
        else:
            print(f"✅ Success!")
            print(f"   Title: {metadata.get('title', 'Unknown')}")
            print(f"   Words: {metadata.get('word_count', 0)}")
            print(f"   Preview: {content[:100]}...")

def test_unified():
    """Test unified extraction."""
    print("\n" + "=" * 50)
    print("Testing Unified Extraction")
    print("=" * 50)
    
    test_inputs = [
        "https://www.youtube.com/watch?v=kCc8FmEb1nY",
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "This is plain text input for testing",
    ]
    
    for input_text in test_inputs:
        print(f"\nTesting: {input_text[:50]}...")
        content, metadata, method = extract_content(input_text)
        
        if metadata.get("error"):
            print(f"❌ Error: {content}")
        else:
            print(f"✅ Success!")
            print(f"   Method: {method}")
            print(f"   Words: {metadata.get('word_count', 0)}")

if __name__ == "__main__":
    test_youtube()
    test_url()
    test_unified()
    
    print("\n" + "=" * 50)
    print("Testing Complete!")
    print("=" * 50)
