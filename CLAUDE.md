# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Aristotle AI Tutor** is a multi-agent Socratic tutoring system that prevents "solution leakage" through architectural design. It supports multi-modal input (text, PDFs, images, YouTube videos, web URLs) and is optimized for latency and cost.

**Core Innovation**: Structural separation prevents answer revelation - the tutor agent NEVER sees the reference solution directly. Instead, a separate verification layer checks student work and provides metadata for guiding questions.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment (required)
# Create .env file and add: OPENROUTER_API_KEY=your_key_here
echo "OPENROUTER_API_KEY=your_key_here" > .env

# Verify setup
python verify_setup.py

# Run the application
streamlit run app.py
```

## Architecture

### Three-Stage Pipeline

1. **Input Processing** ([content_extractors.py](content_extractors.py), [utils.py](utils.py))
   - Text/PDF/DOCX: Direct extraction
   - Images: Vision model (GPT-4o-mini) for OCR
   - YouTube: Transcript extraction via youtube-transcript-api
   - URLs: Web scraping with BeautifulSoup

2. **Solution Generation** ([tutoring_engine.py](tutoring_engine.py) - `generate_reference_solution` method)
   - Uses DeepSeek-R1 for reasoning ($0.20/$4.50 per million tokens)
   - Reference solution stored separately in `TutoringEngine.reference_solution`
   - **CRITICAL**: Never included in tutor's context

3. **Tutoring** ([tutoring_engine.py](tutoring_engine.py) - `tutor_response` method)
   - Claude Haiku 4.5 with `:nitro` for fast responses
   - Streaming enabled (10-100x perceived latency improvement)
   - Prompt caching for static system instructions (85% latency reduction)

### Verification Layer (Key Pattern)

The verification system ([tutoring_engine.py](tutoring_engine.py) - `verify_student_work` method) is the architectural solution to solution leakage:

```python
# Student submits work → Separate verifier compares to reference
verification = verify_student_work(student_work)
# Returns: {is_correct, error_location, hint_suggestion}

# Tutor receives ONLY metadata, not the answer
# Uses this to guide with questions, never revealing solution
```

**Why this matters**: LLMs leak answers even when prompted not to. Structural isolation (tutor never sees answer) prevents this at the architecture level, not the prompt level.

## Key Files

| File | Purpose | Critical Patterns |
|------|---------|------------------|
| [tutoring_engine.py](tutoring_engine.py) | Core multi-agent logic | Solution isolation, verification layer, streaming |
| [openrouter_client.py](openrouter_client.py) | API client | Streaming, caching (`create_cached_messages`), cost estimation |
| [content_extractors.py](content_extractors.py) | Multi-source extraction | YouTube, URL, with fallbacks and error handling |
| [config.py](config.py) | Configuration | Model selection, system prompts, pricing |
| [utils.py](utils.py) | Utilities | File processing, conversation truncation, verification formatting |
| [app.py](app.py) | Streamlit UI | Current main UI - being rebuilt |

## Configuration

### Models ([config.py](config.py) - `MODELS` dict)

Multi-model optimization for cost/performance:
- **Vision**: `openai/gpt-4o-mini` - $0.15/$0.60 per million tokens
- **Reasoning**: `deepseek/deepseek-r1` - $0.20/$4.50 per million tokens
- **Tutoring**: `anthropic/claude-haiku-4.5:nitro` - $1/$5 per million tokens, `:nitro` = fastest provider
- **Verification**: `openai/gpt-4o-mini` - Fast and cheap

### Environment Variables

Required in `.env`:
```
OPENROUTER_API_KEY=sk-or-v1-...
```

## Important Patterns

### 1. Enhanced Tutor: Dual-Mode Teaching

The tutor now intelligently adapts its teaching style based on question type:

**CONCEPTUAL QUESTIONS** ("explain...", "what is...", "difference between..."):
```python
# Example: "What is the difference between supervised and unsupervised learning?"
# Tutor provides:
# 1. Clear definitions
# 2. Fundamental explanations (WHY/HOW/WHEN)
# 3. Concrete examples (2-3 real-world cases)
# 4. Thought-provoking questions to deepen understanding
```

**HOMEWORK PROBLEMS** (specific problems with definite answers):
```python
# Example: "Solve for x: 2x + 5 = 13"
# Tutor uses Socratic method:
# 1. Asks guiding questions
# 2. Never reveals the answer
# 3. Verifies student work via verification layer
# 4. Redirects errors without revealing solution
```

The enhanced prompt ([config.py](config.py) - `TUTOR_PROMPT`) instructs the model to distinguish between these two modes automatically. This allows the tutor to be both explanatory (for learning concepts) and pedagogically sound (for homework).

### 2. Solution Leakage Prevention

**Never** include `TutoringEngine.reference_solution` in tutor messages. Always use the verification layer:

```python
# WRONG - leaks solution
messages = [{
    "role": "system",
    "content": f"Problem: {problem}\nSolution: {reference_solution}"
}]

