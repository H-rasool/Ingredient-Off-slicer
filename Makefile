PY=python

.PHONY: setup run dev test seed

setup:
	$(PY) -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run:
	uvicorn app.main:app --host 0.0.0.0 --port $${PORT:-8001}

dev:
	uvicorn app.main:app --reload --port $${PORT:-8001}

test:
	pytest -q

seed:
	$(PY) scripts/seed_off.py
