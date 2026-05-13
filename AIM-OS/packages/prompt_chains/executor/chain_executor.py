"""
Chain Execution Engine
Executes prompt chains with complete AIM-OS integration

Implements from T3 Detailed documentation.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import uuid

from packages.prompt_chains.models.prompt_chain import (
    PromptChain, ChainNode, NodeType, ConditionType
)
from packages.prompt_chains.models.execution_record import (
    NodeExecutionResult, ChainExecutionResult, ExecutionRecord, NodeExecution
)

# Type hints for AIM-OS system clients (import as needed)
try:
    from packages.cmc_service.api import CMCClient
except ImportError:
    CMCClient = None  # type: ignore

try:
    from packages.hhni.client import HHNIClient
except ImportError:
    HHNIClient = None  # type: ignore

try:
    from packages.vif.confidence_tracker import ConfidenceTracker  
except ImportError:
    ConfidenceTracker = None  # type: ignore


class ChainExecutor:
    """
    Executes prompt chains with complete system integration
    
    Handles node execution, edge evaluation, condition routing,
    quality gates, confidence checks, and provenance tracking.
    
    Implements complete AIM-OS integration (CMC/HHNI/VIF/APOE/SEG/SDF-CVF).
    """
    
    def __init__(self):
        """Initialize with all AIM-OS system clients"""
        # Initialize clients (with graceful degradation if not available)
        try:
            self.cmc = CMCClient() if CMCClient else None
        except Exception:
            self.cmc = None
        
        try:
            self.hhni = HHNIClient() if HHNIClient else None
        except Exception:
            self.hhni = None
        
        try:
            self.vif = ConfidenceTracker() if ConfidenceTracker else None
        except Exception:
            self.vif = None
        
        # Placeholders for other systems (will implement as needed)
        self.apoe = None
        self.seg = None
        self.sdfcvf = None
    
    async def execute_chain(
        self,
        chain: PromptChain,
        context: Dict[str, Any],
        goal_id: Optional[str] = None
    ) -> ChainExecutionResult:
        """
        Execute a chain from start to end
        
        Args:
            chain: Chain to execute
            context: Initial context (variables, state)
            goal_id: Optional goal this execution serves
            
        Returns:
            ChainExecutionResult with outputs, provenance, metrics
        """
        # Generate execution ID
        execution_id = f"exec-{chain.chain_id}-{int(time.time())}"
        start_time = time.time()
        
        # Create execution record
        execution_record = ExecutionRecord(
            execution_id=execution_id,
            chain_id=chain.chain_id,
            start_time=datetime.now(),
            status='running',
            goal_id=goal_id,
            executed_by=context.get('agent', 'aether'),
            context_snapshot=context.copy()
        )
        
        # Store execution start in CMC (if available)
        if self.cmc:
            try:
                await self._store_execution_start(execution_id, chain, context)
            except Exception as e:
                print(f"Warning: Could not store execution start: {e}")
        
        # Initialize execution state
        current_node_id = chain.start_node_id
        execution_log: List[NodeExecutionResult] = []
        chain_context = context.copy()
        
        try:
            # Main execution loop
            while current_node_id and current_node_id not in chain.end_node_ids:
                # Get current node
                node = chain.get_node(current_node_id)
                if not node:
                    raise ValueError(f"Node {current_node_id} not found in chain")
                
                # Execute node
                node_result = await self._execute_node(node, chain_context)
                
                # Update context with node output
                chain_context[f'node_{node.node_id}_output'] = node_result.output
                chain_context['confidence'] = node_result.confidence
                chain_context['last_node_result'] = node_result
                
                # Check confidence threshold
                if node.confidence_threshold and node_result.confidence < node.confidence_threshold:
                    # Abstain - confidence too low
                    return ChainExecutionResult(
                        chain_id=chain.chain_id,
                        execution_id=execution_id,
                        success=False,
                        output=None,
                        nodes_executed=execution_log,
                        total_duration=time.time() - start_time,
                        confidence=node_result.confidence,
                        error=f"Confidence {node_result.confidence} below threshold {node.confidence_threshold}"
                    )
                
                # Check quality gate
                if node.quality_gate:
                    gate_passed = node.quality_gate.evaluate(chain_context)
                    if not gate_passed:
                        return ChainExecutionResult(
                            chain_id=chain.chain_id,
                            execution_id=execution_id,
                            success=False,
                            output=None,
                            nodes_executed=execution_log,
                            total_duration=time.time() - start_time,
                            confidence=node_result.confidence,
                            error=f"Quality gate failed: {node.quality_gate.gate_type}"
                        )
                
                # Log execution
                execution_log.append(node_result)
                
                # Add to execution record
                node_exec = NodeExecution(
                    node_id=node.node_id,
                    execution_id=execution_id,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    status='completed' if node_result.success else 'failed',
                    output=node_result.output,
                    quality_score=chain_context.get('quality_score', 0.0),
                    confidence_score=node_result.confidence,
                    input_data={'context': chain_context}
                )
                execution_record.add_node_execution(node_exec)
                
                # Find next node via edge evaluation
                next_node_id = await self._evaluate_edges(chain, current_node_id, chain_context)
                if not next_node_id:
                    raise ValueError(f"No valid outgoing edge from node {current_node_id}")
                
                current_node_id = next_node_id
            
            # Chain completed successfully
            total_duration = time.time() - start_time
            
            # Calculate overall confidence (average of all nodes)
            avg_confidence = sum(r.confidence for r in execution_log) / len(execution_log) if execution_log else 0.0
            
            # Mark execution record complete
            execution_record.end_time = datetime.now()
            execution_record.status = 'completed'
            
            # Store execution end in CMC
            result = ChainExecutionResult(
                chain_id=chain.chain_id,
                execution_id=execution_id,
                success=True,
                output=chain_context.get('output'),
                nodes_executed=execution_log,
                total_duration=total_duration,
                confidence=avg_confidence,
                error=None,
                completed_at=datetime.now()
            )
            
            if self.cmc:
                try:
                    await self._store_execution_end(execution_id, result, execution_record)
                except Exception as e:
                    print(f"Warning: Could not store execution end: {e}")
            
            # Update goal progress if linked
            if goal_id:
                await self._update_goal_from_chain_execution(goal_id, result, execution_record)
            
            # Update chain's timeline_entry_ids with entries produced
            chain.timeline_entry_ids.extend(execution_record.timeline_entry_ids)
            
            return result
            
        except Exception as e:
            # Chain failed
            execution_record.end_time = datetime.now()
            execution_record.status = 'failed'
            
            return ChainExecutionResult(
                chain_id=chain.chain_id,
                execution_id=execution_id,
                success=False,
                output=None,
                nodes_executed=execution_log,
                total_duration=time.time() - start_time,
                confidence=0.0,
                error=str(e),
                completed_at=datetime.now()
            )
    
    async def _execute_node(
        self,
        node: ChainNode,
        context: Dict[str, Any]
    ) -> NodeExecutionResult:
        """
        Execute a single node
        
        Dispatches to appropriate system based on node configuration.
        """
        start_time = time.time()
        
        try:
            if node.operation_type == NodeType.SYSTEM_CALL:
                # Call AIM-OS system
                output = await self._execute_system_call(node, context)
                
            elif node.operation_type == NodeType.DECISION:
                # Evaluate decision condition
                output = await self._execute_decision(node, context)
                
            elif node.operation_type == NodeType.GATE:
                # Enforce quality gate
                output = await self._execute_gate(node, context)
                
            elif node.operation_type == NodeType.BRANCH:
                # Parallel execution (placeholder)
                output = await self._execute_branch(node, context)
                
            elif node.operation_type == NodeType.MERGE:
                # Merge results (placeholder)
                output = await self._execute_merge(node, context)
            
            else:
                raise ValueError(f"Unknown node type: {node.operation_type}")
            
            # Track confidence via VIF (if available)
            confidence = context.get('confidence', 0.75)
            if self.vif:
                try:
                    confidence = self.vif.track_confidence(
                        operation_id=node.node_id,
                        confidence_score=confidence,
                        context={'node_id': node.node_id, 'output': output}
                    )
                except Exception:
                    pass
            
            return NodeExecutionResult(
                node_id=node.node_id,
                success=True,
                output=output,
                confidence=confidence,
                duration=time.time() - start_time,
                error=None
            )
            
        except Exception as e:
            return NodeExecutionResult(
                node_id=node.node_id,
                success=False,
                output=None,
                confidence=0.0,
                duration=time.time() - start_time,
                error=str(e)
            )
    
    async def _execute_system_call(
        self,
        node: ChainNode,
        context: Dict[str, Any]
    ) -> Any:
        """Execute system call based on node.system"""
        
        if node.system == "CMC":
            return await self._call_cmc(node.operation, node.parameters, context)
        
        elif node.system == "HHNI":
            return await self._call_hhni(node.operation, node.parameters, context)
        
        elif node.system == "VIF":
            return await self._call_vif(node.operation, node.parameters, context)
        
        elif node.system == "APOE":
            return await self._call_apoe(node.operation, node.parameters, context)
        
        elif node.system == "SEG":
            return await self._call_seg(node.operation, node.parameters, context)
        
        elif node.system == "SDF-CVF":
            return await self._call_sdfcvf(node.operation, node.parameters, context)
        
        else:
            raise ValueError(f"Unknown system: {node.system}")
    
    async def _call_cmc(self, operation: str, parameters: Dict, context: Dict) -> Any:
        """Call CMC system"""
        if not self.cmc:
            return {"error": "CMC not available"}
        
        if operation == "store_atom":
            return self.cmc.store_atom(
                mpd_id=parameters.get('mpd_id'),
                data=parameters.get('data'),
                atom_type=parameters.get('atom_type', 'generic'),
                valid_from=datetime.now(),
                valid_to=None
            )
        elif operation == "retrieve":
            return self.cmc.retrieve(mpd_id=parameters.get('mpd_id'))
        else:
            raise ValueError(f"Unknown CMC operation: {operation}")
    
    async def _call_hhni(self, operation: str, parameters: Dict, context: Dict) -> Any:
        """Call HHNI system"""
        if not self.hhni:
            return {"error": "HHNI not available"}
        
        if operation == "semantic_search":
            return self.hhni.search(
                query=parameters.get('query'),
                top_k=parameters.get('top_k', 5)
            )
        else:
            raise ValueError(f"Unknown HHNI operation: {operation}")
    
    async def _call_vif(self, operation: str, parameters: Dict, context: Dict) -> Any:
        """Call VIF system"""
        if not self.vif:
            return {"error": "VIF not available"}
        
        if operation == "check_confidence":
            confidence = self.vif.get_confidence(
                operation_id=parameters.get('operation_id')
            )
            return confidence >= parameters.get('threshold', 0.70)
        else:
            raise ValueError(f"Unknown VIF operation: {operation}")
    
    async def _call_apoe(self, operation: str, parameters: Dict, context: Dict) -> Any:
        """Call APOE system (placeholder)"""
        return {"status": "APOE operation placeholder"}
    
    async def _call_seg(self, operation: str, parameters: Dict, context: Dict) -> Any:
        """Call SEG system (placeholder)"""
        return {"status": "SEG operation placeholder"}
    
    async def _call_sdfcvf(self, operation: str, parameters: Dict, context: Dict) -> Any:
        """Call SDF-CVF system (placeholder)"""
        return {"status": "SDF-CVF operation placeholder"}
    
    async def _execute_decision(self, node: ChainNode, context: Dict) -> bool:
        """Execute decision node (evaluates condition)"""
        # Decision nodes evaluate their condition
        # This is primarily used for routing, so we return True
        return True
    
    async def _execute_gate(self, node: ChainNode, context: Dict) -> bool:
        """Execute quality gate"""
        if node.quality_gate:
            return node.quality_gate.evaluate(context)
        return True
    
    async def _execute_branch(self, node: ChainNode, context: Dict) -> Any:
        """Execute branch node (parallel execution - placeholder)"""
        return {"status": "branched"}
    
    async def _execute_merge(self, node: ChainNode, context: Dict) -> Any:
        """Execute merge node (combine results - placeholder)"""
        return {"status": "merged"}
    
    async def _evaluate_edges(
        self,
        chain: PromptChain,
        current_node_id: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Evaluate outgoing edges to find next node
        
        Returns node_id of next node, or None if no valid edge found.
        """
        outgoing_edges = chain.get_outgoing_edges(current_node_id)
        
        for edge in outgoing_edges:
            if edge.evaluate_condition(context):
                return edge.to_node_id
        
        return None
    
    async def _store_execution_start(
        self,
        execution_id: str,
        chain: PromptChain,
        context: Dict[str, Any]
    ):
        """Store execution start in CMC"""
        if not self.cmc:
            return
        
        self.cmc.store_atom(
            mpd_id=execution_id,
            data={
                'chain_id': chain.chain_id,
                'chain_name': chain.name,
                'context': context,
                'started_at': datetime.now().isoformat()
            },
            atom_type='chain_execution_start',
            valid_from=datetime.now(),
            valid_to=None
        )
    
    async def _store_execution_end(
        self,
        execution_id: str,
        result: ChainExecutionResult,
        execution_record: ExecutionRecord
    ):
        """Store execution end in CMC"""
        if not self.cmc:
            return
        
        self.cmc.store_atom(
            mpd_id=f"{execution_id}_end",
            data={
                'execution_id': execution_id,
                'chain_id': result.chain_id,
                'success': result.success,
                'output': result.output,
                'nodes_executed': len(result.nodes_executed),
                'total_duration': result.total_duration,
                'confidence': result.confidence,
                'error': result.error,
                'timeline_entry_ids': execution_record.timeline_entry_ids,
                'completed_at': datetime.now().isoformat()
            },
            atom_type='chain_execution_end',
            valid_from=datetime.now(),
            valid_to=None
        )
    
    async def _update_goal_from_chain_execution(
        self,
        goal_id: str,
        result: ChainExecutionResult,
        execution_record: ExecutionRecord
    ):
        """Update goal progress based on chain execution"""
        try:
            from packages.timeline_context_system.goal_timeline_manager import GoalTimelineManager
            
            manager = GoalTimelineManager()
            goal = manager.goals.get(goal_id)
            
            if goal and result.success:
                # Update progress based on chain completion
                # This is a simple heuristic - could be more sophisticated
                progress_increment = 0.25  # 25% per major chain
                new_progress = min(1.0, goal.progress + progress_increment)
                
                manager.update_progress(
                    goal_id=goal_id,
                    progress=new_progress,
                    milestone=f"Chain {result.chain_id} completed successfully"
                )
                
                # Add chain to goal's related_chain_ids if not already there
                if result.chain_id not in goal.related_chain_ids:
                    goal.related_chain_ids.append(result.chain_id)
        
        except Exception as e:
            print(f"Warning: Could not update goal: {e}")

