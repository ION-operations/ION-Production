"""
PLIx Parser Bridge

Bridges between TypeScript PLIx parser (Node.js) and Python APOE.
Uses subprocess + JSON for language boundary crossing.
"""

import subprocess
import json
import hashlib
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


class PLIxParseError(Exception):
    """Raised when PLIx parsing fails"""
    
    def __init__(self, errors: list):
        self.errors = errors
        messages = [f"Line {e['line']}: {e['message']}" for e in errors]
        super().__init__("\n".join(messages))


@dataclass
class PLIxIntent:
    """PLIx intent structure (from parser)"""
    speech_act: str
    entity: str
    action: str
    contract: Dict[str, Any]
    plan: Dict[str, Any]
    evidence: Dict[str, Any]
    metadata: Dict[str, Any]


class PLIxParserBridge:
    """
    Bridge to TypeScript PLIx parser.
    
    Calls PLIx parser (Node.js) via subprocess and converts JSON AST
    to Python structures. Includes caching to avoid re-parsing.
    
    Usage:
        bridge = PLIxParserBridge()
        intent = bridge.parse(plix_text)
        # intent is Python PLIxIntent object
    """
    
    def __init__(
        self,
        node_path: str = "node",
        plix_cli_path: str = "packages/plix/dist/cli-json.js",
        cache_ttl_seconds: int = 3600
    ):
        """
        Initialize parser bridge.
        
        Args:
            node_path: Path to Node.js executable
            plix_cli_path: Path to PLIx CLI script
            cache_ttl_seconds: Cache TTL (default: 1 hour)
        """
        self.node_path = node_path
        self.plix_cli_path = plix_cli_path
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        
        # Cache: {intent_hash: (intent, timestamp)}
        self._cache: Dict[str, tuple[PLIxIntent, datetime]] = {}
    
    def parse(self, plix_text: str) -> PLIxIntent:
        """
        Parse PLIx text using TypeScript parser.
        
        Args:
            plix_text: PLIx intent in CNL
            
        Returns:
            PLIxIntent: Parsed intent structure
            
        Raises:
            PLIxParseError: If parsing fails
            FileNotFoundError: If Node.js not found
            subprocess.TimeoutExpired: If parsing takes >30s
        """
        # Check cache
        intent_hash = self._hash_text(plix_text)
        if intent_hash in self._cache:
            cached_intent, cached_time = self._cache[intent_hash]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_intent
        
        # Parse using TypeScript parser
        try:
            result = subprocess.run(
                [self.node_path, self.plix_cli_path, "--json", "-"],
                input=plix_text.encode('utf-8'),
                capture_output=True,
                timeout=30,
                check=False  # We'll check returncode manually
            )
            
            # Parse JSON output
            output_json = json.loads(result.stdout.decode('utf-8'))
            
            if not output_json.get('success', False):
                # Parse failed
                errors = output_json.get('errors', [])
                raise PLIxParseError(errors)
            
            # Convert to Python structures
            intent = self._convert_ast(output_json['intent'])
            
            # Cache result
            self._cache[intent_hash] = (intent, datetime.now())
            
            return intent
        
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Node.js not found at '{self.node_path}'. "
                "Please install Node.js: https://nodejs.org/"
            )
        
        except subprocess.TimeoutExpired:
            raise subprocess.TimeoutExpired(
                f"PLIx parser timeout after 30 seconds. "
                f"Intent may be too complex or parser hung.",
                30
            )
        
        except json.JSONDecodeError as e:
            raise PLIxParseError([{
                "line": 0,
                "column": 0,
                "message": f"Invalid JSON from parser: {e}",
                "code": "JSON_DECODE_ERROR"
            }])
    
    def _convert_ast(self, ast_json: Dict[str, Any]) -> PLIxIntent:
        """
        Convert JSON AST to Python PLIxIntent.
        
        Args:
            ast_json: JSON AST from TypeScript parser
            
        Returns:
            PLIxIntent: Python intent structure
        """
        return PLIxIntent(
            speech_act=ast_json.get('speechAct', 'ask'),
            entity=ast_json.get('entity', ''),
            action=ast_json.get('action', ''),
            contract=ast_json.get('contract', {}),
            plan=ast_json.get('plan', {}),
            evidence=ast_json.get('evidence', {}),
            metadata=ast_json.get('metadata', {})
        )
    
    def _hash_text(self, text: str) -> str:
        """Compute SHA-256 hash of text"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def clear_cache(self):
        """Clear parse cache"""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.now()
        valid_entries = sum(
            1 for _, (_, timestamp) in self._cache.items()
            if now - timestamp < self.cache_ttl
        )
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "stale_entries": len(self._cache) - valid_entries,
            "cache_ttl_seconds": self.cache_ttl.total_seconds()
        }


# Convenience function
def parse_plix(text: str) -> PLIxIntent:
    """
    Parse PLIx text (convenience function).
    
    Args:
        text: PLIx intent in CNL
        
    Returns:
        PLIxIntent: Parsed intent
        
    Example:
        from apoe.plix_compiler import parse_plix
        
        plix_text = '''
        ask ent:room/meeting
          act:reserve
          requires con:available == True
          ensures con:reserved == True
          plan []
        '''
        
        intent = parse_plix(plix_text)
        print(intent.entity)  # "room/meeting"
    """
    bridge = PLIxParserBridge()
    return bridge.parse(text)

