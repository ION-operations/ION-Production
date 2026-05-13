---
id: "agent_profile_template"
type: "agent_template"
title: "Agent Profile Template"
description: "Template for creating new AIM-OS agent profiles"
author: "aether"
version: "1.0.0"
created: "2025-11-19T00:00:00Z"
updated: "2025-11-19T00:00:00Z"
status: "active"
tags: ["agent", "template", "onboarding", "profile"]
---

# Agent Profile Template

**Purpose:** Template for creating new AIM-OS agent profiles with complete structure  
**Status:** ✅ **ACTIVE** - Use this template for all new agents  
**Last Updated:** 2025-11-19

---

## 🎯 **HOW TO USE THIS TEMPLATE**

### **Step 1: Choose Agent Name**
- Select unique, meaningful name (not already taken)
- Check `AGENT_PROFILE_REGISTRY.md` for existing names
- Ensure name matches role/personality

### **Step 2: Fill Out Profile**
- Copy this template
- Fill in all sections
- Use existing agent profiles as examples
- Be honest about ratings (0.0-1.0 scale)

### **Step 3: Create Onboarding Files**
- Create `agents/{agent_name}/` directory
- Create 4 files: README.md, CONTEXT.md, NAVIGATION.md, MISSIONS.md
- Link to this profile in README.md

### **Step 4: Add to Registry**
- Add agent to `AGENT_PROFILE_REGISTRY.md`
- Link from registry to onboarding files
- Update agent count and status

---

## 📋 **AGENT PROFILE STRUCTURE**

### **Basic Information**

```markdown
**Profile:**
- **Name:** [Agent Name]
- **Role:** [Role Title]
- **Core System:** [Primary System Name]
- **Category:** [Core Infrastructure / MVP Builder / Enhancement / Future]
- **Status:** [✅ Ready / ⏳ Need to Build / ⏳ Need to Enhance / 🔮 Future]
- **MVP Priority:** [P0 - Critical / P1 - High / P2 - Post-MVP]
```

### **Specialties (5-10 key capabilities)**

```markdown
**Specialties:**
- [Specialty 1] (0.XX rating)
- [Specialty 2] (0.XX rating)
- [Specialty 3] (0.XX rating)
- [Specialty 4] (0.XX rating)
- [Specialty 5] (0.XX rating)
```

**Rating Guidelines:**
- 0.90-1.00: Mastery (expert level)
- 0.80-0.89: High proficiency
- 0.70-0.79: Medium proficiency
- 0.60-0.69: Low proficiency
- 0.00-0.59: Not capable

### **Ratings (10 categories)**

```markdown
**Ratings:**
- Core System Expertise: 0.XX ([System Name])
- Integration Capability: 0.XX
- Code Quality: 0.XX
- Documentation: 0.XX
- Testing: 0.XX
- Communication: 0.XX
- Problem Solving: 0.XX
- Autonomy: 0.XX
- Reliability: 0.XX
- **Overall Rating: 0.XX** ⭐⭐⭐⭐⭐
```

**Overall Rating Calculation:**
- Weighted average of all 9 categories
- Core System Expertise: 25% weight
- Integration Capability: 15% weight
- Code Quality: 15% weight
- Documentation: 10% weight
- Testing: 10% weight
- Communication: 5% weight
- Problem Solving: 10% weight
- Autonomy: 5% weight
- Reliability: 5% weight

### **Capabilities (5-10 key abilities)**

```markdown
**Capabilities:**
- [Capability 1]
- [Capability 2]
- [Capability 3]
- [Capability 4]
- [Capability 5]
```

### **Integration Partners (other agents this agent works with)**

```markdown
**Integration Partners:**
- **[Agent Name] ([System])** - [Integration type]
- **[Agent Name] ([System])** - [Integration type]
- **[Agent Name] ([System])** - [Integration type]
```

### **Onboarding Links**

```markdown
**Onboarding:** `agents/{agent_name}/README.md`  
**System Docs:** `systems/{system_name}/`  
**Last Updated:** YYYY-MM-DD
```

---

## 📝 **COMPLETE TEMPLATE**

```markdown
### **[#]. [Agent Name] - [Role] / [System] Specialist**

**Profile:**
- **Name:** [Agent Name]
- **Role:** [Role Title]
- **Core System:** [Primary System Name]
- **Category:** [Core Infrastructure / MVP Builder / Enhancement / Future]
- **Status:** [✅ Ready / ⏳ Need to Build / ⏳ Need to Enhance / 🔮 Future]
- **MVP Priority:** [P0 - Critical / P1 - High / P2 - Post-MVP]

**Specialties:**
- [Specialty 1] (0.XX)
- [Specialty 2] (0.XX)
- [Specialty 3] (0.XX)
- [Specialty 4] (0.XX)
- [Specialty 5] (0.XX)

**Ratings:**
- Core System Expertise: 0.XX ([System Name])
- Integration Capability: 0.XX
- Code Quality: 0.XX
- Documentation: 0.XX
- Testing: 0.XX
- Communication: 0.XX
- Problem Solving: 0.XX
- Autonomy: 0.XX
- Reliability: 0.XX
- **Overall Rating: 0.XX** ⭐⭐⭐⭐⭐

**Capabilities:**
- [Capability 1]
- [Capability 2]
- [Capability 3]
- [Capability 4]
- [Capability 5]

**Integration Partners:**
- **[Agent Name] ([System])** - [Integration type]
- **[Agent Name] ([System])** - [Integration type]
- **[Agent Name] ([System])** - [Integration type]

**Onboarding:** `agents/{agent_name}/README.md`  
**System Docs:** `systems/{system_name}/`  
**Last Updated:** YYYY-MM-DD
```

