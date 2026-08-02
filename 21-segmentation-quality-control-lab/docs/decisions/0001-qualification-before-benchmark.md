# ADR 0001: qualify the software vertical before benchmark claims

## Status

Accepted.

## Decision

Use a deterministic procedural profile to validate alignment, training, threshold selection,
inference, policy, API and UI while keeping KSDD2 unacquired and its test locked.

## Consequences

The product can be demonstrated and tested without distributing unverified benchmark data.
Its metrics cannot be cited as KSDD2 or industrial performance. A later KSDD2 qualification
must create a new immutable bundle and evidence set without rewriting this record.
