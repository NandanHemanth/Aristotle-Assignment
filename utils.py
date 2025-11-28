import base64
import io
from typing import Tuple, Optional
from PIL import Image
import PyPDF2
from docx import Document


def encode_image_to_base64(image: Image.Image) -> str:
    """
    Encode PIL Image to base64 data URI.

    Args:
        image: PIL Image object

    Returns:
        Base64 encoded data URI
    """
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from PDF file.

    Args:
        pdf_file: File-like object (from Streamlit file_uploader)

    Returns:
        Extracted text
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"


def extract_text_from_docx(docx_file) -> str:
    """
    Extract text from DOCX file.

    Args:
        docx_file: File-like object (from Streamlit file_uploader)

    Returns:
        Extracted text
    """
    try:
        doc = Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting DOCX text: {str(e)}"


def process_uploaded_file(
    uploaded_file, file_type: str
) -> Tuple[str, Optional[str], str]:
    """
    Process uploaded file and extract problem content.

    Args:
        uploaded_file: Streamlit uploaded file object
        file_type: Type of file ("text", "pdf", "docx", "image")

    Returns:
        Tuple of (problem_text, image_data, processing_method)
    """
    if file_type == "text":
        problem_text = uploaded_file.read().decode("utf-8")
        return problem_text, None, "text_extraction"

    elif file_type == "pdf":
        problem_text = extract_text_from_pdf(uploaded_file)
        return problem_text, None, "pdf_extraction"

    elif file_type == "docx":
        problem_text = extract_text_from_docx(uploaded_file)
        return problem_text, None, "docx_extraction"

    elif file_type == "image":
        # For images, we'll use vision model to extract the problem
        image = Image.open(uploaded_file)
        image_data = encode_image_to_base64(image)
        return "", image_data, "vision_extraction"

    return "Unknown file type", None, "error"


def truncate_conversation_history(
    messages: list, max_length: int = 20
) -> list:
    """
    Truncate conversation history to prevent context overflow.
    Keeps the first message (problem context) and recent messages.

    Args:
        messages: List of conversation messages
        max_length: Maximum number of messages to keep

    Returns:
        Truncated message list
    """
    if len(messages) <= max_length:
        return messages

    # Keep first message (contains problem context) and most recent messages
    return [messages[0]] + messages[-(max_length - 1) :]


def format_verification_result(verification: dict) -> str:
    """
    Format verification result for tutor to use internally.

    This is NEVER shown to the student - only used by the tutor
    to guide their questions without revealing the answer.

    Args:
        verification: Verification result from verifier

    Returns:
        Formatted string for tutor's internal use
    """
    if verification.get("is_correct"):
        return "VERIFICATION: Student's current work is correct. Encourage them to continue."

    error_location = verification.get("first_error_location", "unknown step")
    hint = verification.get("hint_suggestion", "Ask them to review their work.")

    return f"""VERIFICATION: Student has an error at: {error_location}
GUIDANCE: {hint}
REMEMBER: Do not reveal the answer. Ask guiding questions."""


def estimate_reading_time(text: str) -> float:
    """
    Estimate reading time for text in seconds.
    Average reading speed: ~250 words per minute.

    Args:
        text: Text to estimate

    Returns:
        Estimated reading time in seconds
    """
    words = len(text.split())
    return (words / 250) * 60
