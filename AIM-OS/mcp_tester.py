import urllib.request
import json
import time

def call_mcp(tool_name, args):
    req = urllib.request.Request(
        "http://127.0.0.1:5001/mcp/execute",
        data=json.dumps({"tool": tool_name, "arguments": args}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

print("=== Testing ion_query ===")
res = call_mcp("ion_query", {"intent": "AetherEngine"})
content = res.get("result", {}).get("content", [{}])[0].get("text", "")
print(f"Query Result Length: {len(content)} chars")
if len(content) > 100:
    print("SUCCESS: Context retrieved via query.")
else:
    print("FAILED: No context retrieved.")

print("\n=== Testing ion_patch ===")
patch = '''```diff_patch
--- /home/sev/operation-victus/victus/test_patch.py
+++ /home/sev/operation-victus/victus/test_patch.py
@@ -0,0 +1,2 @@
+def hello():
+    print("world")
```'''
res = call_mcp("ion_patch", {"diff_patch": patch})
print("Patch Response:", json.dumps(res, indent=2))
