"""
Enhanced VIF Integration for PLIx

Creates PLIx-specific witnesses using VIF metadata field.
Maintains full backwards compatibility with existing VIF system.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import hashlib
import uuid

from packages.vif.witness import VIF, ConfidenceBand, TaskCriticality


class PLIxVIFIntegration:
    """
    Enhanced VIF integration for PLIx witnesses.
    
    Stores PLIx-specific witness data in VIF metadata field.
    Three witness types:
    - Constraint Replay Witness
    - Purity Proof Witness
    - Subdistribution Witness
    """
    
    def create_constraint_replay_witness(
        self,
        constraint_id: str,
        constraint_text: str,
        variables: Dict[str, Any],
        evaluation_result: bool,
        evidence_dag_hash: str,
        purity_proof: Dict[str, Any],
        context_snapshot_id: str
    ) -> VIF:
        """
        Create VIF witness for constraint replay.
        
        Enables deterministic re-evaluation without re-execution.
        
        Args:
            constraint_id: Unique constraint identifier
            constraint_text: Full constraint expression
            variables: Variable bindings at evaluation time
            evaluation_result: Boolean result of evaluation
            evidence_dag_hash: Hash of supporting evidence DAG
            purity_proof: Purity proof data
            context_snapshot_id: CMC snapshot ID
            
        Returns:
            VIF witness with constraint replay data in metadata
        """
        # Compute hashes
        prompt_content = f"eval({constraint_text}) with {variables}"
        prompt_hash = self._hash_string(prompt_content)
        output_hash = self._hash_string(str(evaluation_result))
        
        return VIF(
            id=f"vif_{uuid.uuid4().hex}",
            version="1.0.0",
            model_id="plix_constraint_evaluator",
            model_provider="aimos",
            context_snapshot_id=context_snapshot_id,
            context_atom_ids=[],
            prompt_hash=prompt_hash,
            prompt_tokens=len(prompt_content.split()),
            confidence_score=1.0,  # Deterministic evaluation
            confidence_band=ConfidenceBand.A,
            output_hash=output_hash,
            output_tokens=1,
            total_tokens=len(prompt_content.split()) + 1,
            task_criticality=TaskCriticality.IMPORTANT,
            kappa_threshold=0.70,
            kappa_gate_passed=True,
            created_at=datetime.now(timezone.utc),
            execution_time_ms=0.0,  # Instant evaluation
            operation_type="plix_constraint_replay",
            parent_vif_id=None,
            child_vif_ids=[],
            metadata={
                "witness_type": "constraint_replay",
                "plix_specific": {
                    "constraint_id": constraint_id,
                    "constraint_text": constraint_text,
                    "variables": variables,
                    "evaluation_result": evaluation_result,
                    "evidence_dag_hash": evidence_dag_hash,
                    "purity_proof": purity_proof
                }
            }
        )
    
    def create_purity_proof_witness(
        self,
        constraint_id: str,
        ast_hash: str,
        allowed_operations: List[str],
        validation_result: bool,
        validator_signature: str,
        context_snapshot_id: str
    ) -> VIF:
        """
        Create VIF witness for purity proof.
        
        Cryptographic proof that constraint is pure (no side effects).
        
        Args:
            constraint_id: Constraint identifier
            ast_hash: SHA-256 hash of constraint AST
            allowed_operations: Set of operations used (all pure)
            validation_result: True if pure, False if impure
            validator_signature: Ed25519 signature
            context_snapshot_id: CMC snapshot ID
            
        Returns:
            VIF witness with purity proof in metadata
        """
        prompt_hash = self._hash_string(f"validate_purity({constraint_id})")
        output_text = "Pure" if validation_result else "Impure"
        output_hash = self._hash_string(output_text)
        
        return VIF(
            id=f"vif_{uuid.uuid4().hex}",
            version="1.0.0",
            model_id="plix_purity_checker",
            model_provider="aimos",
            context_snapshot_id=context_snapshot_id,
            context_atom_ids=[],
            prompt_hash=prompt_hash,
            prompt_tokens=10,
            confidence_score=0.99,  # Very high confidence in purity check
            confidence_band=ConfidenceBand.A,
            output_hash=output_hash,
            output_tokens=1,
            total_tokens=11,
            task_criticality=TaskCriticality.CRITICAL,  # Purity is critical
            kappa_threshold=0.95,
            kappa_gate_passed=True,
            created_at=datetime.now(timezone.utc),
            execution_time_ms=0.0,
            operation_type="plix_purity_proof",
            parent_vif_id=None,
            child_vif_ids=[],
            metadata={
                "witness_type": "purity_proof",
                "plix_specific": {
                    "constraint_id": constraint_id,
                    "ast_hash": ast_hash,
                    "allowed_operations": allowed_operations,
                    "validation_time": datetime.now(timezone.utc).isoformat(),
                    "validation_result": validation_result,
                    "validator_signature": validator_signature
                }
            }
        )
    
    def create_subdistribution_witness(
        self,
        step_id: str,
        attempts: List[Dict[str, Any]],
        final_result: Optional[Any],
        total_probability_mass: float,
        monad_laws_validated: bool,
        context_snapshot_id: str
    ) -> VIF:
        """
        Create VIF witness for subdistribution (probabilistic execution).
        
        Tracks all retry attempts and validates monad laws.
        
        Args:
            step_id: Step identifier
            attempts: List of attempt records
            final_result: Final result (if any)
            total_probability_mass: Total probability (≤ 1.0)
            monad_laws_validated: Whether monad laws hold
            context_snapshot_id: CMC snapshot ID
            
        Returns:
            VIF witness with subdistribution data in metadata
        """
        prompt_hash = self._hash_string(f"execute_with_retry({step_id})")
        output_hash = self._hash_string(str(final_result))
        
        # Confidence = probability of success
        confidence = total_probability_mass if final_result else 0.0
        confidence_band = (
            ConfidenceBand.A if confidence >= 0.90
            else ConfidenceBand.B if confidence >= 0.70
            else ConfidenceBand.C
        )
        
        return VIF(
            id=f"vif_{uuid.uuid4().hex}",
            version="1.0.0",
            model_id="plix_retry_executor",
            model_provider="aimos",
            context_snapshot_id=context_snapshot_id,
            context_atom_ids=[],
            prompt_hash=prompt_hash,
            prompt_tokens=20,
            confidence_score=confidence,
            confidence_band=confidence_band,
            output_hash=output_hash,
            output_tokens=10,
            total_tokens=30,
            task_criticality=TaskCriticality.ROUTINE,
            kappa_threshold=0.70,
            kappa_gate_passed=confidence >= 0.70,
            created_at=datetime.now(timezone.utc),
            execution_time_ms=sum(a.get('duration_ms', 0) for a in attempts),
            operation_type="plix_subdistribution",
            parent_vif_id=None,
            child_vif_ids=[],
            metadata={
                "witness_type": "subdistribution",
                "plix_specific": {
                    "step_id": step_id,
                    "attempts": attempts,
                    "final_result": final_result,
                    "total_probability_mass": total_probability_mass,
                    "failure_probability": round(max(0.0, 1.0 - total_probability_mass), 10),
                    "monad_laws_validated": monad_laws_validated
                }
            }
        )
    
    def extract_plix_metadata(self, vif: VIF) -> Optional[Dict[str, Any]]:
        """
        Extract PLIx-specific metadata from VIF witness.
        
        Args:
            vif: VIF witness
            
        Returns:
            PLIx metadata if present, None otherwise
        """
        return vif.metadata.get('plix_specific')
    
    def is_plix_witness(self, vif: VIF) -> bool:
        """
        Check if VIF witness contains PLIx data.
        
        Args:
            vif: VIF witness
            
        Returns:
            True if PLIx witness
        """
        return (
            vif.operation_type.startswith('plix_') or
            'plix_specific' in vif.metadata
        )
    
    def get_witness_type(self, vif: VIF) -> Optional[str]:
        """
        Get PLIx witness type.
        
        Args:
            vif: VIF witness
            
        Returns:
            Witness type: "constraint_replay" | "purity_proof" | "subdistribution" | None
        """
        return vif.metadata.get('witness_type')
    
    def _hash_string(self, text: str) -> str:
        """Compute SHA-256 hash"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()


