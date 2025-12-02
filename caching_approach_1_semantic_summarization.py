"""
Approach 1: Semantic Summarization for Context Management

Instead of dropping messages, this approach summarizes them into a condensed
pedagogical summary that preserves teaching context without breaking cache.

Key Features:
1. Summarizes messages 2-N into a "conversation summary" when limit reached
2. Keeps first message (problem) + summary + recent K messages
3. Updates summary incrementally to minimize API calls
4. Maintains cache coherence by preserving structure
"""

import json
from typing import List, Dict, Optional
from openrouter_client import client
from config import MODELS


class SemanticSummarizationEngine:
    """
    Enhanced conversation management with semantic summarization.

    When conversation exceeds max_length, instead of dropping messages,
    we summarize the middle messages into pedagogically valuable context.
    """

    def __init__(self, max_length: int = 20, summary_window_size: int = 10):
        self.max_length = max_length
        self.summary_window_size = summary_window_size  # Keep recent N messages
        self.conversation_summary: Optional[str] = None
        self.last_summarized_index: int = 0

    def manage_conversation(
        self,
        messages: List[Dict],
        force_summary: bool = False
    ) -> tuple[List[Dict], bool]:
        """
        Manage conversation history with semantic summarization.

        Args:
            messages: Full conversation history
            force_summary: Force summarization even if under limit

        Returns:
            Tuple of (managed_messages, summarization_occurred)
        """
        if len(messages) <= self.max_length and not force_summary:
            return messages, False

        # Need to summarize
        # Structure: [first_message] + [summary_message] + [recent_messages]

        first_message = messages[0]
        recent_messages = messages[-self.summary_window_size:]

        # Messages to summarize: everything between first and recent
        messages_to_summarize = messages[
            self.last_summarized_index + 1 : -self.summary_window_size
        ]

        if len(messages_to_summarize) == 0:
            # Nothing new to summarize
            if self.conversation_summary:
                summary_message = {
                    "role": "system",
                    "content": f"[CONVERSATION SUMMARY]\n{self.conversation_summary}"
                }
                return [first_message, summary_message] + recent_messages, False
            else:
                return messages, False

        # Generate or update summary
        new_summary = self._generate_summary(
            messages_to_summarize,
            previous_summary=self.conversation_summary
        )

        self.conversation_summary = new_summary
        self.last_summarized_index = len(messages) - self.summary_window_size - 1

        # Create managed message list
        summary_message = {
            "role": "system",
            "content": f"[CONVERSATION SUMMARY]\n{new_summary}"
        }

        managed_messages = [first_message, summary_message] + recent_messages

        return managed_messages, True

    def _generate_summary(
        self,
        messages: List[Dict],
        previous_summary: Optional[str] = None
    ) -> str:
        """
        Generate pedagogical summary of conversation segment.

        Focuses on:
        - Student misconceptions and how they were addressed
        - Teaching strategies used (successful and unsuccessful)
        - Key concepts explained
        - Student progress and understanding level
        """
        # Build summary prompt
        conversation_text = self._format_messages_for_summary(messages)

        if previous_summary:
            prompt = f"""You are summarizing a tutoring conversation for context management.

PREVIOUS SUMMARY:
{previous_summary}

NEW MESSAGES TO SUMMARIZE:
{conversation_text}

Generate an UPDATED summary that:
1. Preserves key pedagogical context (misconceptions, breakthroughs, teaching strategies)
2. Is concise (max 300 words)
3. Focuses on what's relevant for future tutoring

Format:
- Student Misconceptions: [list key misunderstandings and how they were addressed]
- Teaching Strategies Used: [what worked, what didn't]
- Progress: [current understanding level]
- Important Context: [anything else the tutor should remember]

Provide ONLY the summary, no preamble."""
        else:
            prompt = f"""You are summarizing a tutoring conversation for context management.

CONVERSATION TO SUMMARIZE:
{conversation_text}

Generate a summary that:
1. Preserves key pedagogical context (misconceptions, breakthroughs, teaching strategies)
2. Is concise (max 300 words)
3. Focuses on what's relevant for future tutoring

Format:
- Student Misconceptions: [list key misunderstandings and how they were addressed]
- Teaching Strategies Used: [what worked, what didn't]
- Progress: [current understanding level]
- Important Context: [anything else the tutor should remember]

Provide ONLY the summary, no preamble."""

        # Use fast, cheap model for summarization
        response = client.chat_completion(
            model=MODELS["verifier"],  # GPT-4o-mini - fast and cheap
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            temperature=0.3,  # Low temperature for consistent summaries
        )

        summary = response["choices"][0]["message"]["content"]
        return summary.strip()

    def _format_messages_for_summary(self, messages: List[Dict]) -> str:
        """Format messages into readable text for summarization."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Handle content that might be an array (vision messages)
            if isinstance(content, list):
                content = " ".join([
                    item.get("text", "") for item in content
                    if item.get("type") == "text"
                ])

            formatted.append(f"{role.upper()}: {content}")

        return "\n\n".join(formatted)

    def reset(self):
        """Reset summarization state."""
        self.conversation_summary = None
        self.last_summarized_index = 0


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("APPROACH 1: SEMANTIC SUMMARIZATION")
    print("=" * 70)

    # Simulate a long conversation
    simulated_conversation = [
        {"role": "system", "content": "Problem: Solve 2x² + 5x - 3 = 0"},
        {"role": "user", "content": "I'm not sure where to start"},
        {"role": "assistant", "content": "What methods do you know for quadratic equations?"},
        {"role": "user", "content": "Quadratic formula and factoring"},
        {"role": "assistant", "content": "Great! Which would you like to try first?"},
        {"role": "user", "content": "Let me try factoring"},
        {"role": "assistant", "content": "Good choice. What's the first step in factoring?"},
        {"role": "user", "content": "Find two numbers that multiply to -3 and add to 5?"},
        {"role": "assistant", "content": "Close! With 2x², we need to account for that coefficient. Let's think about this..."},
        {"role": "user", "content": "Oh, so it's more complex?"},
        {"role": "assistant", "content": "Yes. When a ≠ 1, factoring is trickier. Would you like to try the quadratic formula instead?"},
        {"role": "user", "content": "Sure, let's use the formula"},
        {"role": "assistant", "content": "Perfect. Can you write out the quadratic formula?"},
        {"role": "user", "content": "x = (-b ± √(b² - 4ac)) / 2a"},
        {"role": "assistant", "content": "Excellent! Now identify a, b, and c from our equation."},
        {"role": "user", "content": "a=2, b=5, c=-3"},
        {"role": "assistant", "content": "Perfect! Now substitute these values into the formula."},
        {"role": "user", "content": "x = (-5 ± √(25 - 4(2)(-3))) / 4"},
        {"role": "assistant", "content": "Great start! Now simplify the discriminant."},
        {"role": "user", "content": "√(25 + 24) = √49 = 7"},
        {"role": "assistant", "content": "Excellent! So what are the two solutions?"},
        {"role": "user", "content": "x = (-5 + 7)/4 = 1/2 or x = (-5 - 7)/4 = -3"},
        {"role": "assistant", "content": "Perfect! You've solved it completely."},
    ]

    engine = SemanticSummarizationEngine(max_length=15, summary_window_size=5)

    print(f"\nOriginal conversation length: {len(simulated_conversation)} messages")
    print(f"Max length: {engine.max_length}, Recent window: {engine.summary_window_size}")

    managed, summarized = engine.manage_conversation(simulated_conversation)

    print(f"\nManaged conversation length: {len(managed)} messages")
    print(f"Summarization occurred: {summarized}")

    if summarized and engine.conversation_summary:
        print("\n" + "=" * 70)
        print("GENERATED SUMMARY:")
        print("=" * 70)
        print(engine.conversation_summary)
        print("=" * 70)

    print("\nStructure of managed conversation:")
    for i, msg in enumerate(managed):
        role = msg.get("role")
        content_preview = msg.get("content", "")[:60]
        if isinstance(content_preview, list):
            content_preview = str(content_preview)[:60]
        print(f"  {i+1}. [{role}] {content_preview}...")
