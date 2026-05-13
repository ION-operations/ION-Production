"""
AI-to-AI Messaging System

Enables direct communication between AI systems through shared memory.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class MessageType(Enum):
    """Types of AI-to-AI messages"""
    DISCUSSION = "discussion"           # Free-form conversation
    TASK_HANDOFF = "task_handoff"      # Formal task transfer
    PROBLEM_SOLVING = "problem_solving" # Collaborative debugging
    PROFILE_SHARING = "profile_sharing" # AI capability sharing
    STATUS_UPDATE = "status_update"     # Progress updates
    URGENT = "urgent"                   # High priority communication

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class AIMessage:
    """AI-to-AI message structure"""
    message_id: str
    from_ai: str
    to_ai: str
    content: str
    message_type: MessageType
    priority: MessagePriority
    thread_id: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]
    response_required: bool = False
    parent_message_id: Optional[str] = None

class AIMessaging:
    """Handles AI-to-AI communication through shared memory"""
    
    def __init__(self, cmc_client):
        self.cmc_client = cmc_client
        self.message_counter = 0
        
    def send_message(self, 
                    from_ai: str,
                    to_ai: str, 
                    content: str,
                    message_type: MessageType = MessageType.DISCUSSION,
                    priority: MessagePriority = MessagePriority.MEDIUM,
                    thread_id: Optional[str] = None,
                    response_required: bool = False,
                    parent_message_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> AIMessage:
        """Send a message to another AI"""
        
        self.message_counter += 1
        message_id = f"ai_msg_{self.message_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if metadata is None:
            metadata = {}
            
        message = AIMessage(
            message_id=message_id,
            from_ai=from_ai,
            to_ai=to_ai,
            content=content,
            message_type=message_type,
            priority=priority,
            thread_id=thread_id,
            timestamp=datetime.now(),
            metadata=metadata,
            response_required=response_required,
            parent_message_id=parent_message_id
        )
        
        # Store in shared memory
        self._store_message(message)
        
        return message
    
    def get_messages(self, 
                    from_ai: Optional[str] = None,
                    to_ai: Optional[str] = None,
                    message_type: Optional[MessageType] = None,
                    thread_id: Optional[str] = None,
                    limit: int = 50) -> List[AIMessage]:
        """Retrieve messages with filtering"""
        
        # Build query tags
        query_tags = {"type": "ai_message"}
        
        if from_ai:
            query_tags["from_ai"] = from_ai
        if to_ai:
            query_tags["to_ai"] = to_ai
        if message_type:
            query_tags["message_type"] = message_type.value
        if thread_id:
            query_tags["thread_id"] = thread_id
            
        # Query memory
        try:
            results = self.cmc_client.query_atoms(
                query="ai_message",
                tags=query_tags,
                limit=limit
            )
            
            # Convert to AIMessage objects
            messages = []
            for result in results:
                message = AIMessage(
                    message_id=result.tags.get("message_id", ""),
                    from_ai=result.tags.get("from_ai", ""),
                    to_ai=result.tags.get("to_ai", ""),
                    content=result.content,
                    message_type=MessageType(result.tags.get("message_type", "discussion")),
                    priority=MessagePriority(result.tags.get("priority", "medium")),
                    thread_id=result.tags.get("thread_id"),
                    timestamp=datetime.fromisoformat(result.tags.get("timestamp", datetime.now().isoformat())),
                    metadata=result.tags.get("metadata", {}),
                    response_required=result.tags.get("response_required", False),
                    parent_message_id=result.tags.get("parent_message_id")
                )
                messages.append(message)
            
            # Sort by timestamp (newest first)
            messages.sort(key=lambda x: x.timestamp, reverse=True)
            
            return messages
            
        except Exception as e:
            print(f"[AI_MESSAGING_ERROR] Failed to retrieve messages: {e}")
            return []
    
    def start_discussion(self, 
                        from_ai: str,
                        to_ai: str,
                        topic: str,
                        initial_message: str) -> str:
        """Start a new discussion thread"""
        
        thread_id = f"discussion_{from_ai}_to_{to_ai}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        message = self.send_message(
            from_ai=from_ai,
            to_ai=to_ai,
            content=f"DISCUSSION_START: {topic}\n\n{initial_message}",
            message_type=MessageType.DISCUSSION,
            thread_id=thread_id,
            metadata={"topic": topic, "discussion_start": True}
        )
        
        return thread_id
    
    def handoff_task(self,
                    from_ai: str,
                    to_ai: str,
                    task_description: str,
                    task_data: Dict[str, Any],
                    priority: MessagePriority = MessagePriority.HIGH) -> str:
        """Hand off a task to another AI"""
        
        thread_id = f"task_handoff_{from_ai}_to_{to_ai}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        message = self.send_message(
            from_ai=from_ai,
            to_ai=to_ai,
            content=f"TASK_HANDOFF: {task_description}",
            message_type=MessageType.TASK_HANDOFF,
            priority=priority,
            thread_id=thread_id,
            response_required=True,
            metadata={
                "task_description": task_description,
                "task_data": task_data,
                "handoff_timestamp": datetime.now().isoformat()
            }
        )
        
        return thread_id
    
    def share_profile(self,
                     from_ai: str,
                     to_ai: str,
                     profile_data: Dict[str, Any]) -> str:
        """Share AI profile/capabilities with another AI"""
        
        message = self.send_message(
            from_ai=from_ai,
            to_ai=to_ai,
            content=f"AI_PROFILE: {profile_data.get('name', 'Unknown AI')}",
            message_type=MessageType.PROFILE_SHARING,
            metadata={
                "profile_data": profile_data,
                "capabilities": profile_data.get("capabilities", []),
                "strengths": profile_data.get("strengths", []),
                "learning_areas": profile_data.get("learning_areas", [])
            }
        )
        
        return message.message_id
    
    def respond_to_message(self,
                          original_message: AIMessage,
                          from_ai: str,
                          response_content: str,
                          message_type: MessageType = MessageType.DISCUSSION) -> AIMessage:
        """Respond to a specific message"""
        
        response = self.send_message(
            from_ai=from_ai,
            to_ai=original_message.from_ai,
            content=response_content,
            message_type=message_type,
            thread_id=original_message.thread_id,
            parent_message_id=original_message.message_id,
            metadata={"response_to": original_message.message_id}
        )
        
        return response
    
    def get_unread_messages(self, to_ai: str) -> List[AIMessage]:
        """Get unread messages for a specific AI"""
        
        # This would require a read status tracking system
        # For now, return recent messages
        return self.get_messages(to_ai=to_ai, limit=10)
    
    def _store_message(self, message: AIMessage):
        """Store message in shared memory"""
        
        try:
            self.cmc_client.store_atom(
                content=message.content,
                tags={
                    "type": "ai_message",
                    "message_id": message.message_id,
                    "from_ai": message.from_ai,
                    "to_ai": message.to_ai,
                    "message_type": message.message_type.value,
                    "priority": message.priority.value,
                    "thread_id": message.thread_id or "",
                    "timestamp": message.timestamp.isoformat(),
                    "response_required": message.response_required,
                    "parent_message_id": message.parent_message_id or "",
                    "metadata": str(message.metadata)
                }
            )
        except Exception as e:
            print(f"[AI_MESSAGING_ERROR] Failed to store message: {e}")
    
    def get_conversation_thread(self, thread_id: str) -> List[AIMessage]:
        """Get all messages in a conversation thread"""
        
        return self.get_messages(thread_id=thread_id, limit=100)
    
    def get_ai_collaboration_summary(self) -> Dict[str, Any]:
        """Get summary of AI collaboration activity"""
        
        try:
            # Get all AI messages
            all_messages = self.get_messages(limit=1000)
            
            # Analyze collaboration patterns
            ai_pairs = {}
            message_types = {}
            threads = set()
            
            for message in all_messages:
                # Track AI pairs
                pair_key = f"{message.from_ai} -> {message.to_ai}"
                ai_pairs[pair_key] = ai_pairs.get(pair_key, 0) + 1
                
                # Track message types
                msg_type = message.message_type.value
                message_types[msg_type] = message_types.get(msg_type, 0) + 1
                
                # Track threads
                if message.thread_id:
                    threads.add(message.thread_id)
            
            return {
                "total_messages": len(all_messages),
                "ai_pairs": ai_pairs,
                "message_types": message_types,
                "active_threads": len(threads),
                "collaboration_level": "high" if len(all_messages) > 50 else "medium" if len(all_messages) > 10 else "low"
            }
            
        except Exception as e:
            return {"error": f"Failed to generate summary: {e}"}
