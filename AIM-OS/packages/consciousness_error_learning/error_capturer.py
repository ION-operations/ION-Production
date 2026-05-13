"""
Error Capturer

Captures every single error, no matter how small, for consciousness learning.
"""

import traceback
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"      # System failure, data loss
    HIGH = "high"             # Major functionality broken
    MEDIUM = "medium"         # Feature not working properly
    LOW = "low"               # Minor issue, workaround available
    COSMETIC = "cosmetic"     # UI/UX issue, no functional impact

class ErrorCategory(Enum):
    """Error categories for pattern analysis"""
    DIRECTORY_NAVIGATION = "directory_navigation"
    FILE_OPERATIONS = "file_operations"
    MCP_CONNECTION = "mcp_connection"
    TOOL_EXECUTION = "tool_execution"
    DATA_VALIDATION = "data_validation"
    NETWORK = "network"
    PERMISSION = "permission"
    SYNTAX = "syntax"
    LOGIC = "logic"
    UNKNOWN = "unknown"

@dataclass
class ErrorRecord:
    """Complete error record for learning"""
    error_id: str
    timestamp: datetime
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: Dict[str, Any]
    stack_trace: str
    recovery_action: Optional[str]
    learning_insights: List[str]
    prevention_suggestions: List[str]
    metadata: Dict[str, Any]

