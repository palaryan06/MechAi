# RFC-AUTO-005: Automotive Domain Fact Intelligence Architecture Review

## 1. Executive Summary
MechAI has successfully implemented foundational document intelligence stages: Parser, Layout Intelligence, Reading Order, and early domain-specific intelligence (Tables, Procedures, Diagrams, Safety). However, to transition from a "document extraction system" to a "diagnostic and repair knowledge engine", the architecture must now focus on **Domain Fact Intelligence**. 

This review audits the current state of extracted facts and defines the roadmap for extracting, normalizing, and resolving conflicts for Torques, Specifications, Tools, Parts, and Diagnostic Trouble Codes (DTCs). It establishes core principles for conflict resolution, unit normalization, and vehicle applicability, while explicitly deferring premature technologies (like LLM reasoning or full graph databases) until the foundational extraction layers are robust.

## 2. Current Architecture Audit
**Currently Implemented:**
- **Stage 1 (Parser):** Raw text and bounding boxes.
- **Stage 2.0 (Layout):** Geometric classification (paragraphs, headers, tables, images).
- **Stage 2.1 (Reading Order):** Human-logical reading flow (OrderedLayoutCIR).
- **Stage AUTO-001 (Tables):** Structural reconstruction of tables.
- **Stage AUTO-002 (Procedures):** Procedural step linking and step extraction.
- **Stage AUTO-003 (Diagrams):** Callout and spatial diagram understanding.
- **Stage AUTO-004 (Safety):** Deterministic extraction of warnings/cautions/notes.

**Current Gaps:**
- Domain entities (Torque, Tools, Specifications, Part Numbers, DTCs) have `Pydantic` models defined in `src/mechai/contracts/domain_facts.py` and `src/mechai/domain/`, but no extraction engines exist yet.
- Extracted procedures contain text like "Tighten to 45 N·m", but the torque value is not structured or queryable.
- There is no mechanism to handle conflicting values across different manual revisions or cross-referenced tables.

## 3. Automotive Fact Inventory
To support diagnostic reasoning and OBD-II integration, the following facts must be extracted deterministically:
- **Vehicle & Powertrain:** Make, Model, Generation, Engine Code (e.g., K10B, F8D), Transmission, Drive Type.
- **Components:** System, Subsystem, Component ID, Location, Function.
- **Specifications:** Value, Unit, Min/Max Tolerances, Operating Conditions (e.g., "Engine Cold").
- **Torques:** Fastener target, Torque Value/Range, Unit, Tightening Sequence, Fastener Condition (dry, oiled, threadlocker).
- **Procedures:** Action, Prerequisites, Required Tools/SSTs, Material, Measurements.
- **Diagnostics:** DTC, Symptom, Inspection, Test Condition, Expected Result, Repair Action.
- **Safety:** Hazards, PPE Requirements, Restrictions.

## 4. Existing vs Missing Capabilities
**Existing:** 
- Table cell relationships, procedure step hierarchy, bounding box provenance, diagram references, and safety admonition bounding.

**Missing:** 
- **Fact Normalization:** Converting `kgf-m` to `N·m` deterministically while preserving original text.
- **Condition Parsing:** Recognizing "when cold" or "if equipped with A/C".
- **Conflict Management:** Storing multiple facts for the same entity and resolving them based on vehicle configuration.
- **Cross-Referencing:** Resolving "See Figure 3" or "Refer to Section 1A" to actual domain models.

## 5. Domain Entity Analysis
Entities like `ExtractedTorque`, `ExtractedTool`, and `ExtractedDiagnosticCode` are currently defined as flat frozen models. They successfully capture the schema but lack deep structural linking to the specific *vehicle configurations* they apply to. The models in `domain/` (e.g. `Vehicle`, `Engine`, `DiagnosticCode`) provide a good basis but require a robust Applicability Matrix to bind them securely to the facts.

## 6. Fact Representation Analysis
Facts currently exist as raw strings inside `OrderedLayoutRegion.text` or `AutomotiveProcedureStep.text`. 
A true Fact Representation must separate:
1. **The Claim:** (e.g., Torque = 45 N·m)
2. **The Evidence:** (Bounding Box, Source Page, Original String)
3. **The Applicability:** (Engine = F8D, Condition = Cold)
4. **The Confidence:** (Deterministic match = 1.0)

## 7. Provenance Requirements
Every extracted domain fact must retain a strict `SourceRef` and `BoundingBox`.
If a torque value is extracted, the engine must point exactly to the pixel coordinates and the `OrderedLayoutRegion` ID where the value was found. This ensures that downstream technicians or diagnostic agents can verify the exact OEM source visually.

## 8. Applicability Model
**The Problem:** Specifications often apply conditionally (e.g., "K10B only", "A/T only", "After 2012").
**The Solution:** An `ApplicabilityContext` model must be attached to every extracted fact. 
- If no constraints are mentioned in the immediate layout region, it inherits the document-level or chapter-level constraints.
- Applicability must be restrictive: A fact is considered applicable to a vehicle *only if* the vehicle satisfies all constraints in the `ApplicabilityContext`.

