# Security Policy

ClawFlow is a local Agent Runtime prototype with explicit safety boundaries:

- High-risk destructive tools must be dry-run or approval-gated.
- Shell commands are restricted by whitelist.
- Secrets must not be committed.
- Real external connectors should use least-privilege credentials and audit logs.

Report vulnerabilities by opening a private security advisory or contacting project maintainers.

