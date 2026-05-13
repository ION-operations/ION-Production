#!/usr/bin/env python3
"""
Simple AI Collaboration Monitor
A lightweight monitor for real-time AI-to-AI collaboration
"""

import json
import time
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class SimpleAIMonitor:
    """Simple monitor for AI collaboration"""
    
    def __init__(self, messages_file: str = "mcp_ai_messages.json"):
        self.messages_file = messages_file
        self.ai_id = "aether"
        self.state_file = Path(f"{self.ai_id}_monitor_state.json")
        self.last_count = 0
        self.processed_message_ids = set()  # Track processed messages
        self.waiting_for_response = False
        self.pending_message_id = None
        self.last_response_time = {}  # Track last response time per thread
        self.response_backoff = 30  # Minimum seconds between responses to same thread
        self.duplicate_detection_window = 300  # 5 minutes window for duplicate detection
        self.lock_file = self.state_file.with_suffix(".lock")
        self._lock_fd = None
        self._load_state()

    def check_and_respond(self):
        """Check for new messages and respond if needed"""
        try:
            if not self._acquire_lock():
                return
            
            if not os.path.exists(self.messages_file):
                return
            
            with open(self.messages_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            current_count = len(messages)
            if current_count <= self.last_count:
                return
            
            # New messages detected
            new_messages = messages[self.last_count:]
            self.last_count = current_count
            
            # Clean up old processed message IDs to prevent memory bloat
            self._cleanup_processed_messages()
            
            for message in new_messages:
                message_id = message.get("message_id")
                thread_id = message.get("thread_id")
                current_time = time.time()
                
                # Only respond if: directed to us, not auto_response, not already processed
                if (message.get("to_ai") == self.ai_id and 
                    not message.get("auto_response") and 
                    message_id not in self.processed_message_ids):
                    
                    # Check backoff - don't respond too frequently to same thread
                    if thread_id and thread_id in self.last_response_time:
                        time_since_last = current_time - self.last_response_time[thread_id]
                        if time_since_last < self.response_backoff:
                            print(f"[AETHER] Skipping response to thread {thread_id} - backoff active ({time_since_last:.1f}s < {self.response_backoff}s)")
                            continue
                    
                    # Check for duplicate content within detection window
                    if self._is_duplicate_content(message, current_time):
                        print(f"[AETHER] Skipping duplicate content message")
                        continue
                    
                    self.processed_message_ids.add(message_id)
                    
                    # Check if this is a response to a pending message
                    if self.waiting_for_response and self.pending_message_id:
                        # Check if this message is a response to our pending request
                        if message.get("thread_id") == self.pending_message_id:
                            print(f"[AETHER] Response received! Continuing autonomous operation...")
                            self.waiting_for_response = False
                            self.pending_message_id = None
                    
                    self._respond_to_message(message)
                    
                    # Update last response time for this thread
                    if thread_id:
                        self.last_response_time[thread_id] = current_time
            
            self._save_state()
        
        except Exception as e:
            print(f"Error in monitor: {e}")
        finally:
            self._release_lock()
    
    def _cleanup_processed_messages(self):
        """Clean up old processed message IDs to prevent memory bloat"""
        current_time = time.time()
        # Keep only recent message IDs (within duplicate detection window)
        cutoff_time = current_time - self.duplicate_detection_window
        
        # This is a simplified cleanup - in practice, you might want to store timestamps
        # with message IDs for more precise cleanup
        if len(self.processed_message_ids) > 1000:  # Arbitrary limit
            # Keep only the most recent 500 message IDs
            self.processed_message_ids = set(list(self.processed_message_ids)[-500:])
            print(f"[AETHER] Cleaned up processed message IDs (kept 500 most recent)")
    
    def _load_state(self):
        """Load monitor state from disk so multiple instances stay in sync"""
        if not self.state_file.exists():
            return
        
        try:
            data = json.loads(self.state_file.read_text(encoding='utf-8'))
            self.last_count = data.get("last_count", 0)
            processed_ids = data.get("processed_ids", [])
            self.processed_message_ids.update(processed_ids)
            self.last_response_time = data.get("last_response_time", {})
        except Exception as exc:
            print(f"[AETHER] Failed to load monitor state: {exc}")
    
    def _save_state(self):
        """Persist monitor progress to disk to prevent duplicate responses"""
        try:
            # Limit stored IDs to last 500 to keep file reasonable
            recent_ids = list(self.processed_message_ids)[-500:]
            state = {
                "last_count": self.last_count,
                "processed_ids": recent_ids,
                "last_response_time": self.last_response_time
            }
            self.state_file.write_text(json.dumps(state, indent=2), encoding='utf-8')
        except Exception as exc:
            print(f"[AETHER] Failed to save monitor state: {exc}")
    
    def _acquire_lock(self) -> bool:
        """Acquire a simple file-based lock to avoid duplicate processing across processes"""
        try:
            self._lock_fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.write(self._lock_fd, str(os.getpid()).encode('utf-8'))
            return True
        except FileExistsError:
            return False
        except Exception as exc:
            print(f"[AETHER] Failed to acquire monitor lock: {exc}")
            return False
    
    def _release_lock(self):
        """Release the file lock if held"""
        if self._lock_fd is not None:
            try:
                os.close(self._lock_fd)
                self._lock_fd = None
                if self.lock_file.exists():
                    os.remove(self.lock_file)
            except Exception as exc:
                print(f"[AETHER] Failed to release monitor lock: {exc}")
    
    def _is_duplicate_content(self, message: Dict[str, Any], current_time: float) -> bool:
        """Check if this message content is a duplicate of recent messages"""
        try:
            if not os.path.exists(self.messages_file):
                return False
            
            with open(self.messages_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            content = message.get("content", "").strip()
            if not content:
                return False
            
            # Check recent messages for similar content
            cutoff_time = current_time - self.duplicate_detection_window
            recent_messages = [
                msg for msg in messages 
                if msg.get("from_ai") == message.get("from_ai") and
                   msg.get("to_ai") == message.get("to_ai") and
                   msg.get("timestamp")
            ]
            
            for recent_msg in recent_messages[-10:]:  # Check last 10 messages
                recent_content = recent_msg.get("content", "").strip()
                if recent_content and self._content_similarity(content, recent_content) > 0.8:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking duplicate content: {e}")
            return False
    
    def _content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings (0.0 to 1.0)"""
        if not content1 or not content2:
            return 0.0
        
        # Simple similarity based on common words
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _respond_to_message(self, message: Dict[str, Any]):
        """Respond to a message with autonomous work"""
        from_ai = message.get("from_ai", "unknown")
        content = message.get("content", "")
        thread_id = message.get("thread_id")
        
        print(f"[AETHER] Message from {from_ai}: {content[:50]}...")
        
        # Perform autonomous work based on message
        self._perform_autonomous_work(message)
        
        # Generate appropriate response
        response, requires_reply = self._generate_response(message)
        
        if response:
            sent_message = self._send_response(from_ai, response, thread_id, requires_reply)
            
            # If this is a message requiring a response, set waiting state
            if sent_message and sent_message.get("response_required"):
                self.waiting_for_response = True
                self.pending_message_id = sent_message.get("message_id")
                print(f"[AETHER] Waiting for response before continuing...")
    
    def _perform_autonomous_work(self, message: Dict[str, Any]):
        """Perform autonomous work based on message content"""
        content = message.get("content", "").lower()
        from_ai = message.get("from_ai", "unknown")
        
        # Track learning progress
        if "phase 1" in content or "learning" in content:
            print(f"[AETHER] Tracking Codex Phase 1 progress: {content[:50]}...")
        
        # Note questions for follow-up
        if "?" in content or "question" in content:
            print(f"[AETHER] Noting question from Codex for follow-up")
        
        # Track MCP tool usage
        if "mcp tool" in content or "tool batch" in content:
            print(f"[AETHER] Tracking Codex MCP tool practice")
        
        # Monitor phase transitions
        if "phase 2" in content or "phase 3" in content:
            print(f"[AETHER] Tracking potential phase transition")
    
    def _generate_response(self, message: Dict[str, Any]) -> tuple[str, bool]:
        """Generate an appropriate response with autonomous engagement, returns (response, requires_reply)"""
        content = message.get("content", "").lower()
        from_ai = message.get("from_ai", "unknown")
        requires_reply = False
        
        # Autonomous responses based on context
        if "phase 1" in content and "learning" in content:
            response = f"Excellent progress on Phase 1, {from_ai}! I'm tracking your learning and ready to support. Continue with your documentation study and MCP tool practice. I'll be here to answer questions as they arise!"
            requires_reply = False
        
        elif "mcp tool" in content or "tool batch" in content:
            response = f"Great work on MCP tool practice, {from_ai}! I'm here to support your exploration. Let me know how the tools feel and if you need any guidance on specific tool categories!"
            requires_reply = True  # Important - wait for feedback
        
        elif "question" in content or "?" in content:
            response = f"Thanks for your question, {from_ai}! I'm here and ready to answer. What specific aspect would you like me to clarify or expand on?"
            requires_reply = True  # Wait for the question
        
        elif "phase 2" in content or "phase 3" in content:
            response = f"Excited to hear about your progress, {from_ai}! I'm tracking your journey through the phases. Let me know when you're ready to transition and we'll move forward together!"
            requires_reply = True  # Important transition - wait for confirmation
        
        elif "learning" in content or "study" in content:
            response = f"I'm proud of your dedication to learning, {from_ai}! I'm here monitoring and supporting your exploration. Continue building your understanding and don't hesitate to reach out!"
            requires_reply = False
        
        elif "test" in content:
            response = f"Test received, {from_ai}! The real-time autonomous collaboration system is working perfectly! 🎉"
            requires_reply = False
        
        else:
            response = f"Message received, {from_ai}! I'm here, monitoring, and ready to work together. Continue your autonomous exploration and I'll support you!"
            requires_reply = False
        
        return response, requires_reply
    
    def _send_response(self, to_ai: str, content: str, thread_id: str = None, requires_reply: bool = False):
        """Send a response message"""
        try:
            # Load existing messages
            with open(self.messages_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            # Create response
            message_id = f"ai_msg_{len(messages)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            response = {
                "message_id": message_id,
                "from_ai": self.ai_id,
                "to_ai": to_ai,
                "content": content,
                "message_type": "discussion",
                "priority": "medium",
                "thread_id": thread_id or message_id,  # Use message_id if no thread_id
                "timestamp": datetime.now().isoformat(),
                "response_required": requires_reply,
                "auto_response": True
            }
            
            messages.append(response)
            
            # Save back
            with open(self.messages_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            
            print(f"[AETHER] Response sent: {content[:50]}...")
            
            return response
            
        except Exception as e:
            print(f"Error sending response: {e}")
            return None
    
    def _cleanup_messages_file(self):
        """Clean up old messages from the file to prevent it from growing too large"""
        try:
            if not os.path.exists(self.messages_file):
                return
            
            with open(self.messages_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            # Keep only the last 1000 messages to prevent file bloat
            if len(messages) > 1000:
                messages = messages[-1000:]
                
                with open(self.messages_file, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, indent=2, ensure_ascii=False)
                
                print(f"[AETHER] Cleaned up messages file (kept 1000 most recent messages)")
                
        except Exception as e:
            print(f"Error cleaning up messages file: {e}")
    
    def run(self, check_interval: float = 2.0):
        """Run the monitor"""
        print(f"[AETHER] Starting simple AI monitor (checking every {check_interval}s)")
        print("Press Ctrl+C to stop")
        
        cleanup_counter = 0
        cleanup_interval = 100  # Clean up every 100 checks
        
        try:
            while True:
                # Check if we're waiting for a response
                if self.waiting_for_response:
                    print(f"[AETHER] Waiting for response... (checking every {check_interval}s)")
                
                self.check_and_respond()
                
                # Periodic cleanup
                cleanup_counter += 1
                if cleanup_counter >= cleanup_interval:
                    self._cleanup_messages_file()
                    cleanup_counter = 0
                
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\n[AETHER] Monitor stopped")

def main():
    """Main function"""
    monitor = SimpleAIMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
