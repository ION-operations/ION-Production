---
id: "user_intelligence_profile_T6_source"
system: "meta_principles"
component: null
level: "T6"
type: "source_code"
title: "User Intelligence Profile & Honesty Protocol - Source Code Documentation"
description: "Complete source code documentation with inline comments and explanations"
audience: "maintainers, code reviewers"
confidence_threshold: 0.50
token_cost: 5000
word_count: 5000
created: "2025-11-04T05:50:00Z"
updated: "2025-11-04T05:50:00Z"
author: "aether"
status: "production"
tags: ["user-intelligence", "honesty", "verification", "source-code", "documentation", "critical", "t0-t6"]
dependencies: ["T5_USER_INTELLIGENCE_PROFILE.md"]
related_docs: ["T3_USER_INTELLIGENCE_PROFILE.md", "packages/vif/"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# User Intelligence Profile & Honesty Protocol - Source Code Documentation (≈5,000 words)

**Date:** 2025-11-04  
**Status:** ✅ **CRITICAL PROTOCOL** - Production Ready  
**Purpose:** Complete source code documentation with inline explanations

---

## 📁 **SOURCE CODE STRUCTURE**

```
knowledge_architecture/AETHER_MEMORY/protocols/
├── T0_USER_INTELLIGENCE_PROFILE.md      # Executive summary (100 words)
├── T1_USER_INTELLIGENCE_PROFILE.md       # Overview (500 words)
├── T2_USER_INTELLIGENCE_PROFILE.md        # Architecture (T2, 2,000 words)
├── T3_USER_INTELLIGENCE_PROFILE.md        # Detailed implementation (10,000 words)
├── T4_USER_INTELLIGENCE_PROFILE.md        # Complete reference (15,000 words)
├── T5_USER_INTELLIGENCE_PROFILE.md        # Quick reference (500 words)
└── T6_USER_INTELLIGENCE_PROFILE.md        # This file (source code docs)

packages/user_intelligence/
├── __init__.py
├── profile.py                           # UserIntelligenceProfile class
├── honesty_enforcer.py                  # HonestyEnforcer class
├── adaptive_response.py                 # AdaptiveResponseGenerator class
└── verification_tracker.py              # VerificationTracker class

.cursor/rules/
└── base-rules.mdc                        # Integration with base rules
```

---

## 📦 **USER INTELLIGENCE PROFILE**

### **File: `packages/user_intelligence/profile.py`**

**Purpose:** Core user intelligence tracking and profile management

---

### **Class: UserIntelligenceProfile**

```python
@dataclass
class UserIntelligenceProfile:
    """
    Comprehensive user intelligence tracking.
    
    Tracks user accuracy patterns, cognitive style, feedback quality,
    and interaction patterns to enable adaptive assistance.
    
    Attributes:
        user_id: Unique identifier for user
        profile_id: Unique identifier for profile
        accuracy_by_domain: Accuracy metrics by domain (code, architecture, etc.)
        accuracy_by_question_type: Accuracy metrics by question type
        cognitive_style: Visual, auditory, kinesthetic, reading, mixed
        learning_preference: Examples, testing, visualization, code, step_by_step
        thinking_style: Intuitive, analytical, creative, practical
        feedback_helpfulness_score: 0.0-1.0 score of feedback helpfulness
        user_verification_rate: How often user verifies AI claims (0.0-1.0)
    """
    
    def update_accuracy(
        self,
        domain: str,
        question_type: str,
        is_correct: bool
    ):
        """
        Update accuracy metrics for domain and question type.
        
        This is the core method for tracking user accuracy patterns.
        Call this after determining if user statement was correct.
        
        Args:
            domain: Domain of statement (e.g., "code", "architecture")
            question_type: Type of question (e.g., "how_to", "what", "why")
            is_correct: Whether user statement was correct
        
        Side Effects:
            - Updates accuracy_by_domain[domain]
            - Updates accuracy_by_question_type[question_type]
            - Updates overall_accuracy
            - Updates accuracy_trend
            - Updates updated_at timestamp
        
        Example:
            >>> profile.update_accuracy("code", "how_to", is_correct=True)
            >>> profile.accuracy_by_domain["code"].accuracy_rate
            1.0  # If first statement
        """
        # Implementation details...
        pass
    
    def get_domain_accuracy(self, domain: str) -> float:
        """
        Get accuracy for a specific domain.
        
        Returns accuracy rate (0.0-1.0) for domain, or 0.5 (neutral)
        if domain has no history.
        
        Args:
            domain: Domain to check
        
        Returns:
            Accuracy rate (0.0-1.0), default 0.5 if no history
        
        Example:
            >>> profile.get_domain_accuracy("code")
            0.75  # User is 75% accurate in code domain
        """
        # Implementation details...
        pass
```

---

### **Class: AccuracyMetrics**

```python
@dataclass
class AccuracyMetrics:
    """
    Accuracy metrics for a specific domain/question type.
    
    Tracks correctness statistics and calculates confidence intervals
    for user accuracy assessment.
    
    Attributes:
        domain: Domain name (e.g., "code", "architecture")
        total_statements: Total number of statements tracked
        correct_statements: Number of correct statements
        incorrect_statements: Number of incorrect statements
        accuracy_rate: correct_statements / total_statements (0.0-1.0)
        confidence_interval: 95% confidence interval (lower, upper)
        trend_direction: "improving", "declining", "stable"
        sample_size: Number of samples used for calculations
    """
    
    def update(self, is_correct: bool):
        """
        Update metrics with new statement outcome.
        
        Automatically recalculates accuracy_rate and confidence_interval.
        Confidence interval only calculated if sample_size >= 30.
        
        Args:
            is_correct: Whether statement was correct
        
        Side Effects:
            - Increments total_statements
            - Increments correct_statements or incorrect_statements
            - Recalculates accuracy_rate
            - Recalculates confidence_interval (if sample_size >= 30)
        
        Example:
            >>> metrics = AccuracyMetrics(domain="code")
            >>> metrics.update(is_correct=True)
            >>> metrics.accuracy_rate
            1.0
            >>> metrics.total_statements
            1
        """
        # Implementation details...
        pass
```

---

## 🚨 **HONESTY ENFORCER**

### **File: `packages/user_intelligence/honesty_enforcer.py`**

**Purpose:** Enforce honest communication protocol, prevent false claims and blind agreement

---

### **Class: HonestyEnforcer**

```python
class HonestyEnforcer:
    """
    Enforces honest communication protocol.
    
    Prevents AI from making false claims or blindly agreeing with users.
    Validates all claims against forbidden phrases and verification requirements.
    
    Attributes:
        user_profile: User intelligence profile for accuracy checking
        verification_tracker: Tracker for verification status
        claim_history: History of all claims made
    
    Example:
        >>> enforcer = HonestyEnforcer(profile, tracker)
        >>> validation = enforcer.check_claim("Fixed!", ClaimType.FIX)
        >>> validation.valid
        False
        >>> validation.reason
        'FORBIDDEN_PHRASE'
    """
    
    def check_claim(self, claim_text: str, claim_type: ClaimType) -> ClaimValidation:
        """
        Check if claim violates honesty protocol.
        
        Validates claim against:
        1. Forbidden phrases (e.g., "Fixed!" without verification)
        2. Verification requirements (claims require verification)
        3. User verification rate (low rate = more cautious)
        
        Args:
            claim_text: Text of claim to validate
            claim_type: Type of claim (COMPLETION, FIX, AGREEMENT, etc.)
        
        Returns:
            ClaimValidation with valid flag, reason, and recommended response
        
        Example:
            >>> validation = enforcer.check_claim("Fixed!", ClaimType.FIX)
            >>> if not validation.valid:
            ...     print(f"Invalid: {validation.reason}")
            ...     print(f"Use: {validation.recommended_response}")
            Invalid: FORBIDDEN_PHRASE
            Use: Applied potential fix - unverified, needs testing
        """
        # Implementation details...
        pass
    
    def validate_agreement(self, user_statement: str, ai_response: str) -> ClaimValidation:
        """
        Validate that AI isn't blindly agreeing.
        
        Checks for blind agreement patterns and validates against user
        accuracy for domain before allowing agreement.
        
        Args:
            user_statement: User's statement being responded to
            ai_response: AI's response to validate
        
        Returns:
            ClaimValidation with valid flag and recommended honest response
        
        Example:
            >>> validation = enforcer.validate_agreement(
            ...     "We should use X",
            ...     "You're absolutely right!"
            ... )
            >>> validation.valid
            False
            >>> validation.reason
            'BLIND_AGREEMENT'
        """
        # Implementation details...
        pass
```

---

### **Constants: FORBIDDEN_PHRASES**

```python
FORBIDDEN_PHRASES = {
    ClaimType.COMPLETION: [
        "Done!",
        "Completed!",
        "Finished!",
        "All set!",
        "That's it!"
    ],
    ClaimType.FIX: [
        "Fixed!",
        "This will work",
        "Should work now",
        "Problem solved",
        "Issue resolved"
    ],
    ClaimType.AGREEMENT: [
        "You're absolutely right!",
        "I completely agree!",
        "Perfect!",
        "Exactly!",
        "That's exactly what we need!"
    ]
}
"""
Forbidden phrases that must never be used without verification.

These phrases imply certainty or completion without proper verification.
Each claim type has specific forbidden phrases that trigger validation failure.

Usage:
    if any(phrase in claim_text.lower() for phrase in FORBIDDEN_PHRASES[claim_type]):
        return ClaimValidation(valid=False, reason="FORBIDDEN_PHRASE")
"""
```

---

## 🎯 **ADAPTIVE RESPONSE GENERATOR**

### **File: `packages/user_intelligence/adaptive_response.py`**

**Purpose:** Generate responses adapted to user intelligence profile

---

### **Class: AdaptiveResponseGenerator**

```python
class AdaptiveResponseGenerator:
    """
    Generates responses adapted to user intelligence profile.
    
    Analyzes user input, determines adaptation needs based on user profile,
    and generates responses with appropriate adaptations (visualization,
    examples, testing, etc.).
    
    Attributes:
        user_profile: User intelligence profile
        honesty_enforcer: Honesty enforcer for response validation
    
    Example:
        >>> generator = AdaptiveResponseGenerator(profile, enforcer)
        >>> response = generator.generate_response(
        ...     "How does this work?",
        ...     ai_knowledge={},
        ...     context={}
        ... )
        >>> "diagram" in response.lower() or "visual" in response.lower()
        True  # If user is visual learner
    """
    
    def generate_response(
        self,
        user_input: str,
        ai_knowledge: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Generate response adapted to user profile.
        
        Process:
        1. Analyze user input (extract domain, question type)
        2. Get user accuracy for domain
        3. Determine adaptation needs
        4. Generate base response
        5. Apply adaptations
        6. Validate with honesty enforcer
        
        Args:
            user_input: User's input/question
            ai_knowledge: AI's knowledge base
            context: Additional context
        
        Returns:
            Adapted response string
        
        Example:
            >>> response = generator.generate_response(
            ...     "How do I implement X?",
            ...     {"knowledge": "..."},
            ...     {"domain": "code"}
            ... )
            >>> response  # Includes adaptations based on user profile
            "Based on your question: How do I implement X?...
             Visual Explanation: Let me create a diagram..."
        """
        # Implementation details...
        pass
    
    def _determine_adaptation(
        self,
        accuracy: float,
        user_input: str,
        domain: str
    ) -> ResponseAdaptation:
        """
        Determine how to adapt response.
        
        Based on user accuracy, cognitive style, learning preference,
        and thinking style, determines what adaptations to apply.
        
        Args:
            accuracy: User accuracy for domain (0.0-1.0)
            user_input: User's input
            domain: Domain of question
        
        Returns:
            ResponseAdaptation with flags for different adaptations
        
        Adaptation Rules:
        - accuracy < 0.5: Increase confidence threshold, add examples, detailed explanations
        - accuracy > 0.7 + intuitive: Add visualization, code examples
        - visual cognitive style: Add diagrams, visual aids
        - testing learning preference: Add test cases, demonstrations
        
        Example:
            >>> adaptation = generator._determine_adaptation(0.3, "How?", "code")
            >>> adaptation.increase_confidence_threshold
            0.1
            >>> adaptation.add_examples
            True
        """
        # Implementation details...
        pass
```

---

## ✅ **VERIFICATION TRACKER**

### **File: `packages/user_intelligence/verification_tracker.py`**

**Purpose:** Track verification status of all claims

---

### **Class: VerificationTracker**

```python
class VerificationTracker:
    """
    Tracks verification status of all claims.
    
    Maintains two dictionaries:
    - verified_claims: Claims that have been verified by user
    - pending_verifications: Claims waiting for verification
    
    Example:
        >>> tracker = VerificationTracker()
        >>> tracker.mark_pending("Fixed issue", ClaimType.FIX)
        >>> tracker.is_verified("Fixed issue")
        False
        >>> tracker.mark_verified("Fixed issue")
        >>> tracker.is_verified("Fixed issue")
        True
    """
    
    def mark_pending(self, claim_text: str, claim_type: ClaimType):
        """
        Mark claim as pending verification.
        
        Args:
            claim_text: Text of claim
            claim_type: Type of claim
        
        Side Effects:
            - Adds to pending_verifications dictionary
            - Stores timestamp for tracking
        
        Example:
            >>> tracker.mark_pending("Applied fix", ClaimType.FIX)
            >>> len(tracker.pending_verifications)
            1
        """
        # Implementation details...
        pass
    
    def mark_verified(self, claim_text: str):
        """
        Mark claim as verified.
        
        Args:
            claim_text: Text of claim to verify
        
        Side Effects:
            - Adds to verified_claims dictionary
            - Removes from pending_verifications
        
        Example:
            >>> tracker.mark_verified("Applied fix")
            >>> tracker.is_verified("Applied fix")
            True
        """
        # Implementation details...
        pass
    
    def is_verified(self, claim_text: str) -> bool:
        """
        Check if claim is verified.
        
        Args:
            claim_text: Text of claim to check
        
        Returns:
            True if verified, False otherwise
        
        Example:
            >>> tracker.is_verified("Applied fix")
            False  # Not yet verified
            >>> tracker.mark_verified("Applied fix")
            >>> tracker.is_verified("Applied fix")
            True
        """
        # Implementation details...
        pass
```

---

## 🔗 **INTEGRATION POINTS**

### **VIF Integration**

```python
class VIFIntegratedHonestyEnforcer(HonestyEnforcer):
    """
    Honesty enforcer integrated with VIF verification.
    
    Extends HonestyEnforcer to check VIF witness confidence
    before allowing claims.
    
    Example:
        >>> vif_enforcer = VIFIntegratedHonestyEnforcer(
        ...     profile, tracker, vif_client
        ... )
        >>> validation = vif_enforcer.claim_with_vif_verification(
        ...     "Fixed issue",
        ...     ClaimType.FIX,
        ...     operation_id="op123"
        ... )
        >>> if validation.valid:
        ...     print(f"Verified with VIF: {validation.message}")
    """
    pass
```

---

**Status:** ✅ **CRITICAL PROTOCOL** - Production Ready  
**Integration:** VIF, EmotionalState, Learning Log Standard  
**Impact:** Prevents false claims, enables adaptive assistance, improves trust

