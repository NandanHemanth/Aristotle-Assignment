import streamlit as st
from streamlit_lottie import st_lottie
import requests

# Page configuration
st.set_page_config(
    page_title="Tutoring App",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Lottie animation
@st.cache_data
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Sidebar
with st.sidebar:
    st.title("📚 Sources")
    st.markdown("---")
    
    # Source input methods
    st.subheader("Upload Source Material")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a file",
        type=["pdf", "html", "docx"],
        help="Upload PDF, HTML, or DOCX files"
    )
    
    if uploaded_file:
        st.success(f"✓ {uploaded_file.name} uploaded")
    
    st.markdown("**OR**")
    
    # URL input
    url_input = st.text_input(
        "Paste a URL",
        placeholder="https://example.com/article",
        help="Enter a URL to extract content from"
    )
    
    if url_input:
        st.success(f"✓ URL added")
    
    st.markdown("---")
    
    # Lottie animation
    lottie_url = "https://lottie.host/eb688d7a-a2ed-47de-915c-a06c0908678b/bNuqYqecqk.json"
    lottie_animation = load_lottie_url(lottie_url)
    
    if lottie_animation:
        st_lottie(lottie_animation, height=150, key="sidebar_animation")

# Main content area - 2 sections (Chat: 2/3, Studio: 1/3)
chat_col, studio_col = st.columns([2, 1])

# Chat Section (Left - 2/3 width)
with chat_col:
    st.header("💬 Chat")
    
    # Chat messages container
    chat_container = st.container(height=500)
    with chat_container:
        if not uploaded_file and not url_input:
            st.info("📤 Add a source to get started\n\nUpload a source file or paste a URL in the sidebar.")
        else:
            st.write("Chat interface will appear here...")
    
    # Chat input at the bottom
    user_input = st.chat_input("Upload a source to get started")

# Studio Section (Right - 1/3 width)
with studio_col:
    st.header("🎨 Studio")
    
    # Studio options
    st.markdown("### Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎵 Audio Overview", use_container_width=True):
            st.info("Audio Overview")
        if st.button("🧠 Mind Map", use_container_width=True):
            st.info("Mind Map")
        if st.button("📊 Infographic", use_container_width=True):
            st.info("Infographic")
    
    with col2:
        if st.button("🎥 Video Overview", use_container_width=True):
            st.info("Video Overview")
        if st.button("📝 Reports", use_container_width=True):
            st.info("Reports")
        if st.button("📑 Quiz", use_container_width=True):
            st.info("Quiz")
        if st.button("🎯 Slide deck", use_container_width=True):
            st.info("Slide deck")
    
    st.markdown("---")
    
    # Studio output area
    st.markdown("### Output")
    st.info("✨ Studio output will be saved here.\n\nAfter adding sources, click to add Audio Overview, study guide, mind map and more!")
    
    if st.button("📝 Add note", use_container_width=True):
        st.success("Note added!")
