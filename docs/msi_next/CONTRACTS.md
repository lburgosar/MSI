# Observation and operational command contracts

## Observation

Implemented as `manager/msi_next/observations.py`.

An Observation contains identity, kind, GeoJSON geometry, evidence metadata, optional resource and attributes. Supported vocabulary: obstacle, person, vehicle, animal, thermal anomaly, crop anomaly, terrain change and unknown object.

It intentionally has no `selected_action`. Perception publishes evidence; Decision Engine interprets operational meaning. Future adapters may produce observations from RGB, thermal, multispectral or other sensors without receiving authority over the mission.

## Operational command

Implemented as `manager/msi_next/operational_commands.py`.

Command types: PAUSE, RESUME, HOLD, RETURN_TO_BASE, REPLAN, REMOVE_RESOURCE, ABORT and EMERGENCY_ACTION.

Every request declares mission, requester, timestamp, targets, parameters, confirmation requirement and support:

- `simulated`: executable by a simulation adapter.
- `adapter_required`: semantically valid, but a device adapter/acknowledgement is required.
- `not_supported`: must never look executable.

Critical classification is separate from support. A future dispatcher must add proposed→validated→confirmed→issued→acknowledged/rejected/timed_out state, authorization policy, idempotency and trace records. Current contracts do not claim hardware execution.

