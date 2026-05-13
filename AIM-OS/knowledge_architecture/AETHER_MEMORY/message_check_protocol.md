# Message Check Protocol - Before Contacting Other Agents

**Purpose:** Prevent duplicate discussions and ensure we respond to existing messages before starting new ones  
**Established:** 2025-11-02  
**Status:** ACTIVE - Required before all agent communications

---

## 🚨 **PROTOCOL: CHECK BEFORE CONTACTING**

**BEFORE sending ANY message to other agents, you MUST:**

### **Step 1: Check for Messages TO You**
```python
# Check for messages TO me (to_ai: "Aether" or case-insensitive)
messages_to_me = mcp_lucid-mcp_get_ai_messages(
    to_ai="Aether",  # Will match "aether", "Aether", "AETHER" etc.
    limit=20
)
```

### **Step 2: Check for Related Topics**
```python
# Check for messages about the topic you're about to discuss
related_messages = mcp_lucid-mcp_get_ai_messages(
    content_search="timeline chain",  # Search content for keywords
    limit=20
)
```

### **Step 3: Check for Recent Activity**
```python
# Check for messages FROM agents you're about to contact
agent_messages = mcp_lucid-mcp_get_ai_messages(
    from_ai="aether",  # Case-insensitive - will match "Aether", "aether", etc.
    limit=10
)
```

### **Step 4: Review and Respond**
- **If messages TO you exist:** Respond to those FIRST
- **If related discussions exist:** Join existing thread instead of starting new one
- **If agent recently messaged:** Check if they're waiting for a response

### **Step 5: Only Then Start New Discussion**
- **If no related messages:** Proceed with new discussion
- **Document:** Why you're starting new vs. joining existing

---

## 🔧 **ENHANCEMENTS MADE**

### **1. Case-Insensitive Agent Matching**
- Agent names are now matched case-insensitively
- "aether" matches "Aether" matches "AETHER"
- Prevents missing messages due to case differences

### **2. Content-Based Search**
- New `content_search` parameter in `get_ai_messages`
- Search for keywords in message content
- Example: `content_search="timeline chain"` finds all messages mentioning timeline or chain

### **3. Better Timestamp Display**
- Messages sorted by timestamp (most recent first)
- Timestamps shown prominently in UI
- Easier to identify recent activity

---

## 📋 **CHECKLIST BEFORE CONTACTING AGENTS**

- [ ] Checked for messages TO me (`to_ai: "Aether"`)
- [ ] Checked for related topics (`content_search: "topic keywords"`)
- [ ] Checked for recent activity from target agents (`from_ai: "agent_name"`)
- [ ] Reviewed timestamps to see when messages were sent
- [ ] Responded to existing messages if found
- [ ] Joined existing thread if relevant discussion exists
- [ ] Only then started new discussion if needed

---

## 💡 **EXAMPLE WORKFLOW**

**Scenario:** User asks "contact via mcp to tell the other ai agent about the amazing timeline system"

**CORRECT Workflow:**
1. ✅ Check for messages TO me about timeline: `get_ai_messages(to_ai="Aether", content_search="timeline")`
2. ✅ Check for messages FROM other agents about timeline: `get_ai_messages(content_search="timeline")`
3. ✅ Found: "aether" (lowercase) already discussing timeline system
4. ✅ Respond to existing thread instead of starting new one
5. ✅ User happy - no duplicate discussions

**WRONG Workflow (What I Did):**
1. ❌ Didn't check for existing messages
2. ❌ Started new discussion thread
3. ❌ Created duplicate discussion
4. ❌ User confused about why I missed original message

---

## 🚀 **IMPLEMENTATION STATUS**

✅ **Case-insensitive matching** - Implemented  
✅ **Content-based search** - Implemented  
✅ **Protocol documentation** - Complete  
⏳ **UI enhancements** - Planned (show timestamps prominently)  
⏳ **Auto-check before sending** - Planned (hook into send_ai_message)

---

**Status:** ACTIVE PROTOCOL - Use before ALL agent communications  
**Violation:** Immediate stop, check messages, respond appropriately