# Convenience functions
def create_constraint_replay_witness(
    constraint_id: str,
    constraint_text: str,
    variables: Dict[str, Any],
    result: bool,
    evidence_hash: str,
    purity_proof: Dict[str, Any],
    snapshot_id: str
) -> VIF:
    """Convenience function for creating constraint replay witness"""
    integration = PLIxVIFIntegration()
    return integration.create_constraint_replay_witness(
        constraint_id, constraint_text, variables, result,
        evidence_hash, purity_proof, snapshot_id
    )


def create_purity_proof_witness(
    constraint_id: str,
    ast_hash: str,
    allowed_ops: List[str],
    is_pure: bool,
    signature: str,
    snapshot_id: str
) -> VIF:
    """Convenience function for creating purity proof witness"""
    integration = PLIxVIFIntegration()
    return integration.create_purity_proof_witness(
        constraint_id, ast_hash, allowed_ops, is_pure,
        signature, snapshot_id
    )


def create_subdistribution_witness(
    step_id: str,
    attempts: List[Dict[str, Any]],
    result: Optional[Any],
    probability: float,
    monad_valid: bool,
    snapshot_id: str
) -> VIF:
    """Convenience function for creating subdistribution witness"""
    integration = PLIxVIFIntegration()
    return integration.create_subdistribution_witness(
        step_id, attempts, result, probability,
        monad_valid, snapshot_id
    )

