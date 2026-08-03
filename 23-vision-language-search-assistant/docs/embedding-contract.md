# Embedding contract

Image and text towers share a model version, dimension and dtype. Every vector is L2
normalized before normalized inner product. Embeddings from different models cannot share
an index. Manifests record dataset, split, normalization, model version and cardinality.

The bundled deterministic adapter proves the contract but not CLIP quality. A real adapter
must preserve its checkpoint preprocessing and version image/text towers together.

