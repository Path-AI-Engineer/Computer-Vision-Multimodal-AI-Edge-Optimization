# Model card — MobileNetV3-Small research target

Intended task: Oxford-IIIT Pet 37-class classification on CPU-oriented inference targets.
The versioned architecture factory uses torchvision MobileNetV3-Small with checkpoint-provided
preprocessing and a project-owned classifier head.

Current online bundle: `qualification-linear-vision-v1`. It is a deterministic contract
fixture, not MobileNetV3. It exists to validate registry, quality, latency, parity, inference
and UI paths without inventing unexecuted research results.

Prohibited claims: universal real-time performance, physical edge validation, Oxford Pets
accuracy, calibrated confidence or production readiness before the final research gate.
