# Model and system card

## Intended use

Portfolio demonstration of auditable OCR and key information extraction on single-page
receipts. Intended users are ML engineers and reviewers inspecting how fields map to source
regions.

## Runtime bundle

- Qualification OCR: `annotated-fixture-v1`.
- Optional upload OCR: `paddleocr-v3`.
- Field extraction: `layout-aware-v1`.
- Normalization: `locale-aware-v1`.
- Review threshold: `0.82`.

## Evidence

The approved bundle contains hashes for the generated dataset manifest, extractor metadata,
evaluation summary and error gallery. Readiness fails if any artifact is missing or changed.

## Limitations

See `docs/threats-to-validity.md`. No SROIE, production SLA, calibrated confidence,
handwriting, table, multipage or compliance claim is made.
