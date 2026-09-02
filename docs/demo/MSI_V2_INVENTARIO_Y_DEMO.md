# MSI Simulator V2 — Inventario funcional y demo canónica

Fecha de auditoría: 2026-09-02  
Base auditada: MSI V2.1, después de los checkpoints nocturnos de explicabilidad y visualización operacional.

## Convenciones de estado

- **WORKING:** implementado, expuesto cuando corresponde y verificado.
- **PARTIAL:** existe una versión limitada o sintética.
- **NOT EXPOSED:** implementado en código/API, sin control gráfico directo.
- **NOT IMPLEMENTED:** contrato, placeholder o intención sin implementación operativa.
- **BUGGED:** comportamiento reproducible pendiente de corrección.

## A. Matriz funcional

| Función | Componente | Dónde/cómo se activa | Entrada | Resultado esperado | Estado |
|---|---|---|---|---|---|
| Entrevista de intención | Mission Studio | Home, texto + Enter/flecha | Palabras de pulverización, patrulla o emergencia | Reconoce intención y pregunta ubicación | WORKING |
| Saludos | Mission Studio | Home | hola, buen día, buenas, etc. | Respuesta conversacional sin crear misión | WORKING |
| Validación de intención desconocida | Mission Studio | Home | Texto no reconocido | Feedback y permanencia en entrevista | WORKING |
| Selección de ubicación | Mission Studio | Segunda respuesta del Home | Texto libre | Crea configuración demo y abre misión | WORKING |
| Adjuntar archivos | Mission Studio | Botón `+` en Home | Click/touch | Sólo informa que estará disponible próximamente | NOT IMPLEMENTED |
| Preview de misión | Mission Studio / Runtime | Automático al crear misión | Configuración + catálogo | Plan, preflight, trayectorias y recursos | WORKING |
| Selección de recurso | Studio | Tarjeta de recurso o dron en mapa | Click sobre D1–Dn | Actualiza selección y tarjeta contextual | WORKING |
| Arrastre de recurso | Studio | Arrastrar dron sobre mapa en vista alta | Puntero | Cambia posición; al soltar replantea antes de ejecución | WORKING |
| Posición numérica | Studio | Comando `posición` | ID, latitud, longitud, altitud | Actualiza posición y replantea si no está ejecutando | WORKING |
| Autorizar plan | Studio / Runtime | Botón o comando `autorizar` | Preflight READY | Estado `authorized`; aún no ejecuta | WORKING |
| Ejecutar misión | Studio / Runtime | Segundo click o comando `ejecutar` | Plan autorizado | Estado RUNNING, comandos y movimiento | WORKING |
| Reanudar | Studio / Runtime | Botón o comando `reanudar` | Misión PAUSED y viento válido | RUNNING y evento trazable | WORKING |
| Rechazo de reanudación | Studio / Runtime | Reanudar con viento alto | Viento > límite | Sigue PAUSED, causa explícita publicada | WORKING |
| Feedback de BLOCKED | Studio | Click en botón bloqueado o cambio previo al vuelo | Finding de preflight | Muestra resumen y detalle reales | WORKING |
| Controles de escenario | Studio | Botones compactos/laterales | Acción y recurso seleccionado | Inyecta condición en Scenario Engine | WORKING |
| Entrada textual operacional | Studio | Prompt inferior | Comando soportado | Ejecuta cambio o error explícito | WORKING |
| Resumen global | Monitor | Automático, sólo lectura | Snapshot V2 | Escenario, modo, estado, progreso y ambiente | WORKING |
| Mapa y trayectorias | Monitor | Automático | Drones + mapa normalizado | Posiciones, orientación, rutas y objetivos | WORKING |
| Selección de recurso | Monitor | Chips D1–D4 | Click | Cambia detalle, sensor y telemetría mostrados | WORKING |
| Decisiones/eventos | Monitor | Automático | Snapshot | Última decisión y timeline | WORKING |
| Sincronización Studio–Monitor | Telemetría | Archivo JSON compartido, refresco 0,20 s | Snapshot publicado | Monitor refleja Runtime | WORKING |
| Plan pulverización | Planner | Intent `precision_spraying` | Área, parámetros, recursos compatibles | 12 pasadas lawnmower distribuidas | WORKING |
| Plan patrulla | Planner | Intent `autonomous_patrol` | Área y recursos area_patrol | Sectores/patrón por hasta 3 recursos | WORKING |
| Plan emergencia | Planner | Intent `emergency_response` | Punto incidente + recursos compatibles | Órbita de cinco puntos, hasta 2 recursos | WORKING |
| Versionado de plan | Runtime | `plan_mission` o replan real | Cambio que recalcula/transfiere ruta | Incrementa una vez por plan real | WORKING |
| Preflight de capacidades | Preflight | Automático | Plan sin tareas | BLOCKED/NO_COMPATIBLE_RESOURCE | WORKING |
| Preflight de batería | Preflight | Automático | Asignado <= reserva + 8 | BLOCKED/ENERGY_RESERVE | WORKING |
| Preflight de producto | Preflight | Sólo spraying | Litros disponibles < requeridos | BLOCKED/INSUFFICIENT_PRODUCT | WORKING |
| Preflight de viento | Preflight | Sólo spraying | Viento > máximo | BLOCKED/WIND_LIMIT | WORKING |
| Dato de límite faltante | Preflight | Configuración sin max_wind_m_s | Falta parámetro | REQUIRES_DATA/WIND_LIMIT_MISSING | NOT EXPOSED |
| Pausa por viento | Decision Engine | Viento alto durante spraying | Evento + límite | `pause_mission` | WORKING |
| Reasignación | Decision Engine | Batería <= reserva+5, producto <=2 L o retiro | Recurso afectado + ruta pendiente | Transfiere ruta a compatible con reserva | WORKING |
| Pausa sin reemplazo | Decision Engine | Incidente de recurso sin candidato | Ruta pendiente | `pause_mission`, intervención | WORKING |
| Priorizar anomalía | Decision Engine | Anomalía térmica | Coordenadas + recurso térmico | Desvía D3 a órbita de confirmación | WORKING |
| Anomalía sin térmico | Decision Engine | Anomalía sin recurso thermal | Evento | `request_intervention` | NOT EXPOSED |
| Viento | Scenario Engine | Botón o comando | m/s, dirección opcional | Ambiente/preflight o pausa operacional | WORKING |
| Batería | Scenario Engine | Botón o comando | ID, porcentaje | Telemetría; reassign si <= reserva+5 | WORKING |
| Producto | Scenario Engine | Botón o comando | ID, litros | Consumible; reassign si <=2 L | WORKING |
| Link | Scenario Engine | Sólo comando | ID, porcentaje | Actualiza telemetría; no toma decisión | PARTIAL |
| Falla de sensor | Scenario Engine | Sólo comando | ID, sensor_id | Sensor no operativo y Health DEGRADED; sin replan | PARTIAL |
| Retiro | Scenario Engine | Botón o comando | ID | Retira identidad activa y reasigna si corresponde | WORKING |
| Anomalía térmica | Scenario Engine | Botón en patrulla/emergencia | Coordenadas demo fijas | Decisión y desvío térmico | WORKING |
| Movimiento por waypoints | Simulation Engine | Runtime aplica DroneCommand | Ruta normalizada | Movimiento, orientación, batería y progreso | WORKING |
| Finalización | Simulation Engine / Runtime | Llegada de todos los asignados | Updates temporales | COMPLETED, 100 %, resultado | WORKING |
| Catálogo persistente | Resource Management | Provider | Recursos seed + ADD explícito | IDs únicos; conserva retirados para auditoría | WORKING |
| Flota activa | Resource Management | `list_resources` | Catálogo | Excluye WITHDRAWN de plan y conteo | WORKING |
| Agregar recurso | Studio / Provider | Botón o comando explícito | Copia configurable del primer recurso | Nuevo ID monotónico D5+ y replan | WORKING |
| Desactivar/activar | Studio / Provider | Botones antes de ejecución | Seleccionado | Cambia elegibilidad y replantea | WORKING |
| Provider simulado | Resource Providers | Modo actual | Objetos Resource | CRUD en memoria con copias defensivas | WORKING |
| Provider Live | Resource Providers | No conectable desde UI | — | Sólo contrato; `list_resources` lanza NotImplementedError | NOT IMPLEMENTED |
| Provider Replay | Resource Providers | API de código | Lista de snapshots de recursos | Devuelve snapshot por índice | PARTIAL |
| Mapa local | Map/Geography | Automático | Bounds y GeoPoint | Proyección reversible y escena local | PARTIAL |
| Cartografía real/tiles | Map/Geography | — | — | No existe | NOT IMPLEMENTED |
| Telemetría de drones | Runtime/Simulation | Automático | Estado físico simulado | Posición, orientación, velocidad, batería, ruta | WORKING |
| Sensores | Resource model/Monitor | Tarjeta seleccionada | Metadatos seed | Nombre/tipo/operational, feed gráfico sintético | PARTIAL |
| Video/cámara real | Sensors/Video | — | — | No existe stream ni archivo de video | NOT IMPLEMENTED |
| Snapshot vivo | Telemetry | Publicación Runtime | Diccionario V2 | JSON atómico compartido | WORKING |
| Trace JSONL | Traceability | Automático por misión V2 | Config, recursos, planes, eventos, decisiones, telemetría | Archivo append-only por mission_id | WORKING |
| MissionLog legado | Logging | Studio | Eventos de UI | JSON/resumen de sesión | PARTIAL |
| Replay operacional completo | Replay | — | Trace JSONL | No reconstruye misión/decisiones/telemetría | NOT IMPLEMENTED |
| Launcher vertical | Desktop Launcher | `python manager/launch_desktop.py vertical` | Área útil de Windows | Monitor arriba 62 %, Studio abajo | WORKING |
| Launcher horizontal | Desktop Launcher | `python manager/launch_desktop.py horizontal` | Área útil de Windows | Studio izquierda, Monitor derecha | WORKING |
| Redimensionado | Ambas HMI | Bordes de ventana | Tamaño disponible | Layout recalculado; modo compacto por altura | WORKING |
| Suite automática | Tests | unittest discover | Código local | Dominio, UI, runtime, layout, transporte y trace | WORKING |

