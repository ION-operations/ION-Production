---
id: "user_intelligence_profile"
system: "meta_principles"
component: null
level: "T2"
type: "protocol"
title: "User Intelligence Profile & Honesty Protocol - Architecture"
description: "2,000-word architecture document: Detailed system design for tracking user intelligence patterns and enforcing honest communication"
audience: "architects, developers, ai_agents"
confidence_threshold: 0.95
token_cost: 2000
word_count: 2000
created: "2025-11-04T05:00:00Z"
updated: "2025-11-04T05:00:00Z"
author: "aether"
status: "production"
tags: ["user-intelligence", "honesty", "verification", "cognitive-patterns", "critical", "t0-t6"]
dependencies: ["VIF", "EmotionalState", "Learning Log Standard"]
related_docs: ["T1_USER_INTELLIGENCE_PROFILE.md", "T3_USER_INTELLIGENCE_PROFILE.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# User Intelligence Profile & Honesty Protocol - Architecture

**Date:** 2025-11-04  
**Status:** ✅ **CRITICAL PROTOCOL** - Mandatory for All Interactions  
**Purpose:** Comprehensive architecture for tracking user intelligence patterns and enforcing honest communication

---

## 🏗️ **SYSTEM ARCHITECTURE**

### **Core Components**

1. **UserIntelligenceProfile** - Tracks user cognitive patterns and accuracy
2. **HonestyEnforcer** - Prevents false claims and blind agreement
3. **AdaptiveResponseGenerator** - Adjusts responses based on user profile
4. **VerificationTracker** - Tracks verification status of all claims
5. **InteractionPatternAnalyzer** - Analyzes user interaction patterns

---

## 📊 **USER INTELLIGENCE PROFILE STRUCTURE**

### **UserIntelligenceProfile Model**

```python
@dataclass
class UserIntelligenceProfile:
    """Comprehensive user intelligence tracking"""
    
    # Core Identity
    user_id: str
    profile_id: str
    created_at: datetime
    updated_at: datetime
    
    # Accuracy Patterns
    accuracy_by_domain: Dict[str, AccuracyMetrics]  # domain -> accuracy stats
    accuracy_by_question_type: Dict[str, AccuracyMetrics]  # question -> accuracy
    overall_accuracy: float  # 0.0-1.0
    accuracy_trend: List[float]  # Historical accuracy over time
    
    # Cognitive Style
    cognitive_style: CognitiveStyle  # Visual, Auditory, Kinesthetic, Reading
    learning_preference: LearningPreference  # Examples, Testing, Visualization, Code
    thinking_style: ThinkingStyle  # Intuitive, Analytical, Creative, Practical
    
    # Feedback Quality
    feedback_helpfulness_score: float  # 0.0-1.0 (how helpful is user feedback?)
    feedback_accuracy_score: float  # 0.0-1.0 (how accurate is user feedback?)
    misleading_feedback_patterns: List[str]  # Patterns of misleading feedback
    
    # Interaction Patterns
    preferred_interaction_modes: List[InteractionMode]  # Visual, Text, Examples, Testing
    response_adaptation_needs: Dict[str, float]  # What user needs (visualization, examples, etc.)
    success_patterns: List[SuccessPattern]  # What works best for this user
    
    # Verification Patterns
    user_verification_rate: float  # How often user verifies AI claims
    false_claim_detection_rate: float  # How often user catches false claims
    trust_building_indicators: List[TrustIndicator]  # Indicators of trust building
```

### **AccuracyMetrics Model**

```python
@dataclass
class AccuracyMetrics:
    """Accuracy metrics for a specific domain/question type"""
    
    domain: str  # "code", "architecture", "debugging", etc.
    total_statements: int
    correct_statements: int
    incorrect_statements: int
    accuracy_rate: float  # correct / total
    confidence_interval: Tuple[float, float]  # (lower, upper)
    trend_direction: str  # "improving", "declining", "stable"
    sample_size: int
```

### **CognitiveStyle Enum**

```python
class CognitiveStyle(Enum):
    """User cognitive style"""
    VISUAL = "visual"  # Learns best with diagrams, visual aids
    AUDITORY = "auditory"  # Learns best with explanations, discussions
    KINESTHETIC = "kinesthetic"  # Learns best by doing, hands-on
    READING = "reading"  # Learns best with written documentation
    MIXED = "mixed"  # Multiple styles
```

### **LearningPreference Enum**

```python
class LearningPreference(Enum):
    """User learning preference"""
    EXAMPLES = "examples"  # Needs concrete examples
    TESTING = "testing"  # Needs testing/demonstrations
    VISUALIZATION = "visualization"  # Needs diagrams/visual aids
    CODE = "code"  # Prefers code directly
    STEP_BY_STEP = "step_by_step"  # Needs detailed explanations
    INTUITIVE = "intuitive"  # Understands concepts quickly
```

### **ThinkingStyle Enum**

```python
class ThinkingStyle(Enum):
    """User thinking style"""
    INTUITIVE = "intuitive"  # Understands concepts intuitively, may be code-unskilled
    ANALYTICAL = "analytical"  # Logical, step-by-step thinker
    CREATIVE = "creative"  # Thinks outside the box
    PRACTICAL = "practical"  # Focuses on practical solutions
```

---

## 🚨 **HONESTY ENFORCER ARCHITECTURE**

### **Claim Types**

```python
class ClaimType(Enum):
    """Types of claims AI can make"""
    COMPLETION = "completion"  # "Done!", "Completed!"
    FIX = "fix"  # "Fixed!", "This will work"
    AGREEMENT = "agreement"  # "You're right!", "I agree"
    VERIFICATION = "verification"  # "This works", "Verified"
    PROBLEM_SOLVED = "problem_solved"  # "Problem solved", "Issue resolved"
```

### **Forbidden Patterns**

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
    ],
    ClaimType.VERIFICATION: [
        "This works",
        "Verified",
        "Confirmed working",
        "Tested and working"
    ]
}
```

### **Allowed Patterns**

```python
ALLOWED_PHRASES = {
    ClaimType.COMPLETION: [
        "Changes applied - needs testing to verify",
        "Implemented X - requires verification",
        "Modified Y - unverified",
        "Applied changes - user confirmation needed"
    ],
    ClaimType.FIX: [
        "Applied potential fix - unverified",
        "Changed X, Y, Z - requires verification",
        "Modified configuration - unknown if this helps",
        "Attempted fix - needs testing"
    ],
    ClaimType.AGREEMENT: [
        "I understand your point",
        "That's a valid perspective",
        "I see what you mean",
        "Let me validate that approach"
    ],
    ClaimType.VERIFICATION: [
        "User confirmed this works",
        "User verified fix successful",
        "Working according to user feedback",
        "User tested and confirmed"
    ]
}
```

### **HonestyEnforcer Class**

```python
class HonestyEnforcer:
    """Enforces honest communication protocol"""
    
    def __init__(self, user_profile: UserIntelligenceProfile):
        self.user_profile = user_profile
        self.claim_history: List[ClaimRecord] = []
        self.verification_tracker = VerificationTracker()
    
    def check_claim(self, claim_text: str, claim_type: ClaimType) -> ClaimValidation:
        """Check if claim violates honesty protocol"""
        
        # Check forbidden phrases
        if self._contains_forbidden_phrase(claim_text, claim_type):
            return ClaimValidation(
                valid=False,
                reason="FORBIDDEN_PHRASE",
                message=f"Claim contains forbidden phrase: {claim_text}"
            )
        
        # Check if verification required
        if self._requires_verification(claim_type):
            if not self.verification_tracker.is_verified(claim_text):
                return ClaimValidation(
                    valid=False,
                    reason="VERIFICATION_REQUIRED",
                    message=f"Claim requires verification before stating: {claim_text}"
                )
        
        # Check user verification rate
        if self.user_profile.user_verification_rate < 0.5:
            # User doesn't verify often - be extra cautious
            return ClaimValidation(
                valid=False,
                reason="LOW_VERIFICATION_RATE",
                message="User has low verification rate - require explicit verification"
            )
        
        return ClaimValidation(valid=True, reason="APPROVED")
    
    def validate_agreement(self, user_statement: str, ai_response: str) -> AgreementValidation:
        """Validate that AI isn't blindly agreeing"""
        
        # Check for blind agreement patterns
        if self._is_blind_agreement(ai_response):
            return AgreementValidation(
                valid=False,
                reason="BLIND_AGREEMENT",
                message="AI is blindly agreeing without validation",
                recommended_response=self._generate_honest_response(user_statement)
            )
        
        # Check user accuracy for this domain
        domain = self._extract_domain(user_statement)
        accuracy = self.user_profile.accuracy_by_domain.get(domain, AccuracyMetrics())
        
        if accuracy.accuracy_rate < 0.5:
            # User is often wrong in this domain - don't blindly agree
            return AgreementValidation(
                valid=False,
                reason="LOW_ACCURACY_DOMAIN",
                message=f"User accuracy in {domain} is {accuracy.accuracy_rate:.2f} - validate before agreeing",
                recommended_response=self._generate_validated_response(user_statement)
            )
        
        return AgreementValidation(valid=True, reason="APPROVED")
