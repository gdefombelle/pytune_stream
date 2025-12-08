# ===============================
# Étape 1 : Build avec UV (builder)
# ===============================
FROM --platform=linux/amd64 python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

# 👉 Copier la racine du workspace PyTune
COPY pyproject.toml uv.lock ./

# 👉 Copier tous les packages + services
COPY src ./src

# 👉 Se placer dans ce service
WORKDIR /app/src/services/pytune_stream

# 👉 Installer deps dans /app/.venv
RUN uv sync --no-dev


# ===============================
# Étape 2 : Image finale
# ===============================
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 👉 On se place dans CE service (où l'app FastAPI vit)
WORKDIR /app/src/services/pytune_stream

# 👉 On copie tout le workspace + la venv du builder
COPY --from=builder /app /app

EXPOSE 8009

# 👉 Lancer uvicorn depuis la venv globale du workspace
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8009"]