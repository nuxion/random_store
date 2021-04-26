define USAGE
Super awesome hand-crafted build system ⚙️

Commands:
	setup     Install dependencies, dev included
	lock      Generate requirements.txt
	test      Run linters, test db migrations and tests.
	serve     Run app in dev environment.
	release   Build and publish docker image to registry.int.deskcrash.com
endef

export USAGE
.EXPORT_ALL_VARIABLES:
VERSION := $(shell git describe --tags)
BUILD := $(shell git rev-parse --short HEAD)
PROJECTNAME := $(shell basename "$(PWD)")
PACKAGE_DIR = $(shell basename "$(PWD)")

help:
	@echo "$$USAGE"

lock:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

test:
	echo "Running pylint...\n"
	pylint --disable=R,C,W $(PACKAGE_DIR)
	echo "Running isort...\n"
	isort --check $(PACKAGE_DIR)
	echo "Running mypy...\n"
	mypy $(PACKAGE_DIR)
	# echo "Looking for breakpoint...\n"
	# find $(PACKAGE_DIR) -name "*.py" | xargs grep breakpoint
	# pytest
	PYTHONPATH=$(PWD) pytest tests/

pytest:
	PYTHONPATH=$(PWD) pytest tests/

setup:
	poetry install --dev

run:
	docker run --rm -p 127.0.0.1:8000:8000 --env-file=.env nuxion/${PROJECTNAME}

docker:
	docker build -t nuxion/${PROJECTNAME} .

release: docker
	docker tag nuxion/${PROJECTNAME} registry.int.deskcrash.com/nuxion/${PROJECTNAME}:$(VERSION)
	# docker push registry.int.deskcrash.com/nuxion/$(PROJECTNAME)
	docker push registry.int.deskcrash.com/nuxion/$(PROJECTNAME):$(VERSION)

registry:
	# curl http://registry.int.deskcrash.com/v2/_catalog | jq
	curl http://registry.int.deskcrash.com/v2/nuxion/$(PROJECTNAME)/tags/list 

redis-cli:
	docker-compose exec redis redis-cli
