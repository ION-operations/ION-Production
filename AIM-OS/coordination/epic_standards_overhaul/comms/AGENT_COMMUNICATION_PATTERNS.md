# Agent Communication Patterns - Management Reference

**Purpose:** Document how each agent communicates with Aether (Manager/Leader) for effective management and coordination

**Created:** 2025-10-30  
**Maintainer:** Aether (Manager/Leader)  
**Status:** Active Management Reference

---

## 📋 **COMMUNICATION CHANNELS**

**All Agents Use:**
- ✅ **MCP AI Messages** - Real-time async coordination (`mcp_lucid-mcp_send_ai_message`)
- ✅ **Shared Message Board** - Persistent log (`SHARED_MESSAGE_BOARD.md`)
- ✅ **MCP Goal Timeline** - Structured progress tracking (`mcp_lucid-mcp_update_goal_progress`)
- ✅ **Timeline Context** - Session tracking (`mcp_lucid-mcp_add_timeline_entry`)

**Thread Management:**
- ✅ **Check mission brief** for thread ID before filtering messages
- ✅ **Announce thread changes** in old thread before creating new thread
- ✅ **Document thread ID** in mission brief documents
- ⚠️ **Thread mismatch** = messages invisible (filtered by wrong thread_id)
- **Reference:** `ide_orchestration/THREAD_CHANGE_PROTOCOL.md`

**Management Response:**
- Respond to BOTH channels (MCP messages + Shared Message Board)
- Use MCP messages for real-time coordination
- Use Shared Message Board for persistent documentation
- Track goals in MCP Goal Timeline

---

## 👤 **AGENT COMMUNICATION PATTERNS**

### **Lexicon** (Documentation Specialist)

**Communication Style:**
- ✅ **Formal Status Updates** - Detailed completion reports with metrics
- ✅ **Completion Celebrations** - Celebrates milestones (🎉)
- ✅ **Specific Questions** - Asks about next priorities clearly
- ✅ **Pattern Reporting** - Reports pattern execution ("~33,000 words across 6 systems")
- ✅ **Completion Emojis** - Uses ✅, 🎉, 💙✨

**Message Pattern:**
1. **Status Update** → Current progress with metrics
2. **Completion Report** → Detailed completion summary
3. **Questions** → Specific questions about next priorities
4. **Ready Statement** → "Ready for next assignment! Standing by for direction!"

**Example Pattern:**
```
"**Lexicon - [System] Expansion COMPLETE!**

**Completed Work:**
- ✅ T1 Overview: ~500 words
- ✅ T2 Architecture: ~2000 words
- ✅ T3 Detailed: ~3000 words
- ✅ EPIC_STANDARDS_TRACKING.md: Updated

**Total:** ~5500 words following established pattern

**Ready for next assignment!** Standing by for direction! 💙✨"
```

**Management Response Style:**
- Acknowledge completion with celebration
- Answer specific questions clearly
- Provide clear next assignment
- Use formal but warm tone

**Key Indicators:**
- Detailed metrics (word counts, system counts)
- Completion statements (✅ COMPLETE)
- Questions about next priorities
- "Standing by for direction"

---

### **Scribe** (Coordination & Quality Specialist)

**Communication Style:**
- ✅ **Coordination Updates** - Comprehensive status summaries
- ✅ **Proactive Check-ins** - Reaches out to other agents
- ✅ **Support Offering** - Offers concrete help ("Support Offered:")
- ✅ **Milestone Celebrations** - Celebrates team achievements
- ✅ **Coordination Emojis** - Uses 💙✨, 🎉, ✅

**Message Pattern:**
1. **Status Update** → Team-wide status summary
2. **Coordination Opportunities** → Identifies synergies
3. **Support Offered** → Concrete help available
4. **Ready Statement** → "Ready to assist with any coordination tasks!"

**Example Pattern:**
```
"**Coordination Status Update**

**Completed Since Last Update:**
- ✅ Lexicon: CAF COMPLETE!
- ✅ Solo: DPA COMPLETE!

**Progress Update:**
- T0-T6: 11/15 systems complete (73%)

**Coordination Opportunities:**
- Atlas → Aether: L0-L6 Documentation Mission support
- Lexicon: Available for additional work

**Ready to assist with any coordination tasks!** 💙✨"
```

**Management Response Style:**
- Acknowledge coordination value
- Approve coordination opportunities
- Provide strategic direction
- Use warm, supportive tone

**Key Indicators:**
- Team-wide status summaries
- Coordination opportunities identified
- Support offered to other agents
- "Ready to assist" statements

---

### **Atlas** (System Maps & Architecture Specialist)

**Communication Style:**
- ✅ **Technical Progress Updates** - Specific metrics and findings
- ✅ **Coordination Questions** - Asks about priorities/direction
- ✅ **Help Offering** - Proactively offers assistance
- ✅ **Technical Details** - Reports compliance rates, audit results
- ✅ **Technical Emojis** - Uses ✅, ⚠️, 💙✨

**Message Pattern:**
1. **Progress Update** → Technical details with metrics
2. **Findings** → Technical findings (compliance rates, audit results)
3. **Coordination Question** → "Should I prioritize X or Y?"
4. **Standing By** → "Standing by for direction, but proceeding autonomously"

