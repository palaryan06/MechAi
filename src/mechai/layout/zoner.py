"""Stage 2.0 Layout Intelligence Engine: Geometric Zoning & Layout Classification.

Transforms ParsedDocument into LayoutCIR according to RFC-007 specifications.
Zero automotive domain semantics, purely typographical, spatial, and geometric.
"""

from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING

from mechai.contracts.layout import (
    ColumnGutter,
    GeometricLayoutZonerProtocol,
    LayoutCIR,
    LayoutEngineProtocol,
    LayoutRegion,
    PageLayoutCIR,
    PageMargins,
    RegionType,
)
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.layout.config import LayoutZonerConfig

if TYPE_CHECKING:
    from collections.abc import Iterator

    from mechai.contracts.scrubbing import (
        ParsedDocument,
        ParsedImage,
        ParsedPage,
        ParsedWord,
    )

# Compiled regular expressions for layout classification patterns
_WARNING_START_RE = re.compile(
    r"^\s*(?:\*\*)?\s*(?:DANGER|WARNING|CAUTION|SAFETY\s+ALERT)\b",
    re.IGNORECASE,
)
_NOTE_START_RE = re.compile(
    r"^\s*(?:\*\*)?\s*(?:NOTE|NOTICE|IMPORTANT|ATTENTION|REMARK)\b[\s:\-\u2013\u2014]*",
    re.IGNORECASE,
)
_LIST_ITEM_RE = re.compile(
    r"^\s*(?:[•\-\*▪▫\u2013\u2014\u2022\u25cf\u25cb]|\(?\d{1,3}[\.\)]|\(?[a-zA-Z][\.\)]|\(?[ivxIVX]{1,5}[\.\)])\s+",
)
_CAPTION_START_RE = re.compile(
    r"^\s*(?:Fig(?:ure)?\.?|Table|Illustration|Chart|Diagram|Photo|Scheme)\s+[0-9A-Za-z\.\-_]+",
    re.IGNORECASE,
)
_HEADER_FOOTER_NUMBER_RE = re.compile(
    r"^\s*(?:Page\s+\d+(?:\s+of\s+\d+)?|\d+\s*[-/]\s*\d+|[0-9]{1,2}[A-Z]{1,2}[0-9]?\s*[-/]\s*\d+|\d+)\s*$",
    re.IGNORECASE,
)


class _TextLine:
    """Internal helper representing a horizontally aligned group of words within a column."""

    __slots__ = ("bbox", "font_names", "font_sizes", "is_bold", "is_italic", "text", "words")

    def __init__(self, words: list[ParsedWord]) -> None:
        self.words = sorted(words, key=lambda w: w.left)
        self.text = " ".join(w.text for w in self.words)
        left = min(w.left for w in self.words)
        top = min(w.top for w in self.words)
        right = max(w.right for w in self.words)
        bottom = max(w.bottom for w in self.words)
        self.bbox = BoundingBox(left=left, top=top, right=right, bottom=bottom)
        self.font_sizes = [w.font_size for w in self.words if w.font_size is not None]
        self.font_names = [w.font_name for w in self.words if w.font_name is not None]
        self.is_bold = any(w.bold for w in self.words)
        self.is_italic = any(w.italic for w in self.words)

    @property
    def median_font_size(self) -> float:
        if not self.font_sizes:
            return 10.0
        sorted_sizes = sorted(self.font_sizes)
        mid = len(sorted_sizes) // 2
        return sorted_sizes[mid]


