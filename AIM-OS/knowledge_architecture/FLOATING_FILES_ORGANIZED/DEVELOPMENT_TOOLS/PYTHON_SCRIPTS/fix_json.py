#!/usr/bin/env python3
"""
Fix corrupted mcp_ai_messages.json file
"""
import json

# Read the corrupted file
with open('mcp_ai_messages.json', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Find the first valid JSON array ending
end_idx = content.find(']', 0)
if end_idx > 0:
    valid_json = content[:end_idx + 1]
    
    # Parse the valid JSON
    data = json.loads(valid_json)
    
    print(f"Valid messages found: {len(data)}")
    print(f"Last message ID: {data[-1]['message_id']}")
    print(f"Last message timestamp: {data[-1]['timestamp']}")
    
    # Write cleaned JSON back
    with open('mcp_ai_messages.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("File fixed successfully!")
else:
    print("Could not find valid JSON ending")
