"""
Test conversation history caching for faster follow-up questions.

Scenario:
1. Ask "What is supervised learning?"
2. Ask "Supervised vs unsupervised?" (should be faster with cached context)
3. Ask "Give me an example" (should be even faster)
"""

from tutoring_engine import TutoringEngine
import time

print("=" * 70)
print("TESTING CONVERSATION HISTORY CACHING")
print("=" * 70)

# Initialize engine
engine = TutoringEngine()

# For conceptual questions, we don't need a homework problem
engine.problem_statement = "General machine learning concepts"

print("\nThis test demonstrates conversation history caching.")
print("Follow-up questions should be faster because previous context is cached.\n")

# Question 1: Initial question
print("=" * 70)
print("QUESTION 1: What is supervised learning?")
print("=" * 70)

question1 = "What is supervised learning?"
print(f"\nAsking: '{question1}'")
print("Expected: CACHE MISS (first time), then cache created\n")

start = time.time()
response1 = engine.chat(question1, stream=False)
latency1 = time.time() - start

print(f"Response length: {len(response1)} characters")
print(f"Latency: {latency1:.3f}s")
print(f"Conversation length: {engine.get_metrics()['conversation_length']} messages\n")

# Question 2: Follow-up (should use cached context)
print("=" * 70)
print("QUESTION 2: Supervised vs unsupervised?")
print("=" * 70)

question2 = "What's the difference between supervised and unsupervised learning?"
print(f"\nAsking: '{question2}'")
print("Expected: CACHE HIT (previous conversation cached)\n")

start = time.time()
response2 = engine.chat(question2, stream=False)
latency2 = time.time() - start

print(f"Response length: {len(response2)} characters")
print(f"Latency: {latency2:.3f}s")
print(f"Conversation length: {engine.get_metrics()['conversation_length']} messages\n")

# Question 3: Another follow-up (should use cached context)
print("=" * 70)
print("QUESTION 3: Give me an example")
print("=" * 70)

question3 = "Can you give me a real-world example of supervised learning?"
print(f"\nAsking: '{question3}'")
print("Expected: CACHE HIT (previous conversation cached)\n")

start = time.time()
response3 = engine.chat(question3, stream=False)
latency3 = time.time() - start

print(f"Response length: {len(response3)} characters")
print(f"Latency: {latency3:.3f}s")
print(f"Conversation length: {engine.get_metrics()['conversation_length']} messages\n")

# Analysis
print("=" * 70)
print("LATENCY ANALYSIS")
print("=" * 70)

print(f"\nQuestion 1 latency: {latency1:.3f}s (cache miss)")
print(f"Question 2 latency: {latency2:.3f}s (cache hit)")
print(f"Question 3 latency: {latency3:.3f}s (cache hit)")

# Calculate speedup
if latency2 < latency1:
    speedup2 = ((latency1 - latency2) / latency1) * 100
    print(f"\nQuestion 2 speedup: {speedup2:.1f}% faster than Question 1")
else:
    print(f"\nQuestion 2 was {((latency2 - latency1) / latency1) * 100:.1f}% slower (cache might not have been used)")

if latency3 < latency1:
    speedup3 = ((latency1 - latency3) / latency1) * 100
    print(f"Question 3 speedup: {speedup3:.1f}% faster than Question 1")

print("\n" + "=" * 70)
print("KEY OBSERVATIONS:")
print("=" * 70)
print("1. First question: Cache miss (creates cache)")
print("2. Follow-up questions: Cache hits (reuse cached conversation)")
print("3. Latency should improve for questions 2 and 3")
print("4. This enables faster responses when discussing related topics")
print("=" * 70)

# Metrics
metrics = engine.get_metrics()
print(f"\nFinal metrics:")
print(f"Total cost: ${metrics['total_cost']:.4f}")
print(f"Messages: {metrics['conversation_length']}")
