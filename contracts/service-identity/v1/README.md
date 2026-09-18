# SP-A1 Service Identity v1

**Program:** ERA 2 — Shared Platform Stabilization  
**Capability:** SP-A1 — Service Identity  
**Contract:** `ServiceIdentityV1` / `ServiceCredentialReferenceV1`  
**Schema version:** `1`  
**Contract version:** `1.0.0`  
**Status:** Contract candidate implemented for ERA2-A1-030 verification; **not L1 accepted**

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
SP_A1_PROMOTION_LEVEL=L0
SP_A1_CONTRACT_DEFINED=YES
SP_A1_L1_ACCEPTED=NO
```

ERA2-A1-030 supplies compatibility and negative-test evidence. L1 acceptance remains a later explicit review.
