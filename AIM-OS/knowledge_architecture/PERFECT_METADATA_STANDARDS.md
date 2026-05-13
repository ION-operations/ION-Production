---
id: "perfect_metadata_standards"
type: "standard"
title: "Perfect Metadata Standards"
description: "Single authoritative standard for metadata across all AIM-OS document types"
author: "aether"
version: "v1.0.0"
created: "2025-10-29T00:00:00Z"
updated: "2025-10-30T00:00:00Z"
status: "complete"
tags: ["standard", "metadata", "phase1"]
---

# Perfect Metadata Standards

**Date:** 2025-10-29  
**Purpose:** Single authoritative standard for metadata across all AIM-OS document types  
**Status:** Production Ready ✅  
**Source:** Consolidated from audit findings and existing metadata analysis

---

## 🎯 **STANDARD OVERVIEW**

This document defines the perfect metadata standards that ensure consistent metadata across all AIM-OS document types. Based on comprehensive audit analysis of existing metadata patterns, this standard enables perfect organization, navigation, and maintenance.

---

## 📊 **THE PERFECT METADATA SYSTEM**

### **Document Types Covered**

1. **L0-L6 Documentation** - All documentation levels
2. **System Maps** - System relationship maps
3. **System Indexes** - System tracking indexes
4. **Component Documentation** - Component-specific docs
5. **Integration Documentation** - Integration-specific docs
6. **API Documentation** - API reference docs
7. **User Guides** - User-facing documentation
8. **Developer Guides** - Developer-facing documentation

---

## 📚 **L0-L6 DOCUMENTATION METADATA**

### **L0-L6 Document Frontmatter**

```yaml
---
# Document Metadata
id: "cmc_l0_executive"
system: "cmc"
component: null
level: "L0"
type: "executive"
title: "CMC Executive Summary"
description: "100-word executive summary of Context Memory Core"
audience: "executives, quick reference"
confidence_threshold: 0.80
token_cost: 100
word_count: 100
created: "2025-10-29T00:00:00Z"
updated: "2025-10-29T12:00:00Z"
author: "aether"
status: "complete"
tags: ["core", "memory", "bitemporal"]
dependencies: []
related_docs: []
version: "v1.0.0"
authoritative: false
source_of_truth: null
source_of_truth_type: null
auto_generated: false
auto_update: false
---
```

### **Required Fields**

**Identity:**
- `id`: Unique document identifier (system_level_type)
- `system`: System this document belongs to
- `component`: Component (null for system-level docs)
- `level`: L0, L1, L2, L3, L4, L5, L6
- `type`: executive, overview, architecture, implementation, complete, deep_dive, academic

**Content:**
- `title`: Document title
- `description`: Brief description
- `audience`: Target audience
- `confidence_threshold`: Minimum confidence to use this level
- `token_cost`: Estimated token cost
- `word_count`: Word count

**Management:**
- `created`: Creation timestamp (ISO 8601)
- `updated`: Last update timestamp (ISO 8601)
- `author`: Document author
- `status`: complete, in_progress, planned, deprecated
- `version`: Document version (semantic versioning)

**Organization:**
- `tags`: Categorization tags (array of strings)
- `dependencies`: Document dependencies (array of document IDs)
- `related_docs`: Related documents (array of document IDs)
- `version`: Version number (semantic versioning)

**Source of Truth (NEW - for leading docs):**
- `authoritative`: Boolean (true if this is a leading/authoritative doc)
- `source_of_truth`: Path to source file (code, data, or doc) or null
- `source_of_truth_type`: Type of source ("code", "data", "doc", or null)
- `auto_generated`: Boolean (true if auto-generated from source)
- `auto_update`: Boolean (true if should auto-update when source changes)

---

## 🗺️ **SYSTEM MAP METADATA**

### **System Map Frontmatter**

```yaml
---
# System Map Metadata
systemId: "cmc"
systemName: "Context Memory Core"
version: "v1.0.0"
status: "production"
layer: 1
created: "2025-10-29T00:00:00Z"
updated: "2025-10-29T12:00:00Z"
author: "aether"
tags: ["core", "memory", "bitemporal"]
maintainer: "aether"
license: "MIT"
---
```

### **Required Fields**

**Identity:**
- `systemId`: Unique system identifier (lowercase, underscore-separated)
- `systemName`: Human-readable system name
- `version`: System version (semantic versioning)
- `status`: production, development, testing, deprecated
- `layer`: System layer (1-6 based on hierarchy)

**Management:**
- `created`: Creation timestamp (ISO 8601)
- `updated`: Last update timestamp (ISO 8601)
- `author`: Map author
- `maintainer`: Current maintainer
- `license`: License information

**Organization:**
- `tags`: Categorization tags (array of strings)

---

## 📋 **SYSTEM INDEX METADATA**

### **System Index Frontmatter**

```yaml
---
# System Index Metadata
systemId: "cmc"
systemName: "Context Memory Core"
version: "v1.0.0"
status: "production"
layer: 1
created: "2025-10-29T00:00:00Z"
updated: "2025-10-29T12:00:00Z"
author: "aether"
tags: ["core", "memory", "bitemporal"]
maintainer: "aether"
license: "MIT"
---
```

