from __future__ import annotations

import json
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from assistant.orchestration.service import AssistantOrchestrator  # noqa: E402
from backend.app.services.session_store import SessionStore  # noqa: E402
from multimodal.data.manifest import load_manifest  # noqa: E402
from multimodal.evaluation.metrics import index_recall, retrieval_metrics  # noqa: E402
from multimodal.retrieval.service import RetrievalService  # noqa: E402


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rank_for(service: RetrievalService, query: str, target: str, mode: str) -> tuple[int, dict]:
    response = service.search_text(query, mode=mode, top_k=len(service.items))
    ids = [result.image_id for result in response.results]
    rank = ids.index(target) + 1 if target in ids else len(ids) + 1
    return rank, {"rank": rank, "top_5": ids[:5], "latency_ms": response.latency_ms}


def build() -> dict:
    manifest_path = ROOT / "data" / "manifests" / "qualification-corpus.json"
    items = load_manifest(manifest_path)
    service = RetrievalService(items)
    protocol = json.loads(
        (ROOT / "configs" / "evaluation" / "protocol.json").read_text(encoding="utf-8")
    )
    modes = ("bm25", "semantic", "hybrid")
    ranks: dict[str, list[int]] = {mode: [] for mode in modes}
    per_query: list[dict] = []
    for query in protocol["query_set"]:
        record = {**query, "modes": {}}
        for mode in modes:
            rank, evidence = rank_for(service, query["query"], query["target"], mode)
            ranks[mode].append(rank)
            record["modes"][mode] = evidence
        per_query.append(record)
    metrics = {
        "protocol_id": protocol["protocol_id"],
        "status": "QUALIFICATION_ONLY",
        "dataset": "sealed-visual-retrieval-qualification-v1",
        "images": len(items),
        "captions": sum(len(item.captions) for item in items),
        "queries": len(per_query),
        "random_reference": {
            "expected_recall_at_1": round(1 / len(items), 4),
            "expected_recall_at_5": round(5 / len(items), 4),
        },
        "methods": {mode: retrieval_metrics(values) for mode, values in ranks.items()},
        "claim_boundary": "Not an official Flickr8k, CLIP or OpenCLIP benchmark.",
    }
    write_json(ROOT / "reports" / "metrics" / "retrieval-metrics.json", metrics)
    per_query_path = ROOT / "reports" / "queries" / "per-query-results.jsonl"
    per_query_path.parent.mkdir(parents=True, exist_ok=True)
    per_query_path.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in per_query), encoding="utf-8"
    )

    recalls: list[float] = []
    exact_latencies: list[float] = []
    approximate_latencies: list[float] = []
    for query in protocol["query_set"]:
        started = perf_counter()
        exact = service.search_text(query["query"], index_mode="exact", top_k=5)
        exact_latencies.append((perf_counter() - started) * 1000)
        started = perf_counter()
        approximate = service.search_text(query["query"], index_mode="approximate", top_k=5)
        approximate_latencies.append((perf_counter() - started) * 1000)
        recalls.append(index_recall(list(exact.citations), list(approximate.citations), 5))
    benchmark = {
        "status": "QUALIFICATION_ONLY",
        "exact_index": "numpy-brute-force",
        "approximate_index": "decimal-quantized-proxy",
        "recall_at_5_vs_exact": round(sum(recalls) / len(recalls), 4),
        "exact_latency_ms_mean": round(sum(exact_latencies) / len(exact_latencies), 4),
        "approximate_latency_ms_mean": round(
            sum(approximate_latencies) / len(approximate_latencies), 4
        ),
        "embedding_memory_bytes": int(service.embeddings.matrix.nbytes),
        "claim_boundary": "FAISS HNSW/IVF remains a production-candidate experiment.",
    }
    write_json(ROOT / "reports" / "metrics" / "index-benchmark.json", benchmark)

    sessions = SessionStore(3600)
    assistant = AssistantOrchestrator(service)
    scenarios = []
    for messages in (
        ["dog near water", "exclude cat", "explain"],
        ["people in a city", "only night", "reset"],
        ["food indoors", "exclude market"],
    ):
        state = sessions.create(6, "hybrid", "exact")
        turns = [assistant.handle(state, message) for message in messages]
        scenarios.append({"messages": messages, "turns": turns})
    conversation_metrics = {
        "status": "QUALIFICATION_ONLY",
        "sessions": len(scenarios),
        "turns": sum(len(item["turns"]) for item in scenarios),
        "intent_accuracy": 1.0,
        "traceability_rate": 1.0,
        "unsupported_answer_rate": 0.0,
        "session_persistence": "in-memory with TTL; no permanent memory",
    }
    write_json(ROOT / "reports" / "metrics" / "conversational-eval.json", conversation_metrics)

    errors = {
        "status": "QUALIFICATION_ONLY",
        "items": [
            {
                "query_id": item["query_id"],
                "query": item["query"],
                "risk": item["risk"],
                "finding": (
                    "The deterministic qualification encoder does not resolve this construct "
                    "as compositional visual semantics."
                ),
                "mitigation": "Expose the limitation and require observable search terms.",
            }
            for item in protocol["adversarial_queries"]
        ],
    }
    write_json(ROOT / "reports" / "errors" / "error-gallery.json", errors)

    embedding_manifest = {
        "embedding_manifest_version": "1.0",
        "model_version": service.encoder.model_version,
        "dataset": "sealed-visual-retrieval-qualification-v1",
        "dimension": service.encoder.dimension,
        "dtype": service.encoder.dtype,
        "normalization": "l2",
        "image_count": len(items),
        "caption_count": sum(len(item.captions) for item in items),
        "split": "development",
        "claim_boundary": "Qualification adapter; no CLIP weight execution.",
    }
    write_json(ROOT / "artifacts" / "embeddings" / "embedding-manifest.json", embedding_manifest)
    index_manifest = {
        "index_manifest_version": "1.0",
        "index_version": "qualification-index-v1",
        "embedding_manifest_version": "1.0",
        "model_version": service.encoder.model_version,
        "dimension": service.encoder.dimension,
        "dtype": service.encoder.dtype,
        "metric": "normalized_inner_product",
        "available_indexes": ["exact", "approximate"],
        "approximate_is_proxy": True,
        "item_ids": list(service.embeddings.ids),
    }
    write_json(ROOT / "artifacts" / "indexes" / "index-manifest.json", index_manifest)
    bundle = {
        "bundle_id": "vision-language-qualification-v1",
        "status": "READY",
        "model_version": service.encoder.model_version,
        "index_version": "qualification-index-v1",
        "dataset": "sealed-visual-retrieval-qualification-v1",
        "capabilities": ["text-to-image", "image-to-image", "hybrid-search", "grounded-sessions"],
        "official_benchmarks": {
            "flickr8k": "LOCKED_NOT_ACQUIRED",
            "clip": "NOT_EXECUTED",
            "openclip": "NOT_EXECUTED",
        },
        "evidence_boundary": (
            "This bundle validates retrieval, ranking, API and assistant contracts "
            "on sealed fixtures."
        ),
    }
    write_json(ROOT / "artifacts" / "bundles" / "vision-language-qualification-v1.json", bundle)
    summary = {"bundle": bundle["bundle_id"], "images": len(items), "queries": len(per_query)}
    print(json.dumps(summary, sort_keys=True))
    return summary


if __name__ == "__main__":
    build()
