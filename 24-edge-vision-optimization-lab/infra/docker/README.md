# Docker runtime

The production image builds the React console, installs only runtime Python dependencies and
runs FastAPI as an unprivileged user. Compose drops Linux capabilities and mounts a small
temporary filesystem while keeping the application filesystem read-only.

Run `docker compose up --build` and open `http://127.0.0.1:8024/app/`.
