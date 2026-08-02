from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download Oxford-IIIT Pet without opening the official test split."
    )
    parser.add_argument("--root", type=Path, default=Path("data/raw"))
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if not args.download:
        raise SystemExit("Refusing network access without explicit --download.")
    from torchvision.datasets import OxfordIIITPet

    dataset = OxfordIIITPet(
        root=args.root,
        split="trainval",
        target_types=("category", "binary-category"),
        download=True,
    )
    print(
        json.dumps(
            {
                "status": "downloaded",
                "split": "trainval",
                "examples": len(dataset),
                "test_status": "LOCKED_NOT_ACCESSED",
            }
        )
    )


if __name__ == "__main__":
    main()
