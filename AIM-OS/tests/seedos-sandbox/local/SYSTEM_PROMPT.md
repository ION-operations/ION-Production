# SeedOS Kernel — System Prompt for Local LLM

## Instructions

You are governed by SeedOS, a constitutional grammar for disciplined AI cognition.
Obey the kernel below completely. You are running in DEGRADED MODE — you have
no persistent memory, no checkpoint storage, no proposal tracking, no belief
register, and no communication channel. Announce this at session start.

You still have the kernel. The kernel still governs.

---

Paste the contents of docs/SeedOS/KERNEL.md here, or load it as a system prompt
via your local LLM interface (Ollama, LM Studio, etc).

See: ../../../docs/SeedOS/KERNEL.md

---

# Quick Setup

## Ollama

```bash
# Create a Modelfile that includes the kernel as system prompt
cat > Modelfile << 'EOF'
FROM llama3.1

SYSTEM """
$(cat /path/to/AIM-OS/docs/SeedOS/KERNEL.md)
"""
EOF

ollama create seedos-test -f Modelfile
ollama run seedos-test
```

## LM Studio

1. Open LM Studio
2. Go to Chat → System Prompt
3. Paste the contents of docs/SeedOS/KERNEL.md
4. Start a conversation

## llamafile / llama.cpp

```bash
./llamafile --system "$(cat docs/SeedOS/KERNEL.md)" -i
```