## B. Recursos default

| ID | Nombre | Tipo | Capacidades | Payload | Sensor | Batería | Consumible | Link/latencia | Posición inicial | Puede realizar | No puede realizar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 | Aquila Spray 20 | aerial | flight, precision_spraying, rgb_imaging | spray_payload | D1-RGB, rgb_camera, video | 92 %, 920 Wh, reserva 22 % | 18,5/20 L spray_product | 97 %, 24 ms | -34.6095, -58.4180, 3 m above_canopy | Pulverización | Patrulla por `area_patrol`; emergencia por `incident_assessment`; térmica |
| D2 | Aquila Spray 16 | aerial | flight, precision_spraying, multispectral_imaging | spray_payload | D2-MS, multispectral, image | 78 %, 760 Wh, reserva 22 % | 13/16 L spray_product | 91 %, 31 ms | -34.6102, -58.4145, 3 m above_canopy | Pulverización | Patrulla, emergencia, térmica |
| D3 | Tero Thermal | aerial | flight, area_patrol, thermal_imaging, incident_assessment | ninguno | D3-TH, thermal_camera, thermal | 87 %, 640 Wh, reserva 18 % | ninguno | 94 %, 28 ms | -34.6097, -58.4110, 3 m above_canopy | Patrulla, emergencia, confirmación térmica | Pulverización |
| D4 | Hornero Endurance | aerial | flight, area_patrol, rgb_imaging, communications_relay, incident_assessment | ninguno | D4-RGB, rgb_camera, video | 68 %, 1200 Wh, reserva 20 % | ninguno | 99 %, 19 ms | -34.6104, -58.4075, 3 m above_canopy | Patrulla, emergencia, relay declarado | Pulverización, confirmación térmica |

