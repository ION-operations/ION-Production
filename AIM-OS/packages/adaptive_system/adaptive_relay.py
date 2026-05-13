"""
Adaptive Relay -- Distributed Signal Relay via MCP Bridge

Enables cross-machine adaptive sensing:
    - Push signals from local machine to remote daemon
    - Pull pending proposals from remote machines
    - Sync calibration data between machines
    - Aggregate multi-machine health dashboards

Communication uses the MCP SSE transport (Port 5001) already deployed.

Usage:
    # Push local signals to Ghost machine
    python -m packages.adaptive_system relay push --target http://ghost:5001
    
    # Pull proposals from Ghost
    python -m packages.adaptive_system relay pull --source http://ghost:5001
    
    # Sync calibration between machines
    python -m packages.adaptive_system relay sync --remote http://ghost:5001
    
    # Show multi-machine status
    python -m packages.adaptive_system relay status
"""

import json
import logging
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("adaptive_relay")


# ---------------------------------------------------------------
# Relay Configuration
# ---------------------------------------------------------------

class RelayConfig:
    """Configuration for multi-machine relay."""
    
    DEFAULT_PORT = 5001
    
    def __init__(
        self,
        local_name: str = "windows",
        peers: Optional[List[dict]] = None,
        config_path: Optional[Path] = None,
    ):
        self.local_name = local_name
        self.config_path = config_path or (
            Path.cwd() / ".agent" / "adaptive" / "relay_config.json"
        )
        self.peers = peers or self._load_peers()
    
    def _load_peers(self) -> List[dict]:
        """Load peer configuration."""
        if self.config_path.exists():
            try:
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                return data.get("peers", [])
            except (json.JSONDecodeError, OSError):
                pass
        
        # Default: Ghost machine
        return [
            {
                "name": "ghost",
                "url": "http://ghost:5001",
                "description": "Ghost Linux Machine",
                "active": True,
            }
        ]
    
    def save(self):
        """Save relay config."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps({
                "local_name": self.local_name,
                "peers": self.peers,
                "updated_at": datetime.now().isoformat(),
            }, indent=2),
            encoding="utf-8",
        )
    
    def add_peer(self, name: str, url: str, description: str = ""):
        """Add a peer machine."""
        self.peers.append({
            "name": name,
            "url": url.rstrip("/"),
            "description": description,
            "active": True,
        })
        self.save()
    
    def get_active_peers(self) -> List[dict]:
        return [p for p in self.peers if p.get("active", True)]


# ---------------------------------------------------------------
# MCP Bridge Transport
# ---------------------------------------------------------------

class MCPBridgeTransport:
    """HTTP transport for MCP bridge communication."""
    
    TIMEOUT_SECONDS = 30
    
    def post(self, url: str, data: dict) -> dict:
        """Send data to a remote MCP endpoint."""
        try:
            payload = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.TIMEOUT_SECONDS) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            logger.error(f"[relay] Connection failed to {url}: {e}")
            return {"error": str(e), "success": False}
        except Exception as e:
            logger.error(f"[relay] Transport error: {e}")
            return {"error": str(e), "success": False}
    
    def get(self, url: str) -> dict:
        """Get data from a remote MCP endpoint."""
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=self.TIMEOUT_SECONDS) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            logger.error(f"[relay] Connection failed to {url}: {e}")
            return {"error": str(e), "success": False}
        except Exception as e:
            logger.error(f"[relay] Transport error: {e}")
            return {"error": str(e), "success": False}
    
    def ping(self, url: str) -> bool:
        """Check if remote endpoint is reachable."""
        try:
            req = urllib.request.Request(f"{url}/health", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False


# ---------------------------------------------------------------
# Signal Relay
# ---------------------------------------------------------------

class SignalRelay:
    """Relays signals between adaptive daemons on different machines."""
    
    def __init__(self, config: Optional[RelayConfig] = None):
        self.config = config or RelayConfig()
        self.transport = MCPBridgeTransport()
        self.relay_log_path = (
            Path.cwd() / ".agent" / "adaptive" / "relay_log.json"
        )
    
    def _log_relay(self, action: str, peer: str, result: dict):
        """Log relay operations for auditing."""
        log = []
        if self.relay_log_path.exists():
            try:
                log = json.loads(self.relay_log_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                log = []
        
        log.append({
            "action": action,
            "peer": peer,
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "details": {k: v for k, v in result.items() if k != "data"},
        })
        
        # Keep last 200 entries
        if len(log) > 200:
            log = log[-200:]
        
        self.relay_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.relay_log_path.write_text(
            json.dumps(log, indent=2, default=str),
            encoding="utf-8",
        )
    
    # ── Push ──
    
    def push_signals(self, target_url: str) -> dict:
        """Push local signals to a remote daemon.
        
        Reads local tracker data and pushes recent signals.
        """
        storage = Path.cwd() / ".agent" / "adaptive"
        signals = []
        
        # Collect recent signals from tracker files
        for tracker_file in storage.glob("*.json"):
            if tracker_file.stem in ("daemon_state", "calibration", "relay_config", "relay_log"):
                continue
            try:
                data = json.loads(tracker_file.read_text(encoding="utf-8"))
                entries = data.get("entries", [])
                for entry in entries[-10:]:  # Last 10 per tracker
                    signal = entry.get("signal", {})
                    signal["source_machine"] = self.config.local_name
                    signal["tracker"] = tracker_file.stem
                    signals.append(signal)
            except (json.JSONDecodeError, OSError):
                continue
        
        if not signals:
            result = {"success": True, "pushed": 0, "message": "No signals to push"}
            self._log_relay("push_signals", target_url, result)
            return result
        
        # Push to remote
        endpoint = f"{target_url}/adaptive/signals"
        response = self.transport.post(endpoint, {
            "source": self.config.local_name,
            "signals": signals,
            "timestamp": datetime.now().isoformat(),
        })
        
        result = {
            "success": not response.get("error"),
            "pushed": len(signals),
            "target": target_url,
            "response": response,
        }
        self._log_relay("push_signals", target_url, result)
        return result
    
    # ── Pull ──
    
    def pull_proposals(self, source_url: str) -> dict:
        """Pull pending proposals from a remote daemon."""
        endpoint = f"{source_url}/adaptive/proposals"
        response = self.transport.get(endpoint)
        
        if response.get("error"):
            result = {"success": False, "error": response["error"]}
            self._log_relay("pull_proposals", source_url, result)
            return result
        
        proposals = response.get("proposals", [])
        
        # Save remote proposals locally (for review)
        if proposals:
            remote_dir = Path.cwd() / ".agent" / "adaptive" / "remote_proposals"
            remote_dir.mkdir(parents=True, exist_ok=True)
            
            for p in proposals:
                p_id = p.get("proposal_id", f"remote_{datetime.now().strftime('%H%M%S')}")
                p["source_machine"] = source_url
                (remote_dir / f"{p_id}.json").write_text(
                    json.dumps(p, indent=2, default=str),
                    encoding="utf-8",
                )
        
        result = {
            "success": True,
            "pulled": len(proposals),
            "source": source_url,
        }
        self._log_relay("pull_proposals", source_url, result)
        return result
    
    # ── Sync Calibration ──
    
    def sync_calibration(self, remote_url: str) -> dict:
        """Sync calibration data between machines.
        
        Strategy: merge calibration, keeping the more experienced data.
        """
        # Read local calibration
        from .adaptive_learner import AdaptiveLearner
        local_learner = AdaptiveLearner()
        local_cal = local_learner.state.data
        
        # Get remote calibration
        endpoint = f"{remote_url}/adaptive/calibration"
        remote_cal = self.transport.get(endpoint)
        
        if remote_cal.get("error"):
            result = {"success": False, "error": remote_cal["error"]}
            self._log_relay("sync_calibration", remote_url, result)
            return result
        
        # Merge: for each system, keep the one with more outcomes
        merged_count = 0
        remote_systems = remote_cal.get("systems", {})
        local_systems = local_cal.get("systems", {})
        
        for name, remote_sys in remote_systems.items():
            local_sys = local_systems.get(name, {})
            remote_total = remote_sys.get("total_proposals", 0)
            local_total = local_sys.get("total_proposals", 0)
            
            if remote_total > local_total:
                # Remote has more experience -- adopt their calibration
                local_cal.setdefault("systems", {})[name] = remote_sys
                merged_count += 1
            
            # Merge suppressed domains (union)
            remote_suppressed = set(remote_sys.get("suppressed_domains", []))
            local_suppressed = set(local_sys.get("suppressed_domains", []))
            merged_suppressed = list(remote_suppressed | local_suppressed)
            
            if name in local_cal.get("systems", {}):
                local_cal["systems"][name]["suppressed_domains"] = merged_suppressed
        
        # Save merged calibration
        local_learner.state.data = local_cal
        local_learner.state.save()
        
        # Push merged calibration back to remote
        self.transport.post(
            f"{remote_url}/adaptive/calibration",
            local_cal,
        )
        
        result = {
            "success": True,
            "merged_systems": merged_count,
            "remote_url": remote_url,
        }
        self._log_relay("sync_calibration", remote_url, result)
        return result
    
    # ── Push to All Peers ──
    
    def push_to_all(self) -> Dict[str, dict]:
        """Push signals to all active peers."""
        results = {}
        for peer in self.config.get_active_peers():
            results[peer["name"]] = self.push_signals(peer["url"])
        return results
    
    def pull_from_all(self) -> Dict[str, dict]:
        """Pull proposals from all active peers."""
        results = {}
        for peer in self.config.get_active_peers():
            results[peer["name"]] = self.pull_proposals(peer["url"])
        return results
    
    def sync_all(self) -> Dict[str, dict]:
        """Sync calibration with all active peers."""
        results = {}
        for peer in self.config.get_active_peers():
            results[peer["name"]] = self.sync_calibration(peer["url"])
        return results
    
    # ── Status ──
    
    def get_status(self) -> dict:
        """Get multi-machine relay status."""
        peers_status = []
        for peer in self.config.peers:
            reachable = self.transport.ping(peer["url"])
            peers_status.append({
                "name": peer["name"],
                "url": peer["url"],
                "active": peer.get("active", True),
                "reachable": reachable,
                "description": peer.get("description", ""),
            })
        
        # Recent relay log
        recent_ops = []
        if self.relay_log_path.exists():
            try:
                log = json.loads(self.relay_log_path.read_text(encoding="utf-8"))
                recent_ops = log[-10:]  # Last 10 operations
            except (json.JSONDecodeError, OSError):
                pass
        
        return {
            "local_machine": self.config.local_name,
            "peers": peers_status,
            "recent_operations": len(recent_ops),
            "last_relay": recent_ops[-1] if recent_ops else None,
        }
