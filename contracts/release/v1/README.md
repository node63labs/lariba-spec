# SP-A9 — Release Provenance V1

Status: canonical L1 contract candidate.

SP-A9 exposes reusable release-provenance semantics while preserving product-local release authorization.

Core invariants:

```text
SHARED_RELEASE_PROVENANCE != SHARED_DEPLOYMENT_AUTHORITY
SOURCE_SHA = IMMUTABLE_SOURCE_AUTHORITY
MUTABLE_REF != SOURCE_AUTHORITY
CI_GREEN != RELEASE_AUTHORIZED
MERGE_AUTHORIZATION != DEPLOYMENT_AUTHORIZATION
RELEASED != VERIFIED
VERIFIED != ACCEPTED
```

The contract composes with NODE63 W3 release governance and SP-A10 environment/service identity. It does not create a second release state machine.

Raw credentials are prohibited from provenance records.

Contract version: 1.0.0
Schema version: 1

## Deterministic validation

Cross-field provenance invariants that cannot be expressed safely in portable JSON Schema are enforced by:

`scripts/ci/validate_contracts.py`

CI-P05 / CI-C03 executes that validator. The validator checks repository/source equality, source-SHA continuity across CI/build/artifact/release-action evidence, release-class action compatibility, environment applicability, binding applicability, non-empty material evidence, and fail-closed aggregate binding semantics.

A structurally valid JSON document is not sufficient when these semantic checks fail.

