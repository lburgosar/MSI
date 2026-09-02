# MSI Simulator V2 — Arquitectura operacional

## Objetivo

Simulator V2 trata a los recursos simulados mediante los mismos modelos y
contratos que utilizarán adaptadores reales. La interfaz no mueve drones ni
decide asignaciones.

```text
Mission Studio / futura MSI TAB
              │
              ▼
       Mission Application
              │
              ▼
      Mission Runtime V2
       │      │       │
       ▼      ▼       ▼
   Planner  Preflight Decision Engine
       │               │
       ▼               ▼
 ResourceProvider   Scenario Engine
   ├─ Simulation
   ├─ Live (contrato, no conectado)
   └─ Replay (provider inicial)
              │
              ▼
 Simulation Engine / recursos reales futuros
              │
              ▼
 Operational State + Events + Decisions + Telemetry
          ↙                             ↘
       Studio                         Monitor
```

## Responsabilidades

- `domain/`: modelos de misión, geografía, recursos, capacidades y estado.
- `providers/`: origen intercambiable de recursos.
- `planning/`: planners por intención y preflight compartido.
- `runtime_v2/`: ciclo de vida, gobierno, incidentes y decisiones.
- `simulation/`: ejecución cinemática simplificada de comandos y waypoints.
- `transport/`: puertos de estado, comandos, telemetría y eventos.
- `traceability/`: registro JSONL para auditoría, replay y datasets.
- `presentation/`: mapa y renderers; nunca son fuente de verdad.
- `mission_studio/`: configuración, preview, autorización y comandos.
- `mission_monitor/`: supervisión, sensores, eventos y decisiones.

## Estados y barrera operacional

```text
configuration → preview → authorization → execution → finished
                    │             │             │
                    └─ blocked    └─ rejected   └─ intervention/paused
```

El plan sólo puede ejecutarse cuando preflight retorna `READY` y el operador
realiza una autorización explícita. Autorizar y ejecutar son acciones separadas.

## Modelos simplificados y límites

- La cinemática no es un modelo aeronáutico.
- El consumo estimado de pulverización usa `área × dosis`.
- El consumo por recurso se distribuye proporcionalmente al progreso asignado.
- La restricción de viento es explícita; MSI pausa en lugar de inventar una
  corrección de altura o velocidad no validada.
- El mapa local usa coordenadas geográficas reales en el modelo, pero su fondo
  es demostrativo y no cartografía certificada.
- Las rutas de pulverización son pasadas alternadas; Patrol usa barrido sectorial
  y Emergency utiliza una órbita de evaluación.

## Simulation / Live / Replay

- Simulation: funcional mediante `SimulatedResourceProvider`.
- Live: contrato definido; no existe conexión de hardware.
- Replay: provider de snapshots inicial; falta reproducir una sesión completa.

El JSON compartido continúa como adaptador local provisional. Studio y Runtime
publican mediante `OperationalStatePublisher`, por lo que podrá reemplazarse sin
cambiar lógica de misión.
