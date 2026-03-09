# ── Stage 1: Build Tailwind CSS ───────────────────────────────────────────────
FROM node:20-alpine AS node-builder
WORKDIR /app
COPY package.json ./
RUN npm install
# Copy everything needed by the Tailwind content scanner
COPY static/    ./static/
COPY templates/ ./templates/
COPY events/templates/  ./events/templates/
COPY users/templates/   ./users/templates/
RUN npm run build

# ── Stage 2: Python deps (needs build tools to compile psycopg2) ───────────────
FROM python:3.12-slim AS python-deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# ── Stage 3: Lean production image ────────────────────────────────────────────
FROM python:3.12-slim AS final

# Only the runtime shared library is needed (not the -dev headers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN useradd --no-create-home --uid 1001 appuser

WORKDIR /app

# Copy installed packages from the deps stage (no build tools in final image)
COPY --from=python-deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy compiled CSS from the node stage
COPY --from=node-builder /app/static/css/output.css ./static/css/output.css

# Copy application source
COPY . .

# collectstatic at build time; SECRET_KEY dummy is fine here — not used cryptographically
RUN SECRET_KEY=build-dummy python manage.py collectstatic --noinput

# Hand ownership to the non-root user
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# 3 workers = 2 × nCPU + 1 (single-core DO droplet)
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "ada_events.wsgi:application"]
