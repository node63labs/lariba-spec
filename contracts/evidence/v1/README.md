# SP-A7 — Evidence / Action Ledger V1

Status: canonical L1 contract candidate.

This contract family defines shared evidence primitives without taking ownership of product-domain truth.

Core invariants:

```text
ACTION_LEDGER_RECORD != AUTHORIZATION
ACTION_LEDGER_RECORD != APPROVAL
ACTION_LEDGER_RECORD != PRODUCT_DOMAIN_TRANSACTION
ACTION_LEDGER_RECORD != OBSERVABILITY_EVENT
ACTION_LEDGER_RECORD != RELEASE_AUTHORIZATION

SHARED_EVIDENCE != PRODUCT_DOMAIN_TRUTH
DOMAIN_RECORD_REF != DIRECT_DATABASE_FOREIGN_KEY
READ_PERMISSION != EXPORT_PERMISSION
```

The ledger is append-only. Corrections create new records. Product-domain records remain owned by the product that created them.

Raw passwords, API keys, private keys, bearer tokens, session secrets, unrestricted environment dumps, and product payload copies are prohibited from canonical shared evidence.

Contract version: 1.0.0
Schema version: 1
