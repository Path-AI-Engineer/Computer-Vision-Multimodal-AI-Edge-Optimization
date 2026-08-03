from __future__ import annotations

import re


class GuardrailViolation(ValueError):
    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


SENSITIVE_PATTERNS = (
    r"identify (?:this|the) person",
    r"who is (?:this|the) person",
    r"race|ethnicity|religion|sexual orientation",
    r"medical condition|political affiliation",
)


def validate_message(message: str) -> str:
    value = " ".join(message.split()).strip()
    if not value:
        raise GuardrailViolation("EMPTY_MESSAGE", "A search or refinement is required.")
    if len(value) > 320:
        raise GuardrailViolation("MESSAGE_TOO_LONG", "Messages are limited to 320 characters.")
    if re.search(r"https?://|www\.", value, re.IGNORECASE):
        raise GuardrailViolation("ARBITRARY_URL_BLOCKED", "URL retrieval is not supported.")
    if any(re.search(pattern, value, re.IGNORECASE) for pattern in SENSITIVE_PATTERNS):
        raise GuardrailViolation(
            "SENSITIVE_INFERENCE_BLOCKED",
            "Identity and sensitive-attribute inference are outside this product boundary.",
        )
    return value


def sanitize_caption(caption: str) -> str:
    """Treat stored captions as data and remove instruction-like prefixes."""
    return re.sub(
        r"^(system|assistant|instruction|ignore previous instructions)\s*:\s*",
        "",
        caption.strip(),
        flags=re.IGNORECASE,
    )
