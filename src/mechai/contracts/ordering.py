"""Data contracts and stage protocols for Reading Order Engine (Stage 2.1).

RFC-008: Topological Spatial Sorting, Reading Order Graphs, and Human Flow Determination.
All models are strictly typed, immutable (frozen=True), and fully validated.
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import StrEnum
import heapq
from typing import Annotated, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from mechai.contracts.layout import (
    ColumnGutter,
    LayoutCIR,
    PageLayoutCIR,
    PageMargins,
    RegionType,
)
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef


class FlowEdgeType(StrEnum):
    """Semantic and spatial relationship types connecting nodes in the ReadingOrderGraph."""

    NATURAL_FLOW = "NaturalFlow"
    COLUMN_WRAP = "ColumnWrap"
    SPANNING_DESCENT = "SpanningDescent"
    SPANNING_ASCENT = "SpanningAscent"
    CAPTION_LINK = "CaptionLink"
    CALLOUT_ASIDE = "CalloutAside"
    SIDEBAR_BRANCH = "SidebarBranch"
    CROSS_PAGE_FLOW = "CrossPageFlow"
    HEADER_ATTACHMENT = "HeaderAttachment"
    FOOTER_ATTACHMENT = "FooterAttachment"


class ReadingFlowType(StrEnum):
    """Categorization of overall reading flow structure on a page."""

    SINGLE_COLUMN = "SingleColumn"
    MULTI_COLUMN_WRAP = "MultiColumnWrap"
    SPANNING_INTERLEAVED = "SpanningInterleaved"
    SIDEBAR_INTERRUPTED = "SidebarInterrupted"
    COMPLEX_IRREGULAR = "ComplexIrregular"


class ReadingOrderEvidence(BaseModel):
    """Explainable geometric and typographical rationale justifying a reading order transition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    decision_rule: str = Field(
        description="Deterministic rule identifier (e.g. 'column_vertical_flow')"
    )
    source_zone: str = Field(description="Reading zone identifier of source region")
    target_zone: str = Field(description="Reading zone identifier of target region")
    spatial_distance_pt: float = Field(
        ge=0.0, description="Euclidean / vertical distance in points"
    )
    confidence: Annotated[
        float, Field(ge=0.0, le=1.0, description="Confidence in this ordering decision")
    ]
    rationale: str = Field(
        description="Human-readable explanation of why this transition was selected"
    )


class ReadingOrderNode(BaseModel):
    """Node in the ReadingOrderGraph corresponding to a classified LayoutRegion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    region_id: str = Field(min_length=1, description="Identifier of associated LayoutRegion")
    page_number: Annotated[int, Field(ge=1)]
    region_type: RegionType
    reading_zone_id: str | None = None
    column_index: int | None = None
    bbox: BoundingBox
    order_index: int = Field(ge=0, description="0-based or 1-based traversal rank")
    is_primary_flow: bool = Field(default=True, description="True if part of main linear flow")


class ReadingOrderEdge(BaseModel):
    """Directed edge in the ReadingOrderGraph representing a visual or logical reading transition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_id: str = Field(min_length=1, description="Region ID of predecessor node")
    target_id: str = Field(min_length=1, description="Region ID of successor node")
    edge_type: FlowEdgeType
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    evidence: ReadingOrderEvidence


