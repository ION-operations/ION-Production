"""
LLM-Assisted NL Tag Generation

Uses fast LLM (Cerebras) to generate high-quality NL tags in real-time.
Provides templates, suggestions, and auto-tagging for new code.

Features:
- Real-time tag generation as code is written
- Context-aware tag suggestions
- Integration point detection
- Design intent extraction
- Schema validation detection
- Teaching mode (shows examples, learns from feedback)

Usage:
    # Generate tags for new function
    tagger = LLMAssistedTagger(api_key=os.getenv("CEREBRAS_API_KEY"))
    
    code = '''
    def create_witness(operation, inputs, outputs):
        \"\"\"Create VIF witness with provenance\"\"\"
        ...
    '''
    
    tags = tagger.generate_tags(code, system="vif", context="witness creation")
    # Returns: [NL_TAG, NL_TAG_CONNECT, NL_TAG_INTENT, NL_TAG_SPEC]
"""

from __future__ import annotations

import os
import ast
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import requests


@dataclass
class TagSuggestion:
    """LLM-generated tag suggestion"""
    tag_id: str
    tag_type: str  # "TAG", "CONNECT", "INTENT", "SPEC"
    description: str
    syntax_ref: str
    dependencies: List[str]
    confidence: float  # LLM's confidence in this suggestion
    rationale: str  # Why this tag was suggested


class LLMAssistedTagger:
    """LLM-assisted tag generation using fast API (Cerebras)"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: str = "https://api.cerebras.ai/v1",
        model: str = "llama3.1-70b"  # Fast Cerebras model
    ):
        """Initialize LLM-assisted tagger
        
        Args:
            api_key: Cerebras API key
            api_base: API base URL
            model: Model to use (llama3.1-70b for speed/quality balance)
        """
        self.api_key = api_key or os.getenv("CEREBRAS_API_KEY")
        self.api_base = api_base
        self.model = model
        
        # Tag ID counters (per system-category)
        self.tag_counters: Dict[str, int] = {}
    
    def generate_tags(
        self,
        code: str,
        system: str,
        context: Optional[str] = None,
        existing_tags: Optional[List[str]] = None
    ) -> List[TagSuggestion]:
        """Generate NL tags for code using LLM
        
        Args:
            code: Code snippet to tag
            system: System name (e.g., "vif", "cmc", "apoe")
            context: Additional context about the code
            existing_tags: Existing tags in file (for reference)
            
        Returns:
            List of suggested tags
        """
        # Build prompt
        prompt = self._build_prompt(code, system, context, existing_tags)
        
        # Call LLM
        response = self._call_llm(prompt)
        
        # Parse suggestions
        suggestions = self._parse_suggestions(response, system)
        
        return suggestions
    
    def _build_prompt(
        self,
        code: str,
        system: str,
        context: Optional[str],
        existing_tags: Optional[List[str]]
    ) -> str:
        """Build prompt for LLM tag generation"""
        
        # Load examples from gold standards
        examples = self._load_examples(system)
        
        prompt = f"""You are an expert at creating NL tags for AI consciousness infrastructure code.

SYSTEM: {system.upper()}
CONTEXT: {context or "New code requiring tags"}

CODE TO TAG:
```python
{code}
```

NL TAG RULES:
1. NL_TAG: Primary function description
   Format: # NL_TAG: {system.upper()}-CATEGORY-NNN | description | function_sig(...) -> ReturnType | [dep_ids]

2. NL_TAG_CONNECT: Cross-system integrations  
   Format: # NL_TAG_CONNECT: {system.upper()}-CONNECT-NNN | integration desc | source → target | [source_id, target_id]

3. NL_TAG_INTENT: Design decisions
   Format: # NL_TAG_INTENT: {system.upper()}-DESIGN-NNN | design rationale | architectural_concept | [ADR-reference]

4. NL_TAG_SPEC: Schema validations
   Format: # NL_TAG_SPEC: {system.upper()}-SPEC-NNN | validation desc | validator_function | [schema_file]

EXAMPLES FROM {system.upper()} (Gold Standard):
{examples}

TASK:
Generate appropriate NL tags for the code above. For each tag:
1. Determine tag type (TAG required, CONNECT/INTENT/SPEC if applicable)
2. Generate unique tag ID with appropriate category
3. Write clear, specific description (not boilerplate!)
4. Match syntax_ref to actual code structure
5. Identify dependencies

OUTPUT FORMAT (JSON):
{{
  "tags": [
    {{
      "tag_type": "TAG",
      "tag_id": "{system.upper()}-CATEGORY-001",
      "description": "Clear description of what this does",
      "syntax_ref": "exact_function_signature",
      "dependencies": [],
      "confidence": 0.95,
      "rationale": "Why this tag"
    }}
  ]
}}

Generate tags now:"""
        
        return prompt
    
    def _load_examples(self, system: str) -> str:
        """Load gold standard examples for system"""
        # In real implementation, load from gold standard files
        # For now, return template examples
        
        examples = {
            "vif": """
# NL_TAG: VIF-WITNESS-001 | Create VIF witness envelope with provenance | create_witness(...) -> VIFWitness | []
# NL_TAG_CONNECT: VIF-CMC-001 | Witness stored in CMC as atom | create_witness → store_atom | [VIF-WITNESS-001, CMC-STORE-001]
# NL_TAG_INTENT: VIF-DESIGN-003 | Witnesses enable deterministic replay | cryptographic_hash + snapshot | [ADR-VIF-WITNESSES]
def create_witness(...) -> VIFWitness:
    \"\"\"Create VIF witness envelope with complete provenance\"\"\"
""",
            "cmc": """
