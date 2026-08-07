"""Step Parser for Automotive Procedure Intelligence Engine (RFC-AUTO-002).

Deterministically tokenizes procedural text into atomic, hierarchical repair steps
preserving sequence, display numbers, parent-child relationships, and branching conditions.
"""

from __future__ import annotations

import re
from typing import NamedTuple

from mechai.contracts.procedures import StepNumberingStyle
from mechai.procedures.config import ProcedureEngineConfig


class ParsedStepLine(NamedTuple):
    """Raw parsed step component before contract assembly."""

    display_number: str
    action_text: str
    numbering_style: StepNumberingStyle
    indent_level: int
    is_optional: bool
    is_branching: bool
    branch_condition: str | None


class StepParser:
    """Deterministic step parser with multi-level hierarchy resolution."""

    def __init__(self, config: ProcedureEngineConfig | None = None) -> None:
        self._config = config or ProcedureEngineConfig()
        self._re_numbered = re.compile(self._config.step_numbered_regex, re.IGNORECASE)
        self._re_alpha = re.compile(self._config.step_alpha_regex)
        self._re_roman = re.compile(self._config.step_roman_regex)
        self._re_bullet = re.compile(self._config.step_bullet_regex)

    def parse_text_lines(self, text: str) -> list[ParsedStepLine]:
        """Split text into distinct procedural step lines and parse their prefixes."""
        lines = [line.rstrip() for line in text.splitlines() if line.strip()]
        if not lines:
            return []

        parsed_steps: list[ParsedStepLine] = []
        current_step: ParsedStepLine | None = None

        for line in lines:
            stripped = line.strip()
            indent_spaces = len(line) - len(line.lstrip())

            # Attempt prefix matching
            parsed_line = self._parse_single_line(stripped, indent_spaces)

            if parsed_line is not None:
                if current_step is not None:
                    parsed_steps.append(current_step)
                current_step = parsed_line
            else:
                # Continuation of previous step narrative
                if current_step is not None:
                    extended_text = f"{current_step.action_text} {stripped}"
                    current_step = ParsedStepLine(
                        display_number=current_step.display_number,
                        action_text=extended_text,
                        numbering_style=current_step.numbering_style,
                        indent_level=current_step.indent_level,
                        is_optional=current_step.is_optional,
                        is_branching=current_step.is_branching,
                        branch_condition=current_step.branch_condition,
                    )
                else:
                    # Initial unnumbered intro line
                    current_step = ParsedStepLine(
                        display_number="",
                        action_text=stripped,
                        numbering_style=StepNumberingStyle.UNNUMBERED,
                        indent_level=indent_spaces // 2,
                        is_optional=False,
                        is_branching=False,
                        branch_condition=None,
                    )

        if current_step is not None:
            parsed_steps.append(current_step)

        return parsed_steps

    def _parse_single_line(self, text: str, indent_spaces: int) -> ParsedStepLine | None:
        """Attempt to match a line against numbering patterns."""
        # 1. Numbered: 1., 2), (1)
        m_num = self._re_numbered.match(text)
        if m_num:
            num_str = m_num.group(1) or m_num.group(2)
            action = m_num.group(3).strip()
            # Verify it's not a subsection heading like "1.2 Description"
            if not re.match(r"^\d+\.\d+", text):
                display = text[: len(text) - len(action)].strip()
                is_opt, is_branch, cond = self._detect_conditions(action)
                return ParsedStepLine(
                    display_number=display,
                    action_text=action,
                    numbering_style=StepNumberingStyle.NUMBERED,
                    indent_level=0 if indent_spaces < 4 else 1,
                    is_optional=is_opt,
                    is_branching=is_branch,
                    branch_condition=cond,
                )

        # 2. Roman Numerals: (i), (ii), i., ii.
        m_rom = self._re_roman.match(text)
        if m_rom:
            rom_str = (m_rom.group(1) or m_rom.group(2)).lower()
            if rom_str in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"):
                action = m_rom.group(3).strip()
                display = text[: len(text) - len(action)].strip()
                is_opt, is_branch, cond = self._detect_conditions(action)
                return ParsedStepLine(
                    display_number=display,
                    action_text=action,
                    numbering_style=StepNumberingStyle.ROMAN,
                    indent_level=2,
                    is_optional=is_opt,
                    is_branching=is_branch,
                    branch_condition=cond,
                )

        # 3. Alphabetical: a., b., (a), (b), A., B.
        m_alpha = self._re_alpha.match(text)
        if m_alpha:
            char_str = m_alpha.group(1) or m_alpha.group(2)
            # Exclude single character words like "A" in "A vehicle..." unless formatted as "a.", "(a)"
            if text.startswith(("(", "[")) or text[1:3] in (". ", ") "):
                action = m_alpha.group(3).strip()
                display = text[: len(text) - len(action)].strip()
                is_opt, is_branch, cond = self._detect_conditions(action)
                return ParsedStepLine(
                    display_number=display,
                    action_text=action,
                    numbering_style=StepNumberingStyle.ALPHABETICAL,
                    indent_level=1,
                    is_optional=is_opt,
                    is_branching=is_branch,
                    branch_condition=cond,
                )

        # 4. Bullet lists: •, -, *
        m_bul = self._re_bullet.match(text)
        if m_bul:
            bullet_char = m_bul.group(1)
            action = m_bul.group(2).strip()
            is_opt, is_branch, cond = self._detect_conditions(action)
            return ParsedStepLine(
                display_number=bullet_char,
                action_text=action,
                numbering_style=StepNumberingStyle.BULLET,
                indent_level=1 if indent_spaces < 4 else 2,
                is_optional=is_opt,
                is_branching=is_branch,
                branch_condition=cond,
            )

        return None

    def _detect_conditions(self, text: str) -> tuple[bool, bool, str | None]:
        """Detect optional steps and conditional branching logic."""
        lower = text.lower()
        is_optional = any(
            kw in lower
            for kw in (
                "if equipped",
                "if necessary",
                "if required",
                "as required",
                "where applicable",
                "(if equipped)",
                "(if necessary)",
            )
        )

        is_branching = False
        branch_condition: str | None = None

        if "if " in lower:
            # Check for branching action phrases
            branch_match = re.search(
                r"\bif\s+(.+?)(?:,\s*|\s+)(?:go\s+to\s+step|refer\s+to|proceed\s+to|replace|repeat)\b",
                text,
                re.IGNORECASE,
            )
            if branch_match:
                is_branching = True
                branch_condition = branch_match.group(0).strip()
            elif "otherwise" in lower or "if out of specification" in lower or "if out of standard" in lower:
                is_branching = True
                branch_condition = text.split(".")[0].strip()

        return is_optional, is_branching, branch_condition
