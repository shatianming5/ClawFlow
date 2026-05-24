from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_ASSETS = [
    "README.md",
    "LICENSE",
    ".github/workflows/ci.yml",
    "docs/technical_report.md",
    "docs/technical_report.docx",
    "docs/technical_report.pdf",
    "slides/ClawFlow_presentation.pptx",
    "slides/ClawFlow_presentation.pdf",
    "docs/openapi.json",
    "outputs/benchmark_results.json",
    "outputs/evaluation_leaderboard.json",
    "outputs/failure_recovery_report.md",
    "dist/clawflow_release.zip",
    "dist/ClawFlow_submission_package.zip",
]


def git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_text(args: list[str], default: str = "") -> str:
    result = git(args)
    if result.returncode != 0:
        return default
    return result.stdout.strip()


def check_file(path: str) -> dict[str, Any]:
    full = ROOT / path
    return {
        "path": path,
        "exists": full.exists(),
        "bytes": full.stat().st_size if full.exists() else 0,
    }


def load_json(path: str) -> dict[str, Any]:
    full = ROOT / path
    if not full.exists():
        return {}
    try:
        return json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"error": "invalid_json"}


def build_report(require_remote: bool = False, require_clean: bool = False) -> dict[str, Any]:
    inside_repo = git(["rev-parse", "--is-inside-work-tree"]).returncode == 0
    branch = git_text(["branch", "--show-current"], "unknown")
    commit = git_text(["rev-parse", "--short", "HEAD"], "unknown")
    remote = git_text(["remote", "get-url", "origin"], "")
    dirty_files = [line for line in git_text(["status", "--short"]).splitlines() if line.strip()]
    assets = [check_file(path) for path in REQUIRED_ASSETS]
    missing_assets = [item["path"] for item in assets if not item["exists"] or item["bytes"] <= 0]

    verification = load_json("outputs/deliverable_verification.json")
    release = load_json("outputs/release_manifest.json")
    benchmark = load_json("outputs/benchmark_results.json")

    errors: list[str] = []
    warnings: list[str] = []
    if not inside_repo:
        errors.append("not a git repository")
    if missing_assets:
        errors.append("missing release assets: " + ", ".join(missing_assets))
    if verification.get("status") != "ok":
        warnings.append("deliverable verification has not been run or is not ok")
    if not release.get("artifact"):
        warnings.append("release manifest has not been generated")
    if benchmark.get("success_rate", 0) < 0.8:
        warnings.append("benchmark success rate is below 0.8 or benchmark is missing")
    if dirty_files:
        message = f"worktree has {len(dirty_files)} changed files"
        if require_clean:
            errors.append(message)
        else:
            warnings.append(message)
    if not remote:
        message = "origin remote is not configured; push cannot run until a GitHub URL is added"
        if require_remote:
            errors.append(message)
        else:
            warnings.append(message)

    status = "ready"
    if errors:
        status = "failed"
    elif remote == "":
        status = "needs_remote"
    elif warnings:
        status = "ready_with_warnings"

    return {
        "status": status,
        "branch": branch,
        "commit": commit,
        "origin": remote or None,
        "git_repository": inside_repo,
        "dirty_file_count": len(dirty_files),
        "dirty_files": dirty_files[:50],
        "required_assets": assets,
        "deliverable_verification": verification,
        "release_manifest": release,
        "benchmark_summary": {
            "total_tasks": benchmark.get("total_tasks"),
            "success_rate": benchmark.get("success_rate"),
            "average_latency": benchmark.get("average_latency"),
            "trace_event_count": benchmark.get("trace_event_count"),
        },
        "warnings": warnings,
        "errors": errors,
        "push_commands": [
            "git remote add origin <github-repo-url>",
            "git push -u origin main",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check ClawFlow GitHub publish readiness.")
    parser.add_argument("--require-remote", action="store_true", help="Fail when origin is missing.")
    parser.add_argument("--require-clean", action="store_true", help="Fail when the git worktree is dirty.")
    parser.add_argument("--write", action="store_true", help="Write outputs/publish_readiness.json.")
    args = parser.parse_args(argv)

    report = build_report(require_remote=args.require_remote, require_clean=args.require_clean)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.write:
        output = ROOT / "outputs" / "publish_readiness.json"
        output.parent.mkdir(exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