# RIGHT - structural isolation
verification = verify_student_work(student_work)
guidance = format_verification_result(verification)  # Metadata only
messages = [{
    "role": "system",
    "content": f"Problem: {problem}\n{guidance}"  # No solution!
}]
```

### 3. Streaming for Latency

Always enable streaming for user-facing responses ([openrouter_client.py](openrouter_client.py) - `chat_completion` method):

```python
# Returns generator, yield chunks as they arrive
stream = client.chat_completion(model, messages, stream=True)
for chunk in stream:
    yield chunk["choices"][0]["delta"]["content"]
```

### 4. Prompt Caching

Use `create_cached_messages()` for static content ([openrouter_client.py](openrouter_client.py) - `create_cached_messages` method):

```python
# System prompt cached, only conversation is variable
messages = client.create_cached_messages(
    system_prompt=TUTOR_PROMPT,  # Static, cached
    conversation_history=history  # Variable
)
```

Cache reads are 10% of input pricing with Claude models.

### 5. Conversation Truncation

Prevent context overflow ([utils.py](utils.py) - `truncate_conversation_history` function):

```python
# Keeps first message + recent N messages
truncated = truncate_conversation_history(messages, max_length=20)
```

## Performance Characteristics

Based on [ANALYSIS.md](ANALYSIS.md) and experiments:

- **Setup time**: 10-18s (one-time solution generation)
- **Response latency**: 0.3-1s (with caching)
- **Cost per session**: ~$0.01 (5 messages)
- **Cost reduction**: 84-87% vs GPT-4o baseline

## Known Limitations

1. **Vision accuracy on handwritten text**: 24-76% depending on neatness (see experiment_3)
   - Mitigation: User verification step in UI
   - Future: Hybrid OCR pipeline

2. **Verification accuracy**: ~60% on complex errors
   - Mitigation: Works for most cases
   - Future: External tools (SymPy for math)

3. **YouTube/URL extraction**: Requires transcripts/accessible content
   - Graceful fallback with clear error messages

## Testing & Debugging

```bash
# Verify all dependencies and configuration
python verify_setup.py

# Test content extractors (YouTube, URL, file processing)
python test_extractors.py

# Test UI components
python test_ui.py

# Test enhanced tutor (conceptual vs homework questions)
python test_enhanced_tutor.py

# Simple integration test
python test_simple.py

# Manual testing via UI
streamlit run app.py
```

### Testing the Enhanced Tutor

The tutor has dual-mode teaching. Test both modes:

**Conceptual Question Test:**
```python
# Upload any problem or use placeholder
# Ask: "What is the difference between supervised and unsupervised learning?"
# Expected: Full explanation with definitions, examples, and questions
```

**Homework Problem Test:**
```python
# Upload: "Solve for x: 2x + 5 = 13"
# Ask: "What is x?"
# Expected: Socratic questions, NO direct answer
```

### Common Issues

1. **Missing API Key**: If you get authentication errors, check that `OPENROUTER_API_KEY` is set in `.env`
2. **Import Errors**: Run `python verify_setup.py` to check all dependencies
3. **YouTube Transcript Errors**: Not all videos have transcripts available - the extractor will fail gracefully
4. **Vision Model Accuracy**: Handwritten text may have 24-76% error rate - verify extracted content before use

Experiment JSONs in `/experiments/` directory contain real conversation transcripts with metrics.

## Current Development Status

**Status**: Fully functional and integrated! ✅

**Current UI** ([app.py](app.py)):
- NotebookLM-style layout with Sources sidebar, Chat section (scrollable), and Studio section
- File upload supports: PDF, DOCX, TXT, PNG, JPG, JPEG
- Manual text input option in sidebar
- Scrollable chat container (height=500px)
- Real-time metrics display (messages count, cost)
- Lottie animation in sidebar
- **Status**: Fully integrated with [tutoring_engine.py](tutoring_engine.py) ✅

**Core Tutoring Logic** ([tutoring_engine.py](tutoring_engine.py)):
- Complete implementation of multi-agent tutoring system
- Solution generation, verification layer, Socratic tutoring
- Streaming responses for fast perceived latency
- **Status**: Fully functional and connected to UI ✅

**How to use:**
1. Upload a file (PDF, DOCX, image, text) or paste text in sidebar
2. Click "Start Tutoring" button
3. Wait 10-15 seconds for solution generation (one-time setup)
4. Chat with Aristotle in the scrollable chat container
5. Messages appear inside the chat widget with streaming responses

## Documentation

### Core Documentation
- [SUMMARY.md](SUMMARY.md) - Complete technical overview and architecture
- [ANALYSIS.md](ANALYSIS.md) - Deep technical analysis and performance optimization
- [README.md](README.md) - Setup and usage guide

### Enhanced Tutor Documentation
- [TUTOR_ENHANCED.md](TUTOR_ENHANCED.md) - Complete guide to dual-mode teaching
- [QUICK_REFERENCE_TUTOR.md](QUICK_REFERENCE_TUTOR.md) - Before/after examples and quick reference
- [SETUP_COMPLETE.md](SETUP_COMPLETE.md) - Integration status and features

### Experimental Evidence
- [EXPERIMENTS_SUMMARY.md](EXPERIMENTS_SUMMARY.md) - Test results and findings
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - File structure and navigation