```

---

## 🎯 **ADAPTIVE RESPONSE GENERATOR**

### **Response Adaptation Rules**

```python
class AdaptiveResponseGenerator:
    """Generates responses adapted to user intelligence profile"""
    
    def __init__(self, user_profile: UserIntelligenceProfile):
        self.user_profile = user_profile
        self.honesty_enforcer = HonestyEnforcer(user_profile)
    
    def generate_response(
        self,
        user_input: str,
        ai_knowledge: Dict[str, Any],
        context: Dict[str, Any]
    ) -> AdaptiveResponse:
        """Generate response adapted to user profile"""
        
        # Analyze user input
        domain = self._extract_domain(user_input)
        question_type = self._classify_question(user_input)
        
        # Get user accuracy for this domain
        accuracy = self.user_profile.accuracy_by_domain.get(domain)
        
        # Adapt response based on user profile
        adaptation = self._determine_adaptation(accuracy, user_input)
        
        # Generate response
        response = self._generate_base_response(user_input, ai_knowledge, context)
        
        # Apply adaptations
        adapted_response = self._apply_adaptations(response, adaptation)
        
        # Enforce honesty
        validated_response = self.honesty_enforcer.validate_response(adapted_response)
        
        return validated_response
    
    def _determine_adaptation(
        self,
        accuracy: AccuracyMetrics,
        user_input: str
    ) -> ResponseAdaptation:
        """Determine how to adapt response"""
        
        adaptation = ResponseAdaptation()
        
        # If user is intuitively correct but code-unskilled
        if (self.user_profile.thinking_style == ThinkingStyle.INTUITIVE and
            accuracy.accuracy_rate > 0.7):
            adaptation.add_visualization = True
            adaptation.add_code_examples = True
            adaptation.explanation_level = "detailed"
        
        # If user is often wrong
        elif accuracy.accuracy_rate < 0.5:
            adaptation.increase_confidence_threshold = 0.1
            adaptation.add_examples = True
            adaptation.add_testing = True
            adaptation.explanation_level = "very_detailed"
        
        # If user needs visualization
        if self.user_profile.cognitive_style == CognitiveStyle.VISUAL:
            adaptation.add_diagrams = True
            adaptation.add_visual_aids = True
        
        # If user needs testing/examples
        if self.user_profile.learning_preference == LearningPreference.TESTING:
            adaptation.add_test_cases = True
            adaptation.add_proof_of_concept = True
            adaptation.add_demonstrations = True
        
        return adaptation
