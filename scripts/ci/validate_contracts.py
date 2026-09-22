#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from uuid import UUID


DRAFT = "https://json-schema.org/draft/2020-12/schema"

EXAMPLE_SCHEMA_MAP = {
    "contracts/evidence/v1/examples/medicamentos-action-ledger.example.json":
        "contracts/evidence/v1/action-ledger-record.schema.json",
    "contracts/observability/v1/examples/medicamentos-observability.example.json":
        "contracts/observability/v1/structured-log-record.schema.json",
    "contracts/release/v1/examples/medicamentos-release-provenance.example.json":
        "contracts/release/v1/release-provenance.schema.json",
}

RELEASE_CLASS_ACTIONS = {
    "RC-01": {"deployment"},
    "RC-02": {"deployment"},
    "RC-03": {"publication", "deployment"},
    "RC-04": {"package_publication"},
    "RC-05": {"contract_promotion"},
}

CI_BUILD_REQUIRED = {"RC-01", "RC-04", "RC-05"}

BINDING_FIELDS = (
    "source_binding",
    "ci_binding",
    "build_binding",
    "artifact_binding",
    "environment_binding",
    "release_action_binding",
    "verification_binding",
)

SAFE_METRIC_DIMENSIONS = {
    "product_id",
    "service_id",
    "environment_class",
    "operation",
    "result",
    "dependency_type",
    "dependency_id",
    "degraded_state",
    "release_version",
}


