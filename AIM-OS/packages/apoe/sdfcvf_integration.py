"""SDF-CVF Integration for APOE

Enables quartet/quintet parity validation for APOE operations:
- Type checker: Validates quartet parity for contracts
- Quality gates: Enforces quality standards via parity gates
- Verifier role: Quality validation using SDF-CVF
- Builder role: Quartet parity enforcement for artifacts
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List
import logging

from .models import Step
from .acl_parser import ExecutionPlan

logger = logging.getLogger(__name__)

# SDF-CVF imports (optional)
try:
    from packages.sdfcvf.quartet import Quartet, QuartetDetector, FileClassification
    from packages.sdfcvf.parity import ParityCalculator, ParityResult, calculate_parity
    from packages.sdfcvf.gates import ParityGate, GateConfig, GateType, GateResult, create_pre_commit_gate
    from packages.sdfcvf.quintet import Quintet, QuintetDetector, QuintetParityCalculator, QuintetParityResult
    SDFCVF_AVAILABLE = True
except ImportError:
    # Fallback for environments without SDF-CVF
    SDFCVF_AVAILABLE = False
    Quartet = None
    QuartetDetector = None
    FileClassification = None
    ParityCalculator = None
    ParityResult = None
    calculate_parity = None
    ParityGate = None
    GateConfig = None
    GateType = None
    GateResult = None
    create_pre_commit_gate = None
    Quintet = None
    QuintetDetector = None
    QuintetParityCalculator = None
    QuintetParityResult = None


class APOESDFCVFIntegration:
    """Integrates APOE with SDF-CVF for quartet/quintet parity validation.
    
    Provides:
    - Type checker quartet parity validation
    - Quality gates with parity enforcement
    - Verifier role quality validation
    - Builder role quartet parity enforcement
    """
    
    def __init__(self, enable_quintet: bool = True):
        """
        Initialize SDF-CVF integration.
        
        Args:
            enable_quintet: If True, use quintet parity (includes NL tags), else quartet
        """
        self.sdfcvf_available = SDFCVF_AVAILABLE
        self.enable_quintet = enable_quintet and SDFCVF_AVAILABLE
        
        if not self.sdfcvf_available:
            logger.warning("SDF-CVF integration disabled: SDF-CVF package not available")
            return
        
        # Initialize detectors and calculators
        if self.enable_quintet:
            self.quintet_detector = QuintetDetector()
            self.quintet_calculator = QuintetParityCalculator()
        else:
            self.parity_calculator = ParityCalculator()
        
        # Default gate configuration
        self.default_gate_config = GateConfig(
            gate_type=GateType.PRE_COMMIT,
            parity_threshold=0.85,
            strict_mode=True
        )

    @staticmethod
    def _threshold_from_config(config: GateConfig, default: float = 0.85) -> float:
        if config is None:
            return default
        if hasattr(config, "parity_threshold"):
            return float(config.parity_threshold)
        if hasattr(config, "min_parity"):
            return float(config.min_parity)
        return default

    @staticmethod
    def _with_gate_compat_fields(result: GateResult) -> GateResult:
        """Attach legacy aliases expected by older call sites/tests."""
        if not hasattr(result, "message"):
            result.message = "; ".join(result.reasons) if result.reasons else ""
        if not hasattr(result, "parity"):
            result.parity = result.parity_score
        return result

    def _make_gate_result(
        self,
        passed: bool,
        parity_score: float,
        threshold: float,
        reasons: List[str],
        can_override: bool = False,
        warnings: Optional[List[str]] = None,
    ) -> GateResult:
        result = GateResult(
            passed=passed,
            parity_score=parity_score,
            threshold=threshold,
            reasons=reasons,
            can_override=can_override,
            warnings=warnings or [],
        )
        return self._with_gate_compat_fields(result)

    @staticmethod
    def _build_quartet(
        code_files: List[str],
        docs_files: List[str],
        tests_files: List[str],
        traces_files: Optional[List[str]] = None,
    ) -> Quartet:
        return Quartet(
            code_files=code_files,
            doc_files=docs_files,
            test_files=tests_files,
            trace_files=traces_files or [],
        )
    
    def validate_contract_parity(
        self,
        code_files: List[str],
        docs_files: List[str],
        tests_files: List[str],
        traces_files: Optional[List[str]] = None,
        min_parity: float = 0.85
    ) -> Dict[str, Any]:
        """
        Validate quartet/quintet parity for contract (type checker integration).
        
        Used by typeChecker component to validate contracts have quartet parity.
        
        Args:
            code_files: List of code file paths
            docs_files: List of documentation file paths
            tests_files: List of test file paths
            traces_files: Optional list of trace file paths
            min_parity: Minimum parity threshold (default 0.85)
            
        Returns:
            Validation result with parity score and pass/fail status
        """
        if not self.sdfcvf_available:
            return {
                "valid": False,
                "error": "SDF-CVF not available",
                "parity": 0.0
            }
        
        try:
            if self.enable_quintet:
                # Use quintet parity
                quintet = self.quintet_detector.detect_from_files(
                    code_files=code_files,
                    docs_files=docs_files,
                    tests_files=tests_files,
                    traces_files=traces_files or []
                )
                result = self.quintet_calculator.calculate_parity(quintet)
                parity_score = result.score
                is_quintet = result.is_quintet
            else:
                # Use quartet parity
                quartet = self._build_quartet(
                    code_files=code_files,
                    docs_files=docs_files,
                    tests_files=tests_files,
                    traces_files=traces_files,
                )
                result = self.parity_calculator.calculate(quartet)
                parity_score = result.parity_score
                is_quintet = False
            
            valid = parity_score >= min_parity
            
            return {
                "valid": valid,
                "parity": parity_score,
                "min_parity": min_parity,
                "is_quintet": is_quintet,
                "code_files": len(code_files),
                "docs_files": len(docs_files),
                "tests_files": len(tests_files),
                "traces_files": len(traces_files or []),
                "details": {
                    "score": parity_score,
                    "threshold": min_parity,
                    "passed": valid
                }
            }
        except Exception as e:
            logger.error(f"Error validating contract parity: {e}")
            return {
                "valid": False,
                "error": str(e),
                "parity": 0.0
            }
    
    def enforce_quality_gate(
        self,
        code_files: List[str],
        docs_files: List[str],
        tests_files: List[str],
        traces_files: Optional[List[str]] = None,
        gate_config: Optional[GateConfig] = None
    ) -> GateResult:
        """
        Enforce quality gate with parity validation (quality gates integration).
        
        Used by qualityGates component to enforce quality standards.
        
        Args:
            code_files: List of code file paths
            docs_files: List of documentation file paths
            tests_files: List of test file paths
            traces_files: Optional list of trace file paths
            gate_config: Optional gate configuration (uses default if None)
            
        Returns:
            Gate result with pass/fail status
        """
        if not self.sdfcvf_available:
            return self._make_gate_result(
                passed=False,
                parity_score=0.0,
                threshold=0.85,
                reasons=["SDF-CVF not available"],
            )
        
        config = gate_config or self.default_gate_config
        threshold = self._threshold_from_config(config)
        
        try:
            # Validate parity first
            validation = self.validate_contract_parity(
                code_files=code_files,
                docs_files=docs_files,
                tests_files=tests_files,
                traces_files=traces_files,
                min_parity=threshold
            )
            
            # Create gate and evaluate
            gate = ParityGate(config)
            
            if self.enable_quintet:
                quintet = self.quintet_detector.detect_from_files(
                    code_files=code_files,
                    docs_files=docs_files,
                    tests_files=tests_files,
                    traces_files=traces_files or []
                )
                # For quintet, calculate parity first then check gate
                quintet_result = self.quintet_calculator.calculate_parity(quintet)
                # Create a parity result compatible with gate
                from packages.sdfcvf.parity import ParityResult
                parity_result = ParityResult(
                    parity_score=quintet_result.score,
                    code_docs_similarity=quintet_result.similarities.get("code_docs", 0.0),
                    code_tests_similarity=quintet_result.similarities.get("code_tests", 0.0),
                    code_traces_similarity=quintet_result.similarities.get("code_traces", 0.0),
                    docs_tests_similarity=quintet_result.similarities.get("docs_tests", 0.0),
                    docs_traces_similarity=quintet_result.similarities.get("docs_traces", 0.0),
                    tests_traces_similarity=quintet_result.similarities.get("tests_traces", 0.0),
                    complete=len(code_files) > 0 and len(docs_files) > 0 and len(tests_files) > 0,
                    warnings=quintet_result.warnings
                )
                result = gate.check(quintet, parity_result)
            else:
                quartet = self._build_quartet(
                    code_files=code_files,
                    docs_files=docs_files,
                    tests_files=tests_files,
                    traces_files=traces_files,
                )
                result = gate.check(quartet)
            
            return self._with_gate_compat_fields(result)
        except Exception as e:
            logger.error(f"Error enforcing quality gate: {e}")
            return self._make_gate_result(
                passed=False,
                parity_score=0.0,
                threshold=threshold,
                reasons=[f"Gate evaluation error: {str(e)}"],
            )
    
    def validate_verification_quality(
        self,
        verification_result: Dict[str, Any],
        code_files: List[str],
        docs_files: List[str],
        tests_files: List[str],
        traces_files: Optional[List[str]] = None,
        min_parity: float = 0.90
    ) -> Dict[str, Any]:
        """
        Validate verification quality using SDF-CVF (verifier role integration).
        
        Used by verifierRole component to validate verification results have quality.
        
        Args:
            verification_result: Verification result from verifier role
            code_files: List of code file paths
            docs_files: List of documentation file paths
            tests_files: List of test file paths
            traces_files: Optional list of trace file paths
            min_parity: Minimum parity threshold (default 0.90, higher for verification)
            
        Returns:
            Quality validation result
        """
        if not self.sdfcvf_available:
            return {
                "valid": False,
                "error": "SDF-CVF not available",
                "verification_quality": 0.0
            }
        
        try:
            # Validate parity
            parity_validation = self.validate_contract_parity(
                code_files=code_files,
                docs_files=docs_files,
                tests_files=tests_files,
                traces_files=traces_files,
                min_parity=min_parity
            )
            
            # Combine verification result with parity validation
            verification_quality = (
                verification_result.get("confidence", 0.0) * 0.5 +
                parity_validation["parity"] * 0.5
            )
            
            valid = (
                parity_validation["valid"] and
                verification_quality >= min_parity and
                verification_result.get("success", False)
            )
            
            return {
                "valid": valid,
                "verification_quality": verification_quality,
                "parity": parity_validation["parity"],
                "verification_confidence": verification_result.get("confidence", 0.0),
                "min_parity": min_parity,
                "details": {
                    "parity_validation": parity_validation,
                    "verification_result": verification_result
                }
            }
        except Exception as e:
            logger.error(f"Error validating verification quality: {e}")
            return {
                "valid": False,
                "error": str(e),
                "verification_quality": 0.0
            }
    
    def enforce_builder_parity(
        self,
        artifacts: Dict[str, List[str]],
        min_parity: float = 0.85
    ) -> Dict[str, Any]:
        """
        Enforce quartet parity for builder artifacts (builder role integration).
        
        Used by builderRole component to ensure code/docs/tests/traces created together.
        
        Args:
            artifacts: Dictionary with keys 'code', 'docs', 'tests', 'traces' (each list of file paths)
            min_parity: Minimum parity threshold (default 0.85)
            
        Returns:
            Parity enforcement result
        """
        if not self.sdfcvf_available:
            return {
                "valid": False,
                "error": "SDF-CVF not available",
                "parity": 0.0
            }
        
        try:
            code_files = artifacts.get("code", [])
            docs_files = artifacts.get("docs", [])
            tests_files = artifacts.get("tests", [])
            traces_files = artifacts.get("traces", [])
            
            # Validate parity
            validation = self.validate_contract_parity(
                code_files=code_files,
                docs_files=docs_files,
                tests_files=tests_files,
                traces_files=traces_files,
                min_parity=min_parity
            )
            
            # Enforce: if parity too low, fail
            if not validation["valid"]:
                return {
                    "valid": False,
                    "parity": validation["parity"],
                    "min_parity": min_parity,
                    "message": f"Parity {validation['parity']:.2f} below threshold {min_parity}",
                    "details": validation
                }
            
            return {
                "valid": True,
                "parity": validation["parity"],
                "min_parity": min_parity,
                "message": f"Parity {validation['parity']:.2f} meets threshold {min_parity}",
                "details": validation
            }
        except Exception as e:
            logger.error(f"Error enforcing builder parity: {e}")
            return {
                "valid": False,
                "error": str(e),
                "parity": 0.0
            }
    
    def check_parity_for_step(
        self,
        step: Step,
        plan: ExecutionPlan,
        min_parity: float = 0.85
    ) -> Dict[str, Any]:
        """
        Check quartet parity for a step's artifacts.
        
        Helper method to check parity for step outputs.
        
        Args:
            step: Step to check
            plan: Parent plan
            min_parity: Minimum parity threshold
            
        Returns:
            Parity check result
        """
        if not self.sdfcvf_available:
            return {
                "valid": False,
                "error": "SDF-CVF not available",
                "parity": 0.0
            }
        
        # Extract artifacts from step outputs
        artifacts = step.outputs or {}
        code_files = artifacts.get("code_files", [])
        docs_files = artifacts.get("docs_files", [])
        tests_files = artifacts.get("tests_files", [])
        traces_files = artifacts.get("traces_files", [])
        
        if not code_files:
            return {
                "valid": False,
                "error": "No code files found in step outputs",
                "parity": 0.0
            }
        
        return self.validate_contract_parity(
            code_files=code_files,
            docs_files=docs_files,
            tests_files=tests_files,
            traces_files=traces_files,
            min_parity=min_parity
        )

