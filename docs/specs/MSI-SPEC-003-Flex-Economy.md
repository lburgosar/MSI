# MSI-SPEC-003 — Flex&Economy

Version: 0.1  
Status: Draft  
Date: 2026-06-29

---

## 1. Definition

Flex&Economy is a core MSI Kernel design principle.

It defines how MSI indicators must be generated, encoded and transmitted in order to maximize useful operational meaning while minimizing communication, processing and energy cost.

Flex&Economy is not only data compression.

It is semantic reduction.

---

## 2. Purpose

Autonomous systems may operate over limited, degraded or high-latency communication links.

Examples:

- UART
- CAN
- MAVLink
- LoRa
- RF mesh
- LTE / 5G
- satellite links

Because of this, MSI must avoid unnecessary raw telemetry transmission.

The system must transmit the minimum amount of information required to support correct mission-level decisions.

---

## 3. Data vs Knowledge

Traditional telemetry transmits raw data.

Example:

- Motor Temperature = 64°C
- ESC Temperature = 58°C
- CPU Temperature = 49°C
- Ambient Temperature = 23°C

MSI should transform those values into semantic knowledge.

Example:

THERMAL_STATUS = NORMAL

The receiver does not need to interpret all raw values during normal operation.

It receives an already meaningful operational state.

---

## 4. Latency

Flex&Economy directly contributes to reducing end-to-end decision latency.

It reduces:

- payload size
- serialization time
- transmission time
- deserialization time
- processing time
- interpretation time

Latency is the measurable result.

Flex&Economy is the architectural strategy.

---

## 5. Operational and Diagnostic Levels

MSI must support two information levels.

### 5.1 Operational Level

Compact semantic indicators used during normal mission execution.

Examples:

- ENERGY
- THERMAL_STATUS
- LINK_STATUS
- GPS_STATUS
- MISSION_STATUS

These indicators are optimized for real-time decisions.

### 5.2 Diagnostic Level

Raw or detailed telemetry available on demand.

Examples:

- Motor temperature
- ESC temperature
- CPU temperature
- Battery voltage
- Battery current
- Sensor raw values

Diagnostic data should not be transmitted continuously unless explicitly required.

---

## 6. Binary Encoding

Text representation is allowed for:

- debugging
- laboratory tests
- development
- documentation

Operational communication should use compact binary IDs.

Example:

THERMAL_STATUS → 0x02  
NORMAL → 0x01

Instead of transmitting:

THERMAL_STATUS=NORMAL

the system may transmit:

0x02 0x01

This reduces communication cost and improves real-time behavior.

---

## 7. Indicator Requirements

Every MSI indicator should answer:

1. What decision does this indicator enable?
2. Can this information be derived locally instead of transmitted?
3. What is the minimum binary representation?
4. What is the required update frequency?
5. What happens if this indicator is not updated for a period of time?
6. What priority does it have under degraded link conditions?

---

## 8. Degraded Communication Behavior

When communication quality decreases, MSI Kernel must be able to reduce transmission load.

Example:

Normal link:

- ENERGY
- POSITION
- LINK_STATUS
- THERMAL_STATUS
- MISSION_STATUS
- VELOCITY
- ORIENTATION

Degraded link:

- ENERGY
- LINK_STATUS
- MISSION_STATUS

Critical link:

- EMERGENCY_STATUS only

This behavior must be controlled by MSI Kernel policies.

---

## 9. Conclusion

Flex&Economy is a fundamental principle for MSI.

It allows MSI systems to operate over limited communication channels by transmitting semantic knowledge instead of raw data.

The goal is not to send more information.

The goal is to send the right information at the right time with the lowest possible cost.