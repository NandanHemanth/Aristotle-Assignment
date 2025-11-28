import json
import time
from typing import Dict, List, Optional, Tuple
from openrouter_client import client
from config import (
    MODELS,
    SOLUTION_GENERATOR_PROMPT,
    TUTOR_PROMPT,
    VERIFIER_PROMPT,
    VISION_PROMPT,
)
from utils import format_verification_result, truncate_conversation_history


class TutoringEngine:
    """
    Multi-agent tutoring engine implementing the architecture from BLUEPRINT.md.

    Three-stage pipeline:
    1. Homework input processing (vision model for images)
    2. Reference solution generation (reasoning model, stored separately)
    3. Student-facing tutoring (fast model with Socratic guidance)

    Key insight: Reference solution is NEVER directly in tutor's context to prevent leakage.
    Instead, we use a verification layer that checks student work and provides guidance.
    """

    def __init__(self):
        self.reference_solution: Optional[str] = None
        self.problem_statement: Optional[str] = None
        self.conversation_history: List[Dict] = []
        self.verification_cache: Dict[str, Dict] = {}

        # Performance metrics
        self.metrics = {
            "solution_generation_time": 0,
            "total_tutor_tokens": 0,
            "total_cost": 0,
        }

    def process_problem_image(self, image_data: str) -> str:
        """
        Stage 1: Extract problem statement from image using vision model.

        Based on BLUEPRINT.md:
        - GPT-4o-mini provides best value for multimodal input
        - Vision models have limitations with handwriting (~24% WER)

        Args:
            image_data: Base64 encoded image

        Returns:
            Extracted problem statement
        """
        try:
            response = client.chat_completion_with_vision(
                model=MODELS["vision"],
                text_prompt=VISION_PROMPT,
                image_data=image_data,
                stream=False,
            )

            problem_text = response["choices"][0]["message"]["content"]
            self.problem_statement = problem_text
            return problem_text

        except Exception as e:
            return f"Error extracting problem from image: {str(e)}"

    def generate_reference_solution(self, problem: str) -> Tuple[str, float]:
        """
        Stage 2: Generate reference solution using reasoning model.

        Based on BLUEPRINT.md:
        - DeepSeek-R1 offers exceptional price-performance for reasoning
        - Solution is stored separately, NEVER in tutor's context
        - This prevents "solution leakage" where tutor reveals answers

        Args:
            problem: Problem statement

        Returns:
            Tuple of (solution, generation_time_seconds)
        """
        self.problem_statement = problem

        messages = [
            {"role": "system", "content": SOLUTION_GENERATOR_PROMPT},
            {"role": "user", "content": f"Solve this problem:\n\n{problem}"},
        ]

        start_time = time.time()

        try:
            response = client.chat_completion(
                model=MODELS["solution_generator"],
                messages=messages,
                stream=False,
                temperature=0.3,  # Lower temperature for more consistent reasoning
            )

            solution = response["choices"][0]["message"]["content"]
            generation_time = time.time() - start_time

            self.reference_solution = solution
            self.metrics["solution_generation_time"] = generation_time

            # Track cost
            usage = response.get("usage", {})
            cost = client.estimate_cost(
                MODELS["solution_generator"],
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0),
            )
            self.metrics["total_cost"] += cost

            return solution, generation_time

        except Exception as e:
            return f"Error generating solution: {str(e)}", 0

    def verify_student_work(self, student_work: str) -> Dict:
        """
        Verification layer: Check student work against reference solution.

        This is the KEY architectural pattern from BLUEPRINT.md to prevent solution leakage:
        - Separate model call compares student work to reference
        - Returns verification metadata (correct/incorrect, where error is)
        - Tutor uses this metadata to guide WITHOUT seeing the reference solution

        Args:
            student_work: Student's current solution attempt

        Returns:
            Verification result dictionary
        """
        if not self.reference_solution:
            return {
                "is_correct": False,
                "first_error_location": "No reference solution available",
                "understanding_level": "unknown",
                "hint_suggestion": "Let's work through this problem step by step.",
            }

        # Check cache to avoid redundant verification
        cache_key = hash(student_work)
        if cache_key in self.verification_cache:
            return self.verification_cache[cache_key]

        messages = [
            {"role": "system", "content": VERIFIER_PROMPT},
            {
                "role": "user",
                "content": f"""Reference Solution:
{self.reference_solution}

Student's Work:
{student_work}

Verify the student's work and provide feedback in JSON format.""",
            },
        ]

        try:
            response = client.chat_completion(
                model=MODELS["verifier"],
                messages=messages,
                stream=False,
                temperature=0.1,  # Very low temperature for consistent verification
            )

            result_text = response["choices"][0]["message"]["content"]

            # Extract JSON from response
            try:
                # Try to find JSON in the response
                start_idx = result_text.find("{")
                end_idx = result_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    result = json.loads(result_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                result = {
                    "is_correct": False,
                    "first_error_location": "Unable to verify",
                    "understanding_level": "partial",
                    "hint_suggestion": "Can you explain your approach to this problem?",
                }

            # Cache result
            self.verification_cache[cache_key] = result

            # Track cost
            usage = response.get("usage", {})
            cost = client.estimate_cost(
                MODELS["verifier"],
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0),
            )
            self.metrics["total_cost"] += cost

            return result

        except Exception as e:
            return {
                "is_correct": False,
                "first_error_location": f"Verification error: {str(e)}",
                "understanding_level": "unknown",
                "hint_suggestion": "Let's continue working through this together.",
            }

    def chat(self, user_message: str, stream: bool = True):
        """
        Stage 3: Student-facing tutoring with Socratic guidance.

        Based on BLUEPRINT.md:
        - Claude Haiku 4.5 with :nitro for fast, responsive dialogue
        - Streaming enabled for 10-100x better perceived latency
        - Prompt caching for static system instructions
        - Verification results guide tutor WITHOUT revealing solution

        Args:
            user_message: Student's message
            stream: Whether to stream the response

        Yields:
            Response chunks (if streaming) or returns complete response
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})

        # Check if user's message contains their work - if so, verify it
        # Simple heuristic: if message is long, it likely contains work
        verification_guidance = ""
        if len(user_message.split()) > 20:
            verification = self.verify_student_work(user_message)
            verification_guidance = (
                "\n\n" + format_verification_result(verification)
            )

        # Create system prompt with problem context but WITHOUT solution
        system_content = f"""{TUTOR_PROMPT}