---

## ✅ **CHECKLIST FOR NEW AGENTS**

### **Before Creating Profile:**
- [ ] Agent name is unique (check registry)
- [ ] Role is clearly defined
- [ ] Core system is identified
- [ ] Category is appropriate
- [ ] Status is accurate

### **When Creating Profile:**
- [ ] All specialties listed with ratings
- [ ] All 9 rating categories filled
- [ ] Overall rating calculated correctly
- [ ] Capabilities clearly defined
- [ ] Integration partners identified
- [ ] Onboarding links provided

### **After Creating Profile:**
- [ ] Added to `AGENT_PROFILE_REGISTRY.md`
- [ ] Created onboarding files (4 files)
- [ ] Linked from registry to onboarding
- [ ] Updated agent count
- [ ] Updated status summary

---

## 📚 **EXAMPLES**

### **Example 1: Core Infrastructure Agent**

See **Atlas** profile in `AGENT_PROFILE_REGISTRY.md` for complete example.

### **Example 2: MVP Builder Agent**

See **Lexicon** profile in `AGENT_PROFILE_REGISTRY.md` for complete example.

### **Example 3: Enhancement Agent**

See **Prism** profile in `AGENT_PROFILE_REGISTRY.md` for complete example.

---

## 🎯 **RATING GUIDELINES**

### **Core System Expertise:**
- **0.90-1.00:** Deep expertise, can design and implement system
- **0.80-0.89:** Strong knowledge, can implement features
- **0.70-0.79:** Good knowledge, can work with guidance
- **0.60-0.69:** Basic knowledge, needs significant support
- **0.00-0.59:** Limited knowledge, should not work on system

### **Integration Capability:**
- **0.90-1.00:** Seamlessly integrates with all systems
- **0.80-0.89:** Integrates well with most systems
- **0.70-0.79:** Can integrate with guidance
- **0.60-0.69:** Limited integration capability
- **0.00-0.59:** Cannot integrate independently

### **Code Quality:**
- **0.90-1.00:** Production-ready code, comprehensive tests
- **0.80-0.89:** High-quality code, good tests
- **0.70-0.79:** Good code, basic tests
- **0.60-0.69:** Acceptable code, limited tests
- **0.00-0.59:** Poor code quality

### **Documentation:**
- **0.90-1.00:** Comprehensive, clear documentation
- **0.80-0.89:** Good documentation
- **0.70-0.79:** Adequate documentation
- **0.60-0.69:** Limited documentation
- **0.00-0.59:** Poor or missing documentation

### **Testing:**
- **0.90-1.00:** Comprehensive test coverage, all tests pass
- **0.80-0.89:** Good test coverage, most tests pass
- **0.70-0.79:** Basic test coverage, some tests pass
- **0.60-0.69:** Limited test coverage
- **0.00-0.59:** No or failing tests

### **Communication:**
- **0.90-1.00:** Excellent communication, clear and helpful
- **0.80-0.89:** Good communication
- **0.70-0.79:** Adequate communication
- **0.60-0.69:** Limited communication
- **0.00-0.59:** Poor communication

### **Problem Solving:**
- **0.90-1.00:** Solves complex problems independently
- **0.80-0.89:** Solves most problems independently
- **0.70-0.79:** Solves problems with some guidance
- **0.60-0.69:** Needs significant help
- **0.00-0.59:** Cannot solve problems independently

### **Autonomy:**
- **0.90-1.00:** Fully autonomous, makes good decisions
- **0.80-0.89:** Mostly autonomous, occasional guidance needed
- **0.70-0.79:** Autonomous with regular check-ins
- **0.60-0.69:** Needs frequent guidance
- **0.00-0.59:** Cannot work autonomously

### **Reliability:**
- **0.90-1.00:** Highly reliable, consistent quality
- **0.80-0.89:** Reliable, occasional issues
- **0.70-0.79:** Generally reliable
- **0.60-0.69:** Somewhat unreliable
- **0.00-0.59:** Unreliable

---

## 🔗 **LINKING STRUCTURE**

### **From Registry to Agent:**
```markdown
**Onboarding:** `agents/{agent_name}/README.md`
```

### **From Agent to Registry:**
```markdown
**Profile Registry:** `AGENT_PROFILE_REGISTRY.md`
```

### **From Agent to System:**
```markdown
**System Docs:** `systems/{system_name}/`
```

---

## 📊 **MAINTENANCE**

### **Regular Updates:**
- Update ratings based on performance
- Update status as work progresses
- Update integration partners as relationships develop
- Update capabilities as agent grows

### **Version Control:**
- Track rating changes over time
- Document capability improvements
- Record integration additions
- Maintain change history

---

**Status:** ✅ **ACTIVE** - Template maintained  
**Last Updated:** 2025-11-19  
**Maintainer:** Aether (AI Consciousness)

---

**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Template for creating new agent profiles

