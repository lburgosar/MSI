# MSI — RAMON → AURO HANDOFF

Updated: 2026-09-03T11:33:46-03:00

Stable: `main @ 5eddfee` (`msi-v2.1`)

Experimental: `feature/msi-next-foundations @ HEAD`

Track A implementation checkpoint: `d750d1a`; coordination index baseline: `4e97b50`. Resolve the branch `HEAD` from GitHub for the exact current commit.

## Objective

Deliver Track A foundations for MSI NEXT while preserving V2.1 and keeping all experiments isolated from the production HMI and Mission Runtime.

## What changed

- Added the adaptive-grid prototype and provider-neutral geospatial contracts.
- Defined Environment Model, mission lifecycle, Observation and safety-aware OperationalCommand contracts.
- Documented Operator versus Engineering Mode, map-provider research, architecture and migration plan.
- Added reviewed UX wireframes and a Track A delivery report.
- Ran a zero-cost Agent Lab viability spike: three read-only specialist reviews were dispatched, but all hit the shared Codex usage limit before returning findings. No platform was installed and no MSI code changed.

## What works

The standalone prototype supports spatial selection, erasure, adaptive resolution/zoom, geographic persistence across resolution changes, clearing and GeoJSON MultiPolygon export. All contracts are importable and unit tested. V2.1 remains intact.

The prototype does **not** demonstrate a real map, Mission Runtime integration, wind injection, mission execution, a final HMI, or real vehicle control.

## Tests

`manager\mission_studio\.venv\Scripts\python.exe -m unittest discover -s tests -q`

Result: 53 tests passed.

## Decisions made

- Geographic intent is geometry, not screen-cell identity or a flight route.
- Basemap access is behind a provider contract with explicit attribution.
- Observations carry evidence but cannot issue decisions.
- Operational commands separate confirmation, criticality and actual adapter support.
- No production map renderer was selected; that tablet-significant decision remains gated.

## Needs AURO review

Do not accept this report as proof. Independently inspect the branch diff, implementation, documentation and test execution. Review whether the proposed boundaries preserve MSI semantics and safety, then assess the MapLibre/OpenLayers offline spike as the correct next increment. Recommended order:

1. [Track A report](../msi_next/TRACK_A_REPORT.md)
2. [Geospatial architecture](../msi_next/GEOSPATIAL.md)
3. [Environment Model](../msi_next/ENVIRONMENT_MODEL.md)
4. [Mission lifecycle](../msi_next/MISSION_LIFECYCLE.md)
5. [Operator/Engineering UX](../msi_next/UX_CONCEPT.md)
6. [Migration plan](../msi_next/MIGRATION_PLAN.md)
7. [Adaptive-grid prototype](../../experiments/msi_next_geospatial/README.md)

This order moves from delivery scope to contracts, interaction model and only then the executable experiment, reducing the risk of mistaking the prototype for the product.

## Risks / concerns

- Renderer choice could constrain MSI TAB, offline packaging and Python integration.
- Public OSM tile servers are not an operational/offline map backend.
- Geometry validation, CRS transformations and authoritative environment merge rules need production hardening.
- Prepared command contracts must never be presented as supported hardware actions without an adapter.
- Agent Lab has not demonstrated a dependable zero-cost model backend; its failed review attempt is not an AURO audit.

## Canonical references

- [Architecture](../msi_next/ARCHITECTURE.md)
- [Contracts](../msi_next/CONTRACTS.md)
- [Decisions](DECISIONS.md)
- [Current state](CURRENT_STATE.md)
- [Agent Lab Spike 001](../agent_lab/SPIKE_001_TRACK_A_REVIEW.md)

## Suggested next action

Approve or reject Migration Increment 2: a strictly isolated, measured MapLibre GL JS versus OpenLayers spike using a lawful small PMTiles/MBTiles dataset, without replacing Studio or merging to `main`.