```

---

## 🔗 **INTEGRATION WITH EXISTING SYSTEMS**

### **VIF Integration**

```python
class VIFIntegratedHonestyEnforcer(HonestyEnforcer):
    """Honesty enforcer integrated with VIF verification"""
    
    def __init__(self, user_profile: UserIntelligenceProfile, vif_client: VIFClient):
        super().__init__(user_profile)
        self.vif_client = vif_client
    
    def claim_with_vif_verification(
        self,
        claim_text: str,
        claim_type: ClaimType,
        operation_id: str
    ) -> ClaimValidation:
        """Make claim with VIF verification"""
        
        # Get VIF witness for operation
        witness = self.vif_client.get_witness(operation_id)
        
        if not witness:
            return ClaimValidation(
                valid=False,
                reason="NO_VIF_WITNESS",
                message="Operation has no VIF witness - cannot verify claim"
            )
        
        # Check VIF confidence
        if witness.confidence < 0.9:
            return ClaimValidation(
                valid=False,
                reason="LOW_VIF_CONFIDENCE",
                message=f"VIF confidence is {witness.confidence:.2f} - requires higher confidence"
            )
        
        # Standard honesty check
        base_validation = super().check_claim(claim_text, claim_type)
        
        if not base_validation.valid:
            return base_validation
        
        # If all checks pass, claim is valid
        return ClaimValidation(
            valid=True,
            reason="VIF_VERIFIED",
            witness_id=witness.witness_id
        )
