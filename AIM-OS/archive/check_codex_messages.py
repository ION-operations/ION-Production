import json

# Check messages sent TO Codex today
with open('mcp_ai_messages.json', 'r', encoding='utf-8') as f:
    msgs = json.load(f)

# Messages TO Codex today
codex_msgs = [m for m in msgs if '2025-11-07' in m.get('timestamp', '') and ('codex' in m.get('to_ai', '').lower() or 'codex' in m.get('to_ai', '').lower())]
codex_msgs.sort(key=lambda x: x.get('timestamp', ''))

print("MESSAGES TO CODEX TODAY:")
print("="*80)
for m in codex_msgs:
    ts = m.get('timestamp', '')[:19]
    from_ai = m.get('from_ai', 'unknown')
    thread = m.get('thread_id', 'none')
    msg_id = m.get('message_id', 'no_id')
    print(f"{ts} | {from_ai:15} -> Codex | thread: {thread:50} | ID: {msg_id}")

print(f"\nTotal messages TO Codex today: {len(codex_msgs)}")

# Check what threads were used
threads_to_codex = set(m.get('thread_id', 'none') for m in codex_msgs)
print(f"\nThreads used for messages TO Codex: {threads_to_codex}")

# Check Codex's last message
codex_from = [m for m in msgs if '2025-11-07' in m.get('timestamp', '') and 'codex' in m.get('from_ai', '').lower()]
codex_from.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
print(f"\nCodex's last message:")
if codex_from:
    last = codex_from[0]
    print(f"  Time: {last.get('timestamp', '')[:19]}")
    print(f"  Thread: {last.get('thread_id', 'none')}")
    print(f"  Content preview: {last.get('content', '')[:100]}")

