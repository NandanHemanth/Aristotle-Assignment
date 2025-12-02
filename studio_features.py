"""
Studio Features Module
Implements all Studio button functionality with pop-ups using different OpenRouter models.
Enhanced with actual file generation: MP3 audio, MP4 video, and PDF slides.
"""

import streamlit as st
from openrouter_client import OpenRouterClient
from config import OPENROUTER_API_KEY
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Media generation libraries
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from PIL import Image, ImageDraw, ImageFont
import markdown
import re

# Initialize OpenRouter client
client = OpenRouterClient(api_key=OPENROUTER_API_KEY)

# Create output directory for generated files
OUTPUT_DIR = Path("studio_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

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
    """Generate an MP3 audio file summary of the problem."""
    st.markdown("### Generating Audio Overview...")

    with st.spinner("Creating audio script and MP3..."):
        try:
            # Step 1: Generate script
            prompt = f"""Create a short, engaging audio script (30-60 seconds when read aloud) that explains this problem:

{problem_statement}

The script should:
1. Briefly state what the problem asks
2. Highlight the key concepts involved
3. Mention what approach would be needed (without giving the answer)
4. Be written in a conversational, easy-to-understand tone

Format as plain text ready to be read aloud (no markdown, no special formatting)."""

            messages = [{"role": "user", "content": prompt}]

            response = client.chat_completion(
                model=STUDIO_MODELS["audio"],
                messages=messages,
                stream=False,
                temperature=0.7
            )

            script = response["choices"][0]["message"]["content"]

            # Clean script for TTS (remove markdown symbols if any)
            clean_script = re.sub(r'[#*`]', '', script)

            # Step 2: Generate MP3 using gTTS
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = OUTPUT_DIR / f"audio_overview_{timestamp}.mp3"

            tts = gTTS(text=clean_script, lang='en', slow=False)
            tts.save(str(audio_filename))

            st.success("✅ Audio MP3 generated!")

            # Display script
            st.markdown("### 📝 Script")
            st.text_area("Audio Script", script, height=200, key="audio_script")

            # Audio player
            st.markdown("### 🎧 Play Audio")
            with open(audio_filename, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')

            # Download button
            st.download_button(
                label="⬇️ Download MP3",
                data=audio_bytes,
                file_name=f"audio_overview_{timestamp}.mp3",
                mime="audio/mp3"
            )

        except Exception as e:
            st.error(f"❌ Error generating audio: {str(e)}")


@st.dialog("🎥 Video Overview", width="large")
def video_overview_modal(problem_statement: str):
    """Generate an actual MP4 video with narration."""
    st.markdown("### Generating Video Overview...")

    with st.spinner("Creating video with narration... (this may take 30-60 seconds)"):
        try:
            # Step 1: Generate script for video
            prompt = f"""Create a concise video script (30-45 seconds) explaining this problem:

{problem_statement}

Write a clear, educational narration script. Format as plain text (no special formatting).
Focus on explaining the problem and key concepts without revealing the answer."""

            messages = [{"role": "user", "content": prompt}]

            response = client.chat_completion(
                model=STUDIO_MODELS["video"],
                messages=messages,
                stream=False,
                temperature=0.7
            )

            script = response["choices"][0]["message"]["content"]
            clean_script = re.sub(r'[#*`]', '', script)

            # Step 2: Generate audio narration
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = OUTPUT_DIR / f"video_audio_{timestamp}.mp3"

            tts = gTTS(text=clean_script, lang='en', slow=False)
            tts.save(str(audio_path))

            # Step 3: Create simple video frames with text
            video_path = OUTPUT_DIR / f"video_overview_{timestamp}.mp4"

            # Create a background image with problem text
            img_width, img_height = 1280, 720
            background = Image.new('RGB', (img_width, img_height), color=(30, 40, 60))
            draw = ImageDraw.Draw(background)

            # Add title
            title_text = "Problem Overview"
            try:
                # Try to use a nicer font
                font_title = ImageFont.truetype("arial.ttf", 60)
                font_body = ImageFont.truetype("arial.ttf", 32)
            except:
                # Fallback to default font
                font_title = ImageFont.load_default()
                font_body = ImageFont.load_default()

            # Draw title
            draw.text((640, 100), title_text, fill=(255, 255, 255), font=font_title, anchor="mm")

            # Draw problem statement (wrapped)
            problem_lines = problem_statement[:200].split('\n')[:3]  # First 200 chars, max 3 lines
            y_position = 300
            for line in problem_lines:
                draw.text((640, y_position), line[:80], fill=(200, 220, 255), font=font_body, anchor="mm")
                y_position += 50

            # Save background image
            img_path = OUTPUT_DIR / f"video_frame_{timestamp}.png"
            background.save(str(img_path))

            # Step 4: Create video with moviepy
            audio_clip = AudioFileClip(str(audio_path))
            duration = audio_clip.duration

            video_clip = ImageClip(str(img_path)).set_duration(duration)
            final_video = video_clip.set_audio(audio_clip)

            final_video.write_videofile(
                str(video_path),
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )

            # Cleanup temporary files
            audio_clip.close()
            final_video.close()

            st.success("✅ Video MP4 generated!")

            # Display script
            st.markdown("### 📝 Video Script")
            st.text_area("Narration", script, height=150, key="video_script")

            # Video player
            st.markdown("### 🎬 Watch Video")
            with open(video_path, 'rb') as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)

            # Download button
            st.download_button(
                label="⬇️ Download MP4",
                data=video_bytes,
                file_name=f"video_overview_{timestamp}.mp4",
                mime="video/mp4"
            )

        except Exception as e:
            st.error(f"❌ Error generating video: {str(e)}")


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
    """Generate PDF presentation slides."""
    st.markdown("### Generating Slide Deck PDF...")

    with st.spinner("Creating presentation slides and PDF..."):
        try:
            # Step 1: Generate slide content
            prompt = f"""Create a slide deck presentation about this problem:

{problem_statement}

Generate 6-8 slides with:
1. Title slide
2. Problem statement slide
3. Key concepts (2-3 slides)
4. Approach methodology slide
5. Practice/Summary slide

For each slide, provide:
- Slide number and title (use ## for slide titles)
- Main content (bullet points, max 5 per slide)

Format in markdown with slide separators (---).
Keep content concise and slide-friendly."""

            messages = [{"role": "user", "content": prompt}]

            response = client.chat_completion(
                model=STUDIO_MODELS["slidedeck"],
                messages=messages,
                stream=False,
                temperature=0.6
            )

            slides_content = response["choices"][0]["message"]["content"]

            # Step 2: Parse slides and create PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = OUTPUT_DIR / f"slides_{timestamp}.pdf"

            # Create PDF
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )

            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                textColor='#1a1a1a',
                spaceAfter=30,
                alignment=TA_CENTER
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading1'],
                fontSize=18,
                textColor='#2c3e50',
                spaceAfter=12,
                alignment=TA_CENTER
            )
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=12,
                textColor='#333333',
                spaceAfter=8,
                alignment=TA_LEFT
            )

            # Build PDF content
            story = []

            # Split slides by separator
            slide_sections = slides_content.split('---')

            for i, slide in enumerate(slide_sections):
                if slide.strip():
                    # Parse slide content
                    lines = slide.strip().split('\n')

                    for line in lines:
                        line = line.strip()
                        if line.startswith('##'):
                            # Slide title
                            title = line.replace('##', '').strip()
                            if i == 0:
                                story.append(Paragraph(title, title_style))
                            else:
                                story.append(Paragraph(title, heading_style))
                            story.append(Spacer(1, 0.2*inch))
                        elif line.startswith('-') or line.startswith('*'):
                            # Bullet point
                            content = line.lstrip('-*').strip()
                            story.append(Paragraph(f"• {content}", body_style))
                        elif line and not line.startswith('#'):
                            # Regular text
                            story.append(Paragraph(line, body_style))

                    # Page break between slides
                    if i < len(slide_sections) - 1:
                        story.append(PageBreak())

            # Build PDF
            doc.build(story)

            st.success("✅ Slide deck PDF generated!")

            # Display markdown preview
            st.markdown("### 📄 Slides Preview")
            st.markdown(slides_content)

            # PDF download
            st.markdown("### 📥 Download PDF")
            with open(pdf_path, 'rb') as pdf_file:
                pdf_bytes = pdf_file.read()
                st.download_button(
                    label="⬇️ Download Slide Deck PDF",
                    data=pdf_bytes,
                    file_name=f"slides_{timestamp}.pdf",
                    mime="application/pdf"
                )

            st.info("💡 **Tip:** Open the PDF in any PDF reader or import into PowerPoint/Google Slides.")

        except Exception as e:
            st.error(f"❌ Error generating slide deck: {str(e)}")


# Helper function to check if setup is complete
def studio_feature_available(session_state) -> bool:
    """Check if studio features can be used (tutoring setup must be complete)."""
    return session_state.get('setup_complete', False) and session_state.get('problem_statement') is not None
