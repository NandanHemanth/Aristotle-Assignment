"""
Simple integration test without Unicode characters.
"""

from tutoring_engine import TutoringEngine

print("Testing Aristotle AI Tutor Integration...")
print("=" * 50)

# Initialize
engine = TutoringEngine()
print("1. Engine initialized: OK")

# Generate solution
problem = "Solve for x: 2x + 5 = 13"
print(f"\n2. Problem: {problem}")

solution, gen_time = engine.generate_reference_solution(problem)
print(f"   Solution generated in {gen_time:.1f}s: OK")

# Test tutoring (non-streaming for simplicity)
student_msg = "What's the first step?"
print(f"\n3. Student asks: {student_msg}")

response = engine.chat(student_msg, stream=False)
print(f"   Tutor responds: {response[:100]}...")

# Check metrics
metrics = engine.get_metrics()
print(f"\n4. Metrics:")
print(f"   - Cost: ${metrics['total_cost']:.4f}")
print(f"   - Messages: {metrics['conversation_length']}")

print("\n" + "=" * 50)
print("All tests passed! Ready to run app.py")
print("=" * 50)
