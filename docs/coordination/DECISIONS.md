# MSI — Decision register

Detailed rationale remains in the canonical design documents linked below.

## MSI-ADR-001

- Date: 2026-09-03
- Subject: V2.1 preservation
- Decision: Preserve `main @ 5eddfee` as tag `msi-v2.1`; develop MSI NEXT on `feature/msi-next-foundations` without merging before review.
- Why: Keep the validated simulator recoverable while foundations evolve independently.
- Status: Accepted

## MSI-ADR-002

- Date: 2026-09-03
- Subject: Geospatial provider boundary
- Decision: Require provider-neutral basemap, geometry and layer contracts; exchange geographic intent as GeoJSON rather than screen cells or waypoints.
- Why: Preserve semantics across desktop, tablet, online/offline maps and future GIS sources.
- Status: Accepted for Track A review — see [GEOSPATIAL.md](../msi_next/GEOSPATIAL.md).

## MSI-ADR-003

- Date: 2026-09-03
- Subject: Operator intent versus generated flight path
- Decision: Operator selection expresses what and where; routes remain a derived Engineering Mode concern.
- Why: Avoid exposing implementation detail as the mission contract.
- Status: Accepted for Track A review — see [ARCHITECTURE.md](../msi_next/ARCHITECTURE.md).

## MSI-ADR-004

- Date: 2026-09-03
- Subject: Map renderer for Desktop and MSI TAB
- Decision: Do not select a production renderer yet. Compare MapLibre GL JS and OpenLayers in an isolated offline-capable spike first.
- Why: This choice materially affects touch, packaging, attribution, offline operation and future tablet reuse.
- Status: Pending AURO + Leandro decision — see [MIGRATION_PLAN.md](../msi_next/MIGRATION_PLAN.md).

## MSI-ADR-005

- Date: 2026-09-03
- Subject: Review entry point
- Decision: Git/GitHub remains the transport and source of truth; use `docs/coordination/AURO_HANDOFF.md` only as the canonical index for AURO review.
- Why: Make checkpoints discoverable without duplicating evidence or turning Leandro into document transport.
- Status: Accepted

## MSI-ADR-006

- Date: 2026-09-03
- Subject: Additional operating cost
- Decision: Treat USD 0 additional spend as an architecture constraint. Do not use paid APIs, credits, SaaS, cloud or subscriptions without Leandro's explicit authorization.
- Why: Continue MSI at full strategic priority through local, open-source, included or mocked/adapted paths.
- Status: Accepted

## MSI-ADR-007

- Date: 2026-09-03
- Subject: Agent Lab platform
- Decision: Do not install Flowise, Langflow, AutoGen or Ollama yet. The first read-only review attempt proved orchestration but failed on shared model quota before producing findings.
- Why: A platform layer cannot solve unavailable model capacity, and Track 3 must save more effort than it consumes.
- Status: Spike closed; revisit only with a timeboxed local-model benchmark — see [Spike 001](../agent_lab/SPIKE_001_TRACK_A_REVIEW.md).
