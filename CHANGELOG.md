# Changelog

All notable changes to ARC-Core are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with semantic versioning.

---

## [Unreleased] — Ecosystem Documentation Pass

### Added
- `ECOSYSTEM.md` — per-repo integration contracts describing exactly where ARC-Core is used and what each of the six sibling repos (Cleanroom Runtime, Cognition Core, LLMBuilder, Language Module, OmniBinary, Arc-RAR) uses it for.
- `.github/FUNDING.yml` — GitHub Sponsors button pointing to `@GareBear99`.
- `.github/ISSUE_TEMPLATE/` — structured issue forms (bug, feature, docs) plus contact-links config routing to Discussions, Ecosystem, Security, and Sponsor.
- `.github/pull_request_template.md` — role-boundary preservation checklist.
- `.github/dependabot.yml` — weekly grouped pip + github-actions updates.
- `.github/labels.yml` — canonical label set covering every ARC-Core layer.
- `CITATION.cff` — machine-readable citation metadata.
- Production `SUPPORT.md` with channel matrix and cross-repo routing.
- Production `SECURITY.md` with supported-version triage SLAs and cross-repo disclosure routing.
- Production `CONTRIBUTING.md` with role-boundary rules and PR checklist.

### Changed
- `README.md` — full rewrite to production standard: hero section, ecosystem Mermaid diagram, where-ARC-Core-is-used table, two-column at-a-glance panel, quick start, feature surface inventory, repository structure, roadmap with status indicators, full documentation index, community section.
- `CODE_OF_CONDUCT.md` — adopted Contributor Covenant v2.1.

---

## Historical audit reports

The following are preserved from prior versioning rounds (each is a snapshot of repo state at the time of audit):

- `AUDIT_REPORT_v2.md`
- `AUDIT_REPORT_v3_GEO.md` — geo subsystem
- `AUDIT_REPORT_v4_SPATIAL_HARDENING.md` — spatial intelligence hardening
- `AUDIT_REPORT_v5_DARPA.md` — DARPA-style review
- `AUDIT_REPORT_v6_COMPLETION.md` — completion status
- `NEXT_STEPS_v7_OPERATOR_GRADE.md` — forward-looking operator-grade plan

---

## [v1.x] — ARC Console prototype

### Added
- FastAPI-backed ARC console prototype
- HTML dashboard with 6 pages: dashboard, signals, graph, timeline, cases, geo
- SQLite persistence
- Auth bootstrap, login, session resolution
- Event ingest + listing
- Entity resolution + normalization + details
- Graph snapshots, timeline views
- Risk-score prioritization (confidence × severity × log-capped event count × edge count + watchlist boost)
- Watchlists, cases, case-event attachment
- Proposals, approval flow, notebook
- Audit log, tamper-evident receipt chain, receipt verification, signed receipts, evidence export bundle
- Filesystem JSONL connectors, connector polling, demo feed bootstrap
- Geospatial: structures, sensors, geofences, blueprint overlays, calibration profiles, track estimation/import/listing, heatmaps, incidents, evidence-pack export
- 13 passing pytest tests

[Unreleased]: https://github.com/GareBear99/ARC-Core/compare/HEAD
