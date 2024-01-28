# Print help message by default (`make` with no arguments)
.DEFAULT_GOAL := help

# Variables ------------------------------------------------------------------------------------------------------------
ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Colours --------------------------------------------------------------------------------------------------------------
C_RESET=\033[39m
C_BLACK=\033[30m
C_RED=\033[31m
C_GREEN=\033[32m
C_YELLOW=\033[33m
C_BLUE=\033[34m
C_MAGENTA=\033[35m
C_CYAN=\033[36m
C_WHITE=\033[37m

# Targets --------------------------------------------------------------------------------------------------------------
# Nicely formatted and coloured list of possible targets
.PHONY: help
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "${C_CYAN}%-30s${C_RESET}%s\n", $$1, $$2}'

.PHONY: test
test: ## Run unit tests
	pytest --disable-warnings -vvs $(ROOT_DIR)/kellog/tests
