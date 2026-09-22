# SET_A_B03 — SP-A1 Identifier Grammar Compatibility Amendment

**Document ID:** NODE63-SET-A-B03-SP-A1-IDENTIFIER-GRAMMAR-COMPATIBILITY-AMENDMENT
**Program:** ERA 2 — Shared Platform Stabilization
**Capability:** SP-A1 Service Identity
**Affected dependencies:** SP-A10 / SP-A4 / SP-A5
**Date:** 2026-09-22
**Status:** IMPLEMENTED ON FEATURE BRANCH — GOVERNED ACCEPTANCE PENDING
**Mutation Class:** SPECIFICATION / VALIDATION ONLY — NO RUNTIME MUTATION
**Canonical spec authority at entry:** `node63labs/lariba-spec@037188610fc716aed0025e00ccc7fcf76d42ba7b`
**Lariba runtime authority observed:** `node63labs/lariba-cloud@5a2b6e4948e809b340e149109c4359df6d94c1c5`

## Finding

SP-A1 v1 permits any non-empty `environment_id` and `service_id`. SP-A10,
SP-A4 and SP-A5 require:

```text
^[a-z0-9][a-z0-9._:-]*$
length 1..255
```

So an upstream-valid SP-A1 v1 identity can be impossible to represent downstream.

```text
SET_A_B03=IDENTIFIER_GRAMMAR_INCOMPATIBILITY
```

## Versioning decision

The original SP-A1 policy says validation-tightening is not backward compatible
and breaking changes require a new major version, migration path, deprecation
window, affected-consumer list, rollback, compatibility evidence and provenance.

Decision:

```text
MODIFY_ACCEPTED_V1_SCHEMA_IN_PLACE=NO
ADD_SERVICE_IDENTITY_V2=YES
SCHEMA_VERSION=2
CONTRACT_VERSION=2.0.0
V1_REMAINS_HISTORICAL_ACCEPTED=YES
```

## Canonical v2 identifier profile

```text
CANONICAL_PATTERN=^[a-z0-9][a-z0-9._:-]*$
MIN_LENGTH=1
MAX_LENGTH=255
```

Applied to:

```text
ServiceIdentityV2.environment.environment_id
ServiceIdentityV2.service_id
```

## Downstream compatibility

| Surface | environment_id | service_id | Result |
|---|---|---|---|
| SP-A1 v1 | non-empty | non-empty | broader historical surface |
| SP-A1 v2 | canonical / 1..255 | canonical / 1..255 | PASS |
| SP-A10 ServiceIdentityReferenceV1 | canonical / 1..255 | canonical / 1..255 | PASS |
| SP-A4 SecretConsumerBindingV1 | canonical / 1..255 | canonical / 1..255 | PASS |
| SP-A5 EventServiceIdentityReferenceV1 | canonical / 1..255 | canonical / 1..255 | PASS |

```text
SP_A1_V2_TO_SP_A10_IDENTIFIER_COMPATIBILITY=PASS
SP_A1_V2_TO_SP_A4_IDENTIFIER_COMPATIBILITY=PASS
SP_A1_V2_TO_SP_A5_IDENTIFIER_COMPATIBILITY=PASS
```

## Migration

A conforming v1 identity may be projected to v2 after explicit compatibility
validation while preserving `principal_id`.

A non-conforming v1 identifier must not be normalized implicitly.

Required sequence:

```text
inventory v1 principal
→ validate issuer/product/environment/service context
→ test v2 identifier grammar
→ if conforming: create attributable v2 projection
→ if non-conforming: require explicit owner-approved mapping
→ preserve principal_id only when logical principal continuity is proven
→ otherwise issue a new principal
→ record migration evidence
```

Raw credential material must never enter migration evidence.

## Rollback

V1 is not modified or removed. If v2 adoption must be rolled back before
acceptance, stop v2 issuance and retain v1 parsing. No reverse normalization is
allowed.

## Deprecation

After amendment acceptance:

```text
V1_NEW_CROSS_PRODUCT_ISSUANCE=DEPRECATED_AND_PROHIBITED
V1_INTERNAL_LEGACY_READ=TEMPORARILY_ALLOWED
V2_NEW_CROSS_PRODUCT_ISSUANCE=REQUIRED
```

No fixed retirement date is invented.

## Deterministic validation

The canonical contract validator is extended to assert:

```text
v1 remains broad and unmodified
v2 is schema_version=2 / contract_version=2.0.0
v2 environment_id and service_id match the canonical grammar
SP-A10 projected identifiers match v2
SP-A4 consumer identifiers match v2
```

SP-A5 remains runtime-authoritative; its current accepted model was separately
inspected and uses the same pattern and bounds.

## Authority boundary

```text
IDENTIFIER_SYNTAX != AUTHORIZATION
SERVICE_IDENTITY != PRODUCT_DOMAIN_PERMISSION
ENVIRONMENT_ID != ENVIRONMENT_AUTHORIZATION_WITHOUT_BINDING
CREDENTIAL_POSSESSION != PRODUCT_AUTHORITY
PRODUCT_DOMAIN_AUTHORITY_PRESERVED=YES
```

## Promotion boundary

```text
SET_A_B03_REMEDIATION_IMPLEMENTED=YES
SET_A_B03_CANONICALLY_CLOSED=NO
SP_A1_V2_CONTRACT_DEFINED=YES
SP_A1_V2_ACCEPTED=NO
MEDICAMENTOS_L2_START_AUTHORIZED=NO
N2_APPROVED=NO
```

# End of Document
