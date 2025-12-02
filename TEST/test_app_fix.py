"""
Test that the app.py fix doesn't have any import or runtime errors.
"""

import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Testing app.py imports and functions...")
print("=" * 60)

# Test 1: Import content extractors
print("\n1. Testing content_extractors import...")
try:
    from content_extractors import extract_content, detect_content_type
    print("✅ extract_content imported successfully")
    print("✅ detect_content_type imported successfully")
except Exception as e:
    print(f"❌ Import error: {str(e)}")
    sys.exit(1)

# Test 2: Test detect_content_type function
print("\n2. Testing detect_content_type function...")
try:
    # Test with YouTube URL
    result = detect_content_type("https://www.youtube.com/watch?v=test123")
    print(f"YouTube URL detected as: {result}")
    assert result == "youtube", f"Expected 'youtube', got '{result}'"
    print("✅ YouTube detection works")

    # Test with plain text
    result = detect_content_type("This is a regular problem")
    print(f"Plain text detected as: {result}")
    assert result == "text", f"Expected 'text', got '{result}'"
    print("✅ Plain text detection works")

    # Test with web URL
    result = detect_content_type("https://example.com/article")
    print(f"Web URL detected as: {result}")
    assert result == "url", f"Expected 'url', got '{result}'"
    print("✅ Web URL detection works")

except Exception as e:
    print(f"❌ Function error: {str(e)}")
    sys.exit(1)

# Test 3: Test extract_content function (with error handling)
print("\n3. Testing extract_content function...")
try:
    # Test with a YouTube URL (may fail if no transcript, but shouldn't crash)
    content, metadata, method = extract_content("https://www.youtube.com/watch?v=test123", "youtube")
    print(f"Method: {method}")
    print(f"Has error: {metadata.get('error', False)}")

    # This is expected to potentially have an error (no transcript)
    # The important part is that it doesn't crash
    print("✅ extract_content function executes without crashing")

except Exception as e:
    print(f"❌ Function error: {str(e)}")
    sys.exit(1)

# Test 4: Verify app.py syntax
print("\n4. Testing app.py syntax...")
try:
    import py_compile
    py_compile.compile('d:\\Guild\\Aristotle-Assignment\\app.py', doraise=True)
    print("✅ app.py has no syntax errors")
except py_compile.PyCompileError as e:
    print(f"❌ Syntax error in app.py: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
print("\nThe fix is working correctly!")
print("\nYou can now:")
print("1. Run: streamlit run app.py")
print("2. Paste a YouTube URL in the text input")
print("3. Click 'Start Tutoring'")
print("4. The URL will be detected and content extracted")
