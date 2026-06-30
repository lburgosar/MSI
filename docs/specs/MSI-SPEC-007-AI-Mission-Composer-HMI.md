# MSI-SPEC-007 — AI Mission Composer & HMI

Version: 0.1
Status: Draft
Date: 2026-06-30

---

# 1. Purpose

This document defines the Human-Machine Interface (HMI) and AI Mission Composer architecture of MSI.

The purpose of the AI Mission Composer is to transform human intent into validated executable mission packages.

The user should express objectives, not technical implementation details.

---

# 2. Core Philosophy

MSI aims to make autonomous systems accessible to non-expert users.

Users should not need expertise in:

* drone flight planning
* GIS systems
* swarm coordination
* communication protocols
* sensor orchestration

Instead, users express goals.

Example:

"Monitor this field and detect dry areas."

The system translates intent into mission logic.

---

# 3. AI Mission Composer Architecture

High-level architecture:

AI Mission Composer
│
├── Intent Parser
├── Dialogue Engine
├── Geo Resolver
├── Resource Planner
├── Risk Analyzer
└── Mission Compiler

---

# 4. Mission Composition Pipeline

Human Prompt
↓
Intent Parsing
↓
Guided Clarification
↓
Spatial Resolution
↓
Risk Analysis
↓
Resource Planning
↓
Mission Compilation
↓
Mission Package

---

# 5. Guided Clarification

The AI must minimize user cognitive load.

It should ask only for missing critical information.

Example:

User:

"Monitor this field."

AI:

"Please indicate the mission area on the map."

The AI should avoid unnecessary questioning.

---

# 6. Goal-Oriented Interaction

Users define objectives rather than low-level commands.

Good interaction:

* inspect this field
* search for fire
* detect dry zones
* monitor livestock

Poor interaction:

* fly at 15 meters
* use 4 drones
* sample every 5 seconds

Low-level planning should be handled by the system.

---

# 7. Progressive Disclosure

MSI HMI must support progressive complexity.

---

## 7.1 Simple Mode

For non-technical users.

User provides:

* objective
* area
* confirmation

Minimal complexity.

---

## 7.2 Advanced Mode

Allows parameter tuning.

Examples:

* altitude
* scan pattern
* sampling frequency
* resource allocation
* energy reserve

---

## 7.3 Expert Mode

Allows deep system customization.

Examples:

* kernel policies
* protocol tuning
* swarm policies
* scheduler parameters
* mission constraints

Expert mode increases control but preserves safety.

---

# 8. AI Decision Authority

The AI Mission Composer is a copilot, not a supreme controller.

The AI may:

* recommend
* optimize
* replan
* predict failure
* adapt mission within authorized limits

The AI must never override safety.

Hierarchy:

Safety Layer
↓
Hard Constraints
↓
Mission Logic
↓
AI Optimization

---

# 9. Autonomous Adaptation

The AI may autonomously adapt mission execution when:

* environmental conditions change
* resource consumption changes
* mission success probability decreases
* communication degrades

Examples:

* reduce mission scope
* reassign node roles
* trigger return-to-home
* switch communication mode

Adaptation must remain within predefined operational margins.

---

# 10. Risk Override Mode

MSI supports controlled risk override.

This mode allows temporary relaxation of soft constraints.

Examples:

* lower battery reserve
* increase wind tolerance
* reduce node spacing
* increase thermal margins

Risk Override requires:

* explicit user authorization
* event logging
* clear risk notification

---

# 11. Hard Safety Limits

Hard safety constraints are never overridable.

Examples:

* collision avoidance
* critical battery shutdown
* hard geofence
* human safety perimeter

Neither AI nor user may bypass hard safety limits.

---

# 12. Design Principle

The AI HMI must reduce operational complexity without removing user agency.

MSI must be:

* safe by default
* flexible by authorization
* impossible to operate beyond hard safety limits

---

# 13. Conclusion

The AI Mission Composer is the human-facing intelligence layer of MSI.

Its goal is to make advanced autonomous systems intuitive, accessible and powerful without sacrificing safety or user control.
