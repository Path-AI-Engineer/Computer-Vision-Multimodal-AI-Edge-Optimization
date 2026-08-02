# Data contract

## Official protocol

The target dataset is Oxford-IIIT Pet: 37 pet categories with official `trainval` and `test`
splits. When the official dataset is acquired, train and validation must be derived only from
`trainval` using a versioned stratified manifest and fixed seed. The official `test` split must
remain closed until model and calibrator selection.

Source: <https://www.robots.ox.ac.uk/~vgg/data/pets/>

Torchvision contract: <https://docs.pytorch.org/vision/main/generated/torchvision.datasets.OxfordIIITPet.html>

## Active qualification dataset

The checked-in qualification fixture contains 222 deterministic procedural images: six per
official breed label. It exists to validate the entire software path cheaply and reproducibly.
It is not sampled from Oxford-IIIT Pet and must not be used to claim real pet-recognition
performance.

## Image input

- accepted encoded formats: JPEG, PNG and WebP;
- maximum payload: 4 MiB by default;
- maximum decoded area: 20 million pixels;
- EXIF orientation normalized before conversion;
- all inference input converted to RGB;
- preprocessing signature: `rgb-hog-160-v1`;
- file names and image content are not written to application logs.

## Manifests

- `data/manifests/dataset_manifest.json` describes source, scope, hashes and test state.
- `data/manifests/split_manifest.csv` assigns stable sample IDs and proves disjoint splits.
- `reports/runs/p19-qualification-v1/run_config.yaml` freezes the executed run configuration.
