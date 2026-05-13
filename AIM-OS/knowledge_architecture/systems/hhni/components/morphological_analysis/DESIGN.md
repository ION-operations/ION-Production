# Morphological Analysis Integration Design

**Date:** 2025-01-27  
**Status:** 📋 **DESIGN** - Phase 1 Enhancement  
**Component:** HHNI SUBWORD Level Enhancement

---

## 🎯 **PURPOSE**

Enhance HHNI's SUBWORD level (Level 6) with morphological analysis to understand words through their parts (prefix, root, suffix). This enables:
- Understanding new words from parts ("psychoacoustics" = "psycho" + "acoustics")
- Learned subword operations (negation, tense, etc.)
- Compositional meaning understanding

---

## 📊 **CURRENT STATE**

### **HHNI SUBWORD Level (Current):**
```python
def _tokenize(sentence: str) -> List[str]:
    tokens = re.findall(r"\w+|\S", sentence)
    return [token for token in tokens if token.strip()]
```

**Limitations:**
- Basic regex tokenization
- No morphological analysis
- No understanding of word parts
- No learned operations

---

## 🏗️ **DESIGN: Morphological Analysis Integration**

### **1. Morphological Decomposition Schema**

**New Data Structure:**
```python
@dataclass
class MorphologicalDecomposition:
    """Morphological analysis of a word."""
    word: str                          # Original word
    root: Optional[str]                # Core meaning (e.g., "happy")
    prefix: Optional[str]              # Prefix (e.g., "un-")
    suffix: Optional[str]              # Suffix (e.g., "-ness")
    stem: Optional[str]                # Stem (root + base)
    lemma: Optional[str]               # Dictionary form
    pos_tag: Optional[str]             # Part of speech
    operations: List[str]              # Learned operations (e.g., ["negation", "noun_formation"])
    parts: List[str]                   # All parts (prefix, root, suffix)
```

**Example:**
```python
MorphologicalDecomposition(
    word="unhappiness",
    root="happy",
    prefix="un-",
    suffix="-ness",
    stem="happi",
    lemma="unhappiness",
    pos_tag="NN",
    operations=["negation", "noun_formation"],
    parts=["un-", "happy", "-ness"]
)
```

---

### **2. Enhanced Tokenization Function**

**New Function:**
```python
def _tokenize_with_morphology(sentence: str) -> List[Tuple[str, MorphologicalDecomposition]]:
    """Tokenize sentence with morphological analysis."""
    # 1. Basic tokenization (existing)
    tokens = _tokenize(sentence)
    
    # 2. Morphological analysis for each token
    results = []
    for token in tokens:
        decomposition = analyze_morphology(token)
        results.append((token, decomposition))
    
    return results
```

**Integration Point:**
- Replace `_tokenize()` calls in `index_document()` with `_tokenize_with_morphology()`
- Store `MorphologicalDecomposition` in `IndexNode.metadata`

---

### **3. Morphological Analysis Implementation**

**Library Options:**
1. **spaCy** (Recommended):
   - Fast, production-ready
   - Good morphological analysis
   - Dependency: `spacy` + language model

2. **NLTK** (Alternative):
   - Comprehensive but slower
   - Good for research
   - Dependency: `nltk` + data downloads

3. **Custom** (Future):
   - Learn subword operations from data
   - Domain-specific rules

**Initial Implementation (spaCy):**
```python
import spacy

# Load model (once, cached)
_nlp = None

def get_nlp_model():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback to basic tokenization
            return None
    return _nlp

def analyze_morphology(word: str) -> MorphologicalDecomposition:
    """Analyze word morphology using spaCy."""
    nlp = get_nlp_model()
    if nlp is None:
        # Fallback: basic decomposition
        return MorphologicalDecomposition(
            word=word,
            root=word,
            prefix=None,
            suffix=None,
            stem=word,
            lemma=word,
            pos_tag=None,
            operations=[],
            parts=[word]
        )
    
    doc = nlp(word)
    if not doc:
        return MorphologicalDecomposition(word=word, ...)
    
    token = doc[0]
    
    # Extract morphological features
    root = token.lemma_ if token.lemma_ != word else None
    pos_tag = token.pos_
    
    # Infer prefix/suffix (heuristic)
    prefix, suffix = _infer_affixes(word, root)
    
    # Infer operations
    operations = _infer_operations(prefix, suffix, pos_tag)
    
    return MorphologicalDecomposition(
        word=word,
        root=root,
        prefix=prefix,
        suffix=suffix,
        stem=token.lemma_,
        lemma=token.lemma_,
        pos_tag=pos_tag,
        operations=operations,
        parts=_combine_parts(prefix, root, suffix)
    )
```

---

### **4. Learned Subword Operations**

**Operation Types:**
- **Negation:** "un-", "non-", "in-", "dis-"
- **Tense:** "-ed", "-ing", "-s"
- **Formation:** "-ness" (noun), "-ly" (adverb), "-able" (adjective)
- **Intensity:** "re-", "pre-", "over-"

