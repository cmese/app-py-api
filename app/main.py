import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.logging_config import configure_logging

# 1. configure structured logging up front
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


# 2. create the app first (with lifespan hook you already had)
app = FastAPI(title="app-py-api", version="0.1.0", lifespan=lifespan)


# 3. add middleware for request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        duration_ms = (time.time() - start) * 1000.0
        # log the exception with context
        log.error(
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            duration_ms=round(duration_ms, 2),
            client_ip=(request.client.host if request.client else None),
            error=str(e),
            exc_info=True,  # <-- structlog can be configured to include stacktrace
        )
        # still return 500 response
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )

    duration_ms = (time.time() - start) * 1000.0

    # normal request log
    log.info(
        "request_handled",
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
        client_ip=(request.client.host if request.client else None),
    )

    return response


# 4. metrics instrumentation MUST happen after app is created, before serving
Instrumentator().instrument(app).expose(app, include_in_schema=False)


# 5. routes
@app.get("/health")
def health():
    # this is now structured in stdout:
    log.info("health_check_called")
    return {"status": "ok"}


# @app.get("/boom")
# def boom():
#     # force an error to test logging path
#     1 / 0
#     return {"status": "this will never execute"}
