"""HHNI indexing helpers."""

from __future__ import annotations

import logging
from time import perf_counter, sleep
from typing import List, Optional, TYPE_CHECKING
import os
import importlib

from .embeddings import embed_and_store
from .models import HHNINode, sha256_hex
from .parsers import parse_paragraphs, parse_sentences
from .safety import HHNISafetyGates
from .morphology import tokenize_with_morphology

if TYPE_CHECKING:
    from packages.seg.seg_graph import SEGraph
    from packages.seg.models import Entity, Relation, RelationType
    from packages.hhni.cross_document_relationships import CrossDocumentRelationshipDetector
    from packages.hhni.semantic_block_organizer import SemanticBlockOrganizer

logger = logging.getLogger(__name__)

PARAGRAPH_COLLECTION = "hhni_paragraphs"
SENTENCE_COLLECTION = "hhni_sentences"
MAX_RETRIES = 3
BACKOFF_SECONDS = 0.5


def _get_cas_tracker():
    """Return ActivationTracker instance if CAS is enabled and available; otherwise None."""
    if os.getenv("CAS_ENABLED", "false").lower() != "true":
        return None
    try:
        module = importlib.import_module("packages.cas.client")
        tracker_cls = getattr(module, "ActivationTracker", None)
        return tracker_cls() if tracker_cls else None
    except Exception:
        return None


