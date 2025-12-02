"""
Studio Features Module
Implements all Studio button functionality with pop-ups using different OpenRouter models.
"""

import streamlit as st
from openrouter_client import OpenRouterClient
from config import OPENROUTER_API_KEY
import json

# Initialize OpenRouter client
client = OpenRouterClient(api_key=OPENROUTER_API_KEY)

# Studio-specific models (different from tutoring models)
STUDIO_MODELS = {
    "audio": "anthropic/claude-haiku-4.5:nitro",  # Fast script generation
    "video": "openai/gpt-4o-mini",  # Storyboard generation
    "mindmap": "openai/gpt-4o",  # Structured output for diagrams
    "report": "deepseek/deepseek-r1",  # Detailed reasoning
    "quiz": "anthropic/claude-sonnet-4.5",  # Better Q&A generation
    "infographic": "openai/gpt-4o-mini",  # Data structuring
    "slidedeck": "anthropic/claude-haiku-4.5:nitro",  # Markdown slides
}


@st.dialog("🎵 Audio Overview", width="large")
def audio_overview_modal(problem_statement: str):
    """Generate a short audio script summary of the problem."""
    st.markdown("### Generating Audio Script...")

    with st.spinner("Creating audio overview..."):
        try:
            prompt = f"""Create a short, engaging audio script (30-60 seconds when read aloud) that explains this problem:

{problem_statement}

The script should:
1. Briefly state what the problem asks
2. Highlight the key concepts involved
3. Mention what approach would be needed (without giving the answer)
4. Be written in a conversational, easy-to-understand tone

Format as a script ready to be read aloud."""

            messages = [{"role": "user", "content": prompt}]

            response = client.chat_completion(
                model=STUDIO_MODELS["audio"],
                messages=messages,
                stream=False,
                temperature=0.7
            )

            script = response["choices"][0]["message"]["content"]

            st.success("✅ Audio script generated!")
            st.markdown("### 🎙️ Audio Script")
            st.text_area("Script", script, height=300, key="audio_script")

            st.info("💡 **Tip:** Copy this script and use a text-to-speech tool to create an audio file.")

        except Exception as e:
            st.error(f"❌ Error generating audio script: {str(e)}")


@st.dialog("🎥 Video Overview", width="large")
def video_overview_modal(problem_statement: str):
    """Generate a basic video storyboard."""
    st.markdown("### Generating Video Storyboard...")

    with st.spinner("Creating video overview..."):
        try:
            prompt = f"""Create a simple video storyboard for explaining this problem:

{problem_statement}

Generate a 4-6 scene storyboard. For each scene, provide:
1. Scene number
2. Visual description (what should be shown)
3. Narration text (what should be said)
4. Duration (in seconds)

Format as a clear storyboard that could be used to create an educational video."""

            messages = [{"role": "user", "content": prompt}]

            response = client.chat_completion(
                model=STUDIO_MODELS["video"],
                messages=messages,
                stream=False,
                temperature=0.7
            )

            storyboard = response["choices"][0]["message"]["content"]

            st.success("✅ Video storyboard generated!")
            st.markdown("### 🎬 Video Storyboard")
            st.markdown(storyboard)

            st.info("💡 **Tip:** Use this storyboard with video editing software or animation tools.")

        except Exception as e:
            st.error(f"❌ Error generating video storyboard: {str(e)}")


@st.dialog("🧠 Mind Map", width="large")
def mindmap_modal(problem_statement: str):
    """Generate a pipeline overview mind map."""
    st.markdown("### Generating Mind Map...")

    with st.spinner("Creating mind map..."):
        try:
            prompt = f"""Create a hierarchical mind map structure for this problem:

{problem_statement}

The mind map should show:
1. Central topic (the main problem)
2. Key concepts involved (2nd level)
3. Sub-concepts and approaches (3rd level)
4. Connections between concepts

Format as a text-based hierarchical structure using indentation and bullet points.
Also provide a Mermaid diagram syntax version that can be rendered."""

            messages = [{"role": "user", "content": prompt}]

            response = client.chat_completion(
                model=STUDIO_MODELS["mindmap"],
                messages=messages,
                stream=False,
                temperature=0.5
            )

            mindmap = response["choices"][0]["message"]["content"]

            st.success("✅ Mind map generated!")
            st.markdown("### 🗺️ Mind Map Structure")
            st.markdown(mindmap)

            st.info("💡 **Tip:** Copy the Mermaid diagram syntax and paste it into a Mermaid live editor to visualize.")

        except Exception as e:
            st.error(f"❌ Error generating mind map: {str(e)}")


