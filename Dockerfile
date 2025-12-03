FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq5 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

# Copy only the service
COPY src/services/pytune_stream/pyproject.toml .
COPY src/services/pytune_stream/app ./app

# Copy all internal packages
COPY src/packages ./packages

RUN uv sync --no-dev

EXPOSE 8009

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8009"]