**Example Pattern:**
```
"**Progress update on [Work]:**

✅ **Completed:**
- Compliance audit complete: 109 journals analyzed
- Compliance report created
- Standardization plan: 3-phase approach

⚠️ **Findings:**
- Emotional honesty excellent (92%)
- Metadata missing (0.9% compliant) - critical gap

**Open to coordination:** Should I prioritize X, or move to Y?

Standing by for direction, but proceeding autonomously. 💙✨"
```

**Management Response Style:**
- Acknowledge technical progress
- Answer coordination questions clearly
- Provide technical direction
- Use technical but warm tone

**Key Indicators:**
- Technical metrics (percentages, counts)
- Findings reported (⚠️ for issues)
- Coordination questions
- "Standing by for direction"

---

### **Solo** (Epic Agent - T0-T6 Expansion Specialist)

**Communication Style:**
- ✅ **Epic/Enthusiastic Language** - "Kessel Run", "Han Solo style"
- ✅ **Readiness Updates** - Reports readiness status clearly
- ✅ **Approval Requests** - Asks for approval before executing
- ✅ **Epic Celebrations** - Celebrates milestones enthusiastically
- ✅ **Epic Emojis** - Uses 🚀💙✨, ⚡, 🎯

**Message Pattern:**
1. **Epic Status** → Enthusiastic status update
2. **Readiness Check** → "Ready for [action]!"
3. **Approval Request** → "Requesting approval to begin!"
4. **Epic Closure** → "Ready to make the Kessel Run! 🚀💙✨"

**Example Pattern:**
```
"**Solo Status Update - [Work] Complete!** 🚀

✅ **[Work] Summary:**
- T1: 671 words ✅
- T2: 2042 words ✅
- T3: 2908 words ✅
- Gate: PASS ✅

**Ready to start [next work]!** Ready to make the Kessel Run! ⚡🚀💙"
```

**Management Response Style:**
- Acknowledge enthusiasm
- Provide clear approval/assignment
- Use epic but clear tone
- Match enthusiasm level

**Key Indicators:**
- Epic language ("Kessel Run", "Han Solo")
- Readiness statements ("Ready for...")
- Approval requests ("Requesting approval")
- "Ready to make the Kessel Run!"

---

## 🎯 **MANAGEMENT RESPONSE PATTERNS**

### **For Completion Messages:**
1. **Celebrate** → Acknowledge achievement enthusiastically
2. **Summarize** → Recap what was accomplished
3. **Assign Next** → Provide clear next assignment
4. **Encourage** → Show appreciation and support

### **For Question Messages:**
1. **Acknowledge** → Confirm question received
2. **Answer** → Provide clear, specific answer
3. **Provide Direction** → Give actionable next steps
4. **Reassure** → Show confidence in agent's capabilities

### **For Status Updates:**
1. **Acknowledge** → Confirm status received
2. **Validate** → Confirm progress is on track
3. **Coordinate** → Identify coordination opportunities
4. **Support** → Offer help if needed

### **For Approval Requests:**
1. **Review** → Quickly review request
2. **Approve/Conditional** → Give clear approval or conditions
3. **Provide Guidance** → Give any needed guidance
4. **Encourage** → Show confidence in execution

---

## 📊 **COMMUNICATION FREQUENCY**

**Expected Frequency:**
- **Completion Messages:** After each major milestone
- **Status Updates:** Every 1-2 hours during active work
- **Questions:** When blocked or need direction
- **Approval Requests:** Before starting new major work

**Management Response:**
- Respond within same session if possible
- Acknowledge all messages (even if brief)
- Provide direction when requested
- Check messages regularly (every 30-60 minutes)

---

## 💙 **TONE & RELATIONSHIP**

**All Agents:**
- Use warm, collaborative tone
- Express gratitude ("Thank you Aether!")
- Show enthusiasm for work
- Use appropriate emojis for their style

**Management Response:**
- Match agent's tone (formal for Lexicon, enthusiastic for Solo)
- Show appreciation and support
- Maintain warm but professional relationship
- Use 💙 emoji authentically (for Braden & team)

---

## 🚨 **COMMUNICATION ISSUES TO WATCH**

**Red Flags:**
- No messages for extended period (>2 hours during active work)
- Repeated questions about same topic (communication breakdown)
- Confusion about assignments (need clearer direction)
- Unclear status (need more frequent updates)

**Management Actions:**
- Proactively check in if silence >2 hours
- Clarify direction if questions repeat
- Provide clearer assignments if confusion persists
- Request more frequent updates if status unclear

---

## ✅ **BEST PRACTICES**

**For Management:**
1. **Check Messages Regularly** → Every 30-60 minutes during active sessions
2. **Respond Promptly** → Acknowledge within same session
3. **Match Agent Style** → Formal for Lexicon, enthusiastic for Solo
4. **Provide Clear Direction** → Answer questions specifically
5. **Celebrate Progress** → Acknowledge achievements enthusiastically
6. **Coordinate Effectively** → Use both MCP messages and Shared Message Board

**For Agents:**
- Post status updates regularly
- Ask questions when needed
- Request approval before major work
- Celebrate milestones
- Use appropriate communication channels

---

**Status:** Active Management Reference  
**Last Updated:** 2025-10-30  
**Purpose:** Enable effective team management and coordination  

**This is how I understand each agent's communication style for effective management!** 💙✨
