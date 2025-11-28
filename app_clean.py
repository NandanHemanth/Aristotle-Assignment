"""
Aristotle AI Tutor - Clean UI
Collapsible sidebar | Fixed scrollable chat | Clean design
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
    initial_sidebar_state="expanded",
)

# Custom CSS for clean UI
st.markdown("""
<style>
    /* Global */
    .main {
        background-color: #0f0f0f;
        padding: 0 !important;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #2a2a2a;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #1a1a1a;
    }
    
    /* Header */
    .app-header {
        background-color: #1a1a1a;
        padding: 1rem 2rem;
        border-bottom: 1px solid #2a2a2a;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .app-title {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0;
    }
    
    /* Chat container */
    .chat-container {
        height: calc(100vh - 200px);
        overflow-y: auto;
        padding: 2rem;
        background-color: #0f0f0f;
    }
    
    /* Messages */
    .message {
        margin-bottom: 1.5rem;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .message-user {
        display: flex;
        justify-content: flex-end;
    }
    
    .message-assistant {
        display: flex;
        justify-content: flex-start;
    }
    
    .message-content {
        max-width: 70%;
        padding: 1rem 1.3rem;
        border-radius: 12px;
        line-height: 1.6;
    }
    
    .message-user .message-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 4px;
    }
    
    .message-assistant .message-content {
        background-color: #1a1a1a;
        color: #e0e0e0;
        border: 1px solid #2a2a2a;
        border-bottom-left-radius: 4px;
    }
    
    .message-label {
        font-size: 0.75rem;
        color: #666;
        margin-bottom: 0.4rem;
        font-weight: 500;
    }
    
    /* Chat input */
    .chat-input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #1a1a1a;
        border-top: 1px solid #2a2a2a;
        padding: 1.5rem 2rem;
        z-index: 99;
    }
    
    /* Empty state */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: calc(100vh - 200px);
        color: #666;
        text-align: center;
    }
    
    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.3;
    }
    
    .empty-text {
        font-size: 1.2rem;
        color: #888;
        margin-bottom: 0.5rem;
    }
    
    .empty-subtext {
        font-size: 0.95rem;
        color: #555;
    }
    
    /* Sidebar sections */
    .sidebar-section {
        margin-bottom: 2rem;
    }
    
    .section-title {
        color: #888;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1rem;
    }
    
    /* Source items */
    .source-item {
        background-color: #2a2a2a;
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.6rem;
        color: #e0e0e0;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        transition: background-color 0.2s;
    }
    
    .source-item:hover {
        background-color: #333;
    }
    
    .source-icon {
        font-size: 1.2rem;
    }
    
    .source-name {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    /* Metrics */
    .metric-card {
        background-color: #2a2a2a;
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.6rem;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.3rem;
    }
    
    .metric-value {
        color: #fff;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Secondary buttons */
    button[kind="secondary"] {
        background: #2a2a2a !important;
        color: #e0e0e0 !important;
    }
    
    button[kind="secondary"]:hover {
        background: #333 !important;
    }
    
    /* File uploader */
    .stFileUploader {
        background-color: #2a2a2a;
        border: 2px dashed #444;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stFileUploader:hover {
        border-color: #667eea;
    }
    
    /* Text input */
    .stTextInput input, .stTextArea textarea {
        background-color: #2a2a2a !important;
        color: #fff !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }
    
    /* Divider */
    hr {
        border-color: #2a2a2a;
        margin: 1.5rem 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #444;
    }
    
    /* Studio tools grid */
    .studio-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .studio-tool {
        background-color: #2a2a2a;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid transparent;
    }
    
    .studio-tool:hover {
        background-color: #333;
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    .tool-icon {
        font-size: 1.8rem;
        margin-bottom: 0.4rem;
    }
    
    .tool-name {
        color: #e0e0e0;
        font-size: 0.8rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript for auto-scroll
st.markdown("""
<script>
function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}
setTimeout(scrollToBottom, 100);
</script>
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
    if "auto_scroll" not in st.session_state:
        st.session_state.auto_scroll = True


def render_sidebar():
    """Render collapsible sidebar."""
    with st.sidebar:
        st.markdown('<p class="section-title">📤 Add Sources</p>', unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload file",
            type=["txt", "pdf", "docx", "png", "jpg", "jpeg"],
            label_visibility="collapsed",
            key="file_upload"
        )
        
        if uploaded_file:
            if st.button("📂 Add File"):
                process_file_upload(uploaded_file)
        
        st.markdown("---")
        
        # URL input
        url_input = st.text_input(
            "URL",
            placeholder="YouTube or web URL...",
            label_visibility="collapsed",
            key="url_input"
        )
        
        if url_input:
            if st.button("🔗 Add URL"):
                process_url_input(url_input)
        
        st.markdown("---")
        
        # Loaded sources
        if st.session_state.sources:
            st.markdown('<p class="section-title">📚 Loaded Sources</p>', unsafe_allow_html=True)
            for source in st.session_state.sources:
                icon = get_source_icon(source['type'])
                st.markdown(f"""
                <div class="source-item">
                    <span class="source-icon">{icon}</span>
                    <span class="source-name">{source['name']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        # System status
        if st.session_state.problem_loaded:
            st.markdown('<p class="section-title">📊 System Status</p>', unsafe_allow_html=True)
            
            metrics = st.session_state.engine.get_metrics()
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Status</div>
                <div class="metric-value">✅ Ready</div>
            </div>
            """, unsafe_allow_html=True)
            
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
        
        # New session button
        if st.button("🔄 New Session", type="secondary"):
            st.session_state.engine.reset()
            st.session_state.sources = []
            st.session_state.messages = []
            st.session_state.problem_loaded = False
            st.rerun()


def render_chat():
    """Render chat area with fixed scrollable container."""
    # Header
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">🎓 Aristotle AI Tutor</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.problem_loaded:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">💬</div>
            <div class="empty-text">Add a source to get started</div>
            <div class="empty-subtext">Upload a file or paste a URL in the sidebar</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Chat messages
        st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.markdown(f"""
                <div class="message message-user">
                    <div>
                        <div class="message-label">You</div>
                        <div class="message-content">{content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message message-assistant">
                    <div>
                        <div class="message-label">Aristotle</div>
                        <div class="message-content">{content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Spacer for fixed input
        st.markdown('<div style="height: 150px;"></div>', unsafe_allow_html=True)


def render_chat_input():
    """Render fixed chat input at bottom."""
    # Create container for input
    input_container = st.container()
    
    with input_container:
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_area(
                "Message",
                placeholder="Type your message...",
                height=80,
                label_visibility="collapsed",
                key="chat_input_field"
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("Send", key="send_btn"):
                if user_input:
                    handle_chat_message(user_input)


def render_studio():
    """Render studio tools in 2-column grid."""
    st.markdown('<p class="section-title">🎨 Studio Tools</p>', unsafe_allow_html=True)
    
    tools = [
        ("🎵", "Audio"),
        ("🎥", "Video"),
        ("🗺️", "Mind Map"),
        ("📊", "Reports"),
        ("🗂️", "Flashcards"),
        ("❓", "Quiz"),
        ("📈", "Infographic"),
        ("📽️", "Slides"),
    ]
    
    # Create 2-column grid
    for i in range(0, len(tools), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            icon, name = tools[i]
            if st.button(f"{icon}\n{name}", key=f"tool_{name}"):
                st.info(f"{name} - Coming soon!")
        
        if i + 1 < len(tools):
            with col2:
                icon, name = tools[i + 1]
                if st.button(f"{icon}\n{name}", key=f"tool_{name}"):
                    st.info(f"{name} - Coming soon!")
    
    st.markdown("---")
    
    # Add note button
    if st.button("📝 Add Note", key="add_note"):
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
    
    # Sidebar
    render_sidebar()
    
    # Main content area
    col1, col2 = st.columns([4, 1])
    
    with col1:
        render_chat()
        if st.session_state.problem_loaded:
            render_chat_input()
    
    with col2:
        if st.session_state.problem_loaded:
            render_studio()


if __name__ == "__main__":
    main()
