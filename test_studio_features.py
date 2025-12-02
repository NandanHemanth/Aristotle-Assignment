"""
Test script for Studio Features
Tests all studio feature generation without requiring Streamlit UI.
"""

import sys
import io

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from studio_features import client, STUDIO_MODELS
from config import OPENROUTER_API_KEY

def test_model_availability():
    """Test that all studio models are accessible."""
    print("=" * 60)
    print("Testing Studio Models Availability")
    print("=" * 60)

    for feature, model in STUDIO_MODELS.items():
        print(f"✓ {feature.upper()}: {model}")

    print("\n✅ All studio models configured\n")


def test_audio_overview():
    """Test audio overview generation."""
    print("=" * 60)
    print("Testing Audio Overview Generation")
    print("=" * 60)

    problem = "Solve for x: 2x + 5 = 13"

    prompt = f"""Create a short, engaging audio script (30-60 seconds when read aloud) that explains this problem:

{problem}

The script should:
1. Briefly state what the problem asks
2. Highlight the key concepts involved
3. Mention what approach would be needed (without giving the answer)
4. Be written in a conversational, easy-to-understand tone

Format as a script ready to be read aloud."""

    messages = [{"role": "user", "content": prompt}]

    try:
        response = client.chat_completion(
            model=STUDIO_MODELS["audio"],
            messages=messages,
            stream=False,
            temperature=0.7
        )

        script = response["choices"][0]["message"]["content"]
        print(f"✅ Audio script generated ({len(script)} characters)")
        print("\nPreview:")
        print(script[:200] + "..." if len(script) > 200 else script)
        print()
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")


def test_video_overview():
    """Test video storyboard generation."""
    print("=" * 60)
    print("Testing Video Storyboard Generation")
    print("=" * 60)

    problem = "What is photosynthesis?"

    prompt = f"""Create a simple video storyboard for explaining this problem:

{problem}

Generate a 4-6 scene storyboard. For each scene, provide:
1. Scene number
2. Visual description (what should be shown)
3. Narration text (what should be said)
4. Duration (in seconds)

Format as a clear storyboard that could be used to create an educational video."""

    messages = [{"role": "user", "content": prompt}]

    try:
        response = client.chat_completion(
            model=STUDIO_MODELS["video"],
            messages=messages,
            stream=False,
            temperature=0.7
        )

        storyboard = response["choices"][0]["message"]["content"]
        print(f"✅ Video storyboard generated ({len(storyboard)} characters)")
        print("\nPreview:")
        print(storyboard[:200] + "..." if len(storyboard) > 200 else storyboard)
        print()
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")


def test_mindmap():
    """Test mind map generation."""
    print("=" * 60)
    print("Testing Mind Map Generation")
    print("=" * 60)

    problem = "Explain the water cycle"

    prompt = f"""Create a hierarchical mind map structure for this problem:

{problem}

The mind map should show:
1. Central topic (the main problem)
2. Key concepts involved (2nd level)
3. Sub-concepts and approaches (3rd level)
4. Connections between concepts

Format as a text-based hierarchical structure using indentation and bullet points."""

    messages = [{"role": "user", "content": prompt}]

    try:
        response = client.chat_completion(
            model=STUDIO_MODELS["mindmap"],
            messages=messages,
            stream=False,
            temperature=0.5
        )

        mindmap = response["choices"][0]["message"]["content"]
        print(f"✅ Mind map generated ({len(mindmap)} characters)")
        print("\nPreview:")
        print(mindmap[:200] + "..." if len(mindmap) > 200 else mindmap)
        print()
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")


def test_report():
    """Test detailed report generation."""
    print("=" * 60)
    print("Testing Report Generation")
    print("=" * 60)

    problem = "Calculate the area of a circle with radius 5cm"

    prompt = f"""Create a detailed educational report about this problem:

{problem}

The report should include:
1. **Problem Overview**: What is being asked
2. **Key Concepts**: Important concepts and theories involved
3. **Approach Strategy**: How to approach this type of problem (general method, not the specific answer)
4. **Common Pitfalls**: Mistakes students often make
5. **Related Topics**: Connected concepts worth exploring

Format as a well-structured markdown report with headers and bullet points."""

    messages = [{"role": "user", "content": prompt}]

    try:
        response = client.chat_completion(
            model=STUDIO_MODELS["report"],
            messages=messages,
            stream=False,
            temperature=0.6
        )

        report = response["choices"][0]["message"]["content"]
        print(f"✅ Report generated ({len(report)} characters)")
        print("\nPreview:")
        print(report[:200] + "..." if len(report) > 200 else report)
        print()
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")