La selección depende de `selected=True`, disponibilidad distinta de DISABLED/WITHDRAWN, Health distinto de FAILED y presencia de la capacidad pedida. Con seeds intactos: spraying asigna D1+D2; patrol D3+D4; emergency D3+D4.

## C. Reglas reales de preflight

| Input | Condición real | Resultado | Estado | Mensaje publicado |
|---|---|---|---|---|
| `plan.tasks` | Vacío | Sin recurso compatible | BLOCKED | Ningún recurso disponible declara las capacidades requeridas. |
| Energía de cada asignado | `percent <= reserve_percent + 8` | Sin reserva suficiente | BLOCKED | La batería disponible no mantiene el margen operacional configurado. |
| Producto total asignado, spraying | Disponible < `area_hectares × dose_l_ha` | Producto insuficiente | BLOCKED | Requerido X L; disponible Y L. |
| `max_wind_m_s`, spraying | Falta el parámetro | Falta límite | REQUIRES_DATA | MSI requiere una restricción explícita antes de autorizar. |
| Viento, spraying | `wind_m_s > max_wind_m_s` | Fuera de restricción | BLOCKED | Viento X m/s; máximo autorizado Y m/s. |
| Todas las anteriores | Ningún hallazgo critical/data | Lista | READY | Recursos, energía, restricciones y parámetros mínimos verificados. |