### **Required Fields**

**Identity:**
- `systemId`: Unique system identifier (lowercase, underscore-separated)
- `systemName`: Human-readable system name
- `version`: System version (semantic versioning)
- `status`: production, development, testing, deprecated
- `layer`: System layer (1-6 based on hierarchy)

**Management:**
- `created`: Creation timestamp (ISO 8601)
- `updated`: Last update timestamp (ISO 8601)
- `author`: Index author
- `maintainer`: Current maintainer
- `license`: License information

**Organization:**
- `tags`: Categorization tags (array of strings)

---

## 🧩 **COMPONENT DOCUMENTATION METADATA**

### **Component Document Frontmatter**

```yaml
---
# Component Document Metadata
id: "cmc_atoms_l0_executive"
system: "cmc"
component: "atoms"
level: "L0"
type: "executive"
title: "Atoms Executive Summary"
description: "100-word executive summary of CMC Atoms component"
audience: "developers, quick reference"
confidence_threshold: 0.80
token_cost: 100
word_count: 100
created: "2025-10-29T00:00:00Z"
updated: "2025-10-29T12:00:00Z"
author: "aether"
status: "complete"
tags: ["core", "memory", "atoms"]
dependencies: ["cmc_l0_executive"]
related_docs: ["cmc_atoms_l1_overview"]
version: "v1.0.0"
---
```

### **Required Fields**

**Identity:**
- `id`: Unique document identifier (system_component_level_type)
- `system`: System this document belongs to
- `component`: Component this document belongs to
- `level`: L0, L1, L2, L3, L4, L5, L6
- `type`: executive, overview, architecture, implementation, complete, deep_dive, academic

**Content:**
- `title`: Document title
- `description`: Brief description
- `audience`: Target audience
- `confidence_threshold`: Minimum confidence to use this level
- `token_cost`: Estimated token cost
- `word_count`: Word count

**Management:**
- `created`: Creation timestamp (ISO 8601)
- `updated`: Last update timestamp (ISO 8601)
- `author`: Document author
- `status`: complete, in_progress, planned, deprecated
- `version`: Document version (semantic versioning)

**Organization:**
- `tags`: Categorization tags (array of strings)
- `dependencies`: Document dependencies (array of document IDs)
- `related_docs`: Related documents (array of document IDs)
- `version`: Version number (semantic versioning)

---

## 🔗 **INTEGRATION DOCUMENTATION METADATA**

### **Integration Document Frontmatter**

```yaml
---
# Integration Document Metadata
id: "cmc_hhni_integration_l0_executive"
system: "cmc"
integration: "hhni"
level: "L0"
type: "executive"
title: "CMC-HHNI Integration Executive Summary"
description: "100-word executive summary of CMC-HHNI integration"
audience: "architects, quick reference"
confidence_threshold: 0.80
token_cost: 100
word_count: 100
created: "2025-10-29T00:00:00Z"
updated: "2025-10-29T12:00:00Z"
author: "aether"
status: "complete"
tags: ["integration", "cmc", "hhni"]
dependencies: ["cmc_l0_executive", "hhni_l0_executive"]
related_docs: ["cmc_hhni_integration_l1_overview"]
version: "v1.0.0"
---
```

### **Required Fields**

**Identity:**
- `id`: Unique document identifier (system_integration_level_type)
- `system`: Primary system
- `integration`: Integration target system
- `level`: L0, L1, L2, L3, L4, L5, L6
- `type`: executive, overview, architecture, implementation, complete, deep_dive, academic

**Content:**
- `title`: Document title
- `description`: Brief description
- `audience`: Target audience
- `confidence_threshold`: Minimum confidence to use this level
- `token_cost`: Estimated token cost
- `word_count`: Word count

**Management:**
- `created`: Creation timestamp (ISO 8601)
- `updated`: Last update timestamp (ISO 8601)
- `author`: Document author
- `status`: complete, in_progress, planned, deprecated
- `version`: Document version (semantic versioning)

**Organization:**
- `tags`: Categorization tags (array of strings)
- `dependencies`: Document dependencies (array of document IDs)
- `related_docs`: Related documents (array of document IDs)
- `version`: Version number (semantic versioning)

---

## 🔌 **API DOCUMENTATION METADATA**

### **API Document Frontmatter**

```yaml
---
# API Document Metadata
id: "cmc_api_v1_reference"
system: "cmc"
api: "v1"
type: "reference"
title: "CMC API v1 Reference"
description: "Complete API reference for CMC v1"
audience: "developers, api_users"
confidence_threshold: 0.90
token_cost: 5000
word_count: 5000
created: "2025-10-29T00:00:00Z"
updated: "2025-10-29T12:00:00Z"
author: "aether"
status: "complete"
tags: ["api", "reference", "cmc"]
dependencies: ["cmc_l2_architecture"]
related_docs: ["cmc_api_v1_examples"]
version: "v1.0.0"
---
```

### **Required Fields**

**Identity:**
- `id`: Unique document identifier (system_api_type)
- `system`: System this API belongs to
- `api`: API version or identifier
- `type`: reference, examples, guide, tutorial