class ValidationFailure(Exception):
    pass


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationFailure(f"unable to load JSON {path}: {exc}") from exc


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def walk_refs(node: object):
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            yield ref
        for value in node.values():
            yield from walk_refs(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk_refs(value)


def resolve_pointer(document: object, fragment: str) -> object:
    if fragment in ("", "#"):
        return document
    if not fragment.startswith("#/"):
        raise ValidationFailure(f"unsupported JSON pointer fragment: {fragment}")

    current = document
    for raw_part in fragment[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            raise ValidationFailure(f"missing JSON pointer fragment: {fragment}")
        current = current[part]
    return current


def resolve_ref(
    schema_path: Path,
    ref: str,
    documents: dict[Path, object],
) -> tuple[Path, object, object]:
    if ref.startswith("#"):
        root = documents[schema_path]
        return schema_path, resolve_pointer(root, ref), root

    if "://" in ref or ref.startswith("urn:"):
        raise ValidationFailure(
            f"{schema_path}: external $ref is not allowed in deterministic validation: {ref}"
        )

    file_part, sep, fragment_part = ref.partition("#")
    target_path = (schema_path.parent / file_part).resolve()

    if target_path not in documents:
        raise ValidationFailure(
            f"{schema_path}: missing relative $ref target {ref}"
        )

    root = documents[target_path]
    fragment = f"#{fragment_part}" if sep else ""
    target = resolve_pointer(root, fragment)
    return target_path, target, root


def type_matches(value: object, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def validate_instance(
    instance: object,
    schema: object,
    schema_path: Path,
    documents: dict[Path, object],
    location: str = "$",
    root_schema: object | None = None,
) -> list[str]:
    errors: list[str] = []

    if not isinstance(schema, dict):
        return errors

    if root_schema is None:
        root_schema = documents[schema_path]

    if "$ref" in schema:
        target_path, target, target_root = resolve_ref(
            schema_path,
            schema["$ref"],
            documents,
        )
        return validate_instance(
            instance,
            target,
            target_path,
            documents,
            location,
            target_root,
        )

    if "const" in schema and instance != schema["const"]:
        return [f"{location}: expected const {schema['const']!r}"]

    if "enum" in schema and instance not in schema["enum"]:
        return [f"{location}: value not in enum"]

    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not type_matches(instance, expected_type):
        return [f"{location}: expected type {expected_type}"]

    if "oneOf" in schema:
        outcomes = [
            validate_instance(
                instance,
                candidate,
                schema_path,
                documents,
                location,
                root_schema,
            )
            for candidate in schema["oneOf"]
        ]
        valid_count = sum(1 for outcome in outcomes if not outcome)
        if valid_count != 1:
            errors.append(f"{location}: oneOf matched {valid_count} branches")

    if "anyOf" in schema:
        outcomes = [
            validate_instance(
                instance,
                candidate,
                schema_path,
                documents,
                location,
                root_schema,
            )
            for candidate in schema["anyOf"]
        ]
        if not any(not outcome for outcome in outcomes):
            errors.append(f"{location}: anyOf matched no branches")

    for candidate in schema.get("allOf", []):
        errors.extend(
            validate_instance(
                instance,
                candidate,
                schema_path,
                documents,
                location,
                root_schema,
            )
        )

    if "if" in schema:
        condition_errors = validate_instance(
            instance,
            schema["if"],
            schema_path,
            documents,
            location,
            root_schema,
        )
        if not condition_errors and "then" in schema:
            errors.extend(
                validate_instance(
                    instance,
                    schema["then"],
                    schema_path,
                    documents,
                    location,
                    root_schema,
                )
            )

    if "not" in schema:
        negative_errors = validate_instance(
            instance,
            schema["not"],
            schema_path,
            documents,
            location,
            root_schema,
        )
        if not negative_errors:
            errors.append(f"{location}: instance matches prohibited schema")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{location}: shorter than minLength")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{location}: longer than maxLength")
        if "pattern" in schema and re.fullmatch(schema["pattern"], instance) is None:
            errors.append(f"{location}: pattern mismatch")
        if schema.get("format") == "date-time":
            try:
                parsed = datetime.fromisoformat(instance.replace("Z", "+00:00"))
                if parsed.tzinfo is None or parsed.utcoffset() is None:
                    raise ValueError("timezone missing")
            except ValueError:
                errors.append(f"{location}: invalid date-time")
        if schema.get("format") == "uuid":
            try:
                UUID(instance)
            except ValueError:
                errors.append(f"{location}: invalid UUID")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{location}: below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{location}: above maximum")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{location}: fewer than minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{location}: more than maxItems")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in instance]
            if len(set(encoded)) != len(encoded):
                errors.append(f"{location}: duplicate array item")
        if "items" in schema:
            for index, item in enumerate(instance):
                errors.extend(
                    validate_instance(
                        item,
                        schema["items"],
                        schema_path,
                        documents,
                        f"{location}[{index}]",
                        root_schema,
                    )
                )
        if "contains" in schema:
            match_count = 0
            for index, item in enumerate(instance):
                item_errors = validate_instance(
                    item,
                    schema["contains"],
                    schema_path,
                    documents,
                    f"{location}[{index}]",
                    root_schema,
                )
                if not item_errors:
                    match_count += 1
            minimum = schema.get("minContains", 1)
            if match_count < minimum:
                errors.append(
                    f"{location}: contains matched {match_count}, expected at least {minimum}"
                )

    if isinstance(instance, dict):
        for required_key in schema.get("required", []):
            if required_key not in instance:
                errors.append(f"{location}: missing required property {required_key}")

        property_names = schema.get("propertyNames")
        if property_names is not None:
            for key in instance:
                errors.extend(
                    validate_instance(
                        key,
                        property_names,
                        schema_path,
                        documents,
                        f"{location}{{key:{key}}}",
                        root_schema,
                    )
                )

        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(
                    validate_instance(
                        value,
                        properties[key],
                        schema_path,
                        documents,
                        f"{location}.{key}",
                        root_schema,
                    )
                )

        additional = schema.get("additionalProperties", True)
        unknown = [key for key in instance if key not in properties]

        if additional is False:
            for key in unknown:
                errors.append(f"{location}: unexpected property {key}")
        elif isinstance(additional, dict):
            for key in unknown:
                errors.extend(
                    validate_instance(
                        instance[key],
                        additional,
                        schema_path,
                        documents,
                        f"{location}.{key}",
                        root_schema,
                    )
                )

        if "minProperties" in schema and len(instance) < schema["minProperties"]:
            errors.append(f"{location}: fewer than minProperties")

    return errors


