"""
Aristotle AI Tutor - NotebookLM-Style Interface
Beautiful, modern UI with sources panel, chat, and analytics
"""

import streamlit as st
import time
from PIL import Image
from tutoring_engine import TutoringEngine
from utils import process_uploaded_file, encode_image_to_base64
from content_extractors import extract_content, detect_content_type
from config import MODELS

# Page configuration
st.set_page_config(
    page_title="Aristotle AI Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for NotebookLM-style UI
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background-color: #1a1a1a;
        color: #e8eaed;
    }

    .stApp {
        background-color: #1a1a1a;
    }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: #9aa0a6;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }

    /* Three Column Layout */
    .column-container {
        display: flex;
        gap: 1rem;
        height: calc(100vh - 200px);
    }

    /* Sources Panel (Left) */
    .sources-panel {
        background-color: #2d2d2d;
        border-radius: 12px;
        padding: 1.5rem;
        width: 300px;
        overflow-y: auto;
    }

    .sources-title {
        color: #e8eaed;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .source-item {
        background-color: #3c4043;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 3px solid #667eea;
        transition: all 0.2s;
    }

    .source-item:hover {
        background-color: #444746;
        transform: translateX(4px);
    }

    .source-type {
        color: #667eea;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }

    .source-title-text {
        color: #e8eaed;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.3rem;
    }

    .source-meta {
        color: #9aa0a6;
        font-size: 0.75rem;
    }

    /* Chat Panel (Center) */
    .chat-panel {
        background-color: #2d2d2d;
        border-radius: 12px;
        padding: 1.5rem;
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
    }

    .chat-title {
        color: #e8eaed;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .chat-messages {
        flex: 1;
        overflow-y: auto;
        margin-bottom: 1rem;
    }

    .message {
        margin-bottom: 1rem;
        padding: 1rem;
        border-radius: 8px;
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 4px;
    }

    .assistant-message {
        background-color: #3c4043;
        color: #e8eaed;
        margin-right: 20%;
        border-bottom-left-radius: 4px;
        border-left: 3px solid #667eea;
    }

    .message-role {
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }

    /* Info Panel (Right) */
    .info-panel {
        background-color: #2d2d2d;
        border-radius: 12px;
        padding: 1.5rem;
        width: 280px;
        overflow-y: auto;
    }

    .info-title {
        color: #e8eaed;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    .metric-label {
        color: #9aa0a6;
        font-size: 0.75rem;
        margin-bottom: 0.3rem;
    }

    .metric-value {
        color: #e8eaed;
        font-size: 1.5rem;
        font-weight: 700;
    }

    .model-badge {
        background-color: #3c4043;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.5rem;
        font-size: 0.8rem;
    }

    .model-label {
        color: #667eea;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }

    .model-name {
        color: #9aa0a6;
        font-size: 0.75rem;
    }

    /* Upload Area */
    .upload-area {
        background-color: #3c4043;
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1rem;
        transition: all 0.3s;
    }

    .upload-area:hover {
        border-color: #764ba2;
        background-color: #444746;
    }

    .upload-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .upload-text {
        color: #e8eaed;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }

    .upload-hint {
        color: #9aa0a6;
        font-size: 0.85rem;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    }

    /* Input Fields */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        background-color: #3c4043;
        color: #e8eaed;
        border: 1px solid #5f6368;
        border-radius: 8px;
    }

    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #2d2d2d;
        border-radius: 10px;
        padding: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #3c4043;
        color: #9aa0a6;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #3c4043;
        border-radius: 8px;
        color: #e8eaed;
    }

    /* Success/Error Messages */
    .stSuccess {
        background-color: rgba(46, 125, 50, 0.1);
        border-left: 3px solid #2e7d32;
        color: #e8eaed;
    }

    .stError {
        background-color: rgba(211, 47, 47, 0.1);
        border-left: 3px solid #d32f2f;
        color: #e8eaed;
    }

    .stInfo {
        background-color: rgba(2, 136, 209, 0.1);
        border-left: 3px solid #0288d1;
        color: #e8eaed;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state"""
    if "engine" not in st.session_state:
        st.session_state.engine = TutoringEngine()
    if "sources" not in st.session_state:
        st.session_state.sources = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "problem_loaded" not in st.session_state:
        st.session_state.problem_loaded = False


def add_source(source_type, title, content, metadata=None):
    """Add a source to the sources list"""
    source = {
        "type": source_type,
        "title": title,
        "content": content,
        "metadata": metadata or {},
        "timestamp": time.time()
    }
    st.session_state.sources.append(source)


def display_header():
    """Display main header"""
    st.markdown('<div class="main-header">🎓 Aristotle AI Tutor</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Intelligent Socratic Learning • Multi-Modal Input • Optimized Performance</div>',
        unsafe_allow_html=True
    )


def display_sources_panel():
    """Display sources panel (left)"""
    st.markdown('<div class="sources-title">📚 Sources</div>', unsafe_allow_html=True)

    if not st.session_state.sources:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #9aa0a6;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📁</div>
            <div>No sources added yet</div>
            <div style="font-size: 0.85rem; margin-top: 0.5rem;">Upload files, add YouTube videos, or paste URLs to get started</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, source in enumerate(st.session_state.sources):
            icon = {
                "file": "📄",
                "pdf": "📕",
                "image": "🖼️",
                "youtube": "🎥",
                "url": "🌐",
                "text": "📝"
            }.get(source["type"], "📄")

            st.markdown(f"""
            <div class="source-item">
                <div class="source-type">{icon} {source["type"].upper()}</div>
                <div class="source-title-text">{source["title"][:50]}...</div>
                <div class="source-meta">{len(source["content"].split())} words</div>
            </div>
            """, unsafe_allow_html=True)


def display_upload_interface():
    """Display upload interface"""
    st.markdown("### 📤 Add Sources")

    tabs = st.tabs(["📁 Upload File", "🎥 YouTube", "🌐 Web URL", "✍️ Paste Text"])

    # Tab 1: File Upload
    with tabs[0]:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["txt", "pdf", "png", "jpg", "jpeg"],
            label_visibility="collapsed"
        )

        if uploaded_file and st.button("📂 Load File", use_container_width=True):
            file_extension = uploaded_file.name.split(".")[-1].lower()
            file_type = "text" if file_extension == "txt" else "pdf" if file_extension == "pdf" else "image"

            with st.spinner("Processing file..."):
                problem_text, image_data, method = process_uploaded_file(uploaded_file, file_type)

                if image_data:
                    problem_text = st.session_state.engine.process_problem_image(image_data)

                add_source(file_type, uploaded_file.name, problem_text)
                st.success(f"✅ Added {uploaded_file.name}")
                st.rerun()

    # Tab 2: YouTube
    with tabs[1]:
        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed"
        )

        if youtube_url and st.button("🎬 Load YouTube Video", use_container_width=True):
            with st.spinner("Extracting transcript..."):
                content, metadata, method = extract_content(youtube_url, "youtube")

                if not metadata.get("error"):
                    add_source("youtube", f"YouTube: {metadata.get('video_id', 'Unknown')}", content, metadata)
                    st.success(f"✅ Extracted {metadata.get('word_count', 0)} words from video")
                    st.rerun()
                else:
                    st.error(content)

    # Tab 3: Web URL
    with tabs[2]:
        web_url = st.text_input(
            "Web URL",
            placeholder="https://example.com/article...",
            label_visibility="collapsed"
        )

        if web_url and st.button("🔗 Load Web Page", use_container_width=True):
            with st.spinner("Crawling website..."):
                content, metadata, method = extract_content(web_url, "url")

                if not metadata.get("error"):
                    add_source("url", metadata.get("title", "Web Page"), content, metadata)
                    st.success(f"✅ Extracted from: {metadata.get('title', 'Unknown')}")
                    st.rerun()
                else:
                    st.error(content)

    # Tab 4: Paste Text
    with tabs[3]:
        text_input = st.text_area(
            "Paste your problem here",
            height=200,
            placeholder="Enter the problem statement or question...",
            label_visibility="collapsed"
        )

        if text_input and st.button("📝 Add Text", use_container_width=True):
            add_source("text", f"Text: {text_input[:30]}...", text_input)
            st.success("✅ Added text")
            st.rerun()

    # Generate Solution Button
    if st.session_state.sources and not st.session_state.problem_loaded:
        st.divider()
        if st.button("🚀 Start Tutoring Session", type="primary", use_container_width=True):
            # Combine all sources
            combined_content = "\n\n---\n\n".join([
                f"**{s['title']}**\n\n{s['content']}" for s in st.session_state.sources
            ])

            with st.spinner("🧠 Generating reference solution..."):
                solution, gen_time = st.session_state.engine.generate_reference_solution(combined_content)

            st.success(f"✅ Solution generated in {gen_time:.2f}s")
            st.session_state.problem_loaded = True
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Hello! I see you've uploaded some content. I'm here to help you understand it better. What would you like to explore first?"
            }]
            st.rerun()


