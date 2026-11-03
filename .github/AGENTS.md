# AGENTS.md — `.github/`

- Workflow actions are pinned to full commit SHAs with the version in a
  comment; a bump replaces both.
- Do not relax the GNN job's provision step. A missing or divergent pin must
  fail the named conformance job, not skip it.
- Keep the dependency groups in `dependabot.yml`; one weekly pull request per
  ecosystem.
- Parent rules: [../AGENTS.md](../AGENTS.md).
