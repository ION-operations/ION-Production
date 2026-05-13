"""
AI Engine — LLM Providers

Each provider implements the same interface:
    complete(prompt, system, model, stream, timeout) -> ProviderResponse
    stream(prompt, system, model, timeout) -> AsyncIterator[str]
    status() -> dict
"""
