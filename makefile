path := .

define Comment
	- Run `make help` to see all the available options.
	- Run `make lint` to run the linter.
	- Run `make lint-check` to check linter conformity.
	- Run `run-pipeline-detach` to start pipeline in detach mode'.
	- Run `run-pipeline` to start pipeline with logs in console.
	- Run `dep-sync` to sync current environment up to date with the locked deps.
endef


.PHONY: lint
lint: black isort flake	## Apply all the linters.


.PHONY: lint-check
lint-check:  ## Check whether the codebase satisfies the linter rules.
	@echo
	@echo "Checking linter rules..."
	@echo "========================"
	@echo
	@black --check $(path)
	@isort --check $(path)
	@flake8 $(path)


.PHONY: black
black: ## Apply black.
	@echo
	@echo "Applying black..."
	@echo "================="
	@echo
	@black --fast $(path)
	@echo


.PHONY: isort
isort: ## Apply isort.
	@echo "Applying isort..."
	@echo "================="
	@echo
	@isort $(path)


.PHONY: flake
flake: ## Apply flake8.
	@echo
	@echo "Applying flake8..."
	@echo "================="
	@echo
	@flake8 $(path)


.PHONY: help
help: ## Show this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


.PHONY: test
test: ## Run the tests against the current version of Python.
	pytest

.PHONY: run-pipeline-detach
run-pipeline-detach: ## start pipeline in detach mode.
	sudo docker compose up -d

.PHONY: run-pipeline
run-pipeline: ## start pipeline with logs in console.
	sudo docker compose up --build

.PHONY: kill-container
kill-container: ## Stop the running docker container.
	sudo docker compose down


.PHONY: run-local
run-local: ## Run the app locally.
	uvicorn src.api.api:app --port 8000 --reload


.PHONY: run-frontend
run-frontend: ## Run the frontend app locally.
	python3 -m frontend_pipeline.frontend

.PHONY: build-pipeline
build-pipeline: ## Run the app in a docker container.
	sudo docker compose build

.PHONY: run-graph-container
run-graph-container: ## Run neo4j graph database.
	sudo docker run --name neo4j -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.23

.PHONY: load-file-docker
load-file-docker: ## Load this file for first time  only
	python -m src.pipeline