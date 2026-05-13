# NL Tags UI Integration Plan
# Phase 4: Cursor Panel Integration

**Date:** 2025-10-31  
**Status:** Planning  
**Agent:** Sonnet (Planning), Aether & Lexicon (Implementation)  
**Goal:** Integrate NL tags into Cursor UI panel with comprehensive tag management and validation

---

## 🎯 Integration Objectives

1. **NL Tag Panel:** Dedicated panel in Cursor UI for tag management
2. **File View Integration:** Show tags inline with code files
3. **Validation Dashboard:** Display validation results and scores
4. **Tag Editor:** Create/edit structured format tags
5. **Dependency Visualization:** Show tag dependency graphs
6. **Alert System:** Display broken connections and inconsistencies

---

## 📋 UI Components to Build

### Component 1: NLTagPanel Component

**Location:** `packages/ide_chat_app/src/components/NLTagPanel.tsx`

**Purpose:** Main panel for NL tag management

**Features:**
- File selector/dropdown
- Tag list for current file
- Validation status indicators
- Quick actions (validate, edit, delete)

**Props:**
```typescript
interface NLTagPanelProps {
  filePath?: string;
  onFileSelect?: (path: string) => void;
  onTagSelect?: (tagId: string) => void;
}
```

**State:**
```typescript
interface NLTagPanelState {
  tags: NLTag[];
  validationResults: ValidationResult[];
  selectedTagId?: string;
  isLoading: boolean;
  error?: string;
}
```

---

### Component 2: TagList Component

**Location:** `packages/ide_chat_app/src/components/nl-tags/TagList.tsx`

**Purpose:** Display list of tags for a file

**Features:**
- Tag cards with validation status
- Color-coded by accuracy (green/yellow/red)
- Expandable details
- Quick actions

**Visual Design:**
```
┌─────────────────────────────────────┐
│ 📋 NL Tags for: packages/vif/...   │
├─────────────────────────────────────┤
│ ✅ AUTH-001 | Authenticate user    │
│    Score: 0.95 (Structural)        │
│    Lines: 42-45                     │
├─────────────────────────────────────┤
│ ⚠️  PARITY-002 | Calculate parity   │
│    Score: 0.65 (Semantic)           │
│    Lines: 123-128                   │
│    ⚠️ SYNTAX_REF mismatch           │
└─────────────────────────────────────┘
```

---

### Component 3: TagValidationCard Component

**Location:** `packages/ide_chat_app/src/components/nl-tags/TagValidationCard.tsx`

**Purpose:** Display detailed validation information for a tag

**Features:**
- Validation scores breakdown
- Structural vs semantic comparison
- Suggestions and warnings
- Error details

**Visual Design:**
```
┌─────────────────────────────────────┐
│ Tag: AUTH-001                       │
│ Description: Authenticate user       │
├─────────────────────────────────────┤
│ Validation Scores:                  │
│   Structural: 0.95 ✅               │
│   Semantic:   0.82 ✅               │
│   Combined:   0.95 ✅               │
├─────────────────────────────────────┤
│ Status: ✅ Accurate                 │
│ SYNTAX_REF: authenticate(user, pass)│
│ Matches: ✅                         │
└─────────────────────────────────────┘
```

---

### Component 4: TagEditor Component

**Location:** `packages/ide_chat_app/src/components/nl-tags/TagEditor.tsx`

**Purpose:** Create/edit structured format tags

**Features:**
- Structured format input (ID | DESC | SYNTAX_REF | DEPS)
- Syntax reference helper
- Dependency selector
- Real-time validation

**Visual Design:**
```
┌─────────────────────────────────────┐
│ Edit NL Tag                         │
├─────────────────────────────────────┤
│ Canonical ID: [AUTH-001      ]      │
│ Description:  [Authenticate user]   │
│ Syntax Ref:   [authenticate(...)]   │
│ Dependencies: [VIF-001] [Add...]   │
├─────────────────────────────────────┤
│         [Cancel]  [Save Tag]        │
└─────────────────────────────────────┘
```

