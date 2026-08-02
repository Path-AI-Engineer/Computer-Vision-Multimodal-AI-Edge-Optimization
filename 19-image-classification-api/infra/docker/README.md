# Docker runtime

The production image is defined in `docker/production.Dockerfile`. It builds the React
application, installs only the HOG inference runtime, copies the versioned qualification
bundle and runs as a non-root user. Use `docker compose up --build` from the project root.
