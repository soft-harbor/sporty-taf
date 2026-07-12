VENV = .venv
ALLURE_RESULTS = allure-results
BROWSER_CONTEXT ?= chrome_headless
TOOLS_DIR = .tools
ALLURE_VERSION = 2.32.0
ALLURE_HOME = $(TOOLS_DIR)/allure-$(ALLURE_VERSION)
ALLURE_BIN = $(ALLURE_HOME)/bin/allure

export PATH := $(HOME)/.local/bin:$(PATH)

UV = uv
PYTEST = $(UV) run pytest

.PHONY: help install-uv install-allure bootstrap sync install-hooks test test-api test-ui quality fix lint format format-check type-check clean \
	allure-api allure-ui allure-report

## help: Show available commands
help:
	@echo "Available commands:"
	@sed -n 's/^##//p' ${MAKEFILE_LIST}

## install-uv: Install uv package manager if missing
install-uv:
	@command -v uv >/dev/null 2>&1 || { \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	}
	@command -v uv >/dev/null 2>&1 || { echo "uv not found; restart shell or add ~/.local/bin to PATH"; exit 1; }

## install-allure: Install Allure CLI if missing (Homebrew on macOS, otherwise download to .tools/)
install-allure:
	@command -v allure >/dev/null 2>&1 && { echo "Allure CLI: $$(command -v allure)"; exit 0; }; \
	if command -v brew >/dev/null 2>&1; then \
		echo "Installing Allure via Homebrew..."; \
		brew install allure; \
	else \
		echo "Downloading Allure $(ALLURE_VERSION) to $(ALLURE_HOME)..."; \
		mkdir -p $(TOOLS_DIR); \
		curl -LsSf "https://github.com/allure-framework/allure2/releases/download/$(ALLURE_VERSION)/allure-$(ALLURE_VERSION).tgz" \
			| tar -xz -C $(TOOLS_DIR); \
		test -x "$(ALLURE_BIN)"; \
	fi

## bootstrap: Install uv and Allure CLI (local tooling)
bootstrap: install-uv install-allure

## sync: Install project dependencies and pre-commit git hook (requires uv in PATH; run make bootstrap once)
sync:
	@command -v uv >/dev/null 2>&1 || { \
		echo "uv not found. Run: make bootstrap"; \
		exit 1; \
	}
	@test -x "$(VENV)/bin/python" || uv venv $(VENV) --python 3.12
	uv sync --no-install-project
	$(MAKE) install-hooks

## install-hooks: Install pre-commit git hook (run automatically by make sync)
install-hooks:
	uv run pre-commit install

## test: Run all tests and open Allure report (report opens even if tests fail)
test:
	@failed=0; \
	$(MAKE) allure-api || failed=1; \
	$(MAKE) allure-ui || failed=1; \
	$(MAKE) allure-report || exit 1; \
	exit $$failed

## test-api: Run API tests
test-api: sync
	$(PYTEST) -m api

## test-ui: Run UI tests (Selenium)
test-ui: sync
	$(PYTEST) -m ui --browser-context $(BROWSER_CONTEXT)

## allure-api: Run API tests and write Allure results to allure-results/api
allure-api: sync
	rm -rf $(ALLURE_RESULTS)/api && mkdir -p $(ALLURE_RESULTS)/api
	$(PYTEST) -m api --alluredir=$(ALLURE_RESULTS)/api

## allure-ui: Run UI tests and write Allure results to allure-results/ui
allure-ui: sync
	rm -rf $(ALLURE_RESULTS)/ui && mkdir -p $(ALLURE_RESULTS)/ui
	$(PYTEST) -m ui --browser-context $(BROWSER_CONTEXT) --alluredir=$(ALLURE_RESULTS)/ui

## allure-report: Merge api/ui shards and open Allure report
allure-report: install-allure
	@merged="$(ALLURE_RESULTS)/_merged"; \
	rm -rf "$$merged" && mkdir -p "$$merged"; \
	for shard in api ui; do \
		if [ -d "$(ALLURE_RESULTS)/$$shard" ]; then \
			cp "$(ALLURE_RESULTS)/$$shard"/* "$$merged/" 2>/dev/null || true; \
		fi; \
	done; \
	if [ -z "$$(ls -A "$$merged" 2>/dev/null)" ]; then \
		echo "No Allure result files in $(ALLURE_RESULTS)/{api,ui}."; \
		echo "Run: make allure-api and/or make allure-ui"; \
		exit 1; \
	fi; \
	allure_cmd=$$(command -v allure || echo "$(CURDIR)/$(ALLURE_BIN)"); \
	test -x "$$allure_cmd" || { echo "Allure CLI not found; run: make install-allure"; exit 1; }; \
	"$$allure_cmd" serve "$$merged"

## fix: Auto-fix lint and formatting (ruff check --fix + ruff format)
fix: sync
	$(UV) run ruff check --fix .
	$(UV) run ruff format .

## lint: Run Ruff linter
lint: sync
	$(UV) run ruff check .

## format: Format code with Ruff
format: sync
	$(UV) run ruff format .

## format-check: Check formatting without writing
format-check: sync
	$(UV) run ruff format --check .

## type-check: Run Pyright
type-check: sync
	$(UV) run pyright

## quality: Run lint, format-check, and type-check
quality: lint format-check type-check

## clean: Remove virtual environment and caches
clean:
	rm -rf $(VENV) $(ALLURE_RESULTS) allure-report allure-history test-results $(TOOLS_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	@echo "Environment and caches cleaned."