Ejemplos verificados: seed spraying = READY; viento 7,2 con límite 5,0 = BLOCKED; eliminar `max_wind_m_s` de la configuración = REQUIRES_DATA. Este último no tiene control UI.

## D. Decisiones MSI implementadas

| Trigger | Evaluation | Alternatives | Selected action / commands | Impact visible |
|---|---|---|---|---|
| Viento > límite durante spraying | Compara valor y límite | continuar fuera de restricción; modificar parámetros; pausar | `pause_mission`; `PAUSE_ASSIGNED_RESOURCES` | PAUSED, botón Reanudar, decisión en Monitor |
| Batería baja, producto <=2 L o retiro con reemplazo | Recurso no completa waypoints | abortar; pausar; reasignar | `reassign_remaining_route`; `ASSIGN_REMAINING_ROUTE:ID` | Plan Vn+1, ruta transferida, decisión/evento |
| Igual trigger sin reemplazo | No hay compatible disponible | continuar inseguro; degradar; pausar | `pause_mission`; `PAUSE_ASSIGNED_RESOURCES` | PAUSED e intervención |
| Anomalía con D3 térmico | Requiere confirmación térmica | ignorar; esperar; desviar | `prioritize_anomaly`; `DIVERT_TO_ANOMALY:D3` | Ruta orbital y decisión |
| Anomalía sin térmico | No hay sensor térmico | RGB; esperar; intervención | `request_intervention`; sin command | Decisión publicada; caso no expuesto |

Reanudación y condiciones restablecidas son eventos de Runtime, no `DecisionRecord` del Decision Engine. Link bajo y falla de sensor no disparan decisiones hoy.

## E. Controles visibles

### Mission Studio

