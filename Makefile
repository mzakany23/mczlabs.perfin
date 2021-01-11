VENV := .venv
VENV_ACTIVATE := $(VENV)/bin/activate
VENV_SENTINEL := $(VENV)/.sentinel
VENV_PIP := $(VENV)/bin/pip $(PIP_EXTRA_OPTS)
VENV_AWS := $(VENV)/bin/aws
VENV_PRECOMMIT := $(VENV)/bin/pre-commit
VENV_PYTEST := $(VENV)/bin/pytest

GIT_COMMIT_HASH := $$(git rev-parse HEAD)

STAGE ?= dev

# Deploys generally want to have a clean git state to ensure consistency
.PHONY: ensure_git_clean
ensure_git_clean:
	@echo This target requires a clean git state, please stash or commit your changes if this fails on the next line
	test -z "$$(git status --porcelain)"


.PHONY: ensure_no_venv
ensure_no_venv:
ifdef VIRTUAL_ENV
	$(error Please deactivate your current virtual env)
endif


.PHONY: $(VENV)
$(VENV):
	$(MAKE) $(VENV_SENTINEL)


$(VENV_SENTINEL): requirements.txt requirements-test.txt .pre-commit-config.yaml
	$(MAKE) ensure_no_venv
	rm -rf $(VENV)
	python3.7 -m venv $(VENV)
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PIP) install -r requirements-test.txt
	$(VENV_PRECOMMIT) install
	touch $(VENV_SENTINEL)


.PHONY: update_requirements
update_requirements:
	$(MAKE) ensure_no_venv
	rm -rf $(VENV)
	python3.7 -m venv $(VENV)
	$(VENV_PIP) install -r requirements-loose.txt
	head -1 requirements-loose.txt > requirements.txt
	$(VENV_PIP) freeze >> requirements.txt


.PHONY: pre-commit
pre-commit: $(VENV)
	$(VENV_PRECOMMIT) run -a


.PHONY: test
.PHONY: test
test:
ifeq ($(TEST_FILE),)
	SKIP_SENTRY=1 \
	$(VENV_PYTEST) --cov=perfin --cov-report term-missing --junitxml=test-reports/pytest/junit.xml tests/
else
ifeq ($(TEST_FN),)
	SKIP_SENTRY=1 \
	$(VENV_PYTEST) ./tests/$(TEST_FILE).py
else
	SKIP_SENTRY=1 \
	$(VENV_PYTEST) ./tests/$(TEST_FILE).py -k $(TEST_FN)
endif
endif


.PHONY: ci_deploy
ci_deploy: ensure_git_clean
	@echo Tag the current commit as the deploy head for this branch
	git tag -f deploy-$(STAGE)-$(GIT_COMMIT_HASH)
	git push --tags origin HEAD


.PHONY: deploy
deploy: ensure_git_clean
	$(MAKE) ensure_no_venv
	@echo Implement me

clean:
	rm -rf $(VENV)
	rm -rf tasks/node_modules
