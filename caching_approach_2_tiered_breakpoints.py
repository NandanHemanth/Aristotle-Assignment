"""
Approach 2: Tiered Cache Breakpoints

Uses multiple cache breakpoints to optimize caching for different content types:
- Tier 1: System prompt (always static, always cached)
- Tier 2: Problem context (static for session, separate cache)
- Tier 3: Mid-conversation history (periodically updated cache)
- Tier 4: Recent messages (no cache, always fresh)

Key Features:
1. Problem context gets its own cache breakpoint (frequently referenced)
2. Conversation history cached at strategic intervals (not just last assistant)
3. Recent messages stay uncached for flexibility
4. Optimal cache budget allocation
"""

from typing import List, Dict, Optional
from openrouter_client import OpenRouterClient
from config import ENABLE_CACHING


class TieredCacheBreakpointEngine:
    """
    Enhanced caching with multiple strategic cache breakpoints.

    Cache Tiers:
    1. System Prompt (Tier 1) - Always cached
    2. Problem Context (Tier 2) - Cached separately, frequently referenced
    3. Mid-Conversation (Tier 3) - Cached at strategic points (every N messages)
    4. Recent Messages (Tier 4) - Not cached, fresh
    """

    def __init__(
        self,
        mid_conversation_cache_interval: int = 10,
        recent_messages_window: int = 5
    ):
        self.mid_conversation_cache_interval = mid_conversation_cache_interval
        self.recent_messages_window = recent_messages_window
        self.last_mid_cache_index = 0

    def create_tiered_cached_messages(
        self,
        system_prompt: str,
        problem_context: str,
        conversation_history: List[Dict]
    ) -> List[Dict]:
        """
        Create messages with tiered cache breakpoints.

        Args:
            system_prompt: Static system instructions
            problem_context: The problem statement (static for session)
            conversation_history: Variable conversation messages

        Returns:
            Messages list with multiple cache breakpoints
        """
        if not ENABLE_CACHING:
            # No caching - simple message structure
            return [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"[PROBLEM]\n{problem_context}"},
            ] + conversation_history

        messages = []

        # TIER 1: System prompt (always cached)
        messages.append({
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ]
        })

        # TIER 2: Problem context (separate cache, frequently referenced)
        messages.append({
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": f"[PROBLEM]\n{problem_context}",
                    "cache_control": {"type": "ephemeral"}
                }
            ]
        })

        if len(conversation_history) == 0:
            return messages

        # Determine cache breakpoint in conversation history
        # TIER 3: Mid-conversation cache (every N messages)
        recent_window_start = max(0, len(conversation_history) - self.recent_messages_window)

        # Find mid-conversation cache point
        mid_cache_idx = self._find_mid_conversation_cache_point(
            conversation_history,
            recent_window_start
        )

        # Add messages before mid-cache point (no cache)
        for i in range(mid_cache_idx):
            messages.append(conversation_history[i])

        # Add message at mid-cache point WITH cache_control (TIER 3)
        if mid_cache_idx < recent_window_start:
            cached_msg = self._add_cache_control(conversation_history[mid_cache_idx])
            messages.append(cached_msg)

            # Add messages between mid-cache and recent window (no cache)
            for i in range(mid_cache_idx + 1, recent_window_start):
                messages.append(conversation_history[i])
        elif recent_window_start > 0:
            # Cache point is within recent window, cache last message before recent
            cached_msg = self._add_cache_control(
                conversation_history[recent_window_start - 1]
            )
            messages.append(cached_msg)

        # TIER 4: Recent messages (no cache, always fresh)
        for i in range(recent_window_start, len(conversation_history)):
            messages.append(conversation_history[i])

        return messages

    def _find_mid_conversation_cache_point(
        self,
        conversation_history: List[Dict],
        recent_window_start: int
    ) -> int:
        """
        Find optimal mid-conversation cache point.

        Strategy: Cache every N messages, preferably at assistant responses.
        """
        if recent_window_start < self.mid_conversation_cache_interval:
            # Not enough messages for mid-cache
            return 0

        # Find cache point: last assistant message before recent window
        # that's at least mid_conversation_cache_interval from start
        candidate_idx = recent_window_start - 1

        # Look backwards for last assistant message
        for i in range(recent_window_start - 1, -1, -1):
            if conversation_history[i].get("role") == "assistant":
                # Found assistant message, check if it's far enough from start
                if i >= self.mid_conversation_cache_interval - 1:
                    return i
                else:
                    # Too close to start, cache at interval boundary
                    return min(
                        self.mid_conversation_cache_interval - 1,
                        recent_window_start - 1
                    )

        # No assistant message found, cache at interval boundary
        return min(self.mid_conversation_cache_interval - 1, recent_window_start - 1)

    def _add_cache_control(self, message: Dict) -> Dict:
        """Add cache_control to a message."""
        msg_copy = message.copy()
        content = msg_copy.get("content", "")

        if isinstance(content, str):
            # Convert string content to array format with cache control
            msg_copy["content"] = [
                {
                    "type": "text",
                    "text": content,
                    "cache_control": {"type": "ephemeral"}
                }
            ]
        elif isinstance(content, list):
            # Already array format, add cache_control to last item
            msg_copy["content"] = content.copy()
            if len(msg_copy["content"]) > 0:
                msg_copy["content"][-1] = {
                    **msg_copy["content"][-1],
                    "cache_control": {"type": "ephemeral"}
                }

        return msg_copy


