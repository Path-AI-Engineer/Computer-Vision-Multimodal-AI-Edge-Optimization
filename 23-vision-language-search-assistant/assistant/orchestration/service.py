from __future__ import annotations

from assistant.grounding.renderer import render_grounded_answer
from assistant.guardrails.policy import validate_message
from assistant.intents.parser import parse_intent
from assistant.state.transitions import apply_intent
from multimodal.core.contracts import SearchState
from multimodal.retrieval.service import RetrievalService


class AssistantOrchestrator:
    def __init__(self, retrieval: RetrievalService) -> None:
        self.retrieval = retrieval

    def handle(self, state: SearchState, message: str) -> dict:
        validated = validate_message(message)
        intent = parse_intent(validated, bool(state.positive_query))
        state = apply_intent(state, intent)
        if intent.name == "reset":
            return {
                "intent": intent.name,
                "reason_code": intent.reason_code,
                "state": state.to_dict(),
                "answer": "The search state was cleared. Start with a new observable query.",
                "search": None,
            }
        if intent.name == "explain":
            cited = ", ".join(state.previous_result_ids[:6]) or "no prior results"
            return {
                "intent": intent.name,
                "reason_code": intent.reason_code,
                "state": state.to_dict(),
                "answer": f"The previous ranking cited: {cited}. Scores are ranking signals only.",
                "search": None,
            }
        response = self.retrieval.search_text(
            state.positive_query,
            mode=state.mode,
            index_mode=state.index_mode,
            top_k=state.top_k,
            negative_terms=tuple(state.negative_terms),
            filters=state.filters,
        )
        state.previous_result_ids = list(response.citations)
        return {
            "intent": intent.name,
            "reason_code": intent.reason_code,
            "state": state.to_dict(),
            "answer": render_grounded_answer(response),
            "search": response.to_dict(),
        }
