# GitHub Publish Guide

This repository is ready for local Git history, release packaging, CI, README presentation and manual GitHub publishing. The only operation that cannot be completed from this workspace without external account state is the actual remote push: `origin` must point to a real GitHub repository that the current user can write to.

## Local Readiness Check

Run the non-destructive publish readiness report:

```bash
make publish-check
```

For a strict pre-push gate after the remote is configured:

```bash
make publish-check-strict
```

The strict gate requires:

- a clean git worktree
- a configured `origin` remote
- generated report/PPT/OpenAPI/benchmark/release artifacts
- successful deliverable verification evidence

## Create the GitHub Repository

Create an empty GitHub repository named `clawflow` or `ClawFlow` in the target account or organization. Do not initialize it with another README, license, or `.gitignore`, because this project already contains those files.

## Add Remote and Push

HTTPS:

```bash
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

SSH:

```bash
git remote add origin git@github.com:<owner>/<repo>.git
git push -u origin main
```

If `origin` already exists and points to the wrong repository:

```bash
git remote set-url origin <github-repo-url>
git push -u origin main
```

## Recommended Pre-push Sequence

```bash
make install
make all
git status --short
make publish-check-strict
git push -u origin main
```

`make all` runs Runtime-backed applications, benchmark, diagrams, screenshots, report, PPT, OpenAPI export, release packaging, deliverable verification and tests.

## GitHub Repository Settings

After the first push:

- enable GitHub Actions if the organization requires manual approval
- add repository topics: `agent-runtime`, `agentos`, `ai-agent`, `workflow-orchestration`, `rag`, `multi-agent`, `observability`
- set the project description to: `A lightweight Agent Runtime / AgentOS Kernel for next-generation personal AI agents`
- attach `dist/clawflow_release.zip` to a GitHub Release when publishing a tagged version
- keep Apache-2.0 as the visible license

## Current Boundary

This guide intentionally does not create a GitHub repository or authenticate `gh` automatically. Those steps require user account choice and credentials. Once a writable remote URL is provided, the local commands above are sufficient to push the complete project.
