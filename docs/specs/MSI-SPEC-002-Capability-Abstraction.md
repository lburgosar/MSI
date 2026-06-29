# MSI-SPEC-002 — Capability Abstraction

Version: 0.2
Status: Draft
Date: 2026-06-29

---

# 1. Definition

Capability Abstraction is the core mechanism of MSI.

It transforms heterogeneous low-level physical telemetry into universal semantic capabilities that are meaningful for mission-level reasoning and decision making.

A capability represents an operational property of a system rather than a raw measurement.

Examples of capabilities:

* ENERGY
* POSITION
* THERMAL_STATUS
* LINK_STATUS
* ORIENTATION
* OBSTACLE_PROXIMITY

Capabilities are independent from:

* hardware vendor
* sensor implementation
* communication protocol
* physical transport medium

---

# 2. Problem Statement

Modern autonomous systems expose raw telemetry.

Examples:

* ADC readings
* PWM signals
* UART frames
* CAN messages
* MAVLink packets
* sensor voltages
* IMU vectors

These data structures are hardware-specific and difficult to consume directly by higher-level software.

Mission logic and AI systems should not need to understand low-level telemetry.

This creates:

* vendor lock-in
* complex integrations
* duplicated logic
* high computational overhead
* increased decision latency

---

# 3. Raw Telemetry vs Capability

Raw telemetry describes physical measurements.

Example:

* Battery Voltage = 15.8V
* Battery Current = 8.2A
* Remaining Time = 11 min
* Temperature = 26°C

This information is useful for low-level diagnostics, but not optimal for high-level decision making.

Capability abstraction converts this data into semantic knowledge.

Example capability:

ENERGY = 82%

This enables direct reasoning without exposing low-level implementation details.

---

# 4. Capability Transformation Pipeline

The transformation pipeline is:

Physical Signal
↓
Acquisition
↓
Normalization
↓
Validation
↓
Sensor Fusion
↓
MSI Algorithms
↓
Capability Generation
↓
Semantic Publication

This pipeline converts raw signals into meaningful semantic indicators.

---

# 5. Capability Properties

Every MSI capability must satisfy the following properties.

## 5.1 Semantic

A capability must represent meaning, not raw data.

Good:

THERMAL_STATUS

Bad:

ADC_CHANNEL_03

---

## 5.2 Compact

A capability must be transport-efficient.

It should minimize:

* payload size
* update cost
* serialization overhead

This aligns with the Flex&Economy principle.

---

## 5.3 Universal

A capability must preserve identical meaning across all supported systems.

Example:

ENERGY must represent the same concept for:

* DJI drone
* PX4 drone
* ground robot
* autonomous vessel
* industrial rover

---

## 5.4 Actionable

A capability must enable decisions.

Example:

LOW_BATTERY

This can immediately trigger:

* return to base
* speed reduction
* safe landing
* mission abort

---

# 6. Capability Publication

Capabilities are published through MSI Core.

Example:

```cpp
MSI.publish(ENERGY, 82);
```

The publisher does not need to know:

* protocol
* packet structure
* transport medium

It only publishes semantic knowledge.

---

# 7. Key Benefit

Capability Abstraction decouples mission intelligence from hardware complexity.

This enables:

* portability
* scalability
* interoperability
* reduced latency
* simplified AI integration

MSI systems reason about capabilities, not hardware.
