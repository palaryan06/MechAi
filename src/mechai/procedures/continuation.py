"""Multi-Page Continuation Stitcher for Automotive Procedure Intelligence Engine (RFC-AUTO-002).

Detects multi-page procedure continuations across page breaks, repeated titles,
and sequential step numbering, merging them into a unified AutomotiveProcedure.
"""

from __future__ import annotations

import re

from mechai.contracts.procedures import AutomotiveProcedure, ProcedureStep
from mechai.procedures.config import ProcedureEngineConfig


class ProcedureContinuationStitcher:
    """Stitches broken multi-page procedures into coherent unified entities."""

    def __init__(self, config: ProcedureEngineConfig | None = None) -> None:
        self._config = config or ProcedureEngineConfig()

    def stitch_procedures(
        self,
        procedures: list[AutomotiveProcedure],
    ) -> list[AutomotiveProcedure]:
        """Iteratively stitch continuous multi-page procedure sequences."""
        if len(procedures) <= 1:
            return procedures

        stitched: list[AutomotiveProcedure] = []
        skip_indices: set[int] = set()

        for i, proc_a in enumerate(procedures):
            if i in skip_indices:
                continue

            current_proc = proc_a

            for j in range(i + 1, len(procedures)):
                if j in skip_indices:
                    continue

                proc_b = procedures[j]

                # Check if proc_b is a continuation of current_proc
                if self._is_continuation(current_proc, proc_b):
                    current_proc = self._merge_two_procedures(current_proc, proc_b)
                    skip_indices.add(j)
                else:
                    break

            stitched.append(current_proc)

        return stitched

    def _is_continuation(
        self,
        proc_a: AutomotiveProcedure,
        proc_b: AutomotiveProcedure,
    ) -> bool:
        """Evaluate if procedure B continues procedure A."""
        # 1. Must be on adjacent pages
        if proc_b.page_span[0] != proc_a.page_span[1] + 1:
            return False

        # 2. Check title similarity or (Continued) marker
        title_b_lower = proc_b.title.lower()
        title_a_lower = proc_a.title.lower()

        has_cont_marker = any(m in title_b_lower for m in self._config.continuation_title_markers)
        cleaned_b_title = title_b_lower
        for m in self._config.continuation_title_markers:
            cleaned_b_title = cleaned_b_title.replace(m, "").strip()

        is_title_match = (
            cleaned_b_title == title_a_lower
            or cleaned_b_title in title_a_lower
            or title_a_lower in cleaned_b_title
        )

        # 3. Check step continuity
        has_step_continuity = False
        if proc_a.steps and proc_b.steps:
            last_seq_a = proc_a.steps[-1].sequence_number
            first_seq_b = proc_b.steps[0].sequence_number
            if first_seq_b == last_seq_a + 1 or first_seq_b == 1:
                # If first step on page 2 is 1 or next integer, and title matches or has marker
                has_step_continuity = True

        return (has_cont_marker and is_title_match) or (is_title_match and has_step_continuity)

    def _merge_two_procedures(
        self,
        proc_a: AutomotiveProcedure,
        proc_b: AutomotiveProcedure,
    ) -> AutomotiveProcedure:
        """Merge procedure B into procedure A."""
        start_page = proc_a.page_span[0]
        end_page = proc_b.page_span[1]

        # Re-index steps to ensure monotonic global sequence
        merged_steps: list[ProcedureStep] = list(proc_a.steps)
        seq_offset = len(merged_steps)

        for step_b in proc_b.steps:
            new_seq = seq_offset + 1
            seq_offset += 1
            updated_step = ProcedureStep(
                step_id=step_b.step_id,
                sequence_number=new_seq,
                display_number=step_b.display_number,
                numbering_style=step_b.numbering_style,
                level=step_b.level,
                parent_step_id=step_b.parent_step_id,
                child_step_ids=step_b.child_step_ids,
                action_text=step_b.action_text,
                bbox=step_b.bbox,
                page_number=step_b.page_number,
                reading_order_ref=step_b.reading_order_ref,
                confidence=step_b.confidence,
                provenance=step_b.provenance,
                bound_admonitions=step_b.bound_admonitions,
                required_tools=step_b.required_tools,
                required_materials=step_b.required_materials,
                referenced_tables=step_b.referenced_tables,
                referenced_figures=step_b.referenced_figures,
                referenced_callouts=step_b.referenced_callouts,
                referenced_pages=step_b.referenced_pages,
                is_optional=step_b.is_optional,
                is_branching=step_b.is_branching,
                branch_condition=step_b.branch_condition,
            )
            merged_steps.append(updated_step)

        # Aggregate unique tools and materials
        seen_tools = {t.name for t in proc_a.required_tools}
        all_tools = list(proc_a.required_tools)
        for t in proc_b.required_tools:
            if t.name not in seen_tools:
                seen_tools.add(t.name)
                all_tools.append(t)

        seen_mats = {m.name for m in proc_a.required_materials}
        all_mats = list(proc_a.required_materials)
        for m in proc_b.required_materials:
            if m.name not in seen_mats:
                seen_mats.add(m.name)
                all_mats.append(m)

        # Combine admonitions
        all_admonitions = tuple(proc_a.bound_admonitions + proc_b.bound_admonitions)

        # Combine references
        all_tables = tuple(dict.fromkeys(proc_a.referenced_tables + proc_b.referenced_tables))
        all_figures = tuple(dict.fromkeys(proc_a.referenced_figures + proc_b.referenced_figures))
        all_regions = tuple(dict.fromkeys(proc_a.region_ids + proc_b.region_ids))

        return AutomotiveProcedure(
            procedure_id=proc_a.procedure_id,
            title=proc_a.title,
            description=proc_a.description or proc_b.description,
            category=proc_a.category,
            steps=tuple(merged_steps),
            preconditions=tuple(dict.fromkeys(proc_a.preconditions + proc_b.preconditions)),
            postconditions=tuple(dict.fromkeys(proc_a.postconditions + proc_b.postconditions)),
            required_tools=tuple(all_tools),
            required_materials=tuple(all_mats),
            bound_admonitions=all_admonitions,
            referenced_tables=all_tables,
            referenced_figures=all_figures,
            estimated_time=proc_a.estimated_time or proc_b.estimated_time,
            difficulty_level=proc_a.difficulty_level or proc_b.difficulty_level,
            page_span=(start_page, end_page),
            bbox=None,  # Multi-page procedures have composite bounding
            confidence=min(proc_a.confidence, proc_b.confidence),
            provenance=proc_a.provenance,
            region_ids=all_regions,
            is_multi_page=True,
        )
