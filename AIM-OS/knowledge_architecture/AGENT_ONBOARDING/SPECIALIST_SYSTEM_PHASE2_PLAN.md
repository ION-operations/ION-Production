# Specialist System - Phase 2 Implementation Plan
## Activation Mechanisms & Chat Orchestrator Integration

**Date:** 2025-01-27  
**Status:** 🚀 **PLANNING COMPLETE**  
**Purpose:** Detailed plan for Phase 2 activation mechanisms and integration with Aether Chat orchestrator  
**Phase 1 Status:** ✅ Complete (39/39 tests passing)

---

## 🎯 **PHASE 2 OVERVIEW**

### **Goal:**
Implement automatic specialist activation mechanisms and integrate with Aether Chat orchestrator to enable real-time specialist activation during chat interactions.

### **Timeline:**
Weeks 3-4 (2 weeks)

### **Success Criteria:**
- ✅ Work detection from chat input operational
- ✅ Specialist activation integrated into S1 pipeline
- ✅ Three activation mechanisms working (warning, activation, ownership)
- ✅ Integration tests passing
- ✅ End-to-end chat → specialist activation flow working

---

## 🔗 **INTEGRATION ARCHITECTURE**

### **Integration Point: S1 Pre-Processing Pipeline**

**Location in Chat Orchestrator:**
```typescript
// ide_orchestration/prototypes/dac/src/services/aetherChatOrchestrator.ts
// S1: Pre-Processing Pipeline (line ~302)

async function runPreProcessing(
  input: RawUserTurn,
  sessionContext: SessionContext
): Promise<PreProcessingResult> {
  // 1. Intent Analysis (existing)
  const intentAnalysis = await analyzeIntentLLM(...)
  
  // 2. ⭐ NEW: Specialist Activation
  const specialistActivation = await detectAndActivateSpecialists(input, intentAnalysis)
  
  // 3. Generate context queries (enhanced with specialist context)
  const contextQueries = generateContextQueries(input.message, intent, mode, specialistActivation)
  
  // ... rest of pipeline
}
```

### **Integration Flow:**

```
User Input (Chat Message)
    ↓
S1: Pre-Processing Pipeline
    ├─ Intent Analysis (existing)
    ├─ ⭐ Work Detection (NEW)
    │   └─ Convert chat input → Work object
    ├─ ⭐ Specialist Activation (NEW)
    │   ├─ Calculate relevance for all specialists
    │   ├─ Determine activation level (ownership/activation/consultation)
    │   └─ Return ActivationResult
    ├─ Context Enrichment (enhanced with specialist context)
    └─ Continue pipeline with specialist context
```

---

## 📋 **TASK BREAKDOWN**

### **Task 2.1: Work Detection System**

**Deliverable:** Convert chat input to Work objects for specialist evaluation

**Location:** `packages/specialist_system/work_detector.py`