def inspect_schema_repository(
    root: Path,
    schema_paths: list[Path],
    documents: dict[Path, object],
) -> list[str]:
    errors: list[str] = []
    seen_ids: dict[str, Path] = {}

    for schema_path in schema_paths:
        schema = documents[schema_path]

        if not isinstance(schema, dict):
            fail(errors, f"{relative(root, schema_path)}: schema root must be object")
            continue

        if schema.get("$schema") != DRAFT:
            fail(errors, f"{relative(root, schema_path)}: JSON Schema draft must be 2020-12")

        schema_id = schema.get("$id")
        if not isinstance(schema_id, str) or not schema_id:
            fail(errors, f"{relative(root, schema_path)}: missing $id")
        elif schema_id in seen_ids:
            fail(
                errors,
                f"{relative(root, schema_path)}: duplicate $id also used by "
                f"{relative(root, seen_ids[schema_id])}",
            )
        else:
            seen_ids[schema_id] = schema_path

        if not isinstance(schema.get("title"), str) or not schema["title"]:
            fail(errors, f"{relative(root, schema_path)}: missing title")

        for ref in walk_refs(schema):
            try:
                resolve_ref(schema_path, ref, documents)
            except ValidationFailure as exc:
                fail(errors, str(exc))

    return errors


def inspect_a7_schema(
    root: Path,
    documents: dict[Path, object],
) -> list[str]:
    errors: list[str] = []
    path = (root / "contracts/evidence/v1/action-ledger-record.schema.json").resolve()
    schema = documents[path]
    rules = schema.get("allOf", [])

    if "authorization" in schema.get("required", []):
        fail(errors, "SP-A7: authorization must not be globally required")

    actor_types = (
        schema.get("$defs", {})
        .get("AuthorityPrincipalReferenceV1", {})
        .get("properties", {})
        .get("principal_type", {})
        .get("enum")
    )
    if actor_types != ["human", "service"]:
        fail(errors, "SP-A7: authority actor types must remain human/service")

    def rule_for(kind: str):
        for rule in rules:
            if (
                rule.get("if", {})
                .get("properties", {})
                .get("record_kind", {})
                .get("const")
                == kind
            ):
                return rule
        return None

    requested = rule_for("ACTION_REQUESTED")
    if requested is None:
        fail(errors, "SP-A7: ACTION_REQUESTED lifecycle rule missing")
    else:
        props = requested.get("then", {}).get("properties", {})
        if props.get("authorization", {}).get("type") != "null":
            fail(errors, "SP-A7: ACTION_REQUESTED must not contain authorization")
        if props.get("approval", {}).get("type") != "null":
            fail(errors, "SP-A7: ACTION_REQUESTED must not contain approval")

    authorized = rule_for("AUTHORIZATION_DECIDED")
    if authorized is None:
        fail(errors, "SP-A7: AUTHORIZATION_DECIDED lifecycle rule missing")
    else:
        then = authorized.get("then", {})
        if "authorization" not in then.get("required", []):
            fail(errors, "SP-A7: AUTHORIZATION_DECIDED must require authorization")
        if then.get("properties", {}).get("approval", {}).get("type") != "null":
            fail(errors, "SP-A7: AUTHORIZATION_DECIDED must not contain approval")

    approved = rule_for("APPROVAL_DECIDED")
    if approved is None:
        fail(errors, "SP-A7: APPROVAL_DECIDED lifecycle rule missing")
    else:
        then = approved.get("then", {})
        for key in ("authorization", "approval"):
            if key not in then.get("required", []):
                fail(errors, f"SP-A7: APPROVAL_DECIDED must require {key}")
        decision = (
            then.get("properties", {})
            .get("authorization", {})
            .get("properties", {})
            .get("decision", {})
            .get("const")
        )
        if decision != "REQUIRE_APPROVAL":
            fail(
                errors,
                "SP-A7: APPROVAL_DECIDED must bind to REQUIRE_APPROVAL authorization",
            )

    return errors


