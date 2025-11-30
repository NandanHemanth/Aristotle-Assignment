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
        Create messages with caching enabled for both system prompt AND conversation history.
        Based on BLUEPRINT.md: caching reduces latency by up to 85% for long prompts.

        Anthropic's prompt caching supports up to 4 cache breakpoints:
        1. System prompt (always cached - static)
        2. Conversation history (cached incrementally for faster follow-ups)

        This enables faster responses for follow-up questions since the previous
        conversation context is already cached and doesn't need to be reprocessed.

        Cache reads are charged at just 10% of input pricing with Claude models.

        Args:
            system_prompt: Static system instructions
            conversation_history: Variable conversation messages

        Returns:
            Messages list with caching enabled
        """
        if not ENABLE_CACHING:
            return [{"role": "system", "content": system_prompt}] + conversation_history

        # Cache the system prompt (first cache breakpoint)
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

        # Add conversation history with caching enabled
        # Strategy: Cache up to the last ASSISTANT response
        # This ensures follow-up questions benefit from cached previous context
        if len(conversation_history) > 0:
            # Find the last assistant message index
            last_assistant_idx = -1
            for i in range(len(conversation_history) - 1, -1, -1):
                if conversation_history[i].get("role") == "assistant":
                    last_assistant_idx = i
                    break

            # Cache up to last assistant response, or last user message if no assistant yet
            cache_up_to_idx = last_assistant_idx if last_assistant_idx >= 0 else len(conversation_history) - 1

            # Add messages before cache breakpoint (no caching)
            for i in range(cache_up_to_idx):
                messages.append(conversation_history[i])

            # Add the message at cache breakpoint WITH cache_control
            if cache_up_to_idx >= 0:
                msg_to_cache = conversation_history[cache_up_to_idx]

                # Convert to cacheable format
                if isinstance(msg_to_cache.get("content"), str):
                    cached_msg = {
                        "role": msg_to_cache["role"],
                        "content": [
                            {
                                "type": "text",
                                "text": msg_to_cache["content"],
                                "cache_control": {"type": "ephemeral"},
                            }
                        ],
                    }
                else:
                    # Already in array format, add cache_control to last item
                    cached_msg = msg_to_cache.copy()
                    if isinstance(cached_msg["content"], list) and len(cached_msg["content"]) > 0:
                        cached_msg["content"] = cached_msg["content"].copy()
                        cached_msg["content"][-1] = {
                            **cached_msg["content"][-1],
                            "cache_control": {"type": "ephemeral"},
                        }

                messages.append(cached_msg)

            # Add remaining messages after cache breakpoint (no caching on new messages)
            for i in range(cache_up_to_idx + 1, len(conversation_history)):
                messages.append(conversation_history[i])

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
