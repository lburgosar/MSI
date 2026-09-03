# MSI Next incremental migration plan

## Checkpoint 0 — preserved

- V2.1 tagged `msi-v2.1`.
- Experimental work isolated on `feature/msi-next-foundations`.

## Increment 1 — contracts and spatial intent (this branch)

- Adaptive grid → geographic MultiPolygon.
- Environment/Evidence, Observation and OperationalCommand contracts.
- Architecture, lifecycle, UX and provider research.
- No production HMI replacement.

Exit: contracts tested, prototype demonstrable, review by Leandro/Auro.

## Increment 2 — basemap spike

- Isolated MapLibre/OpenLayers comparison with PMTiles small-area source.
- Attribution, offline packaging, startup time, memory, touch and failure-mode measurements.
- `BasemapProvider` capability contract.

Exit: explicit MSI TAB decision; no paid credentials.

## Increment 3 — spatial authoring service

- Grid, polygon, point, exclusion and numeric editors.
- Operator/interpreted/verified geometry comparison.
- Geometry validation behind a service; candidate Shapely adapter.

Exit: serialized SpatialIntent drives a planner fixture without UI coupling.

## Increment 4 — authoring shell

- Prototype Operator Mode using shared presentation models.
- MSI proposal, simulation gate, explainable authorization.
- Keep current HMI available as Engineering Mode.

Exit: usability review before replacing Studio.

## Increment 5 — operational command path

- Dispatcher, policy checks, confirmation, acknowledgement and timeout states.
- Simulation adapter first; Live remains unavailable until real hardware contract exists.

Exit: every visible control has an authoritative result/timeout/error.

## Increment 6 — environment memory and reconnaissance

- Versioned repository, freshness/confidence rules and reconnaissance planning.
- Trace operator geometry corrections and outcomes.

## Increment 7 — Monitor and TAB

- Contextual situational awareness, sensor providers and responsive landscape interface.
- Hardware-in-the-loop and safety validation before any real operation.

## Risks and questions requiring review

1. HMI map engine: Pygame-native versus web/native map surface is a significant MSI TAB decision.
2. Offline data distribution: source, geographic scope, update cadence and attribution policy.
3. Which operations require confirmation versus immediate execution under the future safety case?
4. Who can approve learned geometry/policies into durable knowledge?
5. Required positioning accuracy per mission and available GNSS/RTK evidence.

No blocker prevents continuing isolated Track A experiments. These questions block production adoption, not the prototype.
