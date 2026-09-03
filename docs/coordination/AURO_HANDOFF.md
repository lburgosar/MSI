# MSI — RAMON → AURO HANDOFF

Updated: 2026-09-03T11:46:00-03:00

Stable: `main @ 5eddfee` (`msi-v2.1`)

Experimental: `feature/msi-next-foundations @ HEAD`

Latest implementation checkpoint: `b52d3dd`. Resolve branch `HEAD` from GitHub for the exact coordination commit.

## Objective

Deliver the first functional map-first MSI NEXT operator experience while preserving V2.1 and keeping it isolated from the production HMI and Mission Runtime.

## What changed

- Replaced the grid-only screen with a responsive spraying journey: intent, area, preflight, reconnaissance, correction, final plan, authorization and execution.
- Added progressive precision details, resource/environment context, animated operation, global progress and visible wind-triggered pause/explanation.
- Added desktop/compact visual evidence and a separately tested presentation workflow.

## What works

The preview supports spatial selection and erasure, adaptive zoom/resolution, geographic persistence, GeoJSON export and the complete simulated operator flow. Wind can be injected with an evident safety pause. Desktop and compact renders were inspected. V2.1 remains intact.

It does **not** demonstrate a real map, Mission Runtime integration, actual replanning, a final HMI or real vehicle control. Agricultural context, resources, reconnaissance, wind and execution are simulated and labelled.

## Tests

`manager\mission_studio\.venv\Scripts\python.exe -m unittest discover -s tests -q`

Result: 57 tests passed.

## Decisions made

- A single contextual primary action guides the normal operator path.
- Technical coordinates/parameters remain behind progressive disclosure.
- Simulated operational events are explicit UI controls, not hidden keyboard-only commands.
- The UX model remains independent from Pygame and production Runtime.

## Needs AURO review

Do not accept this report as proof. Independently inspect and execute the branch. Review in this order:

1. [UX Iteration 01](../msi_next/UX_ITERATION_01.md)
2. [Runnable preview](../../experiments/msi_next_geospatial/README.md)
3. `experiments/msi_next_geospatial/prototype.py`
4. `manager/msi_next/workflow.py`
5. `tests/test_msi_next_workflow.py`
6. [Track A report](../msi_next/TRACK_A_REPORT.md)

## Risks / concerns

- The simulated agricultural surface is not evidence of a cartographic provider.
- The lifecycle preview does not yet drive Mission Runtime or real command adapters.
- Polygon/line/point precision editors and actual replanning remain future increments.
- Renderer choice still affects MSI TAB, offline packaging and Python integration.

## Canonical references

- [UX Iteration 01](../msi_next/UX_ITERATION_01.md)
- [Architecture](../msi_next/ARCHITECTURE.md)
- [Geospatial design](../msi_next/GEOSPATIAL.md)
- [Current state](CURRENT_STATE.md)
- [Decisions](DECISIONS.md)

## Suggested next action

Audit UX Iteration 01 while Leandro tests it; identify only blocking UX, architecture or safety issues before the next increment.
