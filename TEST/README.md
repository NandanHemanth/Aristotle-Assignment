# Test Suite

This folder contains all test files for the Aristotle AI Tutor project.

## Quick Start

### Verify Setup
```bash
python TEST/verify_setup.py
```
Checks that all dependencies are installed and API keys are configured.

## Test Files

### Core System Tests

| File | Purpose | What It Tests |
|------|---------|---------------|
| **verify_setup.py** | Environment verification | Dependencies, API keys, imports |
| **test_simple.py** | Basic integration test | End-to-end flow: problem → solution → tutoring |
| **test_integration.py** | Full integration test | Complete system with all features |

### Component Tests

| File | Purpose | What It Tests |
|------|---------|---------------|
| **test_extractors.py** | Content extraction | YouTube, URL, file processing |
| **test_ui.py** | UI components | Streamlit interface elements |
| **test_enhanced_tutor.py** | Dual-mode tutoring | Conceptual vs homework question handling |

### Performance Tests

| File | Purpose | What It Tests |
|------|---------|---------------|
| **test_cache_performance.py** | Caching performance | Prompt caching effectiveness, cost savings |
| **test_conversation_caching.py** | Conversation caching | Cache hit rates, latency improvements |
| **test_cost_tracking.py** | Cost estimation | Token usage, cost calculations |

### Studio Feature Tests

| File | Purpose | What It Tests |
|------|---------|---------------|
| **test_studio_features.py** | All studio features | Text-based outputs (Quiz, Report, Mind Map, Infographic) |
| **test_enhanced_studio.py** | Media generation | MP3 audio, MP4 video, PDF slides |

### Fix Tests

| File | Purpose | What It Tests |
|------|---------|---------------|
| **test_youtube_extraction.py** | YouTube URL detection | URL parsing, transcript extraction |
| **test_youtube_live.py** | Live YouTube test | Real video transcript extraction |
| **test_app_fix.py** | App.py integration | URL detection fix in main app |

## Running Tests

### All Tests at Once
```bash
# From project root
cd TEST
python verify_setup.py && python test_simple.py && python test_enhanced_studio.py
```

### Individual Tests

**1. Verify Setup (REQUIRED FIRST)**
```bash
python TEST/verify_setup.py
```
Expected output: ✅ All dependencies installed, API key found

**2. Simple Integration Test**
```bash
python TEST/test_simple.py
```
Tests basic flow: upload problem → generate solution → tutor response

**3. Enhanced Studio Test**
```bash
python TEST/test_enhanced_studio.py
```
Tests: Audio MP3, Video MP4, PDF Slides generation

**4. YouTube Extraction Test**
```bash
python TEST/test_youtube_extraction.py
```
Tests: URL detection, video ID extraction, transcript fetching

**5. Performance Tests**
```bash
python TEST/test_cache_performance.py
python TEST/test_conversation_caching.py
```
Measure caching benefits and cost savings

## Test Results

All tests should pass. Expected results:

```
✅ verify_setup.py         - All dependencies OK
✅ test_simple.py           - End-to-end flow works
✅ test_enhanced_studio.py  - Audio, Video, PDF generation works
✅ test_youtube_extraction  - URL detection works
✅ test_cache_performance   - Caching reduces cost by 70-85%
```

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "API key not found"
Create `.env` file in project root:
```
OPENROUTER_API_KEY=your_key_here
```

### YouTube extraction fails
Normal - not all videos have transcripts. Tests show:
- ✅ URL detection working
- ✅ Video ID extraction working
- ⚠️  Transcript extraction may fail (video-dependent)

### Video generation fails
Ensure you have:
```bash
pip install moviepy gTTS
```

## Test Coverage

| Component | Test File | Coverage |
|-----------|-----------|----------|
| Content Extraction | test_extractors.py | YouTube, URL, PDF, DOCX |
| Tutoring Engine | test_simple.py, test_integration.py | Solution generation, tutoring, verification |
| Prompt Caching | test_cache_performance.py | System prompt cache, conversation cache |
| Studio Features | test_studio_features.py, test_enhanced_studio.py | All 7 features |
| UI | test_ui.py | Streamlit components |
| YouTube Fix | test_youtube_extraction.py, test_app_fix.py | URL detection and extraction |

## Adding New Tests

Create new test files following this pattern:

```python
"""
Test description here
"""

import sys
import io

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Your test code here
def test_feature():
    print("Testing feature...")
    # Test logic
    print("✅ Test passed")

if __name__ == "__main__":
    test_feature()
```

## CI/CD Integration

To run all tests in CI/CD:

```bash
#!/bin/bash
set -e

echo "Running test suite..."

python TEST/verify_setup.py
python TEST/test_simple.py
python TEST/test_enhanced_studio.py
python TEST/test_youtube_extraction.py
python TEST/test_cache_performance.py

echo "All tests passed!"
```

## Performance Benchmarks

From real test runs:

| Test | Duration | Result |
|------|----------|--------|
| verify_setup.py | <1s | ✅ Pass |
| test_simple.py | 5-10s | ✅ Pass |
| test_enhanced_studio.py | 15-30s | ✅ Pass (includes MP3/MP4 generation) |
| test_youtube_extraction.py | 2-5s | ✅ Pass (URL detection always works) |
| test_cache_performance.py | 30-60s | ✅ Pass (measures actual cache savings) |

---

**Total Test Suite Runtime**: ~1-2 minutes

**Last Updated**: 2025-12-01
