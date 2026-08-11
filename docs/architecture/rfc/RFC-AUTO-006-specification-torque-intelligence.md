# RFC-AUTO-006 — Automotive Specification & Torque Intelligence Engine

## 1. Summary
This RFC introduces the **Automotive Specification & Torque Intelligence Engine**, the first canonical Automotive Domain Fact Intelligence layer in MechAI. The engine transforms specification and torque evidence extracted from `OrderedLayoutCIR`, `AutomotiveTableSet`, and `AutomotiveProcedureSet` into structured, provenance-preserving, applicability-aware automotive facts.

It implements the strict constraints defined in RFC-008.5 and RFC-AUTO-005, primarily:
1. **Never use LLMs for numeric extraction**: All values must be extracted deterministically.
2. **Deterministic immutability**: Facts cannot be modified or averaged once created.
3. **No hallucination/Merging**: If two sources disagree, preserve both facts with full provenance.
4. **Preserve unresolved context**: If the system cannot determine applicability, the fact remains unresolved but preserved.
5. **Exact geometric provenance**: All extracted facts trace back to the sub-pixel `BoundingBox` and `SourceRef`.

## 2. Motivation
Automotive manuals contain thousands of numeric specifications—tightening torques, clearances, limits, and capacities. These specifications are distributed across raw text paragraphs, procedural steps, dedicated specification tables, and diagrams. 

To enable automated diagnosis and repair orchestration at scale (100,000+ manuals), MechAI must reliably extract these specifications without losing their engineering context (e.g., "when cold", "apply oil to threads", "only for M/T variants"). 

## 3. Data Contracts
The Engine produces an `AutomotiveSpecificationSet` consisting of distinct `AutomotiveTorqueFact` and `AutomotiveSpecificationFact` models.

### Canonical Units & Normalization
- All torques are normalized to `N.m`.
- Specifications are strictly categorized by `SpecificationType` (e.g., `CAPACITY`, `CLEARANCE`, `PRESSURE`, `TEMPERATURE`).
- Unit ranges (e.g., "10 - 15 N.m", "15 +/- 2 mm") and implicit unit distributions are correctly resolved and parsed via strict regex configurations.

### Applicability Tracking
Applicability is inherently hierarchical:
1. **Document-Level**: Applies to the entire manual (e.g., Manufacturer).
2. **Section/Procedure-Level**: Applies to the procedure (e.g., Engine Code `K10B`).
3. **Table/Row-Level**: Applies to a specific table or row (e.g., Transmission `M/T`).

The engine utilizes an `ApplicabilityContext` to track and merge these constraints, ensuring that a torque value found inside an `M/T` table column explicitly inherits the `M/T` transmission constraint.

### Conflict Detection
The engine evaluates facts to determine if they make identical or conflicting engineering claims:
- **Identical Claims (Deduplication)**: Merged by combining their evidence lists without altering the underlying fact.
- **Conflicting Claims**: Raised as a `ConflictEdge` (e.g., `VALUE_MISMATCH`, `APPLICABILITY_OVERLAP`) if two facts specify different canonical values for the identical target component and applicability context.

## 4. Architecture
The Specification Engine operates as a determinisitic post-processing layer comprising:

- `UnitNormalizer`: Parses ranges, tolerances, and canonicalizes units (e.g., "ft-lb" to "N.m").
- `ConditionParser`: Extracts operating conditions ("cold", "hot") and fastener states ("dry", "engine oil").
- `ApplicabilityResolver`: Reconciles and merges `ApplicabilityContext` scopes deterministically.
- `TorqueExtractor` & `SpecificationExtractor`: Applies deterministic Regex rules to isolate targets, values, units, and angles from `ProcedureStep` action text and `AutomotiveTableCell` content.
- `FactDeduplicator`: Identifies identical facts and combines evidence seamlessly.
- `ConflictDetector`: Builds a conflict graph representing conflicting engineering constraints.

## 5. Backward Compatibility & Future Extensions
This engine conforms to all existing upstream contracts (`OrderedLayoutCIR`, `AutomotiveTable`, `AutomotiveProcedure`).
It paves the way for deeper integration with upcoming Diagnostic Tree and Troubleshooting extraction pipelines.
