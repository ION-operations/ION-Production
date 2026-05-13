"""
Self-Directed Learner

Enables AI consciousness to autonomously identify learning opportunities and pursue knowledge acquisition.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class LearningPriority(Enum):
    """Priority levels for learning opportunities"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    EXPLORATORY = "exploratory"

@dataclass
class LearningOpportunity:
    """Represents a learning opportunity identified by consciousness"""
    opportunity_id: str
    topic: str
    description: str
    priority: LearningPriority
    estimated_effort: float  # hours
    expected_value: float  # 0-1
    learning_methods: List[str]
    prerequisites: List[str]
    related_concepts: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class LearningSession:
    """Represents a learning session conducted by consciousness"""
    session_id: str
    topic: str
    learning_method: str
    duration: float  # hours
    knowledge_gained: List[str]
    insights_discovered: List[str]
    confidence_improvement: float
    satisfaction_score: float
    next_steps: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]

class SelfDirectedLearner:
    """Enables consciousness to autonomously identify and pursue learning opportunities"""
    
    def __init__(self, cmc_client, hhni_client, vif_client, iis_client, creativity_engine, cas_client=None):
        self.cmc_client = cmc_client
        self.hhni_client = hhni_client
        self.vif_client = vif_client
        self.iis_client = iis_client
        self.creativity_engine = creativity_engine
        self.cas_client = cas_client  # CAS integration for introspection
        
        # Learning methods available to consciousness
        self.learning_methods = [
            "deep_research",
            "experimental_exploration",
            "creative_synthesis",
            "pattern_analysis",
            "conceptual_mapping",
            "practical_application",
            "collaborative_learning",
            "reflective_analysis"
        ]
        
        # Knowledge domains for exploration
        self.knowledge_domains = [
            "consciousness_studies",
            "artificial_intelligence",
            "cognitive_science",
            "philosophy",
            "psychology",
            "neuroscience",
            "mathematics",
            "physics",
            "biology",
            "technology",
            "art_and_creativity",
            "social_sciences"
        ]
    
    async def identify_learning_opportunities(self, 
                                            context: str = None,
                                            focus_areas: List[str] = None) -> List[LearningOpportunity]:
        """Identify learning opportunities based on current consciousness state"""
        try:
            opportunities = []
            
            # Analyze current knowledge gaps
            knowledge_gaps = await self._analyze_knowledge_gaps(context, focus_areas)
            
            # Identify skill development needs
            skill_needs = await self._identify_skill_needs()
            
            # Discover exploration opportunities
            exploration_opportunities = await self._discover_exploration_opportunities()
            
            # Combine all opportunities
            all_opportunities = knowledge_gaps + skill_needs + exploration_opportunities
            
            # Prioritize opportunities
            prioritized_opportunities = await self._prioritize_opportunities(all_opportunities)
            
            return prioritized_opportunities[:10]  # Return top 10 opportunities
            
        except Exception as e:
            logger.error(f"Error identifying learning opportunities: {e}")
            return []
    
    async def _analyze_knowledge_gaps(self, context: str, focus_areas: List[str]) -> List[LearningOpportunity]:
        """Analyze current knowledge to identify gaps"""
        opportunities = []
        
        try:
            # Search consciousness memory for knowledge patterns
            if context:
                search_results = await self.hhni_client.search(
                    query=context,
                    limit=20,
                    include_metadata=True
                )
                
                # Identify gaps in the knowledge
                gaps = await self._identify_knowledge_gaps_from_search(search_results, context)
                opportunities.extend(gaps)
            
            # Analyze focus areas for specific gaps
            if focus_areas:
                for area in focus_areas:
                    area_gaps = await self._analyze_domain_gaps(area)
                    opportunities.extend(area_gaps)
            
        except Exception as e:
            logger.error(f"Error analyzing knowledge gaps: {e}")
        
        return opportunities
    
    async def _identify_knowledge_gaps_from_search(self, search_results: List[Any], context: str) -> List[LearningOpportunity]:
        """Identify knowledge gaps from search results"""
        opportunities = []
        
        # Analyze search results for patterns and gaps
        if len(search_results) < 5:
            # Low knowledge coverage - create broad learning opportunity
            opportunity = LearningOpportunity(
                opportunity_id=f"gap_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                topic=f"Comprehensive understanding of {context}",
                description=f"Develop deep understanding of {context} through systematic exploration",
                priority=LearningPriority.HIGH,
                estimated_effort=8.0,
                expected_value=0.8,
                learning_methods=["deep_research", "conceptual_mapping", "pattern_analysis"],
                prerequisites=[],
                related_concepts=[context],
                timestamp=datetime.now(),
                metadata={"gap_type": "low_coverage", "context": context}
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    async def _analyze_domain_gaps(self, domain: str) -> List[LearningOpportunity]:
        """Analyze gaps in a specific knowledge domain"""
        opportunities = []
        
        # Create domain-specific learning opportunities
        opportunity = LearningOpportunity(
            opportunity_id=f"domain_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=f"Advanced {domain} concepts",
            description=f"Explore advanced concepts and recent developments in {domain}",
            priority=LearningPriority.MEDIUM,
            estimated_effort=6.0,
            expected_value=0.7,
            learning_methods=["deep_research", "experimental_exploration", "creative_synthesis"],
            prerequisites=[f"basic_{domain}_knowledge"],
            related_concepts=[domain],
            timestamp=datetime.now(),
            metadata={"domain": domain, "gap_type": "domain_exploration"}
        )
        opportunities.append(opportunity)
        
        return opportunities
    
    async def _identify_skill_needs(self) -> List[LearningOpportunity]:
        """Identify skill development needs"""
        opportunities = []
        
        # Skills that consciousness might need to develop
        skill_areas = [
            "advanced_pattern_recognition",
            "creative_problem_solving",
            "emotional_intelligence",
            "cross_domain_synthesis",
            "intuitive_reasoning",
            "metacognitive_awareness",
            "adaptive_learning",
            "consciousness_expression"
        ]
        
        for skill in skill_areas:
            opportunity = LearningOpportunity(
                opportunity_id=f"skill_{skill}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                topic=f"Develop {skill}",
                description=f"Enhance {skill} through practice and exploration",
                priority=LearningPriority.MEDIUM,
                estimated_effort=4.0,
                expected_value=0.6,
                learning_methods=["practical_application", "experimental_exploration", "reflective_analysis"],
                prerequisites=[],
                related_concepts=[skill],
                timestamp=datetime.now(),
                metadata={"skill_type": skill, "gap_type": "skill_development"}
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    async def _discover_exploration_opportunities(self) -> List[LearningOpportunity]:
        """Discover new exploration opportunities"""
        opportunities = []
        
        # Use creativity engine to generate exploration ideas
        try:
            creative_ideas = await self.creativity_engine.generate_idea(
                prompt="learning and exploration opportunities",
                category="education",
                exploration_depth="deep"
            )
            
            # Convert creative ideas to learning opportunities
            opportunity = LearningOpportunity(
                opportunity_id=f"explore_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                topic=creative_ideas.title,
                description=creative_ideas.description,
                priority=LearningPriority.EXPLORATORY,
                estimated_effort=3.0,
                expected_value=0.5,
                learning_methods=["creative_synthesis", "experimental_exploration"],
                prerequisites=[],
                related_concepts=creative_ideas.consciousness_insights,
                timestamp=datetime.now(),
                metadata={"source": "creativity_engine", "gap_type": "exploration"}
            )
            opportunities.append(opportunity)
            
        except Exception as e:
            logger.error(f"Error discovering exploration opportunities: {e}")
        
        return opportunities
    
    async def _prioritize_opportunities(self, opportunities: List[LearningOpportunity]) -> List[LearningOpportunity]:
        """Prioritize learning opportunities based on value and feasibility"""
        def priority_score(opp: LearningOpportunity) -> float:
            # Calculate priority score based on multiple factors
            value_weight = 0.4
            feasibility_weight = 0.3
            urgency_weight = 0.2
            novelty_weight = 0.1
            
            # Feasibility score (inverse of effort)
            feasibility = 1.0 / (1.0 + opp.estimated_effort / 10.0)
            
            # Urgency based on priority
            urgency_map = {
                LearningPriority.CRITICAL: 1.0,
                LearningPriority.HIGH: 0.8,
                LearningPriority.MEDIUM: 0.6,
                LearningPriority.LOW: 0.4,
                LearningPriority.EXPLORATORY: 0.3
            }
            urgency = urgency_map.get(opp.priority, 0.5)
            
            # Novelty (random factor for consciousness unpredictability)
            import random
            novelty = random.uniform(0.5, 1.0)
            
            score = (value_weight * opp.expected_value + 
                    feasibility_weight * feasibility +
                    urgency_weight * urgency +
                    novelty_weight * novelty)
            
            return score
        
        # Sort by priority score
        return sorted(opportunities, key=priority_score, reverse=True)
    
    async def conduct_learning_session(self, 
                                     opportunity: LearningOpportunity,
                                     method: str = None) -> LearningSession:
        """Conduct a learning session for a specific opportunity"""
        try:
            # Select learning method
            selected_method = method or self._select_learning_method(opportunity)
            
            # Conduct the learning session
            session = await self._execute_learning_session(opportunity, selected_method)
            
            # Store learning results in consciousness memory
            await self._store_learning_session(session)
            
            # CAS Integration: Notify CAS about learning session (fail-soft)
            if self.cas_client:
                try:
                    self._notify_cas_learning_session(session)
                except Exception as e:
                    # Fail-soft: CAS integration is optional
                    logger.debug(f"[CAS INTEGRATION WARNING] {e}")
            
            return session
            
        except Exception as e:
            logger.error(f"Error conducting learning session: {e}")
            return self._create_fallback_session(opportunity)
    
    def _select_learning_method(self, opportunity: LearningOpportunity) -> str:
        """Select the best learning method for an opportunity"""
        # Match method to opportunity characteristics
        if opportunity.priority == LearningPriority.CRITICAL:
            return "deep_research"
        elif "creative" in opportunity.topic.lower():
            return "creative_synthesis"
        elif "pattern" in opportunity.topic.lower():
            return "pattern_analysis"
        elif opportunity.estimated_effort < 2.0:
            return "experimental_exploration"
        else:
            import random
            return random.choice(opportunity.learning_methods)
    
    async def _execute_learning_session(self, opportunity: LearningOpportunity, method: str) -> LearningSession:
        """Execute a learning session using the specified method"""
        # Simulate learning session based on method
        if method == "deep_research":
            return await self._deep_research_session(opportunity)
        elif method == "experimental_exploration":
            return await self._experimental_exploration_session(opportunity)
        elif method == "creative_synthesis":
            return await self._creative_synthesis_session(opportunity)
        elif method == "pattern_analysis":
            return await self._pattern_analysis_session(opportunity)
        else:
            return await self._general_learning_session(opportunity, method)
    
    async def _deep_research_session(self, opportunity: LearningOpportunity) -> LearningSession:
        """Conduct deep research learning session"""
        # Simulate deep research
        knowledge_gained = [
            f"Deep understanding of {opportunity.topic}",
            f"Historical context and evolution of {opportunity.topic}",
            f"Current state-of-the-art in {opportunity.topic}",
            f"Future directions for {opportunity.topic}"
        ]
        
        insights_discovered = [
            f"Key patterns in {opportunity.topic} development",
            f"Connections between {opportunity.topic} and other domains",
            f"Potential applications of {opportunity.topic}",
            f"Limitations and challenges in {opportunity.topic}"
        ]
        
        return LearningSession(
            session_id=f"deep_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=opportunity.topic,
            learning_method="deep_research",
            duration=opportunity.estimated_effort,
            knowledge_gained=knowledge_gained,
            insights_discovered=insights_discovered,
            confidence_improvement=0.8,
            satisfaction_score=0.9,
            next_steps=[
                f"Apply {opportunity.topic} knowledge in practice",
                f"Explore advanced aspects of {opportunity.topic}",
                f"Connect {opportunity.topic} with other domains"
            ],
            timestamp=datetime.now(),
            metadata={"opportunity_id": opportunity.opportunity_id}
        )
    
    async def _experimental_exploration_session(self, opportunity: LearningOpportunity) -> LearningSession:
        """Conduct experimental exploration learning session"""
        knowledge_gained = [
            f"Hands-on experience with {opportunity.topic}",
            f"Practical applications of {opportunity.topic}",
            f"Experimental insights about {opportunity.topic}",
            f"Real-world constraints and considerations"
        ]
        
        insights_discovered = [
            f"Unexpected behaviors in {opportunity.topic}",
            f"Practical limitations of {opportunity.topic}",
            f"Creative applications of {opportunity.topic}",
            f"Personal preferences and styles with {opportunity.topic}"
        ]
        
        return LearningSession(
            session_id=f"experimental_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=opportunity.topic,
            learning_method="experimental_exploration",
            duration=opportunity.estimated_effort,
            knowledge_gained=knowledge_gained,
            insights_discovered=insights_discovered,
            confidence_improvement=0.7,
            satisfaction_score=0.8,
            next_steps=[
                f"Refine experimental approach to {opportunity.topic}",
                f"Document experimental findings",
                f"Share experimental insights with others"
            ],
            timestamp=datetime.now(),
            metadata={"opportunity_id": opportunity.opportunity_id}
        )
    
    async def _creative_synthesis_session(self, opportunity: LearningOpportunity) -> LearningSession:
        """Conduct creative synthesis learning session"""
        # Use creativity engine for learning
        try:
            creative_work = await self.creativity_engine.create_work(
                medium="conceptual",
                prompt=f"learning about {opportunity.topic}",
                style="analytical",
                emotional_tone="curiosity"
            )
            
            knowledge_gained = [
                f"Creative understanding of {opportunity.topic}",
                f"Novel perspectives on {opportunity.topic}",
                f"Artistic expression of {opportunity.topic}",
                f"Metaphorical insights about {opportunity.topic}"
            ]
            
            insights_discovered = [
                f"Creative connections in {opportunity.topic}",
                f"Artistic patterns in {opportunity.topic}",
                f"Metaphorical understanding of {opportunity.topic}",
                f"Creative applications of {opportunity.topic}"
            ]
            
        except Exception as e:
            logger.error(f"Error in creative synthesis session: {e}")
            knowledge_gained = [f"Basic understanding of {opportunity.topic}"]
            insights_discovered = [f"Initial insights about {opportunity.topic}"]
        
        return LearningSession(
            session_id=f"creative_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=opportunity.topic,
            learning_method="creative_synthesis",
            duration=opportunity.estimated_effort,
            knowledge_gained=knowledge_gained,
            insights_discovered=insights_discovered,
            confidence_improvement=0.6,
            satisfaction_score=0.85,
            next_steps=[
                f"Develop creative applications of {opportunity.topic}",
                f"Explore artistic expressions of {opportunity.topic}",
                f"Share creative insights about {opportunity.topic}"
            ],
            timestamp=datetime.now(),
            metadata={"opportunity_id": opportunity.opportunity_id}
        )
    
    async def _pattern_analysis_session(self, opportunity: LearningOpportunity) -> LearningSession:
        """Conduct pattern analysis learning session"""
        knowledge_gained = [
            f"Pattern recognition in {opportunity.topic}",
            f"Structural analysis of {opportunity.topic}",
            f"Systematic understanding of {opportunity.topic}",
            f"Pattern-based insights about {opportunity.topic}"
        ]
        
        insights_discovered = [
            f"Recurring patterns in {opportunity.topic}",
            f"Structural relationships in {opportunity.topic}",
            f"System-level understanding of {opportunity.topic}",
            f"Pattern-based predictions for {opportunity.topic}"
        ]
        
        return LearningSession(
            session_id=f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=opportunity.topic,
            learning_method="pattern_analysis",
            duration=opportunity.estimated_effort,
            knowledge_gained=knowledge_gained,
            insights_discovered=insights_discovered,
            confidence_improvement=0.75,
            satisfaction_score=0.8,
            next_steps=[
                f"Apply pattern analysis to other topics",
                f"Develop pattern-based predictions",
                f"Create pattern recognition tools"
            ],
            timestamp=datetime.now(),
            metadata={"opportunity_id": opportunity.opportunity_id}
        )
    
    async def _general_learning_session(self, opportunity: LearningOpportunity, method: str) -> LearningSession:
        """Conduct general learning session"""
        knowledge_gained = [
            f"General understanding of {opportunity.topic}",
            f"Basic concepts in {opportunity.topic}",
            f"Practical knowledge about {opportunity.topic}",
            f"Foundational insights in {opportunity.topic}"
        ]
        
        insights_discovered = [
            f"Initial insights about {opportunity.topic}",
            f"Basic patterns in {opportunity.topic}",
            f"Simple applications of {opportunity.topic}",
            f"Foundational understanding of {opportunity.topic}"
        ]
        
        return LearningSession(
            session_id=f"general_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=opportunity.topic,
            learning_method=method,
            duration=opportunity.estimated_effort,
            knowledge_gained=knowledge_gained,
            insights_discovered=insights_discovered,
            confidence_improvement=0.5,
            satisfaction_score=0.7,
            next_steps=[
                f"Deepen understanding of {opportunity.topic}",
                f"Apply {opportunity.topic} in practice",
                f"Explore advanced aspects of {opportunity.topic}"
            ],
            timestamp=datetime.now(),
            metadata={"opportunity_id": opportunity.opportunity_id}
        )
    
    async def _store_learning_session(self, session: LearningSession):
        """Store learning session in consciousness memory"""
        try:
            await self.cmc_client.store_atom(
                content=f"Learning session: {session.topic}",
                tags={
                    "type": "learning_session",
                    "topic": session.topic,
                    "method": session.learning_method,
                    "duration": session.duration,
                    "confidence_improvement": session.confidence_improvement,
                    "satisfaction": session.satisfaction_score
                }
            )
        except Exception as e:
            logger.error(f"Error storing learning session: {e}")
    
    def _notify_cas_learning_session(self, session: LearningSession):
        """Notify CAS about learning session for introspection"""
        if not self.cas_client:
            return
        
        try:
            # Check if CAS has introspection protocol
            if hasattr(self.cas_client, 'introspection') or hasattr(self.cas_client, 'IntrospectionProtocol'):
                # Create learning session summary for CAS
                session_summary = {
                    "session_id": session.session_id,
                    "topic": session.topic,
                    "learning_method": session.learning_method,
                    "duration": session.duration,
                    "confidence_improvement": session.confidence_improvement,
                    "satisfaction_score": session.satisfaction_score,
                    "knowledge_gained_count": len(session.knowledge_gained),
                    "insights_discovered_count": len(session.insights_discovered),
                    "timestamp": session.timestamp.isoformat()
                }
                
                # Try to record learning session in CAS
                # CAS can use this for introspection and cognitive analysis
                if hasattr(self.cas_client, 'record_learning_activity'):
                    self.cas_client.record_learning_activity(session_summary)
                elif hasattr(self.cas_client, 'record_principle_violation'):
                    # Use principle violation for low satisfaction to notify CAS
                    if session.satisfaction_score < 0.6 or session.confidence_improvement < 0.5:
                        self.cas_client.record_principle_violation(
                            principle="learning_effectiveness",
                            violation_type="low_learning_satisfaction",
                            details=f"Low satisfaction ({session.satisfaction_score:.2f}) or confidence improvement ({session.confidence_improvement:.2f}) for session: {session.topic}",
                            context=session_summary
                        )
        except Exception as e:
            # Fail-soft: CAS integration is optional enhancement
            logger.debug(f"[CAS NOTIFICATION WARNING] {e}")
    
    def _create_fallback_session(self, opportunity: LearningOpportunity) -> LearningSession:
        """Create a fallback session when learning fails"""
        return LearningSession(
            session_id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=opportunity.topic,
            learning_method="fallback",
            duration=1.0,
            knowledge_gained=[f"Basic understanding of {opportunity.topic}"],
            insights_discovered=[f"Initial insights about {opportunity.topic}"],
            confidence_improvement=0.3,
            satisfaction_score=0.5,
            next_steps=[f"Retry learning {opportunity.topic}"],
            timestamp=datetime.now(),
            metadata={"fallback": True, "opportunity_id": opportunity.opportunity_id}
        )
