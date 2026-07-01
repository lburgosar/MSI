# MSI-SPEC-008 — Semantic ID Registry

Version: 0.1  
Status: Draft  
Date: 2026-07-01

---

## 1. Purpose

This document defines the initial semantic ID registry for MSI Protocol.

Semantic IDs allow MSI entities to be represented as compact binary identifiers instead of text strings.

This supports:

- low-latency communication
- reduced payload size
- protocol interoperability
- Flex&Economy encoding
- Semantic Matrix Encoding

---

## 2. ID Namespace

MSI uses 16-bit semantic IDs.

Reserved ranges:

- `0x1000–0x1FFF` → Capabilities
- `0x2000–0x2FFF` → States
- `0x3000–0x3FFF` → Events
- `0x4000–0x4FFF` → Missions
- `0x5000–0x5FFF` → Constraints
- `0x6000–0x6FFF` → Mission Orders
- `0x7000–0x7FFF` → Diagnostics
- `0x8000–0x8FFF` → Acknowledgements / Control Responses

---

## 3. Initial Capability IDs

| ID | Name | Description |
|---|---|---|
| `0x1001` | ENERGY | Available energy level or energy suitability |
| `0x1002` | TEMPERATURE | Measured or derived temperature |
| `0x1003` | HUMIDITY | Humidity measurement or derived humidity capability |
| `0x1004` | POSITION | Position capability |
| `0x1005` | ORIENTATION | Orientation / attitude capability |
| `0x1006` | LINK_QUALITY | Communication link quality |
| `0x1007` | PAYLOAD_CAPACITY | Payload availability or capacity |
| `0x1008` | NAVIGATION_CONFIDENCE | Navigation reliability |
| `0x1009` | MISSION_SUITABILITY | Mission Suitability Index |

---

## 4. Initial State IDs

| ID | Name | Description |
|---|---|---|
| `0x2001` | ENERGY_STATE | Energy semantic state |
| `0x2002` | THERMAL_STATE | Thermal semantic state |
| `0x2003` | LINK_STATE | Communication semantic state |
| `0x2004` | MISSION_STATE | Mission execution state |
| `0x2005` | NODE_HEALTH_STATE | General node health state |
| `0x2006` | NAVIGATION_STATE | Navigation reliability state |

---

## 5. Initial Event IDs

| ID | Name | Description |
|---|---|---|
| `0x3001` | LOW_BATTERY | Energy below warning threshold |
| `0x3002` | CRITICAL_BATTERY | Energy below critical threshold |
| `0x3003` | LINK_DEGRADED | Communication degraded |
| `0x3004` | LINK_LOST | Communication lost |
| `0x3005` | GPS_LOCK_LOST | Navigation lock lost |
| `0x3006` | OBSTACLE_DETECTED | Obstacle detected |
| `0x3007` | SAFE_MODE_REQUIRED | Safety layer requires safe mode |
| `0x3008` | STATE_CHANGED | Semantic state transition detected |

---

## 6. Initial Mission IDs

| ID | Name | Description |
|---|---|---|
| `0x4001` | FOLLOW_LEADER | Follow dynamic or assigned leader |
| `0x4002` | HOLD_POSITION | Maintain current position |
| `0x4003` | SEARCH_AREA | Search within defined area |
| `0x4004` | MONITOR_AREA | Monitor defined area |
| `0x4005` | HUMIDITY_SCAN | Scan area for humidity values |
| `0x4006` | FIRE_DETECTION | Fire or thermal anomaly detection |

---

## 7. Initial Constraint IDs

| ID | Name | Description |
|---|---|---|
| `0x5001` | MAX_ALTITUDE | Maximum altitude |
| `0x5002` | MIN_BATTERY_RESERVE | Minimum battery reserve |
| `0x5003` | GEO_FENCE | Operational geographic boundary |
| `0x5004` | NO_FLY_ZONE | Forbidden geographic area |
| `0x5005` | MAX_WIND_TOLERANCE | Maximum wind tolerance |
| `0x5006` | HUMAN_SAFETY_RADIUS | Minimum distance from humans |

---

## 8. Initial Mission Order IDs

| ID | Name | Description |
|---|---|---|
| `0x6001` | RETURN_HOME | Return to home or base |
| `0x6002` | ABORT_MISSION | Abort current mission |
| `0x6003` | REDUCE_TASK_SCOPE | Reduce current mission scope |
| `0x6004` | SWITCH_TO_SAFE_MODE | Enter safe mode |
| `0x6005` | REPLAN_REQUIRED | Mission replanning required |
| `0x6006` | TRANSFER_ROLE | Transfer role to another node |

---

## 9. Value Encoding

Semantic IDs identify what is being transmitted.

Values define the associated data.

Examples:

ENERGY may use:

- `uint8` percentage `0–100`
- semantic state enum
- trend value

THERMAL_STATE may use enum:

- `0x00` UNKNOWN
- `0x01` NORMAL
- `0x02` WARNING
- `0x03` CRITICAL

---

## 10. Registry Rules

New IDs must be:

- unique
- documented
- assigned within the correct namespace
- semantically meaningful
- compatible with Flex&Economy principles

IDs should not represent raw hardware channels unless explicitly required for diagnostics.

---

## 11. Conclusion

The Semantic ID Registry defines the common binary vocabulary of MSI.

It allows semantic concepts to be transported efficiently across different protocols, hardware platforms and mission layers.