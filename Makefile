.PHONY: all format format_diff spell_check spell_fix tests integration docs

# Default target executed when no arguments are given to make.
all: help


#############################
# UNIT AND INTEGRATION TESTS
#############################

UNIT_TESTS_DIR ?= tests/unit_tests/
INTEGRATION_TESTS_DIR ?= tests/integration_tests/

tests:
	poetry run pytest $(UNIT_TESTS_DIR)

integration:
	poetry run pytest $(INTEGRATION_TESTS_DIR)

coverage:
	poetry run coverage run --source=pandasai -m pytest $(UNIT_TESTS_DIR)
	poetry run coverage xml

###########################
# SPELLCHECK AND FORMATTING
###########################

IGNORE_FORMATS ?= "*.csv,*.txt,*.lock,*.log"

format:
	poetry run ruff format pandasai examples tests
	poetry run ruff --select I --fix pandasai examples tests

format_diff:
	poetry run ruff format pandasai examples tests --diff
	poetry run ruff --select I pandasai examples tests

spell_check:
	poetry run codespell --toml pyproject.toml --skip=$(IGNORE_FORMATS)

spell_fix:
	poetry run codespell --toml pyproject.toml --skip=$(IGNORE_FORMATS) -w

######################
# DOCS
######################

docs:
	mkdocs serve

######################
# HELP
######################

help:
	@echo '----'
	@echo 'format                       - run code formatters'
	@echo 'spell_check               	- run codespell on the project'
	@echo 'spell_fix               		- run codespell on the project and fix the errors'
	@echo 'tests                        - run unit tests'
	@echo 'integration                  - run integration tests'
	@echo 'coverage                     - run unit tests and generate coverage report'
	@echo 'docs                         - run docs serving'