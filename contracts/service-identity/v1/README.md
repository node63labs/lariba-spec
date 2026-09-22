# SP-A1 Service Identity v1

**Program:** ERA 2 — Shared Platform Stabilization
**Capability:** SP-A1 — Service Identity
**Contract:** `ServiceIdentityV1` / `ServiceCredentialReferenceV1`
**Schema version:** `1`
**Contract version:** `1.0.0`
**Status:** Historical L1-accepted `1.0.0` contract. New Set A cross-capability issuance is subject to the governed SP-A1 v2 compatibility amendment.

## Authority boundary

This contract identifies a non-human service principal. It does not grant product-domain authorization.

```text
ServiceIdentityV1
    = stable service principal

ServiceCredentialReferenceV1
    = safe reference to one authentication credential

credential != principal
identity != authorization
```

The principal ID must remain stable across credential rotation. Product, environment, and service context are explicit. Raw credential material, hashes, peppers, Lariba ORM objects, roles, permissions, scopes, approvals, and business-domain authority are outside the identity contract.

## Canonical schemas

- `service-identity.schema.json`
- `service-credential-reference.schema.json`

The initial issuing authority is:

```text
urn:node63:lariba-cloud:service-identity
```

Initial environment classes:

```text
development
test
preview
staging
production
```

Initial service classes:

```text
api
worker
connector
automation
system
```

## Compatibility rule

Existing Lariba API keys remain a credential implementation. Adoption of this contract is additive and must not require immediate customer credential reissue.

An existing credential may be projected into `ServiceCredentialReferenceV1`, but an SP-A1 identity requires an explicit credential-to-principal binding. An API key ID, Lariba project ID, or source ID must not become the durable service-principal ID.

## Consumer boundary

MedicamentOS may consume the stable service identity and safe credential reference. It must not depend on Lariba API-key/project/source ORM internals. MedicamentOS retains final pharmacy-domain authorization.

## Promotion state

```text
SP_A1_PROMOTION_LEVEL=L1
SP_A1_CONTRACT_DEFINED=YES
SP_A1_L1_ACCEPTED=YES
SP_A1_V1_STATUS=HISTORICAL_ACCEPTED
```

ERA2-A1-920 issued the formal L1 acceptance decision for SP-A1.

## Cross-capability compatibility amendment

The accepted v1 schema allows any non-empty `environment_id` and `service_id`.
Later Set A contracts narrowed those identifiers to:

```text
^[a-z0-9][a-z0-9._:-]*$
length 1..255
```

The v1 schema is intentionally not silently tightened because that would invalidate
values previously valid under the accepted 1.0.0 contract.

The governed amendment is defined by:

```text
contracts/service-identity/compatibility-amendment-2.0.0.md
contracts/service-identity/v2/service-identity.schema.json
```

Until that amendment is accepted, v1 remains the historical accepted contract.
After acceptance, new Set A cross-capability identities must use v2 or an explicitly
validated v1-to-v2 compatibility projection. Silent lowercasing, trimming,
renaming, or other identity normalization is prohibited.
