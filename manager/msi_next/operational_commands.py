"""Safety-oriented command proposals; no hardware execution is implied."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OperationalCommandType(str, Enum):
    PAUSE = "pause"
    RESUME = "resume"
    HOLD = "hold"
    RETURN_TO_BASE = "return_to_base"
    REPLAN = "replan"
    REMOVE_RESOURCE = "remove_resource"
    ABORT = "abort"
    EMERGENCY_ACTION = "emergency_action"


class CommandSupport(str, Enum):
    SIMULATED = "simulated"
    ADAPTER_REQUIRED = "adapter_required"
    NOT_SUPPORTED = "not_supported"


@dataclass(frozen=True)
class OperationalCommand:
    command_id: str
    command_type: OperationalCommandType
    mission_id: str
    requested_by: str
    requested_at: str
    target_resource_ids: tuple[str, ...] = ()
    support: CommandSupport = CommandSupport.NOT_SUPPORTED
    requires_confirmation: bool = False
    parameters: dict[str, Any] = field(default_factory=dict)

    @property
    def executable(self) -> bool:
        return self.support is not CommandSupport.NOT_SUPPORTED

    @property
    def critical(self) -> bool:
        return self.command_type in {
            OperationalCommandType.ABORT,
            OperationalCommandType.RETURN_TO_BASE,
            OperationalCommandType.EMERGENCY_ACTION,
        }

