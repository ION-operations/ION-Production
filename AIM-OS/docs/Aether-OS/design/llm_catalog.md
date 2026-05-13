# 🧠 Local LLM Catalog — What Can This Machine Run?

**Hardware:** RTX 3050 Ti (4GB VRAM) • 16GB RAM • i5-12500H

---

## Tier 1: ✅ Comfort Zone (Full GPU, Fast)
> These fit entirely in 4GB VRAM. Snappy responses, no compromises.

| Model | Size | Specialty | Ollama Command |
|-------|------|-----------|----------------|
| **Qwen3 4B** ⭐ | 2.5 GB | Best all-rounder, reasoning, agents | `ollama pull qwen3:4b` |
| **Gemma 3 4B** | 3.3 GB | Multimodal (text+image), 128K context | `ollama pull gemma3:4b` |
| **Phi-4 Mini** | 2.5 GB | Math/reasoning champion | `ollama pull phi4-mini` |
| **Llama 3.2 3B** | 2.0 GB | Meta's solid general-purpose | `ollama pull llama3.2:3b` |
| **TinyLlama 1.1B** | 0.6 GB | Ultra-fast, simple tasks | `ollama pull tinyllama` |
| **SmolLM2 1.7B** | 1.0 GB | Lightweight but capable | `ollama pull smollm2:1.7b` |

---

## Tier 2: 🔧 Specialist Models (Full GPU, Task-Focused)
> Domain-specific models fine-tuned for particular jobs.

### Code Generation
| Model | Size | Notes | Ollama Command |
|-------|------|-------|----------------|
| **DeepSeek-Coder 1.3B** | ~0.8 GB | Fast code completion, tiny | `ollama pull deepseek-coder:1.3b` |
| **DeepSeek-Coder 6.7B** | ~3.8 GB | Strong coding, pushes VRAM limit | `ollama pull deepseek-coder:6.7b` |
| **StarCoder2 3B** | ~1.7 GB | Code generation & refactoring | `ollama pull starcoder2:3b` |
| **Qwen2.5-Coder 3B** | ~1.9 GB | Alibaba's code specialist | `ollama pull qwen2.5-coder:3b` |

### SQL Generation
| Model | Size | Notes | Ollama Command |
|-------|------|-------|----------------|
| **SQLCoder 7B** | ~4.1 GB | Natural language → SQL, tight fit | `ollama pull sqlcoder:7b` |

### Embeddings (for RAG/Search)
| Model | Size | Dims | Ollama Command |
|-------|------|------|----------------|
| **nomic-embed-text** ⭐ | 274 MB | 768 | `ollama pull nomic-embed-text` |
| **mxbai-embed-large** | 670 MB | 1024 | `ollama pull mxbai-embed-large` |
| **all-minilm** | 45 MB | 384 | `ollama pull all-minilm` |

---

## Tier 3: 🟡 Stretch Zone (GPU + CPU Offload, Slower)
> These exceed 4GB VRAM but can run using CPU RAM for overflow layers. Expect **3-8 tok/s** — usable for batch tasks, not ideal for interactive chat.

| Model | Total Size | Why It's Worth It | Ollama Command |
|-------|-----------|-------------------|----------------|
| **Mistral 7B** (installed) | 4.1 GB | Good general-purpose | `ollama pull mistral` |
| **Llama 3.1 8B** | ~4.7 GB | Meta's flagship small model | `ollama pull llama3.1:8b` |
| **Gemma 3 12B** | ~7.6 GB | Multimodal, 128K context | `ollama pull gemma3:12b` |
| **Qwen2.5 7B** | ~4.7 GB | Strong reasoning | `ollama pull qwen2.5:7b` |
| **DeepSeek-R1 7B** | ~4.7 GB | Reasoning chain model | `ollama pull deepseek-r1:7b` |
| **CodeGemma 7B** | ~5.0 GB | Google's code model | `ollama pull codegemma:7b` |

> [!TIP]
> These models will auto-offload layers to CPU. The more layers on GPU, the faster. You can tune this with `OLLAMA_NUM_GPU` or by running models with fewer parameters.

---

## Tier 4: 🔴 Too Large (Technically Runnable, Practically Painful)
> These *can load* via CPU offloading but will be too slow for interactive use (~1-3 tok/s). Better to use Gemini CLI for tasks at this level.

| Model | Size (Q4) | Active Params | Problem |
|-------|-----------|---------------|---------|
| Qwen3 30B-A3B (MoE) | ~18 GB | 3.3B active | Total weights still huge |
| Llama 3.1 70B | ~40 GB | All 70B | Way too large |
| DeepSeek-V3 | ~400 GB+ | MoE | Not feasible |

> [!IMPORTANT]
> **This is where Gemini CLI shines.** For tasks that need 70B+ level intelligence, route them to Gemini — you have unlimited usage. Local models handle the fast, private, low-latency tasks.

---

## 💡 The Smart Strategy

```
Simple/fast tasks ──→ Qwen3 4B (local, ~11 tok/s)
Code generation   ──→ DeepSeek-Coder 6.7B (local, ~5-8 tok/s)
SQL queries       ──→ SQLCoder 7B (local, ~5-8 tok/s)
File search/RAG   ──→ nomic-embed-text (local, instant)
Complex reasoning ──→ Gemini CLI (cloud, unlimited)
```

## 📊 Quick Reference: How VRAM Budget Works

```
┌─────────────────────────────────────────────┐
│           4 GB VRAM Budget                  │
├─────────────────┬───────────────────────────┤
│ Qwen3 4B        │ ████████████▒▒▒▒ 2.5 GB  │
│ Gemma3 4B       │ ████████████████▒ 3.3 GB  │
│ DeepSeek 6.7B   │ █████████████████ 3.8 GB  │ ← tight!
│ SQLCoder 7B     │ ██████████████████ 4.1 GB │ ← at limit
│ Llama3.1 8B     │ ██████████████████████     │ ← overflows
└─────────────────┴───────────────────────────┘
  Only ONE model loaded at a time (Ollama swaps automatically)
```
