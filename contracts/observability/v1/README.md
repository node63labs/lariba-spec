# SP-A8 — Observability Contract V1

Status: canonical L1 contract candidate.

SP-A8 defines product-aware logging, metrics, correlation, tracing and telemetry-export boundaries.

Core invariants:

```text
OBSERVABILITY != AUTHORIZATION
OBSERVABILITY != PRODUCT_DOMAIN_TRUTH
OBSERVABILITY != ACTION_LEDGER
OBSERVABILITY_OUTAGE != DOMAIN_STATE_CORRUPTION

TRACE_CONTEXT != AUTHORITY
CORRELATION_ID != TRACE_ID
BAGGAGE != AUTHORIZATION
SHARED_TELEMETRY_BACKEND != UNRESTRICTED_CROSS_PRODUCT_ACCESS
```

Raw secrets and broad product-domain payloads are prohibited. Tenant or organization dimensions are policy-controlled and denied by default for metrics.

Contract version: 1.0.0
Schema version: 1
