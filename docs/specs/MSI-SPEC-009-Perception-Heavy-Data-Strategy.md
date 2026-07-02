# MSI-SPEC-009 — Perception & Heavy Data Strategy

Version: 0.1  
Status: Draft  
Date: 2026-07-02

---

## 1. Purpose

This specification defines how MSI handles perception-related data and heavy payloads.

MSI is designed to support autonomous and semi-autonomous systems operating in diverse environments.

Examples include, but are not limited to:

- aerial drones
- ground rovers
- robotic agents
- industrial inspection systems
- environmental monitoring systems
- autonomous sensing networks

This document defines how MSI treats large perception payloads while preserving Flex&Economy principles.

---

## 2. Problem Statement

Modern autonomous systems increasingly rely on sensors that generate large amounts of data.

Examples:

### Visual
- RGB video
- high-resolution images
- thermal imaging
- multispectral cameras
- night vision

### Spatial
- LiDAR
- point clouds
- terrain maps
- SLAM data

### Acoustic
- microphones
- ultrasound
- sonar

### Scientific / Industrial
- gas sensors
- spectroscopy
- seismic data
- radar

These data sources can generate payloads several orders of magnitude larger than standard MSI semantic frames.

---

## 3. Core Principle

MSI is optimized for semantic transport, not raw perception transport.

In other words:

MSI should primarily transport:

- meaning
- interpreted events
- semantic abstractions
- mission-relevant knowledge

MSI should NOT transport raw heavy data by default.

---

## 4. Semantic-First Philosophy

Raw perception data should be processed as close as possible to the source node.

The preferred workflow is:

Raw Perception Data
↓
Local Processing
↓
Inference / Interpretation
↓
Semantic Abstraction
↓
MSI Transport

Example:

Raw camera feed:
- 4K video stream

Semantic output:
- HUMAN_DETECTED
- ANIMAL_COUNT = 42
- FIRE_CONFIDENCE = 94%
- OBSTACLE_DISTANCE = 3.4m

MSI transports semantic outputs whenever possible.

---

## 5. Perception Engine

MSI introduces a dedicated Perception Engine.

Updated MSI node architecture:

Sensors
↓
Acquisition Engine
↓
Perception Engine
↓
Capability Engine
↓
State Engine
↓
Event Engine
↓
Mission Engine
↓
Transport Engine

---

## 6. Heavy Data Handling Modes

MSI defines three heavy data transport modes.

---

### Mode 1 — Semantic Mode (Preferred)

Only semantic information is transmitted.

Examples:
- OBJECT_DETECTED
- PERSON_TRACKED
- GAS_LEAK_DETECTED
- THERMAL_ALERT

Advantages:
- minimal bandwidth
- minimal energy
- minimal latency

This is the default mode.

---

### Mode 2 — Evidence Mode

Compressed evidence is transmitted.

Examples:
- JPEG snapshot
- cropped ROI image
- thermal frame
- short compressed clip

Purpose:
Provide proof or contextual validation for semantic detections.

Advantages:
- moderate bandwidth
- useful for operator validation
- preserves Flex&Economy

---

### Mode 3 — Raw Stream Mode

Continuous heavy data streaming.

Examples:
- live video
- LiDAR streaming
- high-frequency imaging

Raw Stream Mode should only be enabled when:

- explicitly required by mission
- requested by operator
- transport supports required throughput
- node energy allows it

This is the most expensive mode.

---

## 7. Control Plane vs Data Plane

MSI separates communication into two planes.

### Control Plane

Managed by MSI.

Includes:
- mission orders
- events
- states
- semantic data
- safety messages

Payload size:
Typically 8–64 bytes

---

### Data Plane

Handles heavy payload transport.

Examples:
- video
- images
- LiDAR
- maps

Possible transports:
- WiFi
- Ethernet
- LTE / 5G
- Starlink
- high-throughput RF links

MSI may control the data plane without transporting the heavy payload itself.

---

## 8. Adaptive Media Policy

Heavy data transport must be adaptive.

Decision variables include:

- mission priority
- bandwidth availability
- link quality
- energy reserves
- latency requirements
- user preference

Example:

If bandwidth degrades:
- reduce resolution
- reduce FPS
- switch to snapshots
- disable stream

---

## 9. Flex&Economy Compliance

Heavy data handling must respect Flex&Economy.

Optimization targets:

- bandwidth efficiency
- computational efficiency
- latency reduction
- energy savings

The system should always prefer the least expensive transport mode capable of fulfilling mission objectives.

---

## 10. Human-Centered Design

The user should not manually manage low-level streaming decisions.

The AI/HMI layer should assist.

Example:

User request:
“Inspect that pipeline.”

AI Assistant may ask:
- area?
- required inspection quality?
- live view required?

Then automatically configure perception mode.

---

## 11. Conclusion

MSI treats heavy perception data as a separate concern from semantic transport.

The MSI core is optimized for meaning, not raw data.

Raw perception transport remains possible, but only when justified by mission requirements and system constraints.