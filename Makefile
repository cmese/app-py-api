PY=python3
PIP=$(PY) -m pip

venv:
	$(PY) -m venv .venv

install:
	$(PIP) install -r requirements-dev.txt

lint:
	ruff check .
	black --check .

fmt:
	black .
	ruff check --fix .

test:
	pytest -q

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -t app-py-api:dev .

docker-run:
	docker run --rm -p 8000:8000 app-py-api:dev