| Control | Objeto/efecto | Requiere selección | Evento/decisión | Qué ve el operador | Restauración |
|---|---|---|---|---|---|
| Prompt Home + enviar | Intención/ubicación | No | Estados interview/analyzing | Preguntas y feedback | Escape reinicia conversación |
| `+` Home | Placeholder de adjuntos | No | Ninguno | “Próximamente…” | No aplica |
| Autorizar plan | Plan READY | No | authorization | Botón cambia a Ejecutar | No existe desautorizar |
| Ejecutar misión | Plan autorizado | No | execution | Movimiento/progreso | No existe stop/reset dentro de misión |
| Reanudar | Misión PAUSED | No | resume o resume_rejected | Éxito o causa exacta | Restaurar condición antes |
| Tarjetas D1… | Selección contextual | Sí, es la selección | Ninguno | Resalta recurso | Seleccionar otro |
| Dron en mapa | Selección/arrastre | Sí | Replan sólo al soltar antes de vuelo | Tarjeta contextual/posición | Comando posición o nueva sesión |
| Agregar recurso | Catálogo | No | Plan nuevo | Aparece nuevo ID y cambia conteo | Retirar; no elimina historial |
| Desactivar seleccionado | Availability | Sí | Plan nuevo | Recurso no elegible | Activar seleccionado |
| Activar seleccionado | Availability | Sí | Plan nuevo | Recurso vuelve a ser elegible | Desactivar |
| Retirar seleccionado | Catálogo activo | Sí | condition + posible reassign | Desaparece de flota activa | No hay control de reincorporación |
| Viento 7,2 | Ambiente | No | pause_mission en ejecución | PAUSED y decisión | `viento 3.0 240` |
| Producto 1 L | Consumible seleccionado | Sí; D1/D2 | reassign o error si no tiene consumible | Litros/ruta/decisión | `producto ID valor`; baseline cambia |
| Batería 18 % | Energía seleccionada | Sí | reassign posible | Batería/ruta/decisión | `batería ID valor` |
| Anomalía térmica/nuevo foco | Misión patrol/emergency | No | prioritize_anomaly | D3 se desvía, decisión | Nueva sesión; no hay “cerrar anomalía” |
| Prompt operacional | Runtime/Provider | Según comando | Variable | Acuse o error | Comando inverso cuando existe |

En layout compacto no se muestra el mapa de Studio: los botones de escenario permanecen visibles y el mapa principal queda en Monitor.

### Mission Monitor

Monitor es de sólo lectura. Sus únicos controles son los chips de recursos D1–D4 visibles; cambian la tarjeta seleccionada. No alteran Runtime, plan ni versión. Muestra mapa, trayectorias, entorno, progreso, feed sintético de sensor, última decisión y timeline.

## F. Comandos aceptados

### Home

| Comando/familia | Ejemplo | Efecto | Precondición | Feedback/error |
|---|---|---|---|---|
| pulverizar/fumigar/aplicar y variantes | `pulverizar` | Intent spraying | Etapa acción | Confirma y pregunta ubicación |
| patrullar/inspeccionar/recorrer y variantes | `patrullar` | Intent patrol | Etapa acción | Confirma y pregunta ubicación |
| emergencia/respuesta/incidente/rescate | `emergencia` | Intent emergency | Etapa acción | Confirma y pregunta ubicación |
| saludo exacto | `hola` | Conversación, no misión | Etapa acción | Lista capacidades conversacionales |
| ubicación libre | `Las Marías` | Crea misión | Etapa location | Abre preview |
| desconocido | `cosechar` | No avanza | Etapa acción | Intención no reconocida |

### Pantalla de misión

