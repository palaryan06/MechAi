"""Conflict detection subsystem for automotive facts."""

from __future__ import annotations

import uuid
from typing import TypeVar

from mechai.contracts.specifications import (
    BaseCanonicalFact,
    AutomotiveTorqueFact,
    AutomotiveSpecificationFact,
    ConflictEdge,
    ConflictCategory
)

T = TypeVar("T", bound=BaseCanonicalFact)


class ConflictDetector:
    """Detects conflicts between extracted canonical facts."""

    def _generate_id(self) -> str:
        return f"conflict_{uuid.uuid4().hex[:8]}"

    def _detect_torque_conflict(self, fact_a: AutomotiveTorqueFact, fact_b: AutomotiveTorqueFact) -> ConflictEdge | None:
        """Detect conflicts specifically for torque facts."""
        if not fact_a.target_component or not fact_b.target_component:
            return None
            
        # Target must be substantially similar to even be considered a conflict
        if fact_a.target_component.lower() != fact_b.target_component.lower():
            return None

        # Same target, different applicability
        if fact_a.applicability != fact_b.applicability:
            return ConflictEdge(
                id=self._generate_id(),
                fact_a_id=fact_a.id,
                fact_b_id=fact_b.id,
                category=ConflictCategory.APPLICABILITY_CONFLICT,
                reason="Same target, different applicability constraints."
            )

        # Same target, same applicability, different values
        if fact_a.value.canonical_value is not None and fact_b.value.canonical_value is not None:
            # We tolerate a small floating point difference (e.g. 0.1) due to normalizations
            if abs(fact_a.value.canonical_value - fact_b.value.canonical_value) > 0.1:
                return ConflictEdge(
                    id=self._generate_id(),
                    fact_a_id=fact_a.id,
                    fact_b_id=fact_b.id,
                    category=ConflictCategory.VALUE_CONFLICT,
                    reason=f"Conflicting values: {fact_a.value.canonical_value} vs {fact_b.value.canonical_value}"
                )
                
        # Same target, different fastener conditions (e.g. one says dry, one says oil)
        if fact_a.fastener_condition != fact_b.fastener_condition:
            return ConflictEdge(
                id=self._generate_id(),
                fact_a_id=fact_a.id,
                fact_b_id=fact_b.id,
                category=ConflictCategory.CONDITION_CONFLICT,
                reason="Conflicting fastener conditions (e.g. dry vs lubricated)."
            )

        return None

    def _detect_spec_conflict(self, fact_a: AutomotiveSpecificationFact, fact_b: AutomotiveSpecificationFact) -> ConflictEdge | None:
        """Detect conflicts specifically for general specifications."""
        if fact_a.fact_type != fact_b.fact_type:
            return None
            
        if not fact_a.target_component or not fact_b.target_component:
            return None
            
        if fact_a.target_component.lower() != fact_b.target_component.lower():
            return None

        if fact_a.applicability != fact_b.applicability:
            return ConflictEdge(
                id=self._generate_id(),
                fact_a_id=fact_a.id,
                fact_b_id=fact_b.id,
                category=ConflictCategory.APPLICABILITY_CONFLICT,
                reason="Same target, different applicability constraints."
            )

        if fact_a.value.canonical_value is not None and fact_b.value.canonical_value is not None:
            if abs(fact_a.value.canonical_value - fact_b.value.canonical_value) > 0.1:
                return ConflictEdge(
                    id=self._generate_id(),
                    fact_a_id=fact_a.id,
                    fact_b_id=fact_b.id,
                    category=ConflictCategory.VALUE_CONFLICT,
                    reason=f"Conflicting values: {fact_a.value.canonical_value} vs {fact_b.value.canonical_value}"
                )

        if fact_a.measurement_condition != fact_b.measurement_condition:
            return ConflictEdge(
                id=self._generate_id(),
                fact_a_id=fact_a.id,
                fact_b_id=fact_b.id,
                category=ConflictCategory.CONDITION_CONFLICT,
                reason="Conflicting measurement conditions."
            )
            
        return None

    def detect_conflicts(self, facts: list[T]) -> list[ConflictEdge]:
        """Detect conflicts among a list of facts (O(N^2) pairwise comparison)."""
        conflicts: list[ConflictEdge] = []
        n = len(facts)
        
        for i in range(n):
            for j in range(i + 1, n):
                fact_a = facts[i]
                fact_b = facts[j]
                
                conflict = None
                if isinstance(fact_a, AutomotiveTorqueFact) and isinstance(fact_b, AutomotiveTorqueFact):
                    conflict = self._detect_torque_conflict(fact_a, fact_b)
                elif isinstance(fact_a, AutomotiveSpecificationFact) and isinstance(fact_b, AutomotiveSpecificationFact):
                    conflict = self._detect_spec_conflict(fact_a, fact_b)
                    
                if conflict:
                    conflicts.append(conflict)
                    
        return conflicts