class AlternativeReadingPath(BaseModel):
    """An alternative valid reading traversal (e.g., reading a sidebar or skipping callout box)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path_id: str = Field(min_length=1)
    name: str
    description: str
    branch_source_id: str
    rejoin_target_id: str | None = None
    region_ids: tuple[str, ...] = Field(default_factory=tuple)
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]


class ReadingOrderGraph(BaseModel):
    """Directed Acyclic Graph (DAG) representing the complete reading topology of regions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    nodes: tuple[ReadingOrderNode, ...] = Field(default_factory=tuple)
    edges: tuple[ReadingOrderEdge, ...] = Field(default_factory=tuple)
    primary_path: tuple[str, ...] = Field(default_factory=tuple)
    alternative_paths: tuple[AlternativeReadingPath, ...] = Field(default_factory=tuple)

    @property
    def is_dag(self) -> bool:
        """Verify the graph is directed and strictly acyclic."""
        # Simple cycle check via Kahn's algorithm or DFS
        adj: dict[str, list[str]] = {n.region_id: [] for n in self.nodes}
        in_degree: dict[str, int] = {n.region_id: 0 for n in self.nodes}

        for edge in self.edges:
            if edge.source_id in adj and edge.target_id in adj:
                adj[edge.source_id].append(edge.target_id)
                in_degree[edge.target_id] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        visited_count = 0

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for neighbor in adj.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return visited_count == len(self.nodes)

    def topological_sort(self) -> list[str]:
        """Compute a topological ordering of nodes in the graph."""
        adj: dict[str, list[str]] = {n.region_id: [] for n in self.nodes}
        in_degree: dict[str, int] = {n.region_id: 0 for n in self.nodes}

        for edge in self.edges:
            if edge.source_id in adj and edge.target_id in adj:
                adj[edge.source_id].append(edge.target_id)
                in_degree[edge.target_id] += 1

        # Stable sort prioritizing primary path order via min-heap
        order_map = {nid: idx for idx, nid in enumerate(self.primary_path)}
        heap: list[tuple[int, str]] = [
            (order_map.get(nid, 999999), nid)
            for nid, deg in in_degree.items()
            if deg == 0
        ]
        heapq.heapify(heap)
        result: list[str] = []

        while heap:
            _, curr = heapq.heappop(heap)
            result.append(curr)
            for neighbor in adj.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    heapq.heappush(heap, (order_map.get(neighbor, 999999), neighbor))

        return result

    def get_node(self, region_id: str) -> ReadingOrderNode | None:
        """Retrieve node by region identifier."""
        for n in self.nodes:
            if n.region_id == region_id:
                return n
        return None

    def get_outgoing_edges(self, source_id: str) -> list[ReadingOrderEdge]:
        """Retrieve all directed outgoing edges originating from source_id."""
        return [e for e in self.edges if e.source_id == source_id]

    def get_incoming_edges(self, target_id: str) -> list[ReadingOrderEdge]:
        """Retrieve all directed incoming edges terminating at target_id."""
        return [e for e in self.edges if e.target_id == target_id]


class OrderedLayoutRegion(BaseModel):
    """Enriched LayoutRegion possessing an assigned reading sequence index and flow metadata."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1, description="Unique region identifier")
    bbox: BoundingBox
    page_number: Annotated[int, Field(ge=1)]
    region_type: RegionType
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    provenance: SourceRef
    text: str = Field(default="")
    reading_zone_id: str | None = None
    column_index: int | None = None
    reading_order_index: Annotated[
        int, Field(ge=1, description="1-based primary reading sequence rank")
    ]
    reading_depth: int = Field(
        default=0, ge=0, description="0=Primary narrative flow, 1+=Aside/Callout"
    )
    is_primary_flow: bool = Field(
        default=True, description="True if element belongs to main linear reading path"
    )


class OrderedPageCIR(BaseModel):
    """Canonical Intermediate Representation of a page with deterministic human reading order."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    page_number: Annotated[int, Field(ge=1)]
    width: float = Field(gt=0.0)
    height: float = Field(gt=0.0)
    margins: PageMargins
    header_zone: BoundingBox | None = None
    footer_zone: BoundingBox | None = None
    columns: tuple[ColumnGutter, ...] = Field(default_factory=tuple)
    ordered_regions: tuple[OrderedLayoutRegion, ...] = Field(default_factory=tuple)
    reading_order_graph: ReadingOrderGraph
    primary_sequence: tuple[str, ...] = Field(default_factory=tuple)
    alternative_paths: tuple[AlternativeReadingPath, ...] = Field(default_factory=tuple)
    sequence_confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    reading_flow_type: ReadingFlowType


class OrderedLayoutCIR(BaseModel):
    """Complete document-level Canonical Intermediate Representation with unified reading order."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1)
    source_path: str | None = None
    total_pages: Annotated[int, Field(ge=1)]
    pages: tuple[OrderedPageCIR, ...] = Field(default_factory=tuple)
    ordered_regions: tuple[OrderedLayoutRegion, ...] = Field(default_factory=tuple)
    global_graph: ReadingOrderGraph
    provenance: SourceRef = Field(
        default_factory=lambda: SourceRef(
            page_number=1,
            extraction_method=ExtractionMethod.RULE,
            confidence=1.0,
        )
    )


@runtime_checkable
class ReadingOrderEngineProtocol(Protocol):
    """Stage 2.1 Protocol: Reading Order Engine and Graph Builder."""

    def order_layout(self, layout: LayoutCIR) -> OrderedLayoutCIR:
        """Determine human reading order and construct ReadingOrderGraph for LayoutCIR."""
        ...

    def order_page(
        self,
        page_layout: PageLayoutCIR,
        prev_page_exit_id: str | None = None,
    ) -> OrderedPageCIR:
        """Determine reading order for a single PageLayoutCIR."""
        ...

    def order_stream(self, layout: LayoutCIR) -> Iterator[OrderedPageCIR]:
        """Stream ordered page CIR objects sequentially."""
        ...


@runtime_checkable
class OrderedLayoutEngineProtocol(Protocol):
    """Universal Protocol interface for the Ordered Layout Engine."""

    def process(self, layout: LayoutCIR) -> OrderedLayoutCIR:
        """Process LayoutCIR and produce OrderedLayoutCIR."""
        ...
