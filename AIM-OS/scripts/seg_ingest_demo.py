import json
import sys
import os

# Ensure 'packages' is on sys.path to import 'seg' package
repo_root = os.path.dirname(os.path.abspath(__file__))
packages_dir = os.path.join(os.path.dirname(repo_root), "packages")
if packages_dir not in sys.path:
    sys.path.insert(0, packages_dir)

from seg.tcs_integration import ingest_timeline_entry
from seg.seg_graph import SEGraph


def main():
    timeline_entry = {
        "prompt_id": "R-EXEC-NEXUS-002",
        "summary": "Ingest test from Atlas execution request",
        "timestamp": "2025-01-27T12:00:00Z",
        "confidence_metrics": {"average_confidence": 0.87},
        "context_index": {
            "active_tasks": ["seg_ingest_test"],
            "files_read": ["file://example"],
            "insights_gained": ["ingest path ok"],
        },
    }
    graph = SEGraph()
    result = ingest_timeline_entry(
        timeline_entry=timeline_entry,
        atom_id="atom_test_123",
        witness_id=None,
        graph=graph,
    )
    print(json.dumps(result))


if __name__ == "__main__":
    main()

