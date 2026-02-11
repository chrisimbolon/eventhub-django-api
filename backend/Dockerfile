# ----------- Builder stage -----------
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements ./requirements
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements/production.txt

# ----------- Final stage -----------
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq5 netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY requirements ./requirements
RUN pip install --no-cache-dir /wheels/*

COPY . /app

# ✅ FIXED: Create both staticfiles AND media directories
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
     "--threads", "2"]