def display_chat_panel():
    """Display chat panel (center)"""
    st.markdown('<div class="chat-title">💬 Chat with Aristotle</div>', unsafe_allow_html=True)

    # Display messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            st.markdown(f"""
            <div class="message user-message">
                <div class="message-role">You</div>
                <div>{content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message assistant-message">
                <div class="message-role">Aristotle</div>
                <div>{content}</div>
            </div>
            """, unsafe_allow_html=True)

    # Chat input
    st.divider()
    user_input = st.text_area(
        "Your message",
        height=100,
        placeholder="Type your question or share your work...",
        key="chat_input",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("📨 Send", type="primary", use_container_width=True)

    if send_button and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get assistant response with streaming
        full_response = ""
        try:
            for chunk in st.session_state.engine.chat(user_input, stream=True):
                full_response += chunk
        except Exception as e:
            full_response = f"Error: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()


def display_info_panel():
    """Display info panel (right)"""
    st.markdown('<div class="info-title">ℹ️ System Status</div>', unsafe_allow_html=True)

    # Active Models
    st.markdown("**🤖 Active Models**")
    st.markdown(f"""
    <div class="model-badge">
        <div class="model-label">Vision</div>
        <div class="model-name">GPT-4o-mini</div>
    </div>
    <div class="model-badge">
        <div class="model-label">Reasoning</div>
        <div class="model-name">DeepSeek-R1</div>
    </div>
    <div class="model-badge">
        <div class="model-label">Tutor</div>
        <div class="model-name">Claude Haiku 4.5</div>
    </div>
    <div class="model-badge">
        <div class="model-label">Verifier</div>
        <div class="model-name">GPT-4o-mini</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Metrics
    if st.session_state.problem_loaded:
        st.markdown("**📊 Performance**")
        metrics = st.session_state.engine.get_metrics()

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Solution Generation</div>
            <div class="metric-value">{metrics['solution_generation_time']:.2f}s</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Cost</div>
            <div class="metric-value">${metrics['total_cost']:.4f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Messages</div>
            <div class="metric-value">{metrics['conversation_length']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Architecture Info
    with st.expander("🏗️ Architecture"):
        st.markdown("""
        **3-Stage Pipeline:**
        1. Input Processing
        2. Solution Generation (Isolated)
        3. Socratic Tutoring + Verification

        **Key Innovation:**
        Structural separation prevents solution leakage
        """)

    st.divider()

    # Reset button
    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.engine.reset()
        st.session_state.sources = []
        st.session_state.messages = []
        st.session_state.problem_loaded = False
        st.rerun()


def main():
    """Main application"""
    init_session_state()
    display_header()

    # Three-column layout
    col1, col2, col3 = st.columns([1, 2.5, 1])

    with col1:
        display_sources_panel()
        st.divider()
        if not st.session_state.problem_loaded:
            display_upload_interface()

    with col2:
        if st.session_state.problem_loaded:
            display_chat_panel()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem; color: #9aa0a6;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📚</div>
                <div style="font-size: 1.5rem; margin-bottom: 1rem; color: #e8eaed;">Add sources to get started</div>
                <div style="font-size: 1rem;">Upload files, add YouTube videos, or paste URLs from the left panel</div>
                <div style="font-size: 0.9rem; margin-top: 1rem;">Once you've added your sources, click "Start Tutoring Session"</div>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        display_info_panel()


if __name__ == "__main__":
    main()
