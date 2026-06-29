# MSI — Mission Semantic Interface

MSI is a hardware-agnostic abstraction framework designed to transform heterogeneous physical sensor data into compact, universal and decision-oriented indicators.

The framework aims to decouple:

- Physical hardware
- Communication protocols
- Mission logic
- AI / decision systems

## Core Principles

- Capability Abstraction
- Mission Abstraction
- Flex&Economy
- Vendor Agnostic Integration
- Real-Time Optimized Communication

## Project Structure

- `docs/` → Specifications and architecture
- `firmware/` → Embedded node implementation
- `manager/` → Discovery, orchestration and dashboard
- `hardware/` → Lab and physical interfaces
- `tests/` → Validation and integration tests

## Current Lab Status

- Arduino UNO detected and programmed
- Potentiometer mapped as ENERGY
- DHT11 mapped as TEMPERATURE and HUMIDITY
- MSI Core v0.1 functional