def inspect_a8_schema(
    root: Path,
    documents: dict[Path, object],
) -> list[str]:
    errors: list[str] = []
    path = (root / "contracts/observability/v1/metric-observation.schema.json").resolve()
    schema = documents[path]
    dimensions = schema.get("properties", {}).get("dimensions", {})

    if dimensions.get("additionalProperties") is not False:
        fail(errors, "SP-A8: metric dimensions must deny unknown keys by default")

    actual = set(dimensions.get("properties", {}))
    if actual != SAFE_METRIC_DIMENSIONS:
        fail(
            errors,
            "SP-A8: metric dimension allowlist changed without contract review: "
            f"{sorted(actual)}",
        )

    return errors


def inspect_a9_schema(
    root: Path,
    documents: dict[Path, object],
) -> list[str]:
    errors: list[str] = []

    provenance_path = (
        root / "contracts/release/v1/release-provenance.schema.json"
    ).resolve()
    action_path = (
        root / "contracts/release/v1/release-action-binding.schema.json"
    ).resolve()
    binding_path = (
        root / "contracts/release/v1/release-binding-decision.schema.json"
    ).resolve()

    provenance = documents[provenance_path]
    action = documents[action_path]
    binding = documents[binding_path]

    if action.get("properties", {}).get("evidence_refs", {}).get("minItems") != 1:
        fail(errors, "SP-A9: release-action evidence_refs must be non-empty")

    if binding.get("properties", {}).get("evidence_refs", {}).get("minItems") != 1:
        fail(errors, "SP-A9: binding-decision evidence_refs must be non-empty")

    if provenance.get("properties", {}).get("evidence_refs", {}).get("minItems") != 1:
        fail(errors, "SP-A9: top-level evidence_refs must be non-empty")

    match_branch = None
    for branch in binding.get("allOf", [{}])[0].get("oneOf", []):
        if branch.get("properties", {}).get("overall_result", {}).get("const") == "MATCH":
            match_branch = branch
            break

    if match_branch is None:
        fail(errors, "SP-A9: MATCH aggregate binding branch missing")
    elif match_branch.get("properties", {}).get("source_binding", {}).get("const") != "MATCH":
        fail(errors, "SP-A9: MATCH aggregate must require source_binding=MATCH")

    return errors


def non_empty_evidence(record: dict, errors: list[str]) -> None:
    evidence = record.get("evidence_refs")
    if not isinstance(evidence, list) or not evidence:
        fail(errors, "SP-A9: required evidence_refs must be non-empty")


