# ADR 0001: qualify the product path before benchmark training

## Status

Accepted.

## Decision

Ship a clearly labeled procedural qualification artifact for local product verification before
downloading Oxford-IIIT Pet or pretrained weights. Preserve the official test lock and report all
deep candidates as unexecuted until reproducible runs exist.

## Consequences

- API, security, calibration, artifact and interface paths are demonstrable now.
- Qualification metrics are intentionally easy and cannot support benchmark claims.
- Project 19 remains technically `IN_PROGRESS` against the full 28-day map until official-data
  model comparison, final test and Grad-CAM evidence are executed.
