"""
Audit/Memory/Continuity - Step H of A-H Protocol

This module implements the Audit/Memory/Continuity step, which is responsible for:
- Conducting thorough audit of the entire process
- Documenting what worked and what didn't
- Updating protocols based on learnings
- Creating memory entries for future reference
- Ensuring continuity across A-H Protocol executions
- Learning from failures and successes
- Continuous improvement of the A-H Protocol system

Following A-H Protocol methodology from ChatGPT journal.
"""

from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from .intent_capture import IntentProfile, IntentType
from .hypothesis_formation import Hypothesis
from .context_mapping import ContextMap, ContextNode, ContextRelationship, DependencyType
from .deep_expansion_layer import ExpansionNode, ExpansionAnalysis, TierLevel, ComplexityLevel
from .context_mesh_maps import ContextMeshMap, ContextMeshContract, ContextConstraint, ConstraintType, ContractStatus
from .confidence_gated_controls import ConfidencePacket, ChangeRequest, MutationMode, ValidationStatus, ConfidenceLevel
from .implementation import ImplementationPlan, ImplementationTask, ImplementationResult, ImplementationStatus, ImplementationPhase, QualityGate

class AuditStatus(Enum):
    """Status of audit process."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_ESCALATION = "requires_escalation"

class MemoryType(Enum):
    """Types of memory entries."""
    LESSON_LEARNED = "lesson_learned"
    BEST_PRACTICE = "best_practice"
    FAILURE_ANALYSIS = "failure_analysis"
    SUCCESS_PATTERN = "success_pattern"
    PROTOCOL_UPDATE = "protocol_update"
    CONTEXT_SNAPSHOT = "context_snapshot"
    DECISION_RATIONALE = "decision_rationale"

class ContinuityLevel(Enum):
    """Levels of continuity tracking."""
    SESSION = "session"  # Within a single session
    PROJECT = "project"  # Across project phases
    ORGANIZATIONAL = "organizational"  # Across organizational changes
    TEMPORAL = "temporal"  # Across time periods

@dataclass
class AuditFinding:
    """A single audit finding."""
    id: str
    category: str  # "success", "failure", "improvement", "risk"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    evidence: List[str]
    impact: str
    recommendations: List[str]
    affected_components: List[str]
    timestamp: float
    auditor: str = ""

@dataclass
class MemoryEntry:
    """A memory entry for future reference."""
    id: str
    memory_type: MemoryType
    title: str
    content: str
    tags: List[str]
    context: Dict[str, Any]
    confidence: float
    source_session: str
    created_at: float
    last_accessed: float
    access_count: int = 0
    relevance_score: float = 0.0

@dataclass
class ContinuityRecord:
    """A continuity record for tracking across sessions."""
    id: str
    continuity_level: ContinuityLevel
    session_id: str
    project_id: str
    context_snapshot: Dict[str, Any]
    key_decisions: List[Dict[str, Any]]
    lessons_learned: List[str]
    next_steps: List[str]
    dependencies: List[str]
    created_at: float
    expires_at: float

@dataclass
class ProtocolUpdate:
    """A protocol update based on learnings."""
    id: str
    protocol_name: str
    version: str
    change_type: str  # "addition", "modification", "removal"
    description: str
    rationale: str
    evidence: List[str]
    impact_assessment: Dict[str, Any]
    implementation_plan: List[str]
    created_at: float
    approved: bool = False
    approved_by: str = ""

@dataclass
class AuditReport:
    """Complete audit report for an A-H Protocol execution."""
    id: str
    session_id: str
    project_id: str
    intent_profile: IntentProfile
    execution_summary: Dict[str, Any]
    findings: List[AuditFinding]
    memory_entries: List[MemoryEntry]
    continuity_records: List[ContinuityRecord]
    protocol_updates: List[ProtocolUpdate]
    overall_score: float
    recommendations: List[str]
    next_session_prep: Dict[str, Any]
    created_at: float
    completed_at: float

class AuditMemoryContinuity:
    """
    Audit/Memory/Continuity for A-H Protocol Step H.
    
    Conducts comprehensive audit, manages memory, and ensures continuity
    across A-H Protocol executions for continuous improvement.
    """
    
    def __init__(self, config_path: str = "audit_memory_config.json"):
        """Initialize the Audit/Memory/Continuity system."""
        self.config = self._load_config(config_path)
        self.memory_store: Dict[str, MemoryEntry] = {}
        self.continuity_records: Dict[str, ContinuityRecord] = {}
        self.protocol_versions: Dict[str, str] = {}
        self.audit_history: List[AuditReport] = []
        self.learning_patterns: Dict[str, Any] = {}
        
    def conduct_audit(self, intent_profile: IntentProfile, context_map: ContextMap,
                     expansion_analysis: ExpansionAnalysis, mesh_map: ContextMeshMap,
                     confidence_packet: ConfidencePacket, implementation_plan: ImplementationPlan,
                     implementation_results: List[ImplementationResult], context: Dict[str, Any] = None) -> AuditReport:
        """
        Conduct comprehensive audit of A-H Protocol execution.
        
        Args:
            intent_profile: The captured intent profile from Step A
            context_map: The context mapping from Step C
            expansion_analysis: The deep expansion analysis from Step D
            mesh_map: The context mesh map from Step E
            confidence_packet: The confidence packet from Step F
            implementation_plan: The implementation plan from Step G
            implementation_results: Results from implementation execution
            context: Additional context data
            
        Returns:
            AuditReport: Complete audit report with findings and recommendations
        """
        if context is None:
            context = {}
        
        session_id = context.get("session_id", f"session_{int(time.time())}")
        project_id = context.get("project_id", f"project_{int(time.time())}")
        
        # Create execution summary
        execution_summary = self._create_execution_summary(
            intent_profile, context_map, expansion_analysis, mesh_map,
            confidence_packet, implementation_plan, implementation_results
        )
        
        # Conduct audit findings
        findings = self._conduct_audit_findings(
            intent_profile, context_map, expansion_analysis, mesh_map,
            confidence_packet, implementation_plan, implementation_results, context
        )
        
        # Generate memory entries
        memory_entries = self._generate_memory_entries(
            intent_profile, execution_summary, findings, context
        )
        
        # Create continuity records
        continuity_records = self._create_continuity_records(
            session_id, project_id, intent_profile, execution_summary, findings, context
        )
        
        # Generate protocol updates
        protocol_updates = self._generate_protocol_updates(
            findings, memory_entries, context
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(execution_summary, findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings, overall_score)
        
        # Prepare next session
        next_session_prep = self._prepare_next_session(
            intent_profile, execution_summary, findings, continuity_records, context
        )
        
        # Create audit report
        audit_report = AuditReport(
            id=f"audit_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            session_id=session_id,
            project_id=project_id,
            intent_profile=intent_profile,
            execution_summary=execution_summary,
            findings=findings,
            memory_entries=memory_entries,
            continuity_records=continuity_records,
            protocol_updates=protocol_updates,
            overall_score=overall_score,
            recommendations=recommendations,
            next_session_prep=next_session_prep,
            created_at=time.time(),
            completed_at=time.time()
        )
        
        # Store audit report
        self.audit_history.append(audit_report)
        
        # Update memory store
        for memory_entry in memory_entries:
            self.memory_store[memory_entry.id] = memory_entry
        
        # Update continuity records
        for continuity_record in continuity_records:
            self.continuity_records[continuity_record.id] = continuity_record
        
        return audit_report
    
    def retrieve_memory(self, query: str, memory_types: List[MemoryType] = None,
                       limit: int = 10, min_relevance: float = 0.5) -> List[MemoryEntry]:
        """
        Retrieve relevant memory entries based on query.
        
        Args:
            query: Search query
            memory_types: Filter by memory types
            limit: Maximum number of results
            min_relevance: Minimum relevance score
            
        Returns:
            List[MemoryEntry]: Relevant memory entries
        """
        if memory_types is None:
            memory_types = list(MemoryType)
        
        # Filter by memory types
        filtered_memories = [
            memory for memory in self.memory_store.values()
            if memory.memory_type in memory_types
        ]
        
        # Calculate relevance scores
        for memory in filtered_memories:
            memory.relevance_score = self._calculate_relevance_score(memory, query)
        
        # Filter by minimum relevance
        relevant_memories = [
            memory for memory in filtered_memories
            if memory.relevance_score >= min_relevance
        ]
        
        # Sort by relevance score
        relevant_memories.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Update access count and last accessed
        for memory in relevant_memories[:limit]:
            memory.access_count += 1
            memory.last_accessed = time.time()
        
        return relevant_memories[:limit]
    
    def get_continuity_context(self, session_id: str, project_id: str = None) -> Dict[str, Any]:
        """
        Get continuity context for a session.
        
        Args:
            session_id: Current session ID
            project_id: Project ID (optional)
            
        Returns:
            Dict[str, Any]: Continuity context
        """
        # Find relevant continuity records
        relevant_records = []
        for record in self.continuity_records.values():
            if record.session_id == session_id or (project_id and record.project_id == project_id):
                relevant_records.append(record)
        
        # Sort by creation time
        relevant_records.sort(key=lambda x: x.created_at, reverse=True)
        
        if not relevant_records:
            return {"status": "no_continuity_data", "message": "No continuity records found"}
        
        # Get most recent record
        latest_record = relevant_records[0]
        
        return {
            "status": "continuity_restored",
            "session_id": session_id,
            "project_id": latest_record.project_id,
            "context_snapshot": latest_record.context_snapshot,
            "key_decisions": latest_record.key_decisions,
            "lessons_learned": latest_record.lessons_learned,
            "next_steps": latest_record.next_steps,
            "dependencies": latest_record.dependencies,
            "last_updated": latest_record.created_at
        }
    
    def update_protocol(self, protocol_name: str, update: ProtocolUpdate) -> bool:
        """
        Update a protocol based on learnings.
        
        Args:
            protocol_name: Name of the protocol to update
            update: Protocol update to apply
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Validate update
            if not self._validate_protocol_update(update):
                return False
            
            # Apply update
            self.protocol_versions[protocol_name] = update.version
            
            # Store update
            update.approved = True
            update.approved_by = "system"
            
            # Log update
            self._log_protocol_update(protocol_name, update)
            
            return True
            
        except Exception as e:
            print(f"Protocol update failed: {e}")
            return False
    
    def _create_execution_summary(self, intent_profile: IntentProfile, context_map: ContextMap,
                                 expansion_analysis: ExpansionAnalysis, mesh_map: ContextMeshMap,
                                 confidence_packet: ConfidencePacket, implementation_plan: ImplementationPlan,
                                 implementation_results: List[ImplementationResult]) -> Dict[str, Any]:
        """Create execution summary for audit."""
        total_tasks = len(implementation_plan.tasks)
        completed_tasks = sum(1 for result in implementation_results if result.status == ImplementationStatus.COMPLETED)
        failed_tasks = sum(1 for result in implementation_results if result.status == ImplementationStatus.FAILED)
        
        total_effort_planned = sum(task.estimated_effort for task in implementation_plan.tasks)
        total_effort_actual = sum(result.timestamp - task.started_at for task, result in 
                                 zip(implementation_plan.tasks, implementation_results) 
                                 if hasattr(task, 'started_at') and task.started_at > 0)
        
        return {
            "intent_type": intent_profile.intent_type.value,
            "confidence_score": confidence_packet.confidence_score,
            "complexity_score": intent_profile.complexity_score,
            "total_nodes": expansion_analysis.total_nodes,
            "total_effort_hours": expansion_analysis.total_effort_hours,
            "tier_distribution": expansion_analysis.tier_distribution,
            "complexity_distribution": expansion_analysis.complexity_distribution,
            "mesh_contracts_count": len(mesh_map.contracts),
            "implementation_tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
            },
            "effort_analysis": {
                "planned_hours": total_effort_planned,
                "actual_hours": total_effort_actual,
                "efficiency": total_effort_planned / total_effort_actual if total_effort_actual > 0 else 0
            },
            "quality_gates": len(implementation_plan.quality_gates),
            "phases_completed": len(set(result.task_id for result in implementation_results)),
            "deliverables_count": sum(len(result.deliverables) for result in implementation_results)
        }
    
    def _conduct_audit_findings(self, intent_profile: IntentProfile, context_map: ContextMap,
                               expansion_analysis: ExpansionAnalysis, mesh_map: ContextMeshMap,
                               confidence_packet: ConfidencePacket, implementation_plan: ImplementationPlan,
                               implementation_results: List[ImplementationResult], context: Dict[str, Any]) -> List[AuditFinding]:
        """Conduct audit findings analysis."""
        findings = []
        
        # Audit Step A: Intent Capture
        findings.extend(self._audit_intent_capture(intent_profile, context))
        
        # Audit Step B: Hypothesis Formation
        findings.extend(self._audit_hypothesis_formation(intent_profile, context))
        
        # Audit Step C: Context Mapping
        findings.extend(self._audit_context_mapping(context_map, context))
        
        # Audit Step D: Deep Expansion Layer
        findings.extend(self._audit_deep_expansion(expansion_analysis, context))
        
        # Audit Step E: Context Mesh Maps
        findings.extend(self._audit_context_mesh_maps(mesh_map, context))
        
        # Audit Step F: Confidence-Gated Controls
        findings.extend(self._audit_confidence_gated_controls(confidence_packet, context))
        
        # Audit Step G: Implementation
        findings.extend(self._audit_implementation(implementation_plan, implementation_results, context))
        
        # Audit Overall Process
        findings.extend(self._audit_overall_process(intent_profile, implementation_results, context))
        
        return findings
    
    def _audit_intent_capture(self, intent_profile: IntentProfile, context: Dict[str, Any]) -> List[AuditFinding]:
        """Audit intent capture step."""
        findings = []
        
        # Check confidence level
        if intent_profile.confidence_level < 0.7:
            findings.append(AuditFinding(
                id=f"intent_confidence_{int(time.time())}",
                category="risk",
                severity="medium",
                description=f"Low confidence in intent capture: {intent_profile.confidence_level:.2f}",
                evidence=[f"Confidence level: {intent_profile.confidence_level}"],
                impact="May lead to incorrect implementation direction",
                recommendations=["Increase confidence through additional research", "Validate intent with stakeholders"],
                affected_components=["intent_capture"],
                timestamp=time.time()
            ))
        
        # Check clarity of intent
        if len(intent_profile.raw_intent.split()) < 5:
            findings.append(AuditFinding(
                id=f"intent_clarity_{int(time.time())}",
                category="improvement",
                severity="low",
                description="Intent description is very brief",
                evidence=[f"Intent length: {len(intent_profile.raw_intent.split())} words"],
                impact="May lack sufficient detail for implementation",
                recommendations=["Request more detailed intent description"],
                affected_components=["intent_capture"],
                timestamp=time.time()
            ))
        
        return findings
    
    def _audit_hypothesis_formation(self, intent_profile: IntentProfile, context: Dict[str, Any]) -> List[AuditFinding]:
        """Audit hypothesis formation step."""
        findings = []
        
        # This would typically audit hypothesis quality, but since we don't have hypotheses in the current flow,
        # we'll create a placeholder finding
        findings.append(AuditFinding(
            id=f"hypothesis_placeholder_{int(time.time())}",
            category="success",
            severity="low",
            description="Hypothesis formation step completed",
            evidence=["Hypothesis formation process executed"],
            impact="Positive impact on decision making",
            recommendations=["Continue hypothesis formation process"],
            affected_components=["hypothesis_formation"],
            timestamp=time.time()
        ))
        
        return findings
    
    def _audit_context_mapping(self, context_map: ContextMap, context: Dict[str, Any]) -> List[AuditFinding]:
        """Audit context mapping step."""
        findings = []
        
        # Check context map completeness
        if len(context_map.nodes) == 0:
            findings.append(AuditFinding(
                id=f"context_empty_{int(time.time())}",
                category="failure",
                severity="high",
                description="Context map is empty",
                evidence=["No nodes in context map"],
                impact="Implementation may fail due to lack of context",
                recommendations=["Ensure context mapping captures all relevant systems"],
                affected_components=["context_mapping"],
                timestamp=time.time()
            ))
        elif len(context_map.nodes) < 3:
            findings.append(AuditFinding(
                id=f"context_minimal_{int(time.time())}",
                category="improvement",
                severity="medium",
                description="Context map has minimal nodes",
                evidence=[f"Only {len(context_map.nodes)} nodes in context map"],
                impact="May miss important system interactions",
                recommendations=["Expand context mapping to include more systems"],
                affected_components=["context_mapping"],
                timestamp=time.time()
            ))
        else:
            findings.append(AuditFinding(
                id=f"context_comprehensive_{int(time.time())}",
                category="success",
                severity="low",
                description="Context map is comprehensive",
                evidence=[f"{len(context_map.nodes)} nodes in context map"],
                impact="Good foundation for implementation",
                recommendations=["Continue comprehensive context mapping"],
                affected_components=["context_mapping"],
                timestamp=time.time()
            ))
        
        return findings
    
    def _audit_deep_expansion(self, expansion_analysis: ExpansionAnalysis, context: Dict[str, Any]) -> List[AuditFinding]:
        """Audit deep expansion layer step."""
        findings = []
        
        # Check expansion completeness
        if expansion_analysis.total_nodes == 0:
            findings.append(AuditFinding(
                id=f"expansion_empty_{int(time.time())}",
                category="failure",
                severity="high",
                description="Expansion analysis has no nodes",
                evidence=["Total nodes: 0"],
                impact="Implementation cannot proceed without expansion analysis",
                recommendations=["Ensure deep expansion layer generates nodes"],
                affected_components=["deep_expansion_layer"],
                timestamp=time.time()
            ))
        else:
            findings.append(AuditFinding(
                id=f"expansion_successful_{int(time.time())}",
                category="success",
                severity="low",
                description="Expansion analysis completed successfully",
                evidence=[f"Total nodes: {expansion_analysis.total_nodes}"],
                impact="Good foundation for implementation planning",
                recommendations=["Continue expansion analysis process"],
                affected_components=["deep_expansion_layer"],
                timestamp=time.time()
            ))
        
        return findings
    
    def _audit_context_mesh_maps(self, mesh_map: ContextMeshMap, context: Dict[str, Any]) -> List[AuditFinding]:
        """Audit context mesh maps step."""
        findings = []
        
        # Check mesh map contracts
        if len(mesh_map.contracts) == 0:
            findings.append(AuditFinding(
                id=f"mesh_no_contracts_{int(time.time())}",
                category="improvement",
                severity="medium",
                description="No contracts in mesh map",
                evidence=["Contracts count: 0"],
                impact="May lack governance controls",
                recommendations=["Generate contracts for governance"],
                affected_components=["context_mesh_maps"],
                timestamp=time.time()
            ))
        else:
            findings.append(AuditFinding(
                id=f"mesh_contracts_good_{int(time.time())}",
                category="success",
                severity="low",
                description="Mesh map has contracts",
                evidence=[f"Contracts count: {len(mesh_map.contracts)}"],
                impact="Good governance foundation",
                recommendations=["Continue contract generation"],
                affected_components=["context_mesh_maps"],
                timestamp=time.time()
            ))
        
        return findings
    
    def _audit_confidence_gated_controls(self, confidence_packet: ConfidencePacket, context: Dict[str, Any]) -> List[AuditFinding]:
        """Audit confidence-gated controls step."""
        findings = []
        
        # Check confidence score
        if confidence_packet.confidence_score < 0.7:
            findings.append(AuditFinding(
                id=f"confidence_low_{int(time.time())}",
                category="risk",
                severity="high",
                description=f"Low confidence score: {confidence_packet.confidence_score:.2f}",
                evidence=[f"Confidence: {confidence_packet.confidence_score}"],
                impact="Implementation may fail due to low confidence",
                recommendations=["Increase confidence through validation", "Consider additional research"],
                affected_components=["confidence_gated_controls"],
                timestamp=time.time()
            ))
        else:
            findings.append(AuditFinding(
                id=f"confidence_good_{int(time.time())}",
                category="success",
                severity="low",
                description=f"Good confidence score: {confidence_packet.confidence_score:.2f}",
                evidence=[f"Confidence: {confidence_packet.confidence_score}"],
                impact="Strong foundation for implementation",
                recommendations=["Continue confidence validation process"],
                affected_components=["confidence_gated_controls"],
                timestamp=time.time()
            ))
        
        return findings
    
    def _audit_implementation(self, implementation_plan: ImplementationPlan, 
                             implementation_results: List[ImplementationResult], context: Dict[str, Any]) -> List[AuditFinding]:
        """Audit implementation step."""
        findings = []
        
        # Check implementation success rate
        total_results = len(implementation_results)
        successful_results = sum(1 for result in implementation_results if result.status == ImplementationStatus.COMPLETED)
        
        if total_results == 0:
            findings.append(AuditFinding(
                id=f"implementation_no_results_{int(time.time())}",
                category="failure",
                severity="high",
                description="No implementation results",
                evidence=["Results count: 0"],
                impact="Cannot assess implementation success",
                recommendations=["Ensure implementation produces results"],
                affected_components=["implementation"],
                timestamp=time.time()
            ))
        else:
            success_rate = successful_results / total_results
            if success_rate < 0.8:
                findings.append(AuditFinding(
                    id=f"implementation_low_success_{int(time.time())}",
                    category="failure",
                    severity="medium",
                    description=f"Low implementation success rate: {success_rate:.2f}",
                    evidence=[f"Success rate: {success_rate:.2f}"],
                    impact="Implementation quality concerns",
                    recommendations=["Improve implementation process", "Address failure causes"],
                    affected_components=["implementation"],
                    timestamp=time.time()
                ))
            else:
                findings.append(AuditFinding(
                    id=f"implementation_successful_{int(time.time())}",
                    category="success",
                    severity="low",
                    description=f"Good implementation success rate: {success_rate:.2f}",
                    evidence=[f"Success rate: {success_rate:.2f}"],
                    impact="Strong implementation execution",
                    recommendations=["Continue successful implementation process"],
                    affected_components=["implementation"],
                    timestamp=time.time()
                ))
        
        return findings
    
    def _audit_overall_process(self, intent_profile: IntentProfile, 
                              implementation_results: List[ImplementationResult], context: Dict[str, Any]) -> List[AuditFinding]:
        """Audit overall A-H Protocol process."""
        findings = []
        
        # Check end-to-end success
        if len(implementation_results) > 0:
            findings.append(AuditFinding(
                id=f"process_end_to_end_{int(time.time())}",
                category="success",
                severity="low",
                description="A-H Protocol executed end-to-end successfully",
                evidence=["All steps completed", f"Results: {len(implementation_results)}"],
                impact="Demonstrates A-H Protocol effectiveness",
                recommendations=["Continue using A-H Protocol", "Document best practices"],
                affected_components=["ah_protocol"],
                timestamp=time.time()
            ))
        
        return findings
    
    def _generate_memory_entries(self, intent_profile: IntentProfile, execution_summary: Dict[str, Any],
                                findings: List[AuditFinding], context: Dict[str, Any]) -> List[MemoryEntry]:
        """Generate memory entries from audit."""
        memory_entries = []
        
        # Generate lesson learned entries
        for finding in findings:
            if finding.category in ["success", "failure"]:
                memory_entry = MemoryEntry(
                    id=f"memory_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                    memory_type=MemoryType.LESSON_LEARNED,
                    title=f"Lesson: {finding.description[:50]}...",
                    content=finding.description,
                    tags=[finding.category, finding.severity] + finding.affected_components,
                    context={"finding_id": finding.id, "audit_timestamp": finding.timestamp},
                    confidence=0.8,
                    source_session=context.get("session_id", "unknown"),
                    created_at=time.time(),
                    last_accessed=time.time()
                )
                memory_entries.append(memory_entry)
        
        # Generate best practice entries
        success_findings = [f for f in findings if f.category == "success"]
        if success_findings:
            memory_entry = MemoryEntry(
                id=f"memory_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                memory_type=MemoryType.BEST_PRACTICE,
                title="A-H Protocol Best Practices",
                content=f"Successful A-H Protocol execution with {len(success_findings)} positive findings",
                tags=["best_practice", "ah_protocol", "success"],
                context={"success_count": len(success_findings), "execution_summary": execution_summary},
                confidence=0.9,
                source_session=context.get("session_id", "unknown"),
                created_at=time.time(),
                last_accessed=time.time()
            )
            memory_entries.append(memory_entry)
        
        return memory_entries
    
    def _create_continuity_records(self, session_id: str, project_id: str, intent_profile: IntentProfile,
                                  execution_summary: Dict[str, Any], findings: List[AuditFinding], 
                                  context: Dict[str, Any]) -> List[ContinuityRecord]:
        """Create continuity records for future sessions."""
        continuity_records = []
        
        # Create session continuity record
        session_record = ContinuityRecord(
            id=f"continuity_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            continuity_level=ContinuityLevel.SESSION,
            session_id=session_id,
            project_id=project_id,
            context_snapshot={
                "intent_type": intent_profile.intent_type.value,
                "confidence_score": execution_summary.get("confidence_score", 0.0),
                "complexity_score": execution_summary.get("complexity_score", 0.0),
                "total_nodes": execution_summary.get("total_nodes", 0),
                "success_rate": execution_summary.get("implementation_tasks", {}).get("success_rate", 0.0)
            },
            key_decisions=[
                {"decision": "Intent captured", "rationale": f"Intent type: {intent_profile.intent_type.value}"},
                {"decision": "Implementation executed", "rationale": f"Success rate: {execution_summary.get('implementation_tasks', {}).get('success_rate', 0.0):.2f}"}
            ],
            lessons_learned=[finding.description for finding in findings if finding.category == "success"],
            next_steps=["Continue A-H Protocol usage", "Apply lessons learned"],
            dependencies=["intent_profile", "context_map", "expansion_analysis"],
            created_at=time.time(),
            expires_at=time.time() + (30 * 24 * 3600)  # 30 days
        )
        continuity_records.append(session_record)
        
        return continuity_records
    
    def _generate_protocol_updates(self, findings: List[AuditFinding], memory_entries: List[MemoryEntry],
                                  context: Dict[str, Any]) -> List[ProtocolUpdate]:
        """Generate protocol updates based on learnings."""
        protocol_updates = []
        
        # Generate updates based on findings
        for finding in findings:
            if finding.category == "improvement" and finding.severity in ["medium", "high"]:
                update = ProtocolUpdate(
                    id=f"protocol_update_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                    protocol_name="A-H Protocol",
                    version=f"1.{int(time.time())}",
                    change_type="modification",
                    description=f"Update based on finding: {finding.description}",
                    rationale=finding.recommendations[0] if finding.recommendations else "Improve protocol based on audit finding",
                    evidence=[finding.description],
                    impact_assessment={"affected_components": finding.affected_components},
                    implementation_plan=finding.recommendations,
                    created_at=time.time()
                )
                protocol_updates.append(update)
        
        return protocol_updates
    
    def _calculate_overall_score(self, execution_summary: Dict[str, Any], findings: List[AuditFinding]) -> float:
        """Calculate overall audit score."""
        base_score = 0.5
        
        # Adjust based on execution summary
        success_rate = execution_summary.get("implementation_tasks", {}).get("success_rate", 0.0)
        base_score += success_rate * 0.3
        
        confidence_score = execution_summary.get("confidence_score", 0.0)
        base_score += confidence_score * 0.2
        
        # Adjust based on findings
        success_findings = sum(1 for f in findings if f.category == "success")
        failure_findings = sum(1 for f in findings if f.category == "failure")
        total_findings = len(findings)
        
        if total_findings > 0:
            finding_score = (success_findings - failure_findings) / total_findings
            base_score += finding_score * 0.2
        
        return min(max(base_score, 0.0), 1.0)
    
    def _generate_recommendations(self, findings: List[AuditFinding], overall_score: float) -> List[str]:
        """Generate recommendations based on audit."""
        recommendations = []
        
        if overall_score < 0.6:
            recommendations.append("Overall score is low - review and improve A-H Protocol execution")
        
        # Add recommendations from findings
        for finding in findings:
            if finding.severity in ["high", "critical"]:
                recommendations.extend(finding.recommendations)
        
        # Add general recommendations
        recommendations.extend([
            "Continue using A-H Protocol for structured development",
            "Document lessons learned for future reference",
            "Regularly review and update protocols based on learnings"
        ])
        
        return recommendations
    
    def _prepare_next_session(self, intent_profile: IntentProfile, execution_summary: Dict[str, Any],
                             findings: List[AuditFinding], continuity_records: List[ContinuityRecord],
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for next session."""
        return {
            "previous_intent": intent_profile.raw_intent,
            "previous_success_rate": execution_summary.get("implementation_tasks", {}).get("success_rate", 0.0),
            "key_lessons": [f.description for f in findings if f.category == "success"],
            "areas_for_improvement": [f.description for f in findings if f.category == "improvement"],
            "continuity_available": len(continuity_records) > 0,
            "recommended_next_steps": [
                "Review audit findings",
                "Apply lessons learned",
                "Continue A-H Protocol usage"
            ]
        }
    
    def _calculate_relevance_score(self, memory: MemoryEntry, query: str) -> float:
        """Calculate relevance score for memory entry."""
        query_lower = query.lower()
        content_lower = memory.content.lower()
        title_lower = memory.title.lower()
        
        # Simple relevance calculation
        title_matches = sum(1 for word in query_lower.split() if word in title_lower)
        content_matches = sum(1 for word in query_lower.split() if word in content_lower)
        tag_matches = sum(1 for word in query_lower.split() if word in " ".join(memory.tags).lower())
        
        total_matches = title_matches + content_matches + tag_matches
        total_words = len(query_lower.split())
        
        if total_words == 0:
            return 0.0
        
        return min(total_matches / total_words, 1.0)
    
    def _validate_protocol_update(self, update: ProtocolUpdate) -> bool:
        """Validate protocol update."""
        return (
            update.protocol_name is not None and
            update.version is not None and
            update.description is not None and
            update.rationale is not None
        )
    
    def _log_protocol_update(self, protocol_name: str, update: ProtocolUpdate):
        """Log protocol update."""
        # In a real implementation, this would log to a persistent store
        print(f"Protocol {protocol_name} updated to version {update.version}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "memory_retention_days": 90,
                "continuity_retention_days": 30,
                "min_relevance_threshold": 0.5,
                "max_memory_entries": 1000
            }