def semantic_release_errors(record: object) -> list[str]:
    errors: list[str] = []

    if not isinstance(record, dict):
        return ["SP-A9: release provenance must be object"]

    repository = record.get("repository")
    source = record.get("source") or {}
    source_sha = source.get("commit_sha")

    if source.get("repository") != repository:
        fail(errors, "SP-A9: provenance repository must equal source.repository")

    for index, ci in enumerate(record.get("ci_bindings", [])):
        if ci.get("repository") != repository:
            fail(errors, f"SP-A9: ci_bindings[{index}].repository mismatch")
        if ci.get("source_commit_sha") != source_sha:
            fail(errors, f"SP-A9: ci_bindings[{index}].source_commit_sha mismatch")

    for index, build in enumerate(record.get("builds", [])):
        if build.get("repository") != repository:
            fail(errors, f"SP-A9: builds[{index}].repository mismatch")
        if build.get("source_commit_sha") != source_sha:
            fail(errors, f"SP-A9: builds[{index}].source_commit_sha mismatch")

    for index, artifact in enumerate(record.get("artifacts", [])):
        artifact_sha = artifact.get("source_commit_sha")
        if artifact_sha is not None and artifact_sha != source_sha:
            fail(errors, f"SP-A9: artifacts[{index}].source_commit_sha mismatch")

    release_class = record.get("release_class")
    release_action = record.get("release_action")
    environment_context = record.get("environment_context")
    canonical_ref = (record.get("canonical_release_record") or {}).get("record_ref")

    if release_action is not None:
        if release_action.get("source_commit_sha") != source_sha:
            fail(errors, "SP-A9: release-action source SHA mismatch")
        if release_action.get("release_identity") != record.get("release_identity"):
            fail(errors, "SP-A9: release-action release identity mismatch")
        if release_action.get("release_record_ref") != canonical_ref:
            fail(errors, "SP-A9: release-action canonical record reference mismatch")

        action_kind = release_action.get("action_kind")
        allowed = RELEASE_CLASS_ACTIONS.get(release_class, set())
        if action_kind not in allowed:
            fail(
                errors,
                f"SP-A9: release class {release_class} cannot use action {action_kind}",
            )

        if action_kind == "deployment":
            if not isinstance(environment_context, dict):
                fail(errors, "SP-A9: deployment requires environment_context")
            else:
                expected = environment_context.get("environment_identity_ref")
                if release_action.get("environment_ref") != expected:
                    fail(
                        errors,
                        "SP-A9: deployment environment_ref must equal "
                        "environment_context.environment_identity_ref",
                    )
        else:
            if environment_context is not None:
                fail(
                    errors,
                    "SP-A9: non-deployment release action must not claim runtime environment",
                )
            if release_action.get("environment_ref") is not None:
                fail(
                    errors,
                    "SP-A9: non-deployment release action environment_ref must be null",
                )

        non_empty_evidence(release_action, errors)

    for section_name in ("authorization", "verification", "acceptance"):
        section = record.get(section_name)
        if isinstance(section, dict):
            non_empty_evidence(section, errors)

    for index, recovery in enumerate(record.get("failure_recovery", [])):
        if not recovery.get("evidence_refs"):
            fail(errors, f"SP-A9: failure_recovery[{index}] evidence_refs must be non-empty")

    if release_class in CI_BUILD_REQUIRED:
        if not record.get("ci_bindings"):
            fail(errors, f"SP-A9: {release_class} requires CI binding evidence")
        if not record.get("builds"):
            fail(errors, f"SP-A9: {release_class} requires build identity")

    binding = record.get("binding_decision")
    if isinstance(binding, dict):
        if binding.get("release_record_ref") != canonical_ref:
            fail(errors, "SP-A9: binding-decision canonical record reference mismatch")

        statuses = [binding.get(field) for field in BINDING_FIELDS]
        if "MISMATCH" in statuses:
            expected_overall = "MISMATCH"
        elif "INDETERMINATE" in statuses:
            expected_overall = "INDETERMINATE"
        else:
            expected_overall = "MATCH"

        if binding.get("overall_result") != expected_overall:
            fail(
                errors,
                f"SP-A9: aggregate binding result must be {expected_overall}",
            )

        if binding.get("overall_result") == "MATCH":
            if binding.get("source_binding") != "MATCH":
                fail(errors, "SP-A9: successful binding requires source_binding=MATCH")

            if record.get("ci_bindings"):
                if binding.get("ci_binding") != "MATCH":
                    fail(errors, "SP-A9: present CI evidence requires ci_binding=MATCH")
            elif binding.get("ci_binding") != "NOT_APPLICABLE":
                fail(errors, "SP-A9: absent CI evidence requires ci_binding=NOT_APPLICABLE")

            if record.get("builds"):
                if binding.get("build_binding") != "MATCH":
                    fail(errors, "SP-A9: present build identity requires build_binding=MATCH")
            elif binding.get("build_binding") != "NOT_APPLICABLE":
                fail(
                    errors,
                    "SP-A9: absent build identity requires build_binding=NOT_APPLICABLE",
                )

            if record.get("artifacts"):
                if binding.get("artifact_binding") != "MATCH":
                    fail(errors, "SP-A9: present artifacts require artifact_binding=MATCH")
            elif binding.get("artifact_binding") != "NOT_APPLICABLE":
                fail(
                    errors,
                    "SP-A9: absent artifacts require artifact_binding=NOT_APPLICABLE",
                )

            if release_action is not None:
                if binding.get("release_action_binding") != "MATCH":
                    fail(
                        errors,
                        "SP-A9: present release action requires release_action_binding=MATCH",
                    )
            elif binding.get("release_action_binding") != "NOT_APPLICABLE":
                fail(
                    errors,
                    "SP-A9: absent release action requires release_action_binding=NOT_APPLICABLE",
                )

            if isinstance(record.get("verification"), dict):
                if binding.get("verification_binding") != "MATCH":
                    fail(
                        errors,
                        "SP-A9: present verification requires verification_binding=MATCH",
                    )
            elif binding.get("verification_binding") != "NOT_APPLICABLE":
                fail(
                    errors,
                    "SP-A9: absent verification requires verification_binding=NOT_APPLICABLE",
                )

            if (
                isinstance(release_action, dict)
                and release_action.get("action_kind") == "deployment"
            ):
                if binding.get("environment_binding") != "MATCH":
                    fail(
                        errors,
                        "SP-A9: deployment requires environment_binding=MATCH",
                    )
            elif binding.get("environment_binding") != "NOT_APPLICABLE":
                fail(
                    errors,
                    "SP-A9: non-deployment requires environment_binding=NOT_APPLICABLE",
                )

            non_empty_evidence(binding, errors)

    lifecycle = record.get("lifecycle_state")
    if lifecycle in {"VERIFIED", "ACCEPTED"}:
        if not isinstance(binding, dict) or binding.get("overall_result") != "MATCH":
            fail(
                errors,
                f"SP-A9: {lifecycle} requires binding_decision.overall_result=MATCH",
            )
        if source.get("binding_status") != "MATCH":
            fail(errors, f"SP-A9: {lifecycle} requires source binding_status=MATCH")

    return errors