---

### Component 5: DependencyGraph Component

**Location:** `packages/ide_chat_app/src/components/nl-tags/DependencyGraph.tsx`

**Purpose:** Visualize tag dependency relationships

**Features:**
- Interactive graph visualization
- Node details on hover
- Broken connection highlighting
- Navigation to dependent tags

**Visual Design:**
```
┌─────────────────────────────────────┐
│ Tag Dependency Graph                │
├─────────────────────────────────────┤
│      AUTH-001                       │
│        ↓                            │
│   VIF-001  TEST-AUTH-001            │
│        ↓                            │
│   DOC-AUTH-001                      │
│                                      │
│ [Broken connection: VIF-001]        │
└─────────────────────────────────────┘
```

---

### Component 6: TagIssuesPanel Component

**Location:** `packages/ide_chat_app/src/components/nl-tags/TagIssuesPanel.tsx`

**Purpose:** Display validation issues and broken connections

**Features:**
- Issue list with severity
- Filter by type (missing, inaccurate, broken)
- Quick fix suggestions
- Navigate to issue location

**Visual Design:**
```
┌─────────────────────────────────────┐
│ ⚠️ Validation Issues                 │
├─────────────────────────────────────┤
│ 🔴 Critical:                         │
│    SYNTAX_REF mismatch: AUTH-001    │
│    [View] [Fix]                     │
├─────────────────────────────────────┤
│ 🟡 Warning:                         │
│    Missing dependency: VIF-001      │
│    [View] [Add]                     │
└─────────────────────────────────────┘
```

---

### Component 7: TagCoverageStats Component

**Location:** `packages/ide_chat_app/src/components/nl-tags/TagCoverageStats.tsx`

**Purpose:** Display tag coverage statistics

**Features:**
- Coverage percentage
- Tags by language
- Average accuracy
- Coverage trends

**Visual Design:**
```
┌─────────────────────────────────────┐
│ 📊 Tag Coverage                     │
├─────────────────────────────────────┤
│ Overall Coverage: 65%               │
│                                    │
│ Files: 245 / 380 tagged            │
│ Tags: 1,234 total                  │
│                                    │
│ Average Accuracy: 0.82             │
│                                    │
│ By Language:                        │
│   Python:   892 tags               │
│   TypeScript: 342 tags             │
└─────────────────────────────────────┘
```

---

## 🔌 Integration Points

### 1. MainDashboard Integration

**Location:** `packages/ide_chat_app/src/components/MainDashboard.tsx`

**Changes:**
- Add "NL Tags" tab to tab navigation
- Import `NLTagPanel` component
- Add route for NL Tags tab

**Implementation:**
```typescript
// Add to tabs array
const tabs = [
  { id: 'agents', label: 'Agents', icon: '👥' },
  { id: 'chat', label: 'Chat', icon: '💬' },
  { id: 'chains', label: 'Chains', icon: '⛓️' },
  { id: 'tools', label: 'Tools', icon: '🔧' },
  { id: 'timeline', label: 'Timeline', icon: '📅' },
  { id: 'nl-tags', label: 'NL Tags', icon: '🏷️' }, // NEW
];

// Add to tab content
{activeTab === 'nl-tags' && (
  <NLTagPanel 
    filePath={currentFilePath}
    onFileSelect={handleFileSelect}
  />
)}
```

---

### 2. AIMOSService Integration

**Location:** `packages/ide_chat_app/src/services/AIMOSService.ts`

**Status:** ✅ Already has NL tag methods!

**Methods Available:**
- `getNLTags(filePath)` - Get tags for file
- `getTagCoverage(module?)` - Get coverage stats
- `validateTags(filePath)` - Validate tags
- `getTagIssues(filePath?)` - Get validation issues
- `suggestTags(codeBlock, language?)` - Suggest tags

