import streamlit as st
import time
from PIL import Image
import io
import base64
from tutoring_engine import TutoringEngine
from utils import process_uploaded_file, encode_image_to_base64
from config import APP_TITLE, APP_DESCRIPTION, MODELS

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
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
    if "show_metrics" not in st.session_state:
        st.session_state.show_metrics = False


def display_header():
    """Display application header."""
    st.markdown(f'<div class="main-header">{APP_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(APP_DESCRIPTION)
    st.divider()


def display_sidebar():
    """Display sidebar with information and controls."""
    with st.sidebar:
        st.header("📊 System Information")

        # Model information
        st.subheader("Active Models")
        st.caption(f"**Solution Generator:** {MODELS['solution_generator']}")
        st.caption(f"**Tutor:** {MODELS['tutor']}")
        st.caption(f"**Vision:** {MODELS['vision']}")

        st.divider()

        # Architecture explanation
        st.subheader("🏗️ Architecture")
        st.markdown(
            """
        **Three-Stage Pipeline:**
        1. **Input Processing**: Extract problem from uploads
        2. **Solution Generation**: Create reference (hidden from tutor)
        3. **Socratic Tutoring**: Guide student with questions
        """
        )

        st.divider()

        # Performance metrics
        if st.session_state.solution_generated:
            st.subheader("📈 Performance Metrics")
            metrics = st.session_state.engine.get_metrics()

            st.metric(
                "Solution Gen Time",
                f"{metrics['solution_generation_time']:.2f}s",
                help="Time to generate reference solution",
            )
            st.metric(
                "Total Cost",
                f"${metrics['total_cost']:.4f}",
                help="Estimated API cost for this session",
            )
            st.metric(
                "Conversation Length", metrics["conversation_length"], help="Messages"
            )

        st.divider()

        # Reset button
        if st.button("🔄 Start New Problem", use_container_width=True):
            st.session_state.engine.reset()
            st.session_state.problem_loaded = False
            st.session_state.solution_generated = False
            st.session_state.messages = []
            st.rerun()

        # Toggle metrics
        st.session_state.show_metrics = st.checkbox("Show Detailed Metrics", value=False)


def handle_file_upload():
    """Handle file upload and problem extraction."""
    st.subheader("📤 Upload Your Problem")

    upload_method = st.radio(
        "Choose upload method:",
        ["Upload File", "Paste Text", "Paste Screenshot"],
        horizontal=True,
    )

    problem_text = None
    image_data = None
    processing_method = None

    if upload_method == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload your homework problem",
            type=["txt", "pdf", "png", "jpg", "jpeg"],
            help="Supported formats: Text files, PDFs, and images",
        )

        if uploaded_file:
            file_extension = uploaded_file.name.split(".")[-1].lower()

            if file_extension == "txt":
                file_type = "text"
            elif file_extension == "pdf":
                file_type = "pdf"
            else:
                file_type = "image"

            with st.spinner("Processing file..."):
                problem_text, image_data, processing_method = process_uploaded_file(
                    uploaded_file, file_type
                )

    elif upload_method == "Paste Text":
        problem_text = st.text_area(
            "Paste your problem here:",
            height=200,
            placeholder="Enter the problem statement...",
        )
        if problem_text:
            processing_method = "text_input"

    elif upload_method == "Paste Screenshot":
        st.info(
            "📋 Take a screenshot and paste it here using Ctrl+V (Cmd+V on Mac) in the text area below"
        )

        # JavaScript for clipboard image paste
        paste_image = st.text_area(
            "Paste screenshot here (Ctrl+V / Cmd+V):",
            height=100,
            key="paste_area",
            help="After pasting, the image will appear below",
        )

        # Alternative: Manual image upload for screenshots
        screenshot_file = st.file_uploader(
            "Or upload screenshot manually:",
            type=["png", "jpg", "jpeg"],
            key="screenshot_upload",
        )

        if screenshot_file:
            image = Image.open(screenshot_file)
            st.image(image, caption="Uploaded Screenshot", use_column_width=True)
            image_data = encode_image_to_base64(image)
            processing_method = "screenshot_upload"

    # Process button
    if st.button("🚀 Load Problem", type="primary", use_container_width=True):
        if image_data:
            # Use vision model to extract problem from image
            with st.spinner("Extracting problem from image..."):
                start_time = time.time()
                problem_text = st.session_state.engine.process_problem_image(image_data)
                extraction_time = time.time() - start_time

            st.success(
                f"✅ Problem extracted in {extraction_time:.2f}s using vision model"
            )
            st.markdown("**Extracted Problem:**")
            st.info(problem_text)

        elif problem_text:
            st.session_state.engine.problem_statement = problem_text
            st.success("✅ Problem loaded successfully")

        else:
            st.error("Please provide a problem first!")
            return

        # Generate reference solution
        if problem_text:
            with st.spinner(
                "Generating reference solution (this may take a moment for complex problems)..."
            ):
                solution, gen_time = st.session_state.engine.generate_reference_solution(
                    problem_text
                )

            st.success(
                f"✅ Reference solution generated in {gen_time:.2f}s and stored securely (hidden from tutor)"
            )

            if st.session_state.show_metrics:
                with st.expander("🔍 View Reference Solution (Admin Only)"):
                    st.warning(
                        "⚠️ This is hidden from the tutor to prevent solution leakage"
                    )
                    st.markdown(solution)

            st.session_state.problem_loaded = True
            st.session_state.solution_generated = True

            # Add initial tutor message
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Hello! I see you have a problem to work on. Before we begin, can you tell me what you understand about this problem? What is it asking you to find or solve?",
                }
            ]

            st.rerun()


