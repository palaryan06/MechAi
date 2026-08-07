"""Requirement Extractor for Automotive Procedure Intelligence Engine (RFC-AUTO-002).

Deterministically extracts required Special Service Tools (SST), standard workshop tools,
measuring instruments, and consumable materials/sealants from procedural step text.
"""

from __future__ import annotations

import re

from mechai.contracts.procedures import RequiredMaterial, RequiredTool
from mechai.procedures.config import ProcedureEngineConfig


class RequirementExtractor:
    """Deterministic extractor for tools, SSTs, and required materials."""

    def __init__(self, config: ProcedureEngineConfig | None = None) -> None:
        self._config = config or ProcedureEngineConfig()
        self._compiled_sst = [re.compile(pat, re.IGNORECASE) for pat in self._config.sst_regexes]

    def extract_tools(self, text: str) -> list[RequiredTool]:
        """Extract tools and SSTs from step text."""
        tools: list[RequiredTool] = []
        seen_keys: set[str] = set()

        # 1. Extract Special Service Tools (SSTs)
        for regex in self._compiled_sst:
            for match in regex.finditer(text):
                raw_tool_num = match.group(1).strip()
                # Normalize SST number
                clean_tool_num = re.sub(r"^(?:SST|Special\s+Service\s+Tool)\s*(?:No\.?)?\s*[:\s]*", "", raw_tool_num, flags=re.IGNORECASE).strip()
                if not clean_tool_num:
                    continue

                # Check for accompanying tool description in parentheses e.g. "09916-14510 (Valve spring compressor)"
                desc_match = re.search(
                    re.escape(match.group(0)) + r"\s*[\(:]([^\)\n\.,;]+)[\)]?",
                    text,
                    re.IGNORECASE,
                )
                tool_name = desc_match.group(1).strip() if desc_match else f"SST {clean_tool_num}"
                key = f"sst:{clean_tool_num}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    seen_keys.add(tool_name.lower())
                    tools.append(
                        RequiredTool(
                            name=tool_name,
                            tool_number=clean_tool_num,
                            is_sst=True,
                            confidence=0.98,
                        )
                    )

        # 2. Extract Standard Hand Tools & Measuring Instruments
        lower_text = text.lower()
        for kw in self._config.tool_keywords:
            if kw in lower_text and kw not in seen_keys:
                seen_keys.add(kw)
                # Proper title case for canonical name
                canonical_name = kw.title()
                tools.append(
                    RequiredTool(
                        name=canonical_name,
                        tool_number=None,
                        is_sst=False,
                        confidence=0.95,
                    )
                )

        return tools

    def extract_materials(self, text: str) -> list[RequiredMaterial]:
        """Extract required sealants, fluids, gaskets, and single-use replacement parts."""
        materials: list[RequiredMaterial] = []
        seen_keys: set[str] = set()
        lower_text = text.lower()

        # 1. Check for specific chemicals/sealants/lubricants
        for mat_kw in self._config.material_keywords:
            if mat_kw in lower_text and mat_kw not in seen_keys:
                seen_keys.add(mat_kw)
                # Check for brand/spec in surrounding tokens e.g. "Suzuki Bond No. 1215"
                spec_match = re.search(
                    r"\b" + re.escape(mat_kw) + r"(?:\s+(?:No\.?\s*)?([A-Z0-9\-]+))?",
                    text,
                    re.IGNORECASE,
                )
                spec = spec_match.group(1).strip() if spec_match and spec_match.group(1) else None
                materials.append(
                    RequiredMaterial(
                        name=mat_kw.title(),
                        specification=spec,
                        is_replacement_mandatory=False,
                        confidence=0.95,
                    )
                )

        # 2. Dynamic regex extraction for mandatory single-use replacement parts
        replacement_patterns = (
            r"(?:always\s+)?replace\s+(?:with\s+)?(?:a\s+)?new\s+([a-z0-9\s\-]+?)(?:\.|\s+upon|\s+before|\s+during|\s+after|$|\band\b)",
            r"(?:always\s+)?replace\s+([a-z0-9\s\-]+?)\s+with\s+new(?:\.|\s+upon|\s+before|\s+during|\s+after|$|\band\b)",
            r"(?:install|use)\s+(?:a\s+)?new\s+([a-z0-9\s\-]+?)(?:\.|\s+upon|\s+before|\s+during|\s+after|$|\band\b)",
            r"do\s+not\s+reuse\s+(?:the\s+|old\s+)?([a-z0-9\s\-]+?)(?:\.|\s+upon|\s+before|\s+during|\s+after|$|\band\b)",
        )
        for pat in replacement_patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                item = m.group(1).strip()
                # Clean up item text
                item_clean = re.sub(r"^(?:the|a|an|old|damaged)\s+", "", item, flags=re.IGNORECASE).strip()
                if item_clean and len(item_clean) > 2 and item_clean.lower() not in seen_keys:
                    seen_keys.add(item_clean.lower())
                    materials.append(
                        RequiredMaterial(
                            name=item_clean.title(),
                            specification=None,
                            is_replacement_mandatory=True,
                            confidence=0.98,
                        )
                    )

        # 3. Check for static mandatory single-use replacement indicators
        for repl_kw in self._config.mandatory_replacement_keywords:
            if repl_kw in lower_text and repl_kw not in seen_keys:
                seen_keys.add(repl_kw)
                # Extract item name e.g. "new cotter pin" -> "Cotter Pin"
                item_name = repl_kw.replace("new ", "").replace("always replace ", "").replace("use a new ", "").strip()
                if item_name:
                    materials.append(
                        RequiredMaterial(
                            name=item_name.title(),
                            specification=None,
                            is_replacement_mandatory=True,
                            confidence=0.98,
                        )
                    )

        return materials
