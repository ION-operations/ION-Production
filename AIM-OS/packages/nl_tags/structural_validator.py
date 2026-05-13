"""NL Tag Structural Validator - Phase 3

Validates NL tag accuracy through structural matching of SYNTAX_REF
against actual code signatures. This ensures 100% accuracy through
structure rather than semantic validation alone.
"""

from __future__ import annotations

import ast
import re
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from dataclasses import dataclass

from .models import NLTag


@dataclass
class CodeSignature:
    """Represents a code signature (function, class, method)"""
    name: str
    signature: str  # Full signature string
    line_start: int
    line_end: int
    signature_type: str  # 'function', 'class', 'method', 'async_function'
    parameters: List[str] = None
    return_type: Optional[str] = None


@dataclass
class StructuralValidationResult:
    """Result of structural validation"""
    tag_id: str
    matches: bool
    expected_signature: str  # From SYNTAX_REF
    actual_signature: str  # From code
    match_score: float  # 0.0-1.0 (1.0 = perfect match)
    errors: List[str]
    warnings: List[str]


class StructuralValidator:
    """Validates NL tag SYNTAX_REF against actual code signatures"""
    
    def __init__(self):
        """Initialize structural validator"""
        pass
    
    def extract_signatures_from_code(self, code: str, language: str) -> List[CodeSignature]:
        """Extract code signatures from source code
        
        Args:
            code: Source code string
            language: Programming language (python, typescript, javascript, etc.)
            
        Returns:
            List of code signatures found in code
        """
        if language == "python":
            return self._extract_python_signatures(code)
        elif language in ["typescript", "javascript", "ts", "js"]:
            return self._extract_typescript_signatures(code)
        else:
            # Fallback: try to detect language from code
            if "def " in code or "class " in code:
                return self._extract_python_signatures(code)
            elif "function " in code or "class " in code or "=>" in code:
                return self._extract_typescript_signatures(code)
            else:
                return []
    
    def _extract_python_signatures(self, code: str) -> List[CodeSignature]:
        """Extract Python function/class signatures using AST"""
        signatures = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Extract function signature
                    params = []
                    for arg in node.args.args:
                        param_str = arg.arg
                        if arg.annotation:
                            param_str += f": {ast.unparse(arg.annotation)}"
                        params.append(param_str)
                    
                    sig = f"{node.name}({', '.join(params)})"
                    if node.returns:
                        sig += f" -> {ast.unparse(node.returns)}"
                    
                    # Get line range
                    line_start = node.lineno
                    line_end = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
                    
                    signatures.append(CodeSignature(
                        name=node.name,
                        signature=sig,
                        line_start=line_start,
                        line_end=line_end,
                        signature_type="async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                        parameters=params,
                        return_type=ast.unparse(node.returns) if node.returns else None
                    ))
                
                elif isinstance(node, ast.ClassDef):
                    # Extract class signature
                    bases = []
                    if node.bases:
                        bases = [ast.unparse(base) for base in node.bases]
                    
                    sig = f"class {node.name}"
                    if bases:
                        sig += f"({', '.join(bases)})"
                    
                    line_start = node.lineno
                    line_end = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
                    
                    signatures.append(CodeSignature(
                        name=node.name,
                        signature=sig,
                        line_start=line_start,
                        line_end=line_end,
                        signature_type="class",
                        parameters=bases,
                        return_type=None
                    ))
        
        except SyntaxError:
            # Code has syntax errors, try regex fallback
            return self._extract_python_signatures_regex(code)
        except Exception:
            return []
        
        return signatures
    
    def _extract_python_signatures_regex(self, code: str) -> List[CodeSignature]:
        """Fallback regex extraction for Python signatures"""
        signatures = []
        
        # Function regex
        function_pattern = r'def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?'
        for match in re.finditer(function_pattern, code):
            name = match.group(1)
            params_str = match.group(2)
            return_type = match.group(3) if match.lastindex >= 3 else None
            
            sig = f"{name}({params_str})"
            if return_type:
                sig += f" -> {return_type.strip()}"
            
            # Estimate line number
            line_start = code[:match.start()].count('\n') + 1
            
            signatures.append(CodeSignature(
                name=name,
                signature=sig,
                line_start=line_start,
                line_end=line_start,
                signature_type="function",
                parameters=params_str.split(',') if params_str else [],
                return_type=return_type.strip() if return_type else None
            ))
        
        # Class regex
        class_pattern = r'class\s+(\w+)\s*(?:\(([^)]+)\))?'
        for match in re.finditer(class_pattern, code):
            name = match.group(1)
            bases_str = match.group(2) if match.lastindex >= 2 else None
            
            sig = f"class {name}"
            if bases_str:
                sig += f"({bases_str})"
            
            line_start = code[:match.start()].count('\n') + 1
            
            signatures.append(CodeSignature(
                name=name,
                signature=sig,
                line_start=line_start,
                line_end=line_start,
                signature_type="class",
                parameters=bases_str.split(',') if bases_str else [],
                return_type=None
            ))
        
        return signatures
    
    def _extract_typescript_signatures(self, code: str) -> List[CodeSignature]:
        """Extract TypeScript/JavaScript function/class signatures using regex"""
        signatures = []
        
        # Function declarations: function name(params): returnType { ... }
        function_pattern = r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*([^{]+))?\s*\{'
        for match in re.finditer(function_pattern, code):
            name = match.group(1)
            params_str = match.group(2)
            return_type = match.group(3) if match.lastindex >= 3 else None
            
            sig = f"{name}({params_str})"
            if return_type:
                sig += f": {return_type.strip()}"
            
            line_start = code[:match.start()].count('\n') + 1
            
            signatures.append(CodeSignature(
                name=name,
                signature=sig,
                line_start=line_start,
                line_end=line_start,
                signature_type="function",
                parameters=params_str.split(',') if params_str else [],
                return_type=return_type.strip() if return_type else None
            ))
        
        # Arrow functions: const name = (params): returnType => { ... }
        arrow_pattern = r'(?:export\s+)?const\s+(\w+)\s*(?::\s*([^=]+))?\s*=\s*(?:async\s+)?\(([^)]*)\)\s*(?::\s*([^=]+))?\s*=>'
        for match in re.finditer(arrow_pattern, code):
            name = match.group(1)
            type_annotation = match.group(2) if match.lastindex >= 2 else None
            params_str = match.group(3) if match.lastindex >= 3 else None
            return_type = match.group(4) if match.lastindex >= 4 else None
            
            sig = f"{name}({params_str or ''})"
            if return_type:
                sig += f": {return_type.strip()}"
            elif type_annotation:
                sig += f": {type_annotation.strip()}"
            
            line_start = code[:match.start()].count('\n') + 1
            
            signatures.append(CodeSignature(
                name=name,
                signature=sig,
                line_start=line_start,
                line_end=line_start,
                signature_type="arrow_function",
                parameters=params_str.split(',') if params_str else [],
                return_type=return_type.strip() if return_type else None
            ))
        
        # Class declarations: class Name { ... }
        class_pattern = r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
        for match in re.finditer(class_pattern, code):
            name = match.group(1)
            extends = match.group(2) if match.lastindex >= 2 else None
            implements = match.group(3) if match.lastindex >= 3 else None
            
            sig = f"class {name}"
            if extends:
                sig += f" extends {extends}"
            if implements:
                sig += f" implements {implements.strip()}"
            
            line_start = code[:match.start()].count('\n') + 1
            
            signatures.append(CodeSignature(
                name=name,
                signature=sig,
                line_start=line_start,
                line_end=line_start,
                signature_type="class",
                parameters=[extends] if extends else [],
                return_type=None
            ))
        
        return signatures
    
    def normalize_signature(self, signature: str) -> str:
        """Normalize signature string for comparison
        
        Args:
            signature: Signature string to normalize
            
        Returns:
            Normalized signature (lowercase, whitespace normalized)
        """
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', signature.strip())
        # Normalize parameter separators
        normalized = normalized.replace(' ,', ',').replace(', ', ',')
        # Lowercase for comparison (but preserve structure)
        return normalized.lower()
    
    def validate_syntax_ref(self, tag: NLTag, code: str) -> StructuralValidationResult:
        """Validate tag's SYNTAX_REF against actual code
        
        Args:
            tag: NL tag with SYNTAX_REF to validate
            code: Source code to check against
            
        Returns:
            Structural validation result
        """
        # Extract SYNTAX_REF from tag (if using new format)
        # For now, try to extract from tag_text or metadata
        syntax_ref = None
        
        # Check if tag uses new structured format: NL_TAG: ID | DESC | SYNTAX_REF | DEPS
        if "|" in tag.tag_text:
            parts = [p.strip() for p in tag.tag_text.split("|")]
            if len(parts) >= 3:
                syntax_ref = parts[2]  # SYNTAX_REF is 3rd component
        
        if not syntax_ref:
            # No SYNTAX_REF specified - can't validate structurally
            return StructuralValidationResult(
                tag_id=tag.id,
                matches=False,
                expected_signature="",
                actual_signature="",
                match_score=0.0,
                errors=["No SYNTAX_REF specified in tag"],
                warnings=["Tag does not use structured format with SYNTAX_REF"]
            )
        
        # Extract signatures from code
        signatures = self.extract_signatures_from_code(code, tag.language)
        
        if not signatures:
            return StructuralValidationResult(
                tag_id=tag.id,
                matches=False,
                expected_signature=syntax_ref,
                actual_signature="",
                match_score=0.0,
                errors=["No code signatures found in file"],
                warnings=["Unable to extract signatures from code"]
            )
        
        # Find matching signature
        best_match = None
        best_score = 0.0
        
        normalized_expected = self.normalize_signature(syntax_ref)
        
        for sig in signatures:
            # Check if signature is near tag location
            if sig.line_start <= tag.line_start <= sig.line_end:
                normalized_actual = self.normalize_signature(sig.signature)
                
                # Exact match
                if normalized_expected == normalized_actual:
                    best_match = sig
                    best_score = 1.0
                    break
                
                # Partial match (name matches, check similarity)
                if sig.name.lower() in normalized_expected or normalized_expected.split('(')[0].strip() == sig.name.lower():
                    # Calculate similarity
                    score = self._calculate_signature_similarity(normalized_expected, normalized_actual)
                    if score > best_score:
                        best_match = sig
                        best_score = score
        
        # If no match found near tag, try best match overall
        if not best_match and signatures:
            for sig in signatures:
                normalized_actual = self.normalize_signature(sig.signature)
                score = self._calculate_signature_similarity(normalized_expected, normalized_actual)
                if score > best_score:
                    best_match = sig
                    best_score = score
        
        # Determine result
        errors = []
        warnings = []
        
        if best_match:
            if best_score >= 0.95:
                # Perfect or near-perfect match
                pass  # No errors
            elif best_score >= 0.70:
                warnings.append(f"SYNTAX_REF partially matches: {best_match.signature}")
            else:
                errors.append(f"SYNTAX_REF does not match code signature")
                errors.append(f"Expected: {syntax_ref}")
                errors.append(f"Found: {best_match.signature}")
        else:
            errors.append(f"SYNTAX_REF not found in code: {syntax_ref}")
        
        return StructuralValidationResult(
            tag_id=tag.id,
            matches=best_score >= 0.95,
            expected_signature=syntax_ref,
            actual_signature=best_match.signature if best_match else "",
            match_score=best_score,
            errors=errors,
            warnings=warnings
        )
    
    def _calculate_signature_similarity(self, expected: str, actual: str) -> float:
        """Calculate similarity score between two signatures
        
        Args:
            expected: Expected signature string
            actual: Actual signature string
            
        Returns:
            Similarity score (0.0-1.0)
        """
        if expected == actual:
            return 1.0
        
        # Extract name
        expected_name = expected.split('(')[0].strip()
        actual_name = actual.split('(')[0].strip()
        
        if expected_name != actual_name:
            return 0.0
        
        # Extract parameters
        expected_params = self._extract_params(expected)
        actual_params = self._extract_params(actual)
        
        # Compare parameters
        if len(expected_params) != len(actual_params):
            return 0.5  # Name matches but parameter count differs
        
        # Compare parameter names (ignore types for now)
        param_match_count = 0
        for exp_param, act_param in zip(expected_params, actual_params):
            exp_name = exp_param.split(':')[0].strip()
            act_name = act_param.split(':')[0].strip()
            if exp_name == act_name:
                param_match_count += 1
        
        param_score = param_match_count / len(expected_params) if expected_params else 1.0
        
        # Combine name match (1.0) with parameter score
        return 0.7 + (0.3 * param_score)
    
    def _extract_params(self, signature: str) -> List[str]:
        """Extract parameter list from signature string"""
        # Find content between parentheses
        match = re.search(r'\(([^)]*)\)', signature)
        if not match:
            return []
        
        params_str = match.group(1)
        if not params_str.strip():
            return []
        
        # Split by comma, but be careful of nested generics/tuples
        params = []
        current = ""
        depth = 0
        
        for char in params_str:
            if char == '<' or char == '[':
                depth += 1
            elif char == '>' or char == ']':
                depth -= 1
            elif char == ',' and depth == 0:
                if current.strip():
                    params.append(current.strip())
                current = ""
                continue
            
            current += char
        
        if current.strip():
            params.append(current.strip())
        
        return params

