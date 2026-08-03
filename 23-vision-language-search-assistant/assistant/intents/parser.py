from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

IntentName = Literal["search", "refine", "exclude", "reset", "explain"]


@dataclass(frozen=True)
class ParsedIntent:
    name: IntentName
    value: str
    reason_code: str


def parse_intent(message: str, has_query: bool) -> ParsedIntent:
    value = message.strip()
    lowered = value.lower()
    if lowered in {"reset", "start over", "clear", "new search"}:
        return ParsedIntent("reset", "", "EXPLICIT_RESET")
    if lowered.startswith("explain"):
        return ParsedIntent("explain", value[7:].strip(), "EXPLICIT_EXPLAIN")
    exclusion = re.match(r"^(?:exclude|without|remove)\s+(.+)$", value, re.IGNORECASE)
    if exclusion:
        return ParsedIntent("exclude", exclusion.group(1).strip(), "EXPLICIT_EXCLUSION")
    refinement = re.match(r"^(?:refine|also|only|with)\s+(.+)$", value, re.IGNORECASE)
    if has_query and refinement:
        return ParsedIntent("refine", refinement.group(1).strip(), "EXPLICIT_REFINEMENT")
    return ParsedIntent("refine" if has_query else "search", value, "QUERY_TEXT")