# NL_TAG: CMC-STORE-001 | Store atom in CMC with bitemporal versioning | store_atom(atom) -> str | []
# NL_TAG_INTENT: CMC-DESIGN-001 | Bitemporal versioning enables never-delete principle | valid_time + transaction_time | [ADR-BITEMPORAL]
def store_atom(atom) -> str:
    \"\"\"Store atom in CMC with bitemporal tracking\"\"\"
""",
            "apoe": """
# NL_TAG: APOE-ORCH-001 | Orchestrate execution plan with role dispatch | orchestrate(plan) -> Result | []
# NL_TAG_CONNECT: APOE-VIF-001 | Uses VIF κ-gates for abstention | orchestrate → check_kappa_gate | [APOE-ORCH-001, VIF-GATE-001]
def orchestrate(plan) -> Result:
    \"\"\"Orchestrate execution plan\"\"\"
"""
        }
        
        return examples.get(system.lower(), "")
    
    def _call_llm(self, prompt: str) -> str:
        """Call Cerebras LLM API"""
        if not self.api_key:
            raise ValueError("Cerebras API key not set")
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are an expert NL tag generator for AI code."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,  # Low temperature for consistency
                    "max_tokens": 1000
                },
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            # Fallback to basic auto-tagging if LLM fails
            print(f"LLM API error: {e}")
            return "{\"tags\": []}"
    
    def _parse_suggestions(self, llm_response: str, system: str) -> List[TagSuggestion]:
        """Parse LLM response into tag suggestions"""
        try:
            # Extract JSON from response
            json_start = llm_response.find("{")
            json_end = llm_response.rfind("}") + 1
            json_str = llm_response[json_start:json_end]
            
            data = json.loads(json_str)
            tags_data = data.get("tags", [])
            
            suggestions = []
            for tag_data in tags_data:
                suggestion = TagSuggestion(
                    tag_id=tag_data.get("tag_id", ""),
                    tag_type=tag_data.get("tag_type", "TAG"),
                    description=tag_data.get("description", ""),
                    syntax_ref=tag_data.get("syntax_ref", ""),
                    dependencies=tag_data.get("dependencies", []),
                    confidence=tag_data.get("confidence", 0.80),
                    rationale=tag_data.get("rationale", "")
                )
                suggestions.append(suggestion)
            
            return suggestions
        
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return []
    
    def generate_tag_id(self, system: str, category: str) -> str:
        """Generate unique tag ID"""
        key = f"{system.upper()}-{category.upper()}"
        
        if key not in self.tag_counters:
            self.tag_counters[key] = 1
        
        tag_id = f"{system.upper()}-{category.upper()}-{self.tag_counters[key]:03d}"
        self.tag_counters[key] += 1
        
        return tag_id
    
    def teach_by_example(self, code: str, correct_tags: List[str]) -> None:
        """Learn from human-corrected tags (future: fine-tuning)"""
        # Store examples for future fine-tuning
        # For now, just track for statistics
        pass
    
    def format_tags(self, suggestions: List[TagSuggestion]) -> str:
        """Format suggestions as tag comments"""
        lines = []
        
        for sug in suggestions:
            deps_str = ", ".join(sug.dependencies) if sug.dependencies else ""
            
            if sug.tag_type == "TAG":
                line = f"# NL_TAG: {sug.tag_id} | {sug.description} | {sug.syntax_ref} | [{deps_str}]"
            elif sug.tag_type == "CONNECT":
                line = f"# NL_TAG_CONNECT: {sug.tag_id} | {sug.description} | {sug.syntax_ref} | [{deps_str}]"
            elif sug.tag_type == "INTENT":
                line = f"# NL_TAG_INTENT: {sug.tag_id} | {sug.description} | {sug.syntax_ref} | [{deps_str}]"
            elif sug.tag_type == "SPEC":
                line = f"# NL_TAG_SPEC: {sug.tag_id} | {sug.description} | {sug.syntax_ref} | [{deps_str}]"
            
            lines.append(line)
        
        return "\n".join(lines)


class RealTimeTaggingAssistant:
    """Real-time tagging assistant for IDE integration"""
    
    def __init__(self, llm_tagger: LLMAssistedTagger):
        self.llm_tagger = llm_tagger
        self.cache: Dict[str, List[TagSuggestion]] = {}
    
    def on_function_created(
        self,
        function_code: str,
        file_path: str,
        system: str
    ) -> str:
        """Called when new function is created
        
        Returns tag comments to insert above function.
        """
        # Generate tags
        suggestions = self.llm_tagger.generate_tags(
            code=function_code,
            system=system,
            context=f"New function in {file_path}"
        )
        
        # Format as comments
        tag_comments = self.llm_tagger.format_tags(suggestions)
        
        return tag_comments
    
    def on_file_saved(self, file_path: str) -> List[str]:
        """Called when file is saved - check for untagged functions"""
        # Scan file for functions without tags
        untagged = self._find_untagged_functions(file_path)
        
        if untagged:
            return [
                f"Warning: {len(untagged)} functions in {file_path} are not tagged:",
                *[f"  - {func}" for func in untagged[:5]]
            ]
        
        return []
    
    def _find_untagged_functions(self, file_path: str) -> List[str]:
        """Find functions without NL tags"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            lines = content.split('\n')
            
            untagged = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Check if previous line has NL_TAG
                    if node.lineno > 1:
                        prev_lines = lines[max(0, node.lineno-5):node.lineno-1]
                        has_tag = any("# NL_TAG" in line for line in prev_lines)
                        
                        if not has_tag and not node.name.startswith("_test"):
                            untagged.append(f"{node.name} (line {node.lineno})")
            
            return untagged
        
        except Exception:
            return []

