import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_paste_button import paste_image_button
import requests
import base64
from io import BytesIO

# Import our tutoring system
from tutoring_engine import TutoringEngine
from utils import process_uploaded_file
import studio_features
from content_extractors import extract_content, detect_content_type

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

# Initialize session state
if 'engine' not in st.session_state:
    st.session_state.engine = TutoringEngine()

if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'problem_statement' not in st.session_state:
    st.session_state.problem_statement = None

if 'pasted_image' not in st.session_state:
    st.session_state.pasted_image = None

if 'pasted_image_text' not in st.session_state:
    st.session_state.pasted_image_text = None

# Sidebar
with st.sidebar:
    st.title("📚 Sources")
    st.markdown("---")

    # Source input methods
    st.subheader("Upload Source Material")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload a file",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        help="Upload PDF, DOCX, text file, or image with your problem"
    )

    if uploaded_file:
        st.success(f"✓ {uploaded_file.name} uploaded")

    st.markdown("**OR**")

    # Manual text input
    manual_text = st.text_area(
        "Enter problem text",
        placeholder="Paste your homework problem here...",
        height=100
    )

    # Process button
    if st.button("🚀 Start Tutoring", type="primary", use_container_width=True):
        if uploaded_file or manual_text:
            with st.spinner("Processing your problem..."):
                problem_text = None
                image_data = None

                try:
                    if uploaded_file:
                        # Determine file type
                        file_type = None
                        if uploaded_file.name.endswith('.pdf'):
                            file_type = 'pdf'
                        elif uploaded_file.name.endswith('.docx'):
                            file_type = 'docx'
                        elif uploaded_file.name.endswith('.txt'):
                            file_type = 'text'
                        elif uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                            file_type = 'image'

                        # Process file
                        problem_text, image_data, method = process_uploaded_file(uploaded_file, file_type)

                        # If image, use vision model
                        if image_data:
                            problem_text = st.session_state.engine.process_problem_image(image_data)

                    elif manual_text:
                        # Detect if it's a URL (YouTube or web URL)
                        content_type = detect_content_type(manual_text)

                        if content_type in ["youtube", "url"]:
                            st.info(f"📥 Detected {content_type.upper()} link, extracting content...")
                            # Extract content from URL
                            extracted_content, metadata, method = extract_content(manual_text, content_type)

                            # Check for errors
                            if metadata.get("error"):
                                st.error(f"❌ {extracted_content}")
                                problem_text = None
                            else:
                                problem_text = extracted_content
                                st.success(f"✅ Extracted {metadata.get('word_count', 0)} words from {content_type}")
                        else:
                            # Plain text
                            problem_text = manual_text

                    if problem_text and not problem_text.startswith("Error"):
                        # Store problem
                        st.session_state.problem_statement = problem_text

                        # Generate reference solution
                        solution, gen_time = st.session_state.engine.generate_reference_solution(problem_text)

                        if not solution.startswith("Error"):
                            st.session_state.setup_complete = True
                            st.session_state.messages = []
                            st.success(f"✅ Ready! Setup took {gen_time:.1f}s")
                            st.rerun()
                        else:
                            st.error(f"❌ {solution}")
                    else:
                        st.error(f"❌ {problem_text}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please upload a file or enter text!")

    # Reset button
    if st.session_state.setup_complete:
        if st.button("🔄 New Problem", use_container_width=True):
            st.session_state.engine.reset()
            st.session_state.setup_complete = False
            st.session_state.messages = []
            st.session_state.problem_statement = None
            st.rerun()

    st.markdown("---")

    # Show metrics if active
    if st.session_state.setup_complete:
        metrics = st.session_state.engine.get_metrics()
        st.markdown("### 📊 Metrics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Messages", len(st.session_state.messages) // 2)
        with col2:
            st.metric("Cost", f"${metrics['total_cost']:.4f}")

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

    # Chat messages container (scrollable)
    chat_container = st.container(height=500)
    with chat_container:
        if not st.session_state.setup_complete:
            st.info("📤 Add a source to get started\n\nUpload a source file or paste text in the sidebar, then click 'Start Tutoring'.")
        else:
            # Show welcome message if no messages
            if len(st.session_state.messages) == 0:
                with st.chat_message("assistant"):
                    st.markdown("""
                    👋 Hello! I'm Aristotle, your AI tutor. I've reviewed your problem and I'm ready to help.

                    **Important:** I won't give you the answer directly. I'll guide you with questions to help you learn.

                    **Get started by:**
                    - Telling me what you understand about the problem
                    - Sharing any work you've done
                    - Asking about concepts you're unsure about

                    What would you like to explore first?
                    """)

            # Display all messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    # Chat input at the bottom
    if st.session_state.setup_complete:
        # Add paste image button above chat input
        col1, col2 = st.columns([1, 6])
        with col1:
            paste_result = paste_image_button(
                label="📋 Paste Image",
                key="paste_btn",
                errors="raise",
            )

        # Process pasted image
        if paste_result.image_data is not None:
            # Convert PIL image to base64
            buffered = BytesIO()
            paste_result.image_data.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode()

            # Store pasted image
            st.session_state.pasted_image = img_base64

            # Process with vision model - add data URI prefix
            with st.spinner("Processing pasted image..."):
                image_data_uri = f"data:image/png;base64,{img_base64}"
                image_text = st.session_state.engine.process_problem_image(image_data_uri)
                st.session_state.pasted_image_text = image_text
                st.success("Image pasted! Add your question below.")

        # Show pasted image preview if exists
        if st.session_state.pasted_image:
            with st.expander("📎 Pasted Image Context", expanded=True):
                st.image(f"data:image/png;base64,{st.session_state.pasted_image}", width=300)
                st.caption("Vision model extracted:")
                st.info(st.session_state.pasted_image_text)
                if st.button("❌ Clear Image"):
                    st.session_state.pasted_image = None
                    st.session_state.pasted_image_text = None
                    st.rerun()

        user_input = st.chat_input("Ask a question or share your work...")

        if user_input:
            # Prepare message content with image context if available
            message_content = user_input
            if st.session_state.pasted_image_text:
                message_content = f"[Image Context: {st.session_state.pasted_image_text}]\n\n{user_input}"

            # Add user message (display only the text, not the image context)
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })

            # Get tutor response with streaming (send full context including image)
            full_response = ""
            try:
                for chunk in st.session_state.engine.chat(message_content, stream=True):
                    full_response += chunk

                # Add assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

                # Clear pasted image after sending
                st.session_state.pasted_image = None
                st.session_state.pasted_image_text = None

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

            st.rerun()
    else:
        st.chat_input("Upload a source to get started", disabled=True)

