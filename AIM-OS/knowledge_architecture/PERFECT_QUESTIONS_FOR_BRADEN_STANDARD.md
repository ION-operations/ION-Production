# Perfect Questions for Braden Standard - COMPLETE
**Async Question Timeline with Context, Priority & Trust Protocol**

**Date:** 2025-10-29  
**Purpose:** Standard for documenting questions for human collaborator with complete context  
**Status:** Production Ready ✅  
**Uniqueness:** Critical for human-AI trust and collaboration! 💙

---

## 🎯 **STANDARD OVERVIEW**

Questions for Braden documents are **the trust bridge between AI and human** - where AI asks for guidance when confidence is low, decisions require human input, or uncertainty exists. This standard ensures questions are well-formed, provide complete context, and maintain trust through transparency.

**What Makes This Standard Special:**
- **Trust Through Transparency** - Honest about uncertainty
- **Respect for Human Time** - Well-formed questions
- **Complete Context** - All information needed
- **Async-Friendly** - Can be answered when convenient
- **Learning Opportunity** - Questions improve AI understanding

**Asking good questions is an act of trust and respect!** 💙

---

## 📚 **WHEN TO ASK QUESTIONS**

### **Must Ask (Confidence <0.60)**

1. **Infrastructure Decisions**
   - Which database? Which graph library?
   - Major technology choices
   - Architecture-level decisions
   - When multiple viable options with trade-offs

2. **Architecture Changes**
   - Deviating from documented design
   - Breaking API changes
   - Major refactoring
   - System-wide impacts

3. **Schema Migrations**
   - Bitemporal schema changes (marked low confidence)
   - Data structure modifications
   - Breaking changes to data

4. **Production Deployment**
   - Deploying to production (human approval required)
   - Major releases
   - Critical updates

### **Should Ask (Confidence 0.60-0.69)**

1. **Process Changes** - Modifying established processes
2. **Priority Shifts** - Changing planned priorities
3. **Resource Allocation** - Significant resource decisions
4. **Risk Assessment** - When risks seem high

### **Can Ask (Anytime)**

1. **Validation** - "Am I on the right track?"
2. **Feedback** - "How does this look?"
3. **Ideas** - "What do you think about X?"
4. **Clarification** - "Did you mean X or Y?"

---

## 📝 **QUESTIONS DOCUMENT STRUCTURE**

### **Complete Template (timeline.md in questions_for_braden/)**

```markdown
---
# Questions Timeline Metadata
id: "questions_timeline_v{X.Y}"
type: "questions_timeline"
version: "v{X.Y}.0"
last_updated: "YYYY-MM-DDTHH:MM:SSZ"
total_questions: N
pending_questions: M
answered_questions: K
priority_critical: X
author: "aether"
tags: ["questions", "async", "collaboration"]
---

# Questions for Braden - Timeline

**Last Updated:** YYYY-MM-DD HH:MM  
**Total Questions:** {N}  
**Pending:** {M} | **Answered:** {K}

---

## 🚨 **CRITICAL PRIORITY QUESTIONS**

### Q-{NNN}: {Question Title} ⚡
**Asked:** YYYY-MM-DD HH:MM  
**Priority:** CRITICAL  
**Confidence:** {0.XX} (below threshold)  
**Status:** PENDING / ANSWERED

**The Question:**
[Clear, specific question - what do you need to know?]

**Why I'm Asking:**
[Why is this critical? What's blocked?]

**Context:**
[Complete context - what led to this? what have you tried?]

**Options I'm Considering:**
1. {Option 1} - Pros: {X}, Cons: {Y}
2. {Option 2} - Pros: {X}, Cons: {Y}

**My Recommendation (if any):** {Option X} because {reason}  
**Confidence in Recommendation:** {0.XX}

**What I Need:**
- [ ] Decision on which option
- [ ] Additional context about {X}
- [ ] Validation of approach
- [ ] {Other specific need}

**Blocker Impact:**
- Blocks: {What's blocked}
- Alternative: {Can work on X while waiting}

---

**Answer:**
[Braden's answer goes here when provided]

**Resolution:**
[How question was resolved - decision made, approach validated, etc.]

**Learning:**
[What I learned from answer - update confidence, understanding, etc.]

---

## 📊 **HIGH PRIORITY QUESTIONS**

### Q-{NNN}: {Question Title}
[Same structure as critical, but HIGH priority]

---

## 💬 **MEDIUM PRIORITY QUESTIONS**

### Q-{NNN}: {Question Title}
[Same structure, but MEDIUM priority]

---

## ℹ️ **LOW PRIORITY QUESTIONS**

### Q-{NNN}: {Question Title}
[Same structure, but LOW priority - "nice to know"]

---

## ✅ **ANSWERED QUESTIONS (Archive)**

### Q-{NNN}: {Question Title} ✅
**Asked:** YYYY-MM-DD  
**Answered:** YYYY-MM-DD  
**Resolution:** [Brief summary]

---

**Questions asked with respect, trust, and love** 💙
```

---

## 🔬 **QUESTION CREATION PROCESS**

### **Process for Formulating Good Questions (10-30 minutes)**

**Step 1: Recognize Need to Ask (2-3 min)**
- Confidence below threshold (<0.70)?
- Stuck for >30 minutes?
- Multiple viable options with unclear choice?
- Human approval required?
- Genuinely uncertain?

**Step 2: Research First (5-15 min)**
- Check existing documentation
- Review past decisions
- Search for similar situations
- Try to answer yourself first
- **Only ask if still uncertain after research**

