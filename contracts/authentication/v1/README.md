# SP-A2 Authentication Contract v1

**Program:** ERA 2 — Shared Platform Stabilization
**Capability:** SP-A2 — Authentication Contract
**Contract version:** `1.0.0`
**Schema version:** `1`
**Status:** Contract candidate implemented for ERA2-A1-130 verification — **not L1 accepted**

## Contract objects

The canonical SP-A2 V1 contract consists of:

```text
AuthenticationAssertionV1
SessionReferenceV1
AuthenticationAssuranceV1
```

Canonical schemas:

```text
authentication-assertion.schema.json
session-reference.schema.json
authentication-assurance.schema.json
```

## Core boundary

```text
AUTHENTICATION != AUTHORIZATION
AUTHENTICATION != APPROVAL
IDENTITY != PRODUCT MEMBERSHIP
SESSION != ROLE
TOKEN != PRODUCT PERMISSION
```

An authentication assertion proves authenticated identity and authentication context. It does not grant Lariba roles, MedicamentOS membership, pharmacy roles, dispensing authority, stock mutation authority, refund authority, or approval authority.

## Issuer

Initial V1 issuer:

```text
urn:node63:lariba-cloud:authentication
```

Consumers must explicitly trust the issuer. Issuer authority must not be inferred from hostname, cookie name, network route, database location, or token prefix.

## Audience

Every assertion is bound to one explicit audience.

Product audience:

```text
urn:node63:product:<product_id>
```

A future service-specific profile may use:

```text
urn:node63:service:<product_id>:<service_id>
```

A generic all-products audience is not valid in V1. Runtime validation must also verify that the audience and `product_context.product_id` are consistent.

## Principal

For the human-authentication profile:

```text
principal_type = human
```

`principal_id` is an opaque issuer-scoped stable human-principal identifier. Consumers must not require direct access to Lariba `User` persistence. The initial Lariba reference implementation may map the existing stable User UUID into this opaque field.

## Product and environment

The assertion carries:

```text
product_context.product_id
environment.environment_id
environment.environment_class
```

The product context identifies the target product. It does not prove product membership.

Environment classes:

```text
development
test
preview
staging
production
```

Wrong-product and wrong-environment use must fail closed.

## Organization context

`organization_context` is optional and may be included only when authentication itself is materially bound to that organization/tenant context.

Even when present:

```text
organization_context != membership
organization_context != authorization
```

## Authentication methods

Initial V1 method identifiers:

```text
password
passkey
totp
recovery_code
trusted_device
oauth:google
oauth:apple
```

All methods contributing to the authenticated session are reported. Normal refresh is session continuation and must not replace the original authentication-method provenance.

## Assurance

`AuthenticationAssuranceV1` reports factual authentication properties:

```text
factor_count
mfa_satisfied
phishing_resistant
user_verification
trusted_device_used
recovery_method_used
```

These properties describe authentication; they do not grant permissions.

## Authentication time and refresh

`authentication_time` is the original successful authentication event establishing the current session.

It is distinct from `issued_at`, which is the creation time of one assertion instance.

Normal refresh may change:

```text
assertion_id
issued_at
expires_at
```

but must not silently change:

```text
principal_id
session_id
authentication_time
authentication_methods
assurance
product context
environment
```

## Session reference and revocation

`SessionReferenceV1` carries:

```text
session_id
validation_mode
created_at
expires_at
```

V1 uses:

```text
validation_mode = issuer_online
```

The session ID is stable across normal refresh rotation.

The issuer remains authoritative for session state, therefore:

```text
valid signature != active session
```

A revoked, expired, unknown, or principal-mismatched session must fail closed. Local signature verification alone is insufficient to override session revocation.

## Cross-product wire profile

ERA2-A1-120 defines an additive candidate cross-product profile:

```text
JWT / JWS
asymmetric signing
kid-based key selection
public verification-key distribution
```

The existing Lariba web HS256 access/refresh session remains unchanged by this contract candidate. The shared cross-product assertion is additive.

The exact signing algorithm and key-provisioning implementation must be locked during implementation/security review before production use.

## Secret exclusion

Authentication assertions and normal evidence must never contain raw or derived authentication secret material, including passwords, refresh tokens, TOTP secrets/codes, recovery codes, trusted-device tokens, OAuth provider tokens, passkey private-key material, signing private keys, or shared signing secrets.

## MedicamentOS consumer boundary

MedicamentOS may consume authentication identity/context from this assertion, but it must resolve separately:

```text
membership
pharmacy role
dispensing authorization
stock authority
refund authority
other pharmacy-domain permissions
```

## Compatibility requirement

ERA2-A1-130 must prove no regression to existing Lariba password login, email verification, access/refresh behavior, logout/session revocation, password-change revocation, passkeys, passwordless passkeys, TOTP, recovery codes, trusted devices, Google/Apple OAuth, and web BFF session handling.

## Promotion state

```text
SP_A2_PROMOTION_LEVEL=L0
SP_A2_CONTRACT_DEFINED=YES
SP_A2_REFERENCE_IMPLEMENTATION=NOT_YET_VERIFIED
SP_A2_COMPATIBILITY_VERIFIED=NO
SP_A2_NEGATIVE_TESTS_VERIFIED=NO
SP_A2_L1_ACCEPTED=NO
```

ERA2-A1-130 supplies implementation and executable proof. Final L1 acceptance remains a later explicit review.
