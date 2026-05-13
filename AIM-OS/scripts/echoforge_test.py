"""
Echo Forge Self-Test & AI Audit System
=======================================

Tests the Echo Forge pipeline, audits AI provider quality,
and reports results. Can be run standalone or by agents.

Usage:
    python3 echoforge_test.py test        # Quick self-test
    python3 echoforge_test.py audit       # Full audit with Gemini CLI reviewing Ollama
    python3 echoforge_test.py providers   # Check provider status
    python3 echoforge_test.py report      # Generate and post report to bridge
"""
import json
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

ECHOFORGE_URL = "http://localhost:5002"
OLLAMA_URL = "http://localhost:11434"
BRIDGE_URL = "http://localhost:9090"


# ═════════════════════════════════════════════════════
# UTILITIES
# ═════════════════════════════════════════════════════

def http_get(url, timeout=5):
    """Simple HTTP GET."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode()
    except Exception as e:
        return 0, str(e)


def http_post(url, data, timeout=15):
    """Simple HTTP POST with JSON."""
    try:
        body = json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode()
    except Exception as e:
        return 0, str(e)


def parse_sse_response(raw):
    """Parse Server-Sent Events response to extract content."""
    content_parts = []
    for line in raw.split("\n"):
        if line.startswith("data: "):
            try:
                data = json.loads(line[6:])
                if "content" in data:
                    content_parts.append(data["content"])
                elif "response" in data:
                    content_parts.append(data["response"])
                elif "text" in data:
                    content_parts.append(data["text"])
            except json.JSONDecodeError:
                if line[6:].strip() and line[6:].strip() != "[DONE]":
                    content_parts.append(line[6:])
    return "".join(content_parts)


# ═════════════════════════════════════════════════════
# SERVICE CHECKS
# ═════════════════════════════════════════════════════

def check_services():
    """Check all required services."""
    results = {}

    # Echo Forge
    status, body = http_get(f"{ECHOFORGE_URL}/health")
    results["echoforge"] = {"status": "UP" if status == 200 else "DOWN", "port": 5002}
    if status == 200:
        try:
            results["echoforge"]["details"] = json.loads(body)
        except:
            pass

    # Ollama
    status, body = http_get(f"{OLLAMA_URL}/api/tags")
    if status == 200:
        try:
            models = [m["name"] for m in json.loads(body).get("models", [])]
            results["ollama"] = {"status": "UP", "port": 11434, "models": models}
        except:
            results["ollama"] = {"status": "UP", "port": 11434}
    else:
        results["ollama"] = {"status": "DOWN", "port": 11434}

    # Bridge
    status, _ = http_get(f"{BRIDGE_URL}/health")
    results["bridge"] = {"status": "UP" if status == 200 else "DOWN", "port": 9090}

    # Gemini CLI
    try:
        r = subprocess.run(["gemini", "--version"], capture_output=True, text=True, timeout=5)
        results["gemini_cli"] = {"status": "INSTALLED", "version": r.stdout.strip()[:50]}
    except:
        results["gemini_cli"] = {"status": "NOT FOUND"}

    return results


def print_services(results):
    """Pretty print service status."""
    print("\n=== AIM-OS Service Status ===\n")
    for name, info in results.items():
        icon = "✅" if info.get("status") in ("UP", "INSTALLED") else "❌"
        port_str = f":{info['port']}" if 'port' in info else ""
        extra = ""
        if "models" in info:
            extra = f" ({len(info['models'])} models)"
        elif "version" in info:
            extra = f" ({info['version']})"
        print(f"  {icon} {name}{port_str}: {info['status']}{extra}")
    print()


# ═════════════════════════════════════════════════════
# PIPELINE TESTS
# ═════════════════════════════════════════════════════

TEST_PROMPTS = [
    {
        "name": "basic_greeting",
        "prompt": "Say hello in exactly one sentence.",
        "check": lambda r: len(r) > 5 and len(r) < 500,
        "description": "Basic response test"
    },
    {
        "name": "code_generation",
        "prompt": "Write a Python function that adds two numbers. Only output the code.",
        "check": lambda r: "def " in r and "return" in r,
        "description": "Code generation capability"
    },
    {
        "name": "json_output",
        "prompt": "Output a JSON object with keys 'name' and 'age'. Only output valid JSON.",
        "check": lambda r: "{" in r and "}" in r,
        "description": "Structured output test"
    },
    {
        "name": "reasoning",
        "prompt": "What is 17 * 3? Answer with just the number.",
        "check": lambda r: "51" in r,
        "description": "Basic reasoning test"
    },
]


def run_pipeline_test(prompt_config, timeout=30):
    """Run a single pipeline test against Echo Forge."""
    name = prompt_config["name"]
    prompt = prompt_config["prompt"]
    check_fn = prompt_config["check"]

    start = time.time()
    status, raw = http_post(
        f"{ECHOFORGE_URL}/chat",
        {"messages": [{"role": "user", "content": prompt}]},
        timeout=timeout
    )
    elapsed = time.time() - start

    if status == 0:
        return {"name": name, "pass": False, "error": raw, "time_ms": int(elapsed * 1000)}

    # Parse SSE response
    content = parse_sse_response(raw)
    if not content:
        content = raw[:500]

    passed = check_fn(content)

    return {
        "name": name,
        "pass": passed,
        "response": content[:200],
        "time_ms": int(elapsed * 1000),
        "status_code": status,
    }


def run_all_tests():
    """Run all pipeline tests."""
    print("\n=== Echo Forge Pipeline Tests ===\n")
    results = []
    for test in TEST_PROMPTS:
        print(f"  Testing: {test['description']}...", end=" ", flush=True)
        result = run_pipeline_test(test)
        icon = "✅" if result["pass"] else "❌"
        print(f"{icon} ({result['time_ms']}ms)")
        if not result["pass"]:
            print(f"    Response: {result.get('response', result.get('error', ''))[:100]}")
        results.append(result)

    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    print(f"\n  Results: {passed}/{total} passed")
    return results


# ═════════════════════════════════════════════════════
# GEMINI CLI AUDIT
# ═════════════════════════════════════════════════════

def gemini_audit_response(prompt, ollama_response, timeout=30):
    """Use Gemini CLI to audit an Ollama response."""
    audit_prompt = f"""You are an AI quality auditor. Evaluate this LLM response.