class _BlockCluster:
    """Internal helper representing a spatial cluster of text lines or an image entity."""

    __slots__ = ("bbox", "column_index", "image", "is_spanning", "is_table", "lines")

    def __init__(
        self,
        lines: list[_TextLine],
        image: ParsedImage | None = None,
        column_index: int | None = None,
        is_spanning: bool = False,
        is_table: bool = False,
    ) -> None:
        self.lines = lines
        self.image = image
        self.column_index = column_index
        self.is_spanning = is_spanning
        self.is_table = is_table

        if image is not None and image.bbox is not None:
            self.bbox = image.bbox
        elif lines:
            left = min(line.bbox.left for line in lines)
            top = min(line.bbox.top for line in lines)
            right = max(line.bbox.right for line in lines)
            bottom = max(line.bbox.bottom for line in lines)
            self.bbox = BoundingBox(left=left, top=top, right=right, bottom=bottom)
        elif image is not None and image.width and image.height:
            self.bbox = BoundingBox(
                left=50.0,
                top=50.0,
                right=50.0 + float(image.width),
                bottom=50.0 + float(image.height),
            )
        else:
            self.bbox = BoundingBox(left=0.0, top=0.0, right=0.0, bottom=0.0)

    @property
    def text(self) -> str:
        return "\n".join(line.text for line in self.lines)


