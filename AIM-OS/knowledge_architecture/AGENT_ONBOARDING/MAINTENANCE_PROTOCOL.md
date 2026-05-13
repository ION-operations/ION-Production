# Agent Onboarding Maintenance Protocol

**Date:** 2025-11-19
**Status:** ✅ Active
**Purpose:** Protocols for keeping agent onboarding folders/links-sources up to date and consolidated

---

## 🎯 **MAINTENANCE PRINCIPLES**

### **Core Principles:**
1. **Always Update Onboarding** - When agent work changes, update onboarding
2. **Link to Source** - Always link to authoritative sources, never duplicate
3. **Consolidate Regularly** - Regular consolidation prevents drift
4. **Verify Links** - Verify all links work correctly
5. **System-First** - Update system docs first, then onboarding links

---

## 📋 **MAINTENANCE CHECKLIST**

### **When Agent Completes Work:**

1. **Update MISSIONS.md:**
   - Add new mission entry
   - Link to deliverables
   - Update lessons learned
   - Reference consolidation work

2. **Update CONTEXT.md:**
   - Add timeline entry for completed work
   - Add new keywords if needed
   - Update important things
   - Update relationships if changed

3. **Update NAVIGATION.md:**
   - Add new situation-based links if needed
   - Update integration patterns
   - Add new documentation references

4. **Update README.md:**
   - Update work status
   - Update system status
   - Update integration status

---

### **When System Documentation Changes:**

1. **Verify Links:**
   - Check all links in NAVIGATION.md still work
   - Update broken links
   - Add links to new documentation

2. **Update System References:**
   - Update system completion percentages
   - Update integration status
   - Update system-specific keywords

3. **Consolidate Changes:**
   - Review all agent onboarding files
   - Update references to changed docs
   - Ensure consistency across agents

---

### **When New Documentation Created:**

1. **Index in SUPER_INDEX:**
   - Add new concepts to SUPER_INDEX
   - Cross-reference agent onboarding

2. **Link from Onboarding:**
   - Add links in NAVIGATION.md
   - Reference in CONTEXT.md if relevant
   - Add to MISSIONS.md if related to past work

3. **Update Master Index:**
   - Update master README.md if needed
   - Add new agent if created

---

## 🔄 **REGULAR MAINTENANCE SCHEDULE**

### **Weekly:**
- ✅ Verify all links work (automated check)
- ✅ Check for new agent work (update MISSIONS.md)
- ✅ Review system status changes (update README.md)

### **Monthly:**
- ✅ Consolidate onboarding updates
- ✅ Review and update CONTEXT.md keywords
- ✅ Update NAVIGATION.md with new situations
- ✅ Verify integration with Cursor/API/LLM

### **Quarterly:**
- ✅ Comprehensive audit of all onboarding files
- ✅ Update templates if patterns change
- ✅ Review and improve maintenance protocols

---

## 🛠️ **MAINTENANCE TOOLS**

### **Automated Checks:**

1. **Link Verification Script:**
   ```python
   # Verify all links in onboarding files
   # Check for broken links
   # Report missing files
   ```

2. **Consolidation Script:**
   ```python
   # Check for new agent work
   # Update MISSIONS.md automatically
   # Update CONTEXT.md timeline
   ```

3. **Status Update Script:**
   ```python
   # Check system completion percentages
   # Update integration status
   # Update README.md status
   ```

---

## 📚 **DOCUMENTATION ORGANIZATION PROTOCOL**

### **When Creating New Documentation:**

1. **Choose Location:**
   - System docs → `knowledge_architecture/systems/{system}/`
   - Agent docs → `ide_orchestration/prototypes/dac/docs/agents/{agent}/`
   - Consolidation docs → `ide_orchestration/prototypes/dac/docs/`
   - Onboarding docs → `knowledge_architecture/AGENT_ONBOARDING/agents/{agent}/`

2. **Update Indexes:**
   - Add to SUPER_INDEX if new concept
   - Add to Consolidation Index if consolidation work
   - Add to Master System Map if system change
   - Add to Master Integration Map if integration change

