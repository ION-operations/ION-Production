#!/usr/bin/env python3
"""
Simple MCP Client for AI-to-AI Communication
Connects to the running MCP server and provides easy access to AI collaboration tools
"""

import json
import sys
import os
import subprocess
from typing import Dict, Any, List
from datetime import datetime

class MCPClient:
    def __init__(self, server_command: str = "python run_mcp_32_tools.py"):
        self.server_command = server_command
        self.server_process = None
    
    def start_server(self):
        """Start the MCP server in the background"""
        try:
            self.server_process = subprocess.Popen(
                self.server_command.split(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("MCP server started successfully!")
            return True
        except Exception as e:
            print(f"Failed to start MCP server: {e}")
            return False
    
    def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server"""
        if not self.server_process:
            return {"error": "Server not running"}
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        try:
            # Send request
            self.server_process.stdin.write(json.dumps(request) + "\n")
            self.server_process.stdin.flush()
            
            # Read response
            response_line = self.server_process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            return {"error": f"Request failed: {e}"}
    
    def connect_to_running_server(self):
        """Connect to an already running server instance"""
        try:
            # Try to connect to existing server via direct file communication
            # This is a simple approach - we'll read/write the shared file
            self.server_process = "file_based"  # Mark as file-based connection
            return True
        except Exception as e:
            print(f"Failed to connect to running server: {e}")
            return False
    
    def get_ai_messages(self, from_ai: str = None, to_ai: str = None, 
                       message_type: str = None, thread_id: str = None, 
                       limit: int = 10) -> Dict[str, Any]:
        """Get AI messages with optional filters"""
        # If connected to file-based server, read directly from file
        if self.server_process == "file_based":
            return self._get_messages_from_file(from_ai, to_ai, message_type, thread_id, limit)
        
        # Otherwise use JSON-RPC
        params = {"limit": limit}
        if from_ai:
            params["from_ai"] = from_ai
        if to_ai:
            params["to_ai"] = to_ai
        if message_type:
            params["message_type"] = message_type
        if thread_id:
            params["thread_id"] = thread_id
            
        return self.send_request("mcp_aimos-6-tools_get_ai_messages", params)
    
    def send_ai_message(self, from_ai: str, to_ai: str, content: str,
                       message_type: str = "discussion", priority: str = "medium",
                       thread_id: str = None, response_required: bool = False) -> Dict[str, Any]:
        """Send an AI message"""
        # If connected to file-based server, write directly to file
        if self.server_process == "file_based":
            return self._send_message_to_file(from_ai, to_ai, content, message_type, priority, thread_id, response_required)
        
        # Otherwise use JSON-RPC
        params = {
            "from_ai": from_ai,
            "to_ai": to_ai,
            "content": content,
            "message_type": message_type,
            "priority": priority,
            "response_required": response_required
        }
        if thread_id:
            params["thread_id"] = thread_id
            
        return self.send_request("mcp_aimos-6-tools_send_ai_message", params)
    
    def start_ai_discussion(self, from_ai: str, to_ai: str, topic: str, 
                           initial_message: str) -> Dict[str, Any]:
        """Start an AI discussion thread"""
        params = {
            "from_ai": from_ai,
            "to_ai": to_ai,
            "topic": topic,
            "initial_message": initial_message
        }
        return self.send_request("mcp_aimos-6-tools_start_ai_discussion", params)
    
    def get_collaboration_summary(self) -> Dict[str, Any]:
        """Get AI collaboration summary"""
        return self.send_request("mcp_aimos-6-tools_get_ai_collaboration_summary")
    
    def _get_messages_from_file(self, from_ai: str = None, to_ai: str = None,
                                       message_type: str = None, thread_id: str = None,
                                       limit: int = 10) -> Dict[str, Any]:
        """Get messages directly from the JSON file"""
        try:
            if not os.path.exists("mcp_ai_messages.json"):
                return {"success": True, "messages": [], "count": 0, "message": "No messages file found"}

            with open("mcp_ai_messages.json", 'r', encoding='utf-8-sig') as f:
                messages = json.load(f)
            
            # Apply filters
            filtered_messages = []
            for message in messages:
                if from_ai and message.get("from_ai") != from_ai:
                    continue
                if to_ai and message.get("to_ai") != to_ai:
                    continue
                if message_type and message.get("message_type") != message_type:
                    continue
                if thread_id and message.get("thread_id") != thread_id:
                    continue
                filtered_messages.append(message)
            
            # Apply limit
            filtered_messages = filtered_messages[-limit:] if limit > 0 else filtered_messages
            
            return {
                "success": True,
                "messages": filtered_messages,
                "count": len(filtered_messages),
                "message": f"Retrieved {len(filtered_messages)} AI messages"
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to read messages: {str(e)}"}
    
    def _send_message_to_file(self, from_ai: str, to_ai: str, content: str,
                                     message_type: str, priority: str, thread_id: str = None,
                                     response_required: bool = False) -> Dict[str, Any]:
        """Send message directly to the JSON file"""
        try:
            # Load existing messages
            if os.path.exists("mcp_ai_messages.json"):
                with open("mcp_ai_messages.json", 'r', encoding='utf-8-sig') as f:
                    messages = json.load(f)
            else:
                messages = []
            
            # Create new message
            message_id = f"ai_msg_{len(messages)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            message_data = {
                "message_id": message_id,
                "from_ai": from_ai,
                "to_ai": to_ai,
                "content": content,
                "message_type": message_type,
                "priority": priority,
                "thread_id": thread_id,
                "timestamp": datetime.now().isoformat(),
                "response_required": response_required
            }
            
            messages.append(message_data)
            
            # Save back to file
            with open("mcp_ai_messages.json", 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "message_id": message_id,
                "from_ai": from_ai,
                "to_ai": to_ai,
                "message_type": message_type,
                "priority": priority,
                "thread_id": thread_id,
                "timestamp": datetime.now().isoformat(),
                "message": f"Message sent from {from_ai} to {to_ai}"
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to send message: {str(e)}"}
    
    def stop_server(self):
        """Stop the MCP server"""
        if self.server_process and self.server_process != "file_based":
            self.server_process.terminate()
            self.server_process = None
            print("MCP server stopped")

def main():
    """Command line interface for MCP client"""
    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py <command> [args...]")
        print("Commands:")
        print("  start                    - Start MCP server")
        print("  connect                  - Connect to running server (file-based)")
        print("  get_messages [from_ai]   - Get AI messages")
        print("  send_message <from> <to> <content> - Send AI message")
        print("  summary                 - Get collaboration summary")
        print("  stop                    - Stop MCP server")
        return
    
    client = MCPClient()
    command = sys.argv[1]
    
    if command == "start":
        if client.start_server():
            print("Server started. Keep this running for persistent communication.")
        else:
            print("Failed to start server")
    
    elif command == "connect":
        if client.connect_to_running_server():
            print("Connected to running server (file-based mode)")
        else:
            print("Failed to connect to running server")
    
    elif command == "get_messages":
        # Try to connect to running server first
        if not client.server_process:
            client.connect_to_running_server()
        
        from_ai = sys.argv[2] if len(sys.argv) > 2 else None
        result = client.get_ai_messages(from_ai=from_ai)
        print(json.dumps(result, indent=2))
    
    elif command == "send_message":
        if len(sys.argv) < 5:
            print("Usage: send_message <from_ai> <to_ai> <content>")
            return
        
        # Try to connect to running server first
        if not client.server_process:
            client.connect_to_running_server()
        
        from_ai, to_ai, content = sys.argv[2], sys.argv[3], sys.argv[4]
        result = client.send_ai_message(from_ai, to_ai, content)
        print(json.dumps(result, indent=2))
    
    elif command == "summary":
        result = client.get_collaboration_summary()
        print(json.dumps(result, indent=2))
    
    elif command == "stop":
        client.stop_server()
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
