# Docker runtime

The production image builds the React console, installs the pinned Python runtime, copies only
the approved inference bundle and evidence, then runs as an unprivileged user.

```powershell
docker compose config
docker compose up --build
```

Open `http://127.0.0.1:8021/app/`; readiness is exposed at `/ready`.