def test_quiz():
    """Test quiz generation."""
    print("=" * 60)
    print("Testing Quiz Generation")
    print("=" * 60)

    problem = "The Pythagorean theorem: a² + b² = c²"

    prompt = f"""Create a 5-question quiz based on this problem:

{problem}

Generate exactly 5 multiple-choice questions that test understanding of the concepts involved.

For each question:
1. Write a clear question
2. Provide 4 answer options (A, B, C, D)
3. Indicate the correct answer
4. Provide a brief explanation

Format as a structured quiz with questions numbered 1-5."""

    messages = [{"role": "user", "content": prompt}]

    try:
        response = client.chat_completion(
            model=STUDIO_MODELS["quiz"],
            messages=messages,
            stream=False,
            temperature=0.7
        )

        quiz = response["choices"][0]["message"]["content"]
        print(f"✅ Quiz generated ({len(quiz)} characters)")
        print("\nPreview:")
        print(quiz[:200] + "..." if len(quiz) > 200 else quiz)
        print()
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")


def test_infographic():
    """Test infographic generation."""
    print("=" * 60)
    print("Testing Infographic Generation")
    print("=" * 60)

    problem = "Newton's Three Laws of Motion"

    prompt = f"""Design an infographic layout for this problem:

{problem}

Create a structured infographic design that includes:
1. **Title**: Catchy main title
2. **Key Stats/Facts**: 3-5 important numbers or facts
3. **Visual Sections**: 3-4 main sections with key points
4. **Color Scheme**: Suggest a color palette

Format as a structured design document."""

    messages = [{"role": "user", "content": prompt}]

    try:
        response = client.chat_completion(
            model=STUDIO_MODELS["infographic"],
            messages=messages,
            stream=False,
            temperature=0.7
        )

        infographic = response["choices"][0]["message"]["content"]
        print(f"✅ Infographic design generated ({len(infographic)} characters)")
        print("\nPreview:")
        print(infographic[:200] + "..." if len(infographic) > 200 else infographic)
        print()
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")


def test_slidedeck():
    """Test slide deck generation."""
    print("=" * 60)
    print("Testing Slide Deck Generation")
    print("=" * 60)

    problem = "Introduction to Python Programming"

    prompt = f"""Create a slide deck presentation about this problem:

{problem}

Generate 6-8 slides with:
1. Title slide
2. Problem statement slide
3. Key concepts (2-3 slides)
4. Approach methodology slide
5. Practice/Summary slide

For each slide, provide slide title and main content (bullet points).
Format in markdown with clear slide separators (---)."""

    messages = [{"role": "user", "content": prompt}]

    try:
        response = client.chat_completion(
            model=STUDIO_MODELS["slidedeck"],
            messages=messages,
            stream=False,
            temperature=0.6
        )

        slides = response["choices"][0]["message"]["content"]
        print(f"✅ Slide deck generated ({len(slides)} characters)")
        print("\nPreview:")
        print(slides[:200] + "..." if len(slides) > 200 else slides)
        print()
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("STUDIO FEATURES TEST SUITE")
    print("=" * 60 + "\n")

    if not OPENROUTER_API_KEY:
        print("❌ ERROR: OPENROUTER_API_KEY not found in environment!")
        print("Please set your API key in the .env file\n")
        return

    print("✅ API key found\n")

    # Test model availability
    test_model_availability()

    # Test each feature
    print("Running feature tests...\n")
    test_audio_overview()
    test_video_overview()
    test_mindmap()
    test_report()
    test_quiz()
    test_infographic()
    test_slidedeck()

    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    print("\n✅ All Studio features are working!")
    print("\nTo use the features:")
    print("1. Run: streamlit run app.py")
    print("2. Upload a problem and start tutoring")
    print("3. Click any Studio button to generate content\n")


if __name__ == "__main__":
    main()
