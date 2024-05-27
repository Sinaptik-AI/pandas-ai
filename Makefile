.PHONY: all format format_diff spell_check spell_fix tests integration docs help

all: help  ## default target executed when no arguments are given to make

#############################
# UNIT AND INTEGRATION TESTS
#############################

UNIT_TESTS_DIR ?= tests/unit_tests/
INTEGRATION_TESTS_DIR ?= tests/integration_tests/

tests:  ## run unit tests
	poetry run pytest $(UNIT_TESTS_DIR)

integration:  ## run integration tests
	poetry run pytest $(INTEGRATION_TESTS_DIR)

coverage:  ## run unit tests and generate coverage report
	poetry run coverage run --source=pandasai -m pytest $(UNIT_TESTS_DIR)
	poetry run coverage xml

###########################
# SPELLCHECK AND FORMATTING
###########################

IGNORE_FORMATS ?= "*.csv,*.txt,*.lock,*.log"

format:  ## run code formatters
	poetry run ruff format pandasai examples tests
	poetry run ruff --select I --fix pandasai examples tests

format_diff:  ## run code formatters in diff mode
	poetry run ruff format pandasai examples tests --diff
	poetry run ruff --select I pandasai examples tests

spell_check:  ## run codespell on the project
	poetry run codespell --toml pyproject.toml --skip=$(IGNORE_FORMATS) -L $(cat ignore_words.txt)"

spell_fix:  ## run codespell on the project and fix the errors
	poetry run codespell --toml pyproject.toml --skip=$(IGNORE_FORMATS) -L $(cat ignore_words.txt)" -w

######################
# DOCS
######################

docs:  ## run docs serving
	mkdocs serve

######################
# HELP
######################

help:  ## show this help message for each Makefile recipe
ifeq ($(OS),Windows_NT)
	@findstr /R /C:"^[a-zA-Z0-9 -]\+:.*##" $(MAKEFILE_LIST) | awk -F ':.*##' '{printf "\033[1;32m%-15s\033[0m %s\n", $$1, $$2}' | sort
else
	@awk -F ':.*##' '/^[^ ]+:[^:]+##/ {printf "\033[1;32m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
endif