PROMPT: {prompt}
RESPONSE: {ollama_response}

Score the response on:
1. Accuracy (0-10)
2. Completeness (0-10) 
3. Clarity (0-10)

Output ONLY a JSON object: {{"accuracy": N, "completeness": N, "clarity": N, "overall": N, "notes": "brief comment"}}"""

    try:
        result = subprocess.run(
            ["gemini", "-p", audit_prompt],
            capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout.strip()
        # Try to extract JSON from output
        start = output.find("{")
        end = output.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(output[start:end])
        return {"error": "No JSON in response", "raw": output[:200]}
    except subprocess.TimeoutExpired:
        return {"error": "Gemini CLI timeout"}
    except Exception as e:
        return {"error": str(e)}


def run_audit():
    """Full audit: Ollama responds, Gemini reviews."""
    print("\n=== AI Audit: Gemini CLI Reviews Ollama ===\n")

    audit_prompts = [
        "Explain what a neural network is in 2 sentences.",
        "Write a Python function to check if a number is prime.",
        "What are the three laws of thermodynamics?",
    ]

    results = []
    for prompt in audit_prompts:
        print(f"  Prompt: {prompt[:60]}...")

        # Get Ollama response via Echo Forge
        print("    ├─ Getting Ollama response...", end=" ", flush=True)
        status, raw = http_post(
            f"{ECHOFORGE_URL}/chat",
            {"messages": [{"role": "user", "content": prompt}]},
            timeout=30
        )
        ollama_response = parse_sse_response(raw) if status == 200 else f"Error: {raw[:100]}"
        print(f"({len(ollama_response)} chars)")

        # Gemini audit
        print("    └─ Gemini auditing...", end=" ", flush=True)
        audit = gemini_audit_response(prompt, ollama_response)
        if "overall" in audit:
            print(f"Score: {audit['overall']}/10 — {audit.get('notes', '')[:60]}")
        else:
            print(f"Error: {audit.get('error', 'unknown')}")

        results.append({
            "prompt": prompt,
            "ollama_response": ollama_response[:300],
            "audit": audit,
        })

    # Summary
    scores = [r["audit"].get("overall", 0) for r in results if "overall" in r["audit"]]
    avg = sum(scores) / len(scores) if scores else 0
    print(f"\n  Average Score: {avg:.1f}/10 ({len(scores)} audited)")
    return results


# ═════════════════════════════════════════════════════
# REPORTING
# ═════════════════════════════════════════════════════

def generate_report(services, tests, audit=None):
    """Generate a full diagnostic report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "machine": "pop-os (192.168.2.25)",
        "agent": "opus",
        "services": services,
        "tests": tests,
        "audit": audit,
    }

    # Post to bridge
    try:
        summary = f"DIAGNOSTIC REPORT: "
        passed = sum(1 for t in tests if t["pass"])
        summary += f"{passed}/{len(tests)} tests passed. "
        if audit:
            scores = [r["audit"].get("overall", 0) for r in audit if "overall" in r["audit"]]
            avg = sum(scores) / len(scores) if scores else 0
            summary += f"Avg audit score: {avg:.1f}/10."

        http_post(f"{BRIDGE_URL}/message", {
            "from": "opus",
            "content": summary,
        })
        print(f"\n📡 Report posted to bridge.")
    except:
        pass

    # Save report
    report_path = Path("/home/sev/AIM-OS-GIT/.agent/reports")
    report_path.mkdir(parents=True, exist_ok=True)
    fname = f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    (report_path / fname).write_text(json.dumps(report, indent=2, default=str))
    print(f"📄 Report saved to .agent/reports/{fname}")

    return report


# ═════════════════════════════════════════════════════
# CLI
# ═════════════════════════════════════════════════════

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "test"

    if cmd == "providers" or cmd == "status":
        services = check_services()
        print_services(services)

    elif cmd == "test":
        services = check_services()
        print_services(services)
        if services.get("echoforge", {}).get("status") != "UP":
            print("❌ Echo Forge is not running. Start it first.")
            sys.exit(1)
        tests = run_all_tests()
        generate_report(services, tests)

    elif cmd == "audit":
        services = check_services()
        print_services(services)
        tests = run_all_tests()
        audit = run_audit()
        generate_report(services, tests, audit)

    elif cmd == "report":
        services = check_services()
        print_services(services)
        tests = run_all_tests()
        generate_report(services, tests)

    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 echoforge_test.py [test|audit|providers|report]")
