from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.logging_config import configure_logging

configure_logging()
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    log.info("startup_complete")
    try:
        yield
    finally:
        # shutdown
        log.info("shutdown_complete")


# Create app first, attach lifespan
app = FastAPI(title="app-py-api", version="0.1.0", lifespan=lifespan)

# IMPORTANT: instrument & expose metrics *immediately* after app creation
Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.get("/health")
def health():
    return {"status": "ok"}
