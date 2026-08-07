"""Automotive Procedure Intelligence Engine (RFC-AUTO-002).

Deterministically reconstructs structured OEM automotive repair procedures from OrderedLayoutCIR
and AutomotiveTableSet, supporting multi-level hierarchies, tool/SST extraction, admonition binding,
cross-reference resolution, and multi-page continuation stitching.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from mechai.contracts.layout import RegionType
from mechai.contracts.ordering import OrderedLayoutCIR, OrderedLayoutRegion, OrderedPageCIR
from mechai.contracts.procedures import (
    AdmonitionType,
    AutomotiveProcedure,
    AutomotiveProcedureEngineProtocol,
    AutomotiveProcedureSet,
    BoundAdmonition,
    ProcedureCategory,
    ProcedureStep,
    RequiredMaterial,
    RequiredTool,
    StepNumberingStyle,
)
from mechai.contracts.provenance import ExtractionMethod, SourceRef
from mechai.procedures.admonition_binder import AdmonitionBinder
from mechai.procedures.boundary_detector import BoundaryDetector
from mechai.procedures.config import ProcedureEngineConfig
from mechai.procedures.continuation import ProcedureContinuationStitcher
from mechai.procedures.cross_ref_resolver import CrossReferenceResolver
from mechai.procedures.requirement_extractor import RequirementExtractor
from mechai.procedures.step_parser import ParsedStepLine, StepParser

if TYPE_CHECKING:
    from collections.abc import Iterator

    from mechai.contracts.tables import AutomotiveTableSet


class AutomotiveProcedureEngine(AutomotiveProcedureEngineProtocol):
    """Stage 7 Automotive Procedure Intelligence Engine."""

    def __init__(self, config: ProcedureEngineConfig | None = None) -> None:
        self._config = config or ProcedureEngineConfig()
        self._boundary_detector = BoundaryDetector(self._config)
        self._step_parser = StepParser(self._config)
        self._req_extractor = RequirementExtractor(self._config)
        self._admonition_binder = AdmonitionBinder(self._config)
        self._cross_ref_resolver = CrossReferenceResolver(self._config)
        self._continuation_stitcher = ProcedureContinuationStitcher(self._config)

    def reconstruct_procedures(
        self,
        ordered_cir: OrderedLayoutCIR,
        table_set: AutomotiveTableSet | None = None,
    ) -> AutomotiveProcedureSet:
        """Reconstruct structured automotive procedures across an entire ordered document."""
        raw_procedures: list[AutomotiveProcedure] = []

        for page in ordered_cir.pages:
            page_procs = self.reconstruct_page_procedures(page, table_set=table_set)
            raw_procedures.extend(page_procs)

        # Multi-page continuation stitching
        stitched_procedures = self._continuation_stitcher.stitch_procedures(raw_procedures)

        total_steps = sum(p.total_steps for p in stitched_procedures)

        return AutomotiveProcedureSet(
            document_id=ordered_cir.document_id,
            procedures=tuple(stitched_procedures),
            total_procedures=len(stitched_procedures),
            total_steps=total_steps,
            provenance=ordered_cir.provenance,
        )

    def reconstruct_stream(
        self,
        pages: Iterator[OrderedPageCIR],
        table_set: AutomotiveTableSet | None = None,
    ) -> Iterator[AutomotiveProcedure]:
        """Stream reconstructed procedures page-by-page."""
        for page in pages:
            page_procs = self.reconstruct_page_procedures(page, table_set=table_set)
            for proc in page_procs:
                yield proc

    def reconstruct_page_procedures(
        self,
        page: OrderedPageCIR,
        table_set: AutomotiveTableSet | None = None,
    ) -> list[AutomotiveProcedure]:
        """Reconstruct procedures located on a single ordered page."""
        procedures: list[AutomotiveProcedure] = []
        ordered_regions = list(page.ordered_regions)
        if not ordered_regions:
            return []

        # Find procedure boundary starts
        proc_groups: list[tuple[OrderedLayoutRegion, list[OrderedLayoutRegion]]] = []
        current_header: OrderedLayoutRegion | None = None
        current_body: list[OrderedLayoutRegion] = []

        for region in ordered_regions:
            if self._boundary_detector.is_procedure_heading(region):
                if current_header is not None and current_body:
                    proc_groups.append((current_header, current_body))
                current_header = region
                current_body = []
            elif current_header is not None:
                # Include region if it belongs to procedure flow
                if region.region_type in (
                    RegionType.LIST,
                    RegionType.BODY,
                    RegionType.PARAGRAPH,
                    RegionType.WARNING_BOX,
                    RegionType.NOTE_BOX,
                    RegionType.UNKNOWN,
                ):
                    current_body.append(region)
                elif region.region_type in (RegionType.HEADING, RegionType.TITLE):
                    # Another non-procedure heading terminates current procedure
                    if current_body:
                        proc_groups.append((current_header, current_body))
                    current_header = None
                    current_body = []

        if current_header is not None and current_body:
            proc_groups.append((current_header, current_body))

        for header_reg, body_regs in proc_groups:
            proc = self._assemble_single_procedure(header_reg, body_regs, page.page_number, table_set)
            if proc is not None and len(proc.steps) > 0:
                procedures.append(proc)

        return procedures

    def _assemble_single_procedure(
        self,
        header: OrderedLayoutRegion,
        body_regions: list[OrderedLayoutRegion],
        page_number: int,
        table_set: AutomotiveTableSet | None = None,
    ) -> AutomotiveProcedure | None:
        """Assemble an atomic AutomotiveProcedure from its constituent regions."""
        title = header.text.strip()
        category = self._boundary_detector.classify_category(title)
        proc_id = f"proc_p{page_number}_{header.id}"

        # Collect raw step lines across body regions
        raw_parsed_lines: list[tuple[ParsedStepLine, OrderedLayoutRegion]] = []
        bound_admonitions_pool: list[BoundAdmonition] = []
        intro_text_parts: list[str] = []

        for region in body_regions:
            # Check for admonition boxes
            if region.region_type in (RegionType.WARNING_BOX, RegionType.NOTE_BOX):
                adms = self._admonition_binder.extract_admonitions_from_region(region)
                bound_admonitions_pool.extend(adms)
                continue

            # Parse lines for steps
            parsed_lines = self._step_parser.parse_text_lines(region.text)
            for pl in parsed_lines:
                if pl.numbering_style == StepNumberingStyle.UNNUMBERED:
                    # Check if unnumbered text is precondition or postcondition narrative
                    lower_act = pl.action_text.lower()
                    is_pre = any(p in lower_act for p in ("preparation:", "prerequisites:", "prior to", "before removal", "before starting"))
                    is_post = any(p in lower_act for p in ("after installation:", "after reassembly:", "post-service:", "inspection after"))
                    if is_pre or not raw_parsed_lines:
                        intro_text_parts.append(pl.action_text)
                    elif is_post:
                        pass  # Captured via postconditions extraction
                    else:
                        raw_parsed_lines.append((pl, region))
                else:
                    raw_parsed_lines.append((pl, region))

        if not raw_parsed_lines:
            return None

        # Build hierarchical steps and link parent-child relationships
        steps = self._build_hierarchical_steps(
            proc_id=proc_id,
            raw_lines=raw_parsed_lines,
            page_number=page_number,
            admonitions=bound_admonitions_pool,
            table_set=table_set,
        )

        proc_admonitions: list[BoundAdmonition] = []
        if not steps:
            proc_admonitions.extend(bound_admonitions_pool)

        # Extract requirements across procedure
        all_text = " ".join([header.text] + [r.text for r in body_regions])
        preconditions = self._boundary_detector.extract_preconditions(all_text)
        postconditions = self._boundary_detector.extract_postconditions(all_text)
        labor_time, difficulty = self._boundary_detector.extract_labor_time_and_difficulty(all_text)

        # Aggregate unique tools and materials
        seen_tools: set[str] = set()
        proc_tools: list[RequiredTool] = []
        for s in steps:
            for t in s.required_tools:
                if t.name not in seen_tools:
                    seen_tools.add(t.name)
                    proc_tools.append(t)

        seen_mats: set[str] = set()
        proc_mats: list[RequiredMaterial] = []
        for s in steps:
            for m in s.required_materials:
                if m.name not in seen_mats:
                    seen_mats.add(m.name)
                    proc_mats.append(m)

        # Aggregate references
        all_tables: list[str] = []
        all_figures: list[str] = []
        for s in steps:
            for tbl_ref in s.referenced_tables:
                if tbl_ref not in all_tables:
                    all_tables.append(tbl_ref)
            for fig_ref in s.referenced_figures:
                if fig_ref not in all_figures:
                    all_figures.append(fig_ref)

        all_region_ids = [header.id] + [r.id for r in body_regions]

        return AutomotiveProcedure(
            procedure_id=proc_id,
            title=header.text.strip(),
            description=f"Procedure for {header.text.strip()}",
            category=category,
            steps=tuple(steps),
            preconditions=tuple(preconditions),
            postconditions=tuple(postconditions),
            required_tools=tuple(proc_tools),
            required_materials=tuple(proc_mats),
            bound_admonitions=tuple(proc_admonitions),
            referenced_tables=tuple(all_tables),
            referenced_figures=tuple(all_figures),
            estimated_time=labor_time,
            difficulty_level=difficulty,
            page_span=(page_number, page_number),
            bbox=header.bbox,
            confidence=0.98,
            provenance=header.provenance,
            region_ids=tuple(all_region_ids),
            is_multi_page=False,
        )

    def _build_hierarchical_steps(
        self,
        proc_id: str,
        raw_lines: list[tuple[ParsedStepLine, OrderedLayoutRegion]],
        page_number: int,
        admonitions: list[BoundAdmonition] | None = None,
        table_set: AutomotiveTableSet | None = None,
    ) -> list[ProcedureStep]:
        """Convert parsed lines into ProcedureStep models and build parent/child hierarchies."""
        steps_meta: list[dict] = []
        parent_stack: list[dict] = []  # Stack of (level, step_dict)

        for seq_idx, (parsed_line, region) in enumerate(raw_lines, start=1):
            step_id = f"{proc_id}_s{seq_idx:02d}"
            tools = self._req_extractor.extract_tools(parsed_line.action_text)
            materials = self._req_extractor.extract_materials(parsed_line.action_text)
            tables, figs, callouts, pages = self._cross_ref_resolver.resolve_references(
                parsed_line.action_text,
                table_set=table_set,
            )

            # Determine hierarchy level
            level = parsed_line.indent_level
            if parsed_line.numbering_style == StepNumberingStyle.NUMBERED:
                level = 0
            elif parsed_line.numbering_style in (StepNumberingStyle.ALPHABETICAL, StepNumberingStyle.BULLET):
                level = max(1, level)
            elif parsed_line.numbering_style == StepNumberingStyle.ROMAN:
                level = max(2, level)

            # Find parent in stack
            while parent_stack and parent_stack[-1]["level"] >= level:
                parent_stack.pop()

            parent_id = parent_stack[-1]["step_id"] if parent_stack else None

            step_dict = {
                "step_id": step_id,
                "sequence_number": seq_idx,
                "display_number": parsed_line.display_number,
                "numbering_style": parsed_line.numbering_style,
                "level": level,
                "parent_step_id": parent_id,
                "child_step_ids": [],
                "action_text": parsed_line.action_text,
                "bbox": region.bbox,
                "page_number": page_number,
                "reading_order_ref": region.id,
                "confidence": region.confidence,
                "provenance": region.provenance,
                "bound_admonitions": (),
                "required_tools": tuple(tools),
                "required_materials": tuple(materials),
                "referenced_tables": tables,
                "referenced_figures": figs,
                "referenced_callouts": callouts,
                "referenced_pages": pages,
                "is_optional": parsed_line.is_optional,
                "is_branching": parsed_line.is_branching,
                "branch_condition": parsed_line.branch_condition,
            }

            if parent_stack:
                parent_stack[-1]["child_step_ids"].append(step_id)

            parent_stack.append(step_dict)
            steps_meta.append(step_dict)

        # Distribute admonitions to closest steps
        if admonitions and steps_meta:
            for adm in admonitions:
                closest_idx = 0
                min_dist = float("inf")
                for idx, sm in enumerate(steps_meta):
                    dist = abs(sm["bbox"].top - adm.bbox.top)
                    if dist < min_dist:
                        min_dist = dist
                        closest_idx = idx
                current_adms = list(steps_meta[closest_idx]["bound_admonitions"])
                current_adms.append(adm)
                steps_meta[closest_idx]["bound_admonitions"] = tuple(current_adms)

        # Convert dictionaries to immutable ProcedureStep objects
        result_steps: list[ProcedureStep] = []
        for sm in steps_meta:
            result_steps.append(
                ProcedureStep(
                    step_id=sm["step_id"],
                    sequence_number=sm["sequence_number"],
                    display_number=sm["display_number"],
                    numbering_style=sm["numbering_style"],
                    level=sm["level"],
                    parent_step_id=sm["parent_step_id"],
                    child_step_ids=tuple(sm["child_step_ids"]),
                    action_text=sm["action_text"],
                    bbox=sm["bbox"],
                    page_number=sm["page_number"],
                    reading_order_ref=sm["reading_order_ref"],
                    confidence=sm["confidence"],
                    provenance=sm["provenance"],
                    bound_admonitions=sm["bound_admonitions"],
                    required_tools=sm["required_tools"],
                    required_materials=sm["required_materials"],
                    referenced_tables=sm["referenced_tables"],
                    referenced_figures=sm["referenced_figures"],
                    referenced_callouts=sm["referenced_callouts"],
                    referenced_pages=sm["referenced_pages"],
                    is_optional=sm["is_optional"],
                    is_branching=sm["is_branching"],
                    branch_condition=sm["branch_condition"],
                )
            )

        return result_steps
