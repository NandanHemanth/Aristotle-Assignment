"""
Quick test with a popular educational video known to have captions.
"""

import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from content_extractors import extract_content

# Test with Khan Academy or similar educational content
# This is Khan Academy's "What is Photosynthesis?" video - very likely to have captions
test_urls = [
    "https://www.youtube.com/watch?v=g78utcLQrJ4",  # Photosynthesis video
    "https://www.youtube.com/watch?v=UuGrBhK2c7U",  # Another math video
]

print("Testing YouTube extraction with known educational videos...\n")

for i, url in enumerate(test_urls, 1):
    print(f"Test {i}: {url}")
    print("-" * 60)

    try:
        content, metadata, method = extract_content(url, "youtube")

        if metadata.get("error"):
            print(f"❌ Failed: {content}")
        else:
            print(f"✅ SUCCESS!")
            print(f"Word count: {metadata.get('word_count', 0)}")
            print(f"Duration: {metadata.get('duration_seconds', 0) / 60:.1f} minutes")
            print(f"\nFirst 300 characters:")
            print(content[:300] + "...\n")
            break  # Success, no need to test more
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

    print()

print("\n✅ If at least one video extracted successfully, the fix is working!")
print("\nHow the fix works:")
print("1. User pastes YouTube URL in text input")
print("2. App detects it's a YouTube URL")
print("3. Extracts transcript using youtube-transcript-api")
print("4. Passes formatted content to tutoring engine")
print("5. Tutor receives video context and can answer questions about it")
