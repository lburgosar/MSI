# MSI — Current state

Updated: 2026-09-03T11:46:00-03:00

| Field | State |
|---|---|
| Version / generation | MSI V2.1 stable; MSI NEXT experimental |
| Current stable | `main @ 5eddfee` (`msi-v2.1`) |
| Current development | UX Iteration 01 implemented; awaiting AURO audit and Leandro test |
| Active branch | `feature/msi-next-foundations` |
| Last verified implementation commit | `b52d3dd` |
| Test status | 57 tests passed on 2026-09-03 |
| Current priority | Audit and human-test UX Iteration 01 |

## Implemented

- V2.1 planning, simulation, Studio/Monitor workflow and documented demo baseline.
- MSI NEXT provider-neutral architecture and safety contracts.

## Experimental

- Adaptive spatial grid, geographic persistence and GeoJSON export.
- Environment, Observation, OperationalCommand, basemap, layer and SpatialIntent contracts.
- Functional responsive map-first operator preview with guided spraying lifecycle, simulated reconnaissance/execution and wind safety event.

## Not implemented

- Real basemap or lawful offline tile package.
- MSI NEXT connection to Mission Runtime.
- Real environmental provider, actual replanning or real vehicle adapters.
- Production MSI NEXT HMI.

## Known limitations

- Agricultural map context and operational events are simulations.
- Command support contracts do not imply hardware execution.
- The tablet-critical rendering technology decision remains open.

## Cost constraint

Additional software/API/SaaS/cloud/model budget is USD 0. Paid integrations require explicit authorization; local/free paths remain preferred.

See the latest [review entry point](AURO_HANDOFF.md). Branch `HEAD` is authoritative for the exact current commit.
