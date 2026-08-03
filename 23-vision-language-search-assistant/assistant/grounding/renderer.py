from __future__ import annotations

from assistant.guardrails.policy import sanitize_caption
from multimodal.core.contracts import SearchResponse


def render_grounded_answer(response: SearchResponse) -> str:
    if response.status == "INSUFFICIENT_RESULTS" or not response.results:
        return (
            "I do not have sufficient indexed evidence for that request. "
            "Try broader observable terms or reset the active filters."
        )
    lines = [
        f"I found {len(response.results)} ranked images. The strongest indexed match is "
        f"{response.results[0].image_id} with score {response.results[0].score:.3f}."
    ]
    for result in response.results[:3]:
        caption = sanitize_caption(result.evidence_captions[0].text)
        lines.append(f"[{result.image_id}] {caption} (score {result.score:.3f}).")
    lines.append(
        "These statements repeat retrieved captions and ranking signals; they are not "
        "independent facts about the images."
    )
    return " ".join(lines)
