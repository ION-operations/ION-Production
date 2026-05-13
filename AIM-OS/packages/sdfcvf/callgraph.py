"""
Callgraph Builder for CONNECT Tag Validation

This module builds callgraphs from source code to validate NL_TAG_CONNECT tags.
CONNECT tags specify SOURCE → TARGET relationships for function calls.
The callgraph verifies these relationships actually exist in the code.

Features:
- Python AST-based callgraph construction
- Cross-module call detection
- Contract graph (OpenAPI, gRPC) integration
- CONNECT tag validation
- Missing edge detection and reporting

Usage:
    # Build callgraph
    builder = CallgraphBuilder()
    graph = builder.build_from_files(["file1.py", "file2.py"])
    
    # Validate CONNECT tags
    validator = CONNECTTagValidator()
    result = validator.validate(connect_tags, graph)
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import networkx as nx
from collections import defaultdict

# NL_TAG: SDFCVF-MODEL-020 | Call graph edge representation | CallEdge(caller: str, callee: str, call_type: str, file_path: str, line_number: int) | []
@dataclass
class CallEdge:
    """Represents a call from one function to another"""
    caller: str  # Fully qualified name (module.Class.method)
    callee: str  # Fully qualified name
    call_type: str  # "direct", "method", "cross_module", "external"
    file_path: str
    line_number: int

# NL_TAG: SDFCVF-MODEL-021 | Complete callgraph for codebase | Callgraph(graph: nx.DiGraph, edges: list[CallEdge], nodes: dict[str, dict[str, Any]]) | [SDFCVF-MODEL-020]
@dataclass
class Callgraph:
    """Complete callgraph for a codebase"""
    graph: nx.DiGraph  # NetworkX directed graph
    edges: list[CallEdge]
    nodes: dict[str, dict[str, Any]]  # node_name -> metadata
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if edge exists from source to target"""
        return self.graph.has_edge(source, target)
    
    def get_callers(self, node: str) -> list[str]:
        """Get all functions that call this node"""
        return list(self.graph.predecessors(node))
    
    def get_callees(self, node: str) -> list[str]:
        """Get all functions called by this node"""
        return list(self.graph.successors(node))
    
    def find_paths(self, source: str, target: str) -> list[list[str]]:
        """Find all paths from source to target"""
        if not self.graph.has_node(source) or not self.graph.has_node(target):
            return []
        try:
            return list(nx.all_simple_paths(self.graph, source, target, cutoff=10))
        except nx.NetworkXNoPath:
            return []

