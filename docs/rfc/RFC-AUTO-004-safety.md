# RFC-AUTO-004: Automotive Safety & Admonition Intelligence Engine

## Objective
Implement deterministic extraction and binding of safety critical information (Warnings, Cautions, Notes, Danger) from automotive workshop manuals into structured models.

## Architecture
The engine operates after the `OrderedLayoutCIR` is produced, leveraging the layout bounding boxes and the reading order. It integrates with previously extracted structures (`AutomotiveTableSet`, `AutomotiveProcedureSet`, `AutomotiveDiagramSet`) to build contextual relationships.

### Key Components
- **AdmonitionDetector**: Identifies safety layout regions (WARNING_BOX, NOTE_BOX) or uses deterministic textual heuristic fallback.
- **SeverityClassifier**: Classifies text severity based on predefined keywords into `SafetySeverity` enums.
- **HazardExtractor**: Identifies deterministic hazard phrases (e.g. "battery", "hot", "fire") into `HazardCategory`.
- **ConditionExtractor**: Extracts clauses triggered by "when", "before", "during", mapping them to `SafetyCondition`.
- **ActionExtractor**: Extracts actionable guidance ("never", "do not", "always") and restricts vs. requirements into `SafetyAction` and `SafetyRequirement`.
- **ConsequenceExtractor**: Extracts consequences into `SafetyConsequence`.
- **RelationshipBuilder / Binders**: Establishes `SafetyRelationship` instances by evaluating spatial proximity or textual references binding admonitions to procedures, diagrams, and tables.

## Constraints & Principles
- **No LLMs**: Driven entirely by deterministic config and regexes.
- **Evidence > Inference**: Unknown hazards default to `UNKNOWN` or `UNCERTAIN`. Certainty is never hallucinated.
- **Immutability**: All structures use `pydantic` `frozen=True` and strict validation.
- **Provenance**: Every extracted entity and relationship retains strict `SourceRef` linkage to its page and `OrderedLayoutRegion`.