# Studio Section (Right - 1/3 width)
with studio_col:
    st.header("🎨 Studio")

    # Studio options
    st.markdown("### Tools")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎵 Audio Overview", use_container_width=True):
            if studio_features.studio_feature_available(st.session_state):
                studio_features.audio_overview_modal(st.session_state.problem_statement)
            else:
                st.warning("⚠️ Please start tutoring first!")
        if st.button("🧠 Mind Map", use_container_width=True):
            if studio_features.studio_feature_available(st.session_state):
                studio_features.mindmap_modal(st.session_state.problem_statement)
            else:
                st.warning("⚠️ Please start tutoring first!")
        if st.button("📊 Infographic", use_container_width=True):
            if studio_features.studio_feature_available(st.session_state):
                studio_features.infographic_modal(st.session_state.problem_statement)
            else:
                st.warning("⚠️ Please start tutoring first!")

    with col2:
        if st.button("🎥 Video Overview", use_container_width=True):
            if studio_features.studio_feature_available(st.session_state):
                studio_features.video_overview_modal(st.session_state.problem_statement)
            else:
                st.warning("⚠️ Please start tutoring first!")
        if st.button("📝 Reports", use_container_width=True):
            if studio_features.studio_feature_available(st.session_state):
                studio_features.report_modal(st.session_state.problem_statement)
            else:
                st.warning("⚠️ Please start tutoring first!")
        if st.button("📑 Quiz", use_container_width=True):
            if studio_features.studio_feature_available(st.session_state):
                studio_features.quiz_modal(st.session_state.problem_statement)
            else:
                st.warning("⚠️ Please start tutoring first!")
        if st.button("🎯 Slide deck", use_container_width=True):
            if studio_features.studio_feature_available(st.session_state):
                studio_features.slidedeck_modal(st.session_state.problem_statement)
            else:
                st.warning("⚠️ Please start tutoring first!")

    st.markdown("---")

    # Studio output area
    st.markdown("### Output")

    if st.session_state.setup_complete:
        # Show current problem
        with st.expander("📋 Current Problem", expanded=False):
            st.markdown(st.session_state.problem_statement)

        st.info("✨ Studio features coming soon!\n\nFocus on the chat to work through your problem with Aristotle.")
    else:
        st.info("✨ Studio output will be saved here.\n\nAfter adding sources, click to add Audio Overview, study guide, mind map and more!")

    if st.button("📝 Add note", use_container_width=True):
        st.success("Note added!")
