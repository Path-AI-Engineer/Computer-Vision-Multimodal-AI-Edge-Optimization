FROM node:22-alpine AS web
WORKDIR /workspace/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EDGE_VISION_ROOT=/app \
    MAX_UPLOAD_BYTES=6291456 \
    PORT=8080
WORKDIR /app
RUN addgroup --system console && adduser --system --ingroup console console
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY edge_ai ./edge_ai
COPY artifacts ./artifacts
COPY configs ./configs
COPY data/manifests ./data/manifests
COPY data/calibration ./data/calibration
COPY data/samples ./data/samples
COPY reports ./reports
COPY --from=web /workspace/frontend/dist ./frontend/dist
RUN chown -R console:console /app
USER console
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8080')+'/ready',timeout=2)"
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
