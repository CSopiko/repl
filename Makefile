.PHONY: help
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install:
	pip install -r requirements.txt

fmt format:
	isort app tests
	black app tests

lint:
	isort --check app tests
	black --check app tests
	flake8 app tests
	mypy app tests