PROBLEM CONTEXT:
The student is working on this problem:
{self.problem_statement}

Your role is to guide them to solve it themselves through questions and hints.
{verification_guidance}"""

        # Use prompt caching for system instructions
        messages = client.create_cached_messages(
            system_prompt=system_content,
            conversation_history=truncate_conversation_history(
                self.conversation_history
            ),
        )

        if stream:
            # Stream response for better perceived latency
            return self._stream_chat(messages)
        else:
            # Synchronous response
            response = client.chat_completion(
                model=MODELS["tutor"], messages=messages, stream=False, temperature=0.7
            )

            assistant_message = response["choices"][0]["message"]["content"]
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )

            # Track metrics
            usage = response.get("usage", {})
            self.metrics["total_tutor_tokens"] += usage.get("completion_tokens", 0)
            cost = client.estimate_cost(
                MODELS["tutor"],
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0),
                usage.get("cached_tokens", 0),
            )
            self.metrics["total_cost"] += cost

            return assistant_message

    def _stream_chat(self, messages: List[Dict]):
        """
        Stream chat response for better perceived latency.

        Yields response chunks as they arrive.
        """
        assistant_message = ""

        try:
            stream = client.chat_completion(
                model=MODELS["tutor"], messages=messages, stream=True, temperature=0.7
            )

            for chunk in stream:
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        assistant_message += content
                        yield content

            # Save complete message to history
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )

        except Exception as e:
            error_msg = f"Error in chat: {str(e)}"
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            yield error_msg

    def get_metrics(self) -> Dict:
        """Get performance metrics."""
        return {
            **self.metrics,
            "conversation_length": len(self.conversation_history),
            "has_reference_solution": self.reference_solution is not None,
        }

    def reset(self):
        """Reset the tutoring session."""
        self.reference_solution = None
        self.problem_statement = None
        self.conversation_history = []
        self.verification_cache = {}
        self.metrics = {
            "solution_generation_time": 0,
            "total_tutor_tokens": 0,
            "total_cost": 0,
        }
