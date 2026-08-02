# Docker runtime

The production image builds the React client first and then copies only the runtime API,
domain package, approved evidence bundle and static assets into a non-root Python image.

```powershell
docker compose build
docker compose up -d
docker compose ps
Invoke-RestMethod http://127.0.0.1:8022/ready
```

The container has a read-only filesystem, no Linux capabilities and a bounded temporary
filesystem. The lightweight image contains the sealed fixture adapter; add and qualify the
optional OCR runtime in a separate image before accepting arbitrary uploads in production.