## 9. Conflict Resolution Model
**The Evidence-First Model:**
When Source A and Source B provide conflicting torque values for the same fastener:
- The system **MUST NOT** silently overwrite or merge them.
- Both facts are stored in the Knowledge Graph with their respective `SourceRef`.
- A `ConflictEdge` is generated between the two facts.
- **Resolution Strategy:** At query time, conflicts are resolved based on:
  1. *Applicability:* Does one apply specifically to the user's VIN/Variant?
  2. *Recency/Revision:* Is one from a newer TSB or addendum?
  3. *Specificity:* Is one a footnote correction while the other is a generic table?
If unresolved, the API must return *both* values flagged as `CONFLICT_DETECTED` to force human technician review.

## 10. Unit Normalization Strategy
**Principle:** Dual Representation.
- **Original Representation:** `raw_value="4.5 kgf-m"`, `original_unit="kgf-m"`
- **Canonical Representation:** `normalized_value=44.13`, `canonical_unit="N·m"`
Normalization must happen *after* extraction, deterministically, using strict conversion tables. The original source text must always remain intact to prevent silent conversion rounding errors from corrupting the grounding.

## 11. Entity Resolution Requirements
Multiple terms can refer to the same part (e.g., "O2 Sensor", "Oxygen Sensor", "HO2S"). 
An Entity Resolution layer will require an automotive synonym dictionary (Ontology mapping) to map aliases to canonical Component IDs, preventing the creation of disconnected duplicate nodes in the future graph.

## 12. Knowledge Graph Requirements
The eventual graph will require:
- **Nodes:** Components, Tools, Procedures, DTCs, Symptoms, Specifications.
- **Edges:** `REQUIRES_TOOL`, `HAS_TORQUE`, `CAUSES_SYMPTOM`, `RESOLVED_BY`, `DEPICTS`.
- **Edge Properties:** Applicability rules, Confidence, Source Provenance.
*Note: Do not implement a graph database (Neo4j/Neptune) yet. The output should remain JSON-serializable `FrozenSets` until the extraction engines are mature.*

## 13. Dedicated RFC Recommendations & Priority
1. **[CRITICAL] RFC-AUTO-006: Specification & Torque Intelligence**
   *Why:* The most heavily queried automotive facts. Critical for engine assembly and safety.
2. **[CRITICAL] RFC-AUTO-007: Diagnostic & DTC Intelligence**
   *Why:* Direct enabler for the future OBD-II diagnostic assistant.
3. **[HIGH] RFC-AUTO-008: Tool & Part Number Intelligence**
   *Why:* Necessary for repair planning and prerequisites generation.
4. **[MEDIUM] RFC-AUTO-009: Entity & Cross-Reference Resolution**
   *Why:* Required to stitch documents together into a cohesive graph, but depends on facts existing first.
5. **[MEDIUM] RFC-AUTO-010: Applicability & Vehicle Configuration Mapping**
   *Why:* Necessary before deploying to multi-vehicle datasets, but MVP can assume single-manual context.

## 14. Premature Architecture (Things To Defer)
- **LLM-based Fact Extraction:** Retain deterministic regex/NLP for Torque and DTCs. LLMs hallucinate numbers and units, which is unacceptable for torque specs.
- **Graph Databases (Neo4j):** Keep passing JSON/Pydantic models in memory. A heavy database adds unnecessary friction during extraction testing.
- **Vector Databases:** We need exact lookups (e.g., Torque for Bolt A), not semantic similarity yet.
- **Real-Time OBD-II Integration:** The knowledge base must be extracted and verified before connecting it to live vehicles.

## 15. Edge Product Implications
To support future edge-device / microcontroller deployment:
- Extracted facts must be serialized into flat, cacheable binary formats (e.g., SQLite, FlatBuffers).
- The extraction pipeline (heavy OCR/layout) remains in the cloud. The edge device only queries the pre-compiled `KnowledgeGraph` artifacts.
- Provenance references must be capable of rendering small, cropped image fragments of the manual on an edge screen, requiring precise bounding boxes.

## 16. Risks
- **False Positives in Normalization:** Misinterpreting a model number ("Model 45") as a torque value ("45 N·m").
- **Orphaned Facts:** Extracting a torque value without successfully identifying the fastener it applies to.
- **Silent Conflicts:** Missing a conflict because the target entity names didn't perfectly resolve to the same canonical ID.

## 17. Recommended Next Step
**Proceed with RFC-AUTO-006: Automotive Specification & Torque Intelligence.**
Torque values and clearances are the most structurally consistent, high-value facts in the manual. They force the implementation of the Unit Normalization Strategy and the Applicability Model early, setting a solid foundation for more complex entity resolution later.
