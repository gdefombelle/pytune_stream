import asyncio

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import toml
from pathlib import Path
import os
from fastapi.middleware.cors import CORSMiddleware

from simple_logger.logger import get_logger, SimpleLogger
from pytune_configuration.sync_config_singleton import config, SimpleConfig
from app.sse_router import router as sse_router

# 📜 Initialisation
if config is None: config = SimpleConfig()

# 📦 Lecture de pyproject.toml
pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
pyproject_data = toml.load(pyproject_path)

project_metadata = pyproject_data["tool"]["poetry"]
PROJECT_TITLE = project_metadata.get("name", "pytune_stream")
PROJECT_VERSION = project_metadata.get("version", "0.1.0")
PROJECT_DESCRIPTION = project_metadata.get("description", "PyTune SSE Stream")

# 📄 Logger
print("ENV LOG_DIR:", os.getenv("LOG_DIR"))
logger = get_logger("pytune_stream")
logger.info("✅ Logger actif", log_dir=os.getenv("LOG_DIR"))
logger.info("********** STARTING PYTUNE SSE - STREAM ********")

app = FastAPI(
    title=PROJECT_TITLE,
    version=PROJECT_VERSION,
    description=PROJECT_DESCRIPTION,
    # lifespan=lifespan,
)

# 🔗 Middleware CORS
allowed_origins = config.ALLOWED_CORS_ORIGINS
logger.info(f"Allowed CORS origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Authorization"],
)

# 🔗 Inclure les routers
app.include_router(sse_router)

# 📄 Gestion des erreurs FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
import json
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        raw_body = await request.body()
        try:
            decoded_body = raw_body.decode("utf-8")
        except Exception:
            decoded_body = repr(raw_body)  # ✅ safe

        # ✅ DEBUG : log en console pour dev
        print("❌ Validation error:", exc.errors())
        print("📦 Raw body:", decoded_body)

        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "body": decoded_body
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "Exception handler failed", "error": str(e)}
        )

# 📂 Fichiers statiques (optionnel si besoin)
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ❤️ Healthcheck route
@app.get("/")
async def health_check():
    return {"status": "ok", "service": PROJECT_TITLE, "version": PROJECT_VERSION}
