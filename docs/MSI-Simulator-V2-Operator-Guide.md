# MSI Simulator V2 — Guía de validación

## Inicio

```powershell
.\manager\mission_studio\.venv\Scripts\python.exe manager\launch_desktop.py vertical
```

Monitor debe abrir primero. En Studio:

1. Escribir `pulverizar`, `patrullar` o `emergencia`.
2. Indicar una ubicación.
3. Revisar escenario, flota, rutas y estado de preflight.
4. Pulsar **Autorizar plan**.
5. Pulsar **Ejecutar misión**.

## Configuración de recursos

En Studio expandido pueden seleccionarse y arrastrarse recursos sobre el mapa.
También pueden usarse órdenes numéricas:

```text
posición D1 -34.6020 -58.4010 4.5
batería D1 82
producto D1 12
agregar drone
retirar D1
```

Antes de ejecutar, cualquier cambio relevante vuelve a generar plan y preflight.

## Precision Spraying

Parámetros demo documentados:

- área: 3.6 ha;
- dosis: 7.5 L/ha;
- producto estimado: 27 L;
- ancho efectivo: 5 m;
- solapamiento: 10%;
- velocidad: 5 m/s;
- altura: 3 m sobre canopia;
- límite de viento: 5 m/s;
- gota: clase media.

Son parámetros coherentes para demostrar relaciones operacionales, no una
recomendación agronómica ni un modelo certificado.

Incidentes disponibles durante ejecución:

- `Viento 7.2 m/s`: pausa por restricción explícita.
- `Producto 1 L`: evalúa y reasigna ruta restante.
- `Batería 18%`: retira/reasigna según reserva.
- `Retirar seleccionado`: retiro manual y replanificación.

Para reanudar después del viento:

```text
viento 3.0 240
reanudar
```

## Patrol

Genera barridos por sectores con D3 térmico y D4 RGB/endurance. Durante la
ejecución, **Anomalía térmica** cambia prioridad y desvía D3 a confirmación.

## Emergency Response

Asigna recursos con `incident_assessment`. **Nuevo foco prioritario** genera un
evento, evaluación, decisión y órbita especializada. Es un prototipo de
gobernanza, menos profundo que Spraying.

## Trazabilidad

Cada sesión V2 registra configuración, recursos, planes, preflight, eventos,
decisiones y muestras de telemetría en:

```text
manager/mission_studio/data/v2_traces/<mission_id>.jsonl
```

El archivo es append-only y está preparado para auditoría, replay y datasets.
