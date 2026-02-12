# ----------- Builder stage -----------
FROM python:3.12-slim AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements ./requirements

# Upgrade pip + install setuptools first (needed by some packages at build time)
# Then build wheels — note: --no-deps skips transitive deps so setuptools
# must be handled separately
RUN pip install --upgrade pip setuptools && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements/production.txt

# ----------- Final stage -----------
FROM python:3.12-slim
WORKDIR /app

# Only runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Copy and install wheels
COPY --from=builder /wheels /wheels
COPY requirements ./requirements

# Install setuptools explicitly FIRST (not in wheels due to --no-deps),
# then install all project wheels
RUN pip install --no-cache-dir setuptools>=69.0.0 && \
    pip install --no-cache-dir /wheels/*

# Copy project source
COPY . /app

# Create non-root user with correct ownership
RUN useradd -m appuser && \
    mkdir -p /app/staticfiles && \
    mkdir -p /app/media && \
    mkdir -p /app/static && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["gunicorn", "eventmaster.wsgi:application", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "3", \
    "--threads", "2", \
    "--timeout", "60", \
    "--log-level", "info"]