**Learning Mechanism:**
```python
def _infer_operations(prefix: Optional[str], suffix: Optional[str], pos_tag: str) -> List[str]:
    """Infer learned operations from morphology."""
    operations = []
    
    # Prefix operations
    if prefix:
        if prefix in ["un-", "non-", "in-", "dis-"]:
            operations.append("negation")
        elif prefix in ["re-"]:
            operations.append("repetition")
        elif prefix in ["pre-"]:
            operations.append("temporal_before")
    
    # Suffix operations
    if suffix:
        if suffix in ["-ness", "-ity"]:
            operations.append("noun_formation")
        elif suffix in ["-ly"]:
            operations.append("adverb_formation")
        elif suffix in ["-able", "-ible"]:
            operations.append("adjective_formation")
        elif suffix in ["-ed"]:
            operations.append("past_tense")
        elif suffix in ["-ing"]:
            operations.append("present_participle")
    
    return operations
```

---

### **5. CMC Integration**

**Store Morphological Metadata:**
```python
# In CMC atom creation
atom = Atom(
    id=atom_id,
    modality="text",
    content_ref={"inline": token},
    embedding=token_embedding,
    tags=[
        {"key": "morphology_root", "value": decomposition.root},
        {"key": "morphology_prefix", "value": decomposition.prefix},
        {"key": "morphology_suffix", "value": decomposition.suffix},
        {"key": "morphology_operations", "value": ",".join(decomposition.operations)},
    ],
    metadata={
        "morphology": decomposition.model_dump(),
        "hhni_path": hhni_path,
    },
    ...
)
```

---

### **6. SEG Integration**

**Link Subword Parts:**
```python
# Create SEG entities for morphological parts
if decomposition.prefix:
    prefix_entity = Entity(
        type="morphological_part",
        name=f"prefix:{decomposition.prefix}",
        attributes={"part_type": "prefix", "operation": "negation" if "negation" in decomposition.operations else None}
    )
    seg_graph.add_entity(prefix_entity)
    seg_graph.add_relation(
        Relation(
            from_entity=word_entity.id,
            to_entity=prefix_entity.id,
            type=RelationType.DERIVES,
            attributes={"morphological": True}
        )
    )

if decomposition.root:
    root_entity = Entity(
        type="morphological_part",
        name=f"root:{decomposition.root}",
        attributes={"part_type": "root"}
    )
    seg_graph.add_entity(root_entity)
    seg_graph.add_relation(
        Relation(
            from_entity=word_entity.id,
            to_entity=root_entity.id,
            type=RelationType.DERIVES,
            attributes={"morphological": True}
        )
    )
```

---

## 🔧 **IMPLEMENTATION PLAN**

### **Step 1: Create Morphological Analysis Module**
- File: `packages/hhni/morphology.py`
- Functions: `analyze_morphology()`, `_infer_affixes()`, `_infer_operations()`
- Dependencies: `spacy` (optional, with fallback)

### **Step 2: Enhance Hierarchical Index**
- File: `packages/hhni/hierarchical_index.py`
- Replace `_tokenize()` with `_tokenize_with_morphology()`
- Store `MorphologicalDecomposition` in `IndexNode.metadata`

### **Step 3: Update CMC Integration**
- Store morphological metadata in atoms
- Add tags for morphological parts

### **Step 4: Update SEG Integration**
- Link subword parts in graph
- Add morphological relationship types

### **Step 5: Testing**
- Test morphological analysis accuracy
- Test fallback behavior (no spaCy)
- Test integration with HHNI indexing

---

## 📋 **DEPENDENCIES**

**Required:**
- Python 3.7+
- Existing HHNI infrastructure

**Optional (Recommended):**
- `spacy` package
- `en_core_web_sm` model (download: `python -m spacy download en_core_web_sm`)

**Fallback:**
- If spaCy not available, use basic tokenization (current behavior)

---

## 🎯 **SUCCESS CRITERIA**

**Phase 1 Success:**
- ✅ SUBWORD level includes morphological decomposition
- ✅ Can understand "unhappy" from "un-" + "happy"
- ✅ Subword operations learned (negation, tense, etc.)
- ✅ Morphological metadata stored in CMC
- ✅ Subword parts linked in SEG
- ✅ Fallback works (no spaCy available)

---

## 📚 **REFERENCES**

- **User Insights:** `knowledge_architecture/AETHER_MEMORY/investigations/SEMANTIC_ORGANIZATION_ENHANCEMENTS.md`
- **Enhancement Plan:** `knowledge_architecture/AETHER_MEMORY/investigations/SEMANTIC_ORGANIZATION_ENHANCEMENT_PLAN.md`
- **HHNI Architecture:** `knowledge_architecture/systems/hhni/L2_architecture.md`
- **HHNI Hierarchical Index:** `packages/hhni/hierarchical_index.py`

---

**Status:** 📋 **DESIGN COMPLETE** - Ready for implementation  
**Next:** Create morphological analysis module (`packages/hhni/morphology.py`)

