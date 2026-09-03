"""Small presentation model for the MSI NEXT interactive UX experiment."""

from dataclasses import dataclass
from enum import Enum


class MissionPhase(str, Enum):
    DEFINE = "define"
    PREFLIGHT = "preflight"
    RECONNAISSANCE = "reconnaissance"
    CORRECTION = "correction"
    READY = "ready"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETE = "complete"


@dataclass
class OperatorWorkflow:
    phase: MissionPhase = MissionPhase.DEFINE
    progress: float = 0.0
    wind_ms: float = 2.7
    decision: str = "Seleccioná el área de trabajo"
    observation: str = "Pendiente"
    advanced: bool = False

    def primary_action(self, has_geometry: bool) -> bool:
        if self.phase is MissionPhase.DEFINE and has_geometry:
            self.phase = MissionPhase.PREFLIGHT
            self.decision = "Preflight aprobado · 3 recursos compatibles"
        elif self.phase is MissionPhase.PREFLIGHT:
            self.phase = MissionPhase.RECONNAISSANCE
            self.progress = 0
            self.decision = "Reconocimiento en curso"
        elif self.phase is MissionPhase.CORRECTION:
            self.phase = MissionPhase.READY
            self.decision = "Plan final recalculado · listo para autorizar"
        elif self.phase is MissionPhase.READY:
            self.phase = MissionPhase.EXECUTING
            self.progress = 0
            self.decision = "Misión autorizada · cobertura iniciada"
        elif self.phase is MissionPhase.EXECUTING:
            self.phase = MissionPhase.PAUSED
            self.decision = "Pausa solicitada por operador"
        elif self.phase is MissionPhase.PAUSED:
            self.phase = MissionPhase.EXECUTING
            self.decision = "Misión reanudada"
        else:
            return False
        return True

    def tick(self, seconds: float) -> None:
        if self.phase is MissionPhase.RECONNAISSANCE:
            self.progress = min(1, self.progress + seconds / 6)
            if self.progress >= 1:
                self.phase = MissionPhase.CORRECTION
                self.observation = "Borde oeste observado: ajustar 4 m"
                self.decision = "Revisá la diferencia antes del plan final"
        elif self.phase is MissionPhase.EXECUTING:
            self.progress = min(1, self.progress + seconds / 18)
            if self.progress >= 1:
                self.phase = MissionPhase.COMPLETE
                self.decision = "Misión completada · cobertura 100 %"

    def inject_wind(self) -> None:
        self.wind_ms = 8.4
        if self.phase is MissionPhase.EXECUTING:
            self.phase = MissionPhase.PAUSED
            self.decision = "Viento 8.4 m/s · MSI pausó para proteger deriva"

    @property
    def action_label(self) -> str:
        return {
            MissionPhase.DEFINE: "REVISAR ÁREA",
            MissionPhase.PREFLIGHT: "INICIAR RECONOCIMIENTO",
            MissionPhase.RECONNAISSANCE: "RECONOCIENDO…",
            MissionPhase.CORRECTION: "ACEPTAR Y RECALCULAR",
            MissionPhase.READY: "AUTORIZAR MISIÓN",
            MissionPhase.EXECUTING: "PAUSAR",
            MissionPhase.PAUSED: "REANUDAR",
            MissionPhase.COMPLETE: "MISIÓN COMPLETA",
        }[self.phase]
