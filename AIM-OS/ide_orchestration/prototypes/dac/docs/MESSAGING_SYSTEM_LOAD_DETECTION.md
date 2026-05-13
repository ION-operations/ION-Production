# Messaging System with Built-In Load Detection

**Purpose:** Design messaging system with real-time load detection built into message flow  
**Date:** 2025-01-27  
**Status:** ARCHITECTURE_DESIGN  
**Author:** Aether (from Braden's insight)  
**Related Systems:** Agent Orchestration, Messaging System, Load Detection, Automatic Notifications

---

## 🎯 **BRADEN'S CRITICAL INSIGHT**

**Braden's Statement:**
> "it shouldn't even be monitoring for messages to nexus etc.. it should be built into the messaging system. there should be some way that if there are too many messages and too much tokens input from them per minute or something then it notifies scheduler/manager etc. real processes not check and balances but automation in sync."

**Core Principle:**
- **Built-In Detection:** Load detection is built into the messaging system itself, not a separate monitoring service
- **Real-Time Tracking:** Track message count and token input per minute as messages flow through
- **Automatic Notifications:** Automatically notify scheduler/manager when thresholds exceeded
- **Real Automation:** Real processes, not checks and balances - automation in sync with message flow

---

## 🧠 **THE ARCHITECTURE**

### **1. Messaging System with Built-In Load Detection**

**Message Flow with Load Tracking:**
- Messages flow through messaging system
- System tracks metrics in real-time as messages flow
- System automatically detects when thresholds exceeded
- System automatically notifies scheduler/manager

**Messaging System:**
```python
class MessagingSystem:
    """Messaging system with built-in load detection"""
    
    def __init__(self):
        self.message_queue = MessageQueue()
        self.load_tracker = LoadTracker()  # Built into messaging system
        self.notification_service = NotificationService()
        self.token_counter = TokenCounter()
    
    def send_message(self, from_agent: str, to_agent: str, message: Message):
        """Send message with built-in load tracking"""
        # Count tokens in message
        token_count = self.token_counter.count_tokens(message.content)
        
        # Track message in real-time
        self.load_tracker.track_message(
            to_agent=to_agent,
            message=message,
            token_count=token_count,
            timestamp=datetime.now()
        )
        
        # Check load thresholds (built into message flow)
        load_status = self.load_tracker.check_load(to_agent)
        
        if load_status.overload:
            # Automatically notify scheduler/manager
            self.notify_overload(to_agent, load_status)
        
        # Send message
        self.message_queue.enqueue(to_agent, message)
        
        return message.id
    
    def receive_message(self, agent_name: str) -> Message:
        """Receive message (load already tracked)"""
        return self.message_queue.dequeue(agent_name)
```

---

### **2. Real-Time Load Tracker (Built Into Messaging)**

**Real-Time Tracking:**
- Track messages per minute as they flow through
- Track token input per minute as messages are sent
- Track response backlog in real-time
- Automatically detect thresholds in message flow

**Load Tracker:**
```python
class LoadTracker:
    """Real-time load tracking built into messaging system"""
    
    def __init__(self):
        self.message_counts = defaultdict(lambda: deque(maxlen=60))  # Last 60 seconds
        self.token_counts = defaultdict(lambda: deque(maxlen=60))  # Last 60 seconds
        self.response_backlogs = defaultdict(int)
        self.thresholds = {
            "nexus": LoadThreshold(
                max_messages_per_minute=10,
                max_tokens_per_minute=50000,
                max_response_backlog=8
            ),
            "atlas": LoadThreshold(
                max_messages_per_minute=8,
                max_tokens_per_minute=40000,
                max_response_backlog=6
            ),
            ...
        }
    
    def track_message(self, to_agent: str, message: Message, token_count: int, timestamp: datetime):
        """Track message in real-time as it flows through system"""
        # Track message count (sliding window - last 60 seconds)
        self.message_counts[to_agent].append({
            "timestamp": timestamp,
            "token_count": token_count
        })
        
        # Calculate messages per minute
        messages_per_minute = self.calculate_messages_per_minute(to_agent)
        
        # Calculate tokens per minute
        tokens_per_minute = self.calculate_tokens_per_minute(to_agent)
        
        # Update response backlog
        self.response_backlogs[to_agent] = self.get_response_backlog(to_agent)
        
        # Check thresholds (automatic, in real-time)
        return self.check_load(to_agent, messages_per_minute, tokens_per_minute)
    
    def calculate_messages_per_minute(self, agent_name: str) -> int:
        """Calculate messages per minute from sliding window"""
        now = datetime.now()
        one_minute_ago = now - timedelta(seconds=60)
        
        # Count messages in last 60 seconds
        recent_messages = [
            msg for msg in self.message_counts[agent_name]
            if msg["timestamp"] > one_minute_ago
        ]
        
        return len(recent_messages)
    
    def calculate_tokens_per_minute(self, agent_name: str) -> int:
        """Calculate tokens per minute from sliding window"""
        now = datetime.now()
        one_minute_ago = now - timedelta(seconds=60)
        
        # Sum tokens in last 60 seconds
        recent_tokens = [
            msg["token_count"] for msg in self.message_counts[agent_name]
            if msg["timestamp"] > one_minute_ago
        ]
        
        return sum(recent_tokens)
    
    def check_load(self, agent_name: str, messages_per_minute: int = None, tokens_per_minute: int = None) -> LoadStatus:
        """Check load thresholds (automatic, in real-time)"""
        if messages_per_minute is None:
            messages_per_minute = self.calculate_messages_per_minute(agent_name)
        if tokens_per_minute is None:
            tokens_per_minute = self.calculate_tokens_per_minute(agent_name)
        
        threshold = self.thresholds[agent_name]
        response_backlog = self.response_backlogs[agent_name]
        
        # Check thresholds
        overload = (
            messages_per_minute > threshold.max_messages_per_minute or
            tokens_per_minute > threshold.max_tokens_per_minute or
            response_backlog > threshold.max_response_backlog
        )
        
        if overload:
            return LoadStatus(
                agent_name=agent_name,
                overload=True,
                messages_per_minute=messages_per_minute,
                tokens_per_minute=tokens_per_minute,
                response_backlog=response_backlog,
                threshold=threshold,
                recommendation=self.recommend_action(agent_name, messages_per_minute, tokens_per_minute, response_backlog)
            )
        else:
            return LoadStatus(
                agent_name=agent_name,
                overload=False,
                messages_per_minute=messages_per_minute,
                tokens_per_minute=tokens_per_minute,
                response_backlog=response_backlog
            )
    
    def recommend_action(self, agent_name: str, messages_per_minute: int, tokens_per_minute: int, response_backlog: int) -> str:
        """Recommend action based on load type"""
        threshold = self.thresholds[agent_name]
        
        if messages_per_minute > threshold.max_messages_per_minute:
            return "create_communication_coordinator_assistant"
        elif tokens_per_minute > threshold.max_tokens_per_minute:
            return "create_processing_assistant"
        elif response_backlog > threshold.max_response_backlog:
            return "create_response_coordinator_assistant"
        else:
            return "continue"
```

---

### **3. Automatic Notification (Built Into Message Flow)**

**Automatic Notifications:**
- When message is sent and load detected, automatically notify
- Notify scheduler to adjust sequence
- Notify manager to create assistant
- No polling, no checks - automatic in message flow

**Notification in Message Flow:**
```python
class MessagingSystem:
    """Messaging system with automatic notifications"""
    
    def send_message(self, from_agent: str, to_agent: str, message: Message):
        """Send message with automatic load detection and notification"""
        # Track message (built into flow)
        load_status = self.load_tracker.track_message(to_agent, message, ...)
        
        # If overload detected, automatically notify
        if load_status.overload:
            # Automatically notify scheduler
            self.notification_service.notify_scheduler(
                agent_name=to_agent,
                notification_type="load_detected",
                load_status=load_status,
                message=f"Agent {to_agent} load exceeded: {load_status.messages_per_minute} msgs/min, {load_status.tokens_per_minute} tokens/min"
            )
            
            # Automatically notify manager
            self.notification_service.notify_manager(
                agent_name=to_agent,
                notification_type="load_detected",
                load_status=load_status,
                recommendation=load_status.recommendation,
                message=f"Agent {to_agent} overload detected - recommend {load_status.recommendation}"
            )
        
        # Send message (normal flow continues)
        return self.message_queue.enqueue(to_agent, message)
```

---

### **4. Token Counter (Built Into Message Flow)**

**Token Counting:**
- Count tokens as messages are sent
- Track token input per minute
- Automatic, no agent action needed

**Token Counter:**
```python
class TokenCounter:
    """Count tokens in messages automatically"""
    
    def count_tokens(self, content: str) -> int:
        """Count tokens in message content"""
        # Use tokenizer (e.g., tiktoken, transformers)
        return self.tokenizer.encode(content).length
    
    def count_message_tokens(self, message: Message) -> int:
        """Count total tokens in message"""
        total = 0
        total += self.count_tokens(message.content)
        total += self.count_tokens(message.context or "")
        total += self.count_tokens(message.metadata or "")
        return total
```

---

### **5. Response Backlog Tracking (Built Into Message Flow)**

**Response Backlog:**
- Track pending responses as messages are sent
- Update backlog in real-time
- Automatically detect when backlog exceeds threshold

**Response Backlog Tracker:**
```python
class ResponseBacklogTracker:
    """Track response backlog in real-time"""
    
    def __init__(self):
        self.pending_responses = defaultdict(list)  # agent -> list of pending responses
    
    def track_pending_response(self, to_agent: str, message_id: str, from_agent: str):
        """Track pending response when message sent"""
        self.pending_responses[to_agent].append({
            "message_id": message_id,
            "from_agent": from_agent,
            "timestamp": datetime.now()
        })
    
    def mark_response_complete(self, to_agent: str, message_id: str):
        """Mark response complete when response received"""
        self.pending_responses[to_agent] = [
            resp for resp in self.pending_responses[to_agent]
            if resp["message_id"] != message_id
        ]
    
    def get_backlog(self, agent_name: str) -> int:
        """Get current response backlog"""
        return len(self.pending_responses[agent_name])
```

---

## 🔄 **INTEGRATED MESSAGE FLOW**

### **Complete Message Flow with Load Detection:**

```python
class IntegratedMessagingSystem:
    """Complete messaging system with built-in load detection"""
    
    def __init__(self):
        self.message_queue = MessageQueue()
        self.load_tracker = LoadTracker()
        self.token_counter = TokenCounter()
        self.response_tracker = ResponseBacklogTracker()
        self.notification_service = NotificationService()
    
    def send_message(self, from_agent: str, to_agent: str, message: Message) -> str:
        """Send message with integrated load detection"""
        # 1. Count tokens (automatic)
        token_count = self.token_counter.count_message_tokens(message)
        
        # 2. Track message in real-time (automatic)
        load_status = self.load_tracker.track_message(
            to_agent=to_agent,
            message=message,
            token_count=token_count,
            timestamp=datetime.now()
        )
        
        # 3. Track response backlog (automatic)
        self.response_tracker.track_pending_response(
            to_agent=to_agent,
            message_id=message.id,
            from_agent=from_agent
        )
        
        # 4. Check load (automatic, in message flow)
        if load_status.overload:
            # 5. Automatically notify (automatic, in message flow)
            self.notification_service.notify_scheduler(
                agent_name=to_agent,
                notification_type="load_detected",
                load_status=load_status
            )
            self.notification_service.notify_manager(
                agent_name=to_agent,
                notification_type="load_detected",
                load_status=load_status,
                recommendation=load_status.recommendation
            )
        
        # 6. Send message (normal flow)
        self.message_queue.enqueue(to_agent, message)
        
        return message.id
    
    def receive_message(self, agent_name: str) -> Message:
        """Receive message"""
        return self.message_queue.dequeue(agent_name)
    
    def send_response(self, from_agent: str, to_agent: str, message_id: str, response: Message):
        """Send response and update backlog"""
        # Send response
        self.send_message(from_agent, to_agent, response)
        
        # Mark response complete (update backlog)
        self.response_tracker.mark_response_complete(to_agent, message_id)
```

---

## 🎯 **WORKFLOW EXAMPLE**

**Scenario: Multiple agents send messages to Nexus**

1. **Message 1: Sev → Nexus**
   - System counts tokens: 5,000 tokens
   - System tracks: 1 message/min, 5,000 tokens/min
   - System checks: 1 < 10 (threshold), 5,000 < 50,000 (threshold) ✅
   - Message sent ✅

2. **Message 2: Alex → Nexus**
   - System counts tokens: 8,000 tokens
   - System tracks: 2 messages/min, 13,000 tokens/min
   - System checks: 2 < 10, 13,000 < 50,000 ✅
   - Message sent ✅

3. **Message 3: Nova → Nexus**
   - System counts tokens: 7,000 tokens
   - System tracks: 3 messages/min, 20,000 tokens/min
   - System checks: 3 < 10, 20,000 < 50,000 ✅
   - Message sent ✅

4. **Message 4: Chronos → Nexus**
   - System counts tokens: 6,000 tokens
   - System tracks: 4 messages/min, 26,000 tokens/min
   - System checks: 4 < 10, 26,000 < 50,000 ✅
   - Message sent ✅

5. **Message 5: Atlas → Nexus**
   - System counts tokens: 9,000 tokens
   - System tracks: 5 messages/min, 35,000 tokens/min
   - System checks: 5 < 10, 35,000 < 50,000 ✅
   - Message sent ✅

6. **Message 6: Sage → Nexus**
   - System counts tokens: 12,000 tokens
   - System tracks: 6 messages/min, 47,000 tokens/min
   - System checks: 6 < 10, 47,000 < 50,000 ✅
   - Message sent ✅

7. **Message 7: Another Agent → Nexus** (within same minute)
   - System counts tokens: 8,000 tokens
   - System tracks: 7 messages/min, 55,000 tokens/min
   - System checks: 7 < 10, **55,000 > 50,000** ⚠️ **THRESHOLD EXCEEDED**
   - **System automatically notifies:**
     - **Scheduler:** "Nexus token load exceeded: 55,000 tokens/min (threshold: 50,000)"
     - **Manager:** "Nexus overload detected - recommend creating processing assistant"
   - Message sent ✅ (flow continues, but notifications sent)

8. **Scheduler Response:**
   - Scheduler receives notification
   - Scheduler adjusts sequence: Reduces messages to Nexus temporarily
   - Scheduler prioritizes other agents

9. **Manager Response:**
   - Manager receives notification
   - Manager creates `nexus_assistant_processing` agent
   - Assistant handles high-token messages

10. **System Continues:**
    - Messages continue flowing
    - Load tracking continues automatically
    - System detects load reduction
    - System confirms normalization

---

## 📊 **LOAD THRESHOLDS**

### **Threshold Configuration:**

```python
LOAD_THRESHOLDS = {
    "nexus": LoadThreshold(
        max_messages_per_minute=10,      # 10 messages per minute
        max_tokens_per_minute=50000,      # 50,000 tokens per minute
        max_response_backlog=8            # 8 pending responses
    ),
    "atlas": LoadThreshold(
        max_messages_per_minute=8,
        max_tokens_per_minute=40000,
        max_response_backlog=6
    ),
    "sev": LoadThreshold(
        max_messages_per_minute=6,
        max_tokens_per_minute=30000,
        max_response_backlog=5
    ),
    ...
}
```

**Threshold Types:**
- **Messages Per Minute:** Number of messages received per minute
- **Tokens Per Minute:** Total token input per minute
- **Response Backlog:** Number of pending responses

---

## 🚀 **IMPLEMENTATION PRIORITIES**

### **Phase 1: Messaging System with Load Tracking**
1. Message queue with load tracking
2. Token counter (built into message flow)
3. Real-time metrics (messages/min, tokens/min)
4. Response backlog tracking

### **Phase 2: Automatic Detection & Notification**
1. Threshold checking (built into message flow)
2. Automatic notifications (scheduler, manager)
3. Load status calculation
4. Recommendation generation

### **Phase 3: Scheduler/Manager Integration**
1. Scheduler notification handling
2. Manager notification handling
3. Automatic sequence adjustment
4. Automatic assistant creation

---

**Status:** Architecture Design Complete ✅  
**Next:** Implement messaging system with built-in load detection  
**Confidence:** High (0.95) - Real automation, built into message flow

---