# NL_TAG: SDFCVF-CALLGRAPH-001 | Callgraph builder for CONNECT tag validation | CallgraphBuilder() | []
class CallgraphBuilder:
    """Build callgraph from Python source files"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.edges: list[CallEdge] = []
        self.nodes: dict[str, dict[str, Any]] = {}
        self.current_module = ""
        self.current_class = ""
        self.current_function = ""
        self.imports: dict[str, str] = {}  # alias -> full_name
    
    # NL_TAG: SDFCVF-CALLGRAPH-002 | Build callgraph from Python files | build_from_files(file_paths: list[str]) -> Callgraph | [SDFCVF-CALLGRAPH-001, SDFCVF-MODEL-021]
    def build_from_files(self, file_paths: list[str]) -> Callgraph:
        """Build callgraph from list of Python files"""
        self.graph = nx.DiGraph()
        self.edges = []
        self.nodes = {}
        
        for file_path in file_paths:
            self._process_file(file_path)
        
        return Callgraph(
            graph=self.graph,
            edges=self.edges,
            nodes=self.nodes
        )
    
    def _process_file(self, file_path: str) -> None:
        """Process a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            # Extract module name from file path
            path = Path(file_path)
            if path.stem == "__init__":
                self.current_module = path.parent.name
            else:
                self.current_module = path.stem
            
            # Reset imports for each file
            self.imports = {}
            
            # Visit AST
            self._visit_node(tree, file_path)
            
        except Exception as e:
            # Silently skip files with errors
            pass
    
    def _visit_node(self, node: ast.AST, file_path: str) -> None:
        """Visit AST node and extract call information"""
        if isinstance(node, ast.Import):
            self._process_import(node)
        elif isinstance(node, ast.ImportFrom):
            self._process_import_from(node)
        elif isinstance(node, ast.ClassDef):
            self._process_class(node, file_path)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._process_function(node, file_path)
        
        # Recursively visit children
        for child in ast.iter_child_nodes(node):
            self._visit_node(child, file_path)
    
    def _process_import(self, node: ast.Import) -> None:
        """Process 'import X' statements"""
        for alias in node.names:
            name = alias.name
            asname = alias.asname if alias.asname else alias.name
            self.imports[asname] = name
    
    def _process_import_from(self, node: ast.ImportFrom) -> None:
        """Process 'from X import Y' statements"""
        if node.module:
            for alias in node.names:
                name = alias.name
                asname = alias.asname if alias.asname else alias.name
                full_name = f"{node.module}.{name}"
                self.imports[asname] = full_name
    
    def _process_class(self, node: ast.ClassDef, file_path: str) -> None:
        """Process class definition"""
        old_class = self.current_class
        self.current_class = node.name
        
        # Add class as node
        class_fqn = self._get_fqn(node.name)
        self._add_node(class_fqn, "class", file_path, node.lineno)
        
        # Visit class body
        for child in node.body:
            self._visit_node(child, file_path)
        
        self.current_class = old_class
    
    def _process_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, file_path: str) -> None:
        """Process function/method definition"""
        old_function = self.current_function
        self.current_function = node.name
        
        # Add function as node
        func_fqn = self._get_fqn(node.name)
        func_type = "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"
        self._add_node(func_fqn, func_type, file_path, node.lineno)
        
        # Extract calls within function body
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                self._process_call(child, func_fqn, file_path)
        
        self.current_function = old_function
    
    def _process_call(self, node: ast.Call, caller_fqn: str, file_path: str) -> None:
        """Process function call"""
        callee_name = self._extract_call_name(node.func)
        if not callee_name:
            return
        
        # Resolve import aliases
        callee_fqn = self._resolve_name(callee_name)
        
        # Determine call type
        call_type = self._determine_call_type(callee_name, callee_fqn)
        
        # Add edge
        self._add_edge(
            caller=caller_fqn,
            callee=callee_fqn,
            call_type=call_type,
            file_path=file_path,
            line_number=node.lineno
        )
    
    def _extract_call_name(self, node: ast.AST) -> str | None:
        """Extract function name from call node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # Handle obj.method() calls
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.insert(0, current.id)
            return ".".join(parts)
        return None
    
    def _resolve_name(self, name: str) -> str:
        """Resolve name using import information"""
        # Check if it's an imported name
        parts = name.split(".")
        if parts[0] in self.imports:
            # Replace first part with full import path
            resolved = self.imports[parts[0]]
            if len(parts) > 1:
                resolved = f"{resolved}.{'.'.join(parts[1:])}"
            return resolved
        return name
    
    def _determine_call_type(self, name: str, fqn: str) -> str:
        """Determine type of call"""
        if "." in fqn and not name.startswith("self."):
            # Check if it's a cross-module call
            if fqn.startswith(self.current_module):
                return "method"
            else:
                return "cross_module"
        elif name.startswith("self."):
            return "method"
        else:
            return "direct"
    
    def _get_fqn(self, name: str) -> str:
        """Get fully qualified name for current context"""
        parts = [self.current_module]
        if self.current_class:
            parts.append(self.current_class)
        parts.append(name)
        return ".".join(parts)
    
    def _add_node(self, fqn: str, node_type: str, file_path: str, line_number: int) -> None:
        """Add node to graph"""
        if fqn not in self.nodes:
            self.nodes[fqn] = {
                "type": node_type,
                "file_path": file_path,
                "line_number": line_number
            }
            self.graph.add_node(fqn)
    
    def _add_edge(self, caller: str, callee: str, call_type: str, file_path: str, line_number: int) -> None:
        """Add edge to graph"""
        # Ensure both nodes exist
        if caller not in self.graph:
            self.graph.add_node(caller)
        if callee not in self.graph:
            self.graph.add_node(callee)
        
        # Add edge
        self.graph.add_edge(caller, callee)
        
        # Record edge
        edge = CallEdge(
            caller=caller,
            callee=callee,
            call_type=call_type,
            file_path=file_path,
            line_number=line_number
        )
        self.edges.append(edge)


@dataclass
class CONNECTValidationResult:
    """Result of CONNECT tag validation"""
    valid: bool
    missing_edges: list[tuple[str, str]]  # [(source, target), ...]
    invalid_tags: list[str]  # Tag IDs with no matching edges
    warnings: list[str]
    
    @property
    def passed(self) -> bool:
        """Check if validation passed"""
        return self.valid and len(self.missing_edges) == 0

# NL_TAG: SDFCVF-MODEL-022 | CONNECT tag validation result | CONNECTValidationResult(valid: bool, missing_edges: list[tuple[str, str]], invalid_tags: list[str], warnings: list[str]) | []
@dataclass
class CONNECTValidationResult:
    """Result of CONNECT tag validation"""
    valid: bool
    missing_edges: list[tuple[str, str]]  # [(source, target), ...]
    invalid_tags: list[str]  # Tag IDs with no matching edges
    warnings: list[str]
    
    @property
    def passed(self) -> bool:
        """Check if validation passed"""
        return self.valid and len(self.missing_edges) == 0


# NL_TAG: SDFCVF-CALLGRAPH-003 | CONNECT tag validator using callgraph | CONNECTTagValidator(strict: bool = True) | [SDFCVF-CALLGRAPH-002]
class CONNECTTagValidator:
    """Validate NL_TAG_CONNECT tags against callgraph"""
    
    def __init__(self, strict: bool = True):
        """
        Args:
            strict: If True, require exact matches. If False, allow fuzzy matching.
        """
        self.strict = strict
    
    # NL_TAG: SDFCVF-CALLGRAPH-004 | Validate CONNECT tags against callgraph | validate(connect_tags: list[Any], callgraph: Callgraph) -> CONNECTValidationResult | [SDFCVF-CALLGRAPH-003, SDFCVF-MODEL-022]
    def validate(self, connect_tags: list[Any], callgraph: Callgraph) -> CONNECTValidationResult:
        """
        Validate CONNECT tags against callgraph
        
        Args:
            connect_tags: List of NL_TAG_CONNECT tags (with .canonical_id, .dependencies)
            callgraph: Built callgraph
            
        Returns:
            Validation result with missing edges and invalid tags
        """
        missing_edges = []
        invalid_tags = []
        warnings = []
        
        for tag in connect_tags:
            # Parse SOURCE → TARGET from tag dependencies or description
            source, target = self._parse_connect_tag(tag)
            
            if not source or not target:
                warnings.append(f"Tag {tag.canonical_id}: Could not parse SOURCE → TARGET")
                continue
            
            # Check if edge exists in callgraph
            if not self._edge_exists(source, target, callgraph):
                # Try fuzzy matching if not strict
                if not self.strict and self._fuzzy_edge_exists(source, target, callgraph):
                    warnings.append(f"Tag {tag.canonical_id}: Fuzzy match found for {source} → {target}")
                else:
                    missing_edges.append((source, target))
                    invalid_tags.append(tag.canonical_id)
        
        valid = len(missing_edges) == 0
        
        return CONNECTValidationResult(
            valid=valid,
            missing_edges=missing_edges,
            invalid_tags=invalid_tags,
            warnings=warnings
        )
    
    def _parse_connect_tag(self, tag: Any) -> tuple[str | None, str | None]:
        """Parse SOURCE → TARGET from CONNECT tag"""
        # Try parsing from dependencies first
        if hasattr(tag, 'dependencies') and tag.dependencies:
            # Expect dependencies like ["SOURCE", "TARGET"]
            if len(tag.dependencies) >= 2:
                return tag.dependencies[0], tag.dependencies[1]
        
        # Try parsing from description (e.g., "SOURCE → TARGET" or "SOURCE calls TARGET")
        if hasattr(tag, 'tag_text'):
            text = tag.tag_text
            if "→" in text:
                parts = text.split("→")
                if len(parts) == 2:
                    source = parts[0].strip().split()[-1]  # Last word before →
                    target = parts[1].strip().split()[0]   # First word after →
                    return source, target
        
        return None, None
    
    def _edge_exists(self, source: str, target: str, callgraph: Callgraph) -> bool:
        """Check if edge exists in callgraph (exact match)"""
        # Try direct edge
        if callgraph.has_edge(source, target):
            return True
        
        # Try with different qualifications
        # E.g., "func" might be "module.func" or "module.Class.func"
        for node in callgraph.graph.nodes():
            if node.endswith(f".{source}"):
                if callgraph.has_edge(node, target):
                    return True
                for target_node in callgraph.graph.nodes():
                    if target_node.endswith(f".{target}"):
                        if callgraph.has_edge(node, target_node):
                            return True
        
        return False
    
    def _fuzzy_edge_exists(self, source: str, target: str, callgraph: Callgraph) -> bool:
        """Check if edge exists with fuzzy matching"""
        # Find all nodes containing source name
        source_nodes = [n for n in callgraph.graph.nodes() if source in n]
        target_nodes = [n for n in callgraph.graph.nodes() if target in n]
        
        # Check if any combination has an edge
        for s_node in source_nodes:
            for t_node in target_nodes:
                if callgraph.has_edge(s_node, t_node):
                    return True
        
        return False


class ContractGraphBuilder:
    """Build contract graph from API specifications (OpenAPI, gRPC, etc.)"""
    
    def __init__(self):
        self.edges: list[CallEdge] = []
    
    def build_from_openapi(self, spec_path: str) -> list[CallEdge]:
        """
        Build contract edges from OpenAPI specification
        
        This is a placeholder - real implementation would parse OpenAPI YAML/JSON
        and extract service-to-service call contracts.
        """
        # TODO: Implement OpenAPI parsing
        # For now, return empty list
        return []
    
    def build_from_grpc(self, proto_path: str) -> list[CallEdge]:
        """
        Build contract edges from gRPC proto definitions
        
        This is a placeholder - real implementation would parse .proto files
        and extract RPC call contracts.
        """
        # TODO: Implement gRPC proto parsing
        # For now, return empty list
        return []
    
    def merge_into_callgraph(self, callgraph: Callgraph, contract_edges: list[CallEdge]) -> Callgraph:
        """Merge contract edges into existing callgraph"""
        for edge in contract_edges:
            callgraph.graph.add_edge(edge.caller, edge.callee)
            callgraph.edges.append(edge)
        
        return callgraph

