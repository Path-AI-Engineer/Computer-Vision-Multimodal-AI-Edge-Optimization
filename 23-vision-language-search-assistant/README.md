# Vision-Language Retrieval Studio

Project 23 of the AI Engineer path turns multimodal similarity into an auditable search
product. It retrieves a sealed image collection from text, another image or a short sequence
of deterministic refinements. Every answer cites `image_id`, normalized ranking scores and
stored captions. Similarity is never presented as semantic truth.

## Product surface

- Text-to-image search with caption TF-IDF, semantic and hybrid modes.
- Image-to-image search from a sealed corpus image.
- Temporary JPEG, PNG or WebP upload through a documented color-composition adapter.
- Exact and approximate qualification indexes with visible score components.
- Typed, expiring `SearchState` for search, refine, exclude, explain and reset intents.
- Grounded answer rendering from retrieved IDs, scores and captions only.
- Retrieval leaderboard, index comparison and adversarial failure atlas.
- Model, embedding and index cards bound to the same immutable qualification bundle.

## Evidence boundary

The repository includes `sealed-visual-retrieval-qualification-v1`: 12 generated visual
fixtures, 24 captions and 12 fixed development queries. It validates the complete data,
ranking, API, assistant and interface contracts without downloading model weights.

It is **not**:

- the 8,092-image Flickr8k benchmark;
- an execution of OpenAI CLIP or OpenCLIP;
- a FAISS HNSW/IVF benchmark;
- evidence that cosine similarity is a factual interpretation of an image.

The official research dependencies and contracts are versioned separately in
`requirements-research.txt` and `configs/`. Test data remains locked until a reproducible
Flickr8k acquisition and checksum review is completed.

## Architecture

```text
sealed manifest
  -> caption TF-IDF + qualification dual encoder
  -> normalized embeddings
  -> exact / approximate index
  -> lexical / semantic / hybrid retrieval
  -> grounded result schema
  -> FastAPI
  -> React retrieval studio

session message
  -> guardrail policy
  -> deterministic intent parser
  -> typed SearchState transition
  -> retrieval service
  -> evidence-only renderer
```

Offline and online responsibilities are separated:

- `multimodal/`: data, encoders, embeddings, indexes, retrieval and evaluation.
- `assistant/`: guardrails, intents, state transitions, orchestration and grounding.
- `backend/`: thin API resources and runtime composition.
- `frontend/`: React/Vite product experience consuming only API contracts.
- `artifacts/`: compatible embedding, index and online bundle manifests.
- `reports/`: generated metrics, per-query records and error evidence.

## Run locally

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Computer-Vision-Multimodal-AI-Edge-Optimization\23-vision-language-search-assistant"

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3.12 -m venv .venv
}
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt

python scripts\build_qualification_bundle.py
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8023 --reload
```

In a second PowerShell terminal:

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Computer-Vision-Multimodal-AI-Edge-Optimization\23-vision-language-search-assistant\frontend"
npm install
npm run dev
```

Open:

- Studio: `http://127.0.0.1:5173/app/`
- API docs: `http://127.0.0.1:8023/docs`
- Readiness: `http://127.0.0.1:8023/ready`

## Quality gate

```powershell
.\scripts\quality_gate.ps1
```

The gate regenerates evidence, runs Ruff, pytest, the project validator, the frontend build
and Playwright desktop/mobile journeys. It also validates Docker Compose when Docker is
available. Install the Chromium runtime once with `npx playwright install chromium`.

## API

| Method | Route | Responsibility |
|---|---|---|
| GET | `/health` | Liveness without artifact claims |
| GET | `/ready` | Bundle and corpus readiness |
| GET | `/v1/models/current` | Active model/bundle contract |
| GET | `/v1/indexes/current` | Active index contract |
| GET | `/v1/corpus` | Sealed corpus metadata and evidence captions |
| POST | `/v1/search/text` | Caption, semantic or hybrid search |
| POST | `/v1/search/image` | Search from a sealed image ID |
| POST | `/v1/search/image-upload` | Bounded temporary upload search |
| POST | `/v1/sessions` | Create expiring typed state |
| POST | `/v1/sessions/{id}/messages` | Search/refine/exclude/explain/reset |
| DELETE | `/v1/sessions/{id}` | Remove session state |
| GET | `/v1/evaluation/*` | Generated evaluation evidence |

## Deployment preparation

Plan 04 targets AWS. `infra/aws/release.ps1` validates the repository, provisions an
immutable ECR repository and deploys a single container to App Runner only when `-Apply` is
explicitly supplied. No cloud deployment is executed as part of local development.

## Responsible-use boundary

- No person identification or sensitive-attribute inference.
- No arbitrary URL retrieval.
- No permanent conversation memory by default.
- Captions are treated as indexed data, never as instructions.
- Low scores produce `INSUFFICIENT_RESULTS` instead of invented answers.
- Retrieved captions are cited, not converted into guaranteed facts.

> Retrieving a similar image does not authorize inventing what the image means.
