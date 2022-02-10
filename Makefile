VENV := .venv
VENV_ACTIVATE := $(VENV)/bin/activate
RUN := poetry run
CURRENT_PASSWORD ?=
NEW_PASSWORD ?=
EXAMPLE_FILE ?= upload_example
GIT_COMMIT_HASH := $$(git rev-parse HEAD)
CMD ?= run
ELK_VERSION ?= 7.10.2
AWS_PROFILE ?= mzakany

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
$(VENV): rebuild_venv build_develop install_linting


.PHONY: rebuild_venv
rebuild_venv: ensure_no_venv
	rm -rf $(VENV)


.PHONY: build_develop
build_develop:
	poetry install


.PHONY: install_linting
install_linting:
	$(RUN) pre-commit install


.PHONY: pre-commit
pre-commit:
	$(RUN) pre-commit run -a


.PHONY: test
.PHONY: test
test:
ifeq ($(TEST_FILE),)
	SKIP_SENTRY=1 \
	$(RUN) pytest --cov=perfin  --cov-report term-missing tests/ -s
else
ifeq ($(TEST_FN),)
	SKIP_SENTRY=1 \
	$(RUN) pytest ./tests/$(TEST_FILE).py -s
else
	SKIP_SENTRY=1 \
	$(RUN) pytest ./tests/$(TEST_FILE).py -k $(TEST_FN) -s
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
	docker volume rm $(docker volume ls -qf dangling=true) ;\
	docker system prune ;\
	docker system df ;\
	docker container prune ;\
	docker network prune ;\


.PHONY: cli
cli:
	. $(VENV_ACTIVATE) ;\
	export AWS_PROFILE=$(AWS_PROFILE);\
	python ./cli.py $(CMD)


.PHONY: run
start:
	TAG=$(ELK_VERSION) docker-compose up --remove-orphans


.PHONY: stop
stop:
	docker-compose down


.PHONY: terraform_init
terraform_init:
	export AWS_PROFILE=$(AWS_PROFILE);\
	cd ./terraform ;\
	terraform init


.PHONY: terraform_plan
terraform_plan:
	export AWS_PROFILE=$(AWS_PROFILE);\
	cd ./terraform ;\
	terraform plan -var-file=dev.tfvars


.PHONY: terraform_apply
terraform_apply: terraform_init
	export AWS_PROFILE=$(AWS_PROFILE);\
	cd ./terraform ;\
	terraform apply -var-file=dev.tfvars


.PHONY: terraform_apply
terraform_destry: terraform_init
	export AWS_PROFILE=perfin_terraform;\
	cd ./terraform ;\
	terraform destroy


.PHONY: coveralls
coveralls:
	. $(VENV_ACTIVATE) ;\
	coverage run --source=perfin -m pytest tests/ ;\
	coveralls


.PHONY: tox
tox:
	. $(VENV_ACTIVATE) ;\
	tox


.PHONY: deploy
deploy: terraform_apply


.PHONY: destroy
destroy: terraform_destroy
