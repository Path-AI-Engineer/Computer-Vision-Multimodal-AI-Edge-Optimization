# Search contract

Text search accepts `bm25`, `semantic` or `hybrid`. Hybrid returns the lexical, semantic and
combined scores plus alpha. Filters are applied before final top-K selection. Image search
accepts a sealed `image_id`; temporary uploads are bounded and decoded locally.

Every result includes rank, `image_id`, URL, metadata, score components, evidence captions
and reason codes. Scores order the collection and do not establish facts.

