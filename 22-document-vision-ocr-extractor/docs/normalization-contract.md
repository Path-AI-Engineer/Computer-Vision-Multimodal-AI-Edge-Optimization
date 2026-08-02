# Normalization contract

Normalization is deterministic and separately testable:

- date patterns are converted to ISO dates;
- comma-only decimal separators are converted to dots;
- currency markers and thousands separators are removed;
- negative totals and invalid dates are rejected;
- company and address whitespace is compacted before presentation casing.

No dictionary silently replaces OCR content. The raw value remains visible and exportable.
Locale-specific ambiguity such as `03/04/2026` requires a declared locale policy in a future
release; this qualification set avoids ambiguous dates.
