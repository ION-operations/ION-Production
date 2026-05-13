# System-Level Automatic Load Detection

**Purpose:** Design system-level automatic load detection that monitors agents and notifies managers/schedulers  
**Date:** 2025-01-27  
**Status:** ARCHITECTURE_DESIGN (SUPERSEDED - See MESSAGING_SYSTEM_LOAD_DETECTION.md)  
**Author:** Aether (from Braden's insight)  
**Related Systems:** Agent Orchestration, Load Monitoring, Automatic Detection

---

## ⚠️ **SUPERSEDED**

**This document is superseded by:** `MESSAGING_SYSTEM_LOAD_DETECTION.md`

**Reason:** Load detection should be built into the messaging system itself, not a separate monitoring service. See the messaging system architecture for the correct implementation.

---

## 🎯 **BRADEN'S CRITICAL INSIGHT**

**Braden's Statement:**
> "but also we shouldn't make the agent define load, the system should automatically detect it too and notify the agent or manager/scheduler."

**Updated Insight:**
> "it shouldn't even be monitoring for messages to nexus etc.. it should be built into the messaging system. there should be some way that if there are too many messages and too much tokens input from them per minute or something then it notifies scheduler/manager etc. real processes not check and balances but automation in sync."

**Core Principle:**
- **Built-In Detection (Primary):** Load detection is built into the messaging system itself
- **Real-Time Tracking:** Track message count and token input per minute as messages flow through
- **Automatic Notifications:** Automatically notify scheduler/manager when thresholds exceeded
- **Real Automation:** Real processes, not checks and balances - automation in sync with message flow

---

## 🧠 **THE ARCHITECTURE**

### **1. System-Level Monitoring Service**

**Continuous Automatic Monitoring:**
- System monitors all agents continuously (every 5 seconds)
- System collects metrics automatically (no agent action needed)
- System detects issues automatically (threshold-based)
- System notifies agents and managers when issues detected

**Monitoring Service:**
```python
class SystemLoadMonitor:
    """System-level automatic load monitoring service"""
    
    def __init__(self):
        self.monitoring_active = True
        self.monitoring_interval = 5  # seconds
        self.notification_service = NotificationService()
        self.metrics_collector = MetricsCollector()
        self.detector = LoadComplexityDetector()
    
    def start_monitoring(self):
        """Start continuous system-level monitoring"""
        while self.monitoring_active:
            # Monitor all agents
            for agent_name in self.get_all_agents():
                # Collect metrics automatically
                metrics = self.metrics_collector.collect(agent_name)
                
                # Detect issues automatically
                diagnosis = self.detector.detect(agent_name, metrics)
                
                # Notify if issues detected
                if diagnosis.action != "continue":
                    self.notify_load_detected(agent_name, diagnosis)
            
            time.sleep(self.monitoring_interval)
    
    def collect_metrics(self, agent_name: str) -> AgentMetrics:
        """Automatically collect metrics for agent"""
        return AgentMetrics(
            # Task metrics
            task_count=self.get_task_count(agent_name),
            execution_time=self.get_execution_time(agent_name),
            queue_length=self.get_queue_length(agent_name),
            
            # Communication metrics
            concurrent_communications=self.get_concurrent_communications(agent_name),
            coordination_requests=self.get_coordination_requests(agent_name),
            response_backlog=self.get_response_backlog(agent_name),
            
            # Complexity metrics
            task_complexity=self.get_task_complexity(agent_name),
            coordination_count=self.get_coordination_count(agent_name),
            
            # Performance metrics
            response_time=self.get_response_time(agent_name),
            error_rate=self.get_error_rate(agent_name),
            completion_rate=self.get_completion_rate(agent_name)
        )
    
    def detect_issues(self, agent_name: str, metrics: AgentMetrics) -> Diagnosis:
        """System automatically detects issues"""
        detector = LoadComplexityDetector()
        return detector.diagnose(agent_name, metrics)
    
    def notify_load_detected(self, agent_name: str, diagnosis: Diagnosis):
        """System notifies agent and manager when load detected"""
        # Notify agent
        self.notification_service.notify_agent(
            agent_name=agent_name,
            notification_type="load_detected",
            diagnosis=diagnosis,
            message=f"System detected {diagnosis.overload_type} - {diagnosis.recommendation}"
        )
        
        # Notify manager
        self.notification_service.notify_manager(
            agent_name=agent_name,
            notification_type="load_detected",
            diagnosis=diagnosis,
            recommendation=diagnosis.recommendation,
            message=f"Agent {agent_name} overload detected - recommend {diagnosis.recommendation}"
        )
        
        # Notify scheduler
        self.notification_service.notify_scheduler(
            agent_name=agent_name,
            notification_type="load_detected",
            diagnosis=diagnosis,
            recommendation="adjust_sequence",
            message=f"Agent {agent_name} load high - adjust execution sequence"
        )
```

---

### **2. Metrics Collection (Automatic)**

**Automatic Metrics Collection:**
- System collects metrics without agent involvement
- Metrics collected from: execution queue, communication logs, performance monitors
- Real-time collection every 5 seconds
- Historical tracking for trend analysis

**Metrics Collector:**
```python
class MetricsCollector:
    """Automatically collects metrics for all agents"""
    
    def collect(self, agent_name: str) -> AgentMetrics:
        """Collect all metrics for agent automatically"""
        return AgentMetrics(
            # Task metrics (from execution queue)
            task_count=self.get_task_count(agent_name),
            execution_time=self.get_average_execution_time(agent_name),
            queue_length=self.get_queue_length(agent_name),
            
            # Communication metrics (from communication logs)
            concurrent_communications=self.get_concurrent_communications(agent_name),
            coordination_requests=self.get_coordination_requests(agent_name),
            response_backlog=self.get_response_backlog(agent_name),
            
            # Complexity metrics (from task analysis)
            task_complexity=self.calculate_task_complexity(agent_name),
            coordination_count=self.get_coordination_count(agent_name),
            
            # Performance metrics (from performance monitors)
            response_time=self.get_average_response_time(agent_name),
            error_rate=self.get_error_rate(agent_name),
            completion_rate=self.get_completion_rate(agent_name)
        )
    
    def get_concurrent_communications(self, agent_name: str) -> int:
        """Get number of concurrent communications"""
        # Query communication logs
        active_comms = self.communication_log.get_active_communications(agent_name)
        return len(active_comms)
    
    def get_coordination_requests(self, agent_name: str) -> int:
        """Get number of coordination requests"""
        # Query coordination board
        requests = self.coordination_board.get_pending_requests(agent_name)
        return len(requests)
    
    def get_response_backlog(self, agent_name: str) -> int:
        """Get response backlog"""
        # Query response queue
        backlog = self.response_queue.get_backlog(agent_name)
        return len(backlog)
```

---

### **3. Automatic Detection (Threshold-Based)**

**Automatic Detection:**
- System compares metrics to thresholds automatically
- No agent action required
- Objective, consistent detection
- Prevents agents from being too busy to self-diagnose

**Detection Logic:**
```python
class LoadComplexityDetector:
    """Automatically detects load and complexity issues"""
    
    def detect(self, agent_name: str, metrics: AgentMetrics) -> Diagnosis:
        """System automatically detects issues"""
        threshold = self.load_thresholds[agent_name]
        
        # Check load metrics
        overload = (
            metrics.task_count > threshold.max_tasks or
            metrics.execution_time > threshold.max_time or
            metrics.queue_length > threshold.max_queue or
            metrics.concurrent_communications > threshold.max_concurrent_communications or
            metrics.coordination_requests > threshold.max_coordination_requests or
            metrics.response_backlog > threshold.max_response_backlog
        )
        
        # Check complexity metrics
        complexity = (
            metrics.task_complexity > threshold.max_complexity or
            metrics.coordination_count > threshold.max_coordination
        )
        
        # Diagnose
        if overload and complexity:
            return Diagnosis(
                action="create_team",
                overload_type="load_and_complexity",
                recommendation="Create assistant agents and distribute work"
            )
        elif overload:
            return Diagnosis(
                action="create_assistant",
                overload_type="load",
                recommendation="Create assistant agent to share workload"
            )
        elif complexity:
            return Diagnosis(
                action="create_specialist",
                overload_type="complexity",
                recommendation="Create specialist agent for complex subsystem"
            )
        else:
            return Diagnosis(
                action="continue",
                overload_type="none",
                recommendation="Continue current operation"
            )
```

---

### **4. Notification System**

**Automatic Notifications:**
- System notifies agents when load detected
- System notifies managers when load detected
- System notifies schedulers when load detected
- Notifications include: metrics, diagnosis, recommendation

**Notification Service:**
```python
class NotificationService:
    """Sends automatic notifications to agents, managers, schedulers"""
    
    def notify_agent(self, agent_name: str, notification_type: str, diagnosis: Diagnosis, message: str):
        """Notify agent of load detection"""
        notification = Notification(
            recipient=agent_name,
            type=notification_type,
            message=message,
            diagnosis=diagnosis,
            timestamp=datetime.now()
        )
        
        # Send to agent coordination board
        self.coordination_board.post_notification(notification)
        
        # Send to agent's notification queue
        self.agent_queues[agent_name].enqueue(notification)
    
    def notify_manager(self, agent_name: str, notification_type: str, diagnosis: Diagnosis, recommendation: str, message: str):
        """Notify manager of load detection"""
        notification = Notification(
            recipient="manager",
            type=notification_type,
            agent_name=agent_name,
            message=message,
            diagnosis=diagnosis,
            recommendation=recommendation,
            timestamp=datetime.now()
        )
        
        # Send to manager notification queue
        self.manager_queue.enqueue(notification)
        
        # Send to manager dashboard
        self.manager_dashboard.add_alert(notification)
    
    def notify_scheduler(self, agent_name: str, notification_type: str, diagnosis: Diagnosis, recommendation: str, message: str):
        """Notify scheduler of load detection"""
        notification = Notification(
            recipient="scheduler",
            type=notification_type,
            agent_name=agent_name,
            message=message,
            diagnosis=diagnosis,
            recommendation=recommendation,
            timestamp=datetime.now()
        )
        
        # Send to scheduler
        self.scheduler.receive_notification(notification)
        
        # Adjust sequence if needed
        if recommendation == "adjust_sequence":
            self.scheduler.adjust_sequence_for_agent(agent_name)
```

---

### **5. Manager/Scheduler Response**

**Manager Receives Notification:**
- Manager receives automatic notification from system
- Manager reviews metrics and diagnosis
- Manager confirms or adjusts recommendation
- Manager takes action (create assistant, adjust sequence, etc.)

**Scheduler Receives Notification:**
- Scheduler receives automatic notification from system
- Scheduler adjusts execution sequence to reduce load
- Scheduler prioritizes other agents if one is overloaded
- Scheduler balances load across agents

**Manager Response:**
```python
class Manager:
    """Manager receives system notifications and takes action"""
    
    def receive_notification(self, notification: Notification):
        """Manager receives notification from system"""
        # Review notification
        if notification.type == "load_detected":
            # Review metrics and diagnosis
            self.review_load_detection(notification)
            
            # Confirm or adjust recommendation
            if self.confirm_diagnosis(notification):
                # Take action
                self.execute_recommendation(notification.recommendation)
    
    def review_load_detection(self, notification: Notification):
        """Review system's load detection"""
        # Check metrics
        metrics = notification.diagnosis.metrics
        
        # Validate diagnosis
        if self.validate_diagnosis(metrics, notification.diagnosis):
            # Confirm diagnosis
            return True
        else:
            # Adjust diagnosis
            return False
    
    def execute_recommendation(self, recommendation: str):
        """Execute recommendation from system"""
        if recommendation == "create_assistant":
            self.agent_creator.create_assistant(...)
        elif recommendation == "create_specialist":
            self.agent_creator.create_specialist(...)
        elif recommendation == "create_team":
            self.agent_creator.create_team(...)
```

---

## 🎯 **WORKFLOW EXAMPLE**

**Scenario: System detects Nexus communication load**

1. **System Automatic Monitoring:**
   - System monitors Nexus every 5 seconds
   - System collects metrics: 6 concurrent communications, 6 coordination requests
   - System compares to thresholds: 6 > 4 (concurrent), 6 = 6 (coordination)

2. **System Automatic Detection:**
   - System detects: Concurrent communications exceeded
   - System diagnoses: "High communication load"
   - System recommends: "Create communication coordinator assistant"

3. **System Automatic Notifications:**
   - **To Nexus:** "System detected high communication load (6 concurrent, threshold: 4)"
   - **To Manager:** "Nexus overload detected - recommend creating communication coordinator assistant"
   - **To Scheduler:** "Nexus load high - adjust execution sequence to reduce communication pressure"

4. **Manager Response:**
   - Manager receives notification
   - Manager reviews metrics and diagnosis
   - Manager confirms: "System diagnosis accurate"
   - Manager creates `nexus_assistant_coordination` agent

5. **Scheduler Response:**
   - Scheduler receives notification
   - Scheduler adjusts sequence: Reduces Nexus's communication load
   - Scheduler prioritizes other agents temporarily

6. **System Continues Monitoring:**
   - System continues monitoring Nexus and assistant
   - System detects load reduction
   - System confirms: "Load normalized"

---

## 📊 **BENEFITS OF SYSTEM-LEVEL DETECTION**

**Advantages:**
1. **Objective:** System detection is more objective than agent self-diagnosis
2. **Reliable:** System always monitors, even when agents are busy
3. **Consistent:** Same detection logic for all agents
4. **Proactive:** Can detect issues before they become critical
5. **No Agent Overhead:** Agents don't need to spend resources on self-diagnosis

**Comparison:**
- **Agent Self-Diagnosis:** Agent must detect its own load (may be too busy)
- **System Detection:** System automatically detects (always monitoring)

**Best Practice:**
- **Primary:** System-level automatic detection
- **Secondary:** Agent self-diagnosis (optional, supplementary)

---

## 🚀 **IMPLEMENTATION PRIORITIES**

### **Phase 1: System Monitoring Service**
1. Continuous monitoring loop (every 5 seconds)
2. Metrics collection (automatic)
3. Issue detection (threshold-based)
4. Notification system

### **Phase 2: Notification Integration**
1. Agent notifications
2. Manager notifications
3. Scheduler notifications
4. Notification queues

### **Phase 3: Manager/Scheduler Response**
1. Manager notification handling
2. Scheduler sequence adjustment
3. Automatic action execution
4. Monitoring and validation

---

**Status:** Architecture Design Complete ✅  
**Next:** Implement system-level monitoring service  
**Confidence:** High (0.95) - Clear architecture, automatic detection pattern

---

