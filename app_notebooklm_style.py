"""
Aristotle AI Tutor - NotebookLM Style UI
Clean 3-column layout: Sources (left) | Chat (center) | Studio (right)
"""

import streamlit as st
import time
from PIL import Image
from tutoring_engine import TutoringEngine
from utils import process_uploaded_file, encode_image_to_base64
from content_extractors import extract_content

# Page configuration
st.set_page_config(
    page_title="Aristotle AI Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for NotebookLM-style layout
st.markdown("""
<style>
    /* Hide default sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Main container */
    .main {
        padding: 0 !important;
        background-color: #1a1a1a;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Header */
    .app-header {
        background-color: #2d2d2d;
        padding: 0.8rem 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #3d3d3d;
    }
    
    .app-title {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Three column layout */
    .layout-container {
        display: flex;
        height: calc(100vh - 60px);
        background-color: #1a1a1a;
    }
    
    /* Left sidebar - Sources */
    .left-sidebar {
        width: 280px;
        background-color: #2d2d2d;
        border-right: 1px solid #3d3d3d;
        overflow-y: auto;
        padding: 1rem;
    }
    
    .sidebar-section {
        margin-bottom: 1.5rem;
    }
    
    .sidebar-title {
        color: #ffffff;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .source-item {
        background-color: #3d3d3d;
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        color: #e0e0e0;
        font-size: 0.85rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .source-item:hover {
        background-color: #4d4d4d;
    }
    
    .source-icon {
        margin-right: 0.5rem;
    }
    
    /* Center - Chat */
    .center-chat {
        flex: 1;
        display: flex;
        flex-direction: column;
        background-color: #1a1a1a;
        overflow: hidden;
    }
    
    .chat-header {
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #3d3d3d;
        color: #ffffff;
        font-weight: 500;
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem;
    }
    
    .chat-input-area {
        padding: 1rem 1.5rem;
        border-top: 1px solid #3d3d3d;
        background-color: #2d2d2d;
    }
    
    .message {
        margin-bottom: 1.5rem;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .message-user {
        text-align: right;
    }
    
    .message-content {
        display: inline-block;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        max-width: 80%;
        text-align: left;
    }
    
    .message-user .message-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .message-assistant .message-content {
        background-color: #2d2d2d;
        color: #e0e0e0;
        border: 1px solid #3d3d3d;
    }
    
    .message-label {
        font-size: 0.75rem;
        color: #888;
        margin-bottom: 0.3rem;
    }
    
    /* Right sidebar - Studio */
    .right-sidebar {
        width: 280px;
        background-color: #2d2d2d;
        border-left: 1px solid #3d3d3d;
        overflow-y: auto;
        padding: 1rem;
    }
    
    .studio-tool {
        background-color: #3d3d3d;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        cursor: pointer;
        transition: all 0.2s;
        text-align: center;
    }
    
    .studio-tool:hover {
        background-color: #4d4d4d;
        transform: translateY(-2px);
    }
    
    .tool-icon {
        font-size: 1.5rem;
        margin-bottom: 0.3rem;
    }
    
    .tool-name {
        color: #ffffff;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Upload area */
    .upload-area {
        background-color: #3d3d3d;
        border: 2px dashed #5d5d5d;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        margin-bottom: 1rem;
    }
    
    .upload-area:hover {
        border-color: #667eea;
        background-color: #4d4d4d;
    }
    
    .upload-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .upload-text {
        color: #b0b0b0;
        font-size: 0.85rem;
    }
    
    /* Empty state */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #888;
        text-align: center;
        padding: 2rem;
    }
    
    .empty-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    .empty-text {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .empty-subtext {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Streamlit overrides */
    .stTextInput input, .stTextArea textarea {
        background-color: #3d3d3d !important;
        color: #ffffff !important;
        border: 1px solid #5d5d5d !important;
        border-radius: 8px !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Metrics */
    .metric-card {
        background-color: #3d3d3d;
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #888;
        font-size: 0.75rem;
        margin-bottom: 0.2rem;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state."""
    if "engine" not in st.session_state:
        st.session_state.engine = TutoringEngine()
    if "sources" not in st.session_state:
        st.session_state.sources = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "problem_loaded" not in st.session_state:
        st.session_state.problem_loaded = False


def render_header():
    """Render top header bar."""
    st.markdown("""
    <div class="app-header">
        <div class="app-title">
            <span>🎓</span>
            <span>Aristotle AI Tutor</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_left_sidebar():
    """Render left sidebar with sources."""
    with st.container():
        st.markdown('<div class="sidebar-title">Sources</div>', unsafe_allow_html=True)
        
        # Upload section
        st.markdown("**Add Sources**")
        
        uploaded_file = st.file_uploader(
            "Upload file",
            type=["txt", "pdf", "docx", "png", "jpg", "jpeg"],
            label_visibility="collapsed",
            key="file_upload"
        )
        
        if uploaded_file:
            if st.button("📂 Add File", use_container_width=True):
                process_file_upload(uploaded_file)
        
        st.markdown("---")
        
        # URL input
        st.markdown("**Add from URL**")
        url_input = st.text_input(
            "Paste URL",
            placeholder="YouTube or web URL...",
            label_visibility="collapsed",
            key="url_input"
        )
        
        if url_input:
            if st.button("🔗 Add URL", use_container_width=True):
                process_url_input(url_input)
        
        st.markdown("---")
        
        # Display sources
        if st.session_state.sources:
            st.markdown('<div class="sidebar-title">Loaded Sources</div>', unsafe_allow_html=True)
            for idx, source in enumerate(st.session_state.sources):
                icon = get_source_icon(source['type'])
                st.markdown(f"""
                <div class="source-item">
                    <span class="source-icon">{icon}</span>
                    {source['name'][:30]}...
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="color: #666; font-size: 0.85rem; margin-top: 2rem; text-align: center;">
                No sources added yet.<br>Upload files or add URLs above.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # System status
        if st.session_state.problem_loaded:
            st.markdown('<div class="sidebar-title">System Status</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Status</div>
                <div class="metric-value">✅ Ready</div>
            </div>
            """, unsafe_allow_html=True)
            
            metrics = st.session_state.engine.get_metrics()
            if metrics['conversation_length'] > 0:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Messages</div>
                    <div class="metric-value">{metrics['conversation_length']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Cost</div>
                    <div class="metric-value">${metrics['total_cost']:.4f}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Reset button
        if st.button("🔄 New Session", use_container_width=True, type="secondary"):
            st.session_state.engine.reset()
            st.session_state.sources = []
            st.session_state.messages = []
            st.session_state.problem_loaded = False
            st.rerun()


def render_center_chat():
    """Render center chat area."""
    with st.container():
        if not st.session_state.problem_loaded:
            # Empty state
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">💬</div>
                <div class="empty-text">Add a source to get started</div>
                <div class="empty-subtext">Upload a file or paste a URL in the left sidebar</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Chat messages
            for message in st.session_state.messages:
                role = message["role"]
                content = message["content"]
                
                if role == "user":
                    st.markdown(f"""
                    <div class="message message-user">
                        <div class="message-label">You</div>
                        <div class="message-content">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="message message-assistant">
                        <div class="message-label">Aristotle</div>
                        <div class="message-content">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Chat input at bottom
            st.markdown("---")
            col1, col2 = st.columns([5, 1])
            
            with col1:
                user_input = st.text_area(
                    "Message",
                    placeholder="Share your thoughts or ask questions...",
                    height=80,
                    label_visibility="collapsed",
                    key="chat_input"
                )
            
            with col2:
                st.write("")
                st.write("")
                if st.button("Send", use_container_width=True):
                    if user_input:
                        handle_chat_message(user_input)


def render_right_sidebar():
    """Render right sidebar with studio tools."""
    with st.container():
        st.markdown('<div class="sidebar-title">Studio</div>', unsafe_allow_html=True)
        
        st.markdown("**Output Tools**")
        
        # Studio tools
        tools = [
            ("🎵", "Audio Overview"),
            ("🎥", "Video Overview"),
            ("🗺️", "Mind Map"),
            ("📊", "Reports"),
            ("🗂️", "Flashcards"),
            ("❓", "Quiz"),
            ("📈", "Infographic"),
            ("📽️", "Slide Deck"),
        ]
        
        for icon, name in tools:
            if st.button(f"{icon} {name}", use_container_width=True, key=f"tool_{name}"):
                st.info(f"{name} - Coming soon!")
        
        st.markdown("---")
        
        # Add note
        if st.button("📝 Add Note", use_container_width=True):
            st.info("Note feature - Coming soon!")


def get_source_icon(source_type):
    """Get icon for source type."""
    icons = {
        "text": "📄",
        "pdf": "📕",
        "docx": "📘",
        "image": "🖼️",
        "youtube": "🎥",
        "url": "🌐",
    }
    return icons.get(source_type, "📄")


def process_file_upload(uploaded_file):
    """Process uploaded file."""
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if file_extension == "txt":
        file_type = "text"
    elif file_extension == "pdf":
        file_type = "pdf"
    elif file_extension == "docx":
        file_type = "docx"
    else:
        file_type = "image"
    
    with st.spinner("Processing file..."):
        problem_text, image_data, processing_method = process_uploaded_file(
            uploaded_file, file_type
        )
        
        # Extract from image if needed
        if image_data and not problem_text:
            problem_text = st.session_state.engine.process_problem_image(image_data)
        
        if problem_text:
            # Add to sources
            st.session_state.sources.append({
                "name": uploaded_file.name,
                "type": file_type,
                "content": problem_text[:200]
            })
            
            # Generate solution and start session
            start_tutoring_session(problem_text)


def process_url_input(url):
    """Process URL input."""
    with st.spinner("Extracting content..."):
        content, metadata, method = extract_content(url)
        
        if not metadata.get("error"):
            # Determine type
            if "youtube" in url.lower():
                source_type = "youtube"
            else:
                source_type = "url"
            
            # Add to sources
            st.session_state.sources.append({
                "name": metadata.get("title", url)[:50],
                "type": source_type,
                "content": content[:200]
            })
            
            # Start tutoring session
            start_tutoring_session(content)
        else:
            st.error(content)


def start_tutoring_session(problem_text):
    """Start tutoring session with problem."""
    st.session_state.engine.problem_statement = problem_text
    
    # Generate reference solution
    solution, gen_time = st.session_state.engine.generate_reference_solution(problem_text)
    
    st.session_state.problem_loaded = True
    
    # Initialize conversation
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I see you have a problem to work on. Before we begin, can you tell me what you understand about this problem? What is it asking you to find or solve?"
        }
    ]
    
    st.success(f"✅ Ready! Solution generated in {gen_time:.2f}s")
    time.sleep(1)
    st.rerun()


def handle_chat_message(user_input):
    """Handle chat message."""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get tutor response
    with st.spinner("Thinking..."):
        full_response = ""
        try:
            for chunk in st.session_state.engine.chat(user_input, stream=True):
                full_response += chunk
        except Exception as e:
            full_response = f"Error: {str(e)}"
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()


def main():
    """Main application."""
    init_session_state()
    render_header()
    
    # Three column layout
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col1:
        render_left_sidebar()
    
    with col2:
        render_center_chat()
    
    with col3:
        render_right_sidebar()


if __name__ == "__main__":
    main()
