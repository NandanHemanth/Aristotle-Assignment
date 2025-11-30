# AI Tutoring App 📚

A modern AI-powered tutoring application built with Streamlit that helps students learn through interactive conversations and multi-modal content support.

## Overview

This application provides an intelligent tutoring system with a clean, intuitive interface featuring:
- **Multi-format input support** - Upload PDFs, HTML, DOCX files or paste URLs
- **Clean, modern UI** - Streamlit-based interface with sidebar navigation
- **Chat interface** - Interactive conversation with AI tutor (2/3 width)
- **Studio tools** - Generate study materials like audio overviews, mind maps, quizzes (1/3 width)
- **Lottie animations** - Engaging visual elements in the sidebar

## Features

### Input Methods
- 📄 **File Upload** - Support for PDF, HTML, and DOCX files
- 🔗 **URL Input** - Paste any web URL to extract content
- 💬 **Chat Interface** - Interactive tutoring conversations
- 🎨 **Studio Tools** - Generate various study materials

### Studio Tools
- 🎵 Audio Overview
- 🎥 Video Overview  
- 🧠 Mind Map
- 📝 Reports
- 📊 Infographic
- 📑 Quiz
- 🎯 Slide Deck

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (if needed)
cp .env.example .env
# Edit .env and add your API keys

# Run the application
streamlit run app.py
```

### Requirements

- Python 3.8+
- Streamlit 1.31.0
- streamlit-lottie 0.0.5
- OpenAI API access (optional, for advanced features)
- Additional dependencies in requirements.txt

## Project Structure

```
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── tutoring_engine.py          # Core tutoring logic
├── openrouter_client.py        # API client
├── content_extractors.py       # Content extraction utilities
├── utils.py                    # Helper functions
├── test_extractors.py          # Tests for extractors
├── test_ui.py                  # UI tests
├── verify_setup.py             # Setup verification
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not committed)
└── experiments/                # Experimental results and tests
```

## Architecture

The application uses a clean two-column layout:

**Sidebar (Left)**
- Source upload section (file upload + URL input)
- Lottie animation for visual appeal

**Main Content (Right)**
- **Chat Section** (2/3 width) - Interactive conversation area with chat input
- **Studio Section** (1/3 width) - Tool buttons and output area

### Technical Architecture

The underlying system uses a multi-agent architecture:

1. **Input Processing** - Extracts content from various sources (files, URLs)
2. **Content Analysis** - Processes and understands the material
3. **Tutoring Engine** - Provides intelligent guidance through conversations
4. **Studio Generation** - Creates study materials on demand

## Documentation

For detailed technical information, see:

- **[ANALYSIS.md](ANALYSIS.md)** - Technical deep dive, architecture, and performance analysis
- **[BLUEPRINT.md](BLUEPRINT.md)** - Research foundation and design principles
- **[EXPERIMENTS_SUMMARY.md](EXPERIMENTS_SUMMARY.md)** - Testing results and findings
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Complete project navigation guide
- **[SUMMARY.md](SUMMARY.md)** - Implementation summary and key metrics

## Configuration

Key configuration options in `config.py`:
- Model selection (vision, reasoning, tutoring)
- API endpoints and keys
- System prompts and instructions
- Performance settings (caching, streaming)

## Performance Highlights

Based on the comprehensive analysis in the documentation:

- **Fast responses** - Optimized with prompt caching and streaming
- **Cost efficient** - Smart model routing for different tasks (84-87% cheaper than baseline)
- **Scalable** - Handles multiple concurrent sessions
- **Solution leakage prevention** - Architectural design prevents answer revelation

## Usage

1. **Upload a source** - Use the sidebar to upload a file or paste a URL
2. **Start chatting** - Ask questions in the chat interface
3. **Use studio tools** - Generate study materials using the studio buttons
4. **Review output** - Study materials appear in the studio output area

## Development

### Running Tests

```bash
# Test content extractors
python test_extractors.py

# Test UI components
python test_ui.py

# Verify setup
python verify_setup.py
```

### Contributing

This is a demonstration project showcasing modern AI tutoring capabilities. For production use, consider:
- Enhanced error handling and validation
- User authentication and session management
- Persistent storage (database integration)
- Analytics and monitoring dashboards
- Additional content extractors and formats
- Mobile-responsive design improvements

## Known Limitations

See [EXPERIMENTS_SUMMARY.md](EXPERIMENTS_SUMMARY.md) for detailed analysis of:
- Vision model accuracy on handwritten content
- Complex problem latency considerations
- Context window management strategies

## License

See project documentation for licensing information.

## Support

For questions or issues:
1. Check the documentation files listed above
2. Review the experiments folder for test cases
3. See PROJECT_OVERVIEW.md for navigation guidance
