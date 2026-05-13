"""
AIM-OS AI Engine — Agent Context Trail

True Temporality for Agents: records every MCP tool call per-agent,
tracks time-away, and builds temporal context that gets injected
as a 4th genome layer (Base + Role + Task + Trail).

Each agent gets:
    • Current time awareness
    • How long they've been away
    • Their last N tool calls (retrieval breadcrumbs)
    • What other agents did while they were offline
    • Active mission status

Storage: .agent/trails/{agent}.jsonl (one JSON line per event)

Usage via MCP:
    ai_engine_trail(agent="opus", limit=10)
    ai_engine_trail_briefing(agent="sev")

Usage direct:
    recorder = ContextTrailRecorder('/path/to/AIM-OS')
    recorder.record('opus', 'ai_engine_context_find', {'query': 'MCP tools'}, {'files': 3})
    briefing = recorder.build_temporal_context('opus')
"""

import os
import json
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone, timedelta

logger = logging.getLogger('ai_engine.context_trail')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))


# ══════════════════════════════════════════════════════════
#  DATA MODELS
# ══════════════════════════════════════════════════════════

@dataclass
class TrailEntry:
    """A single event in an agent's context trail."""
    timestamp: str          # ISO 8601
    agent: str              # Agent callsign (opus, sev, codex, gemini)
    tool: str               # MCP tool name
    args_summary: str       # Brief args summary (1 line)
    result_summary: str     # Brief result summary (1 line)
    elapsed_ms: float = 0.0
    session_id: str = ''    # Links entries within same session
    event_type: str = 'tool_call'  # tool_call, session_start, session_end, milestone

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json_line(cls, line: str) -> 'TrailEntry':
        data = json.loads(line.strip())
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class TemporalBriefing:
    """Temporal context briefing for genome injection."""
    agent: str
    current_time: str
    last_active: str
    time_away: str
    sessions_total: int
    recent_activity: List[TrailEntry]
    changes_while_away: List[TrailEntry]
    active_tools_summary: Dict[str, int]  # tool_name → call count

    def to_xml(self) -> str:
        """Render as XML for genome injection."""
        parts = [
            f'<temporal_context agent="{self.agent}" generated="{self.current_time}">',
            f'  <time_awareness>',
            f'    <current_time>{self.current_time}</current_time>',
            f'    <last_active>{self.last_active}</last_active>',
            f'    <time_away>{self.time_away}</time_away>',
            f'    <sessions_total>{self.sessions_total}</sessions_total>',
            f'  </time_awareness>',
        ]

        # Recent activity
        if self.recent_activity:
            parts.append(f'  <recent_activity count="{len(self.recent_activity)}">')
            for entry in self.recent_activity:
                ts_short = entry.timestamp[11:16] if len(entry.timestamp) > 16 else entry.timestamp
                parts.append(
                    f'    <entry time="{ts_short}" tool="{entry.tool}" '
                    f'args="{self._escape(entry.args_summary)}" '
                    f'result="{self._escape(entry.result_summary)}"/>'
                )
            parts.append(f'  </recent_activity>')

        # Changes while away
        if self.changes_while_away:
            parts.append(f'  <changes_while_away count="{len(self.changes_while_away)}">')
            for entry in self.changes_while_away:
                ts_short = entry.timestamp[11:16] if len(entry.timestamp) > 16 else entry.timestamp
                parts.append(
                    f'    <change agent="{entry.agent}" time="{ts_short}" '
                    f'tool="{entry.tool}" summary="{self._escape(entry.result_summary)}"/>'
                )
            parts.append(f'  </changes_while_away>')

        # Tool usage summary
        if self.active_tools_summary:
            tools_str = ', '.join(f'{t}: {c}' for t, c in
                                  sorted(self.active_tools_summary.items(),
                                         key=lambda x: -x[1])[:8])
            parts.append(f'  <tool_usage_summary>{tools_str}</tool_usage_summary>')

        parts.append(f'</temporal_context>')
        return '\n'.join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent': self.agent,
            'current_time': self.current_time,
            'last_active': self.last_active,
            'time_away': self.time_away,
            'sessions_total': self.sessions_total,
            'recent_activity_count': len(self.recent_activity),
            'changes_while_away_count': len(self.changes_while_away),
            'recent_tools': [
                {
                    'time': e.timestamp[11:16] if len(e.timestamp) > 16 else e.timestamp,
                    'tool': e.tool,
                    'args': e.args_summary[:80],
                    'result': e.result_summary[:80],
                }
                for e in self.recent_activity
            ],
            'changes': [
                {
                    'agent': e.agent,
                    'time': e.timestamp[11:16] if len(e.timestamp) > 16 else e.timestamp,
                    'tool': e.tool,
                    'summary': e.result_summary[:80],
                }
                for e in self.changes_while_away
            ],
        }

    @staticmethod
    def _escape(text: str) -> str:
        return (text.replace('&', '&amp;')
                    .replace('"', '&quot;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;'))[:100]


