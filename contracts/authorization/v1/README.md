# SP-A3 Authorization Decision Contract v1

**Program:** ERA 2 — Shared Platform Stabilization  
**Capability:** SP-A3 — RBAC / Permission Primitives  
**Contract version:** `1.0.0`  
**Schema version:** `1`  
**Status:** Contract candidate persisted for ERA2-A1-240 verification — **not L1 accepted**

## Canonical objects

```text
PermissionEvaluationRequestV1
AuthorizationPrincipalV1
AuthorizationResourceV1
PolicyReferenceV1
PolicyDecisionV1
ApprovalRequirementV1
ApprovalReferenceV1
PermissionDecisionV1
```

Canonical schemas:

```text
permission-evaluation-request.schema.json
permission-decision.schema.json
medicamentos-policy-overlay.schema.json
```

## Decision vocabulary

```text
ALLOW < REQUIRE_APPROVAL < DENY
```

Composition is attenuation-only. The most restrictive applicable decision wins.

A downstream layer may preserve or restrict inherited authority. It must not broaden it.

```text
DENY + ALLOW             = DENY
DENY + REQUIRE_APPROVAL  = DENY
REQUIRE_APPROVAL + ALLOW = REQUIRE_APPROVAL
ALLOW + DENY             = DENY
```

Approval cannot override `DENY`. A valid exact-bound approval may satisfy a `REQUIRE_APPROVAL` requirement only through a new authorization evaluation.

## Core authority rules

```text
AUTHENTICATION != AUTHORIZATION
AUTHORIZATION != APPROVAL

ROLE != PORTABLE PERMISSION
MACHINE SCOPE != CROSS-PRODUCT PERMISSION

UNKNOWN ROLE       -> FAIL CLOSED
UNKNOWN PERMISSION -> FAIL CLOSED
UNKNOWN SCOPE      -> FAIL CLOSED
UNKNOWN ACTION     -> FAIL CLOSED

PRODUCT CONTEXT     = REQUIRED
ENVIRONMENT CONTEXT = REQUIRED
SEMANTIC ACTION     = REQUIRED

FRONTEND AUTHORITY = NONE
```

The portable authorization unit is the exact semantic action permission, not a global ordinal role rank.

## Path independence

Equivalent semantic actions must not gain broader authority because the execution path changes.

Relevant paths include web UI, REST API, SDK, connector, worker, offline path, agent, desktop runtime, and automation.

Path metadata may be evidence. It is not authority.

## Policy provenance

Every contributing policy decision identifies:

```text
policy_id
policy_version
authority_layer
authority_owner
```

The final decision is bound to principal, product, environment, tenant/resource where applicable, semantic action, policy set/version, and approval/delegation/capability context where applicable.

## MedicamentOS overlay

MedicamentOS uses:

```text
product_id=medicamentos
policy_id=urn:node63:medicamentos:authorization:pharmacy-domain
policy_version=1.0.0
authority_owner=MEDOS-DOMAIN
```

The following are normative:

```text
MEDOS product policy is required for MEDOS domain actions.

Lariba authentication does not grant MEDOS membership.
Lariba roles do not grant MEDOS permissions.
Lariba platform-admin status does not grant MEDOS domain authority.
Lariba API-key scopes/wildcards do not grant MEDOS semantic permissions.
Lariba generic ALLOW is not MEDOS domain ALLOW.

Dispensing authority remains MEDOS-DOMAIN.
Stock authority remains MEDOS-DOMAIN.
Inventory truth remains MEDOS-DOMAIN.
Pharmacy tenant and branch authority remain MEDOS-DOMAIN.

Agent identity alone does not grant dispensing authority.
Offline execution must not broaden authority.
Frontend presentation is not backend authorization.
```

The current source set does not define a canonical MedicamentOS staff-role catalogue or a production action-by-action approval matrix. Those remain product-local inputs and are not invented by this contract.

## Compatibility requirement

ERA2-A1-240 must provide executable proof for at least:

```text
weaker child policy cannot override stronger parent
same semantic action via alternate path cannot gain permission
wrong product denied
wrong environment denied
wrong tenant/branch denied
missing required product policy denied
unknown role/action denied
Lariba role cannot grant MEDOS domain authority
Lariba wildcard cannot grant MEDOS domain authority
missing required approval is not executable
approval cannot override DENY
agent/capability existence cannot grant dispensing authority
offline path cannot broaden authority
```

## Promotion state

```text
SP_A3_CONTRACT_DEFINED=YES
SP_A3_MEDOS_OVERLAY_DEFINED=YES
SP_A3_REFERENCE_IMPLEMENTATION=NOT_YET_VERIFIED
SP_A3_NEGATIVE_TESTS_VERIFIED=NO
SP_A3_L1_ACCEPTED=NO
```

ERA2-A1-240 supplies reference implementation and executable proof. Final L1 acceptance remains reserved for ERA2-A1-920.