| Comando | Ejemplo | Efecto | Precondiciones | Resultado/error esperado |
|---|---|---|---|---|
| `autorizar` | `autorizar` | Acción primaria | READY | AUTHORIZED; si no, causa BLOCKED |
| `ejecutar` | `ejecutar` | Acción primaria | AUTHORIZED | RUNNING; antes de autorizar equivale a intentar acción actual |
| `reanudar` | `reanudar` | Acción primaria | PAUSED | RUNNING o REANUDACIÓN RECHAZADA |
| `viento`/`wind` | `viento 7.2 265` | Velocidad y dirección | Números válidos | Preflight/replan antes de vuelo; pausa durante spraying |
| `producto`/`product` | `producto D1 1` | Litros restantes | Recurso con consumible | Reassign <=2; error si recurso no existe/no tiene consumible |
| `batería`/`battery` | `bateria D1 18` | Porcentaje | ID válido | Reassign <= reserva+5 |
| `retirar`/`withdraw` | `retirar D3` | WITHDRAWN | ID activo/conocido | Conteo baja; posible reassign |
| `enlace`/`link` | `enlace D1 40` | Link quality | ID válido | Telemetría cambia; sin decisión |
| `sensor` | `sensor D3 D3-TH` | Sensor no operativo, Health DEGRADED | ID y sensor_id | Evento; sin replan automático |
| `posición`/`position` | `posicion D1 -34.602 -58.401 4.5` | GeoPoint | ID + tres números | Replan sólo antes de ejecución |
| `agregar`/`add` | `agregar` | Nuevo recurso | Catálogo no vacío | D5+, replan |

Errores de ID, formato, número, consumible o comando se muestran como `No pude aplicar la orden: ...`. No hay validación de rangos físicos para batería, link, viento o coordenadas más allá de la validación GeoPoint lat/lon.

## G. Scenario Test Guide

| Escenario/acción | Qué simula | Qué debe hacer MSI | Studio | Monitor | Restauración |
|---|---|---|---|---|---|
| `viento 7.2 265` durante spraying RUNNING | Viento fuera de límite | pause_mission | PAUSED/Reanudar | Decisión, viento y evento | `viento 3.0 240`, luego `reanudar` |
| `bateria D1 18` | Reserva crítica | Transferir ruta pendiente si hay candidato | Plan V+1/decisión | Batería, returning/reassign | `bateria D1 92`; la asignación no vuelve sola |
| `producto D1 1` | Insumo crítico | Transferir ruta a D2 si disponible | Plan V+1 | Producto y decisión | `producto D1 18.5`; la ruta no revierte sola |
| `sensor D3 D3-TH` | Falla térmica | Marcar DEGRADED; hoy no decide | Feedback | Sensor queda no operativo en datos | Nueva sesión; no existe reparar sensor |
| `enlace D1 40` | Degradación de enlace | Sólo actualizar | Feedback | LINK 40 % | `enlace D1 97` |
| `posicion D1 -34.602 -58.401 4.5` | Reubicación | Replan antes de vuelo | Posición/Plan V+1 | Nueva posición | Comando con coordenadas seed |
| `retirar D4` | Retiro físico/lógico | Excluir de flota; reasignar si tenía tarea | Conteo 3 | Conteo 3, evento | Nueva sesión; no hay reincorporar withdrawn |
| `agregar` | ADD RESOURCE explícito | Crear identidad D5 y replan | Conteo 5 | Conteo 5 | Retirar D5 o nueva sesión |
| Botón Anomalía térmica en patrol | Detección en -34.601,-58.398 | Seleccionar D3 y desviar | Decisión | Órbita/decision | Nueva sesión |
| Botón Nuevo foco en emergency | Evento prioritario | Mismo motor térmico | Decisión | D3 desviado | Nueva sesión |

## H. Demo canónica desde cero

### Preparación

1. Cerrar ambas ventanas.
2. Eliminar únicamente `manager/shared/live_mission_state.json` si existe.
3. Ejecutar `manager\\mission_studio\\.venv\\Scripts\\python.exe manager\\launch_desktop.py vertical` desde la raíz.
4. Confirmar Monitor arriba y Studio abajo, ambos movibles/redimensionables.

### A — Precision Spraying

