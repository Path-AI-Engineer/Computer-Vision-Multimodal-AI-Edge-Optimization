# Architecture

The system separates offline evidence generation from online retrieval. `multimodal` owns
data and vector contracts; `assistant` owns bounded state and grounded language; `backend`
composes both behind HTTP resources; `frontend` renders only returned evidence.

The active bundle is immutable for the lifetime of the process. Readiness validates the
manifest before serving requests. Sessions retain typed state in memory with TTL and can be
deleted explicitly. They never mutate embeddings, indexes or evaluation reports.