def build_hhni_for_atom(
    *,
    atom,
    dgraph_client,
    qdrant_client,
    correlation_id: Optional[str] = None,
    seg_graph: Optional["SEGraph"] = None,
    cross_doc_detector: Optional["CrossDocumentRelationshipDetector"] = None,
    block_organizer: Optional["SemanticBlockOrganizer"] = None,
) -> List[HHNINode]:
    """Build HHNI nodes for the given atom.
    
    Args:
        atom: CMC atom to index
        dgraph_client: DGraph client for node storage
        qdrant_client: Qdrant client for vector storage
        correlation_id: Optional correlation ID for tracing
        seg_graph: Optional SEG graph for morphological part linking
        cross_doc_detector: Optional cross-document relationship detector (Phase 2)
        block_organizer: Optional semantic block organizer (Phase 3)
    """
    HHNISafetyGates.validate_atom_pre_build(atom)

    start = perf_counter()
    nodes: List[HHNINode] = []
    cas_tracker = _get_cas_tracker()
    extra_log = {
        "correlation_id": correlation_id,
        "atom_id": atom.id,
        "action": "hhni.build",
    }

    try:
        # CAS: pre-index hook
        if cas_tracker is not None:
            try:
                cas_tracker.capture_state(
                    source="hhni.pre_index",
                    data={
                        "atom_id": getattr(atom, "id", ""),
                        "modality": getattr(getattr(atom, "content", None), "media_type", ""),
                        "tags": dict(getattr(atom, "tags", {}) or {}),
                        "snapshot_id": getattr(getattr(atom, "witness", None), "snapshot_id", ""),
                        "correlation_id": correlation_id,
                        "content_preview": (getattr(getattr(atom, "content", None), "inline", "") or "")[:500],
                    },
                )
                cas_tracker.record_document_read(document_id=str(getattr(atom, "id", "")))
            except Exception:  # fail-soft
                pass

        doc_node = HHNINode(
            id=f"doc:{atom.id}",
            level=1,
            path=f"/sys:aimos/doc:{atom.id}",
            content_hash=atom.hash,
            parent_id="sys:aimos",
            atom_refs=[atom.id],
            created_at=atom.created_at,
            snapshot_id=atom.witness.snapshot_id or "",
            tags=dict(atom.tags),
        )
        nodes.append(doc_node)

        content = atom.content.inline
        if content is None and atom.content.uri:
            raise ValueError("URI-based content not yet supported for HHNI")
        if not content:
            HHNISafetyGates.validate_node_count(nodes)
            dgraph_client.upsert_nodes([node.to_dict() for node in nodes])
            duration = perf_counter() - start
            logger.info(
                "hhni.build.success",
                extra={**extra_log, "node_count": len(nodes), "duration_ms": duration * 1000},
            )
            return nodes

        paragraphs = parse_paragraphs(content)
        for p_idx, para_text in enumerate(paragraphs):
            HHNISafetyGates.validate_text_length(para_text, text_type="paragraph")
            payload = {
                "atom_id": atom.id,
                "level": 2,
                "paragraph": p_idx,
            }
            vector_id = _embed_with_retry(
                para_text,
                qdrant_client=qdrant_client,
                collection=PARAGRAPH_COLLECTION,
                payload=payload,
            )
            para_node = HHNINode(
                id=f"para:{atom.id}#p{p_idx}",
                level=2,
                path=f"{doc_node.path}/para:{p_idx}",
                content_hash=sha256_hex(para_text),
                text=para_text,
                parent_id=doc_node.id,
                vector_id=vector_id,
                atom_refs=[atom.id],
                created_at=atom.created_at,
                snapshot_id=atom.witness.snapshot_id or "",
                tags=dict(atom.tags),
            )
            nodes.append(para_node)
            doc_node.children_ids.append(para_node.id)

            sentences = parse_sentences(para_text)
            for s_idx, sent_text in enumerate(sentences):
                HHNISafetyGates.validate_text_length(sent_text, text_type="sentence")
                payload = {
                    "atom_id": atom.id,
                    "level": 3,
                    "paragraph": p_idx,
                    "sentence": s_idx,
                }
                sent_vector_id = _embed_with_retry(
                    sent_text,
                    qdrant_client=qdrant_client,
                    collection=SENTENCE_COLLECTION,
                    payload=payload,
                )
                sent_node = HHNINode(
                    id=f"sent:{atom.id}#p{p_idx}#s{s_idx}",
                    level=3,
                    path=f"{para_node.path}/sent:{s_idx}",
                    content_hash=sha256_hex(sent_text),
                    text=sent_text,
                    parent_id=para_node.id,
                    vector_id=sent_vector_id,
                    atom_refs=[atom.id],
                    created_at=atom.created_at,
                    snapshot_id=atom.witness.snapshot_id or "",
                )
                nodes.append(sent_node)
                para_node.children_ids.append(sent_node.id)
                
                # Morphological analysis for SUBWORD level (Level 6)
                # Tokenize with morphological analysis
                token_analyses = tokenize_with_morphology(sent_text)
                for tok_idx, (token, morphology) in enumerate(token_analyses):
                    # Create SUBWORD level node with morphological metadata
                    token_id = f"tok:{atom.id}#p{p_idx}#s{s_idx}#t{tok_idx}"
                    token_node = HHNINode(
                        id=token_id,
                        level=6,  # SUBWORD level
                        path=f"{sent_node.path}/tok:{tok_idx}",
                        content_hash=sha256_hex(token),
                        text=token,
                        parent_id=sent_node.id,
                        atom_refs=[atom.id],
                        created_at=atom.created_at,
                        snapshot_id=atom.witness.snapshot_id or "",
                        tags=dict(atom.tags),  # Keep original atom tags (numeric values)
                        morphology=morphology.model_dump(),  # Store full morphological decomposition
                    )
                    # Store full morphological decomposition in node metadata (via to_dict)
                    nodes.append(token_node)
                    sent_node.children_ids.append(token_id)
                    
                    # SEG Integration: Link morphological parts in graph
                    if seg_graph is not None and morphology.root:
                        _link_morphological_parts_in_seg(
                            seg_graph=seg_graph,
                            word=token,
                            morphology=morphology,
                            hhni_node_id=token_id,
                            atom_id=atom.id,
                            correlation_id=correlation_id,
                        )
        
        # Phase 2: Detect cross-document relationships (if detector provided)
        if seg_graph is not None and cross_doc_detector is not None:
            _detect_cross_document_relationships(
                seg_graph=seg_graph,
                detector=cross_doc_detector,
                atom_id=atom.id,
                correlation_id=correlation_id,
            )
        
        # Phase 3: Organize into semantic blocks (if organizer provided)
        if block_organizer is not None:
            blocks = block_organizer.organize_into_blocks(
                nodes=nodes,
                atom_id=atom.id,
            )
            
            if blocks:
                # Pre-compute relationships between blocks
                relationships = block_organizer.pre_compute_relationships(blocks)
                
                # Store blocks (would integrate with CMC molecules here)
                # For now, just log that blocks were created
                logger.info(
                    "hhni.block.organization.success",
                    extra={
                        "atom_id": atom.id,
                        "block_count": len(blocks),
                        "relationship_count": sum(len(r) for r in relationships.values()),
                        "correlation_id": correlation_id,
                    },
                )

        HHNISafetyGates.validate_node_count(nodes)
        dgraph_client.upsert_nodes([node.to_dict() for node in nodes])

        # CAS: post-index hook
        if cas_tracker is not None:
            try:
                cas_tracker.record_concept_use(
                    concepts=[n.path for n in nodes if getattr(n, "path", None)],
                    metadata={
                        "atom_id": atom.id,
                        "level_counts": {
                            "doc": 1,
                            "paragraph": len([n for n in nodes if n.level == 2]),
                            "sentence": len([n for n in nodes if n.level == 3]),
                            "subword": len([n for n in nodes if n.level == 6]),
                        },
                        "snapshot_id": getattr(getattr(atom, "witness", None), "snapshot_id", ""),
                        "correlation_id": correlation_id,
                    },
                )
                cas_tracker.capture_state(
                    source="hhni.post_index",
                    data={
                        "atom_id": atom.id,
                        "node_count": len(nodes),
                        "paths": [n.path for n in nodes if getattr(n, "path", None)],
                        "correlation_id": correlation_id,
                    },
                )
            except Exception:
                pass

        duration = perf_counter() - start
        logger.info(
            "hhni.build.success",
            extra={**extra_log, "node_count": len(nodes), "duration_ms": duration * 1000},
        )
        return nodes
    except Exception as exc:  # pragma: no cover - safety-critical logging
        duration = perf_counter() - start
        logger.error(
            "hhni.build.failed",
            extra={**extra_log, "error": str(exc), "duration_ms": duration * 1000},
        )
        raise


