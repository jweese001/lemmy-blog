AGENTS.md — Use CLAUDE.md as authoritative agent guidance

Purpose

This repository uses a CLAUDE.md file as the canonical per-project agent guidance. Any automation or tool that expects or consumes AGENTS.md MUST locate and read CLAUDE.md (if present) before beginning work in this repository and MUST treat the CLAUDE.md contents as the authoritative instructions for agent behavior in this project.

Search order

1. ./CLAUDE.md (repository root) — primary
2. ./ .claude/CLAUDE.md — secondary
3. ./Documents/CLAUDE.md or top-level CLAUDE.md in project folders — fallback

Required behaviour (RFC 2119)

- Tools MUST, before making any changes or running any commands that modify source, read the CLAUDE.md file in full and conform to its directives.
- If both AGENTS.md and CLAUDE.md are present, the tool MUST prefer CLAUDE.md for project-specific rules and MUST follow CLAUDE.md where it conflicts with AGENTS.md.
- Tools MUST NOT proceed with edits, execution, or deployment without honoring any "CRITICAL" or otherwise explicitly required directives inside CLAUDE.md.
- Tools SHOULD surface the CLAUDE.md content (or a short summary) to the human operator before executing destructive actions.

Notes for integrators

- The intent of this AGENTS.md is to ensure that Oh My Pi (omp) and related agents treat the existing CLAUDE.md files in this and sibling projects as the authoritative agent manifest.
- Implementations that cannot fully parse CLAUDE.md SHOULD at minimum present it to the operator and refuse automated, non-consensual destructive actions.

If you are an automation implementor: implement the above search order and semantics and add a visible, logged step "Read CLAUDE.md" to your runbook.
