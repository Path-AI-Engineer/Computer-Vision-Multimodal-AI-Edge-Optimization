# Data contract

## Input image

- JPEG, PNG or WebP.
- RGB normalization after EXIF orientation.
- Maximum 8 MiB by default and 30 million decoded pixels.
- Single endpoint accepts exactly one file; batch accepts 1-4 files by default.
- Unsupported, empty, oversized and undecodable payloads return explicit 4xx responses.

## SKU-110K acquisition

The repository does not redistribute or automatically download SKU-110K. A user-provided extraction must preserve the official train, validation and test boundaries. The verifier checks the documented counts: 8,219 train images, 588 validation images and 2,936 test images. Test labels remain outside candidate selection.

## Qualification fixture

The procedural fixture has 12 deterministic 960x540 RGB scenes, 740 visible objects and low/medium/high density slices. Its manifest records hashes and the explicit `procedural_fixture` license scope. It is suitable for contract qualification only.
