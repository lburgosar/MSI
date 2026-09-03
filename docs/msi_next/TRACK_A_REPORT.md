# MSI Next Track A — Delivery report

Date: 2026-09-03

## Delivered

- Stable V2.1 preserved as annotated tag `msi-v2.1` at `5eddfee`.
- Experimental branch `feature/msi-next-foundations`; production HMI unchanged.
- Architecture proposal preserving Runtime/Planner/Preflight/Decision/Simulation assets.
- Geospatial architecture covering basemap, geometry, CRS, layers and spatial selection.
- Map-provider comparison with official sources, license/offline/touch risks and recommendation.
- Runnable adaptive-grid prototype with mouse/touch paint, erase, zoom, clear and GeoJSON MultiPolygon export.
- Minimal persistent Environment Model with evidence source/time/confidence/freshness/accuracy.
- Current→future mission lifecycle mapping including reconnaissance and simulation gate.
- Observation contract that cannot issue mission decisions.
- Safety-aware OperationalCommand contract without false hardware support.
- Operator versus Engineering Mode proposal and reviewed SVG/PNG wireframes.
- Incremental migration plan and explicit MSI TAB decision boundary.

## Architecture status

| Artifact | Status |
|---|---|
| V2.1 application | Preserved / unchanged |
| Adaptive grid | Experimental and executable |
| SpatialIntent/Basemap/Layer contracts | Prepared / tested, not connected |
| Environment repository | Prototype JSON persistence, not connected |
| Observation contract | Prepared / tested, no perception provider |
| Operational commands | Prepared / tested, no dispatcher/hardware adapter |
| Real map | Researched, not integrated |
| New Operator HMI | Wireframe only |

## Recommendation

Review contracts and UX first. If approved, run Migration Increment 2: an isolated MapLibre GL JS versus OpenLayers spike using a lawful small PMTiles/MBTiles extract. Measure offline packaging, attribution, touch, startup, memory and Python bridge. Do not replace Studio until Leandro/Auro make the documented MSI TAB decision.

## Tests

Run:

```powershell
manager\mission_studio\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected at delivery: 53 tests, all passing.

## Review entry point

Start at [README.md](README.md), then run the [adaptive-grid prototype](../../experiments/msi_next_geospatial/README.md).

