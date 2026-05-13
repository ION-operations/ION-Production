"""Safety gates for HHNI operations."""

from __future__ import annotations

from typing import List, Optional


# NL_TAG: VIF-GATE-001 | Write-side safety limits for HHNI indexing. | class HHNISafetyGates | []
class HHNISafetyGates:
    """Write-side safety limits for HHNI indexing."""

    MAX_NODES_PER_ATOM = 1000      # Hard limit on nodes
    MAX_PARAGRAPH_LENGTH = 5000    # Characters per paragraph
    MAX_SENTENCE_LENGTH = 500      # Characters per sentence
    MAX_EMBEDDING_BATCH = 100      # Vectors at once
    INDEXING_TIMEOUT_SEC = 30      # Total operation timeout
    MAX_ATOM_SIZE = 100_000        # 100KB content limit

    @staticmethod
    def validate_atom_pre_build(atom) -> None:
        """Pre-flight validation before HHNI build executes."""
        if atom.content.inline:
            content_size = len(atom.content.inline)
            if content_size > HHNISafetyGates.MAX_ATOM_SIZE:
                raise ValueError(
                    "Atom too large for HHNI: "
                    f"{content_size} bytes (max: {HHNISafetyGates.MAX_ATOM_SIZE})"
                )
        elif atom.content.uri:
            raise ValueError("URI-based atoms not yet supported for HHNI")

    @staticmethod
    def validate_node_count(nodes: List) -> None:
        """Post-build validation of node count."""
        if len(nodes) > HHNISafetyGates.MAX_NODES_PER_ATOM:
            raise RuntimeError(
                "Node explosion detected: "
                f"{len(nodes)} nodes (max: {HHNISafetyGates.MAX_NODES_PER_ATOM})"
            )

    @staticmethod
    def validate_text_length(text: str, text_type: str = "text") -> None:
        """Validate text length based on content type."""
        max_lengths = {
            "paragraph": HHNISafetyGates.MAX_PARAGRAPH_LENGTH,
            "sentence": HHNISafetyGates.MAX_SENTENCE_LENGTH,
            "text": HHNISafetyGates.MAX_ATOM_SIZE,
        }

        max_length = max_lengths.get(text_type, HHNISafetyGates.MAX_ATOM_SIZE)
        if len(text) > max_length:
            raise ValueError(
                f"{text_type.capitalize()} too long: {len(text)} chars "
                f"(max: {max_length})"
            )


# NL_TAG: VIF-GATE-002 | Read-side safety limits for HHNI queries. | class HHNIQueryGates | []
class HHNIQueryGates:
    # NL_TAG: VIF-UTIL-001 | Pre-flight validation before HHNI build executes. | validate_atom_pre_build(atom) | []
    # NL_TAG_SPEC: VIF-SPEC-001 | Validates validate_atom_pre_build specification | validate_atom_pre_build | [spec_file_TBD]
    def validate_atom_pre_build(atom) -> None:
        """Pre-flight validation before HHNI build executes."""
        if atom.content.inline:
            content_size = len(atom.content.inline)
            if content_size > HHNISafetyGates.MAX_ATOM_SIZE:
                raise ValueError(
                    "Atom too large for HHNI: "
                    f"{content_size} bytes (max: {HHNISafetyGates.MAX_ATOM_SIZE})"
                )
        elif atom.content.uri:
            raise ValueError("URI-based atoms not yet supported for HHNI")

    @staticmethod
    # NL_TAG: VIF-UTIL-002 | Post-build validation of node count. | validate_node_count(nodes) | []
    # NL_TAG_SPEC: VIF-SPEC-002 | Validates validate_node_count specification | validate_node_count | [spec_file_TBD]
    def validate_node_count(nodes: List) -> None:
        """Post-build validation of node count."""
        if len(nodes) > HHNISafetyGates.MAX_NODES_PER_ATOM:
            raise RuntimeError(
                "Node explosion detected: "
                f"{len(nodes)} nodes (max: {HHNISafetyGates.MAX_NODES_PER_ATOM})"
            )

    @staticmethod
    # NL_TAG: VIF-UTIL-003 | Validate text length based on content type. | validate_text_length(text, text_type) | []
    # NL_TAG_SPEC: VIF-SPEC-003 | Validates validate_text_length specification | validate_text_length | [spec_file_TBD]
    def validate_text_length(text: str, text_type: str = "text") -> None:
        """Validate text length based on content type."""
        max_lengths = {
            "paragraph": HHNISafetyGates.MAX_PARAGRAPH_LENGTH,
            "sentence": HHNISafetyGates.MAX_SENTENCE_LENGTH,
            "text": HHNISafetyGates.MAX_ATOM_SIZE,
        }

        max_length = max_lengths.get(text_type, HHNISafetyGates.MAX_ATOM_SIZE)
        if len(text) > max_length:
            raise ValueError(
                f"{text_type.capitalize()} too long: {len(text)} chars "
                f"(max: {max_length})"
            )


class HHNIQueryGates:
    """Read-side safety limits for HHNI queries."""

    MAX_TRAVERSAL_DEPTH = 5
    MAX_RESULTS = 1000
    QUERY_TIMEOUT_SEC = 5

    @staticmethod
    # NL_TAG: VIF-UTIL-004 | Apply result limiting to GraphQL queries. | apply_limits(query, first) | []
    def apply_limits(query: str, first: Optional[int] = None) -> str:
        """Apply result limiting to GraphQL queries."""
        if "queryHHNINode(" in query and "first:" not in query:
            limit = min(first or HHNIQueryGates.MAX_RESULTS, HHNIQueryGates.MAX_RESULTS)
            query = query.replace(
                "queryHHNINode(", f"queryHHNINode(first: {limit}, "
            )
        return query

    @staticmethod
    # NL_TAG: VIF-UTIL-005 | Validate traversal depth argument. | validate_depth(depth) | []
    # NL_TAG_SPEC: VIF-SPEC-004 | Validates validate_depth specification | validate_depth | [spec_file_TBD]
    def validate_depth(depth: int) -> None:
        """Validate traversal depth argument."""
        if depth > HHNIQueryGates.MAX_TRAVERSAL_DEPTH:
            raise ValueError(
                f"Traversal depth {depth} exceeds maximum "
                f"({HHNIQueryGates.MAX_TRAVERSAL_DEPTH})"
            )
