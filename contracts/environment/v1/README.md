# SP-A10 Environment / Service Identity Contract v1

**Program:** ERA 2 — Shared Platform Stabilization  
**Capability:** SP-A10 — Environment / Service Identity  
**Contract version:** `1.0.0`  
**Schema version:** `1`  
**Status:** Candidate persisted for ERA2-A2-230 executable isolation proof — **not L1 accepted**

## Canonical objects

```text
EnvironmentIdentityV1
EnvironmentIdentityReferenceV1
EnvironmentClaimV1
ServiceEnvironmentBindingV1
RuntimeObservationV1
ServiceEnvironmentBindingDecisionV1
```

## Core invariants

```text
ENVIRONMENT LABEL != ENVIRONMENT AUTHORITY

SERVICE IDENTITY != RUNTIME BINDING

RUNTIME SELF-CLAIM != CANONICAL AUTHORITY

PROVIDER LABEL != CANONICAL AUTHORITY

PREVIEW != PRODUCTION

DEVELOPMENT != PRODUCTION

SAME SERVICE NAME IN TWO PRODUCTS != SAME AUTHORITY

SERVICE IDENTITY MUST BIND TO ENVIRONMENT
```

A `BOUND` decision requires canonical service/environment/binding authority plus
sufficient independent runtime/provider evidence.

```text
MISMATCH       => FAIL_CLOSED
INDETERMINATE  => FAIL_CLOSED
```

## Evidence precedence

```text
Class A: canonical identity/binding authority
>
Class B: independent runtime/provider evidence
>
Class C: runtime self-claim
>
Class D: domain/display metadata
```

Lower-precedence evidence may corroborate but cannot override higher authority.

## Preview / production rule

A preview service or runtime cannot become production by changing:

```text
LARIBA_ENV
VERCEL_ENV
provider label
branch name
hostname
source.environment
alert.environment
```

Environment-class promotion requires a distinct canonical environment identity and
a distinct service-to-environment binding.

## Provider migration

Provider migration may preserve `EnvironmentIdentityV1` while replacing the
authorized runtime selector in `ServiceEnvironmentBindingV1`.

A superseded provider does not remain authorized merely because it is reachable.

## Database binding

Database credentials are not environment authority. Where an exact database binding
is required, the observed database target must match the bound database role/target.

## A2-230 proof target

Executable proof must include at least:

```text
preview cannot bind production
runtime variable cannot promote environment
provider label cannot promote environment
wrong product denied
wrong environment denied
wrong principal denied
wrong service denied
superseded provider denied
wrong process role denied
wrong database target denied
reachability is not authority
missing provider evidence => indeterminate/fail closed
local runtime without trusted executor => indeterminate/fail closed
same class / different environment denied
same environment class / different product denied
```

## Promotion boundary

A2-230 establishes preview/production and product/runtime isolation evidence.

Release/provenance and SP-A4 secret-to-runtime binding remain A2-240 work.

```text
SP_A10_CANONICAL_SPEC_PERSISTED=YES
SP_A10_PREVIEW_PRODUCTION_ISOLATION_VERIFIED=NO
SP_A10_RELEASE_SECRET_BINDING_VERIFIED=NO
SP_A10_L1_ACCEPTED=NO
```