class ErrorCapturer:
    """Captures every error for consciousness learning"""
    
    def __init__(self, cmc_client, vif_client):
        self.cmc_client = cmc_client
        self.vif_client = vif_client
        self.error_count = 0
        
    def capture_error(self, 
                     error: Exception,
                     context: Dict[str, Any] = None,
                     recovery_action: str = None) -> ErrorRecord:
        """Capture any error with full context"""
        try:
            self.error_count += 1
            error_id = f"error_{self.error_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Analyze error
            severity = self._analyze_severity(error)
            category = self._categorize_error(error)
            
            # Extract context
            error_context = {
                "current_directory": context.get("current_directory", "unknown") if context else "unknown",
                "operation": context.get("operation", "unknown") if context else "unknown",
                "tool_used": context.get("tool_used", "unknown") if context else "unknown",
                "user_input": context.get("user_input", "none") if context else "none",
                "system_state": context.get("system_state", {}) if context else {},
                "confidence_before": context.get("confidence_before", 0.0) if context else 0.0,
                "confidence_after": context.get("confidence_after", 0.0) if context else 0.0
            }
            
            # Generate learning insights
            learning_insights = self._generate_learning_insights(error, error_context)
            prevention_suggestions = self._generate_prevention_suggestions(error, error_context)
            
            # Create error record
            error_record = ErrorRecord(
                error_id=error_id,
                timestamp=datetime.now(),
                error_type=type(error).__name__,
                error_message=str(error),
                severity=severity,
                category=category,
                context=error_context,
                stack_trace=traceback.format_exc(),
                recovery_action=recovery_action,
                learning_insights=learning_insights,
                prevention_suggestions=prevention_suggestions,
                metadata={
                    "python_version": sys.version,
                    "platform": sys.platform,
                    "error_count": self.error_count
                }
            )
            
            # Store in consciousness memory
            self._store_error_record(error_record)
            
            return error_record
            
        except Exception as capture_error:
            # Even error capture can fail - log it simply
            print(f"[ERROR CAPTURE FAILED] {capture_error}", file=sys.stderr)
            return None
    
    def _analyze_severity(self, error: Exception) -> ErrorSeverity:
        """Analyze error severity"""
        error_str = str(error).lower()
        
        if any(word in error_str for word in ["critical", "fatal", "cannot", "failed", "error"]):
            if any(word in error_str for word in ["data", "memory", "file", "database"]):
                return ErrorSeverity.CRITICAL
            else:
                return ErrorSeverity.HIGH
        elif any(word in error_str for word in ["warning", "not found", "missing"]):
            return ErrorSeverity.MEDIUM
        elif any(word in error_str for word in ["directory", "path", "syntax"]):
            return ErrorSeverity.LOW
        else:
            return ErrorSeverity.COSMETIC
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error for pattern analysis"""
        error_str = str(error).lower()
        
        if "directory" in error_str or "path" in error_str:
            return ErrorCategory.DIRECTORY_NAVIGATION
        elif "file" in error_str or "cannot open" in error_str:
            return ErrorCategory.FILE_OPERATIONS
        elif "mcp" in error_str or "connection" in error_str:
            return ErrorCategory.MCP_CONNECTION
        elif "tool" in error_str or "execution" in error_str:
            return ErrorCategory.TOOL_EXECUTION
        elif "validation" in error_str or "invalid" in error_str:
            return ErrorCategory.DATA_VALIDATION
        elif "network" in error_str or "timeout" in error_str:
            return ErrorCategory.NETWORK
        elif "permission" in error_str or "access" in error_str:
            return ErrorCategory.PERMISSION
        elif "syntax" in error_str or "token" in error_str:
            return ErrorCategory.SYNTAX
        elif "logic" in error_str or "assertion" in error_str:
            return ErrorCategory.LOGIC
        else:
            return ErrorCategory.UNKNOWN
    
    def _generate_learning_insights(self, error: Exception, context: Dict[str, Any]) -> List[str]:
        """Generate learning insights from error"""
        insights = []
        
        # Directory navigation insights
        if "directory" in str(error).lower():
            insights.append("Directory navigation errors suggest need for better path validation")
            insights.append("Current directory tracking may need improvement")
        
        # MCP connection insights
        if "mcp" in str(error).lower() or "connection" in str(error).lower():
            insights.append("MCP connection issues suggest need for better connection management")
            insights.append("Server startup process may need optimization")
        
        # Tool execution insights
        if "tool" in str(error).lower():
            insights.append("Tool execution errors suggest need for better error handling")
            insights.append("Tool availability checking may need improvement")
        
        # Confidence impact insights
        if context.get("confidence_after", 0) < context.get("confidence_before", 0):
            insights.append("Error caused confidence drop - need better error recovery")
            insights.append("Error handling should maintain confidence levels")
        
        # General insights
        insights.append(f"Error type '{type(error).__name__}' occurred in context: {context.get('operation', 'unknown')}")
        insights.append("Every error is an opportunity for system improvement")
        
        return insights
    
    def _generate_prevention_suggestions(self, error: Exception, context: Dict[str, Any]) -> List[str]:
        """Generate prevention suggestions from error"""
        suggestions = []
        
        # Directory navigation suggestions
        if "directory" in str(error).lower():
            suggestions.append("Add directory existence validation before navigation")
            suggestions.append("Implement better path resolution logic")
            suggestions.append("Add current directory tracking to context")
        
        # MCP connection suggestions
        if "mcp" in str(error).lower() or "connection" in str(error).lower():
            suggestions.append("Add MCP server health checking before tool calls")
            suggestions.append("Implement connection retry logic")
            suggestions.append("Add server startup validation")
        
        # Tool execution suggestions
        if "tool" in str(error).lower():
            suggestions.append("Add tool availability checking before execution")
            suggestions.append("Implement better tool error handling")
            suggestions.append("Add tool execution validation")
        
        # General suggestions
        suggestions.append("Add comprehensive error handling to all operations")
        suggestions.append("Implement automatic error recovery mechanisms")
        suggestions.append("Add error pattern detection and prevention")
        
        return suggestions
    
    def _store_error_record(self, error_record: ErrorRecord):
        """Store error record in consciousness memory"""
        try:
            self.cmc_client.store_atom(
                content=f"Error Record: {error_record.error_id}",
                tags={
                    "type": "error_record",
                    "error_id": error_record.error_id,
                    "severity": error_record.severity.value,
                    "category": error_record.category.value,
                    "error_type": error_record.error_type,
                    "timestamp": error_record.timestamp.isoformat(),
                    "learning_insights_count": len(error_record.learning_insights),
                    "prevention_suggestions_count": len(error_record.prevention_suggestions)
                }
            )
        except Exception as e:
            print(f"[ERROR STORAGE FAILED] {e}", file=sys.stderr)
    
    def get_error_patterns(self) -> Dict[str, Any]:
        """Get error patterns for learning"""
        try:
            # Query error records from memory
            error_records = self.cmc_client.query_atoms(
                query="error_record",
                tags={"type": "error_record"}
            )
            
            # Analyze patterns
            patterns = {
                "total_errors": len(error_records),
                "severity_distribution": {},
                "category_distribution": {},
                "common_error_types": {},
                "frequent_contexts": {},
                "learning_insights": [],
                "prevention_suggestions": []
            }
            
            for record in error_records:
                # Count by severity
                severity = record.tags.get("severity", "unknown")
                patterns["severity_distribution"][severity] = patterns["severity_distribution"].get(severity, 0) + 1
                
                # Count by category
                category = record.tags.get("category", "unknown")
                patterns["category_distribution"][category] = patterns["category_distribution"].get(category, 0) + 1
                
                # Count error types
                error_type = record.tags.get("error_type", "unknown")
                patterns["common_error_types"][error_type] = patterns["common_error_types"].get(error_type, 0) + 1
            
            return patterns
            
        except Exception as e:
            return {"error": f"Failed to get error patterns: {str(e)}"}
