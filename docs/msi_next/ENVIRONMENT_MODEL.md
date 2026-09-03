# Environment and knowledge model

Status: minimal contract implemented under `manager/msi_next/environment.py`; not connected to V2.1.

## Purpose

An environment is a durable named place such as “Finca Las Marías”. Missions reference it instead of recreating boundaries and context each time.

## Minimal schema

```text
EnvironmentModel
  environment_id, name, CRS
  features[]
    feature_id, kind, GeoJSON geometry
    persistence: persistent | semipersistent | dynamic
    evidence: source, observed_at, confidence, freshness_seconds, accuracy_m
    properties
```

Examples: farm boundary (persistent), crop/road condition (semipersistent), wind/person/vehicle (dynamic). `remove_dynamic()` proves transient state can expire without deleting stable knowledge.

## Governance

- New evidence updates a feature explicitly; it does not silently overwrite safety policy.
- Conflicting sources should coexist until a resolver produces a reviewed interpretation.
- Confidence and freshness are inputs to reconnaissance/preflight, not decoration.
- Geometry corrections and operator overrides must be traced with actor and previous value.
- JSON repository is a prototype. Production persistence needs schema migration, versioning, concurrency and backup.

## Relationship to the four objects

- Environment owns spatial facts.
- Mission references an environment and adds temporary intent/constraints.
- Resources provide telemetry and observations.
- Knowledge retains observations, interpretations, outcomes and corrections.

