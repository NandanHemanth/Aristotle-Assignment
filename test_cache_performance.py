"""
Test prompt caching performance by measuring time-to-first-token.

This test demonstrates the TRUE benefit of caching:
- Input processing time (where caching helps)
- Time-to-first-token (critical for user experience)
"""

from tutoring_engine import TutoringEngine
import time

print("=" * 70)
print("PROMPT CACHING PERFORMANCE TEST")
print("=" * 70)

# Initialize engine
engine = TutoringEngine()
engine.problem_statement = "General machine learning concepts"

print("\nMeasuring time-to-first-token (where caching benefits appear)")
print("Total response time includes generation (not affected by caching)\n")

# Question 1: Initial question (cache miss expected)
print("=" * 70)
print("QUESTION 1: What is supervised learning?")
print("=" * 70)

question1 = "What is supervised learning? Keep it brief."
print(f"Asking: '{question1}'")

start = time.time()
first_token_time = None
chunk_count = 0

for chunk in engine.chat(question1, stream=True):
    if first_token_time is None:
        first_token_time = time.time() - start
        print(f"[TTFT] Time-to-first-token: {first_token_time:.3f}s (CACHE MISS)")
    chunk_count += 1

total_time = time.time() - start
print(f"[TOTAL] Total response time: {total_time:.3f}s")
print(f"[CHUNKS] Chunks received: {chunk_count}\n")

# Small delay to ensure cache is written
time.sleep(0.5)

# Question 2: Follow-up (cache hit expected)
print("=" * 70)
print("QUESTION 2: What about unsupervised learning?")
print("=" * 70)

question2 = "What about unsupervised learning? Keep it brief."
print(f"Asking: '{question2}'")

start = time.time()
first_token_time_2 = None
chunk_count_2 = 0

for chunk in engine.chat(question2, stream=True):
    if first_token_time_2 is None:
        first_token_time_2 = time.time() - start
        print(f"[TTFT] Time-to-first-token: {first_token_time_2:.3f}s (CACHE HIT)")
    chunk_count_2 += 1

total_time_2 = time.time() - start
print(f"[TOTAL] Total response time: {total_time_2:.3f}s")
print(f"[CHUNKS] Chunks received: {chunk_count_2}\n")

# Small delay
time.sleep(0.5)

# Question 3: Another follow-up (cache hit expected)
print("=" * 70)
print("QUESTION 3: Give me an example")
print("=" * 70)

question3 = "Give me one example of supervised learning. Keep it brief."
print(f"Asking: '{question3}'")

start = time.time()
first_token_time_3 = None
chunk_count_3 = 0

for chunk in engine.chat(question3, stream=True):
    if first_token_time_3 is None:
        first_token_time_3 = time.time() - start
        print(f"[TTFT] Time-to-first-token: {first_token_time_3:.3f}s (CACHE HIT)")
    chunk_count_3 += 1

total_time_3 = time.time() - start
print(f"[TOTAL] Total response time: {total_time_3:.3f}s")
print(f"[CHUNKS] Chunks received: {chunk_count_3}\n")

# Analysis
print("=" * 70)
print("CACHING BENEFIT ANALYSIS")
print("=" * 70)

print("\n[ANALYSIS] TIME-TO-FIRST-TOKEN (Where caching helps):")
print(f"   Question 1: {first_token_time:.3f}s (cache miss)")
print(f"   Question 2: {first_token_time_2:.3f}s (cache hit)")
print(f"   Question 3: {first_token_time_3:.3f}s (cache hit)")

if first_token_time_2 < first_token_time:
    speedup = ((first_token_time - first_token_time_2) / first_token_time) * 100
    print(f"\n[SUCCESS] Question 2 speedup: {speedup:.1f}% faster (CACHE WORKING!)")
else:
    slowdown = ((first_token_time_2 - first_token_time) / first_token_time) * 100
    print(f"\n[WARNING] Question 2: {slowdown:.1f}% slower (cache might not be active)")

if first_token_time_3 < first_token_time:
    speedup = ((first_token_time - first_token_time_3) / first_token_time) * 100
    print(f"[SUCCESS] Question 3 speedup: {speedup:.1f}% faster (CACHE WORKING!)")

print("\n[ANALYSIS] TOTAL RESPONSE TIME (Includes generation - NOT affected by caching):")
print(f"   Question 1: {total_time:.3f}s")
print(f"   Question 2: {total_time_2:.3f}s")
print(f"   Question 3: {total_time_3:.3f}s")

# Cost analysis
metrics = engine.get_metrics()
print(f"\n[COST] Cost metrics:")
print(f"   Total cost: ${metrics['total_cost']:.4f}")
print(f"   Messages: {metrics['conversation_length']}")
print(f"   Average cost per message: ${metrics['total_cost'] / (metrics['conversation_length'] / 2):.4f}")

print("\n" + "=" * 70)
print("KEY INSIGHTS:")
print("=" * 70)
print("1. Time-to-first-token shows caching benefit (input processing)")
print("2. Total response time doesn't improve (generation not cached)")
print("3. Caching makes the app FEEL faster (first tokens arrive sooner)")
print("4. Cost savings occur on cached input tokens (90% discount)")
print("=" * 70)
