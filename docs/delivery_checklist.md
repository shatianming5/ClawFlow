# ClawFlow Delivery Checklist

This checklist is intended for course submission, challenge review, GitHub release, and defense rehearsal.

## Required Artifacts

- [x] Runnable Agent Runtime source project.
- [x] CLI Gateway with application commands, trace, memory, tools, approvals, prompts, metrics and policy commands.
- [x] FastAPI backend with OpenAPI export.
- [x] Web Dashboard with real persisted runtime state.
- [x] Runtime-backed Example Applications.
- [x] SQLite-backed Memory, Trace, Audit, Approval and Prompt Template stores.
- [x] Checkpoint & Resume workflow.
- [x] Tool Sandbox and Permission Governance.
- [x] Plugin Registry and local MCP-like connectors.
- [x] RAG pipeline over real local documents.
- [x] Multi-agent project analysis.
- [x] Benchmark, evaluation leaderboard and failure recovery report.
- [x] Generated diagrams, figures and screenshots.
- [x] README, technical report, PPTX/PDF and speaker notes.
- [x] Apache-2.0 license and community files.
- [x] Docker, Makefile, CI and deliverable verification gate.
- [x] Release archive, GitHub publish guide and local publish readiness checker.

## Verification Commands

```bash
make install
make all
python -m scripts.verify_deliverables --with-tests
python -m scripts.package_release
```

## Submission Notes

- Use `README.md` as the GitHub landing page.
- Run `make publish-check` before adding a remote, then `make publish-check-strict` after `origin` is configured.
- Push with `git push -u origin main` once the GitHub repository URL is available.
- Use `docs/technical_report.pdf` or `docs/technical_report.docx` as the formal report.
- Use `slides/ClawFlow_presentation.pptx` for defense.
- Use `outputs/benchmark_results.md`, `outputs/evaluation_leaderboard.md` and `outputs/failure_recovery_report.md` as experiment appendices.
