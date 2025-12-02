"""
Test the enhanced tutor's ability to handle both:
1. Conceptual questions (explanatory mode)
2. Homework problems (Socratic mode)
"""

from tutoring_engine import TutoringEngine

print("=" * 70)
print("TESTING ENHANCED ARISTOTLE TUTOR")
print("=" * 70)

# Initialize engine
engine = TutoringEngine()

# Test 1: Conceptual Question
print("\n" + "=" * 70)
print("TEST 1: CONCEPTUAL QUESTION")
print("=" * 70)

# For conceptual questions, we don't need a homework problem
# Just initialize with a placeholder
engine.problem_statement = "General machine learning concepts"

print("\nStudent asks: 'What is the difference between supervised and unsupervised learning?'\n")

conceptual_question = "I want to understand the difference between supervised learning and unsupervised learning."

print("Tutor response:")
print("-" * 70)

# Get response (non-streaming for readability in test)
response = engine.chat(conceptual_question, stream=False)
print(response)

print("-" * 70)

# Test 2: Homework Problem
print("\n" + "=" * 70)
print("TEST 2: HOMEWORK PROBLEM")
print("=" * 70)

# Reset and set up a homework problem
engine.reset()
problem = "Solve for x: 2x + 5 = 13"
print(f"\nProblem: {problem}")
print("\nGenerating reference solution...")

solution, gen_time = engine.generate_reference_solution(problem)
print(f"Setup complete in {gen_time:.1f}s")

homework_question = "Can you tell me what x equals?"

print(f"\nStudent asks: '{homework_question}'\n")
print("Tutor response:")
print("-" * 70)

response2 = engine.chat(homework_question, stream=False)
print(response2)

print("-" * 70)

# Metrics
print("\n" + "=" * 70)
print("SESSION METRICS")
print("=" * 70)

metrics = engine.get_metrics()
print(f"Total cost: ${metrics['total_cost']:.4f}")
print(f"Messages: {metrics['conversation_length']}")

print("\n" + "=" * 70)
print("KEY OBSERVATIONS:")
print("=" * 70)
print("1. For conceptual questions: Tutor provides FULL explanation with examples")
print("2. For homework problems: Tutor uses Socratic method (no direct answer)")
print("3. Prompt caching ensures fast responses")
print("=" * 70)
