"""Timeline Context System (TCS)

Tracks context across prompts, sessions, and time. Provides timeline entries,
context capacity monitoring, and prompt-level context tracking.

Key modules:
- timeline_api: Core timeline API
- prompt_context_tracker: Tracks context per prompt
- context_capacity_monitor: Monitors context budget usage
- goal_timeline_manager: Goal tracking over time
- enhanced_timeline_tracker: Enhanced tracking with rich metadata
"""

__version__ = "0.1.0"
