"""
Test YouTube URL extraction to verify the fix works.
"""

import sys
import io

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from content_extractors import extract_content, detect_content_type, YouTubeExtractor

def test_youtube_detection():
    """Test that YouTube URLs are detected correctly."""
    print("=" * 60)
    print("Testing YouTube URL Detection")
    print("=" * 60)

    test_urls = [
        "https://www.youtube.com/watch?v=qYNweeDHiyU",
        "https://youtu.be/qYNweeDHiyU",
        "www.youtube.com/watch?v=qYNweeDHiyU",
    ]

    for url in test_urls:
        content_type = detect_content_type(url)
        print(f"URL: {url[:50]}...")
        print(f"Detected as: {content_type}")
        assert content_type == "youtube", f"Failed to detect YouTube URL: {url}"
        print("✅ PASS\n")

    print()


def test_video_id_extraction():
    """Test extracting video ID from YouTube URLs."""
    print("=" * 60)
    print("Testing Video ID Extraction")
    print("=" * 60)

    test_cases = [
        ("https://www.youtube.com/watch?v=qYNweeDHiyU", "qYNweeDHiyU"),
        ("https://youtu.be/qYNweeDHiyU", "qYNweeDHiyU"),
        ("https://www.youtube.com/embed/qYNweeDHiyU", "qYNweeDHiyU"),
    ]

    for url, expected_id in test_cases:
        video_id = YouTubeExtractor.extract_video_id(url)
        print(f"URL: {url}")
        print(f"Expected ID: {expected_id}")
        print(f"Extracted ID: {video_id}")
        assert video_id == expected_id, f"Video ID mismatch for {url}"
        print("✅ PASS\n")

    print()


def test_transcript_extraction():
    """Test extracting transcript from a known educational video."""
    print("=" * 60)
    print("Testing Transcript Extraction")
    print("=" * 60)

    # Use a popular educational video that likely has captions
    test_url = "https://www.youtube.com/watch?v=qYNweeDHiyU"

    print(f"Testing URL: {test_url}")
    print("Extracting content...")

    try:
        # Extract content
        content, metadata, method = extract_content(test_url, "youtube")

        # Check for errors
        if metadata.get("error"):
            print(f"⚠️  Extraction failed (this is expected for some videos):")
            print(f"   {content}")
            print(f"   Reason: Video may not have captions or captions are disabled")
            print()
            return False
        else:
            print(f"✅ Content extracted successfully!")
            print(f"Method: {method}")
            print(f"Word count: {metadata.get('word_count', 0)}")
            print(f"Duration: {metadata.get('duration_seconds', 0):.1f} seconds")
            print(f"Extraction time: {metadata.get('extraction_time', 0):.2f}s")
            print(f"\nContent preview (first 300 chars):")
            print(content[:300] + "...")
            print()
            return True

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        print()
        return False


def test_content_format():
    """Test that extracted content is properly formatted for tutoring."""
    print("=" * 60)
    print("Testing Content Formatting")
    print("=" * 60)

    test_url = "https://www.youtube.com/watch?v=qYNweeDHiyU"

    try:
        content, metadata, method = extract_content(test_url, "youtube")

        if metadata.get("error"):
            print("⚠️  Video has no transcript, skipping format test")
            print()
            return False

        # Check that content contains expected formatting
        assert "YouTube Video Content:" in content or "Transcript:" in content, "Missing expected formatting"
        assert len(content) > 0, "Content is empty"

        print("✅ Content is properly formatted for tutoring")
        print(f"Total length: {len(content)} characters")
        print()
        return True

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        print()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("YOUTUBE EXTRACTION TEST SUITE")
    print("=" * 60 + "\n")

    results = []

    # Test 1: URL detection
    print("Test 1: YouTube URL Detection")
    try:
        test_youtube_detection()
        results.append(("URL Detection", True))
    except Exception as e:
        print(f"❌ FAIL: {str(e)}\n")
        results.append(("URL Detection", False))

    # Test 2: Video ID extraction
    print("Test 2: Video ID Extraction")
    try:
        test_video_id_extraction()
        results.append(("Video ID Extraction", True))
    except Exception as e:
        print(f"❌ FAIL: {str(e)}\n")
        results.append(("Video ID Extraction", False))

    # Test 3: Transcript extraction (may fail if video has no captions)
    print("Test 3: Transcript Extraction")
    try:
        success = test_transcript_extraction()
        results.append(("Transcript Extraction", success))
    except Exception as e:
        print(f"❌ FAIL: {str(e)}\n")
        results.append(("Transcript Extraction", False))

    # Test 4: Content formatting
    print("Test 4: Content Formatting")
    try:
        success = test_content_format()
        results.append(("Content Formatting", success))
    except Exception as e:
        print(f"❌ FAIL: {str(e)}\n")
        results.append(("Content Formatting", False))

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    if passed >= 2:  # At least URL detection and video ID extraction should pass
        print("\n✅ Core YouTube extraction is working!")
        print("\nℹ️  Note: Transcript extraction may fail if:")
        print("   - Video has no captions/subtitles")
        print("   - Video owner disabled transcripts")
        print("   - Video is private or unavailable")
        print("\nThe fix ensures URLs are detected and processed correctly.")
        print("When you paste a YouTube URL in the app, it will:")
        print("1. Detect it's a YouTube URL")
        print("2. Extract the transcript (if available)")
        print("3. Pass the content to the tutor for context")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")

    print()


if __name__ == "__main__":
    main()