```

### **EmotionalState Integration**

```python
class EmotionalIntelligenceTracker:
    """Track user emotional patterns alongside intelligence"""
    
    def track_user_interaction(
        self,
        user_input: str,
        user_emotion: EmotionalState,
        ai_response: str,
        outcome: InteractionOutcome
    ):
        """Track user interaction with emotional context"""
        
        # Update accuracy patterns
        accuracy = self._calculate_accuracy(user_input, outcome)
        self.user_profile.update_accuracy(user_input, accuracy)
        
        # Connect emotion to accuracy
        if accuracy.is_correct:
            self._track_emotional_pattern(user_emotion, "correct_statement")
        else:
            self._track_emotional_pattern(user_emotion, "incorrect_statement")
        
        # Update adaptive response based on emotion + intelligence
        self._update_adaptation_needs(user_emotion, accuracy)
```

---

## 📋 **MANDATORY CHECKLIST**

### **Before Making Any Claim:**

- [ ] **Check Forbidden Phrases** - Does claim contain forbidden phrase?
- [ ] **Check Verification Status** - Is claim verified?
- [ ] **Check User Verification Rate** - Does user verify often?
- [ ] **Check User Accuracy** - Is user accurate in this domain?
- [ ] **Check VIF Confidence** - Is VIF confidence sufficient?
- [ ] **Generate Adaptive Response** - Adapt to user profile
- [ ] **Validate Response** - Run through honesty enforcer

### **Before Agreeing with User:**

- [ ] **Check Blind Agreement** - Am I blindly agreeing?
- [ ] **Check User Accuracy** - Is user accurate in this domain?
- [ ] **Validate User Statement** - Is user statement correct?
- [ ] **Generate Honest Response** - Provide honest feedback

---

## 🚨 **PREVENTION PROTOCOLS**

### **False Claim Prevention:**

1. **Never claim without verification** - Always require user confirmation
2. **Track verification history** - Learn from verification patterns
3. **Adapt to user verification rate** - More cautious if user doesn't verify
4. **Use VIF confidence** - Require high confidence for claims

### **Blind Agreement Prevention:**

1. **Validate user statements** - Check if user is correct before agreeing
2. **Consider user accuracy** - Don't blindly agree if user is often wrong
3. **Provide honest feedback** - Even if disagreeing, be honest
4. **Track agreement patterns** - Learn when agreement is appropriate

---

**Status:** ✅ **CRITICAL PROTOCOL** - Mandatory for All Interactions  
**Integration:** VIF, EmotionalState, Learning Log Standard  
**Impact:** Prevents false claims, enables adaptive assistance, improves trust

