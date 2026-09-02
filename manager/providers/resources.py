"""Contratos de recursos que mantienen al Runtime independiente del origen."""

from __future__ import annotations

from copy import deepcopy
from typing import Protocol

from domain.resources import Availability, Resource


class ResourceProvider(Protocol):
    mode: str

    def list_resources(self) -> list[Resource]: ...
    def list_catalog(self) -> list[Resource]: ...
    def get_resource(self, resource_id: str) -> Resource: ...
    def add_resource(self, resource: Resource) -> None: ...
    def update_resource(self, resource: Resource) -> None: ...
    def withdraw_resource(self, resource_id: str) -> None: ...


class SimulatedResourceProvider:
    mode = "simulation"

    def __init__(self, resources: list[Resource] | None = None) -> None:
        self._resources = {item.resource_id: deepcopy(item) for item in resources or []}

    def list_resources(self) -> list[Resource]:
        """Return resources currently available to the operational model."""
        return [
            deepcopy(item)
            for item in self._resources.values()
            if item.availability is not Availability.WITHDRAWN
        ]

    def list_catalog(self) -> list[Resource]:
        """Return persistent identities, including withdrawn audit records."""
        return [deepcopy(item) for item in self._resources.values()]

    def get_resource(self, resource_id: str) -> Resource:
        try:
            return deepcopy(self._resources[resource_id])
        except KeyError as error:
            raise ValueError(f"Unknown resource: {resource_id}") from error

    def add_resource(self, resource: Resource) -> None:
        if resource.resource_id in self._resources:
            raise ValueError(f"Duplicate resource: {resource.resource_id}")
        self._resources[resource.resource_id] = deepcopy(resource)

    def update_resource(self, resource: Resource) -> None:
        if resource.resource_id not in self._resources:
            raise ValueError(f"Unknown resource: {resource.resource_id}")
        self._resources[resource.resource_id] = deepcopy(resource)

    def withdraw_resource(self, resource_id: str) -> None:
        resource = self.get_resource(resource_id)
        resource.availability = Availability.WITHDRAWN
        resource.selected = False
        self.update_resource(resource)

    def active_ids(self) -> tuple[str, ...]:
        return tuple(item.resource_id for item in self.list_resources())


class LiveResourceProvider:
    """Contrato reservado para adaptadores de hardware; no conectado aún."""

    mode = "live"

    def list_resources(self) -> list[Resource]:
        raise NotImplementedError("Live resource adapter is not connected")


class ReplayResourceProvider:
    """Provider de sólo lectura preparado para reconstruir sesiones grabadas."""

    mode = "replay"

    def __init__(self, snapshots: list[list[Resource]] | None = None) -> None:
        self.snapshots = snapshots or []
        self.index = 0

    def list_resources(self) -> list[Resource]:
        if not self.snapshots:
            return []
        return deepcopy(self.snapshots[min(self.index, len(self.snapshots) - 1)])

    def list_catalog(self) -> list[Resource]:
        return self.list_resources()
