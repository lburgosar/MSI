# MSI Next architecture proposal

Status: reversible proposal. V2.1 remains tagged `msi-v2.1`.

## Evolution without destroying Runtime

```text
Operator / Engineering / MSI TAB interfaces
                  |
          Presentation models
                  |
        Application services / ports
      +-----------+-----------+
      |                       |
Mission Runtime          World Model
      |                 Environment + Knowledge
Planner / Preflight / Decision Engine
      |
Command dispatcher ---- Resource adapters
      |                 simulation | replay | live
Telemetry / Events / Observations / Trace
```

Mission Runtime retains mission authority. New components enter through ports and immutable messages; no renderer, tile provider or device path enters mission logic.

## Boundary rules

1. `SpatialIntent` is geographic geometry plus semantic intent, never screen cells.
2. A planner converts mission+environment+resources into a plan; UI cannot create flight paths implicitly.
3. `Observation` reports evidence; Decision Engine evaluates meaning.
4. `OperationalCommand` states support and confirmation independently from request.
5. MapProvider supplies visual context; geometry services own CRS transformations.
6. EnvironmentRepository persists world knowledge; live state remains separate.
7. Presentation models may be shared by Desktop/TAB but contain no mission rules.

## Proposed ports

- `BasemapProvider`: metadata, attribution, capabilities and tile/image retrieval.
- `GeometryService`: validate, transform, measure, union, simplify and serialize.
- `EnvironmentRepository`: retrieve/version environment knowledge.
- `ObservationPublisher`: publish perception evidence.
- `CommandDispatcher`: validate support, authorize and dispatch commands.
- `MissionStateSubscriber`: interface-neutral state stream.

## Technology decision boundary

Embedding a browser/MapLibre surface into the production HMI may influence the future TAB stack. This branch documents and prototypes contracts only; it does not adopt that stack.

### DECISIÓN MSI TAB

Situación: real interactive maps are strongest in web/native map engines; current HMI is Pygame.

Implicancia para Desktop: a webview can accelerate GIS interaction but adds a second rendering/runtime boundary.

Implicancia para Tablet: MapLibre Native or a browser UI may offer better touch/offline support than Pygame.

Opción A: retain Pygame and write a tile renderer/gesture system.

Opción B: introduce a MapLibre/OpenLayers map surface behind a narrow bridge.

Recomendación técnica: prototype B in isolation, measure packaging/offline/touch behavior, then decide with Leandro/Auro before replacing production HMI.

