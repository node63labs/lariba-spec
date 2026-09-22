# SP-A1 Service Identity v2

**Program:** ERA 2 — Shared Platform Stabilization
**Capability:** SP-A1 — Service Identity
**Contract:** `ServiceIdentityV2`
**Schema version:** `2`
**Contract version:** `2.0.0`
**Status:** Set A B03 compatibility-amendment candidate; governed acceptance pending.

## Purpose

ServiceIdentityV2 resolves the identifier-grammar incompatibility identified by the
Set A aggregate review.

SP-A1 v1 permits any non-empty `environment_id` and `service_id`, while
SP-A10, SP-A4 and SP-A5 require:

```text
^[a-z0-9][a-z0-9._:-]*$
length 1..255
```

V2 adopts that exact grammar for both fields.

## Major-version decision

Tightening v1 in place would make previously valid values invalid. The original
SP-A1 versioning policy classifies that as breaking, so:

```text
V1_SCHEMA_IS_NOT_MUTATED=YES
V2_SCHEMA_VERSION=2
V2_CONTRACT_VERSION=2.0.0
```

## Authority boundary

V2 changes identifier syntax only. It does not change principal identity,
issuing authority, product authority, environment authority, service-class
semantics, credential/principal separation, or authorization boundaries.

## V1 compatibility bridge

A v1 identity may be projected to v2 only when principal continuity is established
and its `environment_id` and `service_id` already satisfy the v2 grammar.

A non-conforming v1 identity must not be silently normalized. Implicit lowercasing,
trimming, space-to-hyphen conversion, punctuation replacement, and identifier
guessing are prohibited.

If a mapping is required, it must be explicit, attributable, and approved by the
owning product/environment authority. Preserve `principal_id` only when logical
principal continuity is proven; otherwise issue a new principal.

## Consumer composition

The v2 grammar is identical to the accepted grammar used by:

```text
SP-A10 ServiceEnvironmentBindingV1 service identity reference
SP-A4 SecretConsumerBindingV1
SP-A5 EventServiceIdentityReferenceV1
```

The SP-A5 runtime surface was rechecked at:

```text
node63labs/lariba-cloud@5a2b6e4948e809b340e149109c4359df6d94c1c5
lariba-cloud/src/schemas/event_envelope.py
```

## Migration / deprecation

After amendment acceptance:

```text
NEW_CROSS_PRODUCT_IDENTITY_ISSUANCE=V2_REQUIRED
NEW_MEDICAMENTOS_L2_IDENTITY_CONSUMPTION=V2_REQUIRED
V1_INTERNAL_LEGACY_READ=ALLOWED_DURING_MIGRATION
V1_NEW_CROSS_PRODUCT_ISSUANCE=PROHIBITED
AUTOMATIC_NORMALIZATION=PROHIBITED
```

No fixed deprecation date is invented here. V1 retirement requires separate
evidence that no required consumer depends on a non-conforming v1 identity.

## Promotion boundary

```text
SP_A1_V2_CONTRACT_DEFINED=YES
SP_A1_V2_ACCEPTED=NO
SET_A_B03_REMEDIATION_IMPLEMENTED=YES
SET_A_B03_CANONICALLY_CLOSED=NO
MEDICAMENTOS_L2_START_AUTHORIZED=NO
```
