from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED = {"train": 8219, "val": 588, "test": 2936}


def image_count(path: Path) -> int:
    return sum(
        1 for item in path.rglob("*") if item.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Verify a user-provided SKU-110K extraction without downloading "
            "or opening test labels."
        )
    )
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    counts = {split: image_count(root / "images" / split) for split in EXPECTED}
    missing = [split for split, expected in EXPECTED.items() if counts[split] != expected]
    payload = {
        "dataset": "SKU-110K",
        "root": str(root),
        "counts": counts,
        "expected": EXPECTED,
        "status": "VALID" if not missing else "INVALID",
        "test_policy": "TEST_IMAGES_PRESENT_BUT_LABELS_NOT_USED_DURING_SELECTION",
        "license_action": "User must independently review and accept upstream terms.",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if missing:
        raise SystemExit(f"Unexpected image counts for: {', '.join(missing)}")


if __name__ == "__main__":
    main()
