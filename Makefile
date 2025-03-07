.PHONY: sdk docker

.DEFAULT_GOAL := docker
TEMPLATE := $(word 2, $(MAKECMDGOALS))
# 自动获取cpu架构
ARCH := $(shell uname -m)
test:
	python -m pytest -k

release:
	cd python-sdk &&\
	python ./setup.py clean &&\
	python ./setup.py sdist &&\
	python ./setup.py bdist_wheel &&\
	twine upload dist/*

docker:
	docker build . -t weopsproxy

docker-arm:
	docker build . -f Dockerfile.arm -t weops-proxy

test:
	cd python-sdk && python -m pytest -k

render:
	consul-template -template templates/$(TEMPLATE).tpl -once --consul-addr=http://proxy.weops.com -dry