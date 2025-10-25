# app-py-api

A small, production-style FastAPI service built for learning cloud/platform/devops fundamentals.

This repo focuses on:

- **Health & readiness**: `/health` endpoint for liveness/readiness probes.
- **Observability / metrics**: `/metrics` endpoint (Prometheus format) for scraping request counts, latency, etc.
- **Structured logging**: JSON logs using `structlog`, so logs can be shipped into central logging/monitoring platforms (Azure Log Analytics / Application Insights).
- **Quality gates**: linting (`ruff`, `black`) and tests (`pytest`) enforced locally with `pre-commit`.
- **Containerization**: Dockerfile included so the exact same artifact can run locally, in CI, or in Azure.

This is intentionally minimal, but it's shaped the way production apps are shaped:
small, observable, automatable.

---

## Tech Stack

**Runtime**

- FastAPI – async Python API framework
- uvicorn – ASGI server

**Observability**

- `/health` route for readiness/liveness checks
- `/metrics` using `prometheus-fastapi-instrumentator`
- Structured JSON logging via `structlog` (machine-parseable logs)

**Quality / Dev Experience**

- `pytest` for tests
- `ruff` and `black` for lint/format
- `pre-commit` to enforce tests + lint before every commit

**Container**

- Dockerfile (Python 3.11 slim base)
- App runs on port `8000` by default

This layout is meant to plug directly into:

- Azure Container Registry (ACR) for image storage
- Azure Container Apps (or AKS) for runtime
- Application Insights / Log Analytics for monitoring and alerting
- Azure DevOps Pipelines for CI/CD

---

## Project Structure

```text
app-py-api/
  app/
    main.py             # FastAPI app, /health and /metrics are defined here
    logging_config.py   # structlog setup for JSON logs
    __init__.py
  tests/
    test_health.py      # basic pytest to verify /health works
  requirements.txt
  requirements-dev.txt
  Dockerfile
  Makefile
  pyproject.toml        # config for ruff/black
  .pre-commit-config.yaml
  README.md
```

---

## Key Endpoints

- `GET /health`  
  Basic readiness/liveness check. Used by containers / orchestrators to know if the service is healthy.

- `GET /metrics`  
  Exposes Prometheus-compatible metrics like request count, latency buckets, etc.  
  This data feeds into dashboards / alerts (for example: “alert if P95 > 500ms for 5 minutes”).

---

## Local Development

### 1. Create a virtual environment and install deps

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 2. Run tests and lint

```bash
pytest -q
ruff .
black --check .
```

Or using the provided `Makefile`:

```bash
make fmt     # auto-format and fix lint
make test    # run pytest
make run     # run the API locally
```

### 3. Run the API locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Now hit:

- http://localhost:8000/health
- http://localhost:8000/metrics

---

## Running in Docker

This simulates the artifact we'd ship to a registry (like Azure Container Registry) and deploy to Azure Container Apps.

### Build the image:

```bash
docker build -t app-py-api:dev .
```

### Run the container:

```bash
docker run --rm -p 8000:8000 app-py-api:dev
```

Then hit:

- http://localhost:8000/health
- http://localhost:8000/metrics

Now you're not running Python directly — you're running the container image that would go to production.

---

## Pre-commit Hooks (Quality Gates)

This repo uses `pre-commit` to enforce quality automatically.

After installing dev requirements:

```bash
pre-commit install
```

Now every time you `git commit`, it will automatically:

- run `black` (format)
- run `ruff` (lint)
- run `pytest` (tests)

That simulates CI locally: you can't even commit code that fails basic health checks.

---

## Azure / Platform Context

This service is designed to run inside Azure as part of a “baseline platform.”

Infra for that lives in a separate (private) Terraform repo that:

- Creates a Resource Group
- Creates an Azure Container Registry (ACR) for images
- Creates a Key Vault for secrets
- Creates a Log Analytics Workspace and an Application Insights instance for centralized logs/metrics/tracing
- Applies tags and naming conventions (`env`, `cost_center`, etc.) for cost/accountability

The idea is:

1. This repo (`app-py-api`) builds a containerized service with health checks, metrics, and structured logs.
2. Terraform provisions the Azure landing zone and observability stack.
3. A CI/CD pipeline (Azure DevOps) will:
   - build and test the image,
   - push to ACR,
   - run `terraform plan` / `terraform apply` to deploy updated versions.

---

## Why this repo exists

This repo is part of a hands-on learning / interview prep project for a cloud/platform/DevOps role.

Goals:

- Show an API that is observable (health, metrics, JSON logs)
- Show basic CI/CD hygiene (lint, tests, pre-commit)
- Show production packaging (Docker image)
- Be ready to plug into an Azure infrastructure stack managed by Terraform

Instead of just “hello world,” this code is shaped like something you would actually ship, monitor, alert on, and roll back.
