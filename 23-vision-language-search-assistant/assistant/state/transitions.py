from __future__ import annotations

from assistant.intents.parser import ParsedIntent
from multimodal.core.contracts import SearchState


def apply_intent(state: SearchState, intent: ParsedIntent) -> SearchState:
    if intent.name == "reset":
        state.positive_query = ""
        state.negative_terms.clear()
        state.filters.clear()
        state.previous_result_ids.clear()
        state.selected_image_id = None
    elif intent.name == "search":
        state.positive_query = intent.value
        state.negative_terms.clear()
        state.previous_result_ids.clear()
    elif intent.name == "refine":
        state.positive_query = " ".join(
            value for value in (state.positive_query, intent.value) if value
        )
    elif intent.name == "exclude":
        if intent.value.lower() not in state.negative_terms:
            state.negative_terms.append(intent.value.lower())
    return state
