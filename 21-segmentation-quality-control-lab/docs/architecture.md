# Architecture

The lab is one deployable service with explicit internal boundaries:

```text
React console -> FastAPI resources -> hash-verified QualityBundle
                                  -> Small U-Net probability map
                                  -> threshold and piece policy
                                  -> versioned evaluation reports
```

`ml/data` owns image/mask contracts and dataset verification. `ml/training` owns candidate
training. `ml/evaluation` owns metrics, threshold selection and inspection policy.
`ml/inference` is the only runtime path that loads an approved bundle. The backend never
trains and the frontend never computes model results locally.

The production image serves the built React console and API together, avoiding a runtime API
URL mismatch. Only evidence and approved runtime artifacts enter the runtime image.
