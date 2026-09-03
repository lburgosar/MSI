# MSI Next UX concept

Status: discussion wireframes, not production HMI.

[Open the Operator/Engineering visual wireframes](assets/operator-engineering-wireframes.svg).

## Operator Mode

```text
┌ Mission / viability / direct critical controls ┐
├ Intent & parameters ┬ TERRITORY / WORK ┬ Context ┤
│ What outcome?       │ basemap          │ assigned│
│ constraints         │ selected area    │ sensors │
│ MSI proposal        │ work state       │ alerts  │
│ Modify / Simulate   │ decisions on map │ impact  │
├ lifecycle: Define → Simulate → Authorize → Operate┤
└ concise explanation / conversation                 ┘
```

The map is primary. Technical paths are an optional engineering layer. The default visual encodes pending/active/completed work, territory, resources and MSI decisions.

## Engineering / Simulation Mode

Adds scenario injection, raw telemetry, route overlay, trace/replay, provider health and numeric editors. It is visibly labelled and cannot be confused with Live operation.

## Context priorities

- Spraying: coverage, swath, product, wind, height, sectors.
- Patrol: grid state, scanned/pending/anomaly, RGB/thermal.
- Emergency: focus, priority, live context, suitable resources, decisions.
- Running: persistent PAUSE plus support-aware HOLD/RTL/ABORT controls.

## Spatial authoring

1. Grid paint for quick intent.
2. Vector refinement for boundaries, point/line/corridor/exclusion.
3. Numeric precision for coordinates, altitude reference, heading and dimensions.
4. Long-press precision mode is proposed: offset crosshair/magnifier so the finger does not cover the target.

## Safety behavior

- PAUSE is immediate when supported.
- ABORT/RTL/emergency actions are large and require deliberate confirmation where policy demands.
- Unsupported hardware commands remain disabled with explanation.
- Alerts and restrictions never disappear due to adaptive prioritization.

## Reference interpretation

The supplied concept image informs hierarchy, cartography, overlays and density. It is not copied and does not prove satellite/map/video capabilities.
