# Project status

Status: **IN_PROGRESS - qualification vertical complete**

## Completed

- Data, annotation, image and inference contracts.
- Deterministic dense-scene qualification dataset and manifests.
- Real connected-component detector, confidence filtering and NMS.
- Executed qualification count-by-mean baseline plus guarded YOLO training entrypoint.
- AP and count evaluation with density slices and overlays.
- Immutable artifact bundle and hash validation.
- FastAPI single/batch inference and evidence endpoints.
- Responsive React operations console.
- Unit, integration and contract gates, Docker Compose validation and an AWS ECR/App Runner release definition.

## Not completed

- SKU-110K acquisition and license acceptance.
- Count-baseline execution on SKU-110K train.
- YOLO nano/small and Faster R-CNN training.
- Candidate and threshold selection on validation.
- Official test execution.
- Hardware-backed production latency and throughput acceptance.
- Production image build and browser E2E acceptance in an unrestricted runtime.
- AWS account template validation and App Runner deployment.

The project must not be described as a completed SKU-110K benchmark until every item above is evidenced.
