# Co-Agency & Trust Layer L2: Architecture

**Detail Level:** 2 of 5 (2,000 words)  
**Context Budget:** ~10,000 tokens  
**Purpose:** Architecture design for Co-Agency

---

## 🏗️ **ARCHITECTURE OVERVIEW**

Co-Agency is a **philosophical framework** that manifests in all AIM-OS systems through:

1. **Transparent Dialogue** - AI explains concerns
2. **Trust Dashboard** - User sees AI's state
3. **Accountable Escalation** - Show why, not just block
4. **Evidence Alignment** - Contradiction detection

## 🔧 **CORE COMPONENTS**

### **1. Disagreement Interface**

```python
@dataclass
class DisagreementStatement:
    """Transparent disagreement from AI"""
    concern: str  # "I'm cautious because..."
    reasoning: List[str]  # Specific reasons
    evidence: Dict  # Supporting evidence
    alternative: Optional[str]  # Suggested alternative
    timestamp: datetime
```

### **2. Trust Dashboard**

```python
@dataclass
class TrustDashboard:
    """Visible trust state for user"""
    identity_confidence: float  # 0-1
    intent_risk_band: str  # Low/Medium/High/Critical
    ethical_tension: float  # 0-1
    evidence_alignment: Dict  # Contradiction info
```

### **3. Escalation Framework**

```python
@dataclass
class EscalationNotice:
    """Accountable escalation"""
    reason: str
    risk_level: str
    options: List[str]
    requires: str  # Admin approval, verification, etc.
```

---

**Next Level:** [L3 Detailed (10kw)](L3_detailed.md)  
**Complete Reference:** [L4 Complete (15kw+)](L4_complete.md)
