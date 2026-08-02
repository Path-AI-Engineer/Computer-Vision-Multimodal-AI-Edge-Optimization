# Architecture

## Runtime flow

```text
Image -> safe decode -> component/candidate detector -> confidence filter
      -> NMS -> XYXY detections -> visible count -> API response -> React canvas
```

FastAPI owns transport contracts and delegates inference to `DetectionService`. The service loads one immutable bundle during application lifespan. The predictor has no filesystem or HTTP concerns. Evaluation reads persisted predictions instead of silently rerunning a different model.

The production container compiles React in a Node stage, installs pinned Python dependencies in a slim runtime stage and serves both API and static UI from one AWS App Runner service. The immutable image is stored in a private Amazon ECR repository and the service is reconciled through versioned CloudFormation.

## Evidence boundary

The checked-in detector is a deterministic connected-component qualification artifact. It proves geometry, API, visualization, packaging and measurement pathways without pretending to be a trained retail detector. YOLO nano, YOLO small and Faster R-CNN adapters fail explicitly when their optional dependencies or local weights are absent.

## Profiles

| Profile | Purpose | Dataset | Current state |
|---|---|---|---|
| `qualification_smoke` | Contract and system qualification | Procedural dense shelf scenes | Executed |
| `development` | Candidate training and validation | SKU-110K train/validation | Not executed |
| `full` | Frozen candidate test and final latency | SKU-110K official test | Locked |

No metric may move between profiles without its profile and evaluation scope.