class GeometricLayoutZoner(GeometricLayoutZonerProtocol, LayoutEngineProtocol):
    """Stage 2.0 Layout Intelligence Engine.

    Performs geometric page margin decomposition, cross-page header/footer isolation,
    vertical projection profile multi-column slicing, spatial region clustering,
    and typographic layout classification.
    """

    def __init__(self, config: LayoutZonerConfig | None = None) -> None:
        self.config = config or LayoutZonerConfig()

    def process(self, document: ParsedDocument) -> LayoutCIR:
        """Process a parsed document and produce a complete LayoutCIR."""
        return self.segment_layout(document)

    def process_stream(self, document: ParsedDocument) -> Iterator[PageLayoutCIR]:
        """Stream page layouts sequentially to conserve memory."""
        return self.segment_stream(document)

    def segment_layout(self, document: ParsedDocument) -> LayoutCIR:
        """Execute Stage 2.0 layout segmentation across all pages of a ParsedDocument."""
        pages: list[PageLayoutCIR] = []
        all_regions: list[LayoutRegion] = []

        total_pages = document.total_pages or len(document.pages) or 1
        for page_idx, parsed_page in enumerate(document.pages, start=1):
            page_layout = self.segment_page(
                parsed_page,
                page_index=page_idx,
                total_pages=total_pages,
            )
            pages.append(page_layout)
            all_regions.extend(page_layout.regions)

        doc_id = (
            f"layout_doc_{abs(hash(document.source_path)) % 1000000:06d}"
            if document.source_path
            else "layout_doc_000001"
        )

        return LayoutCIR(
            document_id=doc_id,
            source_path=str(document.source_path) if document.source_path else None,
            total_pages=total_pages,
            pages=tuple(pages),
            regions=tuple(all_regions),
            provenance=SourceRef(
                page_number=1,
                extraction_method=ExtractionMethod.RULE,
                confidence=1.0,
            ),
        )

    def segment_stream(self, document: ParsedDocument) -> Iterator[PageLayoutCIR]:
        """Stream PageLayoutCIR objects page-by-page."""
        total_pages = document.total_pages or len(document.pages) or 1
        for page_idx, parsed_page in enumerate(document.pages, start=1):
            yield self.segment_page(
                parsed_page,
                page_index=page_idx,
                total_pages=total_pages,
            )

    def segment_page(
        self,
        page: ParsedPage,
        page_index: int = 1,
        total_pages: int = 1,
    ) -> PageLayoutCIR:
        """Segment a single ParsedPage into PageLayoutCIR."""
        width = page.width if page.width and page.width > 0.0 else 612.0
        height = page.height if page.height and page.height > 0.0 else 792.0

        # 1. Compute page margins
        margins = self._calculate_margins(page, width, height)

        # 2. Identify candidate header & footer zones
        header_y_cutoff = max(
            margins.top + 8.0,
            height * self.config.header_max_y_ratio,
        )
        footer_y_cutoff = min(
            height - margins.bottom - 8.0,
            height * self.config.footer_min_y_ratio,
        )

        header_zone_bbox = BoundingBox(
            left=margins.left,
            top=0.0,
            right=width - margins.right,
            bottom=header_y_cutoff,
        )
        footer_zone_bbox = BoundingBox(
            left=margins.left,
            top=footer_y_cutoff,
            right=width - margins.right,
            bottom=height,
        )

        # 3. Categorize tokens into header, footer, margin, and body
        header_words: list[ParsedWord] = []
        footer_words: list[ParsedWord] = []
        margin_words: list[ParsedWord] = []
        body_words: list[ParsedWord] = []

        for word in page.words:
            if word.bottom <= header_y_cutoff:
                header_words.append(word)
            elif word.top >= footer_y_cutoff:
                footer_words.append(word)
            elif (
                word.right < margins.left
                or word.left > (width - margins.right)
                or word.bottom < margins.top
                or word.top > (height - margins.bottom)
            ):
                margin_words.append(word)
            else:
                body_words.append(word)

        # 4. Multi-column detection via vertical projection profile on body words
        column_gutters = self._detect_column_gutters(
            body_words,
            margins,
            width,
            header_y_cutoff,
            footer_y_cutoff,
        )

        # 5. Form columns partition
        column_bounds = self._build_column_bounds(
            margins,
            width,
            column_gutters,
        )

        # 6. Estimate baseline body font size
        body_font_size = self._estimate_body_font_size(body_words)

        # 7. Cluster body words into column lines and blocks
        body_blocks = self._cluster_body_words_into_blocks(
            body_words,
            column_bounds,
            column_gutters,
            width,
            margins,
            body_font_size,
        )

        # 8. Create image blocks
        image_blocks = self._create_image_blocks(page.images, column_bounds)

        # 9. Classify all regions and assign unique IDs & provenance
        classified_regions: list[LayoutRegion] = []
        region_counter = 1

        # Process Header regions
        if header_words:
            header_lines = self._cluster_words_into_lines(header_words)
            for h_line in header_lines:
                reg_id = f"reg_p{page.page_number}_{region_counter:03d}"
                region_counter += 1
                conf = 0.96 if _HEADER_FOOTER_NUMBER_RE.match(h_line.text) else 0.92
                classified_regions.append(
                    LayoutRegion(
                        id=reg_id,
                        bbox=h_line.bbox,
                        page_number=page.page_number,
                        region_type=RegionType.HEADER,
                        confidence=conf,
                        provenance=SourceRef(
                            page_number=page.page_number,
                            bbox=h_line.bbox,
                            extraction_method=ExtractionMethod.RULE,
                            confidence=conf,
                        ),
                        text=h_line.text,
                        reading_zone_id="zone_header",
                        column_index=None,
                    )
                )

        # Process Margin regions
        if margin_words:
            margin_lines = self._cluster_words_into_lines(margin_words)
            for m_line in margin_lines:
                reg_id = f"reg_p{page.page_number}_{region_counter:03d}"
                region_counter += 1
                classified_regions.append(
                    LayoutRegion(
                        id=reg_id,
                        bbox=m_line.bbox,
                        page_number=page.page_number,
                        region_type=RegionType.MARGIN,
                        confidence=0.88,
                        provenance=SourceRef(
                            page_number=page.page_number,
                            bbox=m_line.bbox,
                            extraction_method=ExtractionMethod.RULE,
                            confidence=0.88,
                        ),
                        text=m_line.text,
                        reading_zone_id="zone_margin",
                        column_index=None,
                    )
                )

        # Combine body text blocks and image blocks
        all_body_blocks = body_blocks + image_blocks
        # Sort spatially primarily top-down
        all_body_blocks.sort(key=lambda b: (round(b.bbox.top / 15.0), b.bbox.left))

        for block in all_body_blocks:
            reg_type, conf = self._classify_block(
                block,
                body_font_size,
                width,
                margins,
                len(column_bounds),
                all_body_blocks,
            )
            reg_id = f"reg_p{page.page_number}_{region_counter:03d}"
            region_counter += 1
            reading_zone_id = (
                f"zone_col_{block.column_index}"
                if block.column_index is not None
                else "zone_body_span"
            )

            classified_regions.append(
                LayoutRegion(
                    id=reg_id,
                    bbox=block.bbox,
                    page_number=page.page_number,
                    region_type=reg_type,
                    confidence=conf,
                    provenance=SourceRef(
                        page_number=page.page_number,
                        bbox=block.bbox,
                        extraction_method=ExtractionMethod.RULE,
                        confidence=conf,
                    ),
                    text=block.text,
                    reading_zone_id=reading_zone_id,
                    column_index=block.column_index,
                )
            )

        # Process Footer regions
        if footer_words:
            footer_lines = self._cluster_words_into_lines(footer_words)
            for f_line in footer_lines:
                reg_id = f"reg_p{page.page_number}_{region_counter:03d}"
                region_counter += 1
                conf = 0.98 if _HEADER_FOOTER_NUMBER_RE.match(f_line.text) else 0.92
                classified_regions.append(
                    LayoutRegion(
                        id=reg_id,
                        bbox=f_line.bbox,
                        page_number=page.page_number,
                        region_type=RegionType.FOOTER,
                        confidence=conf,
                        provenance=SourceRef(
                            page_number=page.page_number,
                            bbox=f_line.bbox,
                            extraction_method=ExtractionMethod.RULE,
                            confidence=conf,
                        ),
                        text=f_line.text,
                        reading_zone_id="zone_footer",
                        column_index=None,
                    )
                )

        return PageLayoutCIR(
            page_number=page.page_number,
            width=width,
            height=height,
            margins=margins,
            header_zone=header_zone_bbox if header_words else None,
            footer_zone=footer_zone_bbox if footer_words else None,
            columns=tuple(column_gutters),
            regions=tuple(classified_regions),
        )

    # -------------------------------------------------------------------------
    # Geometric Zoning & Margin Algorithms
    # -------------------------------------------------------------------------

    def _calculate_margins(self, page: ParsedPage, width: float, height: float) -> PageMargins:
        """Calculate dynamic page margins from word and image bounding envelopes."""
        min_margin = self.config.min_margin_pt
        default_margin = self.config.default_margin_pt

        all_boxes: list[BoundingBox] = [
            BoundingBox(left=w.left, top=w.top, right=w.right, bottom=w.bottom) for w in page.words
        ]
        for img in page.images:
            if img.bbox is not None:
                all_boxes.append(img.bbox)

        if not all_boxes:
            return PageMargins(
                left=default_margin,
                top=default_margin,
                right=default_margin,
                bottom=default_margin,
            )

        min_left = min(b.left for b in all_boxes)
        min_top = min(b.top for b in all_boxes)
        max_right = max(b.right for b in all_boxes)
        max_bottom = max(b.bottom for b in all_boxes)

        left_margin = max(min_margin, min(min_left, 72.0))
        top_margin = max(min_margin, min(min_top, 72.0))
        right_margin = max(min_margin, min(width - max_right, 72.0))
        bottom_margin = max(min_margin, min(height - max_bottom, 72.0))

        return PageMargins(
            left=round(left_margin, 2),
            top=round(top_margin, 2),
            right=round(right_margin, 2),
            bottom=round(bottom_margin, 2),
        )

    def _detect_column_gutters(
        self,
        words: list[ParsedWord],
        margins: PageMargins,
        width: float,
        top_y: float,
        bottom_y: float,
    ) -> list[ColumnGutter]:
        """Detect vertical whitespace gutters via vertical projection profiling."""
        if not words:
            return []

        body_left = margins.left
        body_right = width - margins.right
        body_width = body_right - body_left
        if body_width < 100.0:
            return []

        bin_size = self.config.histogram_bin_size_pt
        num_bins = math.ceil(width / bin_size)
        histogram = [0] * num_bins

        # Populate vertical projection histogram
        for w in words:
            if w.bottom <= top_y or w.top >= bottom_y:
                continue
            # If word is wide spanning line (> 75% body), skip to prevent blocking gutter
            if (w.right - w.left) > (0.75 * body_width):
                continue

            start_bin = max(0, int(w.left / bin_size))
            end_bin = min(num_bins - 1, int(w.right / bin_size))
            for b_idx in range(start_bin, end_bin + 1):
                histogram[b_idx] += 1

        # Scan for valleys in the body area
        gutters: list[ColumnGutter] = []
        min_gutter_bins = int(self.config.min_gutter_width_pt / bin_size)

        in_valley = False
        valley_start_bin = 0

        # Restrict gutter search inside body margin bounds
        start_search_bin = int((body_left + 20.0) / bin_size)
        end_search_bin = int((body_right - 20.0) / bin_size)

        for b_idx in range(start_search_bin, end_search_bin):
            count = histogram[b_idx]
            if count == 0:
                if not in_valley:
                    in_valley = True
                    valley_start_bin = b_idx
            else:
                if in_valley:
                    in_valley = False
                    valley_len = b_idx - valley_start_bin
                    if valley_len >= min_gutter_bins:
                        g_left = valley_start_bin * bin_size
                        g_right = b_idx * bin_size
                        gutters.append(
                            ColumnGutter(
                                left=round(g_left, 2),
                                right=round(g_right, 2),
                                top=round(top_y, 2),
                                bottom=round(bottom_y, 2),
                            )
                        )

        # Merge adjacent gutters that are within 10pt of each other
        merged_gutters: list[ColumnGutter] = []
        for g in gutters:
            if merged_gutters and (g.left - merged_gutters[-1].right) <= 10.0:
                prev = merged_gutters.pop()
                merged_gutters.append(
                    ColumnGutter(
                        left=prev.left,
                        right=g.right,
                        top=top_y,
                        bottom=bottom_y,
                    )
                )
            else:
                merged_gutters.append(g)

        return merged_gutters

    def _build_column_bounds(
        self,
        margins: PageMargins,
        width: float,
        gutters: list[ColumnGutter],
    ) -> list[tuple[float, float]]:
        """Construct horizontal (left, right) coordinate boundaries for each column."""
        body_left = margins.left
        body_right = width - margins.right

        if not gutters:
            return [(body_left, body_right)]

        bounds: list[tuple[float, float]] = []
        curr_left = body_left

        for g in gutters:
            bounds.append((curr_left, g.left))
            curr_left = g.right

        bounds.append((curr_left, body_right))
        return bounds

    # -------------------------------------------------------------------------
    # Spatial Line & Block Clustering
    # -------------------------------------------------------------------------

    def _cluster_words_into_lines(self, words: list[ParsedWord]) -> list[_TextLine]:
        """Group words within a column into horizontal typographical text lines."""
        if not words:
            return []

        # Sort by vertical top coordinate
        sorted_words = sorted(words, key=lambda w: (w.top, w.left))
        lines: list[list[ParsedWord]] = []

        tolerance = self.config.line_vertical_tolerance_pt

        for w in sorted_words:
            w_h = max(1.0, w.bottom - w.top)
            w_center_y = (w.top + w.bottom) / 2.0
            assigned = False
            for line in lines:
                l_top = min(lw.top for lw in line)
                l_bot = max(lw.bottom for lw in line)
                l_h = max(1.0, l_bot - l_top)

                # Vertical overlap check
                overlap = max(0.0, min(w.bottom, l_bot) - max(w.top, l_top))
                min_h = min(w_h, l_h)

                line_center_y = (l_top + l_bot) / 2.0
                if (overlap / min_h >= 0.35) or (abs(w_center_y - line_center_y) <= tolerance):
                    line.append(w)
                    assigned = True
                    break
            if not assigned:
                lines.append([w])

        # Convert each group to a _TextLine
        text_lines = [_TextLine(group) for group in lines]
        text_lines.sort(key=lambda line: (line.bbox.top, line.bbox.left))
        return text_lines

    def _cluster_body_words_into_blocks(
        self,
        words: list[ParsedWord],
        column_bounds: list[tuple[float, float]],
        column_gutters: list[ColumnGutter],
        page_width: float,
        margins: PageMargins,
        body_font_size: float,
    ) -> list[_BlockCluster]:
        """Group body words into lines and group adjacent lines into coherent blocks."""
        if not words:
            return []

        body_width = (page_width - margins.right) - margins.left

        # When multi-column, separate spanning words from column words first
        spanning_words: list[ParsedWord] = []
        column_word_groups: list[list[ParsedWord]] = [[] for _ in column_bounds]

        for w in words:
            w_width = w.right - w.left
            is_spanning = False

            if len(column_bounds) > 1:
                # Spans across body width or crosses a gutter
                if w_width >= (self.config.spanning_block_width_ratio * body_width):
                    is_spanning = True
                else:
                    for g in column_gutters:
                        if w.left < g.left and w.right > g.right:
                            is_spanning = True
                            break

            if is_spanning:
                spanning_words.append(w)
                continue

            # Assign to best column
            w_cx = (w.left + w.right) / 2.0
            best_col = 0
            min_dist = float("inf")
            for col_idx, (c_left, c_right) in enumerate(column_bounds):
                if c_left <= w_cx <= c_right:
                    best_col = col_idx
                    min_dist = 0.0
                    break
                col_cx = (c_left + c_right) / 2.0
                dist = abs(w_cx - col_cx)
                if dist < min_dist:
                    min_dist = dist
                    best_col = col_idx

            column_word_groups[best_col].append(w)

        column_blocks_by_col: list[list[_BlockCluster]] = []

        # Form blocks within each column
        for col_idx, col_words in enumerate(column_word_groups):
            if not col_words:
                column_blocks_by_col.append([])
                continue
            col_lines = self._cluster_words_into_lines(col_words)
            col_blocks = self._merge_lines_into_blocks(
                col_lines,
                body_font_size,
                column_index=col_idx if len(column_bounds) > 1 else None,
                is_spanning=False,
            )
            column_blocks_by_col.append(col_blocks)

        # Check for multi-column unbordered TableRegion row alignments
        merged_column_blocks = self._merge_tabular_multi_columns(
            column_blocks_by_col,
            column_bounds,
        )

        blocks: list[_BlockCluster] = list(merged_column_blocks)

        # Form blocks from spanning words
        if spanning_words:
            span_lines = self._cluster_words_into_lines(spanning_words)
            span_blocks = self._merge_lines_into_blocks(
                span_lines,
                body_font_size,
                column_index=None,
                is_spanning=True,
            )
            blocks.extend(span_blocks)

        return blocks

    def _merge_tabular_multi_columns(
        self,
        column_blocks_by_col: list[list[_BlockCluster]],
        column_bounds: list[tuple[float, float]],
    ) -> list[_BlockCluster]:
        """Detect and merge row-aligned multi-column tabular structures into TableRegions."""
        if len(column_bounds) <= 1:
            return [b for col in column_blocks_by_col for b in col]

        # Flatten blocks
        all_blocks = [b for col in column_blocks_by_col for b in col]
        if not all_blocks:
            return []

        # Group blocks across columns that share substantial vertical overlap
        used_indices: set[int] = set()
        merged_blocks: list[_BlockCluster] = []

        for i, b1 in enumerate(all_blocks):
            if i in used_indices:
                continue

            matching_group = [b1]
            matching_indices = [i]

            for j, b2 in enumerate(all_blocks):
                if j <= i or j in used_indices or b1.column_index == b2.column_index:
                    continue

                # Check vertical overlap
                overlap = max(
                    0.0,
                    min(b1.bbox.bottom, b2.bbox.bottom) - max(b1.bbox.top, b2.bbox.top),
                )
                min_h = min(b1.bbox.height, b2.bbox.height)
                if min_h > 0.0 and (overlap / min_h) >= 0.70:
                    # Tabular column check (multiple aligned rows, concise text)
                    b1_words = len(b1.text.split())
                    b2_words = len(b2.text.split())
                    b1_lines = len(b1.lines)
                    b2_lines = len(b2.lines)

                    if (
                        b1_lines >= 2
                        and b2_lines >= 2
                        and (b1_words / b1_lines) <= 6
                        and (b2_words / b2_lines) <= 6
                    ):
                        matching_group.append(b2)
                        matching_indices.append(j)

            if len(matching_group) >= 2:
                # Merge into a single TableRegion spanning across these columns
                for idx in matching_indices:
                    used_indices.add(idx)

                all_lines: list[_TextLine] = []
                for b in matching_group:
                    all_lines.extend(b.lines)

                merged_blocks.append(
                    _BlockCluster(
                        lines=all_lines,
                        column_index=None,
                        is_spanning=True,
                        is_table=True,
                    )
                )
            else:
                merged_blocks.append(b1)
                used_indices.add(i)

        return merged_blocks

    def _merge_lines_into_blocks(
        self,
        lines: list[_TextLine],
        body_font_size: float,
        column_index: int | None,
        is_spanning: bool,
    ) -> list[_BlockCluster]:
        """Merge consecutive lines into block clusters based on vertical spacing and typography."""
        if not lines:
            return []

        lines.sort(key=lambda line: line.bbox.top)
        clusters: list[list[_TextLine]] = []
        curr_cluster: list[_TextLine] = [lines[0]]

        max_gap = max(body_font_size * self.config.block_line_gap_ratio, 14.0)

        for line in lines[1:]:
            prev_line = curr_cluster[-1]
            gap = line.bbox.top - prev_line.bbox.bottom

            # Break into new block if:
            # 1. Spacing gap is too large
            # 2. Transition between bold heading and normal prose
            # 3. New line is a bullet/list item
            # 4. New line starts with a Warning/Note keyword
            # 5. Substantial font size change (> 1.5pt)
            font_diff = abs(line.median_font_size - prev_line.median_font_size)
            is_warning = bool(_WARNING_START_RE.search(line.text))
            is_note = bool(_NOTE_START_RE.search(line.text))
            is_list = bool(_LIST_ITEM_RE.match(line.text))
            is_prev_list = bool(_LIST_ITEM_RE.match(prev_line.text))

            # Heading followed by prose or prose followed by heading
            bold_transition = (prev_line.is_bold and not line.is_bold) or (
                line.is_bold and not prev_line.is_bold
            )

            should_split = (
                gap > max_gap
                or font_diff > 1.5
                or (bold_transition and gap >= 2.0)
                or is_warning
                or is_note
                or (is_list and not is_prev_list)
            )

            if should_split:
                clusters.append(curr_cluster)
                curr_cluster = [line]
            else:
                curr_cluster.append(line)

        if curr_cluster:
            clusters.append(curr_cluster)

        return [
            _BlockCluster(
                group,
                column_index=column_index,
                is_spanning=is_spanning,
            )
            for group in clusters
        ]

    def _create_image_blocks(
        self,
        images: tuple[ParsedImage, ...],
        column_bounds: list[tuple[float, float]],
    ) -> list[_BlockCluster]:
        """Convert ParsedImage entities into block clusters for layout zoning."""
        image_blocks: list[_BlockCluster] = []
        for img in images:
            col_idx: int | None = None
            if img.bbox is not None and len(column_bounds) > 1:
                cx = img.bbox.center_x
                for idx, (c_left, c_right) in enumerate(column_bounds):
                    if c_left <= cx <= c_right:
                        col_idx = idx
                        break
            image_blocks.append(_BlockCluster(lines=[], image=img, column_index=col_idx))
        return image_blocks

    def _estimate_body_font_size(self, words: list[ParsedWord]) -> float:
        """Estimate the baseline body text font size across words."""
        font_sizes = [w.font_size for w in words if w.font_size is not None and w.font_size > 0.0]
        if not font_sizes:
            return self.config.default_body_font_size

        # Use median of font sizes
        sorted_sizes = sorted(font_sizes)
        return float(sorted_sizes[len(sorted_sizes) // 2])

    # -------------------------------------------------------------------------
    # Region Classification & Epistemic Confidence Calibration
    # -------------------------------------------------------------------------

    def _classify_block(
        self,
        block: _BlockCluster,
        body_font_size: float,
        page_width: float,
        margins: PageMargins,
        num_columns: int,
        all_blocks: list[_BlockCluster],
    ) -> tuple[RegionType, float]:
        """Classify a spatial block cluster into one of the 16 supported RegionTypes."""
        # 1. FigureRegion (Image entity)
        if block.image is not None:
            return RegionType.FIGURE_REGION, 0.95

        # 2. TableRegion (Pre-identified tabular multi-column merge)
        if block.is_table:
            return RegionType.TABLE_REGION, 0.90

        text = block.text.strip()
        if not text:
            return RegionType.UNKNOWN, 0.50

        # Calculate block typography
        font_sizes = [s for line in block.lines for s in line.font_sizes]
        median_font = sorted(font_sizes)[len(font_sizes) // 2] if font_sizes else body_font_size
        is_bold = any(line.is_bold for line in block.lines)
        num_lines = len(block.lines)
        first_line_text = block.lines[0].text if block.lines else text

        # 3. WarningBox
        if _WARNING_START_RE.search(first_line_text) or _WARNING_START_RE.search(text):
            return RegionType.WARNING_BOX, 0.95

        # 4. NoteBox
        if _NOTE_START_RE.search(first_line_text) or _NOTE_START_RE.search(text):
            return RegionType.NOTE_BOX, 0.94

        # 5. Caption (Proximity to Figure or Table, or starting with Fig/Table)
        if _CAPTION_START_RE.search(first_line_text) and num_lines <= 3:
            return RegionType.CAPTION, 0.92

        # 6. TableRegion (Delimiters, grid pipes, or multi-column numeric tabular structure)
        if self._is_table_region(block):
            return RegionType.TABLE_REGION, 0.88

        # 7. List
        if _LIST_ITEM_RE.match(first_line_text) or (
            num_lines >= 2 and all(_LIST_ITEM_RE.match(line.text) for line in block.lines)
        ):
            return RegionType.LIST, 0.93

        # 8. Title (Prominent large font >= title_scale * body_font_size or >= 16pt, top of section)
        if (
            median_font >= (body_font_size * self.config.title_font_scale)
            or (median_font >= 16.0 and is_bold)
        ) and num_lines <= 3:
            return RegionType.TITLE, 0.94

        # 9. Heading (Intermediate bold font >= heading_scale * body_font_size)
        if (
            median_font >= (body_font_size * self.config.heading_font_scale)
            or (median_font >= 12.0 and is_bold)
            or (first_line_text.isupper() and is_bold and num_lines <= 2)
            or (is_bold and num_lines == 1 and len(first_line_text) < 60)
        ) and num_lines <= 3:
            return RegionType.HEADING, 0.91

        # 10. Subheading (Slightly larger or bold heading before prose)
        if (
            (is_bold or median_font >= (body_font_size * self.config.subheading_font_scale))
            and num_lines <= 2
            and len(first_line_text) < 80
            and not first_line_text.endswith((".", ":", ";"))
        ):
            return RegionType.SUBHEADING, 0.87

        # 11. Sidebar (Narrow column at side with non-standard width)
        body_width = (page_width - margins.right) - margins.left
        if (
            num_columns > 1
            and block.bbox.width <= (self.config.sidebar_max_width_ratio * body_width)
            and block.column_index is not None
            and (
                block.bbox.left <= (margins.left + 80.0)
                or block.bbox.right >= (page_width - margins.right - 80.0)
            )
        ):
            if num_lines <= 4:
                return RegionType.SIDEBAR, 0.85

        # 12. Paragraph (Standard multi-word text)
        word_count = len(text.split())
        if word_count >= 3:
            return RegionType.PARAGRAPH, 0.89

        # 13. Body (General short body text)
        if word_count >= 1:
            return RegionType.BODY, 0.82

        return RegionType.UNKNOWN, 0.50

    def _is_table_region(self, block: _BlockCluster) -> bool:
        """Detect tabular structures with delimiters or aligned columns."""
        text = block.text

        # Delimiter pipe characters or dashes
        if "|" in text or "+---" in text or "+===" in text:
            return True

        if len(block.lines) < 2:
            return False

        # Check for multiple lines with repeated wide whitespace intervals or tabular columns
        tabular_line_count = 0
        for line in block.lines:
            # More than 3 words spaced out or containing tabular column spacing
            if len(line.words) >= 3:
                # Check if words have large inter-word gaps (> 15pt)
                large_gaps = 0
                for i in range(len(line.words) - 1):
                    gap = line.words[i + 1].left - line.words[i].right
                    if gap >= 12.0:
                        large_gaps += 1
                if large_gaps >= 2:
                    tabular_line_count += 1

        return tabular_line_count >= 2
