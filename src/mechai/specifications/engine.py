"""Automotive Specification Intelligence Engine."""

from __future__ import annotations

from mechai.contracts.ordering import OrderedLayoutCIR
from mechai.contracts.procedures import AutomotiveProcedureSet
from mechai.contracts.tables import AutomotiveTableSet
from mechai.contracts.specifications import (
    ApplicabilityContext,
    AutomotiveSpecificationFact,
    AutomotiveSpecificationSet,
    AutomotiveTorqueFact,
)
from mechai.specifications.applicability import ApplicabilityResolver
from mechai.specifications.config import SpecificationConfig
from mechai.specifications.conflict_detector import ConflictDetector
from mechai.specifications.deduplication import FactDeduplicator
from mechai.specifications.specification_extractor import SpecificationExtractor
from mechai.specifications.torque_extractor import TorqueExtractor


class AutomotiveSpecificationEngine:
    """Orchestrates extraction of specifications and torques into canonical facts."""

    def __init__(
        self,
        config: SpecificationConfig,
        torque_extractor: TorqueExtractor,
        spec_extractor: SpecificationExtractor,
        applicability_resolver: ApplicabilityResolver,
        conflict_detector: ConflictDetector,
        deduplicator: FactDeduplicator,
    ) -> None:
        self._config = config
        self._torque_extractor = torque_extractor
        self._spec_extractor = spec_extractor
        self._applicability_resolver = applicability_resolver
        self._conflict_detector = conflict_detector
        self._deduplicator = deduplicator

    def _apply_context(self, fact: AutomotiveTorqueFact | AutomotiveSpecificationFact, context: ApplicabilityContext) -> AutomotiveTorqueFact | AutomotiveSpecificationFact:
        merged_context = self._applicability_resolver.merge_contexts(fact.applicability, context)
        return fact.model_copy(update={"applicability": merged_context})

    def extract_specifications(
        self,
        cir: OrderedLayoutCIR,
        tables: AutomotiveTableSet | None = None,
        procedures: AutomotiveProcedureSet | None = None,
    ) -> AutomotiveSpecificationSet:
        """Extract canonical specification facts from the document and structures."""
        
        raw_torques: list[AutomotiveTorqueFact] = []
        raw_specs: list[AutomotiveSpecificationFact] = []
        
        # 1. Extract from Procedures
        if procedures:
            for proc in procedures.procedures:
                # Resolve base applicability for this procedure
                base_app = self._applicability_resolver.extract_from_text(proc.title)
                
                for step in proc.steps:
                    step_app = self._applicability_resolver.extract_from_text(step.action_text)
                    merged_app = self._applicability_resolver.merge_contexts(base_app, step_app)
                    
                    tqs = self._torque_extractor.extract_from_text(step.action_text, step.provenance)
                    sps = self._spec_extractor.extract_from_text(step.action_text, step.provenance)
                    
                    for tq in tqs:
                        raw_torques.append(self._apply_context(tq, merged_app))  # type: ignore
                    for sp in sps:
                        raw_specs.append(self._apply_context(sp, merged_app))  # type: ignore
                        
        # 2. Extract from Tables
        if tables:
            for table in tables.tables:
                table_app = self._applicability_resolver.extract_from_text(table.title or "")
                
                # Iterate rows
                for row in table.rows:
                    row_text = " | ".join(cell.raw_text for cell in row.cells)
                    row_app = self._applicability_resolver.extract_from_text(row_text)
                    merged_app = self._applicability_resolver.merge_contexts(table_app, row_app)
                    
                    target_candidate = row.cells[0].raw_text if row.cells else None
                    
                    for cell in row.cells:
                        if not cell.raw_text.strip():
                            continue
                            
                        # If the cell looks like a header, skip fact extraction on it alone
                        if cell.cell_type == "header":
                            continue
                            
                        tqs = self._torque_extractor.extract_from_text(cell.raw_text, cell.provenance, target_override=target_candidate)
                        sps = self._spec_extractor.extract_from_text(cell.raw_text, cell.provenance, target_override=target_candidate)
                        
                        for tq in tqs:
                            raw_torques.append(self._apply_context(tq, merged_app))  # type: ignore
                        for sp in sps:
                            raw_specs.append(self._apply_context(sp, merged_app))  # type: ignore

        # 3. Deduplicate (Evidence gathering)
        dedup_torques = self._deduplicator.deduplicate(raw_torques)
        dedup_specs = self._deduplicator.deduplicate(raw_specs)

        # 4. Conflict Detection
        conflicts = self._conflict_detector.detect_conflicts(dedup_torques)
        conflicts.extend(self._conflict_detector.detect_conflicts(dedup_specs))

        return AutomotiveSpecificationSet(
            document_id=cir.document_id,
            torques=tuple(dedup_torques),
            specifications=tuple(dedup_specs),
            conflicts=tuple(conflicts),
        )
