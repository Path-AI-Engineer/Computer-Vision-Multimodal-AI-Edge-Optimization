from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from ml.data.ksdd2 import validate_ksdd2


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a user-supplied KSDD2 dataset root.")
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    report = validate_ksdd2(args.root)
    print(json.dumps(asdict(report), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
