# ==============================
# backend/Dockerfile
# ==============================

# ----------- Builder stage -----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements ./requirements
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements/production.txt

# ----------- Final stage -----------
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies + netcat for healthchecks
RUN apt-get update && apt-get install -y \
    libpq-dev netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /wheels /wheels
COPY requirements ./requirements
RUN pip install --no-cache-dir /wheels/*

# Copy project
COPY . /app

# Expose port
EXPOSE 8000

# Default command (override in docker-compose)
CMD ["gunicorn", "eventmaster.wsgi:application", "--bind", "0.0.0.0:8000"]