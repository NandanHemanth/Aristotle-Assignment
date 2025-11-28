# Aristotle AI Tutor

An AI-powered Socratic tutoring system that guides students to discover solutions themselves through intelligent multi-modal input processing and optimized performance.

## <¯ Overview

A **multi-agent AI tutoring system** that prevents "solution leakage" through architectural design. Supports multiple input formats including text, PDFs, images, YouTube videos, and web URLs.

### Key Features

-  **Solution Leakage Prevention** - Structural isolation prevents answer revelation
-  **Multi-Format Support** - Text, PDFs, screenshots, YouTube videos, web URLs
-  **Verification Layer** - Separate agent checks work without revealing answers
-  **Optimized Performance** - Prompt caching + streaming + smart model routing
-  **Cost Efficient** - 84-87% cheaper than standard approaches
-  **Clean UI/UX** - Modern Streamlit interface with chat

## =€ Quick Start

### Installation

```bash
cd Aristotle-Assignment
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add: OPENROUTER_API_KEY=your_key_here
streamlit run app.py
```

## =Ú Documentation

- **[ANALYSIS.md](ANALYSIS.md)** - Technical analysis, problems, solutions
- **[BLUEPRINT.md](BLUEPRINT.md)** - Research foundation
- **[/experiments/](experiments/)** - Experimental results

## <× Architecture

Three-stage pipeline with multi-model optimization for latency and performance.

See [ANALYSIS.md](ANALYSIS.md) for detailed documentation.