def validate_examples(
    root: Path,
    documents: dict[Path, object],
) -> list[str]:
    errors: list[str] = []

    discovered = {
        relative(root, path)
        for path in (root / "contracts").rglob("*.example.json")
    }

    unknown = sorted(discovered - set(EXAMPLE_SCHEMA_MAP))
    if unknown:
        fail(
            errors,
            "unregistered contract examples: " + ", ".join(unknown),
        )

    missing = sorted(set(EXAMPLE_SCHEMA_MAP) - discovered)
    if missing:
        fail(
            errors,
            "registered contract examples missing: " + ", ".join(missing),
        )

    for example_ref, schema_ref in EXAMPLE_SCHEMA_MAP.items():
        example_path = (root / example_ref).resolve()
        schema_path = (root / schema_ref).resolve()
        example = documents[example_path]
        schema = documents[schema_path]

        instance_errors = validate_instance(
            example,
            schema,
            schema_path,
            documents,
        )
        errors.extend(
            f"{example_ref}: {message}"
            for message in instance_errors
        )

        if example_ref.endswith("medicamentos-release-provenance.example.json"):
            errors.extend(semantic_release_errors(example))

    return errors


def run_negative_self_tests(
    root: Path,
    documents: dict[Path, object],
) -> list[str]:
    errors: list[str] = []

    release_example_path = (
        root
        / "contracts/release/v1/examples/"
        "medicamentos-release-provenance.example.json"
    ).resolve()
    release_schema_path = (
        root / "contracts/release/v1/release-provenance.schema.json"
    ).resolve()
    release_example = documents[release_example_path]
    release_schema = documents[release_schema_path]

    def expect_release_rejected(name: str, mutate, semantic_only: bool = False):
        candidate = copy.deepcopy(release_example)
        mutate(candidate)
        schema_errors = validate_instance(
            candidate,
            release_schema,
            release_schema_path,
            documents,
        )
        semantic_errors = semantic_release_errors(candidate)
        if semantic_only:
            rejected = bool(semantic_errors)
        else:
            rejected = bool(schema_errors or semantic_errors)
        if not rejected:
            fail(errors, f"self-test did not reject {name}")

    expect_release_rejected(
        "repository mismatch",
        lambda value: value["source"].__setitem__(
            "repository",
            "node63labs/not-medicamentos",
        ),
        semantic_only=True,
    )

    expect_release_rejected(
        "CI source SHA mismatch",
        lambda value: value["ci_bindings"][0].__setitem__(
            "source_commit_sha",
            "2222222222222222222222222222222222222222",
        ),
        semantic_only=True,
    )

    expect_release_rejected(
        "successful binding with source N/A",
        lambda value: value["binding_decision"].__setitem__(
            "source_binding",
            "NOT_APPLICABLE",
        ),
    )

    def make_rc05_deployment(value):
        value["release_class"] = "RC-05"

    expect_release_rejected(
        "RC-05 deployment",
        make_rc05_deployment,
    )

    expect_release_rejected(
        "empty verification evidence",
        lambda value: value["verification"].__setitem__("evidence_refs", []),
    )

    a7_example_path = (
        root
        / "contracts/evidence/v1/examples/"
        "medicamentos-action-ledger.example.json"
    ).resolve()
    a7_schema_path = (
        root / "contracts/evidence/v1/action-ledger-record.schema.json"
    ).resolve()
    a7_example = documents[a7_example_path]
    a7_schema = documents[a7_schema_path]

    def expect_a7_rejected(name: str, mutate):
        candidate = copy.deepcopy(a7_example)
        mutate(candidate)
        candidate_errors = validate_instance(
            candidate,
            a7_schema,
            a7_schema_path,
            documents,
        )
        if not candidate_errors:
            fail(errors, f"self-test did not reject {name}")

    def auth_decision_with_approval(value):
        value["record_kind"] = "AUTHORIZATION_DECIDED"
        value["approval"] = {
            "decision": "APPROVED",
            "approval_ref": "example://approval/should-not-exist",
            "decided_at": "2026-09-22T09:00:00Z",
        }
        value["execution"] = {
            "state": "NOT_STARTED",
            "outcome_code": None,
            "execution_ref": None,
        }
        value["verification"] = {
            "state": "NOT_APPLICABLE",
            "verification_ref": None,
        }

    expect_a7_rejected(
        "authorization decision carrying approval",
        auth_decision_with_approval,
    )

    def approval_without_require_approval(value):
        value["record_kind"] = "APPROVAL_DECIDED"
        value["authorization"]["decision"] = "ALLOW"
        value["approval"] = {
            "decision": "APPROVED",
            "approval_ref": "example://approval/001",
            "decided_at": "2026-09-22T09:00:00Z",
        }
        value["execution"] = {
            "state": "NOT_STARTED",
            "outcome_code": None,
            "execution_ref": None,
        }
        value["verification"] = {
            "state": "NOT_APPLICABLE",
            "verification_ref": None,
        }

    expect_a7_rejected(
        "approval without REQUIRE_APPROVAL authorization",
        approval_without_require_approval,
    )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    contracts_root = root / "contracts"

    if not contracts_root.is_dir():
        print("NODE63_CONTRACT_VALIDATION_ERROR=contracts directory missing")
        return 1

    json_paths = sorted(contracts_root.rglob("*.json"))
    schema_paths = sorted(contracts_root.rglob("*.schema.json"))

    documents: dict[Path, object] = {}
    errors: list[str] = []

    for path in json_paths:
        try:
            documents[path.resolve()] = load_json(path)
        except ValidationFailure as exc:
            errors.append(str(exc))

    if not errors:
        errors.extend(
            inspect_schema_repository(
                root,
                [path.resolve() for path in schema_paths],
                documents,
            )
        )
        errors.extend(inspect_a7_schema(root, documents))
        errors.extend(inspect_a8_schema(root, documents))
        errors.extend(inspect_a9_schema(root, documents))
        errors.extend(validate_examples(root, documents))
        errors.extend(run_negative_self_tests(root, documents))

    if errors:
        for message in errors:
            print(f"NODE63_CONTRACT_VALIDATION_ERROR={message}")
        return 1

    ref_count = sum(
        1
        for path in schema_paths
        for _ in walk_refs(documents[path.resolve()])
    )
    example_count = len(list(contracts_root.rglob("*.example.json")))

    print(
        json.dumps(
            {
                "schema": "node63-contract-validation/v1",
                "schemas": len(schema_paths),
                "examples": example_count,
                "refs_checked": ref_count,
                "semantic_profiles": ["SP-A7", "SP-A8", "SP-A9"],
                "negative_self_tests": 7,
                "result": "PASS",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
