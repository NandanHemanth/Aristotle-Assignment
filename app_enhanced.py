"""
Enhanced Aristotle AI Tutor with Clean UI/UX
Supports: Text, PDF, Images, YouTube videos, Web URLs
Optimized for: Latency, caching, performance, multi-model utilization
"""

import streamlit as st
import time
from PIL import Image
import io
from tutoring_engine import TutoringEngine
from utils import process_uploaded_file, encode_image_to_base64
from content_extractors import extract_content, detect_content_type
from config import APP_TITLE, MODELS

# Page configuration
st.set_page_config(
    page_title="Aristotle AI Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enhanced CSS for modern, clean UI
st.markdown(
    """
<style>
    /* Global Styles */
    .main {
        background-color: #f8f9fa;
    }

    /* Header */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
    }

    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Chat Container */
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        max-height: 600px;
        overflow-y: auto;
    }

    /* Chat Messages */
    .chat-message {
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 15%;
        border-bottom-right-radius: 4px;
    }

    .assistant-message {
        background: #f1f3f5;
        color: #212529;
        margin-right: 15%;
        border-bottom-left-radius: 4px;
        border-left: 4px solid #667eea;
    }

    .message-label {
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.4rem;
        opacity: 0.8;
    }

    /* Input Section */
    .input-section {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.3rem 0;
    }

    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        border-radius: 10px;
        padding: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Problem Context Box */
    .problem-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Success/Error Messages */
    .success-msg {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 8px;
        color: #155724;
    }

    .error-msg {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 8px;
        color: #721c24;
    }

    /* Loading Animation */
    .loading-dots {
        display: inline-block;
    }

    .loading-dots::after {
        content: '...';
        animation: dots 1.5s steps(4, end) infinite;
    }

    @keyframes dots {
        0%, 20% { content: '.'; }
        40% { content: '..'; }
        60%, 100% { content: '...'; }
    }
</style>
""",
    unsafe_allow_html=True,
)


def init_session_state():
    """Initialize Streamlit session state."""
    if "engine" not in st.session_state:
        st.session_state.engine = TutoringEngine()
    if "problem_loaded" not in st.session_state:
        st.session_state.problem_loaded = False
    if "solution_generated" not in st.session_state:
        st.session_state.solution_generated = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "show_advanced" not in st.session_state:
        st.session_state.show_advanced = False
    if "extraction_metadata" not in st.session_state:
        st.session_state.extraction_metadata = {}


def display_header():
    """Display modern header."""
    st.markdown(
        '<div class="main-header">🎓 Aristotle AI Tutor</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">Intelligent Socratic Learning • Multi-Modal Input • Optimized Performance</div>',
        unsafe_allow_html=True,
    )
    st.divider()


def display_sidebar():
    """Enhanced sidebar with comprehensive information."""
    with st.sidebar:
        st.markdown("### 🤖 System Status")

        # Active Models
        with st.expander("🧠 Active Models", expanded=True):
            st.caption("**Vision:** GPT-4o-mini")
            st.caption("**Reasoning:** DeepSeek-R1")
            st.caption("**Tutor:** Claude Haiku 4.5:nitro")
            st.caption("**Verifier:** GPT-4o-mini")

        st.divider()

        # Performance Metrics
        if st.session_state.solution_generated:
            st.markdown("### 📊 Performance")
            metrics = st.session_state.engine.get_metrics()

            # Custom metric cards
            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-label">Solution Generation</div>
                <div class="metric-value">{metrics['solution_generation_time']:.2f}s</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-label">Total Cost</div>
                <div class="metric-value">${metrics['total_cost']:.4f}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-label">Messages</div>
                <div class="metric-value">{metrics['conversation_length']}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.divider()

        # Architecture Info
        with st.expander("🏗️ Architecture"):
            st.markdown(
                """
            **3-Stage Pipeline:**
            1. Input Processing
            2. Solution Generation (Isolated)
            3. Socratic Tutoring + Verification

            **Key Innovation:**
            Structural separation prevents solution leakage
            """
            )

        st.divider()

        # Advanced Options
        st.session_state.show_advanced = st.checkbox(
            "Show Advanced Options", value=False
        )

        if st.session_state.show_advanced:
            with st.expander("⚙️ Advanced Settings"):
                if st.session_state.solution_generated and st.session_state.engine.reference_solution:
                    if st.button("🔍 View Reference Solution"):
                        st.warning("⚠️ Hidden from tutor to prevent leakage")
                        st.code(st.session_state.engine.reference_solution[:500] + "...")

                if st.session_state.extraction_metadata:
                    st.json(st.session_state.extraction_metadata)

        st.divider()

        # Reset Button
        if st.button("🔄 New Problem", use_container_width=True, type="primary"):
            st.session_state.engine.reset()
            st.session_state.problem_loaded = False
            st.session_state.solution_generated = False
            st.session_state.messages = []
            st.session_state.extraction_metadata = {}
            st.rerun()


def handle_input_section():
    """Enhanced input section with multiple input methods."""
    st.markdown("### 📤 Load Your Problem")

    # Tabs for different input methods
    tabs = st.tabs(
        [
            "📁 Upload File",
            "✍️ Paste Text",
            "🖼️ Screenshot",
            "🎥 YouTube",
            "🌐 Web URL",
        ]
    )

    problem_text = None
    image_data = None
    processing_method = None
    metadata = {}

    # Tab 1: File Upload
    with tabs[0]:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["txt", "pdf", "docx", "png", "jpg", "jpeg"],
            help="Upload homework problems as text, PDF, DOCX, or images",
        )

        if uploaded_file:
            file_extension = uploaded_file.name.split(".")[-1].lower()
            if file_extension == "txt":
                file_type = "text"
            elif file_extension == "pdf":
                file_type = "pdf"
            elif file_extension == "docx":
                file_type = "docx"
            else:
                file_type = "image"

            if st.button("📂 Load from File", use_container_width=True):
                with st.spinner("Processing file..."):
                    problem_text, image_data, processing_method = process_uploaded_file(
                        uploaded_file, file_type
                    )
                    metadata = {"source": "file_upload", "type": file_type}

    # Tab 2: Text Input
    with tabs[1]:
        text_input = st.text_area(
            "Paste your problem here",
            height=200,
            placeholder="Enter the problem statement or question...",
        )

        if st.button("📝 Load Text", use_container_width=True) and text_input:
            problem_text = text_input
            processing_method = "text_input"
            metadata = {"source": "text_input"}

    # Tab 3: Screenshot
    with tabs[2]:
        st.info("📸 Upload a screenshot of your problem")
        screenshot_file = st.file_uploader(
            "Upload screenshot",
            type=["png", "jpg", "jpeg"],
            key="screenshot",
        )

        if screenshot_file and st.button(
            "🖼️ Load Screenshot", use_container_width=True
        ):
            image = Image.open(screenshot_file)
            st.image(image, caption="Uploaded Screenshot", use_column_width=True)
            image_data = encode_image_to_base64(image)
            processing_method = "screenshot"
            metadata = {"source": "screenshot"}

    # Tab 4: YouTube
    with tabs[3]:
        st.info("🎥 Extract content from educational YouTube videos")
        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
        )

        if st.button("🎬 Load YouTube Video", use_container_width=True) and youtube_url:
            with st.spinner("Extracting transcript from video..."):
                content, metadata, method = extract_content(youtube_url, "youtube")
                if not metadata.get("error"):
                    problem_text = content
                    processing_method = method
                    st.success(
                        f"✅ Extracted {metadata.get('word_count', 0)} words from video"
                    )
                    st.session_state.extraction_metadata = metadata
                else:
                    st.error(content)

    # Tab 5: Web URL
    with tabs[4]:
        st.info("🌐 Extract content from educational websites")
        web_url = st.text_input(
            "Web URL",
            placeholder="https://example.com/article...",
        )

        if st.button("🔗 Load Web Page", use_container_width=True) and web_url:
            with st.spinner("Crawling and extracting content..."):
                content, metadata, method = extract_content(web_url, "url")
                if not metadata.get("error"):
                    problem_text = content
                    processing_method = method
                    st.success(
                        f"✅ Extracted from: {metadata.get('title', 'Unknown')}"
                    )
                    st.session_state.extraction_metadata = metadata
                else:
                    st.error(content)

    # Process the loaded content
    if problem_text or image_data:
        st.divider()
        if st.button("🚀 Start Tutoring Session", type="primary", use_container_width=True):
            process_problem(problem_text, image_data, processing_method, metadata)


