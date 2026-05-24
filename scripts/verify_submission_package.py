from __future__ import annotations

import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "dist" / "ClawFlow_submission_package.zip"

REQUIRED_ENTRIES = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "GOVERNANCE.md",
    "ROADMAP.md",
    "pyproject.toml",
    "config.yaml",
    "Dockerfile",
    "docker-compose.yml",
    "Makefile",
    "clawflow/core/runtime.py",
    "clawflow/core/executor.py",
    "clawflow/tools/registry.py",
    "clawflow/gateway/cli.py",
    "clawflow/gateway/api.py",
    "applications/research_assistant/app.py",
    "applications/personal_assistant/app.py",
    "applications/safe_tool_call/app.py",
    "applications/multi_agent_project_analysis/app.py",
    "applications/rag_assistant/app.py",
    "docs/technical_report.md",
    "docs/technical_report.docx",
    "docs/technical_report.pdf",
    "slides/ClawFlow_presentation.pptx",
    "slides/ClawFlow_presentation.pdf",
    "docs/assets/screenshots/web_home.png",
    "docs/assets/screenshots/cli_research_application.png",
    "docs/assets/diagrams/architecture.png",
    "docs/assets/diagrams/agentos_kernel.png",
    "docs/assets/figures/benchmark_latency.png",
    "outputs/benchmark_results.json",
    "outputs/evaluation_leaderboard.json",
    "outputs/failure_recovery_report.md",
    "tests/test_runtime.py",
    "tests/test_api.py",
    "scripts/run_benchmark.py",
    "scripts/verify_deliverables.py",
]


def main() -> dict:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"missing submission package: {ZIP_PATH}")
    with zipfile.ZipFile(ZIP_PATH) as archive:
        entries = set(archive.namelist())
        missing = [entry for entry in REQUIRED_ENTRIES if entry not in entries]
    manifest = {
        "package": str(ZIP_PATH.relative_to(ROOT)),
        "entries": len(entries),
        "bytes": ZIP_PATH.stat().st_size,
        "required_entries": REQUIRED_ENTRIES,
        "missing": missing,
        "status": "ok" if not missing else "failed",
    }
    output_json = ROOT / "outputs" / "submission_package_manifest.json"
    output_md = ROOT / "outputs" / "submission_package_manifest.md"
    output_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# ClawFlow Submission Package Manifest",
        "",
        f"- Package: `{manifest['package']}`",
        f"- Entries: {manifest['entries']}",
        f"- Bytes: {manifest['bytes']}",
        f"- Status: {manifest['status']}",
        "",
        "## Required Content Check",
    ]
    lines.extend(f"- [{'x' if item not in missing else ' '}] `{item}`" for item in REQUIRED_ENTRIES)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if missing:
        raise SystemExit("missing required entries: " + ", ".join(missing))
    return manifest


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=2))
