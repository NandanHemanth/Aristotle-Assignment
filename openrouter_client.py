import json
import time
from typing import List, Dict, Optional, Generator
import requests
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, ENABLE_STREAMING, ENABLE_CACHING


class OpenRouterClient:
    """
    Client for interacting with OpenRouter API.
    Implements streaming, caching, and multi-model support based on BLUEPRINT.md research.
    """

    def __init__(self, api_key: str = OPENROUTER_API_KEY):
        self.api_key = api_key
        self.base_url = OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aristotle-tutor.app",  # Optional, for rankings
            "X-Title": "Aristotle AI Tutor",  # Optional, shows in rankings
        }

    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, any]],
        stream: bool = ENABLE_STREAMING,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict | Generator:
        """
        Make a chat completion request to OpenRouter.

        Args:
            model: Model identifier (can include :nitro or :floor suffixes)
            messages: List of message dictionaries
            stream: Whether to stream the response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response dictionary or generator for streaming
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        # Enable usage tracking
        payload["usage"] = {"include": True}

        if stream:
            return self._stream_completion(payload)
        else:
            return self._sync_completion(payload)

    def _sync_completion(self, payload: Dict) -> Dict:
        """Synchronous completion request."""
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=120,
        )

        if response.status_code != 200:
            raise Exception(
                f"OpenRouter API error: {response.status_code} - {response.text}"
            )

        return response.json()

    def _stream_completion(self, payload: Dict) -> Generator:
        """
        Streaming completion request.
        Yields chunks as they arrive for reduced perceived latency (10-100x improvement).
        """
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload,
            stream=True,
            timeout=120,
        )

        if response.status_code != 200:
            raise Exception(
                f"OpenRouter API error: {response.status_code} - {response.text}"
            )

        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        yield chunk
                    except json.JSONDecodeError:
                        continue

    def chat_completion_with_vision(
        self,
        model: str,
        text_prompt: str,
        image_data: str,  # Base64 encoded image or URL
        stream: bool = False,
    ) -> Dict | Generator:
        """
        Make a chat completion request with vision capabilities.

        Args:
            model: Vision-capable model
            text_prompt: Text prompt
            image_data: Base64 encoded image with data URI or image URL

        Returns:
            Response dictionary or generator
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data},
                    },
                ],
            }
        ]

        return self.chat_completion(model, messages, stream=stream)

    def create_cached_messages(
        self, system_prompt: str, conversation_history: List[Dict]
    ) -> List[Dict]:
        """
        Create messages with caching enabled for the system prompt.
        Based on BLUEPRINT.md: caching reduces latency by up to 85% for long prompts.

        Structure: Static content (system prompt) first, then variable content (conversation).
        Cache reads are charged at just 10% of input pricing with Claude models.

        Args:
            system_prompt: Static system instructions
            conversation_history: Variable conversation messages

        Returns:
            Messages list with caching enabled
        """
        if not ENABLE_CACHING:
            return [{"role": "system", "content": system_prompt}] + conversation_history

        # For Anthropic models, use cache_control
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
            }
        ]

        messages.extend(conversation_history)
        return messages

    def estimate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
    ) -> float:
        """
        Estimate cost for a request.
        Prices from BLUEPRINT.md (per million tokens).
        """
        pricing = {
            "deepseek/deepseek-r1": (0.20, 4.50),
            "anthropic/claude-haiku-4.5": (1.0, 5.0),
            "openai/gpt-4o-mini": (0.15, 0.60),
            "gemini/gemini-2.0-flash": (0.10, 0.40),
        }

        # Remove :nitro or :floor suffix for pricing lookup
        base_model = model.split(":")[0]

        if base_model not in pricing:
            return 0.0

        input_price, output_price = pricing[base_model]

        # Cached tokens are 10% of input price for Claude
        cache_discount = 0.1 if "claude" in base_model else 0

        input_cost = (input_tokens - cached_tokens) * input_price / 1_000_000
        cached_cost = cached_tokens * input_price * cache_discount / 1_000_000
        output_cost = output_tokens * output_price / 1_000_000

        return input_cost + cached_cost + output_cost


# Singleton instance
client = OpenRouterClient()
