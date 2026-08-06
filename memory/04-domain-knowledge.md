# Domain Knowledge

## Why This File Exists

This file stores **automotive domain knowledge** that the team has learned. It exists so that agents don't have to re-derive domain facts. Agents should read this when working on automotive topics.

## Core Domain Concepts

### OBD-II

- **OBD-II** is the standardized diagnostic system in vehicles (post-1996).
- Provides **DTCs** (Diagnostic Trouble Codes), **live sensor data** (PIDs), and **freeze-frame data**.
- DTCs are standardized (e.g., P0301 = Cylinder 1 Misfire).
- OBD-II is standardized for emissions; manufacturer-specific PIDs are proprietary.
- See [Research: OBD-II](../docs/research/03-obd-ii-and-telemetry.md).

### Vehicle Systems

Vehicles are composed of interacting systems:

- **Engine** (combustion, ignition, fuel, cooling).
- **Charging** (alternator, battery, voltage regulation).
- **Braking** (hydraulic, ABS, electronic).
- **Cooling** (radiator, thermostat, coolant).
- **Electrical** (wiring, grounds, sensors, ECU).

### Failure Propagation

- Symptoms propagate through systems. A bad ground can cause voltage drops that mimic sensor faults.
- A single symptom can have multiple causes. A single fault can cause multiple symptoms.
- Reasoning must be causal, not pattern-matching.

## Key Insights

- **Naive text retrieval cannot reason.** It finds text but cannot explain *why* a symptom implies a fault.
- **The physical/causal model is essential.** Understanding component relationships is the product.
- **Provenance is critical.** Every claim must trace to a source.

## Status

- **Last updated:** 2026-08-03
- **Status:** Active