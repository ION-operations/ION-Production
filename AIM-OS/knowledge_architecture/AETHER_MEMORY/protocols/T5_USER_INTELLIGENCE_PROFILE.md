---
id: "user_intelligence_profile_T5_quick"
system: "meta_principles"
component: null
level: "T5"
type: "quick_reference"
title: "User Intelligence Profile & Honesty Protocol - Quick Reference"
description: "500-word quick reference cheat sheet for User Intelligence Profile & Honesty Protocol"
audience: "developers, quick lookup"
confidence_threshold: 0.90
token_cost: 500
word_count: 500
created: "2025-11-04T05:30:00Z"
updated: "2025-11-04T05:30:00Z"
author: "aether"
status: "production"
tags: ["user-intelligence", "honesty", "verification", "quick-reference", "cheat-sheet", "critical", "t0-t6"]
dependencies: ["T4_USER_INTELLIGENCE_PROFILE.md"]
related_docs: ["T3_USER_INTELLIGENCE_PROFILE.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# User Intelligence Profile & Honesty Protocol - Quick Reference (≈500 words)

**Quick cheat sheet for user intelligence tracking and honest communication**

---

## 🚨 **FORBIDDEN PHRASES**

**Never Say Without Verification:**
- ❌ "Fixed!" / "Done!" / "Problem solved!"
- ❌ "You're absolutely right!" / "I completely agree!"
- ❌ "This will work" / "Should work now"

**Always Say Before Verification:**
- ✅ "Applied fix - needs testing to verify"
- ✅ "I understand your point - let me validate"
- ✅ "Changes applied - requires verification"

---

## 📊 **USER INTELLIGENCE TRACKING**

**Update Accuracy:**
```python
profile.update_accuracy(domain, question_type, is_correct)
```

**Get Domain Accuracy:**
```python
accuracy = profile.get_domain_accuracy("code")  # Returns 0.0-1.0
```

**Check User Profile:**
```python
if accuracy < 0.5:
    # User often wrong - increase confidence threshold
    adaptation.increase_confidence_threshold = 0.1
    adaptation.add_examples = True
elif accuracy > 0.7 and thinking_style == INTUITIVE:
    # User intuitively correct - provide validation + visualization
    adaptation.add_visualization = True
    adaptation.add_code_examples = True
```

---

## ✅ **HONESTY ENFORCER QUICK CHECK**

```python
# Before making claim
validation = honesty_enforcer.check_claim(claim_text, ClaimType.FIX)
if not validation.valid:
    # Use recommended response
    response = validation.recommended_response

# Before agreeing
validation = honesty_enforcer.validate_agreement(user_statement, ai_response)
if not validation.valid:
    # Use recommended honest response
    response = validation.recommended_response
```

---

## 🎯 **ADAPTIVE RESPONSES**

**Cognitive Style Adaptations:**
- **Visual:** Add diagrams, visual aids
- **Examples:** Add concrete examples
- **Testing:** Add test cases, demonstrations
- **Code:** Provide code directly

**Accuracy-Based Adaptations:**
- **Often Wrong (accuracy < 0.5):** Increase confidence threshold, more examples, detailed explanations
- **Intuitively Correct (accuracy > 0.7, intuitive):** Provide validation, visualization, code examples
- **Standard (accuracy 0.5-0.7):** Standard responses

---

## 🔗 **INTEGRATION QUICK START**

```python
# Initialize
profile_store = UserIntelligenceProfileStore(storage_path)
profile = profile_store.get_profile(user_id) or UserIntelligenceProfile(user_id, profile_id)
tracker = VerificationTracker()
enforcer = HonestyEnforcer(profile, tracker)
generator = AdaptiveResponseGenerator(profile, enforcer)

# Generate response
response = generator.generate_response(user_input, ai_knowledge, context)

# Track interaction
if user_confirmed_correct:
    profile.update_accuracy(domain, question_type, is_correct=True)
tracker.mark_verified(claim_text)
```

---

## 📋 **MANDATORY CHECKLIST**

**Before Making Any Claim:**
- [ ] Check forbidden phrases
- [ ] Check verification status
- [ ] Check user verification rate
- [ ] Check user accuracy for domain
- [ ] Generate adaptive response

**Before Agreeing:**
- [ ] Check blind agreement patterns
- [ ] Check user accuracy for domain
- [ ] Validate user statement
- [ ] Generate honest response

---

## 🎯 **USER PATTERNS**

**Track:**
- Accuracy by domain/question type
- Cognitive style (visual, auditory, kinesthetic)
- Learning preference (examples, testing, visualization)
- Thinking style (intuitive, analytical, creative)
- Feedback quality (helpful vs misleading)

**Adapt:**
- Response complexity (standard, detailed, very_detailed)
- Visual aids (diagrams, examples, code)
- Confidence threshold (standard, increased)
- Explanation depth (summary, detailed, step-by-step)

---

**Status:** ✅ **CRITICAL PROTOCOL** - Mandatory for All Interactions  
**Reference:** See T3 for detailed implementation, T4 for complete reference

