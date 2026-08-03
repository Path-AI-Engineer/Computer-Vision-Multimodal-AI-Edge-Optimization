# Data contract

Each image has one unique `image_id`, one filename, a split, checksum, observable metadata,
one or more globally unique captions and one vector compatible with the declared embedding
contract. Dataset validation rejects missing assets, duplicate IDs, empty captions, empty
vectors and checksum mismatches.

`sealed-visual-retrieval-qualification-v1` contains generated fixtures only. Flickr8k must be
stored outside Git, verified against an approved manifest and split canonically before any
official benchmark is run.

