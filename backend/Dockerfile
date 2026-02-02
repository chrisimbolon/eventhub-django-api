# ----------- Builder stage -----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies (need libpq-dev here for compiling)
RUN apt-get update && apt-get install -y \
    gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements ./requirements
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements/production.txt

# ----------- Final stage -----------
FROM python:3.12-slim

WORKDIR /app

# Only runtime dependencies needed here
RUN apt-get update && apt-get install -y \
    libpq5 netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /wheels /wheels
COPY requirements ./requirements
RUN pip install --no-cache-dir /wheels/*

# Copy project
COPY . /app

# Create non-root user and set ownership
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Workers and threads configurable via env vars
# Defaults: 3 workers, 2 threads
CMD ["gunicorn", "eventmaster.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--threads", "2"]