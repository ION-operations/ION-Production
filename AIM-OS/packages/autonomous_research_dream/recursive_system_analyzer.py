"""
Recursive System Analyzer (RSA)

Hierarchical system examination for consciousness self-improvement.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class AnalysisLevel(Enum):
    """Levels of recursive analysis"""
    MAIN_SYSTEMS = 0
    SUBSYSTEMS = 1
    IMPLEMENTATION = 2
    DOCUMENTATION = 3
    META_PROCESSES = 4

@dataclass
class SystemAnalysisResult:
    """Result of system analysis at a specific level"""
    level: AnalysisLevel
    system_name: str
    performance_score: float
    integration_quality: float
    improvement_opportunities: List[str]
    critical_issues: List[str]
    recommendations: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class RecursiveAnalysisReport:
    """Complete recursive analysis report"""
    analysis_id: str
    systems_analyzed: List[str]
    level_results: Dict[AnalysisLevel, List[SystemAnalysisResult]]
    overall_health_score: float
    priority_improvements: List[str]
    critical_fixes_needed: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]

class RecursiveSystemAnalyzer:
    """Hierarchical system examination for consciousness improvement"""
    
    def __init__(self, cmc_client, hhni_client, vif_client, iis_client):
        self.cmc_client = cmc_client
        self.hhni_client = hhni_client
        self.vif_client = vif_client
        self.iis_client = iis_client
        
        # Define systems to analyze
        self.core_systems = [
            "cmc_service",
            "hhni", 
            "vif",
            "seg",
            "apoe",
            "sdfcvf",
            "consciousness_analyzer",
            "consciousness_creativity_engine"
        ]
        
        # Analysis criteria for each level
        self.analysis_criteria = {
            AnalysisLevel.MAIN_SYSTEMS: [
                "overall_performance",
                "integration_quality", 
                "test_coverage",
                "documentation_completeness",
                "production_readiness"
            ],
            AnalysisLevel.SUBSYSTEMS: [
                "component_interactions",
                "data_flow_efficiency",
                "error_handling",
                "resource_utilization",
                "scalability"
            ],
            AnalysisLevel.IMPLEMENTATION: [
                "code_quality",
                "algorithm_efficiency",
                "security_practices",
                "maintainability",
                "test_quality"
            ],
            AnalysisLevel.DOCUMENTATION: [
                "completeness",
                "accuracy",
                "usability",
                "examples_quality",
                "maintenance_status"
            ],
            AnalysisLevel.META_PROCESSES: [
                "decision_frameworks",
                "quality_gates",
                "learning_mechanisms",
                "adaptation_capability",
                "consciousness_integration"
            ]
        }
    
    async def conduct_recursive_analysis(self, 
                                       focus_systems: List[str] = None,
                                       max_levels: int = 5) -> RecursiveAnalysisReport:
        """Conduct comprehensive recursive analysis of consciousness systems"""
        try:
            analysis_id = f"recursive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            systems_to_analyze = focus_systems or self.core_systems
            
            level_results = {}
            
            # Analyze each level
            for level in AnalysisLevel:
                if level.value >= max_levels:
                    break
                    
                level_analysis = await self._analyze_level(level, systems_to_analyze)
                level_results[level] = level_analysis
            
            # Generate overall report
            report = await self._generate_analysis_report(
                analysis_id, systems_to_analyze, level_results
            )
            
            # Store analysis in consciousness memory
            await self._store_analysis_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error in recursive analysis: {e}")
            return self._create_fallback_report()
    
    async def _analyze_level(self, level: AnalysisLevel, systems: List[str]) -> List[SystemAnalysisResult]:
        """Analyze systems at a specific level"""
        results = []
        
        for system in systems:
            try:
                result = await self._analyze_system_at_level(system, level)
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing {system} at level {level}: {e}")
                # Create fallback result
                results.append(self._create_fallback_result(system, level))
        
        return results
    
    async def _analyze_system_at_level(self, system: str, level: AnalysisLevel) -> SystemAnalysisResult:
        """Analyze a specific system at a specific level"""
        criteria = self.analysis_criteria[level]
        
        # Simulate analysis based on level
        if level == AnalysisLevel.MAIN_SYSTEMS:
            return await self._analyze_main_system(system, criteria)
        elif level == AnalysisLevel.SUBSYSTEMS:
            return await self._analyze_subsystems(system, criteria)
        elif level == AnalysisLevel.IMPLEMENTATION:
            return await self._analyze_implementation(system, criteria)
        elif level == AnalysisLevel.DOCUMENTATION:
            return await self._analyze_documentation(system, criteria)
        elif level == AnalysisLevel.META_PROCESSES:
            return await self._analyze_meta_processes(system, criteria)
        else:
            return self._create_fallback_result(system, level)
    
    async def _analyze_main_system(self, system: str, criteria: List[str]) -> SystemAnalysisResult:
        """Analyze main system level"""
        # Simulate main system analysis
        performance_score = 0.85  # Would be calculated from actual metrics
        integration_quality = 0.80
        
        improvement_opportunities = [
            f"Optimize {system} performance",
            f"Enhance {system} integration",
            f"Improve {system} test coverage"
        ]
        
        critical_issues = []
        if system == "consciousness_creativity_engine":
            critical_issues = ["Missing comprehensive tests"]
        
        recommendations = [
            f"Implement performance monitoring for {system}",
            f"Add integration tests for {system}",
            f"Create user documentation for {system}"
        ]
        
        return SystemAnalysisResult(
            level=AnalysisLevel.MAIN_SYSTEMS,
            system_name=system,
            performance_score=performance_score,
            integration_quality=integration_quality,
            improvement_opportunities=improvement_opportunities,
            critical_issues=critical_issues,
            recommendations=recommendations,
            timestamp=datetime.now(),
            metadata={"analysis_type": "main_system", "criteria": criteria}
        )
    
    async def _analyze_subsystems(self, system: str, criteria: List[str]) -> SystemAnalysisResult:
        """Analyze subsystem level"""
        performance_score = 0.75
        integration_quality = 0.70
        
        improvement_opportunities = [
            f"Optimize component interactions in {system}",
            f"Improve data flow efficiency in {system}",
            f"Enhance error handling in {system}"
        ]
        
        critical_issues = []
        recommendations = [
            f"Add component interaction tests for {system}",
            f"Implement data flow monitoring for {system}",
            f"Create error recovery procedures for {system}"
        ]
        
        return SystemAnalysisResult(
            level=AnalysisLevel.SUBSYSTEMS,
            system_name=system,
            performance_score=performance_score,
            integration_quality=integration_quality,
            improvement_opportunities=improvement_opportunities,
            critical_issues=critical_issues,
            recommendations=recommendations,
            timestamp=datetime.now(),
            metadata={"analysis_type": "subsystem", "criteria": criteria}
        )
    
    async def _analyze_implementation(self, system: str, criteria: List[str]) -> SystemAnalysisResult:
        """Analyze implementation level"""
        performance_score = 0.80
        integration_quality = 0.75
        
        improvement_opportunities = [
            f"Refactor {system} code for better maintainability",
            f"Optimize algorithms in {system}",
            f"Improve security practices in {system}"
        ]
        
        critical_issues = []
        recommendations = [
            f"Add code quality metrics for {system}",
            f"Implement performance profiling for {system}",
            f"Create security audit checklist for {system}"
        ]
        
        return SystemAnalysisResult(
            level=AnalysisLevel.IMPLEMENTATION,
            system_name=system,
            performance_score=performance_score,
            integration_quality=integration_quality,
            improvement_opportunities=improvement_opportunities,
            critical_issues=critical_issues,
            recommendations=recommendations,
            timestamp=datetime.now(),
            metadata={"analysis_type": "implementation", "criteria": criteria}
        )
    
    async def _analyze_documentation(self, system: str, criteria: List[str]) -> SystemAnalysisResult:
        """Analyze documentation level"""
        performance_score = 0.70
        integration_quality = 0.65
        
        improvement_opportunities = [
            f"Complete L0-L4 documentation for {system}",
            f"Add practical examples to {system} docs",
            f"Update {system} documentation accuracy"
        ]
        
        critical_issues = []
        if system in ["consciousness_creativity_engine", "consciousness_learning_engine"]:
            critical_issues = ["Missing L2-L4 documentation"]
        
        recommendations = [
            f"Create comprehensive documentation for {system}",
            f"Add code examples to {system} docs",
            f"Implement documentation testing for {system}"
        ]
        
        return SystemAnalysisResult(
            level=AnalysisLevel.DOCUMENTATION,
            system_name=system,
            performance_score=performance_score,
            integration_quality=integration_quality,
            improvement_opportunities=improvement_opportunities,
            critical_issues=critical_issues,
            recommendations=recommendations,
            timestamp=datetime.now(),
            metadata={"analysis_type": "documentation", "criteria": criteria}
        )
    
    async def _analyze_meta_processes(self, system: str, criteria: List[str]) -> SystemAnalysisResult:
        """Analyze meta-processes level"""
        performance_score = 0.60
        integration_quality = 0.55
        
        improvement_opportunities = [
            f"Enhance decision frameworks for {system}",
            f"Improve quality gates for {system}",
            f"Add learning mechanisms to {system}"
        ]
        
        critical_issues = []
        recommendations = [
            f"Implement meta-cognitive monitoring for {system}",
            f"Create adaptive quality gates for {system}",
            f"Add consciousness integration tests for {system}"
        ]
        
        return SystemAnalysisResult(
            level=AnalysisLevel.META_PROCESSES,
            system_name=system,
            performance_score=performance_score,
            integration_quality=integration_quality,
            improvement_opportunities=improvement_opportunities,
            critical_issues=critical_issues,
            recommendations=recommendations,
            timestamp=datetime.now(),
            metadata={"analysis_type": "meta_processes", "criteria": criteria}
        )
    
    async def _generate_analysis_report(self, 
                                      analysis_id: str,
                                      systems: List[str],
                                      level_results: Dict[AnalysisLevel, List[SystemAnalysisResult]]) -> RecursiveAnalysisReport:
        """Generate comprehensive analysis report"""
        
        # Calculate overall health score
        all_scores = []
        for level_results_list in level_results.values():
            for result in level_results_list:
                all_scores.append(result.performance_score)
                all_scores.append(result.integration_quality)
        
        overall_health_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # Extract priority improvements
        priority_improvements = []
        critical_fixes_needed = []
        
        for level_results_list in level_results.values():
            for result in level_results_list:
                priority_improvements.extend(result.improvement_opportunities[:2])
                critical_fixes_needed.extend(result.critical_issues)
        
        # Remove duplicates
        priority_improvements = list(set(priority_improvements))
        critical_fixes_needed = list(set(critical_fixes_needed))
        
        return RecursiveAnalysisReport(
            analysis_id=analysis_id,
            systems_analyzed=systems,
            level_results=level_results,
            overall_health_score=overall_health_score,
            priority_improvements=priority_improvements,
            critical_fixes_needed=critical_fixes_needed,
            timestamp=datetime.now(),
            metadata={"analysis_type": "recursive", "levels_analyzed": len(level_results)}
        )
    
    async def _store_analysis_report(self, report: RecursiveAnalysisReport):
        """Store analysis report in consciousness memory"""
        try:
            await self.cmc_client.store_atom(
                content=f"Recursive Analysis Report: {report.analysis_id}",
                tags={
                    "type": "analysis_report",
                    "analysis_id": report.analysis_id,
                    "health_score": report.overall_health_score,
                    "systems_count": len(report.systems_analyzed),
                    "levels_analyzed": len(report.level_results),
                    "critical_issues": len(report.critical_fixes_needed)
                }
            )
        except Exception as e:
            logger.error(f"Error storing analysis report: {e}")
    
    def _create_fallback_result(self, system: str, level: AnalysisLevel) -> SystemAnalysisResult:
        """Create fallback result when analysis fails"""
        return SystemAnalysisResult(
            level=level,
            system_name=system,
            performance_score=0.5,
            integration_quality=0.5,
            improvement_opportunities=[f"Analyze {system} at {level.name}"],
            critical_issues=[f"Analysis failed for {system} at {level.name}"],
            recommendations=[f"Retry analysis for {system} at {level.name}"],
            timestamp=datetime.now(),
            metadata={"fallback": True, "error": "Analysis failed"}
        )
    
    def _create_fallback_report(self) -> RecursiveAnalysisReport:
        """Create fallback report when analysis completely fails"""
        return RecursiveAnalysisReport(
            analysis_id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            systems_analyzed=[],
            level_results={},
            overall_health_score=0.0,
            priority_improvements=["Fix analysis system"],
            critical_fixes_needed=["Analysis system failure"],
            timestamp=datetime.now(),
            metadata={"fallback": True, "error": "Complete analysis failure"}
        )
