# API Reference

This document is generated from the live FastAPI app schema by `scripts/export_openapi.py`.

| Method | Path | Summary |
|---|---|---|
| GET | `/` | Dashboard |
| GET | `/applications` | Applications |
| GET | `/applications-page` | Applications Html |
| GET | `/approvals` | Approvals |
| GET | `/approvals-page` | Approvals Html |
| POST | `/approvals-page/{run_id}/approve` | Approval Approve Html |
| POST | `/approvals-page/{run_id}/deny` | Approval Deny Html |
| POST | `/approvals/{run_id}/approve` | Approval Approve |
| POST | `/approvals/{run_id}/deny` | Approval Deny |
| GET | `/audit` | Audit |
| GET | `/audit-log` | Audit Html |
| GET | `/benchmark` | Benchmark |
| GET | `/benchmark-page` | Benchmark Html |
| GET | `/cost` | Cost |
| GET | `/cost-page` | Cost Html |
| GET | `/dashboard` | Dashboard |
| GET | `/evaluation` | Evaluation |
| GET | `/evaluation-leaderboard` | Evaluation Html |
| GET | `/failure-analysis` | Failure Html |
| GET | `/failure-recovery` | Recovery Html |
| GET | `/failures` | Failures |
| GET | `/governance` | Governance |
| GET | `/governance-page` | Governance Html |
| POST | `/governance-page/policy` | Governance Policy Html |
| POST | `/governance/policy` | Governance Policy |
| GET | `/health` | Health |
| GET | `/memory` | Memory |
| POST | `/memory` | Memory Add |
| GET | `/memory-browser` | Memory Html |
| GET | `/metrics` | Metrics |
| GET | `/metrics/tool-usage` | Tool Usage |
| GET | `/multi-agent-page` | Multi Agent Html |
| GET | `/plugins` | Plugins |
| GET | `/plugins-page` | Plugins Html |
| GET | `/prompts` | Prompts |
| POST | `/prompts` | Prompt Upsert |
| GET | `/prompts-page` | Prompts Html |
| POST | `/prompts-page/render` | Prompts Render Html |
| POST | `/prompts/{name}/render` | Prompt Render |
| GET | `/rag-page` | Rag Html |
| GET | `/roadmap` | Roadmap Html |
| POST | `/run` | Run |
| GET | `/run-agent` | Run Agent Get |
| POST | `/run-agent` | Run Agent Post |
| GET | `/runs` | Runs |
| GET | `/runs-page` | Runs Html |
| GET | `/runs/{run_id}` | Run Detail |
| POST | `/runs/{run_id}/resume` | Resume |
| GET | `/runs/{run_id}/trace` | Run Trace |
| GET | `/template-generator` | Template Generator Html |
| POST | `/template-generator/app` | Template Generator App Html |
| POST | `/template-generator/connector` | Template Generator Connector Html |
| POST | `/template-generator/tool` | Template Generator Tool Html |
| POST | `/templates/app` | Template App |
| POST | `/templates/connector` | Template Connector |
| POST | `/templates/tool` | Template Tool |
| GET | `/tool-usage` | Tool Usage Html |
| GET | `/tools` | Tools |
| GET | `/tools-page` | Tools Html |
| GET | `/trace-timeline` | Trace Html |
| GET | `/workflow` | Workflow |
| GET | `/workflow-graph` | Workflow Html |
