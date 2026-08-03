# Index card — qualification index v1

## Exact reference

NumPy brute-force normalized inner product provides the auditable oracle for the sealed
corpus. Stable sorting uses `image_id` as the deterministic tie-breaker.

## Approximate qualification proxy

The approximate path rounds normalized embeddings to one decimal before inner-product
ranking. It exists to exercise index selection, parity metrics and compatibility validation.
It is not FAISS HNSW or IVF.

## Production candidates

- Exact: FAISS `IndexFlatIP` with ID mapping and persisted manifests.
- Approximate: FAISS HNSW or IVF selected through development-only recall/latency sweeps.

## Required benchmark

Recall@K relative to exact, p50/p95 latency, throughput, memory, disk footprint and build time
must be reported before an approximate index becomes eligible for the online bundle.

