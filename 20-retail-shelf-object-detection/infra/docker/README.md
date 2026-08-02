# Docker

`docker/production.Dockerfile` is the single production image contract. It compiles React, installs the pinned Python runtime, copies only runtime artifacts, runs as an unprivileged user and serves UI plus API on `$PORT`.

```powershell
docker compose config
docker compose up --build
```

Accept the runtime only after `http://127.0.0.1:8020/ready` returns `ready` and a real multipart request succeeds.
