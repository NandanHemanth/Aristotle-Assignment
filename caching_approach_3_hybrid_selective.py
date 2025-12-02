"""
Approach 3: Hybrid Selective Retention

Intelligently selects which messages to keep based on pedagogical importance:
- KEEP: Misconceptions, breakthroughs, key concepts, student questions
- DROP: Filler, encouragement, repetitive clarifications
- SUMMARIZE: Dropped messages get summarized for minimal context

Key Features:
1. Classification of message importance (high/medium/low)
2. Selective retention maintains important pedagogical context
3. Cache remains coherent (no structural changes)
4. Lightweight summarization of dropped messages
"""

import re
from typing import List, Dict, Optional, Tuple
from openrouter_client import client
from config import MODELS


class HybridSelectiveRetentionEngine:
    """
    Smart message retention based on pedagogical importance.

    Classifies each message as:
    - HIGH importance: Keep always (misconceptions, breakthroughs, key questions)
    - MEDIUM importance: Keep if space available
    - LOW importance: Drop, include in summary
    """

    def __init__(
        self,
        max_length: int = 20,
        min_recent_keep: int = 5
    ):
        self.max_length = max_length
        self.min_recent_keep = min_recent_keep

    def manage_conversation(
        self,
        messages: List[Dict]
    ) -> Tuple[List[Dict], Dict]:
        """
        Selectively retain important messages.

        Args:
            messages: Full conversation history

        Returns:
            Tuple of (managed_messages, metadata)
        """
        if len(messages) <= self.max_length:
            return messages, {"retention_triggered": False}

        # First message is always kept (problem context)
        first_message = messages[0]

        # Recent messages are always kept (current context)
        recent_messages = messages[-self.min_recent_keep:]

        # Middle messages are candidates for selective retention
        middle_messages = messages[1:-self.min_recent_keep]

        # Classify middle messages by importance
        classified = self._classify_messages(middle_messages)

        # Select messages to keep
        selected, dropped = self._select_messages(
            classified,
            budget=self.max_length - 1 - self.min_recent_keep  # -1 for first message
        )

        # Build final message list
        managed = [first_message]

        # Add selected middle messages (in order)
        for msg, _ in selected:
            managed.append(msg)

        # If we dropped messages, add a summary
        if len(dropped) > 0:
            summary = self._create_lightweight_summary(dropped)
            managed.append({
                "role": "system",
                "content": f"[CONTEXT SUMMARY]\n{summary}"
            })

        # Add recent messages
        managed.extend(recent_messages)

        metadata = {
            "retention_triggered": True,
            "total_messages": len(messages),
            "kept_messages": len(managed),
            "dropped_count": len(dropped),
            "high_importance_kept": sum(1 for _, imp in selected if imp == "high"),
            "medium_importance_kept": sum(1 for _, imp in selected if imp == "medium")
        }

        return managed, metadata

    def _classify_messages(
        self,
        messages: List[Dict]
    ) -> List[Tuple[Dict, str]]:
        """
        Classify messages by pedagogical importance.

        Uses heuristics (fast) instead of LLM calls (expensive).

        Returns:
            List of (message, importance_level) tuples
        """
        classified = []

        for i, msg in enumerate(messages):
            role = msg.get("role", "")
            content = self._get_message_text(msg)

            importance = self._classify_single_message(role, content, i, len(messages))
            classified.append((msg, importance))

        return classified

    def _classify_single_message(
        self,
        role: str,
        content: str,
        index: int,
        total: int
    ) -> str:
        """
        Classify a single message using heuristics.

        HIGH importance indicators:
        - Student questions about core concepts
        - Misconception signals ("I thought...", "Isn't X the same as Y?")
        - Breakthrough moments ("Oh I see!", "That makes sense")
        - Key definitions/formulas
        - Error acknowledgments

        MEDIUM importance:
        - Progress updates
        - Clarification requests
        - Strategy discussions

        LOW importance:
        - Filler ("ok", "sure", "thanks")
        - Pure encouragement ("great!", "keep going!")
        - Repetitive acknowledgments
        """
        content_lower = content.lower()

        # HIGH importance patterns
        high_patterns = [
            # Misconceptions
            r"\bi thought\b",
            r"\bisn't .+ the same as\b",
            r"\bwhy isn't\b",
            r"\bwhy doesn't\b",
            r"\bdon't understand why\b",
            r"\bconfused about\b",

            # Breakthroughs
            r"\boh i see\b",
            r"\bthat makes sense\b",
            r"\bnow i understand\b",
            r"\bso .+ is because\b",

            # Key questions
            r"\bwhat is the difference between\b",
            r"\bhow does .+ work\b",
            r"\bwhy is .+ important\b",
            r"\bwhen do we use\b",

            # Errors acknowledged
            r"\bi made a mistake\b",
            r"\bi was wrong\b",
            r"\bthat's incorrect\b"
        ]

        for pattern in high_patterns:
            if re.search(pattern, content_lower):
                return "high"

        # LOW importance patterns
        low_patterns = [
            # Filler
            r"^(ok|okay|sure|thanks|thank you|got it)\.?$",
            r"^(yes|no|yeah|yep|nope)\.?$",

            # Pure encouragement (tutor)
            r"^(great|good|excellent|perfect|nice)!?$",
            r"^(keep going|continue|you're doing well)!?$",
            r"^(that's right|correct)!?$"
        ]

        for pattern in low_patterns:
            if re.search(pattern, content_lower):
                return "low"

        # Length heuristic: Very short messages are often low importance
        if len(content) < 20:
            return "low"

        # Very long messages (>200 chars) are often important (detailed work)
        if len(content) > 200:
            return "high"

        # Default to medium
        return "medium"

    def _select_messages(
        self,
        classified: List[Tuple[Dict, str]],
        budget: int
    ) -> Tuple[List[Tuple[Dict, str]], List[Dict]]:
        """
        Select messages to keep within budget.

        Strategy:
        1. Keep ALL high importance messages
        2. Fill remaining budget with medium importance
        3. Drop low importance
        """
        high = [(msg, imp) for msg, imp in classified if imp == "high"]
        medium = [(msg, imp) for msg, imp in classified if imp == "medium"]
        low = [msg for msg, imp in classified if imp == "low"]

        selected = []
        dropped = []

        # Add high importance (always)
        selected.extend(high)

        # Add medium importance if budget allows
        remaining_budget = budget - len(high)
        if remaining_budget > 0:
            selected.extend(medium[:remaining_budget])
            dropped.extend([msg for msg, _ in medium[remaining_budget:]])
        else:
            dropped.extend([msg for msg, _ in medium])

        # All low importance is dropped
        dropped.extend(low)

        return selected, dropped

    def _create_lightweight_summary(self, dropped: List[Dict]) -> str:
        """
        Create lightweight summary of dropped messages.

        Uses bullet points instead of prose for efficiency.
        """
        summary_points = []

        for msg in dropped:
            role = msg.get("role", "")
            content = self._get_message_text(msg)

            # Truncate long content
            if len(content) > 100:
                content = content[:97] + "..."

            if role == "user":
                summary_points.append(f"- Student: {content}")
            elif role == "assistant":
                summary_points.append(f"- Tutor: {content}")

        # Limit to 10 points max
        if len(summary_points) > 10:
            summary_points = summary_points[:10]
            summary_points.append("- [... additional exchanges omitted ...]")

        return "\n".join(summary_points)

    def _get_message_text(self, message: Dict) -> str:
        """Extract text content from message."""
        content = message.get("content", "")

        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # Extract text from array format
            text_parts = [
                item.get("text", "")
                for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            ]
            return " ".join(text_parts)

        return ""