def _link_morphological_parts_in_seg(
    *,
    seg_graph: "SEGraph",
    word: str,
    morphology,
    hhni_node_id: str,
    atom_id: str,
    correlation_id: Optional[str] = None,
) -> None:
    """Link morphological parts in SEG graph.
    
    Creates SEG entities for word and its parts (prefix, root, suffix),
    and links them with DERIVES_FROM relations.
    
    Args:
        seg_graph: SEG graph instance
        word: The word being analyzed
        morphology: MorphologicalDecomposition object
        hhni_node_id: HHNI node ID for cross-reference
        atom_id: CMC atom ID for provenance
        correlation_id: Optional correlation ID for tracing
    """
    try:
        # Import here to avoid circular dependency
        from packages.seg.models import Entity, Relation, RelationType
        
        # Create word entity (if not exists)
        word_entity_id = f"morph_word:{word.lower()}"
        word_entity = seg_graph.get_entity(word_entity_id)
        
        if word_entity is None:
            word_entity = Entity(
                id=word_entity_id,  # Use explicit ID for consistent lookup
                type="morphological_word",
                name=word,
                attributes={
                    "hhni_node_id": hhni_node_id,
                    "atom_id": atom_id,
                    "pos_tag": morphology.pos_tag or "",
                    "operations": morphology.operations,
                },
                tags=["morphology", "word"],
                source=f"hhni:{hhni_node_id}",
            )
            seg_graph.add_entity(word_entity)
        else:
            # Update attributes if entity exists
            word_entity.attributes.update({
                "hhni_node_id": hhni_node_id,
                "atom_id": atom_id,
            })
        
        # Create prefix entity and relation (if prefix exists)
        if morphology.prefix:
            prefix_entity_id = f"morph_part:prefix:{morphology.prefix}"
            prefix_entity = seg_graph.get_entity(prefix_entity_id)
            
            if prefix_entity is None:
                prefix_entity = Entity(
                    id=prefix_entity_id,  # Use explicit ID for consistent lookup
                    type="morphological_part",
                    name=f"prefix:{morphology.prefix}",
                    attributes={
                        "part_type": "prefix",
                        "operation": morphology.operations[0] if morphology.operations else None,
                    },
                    tags=["morphology", "prefix"],
                    source=f"hhni:{hhni_node_id}",
                )
                seg_graph.add_entity(prefix_entity)
            
            # Create relation: word → prefix
            relation = Relation(
                source_id=word_entity.id,
                target_id=prefix_entity.id,
                relation_type=RelationType.DERIVES_FROM,
                confidence=1.0,
                tags=["morphology", "prefix_relation"],
                source=f"hhni:{hhni_node_id}",
            )
            seg_graph.add_relation(relation)
        
        # Create root entity and relation (if root exists)
        if morphology.root and morphology.root != word:
            root_entity_id = f"morph_part:root:{morphology.root.lower()}"
            root_entity = seg_graph.get_entity(root_entity_id)
            
            if root_entity is None:
                root_entity = Entity(
                    id=root_entity_id,  # Use explicit ID for consistent lookup
                    type="morphological_part",
                    name=f"root:{morphology.root}",
                    attributes={
                        "part_type": "root",
                    },
                    tags=["morphology", "root"],
                    source=f"hhni:{hhni_node_id}",
                )
                seg_graph.add_entity(root_entity)
            
            # Create relation: word → root
            relation = Relation(
                source_id=word_entity.id,
                target_id=root_entity.id,
                relation_type=RelationType.DERIVES_FROM,
                confidence=1.0,
                tags=["morphology", "root_relation"],
                source=f"hhni:{hhni_node_id}",
            )
            seg_graph.add_relation(relation)
        
        # Create suffix entity and relation (if suffix exists)
        if morphology.suffix:
            suffix_entity_id = f"morph_part:suffix:{morphology.suffix}"
            suffix_entity = seg_graph.get_entity(suffix_entity_id)
            
            if suffix_entity is None:
                suffix_entity = Entity(
                    id=suffix_entity_id,  # Use explicit ID for consistent lookup
                    type="morphological_part",
                    name=f"suffix:{morphology.suffix}",
                    attributes={
                        "part_type": "suffix",
                        "operation": morphology.operations[-1] if morphology.operations else None,
                    },
                    tags=["morphology", "suffix"],
                    source=f"hhni:{hhni_node_id}",
                )
                seg_graph.add_entity(suffix_entity)
            
            # Create relation: word → suffix
            relation = Relation(
                source_id=word_entity.id,
                target_id=suffix_entity.id,
                relation_type=RelationType.DERIVES_FROM,
                confidence=1.0,
                tags=["morphology", "suffix_relation"],
                source=f"hhni:{hhni_node_id}",
            )
            seg_graph.add_relation(relation)
    
    except Exception as exc:
        # Log error but don't fail HHNI indexing if SEG integration fails
        logger.warning(
            "hhni.seg.morphology.link.failed",
            extra={
                "word": word,
                "hhni_node_id": hhni_node_id,
                "error": str(exc),
                "correlation_id": correlation_id,
            },
        )


