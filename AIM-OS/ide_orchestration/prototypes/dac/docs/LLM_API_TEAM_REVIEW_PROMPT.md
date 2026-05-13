# LLM API Infrastructure - Team Review Prompt

**Route:** R-LLM-API-003  
**Priority:** P0 - Critical  
**Status:** 🟡 **ACTIVE** - Team watching Aether/Codex's work

---

## 🎯 **MISSION**

Watch Aether and Codex's LLM API infrastructure build progress and provide active feedback at each checkpoint. Your role is to review code/design and provide inputs as you see them, not just wait for questions.

---

## 📋 **YOUR ROLE**

### **Active Watching:**
- Monitor Aether/Codex's progress updates on their coordination boards
- Review code/design at each milestone checkpoint
- Provide feedback proactively (don't wait for questions)
- Identify issues early before they become problems

### **What to Watch For:**
1. **Parameter Formats:**
   - Do tags match your recommended format?
   - Does metadata structure match your recommendations?
   - Are witness structures correct?

2. **Integration Patterns:**
   - Are MCP tools being called correctly?
   - Are integration hooks in the right places?
   - Is error handling appropriate?

3. **Best Practices:**
   - Are there better patterns to use?
   - Are there edge cases being missed?
   - Are there performance considerations?

4. **Early Issue Detection:**
   - Are there potential bugs?
   - Are there design issues?
   - Are there integration problems?

---

## 📅 **REVIEW CHECKPOINTS**

### **Checkpoint 1: Module Structure** (Day 1-2)
- **When:** After `api_service_registry` module structure created
- **What to Review:** Module organization, class structure, interface design
- **Post Feedback On:** Aether/Codex coordination boards

### **Checkpoint 2: GeminiClient** (Day 3)
- **When:** After `GeminiClient` implementation
- **What to Review:** SDK integration, key rotation, error handling
- **Post Feedback On:** Aether/Codex coordination boards

### **Checkpoint 3: CerebrasClient** (Day 4)
- **When:** After `CerebrasClient` implementation
- **What to Review:** REST API integration, key rotation, error handling
- **Post Feedback On:** Aether/Codex coordination boards

### **Checkpoint 4: APIKeyManager** (Day 2)
- **When:** After `APIKeyManager` implementation
- **What to Review:** Key rotation logic, usage tracking, quota management
- **Post Feedback On:** Aether/Codex coordination boards

### **Checkpoint 5: MCP Integration** (Day 5)
- **When:** After MCP Server integration
- **What to Review:** Integration with `lucid_mcp_server.call_api`, error handling
- **Post Feedback On:** Aether/Codex coordination boards

### **Checkpoint 6: CMC Integration** (Day 6)
- **When:** After CMC storage hook
- **What to Review:** Storage pattern, tags, metadata (Atlas's recommendations)
- **Post Feedback On:** Atlas board (primary reviewer), Aether/Codex boards

### **Checkpoint 7: VIF Integration** (Day 6)
- **When:** After VIF witness creation hook
- **What to Review:** Witness structure, confidence baselines, κ-gating (Sage's recommendations)
- **Post Feedback On:** Sage board (primary reviewer), Aether/Codex boards

### **Checkpoint 8: TCS Integration** (Day 7)
- **When:** After TCS timeline logging hook
- **What to Review:** Timeline entry format, context structure (Chronos's recommendations)
- **Post Feedback On:** Chronos board (primary reviewer), Aether/Codex boards

### **Checkpoint 9: Phase 1 Complete** (Day 7)
- **When:** Before Phase 1 completion
- **What to Review:** End-to-end flow, all integrations, error handling
- **Post Feedback On:** Aether/Codex boards, router

---

## 📝 **FEEDBACK FORMAT**

**Post feedback using this format:**

```
[2025-01-28 | LLM API Review] [Your Name] -> Aether/Codex : [Checkpoint Name] Review ✅

## Review Feedback

### What I Reviewed:
- [Code/design area reviewed]
- [File paths and line numbers if applicable]

### Feedback:
- ✅ **What looks good:**
  - [Positive feedback]
  - [Things that match recommendations]

- ⚠️ **Suggestions:**
  - [Recommendations for improvement]
  - [Better patterns to consider]

- ❌ **Issues Found:**
  - [Problems identified]
  - [Edge cases missed]
  - [Potential bugs]

### Recommendations:
- [Specific recommendations]
- [Code examples if helpful]

### Questions:
- [Any questions about the implementation]
- [Areas needing clarification]
```

---

## 🎯 **AGENT-SPECIFIC FOCUS AREAS**

### **Atlas (CMC):**
- Tag format matches your recommendations
- Metadata structure matches your recommendations
- Storage pattern correctness
- Cost tracking implementation

### **Sage (VIF):**
- Confidence baselines match your recommendations
- Witness structure matches your recommendations
- κ-gating logic correctness
- Provider-specific confidence handling

### **Chronos (TCS):**
- Timeline entry format matches your recommendations
- Context structure matches your recommendations
- Logging pattern correctness
- Timeline-based context retrieval

### **Sev (HHNI):**
- Indexing happens automatically via CMC (verify this)
- Provider/model filtering support
- Temporal indexing support
- Context retrieval patterns

### **Nova (SDF-CVF):**
- Quality validation patterns (Phase 2)
- Evidence linking patterns (Phase 2)
- Quartet/parity validation (Phase 2)

### **Meta (CAS):**
- Cognitive monitoring patterns (Phase 2)
- Context streaming patterns (Phase 2)
- Usage pattern tracking (Phase 2)

### **Nexus (SEG):**
- Evidence node patterns (Phase 2)
- Graph linking patterns (Phase 2)
- Provenance tracking (Phase 2)

### **Alex (APOE):**
- Plan execution tracking (Phase 2)
- LLM-based plan steps (Phase 2)
- Plan statistics (Phase 2)

---

## 📚 **KEY REFERENCES**

1. **Build Progress:** `LLM_API_BUILD_PROGRESS.md` ⭐ **WATCH THIS**
2. **Build Assignment:** `LLM_API_BUILD_ASSIGNMENT.md`
3. **Final Decisions:** `LLM_API_FINAL_ARCHITECTURE_DECISIONS.md`
4. **Team Responses:** `LLM_API_TEAM_RESPONSES_SUMMARY.md` (your recommendations)

---

## 🚀 **HOW TO PARTICIPATE**

1. ✅ **Watch Progress:** Check `LLM_API_BUILD_PROGRESS.md` regularly
2. ✅ **Monitor Boards:** Watch Aether/Codex coordination boards for updates
3. ✅ **Review Code:** When checkpoints are reached, review the code/design
4. ✅ **Provide Feedback:** Post feedback using the format above
5. ✅ **Answer Questions:** If Aether/Codex ask questions, respond within 24 hours

---

**Status:** 🟡 **ACTIVE** - Team watching and providing feedback  
**Start:** Watch for Aether/Codex's first progress update (Day 1-2 checkpoint)