# Comparison utility
def compare_cache_strategies(conversation_history: List[Dict]):
    """
    Compare current single-cache vs. tiered cache strategies.
    """
    from openrouter_client import client

    system_prompt = "You are a Socratic tutor."
    problem_context = "Solve: 2x² + 5x - 3 = 0"

    print("=" * 70)
    print("CACHE STRATEGY COMPARISON")
    print("=" * 70)

    # Current strategy (single cache at last assistant)
    print("\n[CURRENT] Single cache at last assistant message:")
    current_messages = client.create_cached_messages(
        system_prompt + f"\n\n[PROBLEM]\n{problem_context}",
        conversation_history
    )

    cache_points_current = sum(
        1 for msg in current_messages
        if isinstance(msg.get("content"), list)
        and any(
            item.get("cache_control") is not None
            for item in msg["content"]
            if isinstance(item, dict)
        )
    )
    print(f"  Total messages: {len(current_messages)}")
    print(f"  Cache breakpoints: {cache_points_current}")

    # Tiered strategy
    print("\n[TIERED] Multiple cache breakpoints:")
    tiered_engine = TieredCacheBreakpointEngine(
        mid_conversation_cache_interval=10,
        recent_messages_window=5
    )
    tiered_messages = tiered_engine.create_tiered_cached_messages(
        system_prompt,
        problem_context,
        conversation_history
    )

    cache_points_tiered = sum(
        1 for msg in tiered_messages
        if isinstance(msg.get("content"), list)
        and any(
            item.get("cache_control") is not None
            for item in msg["content"]
            if isinstance(item, dict)
        )
    )
    print(f"  Total messages: {len(tiered_messages)}")
    print(f"  Cache breakpoints: {cache_points_tiered}")

    print("\n" + "=" * 70)
    print("CACHE BREAKPOINT LOCATIONS:")
    print("=" * 70)

    print("\n[TIERED] Cache breakpoints at:")
    for i, msg in enumerate(tiered_messages):
        content = msg.get("content")
        if isinstance(content, list) and any(
            item.get("cache_control") is not None
            for item in content
            if isinstance(item, dict)
        ):
            role = msg.get("role")
            print(f"  - Position {i+1}: {role}")

    return {
        "current": {"messages": len(current_messages), "cache_points": cache_points_current},
        "tiered": {"messages": len(tiered_messages), "cache_points": cache_points_tiered}
    }


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("APPROACH 2: TIERED CACHE BREAKPOINTS")
    print("=" * 70)

    # Simulate conversation
    simulated_conversation = [
        {"role": "user", "content": "I'm not sure where to start"},
        {"role": "assistant", "content": "What methods do you know?"},
        {"role": "user", "content": "Quadratic formula"},
        {"role": "assistant", "content": "Great! Write it out."},
        {"role": "user", "content": "x = (-b ± √(b² - 4ac)) / 2a"},
        {"role": "assistant", "content": "Perfect! Now identify a, b, c."},
        {"role": "user", "content": "a=2, b=5, c=-3"},
        {"role": "assistant", "content": "Excellent! Substitute them."},
        {"role": "user", "content": "x = (-5 ± √(25 + 24)) / 4"},
        {"role": "assistant", "content": "Good! Simplify the discriminant."},
        {"role": "user", "content": "√49 = 7"},
        {"role": "assistant", "content": "Perfect! What are the solutions?"},
        {"role": "user", "content": "x = 1/2 or x = -3"},
        {"role": "assistant", "content": "Correct! Well done."},
    ]

    comparison = compare_cache_strategies(simulated_conversation)

    print("\n" + "=" * 70)
    print("BENEFITS OF TIERED CACHING:")
    print("=" * 70)
    print("1. Problem context cached separately (frequently referenced)")
    print("2. Mid-conversation cached at strategic intervals")
    print("3. Recent messages stay fresh (no cache invalidation)")
    print("4. Better cache budget utilization")
    print("=" * 70)