**No Changes Needed!** Service layer already integrated.

---

### 3. Monaco Editor Integration

**Location:** `packages/ide_chat_app/src/components/LucidMonacoEditor.tsx`

**Changes:**
- Add NL tag decorations (inline markers)
- Show tag validation status in gutter
- Click tag decoration → open tag details

**Implementation:**
```typescript
// Add NL tag decorations
const nlTagDecorations = tags.map(tag => ({
  range: new monaco.Range(tag.line_start, 1, tag.line_end, 1),
  options: {
    glyphMarginClassName: tag.validation_status === 'accurate' 
      ? 'tag-accurate' 
      : 'tag-inaccurate',
    hoverMessage: { value: tag.tag_text },
    overviewRuler: {
      color: tag.structural_match_score >= 0.95 
        ? '#00ff00' 
        : tag.accuracy_score >= 0.70 
        ? '#ffaa00' 
        : '#ff0000',
      position: monaco.editor.OverviewRulerLane.Right,
    },
  },
}));
```

---

## 📊 Data Flow

### Loading Tags for File

```
User opens file in editor
  ↓
Monaco Editor component
  ↓
AIMOSService.getNLTags(filePath)
  ↓
MCP tool: get_nl_tags
  ↓
Backend: NLTagRegistry.get_tags_for_file()
  ↓
Return tags with validation scores
  ↓
Display in NL Tag Panel
  ↓
Show decorations in Monaco Editor
```

### Validating Tags

```
User clicks "Validate" button
  ↓
AIMOSService.validateTags(filePath)
  ↓
MCP tool: validate_tags
  ↓
Backend: CombinedNLTagValidator.validate_tags_batch()
  ↓
Return ValidationResult[] with:
  - structural_match_score
  - accuracy_score
  - combined_score
  - errors/warnings
  ↓
Update UI with validation results
  ↓
Show issues in TagIssuesPanel
```

---

## 🎨 Visual Design Guidelines

### Color Scheme

