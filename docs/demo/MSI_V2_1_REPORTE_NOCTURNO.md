# MSI V2.1 — Reporte nocturno

Fecha: 2026-09-02

## Resumen nocturno

MSI V2.1 hace visible una parte sustancial de la lógica que V2 ya ejecutaba. Preflight dejó de ser una etiqueta binaria; la flota muestra compatibilidad, rol, asignación y sector; los incidentes se explican como una cadena operacional; los tres escenarios tienen gramática cartográfica propia; Scenario Control está separado y declara valores inyectados; COMPLETED produce un resultado operacional y un outcome trazable.

## Bugs corregidos

- Feedback operacional calculado pero no visible en Studio.
- BLOCKED sin detalle accionable en la HMI.
- Selección inicial no asignada en Patrol/Emergency.
- Dirección de viento creando una segunda versión de plan sin cambio material.
- Sensor ID desconocido degradando un recurso sin informar error.
- Estado completado mostrando controles de inyección en vez de un cierre de misión.
- Resultado final limitado a 100 % sin métricas ni outcome estructurado.

## Cambios visuales

- Preflight detallado con actual/requerido y resultado de viabilidad.
- Recursos diferenciados por rol, compatibilidad, asignación, tarea y sector.
- Scenario Control con `valor actual → valor inyectado` y recurso afectado.
- Narrativa CONDITION/EVALUATION/DECISION/IMPACT/ACTION.
- Hileras, sectores y cobertura simplificada para Spraying.
- Sectores y contexto de reconocimiento para Patrol.
- Objetivo prioritario para Emergency.
- Feeds RGB/thermal/multispectral diferenciados y marcados como simulados.
- Mission Summary en Studio y Monitor.

## Cambios funcionales

- Snapshot compartido incorpora `preflight_explanation`, semántica de asignación, `decision_narrative` y `mission_summary`.
- Scenario Control visible incorpora link y sensor; el viento puede restaurarse con el mismo control.
- Nueva misión desde el estado completado.
- Trace registra `outcome` al finalizar.

## Commits

- `24abb11` — modelo y presentación de preflight explicable.
- `54e90de` — asignaciones, Scenario Control y decisiones operacionales visibles.
- `ba6c7c6` — vistas diferenciadas por tipo de misión.
- `5b19879` — outcomes estructurados y Mission Summary.
- Commit final de documentación/QA: consultar el siguiente commit en el historial de `main`.

## Tests

- Total: 42.
- Resultado: OK.
- Incluyen identidad/selección, plan_version, conteos, preflight, resume, escenarios, narrativa, outcome, trace, layouts y render responsive.

## Spraying

Estado: WORKING en simulación. Tiene sectores A/B, hileras, cobertura simplificada, producto, pausa por viento, restauración, reasignación y resumen. La física, deriva y cobertura no son científicamente certificadas.

## Patrol

Estado: WORKING en simulación. Patrón, sectores térmico/RGB-relay, anomalía, desvío de D3 y decisión visible. No clasifica realmente imágenes.

## Emergency

Estado: WORKING en simulación, de menor profundidad deliberada. Objetivo prioritario, D3/D4 heterogéneos, anomalía/desvío y trazabilidad.

## UX

La información prioriza misión, viabilidad, asignación, situación y decisiones. Los controles mantienen targets táctiles, no dependen de hover y el modelo de presentación es compartido. En Studio compacto, Monitor continúa siendo la vista cartográfica principal.

## Arquitectura

No se cambió el stack. Runtime sigue siendo fuente de verdad; Simulation ejecuta; MapProvider proyecta; HMI presenta. No se integraron tiles externos para evitar credenciales, licencias/dependencias y acoplamiento prematuro. El mapa local mejorado conserva el provider reemplazable.

## Limitaciones

- MapProvider local, sin cartografía real, pan/zoom ni GIS certificado.
- Feeds totalmente sintéticos; no son cámara, thermal ni multispectral reales.
- LiveResourceProvider no implementado.
- Replay completo no implementado; el trace sí contiene config, planes, eventos, decisiones, comandos implícitos, telemetría y outcome.
- Link y sensor failure aún no disparan políticas MSI.
- Métricas de cobertura/consumo/duración pertenecen al modelo simplificado.
- No hay reincorporación de WITHDRAWN ni reparación de sensor en UI.

## Bloqueos

Ninguno para revisar V2.1. Cartografía real, hardware, Live y feeds reales requerirán decisiones/recursos futuros.

## Cómo probar mañana — máximo 10 minutos

1. Abrir con `manager\\mission_studio\\.venv\\Scripts\\python.exe manager\\launch_desktop.py vertical`.
2. Spraying: `pulverizar` → `Las Marías`; revisar preflight/roles; autorizar y ejecutar.
3. Inyectar producto D1 a 1 L; observar replan y narrativa en Monitor.
4. Inyectar viento 7,2; intentar reanudar; restaurar viento desde el mismo control; reanudar.
5. Dejar completar y revisar Mission Summary.
6. Reiniciar Studio; Patrol: crear, ejecutar, inyectar anomalía y observar desvío térmico D3.
7. Reiniciar Studio; Emergency: crear, ejecutar e inyectar nuevo foco prioritario.

Las capturas canónicas están enlazadas desde [el inventario funcional](MSI_V2_INVENTARIO_Y_DEMO.md#n-actualización-msi-v21).