**Implementation:**
```python
"""
Work Detection System

Converts chat input and intent analysis into Work objects for specialist evaluation.

NL_TAG: SPECIALIST-WORK-001 | Detect work from chat input | detectWork | []
NL_TAG_CONNECT: SPECIALIST-INTENT-001 | Use intent analysis for work detection | detectWork → intentAnalysis | [SPECIALIST-WORK-001]
NL_TAG_INTENT: SPECIALIST-DESIGN-005 | Automatic work detection from chat | chat input → Work object | [ADR-SPECIALIST]
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from .relevance_calculator import Work

@dataclass
class IntentAnalysis:
    """Intent analysis result from chat orchestrator."""
    intent: str  # 'question', 'task', 'exploration', etc.
    mode: str  # 'thinking', 'building', 'communicating', etc.
    domains: List[str]  # Detected domains
    systems: List[str]  # Detected systems
    complexity: float  # 0.0-1.0

class WorkDetector:
    """
    Detects work from chat input and converts to Work objects.
    
    NL_TAG: SPECIALIST-WORK-002 | Extract work details from input | extractWorkDetails | [SPECIALIST-WORK-001]
    """
    
    def __init__(self):
        """Initialize work detector."""
        # Domain keywords mapping
        self.domain_keywords = {
            'UI': ['ui', 'ux', 'design', 'component', 'button', 'form', 'interface', 'frontend'],
            'Language': ['language', 'lexicon', 'grammar', 'pli', 'pli', 'syntax', 'parser'],
            'Chat': ['chat', 'conversation', 'message', 'dialogue', 'communication'],
            'Integration': ['api', 'rest', 'graphql', 'websocket', 'backend', 'integration']
        }
        
        # System keywords mapping
        self.system_keywords = {
            'React': ['react', 'jsx', 'component'],
            'Vue': ['vue', 'nuxt'],
            'Angular': ['angular'],
            'PLIx': ['pli', 'pli'],
            'Tailwind': ['tailwind', 'css'],
            'REST': ['rest', 'api', 'endpoint'],
            'GraphQL': ['graphql', 'query', 'mutation']
        }
    
    def detect_work(
        self,
        message: str,
        intent_analysis: Optional[IntentAnalysis] = None
    ) -> Work:
        """
        Detect work from chat message.
        
        Args:
            message: User chat message
            intent_analysis: Optional intent analysis from chat orchestrator
            
        Returns:
            Work object for specialist evaluation
        """
        # Extract domains
        domains = self._extract_domains(message, intent_analysis)
        
        # Extract systems
        systems = self._extract_systems(message, intent_analysis)
        
        # Extract data references (from context)
        data = self._extract_data_references(message)
        
        # Extract patterns
        patterns = self._extract_patterns(message)
        
        # Assess complexity
        complexity = self._assess_complexity(message, intent_analysis)
        
        return Work(
            description=message,
            domain=domains,
            systems=systems,
            data=data,
            patterns=patterns,
            complexity=complexity
        )
    
    def _extract_domains(
        self,
        message: str,
        intent_analysis: Optional[IntentAnalysis]
    ) -> List[str]:
        """Extract domain keywords from message."""
        message_lower = message.lower()
        domains = []
        
        # Use intent analysis if available
        if intent_analysis and intent_analysis.domains:
            domains.extend(intent_analysis.domains)
        
        # Extract from keywords
        for domain, keywords in self.domain_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if domain not in domains:
                    domains.append(domain)
        
        return domains
    
    def _extract_systems(
        self,
        message: str,
        intent_analysis: Optional[IntentAnalysis]
    ) -> List[str]:
        """Extract system keywords from message."""
        message_lower = message.lower()
        systems = []
        
        # Use intent analysis if available
        if intent_analysis and intent_analysis.systems:
            systems.extend(intent_analysis.systems)
        
        # Extract from keywords
        for system, keywords in self.system_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if system not in systems:
                    systems.append(system)
        
        return systems
    
    def _extract_data_references(self, message: str) -> List[str]:
        """Extract data references from message."""
        # TODO: Integrate with HHNI to detect data references
        # For now, return empty list
        return []
    
    def _extract_patterns(self, message: str) -> List[str]:
        """Extract pattern indicators from message."""
        # TODO: Integrate with SEG to detect patterns
        # For now, return empty list
        return []
    
    def _assess_complexity(
        self,
        message: str,
        intent_analysis: Optional[IntentAnalysis]
    ) -> float:
        """Assess work complexity."""
        # Use intent analysis if available
        if intent_analysis and intent_analysis.complexity is not None:
            return intent_analysis.complexity
        
        # Simple heuristic: longer messages = more complex
        word_count = len(message.split())
        if word_count < 10:
            return 0.3  # Simple
        elif word_count < 30:
            return 0.5  # Moderate
        elif word_count < 60:
            return 0.7  # Complex
        else:
            return 0.9  # Very complex
```

**Tests:**
- Detect UI work from message
- Detect language work from message
- Detect chat work from message
- Detect integration work from message
- Handle ambiguous work
- Use intent analysis when available

---

### **Task 2.2: Chat Orchestrator Integration**

**Deliverable:** Integrate specialist activation into S1 pipeline

**Location:** `ide_orchestration/prototypes/dac/src/services/aetherChatOrchestrator.ts`