def display_chat_interface():
    """Display chat interface for tutoring."""
    st.subheader("💬 Tutoring Session")

    # Display problem context
    with st.expander("📝 Problem Statement", expanded=False):
        st.markdown(st.session_state.engine.problem_statement)

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]

            if role == "user":
                st.markdown(
                    f'<div class="chat-message user-message"><strong>You:</strong><br>{content}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-message assistant-message"><strong>Aristotle:</strong><br>{content}</div>',
                    unsafe_allow_html=True,
                )

    # Chat input
    st.divider()
    user_input = st.text_area(
        "Your response:",
        height=100,
        placeholder="Share your thoughts, work, or ask questions...",
        key="chat_input",
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("📨 Send", type="primary", use_container_width=True)

    if send_button and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get tutor response with streaming
        with st.spinner("Aristotle is thinking..."):
            response_placeholder = st.empty()
            full_response = ""

            try:
                # Stream the response
                for chunk in st.session_state.engine.chat(user_input, stream=True):
                    full_response += chunk
                    response_placeholder.markdown(
                        f'<div class="chat-message assistant-message"><strong>Aristotle:</strong><br>{full_response}▌</div>',
                        unsafe_allow_html=True,
                    )

                # Final response without cursor
                response_placeholder.markdown(
                    f'<div class="chat-message assistant-message"><strong>Aristotle:</strong><br>{full_response}</div>',
                    unsafe_allow_html=True,
                )

            except Exception as e:
                st.error(f"Error: {str(e)}")
                full_response = "I apologize, but I encountered an error. Could you please try again?"

        # Add assistant message
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

        # Clear input and rerun
        st.rerun()


def main():
    """Main application logic."""
    init_session_state()
    display_header()
    display_sidebar()

    if not st.session_state.problem_loaded:
        # Show upload interface
        handle_file_upload()

        # Show example problems
        st.divider()
        st.subheader("💡 Try an Example Problem")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📐 Math Problem", use_container_width=True):
                example_problem = """Solve for x:
2x + 5 = 3x - 7

Show all your work and explain each step."""
                st.session_state.engine.problem_statement = example_problem
                solution, gen_time = st.session_state.engine.generate_reference_solution(
                    example_problem
                )
                st.session_state.problem_loaded = True
                st.session_state.solution_generated = True
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "Hello! I see you have an algebra problem. Before we solve it, can you tell me what you think the first step should be?",
                    }
                ]
                st.rerun()

        with col2:
            if st.button("🧪 Science Problem", use_container_width=True):
                example_problem = """A ball is thrown upward with an initial velocity of 20 m/s.
How high will it go before falling back down?
(Assume g = 10 m/s² and ignore air resistance)"""
                st.session_state.engine.problem_statement = example_problem
                solution, gen_time = st.session_state.engine.generate_reference_solution(
                    example_problem
                )
                st.session_state.problem_loaded = True
                st.session_state.solution_generated = True
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "Hello! I see you have a physics problem about projectile motion. What do you know about how objects move when thrown upward?",
                    }
                ]
                st.rerun()

    else:
        # Show chat interface
        display_chat_interface()


if __name__ == "__main__":
    main()