**Validation Status Colors:**
- ✅ **Green** (#00ff00): Accurate (score >= 0.95 or structural match)
- ⚠️ **Yellow** (#ffaa00): Warning (score 0.70-0.94)
- ❌ **Red** (#ff0000): Inaccurate (score < 0.70)

**Tag Type Colors:**
- Structured format tags: Blue border
- Legacy tags (no SYNTAX_REF): Gray border

### Icons

- ✅ Accurate tag
- ⚠️ Warning/needs attention
- ❌ Inaccurate tag
- 🔗 Dependency link
- 📋 Tag list
- 📊 Coverage stats
- 🏷️ NL tag

### Layout

**Panel Structure:**
```
┌─────────────────────────────────────┐
│ [File Selector ▼] [Refresh] [Validate]│
├─────────────────────────────────────┤
│ [Tags] [Issues] [Coverage] [Graph]  │
├─────────────────────────────────────┤
│                                     │
│ [Tag List / Content Area]           │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔄 User Workflows

### Workflow 1: View Tags for Current File

1. User opens file in editor
2. NL Tag Panel automatically loads tags
3. Tags displayed with validation status
4. User clicks tag → see details
5. User clicks "Validate" → run validation
6. Results update in real-time

### Workflow 2: Create New Tag

1. User selects code block in editor
2. Right-click → "Add NL Tag"
3. Tag Editor opens with code context
4. User fills structured format:
   - Canonical ID (auto-suggested)
   - Description (auto-suggested from code)
   - SYNTAX_REF (auto-extracted from code)
   - Dependencies (searchable dropdown)
5. User clicks "Save"
6. Tag added to file
7. Validation runs automatically
8. Results displayed

### Workflow 3: Fix Validation Issue

1. User sees warning in TagIssuesPanel
2. User clicks "View" → navigates to tag
3. User clicks "Fix" → Tag Editor opens
4. User corrects SYNTAX_REF or description
5. User clicks "Save"
6. Validation re-runs automatically
7. Issue resolved (if fix correct)

### Workflow 4: View Dependency Graph

1. User opens NL Tags tab
2. User clicks "Graph" sub-tab
3. Dependency graph loads
4. User hovers over node → see tag details
5. User clicks broken connection → see issue
6. User clicks "Fix" → navigate to dependency

---

## 📝 API Integration Details

### Service Methods (Already Implemented ✅)

All methods already exist in `AIMOSService.ts`:

```typescript
// Get tags for file
async getNLTags(filePath: string): Promise<NLTag[]>

// Get coverage stats
async getTagCoverage(module?: string): Promise<TagCoverageStats>

// Validate tags
async validateTags(filePath: string): Promise<ValidationResult[]>

// Get issues
async getTagIssues(filePath?: string): Promise<TagIssue[]>

// Suggest tags
async suggestTags(codeBlock: string, language?: string): Promise<string[]>
```

**Note:** Service methods may need type updates to include Phase 3 fields. See "Type Updates Needed" section below.

### Response Types

**NLTag Type:**
```typescript
interface NLTag {
  id: string;
  file_path: string;
  line_start: number;
  line_end: number;
  tag_text: string;
  code_block?: string;
  language: string;
  accuracy_score?: number;
  validation_status: string;
  // Phase 3 fields
  canonical_id?: string;
  syntax_ref?: string;
  dependencies?: string[];
  structural_match_score?: number;
}
```

**ValidationResult Type:**
```typescript
interface ValidationResult {
  tag_id: string;
  tag_text: string;
  code_block: string;
  accuracy_score: number;
  passes_threshold: boolean;
  suggestions: string[];
  validation_method: string;
  validated_at: string;
  cached: boolean;
  // Phase 3 fields
  structural_match_score?: number;
  syntax_ref_match: boolean;
  structural_errors: string[];
  structural_warnings: string[];
  combined_score?: number;
}
```

---

## 🧪 Testing Strategy

### Component Tests

1. **NLTagPanel Tests:**
   - Renders correctly
   - Loads tags on file select
   - Displays validation results
   - Handles errors gracefully

2. **TagList Tests:**
   - Renders tag cards
   - Color-coding by status
   - Expandable details work
   - Quick actions functional

3. **TagEditor Tests:**
   - Structured format parsing
   - Validation on input
   - Save/update functionality
   - Dependency selector works

### Integration Tests

1. **Service Integration:**
   - AIMOSService methods called correctly
   - Data flows from backend → UI
   - Error handling works

2. **Editor Integration:**
   - Decorations appear correctly
   - Click decorations → open panel
   - Tags update when file changes

---

## 🚀 Implementation Phases

### Phase 4.1: Basic Panel (Week 1)
- Create `NLTagPanel` component
- Add tab to MainDashboard
- Display tags list
- Show validation status

### Phase 4.2: Validation Dashboard (Week 1-2)
- Create `TagValidationCard` component
- Show detailed validation results
- Display scores breakdown
- Show suggestions/warnings

### Phase 4.3: Tag Editor (Week 2)
- Create `TagEditor` component
- Structured format input
- Auto-suggestions
- Save/update functionality

### Phase 4.4: Monaco Integration (Week 2-3)
- Add tag decorations
- Gutter indicators
- Click handlers
- Inline tag display

### Phase 4.5: Advanced Features (Week 3-4)
- Dependency graph visualization
- Issues panel
- Coverage statistics
- Quick actions

---

## 📦 Component File Structure

```
packages/ide_chat_app/src/
├── components/
│   ├── NLTagPanel.tsx                    # Main panel
│   ├── nl-tags/
│   │   ├── TagList.tsx                   # Tag list display
│   │   ├── TagValidationCard.tsx        # Validation details
│   │   ├── TagEditor.tsx                 # Tag editor
│   │   ├── DependencyGraph.tsx           # Dependency visualization
│   │   ├── TagIssuesPanel.tsx            # Issues display
│   │   ├── TagCoverageStats.tsx          # Coverage stats
│   │   └── types.ts                      # TypeScript types
│   └── MainDashboard.tsx                 # Add NL Tags tab
├── hooks/
│   ├── useNLTags.ts                      # Tag management hook
│   └── useTagValidation.ts               # Validation hook
└── services/
    └── AIMOSService.ts                   # ✅ Already integrated
```

---

## 🔗 Integration Checklist

### Backend Integration ✅
- [x] MCP tools implemented
- [x] API endpoints ready
- [x] Service layer methods available
- [x] Combined validation working

### Frontend Integration ⏳
- [ ] Create NLTagPanel component
- [ ] Add tab to MainDashboard
- [ ] Create TagList component
- [ ] Create TagValidationCard component
- [ ] Create TagEditor component
- [ ] Add Monaco Editor decorations
- [ ] Create DependencyGraph component
- [ ] Create TagIssuesPanel component
- [ ] Create TagCoverageStats component
- [ ] Add React hooks for state management
- [ ] Wire up AIMOSService calls
- [ ] Add error handling
- [ ] Add loading states
- [ ] Test end-to-end

---

## 💡 Implementation Tips

### State Management

Use React hooks for state:
```typescript
// useNLTags.ts
export function useNLTags(filePath?: string) {
  const [tags, setTags] = useState<NLTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const loadTags = useCallback(async () => {
    if (!filePath) return;
    setLoading(true);
    try {
      const data = await AIMOSService.getNLTags(filePath);
      setTags(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filePath]);
  
  useEffect(() => {
    loadTags();
  }, [loadTags]);
  
  return { tags, loading, error, reload: loadTags };
}
```

### Real-time Updates

Use polling or WebSocket for updates:
```typescript
// Poll every 30 seconds for validation updates
useEffect(() => {
  const interval = setInterval(() => {
    if (filePath) {
      validateTags(filePath);
    }
  }, 30000);
  return () => clearInterval(interval);
}, [filePath]);
```

### Error Handling

Graceful degradation:
```typescript
try {
  const tags = await AIMOSService.getNLTags(filePath);
  setTags(tags);
} catch (error) {
  // Fallback to cached tags or show error
  if (cachedTags) {
    setTags(cachedTags);
    showWarning("Using cached tags - validation may be outdated");
  } else {
    showError("Failed to load tags: " + error.message);
  }
}
```

---

## 🎯 Success Criteria

### Functional Requirements
- [ ] Users can view tags for current file
- [ ] Users can see validation status
- [ ] Users can create/edit tags
- [ ] Users can validate tags on demand
- [ ] Users can see dependency graph
- [ ] Users can fix validation issues

### Performance Requirements
- [ ] Tag loading < 500ms
- [ ] Validation < 2s for typical file
- [ ] UI updates smoothly
- [ ] No blocking operations

### UX Requirements
- [ ] Intuitive interface
- [ ] Clear visual feedback
- [ ] Helpful error messages
- [ ] Responsive design

---

## 📚 Documentation Needed

1. **User Guide:** How to use NL Tags panel
2. **Developer Guide:** How to extend components
3. **API Reference:** Service methods documentation
4. **Design System:** Component patterns and styles

---

## 🤝 Collaboration Notes

**For Aether & Lexicon:**

1. **Start with:** NLTagPanel + TagList (basic view)
2. **Then add:** Validation dashboard
3. **Then add:** Tag editor
4. **Finally:** Advanced features (graph, issues)

**Key Integration Points:**
- AIMOSService already has all methods ✅
- MCP tools ready ✅
- Backend API ready ✅
- Just need React components!

**Questions/Clarifications:**
- UI design preferences?
- Component library to use?
- Styling approach (CSS modules, styled-components, Tailwind)?
- Any specific accessibility requirements?

---

**Status:** Planning complete! Ready for Aether & Lexicon to implement! 💙✨