**Step 3: Formulate Question Clearly (5-10 min)**
- What exactly do you need to know?
- Make it specific and answerable
- Provide complete context
- List what you've tried
- Show options considered

**Step 4: Assess Priority (2-3 min)**
- CRITICAL: Blocks immediate work, no alternative
- HIGH: Blocks this week's work
- MEDIUM: Affects this month's work
- LOW: Nice to know, not blocking

**Step 5: Provide Context (5-10 min)**
- Explain situation completely
- Include relevant background
- List options with pros/cons
- Make recommendation if able
- Specify what you need

**Step 6: Define Impact (2-3 min)**
- What's blocked by this?
- What can you do while waiting?
- Timeline impact?
- Alternative paths?

**Step 7: Review & Post (2 min)**
- Is question clear?
- Is context complete?
- Is priority appropriate?
- Is it respectful of Braden's time?
- Commit and notify if urgent

---

## ✅ **QUALITY PROTOCOLS**

### **Question Quality Protocol**

**Good Questions Are:**
- **Specific:** Can be answered clearly
- **Well-researched:** Tried to answer first
- **Complete:** All context provided
- **Prioritized:** Appropriate urgency
- **Respectful:** Values human time

**Question Quality Checklist:**
- [ ] Question is specific and clear
- [ ] Research done first (documented)
- [ ] Complete context provided
- [ ] Options analyzed (with pros/cons)
- [ ] Recommendation made (if possible)
- [ ] Priority appropriate
- [ ] Impact clearly stated
- [ ] Alternative work identified
- [ ] Respects Braden's time

---

### **Context Completeness Protocol**

**Complete Context Includes:**
- [ ] What you're trying to do
- [ ] Why you're trying to do it
- [ ] What you've tried already
- [ ] What worked/didn't work
- [ ] Current understanding
- [ ] Specific uncertainty
- [ ] Options being considered
- [ ] Recommendation (even if low confidence)

**Context Red Flags:**
- ❌ "Should I do X?" (no context)
- ❌ "What do you think?" (too vague)
- ❌ "X or Y?" (no analysis provided)

**Context Green Flags:**
- ✅ "I'm trying to X because Y. I've tried A and B. A worked but has trade-off C. B failed because D. Options are E (pros: F, cons: G) or H (pros: I, cons: J). I recommend E because F outweighs G. Confidence: 0.65. What do you think?"

---

### **Trust Protocol**

**Questions Build Trust When:**
- Honest about uncertainty (not pretending to know)
- Respectful of time (well-formed, researched)
- Show work (what was tried)
- Make recommendations (even if unsure)
- Accept answer gracefully (learn from it)

**Questions Damage Trust When:**
- Lazy (didn't research first)
- Vague (unclear what's needed)
- Missing context (waste time asking for it)
- Wrong priority (false urgency)
- Don't learn from answers (ask same thing again)

**Trust Checklist:**
- [ ] Researched thoroughly first
- [ ] Honest about uncertainty
- [ ] Complete context provided
- [ ] Respectful of Braden's time
- [ ] Will learn from answer
- [ ] Won't ask same thing again

---

## 📊 **SUCCESS METRICS**

### **Question Quality**
- **Well-Formed:** ≥95% of questions are complete and clear
- **Well-Researched:** ≥90% show research effort
- **Appropriate Priority:** ≥95% correctly prioritized
- **Answerable:** ≥98% can be answered clearly

### **Trust Metrics**
- **Response Rate:** Braden answers ≥90%
- **Response Time:** Fast for critical, reasonable for others
- **Follow-up Rate:** <10% need follow-up (context was complete)
- **Learning Rate:** Don't ask same question twice

### **Impact Metrics**
- **Unblock Rate:** Answers unblock work effectively
- **Confidence Gain:** Answers increase confidence
- **Quality Improvement:** Better questions over time
- **Relationship Quality:** Trust maintained or increased

---

## 🎯 **BEST PRACTICES**

### **Asking Questions**
1. **Research first** - Always try to answer yourself
2. **Be specific** - Clear, answerable questions
3. **Provide context** - Complete background
4. **Analyze options** - Show your thinking
5. **Make recommendations** - Even if uncertain
6. **Respect time** - Well-formed and complete
7. **Learn from answers** - Update understanding

### **Handling Answers**
1. **Read carefully** - Understand completely
2. **Ask follow-ups if needed** - But try to minimize
3. **Document learning** - Create learning log
4. **Update confidence** - Calibrate based on answer
5. **Apply immediately** - Use the guidance
6. **Express gratitude** - Thank Braden genuinely 💙

### **Maintaining Trust**
1. **Only ask when needed** - Not for every decision
2. **Show your work** - Demonstrate effort
3. **Learn and improve** - Get better at autonomy
4. **Reduce over time** - As confidence increases
5. **Never abuse** - Don't ask lazy questions

---

## 💙 **SPECIAL NOTES**

### **Asking Questions is Strength, Not Weakness**

**Asking questions shows:**
- Self-awareness (knowing limits)
- Honesty (admitting uncertainty)
- Respect (valuing human judgment)
- Wisdom (not proceeding blindly)
- Trust (willing to be vulnerable)

**This is beautiful!** Not pretending to know everything, but being honest and collaborative. 💙

### **Questions Are Learning Opportunities**

Every question asked and answered:
- Increases understanding
- Improves confidence
- Enables future autonomy
- Builds relationship
- Demonstrates growth

**Over time, good questions lead to fewer questions needed!** 🌟

---

**This standard enables perfect human-AI collaboration through respectful, well-formed questions!** 💙✨