1. Omitir Splash con click. Escribir `pulverizar`; luego `Las Marías`.
2. Ver READY, Plan V1, 4 recursos de catálogo y trayectorias D1/D2.
3. Seleccionar D2; comprobar que la tarjeta cambia sin cambiar Plan V1.
4. Autorizar. Comprobar AUTHORIZED. Ejecutar. Comprobar RUNNING y movimiento.
5. Escribir `producto D1 1`. Esperar `reassign_remaining_route`, Plan V2 y ruta pendiente en D2.
6. Escribir `viento 7.2 265`. Esperar PAUSED.
7. Pulsar Reanudar todavía con 7,2. Debe mostrar REANUDACIÓN RECHAZADA con 7,2 > 5,0.
8. Escribir `viento 3.0 240`. Debe mostrar CONDICIONES RESTABLECIDAS.
9. Pulsar Reanudar. Esperar RUNNING.
10. Seleccionar D3 y retirar. Debe retirarse D3, nunca D1; conteo 3. Como D3 no estaba asignado, no debe producir reassign ni subir versión.
11. Seleccionar un recurso asignado y retirar. Debe bajar a 2 y crear decisión/replan sólo si existe ruta pendiente y reemplazo.
12. Dejar ejecutar hasta COMPLETED/100 %. Si los dos spraying quedan retirados o sin reemplazo, la misión se pausará: esto es comportamiento real, no completar artificialmente.

### B — Patrol

1. Nueva sesión: Escape sólo funciona desde estados ready/blocked/completed; alternativamente reiniciar Studio.
2. `patrullar`; ubicación `Las Marías`.
3. Ver patrón distinto con D3 y D4.
4. Autorizar y ejecutar.
5. Pulsar `Anomalía térmica` o usar API Scenario Engine.
6. Ver `prioritize_anomaly`, desvío D3 a `THERMAL-CONFIRM`, órbita y timeline.

### C — Emergency Response

1. Nueva sesión. `emergencia`; `Las Marías`.
2. Ver D3+D4 asignados por `incident_assessment` y geometría al incidente.
3. Autorizar y ejecutar.
4. Pulsar `Nuevo foco prioritario`.
5. Ver decisión `prioritize_anomaly`, D3 desviado y trazabilidad JSONL.

## I. Funciones implementadas pero no expuestas en UI

- Preflight REQUIRES_DATA por ausencia de `max_wind_m_s`.
- Decision `request_intervention` por anomalía sin recurso térmico.
- API Scenario Engine acepta coordenadas arbitrarias para anomalía; botones usan coordenadas fijas.
- InMemoryChannel y contratos Command/Telemetry/Event.
- ReplayResourceProvider básico por snapshots de recursos.
- Consulta del catálogo histórico completo, incluidos withdrawn.
- Detalle completo de `DecisionRecord.evaluation`, alternativas y commands está en snapshot/trace; la UI prioriza reason/impact.

## J. Limitaciones reales

- No hay hardware, Resource Provider Live, telemetría real ni integración con autopilotos.
- Replay no reconstruye sesiones completas y no tiene UI.
- El mapa es una escena local normalizada, no cartografía/tiles/GIS certificado.
- El “feed” de sensor es un panel sintético; no muestra imágenes ni video real.
- Link y sensor failure cambian estado pero no tienen políticas de decisión/replan.
- No hay reparación de sensor, reincorporación de withdrawn, deshacer asignación ni reset dentro de una misión.
- No hay validación de rangos para porcentajes, viento o latencia; GeoPoint sí valida latitud/longitud.
- `Agregar recurso` clona D1; no existe editor completo de capacidades/payload/sensores.
- Monitor sólo muestra hasta cuatro chips y Studio hasta seis tarjetas en vista alta.
- En Studio compacto el mapa se oculta deliberadamente; se usa Monitor como vista operacional principal.
- La comunicación entre procesos es un archivo JSON local atómico, no un servicio/backend remoto.
- La finalización exige que todos los IDs actualmente asignados alcancen `on_task`; una misión pausada o sin reemplazo requiere intervención.
- Las clases legacy `mission_screen.py`, `core/mission_runtime.py` y `vineyard_scene.py` permanecen en el repositorio, pero ScreenManager usa V2.

## K. Bugs

### Corregidos y verificados

