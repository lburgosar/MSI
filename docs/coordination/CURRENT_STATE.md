# MSI — Current state

Updated: 2026-09-03T11:33:46-03:00

| Field | State |
|---|---|
| Version / generation | MSI V2.1 stable; MSI NEXT foundations experimental |
| Current stable | `main @ 5eddfee` (`msi-v2.1`) |
| Current development | Track A complete, awaiting AURO + Leandro review |
| Active branch | `feature/msi-next-foundations` |
| Last verified implementation commit | `d750d1a` |
| Coordination index baseline | `4e97b50` |
| Test status | 53 tests passed on 2026-09-03 |
| Current priority | Review Track A before authorizing Migration Increment 2 |

## Implemented

- V2.1 planning, simulation, Studio/Monitor workflow and documented demo baseline.
- MSI NEXT provider-neutral architecture and safety contracts.

## Experimental

- Adaptive spatial grid, geographic persistence and GeoJSON export.
- Environment, Observation, OperationalCommand, basemap, layer and SpatialIntent contracts.
- Operator/Engineering UX wireframes.

## Not implemented

- Real basemap or lawful offline tile package.
- MSI NEXT connection to Mission Runtime.
- Wind/environment injection through the prototype.
- Production MSI NEXT HMI or real vehicle adapters.

## Known limitations

- The grid prototype uses a clearly labelled basemap placeholder.
- Command support is declared explicitly; prepared contracts do not imply hardware execution.
- The tablet-critical rendering technology decision remains open.
- Agent Lab Spike 001 hit the shared Codex usage limit before specialist findings; no dependable zero-cost model backend has been demonstrated.

## Cost constraint

Additional software, API, SaaS, cloud and model budget is USD 0. Paid integrations may be prepared as adapters only and must be labelled `READY — REQUIRES PAID SERVICE`; local/free alternatives remain the execution path.

See the latest [RAMON to AURO review entry point](AURO_HANDOFF.md) and [Agent Lab Spike 001](../agent_lab/SPIKE_001_TRACK_A_REVIEW.md). Branch `HEAD` is authoritative for the exact current commit.
