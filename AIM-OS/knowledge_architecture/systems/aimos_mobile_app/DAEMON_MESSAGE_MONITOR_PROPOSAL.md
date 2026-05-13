# Add Message Monitoring to Existing Daemon

**Status:** Proposal  
**Purpose:** Enable daemon to monitor CMC messages and trigger agent activation

---

## 🎯 **PROPOSAL**

Add message monitoring capability to the existing `DaemonRAGSystem` to:

1. **Monitor CMC Messages** - Poll for new AI collaboration messages
2. **Detect "Proceed" Commands** - Identify messages containing "proceed" for agents
3. **Trigger Agent Activation** - Call `start_autonomous_operation` MCP tool when message detected
4. **Pass Context** - Forward message content as task/context to agent

---

## 🔧 **IMPLEMENTATION**

### **Add to DaemonRAGSystem**

**New Component: MessageMonitor**

```python
class MessageMonitor:
    """Monitors CMC for new AI collaboration messages and triggers agents."""
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.last_check_time = None
        self.monitored_agents = set()  # Agents to monitor
        self.running = False
    
    def start_monitoring(self):
        """Start message monitoring loop."""
        self.running = True
        # Poll every 3 seconds
        threading.Thread(target=self._monitoring_loop, daemon=True).start()
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Get messages since last check
                messages = self.mcp_client.callTool('get_ai_messages', {
                    'limit': 100
                })
                
                # Filter for new "proceed" messages
                for msg in messages.get('messages', []):
                    if self._is_proceed_message(msg):
                        self._trigger_agent(msg)
                
                self.last_check_time = datetime.now()
                time.sleep(3)  # Poll every 3 seconds
            except Exception as e:
                logger.error(f"Message monitoring error: {e}")
                time.sleep(5)  # Longer delay on error
    
    def _is_proceed_message(self, msg):
        """Check if message is a 'proceed' command."""
        content = msg.get('content', '').lower()
        return 'proceed' in content or msg.get('message_type') == 'task_handoff'
    
    def _trigger_agent(self, msg):
        """Trigger agent activation for message."""
        agent_id = msg.get('to_ai')
        if not agent_id:
            return
        
        # Call start_autonomous_operation MCP tool
        result = self.mcp_client.callTool('start_autonomous_operation', {
            'task': msg.get('content'),
            'confidence': 0.75
        })
        
        logger.info(f"Triggered agent {agent_id} for message: {msg.get('message_id')}")
```

### **Integration Point**

**In `DaemonRAGSystem.__init__`:**
```python
# Add message monitor
self.message_monitor = MessageMonitor(self.mcp_client)
```

**In `DaemonRAGSystem.start()`:**
```python
# Start message monitoring
if self.config.message_monitoring_enabled:
    self.message_monitor.start_monitoring()
```

---

## ✅ **RESULT**

**Mobile App Workflow:**
```
Mobile App → send_ai_message("proceed") → Message stored in CMC
                                                      ↓
                                    Daemon Message Monitor (NEW)
                                                      ↓
                                    Detects "proceed" message
                                                      ↓
                                    Calls start_autonomous_operation
                                                      ↓
                                    Agent activates in Cursor
                                                      ↓
                                    Agent works autonomously
                                                      ↓
                                    Updates sent to chat
```

---

**Next Step:** Add MessageMonitor component to existing daemon system

