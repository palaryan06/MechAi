"""Evidence-aware deduplication of canonical facts."""

from __future__ import annotations

from typing import TypeVar, cast

from mechai.contracts.specifications import BaseCanonicalFact, AutomotiveTorqueFact, AutomotiveSpecificationFact

T = TypeVar("T", bound=BaseCanonicalFact)


class FactDeduplicator:
    """Merges canonical facts that represent the same engineering claim."""

    def _are_facts_identical(self, fact_a: T, fact_b: T) -> bool:
        """Determine if two facts make the exact same engineering claim."""
        if type(fact_a) is not type(fact_b):
            return False

        if fact_a.applicability != fact_b.applicability:
            return False

        if isinstance(fact_a, AutomotiveTorqueFact) and isinstance(fact_b, AutomotiveTorqueFact):
            return (
                fact_a.target_component == fact_b.target_component and
                fact_a.fastener_description == fact_b.fastener_description and
                fact_a.value.numeric_value == fact_b.value.numeric_value and
                fact_a.value.original_unit == fact_b.value.original_unit and
                fact_a.tightening_angle_degrees == fact_b.tightening_angle_degrees and
                fact_a.fastener_condition == fact_b.fastener_condition
            )
            
        if isinstance(fact_a, AutomotiveSpecificationFact) and isinstance(fact_b, AutomotiveSpecificationFact):
            return (
                fact_a.target_component == fact_b.target_component and
                fact_a.value.numeric_value == fact_b.value.numeric_value and
                fact_a.value.original_unit == fact_b.value.original_unit and
                fact_a.measurement_condition == fact_b.measurement_condition
            )
            
        return False

    def deduplicate(self, facts: list[T]) -> list[T]:
        """Merge identical facts by combining their evidence."""
        deduplicated: list[T] = []
        
        for fact in facts:
            merged = False
            for i, existing in enumerate(deduplicated):
                if self._are_facts_identical(fact, existing):
                    # Create a new combined evidence tuple
                    combined_evidence = tuple(list(existing.evidence) + list(fact.evidence))
                    # We can't mutate the frozen pydantic model, so we copy and update
                    updated = existing.model_copy(update={"evidence": combined_evidence})
                    deduplicated[i] = cast(T, updated)
                    merged = True
                    break
            
            if not merged:
                deduplicated.append(fact)
                
        return deduplicated
