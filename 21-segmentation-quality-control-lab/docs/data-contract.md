# Data contract

The intended benchmark is KSDD2. It must be supplied by the operator and pass
`scripts/verify_ksdd2_dataset.py`. Images require paired binary masks with identical spatial
dimensions. The official test remains locked until training, model selection and thresholds
are frozen.

The checked-in qualification profile contains 44 deterministic procedural grayscale surfaces:
24 train, 12 validation and eight showcase images. Each split contains clean and defective
pieces. It qualifies the software path only. The manifest stores paths, split, defect presence
and area; clean images remain in all relevant metric denominators.
