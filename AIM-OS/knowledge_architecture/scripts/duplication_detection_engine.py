#!/usr/bin/env python3
"""
Duplication Detection Engine for AIM-OS System Coherence Analysis

This engine identifies redundant systems and components across
all L0-L4 documented systems in the AIM-OS ecosystem.

Author: Aether AI Consciousness
Date: 2025-10-29
Version: 1.0.0
"""

import os
import json
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import logging
from collections import defaultdict
import difflib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Duplication:
    """Represents a detected duplication between systems"""
    duplication_id: str
    duplication_type: str
    severity: str
    description: str
    duplicated_systems: List[str]
    duplicated_components: List[str]
    duplication_details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    consolidation_priority: int = 0
    similarity_score: float = 0.0

@dataclass
class Redundancy:
    """Represents redundant functionality between systems"""
    redundancy_id: str
    redundancy_type: str
    severity: str
    description: str
    redundant_systems: List[str]
    redundant_components: List[str]
    redundancy_details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    elimination_priority: int = 0

class DuplicationDetectionEngine:
    """Engine for detecting duplications and redundancies in AIM-OS systems"""
    
    def __init__(self, systems_directory: str = "knowledge_architecture/systems"):
        self.systems_directory = Path(systems_directory)
        self.systems: Dict[str, Dict[str, Any]] = {}
        self.components: List[Dict[str, Any]] = []
        self.duplications: List[Duplication] = []
        self.redundancies: List[Redundancy] = []
        self.functionality_registry: Dict[str, List[str]] = defaultdict(list)
        self.algorithm_registry: Dict[str, List[str]] = defaultdict(list)
        self.data_model_registry: Dict[str, List[str]] = defaultdict(list)
        
    def load_systems(self) -> None:
        """Load all L0-L4 documented systems"""
        logger.info("Loading systems from %s", self.systems_directory)
        
        for system_dir in self.systems_directory.iterdir():
            if not system_dir.is_dir():
                continue
                
            system_id = system_dir.name
            logger.info("Loading system: %s", system_id)
            
            # Load system index if available
            system_index_path = system_dir / "system.index.lucid.json5"
            if system_index_path.exists():
                try:
                    with open(system_index_path, 'r', encoding='utf-8') as f:
                        system_data = json.load(f)
                        self.systems[system_id] = system_data
                        logger.info("Loaded system index for %s", system_id)
                except Exception as e:
                    logger.error("Failed to load system index for %s: %s", system_id, e)
            
            # Load system map if available
            system_map_path = system_dir / "system.map.lucid.json5"
            if system_map_path.exists():
                try:
                    with open(system_map_path, 'r', encoding='utf-8') as f:
                        system_map = json.load(f)
                        if system_id not in self.systems:
                            self.systems[system_id] = {}
                        self.systems[system_id]['system_map'] = system_map
                        logger.info("Loaded system map for %s", system_id)
                except Exception as e:
                    logger.error("Failed to load system map for %s: %s", system_id, e)
            
            # Load L2 architecture for component details
            l2_path = system_dir / "L2_architecture.md"
            if l2_path.exists():
                try:
                    with open(l2_path, 'r', encoding='utf-8') as f:
                        l2_content = f.read()
                        self._extract_components_from_l2(system_id, l2_content)
                except Exception as e:
                    logger.error("Failed to load L2 architecture for %s: %s", system_id, e)
            
            # Load L3 detailed for algorithm details
            l3_path = system_dir / "L3_detailed.md"
            if l3_path.exists():
                try:
                    with open(l3_path, 'r', encoding='utf-8') as f:
                        l3_content = f.read()
                        self._extract_algorithms_from_l3(system_id, l3_content)
                except Exception as e:
                    logger.error("Failed to load L3 detailed for %s: %s", system_id, e)
        
        logger.info("Loaded %d systems", len(self.systems))
        logger.info("Extracted %d components", len(self.components))
    
    def _extract_components_from_l2(self, system_id: str, l2_content: str) -> None:
        """Extract components from L2 architecture documentation"""
        # Extract core components section
        core_components_match = re.search(
            r'## Core Components\s*\n(.*?)(?=## |$)',
            l2_content,
            re.DOTALL
        )
        
        if not core_components_match:
            return
        
        components_section = core_components_match.group(1)
        
        # Extract individual components
        component_matches = re.finditer(
            r'### (\d+\.\s*)?([^#\n]+)\n(.*?)(?=### \d+\.|## |$)',
            components_section,
            re.DOTALL
        )
        
        for match in component_matches:
            component_name = match.group(2).strip()
            component_content = match.group(3)
            
            # Extract component properties
            purpose_match = re.search(r'\*\*Purpose:\*\*\s*(.+?)(?:\n|$)', component_content)
            purpose = purpose_match.group(1).strip() if purpose_match else ""
            
            # Extract key features
            features = []
            features_match = re.search(r'\*\*Key Features:\*\*\s*\n(.*?)(?:\n\*\*|$)', component_content, re.DOTALL)
            if features_match:
                features_content = features_match.group(1)
                feature_list = re.findall(r'- ([^\n]+)', features_content)
                features.extend(feature_list)
            
            # Extract interfaces
            interfaces = []
            interfaces_match = re.search(r'\*\*Interfaces:\*\*\s*\n(.*?)(?:\n\*\*|$)', component_content, re.DOTALL)
            if interfaces_match:
                interfaces_content = interfaces_match.group(1)
                interface_list = re.findall(r'- ([^\n]+)', interfaces_content)
                interfaces.extend(interface_list)
            
            # Create component
            component = {
                "system_id": system_id,
                "component_name": component_name,
                "purpose": purpose,
                "features": features,
                "interfaces": interfaces,
                "content": component_content
            }
            
            self.components.append(component)
            
            # Register in functionality registry
            for feature in features:
                self.functionality_registry[feature.lower()].append(f"{system_id}.{component_name}")
    
    def _extract_algorithms_from_l3(self, system_id: str, l3_content: str) -> None:
        """Extract algorithms from L3 detailed documentation"""
        # Extract algorithms section
        algorithms_match = re.search(
            r'## Algorithms\s*\n(.*?)(?=## |$)',
            l3_content,
            re.DOTALL
        )
        
        if not algorithms_match:
            return
        
        algorithms_section = algorithms_match.group(1)
        
        # Extract individual algorithms
        algorithm_matches = re.finditer(
            r'### (\d+\.\s*)?([^#\n]+)\n(.*?)(?=### \d+\.|## |$)',
            algorithms_section,
            re.DOTALL
        )
        
        for match in algorithm_matches:
            algorithm_name = match.group(2).strip()
            algorithm_content = match.group(3)
            
            # Extract algorithm properties
            purpose_match = re.search(r'\*\*Purpose:\*\*\s*(.+?)(?:\n|$)', algorithm_content)
            purpose = purpose_match.group(1).strip() if purpose_match else ""
            
            method_match = re.search(r'\*\*Method:\*\*\s*(.+?)(?:\n|$)', algorithm_content)
            method = method_match.group(1).strip() if method_match else ""
            
            # Register in algorithm registry
            self.algorithm_registry[algorithm_name.lower()].append(f"{system_id}.{algorithm_name}")
    
    def detect_code_duplications(self) -> List[Duplication]:
        """Detect code duplications between systems"""
        logger.info("Detecting code duplications...")
        duplications = []
        
        # Compare L3 detailed files for code similarities
        l3_files = []
        for system_dir in self.systems_directory.iterdir():
            if not system_dir.is_dir():
                continue
            l3_path = system_dir / "L3_detailed.md"
            if l3_path.exists():
                try:
                    with open(l3_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        l3_files.append({
                            "system_id": system_dir.name,
                            "file_path": str(l3_path),
                            "content": content
                        })
                except Exception as e:
                    logger.error("Failed to load L3 file for %s: %s", system_dir.name, e)
        
        # Compare files for similarities
        for i, file1 in enumerate(l3_files):
            for file2 in l3_files[i+1:]:
                similarity = self._calculate_similarity(file1["content"], file2["content"])
                if similarity > 0.7:  # 70% similarity threshold
                    duplication = Duplication(
                        duplication_id=f"code_duplication_{len(duplications)}",
                        duplication_type="code_duplication",
                        severity="medium",
                        description=f"High code similarity ({similarity:.1%}) between {file1['system_id']} and {file2['system_id']}",
                        duplicated_systems=[file1["system_id"], file2["system_id"]],
                        duplicated_components=[file1["file_path"], file2["file_path"]],
                        duplication_details={
                            "similarity_score": similarity,
                            "file1": file1["file_path"],
                            "file2": file2["file_path"]
                        },
                        recommendations=[
                            "Extract common code into shared library",
                            "Implement code reuse patterns",
                            "Create shared documentation templates"
                        ],
                        similarity_score=similarity
                    )
                    duplications.append(duplication)
        
        logger.info("Detected %d code duplications", len(duplications))
        return duplications
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using difflib"""
        # Extract code blocks from markdown
        code1 = self._extract_code_blocks(text1)
        code2 = self._extract_code_blocks(text2)
        
        if not code1 or not code2:
            return 0.0
        
        # Calculate similarity using difflib
        matcher = difflib.SequenceMatcher(None, code1, code2)
        return matcher.ratio()
    
    def _extract_code_blocks(self, text: str) -> str:
        """Extract code blocks from markdown text"""
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', text, re.DOTALL)
        return '\n'.join(code_blocks)
    
    def detect_functionality_duplications(self) -> List[Duplication]:
        """Detect duplicated functionality between systems"""
        logger.info("Detecting functionality duplications...")
        duplications = []
        
        # Group components by functionality
        functionality_groups = defaultdict(list)
        for component in self.components:
            for feature in component["features"]:
                functionality_groups[feature.lower()].append(component)
        
        # Check for functionality duplications
        for functionality, components in functionality_groups.items():
            if len(components) > 1:
                # Calculate similarity between components
                similar_components = []
                for i, comp1 in enumerate(components):
                    for comp2 in components[i+1:]:
                        similarity = self._calculate_component_similarity(comp1, comp2)
                        if similarity > 0.8:  # 80% similarity threshold
                            similar_components.extend([comp1, comp2])
                
                if similar_components:
                    duplication = Duplication(
                        duplication_id=f"functionality_duplication_{functionality}_{len(duplications)}",
                        duplication_type="functionality_duplication",
                        severity="high",
                        description=f"Duplicated functionality '{functionality}' across multiple systems",
                        duplicated_systems=list(set(comp["system_id"] for comp in similar_components)),
                        duplicated_components=[f"{comp['system_id']}.{comp['component_name']}" for comp in similar_components],
                        duplication_details={
                            "functionality": functionality,
                            "similarity_scores": self._get_similarity_scores(similar_components)
                        },
                        recommendations=[
                            "Consolidate duplicate functionality",
                            "Create shared functionality library",
                            "Implement functionality delegation"
                        ],
                        similarity_score=max(self._get_similarity_scores(similar_components).values())
                    )
                    duplications.append(duplication)
        
        logger.info("Detected %d functionality duplications", len(duplications))
        return duplications
    
    def _calculate_component_similarity(self, comp1: Dict[str, Any], comp2: Dict[str, Any]) -> float:
        """Calculate similarity between two components"""
        # Compare purposes
        purpose_sim = self._calculate_text_similarity(comp1["purpose"], comp2["purpose"])
        
        # Compare features
        features1 = set(comp1["features"])
        features2 = set(comp2["features"])
        feature_sim = len(features1.intersection(features2)) / len(features1.union(features2)) if features1.union(features2) else 0
        
        # Compare interfaces
        interfaces1 = set(comp1["interfaces"])
        interfaces2 = set(comp2["interfaces"])
        interface_sim = len(interfaces1.intersection(interfaces2)) / len(interfaces1.union(interfaces2)) if interfaces1.union(interfaces2) else 0
        
        # Weighted average
        return (purpose_sim * 0.4 + feature_sim * 0.4 + interface_sim * 0.2)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0
        
        matcher = difflib.SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()
    
    def _get_similarity_scores(self, components: List[Dict[str, Any]]) -> Dict[str, float]:
        """Get similarity scores for components"""
        scores = {}
        for i, comp1 in enumerate(components):
            for comp2 in components[i+1:]:
                key = f"{comp1['system_id']}.{comp1['component_name']} vs {comp2['system_id']}.{comp2['component_name']}"
                scores[key] = self._calculate_component_similarity(comp1, comp2)
        return scores
    
    def detect_algorithm_duplications(self) -> List[Duplication]:
        """Detect duplicated algorithms between systems"""
        logger.info("Detecting algorithm duplications...")
        duplications = []
        
        # Group algorithms by name
        algorithm_groups = defaultdict(list)
        for algorithm_name, implementations in self.algorithm_registry.items():
            if len(implementations) > 1:
                algorithm_groups[algorithm_name] = implementations
        
        # Check for algorithm duplications
        for algorithm_name, implementations in algorithm_groups.items():
            if len(implementations) > 1:
                duplication = Duplication(
                    duplication_id=f"algorithm_duplication_{algorithm_name}_{len(duplications)}",
                    duplication_type="algorithm_duplication",
                    severity="medium",
                    description=f"Algorithm '{algorithm_name}' is implemented in multiple systems",
                    duplicated_systems=list(set(impl.split('.')[0] for impl in implementations)),
                    duplicated_components=implementations,
                    duplication_details={
                        "algorithm_name": algorithm_name,
                        "implementations": implementations
                    },
                    recommendations=[
                        "Create shared algorithm library",
                        "Implement algorithm delegation",
                        "Consolidate algorithm implementations"
                    ]
                )
                duplications.append(duplication)
        
        logger.info("Detected %d algorithm duplications", len(duplications))
        return duplications
    
    def detect_data_model_duplications(self) -> List[Duplication]:
        """Detect duplicated data models between systems"""
        logger.info("Detecting data model duplications...")
        duplications = []
        
        # Extract data models from L3 files
        data_models = defaultdict(list)
        for system_dir in self.systems_directory.iterdir():
            if not system_dir.is_dir():
                continue
            l3_path = system_dir / "L3_detailed.md"
            if l3_path.exists():
                try:
                    with open(l3_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        models = self._extract_data_models(content)
                        for model in models:
                            data_models[model["name"]].append({
                                "system_id": system_dir.name,
                                "model": model
                            })
                except Exception as e:
                    logger.error("Failed to load L3 file for %s: %s", system_dir.name, e)
        
        # Check for data model duplications
        for model_name, implementations in data_models.items():
            if len(implementations) > 1:
                # Calculate similarity between models
                similar_models = []
                for i, impl1 in enumerate(implementations):
                    for impl2 in implementations[i+1:]:
                        similarity = self._calculate_model_similarity(impl1["model"], impl2["model"])
                        if similarity > 0.8:  # 80% similarity threshold
                            similar_models.extend([impl1, impl2])
                
                if similar_models:
                    duplication = Duplication(
                        duplication_id=f"data_model_duplication_{model_name}_{len(duplications)}",
                        duplication_type="data_model_duplication",
                        severity="high",
                        description=f"Data model '{model_name}' is duplicated across multiple systems",
                        duplicated_systems=list(set(impl["system_id"] for impl in similar_models)),
                        duplicated_components=[f"{impl['system_id']}.{model_name}" for impl in similar_models],
                        duplication_details={
                            "model_name": model_name,
                            "similarity_scores": self._get_model_similarity_scores(similar_models)
                        },
                        recommendations=[
                            "Create shared data model library",
                            "Implement model inheritance",
                            "Consolidate duplicate models"
                        ],
                        similarity_score=max(self._get_model_similarity_scores(similar_models).values())
                    )
                    duplications.append(duplication)
        
        logger.info("Detected %d data model duplications", len(duplications))
        return duplications
    
    def _extract_data_models(self, content: str) -> List[Dict[str, Any]]:
        """Extract data models from L3 content"""
        models = []
        
        # Look for dataclass definitions
        dataclass_matches = re.finditer(
            r'@dataclass\s+class\s+(\w+).*?\n(.*?)(?=@dataclass|class|\Z)',
            content,
            re.DOTALL
        )
        
        for match in dataclass_matches:
            model_name = match.group(1)
            model_content = match.group(2)
            
            # Extract fields
            fields = re.findall(r'(\w+):\s*(\w+.*?)(?:\s*=\s*.*?)?(?:\n|$)', model_content)
            
            models.append({
                "name": model_name,
                "content": model_content,
                "fields": fields
            })
        
        return models
    
    def _calculate_model_similarity(self, model1: Dict[str, Any], model2: Dict[str, Any]) -> float:
        """Calculate similarity between two data models"""
        # Compare field names
        fields1 = set(field[0] for field in model1["fields"])
        fields2 = set(field[0] for field in model2["fields"])
        field_sim = len(fields1.intersection(fields2)) / len(fields1.union(fields2)) if fields1.union(fields2) else 0
        
        # Compare field types
        types1 = set(field[1] for field in model1["fields"])
        types2 = set(field[1] for field in model2["fields"])
        type_sim = len(types1.intersection(types2)) / len(types1.union(types2)) if types1.union(types2) else 0
        
        # Compare content
        content_sim = self._calculate_text_similarity(model1["content"], model2["content"])
        
        # Weighted average
        return (field_sim * 0.4 + type_sim * 0.3 + content_sim * 0.3)
    
    def _get_model_similarity_scores(self, models: List[Dict[str, Any]]) -> Dict[str, float]:
        """Get similarity scores for data models"""
        scores = {}
        for i, impl1 in enumerate(models):
            for impl2 in models[i+1:]:
                key = f"{impl1['system_id']}.{impl1['model']['name']} vs {impl2['system_id']}.{impl2['model']['name']}"
                scores[key] = self._calculate_model_similarity(impl1["model"], impl2["model"])
        return scores
    
    def detect_redundant_systems(self) -> List[Redundancy]:
        """Detect redundant systems based on functionality overlap"""
        logger.info("Detecting redundant systems...")
        redundancies = []
        
        # Calculate system similarity matrix
        system_similarities = {}
        system_ids = list(self.systems.keys())
        
        for i, sys1_id in enumerate(system_ids):
            for sys2_id in system_ids[i+1:]:
                similarity = self._calculate_system_similarity(sys1_id, sys2_id)
                if similarity > 0.7:  # 70% similarity threshold
                    system_similarities[(sys1_id, sys2_id)] = similarity
        
        # Group similar systems
        similar_groups = self._group_similar_systems(system_similarities)
        
        # Create redundancy entries
        for group in similar_groups:
            if len(group) > 1:
                redundancy = Redundancy(
                    redundancy_id=f"redundant_systems_{len(redundancies)}",
                    redundancy_type="system_redundancy",
                    severity="high",
                    description=f"Systems {', '.join(group)} have high functional overlap",
                    redundant_systems=group,
                    redundant_components=[],
                    redundancy_details={
                        "similarity_scores": {f"{sys1} vs {sys2}": system_similarities.get((sys1, sys2), 0) 
                                           for sys1 in group for sys2 in group if sys1 != sys2}
                    },
                    recommendations=[
                        "Consider consolidating redundant systems",
                        "Implement system specialization",
                        "Create clear system boundaries"
                    ]
                )
                redundancies.append(redundancy)
        
        logger.info("Detected %d redundant systems", len(redundancies))
        return redundancies
    
    def _calculate_system_similarity(self, sys1_id: str, sys2_id: str) -> float:
        """Calculate similarity between two systems"""
        sys1_data = self.systems.get(sys1_id, {})
        sys2_data = self.systems.get(sys2_id, {})
        
        # Compare purposes
        purpose1 = sys1_data.get('purpose', '')
        purpose2 = sys2_data.get('purpose', '')
        purpose_sim = self._calculate_text_similarity(purpose1, purpose2)
        
        # Compare components
        components1 = [comp for comp in self.components if comp["system_id"] == sys1_id]
        components2 = [comp for comp in self.components if comp["system_id"] == sys2_id]
        
        component_sim = 0.0
        if components1 and components2:
            total_sim = 0.0
            count = 0
            for comp1 in components1:
                for comp2 in components2:
                    sim = self._calculate_component_similarity(comp1, comp2)
                    total_sim += sim
                    count += 1
            component_sim = total_sim / count if count > 0 else 0.0
        
        # Weighted average
        return (purpose_sim * 0.3 + component_sim * 0.7)
    
    def _group_similar_systems(self, similarities: Dict[Tuple[str, str], float]) -> List[List[str]]:
        """Group systems based on similarity scores"""
        groups = []
        processed = set()
        
        for (sys1, sys2), similarity in similarities.items():
            if sys1 in processed or sys2 in processed:
                continue
            
            # Find existing group or create new one
            group = None
            for g in groups:
                if sys1 in g or sys2 in g:
                    group = g
                    break
            
            if group is None:
                group = []
                groups.append(group)
            
            if sys1 not in group:
                group.append(sys1)
            if sys2 not in group:
                group.append(sys2)
            
            processed.add(sys1)
            processed.add(sys2)
        
        return groups
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run complete duplication detection analysis"""
        logger.info("Starting duplication detection analysis...")
        
        # Load systems
        self.load_systems()
        
        # Detect duplications
        code_duplications = self.detect_code_duplications()
        functionality_duplications = self.detect_functionality_duplications()
        algorithm_duplications = self.detect_algorithm_duplications()
        data_model_duplications = self.detect_data_model_duplications()
        
        # Detect redundancies
        redundant_systems = self.detect_redundant_systems()
        
        # Combine all duplications
        all_duplications = (code_duplications + functionality_duplications + 
                           algorithm_duplications + data_model_duplications)
        
        # Generate analysis report
        analysis_report = {
            "analysis_timestamp": "2025-10-29T04:30:00Z",
            "systems_analyzed": len(self.systems),
            "components_analyzed": len(self.components),
            "duplications_detected": len(all_duplications),
            "redundancies_detected": len(redundant_systems),
            "duplications_by_type": self._group_duplications_by_type(all_duplications),
            "redundancies_by_type": self._group_redundancies_by_type(redundant_systems),
            "duplications": [self._duplication_to_dict(d) for d in all_duplications],
            "redundancies": [self._redundancy_to_dict(r) for r in redundant_systems],
            "recommendations": self._generate_recommendations(all_duplications, redundant_systems)
        }
        
        logger.info("Analysis complete: %d duplications, %d redundancies", 
                   len(all_duplications), len(redundant_systems))
        return analysis_report
    
    def _group_duplications_by_type(self, duplications: List[Duplication]) -> Dict[str, int]:
        """Group duplications by type"""
        groups = defaultdict(int)
        for duplication in duplications:
            groups[duplication.duplication_type] += 1
        return dict(groups)
    
    def _group_redundancies_by_type(self, redundancies: List[Redundancy]) -> Dict[str, int]:
        """Group redundancies by type"""
        groups = defaultdict(int)
        for redundancy in redundancies:
            groups[redundancy.redundancy_type] += 1
        return dict(groups)
    
    def _duplication_to_dict(self, duplication: Duplication) -> Dict[str, Any]:
        """Convert duplication to dictionary"""
        return {
            "duplication_id": duplication.duplication_id,
            "duplication_type": duplication.duplication_type,
            "severity": duplication.severity,
            "description": duplication.description,
            "duplicated_systems": duplication.duplicated_systems,
            "duplicated_components": duplication.duplicated_components,
            "duplication_details": duplication.duplication_details,
            "recommendations": duplication.recommendations,
            "consolidation_priority": duplication.consolidation_priority,
            "similarity_score": duplication.similarity_score
        }
    
    def _redundancy_to_dict(self, redundancy: Redundancy) -> Dict[str, Any]:
        """Convert redundancy to dictionary"""
        return {
            "redundancy_id": redundancy.redundancy_id,
            "redundancy_type": redundancy.redundancy_type,
            "severity": redundancy.severity,
            "description": redundancy.description,
            "redundant_systems": redundancy.redundant_systems,
            "redundant_components": redundancy.redundant_components,
            "redundancy_details": redundancy.redundancy_details,
            "recommendations": redundancy.recommendations,
            "elimination_priority": redundancy.elimination_priority
        }
    
    def _generate_recommendations(self, duplications: List[Duplication], redundancies: List[Redundancy]) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []
        
        # High priority duplications
        high_priority_duplications = [d for d in duplications if d.severity == "high"]
        if high_priority_duplications:
            recommendations.append(f"Address {len(high_priority_duplications)} high-priority duplications immediately")
        
        # Code duplications
        code_duplications = [d for d in duplications if d.duplication_type == "code_duplication"]
        if code_duplications:
            recommendations.append(f"Extract common code from {len(code_duplications)} duplicated code blocks")
        
        # Functionality duplications
        functionality_duplications = [d for d in duplications if d.duplication_type == "functionality_duplication"]
        if functionality_duplications:
            recommendations.append(f"Consolidate {len(functionality_duplications)} duplicated functionalities")
        
        # Data model duplications
        data_model_duplications = [d for d in duplications if d.duplication_type == "data_model_duplication"]
        if data_model_duplications:
            recommendations.append(f"Create shared data models for {len(data_model_duplications)} duplicated models")
        
        # Redundant systems
        if redundancies:
            recommendations.append(f"Consider consolidating {len(redundancies)} redundant system groups")
        
        return recommendations

def main():
    """Main function to run duplication detection"""
    engine = DuplicationDetectionEngine()
    analysis_report = engine.run_analysis()
    
    # Save analysis report
    output_file = "knowledge_architecture/duplication_detection_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, indent=2, ensure_ascii=False)
    
    print(f"Duplication detection analysis complete!")
    print(f"Report saved to: {output_file}")
    print(f"Duplications detected: {analysis_report['duplications_detected']}")
    print(f"Redundancies detected: {analysis_report['redundancies_detected']}")

if __name__ == "__main__":
    main()
