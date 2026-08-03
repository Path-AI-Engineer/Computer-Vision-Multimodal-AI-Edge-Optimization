# Assistant contract

The assistant is a deterministic retrieval orchestrator, not an open generative chatbot.

Supported intents are `search`, `refine`, `exclude`, `explain` and `reset`. A typed
`SearchState` records the positive query, negative terms, filters, prior result IDs, selected
image, model/index versions and top K. Explanations cite retrieved IDs, stored captions and
scores only. URLs, identification and sensitive-attribute inference are rejected.

