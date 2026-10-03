# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build deps needed by psycopg2-binary, faiss-cpu, cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Copy installed packages from build stage
COPY --from=builder /install /usr/local

# The worker uses absolute imports: `from ai.agent...`, `from ai.utils...`
# So the WORKDIR must be the project root (one level above the ai/ package).
WORKDIR /app

# Copy the entire ai package (this file lives inside ai/, so context is ai/)
# We copy it into /app/ai/ so that `from ai.xxx import` resolves correctly.
COPY . /app/ai/

# Non-root user for security
RUN useradd -m -u 1000 worker
USER worker

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# worker.py lives at /app/ai/worker.py → run as module ai.worker
CMD ["python", "-m", "ai.worker"]
