# Release checklist

- [x] Qualification artifacts are reproducible.
- [x] Every result exposes image ID and evidence captions.
- [x] Model and index manifests are compatible.
- [x] Guardrails reject URLs, identity and sensitive inference.
- [x] Metrics are generated rather than hardcoded in the frontend.
- [x] API, frontend, Docker and AWS preparation are versioned.
- [x] Python suite, TypeScript, Vite build, Compose config and AWS local preflight pass.
- [ ] Playwright desktop/mobile suite executed outside the managed `spawn EPERM` boundary.
- [ ] Production Docker image built with Docker Desktop running.
- [ ] Official Flickr8k benchmark acquired and approved.
- [ ] CLIP/OpenCLIP and FAISS research dependencies executed.
- [ ] AWS deployment explicitly authorized and smoke-tested.
