"""
Content extraction utilities for YouTube videos and web URLs.
Optimized for educational content with focus on latency and accuracy.
"""

import re
from typing import Tuple, Optional, Dict
import requests
from bs4 import BeautifulSoup
import time

# Try to import youtube_transcript_api with error handling
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
    YOUTUBE_API_AVAILABLE = True
except Exception as e:
    YOUTUBE_API_AVAILABLE = False
    print(f"Warning: YouTube Transcript API not available: {e}")


class YouTubeExtractor:
    """
    Extract content from YouTube videos for tutoring.
    Optimized for educational videos with transcripts.
    """

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various URL formats.

        Args:
            url: YouTube URL (youtube.com, youtu.be, etc.)

        Returns:
            Video ID or None
        """
        patterns = [
            r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)",
            r"youtube\.com\/embed\/([^&\n?#]+)",
            r"youtube\.com\/v\/([^&\n?#]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def get_transcript(video_id: str, languages: list = ["en"]) -> Tuple[str, Dict]:
        """
        Get transcript from YouTube video.

        Args:
            video_id: YouTube video ID
            languages: Preferred languages for transcript

        Returns:
            Tuple of (transcript_text, metadata)
        """
        start_time = time.time()

        if not YOUTUBE_API_AVAILABLE:
            return "Error: YouTube Transcript API not available. Please install: pip install youtube-transcript-api", {
                "error": True,
                "extraction_time": time.time() - start_time,
            }

        try:
            # Get transcript with better error handling
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, languages=languages
            )

            if not transcript_list:
                return "Error: No transcript found for this video", {
                    "error": True,
                    "extraction_time": time.time() - start_time,
                }

            # Combine transcript segments
            full_text = " ".join([segment["text"] for segment in transcript_list])

            # Calculate metadata
            duration = (
                transcript_list[-1]["start"] + transcript_list[-1]["duration"]
                if transcript_list
                else 0
            )
            extraction_time = time.time() - start_time

            metadata = {
                "video_id": video_id,
                "duration_seconds": duration,
                "segments_count": len(transcript_list),
                "extraction_time": extraction_time,
                "word_count": len(full_text.split()),
                "has_timestamps": True,
                "title": f"YouTube Video {video_id}",
            }

            return full_text, metadata

        except TranscriptsDisabled:
            return "Error: Transcripts are disabled for this video. The video owner has disabled captions.", {
                "error": True,
                "extraction_time": time.time() - start_time,
            }
        except NoTranscriptFound:
            return "Error: No transcript found. This video may not have captions available.", {
                "error": True,
                "extraction_time": time.time() - start_time,
            }
        except Exception as e:
            error_msg = str(e)
            if "no element found" in error_msg.lower():
                return "Error: Unable to parse YouTube response. The video may be unavailable or private.", {
                    "error": True,
                    "extraction_time": time.time() - start_time,
                }
            return f"Error: {error_msg}", {
                "error": True,
                "extraction_time": time.time() - start_time,
            }

    @staticmethod
    def extract_from_url(url: str) -> Tuple[str, Dict]:
        """
        Extract content from YouTube URL.

        Args:
            url: YouTube video URL

        Returns:
            Tuple of (content, metadata)
        """
        video_id = YouTubeExtractor.extract_video_id(url)

        if not video_id:
            return "Error: Invalid YouTube URL", {"error": True}

        return YouTubeExtractor.get_transcript(video_id)

    @staticmethod
    def format_for_tutoring(transcript: str, metadata: Dict) -> str:
        """
        Format YouTube transcript for tutoring context.

        Args:
            transcript: Raw transcript text
            metadata: Video metadata

        Returns:
            Formatted content for tutoring
        """
        if metadata.get("error"):
            return transcript

        formatted = f"""YouTube Video Content:
Duration: {metadata.get('duration_seconds', 0) / 60:.1f} minutes
Word Count: {metadata.get('word_count', 0)} words

Transcript:
{transcript[:5000]}{'...' if len(transcript) > 5000 else ''}

