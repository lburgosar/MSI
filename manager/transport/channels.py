"""Puertos de transporte; el Runtime no depende de JSON ni de procesos locales."""

from __future__ import annotations

from collections import deque
from typing import Callable, Generic, Protocol, TypeVar


Payload = dict[str, object]
T = TypeVar("T")


class OperationalStatePublisher(Protocol):
    def publish(self, state: Payload) -> None: ...


class OperationalStateSubscriber(Protocol):
    def read(self) -> Payload: ...


class CommandChannel(Protocol):
    def send(self, command: Payload) -> None: ...


class TelemetryChannel(Protocol):
    def publish_telemetry(self, telemetry: Payload) -> None: ...


class EventChannel(Protocol):
    def publish_event(self, event: Payload) -> None: ...


class CallbackStatePublisher:
    """Adapta el transporte JSON provisional sin exponerlo al Runtime V2."""

    def __init__(self, callback: Callable[[Payload], None]) -> None:
        self.callback = callback

    def publish(self, state: Payload) -> None:
        self.callback(state)


class InMemoryChannel(Generic[T]):
    """Canal determinista para tests y futura composición local."""

    def __init__(self) -> None:
        self.messages: deque[T] = deque()

    def send(self, message: T) -> None:
        self.messages.append(message)

    def receive(self) -> T | None:
        return self.messages.popleft() if self.messages else None
