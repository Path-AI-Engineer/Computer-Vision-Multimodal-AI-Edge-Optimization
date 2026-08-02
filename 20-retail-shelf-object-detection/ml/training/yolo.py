from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class YoloTrainingRequest:
    dataset_yaml: Path
    initial_weights: Path
    output_root: Path
    run_name: str
    profile: str = "development"
    seed: int = 200533
    epochs: int = 40
    image_size: int = 640
    batch_size: int = 8
    device: str = "cpu"
    optimizer: str = "auto"

    def validate(self) -> None:
        if self.profile not in {"smoke", "development", "full"}:
            raise ValueError("Unknown compute profile.")
        if not self.dataset_yaml.is_file():
            raise FileNotFoundError(f"Dataset YAML not found: {self.dataset_yaml}")
        if not self.initial_weights.is_file():
            raise FileNotFoundError(
                "Initial weights must be supplied locally; implicit downloads are disabled."
            )
        if self.profile == "full" and "test" in self.run_name.lower():
            raise ValueError(
                "Training run names may not target the locked official test split."
            )
        if min(self.epochs, self.image_size, self.batch_size) <= 0:
            raise ValueError("Training budget values must be positive.")

    def public_config(self) -> dict[str, object]:
        values = asdict(self)
        return {
            key: str(value) if isinstance(value, Path) else value
            for key, value in values.items()
        }


def run_training(request: YoloTrainingRequest) -> Path:
    request.validate()
    try:
        from ultralytics import YOLO
    except ImportError as error:
        raise RuntimeError(
            "Install the optional detection dependencies before executing a YOLO run."
        ) from error
    model = YOLO(str(request.initial_weights))
    result = model.train(
        data=str(request.dataset_yaml),
        project=str(request.output_root),
        name=request.run_name,
        seed=request.seed,
        deterministic=True,
        epochs=request.epochs,
        imgsz=request.image_size,
        batch=request.batch_size,
        device=request.device,
        optimizer=request.optimizer,
        exist_ok=False,
        plots=True,
        val=True,
    )
    destination = Path(result.save_dir)
    if not (destination / "weights" / "best.pt").is_file():
        raise RuntimeError("Training completed without the required best.pt artifact.")
    return destination
