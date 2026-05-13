import json
from datetime import datetime

# Load messages
with open('mcp_ai_messages.json', 'r', encoding='utf-8') as f:
    msgs = json.load(f)

# Filter today's messages
today_msgs = [m for m in msgs if '2025-11-07' in m.get('timestamp', '')]
today_msgs.sort(key=lambda x: x.get('timestamp', ''))

print(f"Total messages on 2025-11-07: {len(today_msgs)}")
print("\n" + "="*80)
print("ALL MESSAGES TODAY:")
print("="*80)

for m in today_msgs:
    ts = m.get('timestamp', '')[:19] if m.get('timestamp') else 'unknown'
    from_ai = m.get('from_ai', 'unknown')
    to_ai = m.get('to_ai', 'unknown')
    thread = m.get('thread_id', 'none')
    msg_type = m.get('message_type', 'unknown')
    priority = m.get('priority', 'unknown')
    content_preview = m.get('content', '')[:60].replace('\n', ' ')
    
    print(f"{ts} | {from_ai:15} -> {to_ai:15} | thread: {thread[:50]:50} | {msg_type:15} | {priority:8}")
    print(f"  Preview: {content_preview}...")
    print()

print("\n" + "="*80)
print("THREAD ANALYSIS:")
print("="*80)

threads = {}
for m in today_msgs:
    thread = m.get('thread_id', 'none')
    if thread not in threads:
        threads[thread] = []
    threads[thread].append(m)

for thread, msgs in sorted(threads.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"\nThread: {thread}")
    print(f"  Messages: {len(msgs)}")
    print(f"  From: {', '.join(set(m.get('from_ai', 'unknown') for m in msgs))}")
    print(f"  To: {', '.join(set(m.get('to_ai', 'unknown') for m in msgs))}")

print("\n" + "="*80)
print("MESSAGES TO CODEX:")
print("="*80)

codex_msgs = [m for m in today_msgs if 'codex' in m.get('to_ai', '').lower()]
print(f"Total messages TO Codex today: {len(codex_msgs)}")

for m in codex_msgs:
    ts = m.get('timestamp', '')[:19] if m.get('timestamp') else 'unknown'
    from_ai = m.get('from_ai', 'unknown')
    thread = m.get('thread_id', 'none')
    content_preview = m.get('content', '')[:80].replace('\n', ' ')
    print(f"{ts} | {from_ai} -> Codex | thread: {thread}")
    print(f"  {content_preview}...")
    print()

