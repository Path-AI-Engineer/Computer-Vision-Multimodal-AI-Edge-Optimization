# Model card — qualification dual encoder v1

## Intended use

Validate shared-space retrieval contracts, normalization, score composition, API schemas and
grounded assistant behavior on the sealed qualification corpus.

## Implementation

- 12-dimensional deterministic observable-term projection.
- L2-normalized image and text vectors.
- Image vectors are versioned in the sealed corpus manifest.
- Text vectors use a documented vocabulary grouped by observable concepts.

## Not represented

This adapter is not OpenAI CLIP, OpenCLIP or a learned multimodal representation. Results
cannot be cited as foundation-model performance. The optional research requirements define
the packages needed for the later controlled benchmark but are not installed in the default
runtime.

## Known limitations

- Weak compositional understanding and no reliable negation.
- No spatial-relation reasoning.
- Vocabulary-bound semantic coverage.
- No identity, emotion, intent or sensitive-attribute inference.
- A similarity score is only a ranking signal.

## Version binding

The model is compatible only with embedding manifest `1.0`, dimension `12`, `float32`, L2
normalization and index `qualification-index-v1`.