@st.dialog("📝 Reports", width="large")
def report_modal(problem_statement: str):
    """Generate a detailed report on the topic with structured sections."""
    st.markdown("### Generating Detailed Report...")

    with st.spinner("Creating comprehensive report..."):
        try:
            prompt = f"""Create a detailed educational report about this problem:

{problem_statement}

The report should include:
1. **Problem Overview**: What is being asked
2. **Key Concepts**: Important concepts and theories involved
3. **Approach Strategy**: How to approach this type of problem (general method, not the specific answer)
4. **Common Pitfalls**: Mistakes students often make
5. **Related Topics**: Connected concepts worth exploring
6. **Practice Suggestions**: How to practice similar problems

Format as a well-structured markdown report with headers, bullet points, and clear sections.
Include suggestions for where images/diagrams would be helpful (mark as [IMAGE: description])."""

            messages = [{"role": "user", "content": prompt}]

            response = client.chat_completion(
                model=STUDIO_MODELS["report"],
                messages=messages,
                stream=False,
                temperature=0.6
            )

            report = response["choices"][0]["message"]["content"]

            st.success("✅ Report generated!")
            st.markdown("### 📄 Detailed Report")
            st.markdown(report)

            st.info("💡 **Tip:** [IMAGE: ...] markers indicate where diagrams would enhance understanding.")

        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")


@st.dialog("📑 Quiz", width="large")
def quiz_modal(problem_statement: str):
    """Generate 5 questions with answers."""
    st.markdown("### Generating Quiz...")

    with st.spinner("Creating quiz questions..."):
        try:
            prompt = f"""Create a 5-question quiz based on this problem:

{problem_statement}

Generate exactly 5 multiple-choice questions that test understanding of the concepts involved.

For each question:
1. Write a clear question
2. Provide 4 answer options (A, B, C, D)
3. Indicate the correct answer
4. Provide a brief explanation of why the answer is correct

Format as a structured quiz with questions numbered 1-5."""

            messages = [{"role": "user", "content": prompt}]

            response = client.chat_completion(
                model=STUDIO_MODELS["quiz"],
                messages=messages,
                stream=False,
                temperature=0.7
            )

            quiz = response["choices"][0]["message"]["content"]

            st.success("✅ Quiz generated!")
            st.markdown("### ❓ Quiz Questions")
            st.markdown(quiz)

            st.info("💡 **Tip:** Use this quiz to test your understanding before moving on.")

        except Exception as e:
            st.error(f"❌ Error generating quiz: {str(e)}")


@st.dialog("📊 Infographic", width="large")
def infographic_modal(problem_statement: str):
    """Generate infographic data structure."""
    st.markdown("### Generating Infographic Design...")

    with st.spinner("Creating infographic layout..."):
        try:
            prompt = f"""Design an infographic layout for this problem:

{problem_statement}

Create a structured infographic design that includes:
1. **Title**: Catchy main title
2. **Key Stats/Facts**: 3-5 important numbers or facts
3. **Visual Sections**: 3-4 main sections with:
   - Section title
   - Key points (bullet format)
   - Suggested visual (icon, chart type, diagram)
4. **Flow/Process**: If applicable, show step-by-step flow
5. **Color Scheme**: Suggest a color palette

Format as a structured design document that could be given to a graphic designer."""

            messages = [{"role": "user", "content": prompt}]

            response = client.chat_completion(
                model=STUDIO_MODELS["infographic"],
                messages=messages,
                stream=False,
                temperature=0.7
            )

            infographic = response["choices"][0]["message"]["content"]

            st.success("✅ Infographic design generated!")
            st.markdown("### 🎨 Infographic Design")
            st.markdown(infographic)

            st.info("💡 **Tip:** Use this design with tools like Canva, Figma, or Adobe Illustrator.")

        except Exception as e:
            st.error(f"❌ Error generating infographic: {str(e)}")


@st.dialog("🎯 Slide Deck", width="large")
def slidedeck_modal(problem_statement: str):
    """Generate basic presentation slides."""
    st.markdown("### Generating Slide Deck...")

    with st.spinner("Creating presentation slides..."):
        try:
            prompt = f"""Create a slide deck presentation about this problem:

{problem_statement}

Generate 6-8 slides with:
1. Title slide
2. Problem statement slide
3. Key concepts (2-3 slides)
4. Approach methodology slide
5. Practice/Summary slide

For each slide, provide:
- Slide number and title
- Main content (bullet points, max 5 per slide)
- Speaker notes (what to say)

Format in markdown with clear slide separators (---).
Keep content concise and visual-friendly."""

            messages = [{"role": "user", "content": prompt}]

            response = client.chat_completion(
                model=STUDIO_MODELS["slidedeck"],
                messages=messages,
                stream=False,
                temperature=0.6
            )

            slides = response["choices"][0]["message"]["content"]

            st.success("✅ Slide deck generated!")
            st.markdown("### 📊 Presentation Slides")
            st.markdown(slides)

            st.info("💡 **Tip:** Copy these slides to PowerPoint, Google Slides, or Markdown presentation tools.")

        except Exception as e:
            st.error(f"❌ Error generating slide deck: {str(e)}")


# Helper function to check if setup is complete
def studio_feature_available(session_state) -> bool:
    """Check if studio features can be used (tutoring setup must be complete)."""
    return session_state.get('setup_complete', False) and session_state.get('problem_statement') is not None