Note: This is educational content from a video. The student may have questions about concepts explained in this video.
"""
        return formatted


class URLExtractor:
    """
    Extract content from web URLs using requests + BeautifulSoup.
    Optimized for educational websites, documentation, and articles.
    """

    @staticmethod
    def extract_with_requests(url: str) -> Tuple[str, Dict]:
        """
        Extract content using requests + BeautifulSoup with multiple parsers.

        Args:
            url: Web URL to extract

        Returns:
            Tuple of (content, metadata)
        """
        start_time = time.time()

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
            
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()

            # Try multiple parsers in order of preference
            parsers = ['lxml', 'html.parser', 'html5lib']
            soup = None
            
            for parser in parsers:
                try:
                    soup = BeautifulSoup(response.content, parser)
                    break
                except Exception:
                    continue
            
            if soup is None:
                soup = BeautifulSoup(response.content, "html.parser")

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
                element.decompose()

            # Try to find main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|main|article', re.I))
            
            if main_content:
                text = main_content.get_text(separator="\n", strip=True)
            else:
                text = soup.get_text(separator="\n", strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            content = "\n".join(lines)

            # Get title
            title = "Unknown"
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)

            metadata = {
                "url": url,
                "title": title,
                "extraction_time": time.time() - start_time,
                "word_count": len(content.split()),
                "success": True,
                "method": "requests+beautifulsoup",
            }

            return content, metadata

        except requests.exceptions.Timeout:
            return "Error: Request timed out. The website took too long to respond.", {
                "error": True,
                "extraction_time": time.time() - start_time,
            }
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to the website. Check your internet connection.", {
                "error": True,
                "extraction_time": time.time() - start_time,
            }
        except requests.exceptions.HTTPError as e:
            return f"Error: HTTP {e.response.status_code} - {e.response.reason}", {
                "error": True,
                "extraction_time": time.time() - start_time,
            }
        except Exception as e:
            return f"Error: {str(e)}", {
                "error": True,
                "extraction_time": time.time() - start_time,
            }

    @staticmethod
    def extract_from_url(url: str) -> Tuple[str, Dict]:
        """
        Extract content from URL using requests + BeautifulSoup.

        Args:
            url: Web URL

        Returns:
            Tuple of (content, metadata)
        """
        return URLExtractor.extract_with_requests(url)

    @staticmethod
    def format_for_tutoring(content: str, metadata: Dict) -> str:
        """
        Format web content for tutoring context.

        Args:
            content: Extracted content
            metadata: URL metadata

        Returns:
            Formatted content for tutoring
        """
        if metadata.get("error"):
            return content

        formatted = f"""Web Content: {metadata.get('title', 'Unknown')}
URL: {metadata.get('url', 'N/A')}
Word Count: {metadata.get('word_count', 0)} words

Content:
{content[:8000]}{'...' if len(content) > 8000 else ''}

Note: This is educational content from a website. The student may have questions about concepts from this article/page.
"""
        return formatted


def detect_content_type(input_text: str) -> str:
    """
    Detect content type from input string.

    Args:
        input_text: User input

    Returns:
        Content type: 'youtube', 'url', 'text'
    """
    # YouTube URL patterns
    youtube_patterns = [
        r"(?:youtube\.com|youtu\.be)",
    ]

    for pattern in youtube_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            return "youtube"

    # General URL pattern
    url_pattern = r"https?://[^\s]+"
    if re.search(url_pattern, input_text, re.IGNORECASE):
        return "url"

    return "text"


def extract_content(
    input_text: str, content_type: str = None
) -> Tuple[str, Dict, str]:
    """
    Unified content extraction function.

    Args:
        input_text: User input (URL, YouTube link, or text)
        content_type: Optional content type override

    Returns:
        Tuple of (extracted_content, metadata, processing_method)
    """
    # Auto-detect if not specified
    if content_type is None:
        content_type = detect_content_type(input_text)

    if content_type == "youtube":
        content, metadata = YouTubeExtractor.extract_from_url(input_text)
        formatted = YouTubeExtractor.format_for_tutoring(content, metadata)
        return formatted, metadata, "youtube_transcript"

    elif content_type == "url":
        content, metadata = URLExtractor.extract_from_url(input_text)
        formatted = URLExtractor.format_for_tutoring(content, metadata)
        return formatted, metadata, "web_crawl"

    else:
        # Plain text
        return input_text, {"type": "text", "word_count": len(input_text.split())}, "text_input"
