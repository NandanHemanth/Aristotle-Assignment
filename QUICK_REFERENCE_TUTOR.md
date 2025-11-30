# Quick Reference: Enhanced Tutor Behavior

## Side-by-Side Comparison

### Example 1: Conceptual Question

**Student:** "What is the difference between supervised and unsupervised learning?"

#### ❌ OLD Behavior (Pure Socratic)
```
Welcome! Let's explore this together.

I'm glad you're curious about this distinction. Before I guide you,
let me start by understanding what you already know.

Let me ask you a few questions:
1. What does the word "supervised" mean to you in everyday language?
2. When you hear "unsupervised," what comes to mind?
3. Have you encountered any examples of machine learning tasks before?

Once I understand where you're starting from, I can ask better
questions to help you discover the key differences yourself.
```

**Problem:** Student wants to LEARN the concept, not discover it through questions.

#### ✅ NEW Behavior (Explanatory)
```
Great question! Let me explain these two fundamental approaches to
machine learning.

DEFINITIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Supervised Learning: The algorithm learns from labeled data where
each example has both input features and the correct output (label).

Unsupervised Learning: The algorithm finds patterns in data that
has no labels - it discovers structure on its own.

WHY DOES THIS DISTINCTION EXIST?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sometimes we have labeled data (like emails marked spam/not-spam),
but often we don't have labels. Unsupervised learning helps us find
patterns when we don't know what we're looking for yet.

HOW THEY WORK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Supervised Learning:
Think of it like learning with a teacher. You're shown examples
with correct answers, and you learn to predict the answer for new
examples.

Example: Learning to identify cats vs dogs
- Teacher shows you 1000 photos labeled "cat" or "dog"
- You learn the patterns (whiskers, ears, size)
- Now you can identify new photos on your own

Unsupervised Learning:
Like exploring a new city without a map. You discover neighborhoods,
clusters, and patterns on your own.

Example: Grouping customers
- You have data on 10,000 customers (purchases, behavior)
- No labels telling you which "type" each customer is
- The algorithm discovers natural groupings on its own
  (e.g., "budget shoppers", "luxury buyers", "impulse buyers")

REAL-WORLD EXAMPLES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Supervised Learning:
1. Email spam detection - Learn from labeled spam/not-spam emails
2. Medical diagnosis - Learn from patient data with known diagnoses
3. Housing prices - Learn from houses with known sale prices

Unsupervised Learning:
1. Customer segmentation - Find natural customer groups
2. Anomaly detection - Find unusual patterns (fraud, defects)
3. Topic modeling - Discover topics in documents

NOW, TO DEEPEN YOUR UNDERSTANDING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• If you had Netflix viewing data with no genre labels, which
  approach would you use to organize movies? Why?

• What challenges might arise when labels are expensive or hard
  to obtain?

• Can you think of a case where you'd want to use BOTH approaches
  together?
```

**Result:** Student gets full understanding PLUS thought-provoking questions.

---

### Example 2: Homework Problem

**Student:** "Can you tell me what x equals in: 2x + 5 = 13?"

#### ✅ CORRECT Behavior (Socratic - Same Before/After)
```
I won't give you the answer directly, but I'll guide you to
discover it!

To solve this equation, we need to isolate x. Let me ask you:

What's the first operation we can perform to start moving
everything except x to the right side?

Hint: Look at what's being added to 2x on the left side.
```

**Result:** Maintains pedagogical integrity, no answer leakage.

---

### Example 3: Follow-up Conceptual

**Student:** "Wait, so in supervised learning, who creates the labels?"

#### ✅ NEW Behavior (Explanatory)
```
Excellent question! This is a crucial practical consideration.

WHO CREATES LABELS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Labels can come from several sources:

1. HUMAN ANNOTATORS (Most common)
   - Hired workers label data manually
   - Example: People tag images as "cat" or "dog"
   - Can be expensive and time-consuming

2. AUTOMATIC COLLECTION
   - Labels are naturally part of the data
   - Example: Email you manually mark as spam
   - Example: Products you actually purchased (vs just viewed)

3. EXPERT LABELING
   - Domain experts provide labels
   - Example: Doctors diagnosing medical images
   - Example: Financial analysts marking fraudulent transactions
   - More accurate but very expensive

4. WEAK SUPERVISION / SEMI-AUTOMATED
   - Use rules or heuristics to generate approximate labels
   - Example: "If email contains 'CLICK HERE!!!', probably spam"
   - Faster but less accurate

REAL-WORLD EXAMPLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When building a cat/dog classifier:
- Option 1: Pay workers $0.01 per image to label 100,000 images
  Cost: $1,000, Time: 1 week
- Option 2: Use pre-labeled dataset like ImageNet (free but generic)
- Option 3: Use transfer learning - start with model trained on
  labeled data, fine-tune on your small labeled set

THE LABELING BOTTLENECK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is why unsupervised learning is valuable! Getting labels is:
• Expensive (humans are slow and costly)
• Sometimes impossible (who labels "unusual" patterns?)
• Can introduce bias (human labelers make mistakes)

THINK ABOUT THIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• If you're building a medical AI, would you trust labels from
  random people or only doctors? What's the trade-off?

• How might label quality affect your model's performance?

• Can you think of creative ways to get labels cheaply?
```

**Result:** Deep explanation of practical considerations + engagement.

---

## Quick Decision Guide

### When will tutor be EXPLANATORY?

✅ "What is...?"
✅ "Explain..."
✅ "What's the difference between...?"
✅ "How does... work?"
✅ "Why do we use...?"
✅ "Tell me about..."
✅ "I want to understand..."

### When will tutor be SOCRATIC?

✅ "Solve this equation: ..."
✅ "What's the answer to...?"
✅ "Calculate..."
✅ "Find the value of x in..."
✅ "Prove that..."
✅ Any specific homework problem

---

## Teaching Structure

### For Conceptual Questions

```
1. DEFINE (What?)
   ↓
2. EXPLAIN (Why? How? When?)
   ↓
3. EXEMPLIFY (Real-world examples)
   ↓
4. ENGAGE (Thought-provoking questions)
```

### For Homework Problems

```
1. UNDERSTAND (What do you know?)
   ↓
2. GUIDE (Ask leading questions)
   ↓
3. VERIFY (Check student work)
   ↓
4. REDIRECT (Point out errors via questions)
```

---

## Performance

### With Prompt Caching

| Metric | First Message | Cached Messages |
|--------|--------------|-----------------|
| Input processing | ~300ms | ~30ms (10x faster) |
| Time-to-first-token | ~500ms | ~200ms |
| Cost | $0.001 | $0.0001 (cache read) |

### Model Used
- **Claude Haiku 4.5** with `:nitro` routing
- Fast, high-quality, cost-effective
- Excellent instruction-following

---

## Try It!

```bash
# Start the app
streamlit run app.py

# Ask conceptual questions
"What is gradient descent?"
"Explain overfitting vs underfitting"

# Ask homework questions
"Solve: x² - 5x + 6 = 0"
"Find derivative of: f(x) = x³"
```

**You'll see the difference immediately!**