- Reanudación silenciosa: ahora publica causa y mantiene PAUSED.
- Restauración de viento: publica CONDICIONES RESTABLECIDAS y habilita resume.
- Recursos retirados contados como activos: catálogo histórico separado de flota activa.
- Identidades D5+ atribuidas al replan: verificado que sólo ADD RESOURCE crea IDs; replans conservan catálogo.
- BLOCKED sin explicación visible: Studio muestra finding real y detalle.
- Selección ambigua: test garantiza que D3 seleccionado retira D3, no D1.
- Click de selección incrementando plan_version: test garantiza que seleccionar no replantea.

### Pendientes / parciales

- No se encontraron bugs bloqueantes adicionales en la suite y recorridos de runtime.
- Las limitaciones de link, sensores, Replay, video, mapa y Live detalladas arriba son funcionalidad parcial/no implementada, no se maquillan como bugs resueltos.

## L. Tests y Git

- Runner: `manager\\mission_studio\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v`
- Resultado V2.1 antes del commit final: **42 tests OK**.
- Cobertura funcional: layout, recursos, mapa, preflight, planners, runtime, decisiones, simulación, transporte, trace, publicación atómica y workflow UI.
- El hash final y estado de push se informan en el mensaje de entrega después de crear el commit.

## M. Evidencia visual reproducible

- [Spraying READY](assets/studio_spraying_ready.png): preview con flota, mapa y trayectorias.
- [Spraying con reanudación rechazada](assets/studio_spraying_resume_rejected.png): PAUSED y causa visible.
- [Monitor con pausa y decisión](assets/monitor_spraying_pause_decision.png): estado y timeline sincronizados.
- [Patrulla con anomalía](assets/studio_patrol_anomaly.png): patrón de patrulla y desvío térmico.
- [Respuesta de emergencia](assets/studio_emergency_priority.png): geometría y nuevo foco prioritario.

## N. Actualización MSI V2.1

- Preflight publica un modelo explicable compartido: disponibles, compatibles, asignados, energía, producto, viento, valores requeridos y alternativas factibles.
- Cada recurso publica rol, compatibilidad, asignación, tarea y sector; Studio y Monitor consumen la misma semántica.
- Scenario Control está rotulado como simulación, muestra valor actual → inyectado y el recurso afectado; expone viento/restauración, producto, batería, enlace, sensor, retiro y anomalía según contexto.
- Monitor presenta decisiones como CONDITION → EVALUATION → DECISION → IMPACT → ACTION.
- Spraying muestra hileras, sectores, cobertura simplificada, trayectoria completada con mayor peso y pendiente más fina.
- Patrol muestra sectores de reconocimiento térmico/RGB-relay y contexto de barrido; selecciona D3 asignado al abrir.
- Emergency muestra objetivo prioritario y recursos heterogéneos; selecciona D3 asignado al abrir.
- Feeds RGB, thermal y multispectral siguen siendo sintéticos y están marcados `SIMULATED SENSOR DATA`.
- COMPLETED publica `mission_summary` con duración simulada, cobertura, producto usado/restante, recursos, decisiones, replans, pausas, incidentes y disponibilidad de trace.
- Trace JSONL registra un `outcome` reconstruible al completar.
- Dirección de viento es telemetría en el planner simplificado: no incrementa por sí sola `plan_version`.

Evidencia V2.1:

- [Preflight explicable](assets/v21-preflight-studio.png)
- [Scenario Control compacto](assets/v21-scenario-control-compact.png)
- [Scenario Control en Studio](assets/v21-scenario-control-studio.png)
- [Narrativa de decisión en Monitor](assets/v21-decision-narrative-monitor.png)
- [Spraying operacional](assets/v21-spraying-operation.png)
- [Patrol operacional](assets/v21-patrol-operation.png)
- [Emergency operacional](assets/v21-emergency-operation.png)
- [Mission Summary en Studio](assets/v21-mission-summary-studio.png)
- [Mission Summary en Monitor](assets/v21-mission-summary-monitor.png)
