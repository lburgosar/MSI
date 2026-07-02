# MSI-SPEC-010 — Platform Integration & Adapter Architecture

Version: 0.1  
Status: Draft  
Date: 2026-07-02

---

## 1. Purpose

This specification defines how MSI integrates with external autonomous platforms.

MSI is designed as a semantic kernel for autonomous systems.

However, MSI does not assume direct universal access to all hardware.

This document defines the integration strategy required to connect MSI with heterogeneous platforms.

---

## 2. Problem Statement

Autonomous systems are built using diverse hardware and software stacks.

Examples include:

- drones
- rovers
- robotic arms
- quadrupeds
- industrial autonomous machines
- hybrid robotic systems

Each platform may use different:

- processors
- buses
- control loops
- locomotion systems
- vendor protocols
- software stacks

No universal hardware interface exists.

Therefore, MSI cannot assume direct compatibility with every platform.

---

## 3. Core Principle

MSI is not universally hardware-compatible by default.

MSI becomes universal through adapters.

---

## 4. Integration Philosophy

MSI must not depend on specific vendors.

MSI must remain platform-agnostic.

However, MSI must integrate using available interfaces.

Examples:

- MAVLink
- ROS2
- CAN Bus
- UART
- Ethernet
- USB
- vendor SDKs
- direct PWM / GPIO

MSI adapts to existing ecosystems.

MSI does not require vendors to implement native MSI support.

---

## 5. Architecture

Integration architecture:

Platform Hardware
↓
Platform Runtime / Controller
↓
MSI Adapter Layer
↓
MSI Kernel

---

## 6. Platform Runtime

The Platform Runtime is the low-level controller already responsible for physical actuation.

Examples:

Drone runtime:
- flight controller
- PID loops
- attitude stabilization
- motor mixing

Rover runtime:
- wheel control
- steering control
- traction management

Robot runtime:
- gait generation
- balance control
- inverse kinematics

MSI does not replace this runtime in standard integration mode.

---

## 7. MSI Adapter Layer

The Adapter Layer translates between:

External platform protocol
↔
MSI semantic protocol

Responsibilities:

- telemetry ingestion
- command translation
- capability mapping
- event translation
- health monitoring

Example:

External message:
BATTERY_STATUS = 62%

Adapter translates:
MSI_CAPABILITY: ENERGY = 62

---

## 8. Adapter Contract

Every MSI adapter must expose a common integration contract.

Minimum capabilities:

### Telemetry
Provide:
- energy
- position
- health
- motion status
- link quality

### Commands
Support:
- move
- stop
- hold
- return
- mission control

### Capability Discovery
Declare supported capabilities.

Example:

- 3D_MOVEMENT
- HOVER
- CAMERA
- THERMAL_SENSOR
- PAYLOAD_DROP

---

## 9. Integration Modes

MSI supports three modes.

---

### Mode 1 — External Runtime Mode (Recommended)

Existing platform runtime remains active.

Examples:
- PX4
- ArduPilot
- ROS2 systems

MSI operates as supervisory intelligence.

Recommended for V1.

---

### Mode 2 — Hybrid Control Mode

MSI shares control with existing runtime.

Examples:
- vendor FC handles stabilization
- MSI handles advanced coordination

Used for advanced integrations.

---

### Mode 3 — Native MSI Runtime

MSI controls the platform directly.

MSI manages:

- locomotion
- actuation
- control loops

This mode requires platform-specific motion engines.

Most complex mode.

Future research.

---

## 10. Supported Initial Targets

MSI V1 should prioritize integration with platforms exposing accessible interfaces.

Recommended initial targets:

- Pixhawk / Holybro
- PX4
- ArduPilot
- ROS2 robots
- direct microcontroller platforms

Closed systems may require:

- SDK access
- reverse engineering
- hardware bypass

These are not initial priorities.

---

## 11. Strategic Direction

MSI should prioritize adapter-driven expansion.

Goal:

Support heterogeneous autonomous systems without forcing vendor lock-in.

This allows swarm coordination across different vendors and hardware families.

---

## 12. Conclusion

MSI does not achieve universality through direct hardware control.

MSI achieves universality through semantic abstraction and adapter-based integration.

No universal hardware connector exists.

The MSI Adapter Layer is the bridge between heterogeneous platforms and the MSI kernel.