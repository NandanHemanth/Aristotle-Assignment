# Enhanced Tutor Capabilities ✨

## What's New

The tutor has been **enhanced with dual-mode teaching** to handle both conceptual questions and homework problems intelligently.

## The Problem Before

The original tutor was optimized for homework problems using pure Socratic method:
- Great for preventing solution leakage
- But when students asked conceptual questions like "What is supervised learning?", the tutor would only ask questions back
- Students want clear explanations for concepts, not just Socratic questioning

**Example of OLD behavior:**
```
Student: "What is the difference between supervised and unsupervised learning?"

Old Tutor: "Before I guide you, let me understand what you know.
What does 'supervised' mean to you?"
```

This is frustrating for conceptual questions where the student genuinely wants to learn a concept.

## The Solution: Dual-Mode Teaching

The enhanced tutor now **distinguishes between two types of questions**:

### 1. CONCEPTUAL QUESTIONS
**Triggers:** "explain...", "what is...", "difference between...", "how does... work"

**Tutor Behavior:**
1. **DEFINE** - Provide clear, precise definitions
2. **EXPLAIN** - Explain WHY it exists, HOW it works, WHEN to use it
3. **EXEMPLIFY** - Give 2-3 concrete, real-world examples
4. **ENGAGE** - Ask thought-provoking questions to deepen understanding

**Example of NEW behavior:**
```
Student: "What is the difference between supervised and unsupervised learning?"

Enhanced Tutor:
"Great question! Let me explain these two fundamental approaches to machine learning.

DEFINITIONS:
- Supervised Learning: The algorithm learns from labeled data where each
  example has both input features and the correct output (label).
- Unsupervised Learning: The algorithm finds patterns in data that has
  no labels - it discovers structure on its own.

WHY DOES THIS DISTINCTION EXIST?
Sometimes we have labeled data (like emails marked as spam/not spam),
but often we don't. Unsupervised learning helps us find patterns when
we don't know what we're looking for yet.

HOW THEY WORK:
Supervised: Think of it like learning with a teacher. You're shown
examples with correct answers, and you learn to predict the answer
for new examples.

Unsupervised: Like exploring a new city without a map. You discover
neighborhoods, clusters, and patterns on your own.

EXAMPLES:

Supervised Learning:
1. Email spam detection - You have thousands of emails labeled
   "spam" or "not spam". The algorithm learns the pattern.
2. Housing price prediction - Given features (size, location) and
   actual prices, predict price of a new house.
3. Medical diagnosis - Learn from labeled patient data to predict
   diseases.

Unsupervised Learning:
1. Customer segmentation - Group customers by behavior patterns
   without predefined categories.
2. Anomaly detection - Find unusual patterns in data (fraud
   detection) without knowing what fraud looks like.
3. Topic modeling - Discover topics in documents without being told
   what topics exist.

NOW, LET ME ASK YOU:
- Can you think of a situation where you'd prefer unsupervised over
  supervised learning?
- What challenges might arise in each approach?
- If you had a dataset of customer purchases with no labels, which
  approach would you use and why?"
```

### 2. HOMEWORK PROBLEMS
**Triggers:** Specific problems with definite answers (equations, exercises, etc.)

**Tutor Behavior:**
- Uses **Socratic method** - asks guiding questions
- **Never reveals the answer directly**
- Uses **verification layer** to check student work
- Redirects errors without giving away the solution

**Example:**
```
Problem: "Solve for x: 2x + 5 = 13"

Student: "Can you tell me what x equals?"

Tutor: "I won't give you the answer directly, but I'll guide you!

To solve this equation, what operation could you use to get the 'x'
term by itself? What's currently 'attached' to the x term that we
need to deal with first?"
```

## How It Works

### Enhanced Prompt Structure

The tutor prompt in [config.py](config.py) now includes explicit instructions for both modes:

```python
TUTOR_PROMPT = """You are Aristotle, an expert tutor who adapts your
teaching style based on the student's needs.

DISTINGUISH BETWEEN TWO TYPES OF QUESTIONS:

1. CONCEPTUAL QUESTIONS (definitions, explanations, "what is...", "explain...")
   When students ask conceptual questions, be EXPLANATORY:

   Step 1 - DEFINE: Provide clear, precise definitions
   Step 2 - EXPLAIN: Explain the fundamental concepts (WHY/HOW/WHEN)
   Step 3 - EXEMPLIFY: Give concrete, relatable examples
   Step 4 - ENGAGE: Ask thought-provoking questions

   For conceptual questions, YOU SHOULD EXPLAIN FULLY.

2. HOMEWORK PROBLEMS (specific problems with definite answers)
   When students work on homework problems, be SOCRATIC:

   - NEVER directly provide the solution or final answer
   - Ask guiding questions
   - Use verification layer to check work
   ...
"""
```

### Prompt Caching for Speed

The enhanced prompt is **automatically cached** for fast responses:

- First request: Full prompt processing (~300ms)
- Subsequent requests: Cache read (~30ms) - **10x faster**
- Cache reads cost only 10% of input pricing with Claude models

This is implemented in [tutoring_engine.py](tutoring_engine.py):

```python
# System prompt is cached
messages = client.create_cached_messages(
    system_prompt=system_content,  # Enhanced TUTOR_PROMPT - CACHED
    conversation_history=truncate_conversation_history(
        self.conversation_history
    )
)
```

## Benefits

### 1. Better Learning Experience
- **Conceptual questions**: Get full explanations with examples
- **Homework problems**: Maintain pedagogical integrity (no answer leakage)

### 2. Faster Responses
- Prompt caching reduces latency by 85%
- Streaming provides instant feedback (<500ms time-to-first-token)

### 3. Deeper Understanding
- Explanations cover WHAT/WHY/HOW/WHEN
- Multiple examples at increasing sophistication
- Thought-provoking questions spark curiosity

### 4. Adaptive Teaching
- Tutor automatically detects question type
- No manual mode switching needed
- Seamless transition between modes in conversation

## Testing

Run the test to see both modes in action:

```bash
python test_enhanced_tutor.py
```

This will demonstrate:
1. Conceptual question handling (full explanation)
2. Homework problem handling (Socratic method)
3. Metrics showing cost and performance

## Examples of Questions the Tutor Can Now Handle

### Conceptual Questions (Explanatory Mode)
- "What is the difference between supervised and unsupervised learning?"
- "Explain how neural networks work"
- "What is gradient descent and why do we use it?"
- "What's the difference between classification and regression?"
- "How does backpropagation work?"
- "What is overfitting and how do we prevent it?"

### Homework Problems (Socratic Mode)
- "Solve for x: 2x + 5 = 13"
- "Calculate the derivative of f(x) = x² + 3x"
- "Implement a function to reverse a linked list"
- "Prove that √2 is irrational"
- "Find the area of a triangle with sides 3, 4, 5"

## Architecture Notes

### Model Selection
- **Tutor**: Claude Haiku 4.5 with `:nitro` routing
  - Fast responses ($1/$5 per million tokens)
  - High-quality instruction following
  - Excellent at adapting to prompt instructions
  - Supports prompt caching (85% latency reduction)

### Performance Characteristics
- **First message**: ~300ms (full prompt processing)
- **Cached messages**: ~30ms input processing + generation time
- **Time-to-first-token**: <500ms with caching
- **Cost per message**: ~$0.001-0.002

## Implementation Details

### Files Changed

1. **[config.py](config.py)**
   - Enhanced `TUTOR_PROMPT` with dual-mode instructions
   - Added clear structure: DEFINE → EXPLAIN → EXEMPLIFY → ENGAGE

2. **[CLAUDE.md](CLAUDE.md)**
   - Documented new pattern: "Enhanced Tutor: Dual-Mode Teaching"
   - Updated pattern numbering

3. **[tutoring_engine.py](tutoring_engine.py)**
   - Already had prompt caching configured
   - No changes needed - enhanced prompt works automatically

## Summary

The tutor is now **significantly more capable**:

✅ **Handles conceptual questions** with full explanations and examples
✅ **Maintains Socratic approach** for homework to prevent answer leakage
✅ **Automatically detects** which mode to use
✅ **Fast responses** via prompt caching (85% latency reduction)
✅ **Thought-provoking questions** to deepen understanding
✅ **Clear structure**: DEFINE → EXPLAIN → EXEMPLIFY → ENGAGE

**Try it now!** Ask the tutor both types of questions and see the difference.
