"""
API Service Registry for MCP Tools
Provides unified interface for calling external APIs (Meshy, ElevenLabs, Minimax, etc.)
with automatic AIM-OS integration.

Phase 2: MCP Tools Integration
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class APIProvider(str, Enum):
    """Supported API providers"""
    MESHY = "meshy"
    ELEVENLABS = "elevenlabs"
    MINIMAX = "minimax"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    DALLE = "dalle"
    STABLE_DIFFUSION = "stable_diffusion"
    LEONARDO_AI = "leonardo_ai"
    RUNWAY_ML = "runway_ml"
    PIKA_LABS = "pika_labs"
    TAVILY = "tavily"
    PERPLEXITY = "perplexity"
    NEWSAPI = "newsapi"


@dataclass
class APIResponse:
    """Standardized API response"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    aimos: Optional[Dict[str, Any]] = None


class APIServiceRegistry:
    """Registry for API services with automatic AIM-OS integration"""
    
    def __init__(self):
        """Initialize API service registry"""
        self.services: Dict[str, Any] = {}
        self.api_keys: Dict[str, str] = {}
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from environment variables"""
        # Meshy
        if os.getenv("MESHY_API_KEY"):
            self.api_keys["meshy"] = os.getenv("MESHY_API_KEY")
        
        # ElevenLabs
        if os.getenv("ELEVENLABS_API_KEY"):
            self.api_keys["elevenlabs"] = os.getenv("ELEVENLABS_API_KEY")
        
        # Minimax
        if os.getenv("MINIMAX_API_KEY"):
            self.api_keys["minimax"] = os.getenv("MINIMAX_API_KEY")
        
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.api_keys["openai"] = os.getenv("OPENAI_API_KEY")
        
        # Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            self.api_keys["anthropic"] = os.getenv("ANTHROPIC_API_KEY")
        
        # Gemini
        if os.getenv("GEMINI_API_KEY"):
            self.api_keys["gemini"] = os.getenv("GEMINI_API_KEY")
        
        # DeepSeek
        if os.getenv("DEEPSEEK_API_KEY"):
            self.api_keys["deepseek"] = os.getenv("DEEPSEEK_API_KEY")
        
        # Cerebras
        if os.getenv("CEREBRAS_API_KEY"):
            self.api_keys["cerebras"] = os.getenv("CEREBRAS_API_KEY")
        
        # DALL-E (OpenAI)
        if os.getenv("OPENAI_API_KEY"):
            self.api_keys["dalle"] = os.getenv("OPENAI_API_KEY")
        
        # Stable Diffusion (Replicate)
        if os.getenv("REPLICATE_API_TOKEN"):
            self.api_keys["stable_diffusion"] = os.getenv("REPLICATE_API_TOKEN")
        
        # Leonardo AI
        if os.getenv("LEONARDO_AI_API_KEY"):
            self.api_keys["leonardo_ai"] = os.getenv("LEONARDO_AI_API_KEY")
        
        # Runway ML
        if os.getenv("RUNWAY_ML_API_KEY"):
            self.api_keys["runway_ml"] = os.getenv("RUNWAY_ML_API_KEY")
        
        # Pika Labs
        if os.getenv("PIKA_LABS_API_KEY"):
            self.api_keys["pika_labs"] = os.getenv("PIKA_LABS_API_KEY")
        
        # Tavily
        if os.getenv("TAVILY_API_KEY"):
            self.api_keys["tavily"] = os.getenv("TAVILY_API_KEY")
        
        # Perplexity
        if os.getenv("PERPLEXITY_API_KEY"):
            self.api_keys["perplexity"] = os.getenv("PERPLEXITY_API_KEY")
        
        # NewsAPI
        if os.getenv("NEWSAPI_API_KEY"):
            self.api_keys["newsapi"] = os.getenv("NEWSAPI_API_KEY")
    
    def list_apis(self) -> List[Dict[str, Any]]:
        """List all available APIs"""
        apis = []
        
        # Meshy
        apis.append({
            "provider": "meshy",
            "name": "Meshy",
            "description": "3D model generation API",
            "available": "meshy" in self.api_keys,
            "endpoints": [
                "text-to-3d",
                "image-to-3d",
                "multi-image-to-3d",
                "remesh",
                "retexture",
                "rig",
                "balance",
                "get-task-status"
            ]
        })
        
        # ElevenLabs
        apis.append({
            "provider": "elevenlabs",
            "name": "ElevenLabs",
            "description": "Text-to-Speech API",
            "available": "elevenlabs" in self.api_keys,
            "endpoints": [
                "text-to-speech",
                "get-voices",
                "clone-voice",
                "delete-voice",
                "update-voice-settings"
            ]
        })
        
        # Minimax
        apis.append({
            "provider": "minimax",
            "name": "Minimax",
            "description": "LLM chat and video generation API",
            "available": "minimax" in self.api_keys,
            "endpoints": [
                "chat-completion",
                "stream-chat-completion",
                "generate-video",
                "get-task-status"
            ]
        })
        
        # OpenAI
        apis.append({
            "provider": "openai",
            "name": "OpenAI",
            "description": "GPT models, DALL-E, Whisper",
            "available": "openai" in self.api_keys,
            "endpoints": [
                "chat-completion",
                "image-generation",
                "audio-transcription",
                "audio-translation"
            ]
        })
        
        # Anthropic
        apis.append({
            "provider": "anthropic",
            "name": "Anthropic Claude",
            "description": "Claude models",
            "available": "anthropic" in self.api_keys,
            "endpoints": [
                "chat-completion",
                "stream-chat-completion"
            ]
        })
        
        # Gemini
        apis.append({
            "provider": "gemini",
            "name": "Google Gemini",
            "description": "Gemini models",
            "available": "gemini" in self.api_keys,
            "endpoints": [
                "chat-completion",
                "stream-chat-completion"
            ]
        })
        
        # DeepSeek
        apis.append({
            "provider": "deepseek",
            "name": "DeepSeek",
            "description": "DeepSeek models",
            "available": "deepseek" in self.api_keys,
            "endpoints": [
                "chat-completion",
                "stream-chat-completion"
            ]
        })
        
        # Cerebras
        apis.append({
            "provider": "cerebras",
            "name": "Cerebras",
            "description": "Ultra-fast LLM inference",
            "available": "cerebras" in self.api_keys,
            "endpoints": [
                "chat-completion",
                "stream-chat-completion"
            ]
        })
        
        # DALL-E
        apis.append({
            "provider": "dalle",
            "name": "DALL-E",
            "description": "OpenAI DALL-E image generation",
            "available": "dalle" in self.api_keys,
            "endpoints": [
                "create-image",
                "create-image-variation",
                "edit-image"
            ]
        })
        
        # Stable Diffusion (Replicate)
        apis.append({
            "provider": "stable_diffusion",
            "name": "Stable Diffusion",
            "description": "Stable Diffusion via Replicate",
            "available": "stable_diffusion" in self.api_keys,
            "endpoints": [
                "create-prediction",
                "get-prediction",
                "list-models"
            ]
        })
        
        # Leonardo AI
        apis.append({
            "provider": "leonardo_ai",
            "name": "Leonardo AI",
            "description": "Leonardo AI image generation",
            "available": "leonardo_ai" in self.api_keys,
            "endpoints": [
                "generate-image",
                "get-generation-status",
                "upscale-image",
                "remove-background"
            ]
        })
        
        # Runway ML
        apis.append({
            "provider": "runway_ml",
            "name": "Runway ML",
            "description": "Runway ML video generation",
            "available": "runway_ml" in self.api_keys,
            "endpoints": [
                "text-to-video",
                "image-to-video",
                "get-task-status"
            ]
        })
        
        # Pika Labs
        apis.append({
            "provider": "pika_labs",
            "name": "Pika Labs",
            "description": "Pika Labs video generation",
            "available": "pika_labs" in self.api_keys,
            "endpoints": [
                "text-to-video",
                "image-to-video",
                "get-task-status"
            ]
        })
        
        # Tavily
        apis.append({
            "provider": "tavily",
            "name": "Tavily",
            "description": "AI-powered search and research",
            "available": "tavily" in self.api_keys,
            "endpoints": [
                "search",
                "research",
                "answer"
            ]
        })
        
        # Perplexity
        apis.append({
            "provider": "perplexity",
            "name": "Perplexity",
            "description": "Perplexity AI search",
            "available": "perplexity" in self.api_keys,
            "endpoints": [
                "chat-completion",
                "search"
            ]
        })
        
        # NewsAPI
        apis.append({
            "provider": "newsapi",
            "name": "NewsAPI",
            "description": "News aggregation API",
            "available": "newsapi" in self.api_keys,
            "endpoints": [
                "top-headlines",
                "everything",
                "sources"
            ]
        })
        
        return apis
    
    def call_api(
        self,
        provider: str,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        integrate_aimos: bool = True
    ) -> APIResponse:
        """Call an external API with automatic AIM-OS integration"""
        start_time = time.time()
        
        try:
            # Route to appropriate service
            if provider == "meshy":
                result = self._call_meshy(endpoint, method, data)
            elif provider == "elevenlabs":
                result = self._call_elevenlabs(endpoint, method, data)
            elif provider == "minimax":
                result = self._call_minimax(endpoint, method, data)
            elif provider == "openai":
                result = self._call_openai(endpoint, method, data)
            elif provider == "anthropic":
                result = self._call_anthropic(endpoint, method, data)
            elif provider == "gemini":
                result = self._call_gemini(endpoint, method, data)
            elif provider == "deepseek":
                result = self._call_deepseek(endpoint, method, data)
            elif provider == "dalle":
                result = self._call_dalle(endpoint, method, data)
            elif provider == "stable_diffusion":
                result = self._call_stable_diffusion(endpoint, method, data)
            elif provider == "leonardo_ai":
                result = self._call_leonardo_ai(endpoint, method, data)
            elif provider == "runway_ml":
                result = self._call_runway_ml(endpoint, method, data)
            elif provider == "pika_labs":
                result = self._call_pika_labs(endpoint, method, data)
            elif provider == "tavily":
                result = self._call_tavily(endpoint, method, data)
            elif provider == "perplexity":
                result = self._call_perplexity(endpoint, method, data)
            elif provider == "newsapi":
                result = self._call_newsapi(endpoint, method, data)
            elif provider == "cerebras":
                result = self._call_cerebras(endpoint, method, data)
            else:
                return APIResponse(
                    success=False,
                    error=f"Unknown provider: {provider}"
                )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Add metadata
            result.metadata = {
                "provider": provider,
                "endpoint": endpoint,
                "method": method,
                "latency_ms": latency_ms,
                "timestamp": time.time()
            }
            
            # Integrate with AIM-OS (if enabled and CMC available)
            if integrate_aimos:
                try:
                    # Try to import CMC service for integration
                    # This will be called from MCP server context
                    result.aimos = self._integrate_with_aimos(
                        provider=provider,
                        endpoint=endpoint,
                        request=data,
                        response=result.data if result.success else None,
                        latency_ms=latency_ms,
                        success=result.success,
                        error=result.error
                    )
                except Exception as e:
                    # If AIM-OS integration fails, continue without it
                    result.aimos = {"error": str(e)}
            
            return result
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return APIResponse(
                success=False,
                error=str(e),
                metadata={
                    "provider": provider,
                    "endpoint": endpoint,
                    "method": method,
                    "latency_ms": latency_ms,
                    "timestamp": time.time()
                }
            )
    
    def _call_meshy(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call Meshy API"""
        import requests
        
        api_key = self.api_keys.get("meshy")
        if not api_key:
            return APIResponse(success=False, error="Meshy API key not configured")
        
        base_url = "https://api.meshy.ai/v2"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            if endpoint == "text-to-3d":
                url = f"{base_url}/text-to-3d"
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif endpoint == "image-to-3d":
                url = f"{base_url}/image-to-3d"
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif endpoint == "multi-image-to-3d":
                url = f"{base_url}/multi-image-to-3d"
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif endpoint == "remesh":
                url = f"{base_url}/remesh"
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif endpoint == "retexture":
                url = f"{base_url}/retexture"
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif endpoint == "rig":
                url = f"{base_url}/rigging-and-animation"
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif endpoint == "balance":
                url = f"{base_url}/balance"
                response = requests.get(url, headers=headers, timeout=10)
            elif endpoint.startswith("get-task-status"):
                # Extract task_id from endpoint or data
                task_id = data.get("task_id") if data else endpoint.split("/")[-1]
                url = f"{base_url}/text-to-3d/{task_id}"
                response = requests.get(url, headers=headers, timeout=10)
            else:
                return APIResponse(success=False, error=f"Unknown Meshy endpoint: {endpoint}")
            
            response.raise_for_status()
            return APIResponse(success=True, data=response.json())
            
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_elevenlabs(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call ElevenLabs API"""
        import requests
        
        api_key = self.api_keys.get("elevenlabs")
        if not api_key:
            return APIResponse(success=False, error="ElevenLabs API key not configured")
        
        base_url = "https://api.elevenlabs.io/v1"
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        try:
            if endpoint == "text-to-speech":
                voice_id = data.get("voice_id", "21m00Tcm4TlvDq8ikWAM") if data else "21m00Tcm4TlvDq8ikWAM"
                url = f"{base_url}/text-to-speech/{voice_id}"
                response = requests.post(url, json=data, headers=headers, timeout=30)
                # ElevenLabs returns binary audio data
                if response.ok:
                    return APIResponse(success=True, data={"audio_data": response.content})
                else:
                    return APIResponse(success=False, error=response.text)
            elif endpoint == "get-voices":
                url = f"{base_url}/voices"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "clone-voice":
                url = f"{base_url}/voices/add"
                # This requires multipart/form-data, simplified for now
                return APIResponse(success=False, error="Clone voice requires file upload (not yet implemented)")
            elif endpoint == "delete-voice":
                voice_id = data.get("voice_id") if data else None
                if not voice_id:
                    return APIResponse(success=False, error="voice_id required")
                url = f"{base_url}/voices/{voice_id}"
                response = requests.delete(url, headers=headers, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data={})
            elif endpoint == "update-voice-settings":
                voice_id = data.get("voice_id") if data else None
                if not voice_id:
                    return APIResponse(success=False, error="voice_id required")
                url = f"{base_url}/voices/{voice_id}/settings"
                settings = {k: v for k, v in data.items() if k != "voice_id"} if data else {}
                response = requests.post(url, json=settings, headers=headers, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            else:
                return APIResponse(success=False, error=f"Unknown ElevenLabs endpoint: {endpoint}")
                
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_minimax(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call Minimax API"""
        import requests
        
        api_key = self.api_keys.get("minimax")
        if not api_key:
            return APIResponse(success=False, error="Minimax API key not configured")
        
        base_url = "https://api.minimax.chat/v1"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            if endpoint == "chat-completion":
                url = f"{base_url}/chat/completions"
                response = requests.post(url, json=data, headers=headers, timeout=30)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "generate-video":
                url = f"{base_url}/video/generate"
                response = requests.post(url, json=data, headers=headers, timeout=30)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint.startswith("get-task-status"):
                task_id = data.get("task_id") if data else endpoint.split("/")[-1]
                url = f"{base_url}/video/tasks/{task_id}"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            else:
                return APIResponse(success=False, error=f"Unknown Minimax endpoint: {endpoint}")
                
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_openai(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call OpenAI API (GPT, DALL-E, Whisper)"""
        import requests
        
        api_key = self.api_keys.get("openai")
        if not api_key:
            return APIResponse(success=False, error="OpenAI API key not configured")
        
        base_url = "https://api.openai.com/v1"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            if endpoint == "chat-completion":
                url = f"{base_url}/chat/completions"
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "image-generation" or endpoint == "create-image":
                url = f"{base_url}/images/generations"
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "audio-transcription":
                url = f"{base_url}/audio/transcriptions"
                # Audio requires multipart/form-data
                return APIResponse(success=False, error="Audio transcription requires file upload (not yet implemented)")
            elif endpoint == "audio-translation":
                url = f"{base_url}/audio/translations"
                # Audio requires multipart/form-data
                return APIResponse(success=False, error="Audio translation requires file upload (not yet implemented)")
            else:
                return APIResponse(success=False, error=f"Unknown OpenAI endpoint: {endpoint}")
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_dalle(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call DALL-E API (uses OpenAI API)"""
        # DALL-E uses the same OpenAI API key
        return self._call_openai(endpoint if endpoint != "create-image" else "image-generation", method, data)
    
    def _call_stable_diffusion(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call Stable Diffusion via Replicate API"""
        import requests
        
        api_token = self.api_keys.get("stable_diffusion")
        if not api_token:
            return APIResponse(success=False, error="Replicate API token not configured")
        
        base_url = "https://api.replicate.com/v1"
        headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if endpoint == "create-prediction":
                url = f"{base_url}/predictions"
                response = requests.post(url, json=data, headers=headers, timeout=30)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "get-prediction":
                prediction_id = data.get("prediction_id") if data else None
                if not prediction_id:
                    return APIResponse(success=False, error="prediction_id required")
                url = f"{base_url}/predictions/{prediction_id}"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "list-models":
                # List available models (simplified)
                url = f"{base_url}/models"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            else:
                return APIResponse(success=False, error=f"Unknown Stable Diffusion endpoint: {endpoint}")
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_leonardo_ai(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call Leonardo AI API"""
        import requests
        
        api_key = self.api_keys.get("leonardo_ai")
        if not api_key:
            return APIResponse(success=False, error="Leonardo AI API key not configured")
        
        base_url = "https://cloud.leonardo.ai/api/rest/v1"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            if endpoint == "generate-image":
                url = f"{base_url}/generations"
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "get-generation-status":
                generation_id = data.get("generation_id") if data else None
                if not generation_id:
                    return APIResponse(success=False, error="generation_id required")
                url = f"{base_url}/generations/{generation_id}"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "upscale-image":
                url = f"{base_url}/image-upscale"
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "remove-background":
                url = f"{base_url}/image-remove-background"
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            else:
                return APIResponse(success=False, error=f"Unknown Leonardo AI endpoint: {endpoint}")
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_runway_ml(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call Runway ML API"""
        import requests
        
        api_key = self.api_keys.get("runway_ml")
        if not api_key:
            return APIResponse(success=False, error="Runway ML API key not configured")
        
        base_url = "https://api.runwayml.com/v1"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            if endpoint == "text-to-video":
                url = f"{base_url}/text-to-video"
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "image-to-video":
                url = f"{base_url}/image-to-video"
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint.startswith("get-task-status"):
                task_id = data.get("task_id") if data else endpoint.split("/")[-1]
                url = f"{base_url}/tasks/{task_id}"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            else:
                return APIResponse(success=False, error=f"Unknown Runway ML endpoint: {endpoint}")
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_pika_labs(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call Pika Labs API"""
        import requests
        
        api_key = self.api_keys.get("pika_labs")
        if not api_key:
            return APIResponse(success=False, error="Pika Labs API key not configured")
        
        base_url = "https://api.pika.art/v1"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            if endpoint == "text-to-video":
                url = f"{base_url}/generate"
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "image-to-video":
                url = f"{base_url}/generate"
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint.startswith("get-task-status"):
                task_id = data.get("task_id") if data else endpoint.split("/")[-1]
                url = f"{base_url}/tasks/{task_id}"
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            else:
                return APIResponse(success=False, error=f"Unknown Pika Labs endpoint: {endpoint}")
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_tavily(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call Tavily API"""
        import requests
        
        api_key = self.api_keys.get("tavily")
        if not api_key:
            return APIResponse(success=False, error="Tavily API key not configured")
        
        base_url = "https://api.tavily.com"
        headers = {
            "Content-Type": "application/json"
        }
        params = {"api_key": api_key}
        
        try:
            if endpoint == "search":
                url = f"{base_url}/search"
                response = requests.post(url, json=data, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "research":
                url = f"{base_url}/research"
                response = requests.post(url, json=data, headers=headers, params=params, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "answer":
                url = f"{base_url}/answer"
                response = requests.post(url, json=data, headers=headers, params=params, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            else:
                return APIResponse(success=False, error=f"Unknown Tavily endpoint: {endpoint}")
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_perplexity(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call Perplexity API"""
        import requests
        
        api_key = self.api_keys.get("perplexity")
        if not api_key:
            return APIResponse(success=False, error="Perplexity API key not configured")
        
        base_url = "https://api.perplexity.ai"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            if endpoint == "chat-completion":
                url = f"{base_url}/chat/completions"
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "search":
                url = f"{base_url}/search"
                response = requests.post(url, json=data, headers=headers, timeout=60)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            else:
                return APIResponse(success=False, error=f"Unknown Perplexity endpoint: {endpoint}")
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_newsapi(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call NewsAPI"""
        import requests
        
        api_key = self.api_keys.get("newsapi")
        if not api_key:
            return APIResponse(success=False, error="NewsAPI key not configured")
        
        base_url = "https://newsapi.org/v2"
        params = {"apiKey": api_key}
        if data:
            params.update(data)
        
        try:
            if endpoint == "top-headlines":
                url = f"{base_url}/top-headlines"
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "everything":
                url = f"{base_url}/everything"
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            elif endpoint == "sources":
                url = f"{base_url}/sources"
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                return APIResponse(success=True, data=response.json())
            else:
                return APIResponse(success=False, error=f"Unknown NewsAPI endpoint: {endpoint}")
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_cerebras(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call Cerebras API"""
        try:
            from llm_client import CerebrasClient
            
            api_key = self.api_keys.get("cerebras")
            if not api_key:
                return APIResponse(success=False, error="Cerebras API key not configured")
            
            # Extract model from data or use default
            model = data.get("model", "llama3.1-8b") if data else "llama3.1-8b"
            client = CerebrasClient(api_key=api_key, model=model)
            
            if endpoint == "chat-completion":
                prompt = data.get("prompt", "") if data else ""
                if not prompt:
                    return APIResponse(success=False, error="prompt required")
                
                kwargs = {}
                if "temperature" in (data or {}):
                    kwargs["temperature"] = data["temperature"]
                if "max_tokens" in (data or {}):
                    kwargs["max_tokens"] = data["max_tokens"]
                
                response = client.generate(prompt, **kwargs)
                
                return APIResponse(
                    success=True,
                    data={
                        "text": response.text,
                        "model": response.model,
                        "tokens_used": response.tokens_used,
                        "latency_ms": response.latency_ms,
                        "confidence": response.confidence,
                        "metadata": response.metadata
                    }
                )
            else:
                return APIResponse(success=False, error=f"Unknown Cerebras endpoint: {endpoint}")
        except ImportError:
            return APIResponse(success=False, error="llm_client package not available")
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_anthropic(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call Anthropic Claude API"""
        try:
            from llm_client import AnthropicClient
            
            api_key = self.api_keys.get("anthropic")
            if not api_key:
                return APIResponse(success=False, error="Anthropic API key not configured")
            
            # Extract model from data or use default
            model = data.get("model", "claude-3-5-sonnet-20241022") if data else "claude-3-5-sonnet-20241022"
            client = AnthropicClient(api_key=api_key, model=model)
            
            if endpoint == "chat-completion":
                # Support both simple prompt and messages format
                if "messages" in (data or {}):
                    messages = data["messages"]
                    system = data.get("system")
                    prompt = messages[-1]["content"] if messages else ""
                else:
                    prompt = data.get("prompt", "") if data else ""
                    messages = None
                    system = data.get("system") if data else None
                
                if not prompt and not messages:
                    return APIResponse(success=False, error="prompt or messages required")
                
                # Call LLM client
                kwargs = {}
                if messages:
                    kwargs["messages"] = messages
                if system:
                    kwargs["system"] = system
                if "temperature" in (data or {}):
                    kwargs["temperature"] = data["temperature"]
                if "max_tokens" in (data or {}):
                    kwargs["max_tokens"] = data["max_tokens"]
                
                response = client.generate(prompt if not messages else "", **kwargs)
                
                return APIResponse(
                    success=True,
                    data={
                        "text": response.text,
                        "model": response.model,
                        "tokens_used": response.tokens_used,
                        "latency_ms": response.latency_ms,
                        "confidence": response.confidence,
                        "metadata": response.metadata
                    }
                )
            else:
                return APIResponse(success=False, error=f"Unknown Anthropic endpoint: {endpoint}")
        except ImportError:
            return APIResponse(success=False, error="llm_client package not available")
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_gemini(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call Gemini API"""
        # Use existing llm_client package
        try:
            from llm_client import GeminiClient
            api_key = self.api_keys.get("gemini")
            if not api_key:
                return APIResponse(success=False, error="Gemini API key not configured")
            
            client = GeminiClient(api_key=api_key)
            if endpoint == "chat-completion":
                prompt = data.get("prompt") if data else ""
                response = client.generate(prompt)
                return APIResponse(
                    success=True,
                    data={
                        "text": response.text,
                        "model": response.model,
                        "tokens_used": response.tokens_used,
                        "latency_ms": response.latency_ms
                    }
                )
            else:
                return APIResponse(success=False, error=f"Unknown Gemini endpoint: {endpoint}")
        except ImportError:
            return APIResponse(success=False, error="llm_client package not available")
        except Exception as e:
            return APIResponse(success=False, error=str(e))
    
    def _call_deepseek(self, endpoint: str, method: str, data: Optional[Dict[str, Any]]) -> APIResponse:
        """Call DeepSeek API"""
        # Placeholder - implement DeepSeek API calls
        return APIResponse(success=False, error="DeepSeek API not yet implemented")
    
    def _integrate_with_aimos(
        self,
        provider: str,
        endpoint: str,
        request: Optional[Dict[str, Any]],
        response: Optional[Any],
        latency_ms: int,
        success: bool,
        error: Optional[str]
    ) -> Dict[str, Any]:
        """Integrate API call with AIM-OS systems (CMC, HHNI, VIF, SEG)"""
        # This will be called from MCP server context where CMC/VIF/etc are available
        # For now, return placeholder structure
        return {
            "cmc": {"atom_id": None, "stored": False},
            "hhni": {"indexed": False},
            "vif": {"witness_id": None},
            "seg": {"entities_created": 0, "relations_created": 0}
        }
    
    def get_api_status(self, provider: str) -> Dict[str, Any]:
        """Get status for a specific API"""
        api_key = self.api_keys.get(provider)
        return {
            "provider": provider,
            "configured": api_key is not None,
            "available": api_key is not None,
            "endpoints": self._get_endpoints_for_provider(provider)
        }
    
    def _get_endpoints_for_provider(self, provider: str) -> List[str]:
        """Get available endpoints for a provider"""
        apis = self.list_apis()
        for api in apis:
            if api["provider"] == provider:
                return api.get("endpoints", [])
        return []


# Singleton instance
_api_registry: Optional[APIServiceRegistry] = None


def get_api_registry() -> APIServiceRegistry:
    """Get singleton API registry instance"""
    global _api_registry
    if _api_registry is None:
        _api_registry = APIServiceRegistry()
    return _api_registry


# ============================================================================
# LLM API Registry (New - Phase 1 MVP)
# ============================================================================

# Export LLM registry for MCP server
try:
    from .llm import get_api_registry as get_llm_api_registry
    # For LLM calls, use the new LLM registry
    # For other API calls, use the existing registry
    def get_api_registry_for_llm():
        """Get LLM API registry (new implementation)"""
        return get_llm_api_registry()
except ImportError:
    # LLM registry not available yet
    def get_api_registry_for_llm():
        """LLM registry not available"""
        return None
