install:
	pip install -r requirements.txt

lint:
	ruff check src/ tests/

test:
	pytest tests/ -v

collect:
	python src/collector/collector.py

api:
	uvicorn src.api.main:app --reload --port 8000
