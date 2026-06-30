# MSI-SPEC-006 — Protocol Design

Version: 0.1
Status: Draft
Date: 2026-06-30

---

# 1. Purpose

This document defines the communication protocol of MSI.

MSI Protocol specifies how semantic information is exchanged between:

* autonomous nodes
* swarm members
* ground station
* external managers
* AI orchestration layers

The protocol is optimized for low-latency, minimal-overhead and fault-tolerant semantic communication.

---

# 2. Protocol Philosophy

MSI Protocol is not designed as a continuous remote-control channel.

It is designed as a semantic coordination protocol for autonomous systems executing preloaded mission logic.

Ground Station does not continuously command node behavior.

Ground Station:

* initializes missions
* supervises global state
* updates constraints
* issues strategic mission orders

Nodes execute mission logic locally.

---

# 3. Mission Preload Model

MSI assumes mission preload.

Before mission start, nodes receive a Mission Package containing:

* mission objectives
* operational constraints
* thresholds
* fallback policies
* emergency policies
* role definitions
* return-to-home logic

During mission execution, continuous high-bandwidth command traffic should not be required.

---

# 4. Communication Model

MSI communication focuses on semantic exchange.

Examples of transmitted information:

* capabilities
* states
* events
* mission orders
* constraints
* emergency signals

MSI avoids transmitting unnecessary raw telemetry whenever possible.

The network should transport decisions and meaningful state changes rather than low-level control data.

---

# 5. Protocol Modes

MSI Protocol supports dynamic communication modes.

---

## 5.1 Standard Mode

Used during normal operation.

Characteristics:

* flexible payload
* readable structure
* full semantic communication
* debugging friendly

Used when communication quality is healthy.

---

## 5.2 Packed Mode

Used during degraded communication conditions.

Characteristics:

* compressed semantic encoding
* reduced payload size
* increased decoding complexity
* optimized bandwidth usage

Used for:

* RF congestion
* weak links
* swarm scaling
* energy saving

---

## 5.3 Emergency Mode

Used during critical situations.

Only critical semantic signals are transmitted.

Examples:

* RTH
* SAFE_MODE
* ABORT_MISSION
* EMERGENCY_BROADCAST
* COLLISION_ALERT

Emergency mode prioritizes latency and reliability.

---

# 6. Frame Structure

MSI Frame v1:

SOF | MODE | TYPE | LEN | PAYLOAD | CRC

---

## 6.1 SOF (Start of Frame)

1 byte.

Default value:

0xAA

Used for frame synchronization.

---

## 6.2 MODE

1 byte.

Defines communication mode.

Values:

0x01 Standard
0x02 Packed
0x03 Emergency

---

## 6.3 TYPE

1 byte.

Defines semantic entity.

Values:

0x01 Capability
0x02 State
0x03 Event
0x04 Mission
0x05 Constraint
0x06 MissionOrder
0x07 Diagnostic
0x08 Ack

---

## 6.4 LEN

1 byte.

Specifies payload size.

Allows variable-length frames.

---

## 6.5 PAYLOAD

Variable size.

Contains semantic data.

Payload structure depends on TYPE and MODE.

---

## 6.6 CRC

16-bit CRC.

Used for error detection and frame integrity validation.

CRC16 is preferred for noisy communication environments.

Examples:

* RF mesh
* LoRa
* satellite links
* swarm environments

---

# 7. Semantic IDs

MSI uses 16-bit semantic IDs.

This provides namespace separation.

Example ranges:

Capabilities: 0x1000–0x1FFF
States: 0x2000–0x2FFF
Events: 0x3000–0x3FFF
Missions: 0x4000–0x4FFF
Constraints: 0x5000–0x5FFF

This enables protocol scalability and extensibility.

---

# 8. Mission Orders vs Commands

MSI differentiates mission orders from low-level commands.

Low-level control examples:

* motor throttle
* pitch
* roll
* yaw

MSI avoids continuous low-level remote control.

Mission orders represent strategic decisions.

Examples:

* RETURN_HOME
* ABORT_MISSION
* REDUCE_TASK_SCOPE
* SWITCH_TO_SAFE_MODE

Ground Station orders mission changes.

Nodes execute locally.

Ground Station orders.
Nodes decide execution details.

---

# 9. Semantic Matrix Encoding (SME)

MSI supports Semantic Matrix Encoding for ultra-efficient transport.

SME packs multiple semantic indicators into compact symbolic payloads.

Example:

Byte 0:

bits 0-1 → ENERGY_STATE
bits 2-3 → LINK_STATE
bits 4-5 → THERMAL_STATE
bits 6-7 → MISSION_STATE

Benefits:

* reduced airtime
* reduced congestion
* reduced radio energy consumption

Tradeoff:

* higher decoding complexity
* higher local CPU usage

SME is recommended for degraded links and high-density swarms.

---

# 10. Reliability Strategy

MSI supports hybrid reliability.

Normal telemetry:

* no ACK required

Critical signals:

* ACK required

Examples requiring ACK:

* RTH
* mission abort
* emergency mode activation
* safety override

This reduces protocol overhead while preserving reliability.

---

# 11. Conclusion

MSI Protocol is a transport-agnostic semantic coordination protocol.

It is optimized for:

* mission preload
* autonomous node behavior
* minimal communication
* low latency
* efficient bandwidth usage
* fault tolerance

The goal is not continuous control.

The goal is efficient semantic coordination of autonomous systems.