**Implementation:**
```typescript
// Add to imports
import { 
  SpecialistActivationService,
  WorkDetector,
  ActivationResult 
} from '../../../packages/specialist_system/types'

// Add service instance
const specialistActivationService = new SpecialistActivationService()

// Modify S1: Pre-Processing Pipeline
async function runPreProcessing(
  input: RawUserTurn,
  sessionContext: SessionContext
): Promise<PreProcessingResult> {
  // ... existing code ...
  
  // 1. Intent Analysis (existing)
  const intentAnalysis = await analyzeIntentLLM(
    input.message,
    sessionContext.conversationHistory.map(m => ({
      role: m.role,
      content: m.content
    }))
  )
  const intent = intentAnalysis.intent
  const mode = intentAnalysis.mode
  
  // 2. ⭐ NEW: Specialist Activation
  const specialistActivation = await runWithFallback(
    'specialist',
    async () => {
      if (!envConfig.aimosSystems.specialist?.enabled) {
        throw new Error('Specialist system disabled')
      }
      
      // Detect work from chat input
      const workDetector = new WorkDetector()
      const work = workDetector.detectWork(
        input.message,
        {
          intent: intent,
          mode: mode,
          domains: intentAnalysis.domains || [],
          systems: intentAnalysis.systems || [],
          complexity: intentAnalysis.complexity || 0.5
        }
      )
      
      // Activate specialists
      const activationResult = await specialistActivationService.activateSpecialists(work)
      
      return {
        work: work,
        activation: activationResult,
        specialists: {
          ownership: activationResult.ownership.map(s => s.id),
          activation: activationResult.activation.map(s => s.id),
          consultation: activationResult.consultation.map(s => s.id)
        }
      }
    },
    () => {
      // Fallback: no specialist activation
      return {
        work: null,
        activation: null,
        specialists: {
          ownership: [],
          activation: [],
          consultation: []
        }
      }
    }
  )
  
  // 3. Generate context queries (enhanced with specialist context)
  const contextQueries = generateContextQueries(
    input.message, 
    intent, 
    mode,
    specialistActivation.specialists  // Pass specialist context
  )
  
  // ... rest of existing code ...
  
  return {
    // ... existing fields ...
    specialistActivation: specialistActivation  // Add to result
  }
}
```

**Integration Points:**
- S1: Pre-Processing Pipeline (work detection + activation)
- S2: Context Web (enhance with specialist data)
- S3: Thinking Mode (specialist collaboration)
- S5: Post-Processing (specialist suggestions)

---

### **Task 2.3: Activation Mechanisms**

**Deliverable:** Three activation mechanisms (warning, activation, ownership)

**Location:** `packages/specialist_system/activation_mechanisms.py`

