# MSI — RAMON → AURO HANDOFF

Updated: 2026-09-03T02:42:00-03:00

Stable: `main @ 5eddfee` (`msi-v2.1`)

Development: `feature/msi-next-foundations @ d750d1a`

## Objective

Deliver Track A foundations for MSI NEXT while preserving V2.1 and keeping all experiments isolated from the production HMI and Mission Runtime.

## What changed

- Added the adaptive-grid prototype and provider-neutral geospatial contracts.
- Defined Environment Model, mission lifecycle, Observation and safety-aware OperationalCommand contracts.
- Documented Operator versus Engineering Mode, map-provider research, architecture and migration plan.
- Added reviewed UX wireframes and a Track A delivery report.

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

Review whether the proposed boundaries preserve MSI semantics and safety, then assess the MapLibre/OpenLayers offline spike as the correct next increment. Recommended order:

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

## Canonical references

- [Architecture](../msi_next/ARCHITECTURE.md)
- [Contracts](../msi_next/CONTRACTS.md)
- [Decisions](DECISIONS.md)
- [Current state](CURRENT_STATE.md)

## Suggested next action

Approve or reject Migration Increment 2: a strictly isolated, measured MapLibre GL JS versus OpenLayers spike using a lawful small PMTiles/MBTiles dataset, without replacing Studio or merging to `main`.
