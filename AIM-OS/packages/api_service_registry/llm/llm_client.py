"""
LLMClient Abstract Base Class

Defines the interface that all LLM provider clients must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class LLMClient(ABC):
    """
    Abstract base class for all LLM API clients.
    
    All provider implementations (Gemini, Cerebras, Anthropic, etc.) must
    implement this interface to ensure consistent behavior across providers.
    """
    
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """
        Generates a simple text completion.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        context_items: Optional[List[Dict[str, Any]]] = None,
        token_budget: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generates a chat-based completion.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            context_items: Optional HHNI retrieval context items (Sev P0 requirement)
            token_budget: Optional token budget for context window validation (Sev P0 requirement)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Response dict with 'content', 'model', 'tokens_used', etc.
        """
        pass
    
    @abstractmethod
    def get_provider(self) -> str:
        """
        Returns provider name (e.g., 'gemini', 'cerebras').
        
        Returns:
            Provider identifier string
        """
        pass
    
    @abstractmethod
    def get_model(self) -> str:
        """
        Returns default model name for this provider.
        
        Returns:
            Model identifier string (e.g., 'gemini-2.5-pro', 'llama-3.1-8b')
        """
        pass