def _detect_cross_document_relationships(
    *,
    seg_graph: "SEGraph",
    detector: "CrossDocumentRelationshipDetector",
    atom_id: str,
    correlation_id: Optional[str] = None,
) -> None:
    """Detect and create cross-document relationships.
    
    For each entity in the current document, finds similar entities in other
    documents and creates semantic relationships.
    
    Args:
        seg_graph: SEG graph instance
        detector: Cross-document relationship detector
        atom_id: Current atom ID (document ID)
        correlation_id: Optional correlation ID for tracing
    """
    try:
        # Get all entities from current document
        current_entities = [
            e for e in seg_graph.list_entities()
            if e.attributes.get("atom_id") == atom_id
        ]
        
        if not current_entities:
            return
        
        # Get all entities from other documents
        all_entities = seg_graph.list_entities()
        other_doc_entities = [
            e for e in all_entities
            if e.attributes.get("atom_id") != atom_id
        ]
        
        if not other_doc_entities:
            # No other documents yet, skip cross-document detection
            return
        
        # Detect relationships for each current entity
        for current_entity in current_entities:
            # Get target document IDs
            target_doc_ids = [e.attributes.get("atom_id") for e in other_doc_entities]
            
            # Detect semantic relationships
            semantic_relations = detector.detect_semantic_relationships(
                source_entity=current_entity,
                target_entities=other_doc_entities,
                source_doc_id=atom_id,
                target_doc_ids=target_doc_ids,
            )
            
            # Add relations to SEG
            for relation in semantic_relations:
                seg_graph.add_relation(relation)
            
            # Track narrative context (if applicable)
            narrative_relations = detector.track_narrative_context(
                entity=current_entity,
                context_entities=other_doc_entities,
                document_ids=target_doc_ids,
            )
            
            # Add narrative relations to SEG
            for relation in narrative_relations:
                seg_graph.add_relation(relation)
    
    except Exception as exc:
        # Log error but don't fail HHNI indexing if cross-doc detection fails
        logger.warning(
            "hhni.cross_doc.detection.failed",
            extra={
                "atom_id": atom_id,
                "error": str(exc),
                "correlation_id": correlation_id,
            },
        )


def _embed_with_retry(text: str, *, qdrant_client, collection: str, payload: dict) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return embed_and_store(
                text,
                qdrant_client=qdrant_client,
                collection=collection,
                payload=payload,
            )
        except Exception as exc:
            logger.warning(
                "hhni.embed.retry",
                extra={
                    "collection": collection,
                    "attempt": attempt,
                    "error": str(exc),
                },
            )
            if attempt == MAX_RETRIES:
                raise
            sleep(BACKOFF_SECONDS * attempt)
    raise RuntimeError("Unexpected embed retry exhaustion")
