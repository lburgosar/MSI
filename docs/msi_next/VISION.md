# MSI Next — Product and system vision

Status: proposal for Leandro/Auro review. It does not replace V2.1.

MSI is a system for directing autonomous missions, not manually piloting drones. The operator states **what** outcome is needed and **where**; MSI proposes **how**, explains viability, requests authorization, governs execution, adapts to events and preserves evidence.

## Four durable objects

| Object | Question | Owns | Does not own |
|---|---|---|---|
| Environment | Where? | Places, boundaries, infrastructure, restrictions, evidence quality | A flight plan |
| Mission | What outcome? | Intent, spatial definition, constraints, lifecycle, outcome | Physical device drivers |
| Resources | With what? | Capabilities, availability, state, telemetry | Mission intent |
| Knowledge | What is known/learned? | Observations, provenance, corrections, history | Silent safety-policy changes |

## Interaction contract

- Conversation: intent, explanation, queries and complex modification.
- Spatial tools: location and geometry.
- Direct controls: time-critical operational actions.
- Numeric editors: engineering precision.
- MSI: proposes, validates, simulates, assigns, decides and records.

## Non-negotiable safety principles

- Critical actions never depend only on a prompt.
- Learning never silently modifies regulatory, geofence, dose or human safety limits.
- UI never presents an adapter-required command as executed.
- Synthetic maps/sensors are labelled.
- Operator Mode exposes outcomes and decisions; Engineering Mode exposes internals.

## Implemented / prepared / roadmap

- **Implemented today:** V2.1 runtime, planners, preflight, decisions, scenario simulation, telemetry, traces and outcome.
- **Prepared on experimental branch:** adaptive-grid geometry, Environment/Evidence, Observation and OperationalCommand contracts.
- **Roadmap:** real basemap integration, recognition workflow, live adapters, complete replay, learning governance and MSI TAB.