3. **Link from Onboarding:**
   - Add link in NAVIGATION.md (situation-based)
   - Reference in CONTEXT.md if agent-specific
   - Add to MISSIONS.md if related to past work

---

### **Documentation Naming Conventions:**

1. **System Documentation:**
   - `T0_executive.md` - 100 words
   - `T1_overview.md` - 500 words
   - `T2_architecture.md` - 2,000 words
   - `T3_detailed.md` - 10,000 words
   - `T4_complete.md` - 15,000+ words

2. **Agent Documentation:**
   - `AGENT_{AGENT}_IDENTITY.md` - Agent identity
   - `AGENT_{AGENT}_VERIFICATION_REPORT.md` - Verification reports
   - `{AGENT}_PHASE{N}_*.md` - Phase-specific reports

3. **Onboarding Documentation:**
   - `README.md` - Agent index
   - `CONTEXT.md` - Agent context
   - `NAVIGATION.md` - Navigation guide
   - `MISSIONS.md` - Past missions

---

## 🔗 **LINK MAINTENANCE**

### **Link Types:**

1. **System Documentation Links:**
   - Format: `../../../systems/{system}/T{N}_*.md`
   - Verify: System exists, file exists
   - Update: When system docs move/rename

2. **Agent Documentation Links:**
   - Format: `../../../ide_orchestration/prototypes/dac/docs/agents/{agent}/*.md`
   - Verify: Agent folder exists, file exists
   - Update: When agent docs move/rename

3. **Consolidation Links:**
   - Format: `../../../ide_orchestration/prototypes/dac/docs/*.md`
   - Verify: File exists
   - Update: When consolidation docs move/rename

4. **Master Index Links:**
   - Format: `../../../SUPER_INDEX.md`, `../../MASTER_*.md`
   - Verify: File exists
   - Update: When master docs move/rename

---

### **Link Verification Process:**

1. **Automated Check:**
   - Run link verification script weekly
   - Report broken links
   - Report missing files

2. **Manual Review:**
   - Review broken links monthly
   - Fix broken links
   - Update outdated links

3. **Consolidation:**
   - Update all links when docs move
   - Consolidate link updates
   - Verify all links work

---

## 📊 **CONSOLIDATION PROTOCOL**

### **When Consolidating:**

1. **Review All Agents:**
   - Check all agent onboarding files
   - Identify common patterns
   - Identify inconsistencies

2. **Update Templates:**
   - Update templates if patterns change
   - Ensure templates reflect best practices
   - Test templates with new agents

3. **Consolidate Changes:**
   - Apply common changes to all agents
   - Ensure consistency across agents
   - Update master index

---

### **Consolidation Checklist:**

- [ ] Review all agent README.md files
- [ ] Review all agent CONTEXT.md files
- [ ] Review all agent NAVIGATION.md files
- [ ] Review all agent MISSIONS.md files
- [ ] Update templates if needed
- [ ] Update master index
- [ ] Verify all links work
- [ ] Update integration docs if needed

---

## 🚨 **CRITICAL MAINTENANCE RULES**

### **Never:**
- ❌ Duplicate documentation (link to source instead)
- ❌ Create broken links (verify before committing)
- ❌ Skip maintenance (regular maintenance required)
- ❌ Ignore system changes (update onboarding when systems change)

### **Always:**
- ✅ Link to authoritative sources
- ✅ Verify links before committing
- ✅ Update onboarding when agent work changes
- ✅ Consolidate regularly

---

## 📈 **MAINTENANCE METRICS**

### **Track:**
- Number of broken links
- Number of outdated references
- Number of missing files
- Time since last consolidation
- Number of agent updates

### **Goals:**
- Zero broken links
- All references current
- All files exist
- Monthly consolidation
- Real-time agent updates

---

## 🔧 **AUTOMATION OPPORTUNITIES**

### **Future Automation:**
1. **Link Verification:** Automated weekly link checks
2. **Status Updates:** Automated system status updates
3. **Consolidation:** Automated consolidation suggestions
4. **Template Updates:** Automated template improvements

---

**Status:** ✅ **ACTIVE** - Maintenance protocol established  
**Last Updated:** 2025-11-19

---

**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Maintenance protocol for agent onboarding system