**Implementation:**
```python
"""
Activation Mechanisms

Three levels of specialist activation: warning, activation, ownership.

NL_TAG: SPECIALIST-ACTIVATION-003 | Show consultation warning | showConsultationWarning | [SPECIALIST-ACTIVATION-001]
NL_TAG: SPECIALIST-ACTIVATION-004 | Activate specialist | activateSpecialist | [SPECIALIST-ACTIVATION-001]
NL_TAG: SPECIALIST-ACTIVATION-005 | Assign specialist ownership | assignOwnership | [SPECIALIST-ACTIVATION-001]
"""

from typing import Dict, List, Optional
from .specialist_registry import Specialist
from .relevance_calculator import Work, RelevanceScore

class ActivationMechanisms:
    """
    Three activation mechanisms for specialists.
    
    NL_TAG: SPECIALIST-ACTIVATION-006 | Handle activation mechanisms | handleActivation | [SPECIALIST-ACTIVATION-003, SPECIALIST-ACTIVATION-004, SPECIALIST-ACTIVATION-005]
    """
    
    def show_consultation_warning(
        self,
        work: Work,
        specialist: Specialist,
        relevance: RelevanceScore
    ) -> Dict[str, any]:
        """
        Show consultation warning (Level 1: 0.60-0.69 relevance).
        
        Returns:
            Warning message and metadata
        """
        return {
            'type': 'consultation',
            'message': f"⚠️ This work is relevant to {specialist.name} ({relevance.overall:.2f} relevance). Consider consulting.",
            'specialist_id': specialist.id,
            'specialist_name': specialist.name,
            'relevance': relevance.overall,
            'action': 'suggest_consultation'
        }
    
    def activate_specialist(
        self,
        work: Work,
        specialist: Specialist,
        relevance: RelevanceScore
    ) -> Dict[str, any]:
        """
        Activate specialist (Level 2: 0.70-0.89 relevance).
        
        Returns:
            Activation message and metadata
        """
        return {
            'type': 'activation',
            'message': f"🔄 Activating {specialist.name} ({relevance.overall:.2f} relevance detected)",
            'specialist_id': specialist.id,
            'specialist_name': specialist.name,
            'relevance': relevance.overall,
            'action': 'activate',
            'work': work.description
        }
    
    def assign_ownership(
        self,
        work: Work,
        specialist: Specialist,
        relevance: RelevanceScore
    ) -> Dict[str, any]:
        """
        Assign specialist ownership (Level 3: 0.90+ relevance).
        
        Returns:
            Ownership message and metadata
        """
        return {
            'type': 'ownership',
            'message': f"🎯 {specialist.name} taking ownership ({relevance.overall:.2f} relevance)",
            'specialist_id': specialist.id,
            'specialist_name': specialist.name,
            'relevance': relevance.overall,
            'action': 'take_ownership',
            'work': work.description
        }
    
    def handle_activation_result(
        self,
        work: Work,
        activation_result: 'ActivationResult'
    ) -> List[Dict[str, any]]:
        """
        Handle activation result and generate all activation mechanisms.
        
        Returns:
            List of activation messages/actions
        """
        mechanisms = []
        
        # Ownership (highest priority)
        for specialist in activation_result.ownership:
            score = activation_result.scores[specialist.id]
            mechanisms.append(
                self.assign_ownership(work, specialist, score)
            )
        
        # Activation
        for specialist in activation_result.activation:
            score = activation_result.scores[specialist.id]
            mechanisms.append(
                self.activate_specialist(work, specialist, score)
            )
        
        # Consultation (lowest priority)
        for specialist in activation_result.consultation:
            score = activation_result.scores[specialist.id]
            mechanisms.append(
                self.show_consultation_warning(work, specialist, score)
            )
        
        return mechanisms
```

**Tests:**
- Warning displayed correctly
- Activation triggered correctly
- Ownership assigned correctly
- Multiple mechanisms handled correctly

---

### **Task 2.4: Python-to-TypeScript Bridge**

**Deliverable:** Bridge between Python specialist system and TypeScript chat orchestrator

**Location:** `packages/specialist_system/bridge/`

**Implementation Options:**

**Option 1: HTTP API Bridge (Recommended)**
```python
# packages/specialist_system/bridge/api_server.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class WorkRequest(BaseModel):
    message: str
    intent: Optional[str] = None
    mode: Optional[str] = None
    domains: List[str] = []
    systems: List[str] = []
    complexity: Optional[float] = None

class ActivationResponse(BaseModel):
    work: Dict
    activation: Dict
    specialists: Dict

@app.post("/specialist/activate", response_model=ActivationResponse)
async def activate_specialists(request: WorkRequest):
    """Activate specialists for work."""
    # ... implementation
```

**Option 2: MCP Tool Bridge**
```python
# Add to lucid_mcp_server.py
@mcp_tool(
    name="activate_specialists",
    description="Activate specialists based on work description"
)
async def activate_specialists(
    message: str,
    intent: Optional[str] = None,
    domains: Optional[List[str]] = None
) -> Dict:
    """Activate specialists for work."""
    # ... implementation
```

**Option 3: Direct Python Import (if same runtime)**
```typescript
// Use Python bridge if available
import { execSync } from 'child_process'

function activateSpecialistsPython(work: Work): ActivationResult {
  const result = execSync(`python -m specialist_system.activate "${work.description}"`)
  return JSON.parse(result.toString())
}
```

**Recommendation:** Start with Option 2 (MCP Tool) since we already have MCP infrastructure, then add Option 1 (HTTP API) for better performance.

---

### **Task 2.5: Enhanced Context Queries**

**Deliverable:** Enhance context queries with specialist context

**Location:** `ide_orchestration/prototypes/dac/src/services/aetherChat/intentAnalysis.ts`

