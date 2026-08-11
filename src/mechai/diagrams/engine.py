"""Automotive Diagram Intelligence Engine."""

from __future__ import annotations

from mechai.contracts.diagrams import AutomotiveDiagram, AutomotiveDiagramSet
from mechai.contracts.ordering import OrderedLayoutCIR, OrderedPageCIR
from mechai.contracts.procedures import AutomotiveProcedureSet
from mechai.contracts.provenance import ExtractionMethod, SourceRef
from mechai.contracts.tables import AutomotiveTableSet
from mechai.diagrams.callout_detector import CalloutDetector
from mechai.diagrams.classifier import DiagramClassifier
from mechai.diagrams.config import DiagramEngineConfig
from mechai.diagrams.diagram_detector import DiagramDetector
from mechai.diagrams.label_detector import LabelDetector
from mechai.diagrams.procedure_linker import ProcedureLinker
from mechai.diagrams.relationship_builder import RelationshipBuilder
from mechai.diagrams.table_linker import TableLinker


class AutomotiveDiagramEngine:
    """Engine for reconstructing structured automotive diagrams from layout streams.
    
    Implements AutomotiveDiagramEngineProtocol.
    """

    def __init__(self, config: DiagramEngineConfig | None = None) -> None:
        """Initialize the diagram engine and its subcomponents."""
        self._config = config or DiagramEngineConfig()
        
        self._diagram_detector = DiagramDetector(self._config)
        self._callout_detector = CalloutDetector(self._config)
        self._label_detector = LabelDetector(self._config)
        self._relationship_builder = RelationshipBuilder(self._config)
        self._classifier = DiagramClassifier(self._config)
        self._table_linker = TableLinker()
        self._procedure_linker = ProcedureLinker()

    def reconstruct_diagrams(
        self,
        ordered_cir: OrderedLayoutCIR,
        table_set: AutomotiveTableSet | None = None,
        procedure_set: AutomotiveProcedureSet | None = None,
    ) -> AutomotiveDiagramSet:
        """Process an entire document to reconstruct structured automotive diagrams."""
        all_diagrams: list[AutomotiveDiagram] = []
        diag_idx = 1
        
        for page in ordered_cir.pages:
            diagram_groups = self._diagram_detector.detect_diagrams(page.ordered_regions)
            
            for group in diagram_groups:
                fig_reg = group["figure_region"]
                caption_reg = group["caption_region"]
                content_regs = group["content_regions"]
                
                # Extract figure
                figure = self._diagram_detector.extract_figure(caption_reg)
                
                # Extract callouts and labels from content regions
                callouts = []
                labels = []
                region_ids = [fig_reg.id]
                if caption_reg:
                    region_ids.append(caption_reg.id)
                    
                for r in content_regs:
                    region_ids.append(r.id)
                    detected_callouts = self._callout_detector.detect_callouts(r)
                    if detected_callouts:
                        callouts.extend(detected_callouts)
                    else:
                        label = self._label_detector.detect_label(r)
                        if label:
                            labels.append(label)
                            
                # Build relationships
                relationships = self._relationship_builder.build_relationships(
                    callouts=callouts,
                    labels=labels,
                    leader_lines=[],  # Vector path extraction not implemented yet
                    page_number=page.page_number,
                )
                
                # Classify diagram type
                diagram_type = self._classifier.classify(figure, tuple(labels), tuple(callouts))
                
                # Link procedures and tables
                linked_proc_ids = self._procedure_linker.link_procedures(figure, procedure_set)
                linked_table_ids = self._table_linker.link_tables(figure, tuple(labels), table_set)
                
                # Construct AutomotiveDiagram
                diag_id = f"diag_p{page.page_number}_{diag_idx:03d}"
                diag = AutomotiveDiagram(
                    diagram_id=diag_id,
                    diagram_type=diagram_type,
                    figure=figure,
                    callouts=tuple(callouts),
                    labels=tuple(labels),
                    leader_lines=tuple(),
                    relationships=tuple(relationships),
                    linked_procedure_ids=tuple(linked_proc_ids),
                    linked_table_ids=tuple(linked_table_ids),
                    page_span=(page.page_number, page.page_number),
                    bbox=fig_reg.bbox,
                    confidence=fig_reg.confidence,
                    provenance=SourceRef(
                        page_number=page.page_number,
                        extraction_method=ExtractionMethod.RULE,
                        confidence=fig_reg.confidence,
                        bbox=fig_reg.bbox,
                    ),
                    region_ids=tuple(region_ids),
                )
                
                all_diagrams.append(diag)
                diag_idx += 1
                
        return AutomotiveDiagramSet.from_diagrams(
            document_id=ordered_cir.document_id,
            diagrams=all_diagrams,
        )
