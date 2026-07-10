#!/usr/bin/env python3
"""Schema validator for the inference-lab version-pin matrix.

Usage:
    python3 pins/validate_pins.py [FILE ...]

With no arguments, validates pins/pins.yaml and every YAML file under
pins/examples/. Exit code 0 = all files valid; 1 = validation errors;
2 = usage/environment error. Format spec: docs/interfaces.md §3 + ADR-0001.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("error: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent

COMPONENTS = {
    "serving-contracts", "infergate", "infergate-mock", "inferbench", "fleetlab",
    "inferops", "engine-vllm", "engine-llamacpp", "engine-sglang", "model",
    "hardware", "otel-semconv", "other",
}
KINDS = {
    "contract-bundle", "container-image", "binary", "git-commit", "model-revision",
    "config-bundle", "dashboard-bundle", "hardware-profile", "spec-version",
}
PROVENANCE = {"measured", "source-reported", "assumed"}
MILESTONES = {f"I{n}" for n in range(1, 9)}

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_ENTRY_FIELDS = ("id", "component", "kind", "version", "provenance",
                         "date", "proven_at", "source")
OPTIONAL_ENTRY_FIELDS = ("digest", "reverify", "notes")


def check_date(value: object, where: str, errors: list[str]) -> None:
    if isinstance(value, date):  # YAML may parse unquoted dates natively
        return
    if not isinstance(value, str) or not DATE_RE.match(value):
        errors.append(f"{where}: date must be an ISO date (YYYY-MM-DD), got {value!r}")
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        errors.append(f"{where}: {value!r} is not a real calendar date")


def validate_entry(entry: object, idx: int, seen_ids: set[str], errors: list[str]) -> None:
    where = f"artifacts[{idx}]"
    if not isinstance(entry, dict):
        errors.append(f"{where}: entry must be a mapping, got {type(entry).__name__}")
        return
    eid = entry.get("id")
    if isinstance(eid, str):
        where = f"artifacts[{idx}] ({eid})"

    for field in REQUIRED_ENTRY_FIELDS:
        if field not in entry:
            errors.append(f"{where}: missing required field '{field}'")
    unknown = set(entry) - set(REQUIRED_ENTRY_FIELDS) - set(OPTIONAL_ENTRY_FIELDS)
    if unknown:
        errors.append(f"{where}: unknown field(s): {', '.join(sorted(unknown))}")

    if "id" in entry:
        if not isinstance(eid, str) or not ID_RE.match(eid):
            errors.append(f"{where}: id must be kebab-case ([a-z0-9-]), got {eid!r}")
        elif eid in seen_ids:
            errors.append(f"{where}: duplicate id {eid!r}")
        else:
            seen_ids.add(eid)

    if "component" in entry and entry["component"] not in COMPONENTS:
        errors.append(f"{where}: component {entry['component']!r} not in allowed set "
                      f"{sorted(COMPONENTS)}")
    if "kind" in entry and entry["kind"] not in KINDS:
        errors.append(f"{where}: kind {entry['kind']!r} not in allowed set {sorted(KINDS)}")
    if "provenance" in entry and entry["provenance"] not in PROVENANCE:
        errors.append(f"{where}: provenance {entry['provenance']!r} must be one of "
                      f"{sorted(PROVENANCE)}")

    if "version" in entry:
        v = entry["version"]
        if v is not None and (not isinstance(v, str) or not v.strip()):
            errors.append(f"{where}: version must be a non-empty string or null "
                          f"(null only while unpinned), got {v!r}")

    if "date" in entry:
        check_date(entry["date"], f"{where}.date", errors)

    if "proven_at" in entry:
        pa = entry["proven_at"]
        if not isinstance(pa, list):
            errors.append(f"{where}: proven_at must be a list (may be empty), got {pa!r}")
        else:
            bad = [m for m in pa if m not in MILESTONES]
            if bad:
                errors.append(f"{where}: proven_at values {bad!r} not in I1..I8")

    if "source" in entry and (not isinstance(entry["source"], str) or not entry["source"].strip()):
        errors.append(f"{where}: source must be a non-empty string (URL or in-program ref)")

    # digest: mandatory + shape-checked for container images; shape-checked if present otherwise
    digest = entry.get("digest")
    if entry.get("kind") == "container-image":
        if not isinstance(digest, str) or not DIGEST_RE.match(digest):
            errors.append(f"{where}: kind 'container-image' requires digest matching "
                          f"'sha256:<64 hex>', got {digest!r}")
    elif digest is not None and (not isinstance(digest, str) or not digest.strip()):
        errors.append(f"{where}: digest, when present, must be a non-empty string")

    if "reverify" in entry and not isinstance(entry["reverify"], bool):
        errors.append(f"{where}: reverify must be a boolean")
    if "notes" in entry and not isinstance(entry["notes"], str):
        errors.append(f"{where}: notes must be a string")


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"YAML parse error: {exc}"]

    if not isinstance(data, dict):
        return [f"top level must be a mapping, got {type(data).__name__}"]

    if data.get("schema_version") != 1:
        errors.append(f"schema_version must be 1, got {data.get('schema_version')!r}")
    if "updated" not in data:
        errors.append("missing top-level field 'updated'")
    else:
        check_date(data["updated"], "updated", errors)

    rule = data.get("comparability_rule")
    if not isinstance(rule, str) or "comparable" not in rule:
        errors.append("comparability_rule must be present and state the normative "
                      "benchmark comparability rule")

    me = data.get("milestone_evidence")
    if not isinstance(me, dict):
        errors.append(f"milestone_evidence must be a mapping (may be empty), got {me!r}")
    else:
        for key, value in me.items():
            if key not in MILESTONES:
                errors.append(f"milestone_evidence key {key!r} not in I1..I8")
            if not isinstance(value, str) or not value.strip():
                errors.append(f"milestone_evidence[{key!r}] must be a non-empty path/link")

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list):
        errors.append(f"artifacts must be a list (may be empty), got {artifacts!r}")
    else:
        seen_ids: set[str] = set()
        for idx, entry in enumerate(artifacts):
            validate_entry(entry, idx, seen_ids, errors)

    unknown_top = set(data) - {"schema_version", "updated", "comparability_rule",
                               "milestone_evidence", "artifacts"}
    if unknown_top:
        errors.append(f"unknown top-level field(s): {', '.join(sorted(unknown_top))}")

    return errors


def main(argv: list[str]) -> int:
    if argv:
        paths = [Path(a) for a in argv]
    else:
        paths = [REPO_ROOT / "pins" / "pins.yaml"]
        paths += sorted((REPO_ROOT / "pins" / "examples").glob("*.yaml"))

    exit_code = 0
    for path in paths:
        if not path.is_file():
            print(f"FAIL  {path}: file not found")
            exit_code = 1
            continue
        errors = validate_file(path)
        if errors:
            exit_code = 1
            print(f"FAIL  {path}")
            for err in errors:
                print(f"      - {err}")
        else:
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                n = len(data.get("artifacts", []))
            except Exception:
                n = 0
            print(f"OK    {path} ({n} artifact entr{'y' if n == 1 else 'ies'})")
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
