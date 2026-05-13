#!/usr/bin/env python3
"""HHNI Retrieval Performance Benchmark

Measures retrieval latency and relevance against KR-1-2 style targets:
- Retrieval latency target: p95 < 200ms
- Relevance target: mean relevance >= 90%

This benchmark is aligned to the current HHNI API:
- `HierarchicalIndex.index_document(...)`
- `TwoStageRetriever.retrieve(...)`
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

from hhni.hierarchical_index import HierarchicalIndex, IndexLevel
from hhni.retrieval import RetrievalConfig, TwoStageRetriever
from hhni.semantic_search import EmbeddingProvider


def create_test_corpus(size: int) -> List[Dict[str, str]]:
    """Create synthetic documents for retrieval benchmarking."""
    topics = [
        "machine learning",
        "neural networks",
        "ai safety",
        "consciousness",
        "memory systems",
        "context optimization",
        "retrieval algorithms",
        "semantic search",
        "embeddings",
        "knowledge graphs",
    ]
    docs: List[Dict[str, str]] = []
    for i in range(size):
        topic = topics[i % len(topics)]
        content = (
            f"Document {i} topic: {topic}. "
            f"This text describes {topic} concepts, techniques, and tradeoffs. "
            f"It includes repeated terms for retrieval quality measurement. "
            f"{topic} {topic} {topic}."
        )
        docs.append({"doc_id": f"doc_{i}", "topic": topic, "content": content})
    return docs


def build_index(corpus: List[Dict[str, str]]) -> HierarchicalIndex:
    """Build HHNI index from corpus."""
    index = HierarchicalIndex()
    for doc in corpus:
        index.index_document(
            content=doc["content"],
            doc_id=doc["doc_id"],
            metadata={"topic": doc["topic"]},
        )
    return index


def create_test_queries(count: int) -> List[Tuple[str, str]]:
    """Create queries paired with expected topic labels."""
    query_bank = [
        ("What is machine learning?", "machine learning"),
        ("How do neural networks work?", "neural networks"),
        ("Explain AI safety concerns", "ai safety"),
        ("What is consciousness research?", "consciousness"),
        ("How do memory systems operate?", "memory systems"),
        ("Optimize context retrieval", "context optimization"),
        ("Compare retrieval algorithms", "retrieval algorithms"),
        ("Semantic search techniques overview", "semantic search"),
        ("Embedding generation methods", "embeddings"),
        ("Knowledge graph construction", "knowledge graphs"),
    ]
    queries: List[Tuple[str, str]] = []
    while len(queries) < count:
        queries.extend(query_bank)
    return queries[:count]


def calculate_relevance(selected_items: List[Any], expected_topic: str) -> float:
    """Calculate precision-style relevance from selected paragraph nodes."""
    if not selected_items:
        return 0.0
    relevant = 0
    for item in selected_items:
        topic = (item.node.metadata or {}).get("topic", "")
        if str(topic).lower() == expected_topic:
            relevant += 1
    return relevant / len(selected_items)


def benchmark_retrieval(
    index: HierarchicalIndex,
    queries: List[Tuple[str, str]],
    config: RetrievalConfig,
    provider: EmbeddingProvider,
) -> Dict[str, Any]:
    """Run retrieval benchmark for one configuration."""
    retriever = TwoStageRetriever(index, config)

    print(f"\n{'=' * 60}")
    print("Benchmark: HHNI Retrieval Pipeline")
    print(f"Queries: {len(queries)}")
    print(f"Index nodes: {len(index.nodes)}")
    print(f"{'=' * 60}\n")

    latencies: List[float] = []
    relevances: List[float] = []
    tokens_used: List[int] = []

    for i, (query, expected_topic) in enumerate(queries, 1):
        start = time.perf_counter()
        result = retriever.retrieve(
            query,
            target_level=IndexLevel.PARAGRAPH,
            token_budget=config.token_budget,
            provider=provider,
        )
        latency_ms = (time.perf_counter() - start) * 1000.0
        latencies.append(latency_ms)

        relevances.append(calculate_relevance(result.selected_items, expected_topic))
        tokens_used.append(result.total_tokens)

        if i % 10 == 0 or i == len(queries):
            print(f"Progress: {i}/{len(queries)} queries")

    latencies_sorted = sorted(latencies)
    p50 = latencies_sorted[int(len(latencies_sorted) * 0.50)]
    p90 = latencies_sorted[int(len(latencies_sorted) * 0.90)]
    p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)]
    p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)]

    return {
        "queries": len(queries),
        "index_nodes": len(index.nodes),
        "mean_latency_ms": statistics.mean(latencies),
        "median_latency_ms": p50,
        "p90_latency_ms": p90,
        "p95_latency_ms": p95,
        "p99_latency_ms": p99,
        "min_latency_ms": min(latencies),
        "max_latency_ms": max(latencies),
        "mean_relevance": statistics.mean(relevances),
        "median_relevance": statistics.median(relevances),
        "min_relevance": min(relevances),
        "max_relevance": max(relevances),
        "mean_tokens": statistics.mean(tokens_used),
        "config": {
            "coarse_k": config.coarse_k,
            "token_budget": config.token_budget,
            "dvns_iterations": config.dvns_iterations,
            "enable_conflict_resolution": config.enable_conflict_resolution,
            "enable_compression": config.enable_compression,
        },
    }


def benchmark_ablation_study(
    index: HierarchicalIndex,
    queries: List[Tuple[str, str]],
    provider: EmbeddingProvider,
) -> Dict[str, Any]:
    """Run ablation profiles to measure feature impact."""
    print(f"\n{'=' * 60}")
    print("Ablation Study: Feature Impact on Performance")
    print(f"{'=' * 60}\n")

    configs: Dict[str, RetrievalConfig] = {
        "baseline": RetrievalConfig(
            enable_conflict_resolution=False,
            enable_compression=False,
            dvns_iterations=0,
        ),
        "with_dvns": RetrievalConfig(
            enable_conflict_resolution=False,
            enable_compression=False,
            dvns_iterations=50,
        ),
        "with_conflicts": RetrievalConfig(
            enable_conflict_resolution=True,
            enable_compression=False,
            dvns_iterations=50,
        ),
        "full_pipeline": RetrievalConfig(
            enable_conflict_resolution=True,
            enable_compression=True,
            dvns_iterations=50,
        ),
    }

    results: Dict[str, Any] = {}
    for name, cfg in configs.items():
        print(f"Testing configuration: {name}")
        results[name] = benchmark_retrieval(index, queries[:20], cfg, provider)
    return results


def print_results(results: Dict[str, Any], target_latency: float, target_relevance: float) -> None:
    """Print benchmark results and target validation."""
    print(f"\n{'=' * 60}")
    print("RETRIEVAL BENCHMARK RESULTS")
    print(f"{'=' * 60}\n")

    print(f"Index nodes: {results['index_nodes']}")
    print(f"Queries: {results['queries']}")
    print("\nLatency Statistics:")
    print(f"  Mean: {results['mean_latency_ms']:.2f}ms")
    print(f"  Median: {results['median_latency_ms']:.2f}ms")
    print(f"  p90: {results['p90_latency_ms']:.2f}ms")
    print(f"  p95: {results['p95_latency_ms']:.2f}ms")
    print(f"  p99: {results['p99_latency_ms']:.2f}ms")
    print(f"  Range: [{results['min_latency_ms']:.2f}, {results['max_latency_ms']:.2f}]ms")

    print("\nRelevance Statistics:")
    print(f"  Mean: {results['mean_relevance']:.3f} ({results['mean_relevance'] * 100:.1f}%)")
    print(f"  Median: {results['median_relevance']:.3f}")
    print(f"  Range: [{results['min_relevance']:.3f}, {results['max_relevance']:.3f}]")

    print("\nToken Usage:")
    print(f"  Mean: {results['mean_tokens']:.0f} tokens")

    print(f"\n{'=' * 60}")
    print("TARGET VALIDATION")
    print(f"{'=' * 60}\n")

    latency_pass = results["p95_latency_ms"] < target_latency
    relevance_pass = results["mean_relevance"] >= target_relevance

    print(f"{'[PASS]' if latency_pass else '[FAIL]'} Retrieval p95 < {target_latency}ms: {results['p95_latency_ms']:.2f}ms")
    print(f"{'[PASS]' if relevance_pass else '[FAIL]'} Mean relevance >= {target_relevance * 100:.0f}%: {results['mean_relevance'] * 100:.1f}%")
    if latency_pass and relevance_pass:
        print("\n[OK] Targets achieved")
    else:
        print("\n[WARN] Targets not achieved")


def print_ablation_results(results: Dict[str, Any]) -> None:
    """Print concise ablation table."""
    print(f"\n{'=' * 60}")
    print("ABLATION STUDY RESULTS")
    print(f"{'=' * 60}\n")

    print(f"{'Configuration':<20} {'p95 latency':<15} {'Mean relevance':<15} {'Delta latency':<15} {'Delta relevance'}")
    print(f"{'-' * 90}")

    baseline_latency = results["baseline"]["p95_latency_ms"]
    baseline_relevance = results["baseline"]["mean_relevance"]

    for name, data in results.items():
        lat = data["p95_latency_ms"]
        rel = data["mean_relevance"]
        d_lat = lat - baseline_latency
        d_rel = rel - baseline_relevance
        d_lat_s = f"{d_lat:+.2f}ms" if name != "baseline" else "baseline"
        d_rel_s = f"{d_rel:+.3f}" if name != "baseline" else "baseline"
        print(f"{name:<20} {lat:<15.2f} {rel:<15.3f} {d_lat_s:<15} {d_rel_s}")


def main() -> int:
    parser = argparse.ArgumentParser(description="HHNI Retrieval Benchmark")
    parser.add_argument("--queries", type=int, default=100, help="Number of queries")
    parser.add_argument("--corpus", type=int, default=1000, help="Number of documents to index")
    parser.add_argument("--coarse-k", type=int, default=20, help="Coarse retrieval candidate count.")
    parser.add_argument("--dvns-iterations", type=int, default=10, help="DVNS optimization iterations.")
    parser.add_argument("--token-budget", type=int, default=2000, help="Token budget for retrieval result selection.")
    parser.add_argument(
        "--provider",
        choices=["fallback", "local"],
        default="fallback",
        help="Embedding provider for retrieval benchmark.",
    )
    parser.add_argument("--ablation", action="store_true", help="Run ablation study")
    parser.add_argument("--output", type=str, default="", help="Write benchmark JSON output")
    args = parser.parse_args()

    print("\nHHNI Retrieval Performance Benchmark")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print(f"Queries: {args.queries}")
    print(f"Corpus: {args.corpus}")
    print(f"Provider: {args.provider}")
    print(f"Coarse-k: {args.coarse_k}")
    print(f"DVNS iterations: {args.dvns_iterations}")
    print(f"Token budget: {args.token_budget}")

    corpus = create_test_corpus(args.corpus)
    index = build_index(corpus)
    queries = create_test_queries(args.queries)

    config = RetrievalConfig(
        coarse_k=args.coarse_k,
        token_budget=args.token_budget,
        dvns_iterations=args.dvns_iterations,
        enable_conflict_resolution=True,
        enable_compression=True,
    )
    provider = EmbeddingProvider.FALLBACK if args.provider == "fallback" else EmbeddingProvider.LOCAL

    target_latency = 200.0
    target_relevance = 0.90

    results = benchmark_retrieval(index, queries, config, provider)
    print_results(results, target_latency, target_relevance)

    ablation_results: Dict[str, Any] | None = None
    if args.ablation:
        ablation_results = benchmark_ablation_study(index, queries, provider)
        print_ablation_results(ablation_results)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config": {
                "queries": args.queries,
                "corpus": args.corpus,
                "provider": args.provider,
                "coarse_k": args.coarse_k,
                "dvns_iterations": args.dvns_iterations,
                "token_budget": args.token_budget,
            },
            "results": results,
            "targets": {"p95_latency_ms": target_latency, "mean_relevance": target_relevance},
            "ablation": ablation_results,
        }
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"\nResults saved to: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