def process_problem(problem_text, image_data, processing_method, metadata):
    """Process the problem and start tutoring session."""
    # Extract from image if needed
    if image_data and not problem_text:
        with st.spinner("🔍 Analyzing image..."):
            start_time = time.time()
            problem_text = st.session_state.engine.process_problem_image(image_data)
            extraction_time = time.time() - start_time
            st.success(f"✅ Problem extracted in {extraction_time:.2f}s")
            st.info(f"**Extracted:** {problem_text[:200]}...")

    # Set problem statement
    if problem_text:
        st.session_state.engine.problem_statement = problem_text

        # Generate reference solution
        with st.spinner("🧠 Generating reference solution (reasoning in progress)..."):
            solution, gen_time = st.session_state.engine.generate_reference_solution(
                problem_text
            )

        st.success(
            f"✅ Solution generated in {gen_time:.2f}s and stored securely (hidden from tutor)"
        )

        st.session_state.problem_loaded = True
        st.session_state.solution_generated = True

        # Initialize conversation
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I see you have a problem to work on. Before we begin, can you tell me what you understand about this problem? What is it asking you to find or solve?",
            }
        ]

        st.rerun()


def display_chat_interface():
    """Modern chat interface with clean design."""
    # Problem Context
    with st.expander("📝 Problem Statement", expanded=False):
        st.markdown(
            f'<div class="problem-box">{st.session_state.engine.problem_statement[:500]}...</div>',
            unsafe_allow_html=True,
        )

    # Chat Container
    st.markdown("### 💬 Conversation")
    chat_html = '<div class="chat-container">'

    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            chat_html += f'''
            <div class="chat-message user-message">
                <div class="message-label">You</div>
                <div>{content}</div>
            </div>
            '''
        else:
            chat_html += f'''
            <div class="chat-message assistant-message">
                <div class="message-label">Aristotle</div>
                <div>{content}</div>
            </div>
            '''

    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    # Input Section
    st.divider()
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_area(
            "Your response",
            height=100,
            placeholder="Share your thoughts, work, or ask questions...",
            key="chat_input",
            label_visibility="collapsed",
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        send_button = st.button("📨 Send", type="primary", use_container_width=True)

    if send_button and user_input:
        handle_chat_message(user_input)


def handle_chat_message(user_input: str):
    """Handle chat message with streaming response."""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Stream tutor response
    with st.spinner("🤔 Aristotle is thinking..."):
        full_response = ""
        try:
            for chunk in st.session_state.engine.chat(user_input, stream=True):
                full_response += chunk
        except Exception as e:
            full_response = f"Error: {str(e)}"

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()


def display_example_problems():
    """Display example problems for quick start."""
    st.markdown("### 💡 Try an Example")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📐 Algebra", use_container_width=True):
            load_example(
                "Solve for x: 2x + 5 = 3x - 7",
                "Can you tell me what the first step should be to isolate x?",
            )

    with col2:
        if st.button("🧪 Physics", use_container_width=True):
            load_example(
                "A ball is thrown upward with initial velocity 20 m/s. How high will it go? (g = 10 m/s²)",
                "What do you know about how objects move when thrown upward?",
            )

    with col3:
        if st.button("📊 Calculus", use_container_width=True):
            load_example(
                "Find the derivative of f(x) = x³ + 2x² - 5x + 1",
                "What rules do you know for finding derivatives of polynomials?",
            )


def load_example(problem: str, initial_message: str):
    """Load an example problem."""
    st.session_state.engine.problem_statement = problem
    with st.spinner("Generating solution..."):
        solution, gen_time = st.session_state.engine.generate_reference_solution(problem)
    st.session_state.problem_loaded = True
    st.session_state.solution_generated = True
    st.session_state.messages = [{"role": "assistant", "content": initial_message}]
    st.rerun()


def main():
    """Main application logic."""
    init_session_state()
    display_header()
    display_sidebar()

    if not st.session_state.problem_loaded:
        # Show input interface
        handle_input_section()

        st.divider()
        display_example_problems()
    else:
        # Show chat interface
        display_chat_interface()


if __name__ == "__main__":
    main()
