from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.main import app  # noqa: E402
from document_ai.artifacts.bundle import load_bundle  # noqa: E402

REQUIRED_DOCS = (
    "docs/architecture.md",
    "docs/data-contract.md",
    "docs/ocr-contract.md",
    "docs/field-contract.md",
    "docs/api-contract.md",
    "docs/evaluation-protocol.md",
    "docs/threats-to-validity.md",
    "docs/project-status.md",
)
REQUIRED_ROUTES = {
    "/health",
    "/ready",
    "/v1/models/current",
    "/v1/documents/extract",
    "/v1/extractions/{request_id}",
    "/v1/extractions/{request_id}/export",
    "/v1/evaluation/summary",
    "/v1/evaluation/errors",
}


def main() -> None:
    bundle = load_bundle(ROOT)
    if bundle["official_benchmark"] is not False:
        raise RuntimeError("Qualification evidence must not be labeled as an official benchmark.")
    manifest = json.loads((ROOT / "data/manifests/qualification.json").read_text(encoding="utf-8"))
    if manifest["official_sroie_status"] != "LOCKED_NOT_ACQUIRED":
        raise RuntimeError("SROIE evidence boundary changed without an acquisition record.")
    for sample in manifest["samples"]:
        for key in ("image", "annotation"):
            if not (ROOT / sample[key]).is_file():
                raise RuntimeError(f"Missing sample artifact: {sample[key]}")
    missing_docs = [path for path in REQUIRED_DOCS if not (ROOT / path).is_file()]
    if missing_docs:
        raise RuntimeError(f"Missing documentation: {', '.join(missing_docs)}")
    missing_routes = REQUIRED_ROUTES - set(app.openapi()["paths"])
    if missing_routes:
        raise RuntimeError(f"Missing API routes: {sorted(missing_routes)}")
    summary = json.loads(
        (ROOT / "reports/metrics/evaluation-summary.json").read_text(encoding="utf-8")
    )
    required_groups = {"ocr", "end_to_end", "oracle_ocr"}
    if not required_groups <= summary.keys():
        raise RuntimeError("Evaluation summary is incomplete.")
    print(
        json.dumps(
            {
                "status": "passed",
                "bundle": bundle["bundle_id"],
                "samples": len(manifest["samples"]),
                "routes": len(REQUIRED_ROUTES),
                "official_benchmark": False,
            }
        )
    )


if __name__ == "__main__":
    main()