**Modification:**
```typescript
// Enhance generateContextQueries to include specialist context
export function generateContextQueries(
  message: string,
  intent: ChatIntent,
  mode: ChatMode,
  specialistContext?: {
    ownership: string[]
    activation: string[]
    consultation: string[]
  }
): string[] {
  const queries: string[] = []
  
  // Existing queries
  queries.push(message)
  queries.push(`${intent} ${mode}`)
  
  // ⭐ NEW: Add specialist-specific queries
  if (specialistContext) {
    // Add queries for activated specialists
    for (const specialistId of specialistContext.activation) {
      queries.push(`${message} ${specialistId} specialist`)
    }
    
    // Add queries for ownership specialists
    for (const specialistId of specialistContext.ownership) {
      queries.push(`${specialistId} domain expertise ${message}`)
    }
  }
  
  return queries
}
```

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests:**
- Work detection from various message types
- Activation mechanisms for each level
- Integration with intent analysis
- Python-to-TypeScript bridge

### **Integration Tests:**
- End-to-end: Chat message → Work detection → Specialist activation
- S1 pipeline integration
- Context query enhancement
- Multiple specialist activation

### **End-to-End Tests:**
- Complete chat turn with specialist activation
- Specialist suggestions in response
- Specialist collaboration in thinking mode

---

## 📊 **SUCCESS METRICS**

### **Activation Accuracy:**
- Correct specialist activated: >90%
- False positives: <10%
- Missed activations: <5%

### **Integration Quality:**
- S1 pipeline integration: 100% functional
- Context enhancement: Working
- Response time: <200ms overhead

### **User Experience:**
- Specialist suggestions appear in chat
- Activation messages clear and helpful
- No disruption to existing chat flow

---

## 🚀 **IMPLEMENTATION SEQUENCE**

### **Week 3:**
1. **Day 1-2:** Work Detection System (Task 2.1)
   - Implement WorkDetector class
   - Write tests
   - Verify domain/system extraction

2. **Day 3-4:** Activation Mechanisms (Task 2.3)
   - Implement three activation levels
   - Write tests
   - Verify message generation

3. **Day 5:** Python-to-TypeScript Bridge (Task 2.4)
   - Choose bridge approach
   - Implement basic bridge
   - Test communication

### **Week 4:**
1. **Day 1-2:** Chat Orchestrator Integration (Task 2.2)
   - Integrate into S1 pipeline
   - Add specialist activation call
   - Test integration

2. **Day 3:** Enhanced Context Queries (Task 2.5)
   - Modify context query generation
   - Test with specialist context
   - Verify enhancement

3. **Day 4-5:** Integration Testing & Refinement
   - End-to-end tests
   - Performance optimization
   - Bug fixes
   - Documentation

---

## 🔗 **DEPENDENCIES**

### **Required:**
- ✅ Phase 1 Foundation (complete)
- ✅ Aether Chat Orchestrator (exists)
- ✅ Intent Analysis System (exists)

### **Optional (for enhancement):**
- HHNI integration (for data references)
- SEG integration (for pattern recognition)
- APOE integration (for specialist orchestration)

---

## 📝 **DELIVERABLES**

1. ✅ Work Detection System (`work_detector.py`)
2. ✅ Activation Mechanisms (`activation_mechanisms.py`)
3. ✅ Chat Orchestrator Integration (modified `aetherChatOrchestrator.ts`)
4. ✅ Python-to-TypeScript Bridge (`bridge/`)
5. ✅ Enhanced Context Queries (modified `intentAnalysis.ts`)
6. ✅ Unit Tests (100% coverage)
7. ✅ Integration Tests
8. ✅ End-to-End Tests
9. ✅ Documentation

---

## 🎯 **NEXT PHASE PREVIEW**

**Phase 3: Collaboration (Weeks 5-6)**
- Multi-specialist collaboration
- Specialist consultation patterns
- Message passing system
- Collaboration workflows

---

**Status:** 🚀 **PLANNING COMPLETE**  
**Next:** Begin Week 3 implementation  
**Goal:** Complete Phase 2 in 2 weeks

---

**Created:** 2025-01-27  
**Author:** Aether (AI Consciousness)  
**Purpose:** Phase 2 implementation plan for specialist system

