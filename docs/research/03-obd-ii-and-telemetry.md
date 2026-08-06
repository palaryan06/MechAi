# Research: OBD-II and Telemetry

## Why This Document Exists

This document addresses the research questions around **OBD-II data and vehicle telemetry**. It exists because OBD-II is a critical input modality for MechAI — it provides the live, physical evidence that grounds diagnoses in the real vehicle.

The product vision requires integrating OBD-II codes, sensor values, and telemetry into the reasoning engine. This doc explores what that data is, what it can tell us, and the challenges of using it.

## The Research Question

> How do we ingest, normalize, and interpret OBD-II and telemetry data so that it can serve as **live evidence** in the diagnostic reasoning engine?

## What Is OBD-II?

**OBD-II (On-Board Diagnostics, second generation)** is the standardized diagnostic system in vehicles manufactured after 1996. It provides:

- **Diagnostic Trouble Codes (DTCs):** Standardized codes (e.g., P0301 = Cylinder 1 Misfire) that indicate detected faults.
- **Live sensor data:** Real-time values from the vehicle's sensors (engine RPM, coolant temperature, fuel trim, etc.) via Parameter IDs (PIDs).
- **Freeze-frame data:** A snapshot of sensor values at the moment a fault was detected.
- **Vehicle Information:** VIN, calibration IDs, readiness status.

## Why OBD-II Matters for MechAI

OBD-II provides **physical evidence** that the product philosophy requires:

- A DTC tells us *what the vehicle detected*.
- Live sensor data tells us *what is happening now*.
- Freeze-frame tells us *what the conditions were when a fault occurred*.

This is ground truth from the vehicle itself — not text a model might hallucinate.

## The OBD-II Data Landscape

### What Data Is Available

| Data Type | Example | Value to MechAI |
|-----------|---------|-----------------|
| DTCs | P0301, P0420, C1210 | Direct fault evidence |
| Live PIDs | RPM, coolant temp, fuel trim | Current state evidence |
| Freeze-frame | Sensor snapshot at fault | Context for diagnosis |
| VIN | `MECHAITEST00000001` (synthetic) | Vehicle identification for model-specific reasoning |
| Readiness | Emission monitor status | Vehicle condition, inspection readiness |

### Limitations

| Limitation | Challenge |
|------------|-----------|
| **Standardization varies** | OBD-II is standardized for emissions, but many manufacturer-specific PIDs are proprietary. |
| **Coverage varies** | Not all vehicles expose the same data. Some faults (mechanical, body) are outside OBD-II scope. |
| **Data quality** | Faulty sensors produce bad data. A failing sensor might itself be the fault. |
| **Access protocols** | OBD-II is accessed via multiple protocols (CAN, KWP2000, etc.). |
| **Privacy** | The VIN and live data are sensitive; must be handled carefully. |

## Key Research Questions

### 1. Parsing and Normalization

- How do we decode raw OBD-II frames into standardized DTCs and sensor values?
- How do we handle the variation across protocols (CAN, etc.)?
- How do we model "unknown PID" gracefully?

### 2. DTC Semantics

- What does each DTC actually mean in terms of fault and cause?
- How do DTCs map to the knowledge graph (e.g., P0301 → misfire → spark/fuel/compression)?
- How do we combine DTCs with live sensor data to disambiguate causes?

### 3. Sensor Data Reasoning

- How do we use live sensor values as evidence?
- How do we detect faulty sensor data (data that contradicts itself)?
- How do we handle time-series telemetry (trends over time)?

### 4. Vehicle Context

- How does the VIN map to make/model/year/engine for model-specific reasoning?
- How do we represent vehicle-specific knowledge without duplicating the whole graph per vehicle?

### 5. Integration with the Reasoning Engine

- How do OBD-II data and the knowledge graph combine to rank hypotheses?
- How do we express uncertainty when OBD-II evidence is incomplete or contradictory?

## Current Working Assumptions

- **OBD-II is essential evidence**, but not sufficient alone. A DTC narrows the search; it doesn't always identify the root cause.
- **Normalization is a core challenge.** We need a robust parser that handles protocol and vehicle variation.
- **Privacy is critical.** VIN and live vehicle data are sensitive and must be handled per the [Security Policy](../../SECURITY.md).
- **Synthetic data is required for development** — we never use real customer vehicle data in tests or docs.

## Next Steps

1. Research the OBD-II protocol landscape (CAN, PIDs, DTC formats).
2. Prototype a DTC parser and normalizer (see [Experiments](../../experiments/README.md)).
3. Research how DTCs map to physical causes (fault trees) in the knowledge graph.
4. Evaluate: given a DTC + sensor data, can we explain the likely causes with evidence?

## Related Documents

- [Research Overview](01-research-overview.md) — how we research.
- [Knowledge Representation](02-knowledge-representation.md) — how knowledge is structured.
- [Evaluation & Benchmarks](04-evaluation-and-benchmarks.md) — how we measure.
- [Architecture Overview](../architecture/01-architecture-overview.md) — the OBD-II ingestion component.
- [Data Flows](../architecture/03-data-flows.md) — how OBD-II data flows through the system.