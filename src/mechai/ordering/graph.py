"""Graph builder and topological validator for Reading Order Engine.

Constructs Directed Acyclic Graphs (DAG), ensures strict acyclicity,
validates edge transitions, and derives alternative reading trajectories.
"""

from __future__ import annotations

import math

from mechai.contracts.ordering import (
    AlternativeReadingPath,
    FlowEdgeType,
    ReadingOrderEdge,
    ReadingOrderEvidence,
    ReadingOrderGraph,
    ReadingOrderNode,
)


class ReadingOrderGraphBuilder:
    """Stateful builder for constructing, validating, and finalizing ReadingOrderGraph instances."""

    def __init__(self) -> None:
        self._nodes: dict[str, ReadingOrderNode] = {}
        self._edges: list[ReadingOrderEdge] = []
        self._edge_keys: set[tuple[str, str, FlowEdgeType]] = set()
        self._primary_path: list[str] = []
        self._alternative_paths: list[AlternativeReadingPath] = []

    def add_node(self, node: ReadingOrderNode) -> None:
        """Add or update a node in the graph."""
        self._nodes[node.region_id] = node

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: FlowEdgeType,
        confidence: float,
        evidence: ReadingOrderEvidence,
    ) -> bool:
        """Add a directed edge if not already present. Returns True if edge added."""
        if source_id == target_id:
            # Self-loops are strictly prohibited in reading order DAGs
            return False

        key = (source_id, target_id, edge_type)
        if key in self._edge_keys:
            return False

        edge = ReadingOrderEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            confidence=confidence,
            evidence=evidence,
        )
        self._edges.append(edge)
        self._edge_keys.add(key)
        return True

    def set_primary_path(self, path: list[str] | tuple[str, ...]) -> None:
        """Set the main linear reading traversal sequence of region IDs."""
        self._primary_path = list(path)

    def add_alternative_path(self, alt_path: AlternativeReadingPath) -> None:
        """Register an alternative reading traversal path (e.g. sidebar branch)."""
        self._alternative_paths.append(alt_path)

    def compute_sequence_confidence(self) -> float:
        """Derive overall sequence confidence score from primary path edges."""
        if not self._primary_path or len(self._primary_path) <= 1:
            return 1.0

        # Find edges connecting consecutive elements in primary path
        confidences: list[float] = []
        for i in range(len(self._primary_path) - 1):
            src = self._primary_path[i]
            dst = self._primary_path[i + 1]
            matching = [
                e.confidence for e in self._edges if e.source_id == src and e.target_id == dst
            ]
            if matching:
                confidences.append(max(matching))
            else:
                confidences.append(0.80)

        if not confidences:
            return 1.0

        # Geometric mean
        log_sum = sum(math.log(max(1e-4, c)) for c in confidences)
        return float(min(1.0, max(0.0, math.exp(log_sum / len(confidences)))))

    def build(self) -> ReadingOrderGraph:
        """Finalize, validate acyclicity, and return immutable ReadingOrderGraph."""
        # Ensure DAG validity: remove any accidental back-edges that create cycles
        valid_edges = self._eliminate_cycles(self._edges)

        return ReadingOrderGraph(
            nodes=tuple(self._nodes.values()),
            edges=tuple(valid_edges),
            primary_path=tuple(self._primary_path),
            alternative_paths=tuple(self._alternative_paths),
        )

    def _eliminate_cycles(self, edges: list[ReadingOrderEdge]) -> list[ReadingOrderEdge]:
        """Verify acyclicity and filter out any cycle-inducing edges if necessary."""
        # Build adjacency
        adj: dict[str, list[str]] = {nid: [] for nid in self._nodes}
        accepted_edges: list[ReadingOrderEdge] = []

        def creates_cycle(src: str, dst: str) -> bool:
            # If dst can reach src via accepted edges, adding src->dst creates a cycle
            visited: set[str] = set()
            stack = [dst]
            while stack:
                curr = stack.pop()
                if curr == src:
                    return True
                if curr not in visited:
                    visited.add(curr)
                    stack.extend(adj.get(curr, []))
            return False

        for edge in edges:
            if edge.source_id not in self._nodes or edge.target_id not in self._nodes:
                continue
            if not creates_cycle(edge.source_id, edge.target_id):
                adj[edge.source_id].append(edge.target_id)
                accepted_edges.append(edge)

        return accepted_edges
