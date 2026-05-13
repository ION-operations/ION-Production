"""
AIM-OS AI Engine — Session Manager

Wave 5b: Manages Gemini CLI sessions for context carry-over.

Features:
    - Session creation and tracking
    - Context serialisation between sessions
    - Session history for continuity
    - Session pooling for swarm workers
    - Timeout and cleanup management
"""

import os
import time
import uuid
import json
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger('ai_engine.session_manager')


class SessionState(str, Enum):
    CREATED = 'created'
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    FAILED = 'failed'
    EXPIRED = 'expired'


@dataclass
class SessionContext:
    """Serialisable context for session continuity."""
    task_description: str = ''
    agent_role: str = ''
    model_used: str = ''
    files_touched: List[str] = field(default_factory=list)
    conversation_summary: str = ''
    decisions_made: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)

    def to_prompt(self) -> str:
        """Serialise context into a prompt for session resume."""
        parts = [f"# Previous Session Context"]
        if self.task_description:
            parts.append(f"**Task:** {self.task_description}")
        if self.agent_role:
            parts.append(f"**Role:** {self.agent_role}")
        if self.conversation_summary:
            parts.append(f"\n## Summary\n{self.conversation_summary}")
        if self.files_touched:
            parts.append(f"\n## Files Worked On\n" + '\n'.join(f'- {f}' for f in self.files_touched[:10]))
        if self.decisions_made:
            parts.append(f"\n## Decisions\n" + '\n'.join(f'- {d}' for d in self.decisions_made[:5]))
        if self.open_questions:
            parts.append(f"\n## Open Questions\n" + '\n'.join(f'- {q}' for q in self.open_questions[:5]))
        return '\n'.join(parts)


@dataclass
class Session:
    """A single AI Engine session."""
    session_id: str = field(default_factory=lambda: f'sess_{uuid.uuid4().hex[:10]}')
    parent_session_id: str = ''

    # Identity
    agent_id: str = ''
    worker_id: str = ''
    job_id: str = ''

    # State
    state: str = SessionState.CREATED
    context: SessionContext = field(default_factory=SessionContext)

    # Timing
    created_at: float = field(default_factory=time.time)
    started_at: float = 0.0
    completed_at: float = 0.0
    ttl_seconds: int = 300

    # Metrics
    prompts_sent: int = 0
    tokens_in: int = 0
    tokens_out: int = 0

    @property
    def duration_ms(self) -> float:
        end = self.completed_at or time.time()
        start = self.started_at or self.created_at
        return (end - start) * 1000

    @property
    def is_expired(self) -> bool:
        if self.state in (SessionState.COMPLETED, SessionState.FAILED):
            return True
        return time.time() - self.created_at > self.ttl_seconds


class SessionManager:
    """
    Manages sessions for the AI Engine swarm.
    
    Key responsibilities:
        - Track all active sessions
        - Pool sessions for worker reuse
        - Serialise/restore context between sessions
        - Enforce session limits and cleanup expired sessions
    
    Usage:
        mgr = SessionManager()
        session = mgr.create(agent_id='coder_v1', job_id='job_abc')
        mgr.activate(session.session_id)
        mgr.update_context(session.session_id, context)
        mgr.complete(session.session_id)
    """

    MAX_ACTIVE_SESSIONS = 10

    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._session_history: List[str] = []

    def create(
        self,
        agent_id: str = '',
        worker_id: str = '',
        job_id: str = '',
        parent_session_id: str = '',
        ttl_seconds: int = 300,
    ) -> Session:
        """Create a new session."""
        self._cleanup_expired()

        session = Session(
            agent_id=agent_id,
            worker_id=worker_id,
            job_id=job_id,
            parent_session_id=parent_session_id,
            ttl_seconds=ttl_seconds,
        )

        # Inherit context from parent
        if parent_session_id and parent_session_id in self._sessions:
            parent = self._sessions[parent_session_id]
            session.context = SessionContext(
                task_description=parent.context.task_description,
                agent_role=parent.context.agent_role,
                conversation_summary=parent.context.conversation_summary,
            )

        self._sessions[session.session_id] = session
        logger.info(f'[SessionMgr] Created {session.session_id} (agent={agent_id}, job={job_id})')
        return session

    def activate(self, session_id: str) -> bool:
        """Activate a session (mark as started)."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.state = SessionState.ACTIVE
        session.started_at = time.time()
        return True

    def update_context(self, session_id: str, context: SessionContext) -> bool:
        """Update session context."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.context = context
        return True

    def complete(self, session_id: str, summary: str = '') -> bool:
        """Mark a session as completed."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.state = SessionState.COMPLETED
        session.completed_at = time.time()
        if summary:
            session.context.conversation_summary = summary

        self._session_history.append(session_id)
        if len(self._session_history) > 200:
            self._session_history = self._session_history[-200:]

        logger.info(f'[SessionMgr] Completed {session_id} ({session.duration_ms:.0f}ms)')
        return True

    def fail(self, session_id: str, reason: str = '') -> bool:
        """Mark a session as failed."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.state = SessionState.FAILED
        session.completed_at = time.time()
        if reason:
            session.context.open_questions.append(f'FAILURE: {reason}')
        return True

    def get(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def get_active(self) -> List[Session]:
        """Get all active sessions."""
        return [s for s in self._sessions.values() if s.state == SessionState.ACTIVE]

    def _cleanup_expired(self):
        """Remove expired sessions."""
        expired = [sid for sid, s in self._sessions.items() if s.is_expired]
        for sid in expired:
            self._sessions[sid].state = SessionState.EXPIRED
            self._session_history.append(sid)

        # Hard cleanup if too many
        if len(self._sessions) > self.MAX_ACTIVE_SESSIONS * 3:
            active = {sid: s for sid, s in self._sessions.items()
                     if s.state in (SessionState.CREATED, SessionState.ACTIVE)}
            self._sessions = active

    def status(self) -> dict:
        self._cleanup_expired()
        states = {}
        for s in self._sessions.values():
            states[s.state] = states.get(s.state, 0) + 1

        return {
            'total_sessions': len(self._sessions),
            'states': states,
            'history_length': len(self._session_history),
            'max_active': self.MAX_ACTIVE_SESSIONS,
        }
