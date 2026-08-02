from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.training.yolo import YoloTrainingRequest, run_training  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a declared SKU-110K YOLO candidate.")
    parser.add_argument("--dataset-yaml", required=True, type=Path)
    parser.add_argument("--weights", required=True, type=Path)
    parser.add_argument(
        "--profile", choices=("smoke", "development", "full"), default="development"
    )
    parser.add_argument("--name", required=True)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--image-size", type=int, default=640)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--optimizer", default="auto")
    args = parser.parse_args()
    request = YoloTrainingRequest(
        dataset_yaml=args.dataset_yaml.resolve(),
        initial_weights=args.weights.resolve(),
        output_root=ROOT / "reports" / "runs",
        run_name=args.name,
        profile=args.profile,
        epochs=args.epochs,
        image_size=args.image_size,
        batch_size=args.batch_size,
        device=args.device,
        optimizer=args.optimizer,
    )
    print(
        json.dumps({"request": request.public_config(), "state": "VALIDATED"}, sort_keys=True)
    )
    destination = run_training(request)
    print(json.dumps({"run_directory": str(destination), "state": "COMPLETED"}, sort_keys=True))


if __name__ == "__main__":
    main()
