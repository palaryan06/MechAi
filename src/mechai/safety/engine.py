"""Core Safety Intelligence Engine implementation."""

from __future__ import annotations

import uuid
from typing import Sequence

from mechai.contracts.diagrams import AutomotiveDiagramSet
from mechai.contracts.ordering import OrderedLayoutCIR, OrderedLayoutRegion
from mechai.contracts.procedures import AutomotiveProcedureSet
from mechai.contracts.provenance import SourceRef
from mechai.contracts.safety import (
    AutomotiveSafetySet,
    SafetyAdmonition,
)
from mechai.contracts.tables import AutomotiveTableSet
from mechai.safety.action_extractor import ActionExtractor
from mechai.safety.admonition_detector import AdmonitionDetector
from mechai.safety.condition_extractor import ConditionExtractor
from mechai.safety.config import SafetyEngineConfig
from mechai.safety.consequence_extractor import ConsequenceExtractor
from mechai.safety.continuation import AdmonitionContinuationStitcher
from mechai.safety.hazard_extractor import HazardExtractor
from mechai.safety.relationship_builder import RelationshipBuilder
from mechai.safety.severity_classifier import SeverityClassifier


class AutomotiveSafetyEngine:
    """Reconstructs structured safety information from workshop manuals."""

    def __init__(
        self,
        config: SafetyEngineConfig | None = None,
        admonition_detector: AdmonitionDetector | None = None,
        severity_classifier: SeverityClassifier | None = None,
        hazard_extractor: HazardExtractor | None = None,
        condition_extractor: ConditionExtractor | None = None,
        consequence_extractor: ConsequenceExtractor | None = None,
        action_extractor: ActionExtractor | None = None,
        continuation_stitcher: AdmonitionContinuationStitcher | None = None,
        relationship_builder: RelationshipBuilder | None = None,
    ) -> None:
        """Initialize the safety engine with dependency injection."""
        self._config = config or SafetyEngineConfig()
        self._admonition_detector = admonition_detector or AdmonitionDetector(self._config)
        self._severity_classifier = severity_classifier or SeverityClassifier(self._config)
        self._hazard_extractor = hazard_extractor or HazardExtractor(self._config)
        self._condition_extractor = condition_extractor or ConditionExtractor(self._config)
        self._consequence_extractor = consequence_extractor or ConsequenceExtractor(self._config)
        self._action_extractor = action_extractor or ActionExtractor(self._config)
        self._continuation_stitcher = continuation_stitcher or AdmonitionContinuationStitcher()
        self._relationship_builder = relationship_builder or RelationshipBuilder(self._config)

    def reconstruct_safety(
        self,
        ordered_cir: OrderedLayoutCIR,
        procedure_set: AutomotiveProcedureSet | None = None,
        table_set: AutomotiveTableSet | None = None,
        diagram_set: AutomotiveDiagramSet | None = None,
    ) -> AutomotiveSafetySet:
        """Process the document to extract structured safety information."""
        
        all_regions: list[OrderedLayoutRegion] = []
        for page in ordered_cir.pages:
            all_regions.extend(page.ordered_regions)
            
        # 1. Stitch continuations (if any)
        stitched_regions = self._continuation_stitcher.stitch(all_regions)
        
        # 2. Detect Admonitions
        admonition_regions = self._admonition_detector.detect_admonition_regions(stitched_regions)
        
        # 3. Extract and Classify
        safety_admonitions: list[SafetyAdmonition] = []
        for region in admonition_regions:
            text = region.text.strip()
            provenance = SourceRef(page_number=region.page_number)
            
            # Severity
            severity, original_label = self._severity_classifier.classify_severity(text)
            
            # Hazard
            hazard_cat, hazard_conf = self._hazard_extractor.extract_hazard(text)
            
            # Conditions
            conditions = self._condition_extractor.extract_conditions(text, provenance)
            
            # Consequences
            consequences = self._consequence_extractor.extract_consequences(text, provenance)
            
            # Actions and Requirements
            actions = self._action_extractor.extract_actions(text, provenance)
            requirements = self._action_extractor.extract_requirements(text, provenance)
            
            # Compute confidence (conservative approach, if hazard uncertain, overall admonition is lower conf)
            overall_conf = 1.0 if hazard_conf >= 0.8 else 0.5
            
            safety_admonitions.append(
                SafetyAdmonition(
                    admonition_id=f"adm_{uuid.uuid4().hex[:8]}",
                    severity=severity,
                    original_label=original_label,
                    raw_text=text,
                    hazard_category=hazard_cat,
                    conditions=tuple(conditions),
                    consequences=tuple(consequences),
                    actions=tuple(actions),
                    requirements=tuple(requirements),
                    page_span=(region.page_number, region.page_number),
                    bbox=region.bbox,
                    confidence=overall_conf,
                    provenance=provenance,
                    region_ids=(region.id,),
                )
            )
            
        # 4. Build Relationships
        relationships = self._relationship_builder.build_relationships(
            safety_admonitions, procedure_set, table_set, diagram_set
        )
        
        return AutomotiveSafetySet.from_collections(
            document_id=ordered_cir.document_id,
            admonitions=safety_admonitions,
            relationships=relationships,
        )
