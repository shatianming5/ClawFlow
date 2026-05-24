from __future__ import annotations

import json
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_PREFIXES = {
    ".git/",
    "__pycache__/",
    ".pytest_cache/",
    "dist/",
    "outputs/checkpoints/",
    "outputs/outbox/",
    "outputs/calendar/",
}
EXCLUDE_SUFFIXES = {".pyc", ".sqlite3", ".log", ".pid"}


def tracked_files() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode == 0 and completed.stdout.strip():
        return [ROOT / line for line in completed.stdout.splitlines() if line.strip()]
    return [path for path in ROOT.rglob("*") if path.is_file()]


def include(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if any(rel.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
        return False
    if any(rel.endswith(suffix) for suffix in EXCLUDE_SUFFIXES):
        return False
    return True


def main() -> dict:
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    output_zip = dist / "clawflow_release.zip"
    submission_zip = dist / "ClawFlow_submission_package.zip"
    files = [path for path in tracked_files() if path.exists() and include(path)]

    def write_archive(path: Path) -> None:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path in files:
                archive.write(file_path, file_path.relative_to(ROOT).as_posix())

    write_archive(output_zip)
    write_archive(submission_zip)
    manifest = {
        "name": "ClawFlow",
        "artifact": str(output_zip.relative_to(ROOT)),
        "submission_artifact": str(submission_zip.relative_to(ROOT)),
        "file_count": len(files),
        "bytes": output_zip.stat().st_size,
        "submission_bytes": submission_zip.stat().st_size,
        "required_entrypoints": [
            "clawflow.gateway.cli:main",
            "clawflow.gateway.api:app",
            "scripts.run_benchmark",
            "scripts.verify_deliverables",
        ],
        "included_highlights": [
            "README.md",
            "docs/technical_report.md",
            "slides/ClawFlow_presentation.pptx",
            "docs/assets/screenshots/",
            "docs/assets/diagrams/",
            "outputs/benchmark_results.json",
            "outputs/evaluation_leaderboard.json",
        ],
    }
    (ROOT / "outputs" / "release_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = [
        "# ClawFlow Release Manifest",
        "",
        f"- Artifact: `{manifest['artifact']}`",
        f"- Submission package: `{manifest['submission_artifact']}`",
        f"- Included files: {manifest['file_count']}",
        f"- Archive bytes: {manifest['bytes']}",
        f"- Submission bytes: {manifest['submission_bytes']}",
        "",
        "## Entrypoints",
    ]
    md += [f"- `{item}`" for item in manifest["required_entrypoints"]]
    md += ["", "## Highlights"]
    md += [f"- `{item}`" for item in manifest["included_highlights"]]
    (ROOT / "outputs" / "release_manifest.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=2))
