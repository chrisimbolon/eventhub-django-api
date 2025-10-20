# ============================================
# Stage 1 — Builder
# ============================================
FROM python:3.12-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements/production.txt ./requirements.txt
RUN pip install --upgrade pip && pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt


# ============================================
# Stage 2 — Runner
# ============================================
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY backend/requirements/production.txt ./requirements.txt
RUN pip install --no-cache-dir /wheels/*

COPY backend /app

EXPOSE 8000

CMD ["gunicorn", "eventmaster.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3"]
