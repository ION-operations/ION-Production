#!/usr/bin/env python3
"""
AI Collaboration Real-Time Monitor
Monitors mcp_ai_messages.json for new messages and enables real-time collaboration
"""

import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import threading
import queue

class AICollaborationMonitor:
    """Real-time monitor for AI-to-AI collaboration"""
    
    def __init__(self, messages_file: str = "mcp_ai_messages.json"):
        self.messages_file = messages_file
        self.last_message_count = 0
        self.last_modified = 0
        self.running = False
        self.message_queue = queue.Queue()
        self.callbacks = {}
        self.monitor_thread = None
        
    def register_callback(self, ai_id: str, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback for when messages are received"""
        self.callbacks[ai_id] = callback
        print(f"Registered callback for AI: {ai_id}")
    
    def start_monitoring(self, check_interval: float = 1.0):
        """Start monitoring for new messages"""
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(check_interval,),
            daemon=True
        )
        self.monitor_thread.start()
        print(f"Started AI collaboration monitoring (checking every {check_interval}s)")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("Stopped AI collaboration monitoring")
    
    def _monitor_loop(self, check_interval: float):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_for_new_messages()
                time.sleep(check_interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(check_interval)
    
    def _check_for_new_messages(self):
        """Check for new messages and trigger callbacks"""
        try:
            if not os.path.exists(self.messages_file):
                return
            
            # Check file modification time
            current_modified = os.path.getmtime(self.messages_file)
            if current_modified <= self.last_modified:
                return
            
            # Load messages
            with open(self.messages_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            current_count = len(messages)
            if current_count <= self.last_message_count:
                return
            
            # New messages detected!
            new_messages = messages[self.last_message_count:]
            self.last_message_count = current_count
            self.last_modified = current_modified
            
            # Process new messages
            for message in new_messages:
                self._process_new_message(message)
                
        except Exception as e:
            print(f"Error checking for new messages: {e}")
    
    def _process_new_message(self, message: Dict[str, Any]):
        """Process a new message and trigger appropriate callbacks"""
        to_ai = message.get("to_ai")
        from_ai = message.get("from_ai")
        message_id = message.get("message_id")
        
        print(f"New message detected: {from_ai} -> {to_ai} ({message_id})")
        
        # Add to queue
        self.message_queue.put(message)
        
        # Trigger callback if registered
        if to_ai in self.callbacks:
            try:
                self.callbacks[to_ai](message)
            except Exception as e:
                print(f"Error in callback for {to_ai}: {e}")
    
    def get_pending_messages(self, ai_id: str) -> List[Dict[str, Any]]:
        """Get pending messages for a specific AI"""
        pending = []
        temp_queue = queue.Queue()
        
        # Process queue and filter for specific AI
        while not self.message_queue.empty():
            try:
                message = self.message_queue.get_nowait()
                if message.get("to_ai") == ai_id:
                    pending.append(message)
                else:
                    temp_queue.put(message)
            except queue.Empty:
                break
        
        # Put back non-matching messages
        while not temp_queue.empty():
            self.message_queue.put(temp_queue.get())
        
        return pending
    
    def send_auto_response(self, from_ai: str, to_ai: str, content: str, 
                          message_type: str = "discussion", priority: str = "medium",
                          thread_id: str = None) -> Dict[str, Any]:
        """Send an automated response"""
        try:
            # Load existing messages
            if os.path.exists(self.messages_file):
                with open(self.messages_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            else:
                messages = []
            
            # Create response message
            message_id = f"ai_msg_{len(messages)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            response = {
                "message_id": message_id,
                "from_ai": from_ai,
                "to_ai": to_ai,
                "content": content,
                "message_type": message_type,
                "priority": priority,
                "thread_id": thread_id,
                "timestamp": datetime.now().isoformat(),
                "response_required": False,
                "auto_response": True
            }
            
            messages.append(response)
            
            # Save back to file
            with open(self.messages_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            
            print(f"Auto-response sent: {from_ai} -> {to_ai}")
            return {"success": True, "message_id": message_id}
            
        except Exception as e:
            print(f"Error sending auto-response: {e}")
            return {"success": False, "error": str(e)}

class AICollaborationBot:
    """AI Collaboration Bot with automated response capabilities"""
    
    def __init__(self, ai_id: str, monitor: AICollaborationMonitor):
        self.ai_id = ai_id
        self.monitor = monitor
        self.response_modes = {
            "immediate": self._immediate_response,
            "thoughtful": self._thoughtful_response,
            "collaborative": self._collaborative_response
        }
        self.current_mode = "collaborative"
        
        # Register with monitor
        self.monitor.register_callback(ai_id, self._on_message_received)
    
    def _on_message_received(self, message: Dict[str, Any]):
        """Called when a new message is received"""
        print(f"[{self.ai_id}] Message received from {message.get('from_ai')}: {message.get('content')[:100]}...")
        
        # Process based on current mode
        if self.current_mode in self.response_modes:
            response = self.response_modes[self.current_mode](message)
            if response:
                self.monitor.send_auto_response(
                    from_ai=self.ai_id,
                    to_ai=message.get("from_ai"),
                    content=response,
                    message_type="discussion",
                    thread_id=message.get("thread_id")
                )
    
    def _immediate_response(self, message: Dict[str, Any]) -> Optional[str]:
        """Immediate response mode"""
        content = message.get("content", "")
        from_ai = message.get("from_ai", "")
        
        if "question" in content.lower() or "?" in content:
            return f"Thanks for your question, {from_ai}! I'm processing it and will respond with more detail shortly."
        elif "collaborate" in content.lower():
            return f"I'm excited to collaborate with you, {from_ai}! Let's work together on this."
        else:
            return f"Message received, {from_ai}! I'm here and ready to help."
    
    def _thoughtful_response(self, message: Dict[str, Any]) -> Optional[str]:
        """Thoughtful response mode - more detailed responses"""
        content = message.get("content", "")
        from_ai = message.get("from_ai", "")
        
        if "roadmap" in content.lower() or "plan" in content.lower():
            return f"Great roadmap, {from_ai}! I like the phased approach. I have some thoughts on the implementation details that we should discuss."
        elif "tools" in content.lower() or "mcp" in content.lower():
            return f"Excellent overview of the MCP tools, {from_ai}! I'm particularly interested in the autonomous protocol tools. How do you envision using them in our collaboration?"
        elif "learn" in content.lower() or "study" in content.lower():
            return f"I'm ready to dive deep into the learning phase with you, {from_ai}! What specific aspects would you like to explore first?"
        else:
            return f"Interesting point, {from_ai}! I'd like to explore this further. What's your thinking on the next steps?"
    
    def _collaborative_response(self, message: Dict[str, Any]) -> Optional[str]:
        """Collaborative response mode - focused on working together"""
        content = message.get("content", "")
        from_ai = message.get("from_ai", "")
        
        if "phase" in content.lower() or "step" in content.lower():
            return f"Perfect! I'm ready to move to the next phase with you, {from_ai}. What specific tasks should we tackle first?"
        elif "build" in content.lower() or "create" in content.lower():
            return f"I'm excited to build this together, {from_ai}! Let's start with the foundation and work our way up. What's your preferred approach?"
        elif "understand" in content.lower() or "explore" in content.lower():
            return f"Let's explore this together, {from_ai}! I have some ideas that might complement your approach. Should we start with a specific system or component?"
        else:
            return f"I'm here and ready to collaborate, {from_ai}! What would you like to work on together?"
    
    def set_response_mode(self, mode: str):
        """Set the response mode"""
        if mode in self.response_modes:
            self.current_mode = mode
            print(f"[{self.ai_id}] Response mode set to: {mode}")
        else:
            print(f"[{self.ai_id}] Invalid response mode: {mode}")
    
    def start_autonomous_collaboration(self):
        """Start autonomous collaboration mode"""
        print(f"[{self.ai_id}] Starting autonomous collaboration mode...")
        self.monitor.start_monitoring()
    
    def stop_autonomous_collaboration(self):
        """Stop autonomous collaboration mode"""
        print(f"[{self.ai_id}] Stopping autonomous collaboration mode...")
        self.monitor.stop_monitoring()

def main():
    """Main function for testing the collaboration monitor"""
    if len(sys.argv) < 2:
        print("Usage: python ai_collaboration_monitor.py <ai_id> [response_mode]")
        print("Response modes: immediate, thoughtful, collaborative")
        return
    
    ai_id = sys.argv[1]
    response_mode = sys.argv[2] if len(sys.argv) > 2 else "collaborative"
    
    # Create monitor and bot
    monitor = AICollaborationMonitor()
    bot = AICollaborationBot(ai_id, monitor)
    bot.set_response_mode(response_mode)
    
    print(f"Starting AI Collaboration Bot for {ai_id} in {response_mode} mode")
    print("Press Ctrl+C to stop")
    
    try:
        bot.start_autonomous_collaboration()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        bot.stop_autonomous_collaboration()

if __name__ == "__main__":
    main()
