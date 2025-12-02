"""
Test to verify cost tracking works correctly with streaming.
"""

from tutoring_engine import TutoringEngine

print("=" * 60)
print("TESTING COST TRACKING WITH STREAMING")
print("=" * 60)

# Initialize engine
engine = TutoringEngine()

# Set up a simple problem
problem = "Solve for x: 2x + 5 = 13"
print(f"\nProblem: {problem}")

# Generate reference solution
print("\n1. Generating reference solution...")
solution, gen_time = engine.generate_reference_solution(problem)
print(f"   Setup complete in {gen_time:.1f}s")

# Check initial metrics
initial_metrics = engine.get_metrics()
print(f"\n2. Initial metrics:")
print(f"   Cost: ${initial_metrics['total_cost']:.6f}")
print(f"   Messages: {initial_metrics['conversation_length']}")

# Send first message (streaming)
print(f"\n3. Sending message 1 (streaming)...")
student_msg1 = "What's the first step?"
full_response1 = ""
for chunk in engine.chat(student_msg1, stream=True):
    full_response1 += chunk

metrics_after_1 = engine.get_metrics()
print(f"   Response length: {len(full_response1)} characters")
print(f"   Cost after message 1: ${metrics_after_1['total_cost']:.6f}")
print(f"   Messages: {metrics_after_1['conversation_length']}")

# Send second message (streaming)
print(f"\n4. Sending message 2 (streaming)...")
student_msg2 = "I think I should subtract 5 from both sides"
full_response2 = ""
for chunk in engine.chat(student_msg2, stream=True):
    full_response2 += chunk

metrics_after_2 = engine.get_metrics()
print(f"   Response length: {len(full_response2)} characters")
print(f"   Cost after message 2: ${metrics_after_2['total_cost']:.6f}")
print(f"   Messages: {metrics_after_2['conversation_length']}")

# Send third message (streaming)
print(f"\n5. Sending message 3 (streaming)...")
student_msg3 = "Then I divide both sides by 2 to get x = 4"
full_response3 = ""
for chunk in engine.chat(student_msg3, stream=True):
    full_response3 += chunk

metrics_after_3 = engine.get_metrics()
print(f"   Response length: {len(full_response3)} characters")
print(f"   Cost after message 3: ${metrics_after_3['total_cost']:.6f}")
print(f"   Messages: {metrics_after_3['conversation_length']}")

# Verify cost is increasing
print("\n" + "=" * 60)
print("VERIFICATION:")
print("=" * 60)

cost_1 = metrics_after_1['total_cost']
cost_2 = metrics_after_2['total_cost']
cost_3 = metrics_after_3['total_cost']

print(f"Cost progression:")
print(f"  After msg 1: ${cost_1:.6f}")
print(f"  After msg 2: ${cost_2:.6f} (increase: ${cost_2 - cost_1:.6f})")
print(f"  After msg 3: ${cost_3:.6f} (increase: ${cost_3 - cost_2:.6f})")

if cost_1 > 0 and cost_2 > cost_1 and cost_3 > cost_2:
    print("\n[SUCCESS] Cost is increasing with each message!")
else:
    print("\n[FAILURE] Cost is not tracking properly")
    if cost_1 == 0:
        print("  - Message 1 cost is $0 (not tracking)")
    if cost_2 <= cost_1:
        print("  - Message 2 cost did not increase")
    if cost_3 <= cost_2:
        print("  - Message 3 cost did not increase")

print("\n" + "=" * 60)