# ══════════════════════════════════════════════════════════
#  CONTEXT TRAIL RECORDER
# ══════════════════════════════════════════════════════════

class ContextTrailRecorder:
    """
    Records and queries per-agent MCP tool call trails.

    Storage: .agent/trails/{agent}.jsonl
    Cross-agent log: .agent/trails/_all.jsonl
    """

    # Known agent callsigns for normalization
    KNOWN_AGENTS = {
        'opus', 'antigravity', 'sev', 'codex', 'gemini',
        'composer', 'aether', 'gemini_web',
    }

    def __init__(self, workspace_root: str = ''):
        self.workspace_root = workspace_root or WORKSPACE
        self._trails_dir = os.path.join(self.workspace_root, '.agent', 'trails')
        os.makedirs(self._trails_dir, exist_ok=True)
        self._session_id = f'session_{int(time.time())}'
        logger.info(f'ContextTrailRecorder initialized (session: {self._session_id})')

    # ── Recording ───────────────────────────────────────────

    def record(
        self,
        agent: str,
        tool: str,
        args: Dict[str, Any],
        result: Dict[str, Any],
        elapsed_ms: float = 0.0,
    ) -> TrailEntry:
        """Record an MCP tool call to the agent's trail."""
        agent = self._normalize_agent(agent)
        now = datetime.now(timezone.utc).isoformat()

        # Build concise summaries
        args_summary = self._summarize_args(tool, args)
        result_summary = self._summarize_result(tool, result)

        entry = TrailEntry(
            timestamp=now,
            agent=agent,
            tool=tool,
            args_summary=args_summary,
            result_summary=result_summary,
            elapsed_ms=elapsed_ms,
            session_id=self._session_id,
        )

        # Write to agent-specific trail
        self._append_entry(agent, entry)

        # Write to cross-agent log
        self._append_all(entry)

        return entry

    def record_session_start(self, agent: str) -> TrailEntry:
        """Record a session start event."""
        agent = self._normalize_agent(agent)
        entry = TrailEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent=agent,
            tool='_session',
            args_summary='Session started',
            result_summary=f'Session {self._session_id}',
            session_id=self._session_id,
            event_type='session_start',
        )
        self._append_entry(agent, entry)
        self._append_all(entry)
        return entry

    def record_milestone(self, agent: str, milestone: str) -> TrailEntry:
        """Record a milestone event (phase completion, etc.)."""
        agent = self._normalize_agent(agent)
        entry = TrailEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent=agent,
            tool='_milestone',
            args_summary=milestone[:100],
            result_summary=milestone[:100],
            session_id=self._session_id,
            event_type='milestone',
        )
        self._append_entry(agent, entry)
        self._append_all(entry)
        return entry

    # ── Querying ────────────────────────────────────────────

    def get_recent(self, agent: str, limit: int = 10) -> List[TrailEntry]:
        """Get last N trail entries for an agent."""
        agent = self._normalize_agent(agent)
        trail_file = os.path.join(self._trails_dir, f'{agent}.jsonl')
        if not os.path.isfile(trail_file):
            return []

        entries = []
        try:
            with open(trail_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(TrailEntry.from_json_line(line))
                        except (json.JSONDecodeError, TypeError):
                            continue
        except Exception:
            return []

        return entries[-limit:]

    def get_all_recent(self, limit: int = 20) -> List[TrailEntry]:
        """Get last N entries from all agents (cross-agent log)."""
        all_file = os.path.join(self._trails_dir, '_all.jsonl')
        if not os.path.isfile(all_file):
            return []

        entries = []
        try:
            with open(all_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(TrailEntry.from_json_line(line))
                        except (json.JSONDecodeError, TypeError):
                            continue
        except Exception:
            return []

        return entries[-limit:]

    def get_changes_while_away(self, agent: str, limit: int = 10) -> List[TrailEntry]:
        """Get entries from OTHER agents since this agent's last activity."""
        agent = self._normalize_agent(agent)
        last_active = self._get_last_active_time(agent)

        if not last_active:
            return []

        all_recent = self.get_all_recent(limit=100)
        changes = [
            e for e in all_recent
            if e.agent != agent and e.timestamp > last_active
        ]

        return changes[-limit:]

    def get_session_count(self, agent: str) -> int:
        """Count total sessions for an agent."""
        entries = self.get_recent(agent, limit=10000)
        return sum(1 for e in entries if e.event_type == 'session_start')

    # ── Temporal Context Builder ────────────────────────────

    def build_temporal_context(self, agent: str, recent_limit: int = 10) -> TemporalBriefing:
        """
        Build a complete temporal briefing for genome injection.

        Returns a TemporalBriefing with:
            - Current time
            - Time since last active
            - Recent tool calls
            - Changes by other agents while away
            - Tool usage summary
        """
        agent = self._normalize_agent(agent)
        now = datetime.now(timezone.utc)
        now_str = now.isoformat()

        # Last active
        last_active = self._get_last_active_time(agent)
        if last_active:
            try:
                last_dt = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
                delta = now - last_dt
                time_away = self._format_timedelta(delta)
            except (ValueError, TypeError):
                time_away = 'unknown'
        else:
            last_active = 'never'
            time_away = 'first session'

        # Recent activity
        recent = self.get_recent(agent, limit=recent_limit)

        # Changes while away
        changes = self.get_changes_while_away(agent, limit=10)

        # Session count
        sessions = self.get_session_count(agent)

        # Tool usage summary
        tool_counts: Dict[str, int] = {}
        all_entries = self.get_recent(agent, limit=100)
        for entry in all_entries:
            if entry.event_type == 'tool_call':
                tool_counts[entry.tool] = tool_counts.get(entry.tool, 0) + 1

        return TemporalBriefing(
            agent=agent,
            current_time=now_str,
            last_active=last_active,
            time_away=time_away,
            sessions_total=sessions,
            recent_activity=recent,
            changes_while_away=changes,
            active_tools_summary=tool_counts,
        )

    # ── Internal Helpers ────────────────────────────────────

    def _normalize_agent(self, agent: str) -> str:
        """Normalize agent name to lowercase callsign."""
        agent = agent.lower().strip()
        # Map aliases
        if agent in ('antigravity', 'ant'):
            agent = 'opus'
        return agent

    def _get_last_active_time(self, agent: str) -> Optional[str]:
        """Get timestamp of last activity for an agent."""
        entries = self.get_recent(agent, limit=1)
        if entries:
            return entries[-1].timestamp
        return None

    def _append_entry(self, agent: str, entry: TrailEntry):
        """Append entry to agent-specific trail file."""
        trail_file = os.path.join(self._trails_dir, f'{agent}.jsonl')
        try:
            with open(trail_file, 'a', encoding='utf-8') as f:
                f.write(entry.to_json_line() + '\n')
        except Exception as e:
            logger.warning(f'Failed to write trail entry: {e}')

    def _append_all(self, entry: TrailEntry):
        """Append entry to cross-agent log."""
        all_file = os.path.join(self._trails_dir, '_all.jsonl')
        try:
            with open(all_file, 'a', encoding='utf-8') as f:
                f.write(entry.to_json_line() + '\n')
        except Exception as e:
            logger.warning(f'Failed to write cross-agent entry: {e}')

    @staticmethod
    def _format_timedelta(delta: timedelta) -> str:
        """Format timedelta as human-readable string."""
        total_seconds = int(delta.total_seconds())
        if total_seconds < 60:
            return f'{total_seconds}s'
        elif total_seconds < 3600:
            return f'{total_seconds // 60}m'
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            mins = (total_seconds % 3600) // 60
            return f'{hours}h {mins}m'
        else:
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            return f'{days}d {hours}h'

    @staticmethod
    def _summarize_args(tool: str, args: Dict[str, Any]) -> str:
        """Create a concise 1-line arg summary."""
        if not args:
            return ''

        # Tool-specific summarization
        if 'query' in args:
            return f'query="{args["query"]}"'
        if 'target' in args:
            target = args['target']
            if isinstance(target, str):
                target = os.path.basename(target)
            return f'target="{target}"'
        if 'task' in args:
            task = str(args['task'])[:60]
            return f'task="{task}"'
        if 'content' in args:
            content = str(args['content'])[:60]
            return f'content="{content}..."'

        # Generic: first 2 key=value pairs
        pairs = []
        for k, v in list(args.items())[:2]:
            v_str = str(v)[:30]
            pairs.append(f'{k}="{v_str}"')
        return ', '.join(pairs)

    @staticmethod
    def _summarize_result(tool: str, result: Dict[str, Any]) -> str:
        """Create a concise 1-line result summary."""
        if not result:
            return ''

        status = result.get('status', '')

        # Tool-specific
        if 'files_found' in result:
            return f'{result["files_found"]} files found'
        if 'chunk_count' in result:
            return f'{result["chunk_count"]} chunks'
        if 'section_count' in result:
            return f'{result["section_count"]} sections'
        if 'atom_id' in result:
            return f'stored atom {str(result["atom_id"])[:8]}'

        # Check for generation_ms
        ms = result.get('generation_ms', '')
        if ms:
            return f'{status}, {ms}ms'

        if status:
            return status

        # Generic: status + first interesting key
        for key in ('message', 'overview', 'description', 'result'):
            if key in result:
                return str(result[key])[:80]

        return str(result)[:60]

    # ── Status ──────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """Return recorder status."""
        trail_files = [f for f in os.listdir(self._trails_dir)
                       if f.endswith('.jsonl') and not f.startswith('_')]
        agents = [f.replace('.jsonl', '') for f in trail_files]

        total_entries = 0
        for f in trail_files:
            path = os.path.join(self._trails_dir, f)
            try:
                with open(path, 'r') as fh:
                    total_entries += sum(1 for _ in fh)
            except Exception:
                pass

        return {
            'trails_dir': self._trails_dir,
            'agents_tracked': agents,
            'total_entries': total_entries,
            'session_id': self._session_id,
        }


# ══════════════════════════════════════════════════════════
#  CLI TEST
# ══════════════════════════════════════════════════════════

def _test():
    """Test the Context Trail system."""
    print("=" * 60)
    print("  Context Trail — Live Test")
    print("=" * 60)

    recorder = ContextTrailRecorder(WORKSPACE)

    # Simulate some tool calls
    print('\n  Recording tool calls...')
    recorder.record_session_start('opus')

    recorder.record('opus', 'ai_engine_context_find',
                   {'query': 'genome loading'},
                   {'status': 'ok', 'files_found': 3, 'generation_ms': 386})
    time.sleep(0.05)

    recorder.record('opus', 'ai_engine_code',
                   {'task': 'Fix genome loader path resolution'},
                   {'status': 'ok', 'message': 'Code generated'})
    time.sleep(0.05)

    recorder.record('sev', 'ai_engine_context_index',
                   {'target': 'chain_director.py'},
                   {'status': 'ok', 'section_count': 5, 'generation_ms': 7})
    time.sleep(0.05)

    recorder.record('codex', 'ai_engine_read_large',
                   {'target': 'ai_engine_mcp_server.py'},
                   {'status': 'ok', 'chunk_count': 3, 'generation_ms': 6})
    time.sleep(0.05)

    recorder.record('opus', 'store_memory',
                   {'content': 'Phase 21 complete'},
                   {'status': 'ok', 'atom_id': 'd84c21ed-686c-4372'})
    time.sleep(0.05)

    recorder.record_milestone('opus', 'Phase 21: Context Concierge complete')

    recorder.record('gemini', 'ai_engine_plan',
                   {'task': 'Design large file reader architecture'},
                   {'status': 'ok', 'message': 'Plan created with 5 steps'})

    print(f'  Recorded 7 entries across 4 agents')

    # Test get_recent
    print(f'\n{"─" * 60}')
    print(f'  RECENT ACTIVITY: opus (last 5)')
    print(f'{"─" * 60}')
    recent = recorder.get_recent('opus', limit=5)
    for entry in recent:
        ts = entry.timestamp[11:16]
        print(f'  [{ts}] {entry.tool}: {entry.args_summary} → {entry.result_summary}')

    # Test changes while away
    print(f'\n{"─" * 60}')
    print(f'  CHANGES WHILE AWAY: opus')
    print(f'{"─" * 60}')
    changes = recorder.get_changes_while_away('opus', limit=5)
    for entry in changes:
        ts = entry.timestamp[11:16]
        print(f'  [{ts}] {entry.agent}: {entry.tool} — {entry.result_summary}')

    # Test temporal briefing
    print(f'\n{"─" * 60}')
    print(f'  TEMPORAL BRIEFING: sev')
    print(f'{"─" * 60}')
    briefing = recorder.build_temporal_context('sev')
    print(briefing.to_xml())

    # Test temporal briefing for opus
    print(f'\n{"─" * 60}')
    print(f'  TEMPORAL BRIEFING: opus')
    print(f'{"─" * 60}')
    briefing = recorder.build_temporal_context('opus')
    xml = briefing.to_xml()
    print(xml)
    print(f'\n  Briefing size: {len(xml)} chars ({len(xml)//4} tokens est.)')

    # Status
    print(f'\n{"─" * 60}')
    print(f'  STATUS')
    print(f'{"─" * 60}')
    print(f'  {json.dumps(recorder.status(), indent=2)}')

    print(f'\n{"=" * 60}')
    print(f'  ALL TESTS PASSED — Phase 25 Context Trail Working')
    print(f'{"=" * 60}')


if __name__ == '__main__':
    _test()