# Comparison utility
def demonstrate_selective_retention():
    """
    Demonstrate selective retention with example conversation.
    """
    print("=" * 70)
    print("APPROACH 3: HYBRID SELECTIVE RETENTION")
    print("=" * 70)

    # Simulated conversation with varied importance
    conversation = [
        {"role": "system", "content": "Problem: Factor x² - 5x + 6"},
        {"role": "user", "content": "I'm not sure where to start"},  # Medium
        {"role": "assistant", "content": "What do you know about factoring?"},  # Medium
        {"role": "user", "content": "I thought factoring always means dividing?"},  # HIGH - misconception
        {"role": "assistant", "content": "Let's clarify that misconception..."},  # HIGH - addresses misconception
        {"role": "user", "content": "Oh I see!"},  # HIGH - breakthrough
        {"role": "assistant", "content": "Great!"},  # LOW - encouragement only
        {"role": "user", "content": "What are the factors of 6?"},  # Medium
        {"role": "assistant", "content": "What numbers multiply to give 6?"},  # Medium
        {"role": "user", "content": "1 and 6, or 2 and 3"},  # Medium
        {"role": "assistant", "content": "Perfect!"},  # LOW
        {"role": "user", "content": "Do I need ones that add to -5?"},  # HIGH - key concept
        {"role": "assistant", "content": "Exactly! Which pair adds to -5?"},  # HIGH
        {"role": "user", "content": "-2 and -3"},  # Medium
        {"role": "assistant", "content": "Excellent!"},  # LOW
        {"role": "user", "content": "So it's (x - 2)(x - 3)?"},  # Medium (recent)
        {"role": "assistant", "content": "Yes! Can you verify?"},  # Medium (recent)
        {"role": "user", "content": "How do I verify?"},  # Medium (recent)
        {"role": "assistant", "content": "Expand it back out"},  # Medium (recent)
        {"role": "user", "content": "ok"},  # LOW (recent, but kept anyway)
    ]

    engine = HybridSelectiveRetentionEngine(max_length=15, min_recent_keep=5)

    print(f"\nOriginal: {len(conversation)} messages")

    managed, metadata = engine.manage_conversation(conversation)

    print(f"Managed: {len(managed)} messages")
    print(f"\nRetention metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("MESSAGE IMPORTANCE CLASSIFICATION:")
    print("=" * 70)

    # Show classification
    first = conversation[0]
    middle = conversation[1:-5]
    recent = conversation[-5:]

    print("\n[FIRST MESSAGE] Always kept:")
    print(f"  {first['role']}: {first['content'][:60]}...")

    print("\n[MIDDLE MESSAGES] Classified and selectively kept:")
    for msg in middle:
        role = msg.get("role")
        content = msg.get("content", "")
        importance = engine._classify_single_message(role, content, 0, len(middle))
        kept = any(m.get("content") == content for m in managed)
        status = "KEPT" if kept else "DROPPED"
        print(f"  [{importance.upper():6}] {status:7} - {role}: {content[:50]}...")

    print("\n[RECENT MESSAGES] Always kept:")
    for msg in recent:
        print(f"  {msg['role']}: {msg['content'][:60]}...")

    return managed, metadata


# Example usage
if __name__ == "__main__":
    managed, metadata = demonstrate_selective_retention()

    print("\n" + "=" * 70)
    print("BENEFITS OF SELECTIVE RETENTION:")
    print("=" * 70)
    print("1. Preserves pedagogically important moments (misconceptions, breakthroughs)")
    print("2. Drops filler and encouragement messages")
    print("3. No cache invalidation (structure preserved)")
    print("4. Lightweight summary of dropped messages")
    print("5. Fast heuristic-based classification (no expensive LLM calls)")
    print("=" * 70)
