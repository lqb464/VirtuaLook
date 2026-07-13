.PHONY: install notebooks test lint format

PYTHON := python
NB_DIR := notebooks

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -e ".[dev,notebooks]"

notebooks:  ## Launch Jupyter Lab
	jupyter lab $(NB_DIR)/

test:  ## Run tests
	pytest tests/ -v

mlflow-ui:  ## Start MLflow UI
	mlflow ui --backend-store-uri sqlite:///mlruns.db --port 5000

lint:
	flake8 src/ backend/ --max-line-length=120

format:
	black src/ backend/
