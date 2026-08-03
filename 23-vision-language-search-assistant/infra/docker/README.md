# Docker runtime

The production image compiles the React application and serves it from the same non-root
FastAPI container. The runtime contains the sealed qualification corpus and immutable
manifests but excludes research dependencies, raw datasets and permanent session storage.

```powershell
docker compose build
docker compose up
```

Open `http://127.0.0.1:8023/app/` and verify `/ready` semantically reports the active bundle.

