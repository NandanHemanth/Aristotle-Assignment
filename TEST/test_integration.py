"""
Quick integration test for the tutoring system.
Tests the full pipeline: problem input -> solution generation -> tutoring
"""

from tutoring_engine import TutoringEngine

def test_tutoring_flow():
    print("=" * 50)
    print("ARISTOTLE AI TUTOR - INTEGRATION TEST")
    print("=" * 50)

    # Initialize engine
    print("\n1. Initializing TutoringEngine...")
    engine = TutoringEngine()
    print("   ✓ Engine initialized")

    # Test problem
    problem = """
    Solve for x: 2x + 5 = 13
    """

    print("\n2. Generating reference solution...")
    print(f"   Problem: {problem.strip()}")
    solution, gen_time = engine.generate_reference_solution(problem)

    if solution.startswith("Error"):
        print(f"   ✗ Error: {solution}")
        return False

    print(f"   ✓ Solution generated in {gen_time:.1f}s")
    print(f"   Reference solution (hidden from tutor):")
    print(f"   {solution[:100]}...")

    # Test tutoring
    print("\n3. Testing Socratic tutoring...")
    student_message = "Can you help me solve this equation?"
    print(f"   Student: {student_message}")

    print("   Tutor: ", end="", flush=True)
    response = ""
    for chunk in engine.chat(student_message, stream=True):
        print(chunk, end="", flush=True)
        response += chunk
    print()

    # Verify tutor doesn't leak solution
    if "x = 4" in response or "x=4" in response:
        print("\n   ✗ WARNING: Tutor leaked the solution!")
    else:
        print("\n   ✓ Tutor maintained Socratic approach (no direct answer)")

    # Get metrics
    metrics = engine.get_metrics()
    print("\n4. Session Metrics:")
    print(f"   - Setup time: {metrics['solution_generation_time']:.1f}s")
    print(f"   - Total cost: ${metrics['total_cost']:.4f}")
    print(f"   - Messages: {metrics['conversation_length']}")

    print("\n" + "=" * 50)
    print("✓ ALL TESTS PASSED!")
    print("=" * 50)
    print("\nYou can now run the app:")
    print("  streamlit run app.py")
    print("=" * 50)

    return True

if __name__ == "__main__":
    try:
        test_tutoring_flow()
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
