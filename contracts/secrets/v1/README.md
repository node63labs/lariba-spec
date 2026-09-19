# SP-A4 Secrets Isolation Contract v1

**Program:** ERA 2 — Shared Platform Stabilization  
**Capability:** SP-A4 — Secrets Isolation  
**Contract version:** `1.0.0`  
**Schema version:** `1`  
**Status:** Contract candidate persisted for ERA2-A2-140 verification — **not L1 accepted**

## Canonical objects

```text
SecretReferenceV1
SecretScopeV1
SecretConsumerBindingV1
SecretLifecycleReferenceV1
SecretGenerationReferenceV1
SecretUseContextV1
SecretScopeDecisionV1
```

Canonical schemas:

```text
secret-reference.schema.json
secret-scope.schema.json
secret-lifecycle.schema.json
secret-use-context.schema.json
secret-scope-decision.schema.json
```

## Core separation

```text
SECRET REFERENCE != SECRET MATERIAL
SECRET SCOPE != ACTION AUTHORIZATION
SECRET DECRYPTABILITY != AUTHORIZED USE
SECRET OWNER != SECRET CONSUMER
PROVIDER CREDENTIAL != PRODUCT AUTHORITY
```

SP-A3 remains authoritative for action permission. SP-A4 determines whether a secret reference may be resolved in the exact requested context.

```text
SP-A3 ALLOW + SP-A4 MISMATCH = NO SECRET RESOLUTION
SP-A3 DENY  + SP-A4 MATCH    = NO EXECUTION
```

## Mandatory scope

Every V1 scope binds:

```text
product
environment
consumer service
consumer service principal
purpose
privilege class
```

Tenant, project, resource and provider dimensions are either `EXACT` or `NOT_APPLICABLE`.

No wildcard is permitted for product, environment, service or purpose.

## Cross-product sharing

Default:

```text
SINGLE_PRODUCT
```

Cross-product sharing is an explicit exception:

```text
EXPLICIT_MULTI_PRODUCT
+ exact consumer bindings
+ governance justification reference
```

A listed product/environment/service does not imply any other consumer.

## Lifecycle

```text
SECRET MATERIAL GENERATION != ENCRYPTION KEY VERSION
ROTATION != SCOPE MUTATION
PROVIDER RETIREMENT != CREDENTIAL REVOCATION
```

Ordinary material rotation preserves `secret_reference_id` and `scope_id`.

Changing product, environment, service, tenant, project, resource, provider target, purpose, privilege or sharing mode requires a new logical secret reference under V1.

Exactly one primary generation may be active for normal use. Overlap is explicit and time-bounded. Revocation and expiry fail closed.

## No secret transport

The shared contract contains no plaintext secret material and does not transport ciphertext.

```text
PLAINTEXT IN CONTRACT = NO
CIPHERTEXT IN SHARED REFERENCE = NO
PRIVATE KEY MATERIAL IN CONTRACT = NO
```

Storage adapters retain responsibility for protected storage and just-in-time resolution.

## MedicamentOS boundary

MedicamentOS secret use requires explicit:

```text
product=medicamentos
environment
consumer service principal
purpose
privilege
tenant/pharmacy scope where applicable
resource/provider target where applicable
```

Lariba project access, Lariba platform-admin status, or a Lariba secret reference do not grant MedicamentOS secret authority.

## ERA2-A2-140 verification target

Executable proof must cover at least:

```text
wrong product denied
wrong environment denied
wrong service denied
wrong service principal denied
wrong tenant denied
wrong project denied
wrong resource denied
wrong provider/account denied
wrong purpose denied
wrong privilege denied
unlisted shared-secret consumer denied
missing/ambiguous scope denied
revoked/expired/retired/unavailable generation denied
multiple active primary generations rejected
scope mutation cannot masquerade as rotation
missing/wrong encryption key version fails closed
SP-A3 ALLOW cannot bypass SP-A4 mismatch
valid secret cannot repair target mismatch
```

## Promotion state

```text
SP_A4_SCOPE_MODEL=DEFINED
SP_A4_SECRET_REFERENCE_CONTRACT=DEFINED
SP_A4_ROTATION_REVOCATION_CONTRACT=DEFINED
SP_A4_CANONICAL_SPEC_PERSISTED=YES
SP_A4_REFERENCE_IMPLEMENTATION=NOT_YET_VERIFIED
SP_A4_NEGATIVE_TESTS_VERIFIED=NO
SP_A4_L1_ACCEPTED=NO
```

ERA2-A2-140 supplies reference implementation and executable proof. Final L1 acceptance remains reserved for the ERA2-A2 acceptance sequence.
