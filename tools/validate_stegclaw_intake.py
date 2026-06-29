from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DECLARATION = ROOT / "core_lite" / "stegclaw_target_intake.json"
REPORTS = ROOT / "reports"

REQUIRED = [
    "standing_envelope.json",
    "standing_receipt.json",
    "ingestion_candidate.json",
    "ingestion_candidate_receipt.json",
    "outbound_envelope.json",
    "outbound_receipt.json",
    "live_integration_manifest.json",
]


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    data = json.loads(DECLARATION.read_text(encoding="utf-8"))
    missing = [name for name in REQUIRED if name not in data.get("required_artifacts", [])]
    rules = data.get("local_rules", {})
    errors = list(missing)
    if rules.get("requires_workstream_binding") is not True:
        errors.append("requires_workstream_binding")
    if rules.get("requires_transition_block") is not True:
        errors.append("requires_transition_block")
    if rules.get("runtime_connector_installed") is not False:
        errors.append("runtime_connector_installed")
    report = {
        "schema": "core_lite.stegclaw_target_intake_report.v1",
        "target_repo": data.get("target_repo"),
        "upstream_repo": data.get("upstream_repo"),
        "role": data.get("role", []),
        "missing_required_artifacts": missing,
        "validation_errors": errors,
        "decision": "ALLOW" if not errors else "FAIL_CLOSED",
    }
    (REPORTS / "stegclaw_target_intake.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["decision"])
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