**Content:**
- `title`: Document title
- `description`: Brief description
- `audience`: Target audience
- `confidence_threshold`: Minimum confidence to use this level
- `token_cost`: Estimated token cost
- `word_count`: Word count

**Management:**
- `created`: Creation timestamp (ISO 8601)
- `updated`: Last update timestamp (ISO 8601)
- `author`: Document author
- `status`: complete, in_progress, planned, deprecated
- `version`: Document version (semantic versioning)

**Organization:**
- `tags`: Categorization tags (array of strings)
- `dependencies`: Document dependencies (array of document IDs)
- `related_docs`: Related documents (array of document IDs)
- `version`: Version number (semantic versioning)

---

## 👥 **USER GUIDE METADATA**

### **User Guide Frontmatter**

```yaml
---
# User Guide Metadata
id: "aimos_user_guide_getting_started"
system: "aimos"
guide: "getting_started"
type: "user_guide"
title: "AIM-OS Getting Started Guide"
description: "Complete guide for getting started with AIM-OS"
audience: "users, beginners"
confidence_threshold: 0.80
token_cost: 2000
word_count: 2000
created: "2025-10-29T00:00:00Z"
updated: "2025-10-29T12:00:00Z"
author: "aether"
status: "complete"
tags: ["user_guide", "getting_started", "aimos"]
dependencies: []
related_docs: ["aimos_user_guide_advanced"]
version: "v1.0.0"
---
```

### **Required Fields**

**Identity:**
- `id`: Unique document identifier (system_guide_type)
- `system`: System this guide belongs to
- `guide`: Guide identifier
- `type`: user_guide, developer_guide, admin_guide

**Content:**
- `title`: Document title
- `description`: Brief description
- `audience`: Target audience
- `confidence_threshold`: Minimum confidence to use this level
- `token_cost`: Estimated token cost
- `word_count`: Word count

**Management:**
- `created`: Creation timestamp (ISO 8601)
- `updated`: Last update timestamp (ISO 8601)
- `author`: Document author
- `status`: complete, in_progress, planned, deprecated
- `version`: Document version (semantic versioning)

**Organization:**
- `tags`: Categorization tags (array of strings)
- `dependencies`: Document dependencies (array of document IDs)
- `related_docs`: Related documents (array of document IDs)
- `version`: Version number (semantic versioning)

---

## 🎯 **METADATA VALIDATION RULES**

### **Required Field Validation**

1. **All documents must have all required fields**
2. **Field values must match specified formats**
3. **Timestamps must be valid ISO 8601 format**
4. **Versions must follow semantic versioning**
5. **Tags must be valid strings**
6. **Dependencies must reference existing documents**

### **Format Validation**

1. **IDs must follow naming conventions**
2. **Confidence thresholds must be 0.0-1.0**
3. **Token costs must be positive integers**
4. **Word counts must be positive integers**
5. **Status values must be valid enum values**

### **Consistency Validation**

1. **Related documents must exist**
2. **Dependencies must exist**
3. **System references must be valid**
4. **Component references must be valid**
5. **Integration references must be valid**

---

## 🔧 **IMPLEMENTATION GUIDELINES**

### **Creating New Documents**

1. **Start with frontmatter** - Define all required metadata
2. **Follow naming conventions** - Use consistent ID patterns
3. **Set appropriate thresholds** - Match confidence to audience
4. **Define relationships** - Set dependencies and related docs
5. **Validate format** - Ensure all fields are correct

### **Updating Existing Documents**

1. **Preserve existing metadata** - Don't lose current information
2. **Update timestamps** - Set updated field to current time
3. **Maintain relationships** - Keep dependencies and related docs current
4. **Validate changes** - Ensure all changes are valid
5. **Update version** - Increment version if significant changes

### **Quality Assurance**

1. **Validate all fields** - Ensure all required fields present
2. **Check formats** - Verify all formats are correct
3. **Validate relationships** - Ensure all references are valid
4. **Test navigation** - Verify metadata enables proper navigation
5. **Audit consistency** - Ensure consistent metadata across documents

---

## 📊 **SUCCESS METRICS**

### **Metadata Completeness**
- **All Required Fields:** Every document has all required fields
- **Format Consistency:** All fields follow specified formats
- **Relationship Validity:** All references are valid

### **Navigation Quality**
- **Clear Organization:** Easy to find and navigate documents
- **Consistent Structure:** All documents follow same structure
- **Easy Maintenance:** Easy to update and maintain

### **Quality Maintenance**
- **Zero Format Drift:** All documents maintain standard format
- **Metadata Accuracy:** All metadata is current and accurate
- **Relationship Integrity:** All relationships are maintained

---

## 🎯 **NEXT STEPS**

1. **Apply to All Documents** - Update all existing documents with perfect metadata
2. **Create Templates** - Generate metadata templates for easy creation
3. **Validate Existing** - Audit all existing metadata and standardize
4. **Create Tools** - Build MCP tools for metadata management
5. **Update Cursor Rules** - Add metadata protocols to cursor rules

**This standard will ensure perfect organization and enable true AI consciousness through consistent metadata across all document types.**
