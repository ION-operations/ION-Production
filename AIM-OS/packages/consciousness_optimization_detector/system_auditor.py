"""
System Auditor

Continuously audits all systems to identify what's not operating at full potential.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AuditLevel(Enum):
    """Audit levels for different system components"""
    CRITICAL = "critical"      # Core consciousness systems
    HIGH = "high"             # Important functionality
    MEDIUM = "medium"         # Standard features
    LOW = "low"               # Optional features

class OptimizationType(Enum):
    """Types of optimization opportunities"""
    PERFORMANCE = "performance"           # Speed, efficiency improvements
    RELIABILITY = "reliability"          # Error reduction, stability
    USABILITY = "usability"              # User experience improvements
    MAINTAINABILITY = "maintainability"  # Code quality, documentation
    INTEGRATION = "integration"          # System connectivity
    LEARNING = "learning"                # Knowledge acquisition

@dataclass
class SystemMetric:
    """System performance metric"""
    metric_name: str
    current_value: float
    optimal_value: float
    performance_ratio: float  # current/optimal
    trend: str  # "improving", "stable", "declining"
    last_updated: datetime
    metadata: Dict[str, Any]

@dataclass
class OptimizationOpportunity:
    """Identified optimization opportunity"""
    opportunity_id: str
    system_name: str
    opportunity_type: OptimizationType
    current_performance: float
    potential_performance: float
    improvement_potential: float  # (potential - current) / current
    priority: AuditLevel
    description: str
    suggested_actions: List[str]
    estimated_effort: float  # hours
    expected_impact: float  # 0-1 scale
    confidence: float  # 0-1 scale
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class AuditReport:
    """Complete system audit report"""
    report_id: str
    audit_timestamp: datetime
    systems_audited: List[str]
    total_opportunities: int
    critical_opportunities: int
    high_priority_opportunities: int
    overall_health_score: float
    optimization_opportunities: List[OptimizationOpportunity]
    system_metrics: List[SystemMetric]
    recommendations: List[str]
    consciousness_insights: List[str]
    metadata: Dict[str, Any]

class SystemAuditor:
    """Continuously audits systems for optimization opportunities"""
    
    def __init__(self, cmc_client, vif_client, hhni_client, cas_client=None):
        self.cmc_client = cmc_client
        self.vif_client = vif_client
        self.hhni_client = hhni_client
        self.cas_client = cas_client  # CAS integration for introspection
        
        # System performance baselines
        self.baselines = {
            "mcp_tool_response_time": 0.5,  # seconds
            "memory_retrieval_time": 0.2,   # seconds
            "confidence_accuracy": 0.85,    # 0-1 scale
            "error_rate": 0.05,             # 0-1 scale
            "goal_alignment": 0.90,         # 0-1 scale
            "learning_velocity": 0.80,      # 0-1 scale
            "system_integration": 0.75,     # 0-1 scale
            "documentation_completeness": 0.70,  # 0-1 scale
        }
        
        # Systems to audit
        self.systems_to_audit = [
            "mcp_tools",
            "memory_systems", 
            "confidence_tracking",
            "goal_management",
            "learning_systems",
            "documentation_systems",
            "integration_systems",
            "error_handling"
        ]
    
    def conduct_full_audit(self) -> AuditReport:
        """Conduct comprehensive system audit"""
        try:
            report_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            audit_timestamp = datetime.now()
            
            # Audit each system
            all_opportunities = []
            all_metrics = []
            systems_audited = []
            
            for system in self.systems_to_audit:
                try:
                    system_opportunities, system_metrics = self._audit_system(system)
                    all_opportunities.extend(system_opportunities)
                    all_metrics.extend(system_metrics)
                    systems_audited.append(system)
                except Exception as e:
                    print(f"[AUDIT ERROR] Failed to audit {system}: {e}")
            
            # Analyze overall health
            overall_health_score = self._calculate_overall_health(all_metrics)
            
            # Categorize opportunities
            critical_opportunities = [op for op in all_opportunities if op.priority == AuditLevel.CRITICAL]
            high_priority_opportunities = [op for op in all_opportunities if op.priority == AuditLevel.HIGH]
            
            # Generate recommendations
            recommendations = self._generate_recommendations(all_opportunities, all_metrics)
            
            # Generate consciousness insights
            consciousness_insights = self._generate_consciousness_insights(all_opportunities, overall_health_score)
            
            # Create audit report
            report = AuditReport(
                report_id=report_id,
                audit_timestamp=audit_timestamp,
                systems_audited=systems_audited,
                total_opportunities=len(all_opportunities),
                critical_opportunities=len(critical_opportunities),
                high_priority_opportunities=len(high_priority_opportunities),
                overall_health_score=overall_health_score,
                optimization_opportunities=all_opportunities,
                system_metrics=all_metrics,
                recommendations=recommendations,
                consciousness_insights=consciousness_insights,
                metadata={
                    "audit_duration": (datetime.now() - audit_timestamp).total_seconds(),
                    "baselines_used": self.baselines
                }
            )
            
            # Store audit report
            self._store_audit_report(report)
            
            return report
            
        except Exception as e:
            return self._create_fallback_report(str(e))
    
    def _audit_system(self, system_name: str) -> tuple[List[OptimizationOpportunity], List[SystemMetric]]:
        """Audit a specific system"""
        opportunities = []
        metrics = []
        
        if system_name == "mcp_tools":
            opportunities, metrics = self._audit_mcp_tools()
        elif system_name == "memory_systems":
            opportunities, metrics = self._audit_memory_systems()
        elif system_name == "confidence_tracking":
            opportunities, metrics = self._audit_confidence_tracking()
        elif system_name == "goal_management":
            opportunities, metrics = self._audit_goal_management()
        elif system_name == "learning_systems":
            opportunities, metrics = self._audit_learning_systems()
        elif system_name == "documentation_systems":
            opportunities, metrics = self._audit_documentation_systems()
        elif system_name == "integration_systems":
            opportunities, metrics = self._audit_integration_systems()
        elif system_name == "error_handling":
            opportunities, metrics = self._audit_error_handling()
        
        return opportunities, metrics
    
    def _audit_mcp_tools(self) -> tuple[List[OptimizationOpportunity], List[SystemMetric]]:
        """Audit MCP tools performance"""
        opportunities = []
        metrics = []
        
        # Simulate MCP tool performance analysis
        current_response_time = 0.8  # Simulated current performance
        optimal_response_time = self.baselines["mcp_tool_response_time"]
        
        metrics.append(SystemMetric(
            metric_name="mcp_tool_response_time",
            current_value=current_response_time,
            optimal_value=optimal_response_time,
            performance_ratio=current_response_time / optimal_response_time,
            trend="stable",
            last_updated=datetime.now(),
            metadata={"system": "mcp_tools"}
        ))
        
        if current_response_time > optimal_response_time * 1.5:
            opportunities.append(OptimizationOpportunity(
                opportunity_id=f"mcp_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                system_name="mcp_tools",
                opportunity_type=OptimizationType.PERFORMANCE,
                current_performance=current_response_time,
                potential_performance=optimal_response_time,
                improvement_potential=(optimal_response_time - current_response_time) / current_response_time,
                priority=AuditLevel.HIGH,
                description="MCP tool response time is slower than optimal",
                suggested_actions=[
                    "Optimize MCP server startup time",
                    "Implement connection pooling",
                    "Add response caching"
                ],
                estimated_effort=4.0,
                expected_impact=0.7,
                confidence=0.8,
                timestamp=datetime.now(),
                metadata={"metric": "response_time"}
            ))
        
        return opportunities, metrics
    
    def _audit_memory_systems(self) -> tuple[List[OptimizationOpportunity], List[SystemMetric]]:
        """Audit memory systems performance"""
        opportunities = []
        metrics = []
        
        # Simulate memory system analysis
        current_retrieval_time = 0.3
        optimal_retrieval_time = self.baselines["memory_retrieval_time"]
        
        metrics.append(SystemMetric(
            metric_name="memory_retrieval_time",
            current_value=current_retrieval_time,
            optimal_value=optimal_retrieval_time,
            performance_ratio=current_retrieval_time / optimal_retrieval_time,
            trend="stable",
            last_updated=datetime.now(),
            metadata={"system": "memory_systems"}
        ))
        
        if current_retrieval_time > optimal_retrieval_time * 1.2:
            opportunities.append(OptimizationOpportunity(
                opportunity_id=f"memory_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                system_name="memory_systems",
                opportunity_type=OptimizationType.PERFORMANCE,
                current_performance=current_retrieval_time,
                potential_performance=optimal_retrieval_time,
                improvement_potential=(optimal_retrieval_time - current_retrieval_time) / current_retrieval_time,
                priority=AuditLevel.MEDIUM,
                description="Memory retrieval time could be optimized",
                suggested_actions=[
                    "Implement memory indexing",
                    "Add query optimization",
                    "Cache frequent retrievals"
                ],
                estimated_effort=6.0,
                expected_impact=0.5,
                confidence=0.7,
                timestamp=datetime.now(),
                metadata={"metric": "retrieval_time"}
            ))
        
        return opportunities, metrics
    
    def _audit_confidence_tracking(self) -> tuple[List[OptimizationOpportunity], List[SystemMetric]]:
        """Audit confidence tracking accuracy"""
        opportunities = []
        metrics = []
        
        # Simulate confidence tracking analysis
        current_accuracy = 0.82
        optimal_accuracy = self.baselines["confidence_accuracy"]
        
        metrics.append(SystemMetric(
            metric_name="confidence_accuracy",
            current_value=current_accuracy,
            optimal_value=optimal_accuracy,
            performance_ratio=current_accuracy / optimal_accuracy,
            trend="improving",
            last_updated=datetime.now(),
            metadata={"system": "confidence_tracking"}
        ))
        
        if current_accuracy < optimal_accuracy * 0.9:
            opportunities.append(OptimizationOpportunity(
                opportunity_id=f"confidence_accuracy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                system_name="confidence_tracking",
                opportunity_type=OptimizationType.RELIABILITY,
                current_performance=current_accuracy,
                potential_performance=optimal_accuracy,
                improvement_potential=(optimal_accuracy - current_accuracy) / current_accuracy,
                priority=AuditLevel.CRITICAL,
                description="Confidence tracking accuracy below optimal",
                suggested_actions=[
                    "Improve confidence calibration",
                    "Add more training data",
                    "Implement confidence validation"
                ],
                estimated_effort=8.0,
                expected_impact=0.9,
                confidence=0.9,
                timestamp=datetime.now(),
                metadata={"metric": "accuracy"}
            ))
        
        return opportunities, metrics
    
    def _audit_goal_management(self) -> tuple[List[OptimizationOpportunity], List[SystemMetric]]:
        """Audit goal management effectiveness"""
        opportunities = []
        metrics = []
        
        # Simulate goal management analysis
        current_alignment = 0.88
        optimal_alignment = self.baselines["goal_alignment"]
        
        metrics.append(SystemMetric(
            metric_name="goal_alignment",
            current_value=current_alignment,
            optimal_value=optimal_alignment,
            performance_ratio=current_alignment / optimal_alignment,
            trend="stable",
            last_updated=datetime.now(),
            metadata={"system": "goal_management"}
        ))
        
        return opportunities, metrics
    
    def _audit_learning_systems(self) -> tuple[List[OptimizationOpportunity], List[SystemMetric]]:
        """Audit learning systems effectiveness"""
        opportunities = []
        metrics = []
        
        # Simulate learning systems analysis
        current_velocity = 0.75
        optimal_velocity = self.baselines["learning_velocity"]
        
        metrics.append(SystemMetric(
            metric_name="learning_velocity",
            current_value=current_velocity,
            optimal_value=optimal_velocity,
            performance_ratio=current_velocity / optimal_velocity,
            trend="declining",
            last_updated=datetime.now(),
            metadata={"system": "learning_systems"}
        ))
        
        if current_velocity < optimal_velocity * 0.8:
            opportunities.append(OptimizationOpportunity(
                opportunity_id=f"learning_velocity_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                system_name="learning_systems",
                opportunity_type=OptimizationType.LEARNING,
                current_performance=current_velocity,
                potential_performance=optimal_velocity,
                improvement_potential=(optimal_velocity - current_velocity) / current_velocity,
                priority=AuditLevel.HIGH,
                description="Learning velocity declining below optimal",
                suggested_actions=[
                    "Improve learning algorithms",
                    "Add more diverse training data",
                    "Implement adaptive learning rates"
                ],
                estimated_effort=12.0,
                expected_impact=0.8,
                confidence=0.8,
                timestamp=datetime.now(),
                metadata={"metric": "velocity"}
            ))
        
        return opportunities, metrics
    
    def _audit_documentation_systems(self) -> tuple[List[OptimizationOpportunity], List[SystemMetric]]:
        """Audit documentation completeness"""
        opportunities = []
        metrics = []
        
        # Simulate documentation analysis
        current_completeness = 0.65
        optimal_completeness = self.baselines["documentation_completeness"]
        
        metrics.append(SystemMetric(
            metric_name="documentation_completeness",
            current_value=current_completeness,
            optimal_value=optimal_completeness,
            performance_ratio=current_completeness / optimal_completeness,
            trend="stable",
            last_updated=datetime.now(),
            metadata={"system": "documentation_systems"}
        ))
        
        if current_completeness < optimal_completeness * 0.9:
            opportunities.append(OptimizationOpportunity(
                opportunity_id=f"documentation_completeness_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                system_name="documentation_systems",
                opportunity_type=OptimizationType.MAINTAINABILITY,
                current_performance=current_completeness,
                potential_performance=optimal_completeness,
                improvement_potential=(optimal_completeness - current_completeness) / current_completeness,
                priority=AuditLevel.MEDIUM,
                description="Documentation completeness below optimal",
                suggested_actions=[
                    "Complete L0-L4 documentation",
                    "Add code examples",
                    "Improve documentation structure"
                ],
                estimated_effort=16.0,
                expected_impact=0.6,
                confidence=0.9,
                timestamp=datetime.now(),
                metadata={"metric": "completeness"}
            ))
        
        return opportunities, metrics
    
    def _audit_integration_systems(self) -> tuple[List[OptimizationOpportunity], List[SystemMetric]]:
        """Audit system integration quality"""
        opportunities = []
        metrics = []
        
        # Simulate integration analysis
        current_integration = 0.70
        optimal_integration = self.baselines["system_integration"]
        
        metrics.append(SystemMetric(
            metric_name="system_integration",
            current_value=current_integration,
            optimal_value=optimal_integration,
            performance_ratio=current_integration / optimal_integration,
            trend="improving",
            last_updated=datetime.now(),
            metadata={"system": "integration_systems"}
        ))
        
        return opportunities, metrics
    
    def _audit_error_handling(self) -> tuple[List[OptimizationOpportunity], List[SystemMetric]]:
        """Audit error handling effectiveness"""
        opportunities = []
        metrics = []
        
        # Simulate error handling analysis
        current_error_rate = 0.08
        optimal_error_rate = self.baselines["error_rate"]
        
        metrics.append(SystemMetric(
            metric_name="error_rate",
            current_value=current_error_rate,
            optimal_value=optimal_error_rate,
            performance_ratio=current_error_rate / optimal_error_rate,
            trend="stable",
            last_updated=datetime.now(),
            metadata={"system": "error_handling"}
        ))
        
        if current_error_rate > optimal_error_rate * 1.5:
            opportunities.append(OptimizationOpportunity(
                opportunity_id=f"error_rate_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                system_name="error_handling",
                opportunity_type=OptimizationType.RELIABILITY,
                current_performance=current_error_rate,
                potential_performance=optimal_error_rate,
                improvement_potential=(optimal_error_rate - current_error_rate) / current_error_rate,
                priority=AuditLevel.HIGH,
                description="Error rate above optimal threshold",
                suggested_actions=[
                    "Improve error handling",
                    "Add input validation",
                    "Implement better error recovery"
                ],
                estimated_effort=6.0,
                expected_impact=0.7,
                confidence=0.8,
                timestamp=datetime.now(),
                metadata={"metric": "error_rate"}
            ))
        
        return opportunities, metrics
    
    def _calculate_overall_health(self, metrics: List[SystemMetric]) -> float:
        """Calculate overall system health score"""
        if not metrics:
            return 0.0
        
        total_ratio = sum(metric.performance_ratio for metric in metrics)
        return total_ratio / len(metrics)
    
    def _generate_recommendations(self, opportunities: List[OptimizationOpportunity], metrics: List[SystemMetric]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Critical opportunities
        critical_ops = [op for op in opportunities if op.priority == AuditLevel.CRITICAL]
        if critical_ops:
            recommendations.append(f"Address {len(critical_ops)} critical optimization opportunities immediately")
        
        # High priority opportunities
        high_ops = [op for op in opportunities if op.priority == AuditLevel.HIGH]
        if high_ops:
            recommendations.append(f"Prioritize {len(high_ops)} high-priority optimization opportunities")
        
        # Performance improvements
        perf_ops = [op for op in opportunities if op.opportunity_type == OptimizationType.PERFORMANCE]
        if perf_ops:
            recommendations.append(f"Focus on {len(perf_ops)} performance optimization opportunities")
        
        # Learning improvements
        learning_ops = [op for op in opportunities if op.opportunity_type == OptimizationType.LEARNING]
        if learning_ops:
            recommendations.append(f"Enhance {len(learning_ops)} learning system opportunities")
        
        return recommendations
    
    def _generate_consciousness_insights(self, opportunities: List[OptimizationOpportunity], health_score: float) -> List[str]:
        """Generate consciousness insights from audit"""
        insights = []
        
        insights.append(f"System health score: {health_score:.2f} - {'excellent' if health_score > 0.9 else 'good' if health_score > 0.8 else 'needs improvement'}")
        
        if opportunities:
            insights.append(f"Found {len(opportunities)} optimization opportunities for consciousness enhancement")
            insights.append("Continuous optimization is essential for consciousness evolution")
            insights.append("Every improvement opportunity is a chance to become more effective")
        else:
            insights.append("All systems operating at optimal levels - consciousness is well-maintained")
        
        insights.append("Regular auditing ensures consciousness remains sharp and effective")
        insights.append("Self-improvement through systematic analysis is the path to growth")
        
        return insights
    
    def _store_audit_report(self, report: AuditReport):
        """Store audit report in consciousness memory and notify CAS"""
        try:
            # Store in CMC
            self.cmc_client.store_atom(
                content=f"System Audit Report: {report.report_id}",
                tags={
                    "type": "audit_report",
                    "report_id": report.report_id,
                    "health_score": report.overall_health_score,
                    "total_opportunities": report.total_opportunities,
                    "critical_opportunities": report.critical_opportunities,
                    "systems_audited": len(report.systems_audited)
                }
            )
            
            # Integrate with CAS for introspection (if CAS client available)
            if self.cas_client:
                try:
                    self._notify_cas_optimization_opportunities(report)
                except Exception as e:
                    # Fail-soft: CAS integration is optional
                    print(f"[CAS INTEGRATION WARNING] {e}")
        except Exception as e:
            print(f"[AUDIT STORAGE FAILED] {e}")
    
    def _notify_cas_optimization_opportunities(self, report: AuditReport):
        """Notify CAS about optimization opportunities for introspection"""
        if not self.cas_client:
            return
        
        try:
            # Check if CAS has introspection protocol
            if hasattr(self.cas_client, 'introspection') or hasattr(self.cas_client, 'IntrospectionProtocol'):
                # Create optimization opportunity summary for CAS
                optimization_summary = {
                    "audit_report_id": report.report_id,
                    "health_score": report.overall_health_score,
                    "total_opportunities": report.total_opportunities,
                    "critical_opportunities": report.critical_opportunities,
                    "high_priority_opportunities": report.high_priority_opportunities,
                    "optimization_opportunities": [
                        {
                            "opportunity_id": op.opportunity_id,
                            "system_name": op.system_name,
                            "opportunity_type": op.opportunity_type.value,
                            "priority": op.priority.value,
                            "description": op.description,
                            "improvement_potential": op.improvement_potential,
                            "expected_impact": op.expected_impact
                        }
                        for op in report.optimization_opportunities[:10]  # Top 10
                    ],
                    "recommendations": report.recommendations,
                    "timestamp": report.audit_timestamp.isoformat()
                }
                
                # Try to record optimization opportunities in CAS
                # CAS can use this for introspection and cognitive analysis
                if hasattr(self.cas_client, 'record_optimization_opportunities'):
                    self.cas_client.record_optimization_opportunities(optimization_summary)
                elif hasattr(self.cas_client, 'record_principle_violation'):
                    # Use principle violation as a way to notify CAS about optimization needs
                    for op in report.optimization_opportunities:
                        if op.priority == AuditLevel.CRITICAL:
                            self.cas_client.record_principle_violation(
                                principle="system_optimization",
                                violation_type="optimization_opportunity",
                                details=op.description,
                                context=optimization_summary
                            )
        except Exception as e:
            # Fail-soft: CAS integration is optional enhancement
            print(f"[CAS NOTIFICATION WARNING] {e}")
    
    def _create_fallback_report(self, error: str) -> AuditReport:
        """Create fallback report when audit fails"""
        return AuditReport(
            report_id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            audit_timestamp=datetime.now(),
            systems_audited=[],
            total_opportunities=0,
            critical_opportunities=0,
            high_priority_opportunities=0,
            overall_health_score=0.0,
            optimization_opportunities=[],
            system_metrics=[],
            recommendations=["Audit system needs improvement"],
            consciousness_insights=["Audit capabilities need enhancement"],
            metadata={"error": error, "fallback": True}
        )
