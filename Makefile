.PHONY: sdk docker

.DEFAULT_GOAL := docker

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