FROM node:22-alpine AS web
WORKDIR /workspace/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PET_STUDIO_ROOT=/app \
    PORT=8080
WORKDIR /app
RUN addgroup --system studio && adduser --system --ingroup studio studio
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY ml ./ml
COPY models/bundles ./models/bundles
COPY data/manifests ./data/manifests
COPY data/samples ./data/samples
COPY reports/metrics ./reports/metrics
COPY reports/errors ./reports/errors
COPY reports/figures ./reports/figures
COPY --from=web /workspace/frontend/dist ./frontend/dist
RUN chown -R studio:studio /app
USER studio
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8080')+'/ready',timeout=2)"
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
